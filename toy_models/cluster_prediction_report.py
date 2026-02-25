"""Generate falsifiable, SPARC-motivated cluster morphology metrics from maps.

This tool is meant to *operationalize* simple predictions that follow from a
"baryons + intrinsic response" view calibrated on SPARC-like regularities:

H1 (Equilibrium tracking): in relaxed systems, a response proxy should be
    co-located with baryon proxies (small centroid separations).

H2 (Merger / memory): in disturbed mergers, baryon proxies (e.g., X-ray gas)
    can be displaced while the response proxy may remain closer to a lagged or
    collisionless component. Operationally this predicts larger response–gas
    separations than in relaxed systems.

H3 (Uncertainty honesty): lens-model uncertainty should be propagated into any
    derived centroid separation, at least via posterior samples if available.

What this script measures
-------------------------
Given two FITS scalar maps with WCS (A=response, B=baryon proxy), for a set of
percentile "levels" (e.g., 99, 97, 95) it:

- Smooths each map to specified sigma (arcsec)
- Crops to a shared sky ROI (center+radius)
- Extracts connected-component blobs above each percentile threshold
- Selects a "primary" blob per map (largest area by default)
- Reports per-level centroid coordinates and A–B separations

Optional: response posterior samples
-----------------------------------
If you provide a glob of sample maps for A, it repeats the A-blob centroid
measurement per sample and reports a separation distribution vs the fixed B
centroid. To reduce blob switching, the script anchors sample blob selection to

- the best-fit A centroid at that level (within a max anchor distance)

Outputs
-------
- out_metrics_csv: per-level primary-blob metrics and A–B separation
- out_samples_csv: per-sample separation rows (if samples provided)

Example (Bullet: κ vs stacked Chandra rate proxy)
-------------------------------------------------
./.venv/Scripts/python.exe toy_models/cluster_prediction_report.py \
  --map-a toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  --map-b toy_models/out_xray/chandra_xray_rate_stack_full.fits \
  --roi-center-icrs 104.63088146599212,-55.934259101595984 --roi-radius-arcsec 900 \
  --smooth-a-arcsec 8 --smooth-b-arcsec 8 \
  --levels 99 97 95 \
  --a-samples-glob "toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/sample_model/sample_maps/bulletclu-kappa-200mas_*.fits" \
  --anchor-max-arcsec 90 \
  --out-metrics toy_models/out_predictions/bullet_metrics.csv \
  --out-samples toy_models/out_predictions/bullet_samples.csv

Note
----
This does not claim that X-ray surface brightness is a true \rho_bar map.
It's a robust *gas tracer* for morphology and offsets.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class BlobInfo:
    blob_id: int
    area_pix: int
    centroid_x: float
    centroid_y: float
    centroid_ra_deg: float
    centroid_dec_deg: float


def _read_fits(path: Path):
    from astropy.io import fits
    from astropy.wcs import WCS

    with fits.open(path) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    if data is None or np.asarray(data).ndim != 2:
        raise ValueError(f"Expected 2D image in {path}")
    return np.asarray(data, dtype=float), header, WCS(header)


def _pixel_scales_arcsec(wcs) -> tuple[float, float]:
    from astropy.wcs.utils import proj_plane_pixel_scales

    sc = proj_plane_pixel_scales(wcs)  # deg/pix
    return (float(abs(sc[0]) * 3600.0), float(abs(sc[1]) * 3600.0))


def _smooth_gaussian_arcsec(d: np.ndarray, wcs, sigma_arcsec: float) -> np.ndarray:
    if float(sigma_arcsec) <= 0:
        return d
    from scipy.ndimage import gaussian_filter

    sx, sy = _pixel_scales_arcsec(wcs)
    sig_x = float(sigma_arcsec) / sx
    sig_y = float(sigma_arcsec) / sy

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


def _shift_header_for_crop(header, *, origin_yx: tuple[int, int]):
    y0, x0 = origin_yx
    hdr = header.copy()
    if "CRPIX1" in hdr:
        hdr["CRPIX1"] = float(hdr["CRPIX1"]) - float(x0)
    if "CRPIX2" in hdr:
        hdr["CRPIX2"] = float(hdr["CRPIX2"]) - float(y0)
    return hdr


def _primary_blob_centroid(*, data: np.ndarray, wcs, level_pct: float) -> BlobInfo | None:
    from scipy.ndimage import label
    from astropy.coordinates import SkyCoord

    finite = data[np.isfinite(data)]
    if finite.size == 0:
        return None

    thr = float(np.nanpercentile(finite, float(level_pct)))
    mask = np.isfinite(data) & (data >= thr)
    if not mask.any():
        return None

    lab, n = label(mask, structure=np.ones((3, 3), dtype=int))
    if n <= 0:
        return None

    best: BlobInfo | None = None
    for blob_id in range(1, n + 1):
        m = lab == blob_id
        if not m.any():
            continue
        yy, xx = np.nonzero(m)
        area = int(xx.size)
        # Simple unweighted centroid at this threshold (robust, matches mask definition)
        cx = float(np.mean(xx))
        cy = float(np.mean(yy))
        world = wcs.pixel_to_world(cx, cy)

        def _to_deg(sc) -> tuple[float, float]:
            if isinstance(sc, SkyCoord):
                return (float(sc.ra.deg), float(sc.dec.deg))
            return (float(getattr(sc, "ra").deg), float(getattr(sc, "dec").deg))

        ra, dec = _to_deg(world)
        cand = BlobInfo(blob_id=blob_id, area_pix=area, centroid_x=cx, centroid_y=cy, centroid_ra_deg=ra, centroid_dec_deg=dec)
        if best is None or cand.area_pix > best.area_pix:
            best = cand

    return best


def _choose_sample_blob_near_anchor(*, data: np.ndarray, wcs, level_pct: float, anchor_ra_dec_deg: tuple[float, float], max_sep_arcsec: float) -> BlobInfo | None:
    from scipy.ndimage import label
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    finite = data[np.isfinite(data)]
    if finite.size == 0:
        return None

    thr = float(np.nanpercentile(finite, float(level_pct)))
    mask = np.isfinite(data) & (data >= thr)
    if not mask.any():
        return None

    lab, n = label(mask, structure=np.ones((3, 3), dtype=int))
    if n <= 0:
        return None

    anchor = SkyCoord(anchor_ra_dec_deg[0] * u.deg, anchor_ra_dec_deg[1] * u.deg, frame="icrs")

    best: tuple[float, BlobInfo] | None = None
    for blob_id in range(1, n + 1):
        m = lab == blob_id
        if not m.any():
            continue
        yy, xx = np.nonzero(m)
        cx = float(np.mean(xx))
        cy = float(np.mean(yy))
        world = wcs.pixel_to_world(cx, cy)
        ra = float(getattr(world, "ra").deg)
        dec = float(getattr(world, "dec").deg)
        sc = SkyCoord(ra * u.deg, dec * u.deg, frame="icrs")
        sep = float(anchor.separation(sc).to(u.arcsec).value)
        if sep > float(max_sep_arcsec):
            continue
        area = int(xx.size)
        cand = BlobInfo(blob_id=blob_id, area_pix=area, centroid_x=cx, centroid_y=cy, centroid_ra_deg=ra, centroid_dec_deg=dec)
        # Rank by closest sep, tie-break by larger area.
        key = (sep, -area)
        if best is None or key < (best[0], -best[1].area_pix):
            best = (sep, cand)

    return None if best is None else best[1]


def _sep_arcsec(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    a = SkyCoord(ra1 * u.deg, dec1 * u.deg, frame="icrs")
    b = SkyCoord(ra2 * u.deg, dec2 * u.deg, frame="icrs")
    return float(a.separation(b).to(u.arcsec).value)


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
    ap.add_argument("--map-a", type=Path, required=True, help="Response proxy map (e.g., κ).")
    ap.add_argument("--map-b", type=Path, required=True, help="Baryon proxy map (e.g., X-ray tracer).")

    ap.add_argument("--smooth-a-arcsec", type=float, default=8.0)
    ap.add_argument("--smooth-b-arcsec", type=float, default=8.0)

    ap.add_argument("--roi-center-icrs", type=str, required=True, help="ROI center 'RA_DEG,DEC_DEG'.")
    ap.add_argument("--roi-radius-arcsec", type=float, required=True)

    ap.add_argument("--levels", type=float, nargs="+", default=[99.0, 97.0, 95.0])

    ap.add_argument("--a-samples-glob", type=str, default="", help="Glob for response posterior sample maps.")
    ap.add_argument("--anchor-max-arcsec", type=float, default=90.0, help="Max separation for sample blob to match best-fit blob.")

    ap.add_argument("--out-metrics", type=Path, default=Path("toy_models/out_predictions/metrics.csv"))
    ap.add_argument("--out-samples", type=Path, default=Path("toy_models/out_predictions/samples.csv"))

    args = ap.parse_args()

    from astropy.coordinates import SkyCoord
    import astropy.units as u
    from astropy.wcs import WCS

    parts = [p.strip() for p in str(args.roi_center_icrs).split(",")]
    if len(parts) != 2:
        raise SystemExit("--roi-center-icrs must be RA_DEG,DEC_DEG")
    roi_center = SkyCoord(float(parts[0]) * u.deg, float(parts[1]) * u.deg, frame="icrs")

    a_data, a_hdr, a_wcs = _read_fits(args.map_a)
    b_data, b_hdr, b_wcs = _read_fits(args.map_b)

    # Crop to ROI in each map's pixel grid and shift WCS headers accordingly.
    a_crop, a_origin = _roi_crop(data=a_data, wcs=a_wcs, center_icrs=roi_center, radius_arcsec=float(args.roi_radius_arcsec))
    b_crop, b_origin = _roi_crop(data=b_data, wcs=b_wcs, center_icrs=roi_center, radius_arcsec=float(args.roi_radius_arcsec))

    a_hdr2 = _shift_header_for_crop(a_hdr, origin_yx=a_origin)
    b_hdr2 = _shift_header_for_crop(b_hdr, origin_yx=b_origin)

    a_wcs2 = WCS(a_hdr2)
    b_wcs2 = WCS(b_hdr2)

    a_s = _smooth_gaussian_arcsec(a_crop, a_wcs2, float(args.smooth_a_arcsec))
    b_s = _smooth_gaussian_arcsec(b_crop, b_wcs2, float(args.smooth_b_arcsec))

    metric_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []

    bestfit_anchors: dict[float, tuple[float, float]] = {}

    for lvl in [float(x) for x in args.levels]:
        a_blob = _primary_blob_centroid(data=a_s, wcs=a_wcs2, level_pct=lvl)
        b_blob = _primary_blob_centroid(data=b_s, wcs=b_wcs2, level_pct=lvl)

        row: dict[str, object] = {
            "level_pct": lvl,
            "a_blob_id": a_blob.blob_id if a_blob else "",
            "a_area_pix": a_blob.area_pix if a_blob else "",
            "a_centroid_ra_deg": a_blob.centroid_ra_deg if a_blob else "",
            "a_centroid_dec_deg": a_blob.centroid_dec_deg if a_blob else "",
            "b_blob_id": b_blob.blob_id if b_blob else "",
            "b_area_pix": b_blob.area_pix if b_blob else "",
            "b_centroid_ra_deg": b_blob.centroid_ra_deg if b_blob else "",
            "b_centroid_dec_deg": b_blob.centroid_dec_deg if b_blob else "",
        }

        if a_blob and b_blob:
            sep = _sep_arcsec(a_blob.centroid_ra_deg, a_blob.centroid_dec_deg, b_blob.centroid_ra_deg, b_blob.centroid_dec_deg)
            row["sep_arcsec"] = sep
            bestfit_anchors[lvl] = (a_blob.centroid_ra_deg, a_blob.centroid_dec_deg)

        metric_rows.append(row)

    # Optional samples: compute separation distribution per level.
    if args.a_samples_glob:
        import glob

        sample_files = sorted(glob.glob(args.a_samples_glob))
        for lvl, anchor in bestfit_anchors.items():
            # Need B centroid for this level
            b_blob = _primary_blob_centroid(data=b_s, wcs=b_wcs2, level_pct=float(lvl))
            if b_blob is None:
                continue

            for sf in sample_files:
                sdata, shdr, swcs = _read_fits(Path(sf))
                s_crop, s_origin = _roi_crop(data=sdata, wcs=swcs, center_icrs=roi_center, radius_arcsec=float(args.roi_radius_arcsec))
                shdr2 = _shift_header_for_crop(shdr, origin_yx=s_origin)
                swcs2 = WCS(shdr2)
                s_s = _smooth_gaussian_arcsec(s_crop, swcs2, float(args.smooth_a_arcsec))

                s_blob = _choose_sample_blob_near_anchor(
                    data=s_s,
                    wcs=swcs2,
                    level_pct=float(lvl),
                    anchor_ra_dec_deg=anchor,
                    max_sep_arcsec=float(args.anchor_max_arcsec),
                )
                if s_blob is None:
                    continue

                sep = _sep_arcsec(s_blob.centroid_ra_deg, s_blob.centroid_dec_deg, b_blob.centroid_ra_deg, b_blob.centroid_dec_deg)
                sample_rows.append(
                    {
                        "level_pct": float(lvl),
                        "sample_file": str(sf).replace("\\\\", "/"),
                        "a_centroid_ra_deg": s_blob.centroid_ra_deg,
                        "a_centroid_dec_deg": s_blob.centroid_dec_deg,
                        "b_centroid_ra_deg": b_blob.centroid_ra_deg,
                        "b_centroid_dec_deg": b_blob.centroid_dec_deg,
                        "sep_arcsec": sep,
                    }
                )

    _write_csv(args.out_metrics, metric_rows)
    if args.a_samples_glob:
        _write_csv(args.out_samples, sample_rows)

    print(f"Wrote metrics: {args.out_metrics.resolve()}")
    if args.a_samples_glob:
        print(f"Wrote samples: {args.out_samples.resolve()} ({len(sample_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
