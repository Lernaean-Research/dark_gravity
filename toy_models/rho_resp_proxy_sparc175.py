"""Infer a response-density proxy from SPARC rotation-curve residuals.

This is a deliberately *phenomenology-first* ("inverse") construction.

Given per-galaxy profiles r_kpc, vobs_kms, vbar_kms, define

  Δv^2(r) = vobs(r)^2 - vbar(r)^2.

Under a spherical intuition (useful as a diagnostic even for disks), an
"effective extra" enclosed mass satisfies

  M_extra(<r) ∝ r * Δv^2(r),

so an effective extra density scales like

  ρ_extra(r) ∝ (4π r^2)^(-1) d/dr [ r * Δv^2(r) ].

We compute a *proxy* for ρ_extra (up to an overall constant) and fit the
outer-region log-slope. For a flat outer rotation curve (Δv^2≈const), the
proxy tends to ρ ∝ r^{-2}.

Outputs:
- out_rho_resp_proxy/rho_resp_proxy_catalogue.csv : per-galaxy summaries
- out_rho_resp_proxy/rho_resp_proxy_report.md     : aggregate report
- optional plots under out_rho_resp_proxy/png/

Dependency-light: NumPy (+ optional matplotlib for plots).
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

import numpy as np


@dataclass(frozen=True)
class OuterSelection:
    rule: Literal["rfrac", "lastfrac"]
    n_total: int
    n_outer: int
    rmax_kpc: float
    rmin_outer_kpc: float


def _as_float_array(values: Iterable[object]) -> np.ndarray:
    return np.asarray(list(values), dtype=float)


def select_outer_region(
    r_kpc: np.ndarray,
    *,
    outer_last_frac: float = 0.40,
    outer_rfrac: float = 0.60,
    min_points: int = 5,
) -> tuple[np.ndarray, OuterSelection]:
    r_kpc = np.asarray(r_kpc, dtype=float)
    r_kpc = r_kpc[np.isfinite(r_kpc)]

    n = int(r_kpc.size)
    if n == 0:
        return (np.zeros(0, dtype=bool), OuterSelection("lastfrac", 0, 0, math.nan, math.nan))

    rmax = float(np.max(r_kpc))
    mask_r = r_kpc >= (outer_rfrac * rmax)
    if int(np.sum(mask_r)) >= min_points:
        rmin_outer = float(np.min(r_kpc[mask_r]))
        return (mask_r, OuterSelection("rfrac", n, int(np.sum(mask_r)), rmax, rmin_outer))

    k = max(min_points, int(math.ceil(outer_last_frac * n)))
    mask_last = np.zeros(n, dtype=bool)
    mask_last[-k:] = True
    rmin_outer = float(np.min(r_kpc[mask_last]))
    return (mask_last, OuterSelection("lastfrac", n, int(np.sum(mask_last)), rmax, rmin_outer))


def _read_galaxy_csv(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r = []
    vobs = []
    vbar = []

    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r.append(row.get("r_kpc"))
            vobs.append(row.get("vobs_kms"))
            vbar.append(row.get("vbar_kms"))

    r_kpc = _as_float_array(r)
    vobs_kms = _as_float_array(vobs)
    vbar_kms = _as_float_array(vbar)

    m = np.isfinite(r_kpc) & np.isfinite(vobs_kms) & np.isfinite(vbar_kms)
    r_kpc, vobs_kms, vbar_kms = r_kpc[m], vobs_kms[m], vbar_kms[m]

    order = np.argsort(r_kpc)
    return r_kpc[order], vobs_kms[order], vbar_kms[order]


def _safe_log10(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full_like(x, fill_value=np.nan)
    m = np.isfinite(x) & (x > 0)
    out[m] = np.log10(x[m])
    return out


def fit_log_slope(x: np.ndarray, y: np.ndarray) -> tuple[float, int]:
    """Fit y ~ a + b x (ordinary least squares). Returns (b, n_used)."""

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]

    n = int(x.size)
    if n < 3:
        return (math.nan, n)

    # Center for numerical stability
    x0 = float(np.mean(x))
    y0 = float(np.mean(y))
    xx = x - x0
    yy = y - y0

    denom = float(np.sum(xx * xx))
    if denom == 0.0:
        return (math.nan, n)

    b = float(np.sum(xx * yy) / denom)
    return (b, n)


def compute_rho_proxy(
    *,
    r_kpc: np.ndarray,
    vobs_kms: np.ndarray,
    vbar_kms: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (delta_v2, rho_proxy, dy_dr) arrays, aligned with r_kpc."""

    r_kpc = np.asarray(r_kpc, dtype=float)
    vobs_kms = np.asarray(vobs_kms, dtype=float)
    vbar_kms = np.asarray(vbar_kms, dtype=float)

    delta_v2 = vobs_kms**2 - vbar_kms**2  # (km/s)^2

    y = r_kpc * delta_v2  # kpc*(km/s)^2
    # gradient with nonuniform spacing
    dy_dr = np.gradient(y, r_kpc, edge_order=1)

    rho_proxy = np.full_like(r_kpc, fill_value=np.nan)
    m = np.isfinite(r_kpc) & (r_kpc > 0) & np.isfinite(dy_dr)
    rho_proxy[m] = dy_dr[m] / (4.0 * math.pi * (r_kpc[m] ** 2))

    return (delta_v2, rho_proxy, dy_dr)


