#!/usr/bin/env python3
"""
fetch_psz2_clusters.py

Fetch PSZ2 Planck cluster catalog (J/A+A/594/A27) from VizieR.
Extract M_500, redshift, coordinates for the IRS closure trend analysis.
Augment with gas fractions from the literature (Eckert+2019, Ettori+2017).

Also samples Vikhlinin+2009 Chandra relaxed clusters (J/ApJ/692/1060)
which have individual M_gas measurements - useful for M_bar estimates.

Saves:
  repro_checks/raw/psz2_clusters.csv        + provenance JSON
  repro_checks/raw/vikhlinin09_clusters.csv + provenance JSON
  repro_checks/cluster_mass_summary.csv     (merged, ready for trend analysis)
"""

import hashlib, json, sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from astroquery.vizier import Vizier

# ── Constants ──────────────────────────────────────────────────────────────────
G_kpc      = 4.3009e-6   # (km/s)² kpc M_sun⁻¹
A0_KMS2PKC = 3702.813    # a₀ in (km/s)² kpc⁻¹  (= 1.2×10⁻¹⁰ m/s² converted)

# Literature gas fractions (Ettori+2017, Mantz+2016):
# f_gas ≈ 0.125 ± 0.010 at R_500 for M_500 > 3×10^14 M_sun
# A reasonable mean for clusters in PSZ2 range is ~0.12
F_GAS_MEAN  = 0.125     # M_gas / M_500
F_STAR_MEAN = 0.010     # M_star / M_500 (Lin+2003, Gonzalez+2007)
# → f_bar ≈ 0.135 total

# ── Output paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
RAW_DIR    = SCRIPT_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV    = SCRIPT_DIR / "cluster_mass_summary.csv"

viz = Vizier(row_limit=-1, timeout=60)

def save_raw(df, stem, meta):
    path = RAW_DIR / f"{stem}.csv"
    df.to_csv(path, index=False)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    (RAW_DIR / f"{stem}.provenance.json").write_text(
        json.dumps({**meta, "sha256": sha,
                    "fetched_utc": datetime.now(timezone.utc).isoformat()}, indent=2))
    print(f"  saved {path.name}  sha256={sha[:12]}…  ({len(df)} rows)")
    return path

# ══════════════════════════════════════════════════════════════════════════════
# 1.  PSZ2 — Planck+2016  J/A+A/594/A27
# ══════════════════════════════════════════════════════════════════════════════
print("=== PSZ2  J/A+A/594/A27 ===")
psz2_tables = viz.get_catalogs("J/A+A/594/A27")
print(f"  {len(psz2_tables)} tables:")
for t in psz2_tables:
    print(f"  {t.meta.get('name','?')}: {len(t)} rows  cols={t.colnames}")

# Find the main PSZ2 table
psz2_main = None
for t in psz2_tables:
    nm = t.meta.get("name", "")
    df = t.to_pandas()
    if "psz2" in nm.lower() or len(df) > 100:
        psz2_main = df
        psz2_tname = nm
        break

if psz2_main is None and len(psz2_tables) > 0:
    psz2_main  = psz2_tables[0].to_pandas()
    psz2_tname = psz2_tables[0].meta.get("name", "t0")

print(f"\nUsing table '{psz2_tname}': {len(psz2_main)} rows")
print("Columns:", psz2_main.columns.tolist())
print(psz2_main.head(3).to_string())

save_raw(psz2_main, "psz2_main",
         {"catalog": "J/A+A/594/A27", "table": psz2_tname,
          "reference": "Planck Collaboration 2016, A&A 594, A27"})

# ══════════════════════════════════════════════════════════════════════════════
# 2.  Vikhlinin+2009 Chandra clusters  J/ApJ/692/1060
#     These have individual gas+total mass, very well measured
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== Vikhlinin+2009  J/ApJ/692/1060 ===")
vik_tables = viz.get_catalogs("J/ApJ/692/1060")
print(f"  {len(vik_tables)} tables")
vik_main = None
for t in vik_tables:
    nm = t.meta.get("name", "")
    df = t.to_pandas()
    print(f"  {nm}: {len(df)} rows  cols={df.columns.tolist()[:8]}")
    if vik_main is None or len(df) > len(vik_main):
        vik_main = df
        vik_tname = nm

if vik_main is not None:
    print("\nSample:")
    print(vik_main.head(3).to_string())
    save_raw(vik_main, "vikhlinin09_main",
             {"catalog": "J/ApJ/692/1060", "table": vik_tname,
              "reference": "Vikhlinin+2009, ApJ 692, 1060"})

# ══════════════════════════════════════════════════════════════════════════════
# 3.  Try MCXC (X-ray cluster meta-catalog)  J/A+A/534/A109
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== MCXC  J/A+A/534/A109 ===")
mcxc_tables = viz.get_catalogs("J/A+A/534/A109")
print(f"  {len(mcxc_tables)} tables")
mcxc_main = None
for t in mcxc_tables:
    nm = t.meta.get("name", "")
    df = t.to_pandas()
    print(f"  {nm}: {len(df)} rows  cols={df.columns.tolist()[:8]}")
    if mcxc_main is None or len(df) > len(mcxc_main):
        mcxc_main = df
        mcxc_tname = nm

if mcxc_main is not None and len(mcxc_main) > 0:
    print("\nSample:")
    print(mcxc_main.head(3).to_string())
    save_raw(mcxc_main, "mcxc_main",
             {"catalog": "J/A+A/534/A109", "table": mcxc_tname,
              "reference": "Piffaretti+2011, A&A 534, A109"})

