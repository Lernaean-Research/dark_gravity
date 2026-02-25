"""Inventory (and optionally selectively extract) large ZIP data packages.

This is intended for Bullet Cluster lensing packages that may be multi-GB.
It writes simple, auditable inventories so you can quickly answer:

- What file types are present? (.fits/.fits.gz/.csv/.par/...) 
- Which specific FITS/CSV products exist (mass maps, shear catalogs, etc.)?
- What should be extracted for downstream analysis?

Examples
--------
# Inventory only:
./.venv/Scripts/python.exe toy_models/inventory_zip_package.py \
  --zip-path toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/Bullet_Cluster_lens_model.zip

# Inventory + extract only likely analysis artifacts:
./.venv/Scripts/python.exe toy_models/inventory_zip_package.py \
  --zip-path toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/Bullet_Cluster_lens_model.zip \
  --extract --include-ext .fits .fits.gz .csv .par .dat .txt
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ZipEntry:
    path: str
    size: int
    compressed_size: int


def _suffixes_lower(path: str) -> str:
    p = path.lower()
    if p.endswith(".fits.gz"):
        return ".fits.gz"
    if p.endswith(".tar.gz"):
        return ".tar.gz"
    if p.endswith(".csv.gz"):
        return ".csv.gz"
    # fall back to last suffix
    sfx = Path(p).suffix
    return sfx if sfx else ""


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip-path", type=Path, required=True)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory to write inventories (default: <zip-dir>/inventory)",
    )
    p.add_argument(
        "--extract",
        action="store_true",
        help="Extract selected files into <out-dir>/extracted/.",
    )
    p.add_argument(
        "--include-ext",
        nargs="*",
        default=[".fits", ".fits.gz", ".csv", ".par", ".dat", ".txt"],
        help="Extensions to include for selective extraction and a filtered listing.",
    )
    p.add_argument(
        "--name-contains",
        nargs="*",
        default=["kappa", "convergence", "shear", "gamma", "mass", "map", "catalog", "lenstool"],
        help="Keywords to flag in filenames as likely-relevant artifacts.",
    )

    args = p.parse_args()
    zip_path: Path = args.zip_path
    if not zip_path.exists():
        raise SystemExit(f"ZIP not found: {zip_path}")

    out_dir = (args.out_dir or (zip_path.parent / "inventory")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    include_ext = {e.lower() for e in args.include_ext}
    name_contains = [k.lower() for k in args.name_contains]

    import zipfile

    entries: list[ZipEntry] = []
    ext_counter: Counter[str] = Counter()

    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            path = info.filename
            sfx = _suffixes_lower(path)
            ext_counter[sfx] += 1
            entries.append(ZipEntry(path=path, size=int(info.file_size), compressed_size=int(info.compress_size)))

        # Write full file listing.
        file_rows = [
            {
                "path": e.path,
                "size": e.size,
                "compressed_size": e.compressed_size,
                "ext": _suffixes_lower(e.path),
                "flagged": any(k in e.path.lower() for k in name_contains),
            }
            for e in entries
        ]
        _write_csv(out_dir / "zip_files.csv", file_rows)

        # Write extension summary.
        ext_rows = [
            {"ext": ext, "count": int(count)} for ext, count in sorted(ext_counter.items(), key=lambda kv: (-kv[1], kv[0]))
        ]
        _write_csv(out_dir / "zip_extensions.csv", ext_rows)

        # Filtered list (likely analysis artifacts).
        filtered = [r for r in file_rows if (r["ext"] in include_ext) or bool(r["flagged"])]
        filtered.sort(key=lambda r: (r["ext"], r["path"]))
        _write_csv(out_dir / "zip_filtered.csv", filtered)

        summary = {
            "zip_path": str(zip_path),
            "n_files": len(entries),
            "total_uncompressed_bytes": sum(e.size for e in entries),
            "total_compressed_bytes": sum(e.compressed_size for e in entries),
            "top_extensions": ext_rows[:30],
            "include_ext": sorted(include_ext),
            "name_contains": name_contains,
            "outputs": {
                "zip_files_csv": str((out_dir / "zip_files.csv")),
                "zip_extensions_csv": str((out_dir / "zip_extensions.csv")),
                "zip_filtered_csv": str((out_dir / "zip_filtered.csv")),
            },
        }
        (out_dir / "zip_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

        if args.extract:
            extract_dir = out_dir / "extracted"
            extract_dir.mkdir(parents=True, exist_ok=True)

            def want(path: str) -> bool:
                p = path.lower()
                return (_suffixes_lower(p) in include_ext) or any(k in p for k in name_contains)

            for info in zf.infolist():
                if info.is_dir():
                    continue
                if want(info.filename):
                    zf.extract(info, path=extract_dir)

    print(f"Wrote inventories to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
