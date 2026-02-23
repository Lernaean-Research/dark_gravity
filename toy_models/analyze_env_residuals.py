"""Test whether environment correlates with v_extra_asym_kms residuals after BASE controls.

We define BASE controls as in `predict_edge_amplitude_cv.py` suite mode:
  log(sparc_Vflat_kms), log(sparc_Rdisk_kpc) with an intercept.

Workflow
--------
1) Fit OLS on the full selected sample: y = v_extra_asym_kms ~ 1 + log(Vflat) + log(Rdisk)
2) Compute residuals: r_i = y_i - yhat_i
3) Correlate residuals with an environment proxy column (Pearson + Spearman).

Example
-------
  ./.venv/Scripts/python.exe toy_models/analyze_env_residuals.py \
      --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv \
      --env-col env_twompp_delta_external \
      --mask-col env_twompp_in_twompp_grid

"""

from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass


def _is_finite(x: float) -> bool:
    return math.isfinite(x)


def _parse_float(s: str) -> float:
    s = (s or "").strip()
    if not s:
        return float("nan")
    if s.lower() in {"true", "t", "yes", "y"}:
        return 1.0
    if s.lower() in {"false", "f", "no", "n"}:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return float("nan")


def _solve_linear_system(A: list[list[float]], b: list[float], eps: float = 1e-12) -> list[float] | None:
    n = len(A)
    M = [row[:] + [b_i] for row, b_i in zip(A, b)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < eps:
            return None
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]

        piv = M[col][col]
        inv = 1.0 / piv
        for j in range(col, n + 1):
            M[col][j] *= inv

        for r in range(n):
            if r == col:
                continue
            factor = M[r][col]
            if abs(factor) < eps:
                continue
            for j in range(col, n + 1):
                M[r][j] -= factor * M[col][j]

    return [M[i][n] for i in range(n)]


def _ols_fit(X: list[list[float]], y: list[float]) -> list[float] | None:
    n = len(y)
    if n == 0:
        return None
    p = len(X[0])

    XtX = [[0.0 for _ in range(p)] for _ in range(p)]
    Xty = [0.0 for _ in range(p)]
    for xi, yi in zip(X, y):
        for a in range(p):
            Xty[a] += xi[a] * yi
            for b in range(p):
                XtX[a][b] += xi[a] * xi[b]

    return _solve_linear_system(XtX, Xty)


def _predict(beta: list[float], x: list[float]) -> float:
    return sum(beta[j] * x[j] for j in range(len(beta)))


def _ln_beta(a: float, b: float) -> float:
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _beta_continued_fraction(x: float, a: float, b: float, max_iter: int = 200, eps: float = 3e-14) -> float:
    """Evaluate continued fraction for incomplete beta (Lentz’s algorithm)."""

    am, bm = 1.0, 1.0
    az = 1.0
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    bz = 1.0 - qab * x / qap
    if abs(bz) < 1e-30:
        bz = 1e-30

    d = 1.0 / bz
    aold = 0.0
    for m in range(1, max_iter + 1):
        em = float(m)
        tem = em + em
        # even step
        d_even = em * (b - em) * x / ((qam + tem) * (a + tem))
        ap = az + d_even * am
        bp = bz + d_even * bm
        # odd step
        d_odd = -(a + em) * (qab + em) * x / ((a + tem) * (qap + tem))
        app = ap + d_odd * az
        bpp = bp + d_odd * bz
        if abs(bpp) < 1e-30:
            bpp = 1e-30

        am = ap / bpp
        bm = bp / bpp
        az = app / bpp
        bz = 1.0

        if abs(az - aold) < eps * abs(az):
            return az
        aold = az

    return az


def _reg_incomplete_beta(x: float, a: float, b: float) -> float:
    """Regularized incomplete beta I_x(a,b) (Numerical Recipes style)."""

    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    # Use symmetry to improve convergence.
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _reg_incomplete_beta(1.0 - x, b, a)

    ln_bt = a * math.log(x) + b * math.log(1.0 - x) - _ln_beta(a, b)
    bt = math.exp(ln_bt)
    cf = _beta_continued_fraction(x, a, b)
    return (bt * cf) / a


