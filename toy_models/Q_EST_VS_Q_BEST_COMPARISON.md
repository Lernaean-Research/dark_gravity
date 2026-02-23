# Comparing old fitted `Q` (`q_best_kms2`) vs new robust `Q_est` for SPARC (175)

This note compares two **different edge-amplitude summaries** used in this repository:

- **Old (toy-model fit amplitude):** `q_best_kms2` (and `v_extra_asym_kms = sqrt(q_best_kms2)`) from the SPARC runner’s `summary.csv`.
- **New (robust outer estimator):** `q_est_kms2` (and `v_est_asym_kms = sqrt(max(q_est_kms2,0))`) from `q_est.csv`.

They are *not the same estimator* and are optimized for different questions.

## 1. Definitions and methodology

### 1.1 Old method: fitted toy-model amplitude `q_best_kms2`

**Where it comes from**
- Produced by the runner [toy_models/sparc_rotmod_runner.py](toy_models/sparc_rotmod_runner.py).
- Written to [toy_models/out_sparc_runs_full_with_composition/summary.csv](toy_models/out_sparc_runs_full_with_composition/summary.csv).

**Model**
- Build the baryonic rotation curve from SPARC rotmod components:

  $$V_{\rm bar}^2(R)=V_{\rm gas}^2+\Upsilon_{\rm disk}V_{\rm disk}^2+\Upsilon_{\rm bul}V_{\rm bul}^2$$

- Convert to baryonic acceleration:

  $$g_{\rm bar}(R)=\frac{V_{\rm bar}^2(R)}{R}$$

- Construct a unit-normalized auxiliary response $\chi'_{\rm unit}(R)$ from a localized source bump near $R_t$ (estimated by $g_{\rm bar}(R_t)\approx a_0$), with normalization chosen so that $\chi'_{\rm unit}(R)\to 1/R$ at large $R$.

- Define modeled total acceleration:

  $$g_{\rm tot}(R)=g_{\rm bar}(R)+Q\,\chi'_{\rm unit}(R)$$

- Define modeled speed:

  $$V_{\rm model}(R)=\sqrt{g_{\rm tot}(R)\,R}$$

**Fit objective**
- Fit one parameter per galaxy: $Q\ge 0$.
- Minimize

  $$\chi^2(Q)=\sum_i\left(\frac{V_{\rm model}(R_i;Q)-V_{\rm obs}(R_i)}{\sigma_{V,i}}\right)^2$$

  via golden-section search on $Q\in[0,Q_{\rm hi}]$.

**Interpretation**
- At large $R$, $\chi'_{\rm unit}(R)\approx 1/R \Rightarrow g_{\rm extra}\approx Q/R \Rightarrow V_{\rm extra}^2\to Q$.
- Therefore:
  - `q_best_kms2` is the **best-fit asymptotic extra $V^2$ amplitude** under the toy-model form.
  - `v_extra_asym_kms = sqrt(q_best_kms2)` is the corresponding asymptotic velocity scale.

**Key property**: `q_best_kms2` is **fit-based** and constrained to be **non-negative**.

Reference methodology: [toy_models/SPARC_ROTMod_METHODOLOGY.md](toy_models/SPARC_ROTMod_METHODOLOGY.md).

---

### 1.2 New method: robust outer estimator `q_est_kms2`

**Where it comes from**
- Produced by [toy_models/q_est_sparc175.py](toy_models/q_est_sparc175.py).
- Written to [toy_models/out_sparc_runs_full_with_composition/q_est.csv](toy_models/out_sparc_runs_full_with_composition/q_est.csv).

**Definition**
- Define

  $$\Delta(R)=V_{\rm obs}^2(R)-V_{\rm bar}^2(R).$$

- Choose an “outer” subset of radii:
  - Primary: $R\ge 0.6\,R_{\max}$.
  - Fallback (if fewer than 5 points): last $K=\max(5,\lceil 0.4N\rceil)$ radii.

- Compute a **Huber M-estimator location** of $\Delta(R)$ on that outer subset (IRLS with MAD scale; tuning constant $c=1.345$).

