# How to read the side-by-side comparisons

These side-by-side figures compare **the same galaxy** rendered two different ways:

- **Left: Per-galaxy extent** — the dyed panel spans ±R_data for that galaxy, so the image *always fills the frame*.
- **Right: Fixed extent (±40 kpc; masked beyond data)** — the dyed panel spans a *shared physical scale* across galaxies; pixels outside the observed R_data are masked (white) so you don’t accidentally interpret extrapolated structure.

## What is comparable (and what is not)

### 1) Spatial scale (kpc)
- **Comparable on the right, not on the left.**
- On the left, a 2 kpc galaxy and a 40 kpc galaxy both occupy the same visual diameter, because each is scaled to its own R_data.
- On the right, a 2 kpc galaxy is literally tiny within ±40 kpc, which is the correct physical comparison.

### 2) Dye intensity / depth
- In these samples, dye depth is globally normalized (`--fabric-norm global`), so **intensity is on a shared scale** (up to the global-percentile clamp).
- That makes intensity differences *intended* to be interpretable across galaxies.

### 3) “Significance”
- The dyed panel is **not a significance map**. It encodes an inferred effective potential depth profile from circular-orbit kinematics.
- If you want a per-galaxy *fit-improvement* ranking, use the report’s Δχ² / Z diagnostic (that is the closest thing currently to a quantitative “significance” metric).

## Practical comparative reading workflow

1) **Start with the right (fixed extent) version** to compare physical size and where the inferred structure sits in kpc.
2) **Then look at the left (per-galaxy extent)** to compare within-galaxy morphology without “wasting pixels” on empty space.
3) Use the **rotation curve + potential panels** to ground what you think you’re seeing in the dyed panel.

## Important honesty clause

Even the fixed-extent right panel is still an **effective-potential visualization**, not a unique GR spacetime reconstruction and not a computed geodesic map.
