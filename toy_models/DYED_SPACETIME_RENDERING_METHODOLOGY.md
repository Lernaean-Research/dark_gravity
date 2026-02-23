# Dyed-Spacetime Rendering Methodology (Reproducibility + Uncertainty)

This document describes **exactly how the dyed-spacetime figures are computed and drawn** by:

- `toy_models/visualize_dyed_spacetime.py`

It is written to make the visualization **auditable**, **reproducible**, and **explicit about non-claims**.

## Scope / non-claims (read first)

- The figures reconstruct an **effective 1D radial potential** from observed circular speeds, then render it in 2D/3D for intuition.
- This is **not** a GR embedding diagram.
- This is **not** a full metric reconstruction.
- The orbit panel integrates **effective/Newtonian** test-particle motion in a central field inferred from the data; it is **illustrative**, not a GR geodesic calculation.

## Terminology: why this lives under `toy_models/`

The directory name `toy_models/` reflects how this codebase started (rapid prototyping + falsifiability scaffolding). **It does not mean the 6-panel atlas uses synthetic data.**

- The **data source** for the 6-panel figures is real SPARC rotation-curve / rotmod inputs (via the per-galaxy CSVs).
- The **toy/phenomenology** is in the *interpretation layer*: fitted augmentation terms, derived diagnostics, and stylized renderings.

If you want wording that is maximally non-misleading in a paper or release, call these:

- “SPARC-derived effective-potential visualizations”
- “Data-driven kinematic reconstructions with phenomenological overlays”

and reserve “toy model” for the auxiliary-field / edge-response hypothesis itself.

## Provenance map (what is data vs derived vs fitted vs illustrative)

Each 6-panel page contains a mix of quantities with different epistemic status:

### A) Direct SPARC observational inputs (measured)

From the per-galaxy CSV (ultimately from SPARC):

- `r_kpc`
- `vobs_kms`
- `e_vobs_kms` (when present)

These are the only quantities treated as “data” inside the renderer.

### B) Deterministic kinematic reconstructions (derived from measured inputs)

Computed directly from (`r_kpc`, `vobs_kms`) with explicit formulas:

- $g_{obs}(R)=v_{obs}^2/R$
- $\Phi_{obs}(R)$ via $d\Phi/dR=g$ and trapezoid integration
- fabric depth $f(R)\propto-\Phi_{obs}(R)$ and its normalized variants

These are **not** additional fitted parameters; they are deterministic transforms of the observed rotation curve.

### C) Model overlays / phenomenological outputs (not raw data)

If present in the CSV, these curves come from upstream modeling choices:

- `vbar_kms`: baryonic prediction constructed from SPARC component templates and chosen M/L assumptions (see the SPARC runner methodology)
- `vmodel_kms`: a fitted total curve produced by the runner’s phenomenological augmentation
- `gbar_kms2_per_kpc`, `gextra_kms2_per_kpc`: corresponding acceleration profiles

Optional Q‑comparison overlay (renderer feature):

- When `--q-override q_est` is enabled, the renderer will **keep the original fit-based model curve** as a reference overlay and **also** draw a second model curve where the extra field amplitude is rescaled using `q_est.csv`.
- This affects only the *model-dependent overlays* (`vmodel_kms`, `gextra_kms2_per_kpc`) and the corresponding residuals.
- It does **not** affect any quantity reconstructed from `vobs_kms` (Panels 2–5), since those are deterministic transforms of the observed curve.

These are extremely useful for falsifiability (they let you look at residuals), but they are not “measured curves.”

### D) Visualization-only panels (illustrative)

- 2D dyed map: a rotationally symmetric rendering of a 1D depth profile
- 3D proxy: a chosen height mapping in kpc used for legibility (not a GR embedding)
- Orbits: test-particle trajectories integrated in the inferred central field (not observed trajectories; not GR geodesics)

## Interpretation and implications (what to take seriously)

These figures are designed to be **transparent kinematic encodings**, not a mechanistic proof.

