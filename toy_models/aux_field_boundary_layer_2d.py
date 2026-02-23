"""Toy model: auxiliary boundary-layer field chi (effective 2D mode) -> log-tail.

Motivation
----------
This implements the user's core analogy in the cleanest mathematical way:
- A central baryonic overdensity "drops" into the spacetime medium.
- The medium supports an additional quasi-static *boundary-layer / surface mode*.
- That mode is sourced primarily near a transition radius r_t (an "edge").
- The far-field of that mode is not the 3D Newtonian 1/r potential; instead it has
  an effective 2D Green's function, producing:

    chi(r) ~ Q ln r   =>   dchi/dr ~ Q/r

Coupling chi into the physical potential generates an extra acceleration a_extra ~ 1/r,
which yields a flat rotation curve contribution.

This is phenomenological, but it is more faithful to the thought-experiment than
inserting a log term by hand:
- we specify a field equation for chi,
- we specify a localized source near r_t,
- we solve for chi globally with boundary conditions.

Model
-----
Baryons (spherical Hernquist):
  M(<r) = M r^2/(r+a)^2
  a_N(r) = G M(<r) / r^2

Boundary-layer response field chi (effective 2D radial Poisson):
  (1/r) d/dr ( r dchi/dr ) = S(r)

Define u(r) = r chi'(r). Then:
  u'(r) = r S(r)
  chi'(r) = u(r)/r

We choose S(r) to be a narrow bump centered at r_t (where a_N ~ a0), normalized so:
  Q = \int_0^\infty r S(r) dr
Thus for r >> bump region: u(r)->Q and chi'(r)->Q/r.

Coupling to the physical potential:
  Phi_total = Phi_N + eps * chi
  a_total = dPhi_total/dr = a_N + eps * chi'(r)

Units
-----
Dimensionless units with G=1.

Outputs
-------
CSV: toy_models/out_aux_field_boundary_layer_2d.csv
columns: r, aN, aChi, aTot, v, chi

No third-party dependencies.
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
    n: int = 8000

    # Units
    g: float = 1.0

    # Baryons
    m_b: float = 1.0
    a: float = 1.0

    # Empirical/transition scale
    a0: float = 0.01

    # Boundary-layer source width (absolute)
    sigma: float = 1.0

    # Coupling strength from chi to physical potential
    eps: float = 1.0

    # Set integrated "charge" Q (controls asymptotic flat velocity)
    # If use_btfr=True: Q = sqrt(G M_b a0)
    # Else: Q = Q_manual
    use_btfr: bool = True
    q_manual: float = 0.1


def hernquist_mass_enclosed(r: float, m: float, a: float) -> float:
    return m * (r * r) / ((r + a) ** 2)


def a_newton(r: float, p: Params) -> float:
    m_enc = hernquist_mass_enclosed(r, p.m_b, p.a)
    return p.g * m_enc / max(r * r, 1e-30)


def solve_rt(p: Params) -> float:
    # Find r_t such that a_N(r_t) ~ a0 via log bisection.
    lo, hi = 1e-6, p.r_max
    for _ in range(140):
        mid = math.sqrt(lo * hi)
        if a_newton(mid, p) > p.a0:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def gaussian_bump(r: float, center: float, sigma: float) -> float:
    z = (r - center) / max(sigma, 1e-12)
    return math.exp(-0.5 * z * z)


def trapz(xs: list[float], ys: list[float]) -> float:
    s = 0.0
    for i in range(1, len(xs)):
        dx = xs[i] - xs[i - 1]
        s += 0.5 * dx * (ys[i] + ys[i - 1])
    return s


def run(p: Params) -> None:
    rt = solve_rt(p)

    # Choose integrated source strength Q.
    if p.use_btfr:
        # Q has units of (velocity)^2 in these conventions; eps*Q sets v_flat^2.
        # Using BTFR-like scaling ensures v_flat^4 ~ G M a0.
        q = math.sqrt(p.g * p.m_b * p.a0)
    else:
        q = p.q_manual

    dr = (p.r_max - p.r_min) / (p.n - 1)
    rs = [p.r_min + i * dr for i in range(p.n)]

    # Build an unnormalized source profile s0(r) and normalize to achieve Q.
    s0 = [gaussian_bump(r, rt, p.sigma) for r in rs]
    integrand = [r * s for r, s in zip(rs, s0)]
    i0 = trapz(rs, integrand)
    if i0 <= 0:
        raise RuntimeError("Source normalization integral is non-positive")

    # S(r) normalized so that ∫ r S(r) dr = Q
    S = [(q / i0) * s for s in s0]

    # Solve u'(r) = r S(r), u(0)=0 using cumulative trapezoid.
    u = [0.0] * p.n
    for i in range(1, p.n):
        r0, r1 = rs[i - 1], rs[i]
        f0 = r0 * S[i - 1]
        f1 = r1 * S[i]
        u[i] = u[i - 1] + 0.5 * (r1 - r0) * (f0 + f1)

    # chi'(r) = u(r)/r
    chi_p = [u_i / max(r, 1e-30) for u_i, r in zip(u, rs)]

    # Integrate chi from chi' with chi(r_min)=0
    chi = [0.0] * p.n
    for i in range(1, p.n):
        chi[i] = chi[i - 1] + 0.5 * (rs[i] - rs[i - 1]) * (chi_p[i] + chi_p[i - 1])

    # Physical accelerations
    rows: list[tuple[float, float, float, float, float, float]] = []
    for r, chi_prime, chi_val in zip(rs, chi_p, chi):
        aN = a_newton(r, p)
        aChi = p.eps * chi_prime
        aT = aN + aChi
        v = math.sqrt(max(aT * r, 0.0))
        rows.append((r, aN, aChi, aT, v, chi_val))

    out = "toy_models/out_aux_field_boundary_layer_2d.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["r", "aN", "aChi", "aTot", "v", "chi"])
        w.writerows(rows)

    vflat = math.sqrt(max(p.eps * q, 0.0))

    print("Aux-field toy: effective-2D boundary-layer mode chi sourced near r_t")
    print(f"Wrote {out}")
    print("\nParams:")
    print(p)
    print(f"\nDerived:\n  r_t ~ {rt:.3g} (where a_N ~ a0)\n  Q ~ {q:.3g} (∫ r S dr)\n  v_flat(asym) ~ sqrt(eps*Q) ~ {vflat:.3g}")

    sample = [0.5, 1, 2, 3, rt, 2 * rt, 5 * rt, 10 * rt, p.r_max]

    def nearest(rq: float) -> tuple[float, float, float, float, float, float]:
        idx = int(round((rq - p.r_min) / dr))
        idx = max(0, min(p.n - 1, idx))
        return rows[idx]

    print("\n   r        aN        aChi       aTot        v        chi")
    for rq in sample:
        r, aN, aC, aT, v, chi_val = nearest(rq)
        print(f"{r:7.2f}  {aN:9.3e}  {aC:9.3e}  {aT:9.3e}  {v:9.3e}  {chi_val:9.3e}")

    # Outer flatness check
    r_lo = 2.0 * rt
    r_hi = min(20.0 * rt, p.r_max)
    i_lo = int((r_lo - p.r_min) / dr)
    i_hi = int((r_hi - p.r_min) / dr)
    i_lo = max(0, min(p.n - 1, i_lo))
    i_hi = max(0, min(p.n - 1, i_hi))
    vs = [row[4] for row in rows[i_lo : i_hi + 1]]
    if vs:
        vmin, vmax = min(vs), max(vs)
        if vmin > 0:
            print("\nFlatness check:")
            print(f"  v variation over r in [{r_lo:.3g}, {r_hi:.3g}] : {(vmax - vmin) / vmin:.3f} (fraction)")


if __name__ == "__main__":
    run(Params())
