"""Generate a joint SPARC (galaxies) + HFF (clusters) implications report.

This script is intentionally *results-driven*: it reads the existing CSV artifacts
produced by the toy-model pipeline and the HFF robustness grid, recomputes a small
set of headline summary statistics, and writes a single Markdown document that
connects the results to the "intrinsic spacetime response" effective-source / CDM-
candidate thesis.

It does *not* attempt to validate a full field theory; it reports what the current
measurement operators and fit summaries do and do not establish.

Usage:
  ./.venv/Scripts/python.exe toy_models/generate_joint_sparc_hff_implications_report.py \
    --out-md toy_models/SPARC_HFF_JOINT_IMPLICATIONS_REPORT.md

Inputs (default locations; override with flags if needed):
- SPARC per-galaxy curve CSVs: toy_models/out_sparc_runs_full_with_composition/galaxies/*.csv
- SPARC summary table:        toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv
- SPARC composition correlations: toy_models/out_sparc_runs_full_with_composition/composition_vs_edge_correlations.csv
- HFF systematics CSVs:
    toy_models/out_predictions/systematics/abell2744/systematics_summary.csv
    toy_models/out_predictions/systematics/macs0416/systematics_summary.csv

Outputs:
- Markdown report: toy_models/SPARC_HFF_JOINT_IMPLICATIONS_REPORT.md

Requires: numpy, pandas (tabulate optional for nicer markdown tables).
"""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FitDiag:
    galaxy: str
    n_used: int
    chi2_bar: float | None
    chi2_model: float | None
    delta_chi2: float | None
    p_value_1dof: float | None
    z_equiv: float | None
    cls: str


def _to_float(x) -> float:
    try:
        v = float(x)
    except Exception:
        return float("nan")
    return v


def _compute_chi2(v_obs: np.ndarray, v_pred: np.ndarray, sigma: np.ndarray) -> float:
    m = np.isfinite(v_obs) & np.isfinite(v_pred) & np.isfinite(sigma) & (sigma > 0)
    if not np.any(m):
        return float("nan")
    r = (v_obs[m] - v_pred[m]) / sigma[m]
    return float(np.sum(r * r))


def _nested_delta_chi2_p_1dof(delta_chi2: float) -> float:
    if not math.isfinite(delta_chi2) or delta_chi2 <= 0:
        return 1.0
    return float(math.erfc(math.sqrt(delta_chi2 / 2.0)))


def _classify(delta_chi2: float | None, p: float | None) -> str:
    if delta_chi2 is None or p is None or not math.isfinite(delta_chi2) or not math.isfinite(p):
        return "unrated"
    if delta_chi2 <= 0:
        return "no-improvement"
    if p < 1e-6:
        return "very-strong"
    if p < 1e-3:
        return "strong"
    if p < 0.05:
        return "moderate"
    return "weak"


def compute_fit_diagnostics_for_galaxy(curve_csv: Path) -> FitDiag:
    df = pd.read_csv(curve_csv)
    vobs = df.get("vobs_kms", pd.Series(dtype=float)).to_numpy(dtype=float)
    e = df.get("e_vobs_kms", pd.Series(dtype=float)).to_numpy(dtype=float)
    vbar = df.get("vbar_kms", pd.Series(dtype=float)).to_numpy(dtype=float)
    vmodel = df.get("vmodel_kms", pd.Series(dtype=float)).to_numpy(dtype=float)

    m = np.isfinite(vobs) & np.isfinite(e) & (e > 0)
    n_used = int(np.sum(m))

    chi2_bar = None
    chi2_model = None
    delta = None
    p = None
    z = None

    if n_used >= 3 and np.any(np.isfinite(vbar)) and np.any(np.isfinite(vmodel)):
        chi2_bar_val = _compute_chi2(vobs, vbar, e)
        chi2_model_val = _compute_chi2(vobs, vmodel, e)
        if math.isfinite(chi2_bar_val) and math.isfinite(chi2_model_val):
            chi2_bar = float(chi2_bar_val)
            chi2_model = float(chi2_model_val)
            delta_val = chi2_bar - chi2_model
            delta = float(delta_val)
            p = _nested_delta_chi2_p_1dof(delta_val)
            z = float(math.sqrt(delta_val)) if (math.isfinite(delta_val) and delta_val > 0) else 0.0

    cls = _classify(delta, p)
    return FitDiag(
        galaxy=curve_csv.stem,
        n_used=n_used,
        chi2_bar=chi2_bar,
        chi2_model=chi2_model,
        delta_chi2=delta,
        p_value_1dof=p,
        z_equiv=z,
        cls=cls,
    )


