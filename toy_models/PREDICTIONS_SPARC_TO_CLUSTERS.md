# SPARC → Cluster Predictions (Operational + Falsifiable)

This note defines a **minimal**, measurement-first way to translate the SPARC framework’s qualitative content into falsifiable cluster-scale predictions that can be tested on existing public datasets.

## Philosophy

- SPARC constrains an **equilibrium** mapping between baryonic structure and an **effective response**.
- Merging clusters probe the same response sector in **non-equilibrium** conditions.
- Therefore: define a small set of **pre-registered measurement operators** and compare across clusters and dynamical states.

This document does **not** assert that any proxy (e.g., X-ray brightness) equals true baryon density; it separates *robust morphology tests* from *mass-calibrated* tests.

## Proxies

- Response proxy (A): lensing convergence map \(\kappa(\theta)\) or an equivalent lens-model surface-density proxy.
- Gas proxy (B): X-ray surface brightness (counts/s) or a thermal SZE Compton-y map.
- Collisionless proxy (C, optional): galaxy light / member galaxy density map.

## Pre-registered operators

Use the same choices across systems:

- Common sky ROI: center + radius in arcsec.
- Common smoothing: Gaussian \(\sigma\) in arcsec.
- Blob definition: connected components above percentile thresholds (e.g., 99/97/95).
- Primary blob choice: largest-area component at a level.
- Centroid: unweighted centroid of the threshold mask (stable under amplitude rescaling).

## Hypotheses (testable)

### H1 — Relaxed co-location
In relaxed clusters, response and baryon proxies should be nearly co-located.

Operational test:
- For each level, measure separation between A and B primary blob centroids.
- Expect separations \(\ll\) core scale (must choose a common definition of “core scale”, e.g., an aperture radius).

### H2 — Merger separation enhancement
In disturbed mergers, A–B separations should be systematically larger than in relaxed clusters.

Operational test:
- Compute A–B centroid separations for a merger sample and a relaxed sample using identical operators.
- Expect higher median separation in mergers.

### H3 — Between-ness (requires C)
If the response carries memory / finite relaxation, the response centroid should lie between the displaced gas centroid and the collisionless centroid.

Operational test:
- With centroids \(\vec x_B\) (gas), \(\vec x_C\) (collisionless), \(\vec x_A\) (response), define
  \[ f = \frac{(\vec x_A-\vec x_B)\cdot(\vec x_C-\vec x_B)}{|\vec x_C-\vec x_B|^2}. \]
- Expect \(0 < f < 1\) in recent mergers; expect \(f \approx 0\) in relaxed clusters where gas and response coincide.

### H4 — Uncertainty propagation
Any derived centroid separation must include uncertainty from lens-model variability.

Operational test:
- Use posterior \(\kappa\) samples (or multiple team reconstructions) and report the distribution of centroid separations.

## Tools in this repo

- `toy_models/cluster_prediction_report.py`
  - Computes per-level blob centroids and A–B separations.
  - Optional: computes separation distributions across A posterior samples.

- `toy_models/blobology_from_maps.py`
  - Extracts blob catalogs and all-pairs centroid separation tables.

- `toy_models/gradients_from_lensing.py`
  - Computes \(\nabla\kappa\) (or gradient of any scalar map) and annular profiles.

## Example: Bullet (κ vs observed Chandra proxy)

Run:

```powershell
./.venv/Scripts/python.exe toy_models/cluster_prediction_report.py \
  --map-a toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  --map-b toy_models/out_xray/chandra_xray_rate_stack_full.fits \
  --roi-center-icrs 104.63088146599212,-55.934259101595984 --roi-radius-arcsec 900 \
  --smooth-a-arcsec 8 --smooth-b-arcsec 8 \
  --levels 99 97 95 \
  --a-samples-glob "toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/sample_model/sample_maps/bulletclu-kappa-200mas_*.fits" \
  --anchor-max-arcsec 90 \
  --out-metrics toy_models/out_predictions/bullet_metrics.csv \
  --out-samples toy_models/out_predictions/bullet_samples.csv
```

Interpretation:
- If H2 is correct, Bullet should show relatively large A–B separations compared to relaxed clusters using the same operator.
- If you later add a galaxy-density/light map (C), you can test H3 (between-ness).