def _t_cdf(t: float, df: int) -> float:
    """Student-t CDF via regularized incomplete beta.

    For df=v and t>0:
      CDF = 1 - 0.5 * I_{v/(v+t^2)}(v/2, 1/2)
    For t<0:
      CDF = 0.5 * I_{v/(v+t^2)}(v/2, 1/2)
    """

    if not math.isfinite(t) or df <= 0:
        return float("nan")
    v = float(df)
    x = v / (v + t * t)
    ib = _reg_incomplete_beta(x, 0.5 * v, 0.5)
    if t >= 0.0:
        return 1.0 - 0.5 * ib
    return 0.5 * ib


def _corr_pvalue_pearson(r: float, n: int) -> float:
    """Approx two-tailed p-value for Pearson r using t distribution."""

    if not math.isfinite(r) or n < 3:
        return float("nan")
    if abs(r) >= 1.0:
        return 0.0
    df = n - 2
    t = r * math.sqrt(df / (1.0 - r * r))
    cdf = _t_cdf(abs(t), df)
    if not math.isfinite(cdf):
        return float("nan")
    # two-tailed: 2 * (1 - CDF(|t|))
    p = 2.0 * (1.0 - cdf)
    return max(0.0, min(1.0, p))


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _empirical_p_two_tailed(
    x: list[float],
    y: list[float],
    n_perm: int,
    seed: int,
    method: str,
    strata: list[str] | None = None,
) -> float:
    """Two-tailed permutation p-value for correlation(x,y).

    Permutes y relative to x. Uses +1 smoothing:
      p = (count(|stat_perm| >= |stat_obs|) + 1) / (n_perm + 1)

    method: 'pearson' or 'spearman'
    """

    n = len(x)
    if n != len(y) or n < 3 or n_perm <= 0:
        return float("nan")

    rng = random.Random(seed)

    if method == "pearson":
        # Precompute deviations and denominator. Mean is invariant under permutation.
        mx = sum(x) / n
        my = sum(y) / n
        x_dev = [xi - mx for xi in x]
        y_dev = [yi - my for yi in y]
        sxx = _dot(x_dev, x_dev)
        syy = _dot(y_dev, y_dev)
        if sxx <= 0.0 or syy <= 0.0:
            return float("nan")
        denom = math.sqrt(sxx * syy)
        r_obs = _dot(x_dev, y_dev) / denom

        y_work = y_dev[:]

        # Precompute indices per stratum (if provided).
        strata_idx: dict[str, list[int]] | None = None
        if strata is not None:
            if len(strata) != n:
                return float("nan")
            strata_idx = {}
            for i, g in enumerate(strata):
                strata_idx.setdefault(g, []).append(i)

        def shuffle_in_place(arr: list[float]) -> None:
            if strata_idx is None:
                rng.shuffle(arr)
                return
            # Shuffle within each group.
            for idxs in strata_idx.values():
                if len(idxs) < 2:
                    continue
                vals = [arr[i] for i in idxs]
                rng.shuffle(vals)
                for i, v in zip(idxs, vals):
                    arr[i] = v

        hit = 0
        thr = abs(r_obs)
        for _ in range(n_perm):
            shuffle_in_place(y_work)
            r = _dot(x_dev, y_work) / denom
            if abs(r) >= thr:
                hit += 1
        return (hit + 1.0) / (n_perm + 1.0)

    if method == "spearman":
        rx = _rankdata(x)
        ry = _rankdata(y)
        return _empirical_p_two_tailed(rx, ry, n_perm, seed, method="pearson", strata=strata)

    return float("nan")


def _pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n == 0:
        return float("nan")
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    syy = sum((yi - my) ** 2 for yi in y)
    if sxx <= 0.0 or syy <= 0.0:
        return float("nan")
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    return sxy / math.sqrt(sxx * syy)


def _rankdata(vals: list[float]) -> list[float]:
    """Average ranks for ties (1..n)."""
    n = len(vals)
    order = sorted(range(n), key=lambda i: vals[i])
    ranks = [0.0] * n

    i = 0
    while i < n:
        j = i
        v = vals[order[i]]
        while j < n and vals[order[j]] == v:
            j += 1
        # average rank for positions i..j-1 (1-indexed)
        r = 0.5 * ((i + 1) + j)
        for k in range(i, j):
            ranks[order[k]] = r
        i = j

    return ranks


