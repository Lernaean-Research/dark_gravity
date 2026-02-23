"""Compute partial (controlled) correlations from summary.csv (stdlib-only).

Purpose
-------
This script helps answer: do composition ↔ edge-behavior correlations persist
*after controlling for mass/scale proxies*?

Method
------
For each (x, y) pair and a chosen set of control variables Z:
1) Build vectors using rows where x, y, and all Z are finite.
2) Residualize x on Z via OLS:  x = a + Z b + eps_x
3) Residualize y on Z via OLS:  y = c + Z d + eps_y
4) Compute correlation between eps_x and eps_y.

We report:
- partial Pearson r (on residuals)
- partial “Spearman” rho approximation: rank-transform x/y/Z first, then run the
  same residualization and Pearson correlation on rank-residuals.

Usage
-----
Control for luminosity (mass proxy) when scanning composition vs edge metrics:
  ./.venv/Scripts/python.exe toy_models/analyze_partial_matrix.py \
      --summary toy_models/out/summary.csv \
      --control sparc_L36_1e9solLum \
      --x-pattern "frac_*" --x sparc_SBdisk_solLum_pc2 --x sparc_MHI_1e9solMass \
      --y q_best_kms2 --y v_extra_asym_kms \
      --export toy_models/out/partial_comp_vs_edge_L36.csv

Control for multiple proxies (e.g., L36 and Rdisk):
  --control sparc_L36_1e9solLum --control sparc_Rdisk_kpc

Notes
-----
- Stdlib only; no numpy/scipy.
- Pairwise complete cases *including controls*.
- OLS uses a small Gaussian-elimination solver; if the control matrix is
  singular/ill-conditioned, results for that pair are NaN.

"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PartialCorrRow:
    x: str
    y: str
    controls: str
    n: int
    pearson_partial: float
    spearman_partial: float


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


def _solve_linear_system(A: list[list[float]], b: list[float], eps: float = 1e-12) -> list[float] | None:
    """Solve A x = b by Gaussian elimination with partial pivoting.

    Returns None if singular/ill-conditioned.
    """

    n = len(A)
    # Build augmented matrix
    M = [row[:] + [b_i] for row, b_i in zip(A, b)]

    for col in range(n):
        # pivot
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < eps:
            return None
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]

        # normalize pivot row
        piv = M[col][col]
        inv = 1.0 / piv
        for j in range(col, n + 1):
            M[col][j] *= inv

        # eliminate
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col]
            if abs(factor) < eps:
                continue
            for j in range(col, n + 1):
                M[r][j] -= factor * M[col][j]

    return [M[i][n] for i in range(n)]


def _ols_residuals(y: list[float], Z: list[list[float]]) -> list[float] | None:
    """Return OLS residuals of y on [1, Z] where Z is n×k."""

    n = len(y)
    if n == 0:
        return None
    k = len(Z[0]) if Z else 0

    # Design matrix X: n x (k+1)
    p = k + 1

    # Compute normal equations: (X^T X) beta = X^T y
    XtX = [[0.0 for _ in range(p)] for _ in range(p)]
    Xty = [0.0 for _ in range(p)]

    for i in range(n):
        row = [1.0] + (Z[i] if k else [])
        yi = y[i]
        for a in range(p):
            Xty[a] += row[a] * yi
            for b in range(p):
                XtX[a][b] += row[a] * row[b]

    beta = _solve_linear_system(XtX, Xty)
    if beta is None:
        return None

    res: list[float] = []
    for i in range(n):
        row = [1.0] + (Z[i] if k else [])
        yhat = sum(beta[j] * row[j] for j in range(p))
        res.append(y[i] - yhat)
    return res


def _select_columns(fieldnames: list[str], explicit: list[str], patterns: list[str]) -> list[str]:
    cols = set(explicit)
    for pat in patterns:
        for fn in fieldnames:
            if fn == "galaxy":
                continue
            if fnmatch.fnmatch(fn, pat):
                cols.add(fn)
    return sorted(c for c in cols if c)


def _gather_xyZ(rows: list[dict[str, float]], x: str, y: str, controls: list[str]) -> tuple[list[float], list[float], list[list[float]]]:
    xs: list[float] = []
    ys: list[float] = []
    Z: list[list[float]] = []

    for row in rows:
        xv = row.get(x, float("nan"))
        yv = row.get(y, float("nan"))
        if not (_is_finite(xv) and _is_finite(yv)):
            continue
        zv: list[float] = []
        ok = True
        for c in controls:
            cv = row.get(c, float("nan"))
            if not _is_finite(cv):
                ok = False
                break
            zv.append(cv)
        if not ok:
            continue
        xs.append(xv)
        ys.append(yv)
        Z.append(zv)

    return xs, ys, Z


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute partial correlations controlling for one or more columns")
    p.add_argument("--summary", required=True, help="Path to summary.csv")
    p.add_argument("--control", action="append", default=[], help="Control column (can repeat)")
    p.add_argument("--x", action="append", default=[], help="X column name (can repeat)")
    p.add_argument("--y", action="append", default=[], help="Y column name (can repeat)")
    p.add_argument("--x-pattern", action="append", default=[], help="Glob pattern for X columns")
    p.add_argument("--y-pattern", action="append", default=[], help="Glob pattern for Y columns")
    p.add_argument("--min-n", type=int, default=80, help="Minimum N (must include controls)")
    p.add_argument("--export", default="", help="Optional CSV path to write all results")
    p.add_argument("--top", type=int, default=40, help="Print top K by |partial Spearman| then |partial Pearson|")
    return p.parse_args()


def _format_float(x: float) -> str:
    if not math.isfinite(x):
        return "nan"
    return f"{x:+.4f}"


def main() -> None:
    args = parse_args()
    if not args.control:
        raise SystemExit("Provide at least one --control column")

    fieldnames, rows = _read_summary(args.summary)
    available = set(fieldnames)

    for c in args.control + args.x + args.y:
        if c and c not in available:
            raise SystemExit(f"Column not found: {c}")

    xs = _select_columns(fieldnames, args.x, args.x_pattern)
    ys = _select_columns(fieldnames, args.y, args.y_pattern)
    if not xs:
        raise SystemExit("No X columns selected")
    if not ys:
        raise SystemExit("No Y columns selected")

    controls = list(args.control)
    controls_key = "+".join(controls)

    results: list[PartialCorrRow] = []
    for x in xs:
        for y in ys:
            if x == y:
                continue
            xv, yv, Z = _gather_xyZ(rows, x, y, controls)
            n = len(xv)
            if n < args.min_n:
                continue

            rx = _ols_residuals(xv, Z)
            ry = _ols_residuals(yv, Z)
            if rx is None or ry is None:
                p_r = float("nan")
            else:
                p_r = pearson_r(rx, ry)

            # Spearman-partial approximation: rank-transform x/y and each control column,
            # then do the same residual-correlation procedure.
            x_rank = _rankdata(xv)
            y_rank = _rankdata(yv)
            if Z and len(Z[0]) > 0:
                Z_rank: list[list[float]] = []
                # rank each control column separately
                k = len(Z[0])
                cols = [[Z[i][j] for i in range(n)] for j in range(k)]
                cols_r = [_rankdata(col) for col in cols]
                for i in range(n):
                    Z_rank.append([cols_r[j][i] for j in range(k)])
            else:
                Z_rank = []

            rrx = _ols_residuals(x_rank, Z_rank)
            rry = _ols_residuals(y_rank, Z_rank)
            if rrx is None or rry is None:
                p_rho = float("nan")
            else:
                p_rho = pearson_r(rrx, rry)

            results.append(
                PartialCorrRow(
                    x=x,
                    y=y,
                    controls=controls_key,
                    n=n,
                    pearson_partial=p_r,
                    spearman_partial=p_rho,
                )
            )

    results.sort(
        key=lambda cr: (
            -abs(cr.spearman_partial) if math.isfinite(cr.spearman_partial) else float("-inf"),
            -abs(cr.pearson_partial) if math.isfinite(cr.pearson_partial) else float("-inf"),
            cr.x,
            cr.y,
        )
    )

    print("Partial correlation matrix (pairwise complete incl. controls)")
    print(f"Summary: {args.summary}")
    print(f"Controls: {controls_key}")
    print(f"X columns: {len(xs)} | Y columns: {len(ys)} | Results: {len(results)}")
    print("")
    print(f"{'X':30s} {'Y':30s} {'N':>5s} {'Pearson*':>10s} {'Spearman*':>12s}")
    for cr in results[: max(args.top, 0)]:
        print(
            f"{cr.x:30.30s} {cr.y:30.30s} {cr.n:5d} {_format_float(cr.pearson_partial):>10s} {_format_float(cr.spearman_partial):>12s}"
        )

    if args.export:
        with open(args.export, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["x", "y", "controls", "n", "pearson_partial", "spearman_partial"])
            for cr in results:
                w.writerow([cr.x, cr.y, cr.controls, cr.n, cr.pearson_partial, cr.spearman_partial])
        print("")
        print(f"Wrote: {args.export}")


if __name__ == "__main__":
    main()
