# First-Principles IRS Cluster Eigenmode Toy Model

## Run Metadata
- Generated (UTC): 2026-04-06T00:31:00.454338+00:00
- Seed: 20260425
- Input anchor CSV: D:\#Documents\#Publication\Spacetime_Mechanics\repro_checks\cluster_mass_summary.csv
- Input SHA256: b7784c1fd5dd1384c173704b5a091d182bafd99446ec8acb587091956517fc4c
- Median anchor redshift: 0.2240
- Anchor M500: 4.743319e+14 Msun
- Anchor Mbar: 6.403480e+13 Msun
- Derived R500: 1124.71 kpc
- Satellites: 24
- ICM nodes: 16
- Max eigenmode order: 5

## Key Cluster-Scale Metrics
- Closure at R500, ground mode only: 1.197
- Closure at R500, full eigenmode sum: 1.252
- Higher-mode fraction at R500: 0.049
- Predicted sigma at R500: 869.6 km/s
- Anchor sigma: 747.7 km/s
- Baryon fraction at R500: 0.109

## Gate Summary
- higher_modes_non_negligible: FAIL; value=0.0491; criterion=0.05 <= higher_mode_fraction(R500) <= 0.55
- closure_improves_with_modes: PASS; value=0.0548; criterion=closure_full(R500) > closure_ground(R500)
- cluster_scale_closure: FAIL; value=1.2516; criterion=0.65 <= closure_full(R500) <= 1.20
- inner_profile_reasonable: PASS; value=0.7362; criterion=0.65 <= closure_full(0.5 R500) <= 1.35
- outer_profile_not_divergent: PASS; value=1.3728; criterion=0.50 <= closure_full(1.4 R500) <= 1.50
- baryon_fraction_physical: PASS; value=0.1086; criterion=0.10 <= f_b(R500) <= 0.22
- velocity_dispersion_anchor: PASS; value=869.6482; criterion=|sigma_pred - sigma_anchor| / sigma_anchor <= 0.25

## Source Ensemble Summary
- Mean eta_eff (gas nodes): 0.371
- Mean eta_eff (galaxies): 0.397
- Mean eta_eff (all sources): 0.387

## Artifacts
- toy_cluster_sources.csv
- toy_cluster_profile.csv
- toy_cluster_summary.json
- toy_cluster_report.md
