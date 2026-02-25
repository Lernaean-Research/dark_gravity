# HFF all-teams systematics analysis (κ vs Chandra proxy)

This report analyzes the completed robustness grid for two Hubble Frontier Fields clusters, using a preregistered measurement operator to compare a lensing response proxy (κ) against an observational gas proxy (stacked Chandra HEASARC img2 rate map).

## What is measured (pre-registered operator)

For each cluster, each Frontier κ team model, and each ROI radius:

- **Inputs**: (A) a Frontier κ FITS map; (B) a stacked Chandra `*_full_img2.fits.gz` proxy rate map (counts/s).
- **Common processing**: Gaussian smoothing with σ = 8 arcsec applied independently to A and B.
- **Within a circular ROI** (ICRS center fixed per cluster), evaluate thresholds at **99 / 97 / 95 percentiles** of the smoothed pixels.
- **Primary blob rule**: choose the **largest connected component** above threshold (per map) and compute its **unweighted mask centroid**.
- **Metric**: centroid-to-centroid separation in arcseconds.

This is designed to be falsifiable and apples-to-apples across models: the operator is fixed and does not adapt to any individual team, threshold, or cluster beyond the ROI definition.

## Why this design (rationales)

**Why multi-team κ?** Frontier Fields provides multiple independent lens reconstructions. If a κ–gas offset claim depends strongly on the team/model choice, that sensitivity is itself a result and must be quantified.

**Why ROI sweeps?** Frontier κ maps have limited footprints. ROI choice can (i) clip structures, (ii) include/exclude secondary peaks, and (iii) change percentiles. Sweeping ROI radii provides a direct stability check.

**Why percentile thresholds?** Percentiles are scale-free and robust to unknown absolute calibrations between maps, while still selecting the high-intensity/high-κ structures relevant for centroid comparisons.

**Why 8 arcsec smoothing?** This enforces a common effective resolution, reduces pixel-scale noise sensitivity, and stabilizes connected-component topology.

## Data products (what is ‘proxy’)

The Chandra map here is a **proxy stack** constructed directly from HEASARC `img2` images (not event-level CIAO processing).

Stacking procedure (implemented in `toy_models/make_chandra_xray_map.py`):

- Read each `*_full_img2.fits.gz` image.
- Divide by scalar exposure (`EXPOSURE` keyword; fallback to `LIVETIME/ONTIME`).
- Reproject onto a common WCS grid and compute an exposure-weighted mean rate map.

This is appropriate for centroid/peak *geometry* comparisons, but it is not a science-grade X-ray reduction (no exposure maps/vignetting correction, background modeling, point-source masking, etc.).

## Results: cross-team systematics and ROI sensitivity

### Abell 2744

- Teams in grid: **11**
- ROI radii (arcsec): **80, 100, 120**
- Levels (percentiles): **95, 97, 99**
- ROI center (deg): **3.5887474051936,-30.397192536687**
- Chandra proxy FITS: `toy_models/data/hff/abell2744/chandra_stack/abell2744_chandra_full_img2_proxy.fits`
- Combined outputs: `toy_models/out_predictions/systematics/abell2744/systematics_summary.csv`


#### Team spread at ROI = 100"

Summary across κ teams at fixed ROI, per threshold level. The key robustness quantities are the IQR and full range across teams.


|   level_pct |   n |   median |   q25 |   q75 |   iqr |   min |   max |   range |
|------------:|----:|---------:|------:|------:|------:|------:|------:|--------:|
|          95 |  11 |    66.37 | 65.58 | 67.07 |  1.49 | 50.72 | 68.71 |   17.99 |
|          97 |  11 |    65.95 | 65.71 | 66.88 |  1.17 | 46.09 | 68.7  |   22.61 |
|          99 |  11 |    67.38 | 67.07 | 68.5  |  1.42 | 39.79 | 78.06 |   38.28 |


#### Team spread for every ROI radius

Median separation across teams for each (ROI radius, level), plus IQR and min/max across teams.


|   roi_radius_arcsec |   level_pct |   n |   median |   iqr |   min |   max |
|--------------------:|------------:|----:|---------:|------:|------:|------:|
|                  80 |          95 |  11 |    66.21 |  1.39 | 50.43 | 68.01 |
|                  80 |          97 |  11 |    66.84 |  1.39 | 44.74 | 68.78 |
|                  80 |          99 |  11 |    66.94 |  2.36 | 40.69 | 76.54 |
|                 100 |          95 |  11 |    66.37 |  1.49 | 50.72 | 68.71 |
|                 100 |          97 |  11 |    65.95 |  1.17 | 46.09 | 68.7  |
|                 100 |          99 |  11 |    67.38 |  1.42 | 39.79 | 78.06 |
|                 120 |          95 |  11 |    54.51 |  2.33 | 41.54 | 56.95 |
|                 120 |          97 |  11 |    67.1  |  2.03 | 51    | 69.86 |
|                 120 |          99 |  11 |    67.42 |  2.18 | 38.65 | 85.82 |


