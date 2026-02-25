"""Batch-render six-panel κ vs Chandra-proxy figures from systematics outputs.

This driver reads the combined systematics CSV (produced by run_hff_systematics.py)
primarily to discover which (team, version) combinations are available.

It then locates the staged κ FITS for each team and calls
`visualize_hff_kappa_xray_sixpanel.py` to render a 2×3 PNG.

Design goals:
- Separate code path from the existing SPARC/dyed-spacetime six-panel renderer.
- Deterministic filenames and idempotent reruns (skip if PNG exists unless forced).

Example:
  d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe \
    toy_models/render_hff_systematics_sixpanels.py \
    --cluster abell2744 \
    --roi-radius-arcsec 100 \
    --out-dir toy_models/out_predictions/figures/systematics_sixpanel/abell2744
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ClusterConfig:
    key: str
    roi_center_deg: str
    chandra_proxy_fits: Path


CLUSTERS: dict[str, ClusterConfig] = {
    "abell2744": ClusterConfig(
        key="abell2744",
        roi_center_deg="3.5887474051936,-30.397192536687",
        chandra_proxy_fits=Path("toy_models/data/hff/abell2744/chandra_stack/abell2744_chandra_full_img2_proxy.fits"),
    ),
    "macs0416": ClusterConfig(
        key="macs0416",
        roi_center_deg="64.03491667,-24.07244444",
        chandra_proxy_fits=Path("toy_models/data/hff/macs0416/chandra_stack/macs0416_chandra_full_img2_proxy.fits"),
    ),
}


def _find_kappa_fits(*, cluster: str, team: str, version: str) -> Path:
    base = Path("toy_models/data/hff") / cluster / "external_lensing" / "stsci_frontier"
    tag = f"{team}_{version}" if str(version).strip() else f"{team}_noversion"
    d = base / tag
    if not d.exists():
        raise FileNotFoundError(f"Missing staged kappa dir: {d.as_posix()}")

    # Prefer the canonical HLSP naming but tolerate variations.
    cands = sorted(d.glob("*kappa*.fits*"))
    if not cands:
        cands = sorted(d.glob("*.fits*"))
    if not cands:
        raise FileNotFoundError(f"No FITS found in: {d.as_posix()}")
    return cands[0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cluster", required=True, choices=sorted(CLUSTERS.keys()))
    ap.add_argument(
        "--systematics-csv",
        type=Path,
        default=None,
        help="Optional override path to systematics_summary.csv (defaults to toy_models/out_predictions/systematics/<cluster>/systematics_summary.csv).",
    )
    ap.add_argument("--roi-radius-arcsec", type=float, default=100.0)
    ap.add_argument(
        "--teams",
        nargs="+",
        default=["all"],
        help="Subset of team names to render, or 'all'.",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("toy_models/out_predictions/figures/systematics_sixpanel"),
        help="Output directory for PNG figures.",
    )
    ap.add_argument("--force", action="store_true", help="Overwrite existing PNGs.")
    ap.add_argument("--levels", type=float, nargs="+", default=[99.0, 97.0, 95.0])
    ap.add_argument("--smooth-arcsec", type=float, default=8.0)

    args = ap.parse_args()

    cfg = CLUSTERS[str(args.cluster)]
    if args.systematics_csv is None:
        args.systematics_csv = Path("toy_models/out_predictions/systematics") / cfg.key / "systematics_summary.csv"

    if not args.systematics_csv.exists():
        raise SystemExit(f"Missing: {args.systematics_csv.as_posix()}")
    if not cfg.chandra_proxy_fits.exists():
        raise SystemExit(f"Missing: {cfg.chandra_proxy_fits.as_posix()}")

    df = pd.read_csv(args.systematics_csv)
    df = df[df.roi_radius_arcsec.astype(float) == float(args.roi_radius_arcsec)]
    if df.empty:
        raise SystemExit(f"No rows for ROI radius {float(args.roi_radius_arcsec)} in {args.systematics_csv.as_posix()}")

    teams_in = sorted(df.team.unique().tolist())
    want_all = any(str(t).strip().lower() == "all" for t in args.teams)
    if want_all:
        teams = teams_in
    else:
        want = {str(t).strip().lower() for t in args.teams}
        teams = [t for t in teams_in if t.lower() in want]

    out_dir = Path(args.out_dir)
    if out_dir.name != cfg.key:
        out_dir = out_dir / cfg.key
    out_dir.mkdir(parents=True, exist_ok=True)

    levels = [float(x) for x in args.levels]

    n_ok = 0
    for team in teams:
        sub = df[df.team == team]
        # Most teams have exactly one version_dir per cluster; select the modal version.
        version = str(sub.version.mode().iloc[0]) if "version" in sub.columns and not sub.version.mode().empty else ""
        kappa_fits = _find_kappa_fits(cluster=cfg.key, team=str(team), version=version)

        safe_ver = version.replace("/", "").replace(" ", "")
        out_png = out_dir / f"{cfg.key}_{team}_{safe_ver}_roi{int(round(float(args.roi_radius_arcsec)))}_sixpanel.png"
        if out_png.exists() and not args.force:
            n_ok += 1
            continue

        cmd = [
            sys.executable,
            str(Path(__file__).with_name("visualize_hff_kappa_xray_sixpanel.py")),
            "--map-kappa",
            str(kappa_fits),
            "--map-xray",
            str(cfg.chandra_proxy_fits),
            "--roi-center-icrs",
            cfg.roi_center_deg,
            "--roi-radius-arcsec",
            str(float(args.roi_radius_arcsec)),
            "--smooth-kappa-arcsec",
            str(float(args.smooth_arcsec)),
            "--smooth-xray-arcsec",
            str(float(args.smooth_arcsec)),
            "--levels",
            *[str(float(x)) for x in levels],
            "--out-png",
            str(out_png),
            "--title",
            f"{cfg.key} | team={team} | v={version} | ROI={float(args.roi_radius_arcsec):0.0f}\"",
        ]
        subprocess.run(cmd, check=True)
        n_ok += 1

    print(f"Rendered: {n_ok} figures -> {out_dir.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
