# Joint SPARC + Cluster (HFF) results and implications

This report stitches together two layers of evidence already generated in this repository:

- **Galaxy scale (SPARC)**: one-parameter extra-term toy fits to rotation curves, plus derived atlas diagnostics.
- **Cluster scale (HFF)**: a preregistered morphology operator comparing Frontier Fields κ to a Chandra img2 proxy stack.

It is intended as a *project-level* synthesis for the **intrinsic spacetime response** effective-source / CDM-candidate thesis: what the current measurements support, what they do not, and what would falsify key claims.

## Executive results (recomputed from CSV artifacts)

### SPARC: nested Δχ² diagnostic for the extra term (1 additional parameter)

We recompute a per-galaxy nested-model diagnostic using the per-radius curves: "baryons-only" (v_bar) vs "baryons+extra" (v_model), with Δχ² = χ²_bar − χ²_model and 1 dof survival p ≈ erfc(√(Δχ²/2)).

- Curve files read: **175**
- Rated galaxies (finite Δχ²): **175**
- Δχ² summary: median=1.33e+03, IQR=4.98e+03, min=-1.39e-08, max=3.16e+05
- Classification counts (by p-value):
  - very-strong: 161
  - strong: 5
  - moderate: 3
  - weak: 4
  - no-improvement: 2
  - unrated: 0

### SPARC: fitted edge-amplitude proxy and Q summary

- v_extra_asym_kms (edge-amplitude proxy): N=175, median=88.8 km/s, IQR=69.1, range=[0.000588,365]
- q_best_kms2 (fit parameter): N=175, median=7.88e+03 (km/s)^2, IQR=1.31e+04

### SPARC: strongest composition/structure correlations with edge amplitude (from pipeline table)

| x                      | y                |   n |   pearson_r |   spearman_rho |
|:-----------------------|:-----------------|----:|------------:|---------------:|
| sparc_L36_1e9solLum    | v_extra_asym_kms | 175 |    0.761272 |       0.84887  |
| sparc_L36_1e9solLum    | q_best_kms2      | 175 |    0.744119 |       0.84887  |
| sparc_MHI_1e9solMass   | v_extra_asym_kms | 175 |    0.619439 |       0.768595 |
| sparc_MHI_1e9solMass   | q_best_kms2      | 175 |    0.553114 |       0.768595 |
| sparc_SBeff_solLum_pc2 | v_extra_asym_kms | 175 |    0.615296 |       0.738424 |
| sparc_SBeff_solLum_pc2 | q_best_kms2      | 175 |    0.563238 |       0.738424 |
| sparc_L36_1e9solLum    | r_t_kpc          | 175 |    0.815206 |       0.677646 |
| sparc_Rdisk_kpc        | q_best_kms2      | 175 |    0.522121 |       0.668643 |
| sparc_Rdisk_kpc        | v_extra_asym_kms | 175 |    0.5939   |       0.668643 |
| sparc_Rdisk_kpc        | r_t_kpc          | 175 |    0.653203 |       0.664664 |

### HFF: κ–X-ray centroid separations at ROI = 100" (across teams)

Abell 2744 (11 teams):

|   level_pct |   n |   median |     q25 |     q75 |     iqr |     min |     max |   range |
|------------:|----:|---------:|--------:|--------:|--------:|--------:|--------:|--------:|
|          99 |  11 |  67.3755 | 67.0748 | 68.4981 | 1.42324 | 39.7875 | 78.0632 | 38.2757 |
|          97 |  11 |  65.9525 | 65.7064 | 66.881  | 1.17466 | 46.0896 | 68.704  | 22.6144 |
|          95 |  11 |  66.371  | 65.578  | 67.07   | 1.49198 | 50.7205 | 68.7113 | 17.9908 |

MACS J0416.1−2403 (12 teams):

|   level_pct |   n |   median |      q25 |     q75 |      iqr |      min |     max |   range |
|------------:|----:|---------:|---------:|--------:|---------:|---------:|--------:|--------:|
|          99 |  12 |  41.6627 |  7.31982 | 44.7641 | 37.4443  |  4.51144 | 45.8547 | 41.3433 |
|          97 |  12 |  27.8584 | 24.5955  | 44.597  | 20.0015  | 23.5515  | 50.5803 | 27.0288 |
|          95 |  12 |  15.835  | 14.7686  | 17.3633 |  2.59469 | 12.7056  | 34.8225 | 22.1169 |

### HFF: ROI-radius sensitivity (medians across teams; all radii in the grid)

Abell 2744:

