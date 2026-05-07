"""
sparc_sigma_correlation.py
==========================
Open Question #2: Is the IRS source-scale parameter σ_kpc correlated with
observable galaxy properties?

Reads sparc_bic_results.csv produced by sparc_analysis.py and computes
Spearman rank correlations between the fitted σ (from IRS+σ, k=2 and
IRS+σ+Υ, k=3) and:
  - n_pts          : number of rotation-curve data points (richness/radial extent proxy)
  - r_t_kpc        : IRS transition radius (radius where g_bar = a_0)
  - Q_best         : IRS amplitude parameter
  - distance_mpc   : galaxy distance (angular resolution proxy)
  - Y_disk_fit     : fitted Υ_disk (IRS+Υ, k=2)
  - dbic_resp_vs_nfw : pairwise BIC margin

Physical expectation:
  σ_kpc ~ R_eff (half-light radius): galaxies with more extended baryonic
  distributions need a larger source coherence scale to match the outer
  rotation curve.  We expect Spearman r(σ, n_pts) > 0 (bigger = more points)
  and r(σ, r_t_kpc) > 0 (σ tracks the structural scale).
"""

import pathlib
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ─── paths ────────────────────────────────────────────────────────────────────
_DIR = pathlib.Path(__file__).parent
CSV  = _DIR / "sparc_bic_results.csv"
OUT  = _DIR / "sparc_sigma_correlation.json"
FIG  = _DIR / "sparc_sigma_correlation_figure.png"

if not CSV.exists():
    raise FileNotFoundError(f"CSV not found: {CSV}\nRun sparc_analysis.py first.")

df = pd.read_csv(CSV)
print(f"Loaded {len(df)} galaxies from {CSV.name}")

# ─── columns to correlate against σ (both k=2 and k=3 flavours) ───────────────
SIGMA_COLS = ["sigma_fit_kpc", "sigma_fit_k3_kpc"]
SIGMA_LABELS = {
    "sigma_fit_kpc":    "σ_kpc (IRS+σ, k=2)",
    "sigma_fit_k3_kpc": "σ_kpc (IRS+σ+Υ, k=3)",
}

TARGETS = [
    ("n_pts",            "n_pts (data-point count)"),
    ("r_t_kpc",          "R_t  [kpc]  (IRS transition radius)"),
    ("Q_best",           "Q  (IRS amplitude)"),
    ("distance_mpc",     "Distance  [Mpc]"),
    ("Y_disk_fit",       "Υ_disk  (IRS+Υ, k=2)"),
    ("dbic_resp_vs_nfw", "ΔBIC (IRS k=1 − NFW k=2)"),
]

results = {}
print("\n── Spearman correlations ──────────────────────────────────────────────")
for sigma_col, sigma_label in SIGMA_LABELS.items():
    sig_series = df[sigma_col].dropna()
    print(f"\n  [{sigma_label}]  n_valid = {len(sig_series)}")
    results[sigma_col] = {}
    for tcol, tlabel in TARGETS:
        if tcol not in df.columns:
            print(f"    {tlabel:40s}  — column missing, skip")
            continue
        paired = df[[sigma_col, tcol]].dropna()
        if len(paired) < 10:
            print(f"    {tlabel:40s}  — too few paired points ({len(paired)})")
            continue
        r, p = stats.spearmanr(paired[sigma_col], paired[tcol])
        stars = ("***" if p < 0.001 else
                 "**"  if p < 0.01  else
                 "*"   if p < 0.05  else "ns")
        print(f"    {tlabel:40s}  r = {r:+.3f}   p = {p:.4f}  {stars}")
        results[sigma_col][tcol] = {"spearman_r": float(r), "p_value": float(p)}

# ─── partial correlation: σ vs r_t controlling for distance ──────────────────
print("\n── Partial correlations (σ vs R_t, controlled for distance) ──────────")
for sigma_col, sigma_label in SIGMA_LABELS.items():
    needed = [sigma_col, "r_t_kpc", "distance_mpc"]
    sub = df[needed].dropna()
    if len(sub) < 10:
        continue
    # Partial via residuals: regress out distance from both σ and r_t
    def residuals(x, z):
        slope, intercept, *_ = stats.linregress(z, x)
        return x - (slope * z + intercept)
    sig_res = residuals(sub[sigma_col].values, sub["distance_mpc"].values)
    rt_res  = residuals(sub["r_t_kpc"].values,  sub["distance_mpc"].values)
    r_part, p_part = stats.spearmanr(sig_res, rt_res)
    print(f"  [{sigma_label}]  partial r(σ, R_t | dist) = {r_part:+.3f}   p = {p_part:.4f}")
    results[sigma_col]["partial_r_sigma_vs_rt_controlling_distance"] = {
        "spearman_r": float(r_part), "p_value": float(p_part)
    }

