"""Analyze whether outer rho-proxy slope closeness-to-(-2) correlates with q_est and q_best.

This script joins three existing catalogues on `galaxy`:
- toy_models/out_sparc_runs_full_with_composition/q_est.csv
- toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv (for q_best_kms2 and controls)
- toy_models/out_rho_resp_proxy/rho_resp_proxy_catalogue.csv    (outer slope diagnostics)

It then computes correlations between:
- closeness_abs = |slope_outer_abs + 2|
- closeness_pos = |slope_outer_pos + 2| (when defined)

and:
- q_est_kms2
- disagreement = q_est_kms2 - q_best_kms2 (and |disagreement|)

Outputs (default under toy_models/out_rho_resp_proxy/):
- rho_vs_q_merged.csv
- rho_vs_q_report.md
- a few scatter plots

Dependency-light: NumPy (+ optional matplotlib).
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np


def _read_csv_map(path: Path, *, key: str) -> dict[str, dict[str, str]]:
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


def _to_float(x: object) -> float:
    try:
        if x is None:
            return math.nan
        s = str(x).strip()
        if s == "" or s.lower() == "nan":
            return math.nan
        return float(s)
    except Exception:
        return math.nan


def residualize(y: np.ndarray, controls: np.ndarray) -> tuple[np.ndarray, int]:
    """Residualize y against controls via OLS with intercept.

    Returns (residuals, n_used). Rows with any non-finite values are dropped.
    """

    y = np.asarray(y, dtype=float)
    controls = np.asarray(controls, dtype=float)

    if controls.ndim == 1:
        controls = controls.reshape(-1, 1)

    m = np.isfinite(y) & np.all(np.isfinite(controls), axis=1)
    y2 = y[m]
    c2 = controls[m]
    n = int(y2.size)
    if n < 3:
        return (np.full_like(y, fill_value=np.nan), n)

    X = np.column_stack([np.ones(n, dtype=float), c2])
    beta, *_ = np.linalg.lstsq(X, y2, rcond=None)
    yhat = X @ beta
    resid = y2 - yhat

    out = np.full_like(y, fill_value=np.nan)
    out[m] = resid
    return (out, n)


def pearsonr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]
    y = y[m]
    if x.size < 3:
        return math.nan
    x = x - float(np.mean(x))
    y = y - float(np.mean(y))
    denom = float(np.sqrt(np.sum(x * x) * np.sum(y * y)))
    if denom == 0.0:
        return math.nan
    return float(np.sum(x * y) / denom)


def _rankdata_average_ties(a: np.ndarray) -> np.ndarray:
    """Average-rank for ties; ranks start at 1."""

    a = np.asarray(a, dtype=float)
    n = a.size
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(n, dtype=float)

    i = 0
    while i < n:
        j = i
        while j + 1 < n and a[order[j + 1]] == a[order[i]]:
            j += 1
        # average rank of positions i..j (1-based)
        r = 0.5 * ((i + 1) + (j + 1))
        ranks[order[i : j + 1]] = r
        i = j + 1

    return ranks


def spearmanr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]
    y = y[m]
    if x.size < 3:
        return math.nan
    rx = _rankdata_average_ties(x)
    ry = _rankdata_average_ties(y)
    return pearsonr(rx, ry)


def perm_p_value(
    x: np.ndarray,
    y: np.ndarray,
    *,
    stat: str,
    n_perm: int,
    seed: int,
) -> tuple[float, int]:
    """Two-sided permutation p-value for correlation.

    Returns (p, n_used).
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]
    y = y[m]
    n = int(x.size)
    if n < 3:
        return (math.nan, n)

    if stat == "pearson":
        r0 = pearsonr(x, y)
        f = pearsonr
    elif stat == "spearman":
        r0 = spearmanr(x, y)
        f = spearmanr
    else:
        raise ValueError("stat must be pearson or spearman")

    if not np.isfinite(r0):
        return (math.nan, n)

    rng = np.random.default_rng(seed)
    more = 0
    for _ in range(int(n_perm)):
        yp = rng.permutation(y)
        rp = f(x, yp)
        if np.isfinite(rp) and abs(rp) >= abs(r0):
            more += 1

    p = (more + 1.0) / (float(n_perm) + 1.0)
    return (float(p), n)