#### ROI sensitivity (Δ = sep@120" − sep@80")

This quantifies how much the measured separation changes when the ROI is expanded from 80" to 120". Positive Δ means larger measured offsets at larger ROI.


|   level_pct |   n |   median |    q25 |    q75 |   iqr |    min |   max |
|------------:|----:|---------:|-------:|-------:|------:|-------:|------:|
|          95 |  11 |   -11.71 | -11.78 | -11.09 |  0.7  | -16.08 | -8.88 |
|          97 |  11 |     0.67 |   0.11 |   1.02 |  0.91 |  -4.06 |  6.26 |
|          99 |  11 |     1.27 |  -0.71 |   1.67 |  2.38 |  -8.11 | 17.97 |


#### Which effect dominates? (team vs ROI)

A practical way to compare sensitivities is to look at typical ROI-induced change (IQR of Δ) versus typical cross-team spread at a fixed ROI (IQR at ROI=100).

Interpretation guideline:

- If cross-team IQR ≫ ROI Δ IQR, the dominant uncertainty is lens-model systematics.
- If ROI Δ IQR ≫ cross-team IQR, the dominant uncertainty is ROI/footprint sensitivity (operator interacting with morphology).

|   level_pct |   iqr_teams_at100 |   range_teams_at100 |   iqr_delta120_80 |   delta_min |   delta_max |
|------------:|------------------:|--------------------:|------------------:|------------:|------------:|
|          95 |              1.49 |               17.99 |              0.7  |      -16.08 |       -8.88 |
|          97 |              1.17 |               22.61 |              0.91 |       -4.06 |        6.26 |
|          99 |              1.42 |               38.28 |              2.38 |       -8.11 |       17.97 |


#### Team-level stability across radii (range over radii)

For each team and threshold level, this shows the spread of separations across the ROI sweep. Large values indicate ROI sensitivity for that model at that level.


|   level_pct | team             |   median_sep |   min_sep |   max_sep |   range_over_radii |
|------------:|:-----------------|-------------:|----------:|----------:|-------------------:|
|          95 | diego            |        59.89 |     46.27 |     62.35 |              16.08 |
|          95 | keeton           |        65.38 |     52.12 |     66.03 |              13.91 |
|          95 | bradac           |        66.22 |     54.51 |     66.37 |              11.86 |
|          95 | cats             |        66.93 |     55.32 |     67.11 |              11.79 |
|          95 | williams         |        66.21 |     55.1  |     66.87 |              11.77 |
|          95 | zitrin-ltm       |        65.81 |     54.07 |     65.85 |              11.77 |
|          95 | zitrin-ltm-gauss |        68.01 |     56.95 |     68.71 |              11.76 |
|          95 | zitrin-nfw       |        67.33 |     56.29 |     68.02 |              11.74 |
|          95 | glafic           |        65.71 |     54.05 |     65.78 |              11.72 |
|          95 | sharon           |        67.21 |     55.52 |     67.22 |              11.71 |
|          97 | merten           |        46.09 |     44.74 |     51    |               6.26 |
|          97 | diego            |        62.23 |     61.22 |     65.28 |               4.06 |
|          97 | cats             |        67.89 |     66.84 |     68.59 |               1.75 |
|          97 | zitrin-nfw       |        67.68 |     67.61 |     68.77 |               1.15 |
|          97 | glafic           |        66.43 |     65.95 |     67.1  |               1.15 |
|          97 | zitrin-ltm-gauss |        68.78 |     68.7  |     69.86 |               1.15 |
|          97 | williams         |        65.97 |     65.8  |     66.93 |               1.13 |
|          97 | sharon           |        67.5  |     66.93 |     68.03 |               1.11 |
|          97 | zitrin-ltm       |        66.84 |     66.09 |     67.19 |               1.1  |
|          97 | keeton           |        65.76 |     65.61 |     66.7  |               1.09 |
|          99 | cats             |        68.36 |     67.86 |     85.82 |              17.97 |
|          99 | zitrin-ltm       |        68.02 |     67.92 |     76.13 |               8.2  |
|          99 | merten           |        39.79 |     38.65 |     40.69 |               2.04 |
|          99 | williams         |        65.17 |     63.57 |     65.31 |               1.74 |
|          99 | zitrin-nfw       |        68.64 |     67.1  |     68.77 |               1.67 |
|          99 | zitrin-ltm-gauss |        78.06 |     76.54 |     78.21 |               1.67 |
|          99 | glafic           |        67.15 |     66    |     67.28 |               1.28 |
|          99 | sharon           |        67.38 |     66.15 |     67.42 |               1.27 |
|          99 | diego            |        66.94 |     66.21 |     67.04 |               0.84 |
|          99 | bradac           |        68.82 |     68.32 |     69.02 |               0.7  |



