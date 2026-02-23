# Inverse-GR (Phenomenology → Effective Source) Notes

Date: 2026-02-17

This note operationalizes an inverse-GR thought experiment:

- Keep the **Einstein tensor** side standard (GR).
- Do **not** assume particulate CDM.
- Use observed galactic phenomenology (rotation curves) to infer the **effective potentials / effective stress–energy** required, then compress that freedom with a low-DOF “intrinsic medium response” closure.

The goal is not to assert a microscopic ontology for spacetime, but to translate a constitutive/response intuition into a testable, low-DOF effective theory.

## 1) Kinematics → required radial acceleration
For each galaxy, from the observed rotation curve

- $g_{\rm obs}(R) = v_{\rm obs}^2(R)/R$.

From baryons (SPARC components + chosen $\Upsilon_*$)

- $g_{\rm bar}(R)$.

Define the residual

- $g_{\rm extra}(R) \equiv g_{\rm obs}(R) - g_{\rm bar}(R)$.

This is the “missing curvature” in the circular-orbit sector.

## 2) Weak-field metric potentials (what dynamics vs lensing see)
In Newtonian gauge for weak fields:

- $ds^2 = -(1+2\Phi)dt^2 + (1-2\Psi)d\mathbf{x}^2$.

To leading order for nonrelativistic motion, the radial acceleration is

- $\mathbf{a} \approx -\nabla\Phi$.

Lensing depends on the “Weyl” combination

- $\Phi_{\rm lens} \propto (\Phi + \Psi)/2$.

So rotation curves mostly constrain $\Phi$; lensing constrains $(\Phi+\Psi)$.

A “metric-equivalent” intrinsic-medium claim is strongest if it can produce the *same* relation between the potentials that GR+CDM would (often close to $\Phi\approx\Psi$ in many regimes). If it produces gravitational slip ($\Phi\neq\Psi$), that becomes an immediate discriminator.

## 3) Spherical toy inversion (useful intuition even for disks)
For a spherical mass distribution, circular orbits obey

- $v^2(r) = G M(<r)/r$.

Given $v_{\rm obs}(r)$, define an **effective enclosed mass**

- $M_{\rm eff}(<r) = r v_{\rm obs}^2(r)/G$.

Subtract baryons to get an “effective extra”

- $M_{\rm extra}(<r) = r\big(v_{\rm obs}^2(r)-v_{\rm bar}^2(r)\big)/G$.

and an effective density

- $\rho_{\rm extra}(r) = \frac{1}{4\pi r^2}\frac{dM_{\rm extra}}{dr}$.

For a flat outer rotation curve $v\to v_\infty$, one gets

- $M_{\rm eff}(<r)\propto r$ and $\rho_{\rm extra}(r)\propto 1/r^2$.

That is the classic statement: *to keep $v$ flat with a Newtonian-like potential, you need an effective $1/r^2$ halo density.*

In the intrinsic-medium approach, $\rho_{\rm extra}$ is not a new matter species; it is the **effective stress–energy** of the spacetime response.

## 4) Effective stress–energy: what is being added in GR
In standard GR

- $G_{\mu\nu} = 8\pi G\,(T^{\rm bar}_{\mu\nu} + T^{\rm resp}_{\mu\nu})$.

The entire program is to interpret $T^{\rm resp}_{\mu\nu}$ as:

- a polarization-like response of the gravitational sector,
- activated by baryons (especially boundary/transition structure),
- with a small parameter set and a universal functional form.

This makes the “extra” empirically necessary but *not* an ad hoc per-galaxy function.

## 5) Minimal response mechanism that naturally gives a 1/r tail
A robust way to get a $1/r$ gradient outside an activation region is a **flux conservation** structure.

In 2D axisymmetry (disk midplane), any field satisfying approximately

- $\nabla\cdot(\mathbf{J}) = 0$ outside the source,

with a radial current $\mathbf{J}\propto \hat{\mathbf{r}}/R$ will produce a solution with

- field gradient $\propto 1/R$.

This is the logic behind your existing auxiliary-field toy: localize the source near a transition radius $R_t$, then outside it you obtain an asymptotically constant extra speed contribution.

### Covariant template (one of many)
Use GR + scalar response field:

- $S=\int d^4x\sqrt{-g}\left[\frac{1}{16\pi G}R - \frac{1}{2}f(X) - V(\chi) + \mathcal{L}_{\rm bar} + \mathcal{L}_{\rm int}(\chi,\psi)\right]$,

where $X\equiv g^{\mu\nu}\partial_\mu\chi\partial_\nu\chi$.

Choose $f(X)$ (or an AQUAL-like structure) so that the static weak-field equation has a conserved flux outside the activation zone. Choose $\mathcal{L}_{\rm int}$ so activation is tied to a baryonic invariant (e.g., a function of $|\nabla\Phi_{\rm bar}|/a_0$ or a surface-density edge proxy).

This keeps “standard GR” while adding a tightly constrained response sector.

## 6) Falsification-first checklist
A materials-engineering model is only parsimonious if it passes these:

- **Low-DOF compression:** Across galaxies, $g_{\rm extra}(R)$ should be well described by a universal shape family with ≤2 parameters, not a bespoke function.
- **Out-of-sample prediction:** edge-amplitude statistic predicted from internal observables better than from environment proxies, under CV.
- **Stratified-null robustness:** any environment signal must survive distance/Q-flag stratified permutations to count as “direct environment responsiveness.”
- **Potential slip/lensing:** if you claim metric equivalence, you must show the implied $(\Phi,\Psi)$ pair is consistent with lensing constraints; otherwise you must explicitly predict where slip appears.

## 7) How this connects to the current SPARC pipeline
Your current implementation already performs Step 1–2 in operational form:

- compute $g_{\rm bar}(R)$,
- define an activation radius $R_t$ near $g_{\rm bar}\sim a_0$,
- fit an extra $\propto 1/R$ tail with a single nonnegative amplitude.

The next upgrade is not additional PN bookkeeping; it is to:

- formalize the closure as an effective response stress–energy (or auxiliary field action),
- specify what it predicts for lensing slip (even if only qualitatively at first),
- and tighten the low-DOF claim with CV and hard negative controls.

As a next “inverse” diagnostic artifact (spherical intuition applied as a shape check), you can also infer a response-density proxy

- \(\rho_{proxy}(r)\propto (4\pi r^2)^{-1} \mathrm{d}[r\,\Delta v^2]/\mathrm{d}r\)

from the same per-galaxy CSVs. The script and outputs are:

- `toy_models/rho_resp_proxy_sparc175.py`
- `toy_models/out_rho_resp_proxy/`

---

## 8) \(\Lambda\)CDM-alternative completion roadmap (go big)
If you want to develop this into a serious \(\Lambda\)CDM-alternative candidate (not “galaxy-only”), the program-level roadmap is captured in:

- `LCDM_ALTERNATIVE_RESPONSE_SECTOR_ROADMAP.md`
