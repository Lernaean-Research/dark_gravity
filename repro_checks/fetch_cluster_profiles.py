#!/usr/bin/env python3
"""
fetch_cluster_profiles.py

Fetch real cluster mass profiles from VizieR for IRS closure analysis:
  - CLASH:  J/ApJ/821/116  — Umetsu+2016 weak+strong lensing masses, 20 clusters
  - X-COP:  J/A+A/621/A39  — Ettori+2019 hydrostatic masses + gas fractions, 12 clusters

Saves raw tables to repro_checks/raw/ with SHA-256 provenance sidecar files.
Saves merged cluster summary to repro_checks/cluster_mass_summary.csv
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from astroquery.vizier import Vizier

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
RAW_DIR = SCRIPT_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUT_CSV = SCRIPT_DIR / "cluster_mass_summary.csv"

# ── VizieR helper ──────────────────────────────────────────────────────────────
viz = Vizier(row_limit=-1, timeout=60)

def fetch_catalog(catalog_id, label):
    """Fetch all tables in a VizieR catalog. Returns list of (table_name, DataFrame)."""
    print(f"\n[fetch] {label}  ({catalog_id}) …", flush=True)
    result = viz.get_catalogs(catalog_id)
    tables = []
    for tbl in result:
        name = tbl.meta.get("name", "?")
        df = tbl.to_pandas()
        print(f"  table {name}: {len(df)} rows, cols={list(df.columns[:8])}")
        tables.append((name, df))
    return tables

def save_raw(df, stem, provenance_meta):
    """Write CSV + SHA-256 sidecar."""
    csv_path = RAW_DIR / f"{stem}.csv"
    df.to_csv(csv_path, index=False)
    sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    meta = {**provenance_meta, "sha256": sha, "fetched_utc": datetime.now(timezone.utc).isoformat()}
    (RAW_DIR / f"{stem}.provenance.json").write_text(json.dumps(meta, indent=2))
    print(f"  saved {csv_path.name}  sha256={sha[:12]}…")
    return csv_path

# ══════════════════════════════════════════════════════════════════════════════
# 1. CLASH — Umetsu+2016   J/ApJ/821/116
#    Table 2 (table2): cluster-level WL masses M200c, r200c, concentration
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("CLASH  J/ApJ/821/116")
clash_tables = fetch_catalog("J/ApJ/821/116", "CLASH Umetsu+2016")

clash_df = None
for name, df in clash_tables:
    stem = f"clash_{name.replace('/', '_').replace(' ', '_')}"
    save_raw(df, stem, {"catalog": "J/ApJ/821/116", "table": name})
    # Find the main mass table (usually "table2" for cluster-level summary)
    if "table2" in name.lower() or "table1" in name.lower():
        clash_df = df
        clash_name = name

if clash_df is None and clash_tables:
    clash_df = clash_tables[0][1]
    clash_name = clash_tables[0][0]

print(f"\nUsing CLASH table '{clash_name}' for cluster masses")
print(clash_df.columns.tolist())
print(clash_df.head())

# ══════════════════════════════════════════════════════════════════════════════
# 2. X-COP — Ettori+2019   J/A+A/621/A39
#    Contains hydrostatic masses, gas masses, f_gas
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("X-COP  J/A+A/621/A39")
xcop_tables = fetch_catalog("J/A+A/621/A39", "X-COP Ettori+2019")

xcop_df = None
for name, df in xcop_tables:
    stem = f"xcop_{name.replace('/', '_').replace(' ', '_')}"
    save_raw(df, stem, {"catalog": "J/A+A/621/A39", "table": name})
    if xcop_df is None:
        xcop_df = df
        xcop_name = name

print(f"\nUsing X-COP table '{xcop_name}'")
print(xcop_df.columns.tolist())
print(xcop_df.head())

# ══════════════════════════════════════════════════════════════════════════════
# 3. Build merged cluster summary
#    We want: cluster_name, M_bar_Msun, M_total_Msun, source
#    Units note: VizieR often uses 10^14 M_sun for cluster masses
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Building merged cluster_mass_summary.csv …")

rows = []

# ── CLASH ──────────────────────────────────────────────────────────────────
# Columns vary — we look for M200, Mgas200, and cluster name
# Print all columns to diagnose
print("\nCLASH columns:", clash_df.columns.tolist())

# Map common naming patterns
clash_col_map = {}
for col in clash_df.columns:
    cl = col.lower()
    if "name" in cl or "cluster" in cl:
        clash_col_map["name"] = col
    elif col in ("M200", "M200c", "__M200", "logM200") or "m200" in cl:
        clash_col_map["M200"] = col
    elif "mgas" in cl or "m_gas" in cl:
        clash_col_map["Mgas"] = col
    elif "fgas" in cl or "fg" == cl or "f_gas" in cl:
        clash_col_map["fgas"] = col

print("Mapped CLASH columns:", clash_col_map)

for _, row in clash_df.iterrows():
    name = str(row.get(clash_col_map.get("name", clash_df.columns[0]), "?"))
    try:
        # M200 usually stored as 10^14 M_sun or log(M_sun); check magnitude
        m200_raw = float(row[clash_col_map["M200"]]) if "M200" in clash_col_map else np.nan
        # If value is ~0.1–30 → units are 1e14 M_sun; if 13–15 → log10(M_sun)
        if 10 < m200_raw < 20:  # log scale
            M_total = 10**m200_raw
        elif 0.01 < m200_raw < 100:  # 1e14 M_sun units
            M_total = m200_raw * 1e14
        else:
            M_total = np.nan

        # Gas mass
        if "Mgas" in clash_col_map:
            mgas_raw = float(row[clash_col_map["Mgas"]])
            if mgas_raw < 50:
                M_gas = mgas_raw * 1e14
            else:
                M_gas = mgas_raw
        elif "fgas" in clash_col_map and not np.isnan(M_total):
            fg = float(row[clash_col_map["fgas"]])
            M_gas = fg * M_total
        else:
            # Typical cluster gas fraction ~15%
            M_gas = 0.15 * M_total if not np.isnan(M_total) else np.nan

        # Stellar mass ~1e12 M_sun typical; use 1% of total if not available
        M_star = 0.01 * M_total if not np.isnan(M_total) else np.nan
        M_bar = M_gas + M_star if (not np.isnan(M_gas) and not np.isnan(M_star)) else M_gas

        rows.append({
            "cluster": name.strip(),
            "source": "CLASH_Umetsu2016",
            "M_total_Msun": M_total,
            "M_gas_Msun": M_gas,
            "M_star_Msun": M_star,
            "M_bar_Msun": M_bar,
            "f_bar": M_bar / M_total if (not np.isnan(M_bar) and not np.isnan(M_total) and M_total > 0) else np.nan,
        })
    except (KeyError, ValueError, TypeError) as e:
        print(f"  CLASH: skip row {name}: {e}")

# ── X-COP ──────────────────────────────────────────────────────────────────
print("\nX-COP columns:", xcop_df.columns.tolist())

xcop_col_map = {}
for col in xcop_df.columns:
    cl = col.lower()
    if "name" in cl or "cluster" in cl:
        xcop_col_map["name"] = col
    elif col in ("M500", "M_500", "M500c") or "m500" in cl and "gas" not in cl and "500" in col:
        xcop_col_map["M500"] = col
    elif "mgas" in cl or "m_gas" in cl or ("gas" in cl and "m" in cl):
        xcop_col_map["Mgas"] = col
    elif "fgas" in cl or "f_gas" in cl or col == "fg":
        xcop_col_map["fgas"] = col

print("Mapped X-COP columns:", xcop_col_map)

for _, row in xcop_df.iterrows():
    name = str(row.get(xcop_col_map.get("name", xcop_df.columns[0]), "?"))
    try:
        m_key = xcop_col_map.get("M500") or xcop_col_map.get("M200")
        if m_key is None:
            continue
        m_raw = float(row[m_key])
        if 10 < m_raw < 20:
            M_total = 10**m_raw
        elif 0.01 < m_raw < 100:
            M_total = m_raw * 1e14
        else:
            M_total = np.nan

        if "Mgas" in xcop_col_map:
            mgas_raw = float(row[xcop_col_map["Mgas"]])
            M_gas = mgas_raw * 1e14 if mgas_raw < 50 else mgas_raw
        elif "fgas" in xcop_col_map and not np.isnan(M_total):
            fg = float(row[xcop_col_map["fgas"]])
            M_gas = fg * M_total
        else:
            M_gas = 0.15 * M_total if not np.isnan(M_total) else np.nan

        M_star = 0.01 * M_total if not np.isnan(M_total) else np.nan
        M_bar = M_gas + M_star if (not np.isnan(M_gas) and not np.isnan(M_star)) else M_gas

        rows.append({
            "cluster": name.strip(),
            "source": "XCOP_Ettori2019",
            "M_total_Msun": M_total,
            "M_gas_Msun": M_gas,
            "M_star_Msun": M_star,
            "M_bar_Msun": M_bar,
            "f_bar": M_bar / M_total if (not np.isnan(M_bar) and not np.isnan(M_total) and M_total > 0) else np.nan,
        })
    except (KeyError, ValueError, TypeError) as e:
        print(f"  XCOP: skip row {name}: {e}")

# ── Save ───────────────────────────────────────────────────────────────────
cluster_df = pd.DataFrame(rows)
print(f"\nTotal cluster rows: {len(cluster_df)}")
print(cluster_df.to_string())
cluster_df.to_csv(OUT_CSV, index=False)
print(f"\nSaved → {OUT_CSV}")
