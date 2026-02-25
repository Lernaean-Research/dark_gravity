"""Run κ-vs-Chandra metrics across Frontier κ teams and ROI radii.

This executes two robustness checks on an existing staged Chandra proxy map:
1) Lens-model systematics: repeat metrics for multiple Frontier κ teams.
2) ROI sensitivity: repeat metrics for multiple ROI radii.

It relies on `frontier_list_kappa.py` to discover κ URLs.

Outputs:
- Per-run metrics CSVs under toy_models/out_predictions/systematics/<cluster>/
- A combined summary CSV for quick comparison.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class KappaInfo:
    team: str
    version_dir: str
    kappa_url: str
    readme_url: str | None


def _read_kappa_index_ndjson(path: Path) -> list[KappaInfo]:
    infos: list[KappaInfo] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            infos.append(
                KappaInfo(
                    team=str(d["team"]),
                    version_dir=str(d.get("version_dir") or ""),
                    kappa_url=str(d["kappa_url"]),
                    readme_url=None if d.get("readme_url") in (None, "") else str(d["readme_url"]),
                )
            )
    return infos


def _run_list(cluster: str, *, cache_path: Path | None = None, refresh: bool = False) -> list[KappaInfo]:
    if cache_path is not None and cache_path.exists() and cache_path.stat().st_size > 0 and not refresh:
        return _read_kappa_index_ndjson(cache_path)

    cmd = [sys.executable, str(Path(__file__).with_name("frontier_list_kappa.py")), "--cluster", cluster]
    infos: list[KappaInfo] = []
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        out_f = cache_path.open("w", encoding="utf-8", newline="\n")
    else:
        out_f = None

    try:
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        ) as p:
            assert p.stdout is not None
            for raw_line in p.stdout:
                line = raw_line.strip()
                if not line:
                    continue
                if out_f is not None:
                    out_f.write(line + "\n")
                d = json.loads(line)
                infos.append(
                    KappaInfo(
                        team=str(d["team"]),
                        version_dir=str(d.get("version_dir") or ""),
                        kappa_url=str(d["kappa_url"]),
                        readme_url=None if d.get("readme_url") in (None, "") else str(d["readme_url"]),
                    )
                )
            stderr = "" if p.stderr is None else p.stderr.read()
            rc = p.wait()
            if rc != 0:
                raise subprocess.CalledProcessError(rc, cmd, output="", stderr=stderr)
    finally:
        if out_f is not None:
            out_f.close()

    return infos


def _curl_download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 0:
        return
    cmd = ["curl.exe", "-L", url, "-o", str(out_path)]
    subprocess.run(cmd, check=True)


def _run_metrics(*, map_a: Path, map_b: Path, roi_center: str, roi_radius: float, out_metrics: Path) -> None:
    out_metrics.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "toy_models/cluster_prediction_report.py",
        "--map-a",
        str(map_a),
        "--map-b",
        str(map_b),
        "--roi-center-icrs",
        roi_center,
        "--roi-radius-arcsec",
        str(float(roi_radius)),
        "--smooth-a-arcsec",
        "8",
        "--smooth-b-arcsec",
        "8",
        "--levels",
        "99",
        "97",
        "95",
        "--out-metrics",
        str(out_metrics),
    ]
    subprocess.run(cmd, check=True)


def _read_metrics(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cluster", required=True, help="frontier cluster dir (e.g., abell2744, macs0416)")
    ap.add_argument("--chandra-map", required=True, type=Path, help="stacked Chandra proxy FITS")
    ap.add_argument("--roi-center", required=True, help="ROI center 'RA_DEG,DEC_DEG'")
    ap.add_argument("--roi-radii", required=True, nargs="+", type=float, help="ROI radii arcsec")
    ap.add_argument(
        "--teams",
        nargs="+",
        default=["all"],
        help="Frontier team directory names to include, or 'all' to include every team with a public kappa FITS.",
    )
    ap.add_argument(
        "--out-root",
        type=Path,
        default=Path("toy_models/out_predictions/systematics"),
        help="Output root dir.",
    )
    ap.add_argument(
        "--index-cache",
        type=Path,
        default=None,
        help=(
            "Optional NDJSON cache of discovered Frontier κ teams/versions. "
            "If present and non-empty, it is reused unless --refresh-index is set."
        ),
    )
    ap.add_argument(
        "--refresh-index",
        action="store_true",
        help="Force re-scraping the Frontier κ index instead of using --index-cache.",
    )
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="If set, reuse any existing per-run metrics CSVs and only compute missing combinations.",
    )
    args = ap.parse_args()

    if args.index_cache is None:
        args.index_cache = (
            Path("toy_models/data/hff")
            / args.cluster
            / "external_lensing"
            / "stsci_frontier"
            / "kappa_index.ndjson"
        )

    infos = _run_list(args.cluster, cache_path=args.index_cache, refresh=bool(args.refresh_index))
    by_team = {i.team.lower(): i for i in infos}

    want_all = any(str(t).strip().lower() == "all" for t in args.teams)
    if want_all:
        selected = [by_team[k] for k in sorted(by_team.keys())]
    else:
        selected = []
        for t in args.teams:
            k = by_team.get(t.lower())
            if k is None:
                raise SystemExit(
                    f"Team not found for cluster={args.cluster}: {t}. Available: {sorted(by_team.keys())}"
                )
            selected.append(k)

    # Stage κ maps
    staged: list[tuple[KappaInfo, Path]] = []
    for k in selected:
        tag = f"{k.team}_" + (k.version_dir.replace("/", "") if k.version_dir else "noversion")
        out_dir = Path("toy_models/data/hff") / args.cluster / "external_lensing" / "stsci_frontier" / tag
        out_fits = out_dir / Path(k.kappa_url).name
        _curl_download(k.kappa_url, out_fits)
        if k.readme_url:
            _curl_download(k.readme_url, out_dir / Path(k.readme_url).name)
        staged.append((k, out_fits))

    # Run grid
    summary_rows: list[dict[str, object]] = []
    for roi_r in args.roi_radii:
        for k, fits_path in staged:
            tag = f"{k.team}_{k.version_dir}" if k.version_dir else k.team
            safe_tag = tag.replace("/", "").replace(" ", "")
            out_metrics = args.out_root / args.cluster / f"roi{int(round(roi_r))}arcsec" / f"{safe_tag}_metrics.csv"
            if args.skip_existing and out_metrics.exists() and out_metrics.stat().st_size > 0:
                pass
            else:
                _run_metrics(
                    map_a=fits_path,
                    map_b=args.chandra_map,
                    roi_center=args.roi_center,
                    roi_radius=roi_r,
                    out_metrics=out_metrics,
                )
            for r in _read_metrics(out_metrics):
                summary_rows.append(
                    {
                        "cluster": args.cluster,
                        "team": k.team,
                        "version": k.version_dir,
                        "roi_radius_arcsec": float(roi_r),
                        "level_pct": float(r["level_pct"]),
                        "sep_arcsec": float(r["sep_arcsec"]),
                        "a_area_pix": int(float(r["a_area_pix"])),
                        "b_area_pix": int(float(r["b_area_pix"])),
                        "a_centroid_ra_deg": float(r["a_centroid_ra_deg"]),
                        "a_centroid_dec_deg": float(r["a_centroid_dec_deg"]),
                        "b_centroid_ra_deg": float(r["b_centroid_ra_deg"]),
                        "b_centroid_dec_deg": float(r["b_centroid_dec_deg"]),
                        "metrics_csv": str(out_metrics.as_posix()),
                    }
                )

    # Write combined summary
    out_summary = args.out_root / args.cluster / "systematics_summary.csv"
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(summary_rows[0].keys()) if summary_rows else []
    with out_summary.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in summary_rows:
            w.writerow(r)

    print(f"Wrote: {out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
