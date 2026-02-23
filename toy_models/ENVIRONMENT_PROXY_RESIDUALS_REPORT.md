# Environment proxy vs edge-amplitude residuals (SPARC toy-model pipeline)

Date: 2026-02-17

## Executive summary (plain language)

### The question
We want a falsifiable answer to:

> After you account for a galaxy’s own internal dynamical scale, do galaxies in denser environments systematically show a different fitted “edge amplitude” in the toy model?

Here “edge amplitude” is the single-parameter strength of the extra component in the toy fit, reported as:
- `v_extra_asym_kms` (defined by the pipeline as `v_extra_asym_kms = sqrt(q_best_kms2)`)

The environment proxy used here is one operational definition:
- `env_twompp_delta_external`: a 2M++ density-contrast value at the galaxy position.

### How this relates to the two competing narratives (what we did and did not test)
This particular analysis is best thought of as a **stress-test for environment-responsiveness**, not as a full theory-comparison end-to-end.
It speaks to the hypotheses differently:

- **Intrinsic spacetime medium / intrinsic mechanics (Spacetime Mechanics manuscript):**
  - Core claim: the “extra acceleration” phenomenology can arise from **internal metric dynamics** (nonlinear response, boundary-layer / quasi-harmonic modes at a galaxy’s edge) without adding particle dark matter.
  - Typical expectation: once you control for internal scale/structure (size, velocity scale, luminosity/mass proxies, morphology/composition), the residual amplitude should be **primarily an intrinsic property** of the galaxy, with any environment dependence being **indirect** (via how environment alters the baryons through stripping, quenching, etc.).
  - What we test here: whether the fitted edge-amplitude proxy shows a clean residual dependence on a large-scale environment proxy after strong internal controls.
  - What we do *not* test here: the detailed field equations/mechanism for boundary-layer modes; we only use a one-parameter “edge amplitude” summary from a toy fit.

- **Temporal-Pressure Theory (TPT) / Overdensity Screening–Void Activation (OSA) style hypothesis:**
  - Core claim (as formulated in the TPT candidate document `KITCEY_R_D-2026_TPT_environment_responsive_temporal_geometry_v2.1.5.docx`): a single temporal potential Ψ is sourced by **density contrast** (baryons plus an explicit environment/void component) and is intended to be **environment-responsive**; the same Ψ is required to predict both **rotation curves and weak lensing**. The document explicitly frames “void-like vs overdense embeddings,” and notes possible extension to **overdensity screening / void activation** regimes.
  - Typical expectation: at fixed internal scale controls, the extra component should still show a **systematic dependence on environment** (e.g., denser environments suppress the extra amplitude).
  - What we test here: precisely that kind of “environment modulation at fixed internal controls,” albeit using a single environment proxy and a phenomenological edge-amplitude estimator.

So, in terms of discriminating power: **this analysis is much closer to a TPT/OSA discriminant** (environment modulation) than to a direct validation of the intrinsic-medium mechanism (which is mostly about *how* the extra component is generated internally).

Pragmatically: the SPARC-derived dataset and tooling you built originally grew out of the TPT environment-responsiveness idea, and we are reusing that infrastructure here to test whether an *environment signature* remains once we (a) compress each galaxy to an “edge amplitude” summary and (b) control internal scale.

**Key limitation relative to TPT v2.1.5:** TPT’s stated falsifiability hinge is *joint predictivity* (the same Ψ must fit **both** outer-disk dynamics **and** weak-lensing shear/convergence, with null diagnostics like cross-shear). This report does **not** execute that joint dynamics+lensing program. It only tests whether a **rotation-curve-derived phenomenological amplitude proxy** (`v_extra_asym_kms`) shows residual correlation with an environment proxy after internal controls.

### What we did (and why)
1) **Added an environment column to the SPARC summary table** so environment can be tested *on the same objects* as the toy-model fits.
  - Rationale: without a joined, per-galaxy environment measure, “environment vs edge amplitude” can’t be checked reproducibly.