|   roi_radius_arcsec |   level_pct |   n |   median |     iqr |     min |     max |
|--------------------:|------------:|----:|---------:|--------:|--------:|--------:|
|                  80 |          99 |  11 |  66.9351 | 2.35998 | 40.6905 | 76.5354 |
|                  80 |          97 |  11 |  66.8369 | 1.39389 | 44.7389 | 68.7774 |
|                  80 |          95 |  11 |  66.2088 | 1.39121 | 50.4259 | 68.0149 |
|                 100 |          99 |  11 |  67.3755 | 1.42324 | 39.7875 | 78.0632 |
|                 100 |          97 |  11 |  65.9525 | 1.17466 | 46.0896 | 68.704  |
|                 100 |          95 |  11 |  66.371  | 1.49198 | 50.7205 | 68.7113 |
|                 120 |          99 |  11 |  67.4195 | 2.17669 | 38.6534 | 85.8223 |
|                 120 |          97 |  11 |  67.1015 | 2.02768 | 51.0009 | 69.8565 |
|                 120 |          95 |  11 |  54.5096 | 2.33469 | 41.5443 | 56.9544 |

MACS J0416.1−2403:

|   roi_radius_arcsec |   level_pct |   n |   median |      iqr |      min |     max |
|--------------------:|------------:|----:|---------:|---------:|---------:|--------:|
|                  80 |          99 |  12 |  43.5891 | 13.5935  |  4.45372 | 61.7835 |
|                  80 |          97 |  12 |  28.8971 | 19.9536  | 24.0567  | 64.4358 |
|                  80 |          95 |  12 |  26.4484 |  2.67074 | 24.0087  | 48.7384 |
|                 100 |          99 |  12 |  41.6627 | 37.4443  |  4.51144 | 45.8547 |
|                 100 |          97 |  12 |  27.8584 | 20.0015  | 23.5515  | 50.5803 |
|                 100 |          95 |  12 |  15.835  |  2.59469 | 12.7056  | 34.8225 |
|                 120 |          99 |  12 |  37.1138 | 25.0585  |  4.99747 | 45.7495 |
|                 120 |          97 |  12 |  18.6211 | 20.0863  | 14.3337  | 35.7855 |
|                 120 |          95 |  12 |  11.8152 |  2.83491 |  6.53101 | 30.8787 |

## Interpretation: what these results do and do not establish

### What SPARC contributes to the intrinsic-response/CDM-candidate thesis

At galaxy scale, the toy pipeline establishes a consistent *phenomenological* fact pattern: across a large fraction of SPARC objects, a **single extra amplitude parameter** (encoded as q_best or v_extra_asym) improves the weighted fit over baryons-only under a simple nested Δχ² diagnostic.

Project meaning: this supports the claim that an **effective additional source/response term** is empirically demanded by the rotation-curve sector, in a way that is (i) not limited to a small subset of galaxies and (ii) strongly structured by galaxy properties (see correlation table).

What it does *not* establish by itself: whether the extra term is a particle dark matter halo, a modified gravity law, or an intrinsic medium/metric response. SPARC here is evidence for a *required extra phenomenological component*, not a unique mechanism.

### What HFF contributes

At cluster scale, the preregistered κ–X-ray morphology operator measures **centroid separations** between a lensing response proxy (κ) and a gas proxy (Chandra img2 stack), while explicitly quantifying κ-model systematics (multi-team) and ROI sensitivity.

Project meaning: the cluster results provide a cross-domain constraint on any CDM-candidate story: a viable candidate must accommodate (a) mergers where mass-tracing (κ) and gas-tracing (X-ray) morphologies can be displaced, and (b) the observed level of robustness/sensitivity under model systematics and threshold choice.

### Cross-scale synthesis (how they fit together)

A coherent intrinsic-response-as-CDM-candidate narrative needs both:
- a galaxy-scale **equilibrium mapping** (SPARC) where the extra response term tracks internal structure in a simple, compressible way; and
- a cluster-scale **non-equilibrium morphology behavior** (HFF/Bullet) where response vs gas can be displaced, with uncertainties explicitly propagated via κ team spread.

The current artifacts support the *methodological* program (fixed operator, robustness ladders, explicit systematics), and they supply *nontrivial constraints* on environment-responsiveness claims (see environment proxy report).

## Robust implications for the intrinsic spacetime response CDM-candidate thesis

### Supports (in the limited, operational sense)
- **Compressibility at galaxy scale**: A one-parameter extra amplitude is frequently sufficient to materially improve rotation-curve fits; this is compatible with an intrinsic-response sector that is not arbitrarily high-dimensional per galaxy.
- **Structured dependence on internal properties**: Strong correlations of v_extra/q with luminosity, morphology, and composition fractions support the view that the extra term is tied to baryonic structure rather than being pure noise.
- **Non-equilibrium cluster morphology is testable with the same operator**: The HFF results quantify κ–gas offsets in a way that is directly comparable across systems and lens-model teams.

