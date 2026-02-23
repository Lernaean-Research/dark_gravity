# Response-Sector (\(T^{\rm resp}_{\mu\nu}\)) Program: “Go Big” \(\Lambda\)CDM-Alternative Roadmap

Date: 2026-02-21

This note is a deliberately ambitious, falsification-first roadmap for elevating the current “inverse-GR / intrinsic medium response” framing into a **credible \(\Lambda\)CDM-alternative candidate**.

It treats

\[
G_{\mu\nu} = 8\pi G\,(T^{\rm bar}_{\mu\nu} + T^{\rm resp}_{\mu\nu})
\]

as the *organizing principle*, where \(T^{\rm resp}_{\mu\nu}\) is the **response-sector stress–energy** that (i) explains galaxy halo phenomenology without particulate CDM, and (ii) admits a cosmological completion consistent with the empirical \(\Lambda\)CDM success set.

The core discipline: **keep claims partitioned by domain**. It is easy to fit rotation curves; a \(\Lambda\)CDM-alternative lives or dies on lensing + growth + CMB-era consistency.

---

## 1) One-sentence thesis (paper-facing)
Baryonic inhomogeneities source not only the standard GR potentials but also an **effective response sector** \(T^{\rm resp}_{\mu\nu}\) that produces halo-like phenomenology in galaxies; a viable completion must additionally reproduce \(\Lambda\)CDM’s large-scale expansion and perturbation successes while predicting discriminants (e.g., slip, screening, or scale-dependent growth).

---

## 2) What \(T^{\rm resp}_{\mu\nu}\) is (and what it is not)
### 2.1 Definition you can defend
In the “inverse-GR” sense, \(T^{\rm resp}_{\mu\nu}\) is the **effective stress–energy** required so that the metric (or potentials) inferred from phenomenology satisfies the Einstein equation with baryons.

This definition is ontologically agnostic.

### 2.2 Three completions (pick one later; keep the math compatible)
All three can be written in the same bookkeeping form.

1) **Extra field/medium**: \(T^{\rm resp}_{\mu\nu}=T^{\chi}_{\mu\nu}\) for some field(s) \(\chi\).
2) **Modified-gravity / EFT moved RHS**: higher-curvature / nonlocal terms are rewritten as an effective source \(T^{\rm resp}_{\mu\nu}\).
3) **Constitutive closure**: \(T^{\rm resp}_{\mu\nu}=\mathcal{F}[g_{\alpha\beta},T^{\rm bar}_{\alpha\beta}]\) (local or mildly nonlocal), engineered to be low-DOF and falsifiable.

### 2.3 Conservation constraint (non-negotiable)
By Bianchi:
\[
\nabla^{\mu}\big(T^{\rm bar}_{\mu\nu}+T^{\rm resp}_{\mu\nu}\big)=0.
\]
If baryons are minimally coupled and follow \(\nabla^{\mu}T^{\rm bar}_{\mu\nu}=0\), then \(\nabla^{\mu}T^{\rm resp}_{\mu\nu}=0\) must hold as well.

If you instead allow exchange \(\nabla^{\mu}T^{\rm bar}_{\mu\nu}=Q_{\nu}\), then you are predicting a (possibly screened) fifth-force / EP-violation sector and must say so explicitly.

---

## 3) Minimal “must-match” \(\Lambda\)CDM target set
A \(\Lambda\)CDM-alternative candidate should be explicit about which of these it targets *now* vs *later*.

### 3.1 Galaxy regime (quasi-static weak field)
- Reproduce rotation curves with **low per-galaxy DOF**.
- Predict an outer-tail structure and amplitude scaling tied to baryonic structure.
- Provide a falsifiable statement about when/where the response activates (boundary layer / transition trigger).

### 3.2 Lensing regime (Weyl potential)
In Newtonian gauge weak field:
\[
\mathrm{d}s^2=-(1+2\Phi)\,\mathrm{d}t^2+(1-2\Psi)\,\mathrm{d}{\bf x}^2.
\]
- Dynamics: mostly constrains \(\Phi\).
- Lensing: constrains \((\Phi+\Psi)/2\).

A \(\Lambda\)CDM-like “metric equivalence” regime typically wants small slip \(\Phi\approx\Psi\) at least where the data demands it.

