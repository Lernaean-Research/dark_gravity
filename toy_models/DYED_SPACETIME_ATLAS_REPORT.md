# Dyed-Fabric SPARC Atlas: Components, Rationale, and Per-Galaxy Notes

This document explains the **3-panel** dyed-fabric atlas outputs in `toy_models/out_dyed_spacetime/` and provides per-galaxy quantitative notes in the same alphabetical order as the rendered pages.

Although this lives under `toy_models/` (historical prototyping name), the atlas figures are rendered from **SPARC-derived per-galaxy rotation-curve outputs**, with additional derived diagnostics and phenomenological overlays; see the rendering methodology for a measured/derived/fitted/illustrative provenance breakdown.

Note: six-panel (2×3) composite renders are produced to separate output folders (e.g. `toy_models/out_spacetime_sixpanel_*`). The computational definitions of the shared panels (rotation/potential/dye) are the same; see the methodology link below for the full specification.

For a transparent, reproducible description of how each panel is computed and drawn (including uncertainty propagation and the 6-panel layout), see:

- [DYED_SPACETIME_RENDERING_METHODOLOGY.md](DYED_SPACETIME_RENDERING_METHODOLOGY.md)
- [DYED_SPACETIME_SIX_PANEL_HOW_TO_READ.md](DYED_SPACETIME_SIX_PANEL_HOW_TO_READ.md) (reader-facing, panel-by-panel guide)

Primary render outputs:

3-panel dyed-fabric atlas (this report’s per-galaxy notes refer to these pages):

- Multi-page atlas PDF: [toy_models/out_dyed_spacetime/dyed_spacetime_pages.pdf](toy_models/out_dyed_spacetime/dyed_spacetime_pages.pdf)
- Contact sheet PDF: [toy_models/out_dyed_spacetime/dyed_spacetime_contact.pdf](toy_models/out_dyed_spacetime/dyed_spacetime_contact.pdf)
- Per-galaxy PNG directory: [toy_models/out_dyed_spacetime/png](toy_models/out_dyed_spacetime/png)

6-panel (2×3) atlas (current full-catalogue render):

- Multi-page atlas PDF: [toy_models/out_spacetime_sixpanel_full_v3/dyed_spacetime_pages.pdf](toy_models/out_spacetime_sixpanel_full_v3/dyed_spacetime_pages.pdf)
- Per-galaxy PNG directory: [toy_models/out_spacetime_sixpanel_full_v3/png](toy_models/out_spacetime_sixpanel_full_v3/png)

6-panel (2×3) atlas (Q-comparison variant; dual overlay in Panels 1 and 6):

- Multi-page atlas PDF: [toy_models/out_spacetime_sixpanel_full_v3_qcompare/dyed_spacetime_pages.pdf](toy_models/out_spacetime_sixpanel_full_v3_qcompare/dyed_spacetime_pages.pdf)
- Per-galaxy PNG directory: [toy_models/out_spacetime_sixpanel_full_v3_qcompare/png](toy_models/out_spacetime_sixpanel_full_v3_qcompare/png)

## How to read this atlas (executive)

**Paper-ready framing.** Each page is a phenomenology-first visualization: it encodes what the observed circular-orbit kinematics imply about an **effective** radial potential in the rotation-supported sector, without claiming a unique GR metric reconstruction. The dyed-fabric panel is therefore a visual encoding of an inferred potential depth profile (with global normalization for cross-galaxy comparability), not an embedding diagram and not a computed geodesic map.

**Reader-friendly translation.** Think of it as: *given the measured orbital speeds, what radial pull would a test particle have to feel to stay on those circular orbits?* We integrate that pull to get a potential-like depth curve, then render the depth as dye intensity.

Use it in this order:

- **Rotation curve**: check where `v_obs(R)` departs from `v_bar(R)` and whether the fitted `v_model(R)` tracks the data within uncertainties.
- **Potential**: interpret the curve and its band as the integrated consequence of the observed centripetal acceleration $g_{obs}=v_{obs}^2/R$ (band propagated from `e_vobs_kms` when present).
- **Dyed fabric**: read the dye intensity as a global-normalized rendering of the radial depth profile $f(R)\propto-\Phi_{obs}(R)$ (useful for quick cross-galaxy comparison).
- **Δχ² + Z**: treat the per-galaxy $\Delta\chi^2$ (and derived $Z\approx\sqrt{\Delta\chi^2}$) as a ranking/triage diagnostic for how much the 1-parameter extra term improves the weighted fit over baryons-only—not as a final discovery claim.

## 1) What each diagram component means

Each per-galaxy figure has three panels:

- **Rotation curve panel**: observed `v_obs(R)` (with ±1σ band if `e_vobs_kms` exists), plus the baryonic prediction `v_bar(R)` and the fitted total `v_model(R)` if available.
- **Potential panel**: an inferred effective potential profile \(\Phi_{obs}(R)\) defined (up to a constant) by

  $$g_{obs}(R)=\frac{v_{obs}^2(R)}{R},\qquad \frac{d\Phi_{obs}}{dR}=g_{obs}(R),\qquad \Phi_{obs}(R_{min})=0.$$

  If errors are present, we add a conservative propagated band using \(\sigma_g\approx 2|v|\sigma_v/R\) and integrate it.
- **Dyed-fabric panel**: a stylized 2D dye map of the **radial** depth profile \(f(R)\propto -\Phi_{obs}(R)\) rendered as a rotationally symmetric image.

### Rationale and defensibility notes

- The dyed-fabric panel is **not** a GR embedding diagram and it does not attempt to reconstruct a full metric \(g_{\mu\nu}\). It is intentionally phenomenology-first: a visual encoding of an inferred effective potential depth from the circular-orbit sector of the data.
- Orbit rings are **illustrative** (circular orbits), not computed geodesics.
- In the atlas render, depth is **globally normalized** across galaxies (so intensity is comparable).

## 2) Per-galaxy significance diagnostic (Δχ² with 1 extra parameter)

For each galaxy we compute:

- `chi2_bar`: χ² of baryons-only curve (`v_bar`) vs observations (`v_obs`) using `e_vobs_kms`
- `chi2_model`: χ² of fitted model (`v_model`) vs observations
- `Δχ² = chi2_bar - chi2_model`

Interpreting the extra term as adding one fitted degree of freedom, an approximate p-value is

$$p \approx \mathrm{erfc}\!\left(\sqrt{\Delta\chi^2/2}\right),$$

and an approximate equivalent Gaussian significance is \(Z\approx \sqrt{\Delta\chi^2}\). This is a ranking/triage tool and should not be treated as a final claim without checking modeling systematics.

## 3) Galaxy-by-galaxy notes (alphabetical; matches render order)

### CamB

- Figure: [toy_models/out_dyed_spacetime/png/CamB.png](toy_models/out_dyed_spacetime/png/CamB.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/CamB.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/CamB.csv)
- Summary: n=9, Q_flag=2, T=10, D=3.36 Mpc, Vflat=0 km/s, Rdisk=0.47 kpc, Rt=0.73 kpc, v_extra_asym=10.6 km/s, env_delta=0.124
- Fit diagnostic: n_used=9, chi2_bar=45.04, chi2_model=31.31, Δχ²=13.73, p≈2.11e-04, Z≈3.71, class=strong

- Implication: Outer residual RMS (z): 1.74
- Implication: Outer residual mean (z): -1.36
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### D512-2

- Figure: [toy_models/out_dyed_spacetime/png/D512-2.png](toy_models/out_dyed_spacetime/png/D512-2.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/D512-2.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/D512-2.csv)
- Summary: n=4, Q_flag=2, T=10, D=15.2 Mpc, Vflat=0 km/s, Rdisk=1.24 kpc, Rt=1.92 kpc, v_extra_asym=44.7 km/s, env_delta=3.59
- Fit diagnostic: n_used=4, chi2_bar=94.5, chi2_model=28.43, Δχ²=66.07, p≈<1e-6, Z≈8.13, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### D564-8

- Figure: [toy_models/out_dyed_spacetime/png/D564-8.png](toy_models/out_dyed_spacetime/png/D564-8.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/D564-8.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/D564-8.csv)
- Summary: n=6, Q_flag=2, T=10, D=8.79 Mpc, Vflat=0 km/s, Rdisk=0.61 kpc, Rt=1.02 kpc, v_extra_asym=26.9 km/s, env_delta=1.51
- Fit diagnostic: n_used=6, chi2_bar=236.1, chi2_model=15, Δχ²=221.1, p≈<1e-6, Z≈14.9, class=very-strong

- Implication: Outer residual RMS (z): 1.02
- Implication: Outer residual mean (z): 0.553
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### D631-7

- Figure: [toy_models/out_dyed_spacetime/png/D631-7.png](toy_models/out_dyed_spacetime/png/D631-7.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/D631-7.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/D631-7.csv)
- Summary: n=16, Q_flag=1, T=10, D=7.72 Mpc, Vflat=57.7 km/s, Rdisk=0.7 kpc, Rt=1.35 kpc, v_extra_asym=51.3 km/s, env_delta=0.618
- Fit diagnostic: n_used=16, chi2_bar=1693, chi2_model=15.43, Δχ²=1678, p≈<1e-6, Z≈41, class=very-strong

- Implication: Outer residual RMS (z): 0.916
- Implication: Outer residual mean (z): -0.361
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### DDO064

- Figure: [toy_models/out_dyed_spacetime/png/DDO064.png](toy_models/out_dyed_spacetime/png/DDO064.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/DDO064.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/DDO064.csv)
- Summary: n=14, Q_flag=1, T=10, D=6.8 Mpc, Vflat=46.1 km/s, Rdisk=0.69 kpc, Rt=1.88 kpc, v_extra_asym=59 km/s, env_delta=1.49
- Fit diagnostic: n_used=14, chi2_bar=179.1, chi2_model=16.53, Δχ²=162.6, p≈<1e-6, Z≈12.8, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### DDO154

- Figure: [toy_models/out_dyed_spacetime/png/DDO154.png](toy_models/out_dyed_spacetime/png/DDO154.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/DDO154.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/DDO154.csv)
- Summary: n=12, Q_flag=2, T=10, D=4.04 Mpc, Vflat=47 km/s, Rdisk=0.37 kpc, Rt=0.49 kpc, v_extra_asym=47.6 km/s, env_delta=1.12
- Fit diagnostic: n_used=12, chi2_bar=7.04e+04, chi2_model=230, Δχ²=7.017e+04, p≈<1e-6, Z≈265, class=very-strong

- Implication: Outer residual RMS (z): 4.5
- Implication: Outer residual mean (z): -0.954
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### DDO161

- Figure: [toy_models/out_dyed_spacetime/png/DDO161.png](toy_models/out_dyed_spacetime/png/DDO161.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/DDO161.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/DDO161.csv)
- Summary: n=31, Q_flag=1, T=10, D=7.5 Mpc, Vflat=66.3 km/s, Rdisk=1.22 kpc, Rt=2.02 kpc, v_extra_asym=54.2 km/s, env_delta=1.46
- Fit diagnostic: n_used=31, chi2_bar=1.152e+04, chi2_model=263.2, Δχ²=1.126e+04, p≈<1e-6, Z≈106, class=very-strong

- Implication: Outer residual RMS (z): 3.45
- Implication: Outer residual mean (z): 0.594
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### DDO168

- Figure: [toy_models/out_dyed_spacetime/png/DDO168.png](toy_models/out_dyed_spacetime/png/DDO168.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/DDO168.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/DDO168.csv)
- Summary: n=10, Q_flag=2, T=10, D=4.25 Mpc, Vflat=53.4 km/s, Rdisk=1.02 kpc, Rt=0.82 kpc, v_extra_asym=56.5 km/s, env_delta=0.895
- Fit diagnostic: n_used=10, chi2_bar=1609, chi2_model=32.54, Δχ²=1576, p≈<1e-6, Z≈39.7, class=very-strong

- Implication: Outer residual RMS (z): 2.1
- Implication: Outer residual mean (z): 0.212
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### DDO170

- Figure: [toy_models/out_dyed_spacetime/png/DDO170.png](toy_models/out_dyed_spacetime/png/DDO170.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/DDO170.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/DDO170.csv)
- Summary: n=8, Q_flag=2, T=10, D=15.4 Mpc, Vflat=60 km/s, Rdisk=1.95 kpc, Rt=1.87 kpc, v_extra_asym=52.5 km/s, env_delta=6.24
- Fit diagnostic: n_used=8, chi2_bar=4795, chi2_model=43.12, Δχ²=4751, p≈<1e-6, Z≈68.9, class=very-strong

- Implication: Outer residual RMS (z): 1.83
- Implication: Outer residual mean (z): 0.241
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### ESO079-G014

- Figure: [toy_models/out_dyed_spacetime/png/ESO079-G014.png](toy_models/out_dyed_spacetime/png/ESO079-G014.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/ESO079-G014.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/ESO079-G014.csv)
- Summary: n=15, Q_flag=1, T=4, D=28.7 Mpc, Vflat=175 km/s, Rdisk=5.08 kpc, Rt=0.98 kpc, v_extra_asym=136 km/s, env_delta=2
- Fit diagnostic: n_used=15, chi2_bar=5927, chi2_model=264.8, Δχ²=5662, p≈<1e-6, Z≈75.2, class=very-strong

- Implication: Outer residual RMS (z): 4.64
- Implication: Outer residual mean (z): 1.79
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### ESO116-G012

- Figure: [toy_models/out_dyed_spacetime/png/ESO116-G012.png](toy_models/out_dyed_spacetime/png/ESO116-G012.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/ESO116-G012.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/ESO116-G012.csv)
- Summary: n=15, Q_flag=1, T=7, D=13 Mpc, Vflat=109 km/s, Rdisk=1.51 kpc, Rt=1.85 kpc, v_extra_asym=99.7 km/s, env_delta=1.63
- Fit diagnostic: n_used=15, chi2_bar=4944, chi2_model=36.05, Δχ²=4908, p≈<1e-6, Z≈70.1, class=very-strong

- Implication: Outer residual RMS (z): 0.589
- Implication: Outer residual mean (z): 0.177
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### ESO444-G084

- Figure: [toy_models/out_dyed_spacetime/png/ESO444-G084.png](toy_models/out_dyed_spacetime/png/ESO444-G084.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/ESO444-G084.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/ESO444-G084.csv)
- Summary: n=7, Q_flag=2, T=10, D=4.83 Mpc, Vflat=0 km/s, Rdisk=0.46 kpc, Rt=0.77 kpc, v_extra_asym=74.9 km/s, env_delta=0.718
- Fit diagnostic: n_used=7, chi2_bar=1995, chi2_model=114, Δχ²=1881, p≈<1e-6, Z≈43.4, class=very-strong

- Implication: Outer residual RMS (z): 3.63
- Implication: Outer residual mean (z): -0.196
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### ESO563-G021

- Figure: [toy_models/out_dyed_spacetime/png/ESO563-G021.png](toy_models/out_dyed_spacetime/png/ESO563-G021.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/ESO563-G021.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/ESO563-G021.csv)
- Summary: n=30, Q_flag=1, T=4, D=60.8 Mpc, Vflat=315 km/s, Rdisk=5.45 kpc, Rt=2.76 kpc, v_extra_asym=220 km/s, env_delta=0.784
- Fit diagnostic: n_used=30, chi2_bar=7372, chi2_model=708.5, Δχ²=6663, p≈<1e-6, Z≈81.6, class=very-strong

- Implication: Outer residual RMS (z): 3.48
- Implication: Outer residual mean (z): -2.26
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F561-1