2) **Removed the dominant internal scaling first**, because raw correlations are usually dominated by “big galaxies look different than small galaxies.”
  - We used OLS residualization on controls like `log(Vflat)` and `log(Rdisk)` (and later also `log(L36)` and morphology `T`).
  - Rationale: if an environment signal is real, it should show up *after* controlling for obvious internal scale covariates.

3) **Used permutation tests for p-values** rather than trusting asymptotic approximations.
  - Rationale: this is distribution-free and robust when variables are non-Gaussian or have outliers.

4) **Upgraded to partial correlation (`--partial`)** by residualizing *both* the target (`v_extra_asym_kms`) and the environment proxy on the same controls.
  - Rationale: if environment correlates with the controls, then residualizing only the target can exaggerate or distort the apparent association.

5) **Stress-tested the inference with stratified permutations** (shuffle only within bins).
  - Stratifying within `sparc_Q_flag` bins guards against “quality-mix” artifacts.
  - Stratifying within distance quantiles guards against distance-linked selection/systematics.
  - Stratifying within (`Q_flag` × distance) bins guards against both at once.
  - Rationale: if significance disappears under reasonable “like-with-like” shuffles, that’s strong evidence the signal is entangled with sample structure.

### What we found (bottom line)
Using the same control set throughout (controls: `1 + log(Vflat) + log(Rdisk) + log(L36) + T`, partial correlation, 20k permutations):

- The *measured* association is modest and negative (point estimate about Pearson r ≈ -0.20; Spearman ρ ≈ -0.18; N=135).
- If you permute environment **without distance stratification**, the association looks “statistically significant” at about the few-percent level.
- If you permute environment **within distance bins** (and especially within `Q_flag × distance` bins), the empirical significance largely disappears.

### What this implies for “intrinsic medium” vs TPT/OSA, specifically
- The sign of the point estimate (denser `delta_external` → smaller fitted `v_extra_asym_kms`) is **qualitatively consistent** with a screening-type narrative.
- However, the fact that significance **does not survive distance-aware stratified nulls** means we do *not* currently have robust evidence for a clean environment-responsive effect in this dataset/proxy.
- As a result, this environment test currently functions more as a **constraint on strong TPT/OSA-like claims** (at least with this proxy), while remaining **compatible** with an intrinsic-mechanics picture where environment effects are weak/indirect.
- Importantly: “compatible with intrinsic” is not the same as “evidence for intrinsic.” To support intrinsic mechanics positively, the more direct tests are the internal-structure/composition and predictive (CV) comparisons we ran elsewhere in this pipeline.

### What that means (and what it doesn’t)
- This is **not** decisive evidence for external screening.
- The result is best read as: *with this environment proxy, the apparent environment–edge link is sensitive to distance structure in the sample.*
- That sensitivity is exactly what you’d expect if the proxy and/or the usable SPARC subset carries distance-dependent selection, reconstruction uncertainty, or correlated systematics.

### Why it matters / potential applications
- **Model falsifiability:** this is a direct, reproducible test of whether “edge amplitude” is purely internal (scale/composition) or is modulated by environment.
- **Pipeline sanity-check:** stratified permutation is a practical guardrail against over-interpreting weak signals that are actually sample-structure artifacts.
- **Prioritizing follow-up data:** it identifies what to collect next (environment measures less distance-sensitive, e.g., group IDs/central-satellite tags/tidal indices) and how to evaluate them.
- **Manuscript framing:** you can legitimately claim you performed a stringent robustness ladder (controls → partial correlation → permutation → stratified permutation), and that the environment claim is currently *not robust* to distance-aware nulls.

## What we added

### Environment catalog staged in-workspace
- Input catalog: 2M++ density grid crossmatch (external repo source)
- Staged copy: toy_models/data/external_environment_twompp.csv

Key columns used:
- `delta_external`: density contrast proxy at the galaxy location
- `in_twompp_grid`: boolean flag for whether the position lies in the 2M++ grid

### Join into the summary table
We appended the environment columns onto the SPARC run summary:
- Output: toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv
- New columns:
  - `env_twompp_delta_external`
  - `env_twompp_in_twompp_grid`

Join method:
- Exact string match on `galaxy`.
- Join coverage was complete: **175/175** galaxies found in the environment CSV.

