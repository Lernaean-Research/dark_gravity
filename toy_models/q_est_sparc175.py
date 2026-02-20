"""Compute a robust outer velocity-deficit estimator Q_est for SPARC galaxies.

Q_est is defined as a robust location (Huber M-estimator) of

    Δ(R) = V_obs(R)^2 - V_bar(R)^2

computed over an "outer" region.

This script is intentionally dependency-light (NumPy + optional pandas).
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

import numpy as np


@dataclass(frozen=True)
class OuterSelection:
    rule: Literal["rfrac", "lastfrac"]
    n_total: int
    n_outer: int
    rmax_kpc: float
    rmin_outer_kpc: float


def _as_float_array(values: Iterable[object]) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    return arr


def huber_location(
    x: np.ndarray,
    *,
    c: float = 1.345,
    max_iter: int = 50,
    tol: float = 1e-6,
) -> tuple[float, float]:
    """Return (mu, scale) using a simple Huber location estimate.

    - mu is found by iterative reweighted least squares.
    - scale is fixed to a robust MAD estimate (returned for diagnostics).

    This is meant to be stable and reproducible, not a perfect clone of
    statsmodels' internal routines.
    """

    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]

    if x.size == 0:
        return (math.nan, math.nan)

    mu = float(np.median(x))
    mad = float(np.median(np.abs(x - mu)))
    if mad == 0.0:
        return (mu, 0.0)

    scale = 1.4826 * mad
    if scale == 0.0:
        return (mu, 0.0)

    for _ in range(max_iter):
        r = (x - mu) / scale
        a = np.abs(r)
        w = np.ones_like(x)
        mask = a > c
        w[mask] = c / a[mask]
        mu_new = float(np.sum(w * x) / np.sum(w))

        if abs(mu_new - mu) <= tol * scale:
            mu = mu_new
            break
        mu = mu_new

    return (mu, float(scale))


def select_outer_region(
    r_kpc: np.ndarray,
    *,
    outer_last_frac: float = 0.40,
    outer_rfrac: float = 0.60,
    min_points: int = 5,
) -> tuple[np.ndarray, OuterSelection]:
    """Select an "outer" subset by either radius-fraction or last-fraction.

    Primary rule: use all points with r >= outer_rfrac * r_max.
    Fallback rule: if that yields < min_points, use the last K points where
    K = max(min_points, ceil(outer_last_frac * N)).
    """

    r_kpc = np.asarray(r_kpc, dtype=float)
    r_kpc = r_kpc[np.isfinite(r_kpc)]

    n = int(r_kpc.size)
    if n == 0:
        return (np.zeros(0, dtype=bool), OuterSelection("lastfrac", 0, 0, math.nan, math.nan))

    rmax = float(np.max(r_kpc))

    mask_r = r_kpc >= (outer_rfrac * rmax)
    if int(np.sum(mask_r)) >= min_points:
        rmin_outer = float(np.min(r_kpc[mask_r]))
        return (
            mask_r,
            OuterSelection("rfrac", n, int(np.sum(mask_r)), rmax, rmin_outer),
        )

    k = max(min_points, int(math.ceil(outer_last_frac * n)))
    mask_last = np.zeros(n, dtype=bool)
    mask_last[-k:] = True
    rmin_outer = float(np.min(r_kpc[mask_last]))
    return (
        mask_last,
        OuterSelection("lastfrac", n, int(np.sum(mask_last)), rmax, rmin_outer),
    )


def _read_galaxy_csv(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Expected columns from toy_models/sparc_rotmod_runner.py outputs.
    # We deliberately avoid pandas here.
    r = []
    vobs = []
    vbar = []
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r.append(row.get("r_kpc"))
            vobs.append(row.get("vobs_kms"))
            vbar.append(row.get("vbar_kms"))

    r_kpc = _as_float_array(r)
    vobs_kms = _as_float_array(vobs)
    vbar_kms = _as_float_array(vbar)

    m = np.isfinite(r_kpc) & np.isfinite(vobs_kms) & np.isfinite(vbar_kms)
    r_kpc, vobs_kms, vbar_kms = r_kpc[m], vobs_kms[m], vbar_kms[m]

    order = np.argsort(r_kpc)
    return r_kpc[order], vobs_kms[order], vbar_kms[order]


def _read_rotmod_dat(path: Path, *, ups_disk: float = 0.5, ups_bul: float = 0.7) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Read a SPARC *_rotmod.dat file (whitespace-delimited; # comments allowed)."""

    data = np.genfromtxt(
        path,
        comments="#",
        dtype=float,
        invalid_raise=False,
    )

    if data.ndim == 1 and data.size == 0:
        return (np.array([]), np.array([]), np.array([]))

    # Columns by index (SPARC convention):
    # 0 Rad, 1 Vobs, 2 errV, 3 Vgas, 4 Vdisk, 5 Vbul
    r_kpc = data[:, 0]
    vobs_kms = data[:, 1]
    vgas_kms = data[:, 3]
    vdisk_kms = data[:, 4]
    vbul_kms = data[:, 5]

    vbar2 = vgas_kms**2 + ups_disk * (vdisk_kms**2) + ups_bul * (vbul_kms**2)
    vbar2 = np.maximum(vbar2, 0.0)
    vbar_kms = np.sqrt(vbar2)

    m = np.isfinite(r_kpc) & np.isfinite(vobs_kms) & np.isfinite(vbar_kms)
    r_kpc, vobs_kms, vbar_kms = r_kpc[m], vobs_kms[m], vbar_kms[m]

    order = np.argsort(r_kpc)
    return r_kpc[order], vobs_kms[order], vbar_kms[order]


