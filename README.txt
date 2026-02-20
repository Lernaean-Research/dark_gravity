Spacetime Mechanics — Manuscript + SPARC-derived analysis tooling

This folder is a working directory for:

1) The current manuscript draft (DOCX/PDF)
2) Reproducible SPARC-based analysis and visualization scripts (Python)

## Contents

Manuscript drafts:

- Kitcey_2026_Spacetime_Mechanics.v.0.5.3.docx
- Kitcey_2026_Spacetime_Mechanics.v.0.5.3.pdf

Bibliography:

- references.bib

Analysis + rendering (Python):

- toy_models/
    - SPARC runner (per-galaxy fits + summary tables)
    - correlation / partial-correlation / permutation diagnostics
    - dyed-spacetime atlas renderer (3-panel and 6-panel)

Notebook entry point:

- SPARC_EdgeResponse_Analysis.ipynb
- NOTEBOOK_USAGE.md

## Where to start (recommended)

If you are reviewing or reproducing the SPARC-derived figures, start with:

- toy_models/README.md
- toy_models/DYED_SPACETIME_RENDERING_METHODOLOGY.md  (panel definitions + uncertainty propagation + non-claims)
- toy_models/DYED_SPACETIME_SIX_PANEL_HOW_TO_READ.md  (executive guide; how to read each of the six panels)

For the SPARC runner itself:

- toy_models/SPARC_ROTMod_METHODOLOGY.md
- toy_models/ROBUST_Q_EST_SPARC175.md  (robust, non-fitted outer deficit estimator Q_est)

## Outputs

Most scripts write their outputs under toy_models/out_*/.

In particular, the current six-panel “dyed spacetime” atlas render (PNGs + a multipage PDF) is written under:

- toy_models/out_spacetime_sixpanel_full_v3/

See toy_models/DYED_SPACETIME_RENDERING_METHODOLOGY.md for exact output filenames.