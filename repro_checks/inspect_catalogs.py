#!/usr/bin/env python3
"""Quick inspection of VizieR catalog tables to find correct column names."""
from astroquery.vizier import Vizier

viz = Vizier(row_limit=5)

for cat_id, label in [("J/ApJ/821/116", "CLASH"), ("J/A+A/621/A39", "X-COP")]:
    print(f"\n{'='*60}")
    print(f"{label}  {cat_id}")
    r = viz.get_catalogs(cat_id)
    for t in r:
        name = t.meta.get("name", "?")
        print(f"\n  TABLE: {name}  ({len(t)} rows)")
        print(f"  COLS:  {t.colnames}")
        if len(t) > 0:
            print(t[:3])
    if len(r) == 0:
        print("  ** No tables returned!")
