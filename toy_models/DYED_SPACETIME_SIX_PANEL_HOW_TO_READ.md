# How to Read the Six‑Panel “Dyed Spacetime” Pages (Executive Guide)

This document is a **reader’s companion** to the six‑panel (2×3) SPARC‑derived pages produced by:

- `toy_models/visualize_dyed_spacetime.py --six-panel`

It is written for reviewers and collaborators who want an **approachable, technically accurate** explanation of what each panel does and **what it does *not* claim**.

For full reproducibility details (definitions, uncertainty propagation, provenance map), see:

- [DYED_SPACETIME_RENDERING_METHODOLOGY.md](DYED_SPACETIME_RENDERING_METHODOLOGY.md)

Current full‑catalogue six‑panel output set:

Default atlas (single model overlay per page):

- Multi‑page PDF: [out_spacetime_sixpanel_full_v3/dyed_spacetime_pages.pdf](out_spacetime_sixpanel_full_v3/dyed_spacetime_pages.pdf)
- Per‑galaxy PNG pages: [out_spacetime_sixpanel_full_v3/png](out_spacetime_sixpanel_full_v3/png)

Q‑comparison atlas (dual overlay: fitted $Q_{best}$ vs robust $Q_{est}$):

- Multi‑page PDF: [out_spacetime_sixpanel_full_v3_qcompare/dyed_spacetime_pages.pdf](out_spacetime_sixpanel_full_v3_qcompare/dyed_spacetime_pages.pdf)
- Per‑galaxy PNG pages: [out_spacetime_sixpanel_full_v3_qcompare/png](out_spacetime_sixpanel_full_v3_qcompare/png)

## Executive summary (plain language)

Each page compresses a galaxy’s rotation‑curve information into a small set of **kinematic inferences** and **visual encodings**:

1. The observed circular speed profile $v_{obs}(R)$ implies the centripetal acceleration required for circular support:

$$g_{obs}(R)=\frac{v_{obs}^2(R)}{R}.$$

1. Integrating $g_{obs}(R)$ over radius produces an **effective 1D potential** $\Phi_{obs}(R)$ (defined up to an additive constant).

1. The dyed 2D panel and the 3D panel are **two different ways of visualizing the same underlying 1D depth profile** derived from $\Phi_{obs}(R)$. They are designed for *intuition and comparability*, not for claiming a literal geometric embedding.

1. If baryons‑only and/or a fitted phenomenological model curve is available in the input CSV, the figure overlays those curves and provides a residual panel to show where (and how strongly) they succeed or fail relative to $v_{obs}$.

If you only have 30 seconds per galaxy:

- Look at **Rotation (Panel 1)** to see the raw mismatch.
- Look at **Residuals (Panel 6)** to see whether mismatches are significant compared to the stated $e_{vobs}$.
- Use **Potential / Dyed / 3D (Panels 2–4)** for integrated, “shape‑of‑the‑field” intuition.
- Treat **Orbits (Panel 5)** as an illustrative sanity visualization, not as observed trajectories.

## What is data vs. derived vs. illustrative (one‑minute version)

On each page, different items have different epistemic status:

- **Measured inputs**: $R$ and $v_{obs}(R)$ (and $e_{vobs}$ when present) come from SPARC‑derived per‑galaxy CSVs.
- **Derived (deterministic) reconstructions**: $g_{obs}(R)$ and $\Phi_{obs}(R)$ are computed directly from $v_{obs}(R)$ using explicit formulas.
- **Model overlays** (if present): $v_{bar}(R)$ and $v_{model}(R)$ are produced upstream (mass‑model construction and/or fitted phenomenological augmentation).
- **Visualization‑only panels**: dyed map, 3D proxy, and the orbit map are illustrative renderings of the derived 1D field; they are not measurements and not a GR metric reconstruction.

## How to read the page (recommended sequence)

1) **Panel 1 → Panel 6**: “Does the model track the observed curve, and where does it fail?”
2) **Panel 2**: “What does the rotation curve imply for the integrated effective potential?”
3) **Panels 3–4**: “What does that potential *look like* when encoded as depth?”
4) **Panel 5**: “Do illustrative test‑particle trajectories look qualitatively consistent with the inferred central pull?”

## Panel‑by‑panel guide (six panels)