If the theory predicts slip \(\Phi\neq\Psi\), then the slip is a key discriminator and must be predicted, not patched.

### 3.3 Cosmological regime (FLRW background + perturbations)
To be taken seriously as a \(\Lambda\)CDM-alternative you ultimately need:
- A background expansion history that matches distance data to required accuracy.
- Linear perturbation evolution that reproduces the observed growth and BAO structure.
- CMB-era viability (at minimum: do not obviously ruin peak structure; ideally provide a full parameter mapping).

This does *not* require you to solve all of CMB physics immediately, but you must prevent the theory from being “galaxy-only by construction”.

---

## 4) A concrete, minimal response-sector parameterization
Even before you pick a microphysical completion, you can impose a minimal covariant structure:

\[
T^{\rm resp}_{\mu\nu} = (\rho_{\rm resp}+p_{\rm resp})u_\mu u_\nu + p_{\rm resp}g_{\mu\nu} + \Pi_{\mu\nu},
\]
where \(u^\mu\) is a chosen effective rest frame and \(\Pi_{\mu\nu}\) is the anisotropic stress.

Interpretation knobs:
- \(\rho_{\rm resp}\): “effective halo density” in the GR-inverse sense.
- \(p_{\rm resp}\): determines whether the sector is dust-like on large scales.
- \(\Pi_{\mu\nu}\): directly controls slip and lensing deviations.

**Big-picture commitment (if you want \(\Lambda\)CDM-like growth):** on cosmological backgrounds you typically want the response sector to behave approximately like a pressureless clustering component (\(w\equiv p/\rho\approx 0\), small effective sound speed) over the epochs that matter for structure formation.

---

## 5) Bridge from your current SPARC pipeline to \(T^{\rm resp}_{\mu\nu}\)
Your pipeline currently constructs a one-parameter outer-tail toy for the extra acceleration.

Define (disk midplane) the measured residual:
\[
 g_{\rm extra}(R)=g_{\rm obs}(R)-g_{\rm bar}(R).
\]

In an inverse-GR (or inverse-Poisson) sense, this corresponds to an **effective extra density** whose spherical intuition is:
\[
\rho_{\rm extra}(r) \propto \frac{1}{r^2}\frac{\mathrm{d}}{\mathrm{d}r}\big(r\,\Delta v^2(r)\big),\quad \Delta v^2\equiv v_{\rm obs}^2-v_{\rm bar}^2.
\]

Your empirically robust outer statistic \(Q\) (whether \(q_{\rm best}\) or robust \(q_{\rm est}\)) is then a **compressed observable** that roughly measures the asymptotic amplitude of the response sector in the outer region.

Go-big move: treat \(Q\) as a summary statistic of \(T^{\rm resp}_{\mu\nu}\) in a defined quasi-static limit, then demand that the same response sector has a cosmological limit.

---

## 6) “Mechanism sketches” that are still exam-grade
These are not mutually exclusive; they are a menu. The goal is to pick one that naturally yields (i) boundary-layer activation, (ii) an outer \(1/R\)-like tail in galaxies, and (iii) a dust-like cosmological limit.

### 6.1 Auxiliary field with flux conservation outside activation
You already use the key intuition: localize an activation near a transition radius \(R_t\), and outside it impose an approximate flux conservation law that yields a \(1/R\) gradient.

A schematic covariant template:
\[
S=\int \mathrm{d}^4x\sqrt{-g}\left[\frac{R}{16\pi G}+\mathcal{L}_{\rm bar}(g,\psi)+\mathcal{L}_{\chi}(g,\chi)+\mathcal{L}_{\rm int}(g,\chi,\psi)\right].
\]

Operational constraints (so it stays falsifiable):
- \(\mathcal{L}_{\rm int}\) must tie activation to a *baryonic invariant* (edge/transition proxy), not to a per-galaxy hand-fit function.
- The weak-field static equation for \(\chi\) should reduce outside activation to \(\nabla\cdot\mathbf{J}=0\) with radial \(\mathbf{J}\propto \hat{\mathbf{r}}/R\) in disk symmetry, yielding \(\partial_R\chi\propto 1/R\).

