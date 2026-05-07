# IRS Cluster Eigenmode Seed Sweep

## Run Metadata
- Generated (UTC): 2026-04-06T00:31:46.336320+00:00
- Seed count: 12
- Base seed: 20260405
- Seed step: 10
- Satellites: 24
- ICM nodes: 16
- Max order: 5
- Radial points: 36

## Ensemble Summary
- Pass fraction: 0.667 (8/12)
- closure_r500_full: mean=1.1930, median=1.1824, p16=1.1623, p84=1.2443, min=1.1354, max=1.2616
- higher_mode_fraction_r500: mean=0.0509, median=0.0512, p16=0.0491, p84=0.0520, min=0.0486, max=0.0531
- baryon_fraction_r500: mean=0.1121, median=0.1128, p16=0.1086, p84=0.1141, min=0.1076, max=0.1166
- sigma_pred_r500: mean=848.9099, median=845.2536, p16=838.0147, p84=867.0871, min=828.2954, max=873.0933

## Fragile Gates
- cluster_scale_closure: failures=4/12 (0.333); seeds=20260425,20260435,20260465,20260515
- higher_modes_non_negligible: failures=3/12 (0.250); seeds=20260425,20260435,20260465

## Extreme Seeds by R500 Closure
- low: seed=20260405 closure_r500_full=1.1354
- low: seed=20260455 closure_r500_full=1.1424
- low: seed=20260485 closure_r500_full=1.1686
- high: seed=20260435 closure_r500_full=1.2401
- high: seed=20260465 closure_r500_full=1.2575
- high: seed=20260425 closure_r500_full=1.2616

## Per-Seed Results
- seed=20260405 status=PASS closure_r500_full=1.1354 higher_mode_fraction_r500=0.0531 baryon_fraction_r500=0.1166 failed_gates=none
- seed=20260415 status=PASS closure_r500_full=1.1695 higher_mode_fraction_r500=0.0519 baryon_fraction_r500=0.1138 failed_gates=none
- seed=20260425 status=FAIL closure_r500_full=1.2616 higher_mode_fraction_r500=0.0487 baryon_fraction_r500=0.1077 failed_gates=cluster_scale_closure|higher_modes_non_negligible
- seed=20260435 status=FAIL closure_r500_full=1.2401 higher_mode_fraction_r500=0.0492 baryon_fraction_r500=0.1089 failed_gates=cluster_scale_closure|higher_modes_non_negligible
- seed=20260445 status=PASS closure_r500_full=1.1829 higher_mode_fraction_r500=0.0510 baryon_fraction_r500=0.1124 failed_gates=none
- seed=20260455 status=PASS closure_r500_full=1.1424 higher_mode_fraction_r500=0.0524 baryon_fraction_r500=0.1151 failed_gates=none
- seed=20260465 status=FAIL closure_r500_full=1.2575 higher_mode_fraction_r500=0.0486 baryon_fraction_r500=0.1076 failed_gates=cluster_scale_closure|higher_modes_non_negligible
- seed=20260475 status=PASS closure_r500_full=1.1698 higher_mode_fraction_r500=0.0516 baryon_fraction_r500=0.1135 failed_gates=none
- seed=20260485 status=PASS closure_r500_full=1.1686 higher_mode_fraction_r500=0.0516 baryon_fraction_r500=0.1135 failed_gates=none
- seed=20260495 status=PASS closure_r500_full=1.1899 higher_mode_fraction_r500=0.0509 baryon_fraction_r500=0.1122 failed_gates=none
- seed=20260505 status=PASS closure_r500_full=1.1819 higher_mode_fraction_r500=0.0514 baryon_fraction_r500=0.1133 failed_gates=none
- seed=20260515 status=FAIL closure_r500_full=1.2164 higher_mode_fraction_r500=0.0502 baryon_fraction_r500=0.1112 failed_gates=cluster_scale_closure