Scripts:
- toy_models/join_environment.py

## The actual statistical question we tested

### BASE controls definition
To remove the strongest “size/scale” dependence, we fit an OLS model on the selected sample:

\[
\text{BASE:}\quad v_\mathrm{extra} \sim 1 + \log(V_\mathrm{flat}) + \log(R_\mathrm{disk})
\]

where
- \(v_\mathrm{extra}\) is `v_extra_asym_kms`
- \(V_\mathrm{flat}\) is `sparc_Vflat_kms`
- \(R_\mathrm{disk}\) is `sparc_Rdisk_kpc`

Then we computed residuals:
\[
\varepsilon_i = v_{\mathrm{extra},i} - \widehat{v}_{\mathrm{extra},i}^{(\mathrm{BASE})}
\]

### Correlation test
We correlate \(\varepsilon\) with environment proxy `env_twompp_delta_external`:
- Pearson r
- Spearman ρ (tie-averaged ranks)

We also show the raw `v_extra_asym_kms` vs environment correlation as a reference.

Important sample detail:
- Even though the environment join covers all 175 galaxies, the regression requires finite `v_extra_asym_kms` and positive `Vflat` and `Rdisk` (because they are log-transformed), so the working sample is smaller.

Script:
- toy_models/analyze_env_residuals.py

## Results

### ALL usable rows (after BASE/log filtering)
Command:

```powershell
./.venv/Scripts/python.exe toy_models/analyze_env_residuals.py `
  --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv `
  --env-col env_twompp_delta_external
```

Output:
- N = 135
- Residuals vs environment:
  - Pearson: r = -0.2374 (p≈0.00557)
  - Spearman: ρ = -0.2165 (p≈0.0117)
- Raw y vs environment:
  - Pearson: r = -0.1626 (p≈0.0595)
  - Spearman: ρ = -0.1165 (p≈0.178)

**Observation:** controlling for `log(Vflat)` and `log(Rdisk)` *increases* the apparent environment association (raw → residual).
That suggests the environment proxy is not merely re-encoding the same size/velocity scaling captured by BASE.

#### Empirical p-values (permutation test)
We also ran a two-tailed permutation test (20,000 random shuffles of environment values) to avoid relying on asymptotic p-value approximations.

- Residuals vs environment:
  - Pearson: r = -0.2374, p_perm ≈ 0.0062
  - Spearman: ρ = -0.2165, p_perm ≈ 0.0131
- Raw y vs environment:
  - Pearson: r = -0.1626, p_perm ≈ 0.0607
  - Spearman: ρ = -0.1165, p_perm ≈ 0.177

### Quality-flag subset: `sparc_Q_flag == 1`
Command:

```powershell
./.venv/Scripts/python.exe toy_models/analyze_env_residuals.py `
  --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv `
  --env-col env_twompp_delta_external `
  --require-qflag 1
