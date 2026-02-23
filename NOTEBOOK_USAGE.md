# How to use the SPARC edge-response notebook

Notebook: [SPARC_EdgeResponse_Analysis.ipynb](SPARC_EdgeResponse_Analysis.ipynb)

This guide is the step-by-step, reproducible workflow for running the SPARC rotmod fits and correlation analysis for the Spacetime Mechanics auxiliary edge-response toy model.

## 0) One-time setup (kernel)

This notebook expects the workspace virtual environment at:

- `D:/#Documents/#Publication/Spacetime_Mechanics/.venv`

If you haven't set it up yet, bootstrap the environment (creates `.venv` and installs `requirements.txt`):

- `./scripts/bootstrap_venv.ps1`

VS Code needs `ipykernel` installed in that environment.

If VS Code prompts “Running cells requires the ipykernel package”, install it into the `.venv`:

- `d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe -m pip install --upgrade ipykernel`

Note: `ipykernel` is also included in `requirements.txt`, so the bootstrap script should normally cover this.

If `pip` is broken in the `.venv`, repair it first:

- `d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe -m ensurepip --upgrade`

Then retry the `ipykernel` install.

## 1) What the notebook runs

The notebook is a thin, transparent wrapper around two stdlib-only scripts:

- [toy_models/sparc_rotmod_runner.py](toy_models/sparc_rotmod_runner.py)
  - Reads `*_rotmod.dat` files
  - Builds baryonic curves
  - Adds the auxiliary edge-response contribution
  - Fits one parameter per galaxy (`Q >= 0`)
  - Writes per-galaxy CSVs + `summary.csv`

- [toy_models/analyze_summary_correlations.py](toy_models/analyze_summary_correlations.py)
  - Loads `summary.csv`
  - Computes Pearson and Spearman correlations for hypothesis-driven metric pairs
  - Writes `correlations.csv`

Methodology docs:

- [toy_models/SPARC_ROTMod_METHODOLOGY.md](toy_models/SPARC_ROTMod_METHODOLOGY.md)
- [toy_models/ROBUST_METRICS_RATIONALE.md](toy_models/ROBUST_METRICS_RATIONALE.md)
- [toy_models/CORRELATION_METHODOLOGY.md](toy_models/CORRELATION_METHODOLOGY.md)

## 2) Inputs: where the SPARC rotmod files live

By default, the notebook points to the rotmod dataset here:

- `D:\#Documents\#Physics\TPT Paper\Rotmod_LTG`

These are `*_rotmod.dat` files with columns like:

- `Rad[kpc]`, `Vobs[km/s]`, `errV[km/s]`, `Vgas[km/s]`, `Vdisk[km/s]`, `Vbul[km/s]`, ...

The notebook reads the files **in-place** (no copying). If you want to use a different rotmod directory, update the `ROTDMOD_DIR` variable in the configuration cell.

## 3) Running the notebook (recommended order)

Run the notebook top-to-bottom.

### Cell group A: environment info

- Prints Python version, executable, and CWD.

### Cell group B: configure run parameters

Key parameters you can tune:

- `max_galaxies` (set `0` to run all galaxies)
- `sigma_kpc` (width of the edge-source bump)
- `ups_disk`, `ups_bul` (disk/bulge mass-to-light scalings)
- `a0_ms2` (acceleration scale)

### Cell group C: run the SPARC rotmod runner

This calls:

- `toy_models/sparc_rotmod_runner.py`

Outputs:

- `<OUT_DIR>/summary.csv`
- `<OUT_DIR>/galaxies/<galaxy>.csv` (per-galaxy data)

### Cell group D: load and preview `summary.csv`

This prints:

- number of processed galaxies
- the available columns
- a short preview of key derived metrics

### Cell group E: run correlations

This calls:

- `toy_models/analyze_summary_correlations.py`

Outputs:

- `<OUT_DIR>/correlations.csv`

### Cell group F: optional plots

If `matplotlib` is installed in the `.venv`, the notebook will show scatter plots for key pairs.

If `matplotlib` is not installed, it prints text summaries instead.

To install matplotlib (optional):

- `d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe -m pip install matplotlib`

Note: `matplotlib` is included in `requirements.txt`, so the bootstrap script should normally cover this.

## 4) Full 175-galaxy batch run (timestamped output)

At the end of the notebook there is a **Full batch run** section that:

- Runs the runner on **all** `*_rotmod.dat` files (`max_galaxies=0`)
- Writes to a timestamped folder like:
  - `toy_models/out_sparc_runs_full_YYYYMMDD_HHMMSS/`
- Exports:
  - `summary.csv`
  - `correlations.csv`
  - `run_config.json` (machine-readable provenance: paths, parameters, exact commands, python version)

This is the recommended “publication-grade” mode because each run is versioned and reproducible.

## 5) Interpreting the key outputs

### Core fitted parameter

- `q_best_kms2`
  - The best-fit auxiliary-field amplitude per galaxy.

- `v_extra_asym_kms = sqrt(q_best_kms2)`
  - Interpretable asymptotic extra flat-speed scale produced by the auxiliary mode.

### Recommended “center action” proxies

- `gbar_half_rt_kms2_per_kpc`
  - Baryonic acceleration at `0.5 * R_t` (robust and model-aligned)

- `s_in_dlng_dlnr`
  - Inner slope proxy capturing compactness/shape (multi-point and scale-free)

### Outskirts validity checks

Computed over the outer region `R >= 2 * R_t`:

- `outer_resid_mean_z` (mean standardized residual)
- `outer_resid_rms_z` (RMS standardized residual)
- `outer_chi2` (outer-region chi^2 contribution)

These are useful for falsifiability: if the mechanism is “edge-driven”, it should perform best in the outskirts, not just by fitting the inner rise.

## 6) Troubleshooting

### A) VS Code says ipykernel missing / kernel dies

- Install ipykernel into the `.venv`:
  - `d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe -m pip install --upgrade ipykernel`

If pip is broken:

- `d:/#Documents/#Publication/Spacetime_Mechanics/.venv/Scripts/python.exe -m ensurepip --upgrade`

### B) Runner fails with “file not found”

- Confirm `ROTDMOD_DIR` points to an existing folder containing `*_rotmod.dat`.

### C) Very small N in correlation table

- Increase `max_galaxies` or set it to `0` for all galaxies, then rerun.

### D) No plots

- That’s expected if `matplotlib` isn’t installed.
- The notebook still produces `summary.csv` + `correlations.csv` in stdlib-only mode.

## 7) Reproducibility checklist (for the paper / arXiv)

When you run a full batch:

- keep the entire timestamped output folder
- cite the exact `run_config.json` from that run
- archive the versions of:
  - `toy_models/sparc_rotmod_runner.py`
  - `toy_models/analyze_summary_correlations.py`
  - the methodology markdown files

That makes it straightforward for a third party to reproduce results from raw rotmod files.
