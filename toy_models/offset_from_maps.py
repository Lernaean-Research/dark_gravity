"""Compute 2D peak/centroid offsets between two FITS maps using WCS.

Primary use case: Bullet Cluster
- Map A: lensing convergence (kappa) map (DM proxy)
- Map B: gas proxy map (e.g., xray_kappa from the lens model, or an observed X-ray image)

This script does not require the maps to be on the same pixel grid; it converts
peak/centroid pixel coordinates into sky coordinates via WCS and computes
angular separations.

Examples
--------
# Best-fit DM (kappa) vs gas-component (xray_kappa):
./.venv/Scripts/python.exe toy_models/offset_from_maps.py \
  --map-a toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  --map-b toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/xray_kappa_dsdls1.fits \
  --n-peaks 2 --bin-a 8 --bin-b 1 --exclusion-arcsec 25 --centroid-radius-arcsec 15 \
  --out-csv toy_models/out_offsets/canucs_bestfit_dm_vs_gas.csv

# Add uncertainty from Bayesian kappa samples (200 mas):
./.venv/Scripts/python.exe toy_models/offset_from_maps.py \
  --map-a toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  --map-b toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/xray_kappa_dsdls1.fits \
  --a-samples-glob "toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/sample_model/sample_maps/bulletclu-kappa-200mas_*.fits" \
  --n-peaks 2 --bin-a 8 --bin-b 1 --exclusion-arcsec 25 --centroid-radius-arcsec 15 \
  --out-csv toy_models/out_offsets/canucs_bestfit_plus_samples_dm_vs_gas.csv
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class PeakResult:
    label: str
    peak_x: float
    peak_y: float
    peak_val: float
    peak_ra_deg: float
    peak_dec_deg: float
    centroid_x: float
    centroid_y: float
    centroid_ra_deg: float
    centroid_dec_deg: float


def _write_rows_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    # Rows may be heterogeneous (different row_type => different columns).
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
            # Fill missing keys with blanks for CSV.
            w.writerow({k: r.get(k, "") for k in keys})


def _nan_sanitize(data: np.ndarray) -> np.ndarray:
    d = np.array(data, copy=True)
    if not np.isfinite(d).any():
        raise ValueError("No finite values in map")
    # Replace non-finite with a very low floor so argmax ignores them.
    finite = d[np.isfinite(d)]
    floor = np.nanmin(finite)
    d[~np.isfinite(d)] = floor
    return d


def _downsample_mean(d: np.ndarray, factor: int) -> np.ndarray:
    if factor <= 1:
        return d
    ny, nx = d.shape
    ny2 = (ny // factor) * factor
    nx2 = (nx // factor) * factor
    if ny2 <= 0 or nx2 <= 0:
        raise ValueError(f"Cannot downsample shape={d.shape} by factor={factor}")
    trimmed = d[:ny2, :nx2]
    # block mean
    reshaped = trimmed.reshape(ny2 // factor, factor, nx2 // factor, factor)
    return reshaped.mean(axis=(1, 3))


def _pixel_scales_arcsec(wcs) -> tuple[float, float]:
    from astropy.wcs.utils import proj_plane_pixel_scales

    sc = proj_plane_pixel_scales(wcs)  # degrees/pixel
    sx = float(sc[0] * 3600)
    sy = float(sc[1] * 3600)
    return (abs(sx), abs(sy))


def _find_peaks_and_centroids(
    *,
    label_prefix: str,
    data: np.ndarray,
    wcs,
    n_peaks: int,
    bin_factor: int,
    exclusion_arcsec: float,
    refine_arcsec: float,
    centroid_radius_arcsec: float,
) -> list[PeakResult]:
    d0 = _nan_sanitize(data)

    # Working image for peak-finding.
    work = _downsample_mean(d0, bin_factor)

    sx, sy = _pixel_scales_arcsec(wcs)
    sx_work = sx * bin_factor
    sy_work = sy * bin_factor

    excl_x = max(1, int(round(exclusion_arcsec / sx_work)))
    excl_y = max(1, int(round(exclusion_arcsec / sy_work)))

    results: list[PeakResult] = []
    work2 = work.copy()

    for i in range(n_peaks):
        flat_idx = int(np.nanargmax(work2))
        wy, wx = np.unravel_index(flat_idx, work2.shape)
        peak_val_work = float(work2[wy, wx])

        # Refine on original grid around the binned peak position.
        ox = int(wx * bin_factor + bin_factor / 2)
        oy = int(wy * bin_factor + bin_factor / 2)

        refine_x = max(2, int(round(refine_arcsec / sx)))
        refine_y = max(2, int(round(refine_arcsec / sy)))

        y0 = max(0, oy - refine_y)
        y1 = min(d0.shape[0], oy + refine_y + 1)
        x0 = max(0, ox - refine_x)
        x1 = min(d0.shape[1], ox + refine_x + 1)

        cut = d0[y0:y1, x0:x1]
        local_idx = int(np.nanargmax(cut))
        ly, lx = np.unravel_index(local_idx, cut.shape)
        py = float(y0 + ly)
        px = float(x0 + lx)
        peak_val = float(d0[int(py), int(px)])

        # Centroid within a radius around refined peak.
        crad_x = max(2, int(round(centroid_radius_arcsec / sx)))
        crad_y = max(2, int(round(centroid_radius_arcsec / sy)))
        cy0 = max(0, int(py) - crad_y)
        cy1 = min(d0.shape[0], int(py) + crad_y + 1)
        cx0 = max(0, int(px) - crad_x)
        cx1 = min(d0.shape[1], int(px) + crad_x + 1)
        ccut = d0[cy0:cy1, cx0:cx1]

        yy, xx = np.mgrid[cy0:cy1, cx0:cx1]
        rr2 = ((xx - px) / crad_x) ** 2 + ((yy - py) / crad_y) ** 2
        mask = rr2 <= 1.0

        vals = ccut[mask]
        # Weighted centroid: use positive weights above median to avoid negative artifacts.
        med = float(np.nanmedian(vals))
        wts = np.clip(vals - med, 0.0, None)
        if float(np.nansum(wts)) <= 0:
            # fallback: uniform weight in mask
            wts = np.ones_like(vals, dtype=float)

        cx = float(np.nansum(xx[mask] * wts) / np.nansum(wts))
        cy = float(np.nansum(yy[mask] * wts) / np.nansum(wts))

        # WCS -> sky
        from astropy.coordinates import SkyCoord

        pcoord = wcs.pixel_to_world(px, py)
        ccoord = wcs.pixel_to_world(cx, cy)

        def _to_deg(sc) -> tuple[float, float]:
            if isinstance(sc, SkyCoord):
                return (float(sc.ra.deg), float(sc.dec.deg))
            # Fallback if pixel_to_world returns tuple-like
            try:
                return (float(sc[0].deg), float(sc[1].deg))
            except Exception:
                return (float(getattr(sc, "ra").deg), float(getattr(sc, "dec").deg))

        pra, pdec = _to_deg(pcoord)
        cra, cdec = _to_deg(ccoord)

        results.append(
            PeakResult(
                label=f"{label_prefix}{i+1}",
                peak_x=px,
                peak_y=py,
                peak_val=peak_val,
                peak_ra_deg=pra,
                peak_dec_deg=pdec,
                centroid_x=cx,
                centroid_y=cy,
                centroid_ra_deg=cra,
                centroid_dec_deg=cdec,
            )
        )

        # Exclude this peak region from working image.
        y_min = max(0, wy - excl_y)
        y_max = min(work2.shape[0], wy + excl_y + 1)
        x_min = max(0, wx - excl_x)
        x_max = min(work2.shape[1], wx + excl_x + 1)
        work2[y_min:y_max, x_min:x_max] = -np.inf

        # Safety: if the map is effectively flat
        if not np.isfinite(work2).any():
            break
        _ = peak_val_work  # keep for potential debugging

    return results


def _match_pairs_by_min_total_sep(a_coords, b_coords):
    """Return list of (a_index, b_index, sep_arcsec) minimizing total separation."""
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    n = min(len(a_coords), len(b_coords))
    if n == 0:
        return []

    best = None
    best_cost = float("inf")

    for perm in permutations(range(len(b_coords)), n):
        cost = 0.0
        pairs = []
        for i, j in enumerate(perm):
            sep = SkyCoord(a_coords[i]).separation(SkyCoord(b_coords[j])).to(u.arcsec).value
            cost += float(sep)
            pairs.append((i, j, float(sep)))
        if cost < best_cost:
            best_cost = cost
            best = pairs

    return best or []


def _local_peak_near_anchor(
    *,
    data: np.ndarray,
    wcs,
    anchor_coord,
    search_arcsec: float,
    refine_arcsec: float,
) -> tuple[float, float, float]:
    """Find a local maximum near an anchor sky coordinate.

    Returns (ra_deg, dec_deg, peak_val).
    """
    d0 = _nan_sanitize(data)
    sx, sy = _pixel_scales_arcsec(wcs)
    # Convert anchor world->pixel
    ax, ay = wcs.world_to_pixel(anchor_coord)
    if not (np.isfinite(ax) and np.isfinite(ay)):
        raise ValueError("Anchor world_to_pixel returned non-finite")

    rad_x = max(2, int(round(search_arcsec / sx)))
    rad_y = max(2, int(round(search_arcsec / sy)))
    cx = int(round(float(ax)))
    cy = int(round(float(ay)))

    y0 = max(0, cy - rad_y)
    y1 = min(d0.shape[0], cy + rad_y + 1)
    x0 = max(0, cx - rad_x)
    x1 = min(d0.shape[1], cx + rad_x + 1)
    if y1 <= y0 or x1 <= x0:
        raise ValueError("Anchor search window is empty")

    cut = d0[y0:y1, x0:x1]
    local_idx = int(np.nanargmax(cut))
    ly, lx = np.unravel_index(local_idx, cut.shape)
    py = float(y0 + ly)
    px = float(x0 + lx)

    # Optional refinement around the found local peak on original grid.
    refine_x = max(2, int(round(refine_arcsec / sx)))
    refine_y = max(2, int(round(refine_arcsec / sy)))
    ry0 = max(0, int(py) - refine_y)
    ry1 = min(d0.shape[0], int(py) + refine_y + 1)
    rx0 = max(0, int(px) - refine_x)
    rx1 = min(d0.shape[1], int(px) + refine_x + 1)
    rcut = d0[ry0:ry1, rx0:rx1]
    ridx = int(np.nanargmax(rcut))
    rly, rlx = np.unravel_index(ridx, rcut.shape)
    rpy = float(ry0 + rly)
    rpx = float(rx0 + rlx)

    peak_val = float(d0[int(rpy), int(rpx)])

    from astropy.coordinates import SkyCoord

    pcoord = wcs.pixel_to_world(rpx, rpy)
    if isinstance(pcoord, SkyCoord):
        return (float(pcoord.ra.deg), float(pcoord.dec.deg), peak_val)
    return (float(getattr(pcoord, "ra").deg), float(getattr(pcoord, "dec").deg), peak_val)


def _peak_and_centroid_near_anchor(
    *,
    label: str,
    data: np.ndarray,
    wcs,
    anchor_coord,
    search_arcsec: float,
    refine_arcsec: float,
    centroid_radius_arcsec: float,
) -> PeakResult:
    """Find a local peak and centroid near an anchor sky coordinate."""

    from astropy.coordinates import SkyCoord

    d0 = _nan_sanitize(data)
    sx, sy = _pixel_scales_arcsec(wcs)

    ax, ay = wcs.world_to_pixel(anchor_coord)
    if not (np.isfinite(ax) and np.isfinite(ay)):
        raise ValueError("Anchor world_to_pixel returned non-finite")

    rad_x = max(2, int(round(search_arcsec / sx)))
    rad_y = max(2, int(round(search_arcsec / sy)))
    cx = int(round(float(ax)))
    cy = int(round(float(ay)))

    y0 = max(0, cy - rad_y)
    y1 = min(d0.shape[0], cy + rad_y + 1)
    x0 = max(0, cx - rad_x)
    x1 = min(d0.shape[1], cx + rad_x + 1)
    if y1 <= y0 or x1 <= x0:
        raise ValueError("Anchor search window is empty")

    cut = d0[y0:y1, x0:x1]
    local_idx = int(np.nanargmax(cut))
    ly, lx = np.unravel_index(local_idx, cut.shape)
    py = float(y0 + ly)
    px = float(x0 + lx)

    refine_x = max(2, int(round(refine_arcsec / sx)))
    refine_y = max(2, int(round(refine_arcsec / sy)))
    ry0 = max(0, int(py) - refine_y)
    ry1 = min(d0.shape[0], int(py) + refine_y + 1)
    rx0 = max(0, int(px) - refine_x)
    rx1 = min(d0.shape[1], int(px) + refine_x + 1)
    rcut = d0[ry0:ry1, rx0:rx1]
    ridx = int(np.nanargmax(rcut))
    rly, rlx = np.unravel_index(ridx, rcut.shape)
    rpy = float(ry0 + rly)
    rpx = float(rx0 + rlx)

    peak_val = float(d0[int(rpy), int(rpx)])

    crad_x = max(2, int(round(centroid_radius_arcsec / sx)))
    crad_y = max(2, int(round(centroid_radius_arcsec / sy)))
    cy0 = max(0, int(rpy) - crad_y)
    cy1 = min(d0.shape[0], int(rpy) + crad_y + 1)
    cx0 = max(0, int(rpx) - crad_x)
    cx1 = min(d0.shape[1], int(rpx) + crad_x + 1)
    ccut = d0[cy0:cy1, cx0:cx1]

    yy, xx = np.mgrid[cy0:cy1, cx0:cx1]
    rr2 = ((xx - rpx) / crad_x) ** 2 + ((yy - rpy) / crad_y) ** 2
    mask = rr2 <= 1.0

    vals = ccut[mask]
    med = float(np.nanmedian(vals))
    wts = np.clip(vals - med, 0.0, None)
    if float(np.nansum(wts)) <= 0:
        wts = np.ones_like(vals, dtype=float)

    ccx = float(np.nansum(xx[mask] * wts) / np.nansum(wts))
    ccy = float(np.nansum(yy[mask] * wts) / np.nansum(wts))

    pcoord = wcs.pixel_to_world(rpx, rpy)
    ccoord = wcs.pixel_to_world(ccx, ccy)

    def _to_deg(sc) -> tuple[float, float]:
        if isinstance(sc, SkyCoord):
            return (float(sc.ra.deg), float(sc.dec.deg))
        try:
            return (float(sc[0].deg), float(sc[1].deg))
        except Exception:
            return (float(getattr(sc, "ra").deg), float(getattr(sc, "dec").deg))

    pra, pdec = _to_deg(pcoord)
    cra, cdec = _to_deg(ccoord)

    return PeakResult(
        label=label,
        peak_x=float(rpx),
        peak_y=float(rpy),
        peak_val=float(peak_val),
        peak_ra_deg=float(pra),
        peak_dec_deg=float(pdec),
        centroid_x=float(ccx),
        centroid_y=float(ccy),
        centroid_ra_deg=float(cra),
        centroid_dec_deg=float(cdec),
    )


def _flatlcdm_angular_diameter_distance_mpc(z: float, h0: float, om0: float) -> float:
    """SciPy-free angular diameter distance for flat LCDM.

    Uses numerical integration of 1/E(z) with a fixed grid.
    """

    if not (z > 0):
        return 0.0

    c_km_s = 299_792.458
    ol0 = 1.0 - float(om0)
    z = float(z)
    h0 = float(h0)
    om0 = float(om0)

    n = 8192
    zz = np.linspace(0.0, z, n, dtype=float)
    ez = np.sqrt(om0 * (1.0 + zz) ** 3 + ol0)
    inv_e = 1.0 / ez
    integral = float(np.trapezoid(inv_e, zz))
    d_c_mpc = (c_km_s / h0) * integral
    return d_c_mpc / (1.0 + z)


def _arcsec_to_kpc(arcsec: float, z_lens: float, h0: float, om0: float) -> float:
    """Convert angular separation to proper kpc.

    Notes
    -----
    Some astropy cosmology paths rely on SciPy (e.g. `scipy.special`). If SciPy
    isn't installed in the current environment, we return NaN and keep the
    arcsec separation as the primary output.
    """

    try:
        from astropy.cosmology import FlatLambdaCDM
        import astropy.units as u

        cosmo = FlatLambdaCDM(H0=h0 * u.km / u.s / u.Mpc, Om0=om0)
        kpc_per_arcsec = cosmo.kpc_proper_per_arcmin(z_lens).to(u.kpc / u.arcsec).value
        return float(arcsec * kpc_per_arcsec)
    except ModuleNotFoundError:
        # Fall back to a SciPy-free numerical integration.
        d_a_mpc = _flatlcdm_angular_diameter_distance_mpc(float(z_lens), float(h0), float(om0))
        rad_per_arcsec = math.pi / (180.0 * 3600.0)
        return float(arcsec * (d_a_mpc * 1.0e3) * rad_per_arcsec)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map-a", type=Path, required=True)
    ap.add_argument("--map-b", type=Path, required=True)
    ap.add_argument("--n-peaks", type=int, default=2)

    ap.add_argument(
        "--anchor-icrs",
        action="append",
        default=[],
        metavar="RA_DEG,DEC_DEG",
        help=(
            "Fixed anchor coordinate (ICRS degrees) to lock peak identity. Repeat to provide multiple anchors. "
            "Example: --anchor-icrs 104.6587,-55.9572 --anchor-icrs 104.6777,-55.9765"
        ),
    )
    ap.add_argument(
        "--anchor-label",
        action="append",
        default=[],
        metavar="LABEL",
        help="Optional label for each --anchor-icrs (repeat in the same order).",
    )
    ap.add_argument(
        "--anchor-search-arcsec",
        type=float,
        default=30.0,
        help="Search radius around each anchor for map A when using fixed-anchor mode.",
    )
    ap.add_argument(
        "--anchor-search-arcsec-b",
        type=float,
        default=float("nan"),
        help=(
            "Optional search radius around each anchor for map B (defaults to --anchor-search-arcsec). "
            "Useful when A should be tightly locked but B is lower-resolution or more offset."
        ),
    )

    ap.add_argument("--bin-a", type=int, default=8, help="Downsample factor for peak-finding on map A.")
    ap.add_argument("--bin-b", type=int, default=1, help="Downsample factor for peak-finding on map B.")
    ap.add_argument("--exclusion-arcsec", type=float, default=25.0, help="Exclude radius around found peaks.")
    ap.add_argument("--refine-arcsec", type=float, default=10.0, help="Refinement search radius on original grid.")
    ap.add_argument("--centroid-radius-arcsec", type=float, default=15.0, help="Centroid radius around peak.")

    ap.add_argument(
        "--a-samples-glob",
        type=str,
        default="",
        help="Glob for Bayesian sample maps for map A (e.g. '*kappa-200mas_*.fits').",
    )
    ap.add_argument(
        "--sample-search-arcsec",
        type=float,
        default=15.0,
        help=(
            "For Bayesian sample maps, search for each peak locally within this radius around the best-fit peak. "
            "If set too large, the local maximum can jump to a different feature (peak-switching)."
        ),
    )

    ap.add_argument("--z-lens", type=float, default=0.296)
    ap.add_argument("--h0", type=float, default=70.0)
    ap.add_argument("--om0", type=float, default=0.3)

    ap.add_argument("--out-csv", type=Path, default=Path("toy_models/out_offsets/offsets.csv"))

    args = ap.parse_args()

    import astropy.units as u
    from astropy.coordinates import SkyCoord
    from astropy.io import fits
    from astropy.wcs import WCS

    def load_map(path: Path):
        with fits.open(path) as hdul:
            data = hdul[0].data
            wcs = WCS(hdul[0].header)
        if data is None or data.ndim != 2:
            raise ValueError(f"Expected 2D image in {path}")
        return np.asarray(data, dtype=float), wcs

    a_data, a_wcs = load_map(args.map_a)
    b_data, b_wcs = load_map(args.map_b)

    use_anchors = bool(args.anchor_icrs)
    if use_anchors:
        anchors: list[SkyCoord] = []
        for s in args.anchor_icrs:
            parts = [p.strip() for p in str(s).split(",")]
            if len(parts) != 2:
                raise SystemExit(f"Invalid --anchor-icrs '{s}'. Expected RA_DEG,DEC_DEG")
            ra = float(parts[0])
            dec = float(parts[1])
            anchors.append(SkyCoord(ra * u.deg, dec * u.deg, frame="icrs"))

        labels: list[str] = []
        if args.anchor_label:
            if len(args.anchor_label) != len(anchors):
                raise SystemExit("If provided, number of --anchor-label must match number of --anchor-icrs")
            labels = [str(x) for x in args.anchor_label]
        else:
            labels = [f"P{i+1}" for i in range(len(anchors))]

        a_search = float(args.anchor_search_arcsec)
        b_search = float(args.anchor_search_arcsec_b)
        if not np.isfinite(b_search):
            b_search = a_search

        a_peaks = [
            _peak_and_centroid_near_anchor(
                label=f"A_{lab}",
                data=a_data,
                wcs=a_wcs,
                anchor_coord=anc,
                search_arcsec=a_search,
                refine_arcsec=float(args.refine_arcsec),
                centroid_radius_arcsec=float(args.centroid_radius_arcsec),
            )
            for lab, anc in zip(labels, anchors, strict=True)
        ]
        b_peaks = [
            _peak_and_centroid_near_anchor(
                label=f"B_{lab}",
                data=b_data,
                wcs=b_wcs,
                anchor_coord=anc,
                search_arcsec=b_search,
                refine_arcsec=float(args.refine_arcsec),
                centroid_radius_arcsec=float(args.centroid_radius_arcsec),
            )
            for lab, anc in zip(labels, anchors, strict=True)
        ]
    else:
        a_peaks = _find_peaks_and_centroids(
            label_prefix="A",
            data=a_data,
            wcs=a_wcs,
            n_peaks=int(args.n_peaks),
            bin_factor=int(args.bin_a),
            exclusion_arcsec=float(args.exclusion_arcsec),
            refine_arcsec=float(args.refine_arcsec),
            centroid_radius_arcsec=float(args.centroid_radius_arcsec),
        )
        b_peaks = _find_peaks_and_centroids(
            label_prefix="B",
            data=b_data,
            wcs=b_wcs,
            n_peaks=int(args.n_peaks),
            bin_factor=int(args.bin_b),
            exclusion_arcsec=float(args.exclusion_arcsec),
            refine_arcsec=float(args.refine_arcsec),
            centroid_radius_arcsec=float(args.centroid_radius_arcsec),
        )

    # Prepare peak coordinate pairs
    a_peak_coords = [SkyCoord(p.peak_ra_deg * u.deg, p.peak_dec_deg * u.deg, frame="icrs") for p in a_peaks]
    b_peak_coords = [SkyCoord(p.peak_ra_deg * u.deg, p.peak_dec_deg * u.deg, frame="icrs") for p in b_peaks]

    if use_anchors:
        # In fixed-anchor mode, pair by construction (same index).
        pairs = [(i, i, float(a_peak_coords[i].separation(b_peak_coords[i]).to(u.arcsec).value)) for i in range(min(len(a_peak_coords), len(b_peak_coords)))]
    else:
        pairs = _match_pairs_by_min_total_sep(a_peak_coords, b_peak_coords)

    rows: list[dict[str, object]] = []

    # Record peak and centroid info
    for p in a_peaks + b_peaks:
        rows.append(
            {
                "row_type": "peak",
                "map": p.label[0],
                "label": p.label,
                "peak_ra_deg": p.peak_ra_deg,
                "peak_dec_deg": p.peak_dec_deg,
                "centroid_ra_deg": p.centroid_ra_deg,
                "centroid_dec_deg": p.centroid_dec_deg,
                "peak_val": p.peak_val,
            }
        )

    for ai, bi, sep_arcsec in pairs:
        sep_kpc = _arcsec_to_kpc(float(sep_arcsec), float(args.z_lens), float(args.h0), float(args.om0))
        rows.append(
            {
                "row_type": "pair_peak",
                "a_label": a_peaks[ai].label,
                "b_label": b_peaks[bi].label,
                "sep_arcsec": float(sep_arcsec),
                "sep_kpc": float(sep_kpc),
            }
        )

    # Optional: sample uncertainty on A peaks
    if args.a_samples_glob:
        import glob

        sample_paths = [Path(p) for p in sorted(glob.glob(args.a_samples_glob))]
        if sample_paths:
            # Use best-fit A peaks as anchors (already fixed in fixed-anchor mode).
            anchor_coords = a_peak_coords
            for sp in sample_paths:
                s_data, s_wcs = load_map(sp)
                for ai, anchor in enumerate(anchor_coords):
                    try:
                        ra, dec, pval = _local_peak_near_anchor(
                            data=s_data,
                            wcs=s_wcs,
                            anchor_coord=anchor,
                            search_arcsec=float(args.sample_search_arcsec),
                            refine_arcsec=float(args.refine_arcsec),
                        )
                        scoord = SkyCoord(ra * u.deg, dec * u.deg, frame="icrs")
                        sep_arcsec = float(anchor.separation(scoord).to(u.arcsec).value)
                        rows.append(
                            {
                                "row_type": "a_sample_peak",
                                "sample_file": sp.as_posix(),
                                "anchor_label": a_peaks[ai].label,
                                "sample_peak_ra_deg": float(ra),
                                "sample_peak_dec_deg": float(dec),
                                "sample_peak_val": float(pval),
                                "sep_arcsec": float(sep_arcsec),
                            }
                        )
                    except Exception as e:
                        rows.append(
                            {
                                "row_type": "a_sample_peak",
                                "sample_file": sp.as_posix(),
                                "anchor_label": a_peaks[ai].label,
                                "status": f"FAILED: {type(e).__name__}: {e}",
                            }
                        )
        else:
            rows.append({"row_type": "note", "message": "No sample maps matched a-samples-glob"})

    _write_rows_csv(Path(args.out_csv), rows)

    # Print compact summary
    print(f"A peaks: {len(a_peaks)} | B peaks: {len(b_peaks)}")
    for r in rows:
        if r.get("row_type") == "pair_peak":
            print(f"{r['a_label']} vs {r['b_label']}: {r['sep_arcsec']:.2f} arcsec ({r['sep_kpc']:.2f} kpc)")

    if args.a_samples_glob:
        by_anchor: dict[str, list[float]] = {}
        for r in rows:
            if r.get("row_type") != "a_sample_peak":
                continue
            if r.get("status"):
                continue
            lab = str(r.get("anchor_label") or "")
            try:
                sep = float(r.get("sep_arcsec"))
            except (TypeError, ValueError):
                continue
            by_anchor.setdefault(lab, []).append(sep)

        if by_anchor:
            print("Sample peak scatter vs best-fit (arcsec):")
            for lab in sorted(by_anchor.keys()):
                vals = np.array(by_anchor[lab], dtype=float)
                if vals.size == 0:
                    continue
                q16, q50, q84 = np.nanpercentile(vals, [16, 50, 84])
                mean = float(np.nanmean(vals))
                sd = float(np.nanstd(vals, ddof=1)) if vals.size > 1 else float("nan")
                print(
                    f"  {lab}: n={vals.size} mean={mean:.3f} sd={sd:.3f} "
                    f"16/50/84={q16:.3f}/{q50:.3f}/{q84:.3f}"
                )

    print(f"Wrote: {Path(args.out_csv).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
