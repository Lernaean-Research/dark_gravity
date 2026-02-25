"""Inventory the CANUCS Bullet Cluster lens-model package (Rihtaršič et al. 2026).

Creates a reproducible manifest of all files and a compact summary by product type.

Outputs (written into the package root):
- manifest_files.csv

Usage:
  d:/.../.venv/Scripts/python.exe toy_models/inventory_canucs_rihtarsic_2026.py \
    --root toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


def _classify_kind(ext: str) -> str:
    ext = ext.lower()
    if ext in {".fits", ".fit", ".fits.gz", ".fit.gz"}:
        return "fits"
    if ext in {".csv", ".ecsv"}:
        return "table"
    if ext in {".dat", ".par", ".txt"}:
        return "text"
    if ext == ".zip":
        return "archive"
    return "other"


def _tag_from_name(name: str) -> str:
    n = name.lower()
    if "kappa" in n:
        return "kappa"
    if re.search(r"gamma(1|2)?", n):
        return "gamma"
    if "alpha" in n or "dpl" in n:
        return "deflection"
    if "psi" in n or "pot" in n:
        return "potential"
    if n.endswith(".par"):
        return "lenstool_par"
    if any(t in n for t in ("multim", "gold", "bronze")):
        return "images_catalog"
    if "cm_" in n or "cluster_members" in n:
        return "cluster_members"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(
            "toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026"
        ),
        help="Package root directory.",
    )
    args = ap.parse_args()

    root: Path = args.root
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    rows: list[dict[str, object]] = []
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(root).as_posix()
        ext = "".join(p.suffixes).lower()
        kind = _classify_kind(ext)
        tag = _tag_from_name(p.name)
        rows.append(
            {
                "relpath": rel,
                "bytes": int(p.stat().st_size),
                "kind": kind,
                "tag": tag,
            }
        )

    out_csv = root / "manifest_files.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["relpath", "bytes", "kind", "tag"])
        w.writeheader()
        w.writerows(rows)

    kind_counts = Counter(r["kind"] for r in rows)
    tag_counts = Counter(r["tag"] for r in rows if r["tag"])

    print(f"Wrote {out_csv}")
    print("Kinds:")
    for k, v in kind_counts.most_common():
        print(f"  {k:8s} {v}")
    print("Tags:")
    for k, v in tag_counts.most_common():
        print(f"  {k:14s} {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
