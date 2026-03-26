from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build SPARC RA/Dec table independently from notebook logic."
    )
    ap.add_argument(
        "--q-est-csv",
        default="toy_models/out_sparc_runs_full_with_composition/q_est.csv",
        help="Path to q_est.csv with columns galaxy,q_est_kms2",
    )
    ap.add_argument(
        "--output-csv",
        default="rubin_rsp/data/sparc175_reference_independent.csv",
        help="Output merged table with galaxy,ra_deg,dec_deg,sparc_metric,coord_source",
    )
    ap.add_argument(
        "--report-json",
        default="rubin_rsp/out/sparc175_reference_independent_report.json",
        help="Output summary report JSON",
    )
    ap.add_argument(
        "--unresolved-csv",
        default="rubin_rsp/data/sparc175_unresolved_independent.csv",
        help="Output unresolved names",
    )
    ap.add_argument(
        "--timeout-s",
        type=int,
        default=4,
        help="Timeout per SIMBAD fallback query (seconds)",
    )
    ap.add_argument(
        "--max-simbad",
        type=int,
        default=30,
        help="Max unmatched galaxies to resolve via SIMBAD fallback",
    )
    return ap.parse_args()


def normalize_name(name: str) -> str:
    s = str(name).strip().upper()
    return re.sub(r"[\s\-_.]+", "", s)


def possible_keys(name: str) -> set[str]:
    base = normalize_name(name)
    keys = {base}

    # Common SPARC prefixes with possible leading zeros.
    for pfx in ["NGC", "UGC", "IC", "PGC", "DDO", "UGCA", "ESO", "F", "KK"]:
        m = re.match(rf"^{pfx}0*(\d+)([A-Z0-9]*)$", base)
        if m:
            keys.add(f"{pfx}{int(m.group(1))}{m.group(2)}")

    keys.add(base.replace("-", ""))
    return keys


def name_variants(name: str) -> list[str]:
    raw = str(name).strip()
    variants = [raw, raw.replace("_", " "), raw.replace("-", " ")]

    patterns = [
        r"^(NGC)(\d+[A-Z0-9-]*)$",
        r"^(UGC)(\d+[A-Z0-9-]*)$",
        r"^(IC)(\d+[A-Z0-9-]*)$",
        r"^(DDO)(\d+[A-Z0-9-]*)$",
        r"^(ESO)(\d+[A-Z0-9-]*)$",
        r"^(PGC)(\d+[A-Z0-9-]*)$",
        r"^(UGCA)(\d+[A-Z0-9-]*)$",
        r"^(KK)(\d+[A-Z0-9-]*)$",
    ]

    for p in patterns:
        m = re.match(p, raw, flags=re.IGNORECASE)
        if m:
            variants.append(f"{m.group(1).upper()} {m.group(2)}")

    dedup = []
    seen = set()
    for v in variants:
        key = normalize_name(v)
        if v and key not in seen:
            dedup.append(v)
            seen.add(key)
    return dedup


def load_vizier_map() -> dict[str, dict]:
    from astroquery.vizier import Vizier

    Vizier.ROW_LIMIT = -1
    table = Vizier.get_catalogs("J/AJ/152/157/table1")[0]

    required = ["Name", "_RA", "_DE"]
    for c in required:
        if c not in table.colnames:
            raise ValueError(f"VizieR table missing expected column: {c}")

    m: dict[str, dict] = {}
    for row in table:
        name = str(row["Name"]).strip()
        rec = {
            "ra_deg": float(row["_RA"]),
            "dec_deg": float(row["_DE"]),
            "coord_source": "VizieR:J/AJ/152/157/table1",
            "catalog_name": name,
        }
        for k in possible_keys(name):
            if k not in m:
                m[k] = rec
    return m


def build_simbad(timeout_s: int):
    from astroquery.simbad import Simbad

    s = Simbad()
    s.TIMEOUT = int(timeout_s)
    s.add_votable_fields("ra(d)", "dec(d)")
    return s


def resolve_simbad(galaxy: str, simbad) -> dict | None:
    for candidate in name_variants(galaxy):
        try:
            t = simbad.query_object(candidate)
        except Exception:
            continue
        if t is None or len(t) == 0:
            continue
        try:
            return {
                "ra_deg": float(t["RA_d"][0]),
                "dec_deg": float(t["DEC_d"][0]),
                "coord_source": f"SIMBAD:{candidate}",
                "catalog_name": candidate,
            }
        except Exception:
            continue
    return None


def main() -> int:
    args = parse_args()

    q_est_path = Path(args.q_est_csv)
    out_csv = Path(args.output_csv)
    report_json = Path(args.report_json)
    unresolved_csv = Path(args.unresolved_csv)

    q = pd.read_csv(q_est_path)
    if not {"galaxy", "q_est_kms2"}.issubset(q.columns):
        raise ValueError("q_est.csv must include galaxy and q_est_kms2")

    base = q[["galaxy", "q_est_kms2"]].copy()
    base = base.rename(columns={"q_est_kms2": "sparc_metric"})

    vizier_map = load_vizier_map()
    simbad = build_simbad(timeout_s=args.timeout_s)

    rows = []
    unresolved = []
    n_vizier = 0
    n_simbad = 0

    for i, r in base.iterrows():
        g = str(r["galaxy"]).strip()
        m = None

        for k in possible_keys(g):
            if k in vizier_map:
                m = vizier_map[k]
                n_vizier += 1
                break

        if m is None and n_simbad < int(args.max_simbad):
            m = resolve_simbad(g, simbad=simbad)
            if m is not None:
                n_simbad += 1
                time.sleep(0.05)

        if m is None:
            rows.append(
                {
                    "galaxy": g,
                    "ra_deg": np.nan,
                    "dec_deg": np.nan,
                    "sparc_metric": float(r["sparc_metric"]),
                    "coord_source": "missing",
                    "catalog_name": "",
                }
            )
            unresolved.append(g)
        else:
            rows.append(
                {
                    "galaxy": g,
                    "ra_deg": float(m["ra_deg"]),
                    "dec_deg": float(m["dec_deg"]),
                    "sparc_metric": float(r["sparc_metric"]),
                    "coord_source": str(m["coord_source"]),
                    "catalog_name": str(m["catalog_name"]),
                }
            )

        if (i + 1) % 25 == 0:
            print(f"processed {i + 1}/{len(base)}")

    out = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)

    unresolved_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"galaxy": unresolved}).to_csv(unresolved_csv, index=False)

    coverage = 1.0 - float(out["ra_deg"].isna().mean())
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "q_est_csv": str(q_est_path),
        "output_csv": str(out_csv),
        "unresolved_csv": str(unresolved_csv),
        "n_total": int(len(out)),
        "n_vizier": int(n_vizier),
        "n_simbad": int(n_simbad),
        "n_missing": int(len(unresolved)),
        "coverage": float(coverage),
        "unresolved_examples": unresolved[:20],
    }

    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
