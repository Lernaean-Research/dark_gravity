# Data staging

`toy_models/data/` is a **data drop-in / staging** directory.

## Repo vs local machine

This repo intentionally tracks **only small, methodology-relevant files** here:

- templates
- manifests
- inventories
- readme/provenance notes

Large third-party downloads (FITS maps, event lists, archives, compressed products) are expected to exist **only on your local machine** and are excluded by `.gitignore`.

See `toy_models/DATA_POLICY.md` for the rationale and the exact policy.

## Subfolders

- `bullet_cluster/`: Bullet Cluster staging + links/templates
- `hff/`: HFF N=2 benchmark staging (Abell 2744, MACS J0416)
