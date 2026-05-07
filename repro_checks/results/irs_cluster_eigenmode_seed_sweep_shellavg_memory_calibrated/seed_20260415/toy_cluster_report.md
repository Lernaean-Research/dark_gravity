# First-Principles IRS Cluster Eigenmode Toy Model

## Run Metadata
- Generated (UTC): 2026-04-06T00:47:51.078817+00:00
- Seed: 20260415
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
- tau_mem (Myr): 250.0
- assembly_time(R500) (Myr): 4200.0
- assembly_alpha: 0.500
- mode_tau_power: 0.350

## Key Cluster-Scale Metrics
- Closure at R500, ground mode only: 1.010
- Closure at R500, full eigenmode sum: 1.059
- Higher-mode fraction at R500: 0.052
- Mean memory factor at R500: 0.915
- Predicted sigma at R500: 799.8 km/s
- Anchor sigma: 747.7 km/s
- Baryon fraction at R500: 0.126

## Gate Summary
- higher_modes_non_negligible: PASS; value=0.0524; criterion=0.05 <= higher_mode_fraction(R500) <= 0.55
- closure_improves_with_modes: PASS; value=0.0485; criterion=closure_full(R500) > closure_ground(R500)
- cluster_scale_closure: PASS; value=1.0586; criterion=0.65 <= closure_full(R500) <= 1.20
- inner_profile_reasonable: PASS; value=0.6935; criterion=0.65 <= closure_full(0.5 R500) <= 1.35
- outer_profile_not_divergent: PASS; value=1.1985; criterion=0.50 <= closure_full(1.4 R500) <= 1.50
- baryon_fraction_physical: PASS; value=0.1257; criterion=0.10 <= f_b(R500) <= 0.22
- velocity_dispersion_anchor: PASS; value=799.7674; criterion=|sigma_pred - sigma_anchor| / sigma_anchor <= 0.25

## Source Ensemble Summary
- Mean eta_eff (gas nodes): 0.371
- Mean eta_eff (galaxies): 0.416
- Mean eta_eff (all sources): 0.398

## Artifacts
- toy_cluster_sources.csv
- toy_cluster_profile.csv
- toy_cluster_summary.json
- toy_cluster_report.md
