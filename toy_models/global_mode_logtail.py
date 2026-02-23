"""Toy model: global mode seeded by baryons, producing an outer log-tail.

This script encodes the *specific* idea the user is emphasizing:
- The central baryonic overdensity determines global boundary data / mode amplitudes.
- The metric response can have an additional quasi-static mode that is negligible
  in the inner region but dominates at large radii.

We implement this as an *outer* potential component
  Phi_extra(r) = v_inf^2 * ln(r)
which yields an acceleration
  a_extra(r) = v_inf^2 / r
and therefore a strictly flat rotation curve contribution v_extra(r)=v_inf.

Key point:
- The amplitude v_inf is set by baryons (here via a BTFR-like scaling), i.e.
  v_inf^4 = G M_b a0
This is phenomenological (MOND-adjacent), but it serves as a clear demonstration
of what a “global mode with tension-like behavior” must accomplish.

We smoothly turn on the outer mode near a transition radius r_t defined by
  a_N(r_t) ~= a0
so the inner region is essentially Newtonian.

No third-party dependencies.
Outputs CSV toy_models/out_global_mode_logtail.csv.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # Grid
    r_min: float = 1e-3
    r_max: float = 200.0
    n: int = 6000

    # Units (dimensionless): set G=1
    g: float = 1.0

    # Baryons (Hernquist)
    m_b: float = 1.0
    a: float = 1.0

    # Empirical scale (dimensionless analog of a0)
    a0: float = 0.01

    # Smooth turn-on width around r_t (fractional)
    turn_on_frac_width: float = 0.25


def hernquist_mass_enclosed(r: float, m: float, a: float) -> float:
    return m * (r * r) / ((r + a) ** 2)


def a_newton(r: float, params: Params) -> float:
    m_enc = hernquist_mass_enclosed(r, params.m_b, params.a)
    return params.g * m_enc / max(r * r, 1e-30)


def sigmoid(z: float) -> float:
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


def solve_rt(params: Params) -> float:
    # Find r_t such that a_N(r_t) ~ a0 by simple log-space bisection.
    lo, hi = 1e-6, params.r_max
    for _ in range(120):
        mid = math.sqrt(lo * hi)
        if a_newton(mid, params) > params.a0:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def v_inf(params: Params) -> float:
    # BTFR-like scaling: v^4 = G M a0
    return (params.g * params.m_b * params.a0) ** 0.25


def a_extra(r: float, params: Params, rt: float, vflat: float) -> float:
    # Smoothly turn on around rt.
    w = max(params.turn_on_frac_width * rt, 1e-9)
    s = sigmoid((r - rt) / w)
    return s * (vflat * vflat) / max(r, 1e-30)


def run(params: Params) -> None:
    rt = solve_rt(params)
    vflat = v_inf(params)

    dr = (params.r_max - params.r_min) / (params.n - 1)

    rows: list[tuple[float, float, float, float, float]] = []
    for i in range(params.n):
        r = params.r_min + i * dr
        aN = a_newton(r, params)
        aX = a_extra(r, params, rt, vflat)
        aT = aN + aX
        v = math.sqrt(max(aT * r, 0.0))
        rows.append((r, aN, aX, aT, v))

    out = "toy_models/out_global_mode_logtail.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["r", "aN", "aExtra", "aTot", "v"])
        w.writerows(rows)

    # Diagnostics
    sample = [0.5, 1, 2, 3, float(rt), 2 * rt, 5 * rt, 10 * rt, params.r_max]

    def nearest(rq: float) -> tuple[float, float, float, float, float]:
        idx = int(round((rq - params.r_min) / dr))
        idx = max(0, min(params.n - 1, idx))
        return rows[idx]

    print("Global-mode toy: Hernquist baryons + outer log-tail mode")
    print(f"Wrote {out}")
    print("\nParams:")
    print(params)
    print(f"\nDerived:\n  r_t ~ {rt:.3g} (where a_N ~ a0)\n  v_inf ~ {vflat:.3g}")
    print("\n   r        aN       aExtra      aTot        v")
    for rq in sample:
        r, aN, aX, aT, v = nearest(rq)
        print(f"{r:7.2f}  {aN:9.3e}  {aX:9.3e}  {aT:9.3e}  {v:9.3e}")

    # Flatness metric in outer region [2rt, 20rt] (clipped to r_max)
    r_lo = 2.0 * rt
    r_hi = min(20.0 * rt, params.r_max)
    i_lo = int((r_lo - params.r_min) / dr)
    i_hi = int((r_hi - params.r_min) / dr)
    i_lo = max(0, min(params.n - 1, i_lo))
    i_hi = max(0, min(params.n - 1, i_hi))
    vs = [row[4] for row in rows[i_lo : i_hi + 1]]
    if vs:
        vmin, vmax = min(vs), max(vs)
        if vmin > 0:
            print("\nFlatness check:")
            print(f"  v variation over r in [{r_lo:.3g}, {r_hi:.3g}] : {(vmax - vmin) / vmin:.3f} (fraction)")


if __name__ == "__main__":
    run(Params())
