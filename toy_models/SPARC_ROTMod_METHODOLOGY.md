# SPARC rotmod runner methodology (Spacetime Mechanics)

This document describes the exact methodology implemented in:
- [toy_models/sparc_rotmod_runner.py](toy_models/sparc_rotmod_runner.py)

The goal is to provide a **transparent, reproducible** way to apply the current
auxiliary-field / edge-response toy model to a set of galaxies with SPARC
"rotmod" mass-model inputs.

## 1. Inputs

### 1.1 SPARC rotmod files

Each `*_rotmod.dat` file contains a rotation curve with baryonic component
contributions. The script expects whitespace-delimited columns with header lines
starting with `#`.

Columns used (by index):
- `Rad` (kpc)
- `Vobs` (km/s)
- `errV` (km/s)
- `Vgas` (km/s)
- `Vdisk` (km/s)
- `Vbul` (km/s)

The script ignores any additional columns.

### 1.2 Parameters

The runner exposes the following command-line parameters:

- `--sigma-kpc` (default 2.0)
  - Width of the localized source bump `S(R)` that triggers the auxiliary field.

- `--ups-disk` (default 0.5) and `--ups-bul` (default 0.7)
  - Mass-to-light rescalings for disk and bulge templates.

- `--a0-ms2` (default `1.2e-10`)
  - Reference acceleration scale $a_0$ in SI units.

The runner currently fits **one free parameter per galaxy**: `Q`.

Optional metadata join:
- `--sparc-mrt <path>`
  - If provided, the runner parses SPARC Table 1 (`SPARC_Lelli2016c.mrt`) and appends
    metadata columns (e.g., `SBdisk`, `MHI`, `Rdisk`, `Vflat`, quality flag) to `summary.csv`.

## 2. Unit conventions

The rotmod inputs use `R` in kpc and velocities in km/s.

The runner computes accelerations in:

$$
[g] = (\mathrm{km/s})^2/\mathrm{kpc}
$$

The conversion used is:

$$
1\, (\mathrm{km/s})^2/\mathrm{kpc} = \frac{10^6}{\mathrm{kpc\_in\_m}}\, \mathrm{m/s^2}
$$

where `kpc_in_m = 3.085677581491367e19`.

Thus:

$$
 a_0\,[(\mathrm{km/s})^2/\mathrm{kpc}] = \frac{a_0\,[\mathrm{m/s^2}]}{10^6/\mathrm{kpc\_in\_m}}
$$

## 3. Baryonic curve construction

From the rotmod inputs the baryonic circular-speed template is constructed as:

$$
V_{\rm bar}^2(R) = V_{\rm gas}^2(R) + \Upsilon_{\rm disk} V_{\rm disk}^2(R) + \Upsilon_{\rm bul} V_{\rm bul}^2(R).
$$

Baryonic (Newtonian) centripetal acceleration is then:

$$
 g_{\rm bar}(R) = \frac{V_{\rm bar}^2(R)}{R}.
$$

## 4. Transition radius $R_t$

The runner estimates a transition radius $R_t$ defined by:

$$
 g_{\rm bar}(R_t) \approx a_0.
$$

Implementation details:
- It computes $\log(g_{\rm bar}/a_0)$ at the sampled radii.
- If it finds a sign change from $\ge 0$ to $\le 0$ between adjacent points, it
  performs **log-linear interpolation** in $(\log R, \log(g_{\rm bar}/a_0))$ to
  estimate $R_t$.
- If no crossing is present in the tabulated range, it returns the sampled point
  closest to $g_{\rm bar}=a_0$.

This is deterministic and requires no smoothing.

## 5. Auxiliary edge-response model

### 5.1 Effective 2D radial Poisson operator

The auxiliary field $\chi$ is defined by the effective 2D radial Poisson equation:

$$
\frac{1}{R}\frac{d}{dR}\left(R\, \frac{d\chi}{dR}\right) = S(R).
$$

Define $u(R) = R\chi'(R)$, so $u'(R) = R S(R)$.

### 5.2 Localized source bump

The source is chosen to be a Gaussian bump near the transition radius:

$$
 S_0(R) = \exp\left(-\frac{(R-R_t)^2}{2\sigma^2}\right)
