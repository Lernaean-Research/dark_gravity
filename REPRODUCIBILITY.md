# Reproducibility Guide

This repository is organized for transparency and reproducibility while avoiding large third-party data uploads. Large external datasets are excluded from git and must be downloaded separately.

## Quick Start

1. Create the Python environment:

```
./scripts/bootstrap_venv.ps1
```

2. Run a basic SPARC pipeline example:

```
./.venv/Scripts/python.exe toy_models/sparc_rotmod_runner.py \
  --sparc-dir toy_models/data/sparc_rotmod \
  --out-dir toy_models/out_sparc_runs_full_with_composition
```

3. Render dyed-spacetime atlas pages (per-galaxy PNGs):

```
./.venv/Scripts/python.exe toy_models/visualize_dyed_spacetime.py \
  --galaxy-dir toy_models/out_sparc_runs_full_with_composition/galaxies \
  --out-dir toy_models/out_spacetime_sixpanel_full_v3 \
  --six-panel \
  --img-n 320 --dpi 160 --interp bilinear
```

## Data Policy

- See `toy_models/DATA_POLICY.md` for what is tracked vs excluded.
- Large third-party files (FITS, event lists, archives) are excluded by `.gitignore`.

## Where Inputs Come From

- SPARC rotation-curve data: see `toy_models/SPARC_ROTMod_METHODOLOGY.md`.
- Bullet Cluster data links: `toy_models/data/bullet_cluster/DATASET_LINKS.md`.
- HFF data staging: `toy_models/data/hff/README.md`.

## Expected Outputs

- SPARC runner outputs: `toy_models/out_sparc_runs_full_with_composition/summary.csv`
- Robust estimator: `toy_models/out_sparc_runs_full_with_composition/q_est.csv`
- Atlas outputs (PNG/PDF): `toy_models/out_spacetime_sixpanel_full_v3/` (generated locally)

## Notes

- Large output directories are intentionally ignored in git.
- If a journal supplement requires large binaries, publish them as a versioned data release (Zenodo) and link from a manifest.
