"""Compute gradients of mass concentration proxies from lensing maps.

This script is intentionally literal: it operates on a 2D convergence map κ(θ)
(or any scalar FITS image) and computes spatial gradients.

What you get
------------
- ∂κ/∂x, ∂κ/∂y in units of 1/arcsec (or 1/kpc if a redshift is provided)
- |∇κ| (gradient magnitude) map
- Optional 1D radial profiles of κ and |∇κ| around user-specified sky centers

Important caveats
-----------------
- κ is *projected* (2D) and typically dimensionless. ∇κ measures the steepness
  of κ features in projection, not a 3D mass-density gradient.
- Converting κ to physical surface density Σ requires Σ_crit, which depends on
  source redshift distribution; this script does not attempt that.

Example (Bullet CANUCS best-fit κ)
---------------------------------
./.venv/Scripts/python.exe toy_models/gradients_from_lensing.py \
  --map toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  --smooth-arcsec 1.0 \
  --out-grad toy_models/out_gradients/bullet_kappa_gradmag.fits \
  --center-icrs 104.63088146599212,-55.934259101595984 --center-label main \
  --center-icrs 104.65133618524507,-55.954709016840965 --center-label sub \
  --profile-rmax-arcsec 600 --profile-dr-arcsec 6 \
  --out-profile toy_models/out_gradients/bullet_kappa_profiles.csv
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Center:
    label: str
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


def _write_fits_like(path: Path, *, data: np.ndarray, header, bunit: str | None = None) -> None:
    from astropy.io import fits

    path.parent.mkdir(parents=True, exist_ok=True)
    hdr = header.copy()
    if bunit is not None:
        hdr["BUNIT"] = str(bunit)
    hdu = fits.PrimaryHDU(data=np.asarray(data, dtype=float), header=hdr)
    hdu.writeto(path, overwrite=True)


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


def _shift_header_for_crop(header, *, origin_yx: tuple[int, int]):
    """Shift CRPIX to keep WCS consistent after cropping."""

    y0, x0 = origin_yx
    hdr = header.copy()
    if "CRPIX1" in hdr:
        hdr["CRPIX1"] = float(hdr["CRPIX1"]) - float(x0)
    if "CRPIX2" in hdr:
        hdr["CRPIX2"] = float(hdr["CRPIX2"]) - float(y0)
    return hdr


def _gradients_per_arcsec(d: np.ndarray, wcs) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (dk_dx, dk_dy, grad_mag) with x=RA-pixel axis, y=DEC-pixel axis."""

    sx, sy = _pixel_scales_arcsec(wcs)

    # np.gradient expects spacing per axis (rows=y, cols=x)
    dk_dy, dk_dx = np.gradient(d, sy, sx, edge_order=1)
    grad_mag = np.sqrt(dk_dx * dk_dx + dk_dy * dk_dy)
    return dk_dx, dk_dy, grad_mag


def _kpc_per_arcsec(z: float, *, H0: float = 70.0, Om0: float = 0.3) -> float:
    from astropy.cosmology import FlatLambdaCDM
    import astropy.units as u

    cosmo = FlatLambdaCDM(H0=H0 * u.km / u.s / u.Mpc, Om0=Om0)
    return float(cosmo.kpc_proper_per_arcmin(z).to(u.kpc / u.arcsec).value)


def _parse_centers(center_args: list[str], label_args: list[str]) -> list[Center]:
    if not center_args:
        return []
    if label_args and len(label_args) != len(center_args):
        raise ValueError("--center-label must be provided the same number of times as --center-icrs")

    centers: list[Center] = []
    for i, s in enumerate(center_args):
        parts = [p.strip() for p in str(s).split(",")]
        if len(parts) != 2:
            raise ValueError("--center-icrs must be RA_DEG,DEC_DEG")
        ra = float(parts[0])
        dec = float(parts[1])
        label = label_args[i] if label_args else f"C{i+1}"
        centers.append(Center(label=label, ra_deg=ra, dec_deg=dec))
    return centers