$$

and then normalized so that:

$$
\int_0^\infty R\, S(R)\, dR = 1.
$$

With this normalization, for radii beyond the bump region:

$$
\chi'(R) \to \frac{1}{R}.
$$

The runner evaluates the cumulative integral for $u(R)$ using a trapezoid rule
on the sampled radii.

### 5.3 Coupling to observed dynamics

The total modeled acceleration is defined as:

$$
 g_{\rm tot}(R) = g_{\rm bar}(R) + Q\, \chi'_{\rm unit}(R),
$$

where $Q \ge 0$ is fitted per galaxy.

The modeled circular speed is:

$$
 V_{\rm model}(R) = \sqrt{g_{\rm tot}(R)\,R}.
$$

Interpretation of $Q$:
- At large $R$, $\chi'_{\rm unit}(R) \approx 1/R$, so the extra contribution to
  $V^2$ approaches $Q$.
- Therefore $\sqrt{Q}$ is the **asymptotic extra flat velocity scale** generated
  by the auxiliary field.

## 6. Fit procedure

The runner fits exactly one parameter per galaxy: $Q$.

It minimizes weighted chi-squared:

$$
\chi^2(Q) = \sum_i \left(\frac{V_{\rm model}(R_i; Q) - V_{\rm obs}(R_i)}{\sigma_{V,i}}\right)^2.
$$

The minimization uses **golden-section search** on a fixed interval:

- Lower bound: $Q \in [0, \ldots]$
- Upper bound: $Q_{\rm hi} = \max(10, 2\,V_{\rm obs,max}^2)$

This is deterministic and requires no derivative evaluations.

The script also reports a reduced chi-squared proxy:

$$
\chi^2_{\rm red} = \chi^2 / (N-1).
$$

## 7. Outputs

### 7.1 Per-galaxy CSV

For each galaxy, the runner writes:

`out_dir/galaxies/<galaxy>.csv`

Columns:
- `r_kpc`
- `vobs_kms`
- `e_vobs_kms`
- `vbar_kms`
- `vmodel_kms`
- `gbar_kms2_per_kpc`
- `gextra_kms2_per_kpc`
- `gtot_kms2_per_kpc`

For transparency, the runner also writes the rotmod component velocities and
their *fractional contributions* to $V_{\rm bar}^2$ at each sampled radius:
- `vgas_kms`, `vdisk_kms`, `vbul_kms`
- `frac_gas`, `frac_disk`, `frac_bul`

Fractions are defined using the same mass-to-light scalings as $V_{\rm bar}^2$:
$$
\mathrm{frac}_{\rm gas}(R)=\frac{V_{\rm gas}^2}{V_{\rm bar}^2},\quad
\mathrm{frac}_{\rm disk}(R)=\frac{\Upsilon_{\rm disk}V_{\rm disk}^2}{V_{\rm bar}^2},\quad
\mathrm{frac}_{\rm bul}(R)=\frac{\Upsilon_{\rm bul}V_{\rm bul}^2}{V_{\rm bar}^2}.
$$

### 7.2 Summary CSV

The runner writes:

`out_dir/summary.csv`

Columns include:
- Best-fit `Q`
- Estimated `R_t`
- `sqrt(Q)` as the asymptotic extra flat velocity scale

## 7.3 Derived “center action” and “edge reaction” proxies (with rationale)

The runner writes several derived columns intended to test the hypothesis that an
internal baryonic “center action” correlates with an outer “edge reaction”. These
are chosen to be (i) computable from rotmod alone, (ii) relatively insensitive to
single-point outliers, and (iii) interpretable within the present toy model.

### Center-action proxies

- `gbar_inner_kms2_per_kpc`
  - Definition: `gbar` evaluated at the first sampled radius.
  - Rationale: simplest proxy, but **least robust** (inner points can be affected
    by beam smearing, non-circular motions, and limited resolution). Kept mainly
    for completeness and diagnostic review.

- `gbar_rt_kms2_per_kpc` and `gbar_half_rt_kms2_per_kpc`
  - Definition: log-log interpolated `gbar(R)` evaluated at `R_t` and at `0.5 R_t`.
  - Rationale: these align with the model’s own “edge/transition” scale and avoid
    relying solely on the innermost datapoint. `gbar(0.5 R_t)` is a convenient
    “inner-but-not-central” measure.

