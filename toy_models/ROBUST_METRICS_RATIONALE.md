# Robust “center action” ↔ “edge reaction” metrics (rationales)

This note explains which summary metrics are most robust and informative for testing
Spacetime-Mechanics edge-response phenomenology against SPARC rotmod data.

The implementation lives in:
- [toy_models/sparc_rotmod_runner.py](toy_models/sparc_rotmod_runner.py)

and the formal algorithmic details are in:
- [toy_models/SPARC_ROTMod_METHODOLOGY.md](toy_models/SPARC_ROTMod_METHODOLOGY.md)

## Design goals

A metric is considered **robust** here if it:

1. Is computed directly from rotmod inputs (minimal external assumptions).
2. Avoids relying on the single innermost or outermost datapoint.
3. Is interpretable within the toy model (i.e., it corresponds to a parameter or
   regime the model explicitly defines).

## Center action: best options

### 1) `gbar_half_rt_kms2_per_kpc` (recommended default)

- Definition: baryonic acceleration evaluated at $0.5R_t$.
- Why it’s robust: it sits inside the galaxy but not at the resolution-limited
  center.
- Why it’s informative: it measures how “strong” the baryonic field is in the
  inner region that plausibly drives the edge-trigger.

### 2) `s_in_dlng_dlnr` (inner compactness/shape)

- Definition: local slope $d\ln g_{bar}/d\ln R$ over a small inner window.
- Why it’s robust: it uses multiple points, so it is less sensitive to any one
  radius, and it is scale-free.
- Why it’s informative: it distinguishes compact/bulge-dominated systems from
  diffuse disks in a way that an amplitude-only metric cannot.

### 3) `gbar_1kpc_kms2_per_kpc` and `gbar_2kpc_kms2_per_kpc` (fixed physical radii)

- Definition: baryonic acceleration at 1 kpc or 2 kpc.
- Why it’s robust: the radius is standardized across galaxies.
- Caveat: many dwarfs may not have measurements out to 2 kpc; missing values are
  expected and should be handled explicitly.

### What to de-emphasize

- `gbar_inner_kms2_per_kpc` is included but is the least robust because it depends
  on the first sampled point.

## Edge reaction: best options

### 1) `q_best_kms2` and `v_extra_asym_kms = sqrt(q_best_kms2)` (recommended default)

- Definition: fitted auxiliary-field amplitude.
- Why it’s robust: it is constrained by all points through a weighted fit.
- Why it’s informative: in the toy model, the auxiliary contribution asymptotes to
  $g_{extra}\sim Q/R$, implying an asymptotic $V^2$ offset of $Q$.

### 2) `r_t_kpc` (turn-on location)

- Definition: transition radius where $g_{bar}\approx a_0$.
- Why it’s informative: it tests whether the “edge” occurs where the model says it
  should, and enables outer-region residual tests.

### 3) Outer residual diagnostics (systematics in outskirts)

- `outer_resid_mean_z`, `outer_resid_rms_z`, `outer_chi2`
- Why it’s informative: these explicitly test whether the model is performing in
  the regime it is meant to explain: $R\gtrsim 2R_t$.

## Recommended first-pass falsifiability plots

All are computable from `summary.csv` alone:

1. `q_best_kms2` vs `gbar_half_rt_kms2_per_kpc`
2. `v_extra_asym_kms` vs `s_in_dlng_dlnr`
3. `outer_resid_mean_z` vs `s_in_dlng_dlnr` (detect systematic failures by morphology)
4. `r_t_kpc` vs `gbar_2kpc_kms2_per_kpc` (when available)

These are intentionally minimal and auditable. More sophisticated choices (e.g.,
photometry-derived central surface density, environment measures) can be added once
this baseline is behaving sensibly.
