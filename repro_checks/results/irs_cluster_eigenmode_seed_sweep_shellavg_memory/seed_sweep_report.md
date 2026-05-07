# IRS Cluster Eigenmode Seed Sweep

## Run Metadata
- Generated (UTC): 2026-04-06T00:47:29.667035+00:00
- Seed count: 8
- Base seed: 20260405
- Seed step: 10
- Satellites: 24
- ICM nodes: 16
- Max order: 5
- Radial points: 36

## Ensemble Summary
- Pass fraction: 0.000 (0/8)
- closure_r500_full: mean=0.8647, median=0.8692, p16=0.8558, p84=0.8757, min=0.8375, max=0.8785
- higher_mode_fraction_r500: mean=0.0357, median=0.0354, p16=0.0353, p84=0.0360, min=0.0352, max=0.0371
- baryon_fraction_r500: mean=0.1542, median=0.1533, p16=0.1525, p84=0.1555, min=0.1523, max=0.1589
- sigma_pred_r500: mean=722.8221, median=724.7232, p16=719.0789, p84=727.4318, min=711.3696, max=728.5741

## Fragile Gates
- higher_modes_non_negligible: failures=8/8 (1.000); seeds=20260405,20260415,20260425,20260435,20260445,20260455,20260465,20260475
- inner_profile_reasonable: failures=8/8 (1.000); seeds=20260405,20260415,20260425,20260435,20260445,20260455,20260465,20260475

## Extreme Seeds by R500 Closure
- low: seed=20260415 closure_r500_full=0.8375
- low: seed=20260475 closure_r500_full=0.8552
- low: seed=20260405 closure_r500_full=0.8599
- high: seed=20260465 closure_r500_full=0.8720
- high: seed=20260425 closure_r500_full=0.8763
- high: seed=20260435 closure_r500_full=0.8785

## Per-Seed Results
- seed=20260405 status=FAIL closure_r500_full=0.8599 higher_mode_fraction_r500=0.0358 baryon_fraction_r500=0.1550 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
- seed=20260415 status=FAIL closure_r500_full=0.8375 higher_mode_fraction_r500=0.0371 baryon_fraction_r500=0.1589 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
- seed=20260425 status=FAIL closure_r500_full=0.8763 higher_mode_fraction_r500=0.0353 baryon_fraction_r500=0.1525 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
- seed=20260435 status=FAIL closure_r500_full=0.8785 higher_mode_fraction_r500=0.0352 baryon_fraction_r500=0.1523 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
- seed=20260445 status=FAIL closure_r500_full=0.8705 higher_mode_fraction_r500=0.0353 baryon_fraction_r500=0.1528 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
- seed=20260455 status=FAIL closure_r500_full=0.8680 higher_mode_fraction_r500=0.0356 baryon_fraction_r500=0.1538 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
- seed=20260465 status=FAIL closure_r500_full=0.8720 higher_mode_fraction_r500=0.0353 baryon_fraction_r500=0.1527 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
- seed=20260475 status=FAIL closure_r500_full=0.8552 higher_mode_fraction_r500=0.0361 baryon_fraction_r500=0.1555 failed_gates=higher_modes_non_negligible|inner_profile_reasonable
