"""Compare old fitted-Q analyses to new robust Q_est analyses (stdlib-only).

This script targets the most common SPARC analysis pattern in this repo:
"composition proxies" X versus "edge amplitude" Y.

Old edge-amplitude proxies (from summary.csv):
- q_best_kms2 (fitted, constrained Q>=0)
- v_extra_asym_kms = sqrt(q_best_kms2)

New edge-amplitude proxies (from q_est.csv):
- q_est_kms2 (robust outer-location of Δ=Vobs^2-Vbar^2; can be negative)
- v_est_asym_kms = sqrt(max(q_est_kms2,0))

Outputs
-------
- CSV with per-X correlations against each Y (old and new)
- A "delta" view to see how correlation strength changes when replacing Q_best with Q_est

Usage
-----
  ./.venv/Scripts/python.exe toy_models/compare_old_new_q_analyses.py \
      --summary toy_models/out_sparc_runs_full_with_composition/summary.csv \
      --q-est toy_models/out_sparc_runs_full_with_composition/q_est.csv \
      --out-csv toy_models/out_q_est_analysis/comp_vs_edge_old_vs_new.csv

"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import math
import os
from dataclasses import dataclass


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


def spearman_rho(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    rx = _rankdata(xs)
    ry = _rankdata(ys)
    return pearson_r(rx, ry)


@dataclass(frozen=True)
class Corr:
    n: int
    pearson_r: float
    spearman_rho: float


def corr_pair(rows: list[dict[str, float]], x: str, y: str) -> Corr:
    xs: list[float] = []
    ys: list[float] = []
    for row in rows:
        xv = row.get(x, float("nan"))
        yv = row.get(y, float("nan"))
        if _is_finite(xv) and _is_finite(yv):
            xs.append(xv)
            ys.append(yv)
    return Corr(n=len(xs), pearson_r=pearson_r(xs, ys), spearman_rho=spearman_rho(xs, ys))


def _read_summary_with_galaxy(path: str) -> tuple[list[str], list[dict[str, float]], list[str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError("summary.csv has no header")
        fieldnames = list(r.fieldnames)
        galaxies: list[str] = []
        rows: list[dict[str, float]] = []
        for row in r:
            g = (row.get("galaxy") or "").strip()
            galaxies.append(g)
            parsed: dict[str, float] = {}
            for k in fieldnames:
                if k == "galaxy":
                    continue
                parsed[k] = _parse_float(row.get(k, ""))
            rows.append(parsed)
        return fieldnames, rows, galaxies


def _read_q_est(path: str) -> dict[str, dict[str, float]]:
    by_g: dict[str, dict[str, float]] = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError("q_est.csv has no header")
        for row in r:
            g = (row.get("galaxy") or "").strip()
            if not g:
                continue
            q = _parse_float(row.get("q_est_kms2", ""))
            by_g[g] = {
                "q_est_kms2": q,
                "v_est_asym_kms": math.sqrt(q) if _is_finite(q) and q > 0.0 else float("nan"),
            }
    return by_g


def _select_x_columns(fieldnames: list[str], explicit: list[str], patterns: list[str]) -> list[str]:
    cols = set(explicit)
    for pat in patterns:
        for fn in fieldnames:
            if fn == "galaxy":
                continue
            if fnmatch.fnmatch(fn, pat):
                cols.add(fn)
    return sorted(cols)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare correlations using old q_best vs new q_est")
    p.add_argument("--summary", required=True, help="Path to summary.csv")
    p.add_argument("--q-est", required=True, help="Path to q_est.csv")
    p.add_argument("--out-csv", required=True, help="Output CSV path")

    p.add_argument("--x", action="append", default=[], help="X column name (can repeat)")
    p.add_argument("--x-pattern", action="append", default=[], help="Glob pattern for X columns")
    p.add_argument("--min-n", type=int, default=30, help="Minimum pairwise N to report")
    p.add_argument("--top", type=int, default=30, help="Print top K by |ΔSpearman| (q-space)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    fieldnames, s_rows, galaxies = _read_summary_with_galaxy(args.summary)
    q_by_g = _read_q_est(args.q_est)

    # Build joined numeric rows in summary order
    rows: list[dict[str, float]] = []
    n_joined = 0
    for g, sr in zip(galaxies, s_rows):
        qd = q_by_g.get(g)
        if qd is None:
            continue
        jr = dict(sr)
        jr.update(qd)
        rows.append(jr)
        n_joined += 1

    xs = _select_x_columns(fieldnames, args.x, args.x_pattern)
    if not xs:
        # Default matches prior "composition_vs_edge_correlations.csv" intent.
        xs = _select_x_columns(
            fieldnames,
            explicit=[
                "sparc_L36_1e9solLum",
                "sparc_T",
                "sparc_MHI_1e9solMass",
                "sparc_SBeff_solLum_pc2",
                "sparc_Rdisk_kpc",
                "sparc_SBdisk_solLum_pc2",
            ],
            patterns=["frac_*"]
        )

    y_old_q = "q_best_kms2"
    y_old_v = "v_extra_asym_kms"
    y_new_q = "q_est_kms2"
    y_new_v = "v_est_asym_kms"

    # Compute and write
    out_dir = os.path.dirname(args.out_csv)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    results: list[dict[str, object]] = []
    for x in xs:
        c_old_q = corr_pair(rows, x, y_old_q)
        c_new_q = corr_pair(rows, x, y_new_q)
        c_old_v = corr_pair(rows, x, y_old_v)
        c_new_v = corr_pair(rows, x, y_new_v)

        # Only report if we have reasonable support for both q comparisons
        if min(c_old_q.n, c_new_q.n) < args.min_n:
            continue

        results.append({
            "x": x,
            "n_old_q": c_old_q.n,
            "pearson_old_q": c_old_q.pearson_r,
            "spearman_old_q": c_old_q.spearman_rho,
            "n_new_q": c_new_q.n,
            "pearson_new_q": c_new_q.pearson_r,
            "spearman_new_q": c_new_q.spearman_rho,
            "delta_spearman_q": c_new_q.spearman_rho - c_old_q.spearman_rho,
            "delta_pearson_q": c_new_q.pearson_r - c_old_q.pearson_r,
            "n_old_v": c_old_v.n,
            "pearson_old_v": c_old_v.pearson_r,
            "spearman_old_v": c_old_v.spearman_rho,
            "n_new_v": c_new_v.n,
            "pearson_new_v": c_new_v.pearson_r,
            "spearman_new_v": c_new_v.spearman_rho,
            "delta_spearman_v": c_new_v.spearman_rho - c_old_v.spearman_rho,
            "delta_pearson_v": c_new_v.pearson_r - c_old_v.pearson_r,
        })

    with open(args.out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()) if results else ["x"])
        w.writeheader()
        for r in results:
            w.writerow(r)

    # Console triage: where does replacing q_best with q_est change correlations most?
    def key_q(r: dict[str, object]) -> float:
        dv = r.get("delta_spearman_q")
        if isinstance(dv, float) and _is_finite(dv):
            return abs(dv)
        return -1.0

    results_sorted = sorted(results, key=key_q, reverse=True)

    print(f"Joined rows (summary ∩ q_est): {n_joined}")
    print(f"X columns: {len(xs)} | Wrote: {args.out_csv}")
    print("")
    print("Top changes in Spearman (q_est vs q_best):")
    print(f"{'x':28s} {'rho_old':>9s} {'rho_new':>9s} {'Δrho':>9s} {'N_old':>6s} {'N_new':>6s}")
    for r in results_sorted[: max(args.top, 0)]:
        x = str(r["x"])[:28]
        ro = float(r["spearman_old_q"])
        rn = float(r["spearman_new_q"])
        dr = float(r["delta_spearman_q"])
        no = int(r["n_old_q"])
        nn = int(r["n_new_q"])
        print(f"{x:28s} {ro:9.4f} {rn:9.4f} {dr:9.4f} {no:6d} {nn:6d}")


if __name__ == "__main__":
    main()
