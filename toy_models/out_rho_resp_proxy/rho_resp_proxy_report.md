# Response-density proxy from SPARC residuals

This report summarizes the spherical-inversion proxy

$$\rho_{proxy}(r)\;\propto\;\frac{1}{4\pi r^2}\,\frac{d}{dr}\big(r\,\Delta v^2(r)\big),\quad \Delta v^2\equiv v_{obs}^2-v_{bar}^2.$$

For an approximately flat outer residual (Δv² ≈ const), one expects ρ ∝ r^{-2} in the outer region.

## Outer log-slope summary
The outer region is selected with the same rule as Q_est: r ≥ outer_rfrac·r_max (fallback: last outer_last_frac points).

**Positive-only slope** (fit log10(ρ_proxy) vs log10(r) using only points with ρ_proxy>0 in the outer region):

- n_galaxies_used: 168
- mean_slope: -1.668
- p10/p50/p90: -3.860, -1.813, 0.313
- within 0.5 of -2: 65

**Absolute-value slope** (fit log10(|ρ_proxy|) vs log10(r) in the outer region):

- n_galaxies_used: 171
- mean_slope: -1.713
- p10/p50/p90: -3.826, -1.823, 0.231
- within 0.5 of -2: 64

## Notes / caveats
- This is a spherical diagnostic applied to disk galaxies; treat it as a *shape sanity check*, not a literal density reconstruction.
- If Δv² is not flat in the outer region, the expected slope can deviate from -2.
- Negative ρ_proxy can occur where the residual decreases with radius; the absolute-value slope is included as a robustness diagnostic.
