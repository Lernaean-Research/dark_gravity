"""Generate a comprehensive analysis report for HFF κ-vs-Chandra proxy systematics.

Reads the per-cluster combined outputs produced by `run_hff_systematics.py`:
- toy_models/out_predictions/systematics/<cluster>/systematics_summary.csv

Writes a Markdown report with:
- preregistered operator definition
- rationale and robustness design
- cross-team spread at fixed ROI
- ROI sensitivity at fixed team
- notes on limitations and interpretation

Run:
  d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe \
    toy_models/generate_hff_systematics_analysis.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ClusterSpec:
    key: str
    title: str
    summary_csv: Path
    roi_center_deg: str
    chandra_proxy_fits: Path


ROOT = Path("toy_models")

CLUSTERS = [
    ClusterSpec(
        key="abell2744",
        title="Abell 2744",
        summary_csv=ROOT / "out_predictions" / "systematics" / "abell2744" / "systematics_summary.csv",
        roi_center_deg="3.5887474051936,-30.397192536687",
        chandra_proxy_fits=ROOT
        / "data"
        / "hff"
        / "abell2744"
        / "chandra_stack"
        / "abell2744_chandra_full_img2_proxy.fits",
    ),
    ClusterSpec(
        key="macs0416",
        title="MACS J0416.1-2403",
        summary_csv=ROOT / "out_predictions" / "systematics" / "macs0416" / "systematics_summary.csv",
        roi_center_deg="64.03491667,-24.07244444",
        chandra_proxy_fits=ROOT
        / "data"
        / "hff"
        / "macs0416"
        / "chandra_stack"
        / "macs0416_chandra_full_img2_proxy.fits",
    ),
]


def _fmt(x: float) -> str:
    return f"{x:0.2f}"


def _require_exists(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise SystemExit(f"Missing or empty file: {path.as_posix()}")


def _stats_tables(df: pd.DataFrame, roi_ref: float = 100.0) -> dict[str, pd.DataFrame]:
    df = df.copy()
    df["roi_radius_arcsec"] = df["roi_radius_arcsec"].astype(float)
    df["level_pct"] = df["level_pct"].astype(float)
    df["sep_arcsec"] = df["sep_arcsec"].astype(float)

    # Across teams at each (roi, level)
    g = (
        df.groupby(["roi_radius_arcsec", "level_pct"])
        .agg(
            n=("sep_arcsec", "size"),
            median=("sep_arcsec", "median"),
            q25=("sep_arcsec", lambda s: s.quantile(0.25)),
            q75=("sep_arcsec", lambda s: s.quantile(0.75)),
            min=("sep_arcsec", "min"),
            max=("sep_arcsec", "max"),
            mean=("sep_arcsec", "mean"),
            std=("sep_arcsec", "std"),
        )
        .reset_index()
    )
    g["iqr"] = g["q75"] - g["q25"]

    # Cross-team spread at reference ROI
    if (df["roi_radius_arcsec"] == float(roi_ref)).any():
        g100 = (
            df[df.roi_radius_arcsec == float(roi_ref)]
            .groupby("level_pct")["sep_arcsec"]
            .agg(n="size", median="median", q25=lambda s: s.quantile(0.25), q75=lambda s: s.quantile(0.75), min="min", max="max")
            .reset_index()
        )
        g100["iqr"] = g100["q75"] - g100["q25"]
        g100["range"] = g100["max"] - g100["min"]
    else:
        g100 = pd.DataFrame()

    # ROI sensitivity (120 - 80) per team for each level
    radii = sorted(df.roi_radius_arcsec.unique().tolist())
    if 80.0 in radii and 120.0 in radii:
        p80 = df[df.roi_radius_arcsec == 80.0].set_index(["team", "level_pct"])["sep_arcsec"]
        p120 = df[df.roi_radius_arcsec == 120.0].set_index(["team", "level_pct"])["sep_arcsec"]
        delta = (p120 - p80).dropna().reset_index().rename(columns={"sep_arcsec": "delta_120_minus_80"})
        dsum = (
            delta.groupby("level_pct")["delta_120_minus_80"]
            .agg(n="size", median="median", q25=lambda s: s.quantile(0.25), q75=lambda s: s.quantile(0.75), min="min", max="max")
            .reset_index()
        )
        dsum["iqr"] = dsum["q75"] - dsum["q25"]
    else:
        dsum = pd.DataFrame()

    # Team-level ROI curve summary (min/max across radii) per team & level
    team_curve = (
        df.groupby(["team", "level_pct"])
        .agg(
            n=("sep_arcsec", "size"),
            min_sep=("sep_arcsec", "min"),
            max_sep=("sep_arcsec", "max"),
            median_sep=("sep_arcsec", "median"),
        )
        .reset_index()
    )
    team_curve["range_over_radii"] = team_curve["max_sep"] - team_curve["min_sep"]

    return {"by_roi_level": g, "roi_ref": g100, "delta_120_80": dsum, "team_curve": team_curve}


def _to_md_table(df: pd.DataFrame, cols: list[str]) -> str:
    if df.empty:
        return "(no rows)\n"
    d = df[cols].copy()
    for c in d.columns:
        if pd.api.types.is_numeric_dtype(d[c]):
            d[c] = d[c].map(lambda x: _fmt(float(x)))
    return d.to_markdown(index=False) + "\n"


def main() -> int:
    out_path = ROOT / "HFF_ALL_TEAMS_SYSTEMATICS_ANALYSIS.md"

    parts: list[str] = []

    parts.append("# HFF all-teams systematics analysis (κ vs Chandra proxy)\n")
    parts.append(
        "This report analyzes the completed robustness grid for two Hubble Frontier Fields clusters, using a preregistered measurement operator to compare a lensing response proxy (κ) against an observational gas proxy (stacked Chandra HEASARC img2 rate map).\n"
    )

    parts.append("## What is measured (pre-registered operator)\n")
    parts.append(
        "For each cluster, each Frontier κ team model, and each ROI radius:\n\n"
        "- **Inputs**: (A) a Frontier κ FITS map; (B) a stacked Chandra `*_full_img2.fits.gz` proxy rate map (counts/s).\n"
        "- **Common processing**: Gaussian smoothing with σ = 8 arcsec applied independently to A and B.\n"
        "- **Within a circular ROI** (ICRS center fixed per cluster), evaluate thresholds at **99 / 97 / 95 percentiles** of the smoothed pixels.\n"
        "- **Primary blob rule**: choose the **largest connected component** above threshold (per map) and compute its **unweighted mask centroid**.\n"
        "- **Metric**: centroid-to-centroid separation in arcseconds.\n\n"
        "This is designed to be falsifiable and apples-to-apples across models: the operator is fixed and does not adapt to any individual team, threshold, or cluster beyond the ROI definition.\n"
    )

    parts.append("## Why this design (rationales)\n")
    parts.append(
        "**Why multi-team κ?** Frontier Fields provides multiple independent lens reconstructions. If a κ–gas offset claim depends strongly on the team/model choice, that sensitivity is itself a result and must be quantified.\n\n"
        "**Why ROI sweeps?** Frontier κ maps have limited footprints. ROI choice can (i) clip structures, (ii) include/exclude secondary peaks, and (iii) change percentiles. Sweeping ROI radii provides a direct stability check.\n\n"
        "**Why percentile thresholds?** Percentiles are scale-free and robust to unknown absolute calibrations between maps, while still selecting the high-intensity/high-κ structures relevant for centroid comparisons.\n\n"
        "**Why 8 arcsec smoothing?** This enforces a common effective resolution, reduces pixel-scale noise sensitivity, and stabilizes connected-component topology.\n"
    )

    parts.append("## Data products (what is ‘proxy’)\n")
    parts.append(
        "The Chandra map here is a **proxy stack** constructed directly from HEASARC `img2` images (not event-level CIAO processing).\n\n"
        "Stacking procedure (implemented in `toy_models/make_chandra_xray_map.py`):\n\n"
        "- Read each `*_full_img2.fits.gz` image.\n"
        "- Divide by scalar exposure (`EXPOSURE` keyword; fallback to `LIVETIME/ONTIME`).\n"
        "- Reproject onto a common WCS grid and compute an exposure-weighted mean rate map.\n\n"
        "This is appropriate for centroid/peak *geometry* comparisons, but it is not a science-grade X-ray reduction (no exposure maps/vignetting correction, background modeling, point-source masking, etc.).\n"
    )

    parts.append("## Results: cross-team systematics and ROI sensitivity\n")

    for spec in CLUSTERS:
        _require_exists(spec.summary_csv)
        _require_exists(spec.chandra_proxy_fits)

        df = pd.read_csv(spec.summary_csv)
        teams = sorted(df.team.unique().tolist())
        radii = sorted(df.roi_radius_arcsec.unique().tolist())
        levels = sorted(df.level_pct.unique().tolist())

        tables = _stats_tables(df)
        by_roi_level = tables["by_roi_level"]
        roi_ref = tables["roi_ref"]
        delta = tables["delta_120_80"]
        team_curve = tables["team_curve"]

        parts.append(f"### {spec.title}\n")
        parts.append(
            f"- Teams in grid: **{len(teams)}**\n"
            f"- ROI radii (arcsec): **{', '.join(str(int(r)) for r in radii)}**\n"
            f"- Levels (percentiles): **{', '.join(str(int(l)) for l in levels)}**\n"
            f"- ROI center (deg): **{spec.roi_center_deg}**\n"
            f"- Chandra proxy FITS: `{spec.chandra_proxy_fits.as_posix()}`\n"
            f"- Combined outputs: `{spec.summary_csv.as_posix()}`\n"
        )

        parts.append("\n#### Team spread at ROI = 100\"\n")
        parts.append(
            "Summary across κ teams at fixed ROI, per threshold level. The key robustness quantities are the IQR and full range across teams.\n\n"
        )
        parts.append(
            _to_md_table(
                roi_ref,
                ["level_pct", "n", "median", "q25", "q75", "iqr", "min", "max", "range"],
            )
        )

        parts.append("\n#### Team spread for every ROI radius\n")
        parts.append(
            "Median separation across teams for each (ROI radius, level), plus IQR and min/max across teams.\n\n"
        )
        parts.append(
            _to_md_table(
                by_roi_level.sort_values(["roi_radius_arcsec", "level_pct"]),
                ["roi_radius_arcsec", "level_pct", "n", "median", "iqr", "min", "max"],
            )
        )

        parts.append("\n#### ROI sensitivity (Δ = sep@120\" − sep@80\")\n")
        parts.append(
            "This quantifies how much the measured separation changes when the ROI is expanded from 80\" to 120\". Positive Δ means larger measured offsets at larger ROI.\n\n"
        )
        parts.append(_to_md_table(delta, ["level_pct", "n", "median", "q25", "q75", "iqr", "min", "max"]))

        parts.append("\n#### Which effect dominates? (team vs ROI)\n")
        parts.append(
            "A practical way to compare sensitivities is to look at typical ROI-induced change (IQR of Δ) versus typical cross-team spread at a fixed ROI (IQR at ROI=100).\n\n"
            "Interpretation guideline:\n\n"
            "- If cross-team IQR ≫ ROI Δ IQR, the dominant uncertainty is lens-model systematics.\n"
            "- If ROI Δ IQR ≫ cross-team IQR, the dominant uncertainty is ROI/footprint sensitivity (operator interacting with morphology).\n"
        )

        # Add a compact per-level comparison section
        if not roi_ref.empty and not delta.empty:
            m = roi_ref[["level_pct", "iqr", "range"]].merge(
                delta[["level_pct", "iqr", "min", "max"]],
                on="level_pct",
                how="inner",
                suffixes=("_teams_at100", "_delta120_80"),
            )
            m = m.rename(columns={"range": "range_teams_at100", "min": "delta_min", "max": "delta_max"})
            parts.append(
                _to_md_table(
                    m.sort_values("level_pct"),
                    ["level_pct", "iqr_teams_at100", "range_teams_at100", "iqr_delta120_80", "delta_min", "delta_max"],
                )
            )
        else:
            parts.append("(comparison table unavailable)\n")

        parts.append("\n#### Team-level stability across radii (range over radii)\n")
        parts.append(
            "For each team and threshold level, this shows the spread of separations across the ROI sweep. Large values indicate ROI sensitivity for that model at that level.\n\n"
        )
        # Keep table size manageable: show top 10 most ROI-sensitive entries per level
        tc = team_curve.sort_values(["level_pct", "range_over_radii"], ascending=[True, False]).copy()
        tc_top = tc.groupby("level_pct").head(10)
        parts.append(
            _to_md_table(
                tc_top,
                ["level_pct", "team", "median_sep", "min_sep", "max_sep", "range_over_radii"],
            )
        )

        parts.append("\n")

    parts.append("## Global interpretation and caveats\n")
    parts.append(
        "1) **‘Offset’ is not a single number**: it is a function of (i) threshold level and (ii) ROI definition, even before considering κ model systematics.\n"
        "2) **Lens-model systematics are real**: different Frontier κ reconstructions can yield materially different centroid separations under a fixed operator.\n"
        "3) **ROI sensitivity is also real**: expanding the ROI can introduce new connected components or shift percentile structure, changing the primary-blob centroid.\n"
        "4) **Proxy X-ray limitations**: the img2 stack is adequate for geometry/centroid work but can be biased by unresolved point sources, varying backgrounds, vignetting, and differences in bandpass/exposure.\n"
        "5) **Footprint constraint**: ROI must stay within κ coverage. Larger radii may be invalid for some κ products; the sweep used here stays conservative.\n"
    )

    parts.append("\n## Reproducibility\n")
    parts.append(
        "Primary outputs analyzed here:\n\n"
        "- `toy_models/out_predictions/systematics/abell2744/systematics_summary.csv`\n"
        "- `toy_models/out_predictions/systematics/macs0416/systematics_summary.csv`\n\n"
        "Chandra proxy stacks used:\n\n"
        "- `toy_models/data/hff/abell2744/chandra_stack/abell2744_chandra_full_img2_proxy.fits`\n"
        "- `toy_models/data/hff/macs0416/chandra_stack/macs0416_chandra_full_img2_proxy.fits`\n\n"
        "To regenerate systematics grids (example):\n\n"
        "```\n"
        "d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe toy_models/run_hff_systematics.py \\\n"
        "  --cluster abell2744 \\\n"
        "  --chandra-map toy_models/data/hff/abell2744/chandra_stack/abell2744_chandra_full_img2_proxy.fits \\\n"
        "  --roi-center 3.5887474051936,-30.397192536687 \\\n"
        "  --roi-radii 80 100 120 \\\n"
        "  --teams all --skip-existing\n"
        "```\n"
    )

    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote: {out_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
