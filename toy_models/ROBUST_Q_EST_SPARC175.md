# Robust `Q_est` for the SPARC 175 late-type galaxies

This note defines and computes a **non-fitted** outer velocity-deficit estimator

$$
Q_{\mathrm{est}}\;[(\mathrm{km/s})^2]
$$

for the SPARC dataset of **175 late-type galaxies**.

Here, `Q_est` is computed as a **Huber-robust location** of

$$
\Delta(R)=V_{\mathrm{obs}}^2(R)-V_{\mathrm{bar}}^2(R)
$$

over an “outer” subset of radii (defined below). It is intended as a simple,
auditable proxy for the **asymptotic $V^2$ offset** in the outskirts.

## Data source and scope

Two equivalent data routes are supported:

1. **Recommended (already in this repo):** per-galaxy CSVs produced by
   [toy_models/sparc_rotmod_runner.py](toy_models/sparc_rotmod_runner.py), located at:
   - `toy_models/out_sparc_runs_full_with_composition/galaxies/*.csv`

   These CSVs already contain `vbar_kms` computed consistently with the runner
   defaults ($\Upsilon_\mathrm{disk}=0.5$, $\Upsilon_\mathrm{bul}=0.7$).

2. **Raw SPARC rotmod files (external download):** `*_rotmod.dat` ASCII tables with
   (at minimum) columns:
   - `Rad` (kpc), `Vobs` (km/s), `errV` (km/s), `Vgas` (km/s), `Vdisk` (km/s), `Vbul` (km/s)

   The canonical SPARC master table for metadata (e.g. baryonic mass and gas fraction)
   is SPARC Table 1: `SPARC_Lelli2016c.mrt` from:
   - https://astroweb.case.edu/SPARC/

Reference: Lelli et al. (2016), AJ 152(6), 157. https://doi.org/10.3847/0004-6256/152/6/157

## Definitions

### Baryonic rotation curve

Given the component contributions,

$$
V_{\mathrm{bar}}^2(R)=V_{\mathrm{gas}}^2(R)+\Upsilon_{\mathrm{disk}}V_{\mathrm{disk}}^2(R)+\Upsilon_{\mathrm{bul}}V_{\mathrm{bul}}^2(R).
$$

If you are working directly from SPARC `*_rotmod.dat`, the conventional fixed
choices are $\Upsilon_{\mathrm{disk}}=0.5$ and $\Upsilon_{\mathrm{bul}}=0.7$.

### Outer-region selection

Let $R_{\max}$ be the largest sampled radius.

We define the “outer” subset as:

- Primary rule: all points with $R \ge 0.6\,R_{\max}$.
- Fallback rule: if that yields fewer than 5 points, use the last
  $K=\max\left(5,\lceil 0.4N\rceil\right)$ points (largest radii).

This matches the stated intent: **outer 40% or $R>0.6R_{\max}$, whichever yields
at least 5 points**.

### Robust location (Huber)

On the selected outer set, we compute a Huber M-estimator location of
$\Delta(R)$ with tuning constant $c=1.345$ (a common “95% efficiency” choice
under Gaussian residuals).

This repository does **not** depend on `statsmodels`; the implementation in
[toy_models/q_est_sparc175.py](toy_models/q_est_sparc175.py) uses a standard
iteratively reweighted least-squares (IRLS) Huber location with a MAD scale.

## Galaxy list (175)

The 175 galaxies are taken from the per-galaxy files present in:
`toy_models/out_sparc_runs_full_with_composition/galaxies/`.

<details>
<summary>Alphabetical list</summary>

