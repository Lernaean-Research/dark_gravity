# Data policy (what belongs in this repo)

This repository is meant to be **reproducible and reviewable** without bundling multi-GB third-party survey products.

## Principle

Commit:

- **Methodology**: scripts (`.py`), docs (`.md`), configuration, and plotting utilities.
- **Provenance**: manifests, inventories, readmes, and *small* metadata tables that describe what was downloaded and from where.
- **Derived results that are lightweight**: small CSV summaries (metrics tables, systematics grids), and a small number of representative figures used in the manuscript/appendix.

Do **not** commit (by default):

- Large third-party data products (FITS maps, event files, archive bundles, PDFs), especially anything that is:
  - huge (hundreds of MB to many GB),
  - mirrorable from a public archive (HEASARC, MAST, HLSP), or
  - not created by us.

The root `.gitignore` enforces this policy for common large formats under `toy_models/data/`.

## Folder conventions

- `toy_models/data/`
  - **Staging area** for inputs.
  - In the repo, this should mostly contain **manifests/readmes/templates**.
  - On your local machine, it may also contain large downloads, but those are ignored by git.

- `toy_models/out_* /`
  - Generated outputs.
  - Prefer committing small summary CSVs and a minimal set of figures used in writing.
  - Avoid committing full-resolution intermediate products unless they are essential.

## If we ever need to ship large binaries

If a journal supplement or long-term archival requirement forces inclusion of large binaries:

- Use **Git LFS** (and confirm the remote has LFS enabled), or
- Publish a versioned data release elsewhere (Zenodo/OSF/etc.) and link to it from a manifest.