### MACS J0416.1-2403

- Teams in grid: **12**
- ROI radii (arcsec): **80, 100, 120**
- Levels (percentiles): **95, 97, 99**
- ROI center (deg): **64.03491667,-24.07244444**
- Chandra proxy FITS: `toy_models/data/hff/macs0416/chandra_stack/macs0416_chandra_full_img2_proxy.fits`
- Combined outputs: `toy_models/out_predictions/systematics/macs0416/systematics_summary.csv`


#### Team spread at ROI = 100"

Summary across κ teams at fixed ROI, per threshold level. The key robustness quantities are the IQR and full range across teams.


|   level_pct |   n |   median |   q25 |   q75 |   iqr |   min |   max |   range |
|------------:|----:|---------:|------:|------:|------:|------:|------:|--------:|
|          95 |  12 |    15.84 | 14.77 | 17.36 |  2.59 | 12.71 | 34.82 |   22.12 |
|          97 |  12 |    27.86 | 24.6  | 44.6  | 20    | 23.55 | 50.58 |   27.03 |
|          99 |  12 |    41.66 |  7.32 | 44.76 | 37.44 |  4.51 | 45.85 |   41.34 |


#### Team spread for every ROI radius

Median separation across teams for each (ROI radius, level), plus IQR and min/max across teams.


|   roi_radius_arcsec |   level_pct |   n |   median |   iqr |   min |   max |
|--------------------:|------------:|----:|---------:|------:|------:|------:|
|                  80 |          95 |  12 |    26.45 |  2.67 | 24.01 | 48.74 |
|                  80 |          97 |  12 |    28.9  | 19.95 | 24.06 | 64.44 |
|                  80 |          99 |  12 |    43.59 | 13.59 |  4.45 | 61.78 |
|                 100 |          95 |  12 |    15.84 |  2.59 | 12.71 | 34.82 |
|                 100 |          97 |  12 |    27.86 | 20    | 23.55 | 50.58 |
|                 100 |          99 |  12 |    41.66 | 37.44 |  4.51 | 45.85 |
|                 120 |          95 |  12 |    11.82 |  2.83 |  6.53 | 30.88 |
|                 120 |          97 |  12 |    18.62 | 20.09 | 14.33 | 35.79 |
|                 120 |          99 |  12 |    37.11 | 25.06 |  5    | 45.75 |


#### ROI sensitivity (Δ = sep@120" − sep@80")

This quantifies how much the measured separation changes when the ROI is expanded from 80" to 120". Positive Δ means larger measured offsets at larger ROI.


|   level_pct |   n |   median |    q25 |    q75 |   iqr |    min |    max |
|------------:|----:|---------:|-------:|-------:|------:|-------:|-------:|
|          95 |  12 |   -14.61 | -15.39 | -14.51 |  0.88 | -27.65 | -14.03 |
|          97 |  12 |    -9.73 | -10.11 |  -9.72 |  0.39 | -28.65 |  -9.37 |
|          99 |  12 |     0.32 | -10.41 |   0.39 | 10.8  | -38.18 |  16.79 |


#### Which effect dominates? (team vs ROI)

A practical way to compare sensitivities is to look at typical ROI-induced change (IQR of Δ) versus typical cross-team spread at a fixed ROI (IQR at ROI=100).

Interpretation guideline:

- If cross-team IQR ≫ ROI Δ IQR, the dominant uncertainty is lens-model systematics.
- If ROI Δ IQR ≫ cross-team IQR, the dominant uncertainty is ROI/footprint sensitivity (operator interacting with morphology).

|   level_pct |   iqr_teams_at100 |   range_teams_at100 |   iqr_delta120_80 |   delta_min |   delta_max |
|------------:|------------------:|--------------------:|------------------:|------------:|------------:|
|          95 |              2.59 |               22.12 |              0.88 |      -27.65 |      -14.03 |
|          97 |             20    |               27.03 |              0.39 |      -28.65 |       -9.37 |
|          99 |             37.44 |               41.34 |             10.8  |      -38.18 |       16.79 |


#### Team-level stability across radii (range over radii)

