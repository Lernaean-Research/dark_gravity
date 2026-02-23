"""SPARC rotmod runner for the Spacetime-Mechanics auxiliary edge-response toy model.

Purpose
-------
This script wires the existing auxiliary-field "edge-triggered" phenomenology into
real SPARC rotation-curve *mass model* inputs ("rotmod" files).

We intentionally keep this runner:
- dependency-free (stdlib only)
- transparent (every transformation is explicit)
- reproducible (deterministic fits; CSV outputs)

Data model (SPARC rotmod)
------------------------
Each file contains columns (see header in file):
  Rad[kpc], Vobs[km/s], errV[km/s], Vgas[km/s], Vdisk[km/s], Vbul[km/s], ...

The baryonic model velocity is constructed as:
  Vbar^2(R) = Vgas^2 + (Upsilon_disk) * Vdisk^2 + (Upsilon_bul) * Vbul^2

This follows the common SPARC convention that the disk/bulge template curves are
provided for a reference mass-to-light ratio and can be rescaled.

Auxiliary edge-response model
-----------------------------
We treat the galaxy midplane dynamics as a 1D radial effective problem in R.
Define baryonic acceleration:
  g_bar(R) = Vbar^2(R) / R
Units: (km/s)^2/kpc.

Define a transition radius R_t where g_bar(R_t) ~ a0.

Define an auxiliary field chi with effective 2D radial Poisson operator:
  (1/R) d/dR ( R dchi/dR ) = S(R)
where S is a narrow bump centered at R_t with width sigma.

Let u(R) = R chi'(R). Then u'(R) = R S(R).
If S is normalized so that ∫_0^∞ R S(R) dR = 1, then for R beyond the bump
region: u(R) -> 1 and chi'(R) -> 1/R.

We couple chi' into the physical acceleration as:
  g_tot(R) = g_bar(R) + Q * chi'_unit(R)
where chi'_unit is the normalized (unit-charge) solution and Q has units of
(km/s)^2 (so that at large R, g_extra ~ Q/R and V_extra^2 -> Q).

Fit
---
For each galaxy we fit a single non-negative parameter Q by minimizing chi^2:
  chi^2(Q) = Σ_i ((Vmodel(R_i; Q) - Vobs_i) / errV_i)^2
where Vmodel = sqrt(g_tot * R).

Outputs
-------
Per galaxy:
  out_dir/galaxies/<galaxy>.csv  (R, Vobs, Verr, Vbar, Vmodel, gbar, gextra, gtot)
Summary table:
  out_dir/summary.csv

Methodology is documented in toy_models/SPARC_ROTMod_METHODOLOGY.md.

Usage
-----
Example (read rotmod files in-place, no copying):
    ./.venv/Scripts/python.exe toy_models/sparc_rotmod_runner.py --rotmod-dir "D:/#Documents/#Physics/TPT Paper/Rotmod_LTG" --out-dir toy_models/out_sparc_runs --max-galaxies 10

"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from typing import Iterable


A0_SI_DEFAULT = 1.2e-10  # m/s^2
KPC_IN_M = 3.085677581491367e19
MS2_PER_KMS2_PER_KPC = 1e6 / KPC_IN_M  # (km/s)^2/kpc -> m/s^2


def a0_to_kms2_per_kpc(a0_si: float) -> float:
    """Convert a0 from m/s^2 to (km/s)^2/kpc."""
    return a0_si / MS2_PER_KMS2_PER_KPC


@dataclass(frozen=True)
class RotmodRow:
    r_kpc: float
    vobs: float
    e_vobs: float
    vgas: float
    vdisk: float
    vbul: float


@dataclass(frozen=True)
class FitResult:
    galaxy: str
    n: int
    q_best: float
    chi2: float
    chi2_red: float
    r_t_kpc: float
    r_near_half_rt_kpc: float
    frac_gas_half_rt: float
    frac_disk_half_rt: float
    frac_bul_half_rt: float
    r_near_rt_kpc: float
    frac_gas_rt: float
    frac_disk_rt: float
    frac_bul_rt: float
    frac_bul_peak: float
    r_bul_peak_kpc: float
    gbar_inner: float
    gbar_rt: float
    gbar_half_rt: float
    gbar_1kpc: float
    gbar_2kpc: float
    s_in: float
    vobs_outer: float
    outer_resid_mean: float
    outer_resid_rms: float
    outer_chi2: float


@dataclass(frozen=True)
class SparcMeta:
    galaxy: str
    T: float
    D_mpc: float
    e_D_mpc: float
    Inc_deg: float
    e_Inc_deg: float
    L36_1e9solLum: float
    e_L36_1e9solLum: float
    Reff_kpc: float
    SBeff_solLum_pc2: float
    Rdisk_kpc: float
    SBdisk_solLum_pc2: float
    MHI_1e9solMass: float
    RHI_kpc: float
    Vflat_kms: float
    e_Vflat_kms: float
    Q_flag: float


def iter_rotmod_rows(path: str) -> Iterable[RotmodRow]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            r, vobs, ev, vgas, vdisk, vbul = (float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5]))
            yield RotmodRow(r, vobs, ev, vgas, vdisk, vbul)


def _parse_fixed_width_float(s: str) -> float:
    s = s.strip()
    if not s:
        return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def _parse_fixed_width_int(s: str) -> float:
    s = s.strip()
    if not s:
        return float("nan")
    try:
        return float(int(s))
    except ValueError:
        return float("nan")


def normalize_galaxy_name(name: str) -> str:
    # Match SPARC conventions: remove spaces, upper-case.
    return "".join(ch for ch in name.strip().upper() if ch != " ")


def load_sparc_mrt_table(path: str) -> dict[str, SparcMeta]:
    """Load SPARC Table 1 metadata from the .mrt file (fixed-width format).

    This joins convenient composition / overdensity proxies (e.g., SBdisk, MHI)
    onto the rotmod-derived phenomenology.
    """

    meta: dict[str, SparcMeta] = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            # Skip the long byte-by-byte description.
            if s.startswith("Title:") or s.startswith("Authors:") or s.startswith("Table:"):
                continue
            if s.startswith("Byte-by-byte") or s.startswith("Bytes") or s.startswith("Format"):
                continue
            if s.startswith("Note") or s.startswith("---") or s.startswith("===") or s.startswith("***"):
                continue

            parts = s.split()
            # Expected columns (Table 1):
            # Galaxy, T, D, e_D, f_D, Inc, e_Inc, L36, e_L36, Reff, SBeff, Rdisk, SBdisk,
            # MHI, RHI, Vflat, e_Vflat, Q, Ref.
            if len(parts) < 18:
                continue

            galaxy = parts[0]
            d_mpc = _parse_fixed_width_float(parts[2])
            if not math.isfinite(d_mpc):
                continue

            sm = SparcMeta(
                galaxy=galaxy,
                T=_parse_fixed_width_int(parts[1]),
                D_mpc=d_mpc,
                e_D_mpc=_parse_fixed_width_float(parts[3]),
                Inc_deg=_parse_fixed_width_float(parts[5]),
                e_Inc_deg=_parse_fixed_width_float(parts[6]),
                L36_1e9solLum=_parse_fixed_width_float(parts[7]),
                e_L36_1e9solLum=_parse_fixed_width_float(parts[8]),
                Reff_kpc=_parse_fixed_width_float(parts[9]),
                SBeff_solLum_pc2=_parse_fixed_width_float(parts[10]),
                Rdisk_kpc=_parse_fixed_width_float(parts[11]),
                SBdisk_solLum_pc2=_parse_fixed_width_float(parts[12]),
                MHI_1e9solMass=_parse_fixed_width_float(parts[13]),
                RHI_kpc=_parse_fixed_width_float(parts[14]),
                Vflat_kms=_parse_fixed_width_float(parts[15]),
                e_Vflat_kms=_parse_fixed_width_float(parts[16]),
                Q_flag=_parse_fixed_width_int(parts[17]),
            )
            meta[normalize_galaxy_name(galaxy)] = sm

    return meta


def gaussian_bump(r: float, center: float, sigma: float) -> float:
    z = (r - center) / max(sigma, 1e-12)
    return math.exp(-0.5 * z * z)


def trapz(xs: list[float], ys: list[float]) -> float:
    s = 0.0
    for i in range(1, len(xs)):
        dx = xs[i] - xs[i - 1]
        s += 0.5 * dx * (ys[i] + ys[i - 1])
    return s


def chi_prime_unit(rs: list[float], r_t: float, sigma: float) -> list[float]:
    """Return chi'(R) for unit integrated source (∫ R S dR = 1).

    Implements the same cumulative-trapezoid construction as aux_field_boundary_layer_2d.py,
    but normalizes to unit "charge".
    """

    s0 = [gaussian_bump(r, r_t, sigma) for r in rs]
    i0 = trapz(rs, [r * s for r, s in zip(rs, s0)])
    if i0 <= 0.0:
        return [0.0 for _ in rs]

    # S normalized such that ∫ r S dr = 1
    S = [s / i0 for s in s0]

    # u'(r) = r S(r), u(0)=0
    u = [0.0] * len(rs)
    for i in range(1, len(rs)):
        r0, r1 = rs[i - 1], rs[i]
        f0 = r0 * S[i - 1]
        f1 = r1 * S[i]
        u[i] = u[i - 1] + 0.5 * (r1 - r0) * (f0 + f1)

    return [u_i / max(r, 1e-30) for u_i, r in zip(u, rs)]


def build_baryons(rows: list[RotmodRow], ups_disk: float, ups_bul: float) -> tuple[list[float], list[float], list[float], list[float]]:
    rs = [r.r_kpc for r in rows]
    vobs = [r.vobs for r in rows]
    ev = [max(r.e_vobs, 1e-9) for r in rows]

    vbar2 = []
    vbar = []
    gbar = []
    for r in rows:
        v2 = (r.vgas * r.vgas) + ups_disk * (r.vdisk * r.vdisk) + ups_bul * (r.vbul * r.vbul)
        vbar2.append(v2)
        vbar.append(math.sqrt(max(v2, 0.0)))
        gbar.append(v2 / max(r.r_kpc, 1e-12))

    return rs, vobs, ev, vbar, gbar


def _nearest_index(rs: list[float], target: float) -> int:
    if not rs:
        return -1
    return min(range(len(rs)), key=lambda i: abs(rs[i] - target))


def _component_fractions_at(rows: list[RotmodRow], idx: int, ups_disk: float, ups_bul: float) -> tuple[float, float, float]:
    if idx < 0 or idx >= len(rows):
        return float("nan"), float("nan"), float("nan")
    gas2 = rows[idx].vgas * rows[idx].vgas
    disk2 = ups_disk * (rows[idx].vdisk * rows[idx].vdisk)
    bul2 = ups_bul * (rows[idx].vbul * rows[idx].vbul)
    vbar2 = gas2 + disk2 + bul2
    if vbar2 <= 0.0:
        return float("nan"), float("nan"), float("nan")
    return gas2 / vbar2, disk2 / vbar2, bul2 / vbar2


def _bulge_fraction_peak(rows: list[RotmodRow], ups_disk: float, ups_bul: float) -> tuple[float, float]:
    best_frac = float("nan")
    best_r = float("nan")
    for i in range(len(rows)):
        gas2 = rows[i].vgas * rows[i].vgas
        disk2 = ups_disk * (rows[i].vdisk * rows[i].vdisk)
        bul2 = ups_bul * (rows[i].vbul * rows[i].vbul)
        vbar2 = gas2 + disk2 + bul2
        if vbar2 <= 0.0:
            continue
        frac = bul2 / vbar2
        if (not math.isfinite(best_frac)) or frac > best_frac:
            best_frac = frac
            best_r = rows[i].r_kpc
    return best_frac, best_r


def _interp_loglog(x: float, xs: list[float], ys: list[float]) -> float:
    """Log-log interpolate y(x) from sampled (xs, ys).

    - xs must be strictly increasing and positive.
    - ys must be positive; values are clamped to a small floor.

    Returns NaN if x is outside the sampled range.
    """

    if not xs:
        return float("nan")
    if x < xs[0] or x > xs[-1] or x <= 0.0:
        return float("nan")

    # Find bracketing interval
    lo = 0
    hi = len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid

    x0, x1 = xs[lo], xs[hi]
    y0 = max(ys[lo], 1e-60)
    y1 = max(ys[hi], 1e-60)
    if x1 <= x0:
        return float("nan")
    t = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
    return math.exp(math.log(y0) + t * (math.log(y1) - math.log(y0)))


def _inner_log_slope(rs: list[float], gbar: list[float], start_idx: int = 1, end_idx: int = 5) -> float:
    """Estimate inner slope s_in = d ln gbar / d ln r over a small inner window.

    Uses an unweighted least-squares fit in log-log space. Returns NaN if not enough
    valid points.
    """

    n = len(rs)
    if n < 3:
        return float("nan")

    i0 = max(0, start_idx)
    i1 = min(n - 1, end_idx)
    if i1 - i0 < 2:
        return float("nan")

    xs = []
    ys = []
    for i in range(i0, i1 + 1):
        r = rs[i]
        g = gbar[i]
        if r > 0.0 and g > 0.0:
            xs.append(math.log(r))
            ys.append(math.log(g))
    if len(xs) < 3:
        return float("nan")

    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    sxx = sum((x - x_mean) ** 2 for x in xs)
    if sxx <= 0.0:
        return float("nan")
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    return sxy / sxx


def estimate_transition_radius(rs: list[float], gbar: list[float], a0: float) -> float:
    """Estimate R_t where gbar ~ a0 via log-linear interpolation.

    If gbar does not cross a0 within data range, returns a boundary value.
    """

    # Find indices where sign changes in log(gbar/a0).
    vals = [math.log(max(g / a0, 1e-60)) for g in gbar]

    for i in range(1, len(rs)):
        if vals[i - 1] >= 0.0 and vals[i] <= 0.0:
            # Interpolate in log space between (r_{i-1}, vals_{i-1}) and (r_i, vals_i)
            x0, x1 = math.log(rs[i - 1]), math.log(rs[i])
            y0, y1 = vals[i - 1], vals[i]
            if abs(y1 - y0) < 1e-12:
                return math.sqrt(rs[i - 1] * rs[i])
            t = (0.0 - y0) / (y1 - y0)
            return math.exp(x0 + t * (x1 - x0))

    # No crossing: pick closest point
    best_i = min(range(len(rs)), key=lambda k: abs(vals[k]))
    return rs[best_i]


def chi2_for_q(q: float, rs: list[float], vobs: list[float], ev: list[float], gbar: list[float], chi_p_unit: list[float]) -> float:
    s = 0.0
    for r, vo, e, gb, cp in zip(rs, vobs, ev, gbar, chi_p_unit):
        gtot = gb + q * cp
        vmodel = math.sqrt(max(gtot * r, 0.0))
        dz = (vmodel - vo) / e
        s += dz * dz
    return s


def golden_section_minimize(f, a: float, b: float, tol: float = 1e-6, max_iter: int = 120) -> tuple[float, float]:
    """Minimize f on [a, b] using golden-section search."""
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    fc = f(c)
    fd = f(d)

    for _ in range(max_iter):
        if abs(b - a) < tol * (1.0 + abs(a) + abs(b)):
            break
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = f(d)

    x = 0.5 * (a + b)
    return x, f(x)


def fit_galaxy(galaxy: str, rows: list[RotmodRow], ups_disk: float, ups_bul: float, sigma_kpc: float, a0: float) -> tuple[FitResult, list[tuple]]:
    rs, vobs, ev, vbar, gbar = build_baryons(rows, ups_disk, ups_bul)

    r_t = estimate_transition_radius(rs, gbar, a0)
    chi_p_u = chi_prime_unit(rs, r_t, sigma_kpc)

    vmax = max(vobs) if vobs else 0.0
    q_hi = max(10.0, 2.0 * vmax * vmax)  # generous bound

    def f(q: float) -> float:
        return chi2_for_q(q, rs, vobs, ev, gbar, chi_p_u)

    q_best, chi2 = golden_section_minimize(f, 0.0, q_hi)

    dof = max(len(rs) - 1, 1)
    chi2_red = chi2 / dof

    # Diagnostics / robust summary proxies
    gbar_inner = gbar[0] if gbar else float("nan")
    gbar_rt = _interp_loglog(r_t, rs, gbar)
    gbar_half_rt = _interp_loglog(0.5 * r_t, rs, gbar)
    gbar_1kpc = _interp_loglog(1.0, rs, gbar)
    gbar_2kpc = _interp_loglog(2.0, rs, gbar)
    s_in = _inner_log_slope(rs, gbar)

    # Composition fractions (gas/disk/bulge) evaluated near 0.5 R_t and R_t.
    idx_half = _nearest_index(rs, 0.5 * r_t)
    idx_rt = _nearest_index(rs, r_t)
    frac_gas_half, frac_disk_half, frac_bul_half = _component_fractions_at(rows, idx_half, ups_disk, ups_bul)
    frac_gas_rt, frac_disk_rt, frac_bul_rt = _component_fractions_at(rows, idx_rt, ups_disk, ups_bul)
    r_near_half = rs[idx_half] if idx_half >= 0 else float("nan")
    r_near_rt = rs[idx_rt] if idx_rt >= 0 else float("nan")
    frac_bul_peak, r_bul_peak = _bulge_fraction_peak(rows, ups_disk, ups_bul)

    # crude outer Vobs metric: median of last 5 points (robust to a single outlier)
    tail = vobs[-5:] if len(vobs) >= 5 else vobs
    tail_sorted = sorted(tail)
    vobs_outer = tail_sorted[len(tail_sorted) // 2] if tail_sorted else 0.0

    # Outer-region residual diagnostics (tests whether edge-response matches outskirts)
    outer_idx = [i for i, r in enumerate(rs) if r >= 2.0 * r_t]
    outer_resids = []
    outer_chi2 = 0.0
    for i in outer_idx:
        r = rs[i]
        gtot = gbar[i] + q_best * chi_p_u[i]
        vmodel = math.sqrt(max(gtot * r, 0.0))
        z = (vmodel - vobs[i]) / ev[i]
        outer_resids.append(z)
        outer_chi2 += z * z
    if outer_resids:
        outer_resid_mean = sum(outer_resids) / len(outer_resids)
        outer_resid_rms = math.sqrt(sum(z * z for z in outer_resids) / len(outer_resids))
    else:
        outer_resid_mean = float("nan")
        outer_resid_rms = float("nan")

    # Build per-point output rows
    out_rows = []
    for row, r, vo, e, vb, gb, cpu in zip(rows, rs, vobs, ev, vbar, gbar, chi_p_u):
        gextra = q_best * cpu
        gtot = gb + gextra
        vmodel = math.sqrt(max(gtot * r, 0.0))
        gas2 = row.vgas * row.vgas
        disk2 = ups_disk * (row.vdisk * row.vdisk)
        bul2 = ups_bul * (row.vbul * row.vbul)
        vbar2 = gas2 + disk2 + bul2
        if vbar2 > 0.0:
            frac_gas = gas2 / vbar2
            frac_disk = disk2 / vbar2
            frac_bul = bul2 / vbar2
        else:
            frac_gas = float("nan")
            frac_disk = float("nan")
            frac_bul = float("nan")
        out_rows.append((r, vo, e, vb, vmodel, gb, gextra, gtot, row.vgas, row.vdisk, row.vbul, frac_gas, frac_disk, frac_bul))

    return (
        FitResult(
            galaxy=galaxy,
            n=len(rs),
            q_best=q_best,
            chi2=chi2,
            chi2_red=chi2_red,
            r_t_kpc=r_t,
            r_near_half_rt_kpc=r_near_half,
            frac_gas_half_rt=frac_gas_half,
            frac_disk_half_rt=frac_disk_half,
            frac_bul_half_rt=frac_bul_half,
            r_near_rt_kpc=r_near_rt,
            frac_gas_rt=frac_gas_rt,
            frac_disk_rt=frac_disk_rt,
            frac_bul_rt=frac_bul_rt,
            frac_bul_peak=frac_bul_peak,
            r_bul_peak_kpc=r_bul_peak,
            gbar_inner=gbar_inner,
            gbar_rt=gbar_rt,
            gbar_half_rt=gbar_half_rt,
            gbar_1kpc=gbar_1kpc,
            gbar_2kpc=gbar_2kpc,
            s_in=s_in,
            vobs_outer=vobs_outer,
            outer_resid_mean=outer_resid_mean,
            outer_resid_rms=outer_resid_rms,
            outer_chi2=outer_chi2,
        ),
        out_rows,
    )


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run auxiliary edge-response model fits on SPARC rotmod files")
    p.add_argument("--rotmod-dir", required=True, help="Directory containing *_rotmod.dat files")
    p.add_argument("--out-dir", required=True, help="Output directory for per-galaxy and summary CSV")
    p.add_argument("--sparc-mrt", default="", help="Optional path to SPARC Table1 .mrt file (adds metadata columns to summary)")
    p.add_argument("--max-galaxies", type=int, default=0, help="If >0, limit number of galaxies processed")
    p.add_argument("--sigma-kpc", type=float, default=2.0, help="Gaussian source width sigma (kpc)")
    p.add_argument("--ups-disk", type=float, default=0.5, help="Disk mass-to-light scaling")
    p.add_argument("--ups-bul", type=float, default=0.7, help="Bulge mass-to-light scaling")
    p.add_argument("--a0-ms2", type=float, default=A0_SI_DEFAULT, help="a0 in m/s^2")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    a0 = a0_to_kms2_per_kpc(args.a0_ms2)

    rotmod_dir = args.rotmod_dir
    out_dir = args.out_dir

    sparc_meta: dict[str, SparcMeta] = {}
    if args.sparc_mrt:
        sparc_meta = load_sparc_mrt_table(args.sparc_mrt)

    ensure_dir(out_dir)
    galaxies_dir = os.path.join(out_dir, "galaxies")
    ensure_dir(galaxies_dir)

    files = [fn for fn in os.listdir(rotmod_dir) if fn.endswith("_rotmod.dat")]
    files.sort()
    if args.max_galaxies and args.max_galaxies > 0:
        files = files[: args.max_galaxies]

    summary_path = os.path.join(out_dir, "summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as sf:
        sw = csv.writer(sf)
        header = [
            "galaxy",
            "n",
            "sigma_kpc",
            "ups_disk",
            "ups_bul",
            "a0_kms2_per_kpc",
            "r_t_kpc",
            "r_near_half_rt_kpc",
            "frac_gas_half_rt",
            "frac_disk_half_rt",
            "frac_bul_half_rt",
            "r_near_rt_kpc",
            "frac_gas_rt",
            "frac_disk_rt",
            "frac_bul_rt",
            "frac_bul_peak",
            "r_bul_peak_kpc",
            "q_best_kms2",
            "v_extra_asym_kms",
            "chi2",
            "chi2_red",
            "gbar_inner_kms2_per_kpc",
            "gbar_rt_kms2_per_kpc",
            "gbar_half_rt_kms2_per_kpc",
            "gbar_1kpc_kms2_per_kpc",
            "gbar_2kpc_kms2_per_kpc",
            "s_in_dlng_dlnr",
            "vobs_outer_kms",
            "outer_resid_mean_z",
            "outer_resid_rms_z",
            "outer_chi2",
        ]

        if sparc_meta:
            header.extend([
                "sparc_T",
                "sparc_D_mpc",
                "sparc_e_D_mpc",
                "sparc_Inc_deg",
                "sparc_e_Inc_deg",
                "sparc_L36_1e9solLum",
                "sparc_e_L36_1e9solLum",
                "sparc_Reff_kpc",
                "sparc_SBeff_solLum_pc2",
                "sparc_Rdisk_kpc",
                "sparc_SBdisk_solLum_pc2",
                "sparc_MHI_1e9solMass",
                "sparc_RHI_kpc",
                "sparc_Vflat_kms",
                "sparc_e_Vflat_kms",
                "sparc_Q_flag",
            ])

        sw.writerow(header)

        for fn in files:
            galaxy = fn.replace("_rotmod.dat", "")
            path = os.path.join(rotmod_dir, fn)
            rows = list(iter_rotmod_rows(path))
            if len(rows) < 3:
                continue

            fit, per_rows = fit_galaxy(
                galaxy,
                rows,
                ups_disk=args.ups_disk,
                ups_bul=args.ups_bul,
                sigma_kpc=args.sigma_kpc,
                a0=a0,
            )

            # Per-galaxy output
            gal_out = os.path.join(galaxies_dir, f"{galaxy}.csv")
            with open(gal_out, "w", newline="", encoding="utf-8") as gf:
                gw = csv.writer(gf)
                gw.writerow([
                    "r_kpc",
                    "vobs_kms",
                    "e_vobs_kms",
                    "vbar_kms",
                    "vmodel_kms",
                    "gbar_kms2_per_kpc",
                    "gextra_kms2_per_kpc",
                    "gtot_kms2_per_kpc",
                    "vgas_kms",
                    "vdisk_kms",
                    "vbul_kms",
                    "frac_gas",
                    "frac_disk",
                    "frac_bul",
                ])
                gw.writerows(per_rows)

            v_extra_asym = math.sqrt(max(fit.q_best, 0.0))

            out = [
                fit.galaxy,
                fit.n,
                args.sigma_kpc,
                args.ups_disk,
                args.ups_bul,
                a0,
                fit.r_t_kpc,
                fit.r_near_half_rt_kpc,
                fit.frac_gas_half_rt,
                fit.frac_disk_half_rt,
                fit.frac_bul_half_rt,
                fit.r_near_rt_kpc,
                fit.frac_gas_rt,
                fit.frac_disk_rt,
                fit.frac_bul_rt,
                fit.frac_bul_peak,
                fit.r_bul_peak_kpc,
                fit.q_best,
                v_extra_asym,
                fit.chi2,
                fit.chi2_red,
                fit.gbar_inner,
                fit.gbar_rt,
                fit.gbar_half_rt,
                fit.gbar_1kpc,
                fit.gbar_2kpc,
                fit.s_in,
                fit.vobs_outer,
                fit.outer_resid_mean,
                fit.outer_resid_rms,
                fit.outer_chi2,

            ]

            if sparc_meta:
                sm = sparc_meta.get(normalize_galaxy_name(galaxy))
                if sm is None:
                    out.extend([float("nan")] * 16)
                else:
                    out.extend([
                        sm.T,
                        sm.D_mpc,
                        sm.e_D_mpc,
                        sm.Inc_deg,
                        sm.e_Inc_deg,
                        sm.L36_1e9solLum,
                        sm.e_L36_1e9solLum,
                        sm.Reff_kpc,
                        sm.SBeff_solLum_pc2,
                        sm.Rdisk_kpc,
                        sm.SBdisk_solLum_pc2,
                        sm.MHI_1e9solMass,
                        sm.RHI_kpc,
                        sm.Vflat_kms,
                        sm.e_Vflat_kms,
                        sm.Q_flag,
                    ])

            sw.writerow(out)

    print("SPARC rotmod runner complete")
    print(f"Input rotmod dir: {rotmod_dir}")
    print(f"Output dir: {out_dir}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
