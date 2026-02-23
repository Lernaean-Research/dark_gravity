"""Out-of-sample predictor for edge-response amplitude (stdlib-only).

Purpose
-------
Given `summary.csv` from `toy_models/sparc_rotmod_runner.py`, build a simple
linear model to predict the fitted edge-amplitude proxy:

  y = v_extra_asym_kms = sqrt(q_best_kms2)

using:
- baseline controls (e.g., sparc_Vflat_kms, sparc_Rdisk_kpc)
- optional additional predictors (e.g., composition fractions frac_*)

Then quantify whether adding composition improves out-of-sample error using
k-fold cross-validation.

Models
------
We fit OLS with an intercept, using a small Gaussian-elimination solver.
To capture scaling relations, you can log-transform selected positive variables.

Metrics
-------
Reported across all held-out predictions:
- RMSE, MAE (in km/s)
- R^2 (coefficient of determination)
- Also on log-space if enabled for target

Usage
-----
Controls-only baseline:
  ./.venv/Scripts/python.exe toy_models/predict_edge_amplitude_cv.py \
      --summary toy_models/out/summary.csv \
      --target v_extra_asym_kms \
      --features sparc_Vflat_kms sparc_Rdisk_kpc \
      --log-features sparc_Vflat_kms sparc_Rdisk_kpc \
      --k 5 --seed 0

Controls + composition fractions:
  ./.venv/Scripts/python.exe toy_models/predict_edge_amplitude_cv.py \
      --summary toy_models/out/summary.csv \
      --target v_extra_asym_kms \
      --features sparc_Vflat_kms sparc_Rdisk_kpc \
      --log-features sparc_Vflat_kms sparc_Rdisk_kpc \
      --add-pattern "frac_*" \
      --k 5 --seed 0

Convenience mode (run baseline+extended and compare):
  ./.venv/Scripts/python.exe toy_models/predict_edge_amplitude_cv.py \
      --summary toy_models/out/summary.csv \
      --compare \
      --k 5 --seed 0

Suite mode (repeated CV + nested-model F-test; compares targets and Q-flag filters):
    ./.venv/Scripts/python.exe toy_models/predict_edge_amplitude_cv.py \
            --summary toy_models/out/summary.csv \
            --suite --k 5 --seed 0 --repeats 20

"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import math
import random
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


def _read_summary(path: str) -> tuple[list[str], list[dict[str, float]]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError("summary.csv has no header")
        fieldnames = list(r.fieldnames)
        rows: list[dict[str, float]] = []
        galaxies: list[str] = []
        for row in r:
            galaxies.append((row.get("galaxy") or "").strip())
            parsed: dict[str, float] = {}
            for k in fieldnames:
                if k == "galaxy":
                    continue
                parsed[k] = _parse_float(row.get(k, ""))
            rows.append(parsed)
        return fieldnames, rows, galaxies


def _read_q_est_map(path: str) -> dict[str, dict[str, float]]:
    """Read q_est.csv and return per-galaxy numeric values.

    Output keys:
    - q_est_kms2
    - v_est_asym_kms = sqrt(max(q_est,0)) but NaN if q_est <= 0
    """

    out: dict[str, dict[str, float]] = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise RuntimeError("q_est.csv has no header")
        for row in r:
            g = (row.get("galaxy") or "").strip()
            if not g:
                continue
            q = _parse_float(row.get("q_est_kms2", ""))
            v = math.sqrt(q) if _is_finite(q) and q > 0.0 else float("nan")
            out[g] = {"q_est_kms2": q, "v_est_asym_kms": v}
    return out


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
    """Return beta for y ~ X where X already includes intercept column."""

    n = len(y)
    if n == 0:
        return None
    p = len(X[0])

    XtX = [[0.0 for _ in range(p)] for _ in range(p)]
    Xty = [0.0 for _ in range(p)]
    for i in range(n):
        xi = X[i]
        yi = y[i]
        for a in range(p):
            Xty[a] += xi[a] * yi
            for b in range(p):
                XtX[a][b] += xi[a] * xi[b]

    return _solve_linear_system(XtX, Xty)


def _predict_row(beta: list[float], x: list[float]) -> float:
    return sum(beta[j] * x[j] for j in range(len(beta)))


@dataclass(frozen=True)
class Metrics:
    n: int
    rmse: float
    mae: float
    r2: float


def _metrics(y_true: list[float], y_pred: list[float]) -> Metrics:
    n = len(y_true)
    if n == 0:
        return Metrics(n=0, rmse=float("nan"), mae=float("nan"), r2=float("nan"))

    err2 = [(yp - yt) ** 2 for yt, yp in zip(y_true, y_pred)]
    abse = [abs(yp - yt) for yt, yp in zip(y_true, y_pred)]
    rmse = math.sqrt(sum(err2) / n)
    mae = sum(abse) / n

    mean_y = sum(y_true) / n
    ss_tot = sum((yt - mean_y) ** 2 for yt in y_true)
    ss_res = sum(err2)
    r2 = float("nan") if ss_tot <= 0.0 else 1.0 - (ss_res / ss_tot)

    return Metrics(n=n, rmse=rmse, mae=mae, r2=r2)


def _kfold_indices(n: int, k: int, seed: int) -> list[list[int]]:
    idx = list(range(n))
    rng = random.Random(seed)
    rng.shuffle(idx)

    folds: list[list[int]] = [[] for _ in range(k)]
    for i, j in enumerate(idx):
        folds[i % k].append(j)
    return folds


def _select_by_pattern(fieldnames: list[str], patterns: list[str]) -> list[str]:
    out: set[str] = set()
    for pat in patterns:
        for fn in fieldnames:
            if fn == "galaxy":
                continue
            if fnmatch.fnmatch(fn, pat):
                out.add(fn)
    return sorted(out)


def _collect_transformed_rows(
    rows: list[dict[str, float]],
    target: str,
    union_features: list[str],
    log_features: set[str],
    log_target: bool,
    require_qflag: int | None,
) -> tuple[list[dict[str, float]], list[float]]:
    """Collect transformed feature values for the union feature set.

    Returns a list of per-row dictionaries (feature->value) and the target vector.
    Rows are kept only if target, all union_features, and optional Q-flag filter are valid.
    """

    feat_vals: list[dict[str, float]] = []
    y: list[float] = []

    for row in rows:
        if require_qflag is not None:
            qf = row.get("sparc_Q_flag", float("nan"))
            if not _is_finite(qf) or int(round(qf)) != require_qflag:
                continue

        yt = row.get(target, float("nan"))
        if not _is_finite(yt):
            continue
        if log_target:
            if yt <= 0.0:
                continue
            yt = math.log(yt)

        vals: dict[str, float] = {}
        ok = True
        for f in union_features:
            xv = row.get(f, float("nan"))
            if not _is_finite(xv):
                ok = False
                break
            if f in log_features:
                if xv <= 0.0:
                    ok = False
                    break
                xv = math.log(xv)
            vals[f] = xv
        if not ok:
            continue

        feat_vals.append(vals)
        y.append(yt)

    return feat_vals, y


def _collect_transformed_rows_two_targets(
    rows: list[dict[str, float]],
    target_a: str,
    target_b: str,
    union_features: list[str],
    log_features: set[str],
    log_target: bool,
    require_qflag: int | None,
) -> tuple[list[dict[str, float]], list[float], list[float]]:
    """Collect a matched sample for two different targets.

    The returned (feat_vals, ya, yb) use the same row subset so CV folds are
    directly comparable across targets.
    """

    feat_vals: list[dict[str, float]] = []
    ya: list[float] = []
    yb: list[float] = []

    for row in rows:
        if require_qflag is not None:
            qf = row.get("sparc_Q_flag", float("nan"))
            if not _is_finite(qf) or int(round(qf)) != require_qflag:
                continue

        y1 = row.get(target_a, float("nan"))
        y2 = row.get(target_b, float("nan"))
        if not _is_finite(y1) or not _is_finite(y2):
            continue
        if log_target:
            if y1 <= 0.0 or y2 <= 0.0:
                continue
            y1 = math.log(y1)
            y2 = math.log(y2)

        vals: dict[str, float] = {}
        ok = True
        for f in union_features:
            xv = row.get(f, float("nan"))
            if not _is_finite(xv):
                ok = False
                break
            if f in log_features:
                if xv <= 0.0:
                    ok = False
                    break
                xv = math.log(xv)
            vals[f] = xv
        if not ok:
            continue

        feat_vals.append(vals)
        ya.append(y1)
        yb.append(y2)

    return feat_vals, ya, yb


def _build_matrix(feat_vals: list[dict[str, float]], features: list[str]) -> list[list[float]]:
    X: list[list[float]] = []
    for vals in feat_vals:
        row = [1.0]
        for f in features:
            row.append(vals[f])
        X.append(row)
    return X


def _cv_predict(
    X: list[list[float]],
    y: list[float],
    k: int,
    seed: int,
) -> tuple[list[float], list[float]]:
    n = len(y)
    folds = _kfold_indices(n, k, seed)

    y_true_all: list[float] = []
    y_pred_all: list[float] = []

    all_idx = set(range(n))
    for test_idx in folds:
        test_set = set(test_idx)
        train_idx = [i for i in all_idx if i not in test_set]

        X_train = [X[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]
        beta = _ols_fit(X_train, y_train)
        if beta is None:
            # If singular, skip this fold (rare but possible with redundant features)
            continue

        for i in test_idx:
            y_true_all.append(y[i])
            y_pred_all.append(_predict_row(beta, X[i]))

    return y_true_all, y_pred_all


def _fit_sse(X: list[list[float]], y: list[float]) -> tuple[float, int] | None:
    """Fit OLS and return (SSE, dof) where dof = n - p."""
    beta = _ols_fit(X, y)
    if beta is None:
        return None
    n = len(y)
    p = len(X[0])
    sse = 0.0
    for yi, xi in zip(y, X):
        yp = _predict_row(beta, xi)
        e = yi - yp
        sse += e * e
    dof = n - p
    return sse, dof


def _f_cdf(x: float, d1: int, d2: int) -> float:
    """CDF of the F distribution using the regularized incomplete beta.

    CDF(F; d1,d2) = I_{d1*F/(d1*F + d2)}(d1/2, d2/2)
    """

    if not math.isfinite(x) or x < 0.0:
        return float("nan")
    if d1 <= 0 or d2 <= 0:
        return float("nan")
    z = (d1 * x) / (d1 * x + d2)
    return _reg_incomplete_beta(z, 0.5 * d1, 0.5 * d2)


def _reg_incomplete_beta(x: float, a: float, b: float) -> float:
    """Regularized incomplete beta I_x(a,b) (Numerical Recipes style)."""

    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    # Use symmetry to improve convergence.
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _reg_incomplete_beta(1.0 - x, b, a)

    # Compute front factor: exp(a ln x + b ln(1-x) - ln B(a,b)) / a
    ln_bt = a * math.log(x) + b * math.log(1.0 - x) - _ln_beta(a, b)
    bt = math.exp(ln_bt)
    cf = _beta_continued_fraction(x, a, b)
    return (bt * cf) / a


def _ln_beta(a: float, b: float) -> float:
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _beta_continued_fraction(x: float, a: float, b: float, max_iter: int = 200, eps: float = 3e-14) -> float:
    """Evaluate continued fraction for incomplete beta."""
    # Lentz’s algorithm
    am, bm = 1.0, 1.0
    az = 1.0
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    bz = 1.0 - qab * x / qap
    if abs(bz) < 1e-30:
        bz = 1e-30
    em = 0.0
    tem = 0.0
    d = 1.0 / bz
    ap = az
    bp = bz
    app = 0.0
    bpp = 0.0
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


def nested_f_test(
    y: list[float],
    feat_vals: list[dict[str, float]],
    base_features: list[str],
    ext_features: list[str],
) -> tuple[float, float, int, int] | None:
    """Nested model F-test: base ⊂ extended.

    Returns (F, p_value, d1, d2) where d1 = p_ext - p_base, d2 = n - p_ext.
    p_value is the right-tail probability under the null.
    """

    X0 = _build_matrix(feat_vals, base_features)
    X1 = _build_matrix(feat_vals, ext_features)
    n = len(y)
    p0 = len(X0[0])
    p1 = len(X1[0])
    if p1 <= p0 or n <= p1 + 1:
        return None

    fit0 = _fit_sse(X0, y)
    fit1 = _fit_sse(X1, y)
    if fit0 is None or fit1 is None:
        return None
    sse0, _ = fit0
    sse1, _ = fit1
    d1 = p1 - p0
    d2 = n - p1
    if sse1 <= 0.0:
        return None
    num = (sse0 - sse1) / d1
    den = sse1 / d2
    F = num / den if den > 0.0 else float("nan")
    cdf = _f_cdf(F, d1, d2)
    p = 1.0 - cdf if math.isfinite(cdf) else float("nan")
    return F, p, d1, d2


def _print_metrics(label: str, m: Metrics) -> None:
    print(f"{label}: N={m.n} | RMSE={m.rmse:.3f} | MAE={m.mae:.3f} | R^2={m.r2:.4f}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Out-of-sample predictor (k-fold CV) for edge-response amplitude")
    p.add_argument("--summary", required=True, help="Path to summary.csv")
    p.add_argument(
        "--q-est",
        default="",
        help="Optional path to q_est.csv; if provided, adds q_est_kms2 and v_est_asym_kms columns",
    )
    p.add_argument("--target", default="v_extra_asym_kms", help="Target column (default v_extra_asym_kms)")
    p.add_argument("--features", nargs="*", default=[], help="Feature columns (explicit)")
    p.add_argument("--add-pattern", action="append", default=[], help="Add features matching pattern (can repeat)")
    p.add_argument("--log-features", nargs="*", default=[], help="Feature columns to log-transform")
    p.add_argument("--log-target", action="store_true", help="Log-transform the target")
    p.add_argument("--k", type=int, default=5, help="K folds")
    p.add_argument("--seed", type=int, default=0, help="Shuffle seed")
    p.add_argument("--repeats", type=int, default=1, help="Repeat CV with seeds seed..seed+repeats-1")
    p.add_argument("--require-qflag", type=int, default=-1, help="If set to 1/2/3, keep only rows with sparc_Q_flag==value")
    p.add_argument("--export", default="", help="Optional CSV path to write per-point CV predictions")
    p.add_argument("--compare", action="store_true", help="Run baseline vs extended comparison (fixed feature sets)")
    p.add_argument(
        "--compare-old-new",
        action="store_true",
        help="Run the baseline vs extended comparison twice: v_extra_asym_kms vs v_est_asym_kms (requires --q-est)",
    )
    p.add_argument("--suite", action="store_true", help="Run a standard suite (targets × qflag filters) and print summary")
    return p.parse_args()


def _run_one(
    fieldnames: list[str],
    rows: list[dict[str, float]],
    target: str,
    features: list[str],
    log_features: set[str],
    log_target: bool,
    k: int,
    seed: int,
) -> tuple[Metrics, list[float], list[float]]:
    # Single-run helper for generic mode.
    feat_vals, y = _collect_transformed_rows(
        rows,
        target=target,
        union_features=features,
        log_features=log_features,
        log_target=log_target,
        require_qflag=None,
    )
    X = _build_matrix(feat_vals, features)
    y_true, y_pred = _cv_predict(X, y, k, seed)
    return _metrics(y_true, y_pred), y_true, y_pred


def main() -> None:
    args = parse_args()
    fieldnames, rows, galaxies = _read_summary(args.summary)

    if args.q_est:
        q_map = _read_q_est_map(args.q_est)
        # Add in-place (keeps row order)
        for i, g in enumerate(galaxies):
            qd = q_map.get(g)
            if qd is None:
                rows[i]["q_est_kms2"] = float("nan")
                rows[i]["v_est_asym_kms"] = float("nan")
            else:
                rows[i]["q_est_kms2"] = qd["q_est_kms2"]
                rows[i]["v_est_asym_kms"] = qd["v_est_asym_kms"]
        # Ensure availability checks include these.
        fieldnames = list(fieldnames) + ["q_est_kms2", "v_est_asym_kms"]

    available = set(fieldnames)

    target = args.target
    if args.compare_old_new:
        if not args.q_est:
            raise SystemExit("--compare-old-new requires --q-est")
        if "v_extra_asym_kms" not in available:
            raise SystemExit("Target not found: v_extra_asym_kms")
        if "v_est_asym_kms" not in available:
            raise SystemExit("Target not found: v_est_asym_kms")
    else:
        if target not in available:
            raise SystemExit(f"Target not found: {target}")

    require_qflag = None if args.require_qflag < 0 else int(args.require_qflag)

    if args.suite:
        base_features = ["sparc_Vflat_kms", "sparc_Rdisk_kpc"]
        base_log = {"sparc_Vflat_kms", "sparc_Rdisk_kpc"}
        preferred_fracs = [
            "frac_gas_half_rt",
            "frac_bul_half_rt",
            "frac_gas_rt",
            "frac_bul_rt",
            "frac_bul_peak",
        ]
        ext_features = base_features + [f for f in preferred_fracs if f in available]
        ext_log = set(base_log)

        suite_targets = [
            ("v_extra_asym_kms", False),
            ("v_extra_asym_kms", True),
            ("q_best_kms2", False),
            ("q_best_kms2", True),
        ]
        if args.q_est:
            suite_targets.extend([
                ("v_est_asym_kms", False),
                ("v_est_asym_kms", True),
                ("q_est_kms2", False),
                ("q_est_kms2", True),
            ])
        suite_qflags = [None, 1]

        print("Predictor suite (repeated k-fold CV + nested F-test)")
        print(f"Summary: {args.summary}")
        print(f"k={args.k} seed0={args.seed} repeats={args.repeats}")
        print("")

        for qf in suite_qflags:
            qf_label = "ALL" if qf is None else f"Q_flag=={qf}"
            print(f"=== Sample: {qf_label} ===")
            for target, log_target in suite_targets:
                # Use the same rows for base and extended (intersection): union features.
                union = sorted(dict.fromkeys(base_features + ext_features))
                log_feats = base_log  # only log Vflat/Rdisk
                feat_vals, y = _collect_transformed_rows(
                    rows,
                    target=target,
                    union_features=union,
                    log_features=log_feats,
                    log_target=log_target,
                    require_qflag=qf,
                )
                n = len(y)
                if n < max(10, args.k * 5):
                    print(f"Target={target} log={log_target}: N={n} (too small; skipped)")
                    continue

                X0 = _build_matrix(feat_vals, base_features)
                X1 = _build_matrix(feat_vals, ext_features)

                # Repeated CV
                ms0: list[Metrics] = []
                ms1: list[Metrics] = []
                for s in range(args.seed, args.seed + max(args.repeats, 1)):
                    y0t, y0p = _cv_predict(X0, y, args.k, s)
                    y1t, y1p = _cv_predict(X1, y, args.k, s)
                    ms0.append(_metrics(y0t, y0p))
                    ms1.append(_metrics(y1t, y1p))

                def mean(vals: list[float]) -> float:
                    return sum(vals) / len(vals) if vals else float("nan")

                def stdev(vals: list[float]) -> float:
                    if len(vals) < 2:
                        return float("nan")
                    m = mean(vals)
                    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))

                rmse0 = [m.rmse for m in ms0 if math.isfinite(m.rmse)]
                rmse1 = [m.rmse for m in ms1 if math.isfinite(m.rmse)]
                r20 = [m.r2 for m in ms0 if math.isfinite(m.r2)]
                r21 = [m.r2 for m in ms1 if math.isfinite(m.r2)]

                # Nested F-test on full dataset (same N)
                ftest = nested_f_test(y, feat_vals, base_features, ext_features)
                if ftest is None:
                    f_str = "F=nan p=nan"
                else:
                    F, pval, d1, d2 = ftest
                    f_str = f"F={F:.3f} p={pval:.3g} (d1={d1}, d2={d2})"

                print(
                    f"Target={target} log={log_target} N={n} | "
                    f"BASE rmse={mean(rmse0):.3f}±{stdev(rmse0):.3f} r2={mean(r20):.4f}±{stdev(r20):.4f} | "
                    f"EXT rmse={mean(rmse1):.3f}±{stdev(rmse1):.3f} r2={mean(r21):.4f}±{stdev(r21):.4f} | "
                    f"Δrmse={mean([b-a for a,b in zip(rmse0, rmse1)]):+.3f} | Δr2={mean([b-a for a,b in zip(r20, r21)]):+.4f} | {f_str}"
                )
            print("")
        return

    if args.compare_old_new:
        # Fixed comparison run twice on the *same* matched sample.
        base_features = ["sparc_Vflat_kms", "sparc_Rdisk_kpc"]
        base_log = {"sparc_Vflat_kms", "sparc_Rdisk_kpc"}
        preferred_fracs = [
            "frac_gas_half_rt",
            "frac_bul_half_rt",
            "frac_gas_rt",
            "frac_bul_rt",
            "frac_bul_peak",
        ]
        ext_features = base_features + [f for f in preferred_fracs if f in available]

        union = sorted(dict.fromkeys(base_features + ext_features))
        feat_vals, y_old, y_new = _collect_transformed_rows_two_targets(
            rows,
            target_a="v_extra_asym_kms",
            target_b="v_est_asym_kms",
            union_features=union,
            log_features=base_log,
            log_target=args.log_target,
            require_qflag=require_qflag,
        )

        X0 = _build_matrix(feat_vals, base_features)
        X1 = _build_matrix(feat_vals, ext_features)

        # Same folds: same N, same seed => same fold assignment.
        y0t_old, y0p_old = _cv_predict(X0, y_old, args.k, args.seed)
        y1t_old, y1p_old = _cv_predict(X1, y_old, args.k, args.seed)
        y0t_new, y0p_new = _cv_predict(X0, y_new, args.k, args.seed)
        y1t_new, y1p_new = _cv_predict(X1, y_new, args.k, args.seed)

        m0_old = _metrics(y0t_old, y0p_old)
        m1_old = _metrics(y1t_old, y1p_old)
        m0_new = _metrics(y0t_new, y0p_new)
        m1_new = _metrics(y1t_new, y1p_new)

        print("K-fold CV predictor comparison (old vs new targets; matched sample)")
        print(f"Summary: {args.summary}")
        print(f"Q_est:  {args.q_est}")
        print(f"k={args.k} seed={args.seed} log_target={args.log_target}")
        if require_qflag is not None:
            print(f"Filter: sparc_Q_flag=={require_qflag}")
        print("")
        print(f"Matched N (both targets finite + features valid): {len(y_old)}")
        print("")

        print("=== Target: v_extra_asym_kms (old) ===")
        _print_metrics("BASE (Vflat,Rdisk)", m0_old)
        _print_metrics("EXT  (+ frac_*)", m1_old)
        if math.isfinite(m0_old.rmse) and math.isfinite(m1_old.rmse):
            print(f"ΔRMSE (EXT-BASE): {m1_old.rmse - m0_old.rmse:+.3f}")
        if math.isfinite(m0_old.r2) and math.isfinite(m1_old.r2):
            print(f"ΔR^2  (EXT-BASE): {m1_old.r2 - m0_old.r2:+.4f}")
        ftest_old = nested_f_test(y_old, feat_vals, base_features, ext_features)
        if ftest_old is not None:
            F, pval, d1, d2 = ftest_old
            print(f"Nested F-test (full sample): F={F:.3f} p={pval:.3g} (d1={d1}, d2={d2})")
        print("")

        print("=== Target: v_est_asym_kms (new; from q_est) ===")
        _print_metrics("BASE (Vflat,Rdisk)", m0_new)
        _print_metrics("EXT  (+ frac_*)", m1_new)
        if math.isfinite(m0_new.rmse) and math.isfinite(m1_new.rmse):
            print(f"ΔRMSE (EXT-BASE): {m1_new.rmse - m0_new.rmse:+.3f}")
        if math.isfinite(m0_new.r2) and math.isfinite(m1_new.r2):
            print(f"ΔR^2  (EXT-BASE): {m1_new.r2 - m0_new.r2:+.4f}")
        ftest_new = nested_f_test(y_new, feat_vals, base_features, ext_features)
        if ftest_new is not None:
            F, pval, d1, d2 = ftest_new
            print(f"Nested F-test (full sample): F={F:.3f} p={pval:.3g} (d1={d1}, d2={d2})")

        if args.export:
            with open(args.export, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["target", "model", "y_true", "y_pred"])
                for yt, yp in zip(y0t_old, y0p_old):
                    w.writerow(["v_extra_asym_kms", "BASE", yt, yp])
                for yt, yp in zip(y1t_old, y1p_old):
                    w.writerow(["v_extra_asym_kms", "EXT", yt, yp])
                for yt, yp in zip(y0t_new, y0p_new):
                    w.writerow(["v_est_asym_kms", "BASE", yt, yp])
                for yt, yp in zip(y1t_new, y1p_new):
                    w.writerow(["v_est_asym_kms", "EXT", yt, yp])
            print("")
            print(f"Wrote: {args.export}")
        return

    if args.compare:
        # Fixed comparison: controls-only vs controls+composition fractions.
        base_features = ["sparc_Vflat_kms", "sparc_Rdisk_kpc"]
        base_log = {"sparc_Vflat_kms", "sparc_Rdisk_kpc"}
        # NOTE: don't include all three fractions for the same radius window.
        # (frac_gas + frac_disk + frac_bul = 1) makes OLS singular with an intercept.
        preferred_fracs = [
            "frac_gas_half_rt",
            "frac_bul_half_rt",
            "frac_gas_rt",
            "frac_bul_rt",
            "frac_bul_peak",
        ]
        ext_features = base_features + [f for f in preferred_fracs if f in available]
        ext_log = set(base_log)

        union = sorted(dict.fromkeys(base_features + ext_features))
        feat_vals, y = _collect_transformed_rows(
            rows,
            target=target,
            union_features=union,
            log_features=base_log,
            log_target=args.log_target,
            require_qflag=require_qflag,
        )
        X0 = _build_matrix(feat_vals, base_features)
        X1 = _build_matrix(feat_vals, ext_features)

        # Fair comparison: same y, same folds.
        y0t, y0p = _cv_predict(X0, y, args.k, args.seed)
        y1t, y1p = _cv_predict(X1, y, args.k, args.seed)
        m0 = _metrics(y0t, y0p)
        m1 = _metrics(y1t, y1p)

        print("K-fold CV predictor comparison")
        print(f"Summary: {args.summary}")
        print(f"Target: {target}")
        print(f"k={args.k} seed={args.seed} log_target={args.log_target}")
        if require_qflag is not None:
            print(f"Filter: sparc_Q_flag=={require_qflag}")
        print("")

        _print_metrics("BASE (Vflat,Rdisk)", m0)
        _print_metrics("EXT  (+ frac_*)", m1)
        if math.isfinite(m0.rmse) and math.isfinite(m1.rmse):
            print(f"ΔRMSE (EXT-BASE): {m1.rmse - m0.rmse:+.3f}")
        if math.isfinite(m0.r2) and math.isfinite(m1.r2):
            print(f"ΔR^2  (EXT-BASE): {m1.r2 - m0.r2:+.4f}")

        ftest = nested_f_test(y, feat_vals, base_features, ext_features)
        if ftest is not None:
            F, pval, d1, d2 = ftest
            print(f"Nested F-test (full sample): F={F:.3f} p={pval:.3g} (d1={d1}, d2={d2})")

        # Optional export: export extended model held-out preds vs true.
        if args.export:
            with open(args.export, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["y_true", "y_pred"])
                for yt, yp in zip(y1t, y1p):
                    w.writerow([yt, yp])
            print(f"Wrote: {args.export}")
        return

    # Generic single run
    features = list(args.features)
    if args.add_pattern:
        features.extend(_select_by_pattern(fieldnames, args.add_pattern))
    features = sorted(dict.fromkeys(features))

    for f in features:
        if f not in available:
            raise SystemExit(f"Feature not found: {f}")

    log_features = set(args.log_features)

    m, y_true, y_pred = _run_one(fieldnames, rows, target, features, log_features, args.log_target, args.k, args.seed)
    print("K-fold CV predictor")
    print(f"Summary: {args.summary}")
    print(f"Target: {target}")
    print(f"Features ({len(features)}): {', '.join(features)}")
    print(f"k={args.k} seed={args.seed} log_target={args.log_target}")
    print("")
    _print_metrics("MODEL", m)

    if args.export:
        with open(args.export, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["y_true", "y_pred"])
            for yt, yp in zip(y_true, y_pred):
                w.writerow([yt, yp])
        print(f"Wrote: {args.export}")


if __name__ == "__main__":
    main()
