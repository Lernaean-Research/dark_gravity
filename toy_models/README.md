# Toy models (and SPARC-derived visualization tooling)

This folder name is historical (rapid prototyping + falsifiability scaffolding). In particular, the **six-panel “dyed spacetime” atlas figures are rendered from SPARC-derived per-galaxy rotation-curve outputs**, with additional *derived diagnostics* and *phenomenological overlays*.

If you are looking for the most precise, non-misleading description of what each plotted curve/panel represents (measured vs derived vs fitted vs illustrative), start here:

- [DYED_SPACETIME_RENDERING_METHODOLOGY.md](DYED_SPACETIME_RENDERING_METHODOLOGY.md) (see “Provenance map”)
- [DYED_SPACETIME_SIX_PANEL_HOW_TO_READ.md](DYED_SPACETIME_SIX_PANEL_HOW_TO_READ.md) (executive guide; panel-by-panel reading)

These scripts are **sanity checks** for the manuscript hypothesis that *intrinsic spacetime response* (sourced by baryonic structure) could mimic dark-matter phenomenology.

They are intentionally **phenomenological** unless otherwise stated.

## `edge_response_spherical.py`

- Spherical baryons (Hernquist) + an **edge-localized** “boundary-layer” acceleration term.
- Writes `toy_models/out_edge_response_spherical.csv` with columns `r, aN, aBL, aTot, v`.

Run:

- `./.venv/Scripts/python.exe toy_models/edge_response_spherical.py`

Interpretation:

- If a purely edge-localized correction cannot sustain an approximately flat `v(r)` over wide radii, that’s evidence that the mechanism needs either:
  - an extended tail (nonlocal response / additional mode), or
  - a MOND-like scaling relation, not just a local boundary bump.

## `global_mode_logtail.py`

- Spherical baryons (Hernquist) + a **global outer mode** with a log-tail potential.
- Demonstrates why an extended mode naturally produces `a ~ 1/r` and near-flat outer `v(r)`.
- Writes `toy_models/out_global_mode_logtail.csv`.

Run:

- `./.venv/Scripts/python.exe toy_models/global_mode_logtail.py`

## `aux_field_boundary_layer_2d.py`

- Implements an explicit auxiliary response field `chi` with an effective 2D radial Poisson operator.
- A localized source near a transition radius generates a global `chi'(r) ~ 1/r` tail.
- Writes `toy_models/out_aux_field_boundary_layer_2d.csv`.

Run:

- `./.venv/Scripts/python.exe toy_models/aux_field_boundary_layer_2d.py`

## SPARC rotmod runner (batch falsifiability)

`toy_models/sparc_rotmod_runner.py` applies the current auxiliary edge-response toy model to SPARC-style
`*_rotmod.dat` mass-model inputs (R, Vobs, Vgas, Vdisk, Vbul, ...).

- Builds `Vbar(R)` from component templates with fixed mass-to-light scalings.
- Estimates a transition radius where `g_bar ~ a0`.
- Adds an auxiliary-field contribution with `g_extra ~ Q/R` at large R.
- Fits one parameter per galaxy (`Q >= 0`) by deterministic 1D search.
- Writes per-galaxy CSVs and a `summary.csv`.

Methodology and unit conventions:

- `toy_models/SPARC_ROTMod_METHODOLOGY.md`
- `toy_models/ROBUST_Q_EST_SPARC175.md` (robust non-fitted outer deficit estimator; writes `q_est.csv`)

## Cluster radial-profile adapter (Bullet Cluster-style inputs)

`toy_models/cluster_profile_q_est.py` adapts the **exact same** robust outer statistic
used for SPARC galaxies (Huber location of $\Delta v^2$ in an outer region) to any system
where you can supply a **1D radial profile** of either:

- effective circular speeds (`v_tot_kms`, `v_bar_kms`), or
- enclosed masses (`M_tot_Msun`, `M_bar_Msun`) via $v^2 = GM/r$.

This is useful for quick cross-domain *scale checks* (e.g., comparing cluster-scale
outer deficits to the SPARC-derived $q_{est}$ distribution), but it is **not** a full
2D Bullet-Cluster offset test.

## Environment (one-time setup)

This repo is meant to be run from the workspace virtual environment at `.venv/`.

Bootstrap (creates `.venv` and installs `requirements.txt`):

- `./scripts/bootstrap_venv.ps1`

Then run scripts via:

- `./.venv/Scripts/python.exe toy_models/<script>.py [args]`

Data drop-in template:

- `toy_models/data/bullet_cluster/profile_template.csv`

Bullet Cluster dataset links + suggested folder layout:

- `toy_models/data/bullet_cluster/DATASET_LINKS.md`

If you want to bulk-download the HEASARC public S3 directories listed in the manifest:

- `./toy_models/download_bullet_cluster_heasarc.ps1`

## Correlation analyzer (stdlib-only)

`toy_models/analyze_summary_correlations.py` computes Pearson and Spearman correlations from a
SPARC runner `summary.csv` using only pairwise complete cases (rows where both values are finite).

Methodology:

- `toy_models/CORRELATION_METHODOLOGY.md`

## Partial (controlled) correlations (stdlib-only)

`toy_models/analyze_partial_matrix.py` computes **partial correlations** by
residualizing X and Y against one or more control columns (e.g. mass proxies like
`sparc_L36_1e9solLum`, size proxies like `sparc_Rdisk_kpc`) and then correlating
the residuals.

This is useful for checking whether a composition ↔ edge-behavior trend is
mostly just the obvious mass–velocity scaling.

## Dyed-spacetime visualizations (atlas renderer)

`toy_models/visualize_dyed_spacetime.py` renders per-galaxy figures from the SPARC-runner CSV outputs.

- Default: 3-panel (rotation curve | inferred effective potential | dyed potential-depth map)
- Optional: 6-panel (`--six-panel`) adds (3D proxy surface | illustrative orbit map | residuals vs radius)

Methodology + uncertainty propagation + plotting details:

- [DYED_SPACETIME_RENDERING_METHODOLOGY.md](DYED_SPACETIME_RENDERING_METHODOLOGY.md)

### Quickstart (six-panel atlas)

Inputs are the per-galaxy CSVs produced by the SPARC runner (one CSV per galaxy):

- `toy_models/out_sparc_runs_full_with_composition/galaxies/*.csv`

Render the full six-panel atlas to PNGs (one page per galaxy):

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

Package the same settings into a single multi-page PDF:

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

Render a Q-comparison atlas (dual overlay: fit $Q_{best}$ vs robust $Q_{est}$):

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
Outputs:

- PNG pages: `toy_models/out_spacetime_sixpanel_full_v3/png/*.png`
- Multi-page PDF (when `--make-pdf`): `toy_models/out_spacetime_sixpanel_full_v3/dyed_spacetime_pages.pdf`

Q-comparison outputs (when using `--q-override q_est`):

- PNG pages: `toy_models/out_spacetime_sixpanel_full_v3_qcompare/png/*.png`
- Multi-page PDF: `toy_models/out_spacetime_sixpanel_full_v3_qcompare/dyed_spacetime_pages.pdf`