```

Output:
- N = 87
- Residuals vs environment:
  - Pearson: r = -0.1812 (p≈0.0931)
  - Spearman: ρ = -0.1357 (p≈0.21)
- Raw y vs environment:
  - Pearson: r = -0.0973 (p≈0.37)
  - Spearman: ρ = -0.0697 (p≈0.521)

**Observation:** the sign is consistent (negative), but the evidence is weaker in Q=1 and not conventionally significant.
This could mean (at least) one of:
- the effect is real but small and we’ve lost power at N=87,
- the effect is driven by lower-quality objects (or by systematics correlated with Q),
- or the environment proxy has increased noise/mismatch in the Q=1 subset (less likely, but possible).

#### Empirical p-values (permutation test)
- Residuals vs environment:
  - Pearson: r = -0.1812, p_perm ≈ 0.0944
  - Spearman: ρ = -0.1357, p_perm ≈ 0.212
- Raw y vs environment:
  - Pearson: r = -0.0973, p_perm ≈ 0.372
  - Spearman: ρ = -0.0697, p_perm ≈ 0.517

## Confounder checks: does the signal survive morphology/luminosity controls?

Because “environment” correlates with galaxy evolution history, we checked whether the residual–environment association survives adding a simple internal confounder to BASE.

### Add luminosity scale: `log(sparc_L36_1e9solLum)`

Model:
\[
v_\mathrm{extra} \sim 1 + \log(V_\mathrm{flat}) + \log(R_\mathrm{disk}) + \log(L_{3.6})
\]

ALL usable sample (N=135):
- Residuals vs environment:
  - Pearson: r = -0.1960, p_perm ≈ 0.0226
  - Spearman: ρ = -0.1807, p_perm ≈ 0.0383

Q=1 subset (N=87):
- Residuals vs environment:
  - Pearson: r = -0.1098, p_perm ≈ 0.317
  - Spearman: ρ = -0.0930, p_perm ≈ 0.390

**Takeaway:** in the full sample the signal persists but weakens; in Q=1 it largely disappears once L36 is added.
That points to either (i) a real but small effect entangled with mass/luminosity, or (ii) residual systematics that correlate with L36 and environment.

### Add morphology: `sparc_T`

Model:
\[
v_\mathrm{extra} \sim 1 + \log(V_\mathrm{flat}) + \log(R_\mathrm{disk}) + T
\]

ALL usable sample (N=135):
- Residuals vs environment:
  - Pearson: r = -0.2374, p_perm ≈ 0.00625
  - Spearman: ρ = -0.2160, p_perm ≈ 0.0132

Q=1 subset (N=87):
- Residuals vs environment:
  - Pearson: r = -0.1861, p_perm ≈ 0.0864
  - Spearman: ρ = -0.1420, p_perm ≈ 0.192

**Takeaway:** controlling for morphology type alone does not materially change the result.

## Partial-residual (partial correlation) check: control (Vflat, Rdisk, L36, T) simultaneously

The earlier “residual~env” tests residualized the *target only* (i.e., removed BASE from `v_extra_asym_kms`) and then correlated those residuals with the raw environment proxy.

To more cleanly ask “is there any association *beyond the shared dependence on controls*?”, we ran a **partial-residual** variant:
- regress `v_extra_asym_kms` on controls and take residuals
- regress `env_twompp_delta_external` on the same controls and take residuals
- correlate residual(target) vs residual(env)

Controls used:
\[
1 + \log(V_\mathrm{flat}) + \log(R_\mathrm{disk}) + \log(L_{3.6}) + T
\]

### Partial correlation (ALL usable sample)

Command:

```powershell
./.venv/Scripts/python.exe toy_models/analyze_env_residuals.py `
  --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv `
  --env-col env_twompp_delta_external `
  --partial `
  --base-features sparc_Vflat_kms sparc_Rdisk_kpc sparc_L36_1e9solLum sparc_T `
  --log-features sparc_Vflat_kms sparc_Rdisk_kpc sparc_L36_1e9solLum `
  --permute 20000 --perm-seed 0
```

Output:
- N = 135
- Partial (residualized y and env):
  - Pearson: r = -0.1986, p_perm ≈ 0.0209
  - Spearman: ρ = -0.1825, p_perm ≈ 0.0351

### Stratified permutation (guard against Q-flag mixing)

We also repeated the permutation test but **shuffled environment only within `sparc_Q_flag` bins**. This answers: “Would we still see this level of correlation if we preserve the quality-flag composition exactly?”

Command:

```powershell
./.venv/Scripts/python.exe toy_models/analyze_env_residuals.py `
  --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv `
  --env-col env_twompp_delta_external `
  --partial `
  --base-features sparc_Vflat_kms sparc_Rdisk_kpc sparc_L36_1e9solLum sparc_T `
  --log-features sparc_Vflat_kms sparc_Rdisk_kpc sparc_L36_1e9solLum `
  --permute 20000 --perm-seed 0 `
  --stratify-col sparc_Q_flag
```

Output:
- N = 135
- Partial (residualized y and env):
  - Pearson: r = -0.1986, p_perm ≈ 0.0192
  - Spearman: ρ = -0.1825, p_perm ≈ 0.0339

**Takeaway:** the environment association survives (at a modest level) after simultaneously controlling for Vflat, Rdisk, L36, and morphology T, and it also survives stratified permutation within Q bins. That makes it less likely that the ALL-sample signal is *purely* a Q-mixing artifact.