**Interpretation**
- `q_est_kms2` is a **non-fitted** robust summary of the **outer $V^2$ offset** implied directly by data minus baryons.
- `v_est_asym_kms = sqrt(max(q_est_kms2,0))` is a convenience mapping into a velocity scale when `q_est_kms2>0`.

**Key properties**:
- It can be **negative** (outer data prefer $V_{\rm obs}^2<V_{\rm bar}^2$).
- It is intentionally **outer-focused** and robust to a small number of deviant outer points.

Reference methodology: [toy_models/ROBUST_Q_EST_SPARC175.md](toy_models/ROBUST_Q_EST_SPARC175.md).

## 2. How old vs new values affect analyses

Many analyses in this repo treat an “edge amplitude” target $Y$ and compare it to composition/structure predictors $X$.

### 2.1 What the old analyses implicitly measured
When using `q_best_kms2` / `v_extra_asym_kms`:
- You are measuring the **best-fit amplitude** of the *toy-model response shape* across **all radii** (weighted by `errV`).
- Any mismatch between the toy response shape and the true curve (inner regions, transitions, systematics) can influence the best-fit $Q$.

Typical examples in this repo:
- Composition vs edge scans in `composition_vs_edge_correlations.csv`.
- Cross-validated prediction of `v_extra_asym_kms` in [toy_models/predict_edge_amplitude_cv.py](toy_models/predict_edge_amplitude_cv.py).

### 2.2 What the new analyses measure instead
When using `q_est_kms2` / `v_est_asym_kms`:
- You are measuring a **data-driven outer $V^2$ offset**, not a best-fit toy parameter.
- This focuses attention on whether the **outskirts** exhibit a consistent offset and how that offset relates to composition proxies.

### 2.3 What changed in the six-panel atlas (and what did not)

The six-panel “dyed spacetime” pages mix two kinds of content:

- **Data-derived reconstructions** (computed directly from $v_{obs}(R)$):
  effective acceleration $g_{obs}$, effective potential $\Phi_{obs}$, dyed depth map, 3D proxy, and orbit map.
- **Phenomenological overlays** (from upstream modeling choices):
  $v_{bar}(R)$ and $v_{model}(R)$ curves and their residuals.

Replacing fitted `q_best_kms2` with robust `q_est_kms2` changes only the second category.
In particular:

- Panels 2–5 are unchanged (they depend only on the observed curve).
- Panel 1 and Panel 6 can change, because the toy-model overlay amplitude changes.

To make this contrast explicit, the renderer supports a Q-comparison mode that plots:

- **Dashed red:** $v_{model}$ / residuals from the runner fit (fit $Q_{best}$).
- **Solid red:** a rescaled overlay using robust $Q_{est}$ (robust $Q_{est}$).

The full-catalogue output set is written to:

- `toy_models/out_spacetime_sixpanel_full_v3_qcompare/` (PNGs + a multi-page PDF).

Reproducible command:

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

Note on negative values: since the toy-model runner constrains $Q\ge 0$, the
visualization clamps `q_est_kms2` to 0 when it is negative and uses that as the
effective overlay amplitude.

## 3. Comparative results (SPARC 175; this workspace)

### 3.1 Direct old-vs-new agreement (global)
Computed by [toy_models/analyze_q_est_comparison.py](toy_models/analyze_q_est_comparison.py) and written to:
- [toy_models/out_q_est_analysis/q_est_comparison_report.md](toy_models/out_q_est_analysis/q_est_comparison_report.md)

Key results (n=175 joined):
- `q_est < 0`: 2 galaxies (so `v_est_asym_kms` is NaN for 2).
- Q-space (`q_est_kms2` vs `q_best_kms2`):
  - Pearson $r\approx 0.871$; Spearman $\rho\approx 0.973$.
  - Theil–Sen: `q_est ≈ -493 + 1.014*q_best`.
  - Median $\Delta q = q_{\rm est}-q_{\rm best}\approx -371$ $(\mathrm{km/s})^2$.
- v-space (`v_est_asym_kms` vs `v_extra_asym_kms`):
  - Pearson $r\approx 0.949$; Spearman $\rho\approx 0.972$.
  - Theil–Sen: `v_est ≈ -7.04 + 1.042*v_extra`.

Rule sensitivity (from the same report):
- `lastfrac` has a more negative median offset than `rfrac`.