- Figure: [toy_models/out_dyed_spacetime/png/F561-1.png](toy_models/out_dyed_spacetime/png/F561-1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F561-1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F561-1.csv)
- Summary: n=6, Q_flag=3, T=9, D=66.4 Mpc, Vflat=50 km/s, Rdisk=2.79 kpc, Rt=1.61 kpc, v_extra_asym=31.4 km/s, env_delta=5.58
- Fit diagnostic: n_used=6, chi2_bar=21.9, chi2_model=3.094, Δχ²=18.81, p≈1.45e-05, Z≈4.34, class=strong

- Implication: Outer residual RMS (z): 0.779
- Implication: Outer residual mean (z): -0.0776
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F563-1

- Figure: [toy_models/out_dyed_spacetime/png/F563-1.png](toy_models/out_dyed_spacetime/png/F563-1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F563-1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F563-1.csv)
- Summary: n=17, Q_flag=1, T=9, D=48.9 Mpc, Vflat=110 km/s, Rdisk=3.52 kpc, Rt=1.78 kpc, v_extra_asym=103 km/s, env_delta=3.08
- Fit diagnostic: n_used=17, chi2_bar=539, chi2_model=9.884, Δχ²=529.1, p≈<1e-6, Z≈23, class=very-strong

- Implication: Outer residual RMS (z): 0.563
- Implication: Outer residual mean (z): 0.315
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F563-V1

- Figure: [toy_models/out_dyed_spacetime/png/F563-V1.png](toy_models/out_dyed_spacetime/png/F563-V1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F563-V1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F563-V1.csv)
- Summary: n=6, Q_flag=3, T=10, D=54 Mpc, Vflat=0 km/s, Rdisk=3.79 kpc, Rt=3.93 kpc, v_extra_asym=17.1 km/s, env_delta=3.26
- Fit diagnostic: n_used=6, chi2_bar=5.878, chi2_model=3.38, Δχ²=2.498, p≈0.114, Z≈1.58, class=weak

- Implication: Outer residual RMS (z): 0.771
- Implication: Outer residual mean (z): 0.771
- Implication: Extra-term improvement is weak under this diagnostic; baryons-only may already be adequate within errors or the effect is not well captured by a 1/R tail.

### F563-V2

- Figure: [toy_models/out_dyed_spacetime/png/F563-V2.png](toy_models/out_dyed_spacetime/png/F563-V2.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F563-V2.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F563-V2.csv)
- Summary: n=10, Q_flag=1, T=10, D=59.7 Mpc, Vflat=117 km/s, Rdisk=2.43 kpc, Rt=2.35 kpc, v_extra_asym=123 km/s, env_delta=2.05
- Fit diagnostic: n_used=10, chi2_bar=226.6, chi2_model=20.19, Δχ²=206.4, p≈<1e-6, Z≈14.4, class=very-strong

- Implication: Outer residual RMS (z): 0.942
- Implication: Outer residual mean (z): 0.475
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F565-V2

- Figure: [toy_models/out_dyed_spacetime/png/F565-V2.png](toy_models/out_dyed_spacetime/png/F565-V2.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F565-V2.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F565-V2.csv)
- Summary: n=7, Q_flag=2, T=10, D=51.8 Mpc, Vflat=0 km/s, Rdisk=2.17 kpc, Rt=7.54 kpc, v_extra_asym=93 km/s, env_delta=1.28
- Fit diagnostic: n_used=7, chi2_bar=303, chi2_model=61.93, Δχ²=241.1, p≈<1e-6, Z≈15.5, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F567-2

- Figure: [toy_models/out_dyed_spacetime/png/F567-2.png](toy_models/out_dyed_spacetime/png/F567-2.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F567-2.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F567-2.csv)
- Summary: n=5, Q_flag=3, T=9, D=79 Mpc, Vflat=0 km/s, Rdisk=3.08 kpc, Rt=1.92 kpc, v_extra_asym=45.4 km/s, env_delta=0.419
- Fit diagnostic: n_used=5, chi2_bar=51.16, chi2_model=2.993, Δχ²=48.17, p≈<1e-6, Z≈6.94, class=very-strong

- Implication: Outer residual RMS (z): 0.475
- Implication: Outer residual mean (z): 0.417
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F568-1

- Figure: [toy_models/out_dyed_spacetime/png/F568-1.png](toy_models/out_dyed_spacetime/png/F568-1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F568-1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F568-1.csv)
- Summary: n=12, Q_flag=1, T=5, D=90.7 Mpc, Vflat=0 km/s, Rdisk=5.18 kpc, Rt=1.32 kpc, v_extra_asym=120 km/s, env_delta=0.00455
- Fit diagnostic: n_used=12, chi2_bar=477.9, chi2_model=1, Δχ²=476.9, p≈<1e-6, Z≈21.8, class=very-strong

- Implication: Outer residual RMS (z): 0.197
- Implication: Outer residual mean (z): -0.00121
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F568-3

- Figure: [toy_models/out_dyed_spacetime/png/F568-3.png](toy_models/out_dyed_spacetime/png/F568-3.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F568-3.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F568-3.csv)
- Summary: n=18, Q_flag=1, T=7, D=82.4 Mpc, Vflat=0 km/s, Rdisk=4.99 kpc, Rt=4.19 kpc, v_extra_asym=105 km/s, env_delta=0.0736
- Fit diagnostic: n_used=18, chi2_bar=531.6, chi2_model=40.62, Δχ²=490.9, p≈<1e-6, Z≈22.2, class=very-strong

- Implication: Outer residual RMS (z): 1.43
- Implication: Outer residual mean (z): 1.03
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F568-V1

- Figure: [toy_models/out_dyed_spacetime/png/F568-V1.png](toy_models/out_dyed_spacetime/png/F568-V1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F568-V1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F568-V1.csv)
- Summary: n=15, Q_flag=1, T=7, D=80.6 Mpc, Vflat=112 km/s, Rdisk=2.85 kpc, Rt=1.18 kpc, v_extra_asym=110 km/s, env_delta=-0.0241
- Fit diagnostic: n_used=15, chi2_bar=683.5, chi2_model=3.087, Δχ²=680.5, p≈<1e-6, Z≈26.1, class=very-strong

- Implication: Outer residual RMS (z): 0.44
- Implication: Outer residual mean (z): 0.069
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F571-8

- Figure: [toy_models/out_dyed_spacetime/png/F571-8.png](toy_models/out_dyed_spacetime/png/F571-8.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F571-8.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F571-8.csv)
- Summary: n=13, Q_flag=1, T=5, D=53.3 Mpc, Vflat=140 km/s, Rdisk=3.56 kpc, Rt=1.54 kpc, v_extra_asym=112 km/s, env_delta=-0.0771
- Fit diagnostic: n_used=13, chi2_bar=2151, chi2_model=250.6, Δχ²=1900, p≈<1e-6, Z≈43.6, class=very-strong

- Implication: Outer residual RMS (z): 3.39
- Implication: Outer residual mean (z): 0.168
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F571-V1

- Figure: [toy_models/out_dyed_spacetime/png/F571-V1.png](toy_models/out_dyed_spacetime/png/F571-V1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F571-V1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F571-V1.csv)
- Summary: n=7, Q_flag=2, T=7, D=80.1 Mpc, Vflat=83.6 km/s, Rdisk=2.47 kpc, Rt=3.88 kpc, v_extra_asym=75.3 km/s, env_delta=-0.433
- Fit diagnostic: n_used=7, chi2_bar=279, chi2_model=2.989, Δχ²=276, p≈<1e-6, Z≈16.6, class=very-strong

- Implication: Outer residual RMS (z): 0.296
- Implication: Outer residual mean (z): 0.111
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F574-1

- Figure: [toy_models/out_dyed_spacetime/png/F574-1.png](toy_models/out_dyed_spacetime/png/F574-1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F574-1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F574-1.csv)
- Summary: n=14, Q_flag=1, T=7, D=96.8 Mpc, Vflat=97.8 km/s, Rdisk=4.46 kpc, Rt=1.41 kpc, v_extra_asym=87.7 km/s, env_delta=2.06
- Fit diagnostic: n_used=14, chi2_bar=1580, chi2_model=6.166, Δχ²=1574, p≈<1e-6, Z≈39.7, class=very-strong

- Implication: Outer residual RMS (z): 0.447
- Implication: Outer residual mean (z): 0.0466
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F574-2

- Figure: [toy_models/out_dyed_spacetime/png/F574-2.png](toy_models/out_dyed_spacetime/png/F574-2.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F574-2.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F574-2.csv)
- Summary: n=5, Q_flag=3, T=9, D=89.1 Mpc, Vflat=0 km/s, Rdisk=3.76 kpc, Rt=2.17 kpc, v_extra_asym=11.4 km/s, env_delta=0.997
- Fit diagnostic: n_used=5, chi2_bar=0.4449, chi2_model=0.2571, Δχ²=0.1877, p≈0.665, Z≈0.433, class=weak

- Implication: Outer residual RMS (z): 0.0523
- Implication: Outer residual mean (z): 0.011
- Implication: Extra-term improvement is weak under this diagnostic; baryons-only may already be adequate within errors or the effect is not well captured by a 1/R tail.

### F579-V1

- Figure: [toy_models/out_dyed_spacetime/png/F579-V1.png](toy_models/out_dyed_spacetime/png/F579-V1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F579-V1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F579-V1.csv)
- Summary: n=14, Q_flag=1, T=5, D=89.5 Mpc, Vflat=112 km/s, Rdisk=3.37 kpc, Rt=1.47 kpc, v_extra_asym=106 km/s, env_delta=-0.679
- Fit diagnostic: n_used=14, chi2_bar=390.9, chi2_model=40.9, Δχ²=350, p≈<1e-6, Z≈18.7, class=very-strong

- Implication: Outer residual RMS (z): 0.588
- Implication: Outer residual mean (z): 0.438
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F583-1

- Figure: [toy_models/out_dyed_spacetime/png/F583-1.png](toy_models/out_dyed_spacetime/png/F583-1.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F583-1.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F583-1.csv)
- Summary: n=25, Q_flag=1, T=9, D=35.4 Mpc, Vflat=85.8 km/s, Rdisk=2.36 kpc, Rt=1.22 kpc, v_extra_asym=70 km/s, env_delta=0.934
- Fit diagnostic: n_used=25, chi2_bar=1244, chi2_model=5.501, Δχ²=1238, p≈<1e-6, Z≈35.2, class=very-strong

- Implication: Outer residual RMS (z): 0.471
- Implication: Outer residual mean (z): -0.0737
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### F583-4

- Figure: [toy_models/out_dyed_spacetime/png/F583-4.png](toy_models/out_dyed_spacetime/png/F583-4.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/F583-4.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/F583-4.csv)
- Summary: n=12, Q_flag=1, T=5, D=53.3 Mpc, Vflat=0 km/s, Rdisk=1.93 kpc, Rt=1.94 kpc, v_extra_asym=60 km/s, env_delta=-0.0669
- Fit diagnostic: n_used=12, chi2_bar=458.7, chi2_model=15.78, Δχ²=442.9, p≈<1e-6, Z≈21, class=very-strong

- Implication: Outer residual RMS (z): 0.39
- Implication: Outer residual mean (z): 0.114
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### IC2574

- Figure: [toy_models/out_dyed_spacetime/png/IC2574.png](toy_models/out_dyed_spacetime/png/IC2574.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/IC2574.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/IC2574.csv)
- Summary: n=34, Q_flag=2, T=9, D=3.91 Mpc, Vflat=66.4 km/s, Rdisk=2.78 kpc, Rt=6.54 kpc, v_extra_asym=71.7 km/s, env_delta=0.437
- Fit diagnostic: n_used=34, chi2_bar=1.383e+04, chi2_model=1635, Δχ²=1.219e+04, p≈<1e-6, Z≈110, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### IC4202

- Figure: [toy_models/out_dyed_spacetime/png/IC4202.png](toy_models/out_dyed_spacetime/png/IC4202.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/IC4202.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/IC4202.csv)
- Summary: n=32, Q_flag=1, T=4, D=100 Mpc, Vflat=243 km/s, Rdisk=4.78 kpc, Rt=7.72 kpc, v_extra_asym=188 km/s, env_delta=4.46
- Fit diagnostic: n_used=32, chi2_bar=4833, chi2_model=1507, Δχ²=3326, p≈<1e-6, Z≈57.7, class=very-strong

- Implication: Outer residual RMS (z): 0.846
- Implication: Outer residual mean (z): 0.441
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### KK98-251

- Figure: [toy_models/out_dyed_spacetime/png/KK98-251.png](toy_models/out_dyed_spacetime/png/KK98-251.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/KK98-251.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/KK98-251.csv)
- Summary: n=15, Q_flag=2, T=10, D=6.8 Mpc, Vflat=33.7 km/s, Rdisk=1.34 kpc, Rt=1.89 kpc, v_extra_asym=33.9 km/s, env_delta=-0.231
- Fit diagnostic: n_used=15, chi2_bar=320.3, chi2_model=17.96, Δχ²=302.4, p≈<1e-6, Z≈17.4, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0024

- Figure: [toy_models/out_dyed_spacetime/png/NGC0024.png](toy_models/out_dyed_spacetime/png/NGC0024.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0024.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0024.csv)
- Summary: n=29, Q_flag=1, T=5, D=7.3 Mpc, Vflat=106 km/s, Rdisk=1.34 kpc, Rt=1.7 kpc, v_extra_asym=106 km/s, env_delta=0.0492
- Fit diagnostic: n_used=29, chi2_bar=2594, chi2_model=356, Δχ²=2238, p≈<1e-6, Z≈47.3, class=very-strong

- Implication: Outer residual RMS (z): 2.18
- Implication: Outer residual mean (z): 1.78
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0055

- Figure: [toy_models/out_dyed_spacetime/png/NGC0055.png](toy_models/out_dyed_spacetime/png/NGC0055.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0055.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0055.csv)
- Summary: n=21, Q_flag=2, T=9, D=2.11 Mpc, Vflat=85.6 km/s, Rdisk=6.11 kpc, Rt=1.84 kpc, v_extra_asym=62 km/s, env_delta=0.156
- Fit diagnostic: n_used=21, chi2_bar=2501, chi2_model=50.04, Δχ²=2451, p≈<1e-6, Z≈49.5, class=very-strong

- Implication: Outer residual RMS (z): 1.59
- Implication: Outer residual mean (z): -0.691
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0100

- Figure: [toy_models/out_dyed_spacetime/png/NGC0100.png](toy_models/out_dyed_spacetime/png/NGC0100.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0100.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0100.csv)
- Summary: n=21, Q_flag=1, T=6, D=13.5 Mpc, Vflat=88.1 km/s, Rdisk=1.66 kpc, Rt=1.59 kpc, v_extra_asym=75.5 km/s, env_delta=-0.587
- Fit diagnostic: n_used=21, chi2_bar=1079, chi2_model=5.437, Δχ²=1074, p≈<1e-6, Z≈32.8, class=very-strong

- Implication: Outer residual RMS (z): 0.578
- Implication: Outer residual mean (z): -0.0344
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0247

- Figure: [toy_models/out_dyed_spacetime/png/NGC0247.png](toy_models/out_dyed_spacetime/png/NGC0247.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0247.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0247.csv)
- Summary: n=26, Q_flag=2, T=7, D=3.7 Mpc, Vflat=105 km/s, Rdisk=3.74 kpc, Rt=2.15 kpc, v_extra_asym=83.8 km/s, env_delta=0.0655
- Fit diagnostic: n_used=26, chi2_bar=9241, chi2_model=1120, Δχ²=8121, p≈<1e-6, Z≈90.1, class=very-strong

- Implication: Outer residual RMS (z): 2.15
- Implication: Outer residual mean (z): 0.887
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0289