- `gbar_1kpc_kms2_per_kpc` and `gbar_2kpc_kms2_per_kpc`
  - Definition: log-log interpolated `gbar(R)` at fixed radii 1 kpc and 2 kpc.
  - Rationale: easy cross-galaxy comparison on a common physical scale.
  - Note: if the rotmod data do not cover that radius, the runner writes NaN.

- `s_in_dlng_dlnr`
  - Definition: an inner slope estimate $s_{\rm in}=d\ln g_{\rm bar}/d\ln R$ using
    an unweighted least-squares fit over a small inner window (by default indices
    1..5 where available).
  - Rationale: captures baryonic **compactness/shape** using only the rotmod curve,
    and is less sensitive to absolute scaling uncertainties than a single-point
    metric.

### Composition / overdensity-proxy metrics (new)

To directly test whether **inner baryonic composition** correlates with an
outer **edge reaction**, the runner reports gas/disk/bulge fractions near the
model-defined transition radius.

- `frac_gas_half_rt`, `frac_disk_half_rt`, `frac_bul_half_rt` with `r_near_half_rt_kpc`
  - Definition: component fractions at the *nearest sampled radius* to $0.5R_t$.
  - Rationale: a robust, model-aligned proxy for “inner composition” that does not
    require extrapolating to $R\to0$ and avoids log interpolation on potentially
    zero/negative component velocities.

- `frac_gas_rt`, `frac_disk_rt`, `frac_bul_rt` with `r_near_rt_kpc`
  - Definition: component fractions at the nearest sampled radius to $R_t$.
  - Rationale: a direct “composition at the transition” measure.

- `frac_bul_peak`, `r_bul_peak_kpc`
  - Definition: peak bulge fraction (over all sampled radii) and the radius where it occurs.
  - Rationale: a simple proxy for central overdensity / bulge dominance.

If `--sparc-mrt` is provided, additional SPARC Table 1 metadata columns are
added to `summary.csv` as `sparc_*` fields (e.g., `sparc_SBdisk_solLum_pc2`,
`sparc_MHI_1e9solMass`, `sparc_Rdisk_kpc`). These are useful “composition” and
structural proxies beyond what can be inferred from rotmod alone.

### Edge-reaction proxies

- `q_best_kms2` and `v_extra_asym_kms = sqrt(q_best_kms2)`
  - Definition: best-fit auxiliary-field amplitude parameter and its velocity-scale.
  - Rationale: in this toy model, the auxiliary field asymptotes to $g_{\rm extra}\sim Q/R$,
    implying $V_{\rm extra}^2\to Q$ at large radii. Thus $\sqrt{Q}$ is a direct
    “edge reaction amplitude” proxy.

- `vobs_outer_kms`
  - Definition: median of the last 5 observed velocity points.
  - Rationale: a simple outer-speed summary that is more robust than using only
    the last point.

- `outer_resid_mean_z`, `outer_resid_rms_z`, `outer_chi2`
  - Definition: mean and RMS of standardized residuals $z=(V_{\rm model}-V_{\rm obs})/\sigma_V$,
    plus the chi-squared contribution, computed over an “outer” region defined as
    `R >= 2 R_t`.
  - Rationale: explicitly tests whether the edge-response phenomenology is working
    where it is supposed to—**in the outskirts**—and helps detect systematic under/over-shoot.

## 8. Reproducibility notes

- The algorithm is fully deterministic.
- No random seeds are used.
- Only Python standard library modules are required.
- All outputs are CSV for easy third-party verification.

## 9. Scope and limitations (explicit)

This is a *phenomenology runner* to generate falsifiables and correlations.
Limitations to keep in mind:

- Disk geometry is approximated as a 1D radial effective problem.
- $\Upsilon_{\rm disk}$ and $\Upsilon_{\rm bul}$ are held fixed unless you rerun
  with different values; no marginalization is performed.
- The shape of the source bump is assumed Gaussian; other kernels may be tested.
- The transition-radius estimate uses raw sampled points (no smoothing).

These limitations are intentional at this stage to keep the methodology clear
and auditable.