def render_example_plot(
    *,
    out_png: Path,
    galaxy: str,
    r_kpc: np.ndarray,
    delta_v2: np.ndarray,
    rho_proxy: np.ndarray,
    mask_outer: np.ndarray,
) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    r = np.asarray(r_kpc, dtype=float)
    rho = np.asarray(rho_proxy, dtype=float)
    dv2 = np.asarray(delta_v2, dtype=float)

    m = np.isfinite(r) & np.isfinite(rho) & (r > 0)
    r, rho, dv2 = r[m], rho[m], dv2[m]

    if r.size < 4:
        return

    # Reference r^-2 line scaled to last |rho|
    rho_abs = np.abs(rho)
    last = float(rho_abs[-1]) if np.isfinite(rho_abs[-1]) else math.nan
    ref = np.full_like(r, fill_value=np.nan)
    if np.isfinite(last) and last > 0:
        ref = last * (r / float(r[-1])) ** (-2.0)

    fig = plt.figure(figsize=(7.5, 4.2), dpi=160)

    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(r, dv2, color="black", lw=1.4, label=r"$\Delta v^2$")
    if int(np.sum(mask_outer)) > 0:
        ax1.axvspan(float(np.min(r_kpc[mask_outer])), float(np.max(r_kpc[mask_outer])), color="#cccccc", alpha=0.35)
    ax1.set_title(f"{galaxy}: $\\Delta v^2(r)$")
    ax1.set_xlabel("r [kpc]")
    ax1.set_ylabel(r"$\Delta v^2$ [(km/s)$^2$]")

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.loglog(r, np.abs(rho), color="#7a0000", lw=1.4, label=r"$|\rho_{proxy}|$")
    if np.any(np.isfinite(ref)):
        ax2.loglog(r, ref, color="#555555", ls="--", lw=1.2, label=r"$\propto r^{-2}$")
    ax2.set_title(r"$\rho_{proxy}(r) \propto (4\pi r^2)^{-1} d(r\Delta v^2)/dr$")
    ax2.set_xlabel("r [kpc]")
    ax2.set_ylabel("proxy units")
    ax2.legend(loc="best", fontsize=8)

    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)

    p.add_argument(
        "--galaxy-csv-dir",
        type=Path,
        default=Path("toy_models/out_sparc_runs_full_with_composition/galaxies"),
        help="Directory containing per-galaxy CSVs (expects r_kpc, vobs_kms, vbar_kms).",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("toy_models/out_rho_resp_proxy"),
        help="Output directory for catalogue/report/plots.",
    )

    p.add_argument("--outer-last-frac", type=float, default=0.40)
    p.add_argument("--outer-rfrac", type=float, default=0.60)
    p.add_argument("--min-points", type=int, default=5)

    p.add_argument(
        "--make-plots",
        action="store_true",
        help="Render example PNGs (all galaxies unless limited by --plot-max).",
    )
    p.add_argument(
        "--plot-max",
        type=int,
        default=24,
        help="Max number of plots to render (use 0 for none; -1 for all).",
    )

    args = p.parse_args()

    in_dir = args.galaxy_csv_dir
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(in_dir.glob("*.csv"))
    if not files:
        raise SystemExit(f"No galaxy CSVs found in {in_dir}")

    rows: list[dict[str, object]] = []

    plot_budget = int(args.plot_max)
    make_plots = bool(args.make_plots) and plot_budget != 0

    for path in files:
        galaxy = path.stem
        r_kpc, vobs_kms, vbar_kms = _read_galaxy_csv(path)

        if r_kpc.size < 5:
            rows.append(
                {
                    "galaxy": galaxy,
                    "n": int(r_kpc.size),
                    "n_outer": 0,
                    "outer_rule": "",
                    "rmax_kpc": float(np.max(r_kpc)) if r_kpc.size else math.nan,
                    "rmin_outer_kpc": math.nan,
                    "slope_outer_pos": math.nan,
                    "n_slope_pos": 0,
                    "slope_outer_abs": math.nan,
                    "n_slope_abs": 0,
                    "dv2_outer_log_slope": math.nan,
                    "n_dv2_log_slope": 0,
                    "frac_rho_pos_outer": math.nan,
                }
            )
            continue

        delta_v2, rho_proxy, _dy_dr = compute_rho_proxy(r_kpc=r_kpc, vobs_kms=vobs_kms, vbar_kms=vbar_kms)

        mask_outer, sel = select_outer_region(
            r_kpc,
            outer_last_frac=args.outer_last_frac,
            outer_rfrac=args.outer_rfrac,
            min_points=args.min_points,
        )

        # Outer log–log slope of Δv^2 (should be ~0 if Δv^2 is approximately flat)
        dv2_outer = delta_v2[mask_outer]
        r_outer_for_dv2 = r_kpc[mask_outer]
        m_dv2 = np.isfinite(r_outer_for_dv2) & (r_outer_for_dv2 > 0) & np.isfinite(dv2_outer) & (dv2_outer > 0)
        dv2_slope, n_dv2 = fit_log_slope(
            _safe_log10(r_outer_for_dv2[m_dv2]),
            _safe_log10(dv2_outer[m_dv2]),
        )

        # Outer slope of rho_proxy (expected ~ -2 if Δv^2 ~ const)
        rho_outer = rho_proxy[mask_outer]
        r_outer = r_kpc[mask_outer]

        m_pos = np.isfinite(r_outer) & (r_outer > 0) & np.isfinite(rho_outer) & (rho_outer > 0)
        slope_pos, n_pos = fit_log_slope(_safe_log10(r_outer[m_pos]), _safe_log10(rho_outer[m_pos]))

        m_abs = np.isfinite(r_outer) & (r_outer > 0) & np.isfinite(rho_outer) & (np.abs(rho_outer) > 0)
        slope_abs, n_abs = fit_log_slope(_safe_log10(r_outer[m_abs]), _safe_log10(np.abs(rho_outer[m_abs])))

        frac_pos_outer = float(np.mean((rho_outer[np.isfinite(rho_outer)] > 0))) if np.any(np.isfinite(rho_outer)) else math.nan

        rows.append(
            {
                "galaxy": galaxy,
                "n": int(r_kpc.size),
                "n_outer": int(sel.n_outer),
                "outer_rule": sel.rule,
                "rmax_kpc": float(sel.rmax_kpc),
                "rmin_outer_kpc": float(sel.rmin_outer_kpc),
                "slope_outer_pos": float(slope_pos),
                "n_slope_pos": int(n_pos),
                "slope_outer_abs": float(slope_abs),
                "n_slope_abs": int(n_abs),
                "dv2_outer_log_slope": float(dv2_slope),
                "n_dv2_log_slope": int(n_dv2),
                "frac_rho_pos_outer": float(frac_pos_outer),
            }
        )

        if make_plots and (plot_budget < 0 or plot_budget > 0):
            out_png = out_dir / "png" / f"{galaxy}.png"
            render_example_plot(
                out_png=out_png,
                galaxy=galaxy,
                r_kpc=r_kpc,
                delta_v2=delta_v2,
                rho_proxy=rho_proxy,
                mask_outer=mask_outer,
            )
            if plot_budget > 0:
                plot_budget -= 1
                if plot_budget == 0:
                    make_plots = False

    # Write catalogue CSV
    out_csv = out_dir / "rho_resp_proxy_catalogue.csv"
    with out_csv.open("w", newline="") as f:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Aggregate report
    slopes_pos = np.array([r["slope_outer_pos"] for r in rows], dtype=float)
    slopes_abs = np.array([r["slope_outer_abs"] for r in rows], dtype=float)

    def _stats(arr: np.ndarray) -> dict[str, float]:
        a = arr[np.isfinite(arr)]
        if a.size == 0:
            return {"n": 0.0, "mean": math.nan, "p10": math.nan, "p50": math.nan, "p90": math.nan}
        return {
            "n": float(a.size),
            "mean": float(np.mean(a)),
            "p10": float(np.percentile(a, 10)),
            "p50": float(np.percentile(a, 50)),
            "p90": float(np.percentile(a, 90)),
        }

    st_pos = _stats(slopes_pos)
    st_abs = _stats(slopes_abs)

    # Count near -2
    near2_pos = int(np.sum(np.isfinite(slopes_pos) & (np.abs(slopes_pos + 2.0) <= 0.5)))
    near2_abs = int(np.sum(np.isfinite(slopes_abs) & (np.abs(slopes_abs + 2.0) <= 0.5)))

    report = out_dir / "rho_resp_proxy_report.md"
    with report.open("w", encoding="utf-8") as f:
        f.write("# Response-density proxy from SPARC residuals\n\n")
        f.write("This report summarizes the spherical-inversion proxy\n\n")
        f.write(
            r"$$\rho_{proxy}(r)\;\propto\;\frac{1}{4\pi r^2}\,\frac{d}{dr}\big(r\,\Delta v^2(r)\big),\quad \Delta v^2\equiv v_{obs}^2-v_{bar}^2.$$"
        )
        f.write("\n\n")
        f.write("For an approximately flat outer residual (Δv² ≈ const), one expects ρ ∝ r^{-2} in the outer region.\n\n")

        f.write("## Outer log-slope summary\n")
        f.write("The outer region is selected with the same rule as Q_est: r ≥ outer_rfrac·r_max (fallback: last outer_last_frac points).\n\n")

        f.write("**Positive-only slope** (fit log10(ρ_proxy) vs log10(r) using only points with ρ_proxy>0 in the outer region):\n\n")
        f.write(f"- n_galaxies_used: {int(st_pos['n'])}\n")
        f.write(f"- mean_slope: {st_pos['mean']:.3f}\n")
        f.write(f"- p10/p50/p90: {st_pos['p10']:.3f}, {st_pos['p50']:.3f}, {st_pos['p90']:.3f}\n")
        f.write(f"- within 0.5 of -2: {near2_pos}\n\n")

        f.write("**Absolute-value slope** (fit log10(|ρ_proxy|) vs log10(r) in the outer region):\n\n")
        f.write(f"- n_galaxies_used: {int(st_abs['n'])}\n")
        f.write(f"- mean_slope: {st_abs['mean']:.3f}\n")
        f.write(f"- p10/p50/p90: {st_abs['p10']:.3f}, {st_abs['p50']:.3f}, {st_abs['p90']:.3f}\n")
        f.write(f"- within 0.5 of -2: {near2_abs}\n\n")

        f.write("## Notes / caveats\n")
        f.write("- This is a spherical diagnostic applied to disk galaxies; treat it as a *shape sanity check*, not a literal density reconstruction.\n")
        f.write("- If Δv² is not flat in the outer region, the expected slope can deviate from -2.\n")
        f.write("- Negative ρ_proxy can occur where the residual decreases with radius; the absolute-value slope is included as a robustness diagnostic.\n")

    # Optional histogram plot
    try:
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(7.2, 3.6), dpi=160)
        ax = fig.add_subplot(1, 1, 1)
        a = slopes_pos[np.isfinite(slopes_pos)]
        b = slopes_abs[np.isfinite(slopes_abs)]
        if a.size:
            ax.hist(a, bins=24, alpha=0.55, label="outer slope (pos-only)")
        if b.size:
            ax.hist(b, bins=24, alpha=0.35, label="outer slope (abs)")
        ax.axvline(-2.0, color="black", ls="--", lw=1.0)
        ax.set_xlabel("outer log-slope")
        ax.set_ylabel("galaxy count")
        ax.set_title("ρ_proxy outer-slope distribution")
        ax.legend(loc="best", fontsize=8)
        fig.tight_layout()
        fig.savefig(out_dir / "rho_resp_proxy_outer_slope_hist.png")
        plt.close(fig)
    except Exception:
        pass

    print(f"Wrote: {out_csv}")
    print(f"Wrote: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
