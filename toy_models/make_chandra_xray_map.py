"""Build an observed Chandra X-ray proxy map from HEASARC "img2" products.

This is a lightweight, CIAO-free path intended for peak/centroid location work:
- Reads HEASARC-provided *_full_img2.fits.gz (or *_cntr_img2.fits.gz)
- Approximates exposure correction by dividing by the scalar EXPOSURE keyword
- Reprojects each image onto a common WCS grid
- Exposure-weights and stacks into a single rate map (counts/s)

Notes
-----
This is *not* a full science-grade reduction (no exposure maps, vignetting,
background modeling, point-source masking, etc.). For our current purpose
(robust X-ray peak/centroid comparison against lensing maps), this is a
reasonable first-pass observational gas tracer.

Example
-------
./.venv/Scripts/python.exe toy_models/make_chandra_xray_map.py \
  --input-glob "toy_models/data/bullet_cluster/raw/heasarc/chandra/*/primary/*_full_img2.fits.gz" \
  --out-fits toy_models/out_xray/chandra_xray_rate_stack_full.fits

Then run offsets:
./.venv/Scripts/python.exe toy_models/offset_from_maps.py \
  --map-a toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  --map-b toy_models/out_xray/chandra_xray_rate_stack_full.fits \
  --anchor-icrs 104.658730,-55.957154 --anchor-label main \
  --anchor-icrs 104.677746,-55.976544 --anchor-label sub \
    --anchor-search-arcsec 30 --anchor-search-arcsec-b 120 \
  --out-csv toy_models/out_offsets/canucs_kappa_vs_chandra_xray.csv
"""

from __future__ import annotations

import argparse
import csv
import glob
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class InputImage:
    path: Path
    exposure_s: float
    obs_id: str


def _read_image_and_wcs(path: Path):
    from astropy.io import fits
    from astropy.wcs import WCS

    with fits.open(path) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    if data is None or np.asarray(data).ndim != 2:
        raise ValueError(f"Expected 2D image in {path}")
    wcs = WCS(header)
    return np.asarray(data, dtype=float), header, wcs


def _extract_exposure_and_obsid(header) -> tuple[float, str]:
    exp = header.get("EXPOSURE")
    if exp is None:
        exp = header.get("LIVETIME")
    if exp is None:
        exp = header.get("ONTIME")
    if exp is None:
        raise ValueError("No EXPOSURE/LIVETIME/ONTIME keyword found")

    obs = header.get("OBS_ID")
    if obs is None:
        obs = header.get("OBSID")
    if obs is None:
        obs = ""
    return float(exp), str(obs)