def _quantile_stats(x: pd.Series) -> dict[str, float]:
    x = pd.to_numeric(x, errors="coerce")
    x = x[np.isfinite(x.to_numpy(dtype=float))]
    if x.empty:
        return {"n": 0}
    q25 = float(x.quantile(0.25))
    q50 = float(x.quantile(0.50))
    q75 = float(x.quantile(0.75))
    return {
        "n": int(x.shape[0]),
        "median": q50,
        "q25": q25,
        "q75": q75,
        "iqr": q75 - q25,
        "min": float(x.min()),
        "max": float(x.max()),
        "range": float(x.max() - x.min()),
        "mean": float(x.mean()),
        "std": float(x.std(ddof=1)) if x.shape[0] >= 2 else float("nan"),
    }


def _md_table(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        # Fallback to a plain, minimal table.
        return df.to_csv(index=False)


def _rel_link(path: Path) -> str:
    p = path.as_posix()
    return f"[{p}]({p})"


def summarize_hff_systematics(systematics_csv: Path, *, roi_arcsec: float = 100.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(systematics_csv)
    df["roi_radius_arcsec"] = df["roi_radius_arcsec"].astype(float)
    df["level_pct"] = df["level_pct"].astype(float)
    df = df[df["roi_radius_arcsec"] == float(roi_arcsec)].copy()

    rows = []
    for lvl, sub in df.groupby("level_pct"):
        st = _quantile_stats(sub["sep_arcsec"])
        rows.append({"level_pct": float(lvl), **st})
    spread = pd.DataFrame(rows).sort_values("level_pct", ascending=False)

    by_roi = []
    for (roi, lvl), sub in pd.read_csv(systematics_csv).groupby(["roi_radius_arcsec", "level_pct"]):
        st = _quantile_stats(sub["sep_arcsec"])
        by_roi.append({"roi_radius_arcsec": float(roi), "level_pct": float(lvl), "n": st.get("n", 0), "median": st.get("median", float("nan")), "iqr": st.get("iqr", float("nan")), "min": st.get("min", float("nan")), "max": st.get("max", float("nan"))})
    by_roi_df = pd.DataFrame(by_roi).sort_values(["roi_radius_arcsec", "level_pct"], ascending=[True, False])

    return spread, by_roi_df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--galaxy-dir",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/galaxies"),
        help="Directory of per-galaxy curve CSVs.",
    )
    ap.add_argument(
        "--sparc-summary",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv"),
        help="SPARC summary table CSV.",
    )
    ap.add_argument(
        "--sparc-comp-corr",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/composition_vs_edge_correlations.csv"),
        help="SPARC composition-vs-edge correlation table CSV.",
    )
    ap.add_argument(
        "--hff-a2744",
        type=Path,
        default=Path("toy_models/out_predictions/systematics/abell2744/systematics_summary.csv"),
    )
    ap.add_argument(
        "--hff-m0416",
        type=Path,
        default=Path("toy_models/out_predictions/systematics/macs0416/systematics_summary.csv"),
    )
    ap.add_argument("--roi-arcsec", type=float, default=100.0)
    ap.add_argument(
        "--out-md",
        type=Path,
        default=Path("toy_models/SPARC_HFF_JOINT_IMPLICATIONS_REPORT.md"),
    )

    args = ap.parse_args()

    for p in [args.galaxy_dir, args.sparc_summary, args.sparc_comp_corr, args.hff_a2744, args.hff_m0416]:
        if not p.exists():
            raise SystemExit(f"Missing required input: {p.as_posix()}")

    # --- SPARC: compute per-galaxy nested Δχ² diagnostics from curves ---
    curve_paths = sorted([p for p in args.galaxy_dir.glob("*.csv")], key=lambda p: p.name.lower())
    fit_diags: list[FitDiag] = [compute_fit_diagnostics_for_galaxy(p) for p in curve_paths]
    fit_df = pd.DataFrame([d.__dict__ for d in fit_diags])

    cls_counts = fit_df["cls"].value_counts().to_dict()

    rated = fit_df[pd.notna(fit_df["delta_chi2"])].copy()
    rated["delta_chi2"] = pd.to_numeric(rated["delta_chi2"], errors="coerce")
    rated = rated[np.isfinite(rated["delta_chi2"].to_numpy(dtype=float))]

    delta_stats = _quantile_stats(rated["delta_chi2"]) if not rated.empty else {"n": 0}

    # SPARC summary table stats
    sparc = pd.read_csv(args.sparc_summary)
    for c in ["q_best_kms2", "v_extra_asym_kms", "outer_resid_rms_z", "outer_resid_mean_z", "outer_chi2"]:
        if c in sparc.columns:
            sparc[c] = pd.to_numeric(sparc[c], errors="coerce")

    q_stats = _quantile_stats(sparc.get("q_best_kms2", pd.Series(dtype=float)))
    v_stats = _quantile_stats(sparc.get("v_extra_asym_kms", pd.Series(dtype=float)))

    # Composition-vs-edge correlations (already computed in-pipeline)
    comp_corr = pd.read_csv(args.sparc_comp_corr)
    comp_corr = comp_corr.sort_values("spearman_rho", ascending=False)
    top_corr = comp_corr.head(10).copy()

    # --- HFF: summarize systematics at ROI=100" and across radii ---
    a2744_spread, a2744_by_roi = summarize_hff_systematics(args.hff_a2744, roi_arcsec=float(args.roi_arcsec))
    m0416_spread, m0416_by_roi = summarize_hff_systematics(args.hff_m0416, roi_arcsec=float(args.roi_arcsec))

    # Figure directories (if present)
    fig_a2744 = Path("toy_models/out_predictions/figures/systematics_sixpanel/abell2744")
    fig_m0416 = Path("toy_models/out_predictions/figures/systematics_sixpanel/macs0416")

    def list_pngs(d: Path) -> list[str]:
        if not d.exists():
            return []
        return [p.name for p in sorted(d.glob("*.png"), key=lambda p: p.name.lower())]

    a2744_pngs = list_pngs(fig_a2744)
    m0416_pngs = list_pngs(fig_m0416)

    # --- Write report ---
    out_md = args.out_md
    out_md.parent.mkdir(parents=True, exist_ok=True)

    with open(out_md, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Joint SPARC + Cluster (HFF) results and implications\n\n")
        f.write("This report stitches together two layers of evidence already generated in this repository:\n\n")
        f.write("- **Galaxy scale (SPARC)**: one-parameter extra-term toy fits to rotation curves, plus derived atlas diagnostics.\n")
        f.write("- **Cluster scale (HFF)**: a preregistered morphology operator comparing Frontier Fields κ to a Chandra img2 proxy stack.\n\n")
        f.write("It is intended as a *project-level* synthesis for the **intrinsic spacetime response** effective-source / CDM-candidate thesis: what the current measurements support, what they do not, and what would falsify key claims.\n\n")

        f.write("## Executive results (recomputed from CSV artifacts)\n\n")

        f.write("### SPARC: nested Δχ² diagnostic for the extra term (1 additional parameter)\n\n")
        f.write(
            'We recompute a per-galaxy nested-model diagnostic using the per-radius curves: "baryons-only" (v_bar) vs "baryons+extra" (v_model), with Δχ² = χ²_bar − χ²_model and 1 dof survival p ≈ erfc(√(Δχ²/2)).\n\n'
        )
        f.write(f"- Curve files read: **{len(curve_paths)}**\n")
        f.write(f"- Rated galaxies (finite Δχ²): **{int(delta_stats.get('n', 0))}**\n")
        if delta_stats.get("n", 0) > 0:
            f.write(
                "- Δχ² summary: "
                f"median={delta_stats['median']:.3g}, IQR={delta_stats['iqr']:.3g}, min={delta_stats['min']:.3g}, max={delta_stats['max']:.3g}\n"
            )
        f.write("- Classification counts (by p-value):\n")
        for k in ["very-strong", "strong", "moderate", "weak", "no-improvement", "unrated"]:
            f.write(f"  - {k}: {int(cls_counts.get(k, 0))}\n")
        f.write("\n")

        f.write("### SPARC: fitted edge-amplitude proxy and Q summary\n\n")
        if v_stats.get("n", 0) > 0:
            f.write(
                "- v_extra_asym_kms (edge-amplitude proxy): "
                f"N={v_stats['n']}, median={v_stats['median']:.3g} km/s, IQR={v_stats['iqr']:.3g}, range=[{v_stats['min']:.3g},{v_stats['max']:.3g}]\n"
            )
        if q_stats.get("n", 0) > 0:
            f.write(
                "- q_best_kms2 (fit parameter): "
                f"N={q_stats['n']}, median={q_stats['median']:.3g} (km/s)^2, IQR={q_stats['iqr']:.3g}\n"
            )
        f.write("\n")

        f.write("### SPARC: strongest composition/structure correlations with edge amplitude (from pipeline table)\n\n")
        f.write(_md_table(top_corr[["x", "y", "n", "pearson_r", "spearman_rho"]]))
        f.write("\n\n")

        f.write("### HFF: κ–X-ray centroid separations at ROI = ")
        f.write(f"{float(args.roi_arcsec):.0f}\" (across teams)\n\n")
        f.write("Abell 2744 (11 teams):\n\n")
        f.write(_md_table(a2744_spread[["level_pct", "n", "median", "q25", "q75", "iqr", "min", "max", "range"]]))
        f.write("\n\n")
        f.write("MACS J0416.1−2403 (12 teams):\n\n")
        f.write(_md_table(m0416_spread[["level_pct", "n", "median", "q25", "q75", "iqr", "min", "max", "range"]]))
        f.write("\n\n")

        f.write("### HFF: ROI-radius sensitivity (medians across teams; all radii in the grid)\n\n")
        f.write("Abell 2744:\n\n")
        f.write(_md_table(a2744_by_roi[["roi_radius_arcsec", "level_pct", "n", "median", "iqr", "min", "max"]]))
        f.write("\n\n")
        f.write("MACS J0416.1−2403:\n\n")
        f.write(_md_table(m0416_by_roi[["roi_radius_arcsec", "level_pct", "n", "median", "iqr", "min", "max"]]))
        f.write("\n\n")

        f.write("## Interpretation: what these results do and do not establish\n\n")
        f.write(
            "### What SPARC contributes to the intrinsic-response/CDM-candidate thesis\n\n"
            "At galaxy scale, the toy pipeline establishes a consistent *phenomenological* fact pattern: across a large fraction of SPARC objects, a **single extra amplitude parameter** (encoded as q_best or v_extra_asym) improves the weighted fit over baryons-only under a simple nested Δχ² diagnostic.\n\n"
            "Project meaning: this supports the claim that an **effective additional source/response term** is empirically demanded by the rotation-curve sector, in a way that is (i) not limited to a small subset of galaxies and (ii) strongly structured by galaxy properties (see correlation table).\n\n"
        )
        f.write(
            "What it does *not* establish by itself: whether the extra term is a particle dark matter halo, a modified gravity law, or an intrinsic medium/metric response. SPARC here is evidence for a *required extra phenomenological component*, not a unique mechanism.\n\n"
        )

        f.write(
            "### What HFF contributes\n\n"
            "At cluster scale, the preregistered κ–X-ray morphology operator measures **centroid separations** between a lensing response proxy (κ) and a gas proxy (Chandra img2 stack), while explicitly quantifying κ-model systematics (multi-team) and ROI sensitivity.\n\n"
            "Project meaning: the cluster results provide a cross-domain constraint on any CDM-candidate story: a viable candidate must accommodate (a) mergers where mass-tracing (κ) and gas-tracing (X-ray) morphologies can be displaced, and (b) the observed level of robustness/sensitivity under model systematics and threshold choice.\n\n"
        )

        f.write(
            "### Cross-scale synthesis (how they fit together)\n\n"
            "A coherent intrinsic-response-as-CDM-candidate narrative needs both:\n"
            "- a galaxy-scale **equilibrium mapping** (SPARC) where the extra response term tracks internal structure in a simple, compressible way; and\n"
            "- a cluster-scale **non-equilibrium morphology behavior** (HFF/Bullet) where response vs gas can be displaced, with uncertainties explicitly propagated via κ team spread.\n\n"
            "The current artifacts support the *methodological* program (fixed operator, robustness ladders, explicit systematics), and they supply *nontrivial constraints* on environment-responsiveness claims (see environment proxy report).\n\n"
        )

        f.write("## Robust implications for the intrinsic spacetime response CDM-candidate thesis\n\n")
        f.write(
            "### Supports (in the limited, operational sense)\n"
            "- **Compressibility at galaxy scale**: A one-parameter extra amplitude is frequently sufficient to materially improve rotation-curve fits; this is compatible with an intrinsic-response sector that is not arbitrarily high-dimensional per galaxy.\n"
            "- **Structured dependence on internal properties**: Strong correlations of v_extra/q with luminosity, morphology, and composition fractions support the view that the extra term is tied to baryonic structure rather than being pure noise.\n"
            "- **Non-equilibrium cluster morphology is testable with the same operator**: The HFF results quantify κ–gas offsets in a way that is directly comparable across systems and lens-model teams.\n\n"
        )

        f.write(
            "### Challenges / failure modes\n"
            "- **Mechanism underdetermination**: The same SPARC phenomenology can be fit by multiple classes of models; without additional predictions (e.g., lensing/shear nulls, external-field dependence, cross-sample out-of-domain forecasts), it does not uniquely favor an intrinsic-medium explanation.\n"
            "- **Environment-responsiveness is not yet robust**: the dedicated analysis in "
            f"{_rel_link(Path('toy_models/ENVIRONMENT_PROXY_RESIDUALS_REPORT.md'))} finds a modest negative association that does not survive distance-aware stratified nulls; strong OSA/screening claims are therefore constrained by the current proxy/data.\n"
            "- **Operator sensitivity exists**: cluster separations can be threshold/ROI dependent and κ-team dependent; any thesis claim should be phrased in terms of distributions (with systematics), not single-number offsets.\n\n"
        )

        f.write(
            "### What would strengthen or falsify\n"
            "- Strengthen: show that a *single calibrated response law* (fit on SPARC) predicts cluster observables beyond centroid offsets (e.g., shear patterns, between-ness with a collisionless proxy) with correct null diagnostics.\n"
            "- Falsify: show systematic failure of the response law in out-of-sample galaxies, or inability to accommodate observed cluster morphology under controlled operator choices without ad hoc retuning.\n\n"
        )

        f.write("## Pointers to the primary artifacts in this repo\n\n")
        f.write("- SPARC atlas report: " + _rel_link(Path("toy_models/DYED_SPACETIME_ATLAS_REPORT.md")) + "\n")
        f.write("- SPARC environment proxy report: " + _rel_link(Path("toy_models/ENVIRONMENT_PROXY_RESIDUALS_REPORT.md")) + "\n")
        f.write("- SPARC→clusters operator definition: " + _rel_link(Path("toy_models/PREDICTIONS_SPARC_TO_CLUSTERS.md")) + "\n")
        f.write("- HFF all-teams systematics analysis: " + _rel_link(Path("toy_models/HFF_ALL_TEAMS_SYSTEMATICS_ANALYSIS.md")) + "\n")
        f.write("\n")

        f.write("### Six-panel HFF figures (ROI=100\")\n\n")
        if a2744_pngs:
            f.write(f"- Abell 2744 figures ({len(a2744_pngs)} PNGs): {fig_a2744.as_posix()}\n")
            for name in a2744_pngs:
                rel = (fig_a2744 / name).as_posix()
                f.write(f"  - [{name}]({rel})\n")
        else:
            f.write(f"- Abell 2744 figures: (not found at {fig_a2744.as_posix()})\n")

        if m0416_pngs:
            f.write(f"- MACS J0416.1−2403 figures ({len(m0416_pngs)} PNGs): {fig_m0416.as_posix()}\n")
            for name in m0416_pngs:
                rel = (fig_m0416 / name).as_posix()
                f.write(f"  - [{name}]({rel})\n")
        else:
            f.write(f"- MACS J0416.1−2403 figures: (not found at {fig_m0416.as_posix()})\n")

    print(f"Wrote: {out_md.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
