#!/usr/bin/env python3
"""Search VizieR for CLASH and X-COP catalogs to find correct catalog IDs."""
from astroquery.vizier import Vizier
import time

viz = Vizier(row_limit=3)

# Try different catalog ID formats
test_ids = [
    "J/ApJ/821/116",
    "J/A+A/621/A39",
    "J/A+A/621/A40",  # maybe wrong table number
]

# Also try a catalog search by keyword
print("=== Catalog search: CLASH ===")
try:
    clash_results = Vizier.find_catalogs("CLASH lensing cluster mass Umetsu 2016")
    for k, v in list(clash_results.items())[:5]:
        print(f"  {k}: {v.description}")
except Exception as e:
    print(f"  search error: {e}")

print("\n=== Catalog search: X-COP ===")
try:
    xcop_results = Vizier.find_catalogs("X-COP cluster gas fraction Ettori 2019")
    for k, v in list(xcop_results.items())[:5]:
        print(f"  {k}: {v.description}")
except Exception as e:
    print(f"  search error: {e}")

print("\n=== Direct table listing ===")
for cat_id in test_ids:
    try:
        tables = Vizier.find_catalogs(cat_id)
        print(f"\n{cat_id}: {len(tables)} matches")
        for k, v in list(tables.items())[:3]:
            print(f"  {k}: {v.description}")
    except Exception as e:
        print(f"{cat_id}: error {e}")

print("\n=== Direct get_catalogs attempts ===")
for cat_id in test_ids:
    try:
        r = viz.get_catalogs(cat_id)
        print(f"\n{cat_id}: returned {len(r)} tables")
        for t in r:
            print(f"  {t.meta.get('name','?')}: {t.colnames[:8]}")
    except Exception as e:
        print(f"{cat_id}: error {e}")
