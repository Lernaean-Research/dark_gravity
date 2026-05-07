# Result-Dependent Comparison Protocol (Framework-Agnostic)

## Principle

Only **outcome-dependent** comparison is admissible.
No framework receives credit from mechanistic narrative, elegance, or prior preference.
All models are judged only by predictive performance on the same data pipeline.

## GR Gap Ledger (Scale By Scale)

This protocol tracks the empirically inferred gravity gap for
$GR +$ observed baryons only.
The intent is descriptive, not polemical: quantify what must be closed before
claiming framework success.

### Definitions

- Acceleration-form gap:
  $D_g(r) = g_{\mathrm{obs}}(r) / g_{\mathrm{bar}}(r)$
- Mass-form gap:
  $D_M(<r) = M_{\mathrm{dyn}}(<r) / M_{\mathrm{bar}}(<r)$
- Equivalent deficit fraction:
  $f_{\mathrm{def}} = 1 - 1/D$

$D = 1$ means no baryons-only gap. $D > 1$ means additional effective gravity
is required in that regime.

### Regime Snapshot (Indicative)

| Regime | Typical gap metric | Indicative $D$ range | $f_{\mathrm{def}}$ | Robust rationale |
| --- | --- | --- | --- | --- |
| Solar system / strong local tests | $D_g$ | ${\sim}1$ | ${\sim}0\%$ | Precision ephemerides, light deflection, timing, and compact-object tests are accurately reproduced with observed baryonic source terms, leaving no measurable missing-gravity requirement at these scales. |
| Disk-galaxy outer regions | $D_g$ or $D_M$ | ${\sim}2\text{--}10$ | ${\sim}50\text{--}90\%$ | Rotation curves remain elevated above baryons-only Newtonian/GR expectations in outer disks, with deficit strength varying systematically with local acceleration and surface density. |
| Galaxy groups | $D_M$ | ${\sim}3\text{--}10$ | ${\sim}67\text{--}90\%$ | Dynamical mass indicators (velocity dispersion and weak-lensing anchored masses where available) exceed stellar+gas budgets, placing groups between galaxy and rich-cluster regimes as a transition anchor. |
| Rich clusters (near $r_{500}$) | $D_M$ | ${\sim}5\text{--}7$ | ${\sim}80\text{--}86\%$ | Joint X-ray, lensing, and dynamical reconstructions consistently yield total gravitating masses well above hot-gas+stellar baryon inventories. |
| Cluster mergers | morphological | N/A | — | Spatial offset of strong/weak lensing centroid from X-ray emission peak in merging systems provides a geometry-independent gap indicator, free from dynamical-equilibrium assumptions. |
| Background cosmology | $\Omega_m/\Omega_b$ | ${\sim}6.3$ | ${\sim}84\%$ | Global parameter inference from CMB+BAO+LSS requires matter density substantially above baryonic density, producing a cosmic-budget deficit analogue of the cluster-scale gap. |

These are order-of-magnitude guideposts for consistent framework scoring.
For formal comparisons, always compute dataset-specific values with the same
selection, masks, and covariance model used in the fit pipeline.

## Non-Negotiable Rules

1. Same data split for all frameworks.
2. Same preprocessing, masks, and QC filters.
3. Same likelihood function and error model.
4. Same nuisance-parameter treatment policy.
5. Predictions generated before scoring (no post-hoc retuning on test set).
6. Final ranking based only on predefined metrics.

## Required Outputs Per Framework

- Point predictions for each observable.
- Predictive uncertainty (or calibrated surrogate if unavailable).
- Per-object residuals.
- Total objective score.

## Mandatory Metrics

Primary (must report):

- Held-out RMSE (or MAE) on key observables.
- Predictive log-likelihood (test set).
- Information criterion (AIC/BIC or WAIC, depending on setup).

Secondary (recommended):

- Calibration error of uncertainty bands.
- Residual trend slope vs mass/radius/redshift.
- Robustness under bootstrap / cross-validation folds.

## Decision Rule

Framework A is preferred over Framework B only if:

- A beats B on primary metrics under the same split, and
- the improvement survives uncertainty/robustness checks.

If metrics are statistically indistinguishable, declare a tie.

## Prohibited Claims

- "Model X is better because mechanism is more physical" (without score advantage).
- "Model X wins due to parameter interpretability" (without score advantage).
- Any claim of superiority not grounded in held-out performance.

## Reporting Template

Use one table with rows = frameworks and columns = metrics.
Include only quantitative outcomes plus uncertainty.
Narrative discussion must follow table and cannot override ranking.

## Current Workstream Labeling Requirement

Any IRS-reference normalized diagnostic is tagged:

- "Diagnostic normalization only"
- "Not a mechanism-level head-to-head comparison"

This prevents conflation with framework ranking.
