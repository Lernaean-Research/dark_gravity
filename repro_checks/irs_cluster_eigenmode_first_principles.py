#!/usr/bin/env python3
"""Standalone first-principles IRS cluster eigenmode toy model.

This script intentionally does not reuse the Stage III cumulative-mode shortcut.
It rebuilds the cluster-scale toy calculation from the constitutive ingredients:

1. Baryonic gravity from a multibody toy cluster analog dataset.
2. IRS ground mode activated by the local low-acceleration transition.
3. Higher eigenmodes generated source-by-source with geometry-derived eta.
4. Collective superposition evaluated directly from the source ensemble.

Outputs are deterministic and include provenance hashes so the toy model can be
rerun and audited as the cluster program evolves.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


G_KPC = 4.3009e-6
A0_KMS2 = 3702.813
G_SI = 6.67430e-11
M_SUN_KG = 1.98847e30
M_PER_KPC = 3.085677581491367e19
H0_KMS_MPC = 67.4
OMEGA_M = 0.315
OMEGA_L = 0.685
MPC_PER_KPC = 1.0e-3


@dataclass(frozen=True)
class ClusterAnchor:
    z: float
    m500_msun: float
    mbar_msun: float
    mgas_msun: float
    mstar_msun: float
    sigma_kms: float


@dataclass(frozen=True)
class SourceComponent:
    name: str
    kind: str
    mass_msun: float
    q1_kms2: float
    rt_kpc: float
    x_kpc: float
    y_kpc: float
    z_kpc: float
    scale_kpc: float
    diffuseness: float
    overlap: float
    eta_eff: float


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quantile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        raise ValueError("empty sequence")
    if q <= 0.0:
        return sorted_vals[0]
    if q >= 1.0:
        return sorted_vals[-1]
    index = q * (len(sorted_vals) - 1)
    low = int(math.floor(index))
    high = int(math.ceil(index))
    if low == high:
        return sorted_vals[low]
    weight = index - low
    return sorted_vals[low] * (1.0 - weight) + sorted_vals[high] * weight


def hubble_si(z: float) -> float:
    h0_si = H0_KMS_MPC * 1000.0 / (M_PER_KPC * 1000.0)
    return h0_si * math.sqrt(OMEGA_M * (1.0 + z) ** 3 + OMEGA_L)


def E_z(z: float) -> float:
    """Dimensionless Hubble rate E(z) = H(z)/H0 = sqrt(Omega_m*(1+z)^3 + Omega_L)."""
    return math.sqrt(OMEGA_M * (1.0 + z) ** 3 + OMEGA_L)


def critical_density_msun_per_kpc3(z: float) -> float:
    rho_si = 3.0 * hubble_si(z) ** 2 / (8.0 * math.pi * G_SI)
    return rho_si * (M_PER_KPC ** 3) / M_SUN_KG


def q1_kms2(mass_msun: float) -> float:
    return math.sqrt(max(G_KPC * mass_msun * A0_KMS2, 0.0))


def rt_kpc(mass_msun: float) -> float:
    return math.sqrt(max(G_KPC * mass_msun / A0_KMS2, 0.0))


def load_anchor(path: Path) -> ClusterAnchor:
    rows: List[Dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                z = float(row["redshift"])
                m500 = float(row["M500_Msun"])
                mbar = float(row["M_bar_Msun"])
                mgas = float(row["M_gas_Msun"])
                mstar = float(row["M_star_Msun"])
                sigma = float(row["sigma_kms"])
            except (KeyError, TypeError, ValueError):
                continue
            if min(z, m500, mbar, mgas, mstar, sigma) <= 0.0:
                continue
            rows.append(
                {
                    "z": z,
                    "m500": m500,
                    "mbar": mbar,
                    "mgas": mgas,
                    "mstar": mstar,
                    "sigma": sigma,
                }
            )
    if not rows:
        raise RuntimeError(f"No usable rows found in {path}")

    def med(key: str) -> float:
        return statistics.median(row[key] for row in rows)

    return ClusterAnchor(
        z=med("z"),
        m500_msun=med("m500"),
        mbar_msun=med("mbar"),
        mgas_msun=med("mgas"),
        mstar_msun=med("mstar"),
        sigma_kms=med("sigma"),
    )


def build_radius_mass_grid(
    mass_integrand,
    r_max_kpc: float,
    steps: int,
) -> Tuple[List[float], List[float]]:
    radii = [r_max_kpc * idx / steps for idx in range(steps + 1)]
    cumulative = [0.0]
    total = 0.0
    for idx in range(1, len(radii)):
        r0 = radii[idx - 1]
        r1 = radii[idx]
        rm = 0.5 * (r0 + r1)
        shell_mass = mass_integrand(rm) * (r1 - r0)
        total += shell_mass
        cumulative.append(total)
    if total <= 0.0:
        raise RuntimeError("Mass grid integral is non-positive")
    cumulative = [value / total for value in cumulative]
    return radii, cumulative


def interpolate_inverse_cdf(radii: Sequence[float], cdf: Sequence[float], q: float) -> float:
    q = min(max(q, 0.0), 1.0)
    for idx in range(1, len(cdf)):
        if cdf[idx] >= q:
            q0 = cdf[idx - 1]
            q1 = cdf[idx]
            r0 = radii[idx - 1]
            r1 = radii[idx]
            if q1 <= q0:
                return r1
            frac = (q - q0) / (q1 - q0)
            return r0 + frac * (r1 - r0)
    return radii[-1]


def fibonacci_direction(index: int, count: int) -> Tuple[float, float, float]:
    phi = (1.0 + math.sqrt(5.0)) * 0.5
    y = 1.0 - 2.0 * (index + 0.5) / count
    radius = math.sqrt(max(0.0, 1.0 - y * y))
    theta = 2.0 * math.pi * (index / phi)
    return radius * math.cos(theta), radius * math.sin(theta), y


def shell_directions(count: int) -> List[Tuple[float, float, float]]:
    return [fibonacci_direction(index, count) for index in range(count)]


def build_gas_nodes(
    anchor: ClusterAnchor,
    r500_kpc: float,
    gas_nodes: int,
) -> Tuple[List[Dict[str, float]], Dict[str, float]]:
    beta = 0.67
    rc_kpc = 0.12 * r500_kpc
    r_max_kpc = r500_kpc
    q1_total = q1_kms2(anchor.mgas_msun)
    rt_total = rt_kpc(anchor.mgas_msun)

    def shell_integrand(r_kpc: float) -> float:
        profile = (1.0 + (r_kpc / rc_kpc) ** 2) ** (-1.5 * beta)
        return 4.0 * math.pi * r_kpc * r_kpc * profile

    radii, cdf = build_radius_mass_grid(shell_integrand, r_max_kpc, 1200)
    nodes: List[Dict[str, float]] = []
    for idx in range(gas_nodes):
        q = (idx + 0.5) / gas_nodes
        radius = interpolate_inverse_cdf(radii, cdf, q)
        dx, dy, dz = fibonacci_direction(idx, gas_nodes)
        weight = 1.0 / gas_nodes
        shell_width = r_max_kpc / gas_nodes
        nodes.append(
            {
                "name": f"ICM_{idx + 1:02d}",
                "kind": "gas",
                "mass_msun": anchor.mgas_msun * weight,
                "q1_kms2": q1_total * weight,
                "rt_kpc": rt_total,
                "x_kpc": radius * dx,
                "y_kpc": radius * dy,
                "z_kpc": radius * dz,
                "scale_kpc": max(0.30 * shell_width, 0.45 * rc_kpc),
            }
        )
    return nodes, {"beta": beta, "rc_kpc": rc_kpc, "r_max_kpc": r_max_kpc}


def build_satellite_radii(r500_kpc: float, count: int) -> List[float]:
    concentration = 5.8
    rs_kpc = r500_kpc / concentration
    r_max_kpc = 1.4 * r500_kpc

    def shell_integrand(r_kpc: float) -> float:
        x = max(r_kpc / rs_kpc, 1.0e-8)
        density = 1.0 / (x * (1.0 + x) ** 2)
        return 4.0 * math.pi * r_kpc * r_kpc * density

    radii, cdf = build_radius_mass_grid(shell_integrand, r_max_kpc, 1000)
    return [interpolate_inverse_cdf(radii, cdf, (idx + 0.5) / count) for idx in range(count)]


def build_galaxy_sources(
    anchor: ClusterAnchor,
    r500_kpc: float,
    satellites: int,
    rng: random.Random,
) -> List[Dict[str, float]]:
    bcg_mass = 0.40 * anchor.mstar_msun
    remaining_stellar_mass = max(anchor.mstar_msun - bcg_mass, 0.0)
    weights = [math.exp(rng.gauss(0.0, 0.65)) for _ in range(satellites)]
    total_weight = sum(weights)
    radii = build_satellite_radii(r500_kpc, satellites)

    sources: List[Dict[str, float]] = [
        {
            "name": "BCG",
            "kind": "galaxy",
            "mass_msun": bcg_mass,
            "q1_kms2": q1_kms2(bcg_mass),
            "rt_kpc": rt_kpc(bcg_mass),
            "x_kpc": 0.0,
            "y_kpc": 0.0,
            "z_kpc": 0.0,
            "scale_kpc": 11.0,
        }
    ]

    for idx, radius in enumerate(radii):
        phi = rng.uniform(0.0, 2.0 * math.pi)
        cos_theta = rng.uniform(-1.0, 1.0)
        sin_theta = math.sqrt(max(0.0, 1.0 - cos_theta * cos_theta))
        mass = remaining_stellar_mass * weights[idx] / total_weight
        scale_kpc = 2.0 + 2.6 * (mass / 1.0e11) ** 0.35
        sources.append(
            {
                "name": f"GAL_{idx + 1:02d}",
                "kind": "galaxy",
                "mass_msun": mass,
                "q1_kms2": q1_kms2(mass),
                "rt_kpc": rt_kpc(mass),
                "x_kpc": radius * sin_theta * math.cos(phi),
                "y_kpc": radius * sin_theta * math.sin(phi),
                "z_kpc": radius * cos_theta,
                "scale_kpc": scale_kpc,
            }
        )
    return sources


def add_geometry_eta(source_rows: List[Dict[str, float]]) -> List[SourceComponent]:
    total_mass = sum(row["mass_msun"] for row in source_rows)
    completed: List[SourceComponent] = []
    for idx, row in enumerate(source_rows):
        overlap = 0.0
        for jdx, other in enumerate(source_rows):
            if idx == jdx:
                continue
            dx = row["x_kpc"] - other["x_kpc"]
            dy = row["y_kpc"] - other["y_kpc"]
            dz = row["z_kpc"] - other["z_kpc"]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            scale = max(0.5 * (row["rt_kpc"] + other["rt_kpc"]), 1.0)
            overlap += (other["mass_msun"] / total_mass) * math.exp(-distance / scale)

        diffuseness = min(row["scale_kpc"] / max(row["rt_kpc"], 1.0e-6), 2.20)
        driver = 1.55 * diffuseness + 4.20 * overlap
        eta_eff = 0.84 * (1.0 - math.exp(-driver))
        if row["kind"] == "galaxy":
            eta_eff *= 0.90
        eta_eff = min(max(eta_eff, 0.0), 0.84)

        completed.append(
            SourceComponent(
                name=row["name"],
                kind=row["kind"],
                mass_msun=row["mass_msun"],
                q1_kms2=row["q1_kms2"],
                rt_kpc=row["rt_kpc"],
                x_kpc=row["x_kpc"],
                y_kpc=row["y_kpc"],
                z_kpc=row["z_kpc"],
                scale_kpc=row["scale_kpc"],
                diffuseness=diffuseness,
                overlap=overlap,
                eta_eff=eta_eff,
            )
        )
    return completed


def beta_gas_enclosed_mass(r_kpc: float, total_mass_msun: float, rc_kpc: float, beta: float, rmax_kpc: float) -> float:
    steps = 500
    radii, cdf = build_radius_mass_grid(
        lambda rr: 4.0 * math.pi * rr * rr * (1.0 + (rr / rc_kpc) ** 2) ** (-1.5 * beta),
        rmax_kpc,
        steps,
    )
    if r_kpc <= 0.0:
        return 0.0
    if r_kpc >= rmax_kpc:
        return total_mass_msun
    for idx in range(1, len(radii)):
        if radii[idx] >= r_kpc:
            r0 = radii[idx - 1]
            r1 = radii[idx]
            f0 = cdf[idx - 1]
            f1 = cdf[idx]
            frac = (r_kpc - r0) / max(r1 - r0, 1.0e-9)
            return total_mass_msun * (f0 + frac * (f1 - f0))
    return total_mass_msun


def baryon_accel_components(
    r_kpc: float,
    eval_point_kpc: Tuple[float, float, float],
    radial_dir: Tuple[float, float, float],
    galaxy_sources: Sequence[SourceComponent],
    anchor: ClusterAnchor,
    gas_profile: Dict[str, float],
) -> Dict[str, float]:
    gas_mass = beta_gas_enclosed_mass(
        r_kpc,
        anchor.mgas_msun,
        gas_profile["rc_kpc"],
        gas_profile["beta"],
        gas_profile["r_max_kpc"],
    )
    gas_accel = 0.0 if r_kpc <= 0.0 else G_KPC * gas_mass / max(r_kpc * r_kpc, 1.0e-9)
    ex, ey, ez = radial_dir

    galaxy_accel_radial = 0.0
    px, py, pz = eval_point_kpc
    for source in galaxy_sources:
        dx = px - source.x_kpc
        dy = py - source.y_kpc
        dz = pz - source.z_kpc
        s2 = dx * dx + dy * dy + dz * dz + source.scale_kpc ** 2
        radial_projection = dx * ex + dy * ey + dz * ez
        galaxy_accel_radial += G_KPC * source.mass_msun * radial_projection / (s2 ** 1.5)

    return {
        "gas": gas_accel,
        "galaxy": galaxy_accel_radial,
        "total": gas_accel + galaxy_accel_radial,
        "gas_mass_enclosed_msun": gas_mass,
    }


def response_accel_by_mode(
    eval_point_kpc: Tuple[float, float, float],
    radial_dir: Tuple[float, float, float],
    sources: Sequence[SourceComponent],
    max_order: int,
) -> Tuple[List[float], List[float]]:
    by_mode = [0.0 for _ in range(max_order)]
    activation_values: List[float] = []
    px, py, pz = eval_point_kpc
    ex, ey, ez = radial_dir
    for source in sources:
        dx = px - source.x_kpc
        dy = py - source.y_kpc
        dz = pz - source.z_kpc
        s2 = dx * dx + dy * dy + dz * dz + source.scale_kpc ** 2
        s = math.sqrt(s2)
        gbar_local = G_KPC * source.mass_msun * math.sqrt(dx * dx + dy * dy + dz * dz) / (s2 ** 1.5)
        activation = 1.0 / (1.0 + (gbar_local / max(A0_KMS2, 1.0e-12)) ** 2)
        activation_values.append(activation)
        radial_projection = dx * ex + dy * ey + dz * ez
        by_mode[0] += activation * source.q1_kms2 * radial_projection / max(s2, 1.0e-12)
        for mode in range(2, max_order + 1):
            amplitude = activation * source.q1_kms2 * (source.eta_eff * source.rt_kpc) ** (mode - 1)
            by_mode[mode - 1] += amplitude * radial_projection / max(s ** (mode + 1), 1.0e-12)
    return by_mode, activation_values


def nfw_mass_enclosed(r_kpc: float, m500_msun: float, r500_kpc: float, concentration: float) -> float:
    rs_kpc = r500_kpc / concentration

    def f(x: float) -> float:
        return math.log(1.0 + x) - x / (1.0 + x)

    x = max(r_kpc / rs_kpc, 1.0e-9)
    c = concentration
    return m500_msun * f(x) / f(c)


def memory_lag_factor_linear_ramp(tau_myr: float, assembly_myr: float) -> float:
    """Return final-response fraction for dR/dt = (D-R)/tau with linear D(t)=t/T.

    For a source that ramps from 0 to full strength over assembly_myr, this gives
    the retained response fraction at the end of the ramp.
    """
    tau = max(tau_myr, 1.0e-6)
    t_asm = max(assembly_myr, 1.0e-6)
    factor = 1.0 - (tau / t_asm) * (1.0 - math.exp(-t_asm / tau))
    return min(max(factor, 0.0), 1.0)


def mode_memory_factor(
    mode_order: int,
    r_kpc: float,
    r500_kpc: float,
    enable_time_memory: bool,
    tau_mem_myr: float,
    assembly_time_myr: float,
    assembly_alpha: float,
    mode_tau_power: float,
    anchor_z: float = 0.0,
    ez_tau_power: float = 0.0,
    ez_ref_z: float = 0.2,
) -> float:
    if not enable_time_memory:
        return 1.0
    radius_ratio = max(r_kpc / max(r500_kpc, 1.0e-9), 1.0e-3)
    local_assembly_myr = assembly_time_myr * (radius_ratio ** assembly_alpha)
    # E(z) correction: tau_eff = tau_0 * E(z)^(-nu)
    # E(z) correction: tau_eff = tau_0 * (E(z)/E(z_ref))^(-nu)
    # At z < z_ref: ratio<1 -> tau_eff > tau_0 -> more lag -> lower closure (fixes over-closure).
    # At z > z_ref: ratio>1 -> tau_eff < tau_0 -> less lag -> higher closure (fixes under-closure).
    ez_factor = (E_z(anchor_z) / E_z(ez_ref_z)) ** (-ez_tau_power) if ez_tau_power != 0.0 else 1.0
    tau_mode = tau_mem_myr * ez_factor * (mode_order ** mode_tau_power)
    return memory_lag_factor_linear_ramp(tau_mode, local_assembly_myr)


def build_profile_rows(
    radii_kpc: Sequence[float],
    anchor: ClusterAnchor,
    sources: Sequence[SourceComponent],
    max_order: int,
    shell_direction_count: int,
    r500_kpc: float,
    gas_profile: Dict[str, float],
    enable_time_memory: bool,
    tau_mem_myr: float,
    assembly_time_myr: float,
    assembly_alpha: float,
    mode_tau_power: float,
    ez_tau_power: float = 0.0,
    ez_ref_z: float = 0.2,
) -> List[Dict[str, float]]:
    profile_rows: List[Dict[str, float]] = []
    galaxy_sources = [source for source in sources if source.kind == "galaxy"]
    concentration = 3.4
    directions = shell_directions(shell_direction_count)

    for r_kpc in radii_kpc:
        baryon_samples: List[Dict[str, float]] = []
        mode_samples: List[List[float]] = []
        activation_values: List[float] = []
        for direction in directions:
            ex, ey, ez = direction
            eval_point = (r_kpc * ex, r_kpc * ey, r_kpc * ez)
            baryon_samples.append(
                baryon_accel_components(
                    r_kpc=r_kpc,
                    eval_point_kpc=eval_point,
                    radial_dir=direction,
                    galaxy_sources=galaxy_sources,
                    anchor=anchor,
                    gas_profile=gas_profile,
                )
            )
            mode_accels, activ = response_accel_by_mode(
                eval_point_kpc=eval_point,
                radial_dir=direction,
                sources=sources,
                max_order=max_order,
            )
            mode_samples.append(mode_accels)
            activation_values.extend(activ)

        baryon = {
            key: statistics.fmean(sample[key] for sample in baryon_samples)
            for key in ["gas", "galaxy", "total", "gas_mass_enclosed_msun"]
        }
        mode_accels_static = [statistics.fmean(sample[idx] for sample in mode_samples) for idx in range(max_order)]
        mode_memory_factors = [
            mode_memory_factor(
                mode_order=idx + 1,
                r_kpc=r_kpc,
                r500_kpc=r500_kpc,
                enable_time_memory=enable_time_memory,
                tau_mem_myr=tau_mem_myr,
                assembly_time_myr=assembly_time_myr,
                assembly_alpha=assembly_alpha,
                mode_tau_power=mode_tau_power,
                anchor_z=anchor.z,
                ez_tau_power=ez_tau_power,
                ez_ref_z=ez_ref_z,
            )
            for idx in range(max_order)
        ]
        mode_accels = [mode_accels_static[idx] * mode_memory_factors[idx] for idx in range(max_order)]

        g_resp_ground = mode_accels[0]
        g_resp_higher = sum(mode_accels[1:])
        g_resp_total = sum(mode_accels)
        g_total_full = baryon["total"] + g_resp_total
        g_total_ground = baryon["total"] + g_resp_ground
        m_eff_bary = baryon["total"] * r_kpc * r_kpc / G_KPC
        m_eff_ground = g_total_ground * r_kpc * r_kpc / G_KPC
        m_eff_full = g_total_full * r_kpc * r_kpc / G_KPC
        m_obs = nfw_mass_enclosed(r_kpc, anchor.m500_msun, r500_kpc, concentration)
        profile_rows.append(
            {
                "r_kpc": r_kpc,
                "g_bar_total": baryon["total"],
                "g_bar_gas": baryon["gas"],
                "g_bar_galaxies": baryon["galaxy"],
                "g_resp_ground": g_resp_ground,
                "g_resp_higher": g_resp_higher,
                "g_resp_total": g_resp_total,
                "m_eff_bary_msun": m_eff_bary,
                "m_eff_ground_msun": m_eff_ground,
                "m_eff_full_msun": m_eff_full,
                "m_obs_analog_msun": m_obs,
                "closure_ground": m_eff_ground / m_obs,
                "closure_full": m_eff_full / m_obs,
                "higher_mode_fraction": 0.0 if abs(g_resp_total) < 1.0e-12 else g_resp_higher / g_resp_total,
                "mean_activation": statistics.mean(activation_values),
                "baryon_fraction_full": m_eff_bary / m_eff_full,
                "gas_mass_enclosed_msun": baryon["gas_mass_enclosed_msun"],
                "shell_directions": shell_direction_count,
                "time_memory_enabled": int(enable_time_memory),
                "memory_factor_mean": statistics.fmean(mode_memory_factors),
                "mode_1": mode_accels[0],
                **{f"memory_factor_mode_{idx + 1}": mode_memory_factors[idx] for idx in range(max_order)},
                **{f"mode_{idx + 1}": mode_accels[idx] for idx in range(1, max_order)},
            }
        )
    return profile_rows


def evaluate_gates(profile_rows: Sequence[Dict[str, float]], r500_kpc: float, anchor: ClusterAnchor) -> Dict[str, Dict[str, object]]:
    def nearest(radius: float) -> Dict[str, float]:
        return min(profile_rows, key=lambda row: abs(row["r_kpc"] - radius))

    row_half = nearest(0.5 * r500_kpc)
    row_r500 = nearest(r500_kpc)
    row_outer = nearest(1.4 * r500_kpc)

    sigma_pred = math.sqrt(max(G_KPC * row_r500["m_eff_full_msun"] / (3.0 * row_r500["r_kpc"]), 0.0))
    sigma_error = abs(sigma_pred - anchor.sigma_kms) / anchor.sigma_kms
    gates = {
        "higher_modes_non_negligible": {
            "value": row_r500["higher_mode_fraction"],
            "pass": 0.05 <= row_r500["higher_mode_fraction"] <= 0.55,
            "criterion": "0.05 <= higher_mode_fraction(R500) <= 0.55",
        },
        "closure_improves_with_modes": {
            "value": row_r500["closure_full"] - row_r500["closure_ground"],
            "pass": row_r500["closure_full"] > row_r500["closure_ground"],
            "criterion": "closure_full(R500) > closure_ground(R500)",
        },
        "cluster_scale_closure": {
            "value": row_r500["closure_full"],
            "pass": 0.65 <= row_r500["closure_full"] <= 1.20,
            "criterion": "0.65 <= closure_full(R500) <= 1.20",
        },
        "inner_profile_reasonable": {
            "value": row_half["closure_full"],
            "pass": 0.65 <= row_half["closure_full"] <= 1.35,
            "criterion": "0.65 <= closure_full(0.5 R500) <= 1.35",
        },
        "outer_profile_not_divergent": {
            "value": row_outer["closure_full"],
            "pass": 0.50 <= row_outer["closure_full"] <= 1.50,
            "criterion": "0.50 <= closure_full(1.4 R500) <= 1.50",
        },
        "baryon_fraction_physical": {
            "value": row_r500["baryon_fraction_full"],
            "pass": 0.10 <= row_r500["baryon_fraction_full"] <= 0.22,
            "criterion": "0.10 <= f_b(R500) <= 0.22",
        },
        "velocity_dispersion_anchor": {
            "value": sigma_pred,
            "pass": sigma_error <= 0.25,
            "criterion": "|sigma_pred - sigma_anchor| / sigma_anchor <= 0.25",
            "reference": anchor.sigma_kms,
        },
    }
    return gates


def write_csv(path: Path, rows: Sequence[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="First-principles IRS cluster eigenmode toy model")
    parser.add_argument("--seed", type=int, default=20260405, help="Deterministic random seed")
    parser.add_argument("--satellites", type=int, default=24, help="Number of satellite galaxies")
    parser.add_argument("--gas-nodes", type=int, default=16, help="Number of ICM response nodes")
    parser.add_argument("--max-order", type=int, default=5, help="Maximum IRS eigenmode order")
    parser.add_argument("--radial-points", type=int, default=36, help="Number of output radii")
    parser.add_argument("--shell-directions", type=int, default=48, help="Directional samples per radius shell")
    parser.add_argument("--enable-time-memory", action="store_true", help="Enable first-order temporal memory lag on response modes")
    parser.add_argument("--tau-mem-myr", type=float, default=800.0, help="Base memory timescale in Myr")
    parser.add_argument("--assembly-time-myr", type=float, default=3000.0, help="Characteristic assembly timescale at R500 in Myr")
    parser.add_argument("--assembly-alpha", type=float, default=0.7, help="Radial scaling exponent for assembly time: Tasm(r) ~ (r/R500)^alpha")
    parser.add_argument("--mode-tau-power", type=float, default=1.0, help="Mode-order scaling exponent for memory time: tau_n ~ n^p")
    parser.add_argument("--ez-tau-power", type=float, default=0.0, help="E(z) exponent for cosmological tau correction: tau_eff = tau_0 * (E(z)/E(z_ref))^(-nu); 0 disables")
    parser.add_argument("--ez-ref-z", type=float, default=0.2, help="Reference redshift for E(z) normalisation (should match calibration median z)")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "results" / "irs_cluster_eigenmode_first_principles"),
        help="Output directory",
    )
    parser.add_argument("--fail-on-gates", action="store_true", help="Return non-zero if any gate fails")
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent
    input_csv = repo_dir / "cluster_mass_summary.csv"
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    anchor = load_anchor(input_csv)
    rho_crit = critical_density_msun_per_kpc3(anchor.z)
    r500_kpc = ((3.0 * anchor.m500_msun) / (4.0 * math.pi * 500.0 * rho_crit)) ** (1.0 / 3.0)

    rng = random.Random(args.seed)
    gas_rows, gas_profile = build_gas_nodes(anchor, r500_kpc, args.gas_nodes)
    galaxy_rows = build_galaxy_sources(anchor, r500_kpc, args.satellites, rng)
    sources = add_geometry_eta(gas_rows + galaxy_rows)

    radii_kpc = [
        0.08 * r500_kpc + idx * (1.55 * r500_kpc - 0.08 * r500_kpc) / max(args.radial_points - 1, 1)
        for idx in range(args.radial_points)
    ]
    profile_rows = build_profile_rows(
        radii_kpc,
        anchor,
        sources,
        args.max_order,
        args.shell_directions,
        r500_kpc,
        gas_profile,
        args.enable_time_memory,
        args.tau_mem_myr,
        args.assembly_time_myr,
        args.assembly_alpha,
        args.mode_tau_power,
        args.ez_tau_power,
        args.ez_ref_z,
    )
    gates = evaluate_gates(profile_rows, r500_kpc, anchor)

    source_rows = [asdict(source) for source in sorted(sources, key=lambda item: (item.kind, item.name))]
    member_csv = output_dir / "toy_cluster_sources.csv"
    profile_csv = output_dir / "toy_cluster_profile.csv"
    summary_json = output_dir / "toy_cluster_summary.json"
    report_md = output_dir / "toy_cluster_report.md"

    write_csv(member_csv, source_rows, list(source_rows[0].keys()))
    profile_fieldnames = list(profile_rows[0].keys())
    write_csv(profile_csv, profile_rows, profile_fieldnames)

    metadata = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "seed": args.seed,
        "satellites": args.satellites,
        "gas_nodes": args.gas_nodes,
        "max_order": args.max_order,
        "radial_points": args.radial_points,
        "shell_directions": args.shell_directions,
        "enable_time_memory": args.enable_time_memory,
        "tau_mem_myr": args.tau_mem_myr,
        "assembly_time_myr": args.assembly_time_myr,
        "assembly_alpha": args.assembly_alpha,
        "mode_tau_power": args.mode_tau_power,
        "ez_tau_power": args.ez_tau_power,
        "ez_ref_z": args.ez_ref_z,
        "input_csv": str(input_csv),
        "input_sha256": sha256_file(input_csv),
        "anchor": asdict(anchor),
        "r500_kpc": r500_kpc,
        "gas_profile": gas_profile,
        "constants": {
            "G_KPC": G_KPC,
            "A0_KMS2": A0_KMS2,
            "H0_KMS_MPC": H0_KMS_MPC,
            "OMEGA_M": OMEGA_M,
            "OMEGA_L": OMEGA_L,
        },
    }

    summary = {
        "metadata": metadata,
        "gates": gates,
        "key_rows": {
            "at_half_r500": min(profile_rows, key=lambda row: abs(row["r_kpc"] - 0.5 * r500_kpc)),
            "at_r500": min(profile_rows, key=lambda row: abs(row["r_kpc"] - r500_kpc)),
            "at_outer": min(profile_rows, key=lambda row: abs(row["r_kpc"] - 1.4 * r500_kpc)),
        },
        "outputs": {},
    }

    with summary_json.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    outputs = {
        "toy_cluster_sources.csv": sha256_file(member_csv),
        "toy_cluster_profile.csv": sha256_file(profile_csv),
        "toy_cluster_summary.json": sha256_file(summary_json),
    }
    summary["outputs"] = outputs
    with summary_json.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    with report_md.open("w", encoding="utf-8") as handle:
        handle.write("# First-Principles IRS Cluster Eigenmode Toy Model\n\n")
        handle.write("## Run Metadata\n")
        handle.write(f"- Generated (UTC): {metadata['generated_utc']}\n")
        handle.write(f"- Seed: {args.seed}\n")
        handle.write(f"- Input anchor CSV: {input_csv}\n")
        handle.write(f"- Input SHA256: {metadata['input_sha256']}\n")
        handle.write(f"- Median anchor redshift: {anchor.z:.4f}\n")
        handle.write(f"- Anchor M500: {anchor.m500_msun:.6e} Msun\n")
        handle.write(f"- Anchor Mbar: {anchor.mbar_msun:.6e} Msun\n")
        handle.write(f"- Derived R500: {r500_kpc:.2f} kpc\n")
        handle.write(f"- Satellites: {args.satellites}\n")
        handle.write(f"- ICM nodes: {args.gas_nodes}\n")
        handle.write(f"- Max eigenmode order: {args.max_order}\n\n")
        handle.write(f"- Shell directions per radius: {args.shell_directions}\n\n")
        handle.write(f"- Time-memory enabled: {args.enable_time_memory}\n")
        handle.write(f"- tau_mem (Myr): {args.tau_mem_myr:.1f}\n")
        handle.write(f"- assembly_time(R500) (Myr): {args.assembly_time_myr:.1f}\n")
        handle.write(f"- assembly_alpha: {args.assembly_alpha:.3f}\n")
        handle.write(f"- mode_tau_power: {args.mode_tau_power:.3f}\n")
        handle.write(f"- ez_tau_power (E(z) correction nu): {args.ez_tau_power:.3f}\n")
        handle.write(f"- ez_ref_z (normalisation redshift): {args.ez_ref_z:.3f}\n\n")

        key_r500 = summary["key_rows"]["at_r500"]
        handle.write("## Key Cluster-Scale Metrics\n")
        handle.write(f"- Closure at R500, ground mode only: {key_r500['closure_ground']:.3f}\n")
        handle.write(f"- Closure at R500, full eigenmode sum: {key_r500['closure_full']:.3f}\n")
        handle.write(f"- Higher-mode fraction at R500: {key_r500['higher_mode_fraction']:.3f}\n")
        handle.write(f"- Mean memory factor at R500: {key_r500['memory_factor_mean']:.3f}\n")
        sigma_pred = math.sqrt(max(G_KPC * key_r500['m_eff_full_msun'] / (3.0 * key_r500['r_kpc']), 0.0))
        handle.write(f"- Predicted sigma at R500: {sigma_pred:.1f} km/s\n")
        handle.write(f"- Anchor sigma: {anchor.sigma_kms:.1f} km/s\n")
        handle.write(f"- Baryon fraction at R500: {key_r500['baryon_fraction_full']:.3f}\n\n")

        handle.write("## Gate Summary\n")
        for name, gate in gates.items():
            status = "PASS" if gate["pass"] else "FAIL"
            handle.write(f"- {name}: {status}; value={gate['value']:.4f}; criterion={gate['criterion']}\n")

        handle.write("\n## Source Ensemble Summary\n")
        gas_eta = [source.eta_eff for source in sources if source.kind == "gas"]
        gal_eta = [source.eta_eff for source in sources if source.kind == "galaxy"]
        handle.write(f"- Mean eta_eff (gas nodes): {statistics.mean(gas_eta):.3f}\n")
        handle.write(f"- Mean eta_eff (galaxies): {statistics.mean(gal_eta):.3f}\n")
        handle.write(f"- Mean eta_eff (all sources): {statistics.mean(source.eta_eff for source in sources):.3f}\n")
        handle.write("\n## Artifacts\n")
        handle.write("- toy_cluster_sources.csv\n")
        handle.write("- toy_cluster_profile.csv\n")
        handle.write("- toy_cluster_summary.json\n")
        handle.write("- toy_cluster_report.md\n")

    all_pass = all(gate["pass"] for gate in gates.values())
    print(f"anchor_m500={anchor.m500_msun:.6e} r500_kpc={r500_kpc:.2f} all_pass={all_pass}")
    print(f"closure_r500_ground={summary['key_rows']['at_r500']['closure_ground']:.4f}")
    print(f"closure_r500_full={summary['key_rows']['at_r500']['closure_full']:.4f}")
    print(f"higher_mode_fraction_r500={summary['key_rows']['at_r500']['higher_mode_fraction']:.4f}")
    print(f"report={report_md}")

    if args.fail_on_gates and not all_pass:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())