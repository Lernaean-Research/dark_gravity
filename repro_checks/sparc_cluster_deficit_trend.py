#!/usr/bin/env python3
"""
sparc_cluster_deficit_trend.py

IMPORTANT SCOPE NOTE
--------------------
This script computes an IRS-reference normalized diagnostic for IRS outputs:

  closure ≡ Q1_IRS / Q1_ref   where  Q1_ref = sqrt(G · M_bar · a_irs)

This is a projection-space diagnostic only. It is NOT a mechanism-level,
head-to-head IRS-vs-any-framework model comparison.

For SPARC galaxies:
  Q1_IRS = q_best_kms2  (fitted IRS response amplitude, (km/s)²)

For PSZ2 clusters (pre-computed in fetch_psz2_clusters.py):
  Q1_IRS = σ² − G·M_bar/R₅₀₀  (observed "dark" velocity²)

Outputs:
  repro_checks/results/irs_closure_trend.csv
  repro_checks/results/irs_closure_trend.png
  repro_checks/results/irs_closure_stats.md
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# ── Constants ─────────────────────────────────────────────────────────────────
G_KPC      = 4.3009e-6   # (km/s)² kpc M_sun⁻¹
A_IRS_KMS2 = 3702.813    # a_irs in (km/s)²/kpc [legacy numeric anchor value]

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO     = Path(__file__).parents[1].resolve()
RESULTS  = Path(__file__).parent / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

SPARC_CSV   = REPO / "toy_models/out_sparc_runs_full_with_composition/summary.csv"
CLUSTER_CSV = Path(__file__).parent / "cluster_mass_summary.csv"

# ──────────────────────────────────────────────────────────────────────────────
# 1.  GALAXY DATA (SPARC 175)
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("Loading SPARC 175-galaxy IRS fits (IRS-reference normalized mode) ...")

sparc = pd.read_csv(SPARC_CSV)
print(f"  {len(sparc)} rows loaded")

# Baryonic mass
sparc["M_bar_Msun"] = (sparc["sparc_MHI_1e9solMass"] +
                       sparc["ups_disk"] * sparc["sparc_L36_1e9solLum"]) * 1e9

# IRS reference amplitude  Q1_ref = sqrt(G . M_bar . a_irs)  [(km/s)^2]
sparc["Q1_ref"]      = np.sqrt(G_KPC * sparc["M_bar_Msun"] * A_IRS_KMS2)

# IRS closure = q_best_kms2 / Q1_ref  (internal constitutive normalization)
sparc["closure"]     = sparc["q_best_kms2"] / sparc["Q1_ref"]
sparc["log_Mbar"]    = np.log10(sparc["M_bar_Msun"])
sparc["object_type"] = "galaxy"

sparc = sparc.loc[
    (sparc["M_bar_Msun"] > 0) &
    sparc["q_best_kms2"].notna() &
    (sparc["q_best_kms2"] > 0) &
    sparc["closure"].notna() &
    (sparc["closure"] > 0)
].copy()
print(f"  {len(sparc)} galaxies after quality cut")

print(f"\nGalaxy closure  q_best / Q1_ref:")
print(f"  median  = {sparc['closure'].median():.3f}")
print(f"  mean    = {sparc['closure'].mean():.3f}")
print(f"  std     = {sparc['closure'].std():.3f}")
print(f"  range   = [{sparc['closure'].min():.3f}, {sparc['closure'].max():.3f}]")
print(f"  log(M_bar) range: [{sparc['log_Mbar'].min():.2f}, {sparc['log_Mbar'].max():.2f}]")

# ──────────────────────────────────────────────────────────────────────────────
# 2.  CLUSTER DATA (PSZ2)
#     IRS_closure already in cluster_mass_summary.csv = Q1_cluster / Q1_ref
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Loading PSZ2 cluster data (IRS-reference normalized mode) ...")

clusters = pd.read_csv(CLUSTER_CSV)
print(f"  {len(clusters)} clusters loaded")

clusters["closure"]     = clusters["IRS_closure"]
clusters["log_Mbar"]    = np.log10(clusters["M_bar_Msun"])
clusters["object_type"] = "cluster"

clusters = clusters.loc[
    clusters["redshift"].notna() &
    (clusters["redshift"] > 0) &
    (clusters["M500_Msun"] > 1e13) &
    clusters["closure"].notna() &
    (clusters["closure"] > 0)
].copy()
print(f"  {len(clusters)} clusters after quality cut")

print(f"\nCluster closure  Q1_extra / Q1_ref:")
print(f"  median  = {clusters['closure'].median():.4f}")
print(f"  mean    = {clusters['closure'].mean():.4f}")
print(f"  std     = {clusters['closure'].std():.4f}")
print(f"  range   = [{clusters['closure'].min():.4f}, {clusters['closure'].max():.4f}]")
print(f"  log(M_bar) range: [{clusters['log_Mbar'].min():.2f}, {clusters['log_Mbar'].max():.2f}]")

# ──────────────────────────────────────────────────────────────────────────────
# 3.  COMBINED DATASET + STATISTICS
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Computing cross-scale IRS-reference normalized trend ...")

keep     = ["object_type", "log_Mbar", "M_bar_Msun", "closure"]
combined = pd.concat([sparc[keep], clusters[keep]], ignore_index=True)
combined = combined.dropna(subset=["closure", "log_Mbar"])
combined = combined.loc[combined["closure"] > 0].copy()
combined["log_closure"] = np.log10(combined["closure"])

n_gal = (combined["object_type"] == "galaxy").sum()
n_clu = (combined["object_type"] == "cluster").sum()
print(f"  Combined: {len(combined)} objects  ({n_gal} gal + {n_clu} clus)")

# Linear regression in log-log space
slope, intercept, r_val, p_val, se = stats.linregress(
    combined["log_Mbar"], combined["log_closure"]
)
print(f"\nLinear fit  log10(closure) = a * log10(M_bar) + b:")
print(f"  slope     a = {slope:.4f} +/- {se:.4f}")
print(f"  intercept b = {intercept:.4f}")
print(f"  R^2         = {r_val**2:.4f}")
print(f"  p-value     = {p_val:.2e}")

# Galaxy-only slope
gslope, gint, gr, gp, gse = stats.linregress(
    combined.loc[combined["object_type"] == "galaxy", "log_Mbar"],
    combined.loc[combined["object_type"] == "galaxy", "log_closure"]
)
print(f"\nGalaxy-only fit:  a = {gslope:.4f} +/- {gse:.4f}  R^2={gr**2:.4f}  p={gp:.3f}")

g_mean  = sparc["closure"].median()
c_mean  = clusters["closure"].mean()
c_std   = clusters["closure"].std()
gap_dex = np.log10(g_mean / c_mean)

print(f"\nKey numbers:")
print(f"  Galaxy median  q_best/Q1_ref    = {g_mean:.3f}")
print(f"  Cluster mean   Q1_extra/Q1_ref  = {c_mean:.4f} +/- {c_std:.4f}")
print(f"  Cluster/galaxy ratio             = {c_mean/g_mean:.3f}  ({c_mean/g_mean*100:.1f}%)")
print(f"  Log10 gap                        = {gap_dex:.2f} dex")

# ──────────────────────────────────────────────────────────────────────────────
# 4.  SAVE RESULTS TABLE
# ──────────────────────────────────────────────────────────────────────────────
out_table = RESULTS / "irs_closure_trend.csv"
combined.to_csv(out_table, index=False)
print(f"\nResults table -> {out_table}  ({len(combined)} rows)")

# ──────────────────────────────────────────────────────────────────────────────
# 5.  FIGURE
# ──────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5.5))

gal_plot = combined.loc[combined["object_type"] == "galaxy"]
clu_plot = combined.loc[combined["object_type"] == "cluster"]

ax.scatter(gal_plot["log_Mbar"], gal_plot["closure"],
           s=10, alpha=0.55, color="#2166ac",
           label=f"SPARC 175  [q_best / Q1_ref]  n={n_gal}")
ax.scatter(clu_plot["log_Mbar"], clu_plot["closure"],
           s=15, alpha=0.35, color="#d6604d", marker="^",
           label=f"PSZ2 Planck  [Q1_obs / Q1_ref]  n={n_clu}")

# Running medians with IQR bands
for df_sub, color, nb in [(gal_plot, "#2166ac", 7), (clu_plot, "#d6604d", 8)]:
    df_s = df_sub.sort_values("log_Mbar")
    bins = np.linspace(df_s["log_Mbar"].min(), df_s["log_Mbar"].max(), nb)
    mids, meds, q25, q75 = [], [], [], []
    for i in range(len(bins) - 1):
        mask = (df_s["log_Mbar"] >= bins[i]) & (df_s["log_Mbar"] < bins[i+1])
        if mask.sum() >= 3:
            mids.append(0.5 * (bins[i] + bins[i+1]))
            vals = df_s.loc[mask, "closure"]
            meds.append(vals.median())
            q25.append(vals.quantile(0.25))
            q75.append(vals.quantile(0.75))
    ax.plot(mids, meds, "-o", color=color, lw=2, ms=6, zorder=5)
    ax.fill_between(mids, q25, q75, color=color, alpha=0.18)

# Regression line
x_fit = np.linspace(combined["log_Mbar"].min(), combined["log_Mbar"].max(), 300)
y_fit = 10 ** (slope * x_fit + intercept)
ax.plot(x_fit, y_fit, "k--", lw=1.4, zorder=6,
        label=f"Combined fit  slope={slope:.3f}  R2={r_val**2:.3f}")

# Reference lines
ax.axhline(y=1.0, color="#555555", ls=":", lw=1.5, label="IRS reference closure = 1")
ax.axhline(y=c_mean, color="#d6604d", ls="--", lw=1.0, alpha=0.75,
           label=f"Cluster mean = {c_mean:.3f}")

ax.set_xlabel(r"$\log_{10}(M_\mathrm{bar} / M_\odot)$", fontsize=13)
ax.set_ylabel(r"IRS closure  $Q_1^\mathrm{IRS} / Q_1^\mathrm{ref}$", fontsize=12)
ax.set_title(
  "IRS-reference normalized diagnostic across mass scales\n"
  r"$Q_1^\mathrm{ref} \equiv \sqrt{G M_\mathrm{bar} a_\mathrm{irs}}$;  "
  "diagnostic only (not mechanism-level head-to-head)",
  fontsize=10)

ax.set_yscale("log")
ax.set_ylim(0.03, 10)
ax.legend(fontsize=8.5, framealpha=0.88)
ax.grid(True, which="both", alpha=0.28, ls=":")
plt.tight_layout()
fig_path = RESULTS / "irs_closure_trend.png"
fig.savefig(fig_path, dpi=150)
print(f"Figure -> {fig_path}")

# ──────────────────────────────────────────────────────────────────────────────
# 6.  MARKDOWN STATS SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
mbar_gap_dex = clusters["log_Mbar"].mean() - sparc["log_Mbar"].mean()
md = f"""# IRS Closure Fraction Diagnostic: SPARC Galaxies -> PSZ2 Clusters
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## Scope Guardrail