- Figure: [toy_models/out_dyed_spacetime/png/NGC0289.png](toy_models/out_dyed_spacetime/png/NGC0289.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0289.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0289.csv)
- Summary: n=28, Q_flag=2, T=4, D=20.8 Mpc, Vflat=163 km/s, Rdisk=6.74 kpc, Rt=6.17 kpc, v_extra_asym=144 km/s, env_delta=0.919
- Fit diagnostic: n_used=28, chi2_bar=4161, chi2_model=61.96, Δχ²=4099, p≈<1e-6, Z≈64, class=very-strong

- Implication: Outer residual RMS (z): 1.69
- Implication: Outer residual mean (z): -0.0747
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0300

- Figure: [toy_models/out_dyed_spacetime/png/NGC0300.png](toy_models/out_dyed_spacetime/png/NGC0300.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0300.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0300.csv)
- Summary: n=25, Q_flag=2, T=7, D=2.08 Mpc, Vflat=93.3 km/s, Rdisk=1.75 kpc, Rt=0.91 kpc, v_extra_asym=85 km/s, env_delta=0.16
- Fit diagnostic: n_used=25, chi2_bar=4035, chi2_model=53.45, Δχ²=3982, p≈<1e-6, Z≈63.1, class=very-strong

- Implication: Outer residual RMS (z): 1.13
- Implication: Outer residual mean (z): 0.23
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0801

- Figure: [toy_models/out_dyed_spacetime/png/NGC0801.png](toy_models/out_dyed_spacetime/png/NGC0801.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0801.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0801.csv)
- Summary: n=13, Q_flag=1, T=5, D=80.7 Mpc, Vflat=220 km/s, Rdisk=8.72 kpc, Rt=9.97 kpc, v_extra_asym=157 km/s, env_delta=1.09
- Fit diagnostic: n_used=13, chi2_bar=2541, chi2_model=162.9, Δχ²=2378, p≈<1e-6, Z≈48.8, class=very-strong

- Implication: Outer residual RMS (z): 2.21
- Implication: Outer residual mean (z): 0.0134
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC0891

- Figure: [toy_models/out_dyed_spacetime/png/NGC0891.png](toy_models/out_dyed_spacetime/png/NGC0891.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0891.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC0891.csv)
- Summary: n=18, Q_flag=1, T=3, D=9.91 Mpc, Vflat=216 km/s, Rdisk=2.55 kpc, Rt=9.67 kpc, v_extra_asym=152 km/s, env_delta=-0.634
- Fit diagnostic: n_used=18, chi2_bar=2958, chi2_model=240.7, Δχ²=2717, p≈<1e-6, Z≈52.1, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC1003

- Figure: [toy_models/out_dyed_spacetime/png/NGC1003.png](toy_models/out_dyed_spacetime/png/NGC1003.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC1003.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC1003.csv)
- Summary: n=36, Q_flag=1, T=6, D=11.4 Mpc, Vflat=110 km/s, Rdisk=1.61 kpc, Rt=1.25 kpc, v_extra_asym=92.4 km/s, env_delta=-0.686
- Fit diagnostic: n_used=36, chi2_bar=2.133e+04, chi2_model=577.2, Δχ²=2.075e+04, p≈<1e-6, Z≈144, class=very-strong

- Implication: Outer residual RMS (z): 4.12
- Implication: Outer residual mean (z): 0.036
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC1090

- Figure: [toy_models/out_dyed_spacetime/png/NGC1090.png](toy_models/out_dyed_spacetime/png/NGC1090.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC1090.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC1090.csv)
- Summary: n=24, Q_flag=1, T=4, D=37 Mpc, Vflat=164 km/s, Rdisk=3.53 kpc, Rt=2 kpc, v_extra_asym=128 km/s, env_delta=0.684
- Fit diagnostic: n_used=24, chi2_bar=9046, chi2_model=63.4, Δχ²=8982, p≈<1e-6, Z≈94.8, class=very-strong

- Implication: Outer residual RMS (z): 1.34
- Implication: Outer residual mean (z): 0.115
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC1705

- Figure: [toy_models/out_dyed_spacetime/png/NGC1705.png](toy_models/out_dyed_spacetime/png/NGC1705.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC1705.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC1705.csv)
- Summary: n=14, Q_flag=3, T=11, D=5.73 Mpc, Vflat=71.9 km/s, Rdisk=0.39 kpc, Rt=0.22 kpc, v_extra_asym=86 km/s, env_delta=0.335
- Fit diagnostic: n_used=14, chi2_bar=1344, chi2_model=128.9, Δχ²=1215, p≈<1e-6, Z≈34.9, class=very-strong

- Implication: Outer residual RMS (z): 3
- Implication: Outer residual mean (z): -0.473
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2366

- Figure: [toy_models/out_dyed_spacetime/png/NGC2366.png](toy_models/out_dyed_spacetime/png/NGC2366.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2366.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2366.csv)
- Summary: n=26, Q_flag=3, T=10, D=3.27 Mpc, Vflat=50.2 km/s, Rdisk=0.65 kpc, Rt=2.02 kpc, v_extra_asym=55.1 km/s, env_delta=0.265
- Fit diagnostic: n_used=26, chi2_bar=2336, chi2_model=160.6, Δχ²=2175, p≈<1e-6, Z≈46.6, class=very-strong

- Implication: Outer residual RMS (z): 2.61
- Implication: Outer residual mean (z): 2.37
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2403

- Figure: [toy_models/out_dyed_spacetime/png/NGC2403.png](toy_models/out_dyed_spacetime/png/NGC2403.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2403.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2403.csv)
- Summary: n=73, Q_flag=1, T=6, D=3.16 Mpc, Vflat=131 km/s, Rdisk=1.39 kpc, Rt=0.56 kpc, v_extra_asym=108 km/s, env_delta=0.29
- Fit diagnostic: n_used=73, chi2_bar=3.193e+05, chi2_model=3022, Δχ²=3.163e+05, p≈<1e-6, Z≈562, class=very-strong

- Implication: Outer residual RMS (z): 5.9
- Implication: Outer residual mean (z): -0.669
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2683

- Figure: [toy_models/out_dyed_spacetime/png/NGC2683.png](toy_models/out_dyed_spacetime/png/NGC2683.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2683.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2683.csv)
- Summary: n=11, Q_flag=2, T=3, D=9.81 Mpc, Vflat=154 km/s, Rdisk=2.18 kpc, Rt=6.94 kpc, v_extra_asym=146 km/s, env_delta=1.39
- Fit diagnostic: n_used=11, chi2_bar=689.3, chi2_model=56.96, Δχ²=632.3, p≈<1e-6, Z≈25.1, class=very-strong

- Implication: Outer residual RMS (z): 1.27
- Implication: Outer residual mean (z): 0.948
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2841

- Figure: [toy_models/out_dyed_spacetime/png/NGC2841.png](toy_models/out_dyed_spacetime/png/NGC2841.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2841.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2841.csv)
- Summary: n=50, Q_flag=1, T=3, D=14.1 Mpc, Vflat=285 km/s, Rdisk=3.64 kpc, Rt=11.7 kpc, v_extra_asym=254 km/s, env_delta=1.29
- Fit diagnostic: n_used=50, chi2_bar=3.731e+04, chi2_model=2434, Δχ²=3.488e+04, p≈<1e-6, Z≈187, class=very-strong

- Implication: Outer residual RMS (z): 1.93
- Implication: Outer residual mean (z): 0.145
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2903

- Figure: [toy_models/out_dyed_spacetime/png/NGC2903.png](toy_models/out_dyed_spacetime/png/NGC2903.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2903.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2903.csv)
- Summary: n=34, Q_flag=1, T=4, D=6.6 Mpc, Vflat=185 km/s, Rdisk=2.33 kpc, Rt=7.22 kpc, v_extra_asym=154 km/s, env_delta=1.34
- Fit diagnostic: n_used=34, chi2_bar=2.504e+04, chi2_model=687.7, Δχ²=2.435e+04, p≈<1e-6, Z≈156, class=very-strong

- Implication: Outer residual RMS (z): 0.644
- Implication: Outer residual mean (z): 0.3
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2915

- Figure: [toy_models/out_dyed_spacetime/png/NGC2915.png](toy_models/out_dyed_spacetime/png/NGC2915.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2915.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2915.csv)
- Summary: n=30, Q_flag=2, T=11, D=4.06 Mpc, Vflat=83.5 km/s, Rdisk=0.55 kpc, Rt=0.34 kpc, v_extra_asym=81.6 km/s, env_delta=0.271
- Fit diagnostic: n_used=30, chi2_bar=1770, chi2_model=22.29, Δχ²=1748, p≈<1e-6, Z≈41.8, class=very-strong

- Implication: Outer residual RMS (z): 0.816
- Implication: Outer residual mean (z): -0.151
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2955

- Figure: [toy_models/out_dyed_spacetime/png/NGC2955.png](toy_models/out_dyed_spacetime/png/NGC2955.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2955.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2955.csv)
- Summary: n=24, Q_flag=1, T=3, D=97.9 Mpc, Vflat=0 km/s, Rdisk=18.8 kpc, Rt=13 kpc, v_extra_asym=183 km/s, env_delta=0.34
- Fit diagnostic: n_used=24, chi2_bar=407.1, chi2_model=132.6, Δχ²=274.5, p≈<1e-6, Z≈16.6, class=very-strong

- Implication: Outer residual RMS (z): 1.13
- Implication: Outer residual mean (z): 0.933
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2976

- Figure: [toy_models/out_dyed_spacetime/png/NGC2976.png](toy_models/out_dyed_spacetime/png/NGC2976.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2976.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2976.csv)
- Summary: n=27, Q_flag=2, T=5, D=3.58 Mpc, Vflat=85.4 km/s, Rdisk=1.01 kpc, Rt=1.63 kpc, v_extra_asym=74.4 km/s, env_delta=0.387
- Fit diagnostic: n_used=27, chi2_bar=447.1, chi2_model=19.13, Δχ²=428, p≈<1e-6, Z≈20.7, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC2998

- Figure: [toy_models/out_dyed_spacetime/png/NGC2998.png](toy_models/out_dyed_spacetime/png/NGC2998.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2998.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC2998.csv)
- Summary: n=13, Q_flag=1, T=5, D=68.1 Mpc, Vflat=210 km/s, Rdisk=6.2 kpc, Rt=6.3 kpc, v_extra_asym=169 km/s, env_delta=-0.698
- Fit diagnostic: n_used=13, chi2_bar=7591, chi2_model=93.03, Δχ²=7498, p≈<1e-6, Z≈86.6, class=very-strong

- Implication: Outer residual RMS (z): 1.63
- Implication: Outer residual mean (z): 0.00207
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3109

- Figure: [toy_models/out_dyed_spacetime/png/NGC3109.png](toy_models/out_dyed_spacetime/png/NGC3109.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3109.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3109.csv)
- Summary: n=25, Q_flag=1, T=9, D=1.33 Mpc, Vflat=66.2 km/s, Rdisk=1.56 kpc, Rt=2.06 kpc, v_extra_asym=66.5 km/s, env_delta=0.417
- Fit diagnostic: n_used=25, chi2_bar=3718, chi2_model=112.4, Δχ²=3605, p≈<1e-6, Z≈60, class=very-strong

- Implication: Outer residual RMS (z): 1.07
- Implication: Outer residual mean (z): 1.02
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3198

- Figure: [toy_models/out_dyed_spacetime/png/NGC3198.png](toy_models/out_dyed_spacetime/png/NGC3198.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3198.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3198.csv)
- Summary: n=43, Q_flag=1, T=5, D=13.8 Mpc, Vflat=150 km/s, Rdisk=3.14 kpc, Rt=0.786 kpc, v_extra_asym=117 km/s, env_delta=2.88
- Fit diagnostic: n_used=43, chi2_bar=3.264e+04, chi2_model=1202, Δχ²=3.144e+04, p≈<1e-6, Z≈177, class=very-strong

- Implication: Outer residual RMS (z): 5.55
- Implication: Outer residual mean (z): -0.347
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3521

- Figure: [toy_models/out_dyed_spacetime/png/NGC3521.png](toy_models/out_dyed_spacetime/png/NGC3521.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3521.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3521.csv)
- Summary: n=41, Q_flag=1, T=4, D=7.7 Mpc, Vflat=214 km/s, Rdisk=2.4 kpc, Rt=7.29 kpc, v_extra_asym=168 km/s, env_delta=2.28
- Fit diagnostic: n_used=41, chi2_bar=617, chi2_model=117.1, Δχ²=499.9, p≈<1e-6, Z≈22.4, class=very-strong

- Implication: Outer residual RMS (z): 0.297
- Implication: Outer residual mean (z): -0.117
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3726

- Figure: [toy_models/out_dyed_spacetime/png/NGC3726.png](toy_models/out_dyed_spacetime/png/NGC3726.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3726.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3726.csv)
- Summary: n=12, Q_flag=2, T=5, D=18 Mpc, Vflat=168 km/s, Rdisk=3.4 kpc, Rt=3.5 kpc, v_extra_asym=104 km/s, env_delta=3.53
- Fit diagnostic: n_used=12, chi2_bar=577.2, chi2_model=51.35, Δχ²=525.8, p≈<1e-6, Z≈22.9, class=very-strong

- Implication: Outer residual RMS (z): 2.11
- Implication: Outer residual mean (z): -0.822
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3741

- Figure: [toy_models/out_dyed_spacetime/png/NGC3741.png](toy_models/out_dyed_spacetime/png/NGC3741.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3741.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3741.csv)
- Summary: n=21, Q_flag=1, T=10, D=3.21 Mpc, Vflat=50.1 km/s, Rdisk=0.2 kpc, Rt=0.23 kpc, v_extra_asym=48.2 km/s, env_delta=0.722
- Fit diagnostic: n_used=21, chi2_bar=2576, chi2_model=48.54, Δχ²=2528, p≈<1e-6, Z≈50.3, class=very-strong

- Implication: Outer residual RMS (z): 1.49
- Implication: Outer residual mean (z): -0.517
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3769

- Figure: [toy_models/out_dyed_spacetime/png/NGC3769.png](toy_models/out_dyed_spacetime/png/NGC3769.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3769.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3769.csv)
- Summary: n=12, Q_flag=2, T=3, D=18 Mpc, Vflat=119 km/s, Rdisk=3.38 kpc, Rt=2.38 kpc, v_extra_asym=97.1 km/s, env_delta=3.34
- Fit diagnostic: n_used=12, chi2_bar=645.8, chi2_model=8.071, Δχ²=637.7, p≈<1e-6, Z≈25.3, class=very-strong

- Implication: Outer residual RMS (z): 0.793
- Implication: Outer residual mean (z): -0.122
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3877

- Figure: [toy_models/out_dyed_spacetime/png/NGC3877.png](toy_models/out_dyed_spacetime/png/NGC3877.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3877.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3877.csv)
- Summary: n=13, Q_flag=2, T=5, D=18 Mpc, Vflat=168 km/s, Rdisk=2.53 kpc, Rt=1.8 kpc, v_extra_asym=102 km/s, env_delta=3.41
- Fit diagnostic: n_used=13, chi2_bar=413.6, chi2_model=49.56, Δχ²=364.1, p≈<1e-6, Z≈19.1, class=very-strong

- Implication: Outer residual RMS (z): 1.51
- Implication: Outer residual mean (z): 0.159
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3893

- Figure: [toy_models/out_dyed_spacetime/png/NGC3893.png](toy_models/out_dyed_spacetime/png/NGC3893.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3893.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3893.csv)
- Summary: n=10, Q_flag=1, T=5, D=18 Mpc, Vflat=174 km/s, Rdisk=2.38 kpc, Rt=5.85 kpc, v_extra_asym=150 km/s, env_delta=3.14
- Fit diagnostic: n_used=10, chi2_bar=497.4, chi2_model=27.37, Δχ²=470, p≈<1e-6, Z≈21.7, class=very-strong