CamB, D512-2, D564-8, D631-7, DDO064, DDO154, DDO161, DDO168, DDO170, ESO079-G014, ESO116-G012, ESO444-G084, ESO563-G021, F561-1, F563-1, F563-V1, F563-V2, F565-V2, F567-2, F568-1, F568-3, F568-V1, F571-8, F571-V1, F574-1, F574-2, F579-V1, F583-1, F583-4, IC2574, IC4202, KK98-251, NGC0024, NGC0055, NGC0100, NGC0247, NGC0289, NGC0300, NGC0801, NGC0891, NGC1003, NGC1090, NGC1705, NGC2366, NGC2403, NGC2683, NGC2841, NGC2903, NGC2915, NGC2955, NGC2976, NGC2998, NGC3109, NGC3198, NGC3521, NGC3726, NGC3741, NGC3769, NGC3877, NGC3893, NGC3917, NGC3949, NGC3953, NGC3972, NGC3992, NGC4010, NGC4013, NGC4051, NGC4068, NGC4085, NGC4088, NGC4100, NGC4138, NGC4157, NGC4183, NGC4214, NGC4217, NGC4389, NGC4559, NGC5005, NGC5033, NGC5055, NGC5371, NGC5585, NGC5907, NGC5985, NGC6015, NGC6195, NGC6503, NGC6674, NGC6789, NGC6946, NGC7331, NGC7793, NGC7814, PGC51017, UGC00128, UGC00191, UGC00634, UGC00731, UGC00891, UGC01230, UGC01281, UGC02023, UGC02259, UGC02455, UGC02487, UGC02885, UGC02916, UGC02953, UGC03205, UGC03546, UGC03580, UGC04278, UGC04305, UGC04325, UGC04483, UGC04499, UGC05005, UGC05253, UGC05414, UGC05716, UGC05721, UGC05750, UGC05764, UGC05829, UGC05918, UGC05986, UGC05999, UGC06399, UGC06446, UGC06614, UGC06628, UGC06667, UGC06786, UGC06787, UGC06818, UGC06917, UGC06923, UGC06930, UGC06973, UGC06983, UGC07089, UGC07125, UGC07151, UGC07232, UGC07261, UGC07323, UGC07399, UGC07524, UGC07559, UGC07577, UGC07603, UGC07608, UGC07690, UGC07866, UGC08286, UGC08490, UGC08550, UGC08699, UGC08837, UGC09037, UGC09133, UGC09992, UGC10310, UGC11455, UGC11557, UGC11820, UGC11914, UGC12506, UGC12632, UGC12732, UGCA281, UGCA442, UGCA444

</details>

## Representative `Q_est` values (6 galaxies)

Computed from the local per-galaxy CSVs using the procedure above:

| Galaxy | `Q_est` $(\mathrm{km/s})^2$ |
|---|---:|
| UGCA444 | 917.48 |
| DDO154 | 1897.31 |
| NGC6503 | 10996.10 |
| NGC2841 | 65847.14 |
| UGC09133 | 40356.44 |
| ESO563-G021 | 72282.96 |

## How to compute the full 175-galaxy catalogue (local)

This repo includes a small script that writes a CSV catalogue:

```bash
python toy_models/q_est_sparc175.py
```

Outputs:
- `toy_models/out_sparc_runs_full_with_composition/q_est.csv`

To also print the representative sample table:

```bash
python toy_models/q_est_sparc175.py --print-sample
```

## How to compute from raw `*_rotmod.dat` (if you download them)

If you have a directory of SPARC rotmod files (e.g. from the SPARC download), run:

```bash
python toy_models/q_est_sparc175.py --rotmod-dir path/to/Rotmod_LTG --out-csv q_est_from_rotmod.csv
```

You can override the mass-to-light scalings if needed:

```bash
python toy_models/q_est_sparc175.py --rotmod-dir path/to/Rotmod_LTG --ups-disk 0.5 --ups-bul 0.7
```

## Optional: using `Q_est` in simple regressions

If you also parse SPARC Table 1 (`SPARC_Lelli2016c.mrt`) to obtain per-galaxy
baryonic mass $M_b$ and gas fraction $f_{\mathrm{gas}}$, you can join and run a
minimal linear model such as:

$$
\log_{10} Q = a\,\log_{10} M_b + b + c\,f_{\mathrm{gas}}.
$$

Example (column names in the `.mrt` parse may differ; adjust as needed):

```python
import numpy as np
import pandas as pd

q = pd.read_csv('toy_models/out_sparc_runs_full_with_composition/q_est.csv')

# Parse SPARC_Lelli2016c.mrt into a DataFrame 'mrt' by your preferred method.
# Ensure it contains: galaxy name, Mb (or logMb), and f_gas.
mrt = pd.read_csv('SPARC_Lelli2016c.mrt', delim_whitespace=True, comment='#')

df = q.merge(mrt, left_on='galaxy', right_on='Galaxy', how='inner')

# If you need logs, restrict to Q_est > 0
df = df[np.isfinite(df.q_est_kms2) & (df.q_est_kms2 > 0)]
y = np.log10(df.q_est_kms2.to_numpy())

# Replace these with your actual column names
logMb = df['logMb'].to_numpy()
fgas = df['f_gas'].to_numpy()

X = np.column_stack([np.ones(len(df)), logMb, fgas])
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
print({'b': beta[0], 'a': beta[1], 'c': beta[2]})
```

## Notes and caveats

- `Q_est` is a **non-fitted** statistic; it can be negative if the outer data
  prefer $V_{\mathrm{obs}}^2 < V_{\mathrm{bar}}^2$ over the chosen outer region.
- The Huber location is robust to a small number of outlying radii, but it is
  still sensitive to systematic issues (beam smearing, non-circular motions,
  inclination errors) that affect the outer curve coherently.
- If you want to compare to the toy-model fitted amplitude `q_best_kms2`, join
  `q_est.csv` with `toy_models/out_sparc_runs_full_with_composition/summary.csv` on
  the `galaxy` column.