def compute_q_est(
    *,
    r_kpc: np.ndarray,
    vobs_kms: np.ndarray,
    vbar_kms: np.ndarray,
    outer_last_frac: float = 0.40,
    outer_rfrac: float = 0.60,
    min_points: int = 5,
    huber_c: float = 1.345,
) -> tuple[float, float, OuterSelection]:
    """Compute Q_est (km/s)^2 and return (q_est, huber_scale, selection)."""

    delta = vobs_kms**2 - vbar_kms**2

    mask_outer, sel = select_outer_region(
        r_kpc,
        outer_last_frac=outer_last_frac,
        outer_rfrac=outer_rfrac,
        min_points=min_points,
    )

    if int(np.sum(mask_outer)) == 0:
        return (math.nan, math.nan, sel)

    q_est, scale = huber_location(delta[mask_outer], c=huber_c)
    return (q_est, scale, sel)


def _infer_galaxy_name(path: Path) -> str:
    name = path.stem
    if name.endswith("_rotmod"):
        name = name[: -len("_rotmod")]
    return name


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)

    src = p.add_mutually_exclusive_group(required=False)
    src.add_argument(
        "--galaxy-csv-dir",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/galaxies"),
        help="Directory of per-galaxy CSVs (expects columns r_kpc, vobs_kms, vbar_kms).",
    )
    src.add_argument(
        "--rotmod-dir",
        type=Path,
        help="Directory of SPARC *_rotmod.dat files.",
    )

    p.add_argument("--outer-last-frac", type=float, default=0.40)
    p.add_argument("--outer-rfrac", type=float, default=0.60)
    p.add_argument("--min-points", type=int, default=5)

    p.add_argument("--huber-c", type=float, default=1.345)

    p.add_argument("--ups-disk", type=float, default=0.5, help="Only used with --rotmod-dir")
    p.add_argument("--ups-bul", type=float, default=0.7, help="Only used with --rotmod-dir")

    p.add_argument(
        "--out-csv",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/q_est.csv"),
        help="Where to write the Q_est catalogue.",
    )
    p.add_argument(
        "--print-sample",
        action="store_true",
        help="Print Q_est for 6 representative galaxies (if present).",
    )

    args = p.parse_args()

    if args.rotmod_dir is not None:
        in_dir = args.rotmod_dir
        files = sorted(in_dir.glob("*_rotmod.dat"))
        reader_kind = "rotmod"
    else:
        in_dir = args.galaxy_csv_dir
        files = sorted(in_dir.glob("*.csv"))
        reader_kind = "galaxy_csv"

    rows = []
    for path in files:
        galaxy = _infer_galaxy_name(path)

        if reader_kind == "rotmod":
            r_kpc, vobs_kms, vbar_kms = _read_rotmod_dat(
                path,
                ups_disk=args.ups_disk,
                ups_bul=args.ups_bul,
            )
        else:
            r_kpc, vobs_kms, vbar_kms = _read_galaxy_csv(path)

        q_est, scale, sel = compute_q_est(
            r_kpc=r_kpc,
            vobs_kms=vobs_kms,
            vbar_kms=vbar_kms,
            outer_last_frac=args.outer_last_frac,
            outer_rfrac=args.outer_rfrac,
            min_points=args.min_points,
            huber_c=args.huber_c,
        )

        rows.append(
            {
                "galaxy": galaxy,
                "q_est_kms2": q_est,
                "huber_scale_kms2": scale,
                "outer_rule": sel.rule,
                "n_total": sel.n_total,
                "n_outer": sel.n_outer,
                "rmax_kpc": sel.rmax_kpc,
                "rmin_outer_kpc": sel.rmin_outer_kpc,
            }
        )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["galaxy"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    if args.print_sample:
        sample = ["UGCA444", "DDO154", "NGC6503", "NGC2841", "UGC09133", "ESO563-G021"]
        q_by_gal = {r["galaxy"]: r["q_est_kms2"] for r in rows}
        print("Representative sample (Q_est in (km/s)^2):")
        for g in sample:
            if g in q_by_gal:
                print(f"  {g:10s}  {q_by_gal[g]:12.2f}")
            else:
                print(f"  {g:10s}  (missing)")

    print(f"Wrote {len(rows)} rows to {args.out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