- Implication: Outer residual RMS (z): 0.489
- Implication: Outer residual mean (z): 0.422
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3917

- Figure: [toy_models/out_dyed_spacetime/png/NGC3917.png](toy_models/out_dyed_spacetime/png/NGC3917.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3917.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3917.csv)
- Summary: n=17, Q_flag=1, T=6, D=18 Mpc, Vflat=136 km/s, Rdisk=2.63 kpc, Rt=5.24 kpc, v_extra_asym=119 km/s, env_delta=2.5
- Fit diagnostic: n_used=17, chi2_bar=2679, chi2_model=204.7, Δχ²=2474, p≈<1e-6, Z≈49.7, class=very-strong

- Implication: Outer residual RMS (z): 1.14
- Implication: Outer residual mean (z): 0.938
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3949

- Figure: [toy_models/out_dyed_spacetime/png/NGC3949.png](toy_models/out_dyed_spacetime/png/NGC3949.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3949.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3949.csv)
- Summary: n=7, Q_flag=2, T=4, D=18 Mpc, Vflat=163 km/s, Rdisk=3.59 kpc, Rt=4.85 kpc, v_extra_asym=129 km/s, env_delta=3.29
- Fit diagnostic: n_used=7, chi2_bar=47.78, chi2_model=6.998, Δχ²=40.78, p≈<1e-6, Z≈6.39, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3953

- Figure: [toy_models/out_dyed_spacetime/png/NGC3953.png](toy_models/out_dyed_spacetime/png/NGC3953.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3953.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3953.csv)
- Summary: n=8, Q_flag=1, T=4, D=18 Mpc, Vflat=221 km/s, Rdisk=4.89 kpc, Rt=7.25 kpc, v_extra_asym=156 km/s, env_delta=2.39
- Fit diagnostic: n_used=8, chi2_bar=491.3, chi2_model=100.5, Δχ²=390.8, p≈<1e-6, Z≈19.8, class=very-strong

- Implication: Outer residual RMS (z): 0.823
- Implication: Outer residual mean (z): 0.823
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3972

- Figure: [toy_models/out_dyed_spacetime/png/NGC3972.png](toy_models/out_dyed_spacetime/png/NGC3972.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3972.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3972.csv)
- Summary: n=10, Q_flag=1, T=4, D=18 Mpc, Vflat=133 km/s, Rdisk=2.18 kpc, Rt=0.87 kpc, v_extra_asym=103 km/s, env_delta=1.84
- Fit diagnostic: n_used=10, chi2_bar=856.5, chi2_model=16.14, Δχ²=840.4, p≈<1e-6, Z≈29, class=very-strong

- Implication: Outer residual RMS (z): 1.29
- Implication: Outer residual mean (z): -0.24
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC3992

- Figure: [toy_models/out_dyed_spacetime/png/NGC3992.png](toy_models/out_dyed_spacetime/png/NGC3992.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3992.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC3992.csv)
- Summary: n=9, Q_flag=1, T=4, D=23.7 Mpc, Vflat=241 km/s, Rdisk=4.96 kpc, Rt=9.19 kpc, v_extra_asym=208 km/s, env_delta=1.33
- Fit diagnostic: n_used=9, chi2_bar=2587, chi2_model=182, Δχ²=2405, p≈<1e-6, Z≈49, class=very-strong

- Implication: Outer residual RMS (z): 0.655
- Implication: Outer residual mean (z): 0.0599
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4010

- Figure: [toy_models/out_dyed_spacetime/png/NGC4010.png](toy_models/out_dyed_spacetime/png/NGC4010.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4010.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4010.csv)
- Summary: n=12, Q_flag=2, T=7, D=18 Mpc, Vflat=126 km/s, Rdisk=2.81 kpc, Rt=2.61 kpc, v_extra_asym=96.7 km/s, env_delta=3.39
- Fit diagnostic: n_used=12, chi2_bar=675.3, chi2_model=17.97, Δχ²=657.3, p≈<1e-6, Z≈25.6, class=very-strong

- Implication: Outer residual RMS (z): 0.874
- Implication: Outer residual mean (z): -0.224
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4013

- Figure: [toy_models/out_dyed_spacetime/png/NGC4013.png](toy_models/out_dyed_spacetime/png/NGC4013.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4013.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4013.csv)
- Summary: n=36, Q_flag=2, T=3, D=18 Mpc, Vflat=173 km/s, Rdisk=3.53 kpc, Rt=7.5 kpc, v_extra_asym=141 km/s, env_delta=4.18
- Fit diagnostic: n_used=36, chi2_bar=5515, chi2_model=179.2, Δχ²=5336, p≈<1e-6, Z≈73, class=very-strong

- Implication: Outer residual RMS (z): 2.07
- Implication: Outer residual mean (z): -0.232
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4051

- Figure: [toy_models/out_dyed_spacetime/png/NGC4051.png](toy_models/out_dyed_spacetime/png/NGC4051.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4051.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4051.csv)
- Summary: n=7, Q_flag=2, T=4, D=18 Mpc, Vflat=157 km/s, Rdisk=4.65 kpc, Rt=2.89 kpc, v_extra_asym=88.8 km/s, env_delta=4.01
- Fit diagnostic: n_used=7, chi2_bar=78.67, chi2_model=4.856, Δχ²=73.82, p≈<1e-6, Z≈8.59, class=very-strong

- Implication: Outer residual RMS (z): 0.776
- Implication: Outer residual mean (z): 0.314
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4068

- Figure: [toy_models/out_dyed_spacetime/png/NGC4068.png](toy_models/out_dyed_spacetime/png/NGC4068.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4068.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4068.csv)
- Summary: n=6, Q_flag=2, T=10, D=4.37 Mpc, Vflat=0 km/s, Rdisk=0.59 kpc, Rt=1.91 kpc, v_extra_asym=33.9 km/s, env_delta=0.834
- Fit diagnostic: n_used=6, chi2_bar=96.47, chi2_model=0.7843, Δχ²=95.68, p≈<1e-6, Z≈9.78, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4085

- Figure: [toy_models/out_dyed_spacetime/png/NGC4085.png](toy_models/out_dyed_spacetime/png/NGC4085.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4085.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4085.csv)
- Summary: n=7, Q_flag=2, T=5, D=18 Mpc, Vflat=132 km/s, Rdisk=1.65 kpc, Rt=2.83 kpc, v_extra_asym=85.9 km/s, env_delta=2.71
- Fit diagnostic: n_used=7, chi2_bar=99.27, chi2_model=20.24, Δχ²=79.03, p≈<1e-6, Z≈8.89, class=very-strong

- Implication: Outer residual RMS (z): 0.405
- Implication: Outer residual mean (z): -0.405
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4088

- Figure: [toy_models/out_dyed_spacetime/png/NGC4088.png](toy_models/out_dyed_spacetime/png/NGC4088.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4088.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4088.csv)
- Summary: n=12, Q_flag=1, T=4, D=18 Mpc, Vflat=172 km/s, Rdisk=2.58 kpc, Rt=8.58 kpc, v_extra_asym=93.7 km/s, env_delta=2.67
- Fit diagnostic: n_used=12, chi2_bar=148.5, chi2_model=27.87, Δχ²=120.6, p≈<1e-6, Z≈11, class=very-strong

- Implication: Outer residual RMS (z): 1.96
- Implication: Outer residual mean (z): -1.63
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4100

- Figure: [toy_models/out_dyed_spacetime/png/NGC4100.png](toy_models/out_dyed_spacetime/png/NGC4100.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4100.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4100.csv)
- Summary: n=24, Q_flag=1, T=4, D=18 Mpc, Vflat=158 km/s, Rdisk=2.15 kpc, Rt=6.11 kpc, v_extra_asym=148 km/s, env_delta=2.86
- Fit diagnostic: n_used=24, chi2_bar=3349, chi2_model=196.6, Δχ²=3153, p≈<1e-6, Z≈56.1, class=very-strong

- Implication: Outer residual RMS (z): 1.12
- Implication: Outer residual mean (z): 0.813
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4138

- Figure: [toy_models/out_dyed_spacetime/png/NGC4138.png](toy_models/out_dyed_spacetime/png/NGC4138.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4138.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4138.csv)
- Summary: n=7, Q_flag=2, T=0, D=18 Mpc, Vflat=147 km/s, Rdisk=1.51 kpc, Rt=5.47 kpc, v_extra_asym=137 km/s, env_delta=4.18
- Fit diagnostic: n_used=7, chi2_bar=153.4, chi2_model=28.04, Δχ²=125.4, p≈<1e-6, Z≈11.2, class=very-strong

- Implication: Outer residual RMS (z): 1.28
- Implication: Outer residual mean (z): 1.06
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4157

- Figure: [toy_models/out_dyed_spacetime/png/NGC4157.png](toy_models/out_dyed_spacetime/png/NGC4157.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4157.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4157.csv)
- Summary: n=17, Q_flag=1, T=3, D=18 Mpc, Vflat=185 km/s, Rdisk=2.32 kpc, Rt=8.85 kpc, v_extra_asym=132 km/s, env_delta=2.64
- Fit diagnostic: n_used=17, chi2_bar=677.4, chi2_model=32.48, Δχ²=644.9, p≈<1e-6, Z≈25.4, class=very-strong

- Implication: Outer residual RMS (z): 1.22
- Implication: Outer residual mean (z): -1.09
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4183

- Figure: [toy_models/out_dyed_spacetime/png/NGC4183.png](toy_models/out_dyed_spacetime/png/NGC4183.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4183.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4183.csv)
- Summary: n=23, Q_flag=1, T=6, D=18 Mpc, Vflat=111 km/s, Rdisk=2.79 kpc, Rt=0.87 kpc, v_extra_asym=92.4 km/s, env_delta=4.14
- Fit diagnostic: n_used=23, chi2_bar=1743, chi2_model=15.12, Δχ²=1728, p≈<1e-6, Z≈41.6, class=very-strong

- Implication: Outer residual RMS (z): 0.66
- Implication: Outer residual mean (z): -0.101
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4214

- Figure: [toy_models/out_dyed_spacetime/png/NGC4214.png](toy_models/out_dyed_spacetime/png/NGC4214.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4214.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4214.csv)
- Summary: n=14, Q_flag=2, T=10, D=2.87 Mpc, Vflat=80.1 km/s, Rdisk=0.51 kpc, Rt=0.21 kpc, v_extra_asym=87.8 km/s, env_delta=0.744
- Fit diagnostic: n_used=14, chi2_bar=657, chi2_model=58.31, Δχ²=598.7, p≈<1e-6, Z≈24.5, class=very-strong

- Implication: Outer residual RMS (z): 1.72
- Implication: Outer residual mean (z): -0.491
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4217

- Figure: [toy_models/out_dyed_spacetime/png/NGC4217.png](toy_models/out_dyed_spacetime/png/NGC4217.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4217.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4217.csv)
- Summary: n=19, Q_flag=1, T=3, D=18 Mpc, Vflat=181 km/s, Rdisk=2.94 kpc, Rt=8.42 kpc, v_extra_asym=117 km/s, env_delta=3.32
- Fit diagnostic: n_used=19, chi2_bar=818.7, chi2_model=531.7, Δχ²=287, p≈<1e-6, Z≈16.9, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC4389

- Figure: [toy_models/out_dyed_spacetime/png/NGC4389.png](toy_models/out_dyed_spacetime/png/NGC4389.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4389.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4389.csv)
- Summary: n=6, Q_flag=3, T=4, D=18 Mpc, Vflat=0 km/s, Rdisk=2.79 kpc, Rt=2.05 kpc, v_extra_asym=0.000656 km/s, env_delta=3.55
- Fit diagnostic: n_used=6, chi2_bar=83.84, chi2_model=83.84, Δχ²=-2.984e-09, p≈1, Z≈0, class=no-improvement

- Implication: Outer residual RMS (z): 1.78
- Implication: Outer residual mean (z): 0.578
- Implication: No improvement over baryons-only under this diagnostic (Δχ²≤0).

### NGC4559

- Figure: [toy_models/out_dyed_spacetime/png/NGC4559.png](toy_models/out_dyed_spacetime/png/NGC4559.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4559.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC4559.csv)
- Summary: n=32, Q_flag=1, T=6, D=9 Mpc, Vflat=121 km/s, Rdisk=2.1 kpc, Rt=0.67 kpc, v_extra_asym=91.6 km/s, env_delta=3.59
- Fit diagnostic: n_used=32, chi2_bar=2508, chi2_model=86.01, Δχ²=2422, p≈<1e-6, Z≈49.2, class=very-strong

- Implication: Outer residual RMS (z): 1.69
- Implication: Outer residual mean (z): 0.228
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC5005

- Figure: [toy_models/out_dyed_spacetime/png/NGC5005.png](toy_models/out_dyed_spacetime/png/NGC5005.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5005.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5005.csv)
- Summary: n=18, Q_flag=1, T=4, D=16.9 Mpc, Vflat=262 km/s, Rdisk=9.45 kpc, Rt=11.2 kpc, v_extra_asym=198 km/s, env_delta=4.82
- Fit diagnostic: n_used=18, chi2_bar=40.71, chi2_model=18.1, Δχ²=22.61, p≈1.99e-06, Z≈4.75, class=strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC5033

- Figure: [toy_models/out_dyed_spacetime/png/NGC5033.png](toy_models/out_dyed_spacetime/png/NGC5033.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5033.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5033.csv)
- Summary: n=22, Q_flag=1, T=5, D=15.7 Mpc, Vflat=194 km/s, Rdisk=5.16 kpc, Rt=7.84 kpc, v_extra_asym=175 km/s, env_delta=4.97
- Fit diagnostic: n_used=22, chi2_bar=2.089e+04, chi2_model=117.6, Δχ²=2.077e+04, p≈<1e-6, Z≈144, class=very-strong

- Implication: Outer residual RMS (z): 2.25
- Implication: Outer residual mean (z): -0.229
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC5055

- Figure: [toy_models/out_dyed_spacetime/png/NGC5055.png](toy_models/out_dyed_spacetime/png/NGC5055.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5055.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5055.csv)
- Summary: n=28, Q_flag=1, T=4, D=9.9 Mpc, Vflat=179 km/s, Rdisk=3.2 kpc, Rt=9.4 kpc, v_extra_asym=141 km/s, env_delta=2.82
- Fit diagnostic: n_used=28, chi2_bar=5.611e+04, chi2_model=1158, Δχ²=5.495e+04, p≈<1e-6, Z≈234, class=very-strong

- Implication: Outer residual RMS (z): 5.09
- Implication: Outer residual mean (z): -2.6
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC5371

- Figure: [toy_models/out_dyed_spacetime/png/NGC5371.png](toy_models/out_dyed_spacetime/png/NGC5371.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5371.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5371.csv)
- Summary: n=19, Q_flag=1, T=4, D=39.7 Mpc, Vflat=210 km/s, Rdisk=7.44 kpc, Rt=8.63 kpc, v_extra_asym=130 km/s, env_delta=1.51
- Fit diagnostic: n_used=19, chi2_bar=2555, chi2_model=471.4, Δχ²=2083, p≈<1e-6, Z≈45.6, class=very-strong

- Implication: Outer residual RMS (z): 2.42
- Implication: Outer residual mean (z): -0.0202
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC5585

