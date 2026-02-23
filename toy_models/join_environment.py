"""Join an external environment catalog onto an existing SPARC-derived summary table.

This is intentionally stdlib-only and does not require re-running the rotmod fit.

Typical use (2M++ density proxy):
  ./.venv/Scripts/python.exe toy_models/join_environment.py \
      --summary toy_models/out_sparc_runs_full_with_composition/summary.csv \
      --env toy_models/data/external_environment_twompp.csv \
      --out toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv \
      --prefix env_twompp_ \
      --env-cols delta_external in_twompp_grid

The join key is the `galaxy` string column.

"""

from __future__ import annotations

import argparse
import csv


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Join environment catalog columns into summary.csv")
    p.add_argument("--summary", required=True, help="Input summary.csv (must include 'galaxy' column)")
    p.add_argument("--env", required=True, help="Environment CSV (must include 'galaxy' column)")
    p.add_argument("--out", required=True, help="Output CSV path")
    p.add_argument("--prefix", default="env_", help="Prefix to add to joined environment columns")
    p.add_argument(
        "--env-cols",
        nargs="*",
        default=["delta_external", "in_twompp_grid"],
        help="Environment columns to join (default: delta_external in_twompp_grid)",
    )
    p.add_argument(
        "--env-key",
        default="galaxy",
        help="Key column name in env CSV (default: galaxy)",
    )
    p.add_argument(
        "--summary-key",
        default="galaxy",
        help="Key column name in summary CSV (default: galaxy)",
    )
    return p.parse_args()


def _norm_key(s: str) -> str:
    return (s or "").strip()


def _load_env(path: str, key_col: str) -> tuple[list[str], dict[str, dict[str, str]]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError(f"Env CSV has no header: {path}")
        cols = list(r.fieldnames)
        if key_col not in cols:
            raise RuntimeError(f"Env CSV missing key column '{key_col}': {path}")
        by_key: dict[str, dict[str, str]] = {}
        for row in r:
            k = _norm_key(row.get(key_col, ""))
            if not k:
                continue
            by_key[k] = row
        return cols, by_key


def main() -> None:
    args = parse_args()

    _, env_by_key = _load_env(args.env, args.env_key)

    with open(args.summary, "r", encoding="utf-8", newline="") as f_in:
        r = csv.DictReader(f_in)
        if r.fieldnames is None:
            raise RuntimeError(f"Summary CSV has no header: {args.summary}")
        in_fields = list(r.fieldnames)
        if args.summary_key not in in_fields:
            raise RuntimeError(f"Summary CSV missing key column '{args.summary_key}': {args.summary}")

        out_env_fields = [f"{args.prefix}{c}" for c in args.env_cols]
        out_fields = in_fields + [c for c in out_env_fields if c not in in_fields]

        with open(args.out, "w", encoding="utf-8", newline="") as f_out:
            w = csv.DictWriter(f_out, fieldnames=out_fields)
            w.writeheader()

            n_in = 0
            n_join = 0
            for row in r:
                n_in += 1
                k = _norm_key(row.get(args.summary_key, ""))
                env_row = env_by_key.get(k)
                if env_row is not None:
                    n_join += 1
                    for c in args.env_cols:
                        row[f"{args.prefix}{c}"] = env_row.get(c, "")
                else:
                    for c in args.env_cols:
                        row.setdefault(f"{args.prefix}{c}", "")
                w.writerow(row)

    miss = n_in - n_join
    print(f"Wrote: {args.out}")
    print(f"Joined environment rows: {n_join}/{n_in} (missing {miss})")


if __name__ == "__main__":
    main()
