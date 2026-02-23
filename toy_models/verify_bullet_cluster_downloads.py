"""Verify Bullet Cluster HEASARC downloads.

Reads the download-manifest link tables produced by:
  - toy_models/make_heasarc_download_manifest.py
and checks that each expected ObsID directory exists under:
  - toy_models/data/bullet_cluster/raw/heasarc/

Outputs:
  - toy_models/out_cluster_fetch/bullet_cluster/download_verify.csv
  - toy_models/out_cluster_fetch/bullet_cluster/download_verify.md

This is intentionally lightweight: it only checks directory presence and local
file/bytes totals; it does not validate scientific correctness of products.
"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class LinkRow:
    catalog: str
    aws: str
    content_length_bytes: int | None


def _parse_int(s: str) -> int | None:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def read_links_csv(path: Path) -> list[LinkRow]:
    rows: list[LinkRow] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                LinkRow(
                    catalog=(r.get("catalog") or "").strip().lower(),
                    aws=(r.get("aws") or "").strip(),
                    content_length_bytes=_parse_int(r.get("content_length_bytes", "")),
                )
            )
    return rows


def obsid_from_s3(s3: str) -> str:
    s = s3.rstrip("/")
    return s.split("/")[-1]


def walk_stats(root: Path) -> tuple[int, int]:
    file_count = 0
    total_bytes = 0
    if not root.exists():
        return (0, 0)

    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                st = p.stat()
            except OSError:
                continue
            file_count += 1
            total_bytes += st.st_size

    return (file_count, total_bytes)


def fmt_gib(nbytes: int) -> str:
    return f"{nbytes / (1024**3):.3f} GiB"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--links-dir",
        default="toy_models/out_cluster_fetch/bullet_cluster",
        help="Folder containing chanmaster_links.csv and xmmmaster_links.csv",
    )
    ap.add_argument(
        "--raw-root",
        default="toy_models/data/bullet_cluster/raw/heasarc",
        help="Root folder containing chandra/<ObsID>/ and xmm/<ObsID>/",
    )
    ap.add_argument(
        "--out-csv",
        default="toy_models/out_cluster_fetch/bullet_cluster/download_verify.csv",
    )
    ap.add_argument(
        "--out-md",
        default="toy_models/out_cluster_fetch/bullet_cluster/download_verify.md",
    )

    args = ap.parse_args(argv)

    links_dir = Path(args.links_dir)
    raw_root = Path(args.raw_root)

    link_paths = [links_dir / "chanmaster_links.csv", links_dir / "xmmmaster_links.csv"]
    all_rows: list[LinkRow] = []
    for p in link_paths:
        if not p.exists():
            raise FileNotFoundError(f"Missing links CSV: {p}")
        all_rows.extend(read_links_csv(p))

    out_rows: list[dict[str, object]] = []
    missing: list[str] = []
    empty: list[str] = []

    for r in all_rows:
        if not r.aws:
            continue
        obsid = obsid_from_s3(r.aws)

        if r.catalog == "chanmaster":
            local_dir = raw_root / "chandra" / obsid
        elif r.catalog == "xmmmaster":
            local_dir = raw_root / "xmm" / obsid
        else:
            local_dir = raw_root / r.catalog / obsid

        exists = local_dir.exists()
        nfiles, nbytes = walk_stats(local_dir)

        if not exists:
            missing.append(f"{r.catalog}:{obsid}")
        elif nfiles == 0:
            empty.append(f"{r.catalog}:{obsid}")

        out_rows.append(
            {
                "catalog": r.catalog,
                "obsid": obsid,
                "local_dir": str(local_dir).replace("\\", "/"),
                "exists": bool(exists),
                "file_count": nfiles,
                "local_bytes": nbytes,
                "expected_bytes": r.content_length_bytes,
                "local_over_expected": (nbytes / r.content_length_bytes) if (r.content_length_bytes and nbytes) else None,
            }
        )

    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "catalog",
            "obsid",
            "local_dir",
            "exists",
            "file_count",
            "local_bytes",
            "expected_bytes",
            "local_over_expected",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    total_files = sum(int(r["file_count"]) for r in out_rows)
    total_bytes = sum(int(r["local_bytes"]) for r in out_rows)

    def md_lines() -> Iterable[str]:
        yield "# Bullet Cluster HEASARC download verification"
        yield ""
        yield f"Links dir: `{links_dir.as_posix()}`"
        yield f"Raw root: `{raw_root.as_posix()}`"
        yield ""
        yield "## Summary"
        yield ""
        yield f"- Entries checked: {len(out_rows)}"
        yield f"- Total local files: {total_files}"
        yield f"- Total local size: {fmt_gib(total_bytes)}"
        yield f"- Missing dirs: {len(missing)}"
        yield f"- Empty dirs: {len(empty)}"
        if missing:
            yield ""
            yield "Missing:"
            for m in missing:
                yield f"- {m}"
        if empty:
            yield ""
            yield "Empty:"
            for e in empty:
                yield f"- {e}"
        yield ""
        yield "## Output"
        yield ""
        yield f"- CSV: `{out_csv.as_posix()}`"

    out_md.write_text("\n".join(md_lines()) + "\n", encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    print(f"Checked {len(out_rows)} entries: {len(missing)} missing, {len(empty)} empty")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
