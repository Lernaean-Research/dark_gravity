"""Blobology: compare morphology of two WCS-tagged FITS maps fairly.

Motivation
----------
Peak *values* are apples-to-oranges across observables (κ vs X-ray brightness)
when resolution, PSF, and projection physics differ. This tool instead compares
geometric/integral descriptors of *connected regions* ("blobs") above chosen
percentile thresholds, after smoothing both maps to a common angular scale.

What it does
------------
1) Optionally defines a shared sky ROI (center + radius).
2) Smooths each map with a Gaussian sigma in arcsec.
3) For each threshold percentile:
   - Computes a threshold value on finite pixels within ROI
   - Builds a mask (data >= threshold)
   - Connected-component labels blobs
   - For each blob: centroid, peak location, area, equivalent radius,
     axis ratio + orientation from weighted 2nd moments, and a simple flux sum.
4) Writes:
   - A blob catalog CSV (one row per blob)
   - A centroid separation CSV (all A×B centroid separations per level)

This is intended as a robust *sanity check* and comparison scaffold, not a
science-grade reduction.

Example
-------
./.venv/Scripts/python.exe toy_models/blobology_from_maps.py \
  --map-a toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  --map-b toy_models/out_xray/chandra_xray_rate_stack_full.fits \
  --smooth-arcsec 8 \
  --levels 99 97 95 \
  --out-blobs toy_models/out_blobology/kappa_vs_chandra_blobs.csv \
  --out-seps toy_models/out_blobology/kappa_vs_chandra_seps.csv

Tip
---
If the κ map is huge, use ROI cropping:
  --roi-center-icrs 104.63,-55.945 --roi-radius-arcsec 900
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Blob:
    map_name: str
    level_pct: float
    blob_id: int
    n_pix: int
    area_arcsec2: float
    eq_radius_arcsec: float
    peak_val: float
    flux_sum: float
    centroid_x: float
    centroid_y: float
    peak_x: float
    peak_y: float
    centroid_ra_deg: float
    centroid_dec_deg: float
    peak_ra_deg: float
    peak_dec_deg: float
    axis_ratio: float
    theta_deg: float


def _pixel_scales_arcsec(wcs) -> tuple[float, float]:
    from astropy.wcs.utils import proj_plane_pixel_scales

    sc = proj_plane_pixel_scales(wcs)  # deg/pix
    return (float(abs(sc[0]) * 3600.0), float(abs(sc[1]) * 3600.0))


def _read_fits(path: Path):
    from astropy.io import fits
    from astropy.wcs import WCS

    with fits.open(path) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    if data is None or np.asarray(data).ndim != 2:
        raise ValueError(f"Expected 2D image in {path}")
    return np.asarray(data, dtype=float), header, WCS(header)


def _finite_percentile(d: np.ndarray, pct: float) -> float:
    x = d[np.isfinite(d)]
    if x.size == 0:
        return float("nan")
    return float(np.nanpercentile(x, pct))


def _smooth_gaussian_arcsec(d: np.ndarray, wcs, sigma_arcsec: float) -> np.ndarray:
    if float(sigma_arcsec) <= 0:
        return d
    from scipy.ndimage import gaussian_filter

    sx, sy = _pixel_scales_arcsec(wcs)
    sig_x = float(sigma_arcsec) / sx
    sig_y = float(sigma_arcsec) / sy
    # NaN-safe smoothing: fill NaNs with local median-ish (global median) before smoothing, restore NaNs.
    out = np.array(d, copy=True)
    nan_mask = ~np.isfinite(out)
    if nan_mask.any():
        med = float(np.nanmedian(out[np.isfinite(out)]))
        out[nan_mask] = med
    out = gaussian_filter(out, sigma=(sig_y, sig_x), mode="nearest")
    if nan_mask.any():
        out[nan_mask] = np.nan
    return out


def _roi_crop(*, data: np.ndarray, wcs, center_icrs, radius_arcsec: float) -> tuple[np.ndarray, tuple[int, int]]:
    """Return cropped data and (y0,x0) origin in full image pixels."""

    if center_icrs is None or not (float(radius_arcsec) > 0):
        return data, (0, 0)

    cx, cy = wcs.world_to_pixel(center_icrs)
    if not (np.isfinite(cx) and np.isfinite(cy)):
        return data, (0, 0)

    sx, sy = _pixel_scales_arcsec(wcs)
    rx = max(2, int(round(float(radius_arcsec) / sx)))
    ry = max(2, int(round(float(radius_arcsec) / sy)))

    x = int(round(float(cx)))
    y = int(round(float(cy)))

    y0 = max(0, y - ry)
    y1 = min(data.shape[0], y + ry + 1)
    x0 = max(0, x - rx)
    x1 = min(data.shape[1], x + rx + 1)
    if y1 <= y0 or x1 <= x0:
        return data, (0, 0)
    return data[y0:y1, x0:x1], (y0, x0)


def _blobs_for_level(
    *,
    map_name: str,
    level_pct: float,
    data: np.ndarray,
    wcs,
    origin_yx: tuple[int, int],
) -> list[Blob]:
    from scipy.ndimage import label
    from astropy.coordinates import SkyCoord

    y0, x0 = origin_yx

    # Threshold on finite pixels only.
    thr = _finite_percentile(data, float(level_pct))
    if not np.isfinite(thr):
        return []

    mask = np.isfinite(data) & (data >= thr)
    if not mask.any():
        return []

    lab, n = label(mask, structure=np.ones((3, 3), dtype=int))
    if n <= 0:
        return []

    sx, sy = _pixel_scales_arcsec(wcs)
    pix_area = sx * sy

    blobs: list[Blob] = []
    for blob_id in range(1, n + 1):
        m = lab == blob_id
        if not m.any():
            continue

        yy, xx = np.nonzero(m)
        vals = data[m]

        n_pix = int(vals.size)
        area_arcsec2 = float(n_pix * pix_area)
        eq_radius_arcsec = float(math.sqrt(area_arcsec2 / math.pi))

        peak_idx = int(np.nanargmax(vals))
        py = float(yy[peak_idx])
        px = float(xx[peak_idx])
        peak_val = float(vals[peak_idx])

        # Weighted centroid: robustify by subtracting local median and clipping to >=0.
        med = float(np.nanmedian(vals))
        wts = np.clip(vals - med, 0.0, None)
        if float(np.nansum(wts)) <= 0:
            wts = np.ones_like(vals, dtype=float)

        cx = float(np.nansum(xx * wts) / np.nansum(wts))
        cy = float(np.nansum(yy * wts) / np.nansum(wts))

        # 2nd moments for shape
        dx = xx - cx
        dy = yy - cy
        s = float(np.nansum(wts))
        cxx = float(np.nansum(wts * dx * dx) / s)
        cyy = float(np.nansum(wts * dy * dy) / s)
        cxy = float(np.nansum(wts * dx * dy) / s)

        cov = np.array([[cxx, cxy], [cxy, cyy]], dtype=float)
        evals, evecs = np.linalg.eigh(cov)
        # sort descending: evals[1] is major if sorted ascending by eigh
        evals = evals[::-1]
        evecs = evecs[:, ::-1]
        major = float(max(evals[0], 1.0e-12))
        minor = float(max(evals[1], 1.0e-12))
        axis_ratio = float(math.sqrt(minor / major))
        # orientation of major axis (x-axis = RA pixel axis) in degrees
        vx, vy = float(evecs[0, 0]), float(evecs[1, 0])
        theta_deg = float(math.degrees(math.atan2(vy, vx)))

        # Convert to full-image pixel coords
        cx_full = cx + x0
        cy_full = cy + y0
        px_full = px + x0
        py_full = py + y0

        cworld = wcs.pixel_to_world(cx_full, cy_full)
        pworld = wcs.pixel_to_world(px_full, py_full)

        def _to_deg(sc) -> tuple[float, float]:
            if isinstance(sc, SkyCoord):
                return (float(sc.ra.deg), float(sc.dec.deg))
            return (float(getattr(sc, "ra").deg), float(getattr(sc, "dec").deg))

        cra, cdec = _to_deg(cworld)
        pra, pdec = _to_deg(pworld)

        blobs.append(
            Blob(
                map_name=str(map_name),
                level_pct=float(level_pct),
                blob_id=int(blob_id),
                n_pix=n_pix,
                area_arcsec2=area_arcsec2,
                eq_radius_arcsec=eq_radius_arcsec,
                peak_val=peak_val,
                flux_sum=float(np.nansum(vals)),
                centroid_x=float(cx_full),
                centroid_y=float(cy_full),
                peak_x=float(px_full),
                peak_y=float(py_full),
                centroid_ra_deg=float(cra),
                centroid_dec_deg=float(cdec),
                peak_ra_deg=float(pra),
                peak_dec_deg=float(pdec),
                axis_ratio=axis_ratio,
                theta_deg=theta_deg,
            )
        )

    return blobs


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    keys: list[str] = []
    seen: set[str] = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map-a", type=Path, required=True)
    ap.add_argument("--map-b", type=Path, required=True)
    ap.add_argument("--smooth-arcsec", type=float, default=0.0)
    ap.add_argument("--levels", type=float, nargs="+", default=[99.0, 97.0, 95.0])

    ap.add_argument(
        "--roi-center-icrs",
        type=str,
        default="",
        help="Optional ROI center as 'RA_DEG,DEC_DEG'. If omitted, uses map B center.",
    )
    ap.add_argument(
        "--roi-radius-arcsec",
        type=float,
        default=float("nan"),
        help="Optional ROI radius in arcsec. If omitted, uses half-diagonal of map B.",
    )

    ap.add_argument("--out-blobs", type=Path, default=Path("toy_models/out_blobology/blobs.csv"))
    ap.add_argument("--out-seps", type=Path, default=Path("toy_models/out_blobology/seps.csv"))

    args = ap.parse_args()

    from astropy.coordinates import SkyCoord
    import astropy.units as u

    a_data, _, a_wcs = _read_fits(args.map_a)
    b_data, _, b_wcs = _read_fits(args.map_b)

    # Determine ROI center.
    roi_center = None
    if args.roi_center_icrs:
        parts = [p.strip() for p in str(args.roi_center_icrs).split(",")]
        if len(parts) != 2:
            raise SystemExit("--roi-center-icrs must be RA_DEG,DEC_DEG")
        roi_center = SkyCoord(float(parts[0]) * u.deg, float(parts[1]) * u.deg, frame="icrs")
    else:
        # Default to map B center.
        ny, nx = b_data.shape
        ra, dec = b_wcs.pixel_to_world_values(nx / 2.0, ny / 2.0)
        roi_center = SkyCoord(float(ra) * u.deg, float(dec) * u.deg, frame="icrs")

    # Determine ROI radius.
    roi_radius = float(args.roi_radius_arcsec)
    if not np.isfinite(roi_radius) or not (roi_radius > 0):
        # Half-diagonal of B image in arcsec.
        sx, sy = _pixel_scales_arcsec(b_wcs)
        ny, nx = b_data.shape
        roi_radius = 0.5 * math.sqrt((nx * sx) ** 2 + (ny * sy) ** 2)

    # Crop both maps to same sky ROI.
    a_crop, a_origin = _roi_crop(data=a_data, wcs=a_wcs, center_icrs=roi_center, radius_arcsec=roi_radius)
    b_crop, b_origin = _roi_crop(data=b_data, wcs=b_wcs, center_icrs=roi_center, radius_arcsec=roi_radius)

    # Smooth (within ROI crop).
    a_s = _smooth_gaussian_arcsec(a_crop, a_wcs, float(args.smooth_arcsec))
    b_s = _smooth_gaussian_arcsec(b_crop, b_wcs, float(args.smooth_arcsec))

    blob_rows: list[dict[str, object]] = []
    sep_rows: list[dict[str, object]] = []

    all_blobs: dict[tuple[str, float], list[Blob]] = {}

    for lvl in [float(x) for x in args.levels]:
        a_blobs = _blobs_for_level(map_name="A", level_pct=lvl, data=a_s, wcs=a_wcs, origin_yx=a_origin)
        b_blobs = _blobs_for_level(map_name="B", level_pct=lvl, data=b_s, wcs=b_wcs, origin_yx=b_origin)
        all_blobs[("A", lvl)] = a_blobs
        all_blobs[("B", lvl)] = b_blobs

        for bl in a_blobs + b_blobs:
            blob_rows.append(
                {
                    "map": bl.map_name,
                    "level_pct": bl.level_pct,
                    "blob_id": bl.blob_id,
                    "n_pix": bl.n_pix,
                    "area_arcsec2": bl.area_arcsec2,
                    "eq_radius_arcsec": bl.eq_radius_arcsec,
                    "peak_val": bl.peak_val,
                    "flux_sum": bl.flux_sum,
                    "centroid_ra_deg": bl.centroid_ra_deg,
                    "centroid_dec_deg": bl.centroid_dec_deg,
                    "peak_ra_deg": bl.peak_ra_deg,
                    "peak_dec_deg": bl.peak_dec_deg,
                    "axis_ratio": bl.axis_ratio,
                    "theta_deg": bl.theta_deg,
                }
            )

        # All-pairs centroid separations for this level.
        for ai, ab in enumerate(a_blobs, start=1):
            for bi, bb in enumerate(b_blobs, start=1):
                ca = SkyCoord(ab.centroid_ra_deg * u.deg, ab.centroid_dec_deg * u.deg, frame="icrs")
                cb = SkyCoord(bb.centroid_ra_deg * u.deg, bb.centroid_dec_deg * u.deg, frame="icrs")
                sep_arcsec = float(ca.separation(cb).to(u.arcsec).value)
                sep_rows.append(
                    {
                        "level_pct": lvl,
                        "a_blob": f"A{ai}",
                        "b_blob": f"B{bi}",
                        "sep_arcsec": sep_arcsec,
                        "a_centroid_ra_deg": ab.centroid_ra_deg,
                        "a_centroid_dec_deg": ab.centroid_dec_deg,
                        "b_centroid_ra_deg": bb.centroid_ra_deg,
                        "b_centroid_dec_deg": bb.centroid_dec_deg,
                    }
                )

    _write_csv(args.out_blobs, blob_rows)
    _write_csv(args.out_seps, sep_rows)

    print(f"ROI center: {roi_center.ra.deg:.6f}, {roi_center.dec.deg:.6f} | radius_arcsec={roi_radius:.1f}")
    print(f"Wrote blobs: {args.out_blobs.resolve()}")
    print(f"Wrote seps: {args.out_seps.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
