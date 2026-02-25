"""Six-panel visualization for HFF κ vs Chandra-proxy morphology operator.

This is an *independent* 2×3 (six-frame) visualizer for the κ-vs-Xray pipeline.
It does not modify or depend on the existing SPARC/dyed-spacetime 6-panel atlas.

Layout (2×3):
- Top row: κ (smoothed) at levels 99/97/95, with primary-blob mask + centroid.
- Bottom row: Chandra proxy (smoothed) at levels 99/97/95, with primary-blob mask + centroid.

For each column (level), the panel shows:
- image = smoothed, ROI-cropped map
- contour = largest connected component above percentile threshold
- marker = unweighted mask centroid (primary blob)

This script is meant to make the metrics interpretable: you can see *what* blob
was selected in each map at each threshold and how ROI choice affects topology.

Example (Abell 2744, Diego v4.1):
  d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe \
    toy_models/visualize_hff_kappa_xray_sixpanel.py \
    --map-kappa toy_models/data/hff/abell2744/external_lensing/stsci_frontier/diego_v4.1/hlsp_frontier_model_abell2744_diego_v4.1_kappa.fits \
    --map-xray  toy_models/data/hff/abell2744/chandra_stack/abell2744_chandra_full_img2_proxy.fits \
    --roi-center-icrs 3.5887474051936,-30.397192536687 \
    --roi-radius-arcsec 100 \
    --out-png toy_models/out_predictions/figures/abell2744_diego_v4p1_roi100_sixpanel.png
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Blob:
    mask: np.ndarray
    area_pix: int
    cx: float
    cy: float
    ra_deg: float
    dec_deg: float


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
    from scipy.ndimage import gaussian_filter, fourier_gaussian

    sx, sy = _pixel_scales_arcsec(wcs)
    sig_x = float(sigma_arcsec) / sx
    sig_y = float(sigma_arcsec) / sy

    out = np.array(d, copy=True)
    nan_mask = ~np.isfinite(out)
    if nan_mask.any():
        finite = out[np.isfinite(out)]
        fill = float(np.nanmedian(finite)) if finite.size else 0.0
        out[nan_mask] = fill

    # For very fine-pixel maps, 8" corresponds to a huge sigma in pixels.
    # Spatial-domain gaussian_filter becomes extremely slow as sigma grows
    # (effective kernel radius scales with sigma). Switch to FFT-domain
    # smoothing in that regime.
    sigma_pix_max = float(max(sig_x, sig_y))
    if sigma_pix_max >= 25.0:
        pad = int(min(max(32, round(4.0 * sigma_pix_max)), 512))
        padded = np.pad(out, ((pad, pad), (pad, pad)), mode="edge")
        F = np.fft.fftn(padded)
        F2 = fourier_gaussian(F, sigma=(sig_y, sig_x))
        sm = np.fft.ifftn(F2).real
        out = sm[pad : sm.shape[0] - pad, pad : sm.shape[1] - pad]
    else:
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


def _primary_blob(*, data: np.ndarray, wcs, level_pct: float) -> Blob | None:
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

    best: Blob | None = None
    for blob_id in range(1, n + 1):
        m = lab == blob_id
        if not m.any():
            continue
        yy, xx = np.nonzero(m)
        area = int(xx.size)
        cx = float(np.mean(xx))
        cy = float(np.mean(yy))
        world = wcs.pixel_to_world(cx, cy)

        def _to_deg(sc) -> tuple[float, float]:
            if isinstance(sc, SkyCoord):
                return (float(sc.ra.deg), float(sc.dec.deg))
            return (float(getattr(sc, "ra").deg), float(getattr(sc, "dec").deg))

        ra, dec = _to_deg(world)
        cand = Blob(mask=m, area_pix=area, cx=cx, cy=cy, ra_deg=ra, dec_deg=dec)
        if best is None or cand.area_pix > best.area_pix:
            best = cand

    return best


def _robust_vmin_vmax(img: np.ndarray) -> tuple[float, float]:
    finite = img[np.isfinite(img)]
    if finite.size == 0:
        return (0.0, 1.0)
    lo = float(np.nanpercentile(finite, 5.0))
    hi = float(np.nanpercentile(finite, 99.5))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        med = float(np.nanmedian(finite))
        return (med - 1.0, med + 1.0)
    return (lo, hi)


def _make_figure(*, kappa_img: np.ndarray, xray_img: np.ndarray, blobs_k: dict[float, Blob | None], blobs_x: dict[float, Blob | None], levels: list[float], out_png: Path, title: str) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(12, 8), constrained_layout=True)

    # Plot helper
    def draw(ax, img, blob: Blob | None, *, label: str):
        vmin, vmax = _robust_vmin_vmax(img)
        ax.imshow(img, origin="lower", cmap="magma", vmin=vmin, vmax=vmax)
        if blob is not None and np.any(blob.mask):
            ax.contour(blob.mask.astype(float), levels=[0.5], colors=["cyan"], linewidths=1.2)
            ax.plot([blob.cx], [blob.cy], marker="x", color="cyan", markersize=8, mew=2)
            ax.text(0.02, 0.02, f"area={blob.area_pix}", transform=ax.transAxes, ha="left", va="bottom", color="white", fontsize=9)
        ax.set_title(label)
        ax.set_xticks([])
        ax.set_yticks([])

    # Top row: kappa
    for j, lvl in enumerate(levels):
        draw(axes[0, j], kappa_img, blobs_k.get(lvl), label=f"κ (smoothed) @ {int(lvl)}%")

    # Bottom row: xray
    for j, lvl in enumerate(levels):
        ax = axes[1, j]
        draw(ax, xray_img, blobs_x.get(lvl), label=f"Chandra proxy (smoothed) @ {int(lvl)}%")

        bk = blobs_k.get(lvl)
        bx = blobs_x.get(lvl)
        if bk is not None and bx is not None:
            # separation in pixel space is not meaningful; use sky coords if available
            # (we already computed ra/dec at centroids)
            import astropy.units as u
            from astropy.coordinates import SkyCoord

            a = SkyCoord(bk.ra_deg * u.deg, bk.dec_deg * u.deg, frame="icrs")
            b = SkyCoord(bx.ra_deg * u.deg, bx.dec_deg * u.deg, frame="icrs")
            sep = float(a.separation(b).arcsec)
            ax.text(0.02, 0.98, f"sep={sep:0.2f}\"", transform=ax.transAxes, ha="left", va="top", color="white", fontsize=10)

    fig.suptitle(title)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map-kappa", type=Path, required=True, help="Frontier κ FITS")
    ap.add_argument("--map-xray", type=Path, required=True, help="Stacked Chandra proxy FITS")

    ap.add_argument("--roi-center-icrs", type=str, required=True, help="ROI center 'RA_DEG,DEC_DEG'")
    ap.add_argument("--roi-radius-arcsec", type=float, required=True)

    ap.add_argument("--smooth-kappa-arcsec", type=float, default=8.0)
    ap.add_argument("--smooth-xray-arcsec", type=float, default=8.0)
    ap.add_argument("--levels", type=float, nargs="+", default=[99.0, 97.0, 95.0])

    ap.add_argument("--out-png", type=Path, required=True)
    ap.add_argument("--title", type=str, default="")

    args = ap.parse_args()

    from astropy.coordinates import SkyCoord
    import astropy.units as u
    from astropy.wcs import WCS

    parts = [p.strip() for p in str(args.roi_center_icrs).split(",")]
    if len(parts) != 2:
        raise SystemExit("--roi-center-icrs must be RA_DEG,DEC_DEG")
    center = SkyCoord(float(parts[0]) * u.deg, float(parts[1]) * u.deg, frame="icrs")

    k_data, k_hdr, k_wcs = _read_fits(args.map_kappa)
    x_data, x_hdr, x_wcs = _read_fits(args.map_xray)

    k_crop, k_origin = _roi_crop(data=k_data, wcs=k_wcs, center_icrs=center, radius_arcsec=float(args.roi_radius_arcsec))
    x_crop, x_origin = _roi_crop(data=x_data, wcs=x_wcs, center_icrs=center, radius_arcsec=float(args.roi_radius_arcsec))

    k_hdr2 = _shift_header_for_crop(k_hdr, origin_yx=k_origin)
    x_hdr2 = _shift_header_for_crop(x_hdr, origin_yx=x_origin)

    k_wcs2 = WCS(k_hdr2)
    x_wcs2 = WCS(x_hdr2)

    k_s = _smooth_gaussian_arcsec(k_crop, k_wcs2, float(args.smooth_kappa_arcsec))
    x_s = _smooth_gaussian_arcsec(x_crop, x_wcs2, float(args.smooth_xray_arcsec))

    levels = [float(l) for l in args.levels]
    blobs_k = {lvl: _primary_blob(data=k_s, wcs=k_wcs2, level_pct=lvl) for lvl in levels}
    blobs_x = {lvl: _primary_blob(data=x_s, wcs=x_wcs2, level_pct=lvl) for lvl in levels}

    title = args.title.strip()
    if not title:
        title = f"Six-panel κ vs Chandra proxy | ROI={float(args.roi_radius_arcsec):0.0f}\" | levels={','.join(str(int(x)) for x in levels)}"

    _make_figure(
        kappa_img=k_s,
        xray_img=x_s,
        blobs_k=blobs_k,
        blobs_x=blobs_x,
        levels=levels,
        out_png=args.out_png,
        title=title,
    )

    print(f"Wrote: {args.out_png.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
