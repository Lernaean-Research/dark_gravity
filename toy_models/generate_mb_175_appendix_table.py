from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(r"D:/#Documents/#Publication/Spacetime_Mechanics__git/toy_models/out_sparc_runs_full_with_composition")
INPUT = BASE / "summary_with_env.csv"
OUTDIR = BASE / "mb_scaling"


def fmt(v: float, digits: int = 3) -> str:
    if pd.isna(v) or not np.isfinite(v):
        return "--"
    return f"{float(v):.{digits}f}"


def esc(s: str) -> str:
    return str(s).replace("_", r"\_")


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT).replace([np.inf, -np.inf], np.nan)

    req = [
        "galaxy",
        "ups_disk",
        "ups_bul",
        "frac_disk_rt",
        "frac_bul_rt",
        "sparc_L36_1e9solLum",
        "sparc_MHI_1e9solMass",
        "q_best_kms2",
        "v_extra_asym_kms",
        "r_t_kpc",
        "r_near_rt_kpc",
        "r_near_half_rt_kpc",
        "sparc_Vflat_kms",
        "sparc_Q_flag",
    ]
    d = df[req].copy()

    frac_disk = d["frac_disk_rt"].fillna(0.0).to_numpy()
    frac_bul = d["frac_bul_rt"].fillna(0.0).to_numpy()
    stellar_weight = frac_disk + frac_bul
    bulge_share = np.where(stellar_weight > 0, frac_bul / stellar_weight, 0.0)
    d["ups_eff_rt"] = d["ups_disk"] * (1.0 - bulge_share) + d["ups_bul"] * bulge_share
    d["mbary_1e9solMass"] = d["ups_eff_rt"] * d["sparc_L36_1e9solLum"] + 1.33 * d["sparc_MHI_1e9solMass"]

    out_cols = [
        "galaxy",
        "mbary_1e9solMass",
        "q_best_kms2",
        "r_t_kpc",
        "r_near_rt_kpc",
        "r_near_half_rt_kpc",
        "v_extra_asym_kms",
        "sparc_Vflat_kms",
        "sparc_Q_flag",
    ]
    out = d[out_cols].copy()
    out.to_csv(OUTDIR / "mb_175_per_galaxy_table.csv", index=False)

    lines = []
    lines.append("{\\small")
    lines.append("\\setlength{\\LTleft}{0pt}")
    lines.append("\\setlength{\\LTright}{0pt}")
    lines.append("\\setlength{\\tabcolsep}{3pt}")
    lines.append("\\begin{longtable}{l r r r r r r r r}")
    lines.append("\\caption{Per-galaxy baryonic mass and response metrics for the full SPARC-175 joined table. Mass is computed as $M_b=\\Upsilon_{\\rm eff}L_{3.6}+1.33M_{\\rm HI}$. Units: $M_b$ in $10^9\\,M_\\odot$, $Q_{\\rm best}$ in km$^2$ s$^{-2}$, radii in kpc, and velocities in km s$^{-1}$.}\\label{tab:appendix-mb-175}\\\\")
    lines.append("\\hline")
    lines.append("Galaxy & $M_b$ & $Q_{\\rm best}$ & $r_t$ & $r_{\\rm near\\,rt}$ & $r_{\\rm near\\,half\\,rt}$ & $V_{\\rm extra,asym}$ & $V_{\\rm flat}$ & $Q_{\\rm flag}$ \\\\")
    lines.append("\\hline")
    lines.append("\\endfirsthead")
    lines.append("\\hline")
    lines.append("Galaxy & $M_b$ & $Q_{\\rm best}$ & $r_t$ & $r_{\\rm near\\,rt}$ & $r_{\\rm near\\,half\\,rt}$ & $V_{\\rm extra,asym}$ & $V_{\\rm flat}$ & $Q_{\\rm flag}$ \\\\")
    lines.append("\\hline")
    lines.append("\\endhead")

    for _, r in out.iterrows():
        lines.append(
            f"{esc(r['galaxy'])} & {fmt(r['mbary_1e9solMass'])} & {fmt(r['q_best_kms2'])} & {fmt(r['r_t_kpc'])} & "
            f"{fmt(r['r_near_rt_kpc'])} & {fmt(r['r_near_half_rt_kpc'])} & {fmt(r['v_extra_asym_kms'])} & "
            f"{fmt(r['sparc_Vflat_kms'])} & {fmt(r['sparc_Q_flag'], 0)} \\\\" 
        )

    lines.append("\\hline")
    lines.append("\\end{longtable}")
    lines.append("}")

    (OUTDIR / "appendix_175_galaxy_table.tex").write_text("\n".join(lines) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()