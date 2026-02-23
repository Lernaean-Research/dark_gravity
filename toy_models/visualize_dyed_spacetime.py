"""Dyed-spacetime visualizations inferred from SPARC rotation curves.

This is intentionally phenomenology-first: it does not assume a causal model.
It infers an effective weak-field potential from v_obs(R) and renders a stylized
"dyed fabric" visualization. This is not a GR embedding diagram and it does not
solve geodesics in a reconstructed metric; the orbit rings are illustrative.

Inputs are per-galaxy CSVs produced by the SPARC runner, e.g.
`toy_models/out_sparc_runs_full_with_composition/galaxies/CamB.csv`.

Outputs:
- Per-galaxy PNGs (full figure)
- Optional multi-page PDF (one galaxy per page)
- Optional contact-sheet PDF (many galaxies per page; dyed panel only)

Usage (example):
  python toy_models/visualize_dyed_spacetime.py \
    --galaxy-dir toy_models/out_sparc_runs_full_with_composition/galaxies \
    --out-dir toy_models/out_dyed_spacetime \
    --make-pdf \
    --make-contact

Requires: numpy, matplotlib.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


A0_M_S2 = 1.2e-10
KPC_M = 3.0856775814913673e19
KM2_S2_PER_KPC_TO_M_S2 = 1.0e6 / KPC_M
A0_KM2_S2_PER_KPC = A0_M_S2 / KM2_S2_PER_KPC_TO_M_S2


@dataclass
class GalaxyCurve:
    name: str
    r_kpc: np.ndarray
    vobs_kms: np.ndarray
    e_vobs_kms: Optional[np.ndarray]
    vbar_kms: Optional[np.ndarray]
    vmodel_kms: Optional[np.ndarray]
    gbar_kms2_per_kpc: Optional[np.ndarray]
    gextra_kms2_per_kpc: Optional[np.ndarray]

    # Optional comparison overlays: store the original fit-based toy-model curve
    # before applying a Q override.
    vmodel_ref_kms: Optional[np.ndarray] = None
    gextra_ref_kms2_per_kpc: Optional[np.ndarray] = None
    q_best_kms2: Optional[float] = None
    q_alt_kind: Optional[str] = None
    q_alt_input_kms2: Optional[float] = None
    q_alt_effective_kms2: Optional[float] = None


def _parse_float(s: object) -> float:
    try:
        if s is None:
            return float("nan")
        ss = str(s).strip()
        if not ss:
            return float("nan")
        return float(ss)
    except Exception:
        return float("nan")


def _read_q_best_map(summary_csv: str) -> dict[str, float]:
    """Read summary.csv and return galaxy -> q_best_kms2."""
    out: dict[str, float] = {}
    with open(summary_csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError("summary.csv has no header")
        if "galaxy" not in reader.fieldnames or "q_best_kms2" not in reader.fieldnames:
            raise RuntimeError("summary.csv must contain columns: galaxy, q_best_kms2")
        for row in reader:
            g = str(row.get("galaxy", "")).strip()
            if not g:
                continue
            out[g] = _parse_float(row.get("q_best_kms2", ""))
    return out


def _read_q_est_map(q_est_csv: str) -> dict[str, float]:
    """Read q_est.csv and return galaxy -> q_est_kms2."""
    out: dict[str, float] = {}
    with open(q_est_csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError("q_est.csv has no header")
        if "galaxy" not in reader.fieldnames or "q_est_kms2" not in reader.fieldnames:
            raise RuntimeError("q_est.csv must contain columns: galaxy, q_est_kms2")
        for row in reader:
            g = str(row.get("galaxy", "")).strip()
            if not g:
                continue
            out[g] = _parse_float(row.get("q_est_kms2", ""))
    return out


def _apply_q_override_inplace(
    curve: GalaxyCurve,
    *,
    q_best_kms2: float,
    q_new_kms2: float,
) -> None:
    """Override model-dependent columns (v_model, g_extra) using a new Q amplitude.

    The per-galaxy CSVs contain a fitted extra field profile computed as:
      g_extra(R) = q_best * chi'(R)

    so we can recover the unit-response profile chi'(R) = g_extra/q_best and then
    substitute q_new (e.g. q_est) to get a new model overlay.
    """
    if curve.gbar_kms2_per_kpc is None or curve.gextra_kms2_per_kpc is None:
        return
    if not (math.isfinite(q_best_kms2) and q_best_kms2 > 0):
        return
    if not math.isfinite(q_new_kms2):
        return

    # Cache original fit-based curves for comparison plots.
    if curve.vmodel_ref_kms is None and curve.vmodel_kms is not None:
        curve.vmodel_ref_kms = np.asarray(curve.vmodel_kms, dtype=float).copy()
    if curve.gextra_ref_kms2_per_kpc is None and curve.gextra_kms2_per_kpc is not None:
        curve.gextra_ref_kms2_per_kpc = np.asarray(curve.gextra_kms2_per_kpc, dtype=float).copy()

    curve.q_best_kms2 = float(q_best_kms2)
    curve.q_alt_kind = "q_est"
    curve.q_alt_input_kms2 = float(q_new_kms2)

    # The fitted toy-model amplitude is constrained Q >= 0. Keep the overlay in
    # that same parameterization: negative robust estimates are treated as "no
    # extra" rather than as a subtractive field.
    q_eff = float(q_new_kms2) if q_new_kms2 > 0 else 0.0
    curve.q_alt_effective_kms2 = float(q_eff)

    r = np.asarray(curve.r_kpc, dtype=float)
    gbar = np.asarray(curve.gbar_kms2_per_kpc, dtype=float)
    gextra = np.asarray(curve.gextra_kms2_per_kpc, dtype=float)

    chi_p_u = gextra / float(q_best_kms2)
    gextra_new = float(q_eff) * chi_p_u
    gtot_new = gbar + gextra_new
    vmodel_new = np.sqrt(np.maximum(gtot_new * np.maximum(r, 0.0), 0.0))

    curve.gextra_kms2_per_kpc = gextra_new
    curve.vmodel_kms = vmodel_new


def _read_curve_csv(path: str) -> GalaxyCurve:
    name = os.path.splitext(os.path.basename(path))[0]

    rows: List[dict] = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    def col(key: str) -> Optional[np.ndarray]:
        if not rows or key not in rows[0]:
            return None
        out: List[float] = []
        for r in rows:
            s = r.get(key, "")
            if s is None or s == "":
                out.append(float("nan"))
            else:
                out.append(float(s))
        arr = np.asarray(out, dtype=float)
        if np.all(np.isnan(arr)):
            return None
        return arr

    r_kpc = col("r_kpc")
    vobs_kms = col("vobs_kms")
    if r_kpc is None or vobs_kms is None:
        raise ValueError(f"Missing required columns in {path}")

    return GalaxyCurve(
        name=name,
        r_kpc=r_kpc,
        vobs_kms=vobs_kms,
        e_vobs_kms=col("e_vobs_kms"),
        vbar_kms=col("vbar_kms"),
        vmodel_kms=col("vmodel_kms"),
        gbar_kms2_per_kpc=col("gbar_kms2_per_kpc"),
        gextra_kms2_per_kpc=col("gextra_kms2_per_kpc"),
    )


def _sanitize_monotonic_radius(r_kpc: np.ndarray, *ys: Optional[np.ndarray]) -> Tuple[np.ndarray, List[Optional[np.ndarray]]]:
    mask = np.isfinite(r_kpc) & (r_kpc > 0)
    r = r_kpc[mask]
    y_out: List[Optional[np.ndarray]] = []
    for y in ys:
        if y is None:
            y_out.append(None)
        else:
            y_out.append(y[mask])

    order = np.argsort(r)
    r = r[order]
    for i, y in enumerate(y_out):
        if y is not None:
            y_out[i] = y[order]

    # Remove duplicate radii by averaging
    if r.size == 0:
        return r, y_out

    uniq_r: List[float] = []
    uniq_idx_groups: List[List[int]] = []
    current_group: List[int] = [0]
    for i in range(1, r.size):
        if math.isclose(r[i], r[i - 1], rel_tol=0.0, abs_tol=1e-12):
            current_group.append(i)
        else:
            uniq_r.append(float(r[i - 1]))
            uniq_idx_groups.append(current_group)
            current_group = [i]
    uniq_r.append(float(r[-1]))
    uniq_idx_groups.append(current_group)

    r2 = np.asarray(uniq_r, dtype=float)
    y2_out: List[Optional[np.ndarray]] = []
    for y in y_out:
        if y is None:
            y2_out.append(None)
            continue
        vals: List[float] = []
        for g in uniq_idx_groups:
            v = np.nanmean(y[g])
            vals.append(float(v))
        y2_out.append(np.asarray(vals, dtype=float))

    return r2, y2_out


def _trapz_integral(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Cumulative trapezoid integral with y, x 1D arrays."""
    out = np.zeros_like(y, dtype=float)
    if x.size < 2:
        return out
    dx = np.diff(x)
    avg = 0.5 * (y[1:] + y[:-1])
    out[1:] = np.cumsum(dx * avg)
    return out


