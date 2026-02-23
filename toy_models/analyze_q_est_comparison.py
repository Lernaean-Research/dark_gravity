"""Compare robust Q_est against prior runner outputs (summary.csv).

This is a lightweight, reproducible analysis pass intended to answer:
- How does the robust outer-location estimate Q_est compare to the fitted q_best_kms2?
- How does v_est_asym = sqrt(max(Q_est, 0)) compare to v_extra_asym_kms?
- Are differences sensitive to the outer-selection rule (rfrac vs lastfrac)?

Inputs
------
- q_est.csv from toy_models/q_est_sparc175.py
- summary.csv from toy_models/sparc_rotmod_runner.py

Outputs
-------
- joined CSV with per-galaxy comparisons
- a concise markdown report
- a small set of diagnostic plots

Usage
-----
  ./.venv/Scripts/python.exe toy_models/analyze_q_est_comparison.py \
      --q-est toy_models/out_sparc_runs_full_with_composition/q_est.csv \
      --summary toy_models/out_sparc_runs_full_with_composition/summary.csv \
      --out-dir toy_models/out_q_est_analysis

"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class JoinedRow:
    galaxy: str
    outer_rule: str
    q_est_kms2: float
    q_best_kms2: float
    v_est_asym_kms: float
    v_extra_asym_kms: float
    vobs_outer_kms: float
    delta_q_kms2: float
    ratio_q: float
    delta_v_kms: float


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


def _read_csv_rows(path: str) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError(f"CSV has no header: {path}")
        return [dict(row) for row in r]


def _index_by_galaxy(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        g = (row.get("galaxy") or "").strip()
        if not g:
            continue
        out[g] = row
    return out


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


def median(xs: list[float]) -> float:
    if not xs:
        return float("nan")
    xs2 = sorted(xs)
    n = len(xs2)
    mid = n // 2
    if n % 2 == 1:
        return xs2[mid]
    return 0.5 * (xs2[mid - 1] + xs2[mid])


def mad(xs: list[float], center: float | None = None) -> float:
    if not xs:
        return float("nan")
    c = median(xs) if center is None else center
    dev = [abs(x - c) for x in xs]
    return median(dev)


def robust_z_scores(xs: list[float]) -> list[float]:
    """Return robust z = (x-med)/(1.4826*MAD)."""
    if not xs:
        return []
    m = median(xs)
    s = 1.4826 * mad(xs, center=m)
    if not _is_finite(s) or s <= 0.0:
        return [float("nan")] * len(xs)
    return [(x - m) / s for x in xs]


def theil_sen_slope_intercept(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Simple Theil–Sen fit: median pairwise slope, median intercept.

    O(n^2) but fine for n=175.
    """
    n = len(xs)
    if n < 2:
        return float("nan"), float("nan")

    slopes: list[float] = []
    for i in range(n):
        xi = xs[i]
        yi = ys[i]
        for j in range(i + 1, n):
            dx = xs[j] - xi
            if dx == 0:
                continue
            slopes.append((ys[j] - yi) / dx)

    if not slopes:
        return float("nan"), float("nan")

    b = median(slopes)
    intercepts = [y - b * x for x, y in zip(xs, ys)]
    a = median(intercepts)
    return a, b


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare Q_est against prior runner outputs")
    p.add_argument("--q-est", required=True, help="Path to q_est.csv")
    p.add_argument("--summary", required=True, help="Path to summary.csv")
    p.add_argument("--out-dir", required=True, help="Output directory")
    p.add_argument("--tag", default="", help="Optional label for outputs")
    return p.parse_args()


def _safe_sqrt_nonneg(x: float) -> float:
    if not _is_finite(x) or x <= 0.0:
        return float("nan")
    return math.sqrt(x)


def _fmt(x: float, digits: int = 4) -> str:
    if not _is_finite(x):
        return "nan"
    return f"{x:.{digits}g}"