- Figure: [toy_models/out_dyed_spacetime/png/NGC5585.png](toy_models/out_dyed_spacetime/png/NGC5585.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5585.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5585.csv)
- Summary: n=24, Q_flag=1, T=7, D=7.06 Mpc, Vflat=90.3 km/s, Rdisk=1.53 kpc, Rt=0.43 kpc, v_extra_asym=75.8 km/s, env_delta=0.926
- Fit diagnostic: n_used=24, chi2_bar=6956, chi2_model=235.2, Δχ²=6721, p≈<1e-6, Z≈82, class=very-strong

- Implication: Outer residual RMS (z): 2.77
- Implication: Outer residual mean (z): 0.698
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC5907

- Figure: [toy_models/out_dyed_spacetime/png/NGC5907.png](toy_models/out_dyed_spacetime/png/NGC5907.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5907.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5907.csv)
- Summary: n=19, Q_flag=1, T=5, D=17.3 Mpc, Vflat=215 km/s, Rdisk=5.34 kpc, Rt=5.03 kpc, v_extra_asym=174 km/s, env_delta=0.105
- Fit diagnostic: n_used=19, chi2_bar=2.026e+04, chi2_model=286.5, Δχ²=1.997e+04, p≈<1e-6, Z≈141, class=very-strong

- Implication: Outer residual RMS (z): 1.98
- Implication: Outer residual mean (z): -0.076
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC5985

- Figure: [toy_models/out_dyed_spacetime/png/NGC5985.png](toy_models/out_dyed_spacetime/png/NGC5985.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5985.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC5985.csv)
- Summary: n=33, Q_flag=1, T=3, D=39.7 Mpc, Vflat=294 km/s, Rdisk=7.01 kpc, Rt=4.11 kpc, v_extra_asym=250 km/s, env_delta=-0.706
- Fit diagnostic: n_used=33, chi2_bar=2.478e+04, chi2_model=481.4, Δχ²=2.43e+04, p≈<1e-6, Z≈156, class=very-strong

- Implication: Outer residual RMS (z): 1.31
- Implication: Outer residual mean (z): 0.371
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC6015

- Figure: [toy_models/out_dyed_spacetime/png/NGC6015.png](toy_models/out_dyed_spacetime/png/NGC6015.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6015.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6015.csv)
- Summary: n=44, Q_flag=2, T=6, D=17 Mpc, Vflat=154 km/s, Rdisk=2.3 kpc, Rt=1 kpc, v_extra_asym=130 km/s, env_delta=-0.34
- Fit diagnostic: n_used=44, chi2_bar=1.991e+04, chi2_model=817.9, Δχ²=1.91e+04, p≈<1e-6, Z≈138, class=very-strong

- Implication: Outer residual RMS (z): 3.47
- Implication: Outer residual mean (z): -0.122
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC6195

- Figure: [toy_models/out_dyed_spacetime/png/NGC6195.png](toy_models/out_dyed_spacetime/png/NGC6195.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6195.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6195.csv)
- Summary: n=23, Q_flag=1, T=3, D=128 Mpc, Vflat=252 km/s, Rdisk=13.9 kpc, Rt=13.4 kpc, v_extra_asym=154 km/s, env_delta=0.336
- Fit diagnostic: n_used=23, chi2_bar=684.9, chi2_model=98.11, Δχ²=586.8, p≈<1e-6, Z≈24.2, class=very-strong

- Implication: Outer residual RMS (z): 2.12
- Implication: Outer residual mean (z): -1.88
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC6503

- Figure: [toy_models/out_dyed_spacetime/png/NGC6503.png](toy_models/out_dyed_spacetime/png/NGC6503.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6503.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6503.csv)
- Summary: n=31, Q_flag=1, T=6, D=6.26 Mpc, Vflat=116 km/s, Rdisk=2.16 kpc, Rt=2.63 kpc, v_extra_asym=102 km/s, env_delta=0.0675
- Fit diagnostic: n_used=31, chi2_bar=5.158e+04, chi2_model=138.9, Δχ²=5.144e+04, p≈<1e-6, Z≈227, class=very-strong

- Implication: Outer residual RMS (z): 1.85
- Implication: Outer residual mean (z): 0.0272
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC6674

- Figure: [toy_models/out_dyed_spacetime/png/NGC6674.png](toy_models/out_dyed_spacetime/png/NGC6674.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6674.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6674.csv)
- Summary: n=15, Q_flag=1, T=3, D=51.2 Mpc, Vflat=241 km/s, Rdisk=6.04 kpc, Rt=8.34 kpc, v_extra_asym=212 km/s, env_delta=-0.317
- Fit diagnostic: n_used=15, chi2_bar=3.388e+04, chi2_model=151.4, Δχ²=3.373e+04, p≈<1e-6, Z≈184, class=very-strong

- Implication: Outer residual RMS (z): 2.58
- Implication: Outer residual mean (z): -0.12
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC6789

- Figure: [toy_models/out_dyed_spacetime/png/NGC6789.png](toy_models/out_dyed_spacetime/png/NGC6789.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6789.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6789.csv)
- Summary: n=4, Q_flag=2, T=11, D=3.52 Mpc, Vflat=0 km/s, Rdisk=0.31 kpc, Rt=0.3 kpc, v_extra_asym=60.4 km/s, env_delta=0.151
- Fit diagnostic: n_used=4, chi2_bar=87.22, chi2_model=4.413, Δχ²=82.81, p≈<1e-6, Z≈9.1, class=very-strong

- Implication: Outer residual RMS (z): 0.317
- Implication: Outer residual mean (z): 0.317
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC6946

- Figure: [toy_models/out_dyed_spacetime/png/NGC6946.png](toy_models/out_dyed_spacetime/png/NGC6946.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6946.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC6946.csv)
- Summary: n=58, Q_flag=1, T=6, D=5.52 Mpc, Vflat=159 km/s, Rdisk=2.44 kpc, Rt=6.2 kpc, v_extra_asym=120 km/s, env_delta=-0.113
- Fit diagnostic: n_used=58, chi2_bar=9335, chi2_model=613.1, Δχ²=8722, p≈<1e-6, Z≈93.4, class=very-strong

- Implication: Outer residual RMS (z): 0.267
- Implication: Outer residual mean (z): -0.115
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC7331

- Figure: [toy_models/out_dyed_spacetime/png/NGC7331.png](toy_models/out_dyed_spacetime/png/NGC7331.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC7331.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC7331.csv)
- Summary: n=36, Q_flag=1, T=3, D=14.7 Mpc, Vflat=239 km/s, Rdisk=5.02 kpc, Rt=12.1 kpc, v_extra_asym=165 km/s, env_delta=-0.662
- Fit diagnostic: n_used=36, chi2_bar=8701, chi2_model=389.3, Δχ²=8312, p≈<1e-6, Z≈91.2, class=very-strong

- Implication: Outer residual RMS (z): 3.36
- Implication: Outer residual mean (z): -3.12
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC7793

- Figure: [toy_models/out_dyed_spacetime/png/NGC7793.png](toy_models/out_dyed_spacetime/png/NGC7793.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC7793.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC7793.csv)
- Summary: n=46, Q_flag=1, T=7, D=3.61 Mpc, Vflat=0 km/s, Rdisk=1.21 kpc, Rt=0.11 kpc, v_extra_asym=87.3 km/s, env_delta=0.0998
- Fit diagnostic: n_used=46, chi2_bar=682.2, chi2_model=64.77, Δχ²=617.5, p≈<1e-6, Z≈24.8, class=very-strong

- Implication: Outer residual RMS (z): 1.22
- Implication: Outer residual mean (z): -0.635
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### NGC7814

- Figure: [toy_models/out_dyed_spacetime/png/NGC7814.png](toy_models/out_dyed_spacetime/png/NGC7814.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/NGC7814.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/NGC7814.csv)
- Summary: n=18, Q_flag=1, T=2, D=14.4 Mpc, Vflat=219 km/s, Rdisk=2.54 kpc, Rt=7.35 kpc, v_extra_asym=179 km/s, env_delta=-0.605
- Fit diagnostic: n_used=18, chi2_bar=7283, chi2_model=168.9, Δχ²=7114, p≈<1e-6, Z≈84.3, class=very-strong

- Implication: Outer residual RMS (z): 0.777
- Implication: Outer residual mean (z): -0.515
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### PGC51017

- Figure: [toy_models/out_dyed_spacetime/png/PGC51017.png](toy_models/out_dyed_spacetime/png/PGC51017.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/PGC51017.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/PGC51017.csv)
- Summary: n=6, Q_flag=3, T=11, D=13.6 Mpc, Vflat=18.6 km/s, Rdisk=0.53 kpc, Rt=0.99 kpc, v_extra_asym=6.21 km/s, env_delta=2.49
- Fit diagnostic: n_used=6, chi2_bar=9.336, chi2_model=8.779, Δχ²=0.5576, p≈0.455, Z≈0.747, class=weak

- Implication: Outer residual RMS (z): 0.107
- Implication: Outer residual mean (z): 0.0475
- Implication: Extra-term improvement is weak under this diagnostic; baryons-only may already be adequate within errors or the effect is not well captured by a 1/R tail.

### UGC00128

- Figure: [toy_models/out_dyed_spacetime/png/UGC00128.png](toy_models/out_dyed_spacetime/png/UGC00128.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00128.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00128.csv)
- Summary: n=22, Q_flag=1, T=8, D=64.5 Mpc, Vflat=129 km/s, Rdisk=5.95 kpc, Rt=1.25 kpc, v_extra_asym=115 km/s, env_delta=-0.526
- Fit diagnostic: n_used=22, chi2_bar=1.349e+05, chi2_model=565.8, Δχ²=1.343e+05, p≈<1e-6, Z≈366, class=very-strong

- Implication: Outer residual RMS (z): 5.19
- Implication: Outer residual mean (z): 0.272
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC00191

- Figure: [toy_models/out_dyed_spacetime/png/UGC00191.png](toy_models/out_dyed_spacetime/png/UGC00191.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00191.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00191.csv)
- Summary: n=9, Q_flag=1, T=9, D=17.1 Mpc, Vflat=0 km/s, Rdisk=1.58 kpc, Rt=0.87 kpc, v_extra_asym=71.6 km/s, env_delta=-0.479
- Fit diagnostic: n_used=9, chi2_bar=7398, chi2_model=312.3, Δχ²=7086, p≈<1e-6, Z≈84.2, class=very-strong

- Implication: Outer residual RMS (z): 2.11
- Implication: Outer residual mean (z): -0.279
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC00634

- Figure: [toy_models/out_dyed_spacetime/png/UGC00634.png](toy_models/out_dyed_spacetime/png/UGC00634.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00634.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00634.csv)
- Summary: n=4, Q_flag=2, T=9, D=30.9 Mpc, Vflat=0 km/s, Rdisk=2.45 kpc, Rt=4.51 kpc, v_extra_asym=97 km/s, env_delta=0.161
- Fit diagnostic: n_used=4, chi2_bar=5903, chi2_model=70.05, Δχ²=5833, p≈<1e-6, Z≈76.4, class=very-strong

- Implication: Outer residual RMS (z): 0.831
- Implication: Outer residual mean (z): -0.829
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC00731

- Figure: [toy_models/out_dyed_spacetime/png/UGC00731.png](toy_models/out_dyed_spacetime/png/UGC00731.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00731.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00731.csv)
- Summary: n=12, Q_flag=1, T=10, D=12.5 Mpc, Vflat=73.3 km/s, Rdisk=2.3 kpc, Rt=8.19 kpc, v_extra_asym=90 km/s, env_delta=-0.78
- Fit diagnostic: n_used=12, chi2_bar=2334, chi2_model=1211, Δχ²=1123, p≈<1e-6, Z≈33.5, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC00891

- Figure: [toy_models/out_dyed_spacetime/png/UGC00891.png](toy_models/out_dyed_spacetime/png/UGC00891.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00891.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC00891.csv)
- Summary: n=5, Q_flag=2, T=9, D=10.2 Mpc, Vflat=0 km/s, Rdisk=1.43 kpc, Rt=1.48 kpc, v_extra_asym=56.4 km/s, env_delta=-0.442
- Fit diagnostic: n_used=5, chi2_bar=8923, chi2_model=20.29, Δχ²=8903, p≈<1e-6, Z≈94.4, class=very-strong

- Implication: Outer residual RMS (z): 1.78
- Implication: Outer residual mean (z): -0.405
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC01230

- Figure: [toy_models/out_dyed_spacetime/png/UGC01230.png](toy_models/out_dyed_spacetime/png/UGC01230.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC01230.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC01230.csv)
- Summary: n=11, Q_flag=1, T=9, D=53.7 Mpc, Vflat=104 km/s, Rdisk=4.34 kpc, Rt=2.35 kpc, v_extra_asym=96.9 km/s, env_delta=-0.819
- Fit diagnostic: n_used=11, chi2_bar=251.2, chi2_model=2.831, Δχ²=248.3, p≈<1e-6, Z≈15.8, class=very-strong

- Implication: Outer residual RMS (z): 0.458
- Implication: Outer residual mean (z): 0.0734
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC01281

- Figure: [toy_models/out_dyed_spacetime/png/UGC01281.png](toy_models/out_dyed_spacetime/png/UGC01281.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC01281.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC01281.csv)
- Summary: n=25, Q_flag=1, T=8, D=5.27 Mpc, Vflat=55.2 km/s, Rdisk=1.63 kpc, Rt=0.08 kpc, v_extra_asym=53.6 km/s, env_delta=-0.249
- Fit diagnostic: n_used=25, chi2_bar=599.3, chi2_model=3.335, Δχ²=595.9, p≈<1e-6, Z≈24.4, class=very-strong

- Implication: Outer residual RMS (z): 0.292
- Implication: Outer residual mean (z): 0.0396
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC02023

- Figure: [toy_models/out_dyed_spacetime/png/UGC02023.png](toy_models/out_dyed_spacetime/png/UGC02023.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02023.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02023.csv)
- Summary: n=5, Q_flag=2, T=10, D=10.4 Mpc, Vflat=0 km/s, Rdisk=1.55 kpc, Rt=1.51 kpc, v_extra_asym=45.7 km/s, env_delta=-0.607
- Fit diagnostic: n_used=5, chi2_bar=14.95, chi2_model=0.3678, Δχ²=14.58, p≈1.34e-04, Z≈3.82, class=strong

- Implication: Outer residual RMS (z): 0.241
- Implication: Outer residual mean (z): -0.115
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC02259

- Figure: [toy_models/out_dyed_spacetime/png/UGC02259.png](toy_models/out_dyed_spacetime/png/UGC02259.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02259.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02259.csv)
- Summary: n=8, Q_flag=2, T=8, D=10.5 Mpc, Vflat=86.2 km/s, Rdisk=1.62 kpc, Rt=2.04 kpc, v_extra_asym=89.1 km/s, env_delta=-0.619
- Fit diagnostic: n_used=8, chi2_bar=5364, chi2_model=407.6, Δχ²=4956, p≈<1e-6, Z≈70.4, class=very-strong

- Implication: Outer residual RMS (z): 3.41
- Implication: Outer residual mean (z): 3.23
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC02455

- Figure: [toy_models/out_dyed_spacetime/png/UGC02455.png](toy_models/out_dyed_spacetime/png/UGC02455.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02455.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02455.csv)
- Summary: n=8, Q_flag=3, T=10, D=6.92 Mpc, Vflat=0 km/s, Rdisk=0.99 kpc, Rt=1 kpc, v_extra_asym=0.000588 km/s, env_delta=-0.319
- Fit diagnostic: n_used=8, chi2_bar=188.1, chi2_model=188.1, Δχ²=-1.387e-08, p≈1, Z≈0, class=no-improvement

- Implication: Outer residual RMS (z): 4.01
- Implication: Outer residual mean (z): 2.8
- Implication: No improvement over baryons-only under this diagnostic (Δχ²≤0).