# ══════════════════════════════════════════════════════════════════════════════
# 4.  Build cluster mass summary
#     Compute M_bar from M_500 using literature baryon fractions,
#     then compute Q1_ref and store for the IRS deficit trend analysis
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== Building cluster_mass_summary.csv ===")

rows = []

def extract_cluster_rows(df, source_label, m500_col, z_col, name_col):
    """Extract and convert cluster data into standard rows."""
    for _, row in df.iterrows():
        try:
            name   = str(row.get(name_col, "?")).strip()
            m500v  = float(row[m500_col])
            # Determine units: PSZ2 uses 10^14 M_sun, others vary
            if 0.01 < m500v < 100:
                M500 = m500v * 1e14   # units: 10^14 M_sun → M_sun
            elif 12 < m500v < 16:
                M500 = 10**m500v      # log scale
            else:
                continue              # implausible value → skip

            z  = float(row.get(z_col, np.nan))

            # Baryonic mass from literature mean fractions
            M_gas  = F_GAS_MEAN  * M500
            M_star = F_STAR_MEAN * M500
            M_bar  = M_gas + M_star

            # IRS reference amplitude in (km/s)²:
            #   Q1_ref = sqrt(G * M_bar * a_irs)
            #   units: sqrt((km/s)²·kpc/M_sun × M_sun × (km/s)²/kpc) = km/s
            #   → Q1 in (km/s)²  (this is v_flat² predicted by deep MOND BTFR)
            Q1_ref = np.sqrt(G_kpc * M_bar * A0_KMS2PKC)

            # Newtonian virial velocity from σ–M scaling (Munari+2013):
            #   σ_DM [km/s] ≈ 1083 × (M_500 / 10^15 h⁻¹ M_sun)^0.336
            # Using h=0.7:
            sigma = 1083 * (M500 / 1e15 * 0.7)**0.336    # km/s
            sigma2 = sigma**2                              # (km/s)²

            # Baryonic Newtonian velocity at R_500 context
            # (just for reference; not used in main closure ratio)
            # R_500 ~ 1 Mpc = 1000 kpc for massive clusters
            R500_kpc = 1000.0  # rough; good enough for order-of-magnitude
            v_bar2_newt = G_kpc * M_bar / R500_kpc  # Newtonian baryonic at R_500
            Q1_cluster  = sigma2 - v_bar2_newt       # "extra" velocity²
            IRS_closure = Q1_cluster / Q1_ref if Q1_ref > 0 else np.nan

            rows.append({
                "name"       : name,
                "type"       : "cluster",
                "source"     : source_label,
                "redshift"   : z,
                "M500_Msun"  : M500,
                "M_bar_Msun" : M_bar,
                "M_gas_Msun" : M_gas,
                "M_star_Msun": M_star,
                "sigma_kms"  : sigma,
                "sigma2_kms2": sigma2,
                "Q1_ref_kms2"    : Q1_ref,
                "Q1_cluster_kms2": Q1_cluster,
                "IRS_closure"    : IRS_closure,
            })
        except (KeyError, ValueError, TypeError):
            continue
    return rows

# PSZ2 columns: inspect and map
print(f"\nPSZ2 columns: {psz2_main.columns.tolist()}")
# Typical PSZ2 columns include:  Name, GLON, GLAT, RAJ2000, DEJ2000,
#   SNR, z, Y_500, M_SZ (or MSZ), Q_neural
#
# Find mass column (could be MSZ, M_SZ, M500, etc.)
m500_col = None
for c in psz2_main.columns:
    cl = c.lower()
    if "msz" in cl or "m500" in cl or "m_500" in cl or cl == "msz":
        m500_col = c
        break

z_col = None
for c in psz2_main.columns:
    if c.lower() == "z" or c.lower() == "redshift":
        z_col = c
        break

name_col = psz2_main.columns[0]
for c in psz2_main.columns:
    if "name" in c.lower():
        name_col = c
        break

print(f"Mapped: name={name_col}, M500={m500_col}, z={z_col}")

if m500_col and z_col:
    extract_cluster_rows(psz2_main, "PSZ2_Planck2016", m500_col, z_col, name_col)
    print(f"  extracted {len(rows)} PSZ2 clusters so far")

# Vikhlinin if available
if vik_main is not None and len(vik_main) > 0:
    print(f"\nVikhlinin+2009 columns: {vik_main.columns.tolist()}")
    # typical cols: Cluster, z, M500, Mg500, T, etc.
    vik_m500_col = None
    vik_z_col    = None
    vik_name_col = vik_main.columns[0]
    for c in vik_main.columns:
        cl = c.lower()
        if ("m500" in cl or "m_500" in cl) and "g" not in cl:
            vik_m500_col = c
        elif cl == "z" or "redshift" in cl:
            vik_z_col = c
        elif "name" in cl or "cluster" in cl:
            vik_name_col = c
    if vik_m500_col and vik_z_col:
        n_before = len(rows)
        extract_cluster_rows(vik_main, "Vikhlinin+2009", vik_m500_col, vik_z_col, vik_name_col)
        print(f"  extracted {len(rows) - n_before} Vikhlinin clusters")

# Build DataFrame and save
cluster_df = pd.DataFrame(rows)
print(f"\nTotal cluster rows: {len(cluster_df)}")
if len(cluster_df) > 0:
    print(cluster_df[["name","M500_Msun","M_bar_Msun","Q1_ref_kms2",
                       "sigma_kms","IRS_closure"]].head(10).to_string())
    cluster_df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved → {OUT_CSV}")
else:
    print("ERROR: No cluster rows extracted. Check column mapping above.")
    sys.exit(1)