For each team and threshold level, this shows the spread of separations across the ROI sweep. Large values indicate ROI sensitivity for that model at that level.


|   level_pct | team             |   median_sep |   min_sep |   max_sep |   range_over_radii |
|------------:|:-----------------|-------------:|----------:|----------:|-------------------:|
|          95 | merten           |        29.52 |     21.08 |     48.74 |              27.65 |
|          95 | cats             |        12.71 |      6.53 |     24.45 |              17.92 |
|          95 | caminha          |        13.7  |      8.87 |     24.93 |              16.06 |
|          95 | keeton           |        13.11 |      8.85 |     24.01 |              15.16 |
|          95 | diego            |        16.04 |     11.91 |     27.06 |              15.15 |
|          95 | zitrin-ltm       |        15.16 |     11.22 |     25.84 |              14.62 |
|          95 | zitrin-ltm-gauss |        34.82 |     30.88 |     45.48 |              14.6  |
|          95 | zitrin-nfw       |        17.22 |     13.31 |     27.89 |              14.58 |
|          95 | williams         |        17.53 |     13.63 |     28.2  |              14.57 |
|          95 | bradac           |        17.31 |     13.41 |     27.76 |              14.34 |
|          97 | merten           |        50.58 |     35.79 |     64.44 |              28.65 |
|          97 | diego            |        26.69 |     17.36 |     28.2  |              10.83 |
|          97 | caminha          |        24.54 |     15    |     25.71 |              10.71 |
|          97 | bradac           |        44.55 |     35.39 |     45.3  |               9.91 |
|          97 | cats             |        24.01 |     14.37 |     24.26 |               9.89 |
|          97 | zitrin-ltm       |        44.87 |     35.74 |     45.47 |               9.73 |
|          97 | williams         |        41.89 |     32.75 |     42.47 |               9.73 |
|          97 | keeton           |        23.55 |     14.33 |     24.06 |               9.72 |
|          97 | zitrin-nfw       |        29.03 |     19.88 |     29.6  |               9.72 |
|          97 | zitrin-ltm-gauss |        44.74 |     35.62 |     45.34 |               9.72 |
|          99 | sharon           |         6.63 |      6.11 |     44.8  |              38.7  |
|          99 | merten           |        45.85 |     43.37 |     61.78 |              18.42 |
|          99 | cats             |         7.72 |      7.18 |     23.96 |              16.79 |
|          99 | caminha          |        40.62 |     26.56 |     41.77 |              15.21 |
|          99 | diego            |        38.07 |     30.86 |     39.67 |               8.81 |
|          99 | keeton           |         4.77 |      4.61 |      5.66 |               1.06 |
|          99 | zitrin-ltm-gauss |        45.1  |     44.72 |     45.44 |               0.72 |
|          99 | zitrin-ltm       |        45.41 |     45.03 |     45.75 |               0.72 |
|          99 | bradac           |        45.26 |     44.9  |     45.58 |               0.68 |
|          99 | zitrin-nfw       |        44.11 |     43.75 |     44.44 |               0.68 |



## Global interpretation and caveats

1) **‘Offset’ is not a single number**: it is a function of (i) threshold level and (ii) ROI definition, even before considering κ model systematics.
2) **Lens-model systematics are real**: different Frontier κ reconstructions can yield materially different centroid separations under a fixed operator.
3) **ROI sensitivity is also real**: expanding the ROI can introduce new connected components or shift percentile structure, changing the primary-blob centroid.
4) **Proxy X-ray limitations**: the img2 stack is adequate for geometry/centroid work but can be biased by unresolved point sources, varying backgrounds, vignetting, and differences in bandpass/exposure.
5) **Footprint constraint**: ROI must stay within κ coverage. Larger radii may be invalid for some κ products; the sweep used here stays conservative.


## Reproducibility

Primary outputs analyzed here:

- `toy_models/out_predictions/systematics/abell2744/systematics_summary.csv`
- `toy_models/out_predictions/systematics/macs0416/systematics_summary.csv`

Chandra proxy stacks used:

- `toy_models/data/hff/abell2744/chandra_stack/abell2744_chandra_full_img2_proxy.fits`
- `toy_models/data/hff/macs0416/chandra_stack/macs0416_chandra_full_img2_proxy.fits`

To regenerate systematics grids (example):

```
d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe toy_models/run_hff_systematics.py \
  --cluster abell2744 \
  --chandra-map toy_models/data/hff/abell2744/chandra_stack/abell2744_chandra_full_img2_proxy.fits \
  --roi-center 3.5887474051936,-30.397192536687 \
  --roi-radii 80 100 120 \
  --teams all --skip-existing
```