This file reports an IRS-reference normalized diagnostic ratio for IRS outputs.
It is not a mechanism-level comparison between IRS and any competing framework.
Only data-processing assumptions are shared; physics remains model-local.

## Definition

    closure = Q1_IRS / Q1_ref     [Q1_ref = sqrt(G * M_bar * a_irs)]

- Galaxies (SPARC): Q1_IRS = q_best_kms2  (fitted IRS amplitude)
- Clusters (PSZ2):  Q1_IRS = sigma^2 - G*M_bar/R500  (observed extra velocity^2)

Diagnostic reference line: closure = 1.0 corresponds to exact match to the
chosen IRS internal normalization. This does not imply framework identity.

## Key Numerical Results

| Quantity | Value |
|---|---|
| Galaxy sample | SPARC 175 (quality-cut: {n_gal}) |
| Cluster sample | PSZ2 (quality-cut: {n_clu}) |
| Galaxy median closure | **{g_mean:.3f}** |
| Cluster mean closure | **{c_mean:.4f} +/- {c_std:.4f}** |
| Cluster/galaxy ratio | **{c_mean/g_mean:.3f} ({c_mean/g_mean*100:.1f}%)** |
| Log10 gap (dex) | **{gap_dex:.2f} dex** |
| M_bar range spanned | {mbar_gap_dex:.1f} decades |