However, the fact that the signal is weak/non-significant within the Q=1-only subset remains an important caution for interpretation.

## Additional stratification stress-tests: morphology bins and distance bins

These tests ask whether the apparent partial correlation is being “carried” by a particular regime.
We keep the same partial-residual setup (controls: Vflat, Rdisk, L36, T), but we change the permutation scheme.

### Stratify permutations by early/late morphology bins (from `sparc_T`)

We stratify into two bins:
- **early** if `sparc_T <= 0`
- **late** if `sparc_T > 0`

Result (N=135):
- Partial residual correlation:
  - Pearson r = -0.1986, **p_perm ≈ 0.0222**
  - Spearman ρ = -0.1825, **p_perm ≈ 0.0363**

**Takeaway:** stratifying within early/late morphology bins does *not* remove the signal.

### Stratify permutations by distance quantile bins (`sparc_D_mpc`, q=4)

We stratify into 4 quantile bins in `sparc_D_mpc` on the post-filtered sample.

Result (N=135):
- Partial residual correlation:
  - Pearson r = -0.1986, **p_perm ≈ 0.182**
  - Spearman ρ = -0.1825, **p_perm ≈ 0.379**

**Takeaway:** when you only compare galaxies to other galaxies at similar distances (via within-bin shuffling), the empirical significance drops sharply.
That suggests the environment association is at least partly entangled with distance-dependent structure (selection effects, distance systematics, or properties correlated with distance in this sample).
It does not prove the effect is spurious, but it’s a strong caution flag for interpretation.

### Stratify permutations by both quality and distance: (`sparc_Q_flag` × distance quantiles, q=4)

To guard against *both* quality mixing and distance structure at the same time, we stratified the permutation into combined bins:
`Q_flag` (as discrete bins) crossed with 4 distance-quantile bins of `sparc_D_mpc`.

Result (N=135):
- Partial residual correlation:
  - Pearson r = -0.1986, **p_perm ≈ 0.214**
  - Spearman ρ = -0.1825, **p_perm ≈ 0.442**

**Takeaway:** once permutation shuffles are restricted to galaxies with similar distance *and* the same Q_flag, the empirical significance is largely gone.
This strengthens the interpretation that the apparent ALL-sample environment association is not cleanly separable from distance structure in the present dataset/proxy.

### One-line summary table (same controls, different permutation schemes)

Same setup in all rows:
- controls: `1 + log(Vflat) + log(Rdisk) + log(L36) + T`
- mode: `--partial` (residualize BOTH target and environment on controls)
- permutations: `n_perm=20000`, `seed=0`

| Permutation scheme | Pearson r | Pearson p_perm | Spearman ρ | Spearman p_perm |
|---|---:|---:|---:|---:|
| Unstratified | -0.1986 | 0.0209 | -0.1825 | 0.0351 |
| Stratified by `sparc_Q_flag` | -0.1986 | 0.0192 | -0.1825 | 0.0339 |
| Stratified by `sparc_D_mpc` quantiles (q=4) | -0.1986 | 0.182 | -0.1825 | 0.379 |
| Stratified by (`sparc_Q_flag` × `sparc_D_mpc` quantiles), q=4 | -0.1986 | 0.214 | -0.1825 | 0.442 |

Note: the point estimates (r, ρ) are identical here because stratification changes *only the null distribution* (the permutation scheme), not the computed correlation on the observed data.

## BASE+distance control variant (parametric distance control)

Because distance-entanglement was the dominant failure mode under stratified nulls, we also tested a *parametric* distance control directly in the regression stage.
We use the named preset `--preset base_plus_dist`:

- controls: `1 + log(Vflat) + log(Rdisk) + log(D_mpc)`
- mode: `--partial` (residualize BOTH target and environment on controls)
- permutations: `n_perm=20000`, `seed=0`

Observed point estimate on the same working sample (N=135):
- Pearson r = -0.2390
- Spearman ρ = -0.2251

### One-line summary table (BASE+distance, different permutation schemes)