def _log10_pos(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full_like(x, fill_value=np.nan)
    m = np.isfinite(x) & (x > 0)
    out[m] = np.log10(x[m])
    return out


def partial_corr(
    x: np.ndarray,
    y: np.ndarray,
    controls: np.ndarray,
    *,
    kind: str,
) -> tuple[float, int]:
    """Partial correlation corr(resid(x|C), resid(y|C)).

    kind:
      - 'pearson'
      - 'spearman' (rank-transform x,y,controls first)
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    controls = np.asarray(controls, dtype=float)
    if controls.ndim == 1:
        controls = controls.reshape(-1, 1)

    if kind == "spearman":
        # Rank-transform before residualization.
        m = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(controls), axis=1)
        if int(np.sum(m)) < 3:
            return (math.nan, int(np.sum(m)))
        xr = _rankdata_average_ties(x[m])
        yr = _rankdata_average_ties(y[m])
        cr = np.column_stack([_rankdata_average_ties(controls[m, j]) for j in range(controls.shape[1])])
        rx, _ = residualize(xr, cr)
        ry, _ = residualize(yr, cr)
        r = pearsonr(rx, ry)
        return (r, int(np.sum(np.isfinite(rx) & np.isfinite(ry))))

    if kind == "pearson":
        rx, _ = residualize(x, controls)
        ry, _ = residualize(y, controls)
        r = pearsonr(rx, ry)
        return (r, int(np.sum(np.isfinite(rx) & np.isfinite(ry))))

    raise ValueError("kind must be pearson or spearman")


def partial_perm_p_value(
    x: np.ndarray,
    y: np.ndarray,
    controls: np.ndarray,
    *,
    kind: str,
    n_perm: int,
    seed: int,
) -> tuple[float, int]:
    """Permutation p-value for partial correlation.

    Procedure: residualize x and y vs controls, then permute y-residual.
    Two-sided p-value.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    controls = np.asarray(controls, dtype=float)
    if controls.ndim == 1:
        controls = controls.reshape(-1, 1)

    if kind == "spearman":
        # Rank-transform first
        m = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(controls), axis=1)
        x2 = x[m]
        y2 = y[m]
        c2 = controls[m]
        n = int(x2.size)
        if n < 3:
            return (math.nan, n)
        xr = _rankdata_average_ties(x2)
        yr = _rankdata_average_ties(y2)
        cr = np.column_stack([_rankdata_average_ties(c2[:, j]) for j in range(c2.shape[1])])
        rx, _ = residualize(xr, cr)
        ry, _ = residualize(yr, cr)
        rx = rx[np.isfinite(rx) & np.isfinite(ry)]
        ry = ry[np.isfinite(rx) & np.isfinite(ry)]
    else:
        rx, _ = residualize(x, controls)
        ry, _ = residualize(y, controls)
        m = np.isfinite(rx) & np.isfinite(ry)
        rx = rx[m]
        ry = ry[m]
        n = int(rx.size)
        if n < 3:
            return (math.nan, n)

    r0 = pearsonr(rx, ry)
    if not np.isfinite(r0):
        return (math.nan, int(rx.size))

    rng = np.random.default_rng(seed)
    more = 0
    for _ in range(int(n_perm)):
        rp = pearsonr(rx, rng.permutation(ry))
        if np.isfinite(rp) and abs(rp) >= abs(r0):
            more += 1

    p = (more + 1.0) / (float(n_perm) + 1.0)
    return (float(p), int(rx.size))