### UGC02487

- Figure: [toy_models/out_dyed_spacetime/png/UGC02487.png](toy_models/out_dyed_spacetime/png/UGC02487.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02487.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02487.csv)
- Summary: n=17, Q_flag=1, T=0, D=69.1 Mpc, Vflat=332 km/s, Rdisk=7.89 kpc, Rt=15.5 kpc, v_extra_asym=301 km/s, env_delta=0.101
- Fit diagnostic: n_used=17, chi2_bar=4.842e+04, chi2_model=488, Δχ²=4.793e+04, p≈<1e-6, Z≈219, class=very-strong

- Implication: Outer residual RMS (z): 3.45
- Implication: Outer residual mean (z): -0.102
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC02885

- Figure: [toy_models/out_dyed_spacetime/png/UGC02885.png](toy_models/out_dyed_spacetime/png/UGC02885.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02885.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02885.csv)
- Summary: n=19, Q_flag=1, T=5, D=80.6 Mpc, Vflat=290 km/s, Rdisk=11.4 kpc, Rt=11.4 kpc, v_extra_asym=238 km/s, env_delta=1.47
- Fit diagnostic: n_used=19, chi2_bar=2505, chi2_model=112.7, Δχ²=2392, p≈<1e-6, Z≈48.9, class=very-strong

- Implication: Outer residual RMS (z): 1.43
- Implication: Outer residual mean (z): -0.109
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC02916

- Figure: [toy_models/out_dyed_spacetime/png/UGC02916.png](toy_models/out_dyed_spacetime/png/UGC02916.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02916.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02916.csv)
- Summary: n=43, Q_flag=2, T=2, D=65.4 Mpc, Vflat=183 km/s, Rdisk=6.15 kpc, Rt=8.57 kpc, v_extra_asym=171 km/s, env_delta=-0.819
- Fit diagnostic: n_used=43, chi2_bar=4878, chi2_model=1437, Δχ²=3441, p≈<1e-6, Z≈58.7, class=very-strong

- Implication: Outer residual RMS (z): 1.97
- Implication: Outer residual mean (z): 1.79
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC02953

- Figure: [toy_models/out_dyed_spacetime/png/UGC02953.png](toy_models/out_dyed_spacetime/png/UGC02953.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02953.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC02953.csv)
- Summary: n=115, Q_flag=2, T=2, D=16.5 Mpc, Vflat=265 km/s, Rdisk=3.55 kpc, Rt=13.6 kpc, v_extra_asym=232 km/s, env_delta=-0.777
- Fit diagnostic: n_used=115, chi2_bar=2.792e+05, chi2_model=3.155e+04, Δχ²=2.476e+05, p≈<1e-6, Z≈498, class=very-strong

- Implication: Outer residual RMS (z): 1.65
- Implication: Outer residual mean (z): 0.248
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC03205

- Figure: [toy_models/out_dyed_spacetime/png/UGC03205.png](toy_models/out_dyed_spacetime/png/UGC03205.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC03205.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC03205.csv)
- Summary: n=48, Q_flag=1, T=2, D=50 Mpc, Vflat=220 km/s, Rdisk=3.19 kpc, Rt=8.08 kpc, v_extra_asym=175 km/s, env_delta=-0.39
- Fit diagnostic: n_used=48, chi2_bar=2.637e+04, chi2_model=1557, Δχ²=2.481e+04, p≈<1e-6, Z≈158, class=very-strong

- Implication: Outer residual RMS (z): 1.78
- Implication: Outer residual mean (z): -0.585
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC03546

- Figure: [toy_models/out_dyed_spacetime/png/UGC03546.png](toy_models/out_dyed_spacetime/png/UGC03546.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC03546.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC03546.csv)
- Summary: n=30, Q_flag=1, T=1, D=28.7 Mpc, Vflat=197 km/s, Rdisk=3.79 kpc, Rt=7.57 kpc, v_extra_asym=145 km/s, env_delta=-0.399
- Fit diagnostic: n_used=30, chi2_bar=3.047e+04, chi2_model=95.47, Δχ²=3.038e+04, p≈<1e-6, Z≈174, class=very-strong

- Implication: Outer residual RMS (z): 1.87
- Implication: Outer residual mean (z): -1.69
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC03580

- Figure: [toy_models/out_dyed_spacetime/png/UGC03580.png](toy_models/out_dyed_spacetime/png/UGC03580.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC03580.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC03580.csv)
- Summary: n=47, Q_flag=2, T=1, D=20.7 Mpc, Vflat=126 km/s, Rdisk=2.43 kpc, Rt=2.24 kpc, v_extra_asym=94.1 km/s, env_delta=-0.491
- Fit diagnostic: n_used=47, chi2_bar=2.041e+04, chi2_model=2051, Δχ²=1.836e+04, p≈<1e-6, Z≈136, class=very-strong

- Implication: Outer residual RMS (z): 6.67
- Implication: Outer residual mean (z): -1.06
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC04278

- Figure: [toy_models/out_dyed_spacetime/png/UGC04278.png](toy_models/out_dyed_spacetime/png/UGC04278.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04278.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04278.csv)
- Summary: n=25, Q_flag=1, T=7, D=9.51 Mpc, Vflat=91.4 km/s, Rdisk=2.21 kpc, Rt=1.25 kpc, v_extra_asym=72.6 km/s, env_delta=0.6
- Fit diagnostic: n_used=25, chi2_bar=1316, chi2_model=31.64, Δχ²=1284, p≈<1e-6, Z≈35.8, class=very-strong

- Implication: Outer residual RMS (z): 1.19
- Implication: Outer residual mean (z): 0.104
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC04305

- Figure: [toy_models/out_dyed_spacetime/png/UGC04305.png](toy_models/out_dyed_spacetime/png/UGC04305.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04305.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04305.csv)
- Summary: n=22, Q_flag=3, T=10, D=3.45 Mpc, Vflat=34.5 km/s, Rdisk=1.16 kpc, Rt=1.26 kpc, v_extra_asym=14.5 km/s, env_delta=0.292
- Fit diagnostic: n_used=22, chi2_bar=63.07, chi2_model=55.27, Δχ²=7.793, p≈0.00524, Z≈2.79, class=moderate

- Implication: Outer residual RMS (z): 0.785
- Implication: Outer residual mean (z): 0.453
- Implication: Extra-term improves fit at a suggestive level; worth checking for systematics (inclination, distance, inner radii handling).

### UGC04325

- Figure: [toy_models/out_dyed_spacetime/png/UGC04325.png](toy_models/out_dyed_spacetime/png/UGC04325.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04325.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04325.csv)
- Summary: n=8, Q_flag=1, T=9, D=9.6 Mpc, Vflat=90.9 km/s, Rdisk=1.86 kpc, Rt=2.79 kpc, v_extra_asym=102 km/s, env_delta=0.548
- Fit diagnostic: n_used=8, chi2_bar=1830, chi2_model=454.5, Δχ²=1375, p≈<1e-6, Z≈37.1, class=very-strong

- Implication: Outer residual RMS (z): 6.38
- Implication: Outer residual mean (z): 6.38
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC04483

- Figure: [toy_models/out_dyed_spacetime/png/UGC04483.png](toy_models/out_dyed_spacetime/png/UGC04483.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04483.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04483.csv)
- Summary: n=8, Q_flag=2, T=10, D=3.34 Mpc, Vflat=0 km/s, Rdisk=0.18 kpc, Rt=0.4 kpc, v_extra_asym=23.9 km/s, env_delta=0.315
- Fit diagnostic: n_used=8, chi2_bar=240, chi2_model=31.1, Δχ²=208.9, p≈<1e-6, Z≈14.5, class=very-strong

- Implication: Outer residual RMS (z): 1.53
- Implication: Outer residual mean (z): 0.716
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC04499

- Figure: [toy_models/out_dyed_spacetime/png/UGC04499.png](toy_models/out_dyed_spacetime/png/UGC04499.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04499.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC04499.csv)
- Summary: n=9, Q_flag=1, T=8, D=12.5 Mpc, Vflat=72.8 km/s, Rdisk=1.73 kpc, Rt=0.91 kpc, v_extra_asym=63.2 km/s, env_delta=0.654
- Fit diagnostic: n_used=9, chi2_bar=973, chi2_model=11.57, Δχ²=961.4, p≈<1e-6, Z≈31, class=very-strong

- Implication: Outer residual RMS (z): 1.14
- Implication: Outer residual mean (z): -0.284
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05005

- Figure: [toy_models/out_dyed_spacetime/png/UGC05005.png](toy_models/out_dyed_spacetime/png/UGC05005.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05005.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05005.csv)
- Summary: n=11, Q_flag=1, T=10, D=53.7 Mpc, Vflat=98.9 km/s, Rdisk=3.2 kpc, Rt=3.91 kpc, v_extra_asym=75.8 km/s, env_delta=0.982
- Fit diagnostic: n_used=11, chi2_bar=166, chi2_model=11.97, Δχ²=154, p≈<1e-6, Z≈12.4, class=very-strong

- Implication: Outer residual RMS (z): 1.04
- Implication: Outer residual mean (z): -0.611
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05253

- Figure: [toy_models/out_dyed_spacetime/png/UGC05253.png](toy_models/out_dyed_spacetime/png/UGC05253.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05253.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05253.csv)
- Summary: n=73, Q_flag=2, T=2, D=22.9 Mpc, Vflat=214 km/s, Rdisk=8.07 kpc, Rt=10 kpc, v_extra_asym=189 km/s, env_delta=0.149
- Fit diagnostic: n_used=73, chi2_bar=2.62e+04, chi2_model=1698, Δχ²=2.45e+04, p≈<1e-6, Z≈157, class=very-strong

- Implication: Outer residual RMS (z): 1.47
- Implication: Outer residual mean (z): 0.0252
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05414

- Figure: [toy_models/out_dyed_spacetime/png/UGC05414.png](toy_models/out_dyed_spacetime/png/UGC05414.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05414.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05414.csv)
- Summary: n=6, Q_flag=1, T=10, D=9.4 Mpc, Vflat=0 km/s, Rdisk=1.47 kpc, Rt=1.37 kpc, v_extra_asym=54.5 km/s, env_delta=2.11
- Fit diagnostic: n_used=6, chi2_bar=380.4, chi2_model=16.65, Δχ²=363.7, p≈<1e-6, Z≈19.1, class=very-strong

- Implication: Outer residual RMS (z): 0.747
- Implication: Outer residual mean (z): 0.441
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05716

- Figure: [toy_models/out_dyed_spacetime/png/UGC05716.png](toy_models/out_dyed_spacetime/png/UGC05716.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05716.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05716.csv)
- Summary: n=12, Q_flag=2, T=9, D=21.3 Mpc, Vflat=73.1 km/s, Rdisk=1.14 kpc, Rt=1.03 kpc, v_extra_asym=64.4 km/s, env_delta=4.89
- Fit diagnostic: n_used=12, chi2_bar=3.065e+04, chi2_model=179.4, Δχ²=3.047e+04, p≈<1e-6, Z≈175, class=very-strong

- Implication: Outer residual RMS (z): 3.65
- Implication: Outer residual mean (z): -1.3
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05721

- Figure: [toy_models/out_dyed_spacetime/png/UGC05721.png](toy_models/out_dyed_spacetime/png/UGC05721.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05721.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05721.csv)
- Summary: n=23, Q_flag=1, T=7, D=6.18 Mpc, Vflat=79.7 km/s, Rdisk=0.38 kpc, Rt=0.27 kpc, v_extra_asym=87 km/s, env_delta=1.69
- Fit diagnostic: n_used=23, chi2_bar=1960, chi2_model=250.2, Δχ²=1710, p≈<1e-6, Z≈41.4, class=very-strong

- Implication: Outer residual RMS (z): 3.41
- Implication: Outer residual mean (z): -1.35
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05750

- Figure: [toy_models/out_dyed_spacetime/png/UGC05750.png](toy_models/out_dyed_spacetime/png/UGC05750.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05750.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05750.csv)
- Summary: n=11, Q_flag=1, T=8, D=58.7 Mpc, Vflat=0 km/s, Rdisk=3.46 kpc, Rt=9.43 kpc, v_extra_asym=99.1 km/s, env_delta=1.59
- Fit diagnostic: n_used=11, chi2_bar=157.4, chi2_model=107.3, Δχ²=50.02, p≈<1e-6, Z≈7.07, class=very-strong

- Implication: Outer residual RMS (z): 2.6
- Implication: Outer residual mean (z): 2.6
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05764

- Figure: [toy_models/out_dyed_spacetime/png/UGC05764.png](toy_models/out_dyed_spacetime/png/UGC05764.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05764.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05764.csv)
- Summary: n=10, Q_flag=2, T=10, D=7.47 Mpc, Vflat=0 km/s, Rdisk=1.17 kpc, Rt=2.17 kpc, v_extra_asym=78.9 km/s, env_delta=2.13
- Fit diagnostic: n_used=10, chi2_bar=2.202e+04, chi2_model=2692, Δχ²=1.933e+04, p≈<1e-6, Z≈139, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05829

- Figure: [toy_models/out_dyed_spacetime/png/UGC05829.png](toy_models/out_dyed_spacetime/png/UGC05829.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05829.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05829.csv)
- Summary: n=11, Q_flag=2, T=10, D=8.64 Mpc, Vflat=0 km/s, Rdisk=1.99 kpc, Rt=6.29 kpc, v_extra_asym=71.3 km/s, env_delta=2.63
- Fit diagnostic: n_used=11, chi2_bar=259.3, chi2_model=88.97, Δχ²=170.3, p≈<1e-6, Z≈13.1, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05918

- Figure: [toy_models/out_dyed_spacetime/png/UGC05918.png](toy_models/out_dyed_spacetime/png/UGC05918.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05918.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05918.csv)
- Summary: n=8, Q_flag=2, T=10, D=7.66 Mpc, Vflat=0 km/s, Rdisk=1.66 kpc, Rt=2.79 kpc, v_extra_asym=49.4 km/s, env_delta=0.678
- Fit diagnostic: n_used=8, chi2_bar=246.4, chi2_model=48.27, Δχ²=198.1, p≈<1e-6, Z≈14.1, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05986

- Figure: [toy_models/out_dyed_spacetime/png/UGC05986.png](toy_models/out_dyed_spacetime/png/UGC05986.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05986.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05986.csv)
- Summary: n=15, Q_flag=2, T=9, D=8.63 Mpc, Vflat=113 km/s, Rdisk=1.67 kpc, Rt=2.51 kpc, v_extra_asym=113 km/s, env_delta=2.6
- Fit diagnostic: n_used=15, chi2_bar=5300, chi2_model=176.6, Δχ²=5124, p≈<1e-6, Z≈71.6, class=very-strong

- Implication: Outer residual RMS (z): 1.95
- Implication: Outer residual mean (z): 1.65
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC05999

- Figure: [toy_models/out_dyed_spacetime/png/UGC05999.png](toy_models/out_dyed_spacetime/png/UGC05999.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05999.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC05999.csv)
- Summary: n=5, Q_flag=2, T=10, D=47.7 Mpc, Vflat=0 km/s, Rdisk=3.22 kpc, Rt=3.48 kpc, v_extra_asym=84.2 km/s, env_delta=-0.333
- Fit diagnostic: n_used=5, chi2_bar=392.4, chi2_model=10.63, Δχ²=381.8, p≈<1e-6, Z≈19.5, class=very-strong

- Implication: Outer residual RMS (z): 0.47
- Implication: Outer residual mean (z): -0.053
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06399

