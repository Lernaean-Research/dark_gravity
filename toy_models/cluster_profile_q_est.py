"""Compute a SPARC-style robust outer deficit estimator q_est from a *cluster* radial profile.

Why this exists
--------------
Our core SPARC workflow defines a robust outer statistic

    Delta v^2(r) = v_obs(r)^2 - v_bar(r)^2

and then estimates a single outer amplitude

    q_est = robust_location(Delta v^2 in outer region)

using the exact same Huber M-estimator and outer-region selection rules as
`toy_models/q_est_sparc175.py`.

For clusters, there is no rotation curve. But if you have *enclosed mass* profiles
(or effective circular-speed profiles) you can form an analogous Delta v^2(r):

    v_tot^2(r) = G M_tot(<r) / r
    v_bar^2(r) = G M_bar(<r) / r

and then feed (r, v_tot, v_bar) into the same q_est machinery.

Important caveats
-----------------
- Lensing typically constrains *projected* mass, not necessarily the true 3D
  enclosed mass needed for v_c(r). If you supply projected mass, the resulting
  v_tot(r) is only an *effective* diagnostic.
- The Bullet Cluster is a merging, non-spherical system. Any 1D radial profile
  necessarily throws away the key 2D offset information. This script is therefore
  best viewed as a "sanity-check" adapter, not a decisive Bullet-Cluster test.

Inputs
------
CSV with at least a radius column and either:
- velocities: `v_tot_kms` and `v_bar_kms` (preferred if you already computed them), OR
- masses: `M_tot_Msun` and `M_bar_Msun` (enclosed masses)

Radius columns supported:
- `r_kpc` (preferred)
- `r_mpc` (auto-converted to kpc)

Outputs
-------
Writes `q_est_cluster.csv` and `profile_with_dv2.csv` under `--out-dir/--name/`.

Example
-------
./.venv/Scripts/python.exe toy_models/cluster_profile_q_est.py \
  --in-csv toy_models/data/bullet_cluster/profile_template.csv \
  --name bullet_cluster \
  --out-dir toy_models/out_cluster_profiles
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

# Ensure we can import the shared robust q_est implementation when this file is
# executed as a script from the workspace root.
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from toy_models.q_est_sparc175 import compute_q_est  # noqa: E402

# Gravitational constant in units convenient for kpc, Msun, km/s:
#   G = 4.30091e-6  (kpc / Msun) * (km/s)^2
_G_KPC_KMS2_PER_MSUN = 4.30091e-6


def _to_float(x: object) -> float:
    try:
        if x is None:
            return math.nan
        s = str(x).strip()
        if s == "" or s.lower() in {"nan", "none"}:
            return math.nan
        return float(s)
    except Exception:
        return math.nan


def _read_profile(path: Path) -> dict[str, np.ndarray]:
    # Support hand-edited CSVs that contain comment lines.
    with path.open("r", newline="", encoding="utf-8") as f:
        lines = [ln for ln in f if ln.strip() and not ln.lstrip().startswith("#")]
        reader = csv.DictReader(lines)
        rows = list(reader)

    if not rows:
        raise ValueError("Input CSV has no data rows (template file?).")

    cols: dict[str, list[float]] = {}
    for row in rows:
        for k, v in row.items():
            if k is None:
                continue
            cols.setdefault(k, []).append(_to_float(v))

    return {k: np.asarray(v, dtype=float) for k, v in cols.items()}


def _pick_radius_kpc(data: dict[str, np.ndarray]) -> np.ndarray:
    if "r_kpc" in data:
        r = data["r_kpc"]
        return r
    if "r_mpc" in data:
        return 1000.0 * data["r_mpc"]
    raise ValueError("Input CSV must contain r_kpc or r_mpc")


def _compute_velocities(data: dict[str, np.ndarray], r_kpc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if "v_tot_kms" in data and "v_bar_kms" in data:
        return (data["v_tot_kms"], data["v_bar_kms"])

    if "M_tot_Msun" in data and "M_bar_Msun" in data:
        m_tot = data["M_tot_Msun"]
        m_bar = data["M_bar_Msun"]

        # v^2 = G M / r
        vtot2 = _G_KPC_KMS2_PER_MSUN * m_tot / r_kpc
        vbar2 = _G_KPC_KMS2_PER_MSUN * m_bar / r_kpc

        vtot2 = np.where(np.isfinite(vtot2) & (vtot2 >= 0.0), vtot2, np.nan)
        vbar2 = np.where(np.isfinite(vbar2) & (vbar2 >= 0.0), vbar2, np.nan)

        return (np.sqrt(vtot2), np.sqrt(vbar2))

    raise ValueError("Input CSV must have either (v_tot_kms,v_bar_kms) or (M_tot_Msun,M_bar_Msun)")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("No rows to write")

    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in-csv", type=Path, required=True)
    p.add_argument("--name", type=str, default="")
    p.add_argument("--out-dir", type=Path, default=Path("toy_models/out_cluster_profiles"))

    # Keep defaults identical to SPARC q_est.
    p.add_argument("--outer-last-frac", type=float, default=0.40)
    p.add_argument("--outer-rfrac", type=float, default=0.60)
    p.add_argument("--min-points", type=int, default=5)
    p.add_argument("--huber-c", type=float, default=1.345)

    args = p.parse_args()

    if not args.in_csv.exists():
        print(f"ERROR: input CSV not found: {args.in_csv}", file=sys.stderr)
        return 2

    name = args.name.strip() or args.in_csv.stem
    out_dir = args.out_dir / name
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        data = _read_profile(args.in_csv)
        r_kpc = _pick_radius_kpc(data)
        vtot_kms, vbar_kms = _compute_velocities(data, r_kpc)
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Expected columns:", file=sys.stderr)
        print("- radius: r_kpc (preferred) or r_mpc", file=sys.stderr)
        print("- plus either:", file=sys.stderr)
        print("  - velocities: v_tot_kms and v_bar_kms", file=sys.stderr)
        print("  - masses:     M_tot_Msun and M_bar_Msun (enclosed)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Template + notes:", file=sys.stderr)
        print("- toy_models/data/bullet_cluster/profile_template.csv", file=sys.stderr)
        print("- toy_models/data/bullet_cluster/README.md", file=sys.stderr)
        return 2

    m = np.isfinite(r_kpc) & np.isfinite(vtot_kms) & np.isfinite(vbar_kms) & (r_kpc > 0)
    r_kpc = r_kpc[m]
    vtot_kms = vtot_kms[m]
    vbar_kms = vbar_kms[m]

    if r_kpc.size < 3:
        print("ERROR: Not enough finite rows after filtering (need >= 3)", file=sys.stderr)
        return 2

    order = np.argsort(r_kpc)
    r_kpc = r_kpc[order]
    vtot_kms = vtot_kms[order]
    vbar_kms = vbar_kms[order]

    q_est, huber_scale, sel = compute_q_est(
        r_kpc=r_kpc,
        vobs_kms=vtot_kms,
        vbar_kms=vbar_kms,
        outer_last_frac=args.outer_last_frac,
        outer_rfrac=args.outer_rfrac,
        min_points=args.min_points,
        huber_c=args.huber_c,
    )

    dv2 = vtot_kms**2 - vbar_kms**2

    _write_csv(
        out_dir / "profile_with_dv2.csv",
        [
            {
                "r_kpc": float(r),
                "v_tot_kms": float(vt),
                "v_bar_kms": float(vb),
                "dv2_kms2": float(d),
            }
            for r, vt, vb, d in zip(r_kpc, vtot_kms, vbar_kms, dv2)
        ],
    )

    row = {
        "name": name,
        "q_est_kms2": float(q_est) if np.isfinite(q_est) else math.nan,
        "huber_scale_kms2": float(huber_scale) if np.isfinite(huber_scale) else math.nan,
        **{f"outer_sel_{k}": v for k, v in asdict(sel).items()},
        "n_rows_used": int(r_kpc.size),
        "in_csv": str(args.in_csv).replace("\\\\", "/"),
    }
    _write_csv(out_dir / "q_est_cluster.csv", [row])

    print(f"Wrote: {out_dir / 'q_est_cluster.csv'}")
    print(f"Wrote: {out_dir / 'profile_with_dv2.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
