"""Toy model: edge/gradient-sourced metric response (spherical).

Goal
----
A fast viability check for the manuscript's central claim:
  "Baryonic overdensity edges can excite intrinsic metric response that mimics
   a DM halo (flat rotation curves) without adding matter."

We model
  Phi(r) = Phi_N(r) + Phi_BL(r)
with
  - Newtonian acceleration: a_N(r) = G M_b(<r) / r^2
  - An intrinsic response field Phi_BL sourced by a baryon *gradient* proxy

This is intentionally phenomenological: it does NOT claim derivation from an EFT action.
It is meant to test whether plausible edge-sourced terms can generate
  a_total(r) ~ 1/r   (=> flat v(r))
across a decade or two in r without large inner-region distortion.

No third-party dependencies (numpy/scipy/matplotlib) required.
Python 3.10+ recommended.

Outputs
-------
Prints a small table and writes CSV to toy_models/out_edge_response_spherical.csv
with columns: r, aN, aBL, aTot, v

Units
-----
We use dimensionless units (G = 1, M_total ~ 1, scale radius ~ 1).
You can reinterpret by rescaling.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Params:
    # Grid
    r_min: float = 1e-3
    r_max: float = 50.0
    n: int = 4000

    # Baryons: simple Hernquist profile
    m_b: float = 1.0
    a: float = 1.0  # scale radius

    # Edge-response model (phenomenological)
    # a_BL(r) = eps * a0 * F_edge(r)
    eps: float = 2.0
    a0: float = 0.03
    edge_center: float = 4.0
    edge_width: float = 0.6

    # Optional long-range tail multiplier to test whether a localized edge can
    # seed an extended 1/r-like regime. If tail_strength=0, response is purely local.
    tail_strength: float = 1.0
    tail_r0: float = 4.0

    # Safety
    softening: float = 1e-9


def hernquist_density(r: float, m: float, a: float) -> float:
    # rho(r) = (M a) / [2π r (r+a)^3]
    if r <= 0:
        return float("inf")
    return (m * a) / (2.0 * math.pi * r * (r + a) ** 3)


def hernquist_mass_enclosed(r: float, m: float, a: float) -> float:
    # M(<r) = M r^2 / (r+a)^2
    return m * (r * r) / ((r + a) ** 2)


def logistic_step(x: float) -> float:
    # stable logistic
    if x >= 0:
        ex = math.exp(-x)
        return 1.0 / (1.0 + ex)
    ex = math.exp(x)
    return ex / (1.0 + ex)


def edge_window(r: float, center: float, width: float) -> float:
    # A smooth bump localized near center with width.
    # Uses difference of logistics to approximate a smoothed top-hat.
    # Peak ~ 1, compact-ish.
    left = logistic_step((r - (center - width)) / (0.25 * width))
    right = logistic_step((r - (center + width)) / (0.25 * width))
    return max(0.0, left - right)


def tail_factor(r: float, r0: float) -> float:
    # A gentle 1/r tail factor normalized to 1 at r=r0.
    # This is NOT derived; it's a knob to test viability.
    return r0 / max(r, 1e-12)


def newtonian_accel(r: float, m_enc: float, g: float = 1.0) -> float:
    return g * m_enc / max(r * r, 1e-30)


def make_edge_response_accel(params: Params) -> Callable[[float], float]:
    # Core model: localized edge bump, optionally with a long tail.
    def a_bl(r: float) -> float:
        local = edge_window(r, params.edge_center, params.edge_width)
        tail = 1.0 + params.tail_strength * tail_factor(r, params.tail_r0)
        return params.eps * params.a0 * local * tail

    return a_bl


def run(params: Params) -> None:
    dr = (params.r_max - params.r_min) / (params.n - 1)
    a_bl = make_edge_response_accel(params)

    out_rows: list[tuple[float, float, float, float, float]] = []

    for i in range(params.n):
        r = params.r_min + i * dr
        m_enc = hernquist_mass_enclosed(r, params.m_b, params.a)
        a_n = newtonian_accel(r, m_enc)
        a_extra = a_bl(r)
        a_tot = a_n + a_extra
        v = math.sqrt(max(a_tot * r, 0.0))
        out_rows.append((r, a_n, a_extra, a_tot, v))

    csv_path = "toy_models/out_edge_response_spherical.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["r", "aN", "aBL", "aTot", "v"])
        w.writerows(out_rows)

    # Print a small diagnostic table at representative radii.
    sample_rs = [0.5, 1, 2, 3, 4, 5, 8, 12, 20, 35, 50]

    def interp(rq: float) -> tuple[float, float, float, float, float]:
        # nearest-neighbor (good enough for a quick print)
        idx = int(round((rq - params.r_min) / dr))
        idx = max(0, min(params.n - 1, idx))
        return out_rows[idx]

    print("Toy model (dimensionless): Hernquist baryons + edge-response correction")
    print(f"Wrote {csv_path}")
    print("\nParams:")
    print(params)
    print("\n   r        aN        aBL       aTot        v")
    for rq in sample_rs:
        r, a_n, a_x, a_t, v = interp(rq)
        print(f"{r:6.2f}  {a_n:9.3e}  {a_x:9.3e}  {a_t:9.3e}  {v:9.3e}")

    # Quick qualitative flatness metric: v variation over [edge_center, 5*edge_center]
    r_lo = params.edge_center
    r_hi = 5.0 * params.edge_center
    idx_lo = int((r_lo - params.r_min) / dr)
    idx_hi = int((r_hi - params.r_min) / dr)
    idx_lo = max(0, min(params.n - 1, idx_lo))
    idx_hi = max(0, min(params.n - 1, idx_hi))
    vs = [row[4] for row in out_rows[idx_lo: idx_hi + 1]]
    if vs:
        v_min = min(vs)
        v_max = max(vs)
        if v_min > 0:
            print("\nFlatness check:")
            print(f"  v variation over r in [{r_lo:.2f}, {r_hi:.2f}] : {(v_max - v_min) / v_min:.3f} (fraction)")


if __name__ == "__main__":
    run(Params())
