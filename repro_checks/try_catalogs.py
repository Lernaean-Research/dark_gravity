#!/usr/bin/env python3
"""Try various astroquery approaches to access CLASH and X-COP catalogs."""
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord

viz = Vizier(row_limit=-1)

# Method 1: Query constraints directly on catalog tables
print("=== Method 1: query_constraints on specific tables ===")
for tbl in ["J/ApJ/821/116/table1", "J/ApJ/821/116/table2", "J/ApJ/821/116/table3"]:
    try:
        r = Vizier(row_limit=5).query_constraints(catalog=tbl)
        print(f"\n{tbl}: {len(r)} result sets")
        for t in r:
            print(f"  cols: {t.colnames[:10]}")
            print(t[:2])
    except Exception as e:
        print(f"{tbl}: {e}")

print("\n=== Method 2: find_catalogs with ApJ ===")
try:
    r = Vizier.find_catalogs("J/ApJ/821/116")
    print(f"Found: {list(r.keys())}")
    for k, v in r.items():
        print(f"  {k}: {v.description}")
        if hasattr(v, 'tables'):
            print(f"    tables: {v.tables}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Method 3: X-COP direct ===")
for tbl in ["J/A+A/621/A39/table1", "J/A+A/621/A39/table2", "J/A+A/621/A39/table3"]:
    try:
        r = Vizier(row_limit=5).query_constraints(catalog=tbl)
        print(f"\n{tbl}: {len(r)} result sets")
        for t in r:
            print(f"  cols: {t.colnames[:10]}")
            print(t[:2])
    except Exception as e:
        print(f"{tbl}: {e}")

print("\n=== Method 4: Try other known cluster lensing catalogs ===")
# Hoekstra+2015 CCCP weak lensing
# Herbonnet+2020  
# Mantz+2016 WtG
alt_cats = [
    "J/MNRAS/449/685",   # Hoekstra+2015 CCCP
    "J/ApJ/805/79",       # Umetsu+2014 CLASH-WL 20 clusters
    "J/ApJ/795/163",      # Applegate+2014 WtG
    "J/A+A/621/A41",      # X-COP Ghirardini+2019
    "J/A+A/621/A40",      # X-COP Bartalucci+2019
    "J/A+A/621/A38",      # X-COP
]
for cat in alt_cats:
    try:
        r = Vizier(row_limit=3).get_catalogs(cat)
        if len(r) > 0:
            print(f"\n{cat}: {len(r)} tables")
            for t in r:
                print(f"  {t.meta.get('name','?')}: cols={t.colnames[:6]}")
        else:
            print(f"{cat}: empty")
    except Exception as e:
        print(f"{cat}: {e}")
