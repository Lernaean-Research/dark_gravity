"""Generate a comprehensive markdown guide for the dyed-spacetime atlas.

The atlas figures are phenomenology-first visualizations inferred from observed
rotation curves. This script documents:
- What each panel represents and why it is constructed that way.
- Global normalization and uncertainty band rationale.
- Per-galaxy quantitative summary in the same order as rendering.

It also computes a per-galaxy "significance" for the fitted extra term using a
nested-model Δχ² test with 1 added parameter (Q). This is an approximate
frequentist diagnostic; it is intended for ranking/triage rather than as a
sole scientific claim.

Usage:
  python toy_models/generate_dyed_spacetime_atlas_report.py \
    --galaxy-dir toy_models/out_sparc_runs_full_with_composition/galaxies \
    --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv \
    --png-dir toy_models/out_dyed_spacetime/png \
    --atlas-pages toy_models/out_dyed_spacetime/dyed_spacetime_pages.pdf \
    --atlas-contact toy_models/out_dyed_spacetime/dyed_spacetime_contact.pdf \
    --out-md toy_models/DYED_SPACETIME_ATLAS_REPORT.md

Requires: numpy.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class GalaxySummary:
    galaxy: str
    n: Optional[int]
    r_t_kpc: Optional[float]
    q_best_kms2: Optional[float]
    v_extra_asym_kms: Optional[float]
    chi2: Optional[float]
    chi2_red: Optional[float]
    vobs_outer_kms: Optional[float]
    outer_resid_mean_z: Optional[float]
    outer_resid_rms_z: Optional[float]
    outer_chi2: Optional[float]
    sparc_T: Optional[float]
    sparc_D_mpc: Optional[float]
    sparc_Rdisk_kpc: Optional[float]
    sparc_Vflat_kms: Optional[float]
    sparc_Q_flag: Optional[float]
    env_twompp_delta_external: Optional[float]


@dataclass
class GalaxyFitDiagnostics:
    n_used: int
    chi2_bar: Optional[float]
    chi2_model: Optional[float]
    delta_chi2: Optional[float]
    p_value_1dof: Optional[float]
    z_equiv: Optional[float]


def _safe_float(d: dict, key: str) -> Optional[float]:
    s = d.get(key, "")
    if s is None or s == "":
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    if not math.isfinite(v):
        return None
    return v


def _safe_int(d: dict, key: str) -> Optional[int]:
    v = _safe_float(d, key)
    if v is None:
        return None
    return int(v)


def _read_summary(path: str) -> Dict[str, GalaxySummary]:
    out: Dict[str, GalaxySummary] = {}
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            galaxy = row.get("galaxy", "")
            if not galaxy:
                continue
            out[galaxy] = GalaxySummary(
                galaxy=galaxy,
                n=_safe_int(row, "n"),
                r_t_kpc=_safe_float(row, "r_t_kpc"),
                q_best_kms2=_safe_float(row, "q_best_kms2"),
                v_extra_asym_kms=_safe_float(row, "v_extra_asym_kms"),
                chi2=_safe_float(row, "chi2"),
                chi2_red=_safe_float(row, "chi2_red"),
                vobs_outer_kms=_safe_float(row, "vobs_outer_kms"),
                outer_resid_mean_z=_safe_float(row, "outer_resid_mean_z"),
                outer_resid_rms_z=_safe_float(row, "outer_resid_rms_z"),
                outer_chi2=_safe_float(row, "outer_chi2"),
                sparc_T=_safe_float(row, "sparc_T"),
                sparc_D_mpc=_safe_float(row, "sparc_D_mpc"),
                sparc_Rdisk_kpc=_safe_float(row, "sparc_Rdisk_kpc"),
                sparc_Vflat_kms=_safe_float(row, "sparc_Vflat_kms"),
                sparc_Q_flag=_safe_float(row, "sparc_Q_flag"),
                env_twompp_delta_external=_safe_float(row, "env_twompp_delta_external"),
            )
    return out


def _list_galaxy_names_from_dir(galaxy_dir: str) -> List[str]:
    names: List[str] = []
    for fn in os.listdir(galaxy_dir):
        if fn.lower().endswith(".csv"):
            names.append(os.path.splitext(fn)[0])
    names.sort(key=str.lower)
    return names


def _read_curve_csv(path: str) -> List[dict]:
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _compute_chi2(v_obs: np.ndarray, v_pred: np.ndarray, sigma: np.ndarray) -> float:
    m = np.isfinite(v_obs) & np.isfinite(v_pred) & np.isfinite(sigma) & (sigma > 0)
    if not np.any(m):
        return float("nan")
    r = (v_obs[m] - v_pred[m]) / sigma[m]
    return float(np.sum(r * r))


def _nested_delta_chi2_p_1dof(delta_chi2: float) -> float:
    """Survival function for χ² with 1 dof: p = P(Χ² >= delta)."""
    if not math.isfinite(delta_chi2) or delta_chi2 <= 0:
        return 1.0
    return float(math.erfc(math.sqrt(delta_chi2 / 2.0)))


def compute_fit_diagnostics(curve_rows: List[dict]) -> GalaxyFitDiagnostics:
    def arr(key: str) -> np.ndarray:
        vals: List[float] = []
        for r in curve_rows:
            s = r.get(key, "")
            try:
                v = float(s)
            except Exception:
                v = float("nan")
            vals.append(v)
        return np.asarray(vals, dtype=float)

    vobs = arr("vobs_kms")
    e = arr("e_vobs_kms")
    vbar = arr("vbar_kms")
    vmodel = arr("vmodel_kms")

    # Use only rows with all needed values; keep diagnostic conservative.
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
            # Rough equivalence for 1 dof: Δχ² ~ Z^2.
            z = float(math.sqrt(delta_val)) if (math.isfinite(delta_val) and delta_val > 0) else 0.0

    return GalaxyFitDiagnostics(
        n_used=n_used,
        chi2_bar=chi2_bar,
        chi2_model=chi2_model,
        delta_chi2=delta,
        p_value_1dof=p,
        z_equiv=z,
    )


def _fmt(x: Optional[float], digits: int = 3) -> str:
    if x is None or not math.isfinite(x):
        return "—"
    return f"{x:.{digits}g}"


def _p_fmt(p: Optional[float]) -> str:
    if p is None or not math.isfinite(p):
        return "—"
    if p < 1e-6:
        return "<1e-6"
    if p < 1e-3:
        return f"{p:.2e}"
    return f"{p:.3g}"


def _classification(delta_chi2: Optional[float], p: Optional[float]) -> str:
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


def build_report(
    *,
    galaxy_dir: str,
    summary_path: str,
    png_dir: Optional[str],
    atlas_pages_pdf: Optional[str],
    atlas_contact_pdf: Optional[str],
    out_md: str,
) -> None:
    summary = _read_summary(summary_path)
    names = _list_galaxy_names_from_dir(galaxy_dir)

    # Aggregate stats
    counts = {"very-strong": 0, "strong": 0, "moderate": 0, "weak": 0, "no-improvement": 0, "unrated": 0}

    # Precompute global scale label from atlas generation choices
    with open(out_md, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Dyed-Fabric SPARC Atlas: Components, Rationale, and Per-Galaxy Notes\n\n")
        f.write("This document explains the dyed-fabric atlas outputs in `toy_models/out_dyed_spacetime/` and provides per-galaxy quantitative notes in the same alphabetical order as the rendered pages.\n\n")

        if atlas_pages_pdf:
            pages = atlas_pages_pdf.replace("\\", "/")
            f.write(f"- Multi-page atlas PDF: [{pages}]({pages})\n")
        if atlas_contact_pdf:
            contact = atlas_contact_pdf.replace("\\", "/")
            f.write(f"- Contact sheet PDF: [{contact}]({contact})\n")
        if png_dir:
            png_dir_link = png_dir.replace("\\", "/")
            f.write(f"- Per-galaxy PNG directory: [{png_dir_link}]({png_dir_link})\n")
        f.write("\n")

        f.write("## How to read this atlas (executive)\n\n")
        f.write(
            "**Paper-ready framing.** Each page is a phenomenology-first visualization: it encodes what the observed "
            "circular-orbit kinematics imply about an **effective** radial potential in the rotation-supported sector, "
            "without claiming a unique GR metric reconstruction. The dyed-fabric panel is therefore a visual encoding "
            "of an inferred potential depth profile (with global normalization for cross-galaxy comparability), not an "
            "embedding diagram and not a computed geodesic map.\n\n"
        )
        f.write(
            "**Reader-friendly translation.** Think of it as: *given the measured orbital speeds, what radial pull would "
            "a test particle have to feel to stay on those circular orbits?* We integrate that pull to get a potential-like "
            "depth curve, then render the depth as dye intensity.\n\n"
        )
        f.write("Use it in this order:\n\n")
        f.write(
            "- **Rotation curve**: check where `v_obs(R)` departs from `v_bar(R)` and whether the fitted `v_model(R)` tracks the data within uncertainties.\n"
        )
        f.write(
            "- **Potential**: interpret the curve and its band as the integrated consequence of the observed centripetal acceleration $g_{obs}=v_{obs}^2/R$ (band propagated from `e_vobs_kms` when present).\n"
        )
        f.write(
            "- **Dyed fabric**: read the dye intensity as a global-normalized rendering of the radial depth profile $f(R)\\propto-\\Phi_{obs}(R)$ (useful for quick cross-galaxy comparison).\n"
        )
        f.write(
            "- **Δχ² + Z**: treat the per-galaxy $\\Delta\\chi^2$ (and derived $Z\\approx\\sqrt{\\Delta\\chi^2}$) as a ranking/triage diagnostic for how much the 1-parameter extra term improves the weighted fit over baryons-only—not as a final discovery claim.\n\n"
        )

        f.write("## 1) What each diagram component means\n\n")
        f.write("Each per-galaxy figure has three panels:\n\n")
        f.write("- **Rotation curve panel**: observed `v_obs(R)` (with ±1σ band if `e_vobs_kms` exists), plus the baryonic prediction `v_bar(R)` and the fitted total `v_model(R)` if available.\n")
        f.write(
            "- **Potential panel**: an inferred effective potential profile "
            "\\(\\Phi_{obs}(R)\\) defined (up to a constant) by\n\n"
        )
        f.write(
            "  $$g_{obs}(R)=\\frac{v_{obs}^2(R)}{R},\\qquad "
            "\\frac{d\\Phi_{obs}}{dR}=g_{obs}(R),\\qquad "
            "\\Phi_{obs}(R_{min})=0.$$\n\n"
        )
        f.write(
            "  If errors are present, we add a conservative propagated band using "
            "\\(\\sigma_g\\approx 2|v|\\sigma_v/R\\) and integrate it.\n"
        )
        f.write(
            "- **Dyed-fabric panel**: a stylized 2D dye map of the **radial** depth profile "
            "\\(f(R)\\propto -\\Phi_{obs}(R)\\) rendered as a rotationally symmetric image.\n\n"
        )

        f.write("### Rationale and defensibility notes\n\n")
        f.write(
            "- The dyed-fabric panel is **not** a GR embedding diagram and it does not attempt "
            "to reconstruct a full metric \\(g_{\\mu\\nu}\\). It is intentionally phenomenology-first: "
            "a visual encoding of an inferred effective potential depth from the circular-orbit "
            "sector of the data.\n"
        )
        f.write("- Orbit rings are **illustrative** (circular orbits), not computed geodesics.\n")
        f.write("- In the atlas render, depth is **globally normalized** across galaxies (so intensity is comparable).\n\n")

        f.write("## 2) Per-galaxy significance diagnostic (Δχ² with 1 extra parameter)\n\n")
        f.write("For each galaxy we compute:\n\n")
        f.write("- `chi2_bar`: χ² of baryons-only curve (`v_bar`) vs observations (`v_obs`) using `e_vobs_kms`\n")
        f.write("- `chi2_model`: χ² of fitted model (`v_model`) vs observations\n")
        f.write("- `Δχ² = chi2_bar - chi2_model`\n\n")
        f.write("Interpreting the extra term as adding one fitted degree of freedom, an approximate p-value is\n\n")
        f.write("$$p \\approx \\mathrm{erfc}\\!\\left(\\sqrt{\\Delta\\chi^2/2}\\right),$$\n\n")
        f.write(
            "and an approximate equivalent Gaussian significance is \\(Z\\approx \\sqrt{\\Delta\\chi^2}\\). "
            "This is a ranking/triage tool and should not be treated as a final claim without "
            "checking modeling systematics.\n\n"
        )

        f.write("## 3) Galaxy-by-galaxy notes (alphabetical; matches render order)\n\n")

        for name in names:
            curve_path = os.path.join(galaxy_dir, f"{name}.csv")
            rows = _read_curve_csv(curve_path)
            diag = compute_fit_diagnostics(rows)

            summ = summary.get(name)
            delta = diag.delta_chi2
            p = diag.p_value_1dof
            cls = _classification(delta, p)
            counts[cls] = counts.get(cls, 0) + 1

            png_link = None
            if png_dir:
                png_path = os.path.join(png_dir, f"{name}.png")
                if os.path.exists(png_path):
                    png_link = png_path.replace("\\", "/")

            f.write(f"### {name}\n\n")
            if png_link is not None:
                f.write(f"- Figure: [{png_link}]({png_link})\n")
            curve_link = curve_path.replace("\\", "/")
            f.write(f"- Data: [{curve_link}]({curve_link})\n")

            if summ is not None:
                f.write(
                    "- Summary: "
                    + ", ".join(
                        [
                            f"n={summ.n}",
                            f"Q_flag={_fmt(summ.sparc_Q_flag, 2)}",
                            f"T={_fmt(summ.sparc_T, 2)}",
                            f"D={_fmt(summ.sparc_D_mpc, 3)} Mpc",
                            f"Vflat={_fmt(summ.sparc_Vflat_kms, 3)} km/s",
                            f"Rdisk={_fmt(summ.sparc_Rdisk_kpc, 3)} kpc",
                            f"Rt={_fmt(summ.r_t_kpc, 3)} kpc",
                            f"v_extra_asym={_fmt(summ.v_extra_asym_kms, 3)} km/s",
                            f"env_delta={_fmt(summ.env_twompp_delta_external, 3)}",
                        ]
                    )
                    + "\n"
                )

            f.write(
                "- Fit diagnostic: "
                + ", ".join(
                    [
                        f"n_used={diag.n_used}",
                        f"chi2_bar={_fmt(diag.chi2_bar, 4)}",
                        f"chi2_model={_fmt(diag.chi2_model, 4)}",
                        f"Δχ²={_fmt(diag.delta_chi2, 4)}",
                        f"p≈{_p_fmt(diag.p_value_1dof)}",
                        f"Z≈{_fmt(diag.z_equiv, 3)}",
                        f"class={cls}",
                    ]
                )
                + "\n\n"
            )

            # Implications: short, systematic, and honest.
            implications: List[str] = []
            if summ is not None:
                if summ.outer_resid_rms_z is not None and math.isfinite(summ.outer_resid_rms_z):
                    implications.append(f"Outer residual RMS (z): {summ.outer_resid_rms_z:.3g}")
                if summ.outer_resid_mean_z is not None and math.isfinite(summ.outer_resid_mean_z):
                    implications.append(f"Outer residual mean (z): {summ.outer_resid_mean_z:.3g}")

            if cls in {"very-strong", "strong"}:
                implications.append("Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.")
            elif cls == "moderate":
                implications.append("Extra-term improves fit at a suggestive level; worth checking for systematics (inclination, distance, inner radii handling).")
            elif cls == "weak":
                implications.append("Extra-term improvement is weak under this diagnostic; baryons-only may already be adequate within errors or the effect is not well captured by a 1/R tail.")
            elif cls == "no-improvement":
                implications.append("No improvement over baryons-only under this diagnostic (Δχ²≤0).")
            else:
                implications.append("Insufficient information to rate (missing errors or model columns).")

            for line in implications[:4]:
                f.write(f"- Implication: {line}\n")
            f.write("\n")

        # Add aggregate counts at end
        f.write("## 4) Aggregate counts (Δχ² diagnostic classes)\n\n")
        for k in ["very-strong", "strong", "moderate", "weak", "no-improvement", "unrated"]:
            f.write(f"- {k}: {counts.get(k, 0)}\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--galaxy-dir", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--png-dir", default="")
    ap.add_argument("--atlas-pages", default="")
    ap.add_argument("--atlas-contact", default="")
    ap.add_argument("--out-md", required=True)
    args = ap.parse_args(argv)

    build_report(
        galaxy_dir=args.galaxy_dir,
        summary_path=args.summary,
        png_dir=args.png_dir or None,
        atlas_pages_pdf=args.atlas_pages or None,
        atlas_contact_pdf=args.atlas_contact or None,
        out_md=args.out_md,
    )
    print(f"Wrote: {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