def _reproject_to_ref(*, src_data: np.ndarray, src_wcs, ref_wcs, ref_shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    """Reproject src_data onto the reference WCS grid.

    Returns (values, valid_mask) where valid_mask is True for pixels whose
    world-coordinates map inside src_data bounds.
    """

    from scipy.ndimage import map_coordinates

    ny, nx = ref_shape
    yy, xx = np.indices((ny, nx), dtype=float)

    # Pixel -> world on reference grid.
    ra_deg, dec_deg = ref_wcs.pixel_to_world_values(xx, yy)
    # World -> pixel in source grid.
    sx, sy = src_wcs.world_to_pixel_values(ra_deg, dec_deg)

    valid = (
        np.isfinite(sx)
        & np.isfinite(sy)
        & (sx >= 0)
        & (sy >= 0)
        & (sx <= (src_data.shape[1] - 1))
        & (sy <= (src_data.shape[0] - 1))
    )

    out = np.full((ny, nx), np.nan, dtype=float)
    if not np.any(valid):
        return out, valid

    coords = np.vstack([sy[valid], sx[valid]])
    sampled = map_coordinates(src_data, coords, order=1, mode="constant", cval=np.nan)
    out[valid] = sampled
    return out, valid


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input-glob",
        type=str,
        default="toy_models/data/bullet_cluster/raw/heasarc/chandra/*/primary/*_full_img2.fits.gz",
        help="Glob for HEASARC img2 FITS.gz inputs.",
    )
    ap.add_argument(
        "--reference",
        type=str,
        default="",
        help="Optional path to the reference FITS (defaults to max exposure among inputs).",
    )
    ap.add_argument(
        "--out-fits",
        type=Path,
        default=Path("toy_models/out_xray/chandra_xray_rate_stack.fits"),
        help="Output FITS path (rate map, counts/s).",
    )
    ap.add_argument(
        "--out-manifest",
        type=Path,
        default=Path("toy_models/out_xray/chandra_xray_stack_manifest.csv"),
        help="CSV manifest of inputs used in the stack.",
    )
    ap.add_argument(
        "--smooth-arcsec",
        type=float,
        default=0.0,
        help="Optional Gaussian smoothing sigma in arcsec (0 = none).",
    )

    args = ap.parse_args()

    paths = [Path(p) for p in sorted(glob.glob(args.input_glob))]
    if not paths:
        raise SystemExit(f"No inputs matched: {args.input_glob}")

    inputs: list[InputImage] = []
    for p in paths:
        _, h, _ = _read_image_and_wcs(p)
        exp, obs = _extract_exposure_and_obsid(h)
        inputs.append(InputImage(path=p, exposure_s=exp, obs_id=obs))

    if args.reference:
        ref_path = Path(args.reference)
    else:
        ref_path = max(inputs, key=lambda x: x.exposure_s).path

    ref_data, ref_header, ref_wcs = _read_image_and_wcs(ref_path)
    ref_shape = ref_data.shape

    num = np.zeros(ref_shape, dtype=float)
    den = np.zeros(ref_shape, dtype=float)

    for inp in inputs:
        data, header, wcs = _read_image_and_wcs(inp.path)
        exp, _ = _extract_exposure_and_obsid(header)
        if exp <= 0:
            continue

        rate = data / exp
        reproj_rate, valid = _reproject_to_ref(src_data=rate, src_wcs=wcs, ref_wcs=ref_wcs, ref_shape=ref_shape)

        # Exposure-weighted average of rate => sum(rate*exp)/sum(exp)
        w = float(exp)
        num[valid] += reproj_rate[valid] * w
        den[valid] += w

    out = np.full(ref_shape, np.nan, dtype=float)
    m = den > 0
    out[m] = num[m] / den[m]

    if float(args.smooth_arcsec) > 0:
        from astropy.wcs.utils import proj_plane_pixel_scales
        from scipy.ndimage import gaussian_filter

        sc = proj_plane_pixel_scales(ref_wcs)  # deg/pix
        pix_arcsec = float(abs(sc[0]) * 3600.0)
        sigma_pix = float(args.smooth_arcsec) / pix_arcsec
        out = gaussian_filter(out, sigma=sigma_pix, mode="nearest")

    # Write outputs
    args.out_fits.parent.mkdir(parents=True, exist_ok=True)
    args.out_manifest.parent.mkdir(parents=True, exist_ok=True)

    from astropy.io import fits

    hdr = ref_header.copy()
    hdr["BUNIT"] = "count/s"
    hdr.add_history("Stacked HEASARC Chandra img2 products (rate map, counts/s)")
    hdr.add_history(f"Input glob: {args.input_glob}")
    hdr.add_history(f"Reference: {ref_path.as_posix()}")
    if float(args.smooth_arcsec) > 0:
        hdr.add_history(f"Gaussian smoothing sigma_arcsec={float(args.smooth_arcsec):.3f}")

    fits.writeto(args.out_fits, out.astype(np.float32), header=hdr, overwrite=True)

    with args.out_manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "obs_id", "exposure_s"])
        w.writeheader()
        for inp in sorted(inputs, key=lambda x: x.exposure_s, reverse=True):
            w.writerow({"path": inp.path.as_posix(), "obs_id": inp.obs_id, "exposure_s": f"{inp.exposure_s:.6f}"})

    print(f"Inputs: {len(inputs)}")
    print(f"Reference: {ref_path}")
    print(f"Wrote FITS: {args.out_fits.resolve()}")
    print(f"Wrote manifest: {args.out_manifest.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
