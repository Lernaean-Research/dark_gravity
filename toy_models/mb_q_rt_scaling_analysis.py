import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, t


BASE = Path(r"D:/#Documents/#Publication/Spacetime_Mechanics__git/toy_models/out_sparc_runs_full_with_composition")
INPUT = BASE / "summary_with_env.csv"
OUTDIR = BASE / "mb_scaling"


def fit_loglog(x: np.ndarray, y: np.ndarray) -> dict:
    lx = np.log10(x)
    ly = np.log10(y)
    X = np.column_stack([np.ones(len(lx)), lx])
    beta, *_ = np.linalg.lstsq(X, ly, rcond=None)
    yhat = X @ beta
    resid = ly - yhat
    dof = len(ly) - X.shape[1]
    sse = float(np.sum(resid**2))
    sst = float(np.sum((ly - np.mean(ly)) ** 2))
    sigma2 = sse / dof if dof > 0 else np.nan
    xtx_inv = np.linalg.inv(X.T @ X)
    cov = sigma2 * xtx_inv if np.isfinite(sigma2) else np.full((2, 2), np.nan)
    se = np.sqrt(np.diag(cov))
    tcrit = float(t.ppf(0.975, dof)) if dof > 0 else np.nan
    slope = float(beta[1])
    intercept = float(beta[0])
    slope_ci = [float(slope - tcrit * se[1]), float(slope + tcrit * se[1])] if np.isfinite(tcrit) else [np.nan, np.nan]
    intercept_ci = [float(intercept - tcrit * se[0]), float(intercept + tcrit * se[0])] if np.isfinite(tcrit) else [np.nan, np.nan]
    r2 = 1.0 - sse / sst if sst > 0 else np.nan
    r_log, p_log = pearsonr(lx, ly)
    return {
        "intercept": intercept,
        "slope": slope,
        "intercept_se": float(se[0]),
        "slope_se": float(se[1]),
        "intercept_ci95": intercept_ci,
        "slope_ci95": slope_ci,
        "r2": float(r2),
        "pearson_log_r": float(r_log),
        "pearson_log_p": float(p_log),
    }


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT).replace([np.inf, -np.inf], np.nan)
    use_cols = [
        "galaxy",
        "ups_disk",
        "ups_bul",
        "frac_disk_rt",
        "frac_bul_rt",
        "q_best_kms2",
        "r_t_kpc",
        "sparc_L36_1e9solLum",
        "sparc_MHI_1e9solMass",
    ]
    d = df[use_cols].dropna().copy()
    d = d[
        (d["q_best_kms2"] > 0)
        & (d["r_t_kpc"] > 0)
        & (d["sparc_L36_1e9solLum"] > 0)
        & (d["sparc_MHI_1e9solMass"] >= 0)
        & (d["ups_disk"] > 0)
        & (d["ups_bul"] > 0)
    ].copy()

    stellar_weight = d["frac_disk_rt"] + d["frac_bul_rt"]
    bulge_share_proxy = np.where(stellar_weight > 0, d["frac_bul_rt"] / stellar_weight, 0.0)
    d["bulge_share_proxy_rt"] = np.clip(bulge_share_proxy, 0.0, 1.0)
    d["ups_eff_rt"] = d["ups_disk"] * (1.0 - d["bulge_share_proxy_rt"]) + d["ups_bul"] * d["bulge_share_proxy_rt"]

    d["mstar_1e9solMass"] = d["ups_eff_rt"] * d["sparc_L36_1e9solLum"]
    d["mgas_1e9solMass"] = 1.33 * d["sparc_MHI_1e9solMass"]
    d["mbary_1e9solMass"] = d["mstar_1e9solMass"] + d["mgas_1e9solMass"]

    rho_q, p_q = spearmanr(d["mbary_1e9solMass"], d["q_best_kms2"])
    rho_rt, p_rt = spearmanr(d["mbary_1e9solMass"], d["r_t_kpc"])

    fit_q = fit_loglog(d["mbary_1e9solMass"].to_numpy(), d["q_best_kms2"].to_numpy())
    fit_rt = fit_loglog(d["mbary_1e9solMass"].to_numpy(), d["r_t_kpc"].to_numpy())

    d[[
        "galaxy",
        "mbary_1e9solMass",
        "mstar_1e9solMass",
        "mgas_1e9solMass",
        "ups_eff_rt",
        "bulge_share_proxy_rt",
        "q_best_kms2",
        "r_t_kpc",
    ]].to_csv(OUTDIR / "mb_q_rt_scaling_sample.csv", index=False)

    summary = {
        "n": int(len(d)),
        "mass_construction": {
            "stellar": "Mstar = Upsilon_eff * L36 with Upsilon_eff built from ups_disk, ups_bul, and rt stellar bulge-share proxy",
            "gas": "Mgas = 1.33 * MHI",
            "ups_disk_baseline": float(d["ups_disk"].median()),
            "ups_bul_baseline": float(d["ups_bul"].median()),
            "median_ups_eff_rt": float(d["ups_eff_rt"].median()),
            "median_bulge_share_proxy_rt": float(d["bulge_share_proxy_rt"].median()),
        },
        "spearman": {
            "mb_q": {"rho": float(rho_q), "p": float(p_q)},
            "mb_rt": {"rho": float(rho_rt), "p": float(p_rt)},
        },
        "loglog_fits": {
            "mb_q": fit_q,
            "mb_rt": fit_rt,
        },
    }
    with open(OUTDIR / "mb_q_rt_scaling_summary.json", "w", encoding="ascii") as f:
        json.dump(summary, f, indent=2)

    with open(OUTDIR / "mb_q_rt_scaling_key_results.txt", "w", encoding="ascii") as f:
        f.write(f"Sample size after QC cuts: n={len(d)}\n")
        f.write("Mass construction:\n")
        f.write("  Mstar = Upsilon_eff * L36 with Upsilon_eff from ups_disk/ups_bul and rt bulge-share proxy\n")
        f.write("  Mgas = 1.33 * MHI\n")
        f.write(f"  median Upsilon_eff(rt) = {d['ups_eff_rt'].median():.4f}\n")
        f.write(f"  median bulge-share proxy(rt) = {d['bulge_share_proxy_rt'].median():.4f}\n")
        f.write(f"Spearman Mb-Q: rho={rho_q:.6f}, p={p_q:.3e}\n")
        f.write(f"Spearman Mb-rt: rho={rho_rt:.6f}, p={p_rt:.3e}\n")
        f.write(
            "Log10(Q) = a + b Log10(Mb): "
            f"b={fit_q['slope']:.6f} (95% CI {fit_q['slope_ci95'][0]:.6f}, {fit_q['slope_ci95'][1]:.6f}), "
            f"r={fit_q['pearson_log_r']:.6f}, p={fit_q['pearson_log_p']:.3e}, R2={fit_q['r2']:.6f}\n"
        )
        f.write(
            "Log10(rt) = a + b Log10(Mb): "
            f"b={fit_rt['slope']:.6f} (95% CI {fit_rt['slope_ci95'][0]:.6f}, {fit_rt['slope_ci95'][1]:.6f}), "
            f"r={fit_rt['pearson_log_r']:.6f}, p={fit_rt['pearson_log_p']:.3e}, R2={fit_rt['r2']:.6f}\n"
        )

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), constrained_layout=True)
    panels = [
        (axes[0], "q_best_kms2", fit_q, "Q [km^2/s^2]", "Mb-Q scaling"),
        (axes[1], "r_t_kpc", fit_rt, "r_t [kpc]", "Mb-r_t scaling"),
    ]
    log_mb = np.log10(d["mbary_1e9solMass"])
    xgrid = np.linspace(log_mb.min(), log_mb.max(), 200)

    for ax, ycol, fit, ylabel, title in panels:
        ax.scatter(d["mbary_1e9solMass"], d[ycol], s=28, alpha=0.8, edgecolors="none")
        ygrid = 10 ** (fit["intercept"] + fit["slope"] * xgrid)
        ax.plot(10 ** xgrid, ygrid, color="black", lw=1.5)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Mbary [10^9 Msun]")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{title}\nSlope={fit['slope']:.3f}")
        ax.grid(alpha=0.2, which="both")

    fig.savefig(OUTDIR / "mb_q_rt_scaling_figure.png", dpi=220)


if __name__ == "__main__":
    main()