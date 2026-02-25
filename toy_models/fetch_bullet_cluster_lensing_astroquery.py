"""Discover *lensing* products for the Bullet Cluster using astroquery.

This complements `toy_models/fetch_bullet_cluster_astroquery.py` (X-ray metadata).
Here we focus on finding public artifacts relevant to a true 2D Bullet Cluster test:

- weak-lensing shear catalogs (tables of shapes / shear estimates)
- lensing mass / convergence maps (often as FITS images, sometimes as HLSP products)

Important reality check
----------------------
There is no single, universal archive endpoint that guarantees you can programmatically
retrieve "the" Bullet Cluster weak-lensing shear catalog and mass map. Much of the
canonical material is distributed as:

- paper supplementary material,
- journal-hosted data tables,
- author websites / Zenodo,
- or HST/MAST High Level Science Products (HLSP) when available.

This script is therefore a *discovery + manifest* generator:

1) VizieR: keyword-search catalogs, then optionally query region to confirm data exist.
2) MAST: query observations around the target and list downloadable products.

Outputs
-------
Writes several CSVs under `--out-dir/--name/` (default: toy_models/out_lensing_fetch/bullet_cluster/)
so the workflow is reproducible even if you later download manually.

Examples
--------
./.venv/Scripts/python.exe toy_models/fetch_bullet_cluster_lensing_astroquery.py \
  --target "1E 0657-56" --radius-arcmin 12 \
  --out-dir toy_models/out_lensing_fetch --name bullet_cluster

If you want to attempt downloading small MAST products:

./.venv/Scripts/python.exe toy_models/fetch_bullet_cluster_lensing_astroquery.py \
  --target "1E 0657-56" --radius-arcmin 12 \
  --download-mast --mast-max-obs 25
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import astropy.units as u
from astropy.coordinates import SkyCoord


def _write_rows_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        # Still create a header-only CSV so the run is auditable.
        with path.open("w", newline="", encoding="utf-8") as f:
            f.write("\n")
        return
    keys: list[str] = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _safe_str(x: object) -> str:
    if x is None:
        return ""
    return str(x)


def _looks_like_shear_columns(columns: Iterable[str]) -> bool:
    cols = {c.lower() for c in columns}
    # Heuristic: common shear/shape columns.
    tokens = {
        "g1",
        "g2",
        "gamma1",
        "gamma2",
        "e1",
        "e2",
        "ell1",
        "ell2",
        "eps1",
        "eps2",
        "kappa",
        "convergence",
        "shear",
    }
    if any(t in cols for t in tokens):
        return True
    # Also look for pattern-like names.
    patterns = [r"^(g|e|eps|ell)(1|2)$", r"^gamma(1|2)$", r"^kappa$"]
    for c in cols:
        if any(re.match(p, c) for p in patterns):
            return True
    return False


@dataclass(frozen=True)
class VizierCandidate:
    catalog_id: str
    title: str
    url: str


def _vizier_find_candidates(keywords: list[str], max_catalogs: int) -> list[VizierCandidate]:
    from astroquery.vizier import Vizier

    seen: set[str] = set()
    out: list[VizierCandidate] = []

    for kw in keywords:
        try:
            found = Vizier.find_catalogs(kw)
        except Exception as e:
            print(f"VizieR find_catalogs({kw!r}) FAILED ({type(e).__name__}: {e})")
            continue

        for cat_id, cats in found.items():
            if cat_id in seen:
                continue
            seen.add(cat_id)

            # 'cats' is a list of VizierCatalog objects; pick a representative title/url.
            title = ""
            url = ""
            try:
                if cats:
                    title = _safe_str(getattr(cats[0], "description", "")) or _safe_str(
                        getattr(cats[0], "title", "")
                    )
                    url = _safe_str(getattr(cats[0], "url", ""))
            except Exception:
                pass

            out.append(VizierCandidate(catalog_id=str(cat_id), title=title, url=url))
            if len(out) >= max_catalogs:
                return out

    return out


def _vizier_probe_region(
    coord: SkyCoord,
    radius: u.Quantity,
    candidates: list[VizierCandidate],
    max_tables: int,
    row_limit: int,
) -> list[dict[str, object]]:
    from astroquery.vizier import Vizier

    v = Vizier(columns=["*"], row_limit=row_limit)
    rows: list[dict[str, object]] = []
    n_tables = 0

    for cand in candidates:
        if n_tables >= max_tables:
            break

        try:
            tables = v.query_region(coord, radius=radius, catalog=cand.catalog_id)
        except Exception as e:
            rows.append(
                {
                    "catalog_id": cand.catalog_id,
                    "catalog_title": cand.title,
                    "table_name": "",
                    "n_rows": "",
                    "looks_like_shear": "",
                    "status": f"FAILED: {type(e).__name__}: {e}",
                }
            )
            continue

        if tables is None or len(tables) == 0:
            rows.append(
                {
                    "catalog_id": cand.catalog_id,
                    "catalog_title": cand.title,
                    "table_name": "",
                    "n_rows": 0,
                    "looks_like_shear": False,
                    "status": "NO_TABLES_RETURNED",
                }
            )
            continue

        for tname in tables.keys():
            if n_tables >= max_tables:
                break
            t = tables[tname]
            colnames = list(getattr(t, "colnames", []))
            looks = _looks_like_shear_columns(colnames)
            rows.append(
                {
                    "catalog_id": cand.catalog_id,
                    "catalog_title": cand.title,
                    "table_name": str(tname),
                    "n_rows": int(len(t)),
                    "looks_like_shear": bool(looks),
                    "status": "OK",
                }
            )
            n_tables += 1

    return rows


def _mast_query_and_manifest(
    coord: SkyCoord,
    radius: u.Quantity,
    max_obs: int,
    download: bool,
    out_dir: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Return (observations_rows, products_rows)."""

    from astroquery.mast import Observations

    obs_rows: list[dict[str, object]] = []
    prod_rows: list[dict[str, object]] = []

    obs = Observations.query_region(coord, radius=radius)

    # Sort by mission/collection then by exposure if present.
    try:
        if "t_exptime" in obs.colnames:
            obs.sort("t_exptime")
            obs = obs[::-1]
    except Exception:
        pass

    if max_obs > 0 and len(obs) > max_obs:
        obs = obs[:max_obs]

    for row in obs:
        obsid = _safe_str(row.get("obsid"))
        obs_collection = _safe_str(row.get("obs_collection"))
        dataproduct_type = _safe_str(row.get("dataproduct_type"))
        filters = _safe_str(row.get("filters"))
        project = _safe_str(row.get("project"))
        instrument_name = _safe_str(row.get("instrument_name"))
        t_exptime = row.get("t_exptime")
        s_ra = row.get("s_ra")
        s_dec = row.get("s_dec")

        obs_rows.append(
            {
                "obsid": obsid,
                "obs_collection": obs_collection,
                "project": project,
                "instrument": instrument_name,
                "dataproduct_type": dataproduct_type,
                "filters": filters,
                "t_exptime": float(t_exptime) if t_exptime is not None else "",
                "s_ra": float(s_ra) if s_ra is not None else "",
                "s_dec": float(s_dec) if s_dec is not None else "",
            }
        )

        # Pull product list and optionally download (usually small metadata+FITS).
        try:
            products = Observations.get_product_list(obsid)
        except Exception as e:
            prod_rows.append(
                {
                    "obsid": obsid,
                    "status": f"FAILED get_product_list: {type(e).__name__}: {e}",
                }
            )
            continue

        # Filter: public + prefer science products, but keep everything in manifest.
        for p in products:
            prod_rows.append(
                {
                    "obsid": obsid,
                    "productFilename": _safe_str(p.get("productFilename")),
                    "productType": _safe_str(p.get("productType")),
                    "productSubGroupDescription": _safe_str(p.get("productSubGroupDescription")),
                    "productGroupDescription": _safe_str(p.get("productGroupDescription")),
                    "dataRights": _safe_str(p.get("dataRights")),
                    "size": int(p.get("size")) if p.get("size") is not None else "",
                    "description": _safe_str(p.get("description")),
                }
            )

        if download:
            try:
                # Start conservative: download only products already marked as science and public.
                flt = Observations.filter_products(
                    products,
                    mrp_only=False,
                    productType=["SCIENCE"],
                    dataRights=["PUBLIC"],
                )
                if len(flt) > 0:
                    Observations.download_products(flt, download_dir=str(out_dir / "mast_downloads"), cache=True)
            except Exception as e:
                prod_rows.append(
                    {
                        "obsid": obsid,
                        "status": f"FAILED download_products: {type(e).__name__}: {e}",
                    }
                )

    return obs_rows, prod_rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", type=str, default="1E 0657-56")
    p.add_argument("--radius-arcmin", type=float, default=12.0)
    p.add_argument("--out-dir", type=Path, default=Path("toy_models/out_lensing_fetch"))
    p.add_argument("--name", type=str, default="bullet_cluster")

    # Network behavior
    p.add_argument(
        "--timeout-sec",
        type=float,
        default=45.0,
        help="Per-request network timeout in seconds (best-effort; depends on backend).",
    )
    p.add_argument(
        "--skip-vizier",
        action="store_true",
        help="Skip VizieR discovery (useful when VizieR is slow/unreachable).",
    )
    p.add_argument(
        "--skip-mast",
        action="store_true",
        help="Skip MAST discovery.",
    )

    # VizieR discovery
    p.add_argument(
        "--vizier-keywords",
        type=str,
        nargs="*",
        default=[
            "1E 0657-56",
            "Bullet Cluster",
            "1E0657-56",
            "weak lensing 1E 0657-56",
            "shear 1E 0657-56",
            "lensing mass map 1E 0657-56",
        ],
    )
    p.add_argument("--vizier-max-catalogs", type=int, default=40)
    p.add_argument("--vizier-probe-region", action="store_true")
    p.add_argument("--vizier-max-tables", type=int, default=80)
    p.add_argument("--vizier-row-limit", type=int, default=50)

    # MAST discovery
    p.add_argument("--mast-max-obs", type=int, default=50)
    p.add_argument("--download-mast", action="store_true")

    args = p.parse_args()

    out_dir = (args.out_dir / args.name).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Resolve target name -> coordinates.
    try:
        coord = SkyCoord.from_name(args.target)
    except Exception as e:
        print(f"ERROR: failed to resolve target name {args.target!r} ({type(e).__name__}: {e})", file=sys.stderr)
        return 2

    radius = float(args.radius_arcmin) * u.arcmin
    print(f"Resolved {args.target!r} -> ra={coord.ra.deg:.6f} deg dec={coord.dec.deg:.6f} deg")
    print(f"Search radius: {radius.to(u.arcmin).value:.2f} arcmin")
    print(f"Output dir: {out_dir.as_posix()}")

    # Best-effort: configure astroquery timeouts.
    # (Different astroquery modules may use different underlying session objects.)
    timeout_sec = float(args.timeout_sec)
    if timeout_sec <= 0:
        timeout_sec = 45.0

    # --- VizieR ---
    vizier_catalog_rows: list[dict[str, object]] = []
    vizier_probe_rows: list[dict[str, object]] = []

    if args.skip_vizier:
        print("VizieR: skipped")
    else:
        try:
            from astroquery.vizier import Vizier

            Vizier.TIMEOUT = timeout_sec
            candidates = _vizier_find_candidates(args.vizier_keywords, max_catalogs=int(args.vizier_max_catalogs))
            vizier_catalog_rows = [
                {"catalog_id": c.catalog_id, "title": c.title, "url": c.url} for c in candidates
            ]
            _write_rows_csv(out_dir / "vizier_catalog_candidates.csv", vizier_catalog_rows)
            print(f"VizieR: {len(candidates)} candidate catalogs written")

            if args.vizier_probe_region:
                vizier_probe_rows = _vizier_probe_region(
                    coord=coord,
                    radius=radius,
                    candidates=candidates,
                    max_tables=int(args.vizier_max_tables),
                    row_limit=int(args.vizier_row_limit),
                )
                _write_rows_csv(out_dir / "vizier_region_probe.csv", vizier_probe_rows)
                ok = sum(1 for r in vizier_probe_rows if r.get("status") == "OK")
                looks = sum(1 for r in vizier_probe_rows if bool(r.get("looks_like_shear")))
                print(f"VizieR: region probe wrote {len(vizier_probe_rows)} rows (OK={ok}, shear-ish={looks})")
        except KeyboardInterrupt:
            print("VizieR discovery interrupted")
        except Exception as e:
            print(f"VizieR discovery FAILED ({type(e).__name__}: {e})")

    # --- MAST ---
    if args.skip_mast:
        print("MAST: skipped")
    else:
        try:
            from astroquery.mast import Observations

            Observations.TIMEOUT = timeout_sec
            obs_rows, prod_rows = _mast_query_and_manifest(
                coord=coord,
                radius=radius,
                max_obs=int(args.mast_max_obs),
                download=bool(args.download_mast),
                out_dir=out_dir,
            )
            _write_rows_csv(out_dir / "mast_observations.csv", obs_rows)
            _write_rows_csv(out_dir / "mast_products.csv", prod_rows)
            print(f"MAST: wrote {len(obs_rows)} observations and {len(prod_rows)} products")
        except KeyboardInterrupt:
            print("MAST discovery interrupted")
        except Exception as e:
            print(f"MAST discovery FAILED ({type(e).__name__}: {e})")

    print("\nWhat to do next (manual triage):")
    print("- Open vizier_catalog_candidates.csv and search for shear/shape columns (g1,g2,e1,e2,gamma1,gamma2).")
    print("- Open mast_products.csv and look for HLSP/cat/massmap/kappa keywords in product descriptions.")
    print("- Once you have a lensing mass map (FITS image) and an X-ray image, run the offset utility:")
    print("  ./.venv/Scripts/python.exe toy_models/offset_from_maps.py --help")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
