# Spacetime Mechanics (manuscript + SPARC-derived analysis tooling)

This repository contains:

- Manuscript drafts (DOCX/PDF)
- Reproducible SPARC-based analysis and visualization scripts (Python)

The main analysis and rendering code lives in [toy_models/](toy_models/).

## Where to start

- [toy_models/README.md](toy_models/README.md) (index of scripts and quickstarts)
- [toy_models/SPARC_ROTMod_METHODOLOGY.md](toy_models/SPARC_ROTMod_METHODOLOGY.md) (SPARC rotmod runner: definitions, units, outputs)
- [toy_models/DYED_SPACETIME_RENDERING_METHODOLOGY.md](toy_models/DYED_SPACETIME_RENDERING_METHODOLOGY.md) (plot provenance + uncertainty propagation + non-claims)
- [toy_models/DYED_SPACETIME_SIX_PANEL_HOW_TO_READ.md](toy_models/DYED_SPACETIME_SIX_PANEL_HOW_TO_READ.md) (executive guide; panel-by-panel reading)

## Robust `Q_est` catalogue (SPARC 175)

A robust, non-fitted outer deficit estimator `Q_est` (in $(\mathrm{km/s})^2$) is documented here:

- [toy_models/ROBUST_Q_EST_SPARC175.md](toy_models/ROBUST_Q_EST_SPARC175.md)

To (re)compute the full 175-galaxy catalogue from the local per-galaxy CSVs:

```bash
python toy_models/q_est_sparc175.py
```

This writes:

- `toy_models/out_sparc_runs_full_with_composition/q_est.csv`

## License

© Copyright 2026 Robert D. Kitcey. Licensed under **CC BY-NC-ND 4.0**.

See [LICENSE](LICENSE).

## Data provenance

SPARC data products (e.g. `*_rotmod.dat`, `SPARC_Lelli2016c.mrt`) are from the SPARC project
(Lelli et al. 2016) and may be subject to SPARC’s own distribution/usage terms.