def _bilinear_sample(img: np.ndarray, x: float, y: float) -> float:
    from scipy.ndimage import map_coordinates

    # map_coordinates uses (row=y, col=x)
    v = map_coordinates(img, [[y], [x]], order=1, mode="nearest")
    return float(v[0])


def _radial_profile(
    *,
    data: np.ndarray,
    gradmag: np.ndarray,
    wcs,
    center: Center,
    rmax_arcsec: float,
    dr_arcsec: float,
) -> list[dict[str, object]]:
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    sc = SkyCoord(center.ra_deg * u.deg, center.dec_deg * u.deg, frame="icrs")
    cx, cy = wcs.world_to_pixel(sc)
    if not (np.isfinite(cx) and np.isfinite(cy)):
        return []

    sx, sy = _pixel_scales_arcsec(wcs)
    # Use isotropic radial distance in arcsec with average scale.
    s = 0.5 * (sx + sy)

    ny, nx = data.shape
    yy, xx = np.mgrid[0:ny, 0:nx]
    rr_arcsec = np.sqrt((xx - float(cx)) ** 2 + (yy - float(cy)) ** 2) * s

    rows: list[dict[str, object]] = []
    nb = int(max(1, math.floor(float(rmax_arcsec) / float(dr_arcsec))))
    for i in range(nb):
        r0 = i * float(dr_arcsec)
        r1 = (i + 1) * float(dr_arcsec)
        m = (rr_arcsec >= r0) & (rr_arcsec < r1) & np.isfinite(data) & np.isfinite(gradmag)
        if not m.any():
            continue
        rows.append(
            {
                "center": center.label,
                "r_mid_arcsec": 0.5 * (r0 + r1),
                "kappa_median": float(np.nanmedian(data[m])),
                "kappa_p16": float(np.nanpercentile(data[m], 16)),
                "kappa_p84": float(np.nanpercentile(data[m], 84)),
                "gradmag_median_per_arcsec": float(np.nanmedian(gradmag[m])),
                "gradmag_p16_per_arcsec": float(np.nanpercentile(gradmag[m], 16)),
                "gradmag_p84_per_arcsec": float(np.nanpercentile(gradmag[m], 84)),
                "n_pix": int(np.sum(m)),
            }
        )
    return rows


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
    ap.add_argument("--map", type=Path, required=True, help="Input FITS scalar map (e.g., κ).")
    ap.add_argument("--smooth-arcsec", type=float, default=0.0)

    ap.add_argument(
        "--roi-center-icrs",
        type=str,
        default="",
        help="Optional ROI center as 'RA_DEG,DEC_DEG'. If omitted and centers are provided, uses the first center.",
    )
    ap.add_argument(
        "--roi-radius-arcsec",
        type=float,
        default=float("nan"),
        help="Optional ROI radius in arcsec. If omitted, uses ~profile_rmax+100 arcsec when profiling.",
    )

    ap.add_argument("--out-grad", type=Path, default=Path("toy_models/out_gradients/gradmag.fits"))
    ap.add_argument("--out-dkx", type=Path, default=None, help="Optional output FITS for ∂map/∂x.")
    ap.add_argument("--out-dky", type=Path, default=None, help="Optional output FITS for ∂map/∂y.")

    ap.add_argument("--z", type=float, default=float("nan"), help="Optional lens redshift for per-kpc scaling.")
    ap.add_argument("--H0", type=float, default=70.0)
    ap.add_argument("--Om0", type=float, default=0.3)

    ap.add_argument("--center-icrs", type=str, action="append", default=[])
    ap.add_argument("--center-label", type=str, action="append", default=[])
    ap.add_argument("--profile-rmax-arcsec", type=float, default=0.0)
    ap.add_argument("--profile-dr-arcsec", type=float, default=0.0)
    ap.add_argument("--out-profile", type=Path, default=None)

    args = ap.parse_args()

    from astropy.coordinates import SkyCoord
    import astropy.units as u

    data, header, wcs = _read_fits(args.map)

    centers = _parse_centers(args.center_icrs, args.center_label)

    roi_center = None
    if args.roi_center_icrs:
        parts = [p.strip() for p in str(args.roi_center_icrs).split(",")]
        if len(parts) != 2:
            raise SystemExit("--roi-center-icrs must be RA_DEG,DEC_DEG")
        roi_center = SkyCoord(float(parts[0]) * u.deg, float(parts[1]) * u.deg, frame="icrs")
    elif centers:
        roi_center = SkyCoord(centers[0].ra_deg * u.deg, centers[0].dec_deg * u.deg, frame="icrs")

    roi_radius = float(args.roi_radius_arcsec)
    if not (np.isfinite(roi_radius) and roi_radius > 0):
        if float(args.profile_rmax_arcsec) > 0:
            roi_radius = float(args.profile_rmax_arcsec) + 100.0
        else:
            roi_radius = float("nan")

    origin = (0, 0)
    if roi_center is not None and np.isfinite(roi_radius) and roi_radius > 0:
        data, origin = _roi_crop(data=data, wcs=wcs, center_icrs=roi_center, radius_arcsec=roi_radius)
        header = _shift_header_for_crop(header, origin_yx=origin)
        from astropy.wcs import WCS

        wcs = WCS(header)

    data_s = _smooth_gaussian_arcsec(data, wcs, float(args.smooth_arcsec))

    dk_dx, dk_dy, gradmag = _gradients_per_arcsec(data_s, wcs)

    # Optional physical scaling
    unit = "1/arcsec"
    if np.isfinite(float(args.z)) and float(args.z) > 0:
        kpa = _kpc_per_arcsec(float(args.z), H0=float(args.H0), Om0=float(args.Om0))
        dk_dx = dk_dx * kpa
        dk_dy = dk_dy * kpa
        gradmag = gradmag * kpa
        unit = "1/kpc"
        header = header.copy()
        header["KPC_ARC"] = float(kpa)

    _write_fits_like(args.out_grad, data=gradmag, header=header, bunit=unit)
    if args.out_dkx is not None:
        _write_fits_like(Path(args.out_dkx), data=dk_dx, header=header, bunit=unit)
    if args.out_dky is not None:
        _write_fits_like(Path(args.out_dky), data=dk_dy, header=header, bunit=unit)

    profile_rows: list[dict[str, object]] = []
    if centers and args.out_profile is not None and float(args.profile_rmax_arcsec) > 0 and float(args.profile_dr_arcsec) > 0:
        for c in centers:
            # Also report gradient magnitude at the exact center (bilinear sample)
            from astropy.coordinates import SkyCoord
            import astropy.units as u

            sc = SkyCoord(c.ra_deg * u.deg, c.dec_deg * u.deg, frame="icrs")
            cx, cy = wcs.world_to_pixel(sc)
            if np.isfinite(cx) and np.isfinite(cy):
                profile_rows.append(
                    {
                        "row_type": "center_sample",
                        "center": c.label,
                        "ra_deg": c.ra_deg,
                        "dec_deg": c.dec_deg,
                        "kappa": _bilinear_sample(data_s, float(cx), float(cy)),
                        f"gradmag_{unit}": _bilinear_sample(gradmag, float(cx), float(cy)),
                    }
                )

            for r in _radial_profile(
                data=data_s,
                gradmag=gradmag,
                wcs=wcs,
                center=c,
                rmax_arcsec=float(args.profile_rmax_arcsec),
                dr_arcsec=float(args.profile_dr_arcsec),
            ):
                r["row_type"] = "annulus"
                r["unit"] = unit
                profile_rows.append(r)

        _write_csv(Path(args.out_profile), profile_rows)

    print(f"Read: {args.map}")
    print(f"Smoothing sigma: {float(args.smooth_arcsec):g} arcsec")
    print(f"Gradient units: {unit}")
    print(f"Wrote grad magnitude: {args.out_grad.resolve()}")
    if args.out_profile is not None and profile_rows:
        print(f"Wrote profile: {Path(args.out_profile).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