# ─── figures ──────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10))
fig.suptitle(
    "IRS σ_kpc Correlation Analysis — SPARC 171 Galaxies\n"
    "σ as proxy for baryonic source coherence scale",
    fontsize=13, fontweight="bold")

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)

plot_pairs = [
    ("r_t_kpc",          "R_t [kpc]",             0, 0),
    ("n_pts",            "Data-point count",       0, 1),
    ("Q_best",           "IRS amplitude Q",        0, 2),
    ("distance_mpc",     "Distance [Mpc]",         1, 0),
    ("Y_disk_fit",       "Υ_disk (IRS+Υ, k=2)",   1, 1),
    ("dbic_resp_vs_nfw", "ΔBIC (IRS k=1 − NFW k=2)", 1, 2),
]

sigma_col_plot = "sigma_fit_kpc"
for tcol, tlabel, row, col in plot_pairs:
    ax = fig.add_subplot(gs[row, col])
    if tcol not in df.columns:
        ax.text(0.5, 0.5, "no data", transform=ax.transAxes, ha="center")
        ax.set_title(tlabel, fontsize=10)
        continue
    paired = df[[sigma_col_plot, tcol]].dropna()
    if len(paired) < 5:
        ax.text(0.5, 0.5, f"n={len(paired)}", transform=ax.transAxes, ha="center")
        ax.set_title(tlabel, fontsize=10)
        continue
    x = paired[tcol].values
    y = paired[sigma_col_plot].values

    # Log-scale axes where appropriate
    use_log_x = tcol in ["r_t_kpc", "Q_best", "distance_mpc"]
    use_log_y = True

    xp = np.log10(np.maximum(x, 1e-9)) if use_log_x else x
    yp = np.log10(np.maximum(y, 1e-9))

    ax.scatter(xp, yp, s=8, alpha=0.5, color="#1976D2")

    # regression line
    slope, intercept, *_ = stats.linregress(xp, yp)
    xline = np.linspace(xp.min(), xp.max(), 100)
    ax.plot(xline, slope * xline + intercept, "r-", linewidth=1.5, alpha=0.8)

    r, p = stats.spearmanr(x, y)
    stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    ax.set_title(f"σ vs {tlabel}\nr = {r:+.3f}  {stars}", fontsize=9)
    ax.set_xlabel(("log₁₀ " if use_log_x else "") + tlabel, fontsize=8)
    ax.set_ylabel("log₁₀ σ [kpc]", fontsize=8)

plt.savefig(FIG, dpi=150, bbox_inches="tight")
print(f"\nFigure saved: {FIG}")

# ─── save JSON ────────────────────────────────────────────────────────────────
with open(OUT, "w") as fh:
    json.dump(results, fh, indent=2)
print(f"Results saved: {OUT}")

# ─── summary interpretation ───────────────────────────────────────────────────
print("\n── Physical interpretation ────────────────────────────────────────────")
for sigma_col, sigma_label in SIGMA_LABELS.items():
    r_rt = results[sigma_col].get("r_t_kpc", {}).get("spearman_r", None)
    r_np = results[sigma_col].get("n_pts",   {}).get("spearman_r", None)
    r_d  = results[sigma_col].get("distance_mpc", {}).get("spearman_r", None)
    print(f"\n  {sigma_label}:")
    if r_rt is not None:
        direction = "σ tracks R_t (coherence scale ~ transition radius)" if r_rt > 0 \
                    else "σ anti-correlated with R_t (anomalous)"
        print(f"    r(σ, R_t) = {r_rt:+.3f}  → {direction}")
    if r_np is not None:
        direction = "larger/richer galaxies prefer larger σ" if r_np > 0 \
                    else "smaller galaxies prefer larger σ (possible noise regime)"
        print(f"    r(σ, n_pts) = {r_np:+.3f}  → {direction}")
    if r_d is not None:
        concern = "  ⚠ potential resolution bias" if abs(r_d) > 0.3 else "  ✓ low resolution bias"
        print(f"    r(σ, dist) = {r_d:+.3f}{concern}")

print("\nDone.")