def main() -> None:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    q_rows = _read_csv_rows(args.q_est)
    s_rows = _read_csv_rows(args.summary)

    q_by_g = _index_by_galaxy(q_rows)
    s_by_g = _index_by_galaxy(s_rows)

    galaxies = sorted(set(q_by_g.keys()) & set(s_by_g.keys()))
    missing_in_summary = sorted(set(q_by_g.keys()) - set(s_by_g.keys()))
    missing_in_qest = sorted(set(s_by_g.keys()) - set(q_by_g.keys()))

    joined: list[JoinedRow] = []
    for g in galaxies:
        q = q_by_g[g]
        s = s_by_g[g]

        outer_rule = (q.get("outer_rule") or "").strip()
        q_est = _parse_float(q.get("q_est_kms2"))
        q_best = _parse_float(s.get("q_best_kms2"))
        v_extra = _parse_float(s.get("v_extra_asym_kms"))
        vobs_outer = _parse_float(s.get("vobs_outer_kms"))

        v_est = _safe_sqrt_nonneg(q_est)
        delta_q = q_est - q_best if _is_finite(q_est) and _is_finite(q_best) else float("nan")
        ratio_q = q_est / q_best if _is_finite(q_est) and _is_finite(q_best) and q_best != 0.0 else float("nan")
        delta_v = v_est - v_extra if _is_finite(v_est) and _is_finite(v_extra) else float("nan")

        joined.append(
            JoinedRow(
                galaxy=g,
                outer_rule=outer_rule,
                q_est_kms2=q_est,
                q_best_kms2=q_best,
                v_est_asym_kms=v_est,
                v_extra_asym_kms=v_extra,
                vobs_outer_kms=vobs_outer,
                delta_q_kms2=delta_q,
                ratio_q=ratio_q,
                delta_v_kms=delta_v,
            )
        )

    # Write joined CSV
    tag = f"_{args.tag}" if args.tag else ""
    out_joined = os.path.join(args.out_dir, f"q_est_joined_summary{tag}.csv")
    with open(out_joined, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "galaxy",
                "outer_rule",
                "q_est_kms2",
                "q_best_kms2",
                "v_est_asym_kms",
                "v_extra_asym_kms",
                "vobs_outer_kms",
                "delta_q_kms2",
                "ratio_q",
                "delta_v_kms",
            ]
        )
        for r in joined:
            w.writerow(
                [
                    r.galaxy,
                    r.outer_rule,
                    r.q_est_kms2,
                    r.q_best_kms2,
                    r.v_est_asym_kms,
                    r.v_extra_asym_kms,
                    r.vobs_outer_kms,
                    r.delta_q_kms2,
                    r.ratio_q,
                    r.delta_v_kms,
                ]
            )

    # Summary stats
    q_est_all = [r.q_est_kms2 for r in joined if _is_finite(r.q_est_kms2)]
    q_best_all = [r.q_best_kms2 for r in joined if _is_finite(r.q_best_kms2)]
    delta_q_all = [r.delta_q_kms2 for r in joined if _is_finite(r.delta_q_kms2)]
    ratio_q_pos = [r.ratio_q for r in joined if _is_finite(r.ratio_q) and r.ratio_q > 0.0]

    v_est_all = [r.v_est_asym_kms for r in joined if _is_finite(r.v_est_asym_kms)]
    v_extra_all = [r.v_extra_asym_kms for r in joined if _is_finite(r.v_extra_asym_kms)]
    delta_v_all = [r.delta_v_kms for r in joined if _is_finite(r.delta_v_kms)]

    n_total = len(joined)
    n_neg_q_est = sum(1 for r in joined if _is_finite(r.q_est_kms2) and r.q_est_kms2 < 0.0)
    n_nan_v_est = sum(1 for r in joined if not _is_finite(r.v_est_asym_kms))

    # Correlations
    # q_est vs q_best
    q_pairs = [(r.q_best_kms2, r.q_est_kms2) for r in joined if _is_finite(r.q_best_kms2) and _is_finite(r.q_est_kms2)]
    xs_q = [x for x, _ in q_pairs]
    ys_q = [y for _, y in q_pairs]
    pear_q = pearson_r(xs_q, ys_q)
    spear_q = spearman_rho(xs_q, ys_q)

    # v_est vs v_extra
    v_pairs = [(r.v_extra_asym_kms, r.v_est_asym_kms) for r in joined if _is_finite(r.v_extra_asym_kms) and _is_finite(r.v_est_asym_kms)]
    xs_v = [x for x, _ in v_pairs]
    ys_v = [y for _, y in v_pairs]
    pear_v = pearson_r(xs_v, ys_v)
    spear_v = spearman_rho(xs_v, ys_v)

    # Theil–Sen fits (interpretable slope/intercept)
    a_q, b_q = theil_sen_slope_intercept(xs_q, ys_q)
    a_v, b_v = theil_sen_slope_intercept(xs_v, ys_v)

    # Robust deltas
    med_dq = median(delta_q_all)
    mad_dq = mad(delta_q_all, center=med_dq)
    med_dv = median(delta_v_all)
    mad_dv = mad(delta_v_all, center=med_dv)

    med_log10_ratio = median([math.log10(x) for x in ratio_q_pos]) if ratio_q_pos else float("nan")

    # Outliers by robust z on delta_v
    z_dv = robust_z_scores(delta_v_all)
    dv_with_gal: list[tuple[float, str, float]] = []
    j = 0
    for r in joined:
        if _is_finite(r.delta_v_kms):
            dv_with_gal.append((abs(z_dv[j]) if _is_finite(z_dv[j]) else float("nan"), r.galaxy, r.delta_v_kms))
            j += 1
    dv_with_gal.sort(reverse=True)
    top_outliers = dv_with_gal[:10]

    # Split by outer_rule
    by_rule: dict[str, list[JoinedRow]] = {}
    for r in joined:
        by_rule.setdefault(r.outer_rule or "(blank)", []).append(r)

    # Report markdown
    out_report = os.path.join(args.out_dir, f"q_est_comparison_report{tag}.md")
    with open(out_report, "w", encoding="utf-8") as f:
        f.write("# Q_est comparison against prior runner outputs\n\n")
        f.write(f"Inputs:\n- q_est: `{args.q_est}`\n- summary: `{args.summary}`\n\n")
        f.write("## Join integrity\n")
        f.write(f"- Joined galaxies: {n_total}\n")
        if missing_in_summary:
            f.write(f"- Present in q_est but missing in summary: {len(missing_in_summary)}\n")
        if missing_in_qest:
            f.write(f"- Present in summary but missing in q_est: {len(missing_in_qest)}\n")
        f.write("\n")

        f.write("## Sanity counts\n")
        f.write(f"- q_est < 0: {n_neg_q_est}\n")
        f.write(f"- v_est_asym = sqrt(max(q_est,0)) is NaN (due to q_est<=0 or missing): {n_nan_v_est}\n\n")

        f.write("## Q-space comparison (q_est_kms2 vs q_best_kms2)\n")
        f.write(f"- Pearson r: {_fmt(pear_q)}\n")
        f.write(f"- Spearman ρ: {_fmt(spear_q)}\n")
        f.write(f"- Theil–Sen fit: q_est ≈ a + b·q_best with a={_fmt(a_q)}, b={_fmt(b_q)}\n")
        f.write(f"- Δq = q_est − q_best: median={_fmt(med_dq)}, MAD={_fmt(mad_dq)}\n")
        f.write(f"- log10(q_est/q_best) (positive ratios only): median={_fmt(med_log10_ratio)}\n\n")

        f.write("## v-space comparison (v_est_asym_kms vs v_extra_asym_kms)\n")
        f.write(f"- Pearson r: {_fmt(pear_v)}\n")
        f.write(f"- Spearman ρ: {_fmt(spear_v)}\n")
        f.write(f"- Theil–Sen fit: v_est ≈ a + b·v_extra with a={_fmt(a_v)}, b={_fmt(b_v)}\n")
        f.write(f"- Δv = v_est − v_extra: median={_fmt(med_dv)}, MAD={_fmt(mad_dv)}\n\n")

        f.write("## Differences by outer selection rule\n")
        for rule, rows in sorted(by_rule.items(), key=lambda kv: kv[0]):
            dqs = [r.delta_q_kms2 for r in rows if _is_finite(r.delta_q_kms2)]
            dvs = [r.delta_v_kms for r in rows if _is_finite(r.delta_v_kms)]
            f.write(
                f"- `{rule}`: n={len(rows)}, median(Δq)={_fmt(median(dqs))}, MAD(Δq)={_fmt(mad(dqs, center=median(dqs)))}; "
                f"median(Δv)={_fmt(median(dvs))}, MAD(Δv)={_fmt(mad(dvs, center=median(dvs)))}\n"
            )
        f.write("\n")

        f.write("## Largest |Δv| robust outliers\n")
        f.write("(Ranked by |robust z| on Δv)\n\n")
        f.write("|rank|galaxy|Δv (km/s)|\n|---:|---|---:|\n")
        for k, (_, g, dv) in enumerate(top_outliers, start=1):
            f.write(f"|{k}|{g}|{_fmt(dv)}|\n")

        f.write("\n## Files written\n")
        f.write(f"- `{out_joined}`\n")
        f.write(f"- `{out_report}`\n")

    # Plots (matplotlib is optional-ish, but we already depend on it elsewhere)
    try:
        import matplotlib.pyplot as plt

        # Scatter: q_best vs q_est (log scales)
        qx = np.array(xs_q, dtype=float)
        qy = np.array(ys_q, dtype=float)
        fig = plt.figure(figsize=(6.0, 5.0), dpi=160)
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(qx, qy, s=12, alpha=0.7)
        lo = float(np.nanmin(np.concatenate([qx, qy])))
        hi = float(np.nanmax(np.concatenate([qx, qy])))
        if lo > 0 and hi > 0:
            ax.set_xscale("log")
            ax.set_yscale("log")
        ax.plot([lo, hi], [lo, hi], "k--", lw=1, alpha=0.6)
        ax.set_xlabel("q_best_kms2")
        ax.set_ylabel("q_est_kms2")
        ax.set_title("Q comparison")
        ax.grid(True, which="both", ls=":", alpha=0.3)
        out_png_q = os.path.join(args.out_dir, f"scatter_q_est_vs_q_best{tag}.png")
        fig.tight_layout()
        fig.savefig(out_png_q)
        plt.close(fig)

        # Scatter: v_extra vs v_est
        vx = np.array(xs_v, dtype=float)
        vy = np.array(ys_v, dtype=float)
        fig = plt.figure(figsize=(6.0, 5.0), dpi=160)
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(vx, vy, s=12, alpha=0.7)
        lo = float(np.nanmin(np.concatenate([vx, vy])))
        hi = float(np.nanmax(np.concatenate([vx, vy])))
        ax.plot([lo, hi], [lo, hi], "k--", lw=1, alpha=0.6)
        ax.set_xlabel("v_extra_asym_kms")
        ax.set_ylabel("v_est_asym_kms")
        ax.set_title("Asymptotic v comparison")
        ax.grid(True, which="both", ls=":", alpha=0.3)
        out_png_v = os.path.join(args.out_dir, f"scatter_v_est_vs_v_extra{tag}.png")
        fig.tight_layout()
        fig.savefig(out_png_v)
        plt.close(fig)

        # Histogram: delta_v
        dv = np.array(delta_v_all, dtype=float)
        fig = plt.figure(figsize=(6.0, 4.0), dpi=160)
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(dv[np.isfinite(dv)], bins=30)
        ax.axvline(float(med_dv), color="k", lw=1, ls="--", alpha=0.7)
        ax.set_xlabel("Δv = v_est − v_extra (km/s)")
        ax.set_ylabel("count")
        ax.set_title("Δv distribution")
        ax.grid(True, ls=":", alpha=0.3)
        out_png_dv = os.path.join(args.out_dir, f"hist_delta_v{tag}.png")
        fig.tight_layout()
        fig.savefig(out_png_dv)
        plt.close(fig)

    except Exception as e:  # pragma: no cover
        # Keep the analysis usable even if matplotlib backends fail.
        with open(os.path.join(args.out_dir, f"plot_error{tag}.txt"), "w", encoding="utf-8") as f:
            f.write(f"Plotting failed: {type(e).__name__}: {e}\n")

    print(f"Joined: {n_total} galaxies")
    if missing_in_summary:
        print(f"Missing in summary: {len(missing_in_summary)}")
    if missing_in_qest:
        print(f"Missing in q_est: {len(missing_in_qest)}")
    print(f"Wrote: {out_joined}")
    print(f"Wrote: {out_report}")


if __name__ == "__main__":
    main()