def _infer_potential_from_g(r_kpc: np.ndarray, g_kms2_per_kpc: np.ndarray) -> np.ndarray:
    """Return Phi(R) up to an additive constant in units of km^2/s^2.

    We take dPhi/dR = +g(R) for a central attractive field (since a = -dPhi/dR).
    Only differences matter for visualization; we set Phi(R_min)=0.
    """
    g = np.asarray(g_kms2_per_kpc, dtype=float)
    g = np.where(np.isfinite(g), g, 0.0)
    phi = _trapz_integral(r_kpc, g)
    phi -= phi[0]
    return phi


def _infer_potential_sigma_from_vobs(
    r_kpc: np.ndarray,
    vobs_kms: np.ndarray,
    e_vobs_kms: Optional[np.ndarray],
) -> Optional[np.ndarray]:
    """Approximate 1-sigma uncertainty on Phi inferred from v_obs.

    For g = v^2/R, propagate sigma_g ~= |dg/dv| sigma_v = 2|v| sigma_v / R,
    then integrate sigma_phi(R) = \\int sigma_g dR.

    This is conservative (ignores covariances between points).
    """
    if e_vobs_kms is None:
        return None
    if e_vobs_kms.shape != vobs_kms.shape:
        return None
    v = np.asarray(vobs_kms, dtype=float)
    sv = np.asarray(e_vobs_kms, dtype=float)
    if v.size < 2:
        return None
    sigma_g = (2.0 * np.abs(v) * sv) / r_kpc
    sigma_g = np.where(np.isfinite(sigma_g), sigma_g, 0.0)
    sigma_phi = _trapz_integral(r_kpc, sigma_g)
    sigma_phi -= sigma_phi[0]
    return sigma_phi


def _fabric_profile_from_phi(phi_obs: np.ndarray) -> np.ndarray:
    """Nonnegative fabric depth profile used for dye visualization."""
    f = -np.asarray(phi_obs, dtype=float)
    f -= np.nanmin(f)
    f = np.where(np.isfinite(f), f, 0.0)
    return f


def _compute_global_fabric_scale(curves: Sequence[GalaxyCurve], percentile: float = 95.0) -> float:
    """Compute a global depth scale for cross-galaxy comparable dye intensity."""
    depths: List[float] = []
    for curve in curves:
        r, ys = _sanitize_monotonic_radius(curve.r_kpc, curve.vobs_kms)
        vobs = ys[0]
        if r.size < 3:
            continue
        gobs = (vobs ** 2) / r
        phi = _infer_potential_from_g(r, gobs)
        f = _fabric_profile_from_phi(phi)
        if f.size:
            depths.append(float(np.nanmax(f)))
    if not depths:
        return 1.0
    scale = float(np.nanpercentile(np.asarray(depths, dtype=float), percentile))
    if not np.isfinite(scale) or scale <= 0:
        scale = float(np.nanmax(depths))
    return float(max(scale, 1e-9))


def _pick_rt_from_gbar(r_kpc: np.ndarray, gbar_kms2_per_kpc: Optional[np.ndarray]) -> Optional[float]:
    if gbar_kms2_per_kpc is None:
        return None
    g = np.asarray(gbar_kms2_per_kpc, dtype=float)
    m = np.isfinite(r_kpc) & np.isfinite(g)
    if not np.any(m):
        return None
    rr = r_kpc[m]
    gg = g[m]
    j = int(np.argmin(np.abs(gg - A0_KM2_S2_PER_KPC)))
    return float(rr[j])


def _central_accel_from_g(r_kpc: np.ndarray, g_kms2_per_kpc: np.ndarray, x: float, y: float) -> Tuple[float, float]:
    """Central acceleration a = -g(R) r_hat in units of km^2/s^2/kpc.

    Coordinates x,y are in kpc. The returned acceleration components are in km^2/s^2/kpc.
    """
    R = float(math.hypot(x, y))
    if not math.isfinite(R) or R <= 0:
        return 0.0, 0.0
    r0 = float(r_kpc[0])
    R_eval = max(R, r0)
    g = float(np.interp(R_eval, r_kpc, g_kms2_per_kpc, left=g_kms2_per_kpc[0], right=g_kms2_per_kpc[-1]))
    ax = -(g * x / R)
    ay = -(g * y / R)
    return ax, ay


def _integrate_orbit_leapfrog(
    r_kpc: np.ndarray,
    g_kms2_per_kpc: np.ndarray,
    *,
    x0: float,
    y0: float,
    vx0: float,
    vy0: float,
    dt: float,
    nsteps: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Integrate a 2D orbit in the inferred central potential using leapfrog.

    Units:
      - x,y in kpc
      - v in km/s
      - a in km^2/s^2/kpc
      - dt in (kpc*s)/km so that dx = v*dt and dv = a*dt

    Note: This is an effective/Newtonian dynamics map in the inferred potential sector,
    not a GR geodesic integration.
    """
    x = float(x0)
    y = float(y0)
    vx = float(vx0)
    vy = float(vy0)

    xs = np.empty(int(nsteps), dtype=float)
    ys = np.empty(int(nsteps), dtype=float)

    ax, ay = _central_accel_from_g(r_kpc, g_kms2_per_kpc, x, y)
    vx_half = vx + 0.5 * ax * dt
    vy_half = vy + 0.5 * ay * dt

    for i in range(int(nsteps)):
        xs[i] = x
        ys[i] = y

        x = x + vx_half * dt
        y = y + vy_half * dt

        ax, ay = _central_accel_from_g(r_kpc, g_kms2_per_kpc, x, y)
        vx_half = vx_half + ax * dt
        vy_half = vy_half + ay * dt

    return xs, ys


def render_orbit_map(
    curve: GalaxyCurve,
    out_png_path: str,
    *,
    orbit_turns: float = 2.0,
    steps_per_turn: int = 400,
    out_dpi: int = 180,
) -> None:
    """Render an orbit/trajectory map in the inferred effective potential.

    The force law is built directly from the observed circular-orbit centripetal acceleration:
      g_obs(R) = v_obs(R)^2 / R.
    We then integrate test-particle motion in that central field.
    """
    r, ys = _sanitize_monotonic_radius(curve.r_kpc, curve.vobs_kms, curve.gbar_kms2_per_kpc)
    vobs, gbar = ys
    if r.size < 3:
        raise ValueError(f"Not enough data points for {curve.name}")

    gobs = (vobs ** 2) / r
    gobs = np.where(np.isfinite(gobs), gobs, 0.0)

    rt = _pick_rt_from_gbar(r, gbar)
    rmax = float(np.max(r))

    # Choose a few starting radii: around Rt if available, else fractions of rmax.
    radii: List[float] = []
    if rt is not None and math.isfinite(rt) and rt > 0:
        radii = [0.6 * rt, 1.0 * rt, 1.6 * rt, 2.3 * rt]
    else:
        radii = [0.25 * rmax, 0.45 * rmax, 0.65 * rmax, 0.85 * rmax]
    radii = [rr for rr in radii if rr > float(r[0]) and rr < 0.98 * rmax]
    if not radii:
        radii = [0.5 * rmax]

    fig, ax = plt.subplots(figsize=(6.2, 6.2), constrained_layout=True)
    ax.set_title(curve.name, fontsize=12)

    # Integrate each orbit for a few turns using a dt based on local circular period.
    for j, r0 in enumerate(radii):
        v0 = float(np.interp(r0, r, vobs, left=vobs[0], right=vobs[-1]))
        v0 = max(v0, 1e-3)
        period = 2.0 * math.pi * r0 / v0  # (kpc*s)/km
        dt = period / float(max(50, int(steps_per_turn)))
        nsteps = int(max(200, int(orbit_turns * steps_per_turn)))

        xs, ys2 = _integrate_orbit_leapfrog(
            r,
            gobs,
            x0=r0,
            y0=0.0,
            vx0=0.0,
            vy0=v0,
            dt=dt,
            nsteps=nsteps,
        )
        ax.plot(xs, ys2, lw=1.1, alpha=0.85, label=f"r0={r0:.2f} kpc")

    # Reference circles
    theta = np.linspace(0.0, 2.0 * np.pi, 400)
    ax.plot(rmax * np.cos(theta), rmax * np.sin(theta), color="black", lw=0.8, alpha=0.35)
    if rt is not None and rt > 0:
        ax.plot(rt * np.cos(theta), rt * np.sin(theta), color="#9467bd", lw=0.9, alpha=0.7)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x (kpc)")
    ax.set_ylabel("y (kpc)")
    ax.set_xlim(-rmax, rmax)
    ax.set_ylim(-rmax, rmax)
    ax.grid(True, alpha=0.2)
    ax.legend(frameon=False, fontsize=8, loc="upper right")

    ax.text(
        0.02,
        0.02,
        r"Trajectories in inferred central field $g_{obs}(R)=v_{obs}^2/R$ (illustrative)",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
        ha="left",
        color="black",
        bbox=dict(boxstyle="round,pad=0.22", facecolor=(1, 1, 1, 0.70), edgecolor="none"),
    )

    os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
    fig.savefig(out_png_path, dpi=int(out_dpi))
    plt.close(fig)


def _plot_orbit_map_into_axis(
    ax: plt.Axes,
    curve: GalaxyCurve,
    *,
    orbit_turns: float = 2.0,
    steps_per_turn: int = 400,
) -> None:
    """Plot an orbit/trajectory map into an existing axis (for multi-panel figures)."""
    r, ys = _sanitize_monotonic_radius(curve.r_kpc, curve.vobs_kms, curve.gbar_kms2_per_kpc)
    vobs, gbar = ys
    if r.size < 3:
        raise ValueError(f"Not enough data points for {curve.name}")

    gobs = (vobs ** 2) / r
    gobs = np.where(np.isfinite(gobs), gobs, 0.0)

    rt = _pick_rt_from_gbar(r, gbar)
    rmax = float(np.max(r))

    radii: List[float] = []
    if rt is not None and math.isfinite(rt) and rt > 0:
        radii = [0.6 * rt, 1.0 * rt, 1.6 * rt, 2.3 * rt]
    else:
        radii = [0.25 * rmax, 0.45 * rmax, 0.65 * rmax, 0.85 * rmax]
    radii = [rr for rr in radii if rr > float(r[0]) and rr < 0.98 * rmax]
    if not radii:
        radii = [0.5 * rmax]

    for r0 in radii:
        v0 = float(np.interp(r0, r, vobs, left=vobs[0], right=vobs[-1]))
        v0 = max(v0, 1e-3)
        period = 2.0 * math.pi * r0 / v0
        dt = period / float(max(50, int(steps_per_turn)))
        nsteps = int(max(200, int(orbit_turns * steps_per_turn)))

        xs, ys2 = _integrate_orbit_leapfrog(
            r,
            gobs,
            x0=r0,
            y0=0.0,
            vx0=0.0,
            vy0=v0,
            dt=dt,
            nsteps=nsteps,
        )
        ax.plot(xs, ys2, lw=1.0, alpha=0.85)

    theta = np.linspace(0.0, 2.0 * np.pi, 400)
    ax.plot(rmax * np.cos(theta), rmax * np.sin(theta), color="black", lw=0.8, alpha=0.25)
    if rt is not None and rt > 0:
        ax.plot(rt * np.cos(theta), rt * np.sin(theta), color="#9467bd", lw=0.9, alpha=0.6)

    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Orbits (illustrative)", fontsize=10)
    ax.set_xlabel("x (kpc)")
    ax.set_ylabel("y (kpc)")
    ax.set_xlim(-rmax, rmax)
    ax.set_ylim(-rmax, rmax)
    ax.grid(True, alpha=0.2)


def _plot_residuals_into_axis(
    ax: plt.Axes,
    *,
    r_kpc: np.ndarray,
    vobs_kms: np.ndarray,
    e_vobs_kms: Optional[np.ndarray],
    vbar_kms: Optional[np.ndarray],
    vmodel_kms: Optional[np.ndarray],
    vmodel_alt_kms: Optional[np.ndarray] = None,
    vmodel_label: str = r"$v_{obs}-v_{model}$",
    vmodel_alt_label: str = r"$v_{obs}-v_{model}$ (alt)",
) -> None:
    """Plot velocity residuals vs radius."""
    ax.set_title("Residuals", fontsize=10)
    ax.axhline(0.0, color="0.2", lw=0.8, alpha=0.6)

    have_any = False
    have_e = e_vobs_kms is not None and e_vobs_kms.shape == vobs_kms.shape

    if vmodel_kms is not None:
        dv = vobs_kms - vmodel_kms
        ax.plot(r_kpc, dv, color="#d62728", lw=1.2, label=vmodel_label)
        if have_e:
            ax.fill_between(
                r_kpc,
                dv - e_vobs_kms,
                dv + e_vobs_kms,
                color="#d62728",
                alpha=0.10,
                linewidth=0,
            )
        have_any = True

    if vmodel_alt_kms is not None and vmodel_alt_kms.shape == vobs_kms.shape:
        dv2 = vobs_kms - vmodel_alt_kms
        ax.plot(r_kpc, dv2, color="#d62728", lw=1.2, ls="--", alpha=0.85, label=vmodel_alt_label)
        have_any = True

    if vbar_kms is not None:
        dvb = vobs_kms - vbar_kms
        ax.plot(r_kpc, dvb, color="#1f77b4", lw=1.0, alpha=0.9, label=r"$v_{obs}-v_{bar}$")
        if have_e:
            ax.fill_between(
                r_kpc,
                dvb - e_vobs_kms,
                dvb + e_vobs_kms,
                color="#1f77b4",
                alpha=0.07,
                linewidth=0,
            )
        have_any = True

    ax.set_xlabel("R (kpc)")
    ax.set_ylabel(r"$\Delta v$ (km s$^{-1}$)")
    ax.grid(True, alpha=0.25)
    if have_any:
        ax.legend(frameon=False, fontsize=8, loc="best")


def _polar_fabric_image(
    r_kpc: np.ndarray,
    scalar_r: np.ndarray,
    r_max: float,
    n_r: int,
    n_theta: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create a polar fabric image in Cartesian grid for fast display.

    Returns X, Y, C arrays for pcolormesh.
    """
    r_grid = np.linspace(0.0, r_max, n_r)
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)

    # Interpolate scalar profile onto r_grid
    scalar_grid = np.interp(r_grid, r_kpc, scalar_r, left=scalar_r[0], right=scalar_r[-1])

    R, T = np.meshgrid(r_grid, theta, indexing="xy")
    X = R * np.cos(T)
    Y = R * np.sin(T)
    C = np.tile(scalar_grid[None, :], (theta.size, 1))
    return X, Y, C