def _scatter(out_png: Path, x: np.ndarray, y: np.ndarray, *, xlabel: str, ylabel: str, title: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]
    y = y[m]
    if x.size < 3:
        return

    fig = plt.figure(figsize=(5.2, 4.0), dpi=170)
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x, y, s=18, alpha=0.75, edgecolors="none")

    # simple least-squares line
    x0 = float(np.mean(x))
    y0 = float(np.mean(y))
    xx = x - x0
    denom = float(np.sum(xx * xx))
    if denom > 0:
        b = float(np.sum(xx * (y - y0)) / denom)
        a = y0 - b * x0
        xs = np.linspace(float(np.min(x)), float(np.max(x)), 100)
        ax.plot(xs, a + b * xs, color="#333333", lw=1.2)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)

    p.add_argument(
        "--q-est",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/q_est.csv"),
    )
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
        "--out-dir",
        type=Path,
        default=Path("toy_models/out_rho_resp_proxy"),
    )

    p.add_argument("--n-perm", type=int, default=5000, help="Permutation count for p-values.")
    p.add_argument("--seed", type=int, default=12345)

    args = p.parse_args()

    q_map = _read_csv_map(args.q_est, key="galaxy")
    s_map = _read_csv_map(args.summary, key="galaxy")
    r_map = _read_csv_map(args.rho, key="galaxy")

    galaxies = sorted(set(q_map) & set(s_map) & set(r_map))
    if not galaxies:
        raise SystemExit("No overlapping galaxies among inputs")

    merged_rows: list[dict[str, object]] = []

    x_close_abs: list[float] = []
    x_close_pos: list[float] = []
    y_qest: list[float] = []
    y_qbest: list[float] = []
    y_dq: list[float] = []
    y_abs_dq: list[float] = []
    dv2_slope: list[float] = []
    c_log_vflat: list[float] = []
    c_log_rdisk: list[float] = []
    c_log_d: list[float] = []

    for g in galaxies:
        q_est = _to_float(q_map[g].get("q_est_kms2"))
        q_best = _to_float(s_map[g].get("q_best_kms2"))
        vflat = _to_float(s_map[g].get("sparc_Vflat_kms"))
        rdisk = _to_float(s_map[g].get("sparc_Rdisk_kpc"))
        dist = _to_float(s_map[g].get("sparc_D_mpc"))
        slope_abs = _to_float(r_map[g].get("slope_outer_abs"))
        slope_pos = _to_float(r_map[g].get("slope_outer_pos"))
        dv2_log_slope = _to_float(r_map[g].get("dv2_outer_log_slope"))

        close_abs = abs(slope_abs + 2.0) if np.isfinite(slope_abs) else math.nan
        close_pos = abs(slope_pos + 2.0) if np.isfinite(slope_pos) else math.nan

        dq = q_est - q_best if (np.isfinite(q_est) and np.isfinite(q_best)) else math.nan
        abs_dq = abs(dq) if np.isfinite(dq) else math.nan

        log_vflat = float(np.log10(vflat)) if np.isfinite(vflat) and vflat > 0 else math.nan
        log_rdisk = float(np.log10(rdisk)) if np.isfinite(rdisk) and rdisk > 0 else math.nan
        log_d = float(np.log10(dist)) if np.isfinite(dist) and dist > 0 else math.nan

        merged_rows.append(
            {
                "galaxy": g,
                "q_est_kms2": q_est,
                "q_best_kms2": q_best,
                "dq_est_minus_best_kms2": dq,
                "abs_dq_kms2": abs_dq,
                "sparc_Vflat_kms": vflat,
                "sparc_Rdisk_kpc": rdisk,
                "sparc_D_mpc": dist,
                "log10_Vflat": log_vflat,
                "log10_Rdisk": log_rdisk,
                "log10_D": log_d,
                "rho_slope_outer_abs": slope_abs,
                "rho_slope_outer_pos": slope_pos,
                "rho_closeness_abs": close_abs,
                "rho_closeness_pos": close_pos,
                "dv2_outer_log_slope": dv2_log_slope,
            }
        )

        x_close_abs.append(close_abs)
        x_close_pos.append(close_pos)
        y_qest.append(q_est)
        y_qbest.append(q_best)
        y_dq.append(dq)
        y_abs_dq.append(abs_dq)
        dv2_slope.append(dv2_log_slope)
        c_log_vflat.append(log_vflat)
        c_log_rdisk.append(log_rdisk)
        c_log_d.append(log_d)

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    merged_csv = out_dir / "rho_vs_q_merged.csv"
    with merged_csv.open("w", newline="") as f:
        fieldnames = list(merged_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(merged_rows)

    # Define a "flat-ish outer residual" subset based on dv2 log-slope.
    dv2 = np.asarray(dv2_slope, dtype=float)
    flat_mask = np.isfinite(dv2) & (np.abs(dv2) <= 0.5)

    def _corr_block(name: str, x: np.ndarray, y: np.ndarray) -> dict[str, object]:
        rp = pearsonr(x, y)
        rs = spearmanr(x, y)
        pp, n1 = perm_p_value(x, y, stat="pearson", n_perm=args.n_perm, seed=args.seed)
        ps, n2 = perm_p_value(x, y, stat="spearman", n_perm=args.n_perm, seed=args.seed + 1)
        return {
            "name": name,
            "n": int(min(n1, n2)),
            "pearson_r": rp,
            "pearson_p_perm": pp,
            "spearman_r": rs,
            "spearman_p_perm": ps,
        }

    xabs = np.asarray(x_close_abs, dtype=float)
    xpos = np.asarray(x_close_pos, dtype=float)
    qest = np.asarray(y_qest, dtype=float)
    dq = np.asarray(y_dq, dtype=float)
    absdq = np.asarray(y_abs_dq, dtype=float)

    blocks: list[dict[str, object]] = []

    blocks.append(_corr_block("closeness_abs vs q_est", xabs, qest))
    blocks.append(_corr_block("closeness_abs vs log10(q_est)", xabs, _log10_pos(qest)))
    blocks.append(_corr_block("closeness_abs vs abs(q_est-q_best)", xabs, absdq))
    blocks.append(_corr_block("closeness_abs vs (q_est-q_best)", xabs, dq))

    blocks.append(_corr_block("closeness_pos vs q_est", xpos, qest))
    blocks.append(_corr_block("closeness_pos vs log10(q_est)", xpos, _log10_pos(qest)))
    blocks.append(_corr_block("closeness_pos vs abs(q_est-q_best)", xpos, absdq))
    blocks.append(_corr_block("closeness_pos vs (q_est-q_best)", xpos, dq))

    # Repeat on the "flat-ish" subset.
    blocks.append(_corr_block("[flat dv2] closeness_abs vs log10(q_est)", xabs[flat_mask], _log10_pos(qest[flat_mask])))
    blocks.append(_corr_block("[flat dv2] closeness_abs vs abs(q_est-q_best)", xabs[flat_mask], absdq[flat_mask]))

    # Partial correlations: residualize against control sets.
    logv = np.asarray(c_log_vflat, dtype=float)
    logr = np.asarray(c_log_rdisk, dtype=float)
    logd = np.asarray(c_log_d, dtype=float)

    def _pcorr_block(name: str, x: np.ndarray, y: np.ndarray, controls: np.ndarray) -> dict[str, object]:
        r_p, n_p = partial_corr(x, y, controls, kind="pearson")
        r_s, n_s = partial_corr(x, y, controls, kind="spearman")
        p_p, npp = partial_perm_p_value(x, y, controls, kind="pearson", n_perm=args.n_perm, seed=args.seed)
        p_s, nps = partial_perm_p_value(x, y, controls, kind="spearman", n_perm=args.n_perm, seed=args.seed + 1)
        return {
            "name": name,
            "n": int(min(n_p, n_s, npp, nps)),
            "pearson_r": r_p,
            "pearson_p_perm": p_p,
            "spearman_r": r_s,
            "spearman_p_perm": p_s,
        }

    pblocks: list[dict[str, object]] = []

    y_logq = _log10_pos(qest)

    # Controls: (log Vflat), (log Vflat + log Rdisk), (+ log D), and (+ q_best)
    c1 = logv
    c2 = np.column_stack([logv, logr])
    c3 = np.column_stack([logv, logr, logd])
    c4 = np.column_stack([logv, logr, np.asarray(y_qbest, dtype=float)])

    pblocks.append(_pcorr_block("partial: closeness_abs vs log10(q_est) (controls: logVflat)", xabs, y_logq, c1))
    pblocks.append(_pcorr_block("partial: closeness_abs vs log10(q_est) (controls: logVflat, logRdisk)", xabs, y_logq, c2))
    pblocks.append(_pcorr_block("partial: closeness_abs vs log10(q_est) (controls: logVflat, logRdisk, logD)", xabs, y_logq, c3))
    pblocks.append(_pcorr_block("partial: closeness_abs vs abs(q_est-q_best) (controls: logVflat, logRdisk)", xabs, absdq, c2))
    pblocks.append(_pcorr_block("partial: closeness_abs vs abs(q_est-q_best) (controls: logVflat, logRdisk, q_best)", xabs, absdq, c4))

    pblocks.append(_pcorr_block("[flat dv2] partial: closeness_abs vs log10(q_est) (controls: logVflat, logRdisk)", xabs[flat_mask], y_logq[flat_mask], c2[flat_mask]))
    pblocks.append(_pcorr_block("[flat dv2] partial: closeness_abs vs abs(q_est-q_best) (controls: logVflat, logRdisk)", xabs[flat_mask], absdq[flat_mask], c2[flat_mask]))

    report = out_dir / "rho_vs_q_report.md"
    with report.open("w", encoding="utf-8") as f:
        f.write("# Outer ρ-slope closeness vs Q (q_est)\n\n")
        f.write("This report tests whether the *outer* spherical-inversion proxy slope\n\n")
        f.write("- `rho_slope_outer_abs` (fit to log10(|ρ_proxy|) vs log10(r))\n")
        f.write("- `rho_closeness_abs = |rho_slope_outer_abs + 2|`\n\n")
        f.write("correlates with the robust outer statistic `q_est_kms2` and with fit-vs-robust disagreement.\n\n")
        f.write("**Files**\n\n")
        f.write(f"- merged catalogue: `{merged_csv.as_posix()}`\n")
        f.write("\n")

        f.write("## Correlations (permutation p-values; two-sided)\n\n")
        f.write("Columns: n, Pearson r (p_perm), Spearman ρ (p_perm).\n\n")
        f.write("| test | n | pearson r | p_perm | spearman ρ | p_perm |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for b in blocks:
            f.write(
                "| {name} | {n} | {pr:.3f} | {pp:.4f} | {sr:.3f} | {sp:.4f} |\n".format(
                    name=b["name"],
                    n=b["n"],
                    pr=float(b["pearson_r"]) if np.isfinite(b["pearson_r"]) else math.nan,
                    pp=float(b["pearson_p_perm"]) if np.isfinite(b["pearson_p_perm"]) else math.nan,
                    sr=float(b["spearman_r"]) if np.isfinite(b["spearman_r"]) else math.nan,
                    sp=float(b["spearman_p_perm"]) if np.isfinite(b["spearman_p_perm"]) else math.nan,
                )
            )

        f.write("\n")
        f.write("## Partial correlations (residualized controls; permutation p-values)\n\n")
        f.write("Columns: n, partial Pearson r (p_perm), partial Spearman ρ (p_perm).\n")
        f.write("\n")
        f.write("| test | n | pearson r | p_perm | spearman ρ | p_perm |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for b in pblocks:
            f.write(
                "| {name} | {n} | {pr:.3f} | {pp:.4f} | {sr:.3f} | {sp:.4f} |\n".format(
                    name=b["name"],
                    n=b["n"],
                    pr=float(b["pearson_r"]) if np.isfinite(b["pearson_r"]) else math.nan,
                    pp=float(b["pearson_p_perm"]) if np.isfinite(b["pearson_p_perm"]) else math.nan,
                    sr=float(b["spearman_r"]) if np.isfinite(b["spearman_r"]) else math.nan,
                    sp=float(b["spearman_p_perm"]) if np.isfinite(b["spearman_p_perm"]) else math.nan,
                )
            )

        f.write("\n")
        f.write("## Notes\n")
        f.write("- `q_best_kms2` is constrained ≥0 by construction; `q_est_kms2` can be negative in principle (though typically positive).\n")
        f.write("- `rho_proxy` is a spherical diagnostic applied to disks; interpret the slope as a *shape sanity check*, not a literal density.\n")
        f.write("- The [flat dv2] subset keeps only galaxies with |dv2_outer_log_slope| ≤ 0.5 (Δv² roughly outer-flat in log–log).\n")

    # Plots
    png_dir = out_dir / "png_rho_vs_q"
    _scatter(
        png_dir / "closeness_abs_vs_log10_qest.png",
        xabs,
        _log10_pos(qest),
        xlabel=r"closeness to -2: |slope_abs + 2|",
        ylabel=r"log10(q_est [km^2/s^2])",
        title="Outer slope closeness vs q_est",
    )
    _scatter(
        png_dir / "closeness_abs_vs_absdq.png",
        xabs,
        absdq,
        xlabel=r"closeness to -2: |slope_abs + 2|",
        ylabel=r"|q_est - q_best| [(km/s)^2]",
        title="Outer slope closeness vs fit/robust disagreement",
    )

    # Partial case: residualize both x and y vs (logVflat, logRdisk) then scatter.
    rx, _ = residualize(xabs, c2)
    ry, _ = residualize(_log10_pos(qest), c2)
    _scatter(
        png_dir / "partial_closeness_abs_vs_log10_qest__controls_logVflat_logRdisk.png",
        rx,
        ry,
        xlabel=r"resid(closeness_abs | logVflat,logRdisk)",
        ylabel=r"resid(log10(q_est) | logVflat,logRdisk)",
        title="Partial: closeness vs log10(q_est)",
    )

    print(f"Wrote: {merged_csv}")
    print(f"Wrote: {report}")
    print(f"Plots (if matplotlib available): {png_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
