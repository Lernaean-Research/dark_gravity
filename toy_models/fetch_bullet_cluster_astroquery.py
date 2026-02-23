"""Find Bullet Cluster (1E 0657-56) datasets via astroquery.

This script does *discovery* (observation metadata), not full reduction.
It is meant to answer: "what public datasets exist and what are their IDs?"

Why this helps the cluster-profile adapter
-----------------------------------------
To run the 1D cluster-profile q_est adapter (`toy_models/cluster_profile_q_est.py`) you
ultimately need radial profiles like M_tot(<r) and M_bar(<r).

Those profiles can come from:
- published tables / model parameters (fastest), or
- reduction of raw observations (X-ray + lensing).

This script helps you find the relevant raw observations quickly:
- Chandra observation log: HEASARC `chanmaster`
- XMM observation log: HEASARC `xmmmaster`
- ROSAT observation log: HEASARC `rosmaster`

Outputs
-------
Writes one CSV per catalog under `--out-dir`.

Example
-------
python toy_models/fetch_bullet_cluster_astroquery.py --target "1E 0657-56" --radius-arcmin 12
"""

from __future__ import annotations

import argparse
from pathlib import Path

import astropy.units as u
from astropy.coordinates import SkyCoord


def _write_table_csv(path: Path, table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Astropy Table supports .write
    table.write(path, format="csv", overwrite=True)


def _safe_len(x) -> int:
    try:
        return int(len(x))
    except Exception:
        return -1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", type=str, default="1E 0657-56")
    p.add_argument("--radius-arcmin", type=float, default=12.0)
    p.add_argument("--out-dir", type=Path, default=Path("toy_models/out_cluster_fetch"))
    args = p.parse_args()

    target = args.target
    radius = float(args.radius_arcmin) * u.arcmin

    coord = SkyCoord.from_name(target)
    print(f"Resolved {target!r} -> ra={coord.ra.deg:.6f} deg dec={coord.dec.deg:.6f} deg")

    # HEASARC is the most reliable/fast for observation metadata.
    from astroquery.heasarc import Heasarc

    h = Heasarc()

    catalogs = {
        "chanmaster": "Chandra observation log (ObsIDs, exposure, detector)",
        "xmmmaster": "XMM-Newton observation log (ObsIDs, duration)",
        "rosmaster": "ROSAT observation log",
    }

    for cat, desc in catalogs.items():
        try:
            t = h.query_region(coord, catalog=cat, radius=radius)
            print(f"{cat}: {_safe_len(t)} rows  ({desc})")
            out = args.out_dir / f"{cat}.csv"
            _write_table_csv(out, t)
            print(f"  wrote {out.as_posix()}")
        except Exception as e:
            print(f"{cat}: FAILED ({type(e).__name__}: {e})")

    print("\nNext step:")
    print("- Use the ObsIDs in these CSVs to download raw data from the mission archive (CDA/XSA/ROSAT),")
    print("  OR locate published mass-profile tables/fit parameters for Bullet Cluster and skip raw reduction.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
