# HFF N=2 benchmark (κ vs Chandra proxy)

This is a minimal two-cluster robustness check using the same measurement operator used for Bullet:
- Map A (response proxy): Frontier Fields κ (Diego v4.1) FITS
- Map B (baryon/gas tracer): stacked Chandra HEASARC `*_full_img2.fits.gz` rate proxy (counts/s)
- Smoothing: 8 arcsec on both maps
- Levels: 99 / 97 / 95 percentiles
- Primary blob: largest connected component above threshold; centroid is unweighted mask centroid

Note: ROI radii are kept small to stay within the Frontier κ footprint (the κ FITS maps are only a few arcminutes across).

## Summary table

| Cluster | κ map (A) | Chandra ObsIDs (img2 inputs) | ROI center (RA, Dec deg) | ROI radius (arcsec) | Sep @99% (arcsec) | Sep @97% (arcsec) | Sep @95% (arcsec) | Outputs |
|---|---|---|---:|---:|---:|---:|---:|---|
| Abell 2744 | [data/hff/abell2744/external_lensing/stsci_frontier/diego_v4.1/hlsp_frontier_model_abell2744_diego_v4.1_kappa.fits](data/hff/abell2744/external_lensing/stsci_frontier/diego_v4.1/hlsp_frontier_model_abell2744_diego_v4.1_kappa.fits) | 25907, 25917, 25922, 25926, 25955 | 3.5887474051936, -30.397192536687 | 100 | 67.0447 | 62.2330 | 59.8894 | [metrics CSV](out_predictions/abell2744_diego_v4p1_kappa_vs_chandra_metrics.csv), [stacked Chandra FITS](out_xray/abell2744_chandra_xray_rate_stack_full.fits) |
| MACS J0416.1-2403 | [data/hff/macs0416/external_lensing/stsci_frontier/diego_v4.1/hlsp_frontier_model_macs0416_diego_v4.1_kappa.fits](data/hff/macs0416/external_lensing/stsci_frontier/diego_v4.1/hlsp_frontier_model_macs0416_diego_v4.1_kappa.fits) | 16236, 16237, 16304, 16523, 17313 | 64.03491667, -24.07244444 | 90 | 38.4514 | 27.4331 | 17.6874 | [metrics CSV](out_predictions/macs0416_diego_v4p1_kappa_vs_chandra_metrics.csv), [stacked Chandra FITS](out_xray/macs0416_chandra_xray_rate_stack_full.fits) |

## Repro commands (exact paths)

### Abell 2744

Stack Chandra proxy:

```
d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe toy_models/make_chandra_xray_map.py \
  --input-glob "toy_models/data/hff/abell2744/raw/heasarc/chandra/*/primary/*_full_img2.fits.gz" \
  --out-fits toy_models/out_xray/abell2744_chandra_xray_rate_stack_full.fits \
  --out-manifest toy_models/out_xray/abell2744_chandra_xray_rate_stack_full_manifest.csv
```

Run metrics:

```
d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe toy_models/cluster_prediction_report.py \
  --map-a toy_models/data/hff/abell2744/external_lensing/stsci_frontier/diego_v4.1/hlsp_frontier_model_abell2744_diego_v4.1_kappa.fits \
  --map-b toy_models/out_xray/abell2744_chandra_xray_rate_stack_full.fits \
  --roi-center-icrs 3.5887474051936,-30.397192536687 \
  --roi-radius-arcsec 100 \
  --smooth-a-arcsec 8 --smooth-b-arcsec 8 \
  --levels 99 97 95 \
  --out-metrics toy_models/out_predictions/abell2744_diego_v4p1_kappa_vs_chandra_metrics.csv
```

### MACS J0416.1-2403

Stack Chandra proxy:

```
d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe toy_models/make_chandra_xray_map.py \
  --input-glob "toy_models/data/hff/macs0416/raw/heasarc/chandra/*/primary/*_full_img2.fits.gz" \
  --out-fits toy_models/out_xray/macs0416_chandra_xray_rate_stack_full.fits \
  --out-manifest toy_models/out_xray/macs0416_chandra_xray_rate_stack_full_manifest.csv
```

Run metrics:

```
d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe toy_models/cluster_prediction_report.py \
  --map-a toy_models/data/hff/macs0416/external_lensing/stsci_frontier/diego_v4.1/hlsp_frontier_model_macs0416_diego_v4.1_kappa.fits \
  --map-b toy_models/out_xray/macs0416_chandra_xray_rate_stack_full.fits \
  --roi-center-icrs 64.03491667,-24.07244444 \
  --roi-radius-arcsec 90 \
  --smooth-a-arcsec 8 --smooth-b-arcsec 8 \
  --levels 99 97 95 \
  --out-metrics toy_models/out_predictions/macs0416_diego_v4p1_kappa_vs_chandra_metrics.csv
```