| Permutation scheme | Pearson r | Pearson p_perm | Spearman ρ | Spearman p_perm |
|---|---:|---:|---:|---:|
| Unstratified | -0.2390 | 0.00585 | -0.2251 | 0.00985 |
| Stratified by `sparc_Q_flag` | -0.2390 | 0.00455 | -0.2251 | 0.00790 |
| Stratified by `sparc_D_mpc` quantiles (q=4) | -0.2390 | 0.0925 | -0.2251 | 0.235 |
| Stratified by (`sparc_Q_flag` × `sparc_D_mpc` quantiles), q=4 | -0.2390 | 0.0772 | -0.2251 | 0.209 |

**Takeaway:** adding distance as an explicit control does not remove the negative point estimate, and unstratified/Q-flag-stratified permutation still suggests a small p-value. But as before, **distance-aware stratified nulls greatly weaken the empirical significance**, reinforcing that distance/sample-structure issues remain the key interpretive constraint for this proxy.

## What might this mean physically (and what it does *not* mean)

### A conservative reading
The negative residual correlation can be read as:
- At fixed internal dynamical scale (Vflat, Rdisk), galaxies in denser external environments (higher `delta_external`) tend to have **slightly smaller** fitted edge-amplitude (`v_extra_asym_kms`) than expected.

That is **qualitatively compatible** with an “external screening / external field” picture where stronger external influence suppresses the extra component.

### But it is not uniquely diagnostic
This result alone does **not** decisively distinguish:
- external screening (environment-dependent physics)
from
- internal edge-response that is *also* correlated with environment indirectly (e.g., environment ↔ gas content, morphology, stripping history),
from
- analysis/systematic artifacts (distance systematics, selection effects, environment proxy uncertainties).

## Robustness and caveats

1) **p-values are approximate.**
   - Pearson p-values use the standard t-approximation.
   - Spearman p-values are also approximated via the same t formula on ρ, which is generally OK as a quick screen at N~O(100), but it is not exact.

2) **Sample restriction matters.**
   - Working N is set by finite `v_extra_asym_kms` and positive `Vflat`, `Rdisk` (log transforms).

3) **Environment proxy is one specific construction.**
   - `delta_external` comes from a particular 2M++ grid / distance inference pipeline; it is not the same as group membership or a tidal index.

4) **Possible confounding** not yet explicitly removed:
   - morphology (`sparc_T`), surface brightness (`sparc_SBdisk_solLum_pc2`), gas fraction (`sparc_MHI_1e9solMass`), luminosity (`sparc_L36_1e9solLum`), etc.

## Recommended next checks (high value, still stdlib-only)

To decide whether the above is “meaningful” in a publication sense, I’d do these next:

1) **Alternative environment measures** on the same sample:
   - group membership (group ID + central/satellite flag)
   - tidal index (e.g., \(\sum M_j/r_{ij}^3\) proxy)
   - nearest-neighbor density or projected density

2) **Confounder control** in the residualization stage:
   - extend BASE to include one more internal covariate at a time:
     - `log(sparc_L36_1e9solLum)`
     - `log(sparc_MHI_1e9solMass + const)` (or use finite-only subset)
     - `sparc_T`

3) **Permutation test** (exactly distribution-free):
   - shuffle env values across galaxies and recompute r/ρ to get an empirical p-value.

4) **Report split diagnostics**:
   - compare Field vs Group/Cluster categories if you provide group membership
   - examine whether the sign survives separately for gas-dominated vs bulge-dominated subsamples.

## Reproducibility notes

- Join command:
  - `./.venv/Scripts/python.exe toy_models/join_environment.py --summary toy_models/out_sparc_runs_full_with_composition/summary.csv --env toy_models/data/external_environment_twompp.csv --out toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv --prefix env_twompp_ --env-cols delta_external in_twompp_grid`

- Residual correlation commands:
  - ALL: `./.venv/Scripts/python.exe toy_models/analyze_env_residuals.py --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv --env-col env_twompp_delta_external`
  - Q=1: `./.venv/Scripts/python.exe toy_models/analyze_env_residuals.py --summary toy_models/out_sparc_runs_full_with_composition/summary_with_env.csv --env-col env_twompp_delta_external --require-qflag 1`