### 3.2 Composition-vs-edge correlation shifts (old targets vs new targets)
We recomputed the standard “composition proxies $X$ vs edge amplitude $Y$” correlations using both old and new $Y$.

Script:
- [toy_models/compare_old_new_q_analyses.py](toy_models/compare_old_new_q_analyses.py)

Outputs:
- [toy_models/out_q_est_analysis/comp_vs_edge_old_vs_new.csv](toy_models/out_q_est_analysis/comp_vs_edge_old_vs_new.csv)

Summary: replacing `q_best_kms2` with `q_est_kms2` generally **strengthens** the monotonic (Spearman) correlations of several classic predictors with edge amplitude.

Largest Spearman changes for Q-space (Δρ = ρ(x,q_est) − ρ(x,q_best)):
- `sparc_MHI_1e9solMass`: Δρ ≈ +0.0668
- `frac_disk_rt`: Δρ ≈ +0.0651
- `frac_gas_rt`: Δρ ≈ −0.0742 (more negative)
- `frac_gas_half_rt`: Δρ ≈ −0.0508

For the velocity proxies (Δρ = ρ(x,v_est) − ρ(x,v_extra)) the pattern is similar, often with slightly larger magnitude (because sqrt compresses dynamic range but preserves ranks for positive values).

Interpretation:
- The new robust outer statistic appears to produce a **cleaner monotonic ordering** with several composition proxies, consistent with the idea that it measures the outskirts more directly (and is less affected by inner-region fit compromises).

## 4. Reproducibility: how to run everything

### 4.1 Old runner (fitted Q)
Produces `summary.csv` containing `q_best_kms2` and `v_extra_asym_kms`.

```bash
./.venv/Scripts/python.exe toy_models/sparc_rotmod_runner.py --rotmod-dir path/to/Rotmod_LTG --out-dir toy_models/out_sparc_runs_full_with_composition
```

### 4.2 New robust outer estimator
Produces `q_est.csv`.

```bash
./.venv/Scripts/python.exe toy_models/q_est_sparc175.py
```

### 4.3 Direct old-vs-new agreement report + plots

```bash
./.venv/Scripts/python.exe toy_models/analyze_q_est_comparison.py \
  --q-est toy_models/out_sparc_runs_full_with_composition/q_est.csv \
  --summary toy_models/out_sparc_runs_full_with_composition/summary.csv \
  --out-dir toy_models/out_q_est_analysis
```

### 4.4 Composition-vs-edge correlation deltas

```bash
./.venv/Scripts/python.exe toy_models/compare_old_new_q_analyses.py \
  --summary toy_models/out_sparc_runs_full_with_composition/summary.csv \
  --q-est toy_models/out_sparc_runs_full_with_composition/q_est.csv \
  --out-csv toy_models/out_q_est_analysis/comp_vs_edge_old_vs_new.csv
```

### 4.5 Apples-to-apples out-of-sample prediction (CV) for old vs new targets

This extends the existing CV script to run the **same model classes** against
both targets on a **matched galaxy subset** (so fold assignments and N are
identical across targets).

```bash
./.venv/Scripts/python.exe toy_models/predict_edge_amplitude_cv.py \
  --summary toy_models/out_sparc_runs_full_with_composition/summary.csv \
  --q-est toy_models/out_sparc_runs_full_with_composition/q_est.csv \
  --compare-old-new --k 5 --seed 0
```

Notes:
- The matched sample excludes galaxies where `v_est_asym_kms` is NaN (i.e.,
  `q_est_kms2 <= 0`), since the new velocity proxy is defined as
  `sqrt(max(q_est_kms2,0))`.

## 5. Caveats and recommended usage

- `q_best_kms2` and `q_est_kms2` answer **different questions**:
  - `q_best_kms2`: “What amplitude best fits the toy response shape (all radii)?”
  - `q_est_kms2`: “What robust $V^2$ offset is implied in the outskirts?”
- For analyses that specifically care about **outskirts behavior**, prefer `q_est_kms2` (and be explicit about how you handle `q_est<=0`).
- For analyses testing whether the **toy model** provides a good global fit, `q_best_kms2` (plus `chi2`, `outer_chi2`, residual diagnostics) remains essential.
