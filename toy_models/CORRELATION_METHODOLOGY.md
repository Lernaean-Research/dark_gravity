# Correlation methodology (stdlib-only)

This document describes the methodology implemented in:
- [toy_models/analyze_summary_correlations.py](toy_models/analyze_summary_correlations.py)

The intent is to provide a **transparent, auditable** way to quantify the strength
of proposed falsifiability correlations using only the `summary.csv` output from
`toy_models/sparc_rotmod_runner.py`.

## 1. Inputs

- A CSV file `summary.csv` with a header row and numeric columns.
- Missing values are represented by empty strings or `nan`.

## 2. Pairwise complete cases

For each pair of columns `(X, Y)`, the script uses **pairwise complete cases**:

- It constructs vectors `(x_i, y_i)` using only rows where both values are finite.
- The sample size `N` reported for each pair is therefore pair-specific.

Rationale:
- This avoids inventing values for missing entries.
- It keeps each correlation maximally data-driven.

## 3. Pearson correlation

Pearson correlation coefficient is computed as:

$$
 r = \frac{\sum_i (x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_i (x_i-\bar{x})^2\,\sum_i (y_i-\bar{y})^2}}
$$

If either variable has zero variance in the paired sample, the script returns `nan`.

## 4. Spearman rank correlation

Spearman’s $\rho$ is computed by:

1. Converting `X` and `Y` into ranks (1..N).
2. Handling ties by assigning **average ranks** for tied values.
3. Computing Pearson correlation on the rank vectors.

Rationale:
- $\rho$ is more robust to outliers and non-linear monotonic trends.

## 5. Default hypothesis-driven pairs

If no `--x/--y` are provided, the script computes a small default set of pairs
chosen to probe the “center action ↔ edge reaction” thesis:

- `gbar_half_rt_kms2_per_kpc` vs `q_best_kms2`
- `s_in_dlng_dlnr` vs `q_best_kms2`
- `gbar_half_rt_kms2_per_kpc` vs `v_extra_asym_kms`
- `s_in_dlng_dlnr` vs `v_extra_asym_kms`
- `gbar_half_rt_kms2_per_kpc` vs `r_t_kpc`
- `s_in_dlng_dlnr` vs `outer_resid_mean_z`
- `s_in_dlng_dlnr` vs `outer_resid_rms_z`

You can override these by specifying `--x` and `--y`.

## 6. Outputs

The script prints a compact table to stdout and can optionally write a CSV via:

- `--export <path>`

Columns in the export:
- `x`, `y`, `n`, `pearson_r`, `spearman_rho`

## 7. Caveats (explicit)

- The script does **not** compute p-values or confidence intervals (to avoid
  importing external statistical libraries). If you want, we can add a bootstrap
  CI (still stdlib-only) in a fully reproducible way.
- Correlation does not imply causation; these statistics are used as a diagnostic
  to guide falsifiability tests, not as proof of mechanism.
