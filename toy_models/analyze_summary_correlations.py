"""Analyze correlations from SPARC rotmod runner summary.csv (stdlib-only).

Purpose
-------
Given `summary.csv` produced by `toy_models/sparc_rotmod_runner.py`, this script:
- computes pairwise correlations between chosen columns
- reports both Pearson r and Spearman rho (rank correlation)
- handles NaN/missing values transparently

This is intended to make falsifiability checks reproducible without adding numpy/scipy.

Usage
-----
Default (analyzes a standard set of hypothesis-driven pairs):
  ./.venv/Scripts/python.exe toy_models/analyze_summary_correlations.py --summary toy_models/out_sparc_runs_sm_metrics/summary.csv

Custom columns:
  ./.venv/Scripts/python.exe toy_models/analyze_summary_correlations.py --summary <path> --x gbar_half_rt_kms2_per_kpc --y q_best_kms2

Export full correlation table (CSV):
  ./.venv/Scripts/python.exe toy_models/analyze_summary_correlations.py --summary <path> --export toy_models/out_sparc_runs_sm_metrics/correlations.csv

"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PairResult:
    x: str
    y: str
    n: int
    pearson_r: float
    spearman_rho: float


def _is_finite(x: float) -> bool:
    return math.isfinite(x)


def _parse_float(s: str) -> float:
    s = s.strip()
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
                parsed[k] = _parse_float(row.get(k, "")) if k != "galaxy" else float("nan")
            # keep galaxy name separately as raw string? we don't need it for correlations.
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
    """Assign average ranks (1..n) with tie handling."""
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n

    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        # average rank for ties; ranks are 1-based
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


def iter_default_pairs() -> Iterable[tuple[str, str]]:
    # Hypothesis-driven defaults: "center action" -> "edge reaction" and outer diagnostics.
    yield ("gbar_half_rt_kms2_per_kpc", "q_best_kms2")
    yield ("s_in_dlng_dlnr", "q_best_kms2")
    yield ("gbar_half_rt_kms2_per_kpc", "v_extra_asym_kms")
    yield ("s_in_dlng_dlnr", "v_extra_asym_kms")
    yield ("gbar_half_rt_kms2_per_kpc", "r_t_kpc")
    yield ("s_in_dlng_dlnr", "outer_resid_mean_z")
    yield ("s_in_dlng_dlnr", "outer_resid_rms_z")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute Pearson/Spearman correlations from summary.csv")
    p.add_argument("--summary", required=True, help="Path to summary.csv")
    p.add_argument("--x", default="", help="X column name (optional; if set requires --y)")
    p.add_argument("--y", default="", help="Y column name (optional; if set requires --x)")
    p.add_argument("--export", default="", help="Optional path to write correlations CSV")
    return p.parse_args()


def _format_float(x: float) -> str:
    if not math.isfinite(x):
        return "nan"
    return f"{x:+.4f}"


def main() -> None:
    args = parse_args()
    fieldnames, rows = _read_summary(args.summary)

    # Determine pairs
    pairs: list[tuple[str, str]] = []
    if bool(args.x) ^ bool(args.y):
        raise SystemExit("If specifying custom columns, provide both --x and --y")
    if args.x and args.y:
        pairs = [(args.x, args.y)]
    else:
        pairs = list(iter_default_pairs())

    # Validate requested columns
    available = set(fieldnames)
    for x, y in pairs:
        if x not in available:
            raise SystemExit(f"Column not found: {x}")
        if y not in available:
            raise SystemExit(f"Column not found: {y}")

    results: list[PairResult] = []
    for x, y in pairs:
        xs, ys = _paired_vectors(rows, x, y)
        r = pearson_r(xs, ys)
        rho = spearman_rho(xs, ys)
        results.append(PairResult(x=x, y=y, n=len(xs), pearson_r=r, spearman_rho=rho))

    # Print a compact table
    print("Correlations (pairwise complete cases)")
    print(f"Summary: {args.summary}")
    print("")
    print(f"{'X':38s} {'Y':28s} {'N':>5s} {'Pearson r':>10s} {'Spearman ρ':>12s}")
    for pr in results:
        print(f"{pr.x:38.38s} {pr.y:28.28s} {pr.n:5d} {_format_float(pr.pearson_r):>10s} {_format_float(pr.spearman_rho):>12s}")

    if args.export:
        with open(args.export, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["x", "y", "n", "pearson_r", "spearman_rho"])
            for pr in results:
                w.writerow([pr.x, pr.y, pr.n, pr.pearson_r, pr.spearman_rho])
        print("")
        print(f"Wrote: {args.export}")


if __name__ == "__main__":
    main()
