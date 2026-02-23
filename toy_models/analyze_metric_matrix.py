"""Compute a correlation matrix between two sets of columns from summary.csv (stdlib-only).

Purpose
-------
This script is a broad "scan" tool: given `summary.csv` produced by
`toy_models/sparc_rotmod_runner.py`, compute Pearson r and Spearman rho for:

  (x in X-columns) × (y in Y-columns)

It is intended for face-value screening of correlations like:
- "center composition" proxies (gas/disk/bulge fractions, SBdisk, MHI, ...)
  versus
- "edge behavior" proxies (Q, sqrt(Q), outer residual diagnostics, ...)

Usage
-----
Example (composition vs edge behavior):
  ./.venv/Scripts/python.exe toy_models/analyze_metric_matrix.py \
      --summary toy_models/out_all/summary.csv \
      --x-pattern "frac_*" --x "sparc_SBdisk_solLum_pc2" --x "sparc_MHI_1e9solMass" \
      --y "q_best_kms2" --y "v_extra_asym_kms" --y "outer_resid_rms_z" \
      --export toy_models/out_all/comp_vs_edge_correlations.csv

Patterns use fnmatch (glob-like): "frac_*", "sparc_*", "outer_*", etc.

Notes
-----
- Pairwise complete cases (drops NaN per pair).
- Spearman uses average ranks for ties.
- This is not a causal analysis; it’s a triage tool.

"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CorrRow:
    x: str
    y: str
    n: int
    pearson_r: float
    spearman_rho: float


def _is_finite(x: float) -> bool:
    return math.isfinite(x)


def _parse_float(s: str) -> float:
    s = (s or "").strip()
    if not s:
        return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def _read_summary(path: str) -> tuple[list[str], list[dict[str, float]]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError("summary.csv has no header")
        fieldnames = list(r.fieldnames)
        rows: list[dict[str, float]] = []
        for row in r:
            parsed: dict[str, float] = {}
            for k in fieldnames:
                if k == "galaxy":
                    continue
                parsed[k] = _parse_float(row.get(k, ""))
            rows.append(parsed)
        return fieldnames, rows


def _paired_vectors(rows: list[dict[str, float]], x: str, y: str) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    for row in rows:
        xv = row.get(x, float("nan"))
        yv = row.get(y, float("nan"))
        if _is_finite(xv) and _is_finite(yv):
            xs.append(xv)
            ys.append(yv)
    return xs, ys


def pearson_r(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0.0 or syy <= 0.0:
        return float("nan")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / math.sqrt(sxx * syy)


def _rankdata(values: list[float]) -> list[float]:
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n

    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = 0.5 * ((i + 1) + (j + 1))
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1

    return ranks


def spearman_rho(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    rx = _rankdata(xs)
    ry = _rankdata(ys)
    return pearson_r(rx, ry)


def _format_float(x: float) -> str:
    if not math.isfinite(x):
        return "nan"
    return f"{x:+.4f}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute correlation matrix between column sets from summary.csv")
    p.add_argument("--summary", required=True, help="Path to summary.csv")
    p.add_argument("--x", action="append", default=[], help="X column name (can repeat)")
    p.add_argument("--y", action="append", default=[], help="Y column name (can repeat)")
    p.add_argument("--x-pattern", action="append", default=[], help="Glob pattern for X columns (fnmatch)")
    p.add_argument("--y-pattern", action="append", default=[], help="Glob pattern for Y columns (fnmatch)")
    p.add_argument("--min-n", type=int, default=30, help="Minimum pairwise N to report")
    p.add_argument("--export", default="", help="Optional CSV path to write all results")
    p.add_argument("--top", type=int, default=30, help="Print top K by |Spearman| then |Pearson|")
    return p.parse_args()


def _select_columns(fieldnames: list[str], explicit: list[str], patterns: list[str]) -> list[str]:
    cols = set(explicit)
    for pat in patterns:
        for fn in fieldnames:
            if fn == "galaxy":
                continue
            if fnmatch.fnmatch(fn, pat):
                cols.add(fn)
    return sorted(cols)


def main() -> None:
    args = parse_args()
    fieldnames, rows = _read_summary(args.summary)

    available = set(fieldnames)
    for c in args.x + args.y:
        if c and c not in available:
            raise SystemExit(f"Column not found: {c}")

    xs = _select_columns(fieldnames, args.x, args.x_pattern)
    ys = _select_columns(fieldnames, args.y, args.y_pattern)
    if not xs:
        raise SystemExit("No X columns selected. Use --x and/or --x-pattern")
    if not ys:
        raise SystemExit("No Y columns selected. Use --y and/or --y-pattern")

    results: list[CorrRow] = []
    for x in xs:
        for y in ys:
            if x == y:
                continue
            xv, yv = _paired_vectors(rows, x, y)
            n = len(xv)
            if n < args.min_n:
                continue
            r = pearson_r(xv, yv)
            rho = spearman_rho(xv, yv)
            results.append(CorrRow(x=x, y=y, n=n, pearson_r=r, spearman_rho=rho))

    results.sort(key=lambda cr: (
        -abs(cr.spearman_rho) if math.isfinite(cr.spearman_rho) else float("-inf"),
        -abs(cr.pearson_r) if math.isfinite(cr.pearson_r) else float("-inf"),
        cr.x,
        cr.y,
    ))

    print("Correlation matrix (pairwise complete cases)")
    print(f"Summary: {args.summary}")
    print(f"X columns: {len(xs)} | Y columns: {len(ys)} | Results: {len(results)}")
    print("")
    print(f"{'X':34s} {'Y':34s} {'N':>5s} {'Pearson r':>10s} {'Spearman ρ':>12s}")
    for cr in results[: max(args.top, 0)]:
        print(f"{cr.x:34.34s} {cr.y:34.34s} {cr.n:5d} {_format_float(cr.pearson_r):>10s} {_format_float(cr.spearman_rho):>12s}")

    if args.export:
        with open(args.export, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["x", "y", "n", "pearson_r", "spearman_rho"])
            for cr in results:
                w.writerow([cr.x, cr.y, cr.n, cr.pearson_r, cr.spearman_rho])
        print("")
        print(f"Wrote: {args.export}")


if __name__ == "__main__":
    main()