def _spearman(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) == 0:
        return float("nan")
    rx = _rankdata(x)
    ry = _rankdata(y)
    return _pearson(rx, ry)


@dataclass(frozen=True)
class CorrResult:
    n: int
    pearson_r: float
    spearman_rho: float
    pearson_p_2tail: float
    spearman_p_2tail_approx: float
    pearson_p_perm_2tail: float
    spearman_p_perm_2tail: float


def _corr(x: list[float], y: list[float], n_perm: int, perm_seed: int) -> CorrResult:
    n = len(x)
    pr = _pearson(x, y)
    sr = _spearman(x, y)

    # Spearman p-value is approximate; we use the same t approximation with df=n-2.
    # For n~O(100), this is generally adequate for a quick robustness screen.
    p_pr = _corr_pvalue_pearson(pr, n)
    p_sr = _corr_pvalue_pearson(sr, n)

    # Empirical permutation p-values (two-tailed) if requested.
    p_pr_perm = _empirical_p_two_tailed(x, y, n_perm=n_perm, seed=perm_seed, method="pearson") if n_perm > 0 else float("nan")
    # Use a different seed stream for Spearman so the two aren't identical.
    p_sr_perm = (
        _empirical_p_two_tailed(x, y, n_perm=n_perm, seed=perm_seed + 1337, method="spearman") if n_perm > 0 else float("nan")
    )

    return CorrResult(
        n=n,
        pearson_r=pr,
        spearman_rho=sr,
        pearson_p_2tail=p_pr,
        spearman_p_2tail_approx=p_sr,
        pearson_p_perm_2tail=p_pr_perm,
        spearman_p_perm_2tail=p_sr_perm,
    )