### Challenges / failure modes
- **Mechanism underdetermination**: The same SPARC phenomenology can be fit by multiple classes of models; without additional predictions (e.g., lensing/shear nulls, external-field dependence, cross-sample out-of-domain forecasts), it does not uniquely favor an intrinsic-medium explanation.
- **Environment-responsiveness is not yet robust**: the dedicated analysis in [toy_models/ENVIRONMENT_PROXY_RESIDUALS_REPORT.md](toy_models/ENVIRONMENT_PROXY_RESIDUALS_REPORT.md) finds a modest negative association that does not survive distance-aware stratified nulls; strong OSA/screening claims are therefore constrained by the current proxy/data.
- **Operator sensitivity exists**: cluster separations can be threshold/ROI dependent and κ-team dependent; any thesis claim should be phrased in terms of distributions (with systematics), not single-number offsets.

### What would strengthen or falsify
- Strengthen: show that a *single calibrated response law* (fit on SPARC) predicts cluster observables beyond centroid offsets (e.g., shear patterns, between-ness with a collisionless proxy) with correct null diagnostics.
- Falsify: show systematic failure of the response law in out-of-sample galaxies, or inability to accommodate observed cluster morphology under controlled operator choices without ad hoc retuning.

## Pointers to the primary artifacts in this repo

- SPARC atlas report: [toy_models/DYED_SPACETIME_ATLAS_REPORT.md](toy_models/DYED_SPACETIME_ATLAS_REPORT.md)
- SPARC environment proxy report: [toy_models/ENVIRONMENT_PROXY_RESIDUALS_REPORT.md](toy_models/ENVIRONMENT_PROXY_RESIDUALS_REPORT.md)
- SPARC→clusters operator definition: [toy_models/PREDICTIONS_SPARC_TO_CLUSTERS.md](toy_models/PREDICTIONS_SPARC_TO_CLUSTERS.md)
- HFF all-teams systematics analysis: [toy_models/HFF_ALL_TEAMS_SYSTEMATICS_ANALYSIS.md](toy_models/HFF_ALL_TEAMS_SYSTEMATICS_ANALYSIS.md)

### Six-panel HFF figures (ROI=100")

- Abell 2744 figures (11 PNGs): toy_models/out_predictions/figures/systematics_sixpanel/abell2744
  - [abell2744_bradac_v2_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_bradac_v2_roi100_sixpanel.png)
  - [abell2744_cats_v4.1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_cats_v4.1_roi100_sixpanel.png)
  - [abell2744_diego_v4.1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_diego_v4.1_roi100_sixpanel.png)
  - [abell2744_glafic_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_glafic_v4_roi100_sixpanel.png)
  - [abell2744_keeton_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_keeton_v4_roi100_sixpanel.png)
  - [abell2744_merten_v1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_merten_v1_roi100_sixpanel.png)
  - [abell2744_sharon_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_sharon_v4_roi100_sixpanel.png)
  - [abell2744_williams_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_williams_v4_roi100_sixpanel.png)
  - [abell2744_zitrin-ltm-gauss_v3_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_zitrin-ltm-gauss_v3_roi100_sixpanel.png)
  - [abell2744_zitrin-ltm_v1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_zitrin-ltm_v1_roi100_sixpanel.png)
  - [abell2744_zitrin-nfw_v3_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/abell2744/abell2744_zitrin-nfw_v3_roi100_sixpanel.png)
- MACS J0416.1−2403 figures (12 PNGs): toy_models/out_predictions/figures/systematics_sixpanel/macs0416
  - [macs0416_bradac_v3_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_bradac_v3_roi100_sixpanel.png)
  - [macs0416_caminha_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_caminha_v4_roi100_sixpanel.png)
  - [macs0416_cats_v4.1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_cats_v4.1_roi100_sixpanel.png)
  - [macs0416_diego_v4.1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_diego_v4.1_roi100_sixpanel.png)
  - [macs0416_glafic_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_glafic_v4_roi100_sixpanel.png)
  - [macs0416_keeton_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_keeton_v4_roi100_sixpanel.png)
  - [macs0416_merten_v1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_merten_v1_roi100_sixpanel.png)
  - [macs0416_sharon_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_sharon_v4_roi100_sixpanel.png)
  - [macs0416_williams_v4_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_williams_v4_roi100_sixpanel.png)
  - [macs0416_zitrin-ltm-gauss_v3_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_zitrin-ltm-gauss_v3_roi100_sixpanel.png)
  - [macs0416_zitrin-ltm_v1_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_zitrin-ltm_v1_roi100_sixpanel.png)
  - [macs0416_zitrin-nfw_v3_roi100_sixpanel.png](toy_models/out_predictions/figures/systematics_sixpanel/macs0416/macs0416_zitrin-nfw_v3_roi100_sixpanel.png)