def _fabric_cartesian_image(
    r_kpc: np.ndarray,
    scalar_r: np.ndarray,
    r_max: float,
    img_n: int,
    *,
    mask_r_gt: Optional[float] = None,
) -> Tuple[np.ndarray, float]:
    """Return a square raster image C(y,x) suitable for imshow.

    This avoids very slow vector output when saving PDFs.
    """
    n = int(max(32, img_n))
    x = np.linspace(-r_max, r_max, n)
    y = np.linspace(-r_max, r_max, n)
    X, Y = np.meshgrid(x, y, indexing="xy")
    R = np.sqrt(X * X + Y * Y)
    scalar_grid = np.interp(R.ravel(), r_kpc, scalar_r, left=scalar_r[0], right=scalar_r[-1]).reshape(R.shape)
    if mask_r_gt is not None and np.isfinite(mask_r_gt):
        scalar_grid = np.where(R <= float(mask_r_gt), scalar_grid, np.nan)
    return scalar_grid, r_max


def render_galaxy_figure(
    curve: GalaxyCurve,
    out_png_path: Optional[str] = None,
    *,
    n_r: int = 240,
    n_theta: int = 240,
    img_n: int = 320,
    fabric_norm: str = "per_galaxy",
    global_fabric_scale: Optional[float] = None,
    fabric_extent: str = "per_galaxy",
    global_r_max_kpc: Optional[float] = None,
    fixed_r_max_kpc: Optional[float] = None,
    show_phi_uncert: bool = True,
    imshow_interpolation: str = "bilinear",
    out_dpi: int = 160,
    six_panel: bool = False,
    surface_height_mode: str = "manual",
    surface_height_norm: str = "per_galaxy",
    surface_color_norm: str = "auto",
    surface_height_kpc: float = 0.0,
    surface_height_frac: float = 0.35,
    surface_z_exag: float = 1.0,
    orbit_turns: float = 2.0,
    orbit_steps_per_turn: int = 400,
) -> plt.Figure:
    r, ys = _sanitize_monotonic_radius(
        curve.r_kpc,
        curve.vobs_kms,
        curve.e_vobs_kms,
        curve.vbar_kms,
        curve.vmodel_kms,
        curve.gbar_kms2_per_kpc,
        curve.gextra_kms2_per_kpc,
    )
    vobs, e_vobs, vbar, vmodel, gbar, gextra = ys

    if r.size < 3:
        raise ValueError(f"Not enough data points for {curve.name}")

    gobs = (vobs ** 2) / r
    phi_obs = _infer_potential_from_g(r, gobs)
    phi_sigma = _infer_potential_sigma_from_vobs(r, vobs, e_vobs) if show_phi_uncert else None

    phi_bar = None
    if vbar is not None:
        gbar_from_vbar = (vbar ** 2) / r
        phi_bar = _infer_potential_from_g(r, gbar_from_vbar)

    # Color scalar: default to gextra (if available) else gobs
    color_profile = gextra if gextra is not None else gobs

    # Normalize for display (robust)
    c = np.asarray(color_profile, dtype=float)
    c = np.where(np.isfinite(c), c, 0.0)
    c_lo, c_hi = np.percentile(c, [2.0, 98.0])
    if not np.isfinite(c_lo) or not np.isfinite(c_hi) or c_hi <= c_lo:
        c_lo, c_hi = float(np.min(c)), float(np.max(c) + 1e-9)

    # Fabric scalar: use -phi_obs so deeper potential is "lower" (darker)
    f = _fabric_profile_from_phi(phi_obs)
    if fabric_norm not in {"per_galaxy", "global"}:
        raise ValueError("fabric_norm must be 'per_galaxy' or 'global'")

    if fabric_norm == "global":
        if global_fabric_scale is None or not np.isfinite(global_fabric_scale) or global_fabric_scale <= 0:
            raise ValueError("global_fabric_scale must be provided and > 0 when fabric_norm='global'")
        f_scale = float(global_fabric_scale)
    else:
        f_scale = float(np.nanpercentile(f, 95.0))
        if not np.isfinite(f_scale) or f_scale <= 0:
            f_scale = float(np.max(f) + 1e-9)

    f_norm = np.clip(f / f_scale, 0.0, 1.0)

    r_data_max = float(np.max(r))
    if fabric_extent not in {"per_galaxy", "global_max", "fixed"}:
        raise ValueError("fabric_extent must be one of: per_galaxy, global_max, fixed")
    if fabric_extent == "per_galaxy":
        r_plot_max = r_data_max
    elif fabric_extent == "global_max":
        if global_r_max_kpc is None or not np.isfinite(global_r_max_kpc) or global_r_max_kpc <= 0:
            raise ValueError("global_r_max_kpc must be provided and > 0 when fabric_extent='global_max'")
        r_plot_max = float(global_r_max_kpc)
    else:
        if fixed_r_max_kpc is None or not np.isfinite(fixed_r_max_kpc) or fixed_r_max_kpc <= 0:
            raise ValueError("fixed_r_max_kpc must be provided and > 0 when fabric_extent='fixed'")
        r_plot_max = float(fixed_r_max_kpc)

    # If plotting beyond the data, mask that region to avoid implying extrapolated structure.
    mask_r_gt = None if r_plot_max <= r_data_max + 1e-12 else r_data_max
    C_img, _ = _fabric_cartesian_image(r, f_norm, r_max=r_plot_max, img_n=img_n, mask_r_gt=mask_r_gt)

    # Prepare figure
    if six_panel:
        fig = plt.figure(figsize=(11.0, 8.2), constrained_layout=True)
        gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0], width_ratios=[1.05, 1.0, 1.2])
        ax0 = fig.add_subplot(gs[0, 0])
        ax1 = fig.add_subplot(gs[0, 1])
        ax2 = fig.add_subplot(gs[0, 2])
        ax3 = fig.add_subplot(gs[1, 0], projection="3d")
        ax4 = fig.add_subplot(gs[1, 1])
        ax5 = fig.add_subplot(gs[1, 2])
    else:
        fig = plt.figure(figsize=(11.0, 4.2), constrained_layout=True)
        gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.2])
        ax0 = fig.add_subplot(gs[0, 0])
        ax1 = fig.add_subplot(gs[0, 1])
        ax2 = fig.add_subplot(gs[0, 2])

    # Panel 1: rotation curve
    ax0.set_title("Rotation curve", fontsize=10)
    ax0.plot(r, vobs, color="black", lw=1.4, label=r"$v_{obs}$")
    if e_vobs is not None:
        ax0.fill_between(r, vobs - e_vobs, vobs + e_vobs, color="black", alpha=0.12, linewidth=0)
    if vbar is not None:
        ax0.plot(r, vbar, color="#1f77b4", lw=1.2, label=r"$v_{bar}$")
    # If a Q override was applied, plot both the original fit model and the overridden model.
    vmodel_ref = curve.vmodel_ref_kms
    have_ref = vmodel_ref is not None and vmodel is not None and vmodel_ref.shape == vmodel.shape
    if have_ref:
        ax0.plot(r, vmodel_ref, color="#d62728", lw=1.2, ls="--", alpha=0.85, label=r"$v_{model}$ (fit $Q_{best}$)")
        ax0.plot(r, vmodel, color="#d62728", lw=1.2, label=r"$v_{model}$ (robust $Q_{est}$)")
    elif vmodel is not None:
        ax0.plot(r, vmodel, color="#d62728", lw=1.2, label=r"$v_{model}$")
    ax0.set_xlabel("R (kpc)")
    ax0.set_ylabel(r"$v$ (km s$^{-1}$)")
    ax0.grid(True, alpha=0.25)
    ax0.legend(frameon=False, fontsize=8, loc="best")

    # Panel 2: inferred potentials
    ax1.set_title("Effective potential", fontsize=10)
    ax1.plot(r, phi_obs, color="black", lw=1.4, label=r"$\Phi_{obs}$")
    if phi_sigma is not None:
        ax1.fill_between(r, phi_obs - phi_sigma, phi_obs + phi_sigma, color="black", alpha=0.10, linewidth=0)
    if phi_bar is not None:
        ax1.plot(r, phi_bar, color="#1f77b4", lw=1.2, label=r"$\Phi_{bar}$")
    ax1.set_xlabel("R (kpc)")
    ax1.set_ylabel(r"$\Phi$ (km$^2$ s$^{-2}$)")
    ax1.grid(True, alpha=0.25)
    ax1.legend(frameon=False, fontsize=8, loc="best")

    rt = _pick_rt_from_gbar(r, gbar)
    if rt is not None:
        for ax in (ax0, ax1):
            ax.axvline(rt, color="#9467bd", lw=1.0, alpha=0.8)
        ax1.text(rt, ax1.get_ylim()[0], r"$R_t$", color="#9467bd", fontsize=9, ha="left", va="bottom")

    # Panel 3: dyed fabric (polar)
    ax2.set_title("Dyed potential depth", fontsize=10)
    cmap = plt.get_cmap("magma").copy()
    cmap.set_bad(color=(1.0, 1.0, 1.0, 1.0))
    im = ax2.imshow(
        C_img,
        cmap=cmap,
        origin="lower",
        extent=[-r_plot_max, r_plot_max, -r_plot_max, r_plot_max],
        interpolation=imshow_interpolation,
    )

    # Overlay a few circular-orbit rings (purely illustrative; not computed geodesics)
    ring_radii = []
    if rt is not None:
        ring_radii = [0.5 * rt, rt, 2.0 * rt]
    else:
        ring_radii = [0.4 * r_plot_max, 0.7 * r_plot_max, 0.9 * r_plot_max]

    theta = np.linspace(0.0, 2.0 * np.pi, 400)
    for rr in ring_radii:
        if rr <= 0 or rr > r_plot_max:
            continue
        ax2.plot(rr * np.cos(theta), rr * np.sin(theta), color="white", lw=0.9, alpha=0.8)

    norm_str = "global" if fabric_norm == "global" else "per-galaxy"

    ax2.text(
        0.98,
        0.02,
        f"Rmax={r_data_max:.1f} kpc",
        transform=ax2.transAxes,
        fontsize=8,
        color="white",
        va="bottom",
        ha="right",
        bbox=dict(boxstyle="round,pad=0.20", facecolor=(0, 0, 0, 0.25), edgecolor="none"),
    )

    # Add a colorbar keyed to the fabric normalization
    cb = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.03)
    cb.set_label(f"Depth (normalized, {norm_str})", fontsize=8)
    cb.ax.tick_params(labelsize=8)

    ax2.set_aspect("equal", adjustable="box")
    ax2.set_xlabel("x (kpc)")
    ax2.set_ylabel("y (kpc)")
    ax2.set_xlim(-r_plot_max, r_plot_max)
    ax2.set_ylim(-r_plot_max, r_plot_max)

    # Clean figure header
    fig.suptitle(curve.name, fontsize=12)
    fig.text(
        0.5,
        0.01,
        r"Inferred from $v_{obs}(R)$; dyed panel is a visualization proxy (not a GR embedding)",
        ha="center",
        va="bottom",
        fontsize=8,
        color="0.25",
    )

    if six_panel:
        _plot_fabric_surface_3d_into_axis(
            ax3,
            curve,
            img_n=max(140, img_n // 2),
            fabric_norm=fabric_norm,
            global_fabric_scale=global_fabric_scale,
            fabric_extent=fabric_extent,
            global_r_max_kpc=global_r_max_kpc,
            fixed_r_max_kpc=fixed_r_max_kpc,
            surface_height_mode=surface_height_mode,
            surface_height_norm=surface_height_norm,
            surface_color_norm=surface_color_norm,
            surface_height_kpc=surface_height_kpc,
            surface_height_frac=surface_height_frac,
            z_exaggeration=surface_z_exag,
        )
        _plot_orbit_map_into_axis(
            ax4,
            curve,
            orbit_turns=float(orbit_turns),
            steps_per_turn=int(orbit_steps_per_turn),
        )
        _plot_residuals_into_axis(
            ax5,
            r_kpc=r,
            vobs_kms=vobs,
            e_vobs_kms=e_vobs,
            vbar_kms=vbar,
            vmodel_kms=vmodel,
            vmodel_alt_kms=(curve.vmodel_ref_kms if (curve.vmodel_ref_kms is not None and vmodel is not None and curve.vmodel_ref_kms.shape == vmodel.shape) else None),
            vmodel_label=r"$v_{obs}-v_{model}$ (robust $Q_{est}$)",
            vmodel_alt_label=r"$v_{obs}-v_{model}$ (fit $Q_{best}$)",
        )

    if out_png_path is not None:
        os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
        fig.savefig(out_png_path, dpi=int(out_dpi))

    return fig


def render_fabric_surface_3d(
    curve: GalaxyCurve,
    out_png_path: str,
    *,
    img_n: int = 220,
    fabric_norm: str = "per_galaxy",
    global_fabric_scale: Optional[float] = None,
    fabric_extent: str = "per_galaxy",
    global_r_max_kpc: Optional[float] = None,
    fixed_r_max_kpc: Optional[float] = None,
    surface_height_mode: str = "manual",
    surface_height_norm: str = "per_galaxy",
    surface_color_norm: str = "auto",
    surface_height_kpc: float = 0.0,
    surface_height_frac: float = 0.25,
    z_exaggeration: float = 1.0,
    out_dpi: int = 160,
) -> None:
    """Render a simple 3D surface proxy of the dyed fabric.

    This is an embedding-style visualization of the inferred effective potential depth
    profile (from v_obs), not a GR metric embedding.
    """
    r, ys = _sanitize_monotonic_radius(curve.r_kpc, curve.vobs_kms)
    vobs = ys[0]
    if r.size < 3:
        raise ValueError(f"Not enough data points for {curve.name}")

    gobs = (vobs ** 2) / r
    phi_obs = _infer_potential_from_g(r, gobs)
    f = _fabric_profile_from_phi(phi_obs)

    if fabric_norm not in {"per_galaxy", "global"}:
        raise ValueError("fabric_norm must be 'per_galaxy' or 'global'")
    if fabric_norm == "global":
        if global_fabric_scale is None or not np.isfinite(global_fabric_scale) or global_fabric_scale <= 0:
            raise ValueError("global_fabric_scale must be provided and > 0 when fabric_norm='global'")
        f_scale_color = float(global_fabric_scale)
    else:
        f_scale_color = float(np.nanpercentile(f, 95.0))
        if not np.isfinite(f_scale_color) or f_scale_color <= 0:
            f_scale_color = float(np.max(f) + 1e-9)
    f_norm_color = np.clip(f / f_scale_color, 0.0, 1.0)

    if surface_height_norm not in {"per_galaxy", "match_color"}:
        raise ValueError("surface_height_norm must be one of: per_galaxy, match_color")
    if surface_height_norm == "match_color":
        f_norm_height = f_norm_color
    else:
        f_scale_height = float(np.nanpercentile(f, 95.0))
        if not np.isfinite(f_scale_height) or f_scale_height <= 0:
            f_scale_height = float(np.max(f) + 1e-9)
        f_norm_height = np.clip(f / f_scale_height, 0.0, 1.0)

    r_data_max = float(np.max(r))
    if fabric_extent not in {"per_galaxy", "global_max", "fixed"}:
        raise ValueError("fabric_extent must be one of: per_galaxy, global_max, fixed")
    if fabric_extent == "per_galaxy":
        r_plot_max = r_data_max
    elif fabric_extent == "global_max":
        if global_r_max_kpc is None or not np.isfinite(global_r_max_kpc) or global_r_max_kpc <= 0:
            raise ValueError("global_r_max_kpc must be provided and > 0 when fabric_extent='global_max'")
        r_plot_max = float(global_r_max_kpc)
    else:
        if fixed_r_max_kpc is None or not np.isfinite(fixed_r_max_kpc) or fixed_r_max_kpc <= 0:
            raise ValueError("fixed_r_max_kpc must be provided and > 0 when fabric_extent='fixed'")
        r_plot_max = float(fixed_r_max_kpc)

    mask_r_gt = None if r_plot_max <= r_data_max + 1e-12 else r_data_max

    # Two separate scalar fields:
    # - color field: normalized depth (0..1), comparable across galaxies when fabric_norm='global'
    # - height field: proxy height in kpc, so x/y/z share the same unit
    C_color, _ = _fabric_cartesian_image(r, f_norm_color, r_max=r_plot_max, img_n=img_n, mask_r_gt=mask_r_gt)

    if surface_height_mode not in {"manual", "phi_over_c2", "accel_over_a0"}:
        raise ValueError("surface_height_mode must be one of: manual, phi_over_c2, accel_over_a0")

    if not np.isfinite(z_exaggeration) or z_exaggeration <= 0:
        z_exaggeration = 1.0

    z_scale_note = ""
    if surface_height_mode == "manual":
        # Manual mapping: user chooses z_max (in kpc) either explicitly or as a fraction of R_plot.
        if not np.isfinite(surface_height_kpc):
            surface_height_kpc = 0.0
        if not np.isfinite(surface_height_frac) or surface_height_frac <= 0:
            surface_height_frac = 0.25
        if surface_height_kpc and surface_height_kpc > 0:
            z_max_kpc = float(surface_height_kpc)
            z_scale_note = f"z_max={z_max_kpc:g} kpc"
        else:
            z_max_kpc = float(surface_height_frac) * float(r_plot_max)
            z_scale_note = f"z_max={surface_height_frac:g}\u00d7R_plot"
        z_max_kpc *= float(z_exaggeration)
        height_profile_kpc = f_norm_height * float(z_max_kpc)
        z_scale_note = f"{z_scale_note}; \u00d7z_exag={z_exaggeration:g}"
    elif surface_height_mode == "phi_over_c2":
        # Physically tiny: use dimensionless potential depth ~ Phi/c^2, mapped to a length scale via R_plot.
        # This keeps units consistent (kpc) without inventing an arbitrary vertical scale.
        c_km_s = 299_792.458
        c2 = c_km_s * c_km_s
        # f has units km^2/s^2; f/c^2 is dimensionless.
        height_profile_kpc = (f / float(c2)) * float(r_plot_max) * float(z_exaggeration)
        height_profile_kpc = np.where(np.isfinite(height_profile_kpc), height_profile_kpc, 0.0)
        height_profile_kpc -= float(np.nanmin(height_profile_kpc))
        z_max_kpc = float(np.nanmax(height_profile_kpc))
        z_scale_note = (
            f"height=(\u0394\u03a6/c^2)\u00d7R_plot; \u00d7z_exag={z_exaggeration:g}; "
            f"z_max\u2248{z_max_kpc:.3g} kpc"
        )
    else:
        # Still unit-consistent and typically visible: integrate g/a0 over R to get a kpc-scale proxy.
        # This is a visualization proxy, not a GR embedding.
        a0 = float(A0_KM2_S2_PER_KPC)
        if not np.isfinite(a0) or a0 <= 0:
            raise ValueError("A0_KM2_S2_PER_KPC must be finite and > 0")
        h = _trapz_integral(r, gobs / a0)  # kpc
        h = np.where(np.isfinite(h), h, 0.0)
        # Make center 'deeper' (larger height) like the dye depth visualization.
        height_profile_kpc = (float(np.nanmax(h)) - h) * float(z_exaggeration)
        height_profile_kpc -= float(np.nanmin(height_profile_kpc))
        z_max_kpc = float(np.nanmax(height_profile_kpc))
        z_scale_note = f"height=\u222b(g/a0)dR; \u00d7z_exag={z_exaggeration:g}; z_max\u2248{z_max_kpc:.3g} kpc"

    if not np.isfinite(z_max_kpc) or z_max_kpc <= 0:
        z_max_kpc = 1e-6

    C_height, _ = _fabric_cartesian_image(r, height_profile_kpc, r_max=r_plot_max, img_n=img_n, mask_r_gt=mask_r_gt)

    n = C_color.shape[0]
    xs = np.linspace(-r_plot_max, r_plot_max, n)
    ys2 = np.linspace(-r_plot_max, r_plot_max, n)
    X, Y = np.meshgrid(xs, ys2, indexing="xy")
    Z_color = np.where(np.isfinite(C_color), C_color, np.nan)
    Z_plot = np.where(np.isfinite(C_height), C_height, np.nan)

    fig = plt.figure(figsize=(6.8, 5.4), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title(curve.name, fontsize=12)
    ax.text2D(
        0.02,
        0.98,
        f"3D proxy surface  |  z in kpc ({surface_height_mode})",
        transform=ax.transAxes,
        fontsize=8,
        ha="left",
        va="top",
        color="0.25",
    )

    # Plot: colors are normalized depth (0..1). Height is kpc.
    cmap = plt.get_cmap("magma")
    if surface_color_norm not in {"auto", "fixed01"}:
        raise ValueError("surface_color_norm must be one of: auto, fixed01")

    Zc = np.nan_to_num(Z_color, nan=0.0)
    if surface_color_norm == "fixed01":
        norm = matplotlib.colors.Normalize(vmin=0.0, vmax=1.0)
    else:
        finite = np.isfinite(Z_color)
        if np.any(finite):
            vmin = float(np.nanmin(Z_color[finite]))
            vmax = float(np.nanmax(Z_color[finite]))
        else:
            vmin, vmax = 0.0, 1.0
        if not np.isfinite(vmin) or not np.isfinite(vmax) or vmax <= vmin + 1e-12:
            vmin, vmax = 0.0, 1.0
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)

    facecolors = cmap(norm(Zc))
    facecolors[..., 3] = np.where(np.isfinite(Z_color) & np.isfinite(Z_plot), 0.95, 0.0)

    ax.plot_surface(
        X,
        Y,
        Z_plot,
        rstride=2,
        cstride=2,
        facecolors=facecolors,
        linewidth=0,
        antialiased=True,
        shade=True,
    )

    ax.set_xlabel("x (kpc)")
    ax.set_ylabel("y (kpc)")
    ax.set_zlabel("proxy height (kpc)")
    ax.view_init(elev=28, azim=-55)

    # Stable z-scale so comparisons don't auto-stretch.
    try:
        ax.set_zlim(0.0, float(z_max_kpc))
    except Exception:
        pass

    # Make x/y comparable and avoid wildly stretched boxes.
    try:
        # Equal-unit scaling: box aspect proportional to actual coordinate ranges.
        # x,y span 2*R_plot; z spans z_max_kpc.
        ax.set_box_aspect((2.0 * float(r_plot_max), 2.0 * float(r_plot_max), float(z_max_kpc)))
    except Exception:
        pass

    ax.text2D(
        0.02,
        0.02,
        f"Rmax={r_data_max:.1f} kpc  |  zmax={z_max_kpc:.3g} kpc",
        transform=ax.transAxes,
        fontsize=8,
        ha="left",
        va="bottom",
        color="0.25",
    )
    os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
    fig.savefig(out_png_path, dpi=int(out_dpi))
    plt.close(fig)


def _plot_fabric_surface_3d_into_axis(
    ax,
    curve: GalaxyCurve,
    *,
    img_n: int = 220,
    fabric_norm: str = "per_galaxy",
    global_fabric_scale: Optional[float] = None,
    fabric_extent: str = "per_galaxy",
    global_r_max_kpc: Optional[float] = None,
    fixed_r_max_kpc: Optional[float] = None,
    surface_height_mode: str = "manual",
    surface_height_norm: str = "per_galaxy",
    surface_color_norm: str = "auto",
    surface_height_kpc: float = 0.0,
    surface_height_frac: float = 0.25,
    z_exaggeration: float = 1.0,
) -> None:
    """Render the 3D proxy surface into a provided 3D axis."""
    r, ys = _sanitize_monotonic_radius(curve.r_kpc, curve.vobs_kms)
    vobs = ys[0]
    if r.size < 3:
        raise ValueError(f"Not enough data points for {curve.name}")

    gobs = (vobs ** 2) / r
    phi_obs = _infer_potential_from_g(r, gobs)
    f = _fabric_profile_from_phi(phi_obs)

    if fabric_norm not in {"per_galaxy", "global"}:
        raise ValueError("fabric_norm must be 'per_galaxy' or 'global'")
    if fabric_norm == "global":
        if global_fabric_scale is None or not np.isfinite(global_fabric_scale) or global_fabric_scale <= 0:
            raise ValueError("global_fabric_scale must be provided and > 0 when fabric_norm='global'")
        f_scale_color = float(global_fabric_scale)
    else:
        f_scale_color = float(np.nanpercentile(f, 95.0))
        if not np.isfinite(f_scale_color) or f_scale_color <= 0:
            f_scale_color = float(np.max(f) + 1e-9)
    f_norm_color = np.clip(f / f_scale_color, 0.0, 1.0)

    if surface_height_norm not in {"per_galaxy", "match_color"}:
        raise ValueError("surface_height_norm must be one of: per_galaxy, match_color")
    if surface_height_norm == "match_color":
        f_norm_height = f_norm_color
    else:
        f_scale_height = float(np.nanpercentile(f, 95.0))
        if not np.isfinite(f_scale_height) or f_scale_height <= 0:
            f_scale_height = float(np.max(f) + 1e-9)
        f_norm_height = np.clip(f / f_scale_height, 0.0, 1.0)

    r_data_max = float(np.max(r))
    if fabric_extent not in {"per_galaxy", "global_max", "fixed"}:
        raise ValueError("fabric_extent must be one of: per_galaxy, global_max, fixed")
    if fabric_extent == "per_galaxy":
        r_plot_max = r_data_max
    elif fabric_extent == "global_max":
        if global_r_max_kpc is None or not np.isfinite(global_r_max_kpc) or global_r_max_kpc <= 0:
            raise ValueError("global_r_max_kpc must be provided and > 0 when fabric_extent='global_max'")
        r_plot_max = float(global_r_max_kpc)
    else:
        if fixed_r_max_kpc is None or not np.isfinite(fixed_r_max_kpc) or fixed_r_max_kpc <= 0:
            raise ValueError("fixed_r_max_kpc must be provided and > 0 when fabric_extent='fixed'")
        r_plot_max = float(fixed_r_max_kpc)

    mask_r_gt = None if r_plot_max <= r_data_max + 1e-12 else r_data_max
    C_color, _ = _fabric_cartesian_image(r, f_norm_color, r_max=r_plot_max, img_n=img_n, mask_r_gt=mask_r_gt)

    if surface_height_mode not in {"manual", "phi_over_c2", "accel_over_a0"}:
        raise ValueError("surface_height_mode must be one of: manual, phi_over_c2, accel_over_a0")
    if not np.isfinite(z_exaggeration) or z_exaggeration <= 0:
        z_exaggeration = 1.0

    if surface_height_mode == "manual":
        if not np.isfinite(surface_height_kpc):
            surface_height_kpc = 0.0
        if not np.isfinite(surface_height_frac) or surface_height_frac <= 0:
            surface_height_frac = 0.25
        if surface_height_kpc and surface_height_kpc > 0:
            z_max_kpc = float(surface_height_kpc)
        else:
            z_max_kpc = float(surface_height_frac) * float(r_plot_max)
        z_max_kpc *= float(z_exaggeration)
        height_profile_kpc = f_norm_height * float(z_max_kpc)
    elif surface_height_mode == "phi_over_c2":
        c_km_s = 299_792.458
        c2 = c_km_s * c_km_s
        height_profile_kpc = (f / float(c2)) * float(r_plot_max) * float(z_exaggeration)
        height_profile_kpc = np.where(np.isfinite(height_profile_kpc), height_profile_kpc, 0.0)
        height_profile_kpc -= float(np.nanmin(height_profile_kpc))
        z_max_kpc = float(np.nanmax(height_profile_kpc))
    else:
        a0 = float(A0_KM2_S2_PER_KPC)
        h = _trapz_integral(r, gobs / a0)
        h = np.where(np.isfinite(h), h, 0.0)
        height_profile_kpc = (float(np.nanmax(h)) - h) * float(z_exaggeration)
        height_profile_kpc -= float(np.nanmin(height_profile_kpc))
        z_max_kpc = float(np.nanmax(height_profile_kpc))

    if not np.isfinite(z_max_kpc) or z_max_kpc <= 0:
        z_max_kpc = 1e-6

    C_height, _ = _fabric_cartesian_image(r, height_profile_kpc, r_max=r_plot_max, img_n=img_n, mask_r_gt=mask_r_gt)
    n = C_color.shape[0]
    xs = np.linspace(-r_plot_max, r_plot_max, n)
    ys2 = np.linspace(-r_plot_max, r_plot_max, n)
    X, Y = np.meshgrid(xs, ys2, indexing="xy")
    Z_color = np.where(np.isfinite(C_color), C_color, np.nan)
    Z_plot = np.where(np.isfinite(C_height), C_height, np.nan)

    cmap = plt.get_cmap("magma")
    if surface_color_norm not in {"auto", "fixed01"}:
        raise ValueError("surface_color_norm must be one of: auto, fixed01")
    Zc = np.nan_to_num(Z_color, nan=0.0)
    if surface_color_norm == "fixed01":
        norm = matplotlib.colors.Normalize(vmin=0.0, vmax=1.0)
    else:
        finite = np.isfinite(Z_color)
        if np.any(finite):
            vmin = float(np.nanmin(Z_color[finite]))
            vmax = float(np.nanmax(Z_color[finite]))
        else:
            vmin, vmax = 0.0, 1.0
        if not np.isfinite(vmin) or not np.isfinite(vmax) or vmax <= vmin + 1e-12:
            vmin, vmax = 0.0, 1.0
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)

    facecolors = cmap(norm(Zc))
    facecolors[..., 3] = np.where(np.isfinite(Z_color) & np.isfinite(Z_plot), 0.95, 0.0)

    ax.plot_surface(
        X,
        Y,
        Z_plot,
        rstride=2,
        cstride=2,
        facecolors=facecolors,
        linewidth=0,
        antialiased=True,
        shade=True,
    )
    ax.set_title("3D proxy", fontsize=10)
    ax.set_xlabel("x (kpc)")
    ax.set_ylabel("y (kpc)")
    # Matplotlib 3D z-label placement is hard to control precisely and can overlap
    # the neighboring subplot in a tight 2x3 layout. Disable the native z-label and
    # draw a left-anchored label in axes coordinates instead.
    ax.set_zlabel("")
    zlab = ax.text2D(
        -0.10,
        0.55,
        "z (kpc)",
        transform=ax.transAxes,
        rotation=90,
        ha="right",
        va="center",
        fontsize=9,
        color="0.2",
    )
    try:
        zlab.set_in_layout(False)
    except Exception:
        pass
    ax.view_init(elev=28, azim=-55)

    # Keep tick labels compact; nudge z tick labels slightly inward.
    # (Big negative pads tend to break across backends/DPI.)
    try:
        ax.xaxis.set_tick_params(labelsize=8, pad=0)
        ax.yaxis.set_tick_params(labelsize=8, pad=0)
        ax.zaxis.set_tick_params(labelsize=8, pad=-2)
    except Exception:
        pass
    try:
        ax.set_zlim(0.0, float(z_max_kpc))
    except Exception:
        pass
    try:
        # A strict equal-unit box (x/y span 2R_plot, z spans z_max) often looks
        # like a pancake in the 2x3 layout. Use a gentle minimum z/xy aspect so
        # the surface has room to breathe while still respecting the z scale.
        z_to_xy = float(z_max_kpc) / max(2.0 * float(r_plot_max), 1e-9)
        z_aspect = max(0.35, min(0.85, z_to_xy))
        # Nudge the 3D box a bit narrower in x/y so the right-side gutter to the
        # orbit panel matches the reference layout.
        ax.set_box_aspect((0.92, 0.92, float(z_aspect)))
    except Exception:
        pass

    # Native 3D z tick labels can protrude outside the axes (overlapping the
    # neighboring subplot). Hide them and redraw the scale numbers on the left
    # *inside* the 3D panel.
    try:
        ax.xaxis.set_tick_params(labelsize=8, pad=0)
        ax.yaxis.set_tick_params(labelsize=8, pad=0)
        z0, z1 = ax.get_zlim()
        # Disable native z ticks entirely so constrained_layout doesn't reserve
        # right-side space for 3D tick labels.
        ax.set_zticks([])
        locator = matplotlib.ticker.MaxNLocator(nbins=5)
        ticks = [float(t) for t in locator.tick_values(float(z0), float(z1)) if np.isfinite(t) and z0 - 1e-12 <= t <= z1 + 1e-12]
        dz = float(z1 - z0) if np.isfinite(z1 - z0) else 0.0
        for t in ticks:
            frac = 0.0 if dz <= 0 else (t - float(z0)) / dz
            y = 0.14 + 0.76 * float(np.clip(frac, 0.0, 1.0))
            tt = ax.text2D(
                0.015,
                y,
                f"{t:g}",
                transform=ax.transAxes,
                ha="left",
                va="center",
                fontsize=8,
                color="0.2",
                bbox=dict(boxstyle="round,pad=0.12", facecolor=(1, 1, 1, 0.55), edgecolor="none"),
            )
            try:
                tt.set_in_layout(False)
            except Exception:
                pass
    except Exception:
        pass
    ax.text2D(
        0.02,
        0.02,
        f"Rmax={r_data_max:.1f} kpc | zmax={z_max_kpc:.3g} kpc",
        transform=ax.transAxes,
        fontsize=8,
        ha="left",
        va="bottom",
        color="0.25",
    )