### Plotting conventions (when present)

- $v_{obs}$ is plotted as the primary observed curve (typically black).
- $v_{bar}$ (baryons‑only prediction) is an overlay curve (typically blue).
- $v_{model}$ (total curve) is an overlay curve (typically red).
- If a curve is absent, it is because the corresponding column was not present in the per‑galaxy CSV.
- Shaded regions appear only when $e_{vobs}$ is available.

Special case: Q‑comparison pages

- In the Q‑comparison atlas, **two** red model curves may appear in Panel 1:
  - **Dashed red:** $v_{model}$ from the upstream runner fit (fitted $Q_{best}$).
  - **Solid red:** a rescaled overlay using the robust outer estimator (robust $Q_{est}$).
- In Panel 6, the corresponding residual curves appear as:
  - **Dashed red:** $v_{obs}-v_{model}$ (fit $Q_{best}$).
  - **Solid red:** $v_{obs}-v_{model}$ (robust $Q_{est}$).

Important: Panels 2–5 are reconstructed from $v_{obs}(R)$ and do not depend on $Q$.

### Panel 1 (top‑left): Rotation curve

#### Rotation curve — What it shows

- $v_{obs}(R)$ (observed circular speed) versus radius.
- Optional overlays (if available in the CSV):
  - $v_{bar}(R)$: baryonic prediction.
  - $v_{model}(R)$: a total curve from the upstream runner.

If you are reading a Q‑comparison page, the rotation panel may include two red overlays:

- **Dashed**: fitted $Q_{best}$ overlay (runner output).
- **Solid**: robust $Q_{est}$ overlay (a rescaling used only for visual comparison).
- If $e_{vobs}(R)$ exists: a ±1σ band around $v_{obs}(R)$.

#### Rotation curve — How to use it

- Identify the regime where $v_{bar}$ underpredicts $v_{obs}$ (typically outer radii).
- Check whether $v_{model}$ tracks $v_{obs}$ within the observational band.
- The plot often includes a marked transition radius $R_t$ (when $g_{bar}$ is available) as a visual reference point.

#### Rotation curve — If there is no uncertainty band

- Some CSVs do not include $e_{vobs}$; in that case the plot is still useful, but the figure cannot visually communicate significance relative to stated measurement errors.

#### Rotation curve — What not to over‑interpret

- Visual agreement does not by itself validate a mechanism; it only shows descriptive adequacy of the curve overlay.

### Panel 2 (top‑middle): Inferred effective potential $\Phi_{obs}(R)$

#### Effective potential — What it shows

- A 1D “potential‑like” function $\Phi_{obs}(R)$ constructed from the observed centripetal acceleration.
- When $e_{vobs}$ is present, an approximate propagated band is shown (details in the methodology).

#### Effective potential — How to use it

- Read it as the integrated consequence of the rotation curve: steepening corresponds to larger inferred $g_{obs}$.
- Use it for comparing *field‑shape* between systems (especially when combined with global normalization in Panels 3–4).

#### Effective potential — Key caveat

- This is not a unique gravitational potential in a full dynamical sense; it is an effective radial reconstruction tied to circular support.

### Panel 3 (top‑right): 2D dyed fabric (depth map)

#### 2D dyed fabric — What it shows

- A rotationally symmetric 2D rendering of a nonnegative depth scalar $f(R)$ derived from $\Phi_{obs}(R)$.
- Color intensity encodes depth; because the input is radial, any apparent azimuthal structure is purely visual.

#### 2D dyed fabric — How to use it

- Use dye intensity as a quick proxy for “how deep” the inferred effective potential is.
- With global normalization enabled, intensity becomes broadly comparable across galaxies.

#### 2D dyed fabric — Common pitfall

- Do not interpret patterns as 2D structural measurements (spirals/bars); the map is a visualization of a 1D profile.

### Panel 4 (bottom‑left): 3D proxy surface

#### 3D proxy surface — What it shows

- The same depth profile used in Panel 3, now shown as a 3D surface for legibility.
- The vertical axis is a **kpc‑scaled pseudo‑height** chosen for visualization.

#### 3D proxy surface — How to use it

- Use it to see relative “curvature” and where the depth profile changes most rapidly.
- Use the left‑side z‑scale annotation only as a depiction of the chosen mapping; it is not a physical embedding height.

