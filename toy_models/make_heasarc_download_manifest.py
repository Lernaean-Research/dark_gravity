"""Generate a download manifest (URLs + S3 paths) for HEASARC observation catalogs.

This script is intended to bridge the gap between:
- *discovery* (finding observation IDs around a target), and
- *acquisition* (getting the raw data products).

It queries HEASARC catalogs around a target and then uses `Heasarc.locate_data()`
(VO/Datalink) to obtain the directory URLs where the data live.

By default this is configured for Bullet Cluster style X-ray inputs:
- `chanmaster` (Chandra)
- `xmmmaster` (XMM)

ROSAT can be included, but VO table discovery can be slow in some environments.

Example
-------
python toy_models/make_heasarc_download_manifest.py \
  --target "1E 0657-56" \
  --radius-arcmin 12 \
  --out-dir toy_models/out_cluster_fetch/bullet_cluster
"""

from __future__ import annotations

import argparse
from pathlib import Path

import astropy.units as u
from astropy.coordinates import SkyCoord


def _safe_len(x) -> int:
    try:
        return int(len(x))
    except Exception:
        return -1


def _write_table_csv(path: Path, table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table.write(path, format="csv", overwrite=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", type=str, default="1E 0657-56")
    p.add_argument("--radius-arcmin", type=float, default=12.0)
    p.add_argument("--out-dir", type=Path, default=Path("toy_models/out_cluster_fetch/bullet_cluster"))
    p.add_argument(
        "--include-rosat",
        action="store_true",
        help="Also attempt rosmaster locate_data (can be slow in some environments).",
    )
    args = p.parse_args()

    coord = SkyCoord.from_name(args.target)
    radius = float(args.radius_arcmin) * u.arcmin

    from astroquery.heasarc import Heasarc

    h = Heasarc()

    catalogs = [
        ("chanmaster", "Chandra observation log"),
        ("xmmmaster", "XMM-Newton observation log"),
    ]
    if args.include_rosat:
        catalogs.append(("rosmaster", "ROSAT observation log"))

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    md_lines: list[str] = []
    md_lines.append(f"# HEASARC download manifest: {args.target}\n")
    md_lines.append(f"Resolved target: ra={coord.ra.deg:.6f} deg, dec={coord.dec.deg:.6f} deg\n")
    md_lines.append(f"Search radius: {args.radius_arcmin:.2f} arcmin\n")

    for cat, desc in catalogs:
        print(f"Querying {cat}...")
        try:
            res = h.query_region(coord, catalog=cat, radius=radius)
        except Exception as e:
            print(f"  {cat} query FAILED: {type(e).__name__}: {e}")
            md_lines.append(f"## {cat}\n\n- {desc}\n- Query failed: `{type(e).__name__}: {e}`\n")
            continue

        print(f"  {cat} rows: {_safe_len(res)}")
        _write_table_csv(out_dir / f"{cat}_query.csv", res)

        link_rows = []
        md_lines.append(f"## {cat}\n\n- {desc}\n- Rows: {_safe_len(res)}\n")

        if len(res) == 0:
            md_lines.append("\n")
            continue

        md_lines.append("| index | id | access_url | aws | sciserver | bytes |\n")
        md_lines.append("|---:|---|---|---|---|---:|\n")

        for i, row in enumerate(res):
            try:
                links = h.locate_data(row, catalog_name=cat)
                if len(links) == 0:
                    continue
                link = links[0]
                access_url = str(link.get("access_url", ""))
                aws = str(link.get("aws", ""))
                sciserver = str(link.get("sciserver", ""))
                nbytes = link.get("content_length", "")
                id_ = str(link.get("ID", ""))

                link_rows.append(
                    {
                        "catalog": cat,
                        "index": i,
                        "ID": id_,
                        "access_url": access_url,
                        "aws": aws,
                        "sciserver": sciserver,
                        "content_length_bytes": nbytes,
                    }
                )
                md_lines.append(
                    f"| {i} | {id_} | {access_url} | {aws} | {sciserver} | {nbytes} |\n"
                )
            except KeyboardInterrupt:
                raise
            except Exception as e:
                # Keep going even if one row fails.
                md_lines.append(f"| {i} | (failed) |  |  |  |  |\n")
                print(f"  locate_data failed for {cat} row {i}: {type(e).__name__}: {e}")

        if link_rows:
            import csv

            with (out_dir / f"{cat}_links.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(link_rows[0].keys()))
                w.writeheader()
                for r in link_rows:
                    w.writerow(r)

            md_lines.append("\n")
            md_lines.append("**Suggested download approaches**\n\n")
            md_lines.append("- If you have AWS CLI configured: `aws s3 sync <aws_path> <local_dir>`\n")
            md_lines.append("- If you have wget (Git-Bash/WSL): `wget -r -np -nH --cut-dirs=3 <access_url>`\n")
            md_lines.append("  (Adjust `--cut-dirs` depending on the URL depth.)\n\n")

        md_lines.append("\n")

    manifest = out_dir / "download_manifest.md"
    manifest.write_text("".join(md_lines), encoding="utf-8")
    print(f"Wrote: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
