import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE = Path(r"D:/#Documents/#Publication/Spacetime_Mechanics__git/toy_models/out_sparc_runs_full_with_composition")
INPUT = BASE / "summary_with_env.csv"
OUTDIR = BASE / "fixed_vmax_diversity"


def fit_ols(X: np.ndarray, y: np.ndarray) -> dict:
    X1 = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    yhat = X1 @ beta
    resid = y - yhat
    sse = float(np.sum(resid**2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - sse / sst if sst > 0 else np.nan
    return {"beta": beta, "yhat": yhat, "resid": resid, "r2": r2}


def kfold_cv_r2(X: np.ndarray, y: np.ndarray, k: int = 5, seed: int = 42) -> float:
    n = len(y)
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    folds = np.array_split(idx, k)
    y_true_all = []
    y_pred_all = []

    for test_idx in folds:
        train_mask = np.ones(n, dtype=bool)
        train_mask[test_idx] = False
        train_idx = np.where(train_mask)[0]

        Xtr, ytr = X[train_idx], y[train_idx]
        Xte, yte = X[test_idx], y[test_idx]

        mu = Xtr.mean(axis=0)
        sd = Xtr.std(axis=0)
        sd[sd == 0] = 1.0
        Xtrz = (Xtr - mu) / sd
        Xtez = (Xte - mu) / sd

        fit = fit_ols(Xtrz, ytr)
        beta = fit["beta"]
        ypred = np.column_stack([np.ones(len(Xtez)), Xtez]) @ beta

        y_true_all.append(yte)
        y_pred_all.append(ypred)

    y_true = np.concatenate(y_true_all)
    y_pred = np.concatenate(y_pred_all)
    sse = float(np.sum((y_true - y_pred) ** 2))
    sst = float(np.sum((y_true - np.mean(y_true)) ** 2))
    return 1.0 - sse / sst if sst > 0 else np.nan


def permutation_pvalue(X: np.ndarray, y: np.ndarray, observed: float, n_perm: int = 500, seed: int = 123) -> float:
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        yp = rng.permutation(y)
        r2p = kfold_cv_r2(X, yp, k=5, seed=int(rng.integers(0, 1_000_000_000)))
        if np.isfinite(r2p) and r2p >= observed:
            count += 1
    return (count + 1) / (n_perm + 1)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT)

    use_cols = [
        "galaxy",
        "sparc_Vflat_kms",
        "s_in_dlng_dlnr",
        "v_extra_asym_kms",
        "sparc_Rdisk_kpc",
        "frac_gas_rt",
        "frac_bul_rt",
    ]
    d = df[use_cols].copy()
    d = d.replace([np.inf, -np.inf], np.nan).dropna()
    d = d[d["sparc_Vflat_kms"] > 20.0].copy()

    d["logV"] = np.log10(d["sparc_Vflat_kms"])
    d["logRdisk"] = np.log10(d["sparc_Rdisk_kpc"])

    # Fixed-width Vmax bins to quantify shape diversity at matched velocity scale.
    bins = [20, 60, 100, 140, 200, 360]
    labels = ["20-60", "60-100", "100-140", "140-200", "200-360"]
    d["vmax_bin"] = pd.cut(d["sparc_Vflat_kms"], bins=bins, labels=labels, right=False)

    bin_table = (
        d.groupby("vmax_bin", observed=True)
        .agg(
            n=("galaxy", "count"),
            Vflat_mean=("sparc_Vflat_kms", "mean"),
            slope_std=("s_in_dlng_dlnr", "std"),
            slope_iqr=("s_in_dlng_dlnr", lambda x: x.quantile(0.75) - x.quantile(0.25)),
            asym_std=("v_extra_asym_kms", "std"),
            asym_iqr=("v_extra_asym_kms", lambda x: x.quantile(0.75) - x.quantile(0.25)),
            mean_gas=("frac_gas_rt", "mean"),
            mean_bulge=("frac_bul_rt", "mean"),
        )
        .reset_index()
    )
    bin_table.to_csv(OUTDIR / "fixed_vmax_diversity_bins.csv", index=False)

    # Step 1: remove Vmax trend from shape metric.
    trend_fit = fit_ols(d[["logV"]].to_numpy(), d["s_in_dlng_dlnr"].to_numpy())
    d["shape_resid"] = trend_fit["resid"]

    # Step 2: explain residual diversity with baryonic geometry/composition proxies.
    X = d[["logRdisk", "frac_gas_rt", "frac_bul_rt"]].to_numpy()
    y = d["shape_resid"].to_numpy()

    X_mu = X.mean(axis=0)
    X_sd = X.std(axis=0)
    X_sd[X_sd == 0] = 1.0
    Xz = (X - X_mu) / X_sd

    geom_fit = fit_ols(Xz, y)
    cv_r2 = kfold_cv_r2(X, y, k=5, seed=42)
    pval = permutation_pvalue(X, y, cv_r2, n_perm=500, seed=123)

    d["shape_resid_pred"] = geom_fit["yhat"]

    # Residual spread before vs after geometry model within each fixed-Vmax bin.
    spread_rows = []
    for label in labels:
        sub = d[d["vmax_bin"] == label]
        if len(sub) < 5:
            continue
        pre = float(sub["shape_resid"].std(ddof=1))
        post = float((sub["shape_resid"] - sub["shape_resid_pred"]).std(ddof=1))
        frac_red = (pre - post) / pre if pre > 0 else np.nan
        spread_rows.append({
            "vmax_bin": label,
            "n": int(len(sub)),
            "resid_std_pre": pre,
            "resid_std_post": post,
            "fractional_reduction": frac_red,
        })

    spread_df = pd.DataFrame(spread_rows)
    spread_df.to_csv(OUTDIR / "fixed_vmax_residual_spread_reduction.csv", index=False)

    coef = geom_fit["beta"]
    model_summary = {
        "n": int(len(d)),
        "trend_model_r2": float(trend_fit["r2"]),
        "geometry_model_r2_in_sample": float(geom_fit["r2"]),
        "geometry_model_cv_r2": float(cv_r2),
        "geometry_model_cv_r2_permutation_p": float(pval),
        "coefficients_standardized": {
            "intercept": float(coef[0]),
            "logRdisk": float(coef[1]),
            "frac_gas_rt": float(coef[2]),
            "frac_bul_rt": float(coef[3]),
        },
        "slope_std_all": float(d["s_in_dlng_dlnr"].std(ddof=1)),
        "shape_resid_std_all": float(d["shape_resid"].std(ddof=1)),
        "shape_resid_after_geom_std_all": float((d["shape_resid"] - d["shape_resid_pred"]).std(ddof=1)),
    }
    with open(OUTDIR / "fixed_vmax_model_summary.json", "w", encoding="ascii") as f:
        json.dump(model_summary, f, indent=2)

    # Figure: fixed-Vmax diversity + geometry model explanatory power.
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), constrained_layout=True)

    ax = axes[0]
    sc = ax.scatter(
        d["sparc_Vflat_kms"],
        d["s_in_dlng_dlnr"],
        c=d["frac_gas_rt"],
        cmap="viridis",
        s=28,
        alpha=0.8,
        edgecolors="none",
    )
    vgrid = np.linspace(d["sparc_Vflat_kms"].min(), d["sparc_Vflat_kms"].max(), 200)
    vtrend = np.column_stack([np.ones(len(vgrid)), np.log10(vgrid)]) @ trend_fit["beta"]
    ax.plot(vgrid, vtrend, color="black", lw=1.6, label="trend vs log10(Vflat)")

    for _, row in bin_table.iterrows():
        xc = row["Vflat_mean"]
        ys = row["slope_std"]
        ax.text(xc, -1.9, f"{row['vmax_bin']}\n$\\sigma_s$={ys:.2f}", fontsize=7, ha="center")

    ax.set_xlabel("SPARC Vflat [km/s]")
    ax.set_ylabel("Shape metric s_in_dlng_dlnr")
    ax.set_title("Rotation-curve shape diversity at fixed Vmax")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", fontsize=8)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_label("Gas fraction at r_t")

    ax2 = axes[1]
    ax2.scatter(d["shape_resid_pred"], d["shape_resid"], s=28, alpha=0.8, edgecolors="none")
    lim = max(np.max(np.abs(d["shape_resid_pred"])), np.max(np.abs(d["shape_resid"]))) * 1.05
    ax2.plot([-lim, lim], [-lim, lim], "k--", lw=1.0)
    ax2.set_xlim(-lim, lim)
    ax2.set_ylim(-lim, lim)
    ax2.set_xlabel("Predicted residual (geometry model)")
    ax2.set_ylabel("Observed residual after Vmax trend removal")
    ax2.set_title(
        f"Geometry explains fixed-Vmax residuals\n"
        f"CV $R^2$={cv_r2:.3f}, perm-p={pval:.3f}"
    )
    ax2.grid(alpha=0.2)

    fig.savefig(OUTDIR / "fixed_vmax_diversity_figure.png", dpi=220)

    # Plain-text report for easy manuscript insertion.
    with open(OUTDIR / "fixed_vmax_key_results.txt", "w", encoding="ascii") as f:
        f.write(f"Sample size after QC cuts: n={len(d)}\n")
        f.write("Diversity by fixed Vflat bins (std of shape metric s):\n")
        for _, row in bin_table.iterrows():
            f.write(
                f"  {row['vmax_bin']}: n={int(row['n'])}, "
                f"std_s={row['slope_std']:.3f}, iqr_s={row['slope_iqr']:.3f}, "
                f"std_asym={row['asym_std']:.2f}\n"
            )
        f.write(
            "Geometry model on residual shape at fixed Vmax: "
            f"in-sample R2={geom_fit['r2']:.3f}, CV R2={cv_r2:.3f}, perm-p={pval:.3f}\n"
        )
        f.write(
            "Standardized coefficients: "
            f"logRdisk={coef[1]:.3f}, frac_gas_rt={coef[2]:.3f}, frac_bul_rt={coef[3]:.3f}\n"
        )


if __name__ == "__main__":
    main()
