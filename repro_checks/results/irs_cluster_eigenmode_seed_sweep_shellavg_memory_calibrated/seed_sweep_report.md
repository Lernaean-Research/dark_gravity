# IRS Cluster Eigenmode Seed Sweep

## Run Metadata
- Generated (UTC): 2026-04-06T00:48:05.114427+00:00
- Seed count: 8
- Base seed: 20260405
- Seed step: 10
- Satellites: 24
- ICM nodes: 16
- Max order: 5
- Radial points: 36

## Ensemble Summary
- Pass fraction: 0.500 (4/8)
- closure_r500_full: mean=1.0937, median=1.0995, p16=1.0821, p84=1.1079, min=1.0586, max=1.1114
- higher_mode_fraction_r500: mean=0.0505, median=0.0501, p16=0.0499, p84=0.0509, min=0.0497, max=0.0524
- baryon_fraction_r500: mean=0.1219, median=0.1212, p16=0.1206, p84=0.1229, min=0.1204, max=0.1257
- sigma_pred_r500: mean=812.9038, median=815.0898, p16=808.6172, p84=818.1927, min=799.7674, max=819.4818

## Fragile Gates
- higher_modes_non_negligible: failures=4/8 (0.500); seeds=20260425,20260435,20260445,20260465

## Extreme Seeds by R500 Closure
- low: seed=20260415 closure_r500_full=1.0586
- low: seed=20260475 closure_r500_full=1.0814
- low: seed=20260405 closure_r500_full=1.0875
- high: seed=20260465 closure_r500_full=1.1031
- high: seed=20260425 closure_r500_full=1.1086
- high: seed=20260435 closure_r500_full=1.1114

## Per-Seed Results
- seed=20260405 status=PASS closure_r500_full=1.0875 higher_mode_fraction_r500=0.0506 baryon_fraction_r500=0.1226 failed_gates=none
- seed=20260415 status=PASS closure_r500_full=1.0586 higher_mode_fraction_r500=0.0524 baryon_fraction_r500=0.1257 failed_gates=none
- seed=20260425 status=FAIL closure_r500_full=1.1086 higher_mode_fraction_r500=0.0499 baryon_fraction_r500=0.1206 failed_gates=higher_modes_non_negligible
- seed=20260435 status=FAIL closure_r500_full=1.1114 higher_mode_fraction_r500=0.0497 baryon_fraction_r500=0.1204 failed_gates=higher_modes_non_negligible
- seed=20260445 status=FAIL closure_r500_full=1.1012 higher_mode_fraction_r500=0.0499 baryon_fraction_r500=0.1208 failed_gates=higher_modes_non_negligible
- seed=20260455 status=PASS closure_r500_full=1.0979 higher_mode_fraction_r500=0.0503 baryon_fraction_r500=0.1216 failed_gates=none
- seed=20260465 status=FAIL closure_r500_full=1.1031 higher_mode_fraction_r500=0.0499 baryon_fraction_r500=0.1207 failed_gates=higher_modes_non_negligible
- seed=20260475 status=PASS closure_r500_full=1.0814 higher_mode_fraction_r500=0.0510 baryon_fraction_r500=0.1230 failed_gates=none
