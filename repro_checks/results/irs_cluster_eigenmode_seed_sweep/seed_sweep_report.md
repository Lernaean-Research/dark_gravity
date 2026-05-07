# IRS Cluster Eigenmode Seed Sweep

## Run Metadata
- Generated (UTC): 2026-04-06T00:31:04.772681+00:00
- Seed count: 12
- Base seed: 20260405
- Seed step: 10
- Satellites: 24
- ICM nodes: 16
- Max order: 5
- Radial points: 36

## Ensemble Summary
- Pass fraction: 0.667 (8/12)
- closure_r500_full: mean=1.1813, median=1.1699, p16=1.1466, p84=1.2282, min=1.1270, max=1.2516
- higher_mode_fraction_r500: mean=0.0515, median=0.0518, p16=0.0497, p84=0.0528, min=0.0491, max=0.0536
- baryon_fraction_r500: mean=0.1133, median=0.1139, p16=0.1098, p84=0.1158, min=0.1086, max=0.1176
- sigma_pred_r500: mean=844.7610, median=840.7709, p16=832.3643, p84=861.4675, min=825.2252, max=869.6482

## Fragile Gates
- cluster_scale_closure: failures=4/12 (0.333); seeds=20260425,20260435,20260465,20260515
- higher_modes_non_negligible: failures=3/12 (0.250); seeds=20260425,20260435,20260465

## Extreme Seeds by R500 Closure
- low: seed=20260405 closure_r500_full=1.1270
- low: seed=20260415 closure_r500_full=1.1465
- low: seed=20260455 closure_r500_full=1.1467
- high: seed=20260435 closure_r500_full=1.2241
- high: seed=20260465 closure_r500_full=1.2414
- high: seed=20260425 closure_r500_full=1.2516

## Per-Seed Results
- seed=20260405 status=PASS closure_r500_full=1.1270 higher_mode_fraction_r500=0.0536 baryon_fraction_r500=0.1176 failed_gates=none
- seed=20260415 status=PASS closure_r500_full=1.1465 higher_mode_fraction_r500=0.0531 baryon_fraction_r500=0.1161 failed_gates=none
- seed=20260425 status=FAIL closure_r500_full=1.2516 higher_mode_fraction_r500=0.0491 baryon_fraction_r500=0.1086 failed_gates=cluster_scale_closure|higher_modes_non_negligible
- seed=20260435 status=FAIL closure_r500_full=1.2241 higher_mode_fraction_r500=0.0499 baryon_fraction_r500=0.1101 failed_gates=cluster_scale_closure|higher_modes_non_negligible
- seed=20260445 status=PASS closure_r500_full=1.1750 higher_mode_fraction_r500=0.0514 baryon_fraction_r500=0.1132 failed_gates=none
- seed=20260455 status=PASS closure_r500_full=1.1467 higher_mode_fraction_r500=0.0527 baryon_fraction_r500=0.1157 failed_gates=none
- seed=20260465 status=FAIL closure_r500_full=1.2414 higher_mode_fraction_r500=0.0493 baryon_fraction_r500=0.1088 failed_gates=cluster_scale_closure|higher_modes_non_negligible
- seed=20260475 status=PASS closure_r500_full=1.1552 higher_mode_fraction_r500=0.0524 baryon_fraction_r500=0.1149 failed_gates=none
- seed=20260485 status=PASS closure_r500_full=1.1600 higher_mode_fraction_r500=0.0521 baryon_fraction_r500=0.1145 failed_gates=none
- seed=20260495 status=PASS closure_r500_full=1.1775 higher_mode_fraction_r500=0.0515 baryon_fraction_r500=0.1134 failed_gates=none
- seed=20260505 status=PASS closure_r500_full=1.1648 higher_mode_fraction_r500=0.0523 baryon_fraction_r500=0.1149 failed_gates=none
- seed=20260515 status=FAIL closure_r500_full=1.2063 higher_mode_fraction_r500=0.0507 baryon_fraction_r500=0.1123 failed_gates=cluster_scale_closure
