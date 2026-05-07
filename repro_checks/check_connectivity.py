#!/usr/bin/env python3
"""
Test network connectivity and find accessible cluster mass catalogs.
Focus on VizieR-accessible catalogs with real data.
"""
import requests
import sys

# First check basic connectivity
print("=== Basic connectivity ===")
for url in [
    "https://vizier.cds.unistra.fr/",
    "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/AJ/152/157&-out.max=2",
    "https://ned.ipac.caltech.edu/",
]:
    try:
        r = requests.get(url, timeout=10)
        print(f"  {url[:60]}: {r.status_code} {len(r.content)} bytes")
    except Exception as e:
        print(f"  {url[:60]}: ERROR {e}")

# Check what the VizieR CLASH response actually says
print("\n=== CLASH catalog VizieR response head ===")
try:
    r = requests.get(
        "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJ/821/116&-out.max=5",
        timeout=10
    )
    print(r.text[:500])
except Exception as e:
    print(f"Error: {e}")

# Try PSZ2 Planck catalog (highly cited, should be on VizieR)
print("\n=== PSZ2 Planck catalog ===")
from astroquery.vizier import Vizier
viz = Vizier(row_limit=5)
for cat_id in [
    "J/A+A/594/A27",        # PSZ2
    "J/A+A/550/A131",       # PSZ1
    "J/ApJ/767/116",        # Vikhlinin+2009 Chandra clusters
    "J/MNRAS/392/1509",     # Pratt+2010 REXCESS
    "J/A+A/517/A92",        # Arnaud+2010 universal pressure profile
]:
    try:
        r = viz.get_catalogs(cat_id)
        if len(r) > 0:
            print(f"\n✓ {cat_id}: {len(r)} tables")
            for t in r:
                print(f"  {t.meta.get('name','?')}: {len(t)} rows, cols={t.colnames[:6]}")
                if len(t) > 0:
                    print(f"  Sample row: {dict(list(t[0].items())[:4])}")
        else:
            print(f"  {cat_id}: empty (0 tables)")
    except Exception as e:
        print(f"  {cat_id}: {e}")