#### 3D proxy surface — Implementation note (why the z scale looks “custom”)

- The z tick labels are drawn inside the panel for layout robustness; this prevents 3D tick labels from spilling into neighboring subplots.

#### 3D proxy surface — Non‑claims (important)

- This is **not** a GR embedding diagram.
- This is **not** a reconstructed 3D mass distribution.

### Panel 5 (bottom‑middle): Illustrative orbit map

#### Orbit map — What it shows

- Test‑particle trajectories integrated in an effective central field inferred from the reconstructed $\Phi_{obs}(R)$.

#### Orbit map — How to use it

- Treat it as a sanity visualization: does the inferred central pull produce qualitatively bound, coherent trajectories over the plotted time window?
- Compare systems: tighter “orbital confinement” typically corresponds to a deeper inferred potential.

#### Orbit map — Non‑claims

- These are not observed stellar/gas orbits.
- This is not a GR geodesic integration; it is an effective Newtonian‑style integration in a central field.

### Panel 6 (bottom‑right): Residuals vs radius

#### Residuals — What it shows

- Residual curves (when the corresponding overlays exist):
  - $\Delta v_{model}(R)=v_{obs}(R)-v_{model}(R)$
  - $\Delta v_{bar}(R)=v_{obs}(R)-v_{bar}(R)$

On Q‑comparison pages, there may be **two** model residual curves:

- **Solid red:** $v_{obs}-v_{model}$ (robust $Q_{est}$).
- **Dashed red:** $v_{obs}-v_{model}$ (fit $Q_{best}$).
- If $e_{vobs}$ exists, the uncertainty band is drawn **around each residual curve**:

$$\Delta v(R) \pm e_{vobs}(R).$$

#### Residuals — How to use it (most diagnostic panel)

- If a residual curve is consistently offset from 0 by more than the local band, that indicates a systematic mismatch in that regime (given the stated observational uncertainties).
- Compare $\Delta v_{bar}$ vs $\Delta v_{model}$ to see *where* the fitted model improves the baryons‑only description.

#### Residuals — If only one residual curve appears

- If $v_{model}$ is absent, only $\Delta v_{bar}$ can be shown.
- If $v_{bar}$ is absent (uncommon for runner outputs), only $\Delta v_{model}$ can be shown.

#### Residuals — Caveats

- The band reflects only $e_{vobs}$ unless additional model uncertainties are explicitly added. Systematics (distance, inclination, beam smearing, baryonic M/L choices) are not fully represented here.

## Reproducing the six‑panel atlas (reference command lines)

Render PNG pages:

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

Package as a single multi‑page PDF:

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

Render the Q‑comparison atlas (dual overlay: fit $Q_{best}$ vs robust $Q_{est}$):

```bash
./.venv/Scripts/python.exe toy_models/visualize_dyed_spacetime.py \
  --galaxy-dir toy_models/out_sparc_runs_full_with_composition/galaxies \
  --out-dir toy_models/out_spacetime_sixpanel_full_v3_qcompare \
  --six-panel --make-pdf \
  --img-n 320 --dpi 160 --interp bilinear \
  --fabric-norm global --global-percentile 95 \
  --fabric-extent per_galaxy \
  --surface-height-mode manual --surface-height-frac 0.35 \
  --surface-height-norm per_galaxy \
  --surface-color-norm auto --surface-z-exag 1 \
  --q-override q_est \
  --summary toy_models/out_sparc_runs_full_with_composition/summary.csv \
  --q-est toy_models/out_sparc_runs_full_with_composition/q_est.csv
```
```

## Glossary (quick)

- $R$ (kpc): galactocentric radius.
- $v_{obs}$ (km/s): observed circular speed.
- $e_{vobs}$ (km/s): quoted 1σ uncertainty on $v_{obs}$.
- $v_{bar}$ (km/s): baryonic prediction from component templates (upstream).
- $v_{model}$ (km/s): fitted total curve from a phenomenological augmentation (upstream).
- $g_{obs}=v_{obs}^2/R$ (km²/s²/kpc): required centripetal acceleration for circular support.
- $\Phi_{obs}$: effective potential inferred by integrating $g_{obs}$.