- Figure: [toy_models/out_dyed_spacetime/png/UGC06399.png](toy_models/out_dyed_spacetime/png/UGC06399.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06399.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06399.csv)
- Summary: n=9, Q_flag=1, T=9, D=18 Mpc, Vflat=85 km/s, Rdisk=2.05 kpc, Rt=1.74 kpc, v_extra_asym=80.2 km/s, env_delta=2.7
- Fit diagnostic: n_used=9, chi2_bar=645.8, chi2_model=8.624, Δχ²=637.2, p≈<1e-6, Z≈25.2, class=very-strong

- Implication: Outer residual RMS (z): 0.451
- Implication: Outer residual mean (z): 0.17
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06446

- Figure: [toy_models/out_dyed_spacetime/png/UGC06446.png](toy_models/out_dyed_spacetime/png/UGC06446.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06446.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06446.csv)
- Summary: n=17, Q_flag=1, T=7, D=12 Mpc, Vflat=82.2 km/s, Rdisk=1.49 kpc, Rt=0.58 kpc, v_extra_asym=77.4 km/s, env_delta=2.16
- Fit diagnostic: n_used=17, chi2_bar=1654, chi2_model=51.28, Δχ²=1603, p≈<1e-6, Z≈40, class=very-strong

- Implication: Outer residual RMS (z): 1.67
- Implication: Outer residual mean (z): -0.395
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06614

- Figure: [toy_models/out_dyed_spacetime/png/UGC06614.png](toy_models/out_dyed_spacetime/png/UGC06614.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06614.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06614.csv)
- Summary: n=13, Q_flag=1, T=1, D=88.7 Mpc, Vflat=200 km/s, Rdisk=5.1 kpc, Rt=7.61 kpc, v_extra_asym=125 km/s, env_delta=0.052
- Fit diagnostic: n_used=13, chi2_bar=348, chi2_model=87.2, Δχ²=260.8, p≈<1e-6, Z≈16.1, class=very-strong

- Implication: Outer residual RMS (z): 2.68
- Implication: Outer residual mean (z): -1.99
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06628

- Figure: [toy_models/out_dyed_spacetime/png/UGC06628.png](toy_models/out_dyed_spacetime/png/UGC06628.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06628.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06628.csv)
- Summary: n=7, Q_flag=2, T=9, D=15.1 Mpc, Vflat=41.8 km/s, Rdisk=2.82 kpc, Rt=1.1 kpc, v_extra_asym=18.5 km/s, env_delta=3.94
- Fit diagnostic: n_used=7, chi2_bar=4.472, chi2_model=3.491, Δχ²=0.9814, p≈0.322, Z≈0.991, class=weak

- Implication: Outer residual RMS (z): 0.7
- Implication: Outer residual mean (z): -0.143
- Implication: Extra-term improvement is weak under this diagnostic; baryons-only may already be adequate within errors or the effect is not well captured by a 1/R tail.

### UGC06667

- Figure: [toy_models/out_dyed_spacetime/png/UGC06667.png](toy_models/out_dyed_spacetime/png/UGC06667.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06667.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06667.csv)
- Summary: n=9, Q_flag=1, T=6, D=18 Mpc, Vflat=83.8 km/s, Rdisk=5.15 kpc, Rt=5.24 kpc, v_extra_asym=101 km/s, env_delta=2.56
- Fit diagnostic: n_used=9, chi2_bar=2018, chi2_model=451.3, Δχ²=1567, p≈<1e-6, Z≈39.6, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06786

- Figure: [toy_models/out_dyed_spacetime/png/UGC06786.png](toy_models/out_dyed_spacetime/png/UGC06786.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06786.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06786.csv)
- Summary: n=45, Q_flag=1, T=0, D=29.3 Mpc, Vflat=219 km/s, Rdisk=3.6 kpc, Rt=6.52 kpc, v_extra_asym=202 km/s, env_delta=2.02
- Fit diagnostic: n_used=45, chi2_bar=5.878e+04, chi2_model=2597, Δχ²=5.619e+04, p≈<1e-6, Z≈237, class=very-strong

- Implication: Outer residual RMS (z): 1.95
- Implication: Outer residual mean (z): 0.721
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06787

- Figure: [toy_models/out_dyed_spacetime/png/UGC06787.png](toy_models/out_dyed_spacetime/png/UGC06787.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06787.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06787.csv)
- Summary: n=71, Q_flag=2, T=2, D=21.3 Mpc, Vflat=248 km/s, Rdisk=5.37 kpc, Rt=7.88 kpc, v_extra_asym=213 km/s, env_delta=1.42
- Fit diagnostic: n_used=71, chi2_bar=1.042e+05, chi2_model=6664, Δχ²=9.751e+04, p≈<1e-6, Z≈312, class=very-strong

- Implication: Outer residual RMS (z): 8.02
- Implication: Outer residual mean (z): 0.311
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06818

- Figure: [toy_models/out_dyed_spacetime/png/UGC06818.png](toy_models/out_dyed_spacetime/png/UGC06818.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06818.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06818.csv)
- Summary: n=8, Q_flag=2, T=9, D=18 Mpc, Vflat=71.2 km/s, Rdisk=1.39 kpc, Rt=0.87 kpc, v_extra_asym=56.3 km/s, env_delta=3.76
- Fit diagnostic: n_used=8, chi2_bar=201.1, chi2_model=17.6, Δχ²=183.5, p≈<1e-6, Z≈13.5, class=very-strong

- Implication: Outer residual RMS (z): 1.57
- Implication: Outer residual mean (z): 0.218
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06917

- Figure: [toy_models/out_dyed_spacetime/png/UGC06917.png](toy_models/out_dyed_spacetime/png/UGC06917.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06917.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06917.csv)
- Summary: n=11, Q_flag=1, T=9, D=18 Mpc, Vflat=109 km/s, Rdisk=2.76 kpc, Rt=1.74 kpc, v_extra_asym=92.5 km/s, env_delta=2.75
- Fit diagnostic: n_used=11, chi2_bar=1417, chi2_model=44.96, Δχ²=1372, p≈<1e-6, Z≈37, class=very-strong

- Implication: Outer residual RMS (z): 0.831
- Implication: Outer residual mean (z): -0.0288
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06923

- Figure: [toy_models/out_dyed_spacetime/png/UGC06923.png](toy_models/out_dyed_spacetime/png/UGC06923.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06923.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06923.csv)
- Summary: n=6, Q_flag=2, T=10, D=18 Mpc, Vflat=79.6 km/s, Rdisk=1.44 kpc, Rt=0.93 kpc, v_extra_asym=70.1 km/s, env_delta=2.22
- Fit diagnostic: n_used=6, chi2_bar=183.3, chi2_model=2.409, Δχ²=180.9, p≈<1e-6, Z≈13.5, class=very-strong

- Implication: Outer residual RMS (z): 0.66
- Implication: Outer residual mean (z): -0.0407
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06930

- Figure: [toy_models/out_dyed_spacetime/png/UGC06930.png](toy_models/out_dyed_spacetime/png/UGC06930.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06930.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06930.csv)
- Summary: n=10, Q_flag=1, T=7, D=18 Mpc, Vflat=107 km/s, Rdisk=3.94 kpc, Rt=1.74 kpc, v_extra_asym=89.7 km/s, env_delta=2.98
- Fit diagnostic: n_used=10, chi2_bar=573.9, chi2_model=8.511, Δχ²=565.4, p≈<1e-6, Z≈23.8, class=very-strong

- Implication: Outer residual RMS (z): 0.672
- Implication: Outer residual mean (z): -0.119
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06973

- Figure: [toy_models/out_dyed_spacetime/png/UGC06973.png](toy_models/out_dyed_spacetime/png/UGC06973.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06973.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06973.csv)
- Summary: n=9, Q_flag=3, T=2, D=18 Mpc, Vflat=174 km/s, Rdisk=1.07 kpc, Rt=6.1 kpc, v_extra_asym=117 km/s, env_delta=4.49
- Fit diagnostic: n_used=9, chi2_bar=656.7, chi2_model=542.4, Δχ²=114.3, p≈<1e-6, Z≈10.7, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC06983

- Figure: [toy_models/out_dyed_spacetime/png/UGC06983.png](toy_models/out_dyed_spacetime/png/UGC06983.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06983.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC06983.csv)
- Summary: n=17, Q_flag=1, T=6, D=18 Mpc, Vflat=109 km/s, Rdisk=3.21 kpc, Rt=1.74 kpc, v_extra_asym=97.2 km/s, env_delta=2.29
- Fit diagnostic: n_used=17, chi2_bar=1922, chi2_model=39.71, Δχ²=1882, p≈<1e-6, Z≈43.4, class=very-strong

- Implication: Outer residual RMS (z): 0.771
- Implication: Outer residual mean (z): 0.0332
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07089

- Figure: [toy_models/out_dyed_spacetime/png/UGC07089.png](toy_models/out_dyed_spacetime/png/UGC07089.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07089.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07089.csv)
- Summary: n=12, Q_flag=2, T=8, D=18 Mpc, Vflat=0 km/s, Rdisk=2.26 kpc, Rt=2.61 kpc, v_extra_asym=60.3 km/s, env_delta=4.34
- Fit diagnostic: n_used=12, chi2_bar=265.3, chi2_model=7.037, Δχ²=258.2, p≈<1e-6, Z≈16.1, class=very-strong

- Implication: Outer residual RMS (z): 0.516
- Implication: Outer residual mean (z): -0.0522
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07125

- Figure: [toy_models/out_dyed_spacetime/png/UGC07125.png](toy_models/out_dyed_spacetime/png/UGC07125.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07125.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07125.csv)
- Summary: n=13, Q_flag=1, T=9, D=19.8 Mpc, Vflat=65.2 km/s, Rdisk=3.38 kpc, Rt=2.88 kpc, v_extra_asym=48.9 km/s, env_delta=5.28
- Fit diagnostic: n_used=13, chi2_bar=1052, chi2_model=8.106, Δχ²=1044, p≈<1e-6, Z≈32.3, class=very-strong

- Implication: Outer residual RMS (z): 0.637
- Implication: Outer residual mean (z): 0.0387
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07151

- Figure: [toy_models/out_dyed_spacetime/png/UGC07151.png](toy_models/out_dyed_spacetime/png/UGC07151.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07151.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07151.csv)
- Summary: n=11, Q_flag=1, T=6, D=6.87 Mpc, Vflat=73.5 km/s, Rdisk=1.25 kpc, Rt=1 kpc, v_extra_asym=72.2 km/s, env_delta=1.65
- Fit diagnostic: n_used=11, chi2_bar=1274, chi2_model=129.6, Δχ²=1144, p≈<1e-6, Z≈33.8, class=very-strong

- Implication: Outer residual RMS (z): 2.88
- Implication: Outer residual mean (z): 0.194
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07232

- Figure: [toy_models/out_dyed_spacetime/png/UGC07232.png](toy_models/out_dyed_spacetime/png/UGC07232.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07232.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07232.csv)
- Summary: n=4, Q_flag=2, T=10, D=2.83 Mpc, Vflat=0 km/s, Rdisk=0.29 kpc, Rt=0.41 kpc, v_extra_asym=38.6 km/s, env_delta=0.731
- Fit diagnostic: n_used=4, chi2_bar=72.74, chi2_model=2.218, Δχ²=70.53, p≈<1e-6, Z≈8.4, class=very-strong

- Implication: Outer residual RMS (z): 0.0402
- Implication: Outer residual mean (z): 0.0402
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07261

- Figure: [toy_models/out_dyed_spacetime/png/UGC07261.png](toy_models/out_dyed_spacetime/png/UGC07261.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07261.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07261.csv)
- Summary: n=7, Q_flag=2, T=8, D=13.1 Mpc, Vflat=74.7 km/s, Rdisk=1.2 kpc, Rt=1.9 kpc, v_extra_asym=72.5 km/s, env_delta=6.87
- Fit diagnostic: n_used=7, chi2_bar=238.7, chi2_model=37.54, Δχ²=201.1, p≈<1e-6, Z≈14.2, class=very-strong

- Implication: Outer residual RMS (z): 0.695
- Implication: Outer residual mean (z): 0.41
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07323

- Figure: [toy_models/out_dyed_spacetime/png/UGC07323.png](toy_models/out_dyed_spacetime/png/UGC07323.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07323.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07323.csv)
- Summary: n=10, Q_flag=1, T=8, D=8 Mpc, Vflat=0 km/s, Rdisk=2.26 kpc, Rt=4.65 kpc, v_extra_asym=80.3 km/s, env_delta=2.09
- Fit diagnostic: n_used=10, chi2_bar=369.2, chi2_model=49, Δχ²=320.2, p≈<1e-6, Z≈17.9, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07399

- Figure: [toy_models/out_dyed_spacetime/png/UGC07399.png](toy_models/out_dyed_spacetime/png/UGC07399.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07399.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07399.csv)
- Summary: n=10, Q_flag=1, T=8, D=8.43 Mpc, Vflat=103 km/s, Rdisk=1.64 kpc, Rt=0.61 kpc, v_extra_asym=111 km/s, env_delta=2.19
- Fit diagnostic: n_used=10, chi2_bar=3291, chi2_model=251.4, Δχ²=3040, p≈<1e-6, Z≈55.1, class=very-strong

- Implication: Outer residual RMS (z): 4.38
- Implication: Outer residual mean (z): -0.752
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07524

- Figure: [toy_models/out_dyed_spacetime/png/UGC07524.png](toy_models/out_dyed_spacetime/png/UGC07524.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07524.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07524.csv)
- Summary: n=31, Q_flag=1, T=9, D=4.74 Mpc, Vflat=79.5 km/s, Rdisk=3.46 kpc, Rt=0.35 kpc, v_extra_asym=65.3 km/s, env_delta=1.28
- Fit diagnostic: n_used=31, chi2_bar=3194, chi2_model=26.53, Δχ²=3168, p≈<1e-6, Z≈56.3, class=very-strong

- Implication: Outer residual RMS (z): 0.876
- Implication: Outer residual mean (z): -0.016
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07559

- Figure: [toy_models/out_dyed_spacetime/png/UGC07559.png](toy_models/out_dyed_spacetime/png/UGC07559.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07559.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07559.csv)
- Summary: n=7, Q_flag=2, T=10, D=4.97 Mpc, Vflat=0 km/s, Rdisk=0.58 kpc, Rt=0.72 kpc, v_extra_asym=29.6 km/s, env_delta=1.3
- Fit diagnostic: n_used=7, chi2_bar=64.69, chi2_model=3.298, Δχ²=61.39, p≈<1e-6, Z≈7.84, class=very-strong

- Implication: Outer residual RMS (z): 0.747
- Implication: Outer residual mean (z): -0.0494
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07577

- Figure: [toy_models/out_dyed_spacetime/png/UGC07577.png](toy_models/out_dyed_spacetime/png/UGC07577.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07577.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07577.csv)
- Summary: n=9, Q_flag=2, T=10, D=2.59 Mpc, Vflat=0 km/s, Rdisk=0.9 kpc, Rt=1.32 kpc, v_extra_asym=10.8 km/s, env_delta=0.619
- Fit diagnostic: n_used=9, chi2_bar=4.779, chi2_model=0.5315, Δχ²=4.248, p≈0.0393, Z≈2.06, class=moderate

- Implication: Extra-term improves fit at a suggestive level; worth checking for systematics (inclination, distance, inner radii handling).

### UGC07603

- Figure: [toy_models/out_dyed_spacetime/png/UGC07603.png](toy_models/out_dyed_spacetime/png/UGC07603.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07603.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07603.csv)
- Summary: n=12, Q_flag=1, T=7, D=4.7 Mpc, Vflat=61.6 km/s, Rdisk=0.53 kpc, Rt=0.68 kpc, v_extra_asym=68.8 km/s, env_delta=1.39
- Fit diagnostic: n_used=12, chi2_bar=1421, chi2_model=91.95, Δχ²=1330, p≈<1e-6, Z≈36.5, class=very-strong