def _corr_with_stratified_perm(
    x: list[float],
    y: list[float],
    n_perm: int,
    perm_seed: int,
    strata: list[str] | None,
) -> CorrResult:
    """Same as _corr, but uses stratified permutation p-values if strata is provided."""

    base = _corr(x, y, n_perm=0, perm_seed=perm_seed)
    if n_perm <= 0:
        return base
    p_pr_perm = _empirical_p_two_tailed(x, y, n_perm=n_perm, seed=perm_seed, method="pearson", strata=strata)
    p_sr_perm = _empirical_p_two_tailed(x, y, n_perm=n_perm, seed=perm_seed + 1337, method="spearman", strata=strata)
    return CorrResult(
        n=base.n,
        pearson_r=base.pearson_r,
        spearman_rho=base.spearman_rho,
        pearson_p_2tail=base.pearson_p_2tail,
        spearman_p_2tail_approx=base.spearman_p_2tail_approx,
        pearson_p_perm_2tail=p_pr_perm,
        spearman_p_perm_2tail=p_sr_perm,
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Correlate BASE residuals with an environment proxy")
    p.add_argument("--summary", required=True, help="Path to summary_with_env.csv")
    p.add_argument("--target", default="v_extra_asym_kms", help="Target column (default v_extra_asym_kms)")
    p.add_argument("--env-col", required=True, help="Environment proxy column to test")
    p.add_argument(
        "--preset",
        default="",
        choices=["", "base_plus_dist"],
        help=(
            "Named control presets. "
            "base_plus_dist: BASE controls plus distance (log(Vflat), log(Rdisk), log(D_mpc)). "
            "If set, overrides --base-features and --log-features."
        ),
    )
    p.add_argument(
        "--base-features",
        nargs="*",
        default=["sparc_Vflat_kms", "sparc_Rdisk_kpc"],
        help="BASE control features (default: sparc_Vflat_kms sparc_Rdisk_kpc)",
    )
    p.add_argument(
        "--log-features",
        nargs="*",
        default=["sparc_Vflat_kms", "sparc_Rdisk_kpc"],
        help="Features to log-transform (default: sparc_Vflat_kms sparc_Rdisk_kpc)",
    )
    p.add_argument(
        "--mask-col",
        default="",
        help="Optional boolean/numeric mask column (e.g. env_twompp_in_twompp_grid); keep rows where mask>0",
    )
    p.add_argument(
        "--require-qflag",
        type=int,
        default=-1,
        help="If set to 1/2/3, keep only rows with sparc_Q_flag==value",
    )
    p.add_argument(
        "--permute",
        type=int,
        default=0,
        help="If >0, compute two-tailed empirical p-values via permutation test with this many shuffles",
    )
    p.add_argument(
        "--perm-seed",
        type=int,
        default=0,
        help="Random seed for permutation test",
    )
    p.add_argument(
        "--partial",
        action="store_true",
        help="If set, compute partial correlation by residualizing BOTH target and env on the control features",
    )
    p.add_argument(
        "--stratify-col",
        default="",
        help="Optional column name to stratify permutation (shuffle env within bins, e.g. sparc_Q_flag)",
    )
    p.add_argument(
        "--stratify-morph2",
        action="store_true",
        help="Stratify permutation into early/late morphology bins derived from sparc_T (early if T<=morph-cut)",
    )
    p.add_argument(
        "--morph-cut",
        type=float,
        default=0.0,
        help="Cut on sparc_T for early/late bins when --stratify-morph2 is set (default 0.0)",
    )
    p.add_argument(
        "--stratify-dist-quantiles",
        type=int,
        default=0,
        help="If >0, stratify permutation into this many distance quantile bins using sparc_D_mpc",
    )
    p.add_argument(
        "--stratify-qflag-dist-quantiles",
        type=int,
        default=0,
        help="If >0, stratify permutation into combined bins: (sparc_Q_flag) × (distance quantiles of dist-col)",
    )
    p.add_argument(
        "--dist-col",
        default="sparc_D_mpc",
        help="Distance column for quantile stratification (default sparc_D_mpc)",
    )
    return p.parse_args()


def _quantile_edges(vals: list[float], q: int) -> list[float]:
    """Return (q-1) cut edges for q quantile bins. vals must be non-empty."""

    if q <= 1:
        return []
    xs = sorted(vals)
    n = len(xs)
    edges: list[float] = []
    for i in range(1, q):
        # Use nearest-rank style cut.
        k = int(math.floor(i * n / q))
        k = max(0, min(n - 1, k))
        edges.append(xs[k])
    # Ensure non-decreasing edges.
    edges = sorted(edges)
    return edges


def _assign_quantile_bin(x: float, edges: list[float]) -> int:
    """Return 0..len(edges) quantile bin index."""

    for i, e in enumerate(edges):
        if x <= e:
            return i
    return len(edges)


def main() -> None:
    args = parse_args()

    if args.preset == "base_plus_dist":
        # BASE + distance control variant.
        # Use a log transform for distance to treat it as a scale variable.
        args.base_features = ["sparc_Vflat_kms", "sparc_Rdisk_kpc", "sparc_D_mpc"]
        args.log_features = ["sparc_Vflat_kms", "sparc_Rdisk_kpc", "sparc_D_mpc"]

    log_feats = set(args.log_features)

    strat_modes = 0
    if args.stratify_col:
        strat_modes += 1
    if args.stratify_morph2:
        strat_modes += 1
    if args.stratify_dist_quantiles > 0:
        strat_modes += 1
    if args.stratify_qflag_dist_quantiles > 0:
        strat_modes += 1
    if strat_modes > 1:
        raise SystemExit("Choose only one stratification mode: --stratify-col OR --stratify-morph2 OR --stratify-dist-quantiles")

    y: list[float] = []
    env: list[float] = []
    X: list[list[float]] = []

    strata: list[str] = []
    # For distance-based stratifications we finalize bins after filtering.
    qflag_vals_for_bins: list[str] = []
    dist_vals_for_bins: list[float] = []

    # For reporting: also keep raw y/env pairs for raw correlation
    y_raw: list[float] = []
    env_raw: list[float] = []

    with open(args.summary, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError("summary has no header")
        fields = set(r.fieldnames)

        required_cols = [args.target, args.env_col, *args.base_features]
        if args.require_qflag >= 0:
            required_cols.append("sparc_Q_flag")
        if args.stratify_col:
            required_cols.append(args.stratify_col)
        if args.stratify_morph2:
            required_cols.append("sparc_T")
        if args.stratify_dist_quantiles > 0:
            required_cols.append(args.dist_col)
        if args.stratify_qflag_dist_quantiles > 0:
            required_cols.append("sparc_Q_flag")
            required_cols.append(args.dist_col)

        missing = [c for c in required_cols if c not in fields]
        if missing:
            raise SystemExit(f"Missing columns in summary: {missing}")
        if args.mask_col and args.mask_col not in fields:
            raise SystemExit(f"Mask column not found: {args.mask_col}")

        for row in r:
            if args.require_qflag >= 0:
                qf = _parse_float(row.get("sparc_Q_flag", ""))
                if not _is_finite(qf) or int(round(qf)) != int(args.require_qflag):
                    continue

            if args.mask_col:
                mv = _parse_float(row.get(args.mask_col, ""))
                if not _is_finite(mv) or mv <= 0.0:
                    continue

            yt = _parse_float(row.get(args.target, ""))
            et = _parse_float(row.get(args.env_col, ""))
            if not _is_finite(yt) or not _is_finite(et):
                continue

            feats: list[float] = [1.0]
            ok = True
            for fcol in args.base_features:
                xv = _parse_float(row.get(fcol, ""))
                if not _is_finite(xv):
                    ok = False
                    break
                if fcol in log_feats:
                    if xv <= 0.0:
                        ok = False
                        break
                    xv = math.log(xv)
                feats.append(xv)
            if not ok:
                continue

            y.append(yt)
            env.append(et)
            X.append(feats)

            if args.stratify_col:
                strata.append((row.get(args.stratify_col, "") or "").strip() or "(blank)")
            elif args.stratify_morph2:
                tv = _parse_float(row.get("sparc_T", ""))
                if not _is_finite(tv):
                    strata.append("(nan)")
                else:
                    strata.append("early" if tv <= args.morph_cut else "late")
            elif args.stratify_dist_quantiles > 0:
                dv = _parse_float(row.get(args.dist_col, ""))
                if not _is_finite(dv):
                    strata.append("(nan)")
                else:
                    strata.append("(pending)")
                    dist_vals_for_bins.append(dv)
            elif args.stratify_qflag_dist_quantiles > 0:
                qf_raw = row.get("sparc_Q_flag", "")
                qf = _parse_float(qf_raw)
                qf_key = "(nan)" if not _is_finite(qf) else f"Q{int(round(qf))}"
                dv = _parse_float(row.get(args.dist_col, ""))
                if not _is_finite(dv):
                    strata.append(f"{qf_key}_dist_(nan)")
                else:
                    strata.append("(pending)")
                    qflag_vals_for_bins.append(qf_key)
                    dist_vals_for_bins.append(dv)

            y_raw.append(yt)
            env_raw.append(et)

    if len(y) < max(10, len(args.base_features) + 5):
        raise SystemExit(f"Too few rows after filtering: N={len(y)}")

    # Finalize distance-bin strata if requested (simple distance bins).
    if args.stratify_dist_quantiles > 0:
        q = int(args.stratify_dist_quantiles)
        if q < 2:
            raise SystemExit("--stratify-dist-quantiles must be >=2")
        finite_dist = [d for d in dist_vals_for_bins if _is_finite(d)]
        if len(finite_dist) < max(10, q * 3):
            raise SystemExit(f"Too few finite distances for quantile bins: {len(finite_dist)}")
        edges = _quantile_edges(finite_dist, q)
        # Walk over strata and fill pending entries in order of stored dist_vals_for_bins.
        j = 0
        for i in range(len(strata)):
            if strata[i] != "(pending)":
                continue
            d = dist_vals_for_bins[j]
            j += 1
            b = _assign_quantile_bin(d, edges)
            strata[i] = f"dist_q{b+1}_of_{q}"

    # Finalize combined Q_flag × distance quantile bins.
    if args.stratify_qflag_dist_quantiles > 0:
        q = int(args.stratify_qflag_dist_quantiles)
        if q < 2:
            raise SystemExit("--stratify-qflag-dist-quantiles must be >=2")
        finite_dist = [d for d in dist_vals_for_bins if _is_finite(d)]
        if len(finite_dist) < max(10, q * 3):
            raise SystemExit(f"Too few finite distances for quantile bins: {len(finite_dist)}")
        edges = _quantile_edges(finite_dist, q)

        j = 0
        for i in range(len(strata)):
            if strata[i] != "(pending)":
                continue
            qf_key = qflag_vals_for_bins[j]
            d = dist_vals_for_bins[j]
            j += 1
            b = _assign_quantile_bin(d, edges)
            strata[i] = f"{qf_key}_dist_q{b+1}_of_{q}"

    beta = _ols_fit(X, y)
    if beta is None:
        raise SystemExit("OLS fit failed (singular?)")

    y_hat = [_predict(beta, xi) for xi in X]
    resid_y = [yi - yh for yi, yh in zip(y, y_hat)]

    if args.partial:
        beta_e = _ols_fit(X, env)
        if beta_e is None:
            raise SystemExit("OLS fit for env failed (singular?)")
        env_hat = [_predict(beta_e, xi) for xi in X]
        resid_env = [ei - eh for ei, eh in zip(env, env_hat)]
    else:
        resid_env = env

    use_strata = bool(args.stratify_col) or bool(args.stratify_morph2) or (args.stratify_dist_quantiles > 0) or (
        args.stratify_qflag_dist_quantiles > 0
    )
    strata_or_none: list[str] | None = strata if use_strata else None
    corr_resid = _corr_with_stratified_perm(
        resid_y,
        resid_env,
        n_perm=args.permute,
        perm_seed=args.perm_seed,
        strata=strata_or_none,
    )
    corr_raw = _corr_with_stratified_perm(
        y_raw,
        env_raw,
        n_perm=args.permute,
        perm_seed=args.perm_seed,
        strata=strata_or_none,
    )

    print("Environment vs BASE residuals")
    print(f"Summary: {args.summary}")
    if args.require_qflag >= 0:
        print(f"Filter: sparc_Q_flag=={args.require_qflag}")
    if args.mask_col:
        print(f"Mask: {args.mask_col} > 0")
    print(f"Target: {args.target}")
    print(f"Env: {args.env_col}")
    print(f"BASE: 1 + " + " + ".join([("log(" + f + ")") if f in log_feats else f for f in args.base_features]))
    if args.partial:
        print("Mode: partial (residualize BOTH target and env on BASE)")
    else:
        print("Mode: residual (residualize target only)")
    print("")

    if args.permute > 0:
        perm_line = f"Permutation test: n_perm={args.permute} seed={args.perm_seed}"
        if args.stratify_col:
            perm_line += f" | stratified by {args.stratify_col}"
        elif args.stratify_morph2:
            perm_line += f" | stratified by morph2 (sparc_T <= {args.morph_cut:g} vs > {args.morph_cut:g})"
        elif args.stratify_dist_quantiles > 0:
            perm_line += f" | stratified by {args.dist_col} quantiles (q={args.stratify_dist_quantiles})"
        elif args.stratify_qflag_dist_quantiles > 0:
            perm_line += f" | stratified by (sparc_Q_flag × {args.dist_col} quantiles), q={args.stratify_qflag_dist_quantiles}"
        print(perm_line)

    def _fmt_p(p: float) -> str:
        return "nan" if not math.isfinite(p) else f"{p:.3g}"

    resid_line = (
        f"N={corr_resid.n} | resid~env: Pearson r={corr_resid.pearson_r:+.4f} "
        f"(p≈{_fmt_p(corr_resid.pearson_p_2tail)}"
    )
    if args.permute > 0:
        resid_line += f", p_perm={_fmt_p(corr_resid.pearson_p_perm_2tail)}"
    resid_line += ") | "
    resid_line += (
        f"Spearman rho={corr_resid.spearman_rho:+.4f} "
        f"(p≈{_fmt_p(corr_resid.spearman_p_2tail_approx)}"
    )
    if args.permute > 0:
        resid_line += f", p_perm={_fmt_p(corr_resid.spearman_p_perm_2tail)}"
    resid_line += ")"
    print(resid_line)

    raw_line = (
        f"N={corr_raw.n} | raw y~env:  Pearson r={corr_raw.pearson_r:+.4f} "
        f"(p≈{_fmt_p(corr_raw.pearson_p_2tail)}"
    )
    if args.permute > 0:
        raw_line += f", p_perm={_fmt_p(corr_raw.pearson_p_perm_2tail)}"
    raw_line += ") | "
    raw_line += (
        f"Spearman rho={corr_raw.spearman_rho:+.4f} "
        f"(p≈{_fmt_p(corr_raw.spearman_p_2tail_approx)}"
    )
    if args.permute > 0:
        raw_line += f", p_perm={_fmt_p(corr_raw.spearman_p_perm_2tail)}"
    raw_line += ")"
    print(raw_line)


if __name__ == "__main__":
    main()
