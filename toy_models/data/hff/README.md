# HFF (Frontier Fields) data staging

This folder holds **inputs** for the HFF κ–X-ray morphology benchmarking and systematics sweeps.

## What is tracked in git

Tracked (small, methodological):

- Readme/provenance files from HLSP model folders (when available)
- Manifests describing what was downloaded and where it came from
- Small derived products (e.g., stacking manifests)

Not tracked (local-only, large third-party data):

- Raw Chandra products/events downloaded from HEASARC
- HLSP κ maps in FITS form

Those large files are intentionally excluded by the repo’s `.gitignore` (see `toy_models/DATA_POLICY.md`).

## Current clusters

- `abell2744/`
  - `chandra_stack/abell2744_chandra_stack_manifest.csv`
  - `external_lensing/` (folder layout for HFF κ models)

- `macs0416/`
  - `chandra_stack/macs0416_chandra_stack_manifest.csv`
  - `external_lensing/`