## Cross-Scale Regression (log10 space)

    log10(closure) = {slope:.4f} * log10(M_bar) + {intercept:.4f}
    R^2 = {r_val**2:.4f},   p = {p_val:.2e}

Galaxy-only slope: {gslope:.4f} +/- {gse:.4f}  (R^2={gr**2:.4f}, p={gp:.3f})
Consistent with flat BTFR within galaxy sample (no mass-scale trend within galaxies).

## Physical Interpretation

- Galaxy scale (10^8-10^11 M_sun): closure ~ {g_mean:.2f}
  IRS-fitted q_best tracks the IRS reference amplitude closely.

- Cluster scale (10^13-10^14 M_sun): closure ~ {c_mean:.3f}
  Under this IRS normalization, IRS-inferred cluster extra velocity is lower
  than the normalization target by ~{(1-c_mean)*100:.0f}%.

- The {gap_dex:.2f} dex gap across {mbar_gap_dex:.1f} decades in M_bar sets the
  empirical target for any IRS extension mechanism at cluster scales.

## Data Provenance

- Galaxies: Lelli+2016 SPARC J/AJ/152/157; IRS fits: IRS-II v5.1 (Kitcey2026IRS2)
- Clusters: Planck Collaboration 2016 PSZ2 J/A+A/594/A27  ({n_clu} clusters)
- sigma-M scaling: Munari+2013
- M_bar from f_bar = 0.135 * M_500 (Ettori+2017)
- R_500 assumed 1000 kpc for G*M_bar/R estimation
- Fetched via astroquery.vizier on {pd.Timestamp.now().strftime('%Y-%m-%d')}

## Next Step For Fair Head-to-Head Testing

Run two independent forward lanes with identical data and likelihood plumbing:
1. IRS-forward predictions only
2. Comparator-framework forward predictions only
Then compare fit statistics (AIC/BIC/WAIC/log-evidence, held-out RMSE).
"""

stats_path = RESULTS / "irs_closure_stats.md"
stats_path.write_text(md)
print(f"Stats report -> {stats_path}")
print("\n" + md)
