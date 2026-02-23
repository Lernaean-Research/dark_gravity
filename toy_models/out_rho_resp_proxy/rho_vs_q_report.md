# Outer ρ-slope closeness vs Q (q_est)

This report tests whether the *outer* spherical-inversion proxy slope

- `rho_slope_outer_abs` (fit to log10(|ρ_proxy|) vs log10(r))
- `rho_closeness_abs = |rho_slope_outer_abs + 2|`

correlates with the robust outer statistic `q_est_kms2` and with fit-vs-robust disagreement.

**Files**

- merged catalogue: `toy_models/out_rho_resp_proxy/rho_vs_q_merged.csv`

## Correlations (permutation p-values; two-sided)

Columns: n, Pearson r (p_perm), Spearman ρ (p_perm).

| test | n | pearson r | p_perm | spearman ρ | p_perm |
|---|---:|---:|---:|---:|---:|
| closeness_abs vs q_est | 171 | 0.166 | 0.0290 | 0.170 | 0.0264 |
| closeness_abs vs log10(q_est) | 169 | 0.096 | 0.2110 | 0.199 | 0.0088 |
| closeness_abs vs abs(q_est-q_best) | 171 | 0.046 | 0.4951 | -0.050 | 0.5179 |
| closeness_abs vs (q_est-q_best) | 171 | -0.065 | 0.3121 | 0.080 | 0.2947 |
| closeness_pos vs q_est | 168 | 0.089 | 0.2386 | 0.108 | 0.1666 |
| closeness_pos vs log10(q_est) | 167 | -0.017 | 0.8216 | 0.128 | 0.1044 |
| closeness_pos vs abs(q_est-q_best) | 168 | 0.039 | 0.5661 | -0.082 | 0.2893 |
| closeness_pos vs (q_est-q_best) | 168 | -0.067 | 0.2627 | 0.049 | 0.5155 |
| [flat dv2] closeness_abs vs log10(q_est) | 97 | 0.150 | 0.1456 | 0.237 | 0.0226 |
| [flat dv2] closeness_abs vs abs(q_est-q_best) | 97 | -0.194 | 0.0588 | -0.209 | 0.0446 |

## Partial correlations (residualized controls; permutation p-values)

Columns: n, partial Pearson r (p_perm), partial Spearman ρ (p_perm).

| test | n | pearson r | p_perm | spearman ρ | p_perm |
|---|---:|---:|---:|---:|---:|
| partial: closeness_abs vs log10(q_est) (controls: logVflat) | 135 | -0.020 | 0.8066 | 0.064 | 0.4519 |
| partial: closeness_abs vs log10(q_est) (controls: logVflat, logRdisk) | 135 | -0.012 | 0.8816 | 0.061 | 0.4691 |
| partial: closeness_abs vs log10(q_est) (controls: logVflat, logRdisk, logD) | 135 | -0.012 | 0.8804 | 0.064 | 0.4481 |
| partial: closeness_abs vs abs(q_est-q_best) (controls: logVflat, logRdisk) | 135 | 0.017 | 0.8236 | -0.168 | 0.0514 |
| partial: closeness_abs vs abs(q_est-q_best) (controls: logVflat, logRdisk, q_best) | 135 | -0.099 | 0.2308 | -0.169 | 0.0512 |
| [flat dv2] partial: closeness_abs vs log10(q_est) (controls: logVflat, logRdisk) | 92 | 0.076 | 0.4587 | 0.072 | 0.5071 |
| [flat dv2] partial: closeness_abs vs abs(q_est-q_best) (controls: logVflat, logRdisk) | 92 | -0.245 | 0.0258 | -0.292 | 0.0054 |

## Notes
- `q_best_kms2` is constrained ≥0 by construction; `q_est_kms2` can be negative in principle (though typically positive).
- `rho_proxy` is a spherical diagnostic applied to disks; interpret the slope as a *shape sanity check*, not a literal density.
- The [flat dv2] subset keeps only galaxies with |dv2_outer_log_slope| ≤ 0.5 (Δv² roughly outer-flat in log–log).