def _iter_csv_files(galaxy_dir: str) -> List[str]:
    paths: List[str] = []
    for name in os.listdir(galaxy_dir):
        if name.lower().endswith(".csv"):
            paths.append(os.path.join(galaxy_dir, name))
    paths.sort(key=lambda p: os.path.basename(p).lower())
    return paths


def _render_contact_sheet(
    curves: Sequence[GalaxyCurve],
    out_pdf_path: str,
    *,
    nrows: int = 3,
    ncols: int = 4,
    img_n: int = 240,
    fabric_norm: str = "per_galaxy",
    global_fabric_scale: Optional[float] = None,
    fabric_extent: str = "per_galaxy",
    global_r_max_kpc: Optional[float] = None,
    fixed_r_max_kpc: Optional[float] = None,
    imshow_interpolation: str = "bilinear",
    out_dpi: int = 160,
) -> None:
    per_page = nrows * ncols
    if per_page <= 0:
        return

    os.makedirs(os.path.dirname(out_pdf_path), exist_ok=True)
    with PdfPages(out_pdf_path) as pdf:
        for start in range(0, len(curves), per_page):
            batch = curves[start : start + per_page]
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(11.0, 8.5), constrained_layout=True)
            axes_list = list(np.ravel(axes))

            for ax in axes_list:
                ax.set_axis_off()

            for ax, curve in zip(axes_list, batch):
                r, ys = _sanitize_monotonic_radius(curve.r_kpc, curve.vobs_kms, curve.gbar_kms2_per_kpc)
                vobs, gbar = ys
                gobs = (vobs ** 2) / r
                phi_obs = _infer_potential_from_g(r, gobs)
                f = _fabric_profile_from_phi(phi_obs)
                if fabric_norm == "global":
                    if global_fabric_scale is None or not np.isfinite(global_fabric_scale) or global_fabric_scale <= 0:
                        raise ValueError("global_fabric_scale must be provided and > 0 when fabric_norm='global'")
                    f_scale = float(global_fabric_scale)
                else:
                    f_scale = float(np.nanpercentile(f, 95.0))
                    if not np.isfinite(f_scale) or f_scale <= 0:
                        f_scale = float(np.max(f) + 1e-9)
                f_norm = np.clip(f / f_scale, 0.0, 1.0)

                r_data_max = float(np.max(r))
                if fabric_extent not in {"per_galaxy", "global_max", "fixed"}:
                    raise ValueError("fabric_extent must be one of: per_galaxy, global_max, fixed")
                if fabric_extent == "per_galaxy":
                    r_plot_max = r_data_max
                elif fabric_extent == "global_max":
                    if global_r_max_kpc is None or not np.isfinite(global_r_max_kpc) or global_r_max_kpc <= 0:
                        raise ValueError("global_r_max_kpc must be provided and > 0 when fabric_extent='global_max'")
                    r_plot_max = float(global_r_max_kpc)
                else:
                    if fixed_r_max_kpc is None or not np.isfinite(fixed_r_max_kpc) or fixed_r_max_kpc <= 0:
                        raise ValueError("fixed_r_max_kpc must be provided and > 0 when fabric_extent='fixed'")
                    r_plot_max = float(fixed_r_max_kpc)

                mask_r_gt = None if r_plot_max <= r_data_max + 1e-12 else r_data_max
                C_img, _ = _fabric_cartesian_image(r, f_norm, r_max=r_plot_max, img_n=img_n, mask_r_gt=mask_r_gt)

                ax.set_axis_on()
                cmap = plt.get_cmap("magma").copy()
                cmap.set_bad(color=(1.0, 1.0, 1.0, 1.0))
                ax.imshow(
                    C_img,
                    cmap=cmap,
                    origin="lower",
                    extent=[-r_plot_max, r_plot_max, -r_plot_max, r_plot_max],
                    interpolation=imshow_interpolation,
                )
                ax.set_aspect("equal", adjustable="box")
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title(f"{curve.name}\nRmax={r_data_max:.1f} kpc", fontsize=8)

            fig.suptitle("Dyed-fabric contact sheet (inferred effective potential from v_obs(R))", fontsize=12)
            pdf.savefig(fig, dpi=int(out_dpi))
            plt.close(fig)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--galaxy-dir",
        required=True,
        help="Directory containing per-galaxy CSVs (from SPARC runner).",
    )
    ap.add_argument(
        "--out-dir",
        required=True,
        help="Output directory for rendered figures.",
    )
    ap.add_argument(
        "--make-pdf",
        action="store_true",
        help="Also create a multi-page PDF (one galaxy per page).",
    )
    ap.add_argument(
        "--make-contact",
        action="store_true",
        help="Also create a contact-sheet PDF (many galaxies per page; polar panel only).",
    )
    ap.add_argument(
        "--max-galaxies",
        type=int,
        default=0,
        help="If >0, limit to the first N galaxies (debug/speed).",
    )
    ap.add_argument(
        "--only",
        type=str,
        default="",
        help="Comma-separated list of galaxy names (CSV stem) to render, e.g. 'CamB,ESO563-G021'.",
    )
    ap.add_argument("--n-r", type=int, default=240, help="Polar radius resolution.")
    ap.add_argument("--n-theta", type=int, default=240, help="Polar angle resolution.")
    ap.add_argument("--img-n", type=int, default=320, help="Raster image resolution (square).")
    ap.add_argument("--dpi", type=int, default=160, help="Output DPI for PNG/PDF pages.")
    ap.add_argument(
        "--interp",
        choices=["nearest", "bilinear", "bicubic"],
        default="bilinear",
        help="Interpolation used for dyed-panel imshow (speed/appearance tradeoff).",
    )
    ap.add_argument(
        "--fabric-norm",
        choices=["per_galaxy", "global"],
        default="per_galaxy",
        help="How to normalize dyed-panel depth across galaxies.",
    )
    ap.add_argument(
        "--fabric-extent",
        choices=["per_galaxy", "global_max", "fixed"],
        default="per_galaxy",
        help=(
            "How to set the dyed-panel spatial extent in kpc. "
            "per_galaxy: each panel spans its own max observed radius; "
            "global_max: all panels share the maximum observed radius across the sample; "
            "fixed: all panels share a user-provided radius via --fixed-rmax-kpc."
        ),
    )
    ap.add_argument(
        "--fixed-rmax-kpc",
        type=float,
        default=0.0,
        help="If --fabric-extent=fixed, the dyed panel spans ±this radius in kpc.",
    )
    ap.add_argument(
        "--global-percentile",
        type=float,
        default=95.0,
        help="If --fabric-norm=global, use this percentile of per-galaxy max depth as the global scale.",
    )
    ap.add_argument(
        "--no-phi-uncert",
        action="store_true",
        help="Disable propagated potential uncertainty band even if e_vobs_kms exists.",
    )
    ap.add_argument(
        "--make-3d",
        action="store_true",
        help="Also render a simple 3D embedding-style proxy surface PNG per galaxy.",
    )
    ap.add_argument(
        "--make-orbit-map",
        action="store_true",
        help="Also render a computed trajectory/orbit map in the inferred effective potential (per galaxy).",
    )
    ap.add_argument(
        "--six-panel",
        action="store_true",
        help="Render a 2x3 combined figure: (rotation, potential, dyed) on top; (3D proxy, orbits, residuals) on bottom.",
    )

    ap.add_argument(
        "--q-override",
        choices=["none", "q_est"],
        default="none",
        help=(
            "Override the toy-model amplitude used for v_model/g_extra. "
            "q_est swaps the fitted q_best for the robust outer estimator from q_est.csv."
        ),
    )
    ap.add_argument(
        "--summary",
        type=str,
        default="",
        help="Path to summary.csv (required for --q-override=q_est).",
    )
    ap.add_argument(
        "--q-est",
        type=str,
        default="",
        help="Path to q_est.csv (required for --q-override=q_est).",
    )
    ap.add_argument(
        "--orbit-turns",
        type=float,
        default=2.0,
        help="Number of approximate circular periods to integrate for the orbit map.",
    )
    ap.add_argument(
        "--orbit-steps-per-turn",
        type=int,
        default=400,
        help="Integration steps per nominal circular period (orbit map).",
    )
    ap.add_argument(
        "--surface-z-exag",
        type=float,
        default=1.0,
        help=(
            "Multiplier applied to the proxy height of the 3D surface (in kpc). "
            "This is applied uniformly across all galaxies."
        ),
    )
    ap.add_argument(
        "--surface-height-mode",
        choices=["manual", "phi_over_c2", "accel_over_a0"],
        default="manual",
        help=(
            "How to map the inferred field into a 3D surface height (z) in kpc. "
            "manual: z_max set by --surface-height-kpc or --surface-height-frac; "
            "phi_over_c2: height ~ (\u0394\u03a6/c^2)\u00d7R_plot (physically tiny); "
            "accel_over_a0: height ~ \u222b(g/a0)dR (kpc-scale proxy)."
        ),
    )
    ap.add_argument(
        "--surface-height-norm",
        choices=["per_galaxy", "match_color"],
        default="per_galaxy",
        help=(
            "How to normalize the 3D height field before mapping to kpc height in manual mode. "
            "per_galaxy: each galaxy uses its own depth scale (helps the surface fill the frame); "
            "match_color: use the same normalization as the dyed color field (e.g., global)."
        ),
    )
    ap.add_argument(
        "--surface-color-norm",
        choices=["auto", "fixed01"],
        default="auto",
        help=(
            "How to map normalized depth values to colors on the 3D surface. "
            "auto: per-galaxy contrast (matches 2D imshow default; avoids near-black dwarfs under global scaling); "
            "fixed01: fixed 0..1 mapping (strictly comparable across galaxies when fabric_norm=global)."
        ),
    )
    ap.add_argument(
        "--surface-height-kpc",
        type=float,
        default=0.0,
        help=(
            "Set the 3D surface max height (z_max) explicitly in kpc. "
            "If >0, this overrides --surface-height-frac."
        ),
    )
    ap.add_argument(
        "--surface-height-frac",
        type=float,
        default=0.25,
        help=(
            "Set the 3D surface max height as a fraction of R_plot (z_max = frac * R_plot). "
            "Used when --surface-height-kpc <= 0."
        ),
    )
    args = ap.parse_args(argv)

    galaxy_dir = args.galaxy_dir
    out_dir = args.out_dir

    q_best_map: dict[str, float] = {}
    q_est_map: dict[str, float] = {}
    if str(args.q_override) == "q_est":
        if not args.summary:
            raise SystemExit("--q-override=q_est requires --summary <summary.csv>")
        if not args.q_est:
            raise SystemExit("--q-override=q_est requires --q-est <q_est.csv>")
        q_best_map = _read_q_best_map(str(args.summary))
        q_est_map = _read_q_est_map(str(args.q_est))

    csv_paths = _iter_csv_files(galaxy_dir)
    if args.only:
        wanted = {s.strip() for s in str(args.only).split(",") if s.strip()}
        if wanted:
            csv_paths = [p for p in csv_paths if os.path.splitext(os.path.basename(p))[0] in wanted]
    if args.max_galaxies and args.max_galaxies > 0:
        csv_paths = csv_paths[: args.max_galaxies]

    if not csv_paths:
        raise SystemExit(f"No galaxy CSVs found in {galaxy_dir}")

    os.makedirs(out_dir, exist_ok=True)
    out_png_dir = os.path.join(out_dir, "png")
    os.makedirs(out_png_dir, exist_ok=True)
    out_3d_dir = os.path.join(out_dir, "png_3d")
    if args.make_3d:
        os.makedirs(out_3d_dir, exist_ok=True)
    out_orbit_dir = os.path.join(out_dir, "png_orbits")
    if args.make_orbit_map:
        os.makedirs(out_orbit_dir, exist_ok=True)

    curves: List[GalaxyCurve] = []
    for p in csv_paths:
        curve = _read_curve_csv(p)
        if str(args.q_override) == "q_est":
            q_best = q_best_map.get(curve.name, float("nan"))
            q_new = q_est_map.get(curve.name, float("nan"))
            _apply_q_override_inplace(curve, q_best_kms2=q_best, q_new_kms2=q_new)
        curves.append(curve)

    global_r_max_kpc: Optional[float] = None
    if args.fabric_extent == "global_max":
        rmax_list: List[float] = []
        for c in curves:
            rr, _ = _sanitize_monotonic_radius(c.r_kpc, c.vobs_kms)
            if rr.size:
                rmax_list.append(float(np.max(rr)))
        if rmax_list:
            global_r_max_kpc = float(np.max(rmax_list))
            print(f"Global max radius: {global_r_max_kpc:.6g} kpc")

    fixed_r_max_kpc: Optional[float] = None
    if args.fabric_extent == "fixed":
        if not np.isfinite(args.fixed_rmax_kpc) or float(args.fixed_rmax_kpc) <= 0:
            raise SystemExit("--fixed-rmax-kpc must be > 0 when --fabric-extent=fixed")
        fixed_r_max_kpc = float(args.fixed_rmax_kpc)

    global_fabric_scale: Optional[float] = None
    if args.fabric_norm == "global":
        global_fabric_scale = _compute_global_fabric_scale(curves, percentile=float(args.global_percentile))
        print(f"Global fabric scale (p={args.global_percentile:g}%): {global_fabric_scale:.6g} km^2/s^2")

    pdf_pages: Optional[PdfPages] = None
    if args.make_pdf:
        pdf_path = os.path.join(out_dir, "dyed_spacetime_pages.pdf")
        pdf_pages = PdfPages(pdf_path)

    try:
        for i, curve in enumerate(curves, start=1):
            out_png = os.path.join(out_png_dir, f"{curve.name}.png")
            fig = render_galaxy_figure(
                curve,
                out_png_path=out_png,
                n_r=args.n_r,
                n_theta=args.n_theta,
                img_n=args.img_n,
                fabric_norm=args.fabric_norm,
                global_fabric_scale=global_fabric_scale,
                fabric_extent=args.fabric_extent,
                global_r_max_kpc=global_r_max_kpc,
                fixed_r_max_kpc=fixed_r_max_kpc,
                show_phi_uncert=not args.no_phi_uncert,
                imshow_interpolation=args.interp,
                out_dpi=args.dpi,
                six_panel=bool(args.six_panel),
                surface_height_mode=str(args.surface_height_mode),
                surface_height_norm=str(args.surface_height_norm),
                surface_color_norm=str(args.surface_color_norm),
                surface_height_kpc=float(args.surface_height_kpc),
                surface_height_frac=float(args.surface_height_frac),
                surface_z_exag=float(args.surface_z_exag),
                orbit_turns=float(args.orbit_turns),
                orbit_steps_per_turn=int(args.orbit_steps_per_turn),
            )
            if pdf_pages is not None:
                pdf_pages.savefig(fig, dpi=int(args.dpi))
            plt.close(fig)

            if args.make_3d:
                out_3d = os.path.join(out_3d_dir, f"{curve.name}_3d.png")
                render_fabric_surface_3d(
                    curve,
                    out_3d,
                    img_n=max(140, args.img_n // 2),
                    fabric_norm=args.fabric_norm,
                    global_fabric_scale=global_fabric_scale,
                    fabric_extent=args.fabric_extent,
                    global_r_max_kpc=global_r_max_kpc,
                    fixed_r_max_kpc=fixed_r_max_kpc,
                    surface_height_mode=str(args.surface_height_mode),
                    surface_height_norm=str(args.surface_height_norm),
                    surface_color_norm=str(args.surface_color_norm),
                    surface_height_kpc=float(args.surface_height_kpc),
                    surface_height_frac=float(args.surface_height_frac),
                    z_exaggeration=float(args.surface_z_exag),
                    out_dpi=args.dpi,
                )

            if args.make_orbit_map:
                out_orbit = os.path.join(out_orbit_dir, f"{curve.name}_orbits.png")
                render_orbit_map(
                    curve,
                    out_orbit,
                    orbit_turns=float(args.orbit_turns),
                    steps_per_turn=int(args.orbit_steps_per_turn),
                    out_dpi=args.dpi,
                )

            if i % 25 == 0:
                print(f"Rendered {i}/{len(curves)}")
    finally:
        if pdf_pages is not None:
            pdf_pages.close()

    if args.make_contact:
        contact_path = os.path.join(out_dir, "dyed_spacetime_contact.pdf")
        _render_contact_sheet(
            curves,
            contact_path,
            img_n=max(160, args.img_n // 2),
            fabric_norm=args.fabric_norm,
            global_fabric_scale=global_fabric_scale,
            fabric_extent=args.fabric_extent,
            global_r_max_kpc=global_r_max_kpc,
            fixed_r_max_kpc=fixed_r_max_kpc,
            imshow_interpolation=args.interp,
            out_dpi=args.dpi,
        )

    print(f"Done. Output in: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
