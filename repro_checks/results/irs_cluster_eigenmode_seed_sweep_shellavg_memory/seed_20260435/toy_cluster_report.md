# First-Principles IRS Cluster Eigenmode Toy Model

## Run Metadata
- Generated (UTC): 2026-04-06T00:47:21.093036+00:00
- Seed: 20260435
- Input anchor CSV: D:\#Documents\#Publication\Spacetime_Mechanics\repro_checks\cluster_mass_summary.csv
- Input SHA256: b7784c1fd5dd1384c173704b5a091d182bafd99446ec8acb587091956517fc4c
- Median anchor redshift: 0.2240
- Anchor M500: 4.743319e+14 Msun
- Anchor Mbar: 6.403480e+13 Msun
- Derived R500: 1124.71 kpc
- Satellites: 24
- ICM nodes: 16
- Max eigenmode order: 5

- Shell directions per radius: 48

- Time-memory enabled: True
- tau_mem (Myr): 900.0
- assembly_time(R500) (Myr): 3200.0
- assembly_alpha: 0.700
- mode_tau_power: 1.100

## Key Cluster-Scale Metrics
- Closure at R500, ground mode only: 0.852
- Closure at R500, full eigenmode sum: 0.878
- Higher-mode fraction at R500: 0.035
- Mean memory factor at R500: 0.436
- Predicted sigma at R500: 728.6 km/s
- Anchor sigma: 747.7 km/s
- Baryon fraction at R500: 0.152

## Gate Summary
- higher_modes_non_negligible: FAIL; value=0.0352; criterion=0.05 <= higher_mode_fraction(R500) <= 0.55
- closure_improves_with_modes: PASS; value=0.0262; criterion=closure_full(R500) > closure_ground(R500)
- cluster_scale_closure: PASS; value=0.8785; criterion=0.65 <= closure_full(R500) <= 1.20
- inner_profile_reasonable: FAIL; value=0.4868; criterion=0.65 <= closure_full(0.5 R500) <= 1.35
- outer_profile_not_divergent: PASS; value=1.0384; criterion=0.50 <= closure_full(1.4 R500) <= 1.50
- baryon_fraction_physical: PASS; value=0.1523; criterion=0.10 <= f_b(R500) <= 0.22
- velocity_dispersion_anchor: PASS; value=728.5741; criterion=|sigma_pred - sigma_anchor| / sigma_anchor <= 0.25

## Source Ensemble Summary
- Mean eta_eff (gas nodes): 0.370
- Mean eta_eff (galaxies): 0.392
- Mean eta_eff (all sources): 0.384

## Artifacts
- toy_cluster_sources.csv
- toy_cluster_profile.csv
- toy_cluster_summary.json
- toy_cluster_report.md