- Implication: Outer residual RMS (z): 2.75
- Implication: Outer residual mean (z): -0.639
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07608

- Figure: [toy_models/out_dyed_spacetime/png/UGC07608.png](toy_models/out_dyed_spacetime/png/UGC07608.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07608.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07608.csv)
- Summary: n=8, Q_flag=1, T=10, D=8.21 Mpc, Vflat=0 km/s, Rdisk=1.5 kpc, Rt=4.78 kpc, v_extra_asym=80.7 km/s, env_delta=2.33
- Fit diagnostic: n_used=8, chi2_bar=200, chi2_model=37.64, Δχ²=162.4, p≈<1e-6, Z≈12.7, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07690

- Figure: [toy_models/out_dyed_spacetime/png/UGC07690.png](toy_models/out_dyed_spacetime/png/UGC07690.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07690.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07690.csv)
- Summary: n=7, Q_flag=2, T=10, D=8.11 Mpc, Vflat=57.4 km/s, Rdisk=0.57 kpc, Rt=0.59 kpc, v_extra_asym=56 km/s, env_delta=2.32
- Fit diagnostic: n_used=7, chi2_bar=195, chi2_model=45.2, Δχ²=149.8, p≈<1e-6, Z≈12.2, class=very-strong

- Implication: Outer residual RMS (z): 2.47
- Implication: Outer residual mean (z): -1.01
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC07866

- Figure: [toy_models/out_dyed_spacetime/png/UGC07866.png](toy_models/out_dyed_spacetime/png/UGC07866.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07866.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC07866.csv)
- Summary: n=7, Q_flag=2, T=10, D=4.57 Mpc, Vflat=0 km/s, Rdisk=0.61 kpc, Rt=1 kpc, v_extra_asym=31 km/s, env_delta=1.11
- Fit diagnostic: n_used=7, chi2_bar=51.85, chi2_model=6.919, Δχ²=44.93, p≈<1e-6, Z≈6.7, class=very-strong

- Implication: Outer residual RMS (z): 0.597
- Implication: Outer residual mean (z): 0.581
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC08286

- Figure: [toy_models/out_dyed_spacetime/png/UGC08286.png](toy_models/out_dyed_spacetime/png/UGC08286.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08286.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08286.csv)
- Summary: n=17, Q_flag=1, T=6, D=6.5 Mpc, Vflat=82.4 km/s, Rdisk=1.05 kpc, Rt=2.37 kpc, v_extra_asym=86.1 km/s, env_delta=1.53
- Fit diagnostic: n_used=17, chi2_bar=7951, chi2_model=725.1, Δχ²=7226, p≈<1e-6, Z≈85, class=very-strong

- Implication: Outer residual RMS (z): 3.28
- Implication: Outer residual mean (z): 3.17
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC08490

- Figure: [toy_models/out_dyed_spacetime/png/UGC08490.png](toy_models/out_dyed_spacetime/png/UGC08490.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08490.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08490.csv)
- Summary: n=30, Q_flag=1, T=9, D=4.65 Mpc, Vflat=78.6 km/s, Rdisk=0.67 kpc, Rt=0.68 kpc, v_extra_asym=77.6 km/s, env_delta=0.708
- Fit diagnostic: n_used=30, chi2_bar=4436, chi2_model=236.6, Δχ²=4200, p≈<1e-6, Z≈64.8, class=very-strong

- Implication: Outer residual RMS (z): 2.39
- Implication: Outer residual mean (z): -0.521
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC08550

- Figure: [toy_models/out_dyed_spacetime/png/UGC08550.png](toy_models/out_dyed_spacetime/png/UGC08550.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08550.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08550.csv)
- Summary: n=11, Q_flag=1, T=7, D=6.7 Mpc, Vflat=56.9 km/s, Rdisk=0.45 kpc, Rt=0.97 kpc, v_extra_asym=59.6 km/s, env_delta=1.37
- Fit diagnostic: n_used=11, chi2_bar=2213, chi2_model=197.4, Δχ²=2015, p≈<1e-6, Z≈44.9, class=very-strong

- Implication: Outer residual RMS (z): 2.74
- Implication: Outer residual mean (z): -0.192
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC08699

- Figure: [toy_models/out_dyed_spacetime/png/UGC08699.png](toy_models/out_dyed_spacetime/png/UGC08699.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08699.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08699.csv)
- Summary: n=41, Q_flag=2, T=2, D=39.3 Mpc, Vflat=182 km/s, Rdisk=3.09 kpc, Rt=4.81 kpc, v_extra_asym=150 km/s, env_delta=1.22
- Fit diagnostic: n_used=41, chi2_bar=6536, chi2_model=474.6, Δχ²=6061, p≈<1e-6, Z≈77.9, class=very-strong

- Implication: Outer residual RMS (z): 1.41
- Implication: Outer residual mean (z): 0.126
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC08837

- Figure: [toy_models/out_dyed_spacetime/png/UGC08837.png](toy_models/out_dyed_spacetime/png/UGC08837.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08837.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC08837.csv)
- Summary: n=8, Q_flag=2, T=10, D=7.21 Mpc, Vflat=0 km/s, Rdisk=1.72 kpc, Rt=2.63 kpc, v_extra_asym=40.9 km/s, env_delta=1.14
- Fit diagnostic: n_used=8, chi2_bar=140, chi2_model=1.974, Δχ²=138, p≈<1e-6, Z≈11.7, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC09037

- Figure: [toy_models/out_dyed_spacetime/png/UGC09037.png](toy_models/out_dyed_spacetime/png/UGC09037.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC09037.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC09037.csv)
- Summary: n=22, Q_flag=2, T=6, D=83.6 Mpc, Vflat=152 km/s, Rdisk=4.28 kpc, Rt=2.64 kpc, v_extra_asym=86.5 km/s, env_delta=-0.48
- Fit diagnostic: n_used=22, chi2_bar=749.7, chi2_model=242.6, Δχ²=507, p≈<1e-6, Z≈22.5, class=very-strong

- Implication: Outer residual RMS (z): 2.61
- Implication: Outer residual mean (z): -0.688
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC09133

- Figure: [toy_models/out_dyed_spacetime/png/UGC09133.png](toy_models/out_dyed_spacetime/png/UGC09133.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC09133.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC09133.csv)
- Summary: n=68, Q_flag=1, T=2, D=57.1 Mpc, Vflat=227 km/s, Rdisk=6.97 kpc, Rt=12.7 kpc, v_extra_asym=199 km/s, env_delta=0.0407
- Fit diagnostic: n_used=68, chi2_bar=1.197e+05, chi2_model=1533, Δχ²=1.181e+05, p≈<1e-6, Z≈344, class=very-strong

- Implication: Outer residual RMS (z): 3.62
- Implication: Outer residual mean (z): -0.57
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC09992

- Figure: [toy_models/out_dyed_spacetime/png/UGC09992.png](toy_models/out_dyed_spacetime/png/UGC09992.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC09992.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC09992.csv)
- Summary: n=5, Q_flag=2, T=10, D=10.7 Mpc, Vflat=33.6 km/s, Rdisk=1.04 kpc, Rt=0.78 kpc, v_extra_asym=29.3 km/s, env_delta=0.118
- Fit diagnostic: n_used=5, chi2_bar=19.62, chi2_model=7.473, Δχ²=12.15, p≈4.91e-04, Z≈3.49, class=strong

- Implication: Outer residual RMS (z): 0.497
- Implication: Outer residual mean (z): 0.0798
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC10310

- Figure: [toy_models/out_dyed_spacetime/png/UGC10310.png](toy_models/out_dyed_spacetime/png/UGC10310.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC10310.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC10310.csv)
- Summary: n=7, Q_flag=1, T=9, D=15.2 Mpc, Vflat=71.4 km/s, Rdisk=1.8 kpc, Rt=2.21 kpc, v_extra_asym=68.8 km/s, env_delta=0.279
- Fit diagnostic: n_used=7, chi2_bar=267.2, chi2_model=33.49, Δχ²=233.7, p≈<1e-6, Z≈15.3, class=very-strong

- Implication: Outer residual RMS (z): 1.03
- Implication: Outer residual mean (z): 0.635
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC11455

- Figure: [toy_models/out_dyed_spacetime/png/UGC11455.png](toy_models/out_dyed_spacetime/png/UGC11455.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11455.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11455.csv)
- Summary: n=36, Q_flag=1, T=6, D=78.6 Mpc, Vflat=269 km/s, Rdisk=5.93 kpc, Rt=14.6 kpc, v_extra_asym=203 km/s, env_delta=0.423
- Fit diagnostic: n_used=36, chi2_bar=2835, chi2_model=510.3, Δχ²=2325, p≈<1e-6, Z≈48.2, class=very-strong

- Implication: Outer residual RMS (z): 1.69
- Implication: Outer residual mean (z): -0.677
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC11557

- Figure: [toy_models/out_dyed_spacetime/png/UGC11557.png](toy_models/out_dyed_spacetime/png/UGC11557.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11557.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11557.csv)
- Summary: n=12, Q_flag=2, T=8, D=24.2 Mpc, Vflat=0 km/s, Rdisk=2.75 kpc, Rt=0.99 kpc, v_extra_asym=36.2 km/s, env_delta=-0.887
- Fit diagnostic: n_used=12, chi2_bar=26.7, chi2_model=15.88, Δχ²=10.83, p≈0.001, Z≈3.29, class=moderate

- Implication: Outer residual RMS (z): 0.881
- Implication: Outer residual mean (z): 0.0744
- Implication: Extra-term improves fit at a suggestive level; worth checking for systematics (inclination, distance, inner radii handling).

### UGC11820

- Figure: [toy_models/out_dyed_spacetime/png/UGC11820.png](toy_models/out_dyed_spacetime/png/UGC11820.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11820.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11820.csv)
- Summary: n=10, Q_flag=1, T=9, D=18.1 Mpc, Vflat=0 km/s, Rdisk=2.08 kpc, Rt=1.01 kpc, v_extra_asym=67.2 km/s, env_delta=-0.517
- Fit diagnostic: n_used=10, chi2_bar=1.195e+04, chi2_model=161.3, Δχ²=1.179e+04, p≈<1e-6, Z≈109, class=very-strong

- Implication: Outer residual RMS (z): 5.16
- Implication: Outer residual mean (z): 0.206
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC11914

- Figure: [toy_models/out_dyed_spacetime/png/UGC11914.png](toy_models/out_dyed_spacetime/png/UGC11914.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11914.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC11914.csv)
- Summary: n=65, Q_flag=1, T=2, D=16.9 Mpc, Vflat=288 km/s, Rdisk=2.44 kpc, Rt=9.83 kpc, v_extra_asym=365 km/s, env_delta=-0.634
- Fit diagnostic: n_used=65, chi2_bar=1.34e+04, chi2_model=7137, Δχ²=6264, p≈<1e-6, Z≈79.1, class=very-strong

- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC12506

- Figure: [toy_models/out_dyed_spacetime/png/UGC12506.png](toy_models/out_dyed_spacetime/png/UGC12506.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC12506.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC12506.csv)
- Summary: n=31, Q_flag=2, T=6, D=101 Mpc, Vflat=234 km/s, Rdisk=7.38 kpc, Rt=4.1 kpc, v_extra_asym=207 km/s, env_delta=-0.495
- Fit diagnostic: n_used=31, chi2_bar=2416, chi2_model=40.72, Δχ²=2375, p≈<1e-6, Z≈48.7, class=very-strong

- Implication: Outer residual RMS (z): 0.552
- Implication: Outer residual mean (z): 0.0635
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC12632

- Figure: [toy_models/out_dyed_spacetime/png/UGC12632.png](toy_models/out_dyed_spacetime/png/UGC12632.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC12632.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC12632.csv)
- Summary: n=15, Q_flag=1, T=9, D=9.77 Mpc, Vflat=71.7 km/s, Rdisk=2.42 kpc, Rt=2.85 kpc, v_extra_asym=67.1 km/s, env_delta=-0.601
- Fit diagnostic: n_used=15, chi2_bar=1828, chi2_model=86.12, Δχ²=1742, p≈<1e-6, Z≈41.7, class=very-strong

- Implication: Outer residual RMS (z): 1.11
- Implication: Outer residual mean (z): 1.08
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGC12732

- Figure: [toy_models/out_dyed_spacetime/png/UGC12732.png](toy_models/out_dyed_spacetime/png/UGC12732.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGC12732.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGC12732.csv)
- Summary: n=16, Q_flag=1, T=9, D=13.2 Mpc, Vflat=0 km/s, Rdisk=1.98 kpc, Rt=1.92 kpc, v_extra_asym=77.4 km/s, env_delta=-0.67
- Fit diagnostic: n_used=16, chi2_bar=2607, chi2_model=66.42, Δχ²=2541, p≈<1e-6, Z≈50.4, class=very-strong

- Implication: Outer residual RMS (z): 1.23
- Implication: Outer residual mean (z): 0.124
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGCA281

- Figure: [toy_models/out_dyed_spacetime/png/UGCA281.png](toy_models/out_dyed_spacetime/png/UGCA281.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGCA281.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGCA281.csv)
- Summary: n=7, Q_flag=3, T=11, D=5.68 Mpc, Vflat=0 km/s, Rdisk=1.72 kpc, Rt=0.41 kpc, v_extra_asym=31.8 km/s, env_delta=1.23
- Fit diagnostic: n_used=7, chi2_bar=279.8, chi2_model=33.9, Δχ²=245.9, p≈<1e-6, Z≈15.7, class=very-strong

- Implication: Outer residual RMS (z): 2.33
- Implication: Outer residual mean (z): 2
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGCA442

- Figure: [toy_models/out_dyed_spacetime/png/UGCA442.png](toy_models/out_dyed_spacetime/png/UGCA442.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGCA442.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGCA442.csv)
- Summary: n=8, Q_flag=1, T=9, D=4.35 Mpc, Vflat=56.4 km/s, Rdisk=1.18 kpc, Rt=2.11 kpc, v_extra_asym=55.1 km/s, env_delta=0.078
- Fit diagnostic: n_used=8, chi2_bar=4310, chi2_model=93.46, Δχ²=4217, p≈<1e-6, Z≈64.9, class=very-strong

- Implication: Outer residual RMS (z): 1.49
- Implication: Outer residual mean (z): 0.423
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

### UGCA444

- Figure: [toy_models/out_dyed_spacetime/png/UGCA444.png](toy_models/out_dyed_spacetime/png/UGCA444.png)
- Data: [toy_models/out_sparc_runs_full_with_composition/galaxies/UGCA444.csv](toy_models/out_sparc_runs_full_with_composition/galaxies/UGCA444.csv)
- Summary: n=36, Q_flag=2, T=10, D=0.98 Mpc, Vflat=37 km/s, Rdisk=0.83 kpc, Rt=1.11 kpc, v_extra_asym=40.8 km/s, env_delta=0.208
- Fit diagnostic: n_used=36, chi2_bar=454.7, chi2_model=48.97, Δχ²=405.7, p≈<1e-6, Z≈20.1, class=very-strong

- Implication: Outer residual RMS (z): 0.942
- Implication: Outer residual mean (z): 0.885
- Implication: Extra-term materially improves weighted fit over baryons-only under a 1-parameter nested Δχ² diagnostic.

## 4) Aggregate counts (Δχ² diagnostic classes)

- very-strong: 161
- strong: 5
- moderate: 3
- weak: 4
- no-improvement: 2
- unrated: 0
