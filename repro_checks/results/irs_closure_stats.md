# IRS Closure Fraction Diagnostic: SPARC Galaxies -> PSZ2 Clusters
Generated: 2026-04-05 23:44

## Scope Guardrail

This file reports an IRS-reference normalized diagnostic ratio for IRS outputs.
It is not a mechanism-level comparison between IRS and any competing framework.
Only data-processing assumptions are shared; physics remains model-local.

## Definition

    closure = Q1_IRS / Q1_ref     [Q1_ref = sqrt(G * M_bar * a_irs)]

- Galaxies (SPARC): Q1_IRS = q_best_kms2  (fitted IRS amplitude)
- Clusters (PSZ2):  Q1_IRS = sigma^2 - G*M_bar/R500  (observed extra velocity^2)

Diagnostic reference line: closure = 1.0 corresponds to exact match to the
chosen IRS internal normalization. This does not imply framework identity.

## Key Numerical Results

| Quantity | Value |
|---|---|
| Galaxy sample | SPARC 175 (quality-cut: 175) |
| Cluster sample | PSZ2 (quality-cut: 1094) |
| Galaxy median closure | **0.882** |
| Cluster mean closure | **0.2790 +/- 0.0165** |
| Cluster/galaxy ratio | **0.316 (31.6%)** |
| Log10 gap (dex) | **0.50 dex** |
| M_bar range spanned | 4.1 decades |

## Cross-Scale Regression (log10 space)

    log10(closure) = -0.0793 * log10(M_bar) + 0.5384
    R^2 = 0.0680,   p = 3.48e-21

Galaxy-only slope: -0.0207 +/- 0.0927  (R^2=0.0003, p=0.823)
Consistent with flat BTFR within galaxy sample (no mass-scale trend within galaxies).

## Physical Interpretation

- Galaxy scale (10^8-10^11 M_sun): closure ~ 0.88
  IRS-fitted q_best tracks the IRS reference amplitude closely.

- Cluster scale (10^13-10^14 M_sun): closure ~ 0.279
  Under this IRS normalization, IRS-inferred cluster extra velocity is lower
  than the normalization target by ~72%.

- The 0.50 dex gap across 4.1 decades in M_bar sets the
  empirical target for any IRS extension mechanism at cluster scales.

## Data Provenance

- Galaxies: Lelli+2016 SPARC J/AJ/152/157; IRS fits: IRS-II v5.1 (Kitcey2026IRS2)
- Clusters: Planck Collaboration 2016 PSZ2 J/A+A/594/A27  (1094 clusters)
- sigma-M scaling: Munari+2013
- M_bar from f_bar = 0.135 * M_500 (Ettori+2017)
- R_500 assumed 1000 kpc for G*M_bar/R estimation
- Fetched via astroquery.vizier on 2026-04-05

## Next Step For Fair Head-to-Head Testing

Run two independent forward lanes with identical data and likelihood plumbing:
1. IRS-forward predictions only
2. Comparator-framework forward predictions only
Then compare fit statistics (AIC/BIC/WAIC/log-evidence, held-out RMSE).