### 6.2 Constitutive “gravitational dielectric” closure
In the weak-field regime, one can define an effective polarization field \(\mathbf{P}\) such that the modified Poisson equation becomes a constitutive law:
\[
\nabla\cdot\big(\nabla\Phi-4\pi G\,\mathbf{P}\big)=4\pi G\,\rho_{\rm bar}.
\]
Then \(\rho_{\rm resp}\equiv-\nabla\cdot\mathbf{P}\) plays the role of the effective response density.

Go-big version: restrict \(\mathbf{P}\) to depend on baryonic invariants and a small number of constants, and embed it in a covariant action (or at least a controlled EFT expansion) so lensing and cosmology are addressable.

### 6.3 Dark-fluid completion (dust-like on FLRW, structured response in galaxies)
Treat \(T^{\rm resp}_{\mu\nu}\) as a fluid whose background behaves like \(w\approx 0\) (CDM-like), but whose *galaxy-scale* constitutive relation includes a baryon-triggered polarization/pressure/anisotropic-stress response that generates the observed rotation-curve residuals.

This is the “most \(\Lambda\)CDM-like” route if you want to match growth quickly, but it forces you to confront:
- effective sound speed constraints,
- stability,
- and whether baryon coupling introduces EP violations.

---

## 7) The discriminant triad (your flagship tests)
If you want to “go big,” don’t lead with fitting curves; lead with discriminants.

### 7.1 Low-DOF compression across SPARC
Your current results already move in this direction.
- Claim you want: the response sector in the galaxy quasi-static limit is described by a universal family with \(\le 2\) DOF per galaxy.
- Killer failure mode: needing an arbitrary function per galaxy.

### 7.2 Rotation vs lensing consistency (Weyl potential)
The response sector must give a definite relation between dynamics (\(\Phi\)) and lensing (\(\Phi+\Psi\)).
- If \(\Phi\approx\Psi\) in the relevant regime, you should say “metric-equivalent *in that regime*.”
- If not, predict where slip appears.

### 7.3 Cosmological growth and background viability
Define a minimal cosmology target:
- match background distances to first order,
- demonstrate that the response sector can cluster appropriately (or show why it does not ruin existing constraints).

Even a qualitative “consistency sketch” here is stronger than silence.

---

## 8) Implementation ladder (what to build next in code/analysis)
This is ordered by “highest credibility per unit effort.”

1) **Publishable galaxy-domain closure** (already underway)
   - Lock the robust outer amplitude statistic (\(q_{\rm est}\)) and keep the fitted \(q_{\rm best}\) as a baseline.
   - State explicitly what parts of the six-panel atlas are data-derived vs model-dependent.

2) **From \(g_{\rm extra}(R)\) to an inferred \(\rho_{\rm resp}(r)\) proxy**
   - Even if spherical is only intuition, producing \(\rho_{\rm resp}\sim 1/r^2\) outer behavior is a compelling intermediate artifact.

3) **First lensing-facing statement**
   - Either: assume \(\Phi\approx\Psi\) as a *working hypothesis* and derive the implied lensing mass profile.
   - Or: introduce a single slip parameter/function class and constrain it (do not let it become a free function).

4) **Cosmology “minimal viability” sketch**
   - Write down the background \(\rho_{\rm resp}(a)\) behavior you want (e.g., \(\propto a^{-3}\) over a target redshift range).
   - State what the response sector’s perturbations do at linear order (even if only a controlled ansatz).

---

## 9) “Do not overclaim” language that still reads bold
- Say: “\(T^{\rm resp}_{\mu\nu}\) is the minimal effective response required by the inferred metric potentials.”
- Avoid: “spacetime *is literally* a fluid/solid.”
- Say: “This is an EFT/constitutive closure candidate.”
- If cosmology is not yet implemented, say: “This work establishes the galaxy-domain closure and enumerates the cosmological completion requirements and discriminants.”

---

## 10) Links to existing notes
- Inverse-GR operational note: see `INVERSE_GR_PHENOMENOLOGY_TO_EFFECTIVE_SOURCE.md`.
- Paper-plan framing: see `INTRINSIC_SPACETIME_MEDIUM_NEW_PAPER_PLAN.md`.
