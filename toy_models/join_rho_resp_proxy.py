"""Join rho-response proxy summaries into the main SPARC summary table.

Reads:
- toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv
- toy_models/out_rho_resp_proxy/rho_resp_proxy_catalogue.csv

Writes:
- toy_models/out_sparc_runs_full_with_composition/summary_with_env_with_rho_proxy.csv

Join key: galaxy

Dependency-light: stdlib only.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


RHO_FIELDS_ORDER = [
    "n_outer",
    "outer_rule",
    "rmax_kpc",
    "rmin_outer_kpc",
    "slope_outer_pos",
    "n_slope_pos",
    "slope_outer_abs",
    "n_slope_abs",
    "dv2_outer_log_slope",
    "n_dv2_log_slope",
    "frac_rho_pos_outer",
]


def read_map(path: Path, *, key: str) -> dict[str, dict[str, str]]:
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {path}")
        out: dict[str, dict[str, str]] = {}
        for row in reader:
            k = (row.get(key) or "").strip()
            if not k:
                continue
            out[k] = row
        return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)

    p.add_argument(
        "--summary",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv"),
    )
    p.add_argument(
        "--rho",
        type=Path,
        default=Path("toy_models/out_rho_resp_proxy/rho_resp_proxy_catalogue.csv"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path(
            "toy_models/out_sparc_runs_full_with_composition/summary_with_env_with_rho_proxy.csv"
        ),
    )

    args = p.parse_args()

    rho_map = read_map(args.rho, key="galaxy")

    missing_in_rho: list[str] = []
    used = 0

    with args.summary.open("r", newline="") as fin:
        reader = csv.DictReader(fin)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {args.summary}")

        base_fields = list(reader.fieldnames)
        out_fields = base_fields + [f"rho_{name}" for name in RHO_FIELDS_ORDER]

        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=out_fields)
            writer.writeheader()

            for row in reader:
                galaxy = (row.get("galaxy") or "").strip()
                rho_row = rho_map.get(galaxy)
                if rho_row is None:
                    missing_in_rho.append(galaxy)
                    for name in RHO_FIELDS_ORDER:
                        row[f"rho_{name}"] = ""
                else:
                    used += 1
                    for name in RHO_FIELDS_ORDER:
                        row[f"rho_{name}"] = rho_row.get(name, "")

                writer.writerow(row)

    print(f"Wrote: {args.out}")
    print(f"Matched galaxies: {used} / {len(rho_map)} rho rows")
    if missing_in_rho:
        missing_preview = ", ".join(missing_in_rho[:8])
        print(f"Missing rho rows for {len(missing_in_rho)} galaxies (first few: {missing_preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
