#!/usr/bin/env python3
"""
Probe VizieR HTTP API directly to check if catalogs exist,
then fall back to known cluster databases:
  - NASA/IPAC NED (ned.ipac.caltech.edu) 
  - CLASH public data (https://archive.stsci.edu/missions/clash/)
  - X-COP public data
Also tries alternative VizieR catalog IDs.
"""
import requests
import json

BASE_VIZ = "https://vizier.cds.unistra.fr/viz-bin/votable"

def check_viz_catalog(cat_id):
    """Check if a VizieR catalog exists via its HTTP API."""
    params = {
        "-source": cat_id,
        "-out.max": 2,
        "-out.form": "mini",
    }
    try:
        r = requests.get(BASE_VIZ, params=params, timeout=15)
        has_data = "TABLEDATA" in r.text or "DATA" in r.text
        size = len(r.text)
        return has_data, size, r.status_code
    except Exception as e:
        return False, 0, str(e)

print("=== Checking VizieR catalogs via HTTP ===\n")
for cat, label in [
    ("J/ApJ/821/116/table2", "CLASH Umetsu+2016 table2"),
    ("J/ApJ/821/116/table3", "CLASH Umetsu+2016 table3"),
    ("J/ApJ/805/79",         "CLASH Umetsu+2014 all clusters"),
    ("J/A+A/621/A39",        "X-COP Ettori+2019"),
    ("J/A+A/621/A41",        "X-COP Ghirardini+2019"),
    ("J/MNRAS/449/685",      "CCCP Hoekstra+2015"),
    ("J/AJ/152/157/table2",  "SPARC (known good)"),
    ("VIII/65A",             "Test: HIPASS"),
]:
    has_data, size, status = check_viz_catalog(cat)
    print(f"  {cat:<35}  data={has_data}  size={size:5d}  status={status}  [{label}]")

# ── Also check NASA/IPAC cluster catalogs via their API ──────────────────────
print("\n=== NASA/IPAC NED object query test ===")
# NED has cluster info via object query
try:
    r = requests.get(
        "https://ned.ipac.caltech.edu/srs/ObjectLookup",
        params={"name": "Abell 2744", "quiet": 1},
        timeout=10
    )
    print(f"  NED API accessible: {r.status_code}, response size={len(r.text)}")
except Exception as e:
    print(f"  NED API error: {e}")

# ── Check if CLASH public archive is reachable ──────────────────────────────
print("\n=== MAST/CLASH archive check ===")
try:
    r = requests.head("https://archive.stsci.edu/missions/clash/", timeout=10)
    print(f"  MAST CLASH accessible: {r.status_code}")
except Exception as e:
    print(f"  MAST error: {e}")

# ── Check SIMBAD for cluster masses ─────────────────────────────────────────
print("\n=== SIMBAD access test ===")
try:
    from astroquery.simbad import Simbad
    result = Simbad.query_object("Abell 2744")
    print(f"  SIMBAD accessible: {result is not None}")
    if result is not None:
        print(f"  cols: {result.colnames}")
except Exception as e:
    print(f"  SIMBAD error: {e}")