- If $v_{obs}(R)$ is trusted, then $g_{obs}(R)=v_{obs}^2/R$ is the acceleration required for circular support. The inferred $\Phi_{obs}(R)$ is therefore a compact way to visualize the *integrated consequence* of the rotation curve.
- The dyed (and 3D) panels are **rotationally symmetric renderings of a 1D profile**. Any apparent azimuthal “structure” is purely a visualization choice; the data input is radial.
- Global normalization makes dye intensity comparable across galaxies, but it also means low-depth systems can look visually “flat” compared to deep systems.
- Residuals are the most direct falsifiability panel: if $v_{obs}-v_{model}$ remains systematically nonzero compared to the stated uncertainties, the model is failing in that regime.

What you should **not** infer:

- The 3D proxy height is not a measured geometric embedding height.
- The orbit map does not represent measured stellar trajectories; it is a sanity visualization of the inferred central pull.
- The uncertainty bands shown here do not include all astrophysical systematics; they are best viewed as *internal consistency with stated $v_{obs}$ errors*.

## Inputs

### Per-galaxy CSVs

The script expects per-galaxy CSVs (one file per galaxy), typically produced by the SPARC runner:

- `toy_models/out_sparc_runs_full_with_composition/galaxies/<NAME>.csv`

Required columns:

- `r_kpc` (radius, kpc)
- `vobs_kms` (observed circular speed, km/s)

Optional columns (used when present):

- `e_vobs_kms` (1σ uncertainty on `vobs_kms`, km/s)
- `vbar_kms` (baryonic prediction, km/s)
- `vmodel_kms` (total fitted model, km/s)
- `gbar_kms2_per_kpc` (baryonic acceleration proxy, km²/s²/kpc)
- `gextra_kms2_per_kpc` (extra acceleration term, km²/s²/kpc)

### Optional: robust-`Q` overlay inputs (Q comparison mode)

If you run with `--q-override q_est`, you must also provide:

- `--summary toy_models/out_sparc_runs_full_with_composition/summary.csv` (to read `q_best_kms2` per galaxy)
- `--q-est toy_models/out_sparc_runs_full_with_composition/q_est.csv` (to read `q_est_kms2` per galaxy)

This mode requires that the per-galaxy CSV contains `gextra_kms2_per_kpc` and that `q_best_kms2>0` for that galaxy; otherwise the override is skipped (the page will fall back to the single-overlay behavior).

### Data sanitation

Before any physics/plotting, the renderer:

1. Drops non-finite or non-positive radii.
2. Sorts by radius.
3. Collapses duplicate radii by **averaging** values at identical `r_kpc` (within `1e-12` kpc absolute tolerance).

This happens in `_sanitize_monotonic_radius()`.

## Derived quantities (units are explicit)

Let radius be $R$ (kpc) and observed speed $v_{obs}$ (km/s).

### Effective centripetal acceleration

The effective circular-orbit acceleration used throughout is:

$$g_{obs}(R) = \frac{v_{obs}^2(R)}{R}\qquad [\mathrm{km^2\ s^{-2}\ kpc^{-1}}].$$

This is a kinematic inference: it is the radial pull required for circular support.

### Effective potential from $g(R)$

A 1D potential-like function is defined (up to an additive constant) by:

$$\frac{d\Phi}{dR} = g(R),\qquad \Phi(R_{min}) = 0,$$

using a cumulative trapezoid integral (`_trapz_integral`).

Notes:

- The sign convention is chosen so an attractive field corresponds to $a_R=-d\Phi/dR$.
- Only **differences** in $\Phi$ matter for visualization.

### “Fabric depth” scalar used for dye

The dyed map uses a nonnegative scalar derived from the inferred potential:

$$f(R) = -\Phi_{obs}(R) - \min_R(-\Phi_{obs}(R)),$$

implemented in `_fabric_profile_from_phi()`.

Interpretation:

- Larger $f$ = deeper inferred effective potential (in this visualization convention).

## Uncertainty propagation (what the shaded bands mean)

### Rotation curve band

If `e_vobs_kms` exists, the rotation panel draws:

- a line for $v_{obs}(R)$
- a ±1σ band: $v_{obs}(R) \pm e_{vobs}(R)$

This is a direct visualization of the measurement uncertainty in $v_{obs}$.

### Potential band (propagated from `e_vobs_kms`)

If `e_vobs_kms` exists and `--no-phi-uncert` is not set, the potential panel draws an approximate 1σ band for $\Phi_{obs}$ by propagating uncertainty through:

$$g(R)=\frac{v^2(R)}{R}.$$

Using local linear propagation:

$$\sigma_g(R) \approx \left|\frac{\partial g}{\partial v}\right|\sigma_v(R) = \frac{2|v(R)|}{R}\,\sigma_v(R).$$

Then the script integrates:

$$\sigma_{\Phi}(R) \approx \int_{R_{min}}^{R} \sigma_g(R')\, dR'.$$

Implementation: `_infer_potential_sigma_from_vobs()`.

Caveats (important):

- This ignores covariance between points and is therefore conservative in the sense that it can overstate uncertainty.
- It includes only the uncertainty in $v_{obs}$, not systematics in inclination, distance, beam smearing, baryonic modeling, etc.

### Residuals band (correct placement)

In the 6-panel figure, the residual panel shows residual curves such as:

- $\Delta v_{model}(R)=v_{obs}(R)-v_{model}(R)$ (red)
- $\Delta v_{bar}(R)=v_{obs}(R)-v_{bar}(R)$ (blue)

If `e_vobs_kms` exists, the shaded band is drawn **around each residual curve**:

$$\Delta v(R) \pm e_{vobs}(R).$$

Rationale:

- If only $v_{obs}$ is treated as uncertain (and $v_{model}, v_{bar}$ are treated as exact curves), then $\sigma_{\Delta v}\approx\sigma_{v_{obs}}$.

If you later add uncertainties in baryonic modeling or the fitted model, this band should be updated to combine them (e.g., in quadrature).

## Transition radius marker $R_t$ (how it is chosen)

If `gbar_kms2_per_kpc` exists, a transition radius is marked as:

$$R_t := \operatorname*{argmin}_{R_i}\,\left|g_{bar}(R_i)-a_0\right|,$$

where $a_0$ is fixed to $1.2\times 10^{-10}\,\mathrm{m\,s^{-2}}$ and converted internally into km²/s²/kpc.

This is a pragmatic “closest approach” definition (no interpolation) and is used only as a visual marker and for choosing illustrative radii.

## Figure layouts

The script supports:

- 3-panel figure (default): rotation | potential | dyed
- 6-panel figure (`--six-panel`):
  - top row: rotation | potential | dyed
  - bottom row: 3D proxy | orbits | residuals

Output is written to:

- `<out-dir>/png/<NAME>.png`

Optional separate outputs:

- `<out-dir>/png_3d/<NAME>_3d.png` (when `--make-3d`)
- `<out-dir>/png_orbits/<NAME>_orbits.png` (when `--make-orbit-map`)
- `<out-dir>/dyed_spacetime_pages.pdf` (when `--make-pdf`)
- `<out-dir>/dyed_spacetime_contact.pdf` (when `--make-contact`)

## Q override mode (what changes, exactly)

The renderer can optionally replace the model overlay amplitude while keeping the underlying response shape.

### Goal

Provide an apples-to-apples visual comparison of the *same* toy-model response profile using two different amplitude summaries:

- fitted amplitude: `q_best_kms2` (from the runner fit; constrained $Q\ge 0$)
- robust outer estimator: `q_est_kms2` (Huber location of $V_{obs}^2-V_{bar}^2$ at large radii; can be negative)

### Mechanism

Per-galaxy CSVs produced by the runner include a fitted extra-field profile of the form:

$$g_{extra}(R)=q_{best}\,\chi'(R).$$

So, when `q_best_kms2>0`, the renderer recovers the unit-response profile:

$$\chi'(R)=g_{extra}(R)/q_{best}.$$

It then substitutes a new amplitude $q_{new}$ (from `q_est.csv`) to produce an alternate overlay:

$$g_{extra,new}(R)=q_{new}\,\chi'(R),\qquad g_{tot,new}(R)=g_{bar}(R)+g_{extra,new}(R),\qquad v_{model,new}(R)=\sqrt{g_{tot,new}(R)\,R}.$$

### Handling negative `q_est`

The runner’s toy-model parameterization constrains $Q\ge 0$. To keep the visualization consistent with that parameterization, the override uses:

$$q_{new,eff}=\max(q_{est},0).$$

This means negative robust estimates are treated as “no extra field” rather than as a subtractive field.

### What does *not* change

Panels derived from `vobs_kms` (effective potential, dyed depth map, 3D proxy, orbit map) do not change when switching $Q$ overlays.

## Panel-by-panel drawing details

### 1) Rotation curve

- Plots: $v_{obs}$ (black), optional $v_{bar}$ (blue), optional $v_{model}$ (red)
- Uncertainty: if `e_vobs_kms` exists, fills $v_{obs}\pm e_{vobs}$
- Transition marker: if `gbar_kms2_per_kpc` exists, defines $R_t$ as the radius where $g_{bar}$ is closest to $a_0$ and draws a vertical line.

### 2) Effective potential

- Plots: $\Phi_{obs}$ inferred from $g_{obs}$
- Optional: $\Phi_{bar}$ inferred from $g_{bar}=v_{bar}^2/R$
- Uncertainty: propagated band $\Phi_{obs}\pm\sigma_\Phi$ when `e_vobs_kms` exists and potential-uncertainty is enabled.

### 3) Dyed potential depth (2D)

- Builds a **rotationally symmetric** 2D image from the 1D depth profile $f(R)$.
- Rasterization: converts to a square image via interpolation in radius on a Cartesian grid (`_fabric_cartesian_image`) to keep PDF generation fast.
- Colormap: `magma`; masked values (outside data support when plotting beyond $R_{max}$) are set to white.

Normalization (`--fabric-norm`):

- `per_galaxy`: scale depth by that galaxy’s 95th percentile of $f(R)$.
- `global`: scale depth by a global scale computed across the sample (`_compute_global_fabric_scale`).

Extent (`--fabric-extent`):

- `per_galaxy`: plot out to that galaxy’s maximum observed radius.
- `global_max`: plot out to the maximum radius seen anywhere in the sample.
- `fixed`: plot out to `--fixed-rmax-kpc`.

If the plotted extent exceeds the data max radius, values beyond the data are **masked** (not extrapolated).

### 4) 3D proxy surface (bottom-left; 6-panel)

Purpose:

- Provide a visually legible “height map” proxy that shares the same x/y units (kpc) and is explicitly not a physical GR embedding.

Construction:

- The surface uses a rotationally symmetric raster field on an x/y grid in kpc.
- The **color** on the surface is derived from the normalized depth field (same dye scalar, normalized to 0..1).
- The **height** is controlled by `--surface-height-mode`:

`manual` (default in atlas runs)

- Height profile: $z(R) = f_{norm,height}(R)\, z_{max}$
- Where $z_{max}$ is set by either:
  - `--surface-height-kpc` if > 0, or
  - `--surface-height-frac * R_{plot}` otherwise
- `--surface-z-exag` multiplies $z_{max}$

`phi_over_c2`

- A physically tiny weak-field proxy:
  - $z(R) \propto f(R)/c^2$ (scaled to keep units manageable)
- Expect this to look nearly flat at kpc scales.

`accel_over_a0`

- A dimensionless acceleration proxy integrated over radius:
  - $h(R)=\int (g_{obs}(R)/a_0)\, dR$
  - $z(R) \propto (\max(h)-h)$, scaled by `--surface-z-exag`

Aspect and view:

- The axis box aspect is set proportional to coordinate spans so x/y/z share consistent units.
- Default view: `elev=28`, `azim=-55`.

Color normalization on the surface (`--surface-color-norm`):

- `auto`: per-galaxy min/max contrast (prevents “all black” dwarfs under global scaling)
- `fixed01`: fixed mapping for strict comparability when `--fabric-norm global`

### 5) Orbits (illustrative; bottom-middle)

- Central field is derived from $g_{obs}(R)=v_{obs}^2/R$.
- Integrator: leapfrog in 2D using consistent units:
  - position: kpc
  - velocity: km/s
  - acceleration: km²/s²/kpc
  - timestep: (kpc·s)/km, so that `dx = v*dt` and `dv = a*dt`
- For each chosen starting radius $r_0$, an initial circular-speed guess is taken from interpolated $v_{obs}(r_0)$.
- Timestep is set from an estimated local circular period:

$$T \approx \frac{2\pi r_0}{v_0},\quad dt = T/\mathrm{steps\_per\_turn}.$$

Caveat:

- These trajectories are meant as a qualitative sanity visualization of the inferred central pull; they are not constrained to match observed non-circular motions, bars, warps, or a full disk potential.

### 6) Residuals vs radius (bottom-right)

- Plots $v_{obs}-v_{model}$ and/or $v_{obs}-v_{bar}$.
- If `e_vobs_kms` exists, shades ±1σ **around each residual curve**.

## Reproducible run commands (examples)

Two-galaxy sanity check:

```bash
./.venv/Scripts/python.exe toy_models/visualize_dyed_spacetime.py \
  --galaxy-dir toy_models/out_sparc_runs_full_with_composition/galaxies \
  --out-dir toy_models/out_spacetime_sixpanel_sample \
  --only CamB,ESO563-G021 \
  --six-panel \
  --img-n 320 --dpi 160 --interp bilinear \
  --fabric-norm global --global-percentile 95 \
  --fabric-extent per_galaxy \
  --surface-height-mode manual --surface-height-frac 0.35 \
  --surface-height-norm per_galaxy \
  --surface-color-norm auto --surface-z-exag 1
```

Full atlas (all galaxies):

```bash
./.venv/Scripts/python.exe toy_models/visualize_dyed_spacetime.py \
  --galaxy-dir toy_models/out_sparc_runs_full_with_composition/galaxies \
  --out-dir toy_models/out_spacetime_sixpanel_full_v3 \
  --six-panel \
  --img-n 320 --dpi 160 --interp bilinear \
  --fabric-norm global --global-percentile 95 \
  --fabric-extent per_galaxy \
  --surface-height-mode manual --surface-height-frac 0.35 \
  --surface-height-norm per_galaxy \
  --surface-color-norm auto --surface-z-exag 1
```

Full atlas (all galaxies) + multipage PDF packaging:

```bash
./.venv/Scripts/python.exe toy_models/visualize_dyed_spacetime.py \
  --galaxy-dir toy_models/out_sparc_runs_full_with_composition/galaxies \
  --out-dir toy_models/out_spacetime_sixpanel_full_v3 \
  --six-panel --make-pdf \
  --img-n 320 --dpi 160 --interp bilinear \
  --fabric-norm global --global-percentile 95 \
  --fabric-extent per_galaxy \
  --surface-height-mode manual --surface-height-frac 0.35 \
  --surface-height-norm per_galaxy \
  --surface-color-norm auto --surface-z-exag 1
```

## Software environment

- Python: any modern Python 3.x
- Packages:
  - `numpy`
  - `matplotlib`

The script forces Matplotlib’s `Agg` backend for batch rendering.

## Known limitations / transparency notes

- This pipeline assumes the CSVs already represent the chosen pre-processing of SPARC (distance, inclination, beam-smearing corrections, etc.). Those upstream choices dominate many systematics.
- The potential inference uses only the circular-orbit relation; it does not model pressure support, non-circular motions, or non-axisymmetric structure.
- Residual uncertainty bands currently treat $v_{bar}$ and $v_{model}$ as exact curves. If you want a more honest band, you need an uncertainty model for baryonic mass-to-light ratios, gas scaling, and any fitted parameters.
