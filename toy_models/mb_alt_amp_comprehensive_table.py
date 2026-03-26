import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, rankdata, spearmanr, t


BASE = Path(r"D:/#Documents/#Publication/Spacetime_Mechanics__git/toy_models/out_sparc_runs_full_with_composition")
INPUT = BASE / "summary_with_env.csv"
OUTDIR = BASE / "mb_scaling"


def ols_residual(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    X1 = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    return y - (X1 @ beta)


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple[float, float]:
    xr = rankdata(x)
    yr = rankdata(y)
    zr = rankdata(z)
    ex = ols_residual(xr, zr.reshape(-1, 1))
    ey = ols_residual(yr, zr.reshape(-1, 1))
    return pearsonr(ex, ey)


def fit_loglog(x: np.ndarray, y: np.ndarray) -> dict:
    lx = np.log10(x)
    ly = np.log10(y)
    X = np.column_stack([np.ones(len(lx)), lx])
    beta, *_ = np.linalg.lstsq(X, ly, rcond=None)
    yhat = X @ beta
    resid = ly - yhat
    dof = len(ly) - 2
    sse = float(np.sum(resid**2))
    sst = float(np.sum((ly - np.mean(ly)) ** 2))
    sigma2 = sse / dof if dof > 0 else np.nan
    xtx_inv = np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(sigma2 * xtx_inv)) if np.isfinite(sigma2) else np.array([np.nan, np.nan])
    tcrit = float(t.ppf(0.975, dof)) if dof > 0 else np.nan
    slope = float(beta[1])
    slope_ci = [float(slope - tcrit * se[1]), float(slope + tcrit * se[1])] if np.isfinite(tcrit) else [np.nan, np.nan]
    r, p = pearsonr(lx, ly)
    r2 = 1.0 - sse / sst if sst > 0 else np.nan
    return {
        "slope": slope,
        "slope_ci95_lo": slope_ci[0],
        "slope_ci95_hi": slope_ci[1],
        "pearson_log_r": float(r),
        "pearson_log_p": float(p),
        "r2": float(r2),
    }


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT).replace([np.inf, -np.inf], np.nan)

    cols = [
        "galaxy",
        "ups_disk",
        "ups_bul",
        "frac_disk_rt",
        "frac_bul_rt",
        "sparc_L36_1e9solLum",
        "sparc_MHI_1e9solMass",
        "sparc_Vflat_kms",
        "q_best_kms2",
        "v_extra_asym_kms",
        "r_t_kpc",
        "r_near_rt_kpc",
        "r_near_half_rt_kpc",
    ]
    d = df[cols].copy()
    d = d[
        d["ups_disk"].notna()
        & d["ups_bul"].notna()
        & d["sparc_L36_1e9solLum"].notna()
        & d["sparc_MHI_1e9solMass"].notna()
        & d["sparc_Vflat_kms"].notna()
    ].copy()
    d = d[
        (d["ups_disk"] > 0)
        & (d["ups_bul"] > 0)
        & (d["sparc_L36_1e9solLum"] > 0)
        & (d["sparc_MHI_1e9solMass"] >= 0)
        & (d["sparc_Vflat_kms"] > 0)
    ].copy()

    frac_disk = d["frac_disk_rt"].fillna(0.0).to_numpy()
    frac_bul = d["frac_bul_rt"].fillna(0.0).to_numpy()
    stellar_weight = frac_disk + frac_bul
    bulge_share = np.where(stellar_weight > 0, frac_bul / stellar_weight, 0.0)
    d["ups_eff_rt"] = d["ups_disk"] * (1.0 - bulge_share) + d["ups_bul"] * bulge_share
    d["mbary_1e9solMass"] = d["ups_eff_rt"] * d["sparc_L36_1e9solLum"] + 1.33 * d["sparc_MHI_1e9solMass"]

    # Keep a full frame (with Mb when computable) for exclusion auditing.
    full = df[cols].copy()
    frac_disk_full = full["frac_disk_rt"].fillna(0.0).to_numpy()
    frac_bul_full = full["frac_bul_rt"].fillna(0.0).to_numpy()
    stellar_weight_full = frac_disk_full + frac_bul_full
    bulge_share_full = np.where(stellar_weight_full > 0, frac_bul_full / stellar_weight_full, 0.0)
    full["ups_eff_rt"] = full["ups_disk"] * (1.0 - bulge_share_full) + full["ups_bul"] * bulge_share_full
    full["mbary_1e9solMass"] = full["ups_eff_rt"] * full["sparc_L36_1e9solLum"] + 1.33 * full["sparc_MHI_1e9solMass"]

    metric_specs = [
        ("q_best_kms2", "amplitude", "Q_best"),
        ("v_extra_asym_kms", "amplitude", "V_extra_asym"),
        ("r_t_kpc", "altitude", "r_t"),
        ("r_near_rt_kpc", "altitude", "r_near_rt"),
        ("r_near_half_rt_kpc", "altitude", "r_near_half_rt"),
    ]

    rows = []
    exclusion_rows = []
    logV = np.log10(d["sparc_Vflat_kms"].to_numpy())
    for col, family, label in metric_specs:
        sub = d[["mbary_1e9solMass", col, "sparc_Vflat_kms"]].copy()
        sub = sub[sub[col].notna()].copy()
        sub = sub[(sub["mbary_1e9solMass"] > 0)]
        if col in {"q_best_kms2", "r_t_kpc", "r_near_rt_kpc", "r_near_half_rt_kpc"}:
            sub = sub[sub[col] > 0]

        x = sub["mbary_1e9solMass"].to_numpy()
        y = sub[col].to_numpy()
        z = np.log10(sub["sparc_Vflat_kms"].to_numpy())

        rho, p_rho = spearmanr(x, y)
        prho, p_prho = partial_spearman(x, y, z)

        rec = {
            "metric_family": family,
            "metric": label,
            "n": int(len(sub)),
            "spearman_rho": float(rho),
            "spearman_p": float(p_rho),
            "partial_spearman_rho_control_logVflat": float(prho),
            "partial_spearman_p_control_logVflat": float(p_prho),
        }

        can_log = np.all(x > 0) and np.all(y > 0)
        if can_log:
            rec.update(fit_loglog(x, y))
        else:
            rec.update({
                "slope": np.nan,
                "slope_ci95_lo": np.nan,
                "slope_ci95_hi": np.nan,
                "pearson_log_r": np.nan,
                "pearson_log_p": np.nan,
                "r2": np.nan,
            })

        rows.append(rec)

        # Per-metric exclusion audit with explicit field-level reasons.
        for _, rfull in full.iterrows():
            reasons = []

            if pd.isna(rfull["ups_disk"]):
                reasons.append("missing ups_disk")
            elif rfull["ups_disk"] <= 0:
                reasons.append("non-positive ups_disk")

            if pd.isna(rfull["ups_bul"]):
                reasons.append("missing ups_bul")
            elif rfull["ups_bul"] <= 0:
                reasons.append("non-positive ups_bul")

            if pd.isna(rfull["sparc_L36_1e9solLum"]):
                reasons.append("missing sparc_L36_1e9solLum")
            elif rfull["sparc_L36_1e9solLum"] <= 0:
                reasons.append("non-positive sparc_L36_1e9solLum")

            if pd.isna(rfull["sparc_MHI_1e9solMass"]):
                reasons.append("missing sparc_MHI_1e9solMass")
            elif rfull["sparc_MHI_1e9solMass"] < 0:
                reasons.append("negative sparc_MHI_1e9solMass")

            if pd.isna(rfull["sparc_Vflat_kms"]):
                reasons.append("missing sparc_Vflat_kms")
            elif rfull["sparc_Vflat_kms"] <= 0:
                reasons.append("non-positive sparc_Vflat_kms")

            if pd.isna(rfull[col]):
                reasons.append(f"missing {col}")
            elif col in {"q_best_kms2", "r_t_kpc", "r_near_rt_kpc", "r_near_half_rt_kpc"} and rfull[col] <= 0:
                reasons.append(f"non-positive {col}")

            if pd.isna(rfull["mbary_1e9solMass"]):
                reasons.append("unable to construct mbary_1e9solMass")
            elif rfull["mbary_1e9solMass"] <= 0:
                reasons.append("non-positive mbary_1e9solMass")

            if reasons:
                exclusion_rows.append(
                    {
                        "metric_family": family,
                        "metric": label,
                        "galaxy": rfull.get("galaxy", ""),
                        "reason": "; ".join(reasons),
                    }
                )

    out = pd.DataFrame(rows)
    out.to_csv(OUTDIR / "mb_alt_amp_comprehensive_table.csv", index=False)

    excl = pd.DataFrame(exclusion_rows)
    excl.to_csv(OUTDIR / "mb_alt_amp_exclusions_by_metric.csv", index=False)

    md_lines = [
        "# Comprehensive Mb-Altitude/Amplitude Relationships",
        "",
        "Mass definition: Mb = Upsilon_eff * L36 + 1.33*MHI, with Upsilon_eff from ups_disk/ups_bul and rt bulge-share proxy.",
        "",
        "| Family | Metric | n | Spearman rho (p) | Partial rho | Log-log slope b [95% CI] | log Pearson r (p) | R2 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for _, r in out.iterrows():
        md_lines.append(
            "| "
            f"{r['metric_family']} | {r['metric']} | {int(r['n'])} | "
            f"{r['spearman_rho']:.3f} ({r['spearman_p']:.2e}) | "
            f"{r['partial_spearman_rho_control_logVflat']:.3f} ({r['partial_spearman_p_control_logVflat']:.2e}) | "
            f"{r['slope']:.3f} [{r['slope_ci95_lo']:.3f}, {r['slope_ci95_hi']:.3f}] | "
            f"{r['pearson_log_r']:.3f} ({r['pearson_log_p']:.2e}) | "
            f"{r['r2']:.3f} |"
        )

    (OUTDIR / "mb_alt_amp_comprehensive_table.md").write_text("\n".join(md_lines) + "\n", encoding="ascii")

    excl_lines = [
        "# Mb-Altitude/Amplitude Exclusions By Metric",
        "",
        "Each row lists a galaxy omitted for that metric and why it could not be included.",
        "",
    ]
    if len(excl) == 0:
        excl_lines.append("No exclusions.")
    else:
        grouped = excl.groupby(["metric_family", "metric"], observed=True)
        for (fam, met), g in grouped:
            excl_lines.append(f"## {fam} :: {met}")
            excl_lines.append("")
            excl_lines.append(f"Excluded count: {len(g)}")
            excl_lines.append("")
            excl_lines.append("| Galaxy | Reason |")
            excl_lines.append("|---|---|")
            for _, rr in g.sort_values("galaxy").iterrows():
                excl_lines.append(f"| {rr['galaxy']} | {rr['reason']} |")
            excl_lines.append("")
    (OUTDIR / "mb_alt_amp_exclusions_by_metric.md").write_text("\n".join(excl_lines) + "\n", encoding="ascii")

    payload = {
        "n_total_after_qc": int(len(d)),
        "table_csv": str(OUTDIR / "mb_alt_amp_comprehensive_table.csv"),
        "table_md": str(OUTDIR / "mb_alt_amp_comprehensive_table.md"),
        "exclusions_csv": str(OUTDIR / "mb_alt_amp_exclusions_by_metric.csv"),
        "exclusions_md": str(OUTDIR / "mb_alt_amp_exclusions_by_metric.md"),
    }
    with open(OUTDIR / "mb_alt_amp_comprehensive_summary.json", "w", encoding="ascii") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    main()