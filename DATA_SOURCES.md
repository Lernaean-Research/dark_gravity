# Data Sources and Provenance

This repository relies on public astrophysical data products that are not redistributed here due to size and licensing constraints. Download links and staging conventions are provided.

## SPARC Galaxy Rotation Curves

- Source: SPARC database (Lelli et al. 2016)
- Typical inputs: `*_rotmod.dat`, `SPARC_Lelli2016c.mrt`
- Staging: `toy_models/data/sparc_rotmod/`

## Bullet Cluster (1E 0657-56)

- Primary download links are documented in:
  - `toy_models/data/bullet_cluster/DATASET_LINKS.md`
- Local staging directories:
  - `toy_models/data/bullet_cluster/raw/heasarc/chandra/<ObsID>/`
  - `toy_models/data/bullet_cluster/raw/heasarc/xmm/<ObsID>/`

## Hubble Frontier Fields (HFF)

- Lensing model inputs and manifests are staged under:
  - `toy_models/data/hff/abell2744/`
  - `toy_models/data/hff/macs0416/`
- See `toy_models/data/hff/README.md` for details.

## Chandra / HEASARC

- HEASARC archive access:
  - https://heasarc.gsfc.nasa.gov/docs/archive.html

## MAST (HST Frontier Fields)

- MAST HLSP archive:
  - https://archive.stsci.edu/hlsp/frontier/

## Notes

- Large FITS/event files and archive bundles are excluded from git.
- Scripts and manifests in `toy_models/` provide reproducible acquisition and processing steps.
