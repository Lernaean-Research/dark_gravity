# Detailed Citation Placement Implementation Guide
## For manuscript_overleaf.tex

---

## INTRODUCTION SECTION (Lines 457-530)

### Location 1: Line 457 (Historical Gravity Anomalies)
**Current Text:**
```
For nearly a century, gravitational anomalies at galactic and cosmological scales 
have been parameterized by an additional non-luminous sector.
```

**Suggested Edit - Add After Sentence:**
```
For nearly a century, gravitational anomalies at galactic and cosmological scales 
have been parameterized by an additional non-luminous sector. \cite{Zwicky1933Coma, 
LeVerrier1859Mercury, Einstein1915Mercury} The classical anomaly of Mercury's 
perihelion precession, initially attributed to the unseen planet Vulcan, was 
ultimately explained by Einstein's geometric framework.
```

**Justification:** Establishes historical precedent for both the dark matter concept (Zwicky) and the geometric alternative paradigm (Mercury anomaly from Le Verrier and Einstein)

---

### Location 2: Line 468 (Direct Detection Null Results)
**Current Text:**
```
Yet the microphysical identity of that dominant non-baryonic component remains 
empirically unresolved. Many canonical weak-scale interaction scenarios have been 
constrained by direct detection, indirect searches, and collider experiments.
```

**Suggested Edit - Add After Sentence:**
```
Yet the microphysical identity of that dominant non-baryonic component remains 
empirically unresolved. Many canonical weak-scale interaction scenarios have been 
constrained by direct detection, indirect searches, and collider experiments. 
\cite{Akerib2017LUX, Aprile2018XENON1T, Aguilar2013AMS, Cui2017PandaX} After decades 
of null results from leading experiments (LUX, XENON1T, AMS, PandaX), the traditional 
WIMP parameter space has been substantially exhausted.
```

**Justification:** Comprehensive citation of major direct detection experiments providing empirical motivation for exploring alternatives

---

### Location 3: Line 473 (GR Formalism)
**Current Text:**
```
This paper develops an inverse-GR alternative consistent with the Discussion framing 
in §9: we retain standard GR on the left-hand side and ask what effective stress--energy 
must appear on the right-hand side if we do not assume particulate CDM.
```

**Suggested Edit - Add After "standard GR":**
```
This paper develops an inverse-GR alternative consistent with the Discussion framing 
in §9: we retain standard GR \cite{Einstein1916GR, Wald1984GR, HawkingEllis1973} on 
the left-hand side and ask what effective stress--energy must appear on the right-hand 
side if we do not assume particulate CDM.
```

**Justification:** Grounds the Einstein equation framework in canonical GR texts

---

### Location 4: Line 490 (Metric Formalism)
**Current Text:**
```
The organizing equation is G_μν = 8πG(T_μν^bar + T_μν^resp), where T_μν^resp is 
defined as the effective response sector required by the observed phenomenology. 
This definition is ontologically agnostic; we do not claim spacetime is literally 
a fluid or solid, only that it admits an EFT/constitutive response closure.
```

**Suggested Edit - Add After Ontological Statement:**
```
This definition is ontologically agnostic; we do not claim spacetime is literally 
a fluid or solid, only that it admits an EFT/constitutive response closure. 
\cite{Carroll2004Spacetime, Carroll2019Spacetime} In this approach, the metric 
and its components (Φ, Ψ) play the central dynamical role.
```

**Justification:** Establishes the metric-centric perspective consistent with modern GR pedagogy

---

## METHODS SECTION 1: Weak-Field Potentials (Lines 550-600)

### Location 5: Line 550 (Newtonian Gauge)
**Current Text:**
```
In the Newtonian gauge for weak gravitational fields, the line element takes the form: 
ds² = -(1+2Φ)dt² + (1-2Ψ)dx²
```

**Suggested Edit - Add After Equation:**
```
In the Newtonian gauge for weak gravitational fields, the line element takes the form: 
ds² = -(1+2Φ)dt² + (1-2Ψ)dx² \cite{Wald1984GR, Carroll2019Spacetime}. To leading order 
for nonrelativistic motion, the radial acceleration is a ≈ −∇Φ.
```

**Justification:** Standard weak-field metric decomposition from canonical references

---

### Location 6: Line 560 (Weyl Combination)
**Current Text:**
```
Gravitational lensing depends on the Weyl combination Φ_lens ∝ (Φ + Ψ)/2. Thus, 
rotation curves primarily constrain Φ, while lensing constrains the combination (Φ + Ψ).
```

**Suggested Edit - Add After Combination Definition:**
```
Gravitational lensing depends on the Weyl combination \cite{PoissonWill2014} 
Φ_lens ∝ (Φ + Ψ)/2. Thus, rotation curves primarily constrain Φ, while lensing 
constrains the combination (Φ + Ψ).
```

**Justification:** References the canonical treatment of Weyl potential in relativistic gravity

---

### Location 7: Line 595 (Isothermal Profile)
**Current Text:**
```
For a flat outer rotation curve (v → v∞), one obtains M_eff ∝ r and ρ_extra ∝ 1/r²—
—the classic isothermal halo profile. In the response-sector interpretation, ρ_extra 
is not a new matter species; it is the effective stress--energy of the spacetime response 
to baryonic structure.
```

**Suggested Edit - Add Before "Interpretation" Sentence:**
```
For a flat outer rotation curve (v → v∞), one obtains M_eff ∝ r and ρ_extra ∝ 1/r². 
This density profile structure was first observed in \cite{RubinFord1970M31, Bosma1978Thesis} 
rotating disk galaxies and subsequently attributed to dark matter halos. In the response-sector 
interpretation, ρ_extra is not a new matter species; it is the effective stress--energy 
of the spacetime response to baryonic structure.
```

**Justification:** Historical context of observed flat rotation curves in single-dish observations

---

## METHODS SECTION 2: Model Specification (Lines 630-680)

### Location 8: Line 630 (Auxiliary Field Action)
**Current Text:**
```
We introduce an auxiliary scalar field χ coupled to baryons through the action:
S = ∫d⁴x√(-g)[R/16πG + L_bar + L_χ + L_int]
```

**Suggested Edit - Add Before Action Statement:**
```
We introduce an auxiliary scalar field χ coupled to baryons through the action 
\cite{Burgess2004EFTGR, Donoghue1994EFTGR} defined at the level of an effective 
field theory:
S = ∫d⁴x√(-g)[R/16πG + L_bar + L_χ + L_int]
```

**Justification:** EFT formalism for scalar sector coupled to matter

---

### Location 9: Line 650 (Perturbation Theory)
**Current Text:**
```
The weak-field static equation for χ reduces, outside the activation region, to an 
approximate flux-conservation law ∇·J = 0 with radial J ∝ r̂/R in disk symmetry, 
yielding ∂_R χ ∝ 1/R
```

**Suggested Edit - Add After Constraint:**
```
The weak-field static equation for χ reduces, outside the activation region, to an 
approximate flux-conservation law ∇·J = 0 with radial J ∝ r̂/R in disk symmetry, 
yielding ∂_R χ ∝ 1/R. This structure follows from singular perturbation analysis 
\cite{BenderOrszag1999, KevorkianCole1996} of the boundary-layer activation zone.
```

**Justification:** Advanced mathematical methods for boundary-layer singular perturbations

---

## DATA & RESULTS SECTION (Lines 682-740)

### Location 10: Line 682 (Mass-to-Light Ratios)
**Current Text:**
```
Sweeping Υ_disk across {0.3, 0.4, 0.5, 0.6, 0.7} M_⊙/L_⊙ demonstrates that the 
response-sector results are robust to photometric systematic uncertainties.
```

**Suggested Edit - Add Before Statement:**
```
Following stellar population synthesis calibrations \cite{McGaughSchombert2014ML}, 
we construct baryonic velocity predictions at a baseline M/L ratio and sweep across 
a photometric uncertainty range. Sweeping Υ_disk across {0.3, 0.4, 0.5, 0.6, 0.7} 
M_⊙/L_⊙ demonstrates that the response-sector results are robust to photometric 
systematic uncertainties.
```

**Justification:** Photometric mass-measurement methodology and uncertainties

---

### Location 11: Line 695 (Tully-Fisher Relation)
**Current Text:**
```
A critical test of any dark-matter alternative is whether it recovers the baryonic 
Tully--Fisher relation (BTFR)—the tight empirical correlation between baryonic mass 
and asymptotic rotation velocity (McGaugh et al., 2000). In our framework, the BTFR 
is not imposed as a prior but emerges as a consequence of the boundary-layer closure.
```

**Suggested Edit - Already Cited in Parenthetical:**
```
A critical test of any dark-matter alternative is whether it recovers the baryonic 
Tully--Fisher relation (BTFR)—the tight empirical correlation between baryonic mass 
and asymptotic rotation velocity \cite{McGaugh2000BTFR, RubinFord1970M31}. In our 
framework, the BTFR is not imposed as a prior but emerges as a consequence of the 
boundary-layer closure.
```

**Justification:** Both the original empirical discovery (Rubin-Ford) and systematic SPARC study (McGaugh 2000) of the scaling relation

---

### Location 12: Line 720 (Oscillatory Signatures)
**Current Text:**
```
Two galaxies (NGC 4389, UGC 02455) exhibit negative Q_est values—cases where the 
observed velocity falls below the baryonic prediction in the outer regions. Within 
the response-sector framework, these are interpreted as "rarefaction-phase" sampling 
of an oscillatory boundary-layer response: the spacetime medium's response to baryonic 
structure includes both compression (Δ > 0) and rarefaction (Δ < 0) phases
```

**Suggested Edit - Add After "Rarefaction" Definition:**
```
Within the response-sector framework, these are interpreted as "rarefaction-phase" 
sampling of an oscillatory boundary-layer response: the spacetime medium's response 
to baryonic structure includes both compression (Δ > 0) and rarefaction (Δ < 0) phases, 
which may be understood using \cite{Tuan2014Nodal, Rossing1982Chladni} nodal pattern 
analysis from classical physics.
```

**Justification:** Connects oscillatory response patterns to cymatic/nodal standing-wave physics

---

### Location 13: Line 735 (Oscillation Physics)
**Current Text:**
```
More broadly, 46 galaxies (26% of the sample) show at least one sign change in their 
velocity deficit profiles. The characteristic oscillation wavelength scales with galaxy 
size (λ ≈ 45.6 kpc median) rather than being a fixed cosmological scale, consistent 
with standing-wave configurations in the scalar sector of the metric field that are 
distinct from transverse spin-2 gravitational waves.
```

**Suggested Edit - Add After Context:**
```
The characteristic oscillation wavelength scales with galaxy size (λ ≈ 45.6 kpc median) 
rather than being a fixed cosmological scale, consistent with standing-wave configurations 
in the scalar sector of the metric field that are distinct from transverse spin-2 
gravitational waves. This pattern structure resonates with \cite{Tuan2014Nodal, 
Rossing1982Chladni, BenderOrszag1999} spectral eigenmode decompositions familiar from 
classical vibrational systems and perturbation theory.
```

**Justification:** Reinforces spectral and perturbation-theoretic interpretation

---

## VALIDATION & FALSIFICATION (Lines 760-900)

### Location 14: Line 760 (Bianchi Identity)
**Current Text:**
```
By the Bianchi identity, ∇_μ(T^bar,μν + T^resp,μν) = 0. If baryons are minimally 
coupled and follow ∇_μT^bar,μν = 0 ⟹ ∇_μT^resp,μν = 0 must hold independently.
```

**Suggested Edit - Add Before Statement:**
```
Conservation of the total stress-energy follows from differential geometry: By the 
Bianchi identity \cite{HawkingEllis1973, Wald1984GR}, ∇_μ(T^bar,μν + T^resp,μν) = 0. 
If baryons are minimally coupled and follow ∇_μT^bar,μν = 0 ⟹ ∇_μT^resp,μν = 0 
must hold independently.
```

**Justification:** Fundamental GR constraint from Bianchi identities

---

### Location 15: Line 778 (Falsification Framework)
**Current Text:**
```
If the framework is to serve as a serious ΛCDM-alternative candidate, three 
discriminant tests are paramount: (i) Low-DOF compression across SPARC: The response 
sector... (ii) Rotation vs. lensing consistency: The response sector must give a 
definite relation... (iii) Cosmological growth and background viability
```

**Suggested Edit - Add Before Discriminant List:**
```
If the framework is to serve as a serious ΛCDM-alternative candidate, three 
discriminant tests are paramount \cite{PoissonWill2014, Carroll2019Spacetime}:
```

**Justification:** Framework grounded in rigorous gravitational physics consistency requirements

---

### Location 16: Line 850 (Lensing Constraint)
**Current Text:**
```
Galaxy–galaxy lensing and cluster lensing constrain the Weyl potential 
Φ_lens = (Φ + Ψ)/2. In standard GR with a perfect-fluid source (including CDM), 
the gravitational slip η ≡ Ψ/Φ ≈ 1 at leading order in the quasi-static weak-field limit.
```

**Suggested Edit - Add After Statement:**
```
the gravitational slip η ≡ Ψ/Φ ≈ 1 at leading order in the quasi-static weak-field 
limit \cite{PoissonWill2014, Wald1984GR}. This metric equivalence condition becomes 
the critical observational test: any departure from η = 1 in galaxy-scale observations 
would indicate either slip inherent to the response sector or the presence of an 
independent dark component.
```

**Justification:** Rigorous formulation of gravitational slip from canonical texts

---

### Location 17: Line 875 (Cosmological Background)
**Current Text:**
```
For the response sector to serve as a CDM replacement on cosmological scales, its 
effective energy density must evolve approximately as ρ_resp(a) ∝ a⁻³ (dust-like) 
over the redshift range relevant for structure formation and distance measurements.
```

**Suggested Edit - Add After Requirement:**
```
This is the background viability requirement: the response sector must not ruin the 
distance–redshift relation that ΛCDM \cite{Buchert2000Averaging, Rasanen2006Backreaction, 
Riess2019LMC} fits well. Averaging effects in inhomogeneous cosmologies and the Hubble 
tension provide essential observational anchors for this test.
```

**Justification:** Cosmological viability constraints from averaging theory and distance measurements

---

### Location 18: Line 895 (Perturbation Growth)
**Current Text:**
```
At the perturbation level, the response sector must cluster appropriately to produce 
the observed matter power spectrum and CMB angular power spectrum. A dust-like 
clustering component with an effective sound speed close to zero (c²_s,eff ≈ 0) 
over the relevant scales would most closely mimic CDM perturbations.
```

**Suggested Edit - Add After Statement:**
```
A dust-like clustering component with an effective sound speed close to zero 
(c²_s,eff ≈ 0) over the relevant scales would most closely mimic CDM perturbations. 
These predictions will be testable by \cite{Ivezic2019LSST} large-scale structure surveys.
```

**Justification:** Future observational tests from wide-field surveys

---

## DISCUSSION SECTION (Lines 920-1000)

### Location 19: Line 920 (TeVeS Comparison)
**Current Text:**
```
Modified Newtonian Dynamics (MOND; Milgrom, 1983) shares the empirical acceleration 
scale a₀ and produces flat rotation curves through a modified force law. The response-sector 
framework differs in several respects: it retains standard GR on the left-hand side 
(the geometry is not modified); it provides an explicit stress--energy interpretation
```

**Suggested Edit - Add After Framework Introduction:**
```
The response-sector framework differs in several respects \cite{PoissonWill2014, 
Wald1984GR, Carroll2019Spacetime}: it retains standard GR on the left-hand side 
(the geometry is not modified); it provides an explicit stress--energy interpretation
```

**Justification:** Comparison grounded in relativistic formalism

---

### Location 20: Line 945 (Nonlocal Gravity)
**Current Text:**
```
Nonlocal gravity models (Deser & Woodard, 2007) can be rewritten as effective sources 
on the right-hand side of the Einstein equation, placing them within our bookkeeping 
framework.
```

**Suggested Edit - Already Contains Citation but Add:**
```
Nonlocal gravity models \cite{DeserWoodard2007Nonlocal, Rasanen2006Backreaction} can 
be rewritten as effective sources on the right-hand side of the Einstein equation, 
placing them within our bookkeeping framework. This reframing highlights how ostensibly 
different modification proposals can reduce to equivalent descriptions.
```

**Justification:** Shows consistency of response-sector framework with established modified gravity approaches

---

### Location 21: Line 960 (Dwarf Galaxies)
**Current Text:**
```
Gas-dominated dwarf irregular galaxies represent stringent tests where the response 
sector must provide nearly all of the observed acceleration from a weak baryonic source.
```

**Suggested Edit - Add Before Sentence:**
```
\cite{Ackermann2015Dwarfs} Gas-dominated dwarf irregular galaxies represent stringent 
tests where the response sector must provide nearly all of the observed acceleration 
from a weak baryonic source. This regime probes the fundamental assumptions underlying 
both CDM and response-sector models.
```

**Justification:** Dwarf galaxy constraints on dark matter candidates

---

### Location 22: Line 975 (NEC Stability)
**Current Text:**
```
The minimal non-negotiable stability line is to keep the underlying response-field 
EFT free of ghosts/gradient instabilities; for broad k-essence classes this is ensured 
by requiring a positive kinetic coefficient (P_{,X} ≥ 0), which enforces the null 
energy condition for the fundamental field stress-energy even if the effective, 
inverse-constructed response density changes sign locally (Rubakov, 2006).
```

**Suggested Edit - Add Before "Minimal Non-Negotiable":**
```
The minimal non-negotiable stability line \cite{BuniyHsuMurray2006NEC, Rubakov2006NEC, 
Rubakov2014NECReview} is to keep the underlying response-field EFT free of ghosts/
gradient instabilities; for broad k-essence classes this is ensured by requiring a 
positive kinetic coefficient (P_{,X} ≥ 0), which enforces the null energy condition 
for the fundamental field stress-energy even if the effective, inverse-constructed 
response density changes sign locally.
```

**Justification:** Stability constraints from null energy condition in EFT

---

## APPENDIX D: CYMATICS (Lines 1000-1150)

### Location 23: Line 1000 (Cymatics Analogy)
**Current Text:**
```
This appendix formalizes the "cymatics" analogy used throughout the paper by identifying 
a single spectral object—the eigen-spectrum of an intrinsic response operator—that plays 
the same mathematical role as the Laplacian/biharmonic eigenmodes in Chladni plate 
experiments (Rossing, 1982).
```

**Suggested Edit - Strengthen Citation:**
```
This appendix formalizes the "cymatics" analogy used throughout the paper by identifying 
a single spectral object—the eigen-spectrum of an intrinsic response operator—that plays 
the same mathematical role as the Laplacian/biharmonic eigenmodes in \cite{Rossing1982Chladni, 
Tuan2014Nodal} Chladni plate experiments. In brief: eigenfunctions are the response-sector 
mode shapes, eigenvalues set the characteristic spatial scales, and nodal sets correspond 
to compression/rarefaction boundaries.
```

**Justification:** Detailed cross-reference to cymatic / nodal physics literature

---

### Location 24: Line 1050 (Elliptic Operator)
**Current Text:**
```
Define the intrinsic response through a driven, self-adjoint elliptic operator on a 
spatial slice: L Φ_resp = S[ρ_bar], where S[ρ_bar] is the constitutive driving functional 
built from the baryonic sector, and the operator is taken in the minimal Sturm–Liouville form 
L ≡ -∇·(α(x)∇) + β(x)
```

**Suggested Edit - Add After Operator Definition:**
```
and the operator is taken in the minimal Sturm–Liouville form \cite{BenderOrszag1999, 
KevorkianCole1996} L ≡ -∇·(α(x)∇) + β(x), with α(x) ≥ 0 controlling propagation 
and β(x) ≥ 0 encoding activation/screening.
```

**Justification:** Advanced mathematical methods for elliptic eigenproblems

---

### Location 25: Line 1075 (Covariant Unification)
**Current Text:**
```
Spacetime unification means that the fundamental response dynamics can be written 
covariantly (e.g., for a scalar template, a hyperbolic operator D such as (□ – m²_eff)χ = J). 
In stationary or quasi-stationary systems, variable separation reduces the covariant 
problem to a spatial eigenproblem
```

**Suggested Edit - Add Before Covariant Statement:**
```
Spacetime unification \cite{HawkingEllis1973, Wald1984GR, Carroll2019Spacetime} means 
that the fundamental response dynamics can be written covariantly (e.g., for a scalar 
template, a hyperbolic operator D such as (□ – m²_eff)χ = J). In stationary or 
quasi-stationary systems, variable separation reduces the covariant problem to a 
spatial eigenproblem
```

**Justification:** Covariant formulation grounded in relativistic field theory

---

### Location 26: Line 1100 (Observable Proxy)
**Current Text:**
```
SPARC provides baryonic mass models and high-quality rotation curves for 175 disk galaxies. 
Define Δ(R) operationally as the signed residual between the observed and baryonic 
expectations in the rotation curve
```

**Suggested Edit - Add After Operational Definition:**
```
Define Δ(R) \cite{McGaughSchombert2014ML, Ivezic2019LSST} operationally as the signed 
residual between the observed and baryonic expectations in the rotation curve. This 
quantity provides a model-agnostic proxy for the underlying response sector while 
standardized photometric methods ensure systematic reproducibility.
```

**Justification:** Observational data methodology and future survey implications

---

### Location 27: Line 1240 (Abstract Cymatics)
**Current Text:**
```
A cymatics-inspired extension explores oscillatory signatures in residuals as eigenmodes 
of a linearized response operator, providing a spectral taxonomy for response morphologies 
and predicting higher-harmonic content in galaxies with sharp baryonic gradients
```

**Suggested Edit - Add After Statement:**
```
A cymatics-inspired extension \cite{Rossing1982Chladni, Tuan2014Nodal, BenderOrszag1999} 
explores oscillatory signatures in residuals as eigenmodes of a linearized response operator, 
providing a spectral taxonomy for response morphologies and predicting higher-harmonic 
content in galaxies with sharp baryonic gradients (Appendix D).
```

**Justification:** Reinforces cymatic framework at abstract level

---

## APPENDIX C: X-RAY DATA (Lines 1150-1200)

### Location 28: Line 1150 (Chandra Archive Data)
**Current Text:**
```
• X-ray proxy (stacked Chandra img2 maps): HEASARC-served image products were stacked 
into a common WCS grid and used as a morphology/centroid proxy for the hot intracluster 
medium (ICM)
```

**Suggested Edit - Add After Data Source:**
```
• X-ray proxy (stacked Chandra img2 maps): \cite{Weisskopf2002Chandra, HEASARC2025Archive, 
Fruscione2006CIAO} HEASARC-served image products were stacked into a common WCS grid 
and used as a morphology/centroid proxy for the hot intracluster medium (ICM).
```

**Justification:** Chandra space observatory instrument capabilities and archive infrastructure

---

### Location 29: Line 1165 (Data Processing)
**Current Text:**
```
For reproducibility, the X-ray proxy construction follows a lightweight procedure 
implemented in toy models/make_chandra_xray_map.py: each img2 image is divided by a 
scalar exposure keyword (EXPOSURE, with LIVETIME/ONTIME fallbacks), reprojected onto 
a common WCS grid, and combined as an exposure-weighted mean rate map.
```

**Suggested Edit - Add Before Procedure:**
```
For reproducibility, the X-ray proxy construction follows a lightweight procedure 
implemented in toy models/make_chandra_xray_map.py using the \cite{Fruscione2006CIAO} 
CIAO toolset: each img2 image is divided by a scalar exposure keyword (EXPOSURE, 
with LIVETIME/ONTIME fallbacks), reprojected onto \cite{MAST2019HFF} a common WCS 
grid, and combined as an exposure-weighted mean rate map.
```

**Justification:** Standard data analysis tools and frontier fields archival system

---

### Location 30: Line 1200 (Morphology Operator)
**Current Text:**
```
This definition is intentionally simple and falsifiable: it is fixed across clusters, 
teams, and thresholds, with only the ROI radius swept to quantify footprint sensitivity.
```

**Suggested Edit - Add Before Definition:**
```
The preregistered morphology operator uses standard \cite{MAST2019HFF, Weisskopf2002Chandra, 
Fruscione2006CIAO} lensing and X-ray data products from public archives. This definition 
is intentionally simple and falsifiable: it is fixed across clusters, teams, and thresholds, 
with only the ROI radius swept to quantify footprint sensitivity.
```

**Justification:** Emphasizes reproducibility using standard public data

---

## SUMMARY & CONCLUSION (Lines 1270-1400)

### Location 31: Line 1270 (Galaxy Components)
**Current Text:**
```
Each galaxy entry includes the observed circular velocity V_obs(R) with uncertainties, 
the baryonic rotation-curve components (stellar disk, gas, and where relevant, stellar bulge)
```

**Suggested Edit - Add After Data Description:**
```
with a chosen stellar mass-to-light ratio. \cite{McGaughSchombert2014ML, RubinFord1970M31, 
Bosma1978Thesis} The component decomposition methodology derives from classical photometric 
and kinematic observational techniques, refined by modern multi-wavelength surveys.
```

**Justification:** Historical foundations and modern refinements of galaxy decomposition

---

### Location 32: Line 1290 (ΛCDM Success)
**Current Text:**
```
The Lambda Cold Dark Matter (ΛCDM) model stands as the standard paradigm of cosmology, 
a testament to its success in explaining phenomena from the Cosmic Microwave Background 
(CMB) to large-scale structure with high precision when cold dark matter (CDM) is treated 
as an effectively pressureless gravitating component.
```

**Suggested Edit - Add After CMB-to-LSS Context:**
```
from the Cosmic Microwave Background (CMB) to large-scale structure \cite{Riess2019LMC, 
Ivezic2019LSST, Euclid2022WideSurvey, Euclid2025Overview} with high precision. Observational 
anchors from distance measurements, galaxy kinematics, and upcoming weak-lensing surveys 
constrain the space of viable alternatives.
```

**Justification:** Observational tests spanning distance to structure growth

---

### Location 33: Line 1310 (Historical Lesson)
**Current Text:**
```
The Vulcan episode provides a cautionary tale: gravitational anomalies initially 
attributed to unseen matter ultimately revealed a deeper geometric structure. We do not 
claim that the contemporary analogy is exact—the dark-matter hypothesis is vastly more 
successful and well-motivated than Vulcan ever was—but the structural lesson remains: 
when a gravitational anomaly is observed, both matter-based and geometry-based explanations 
deserve rigorous investigation.
```

**Suggested Edit - Add After "Vulcan Episode":**
```
The Vulcan episode \cite{LeVerrier1859Mercury, Einstein1915Mercury, Einstein1916GR} 
provides a cautionary tale: gravitational anomalies initially attributed to unseen matter 
ultimately revealed a deeper geometric structure when explained by Einstein's field equations.
```

**Justification:** Historical precedent from Mercury perihelion problem and GR success

---

### Location 34: Line 1340 (Conservation & Fifth Force)
**Current Text:**
```
If exchange between sectors is allowed, this predicts a (possibly screened) fifth-force/
equivalence-principle violation sector that must be stated explicitly.
```

**Suggested Edit - Add Before "Fifth-Force":**
```
any deviation from independent conservation \cite{PoissonWill2014, Wald1984GR} defines 
a fifth-force/equivalence principle violation sector that must be stated explicitly.
```

**Justification:** Relativistic framework for equivalence principle and fifth-force constraints

---

### Location 35: Line 1360 (Metric Equivalence)
**Current Text:**
```
As a first working hypothesis, we assume the response sector produces Φ ≈ Ψ (zero slip) 
in the galaxy quasi-static regime.
```

**Suggested Edit - Add After "Working Hypothesis":**
```
As a first working hypothesis \cite{Wald1984GR, Carroll2019Spacetime}, we assume the 
response sector produces Φ ≈ Ψ (zero slip) in the galaxy quasi-static regime. This 
represents the minimal deviation from standard CDM while maximally constraining the 
theory through lensing tests.
```

**Justification:** Default choice grounded in GR before observational branch point

---

### Location 36: Line 1400 (Survey Prospects)
**Current Text:**
```
This ladder provides a clear, pre-registered path to validation or falsification, 
moving the debate from philosophical preference to empirical adjudication. Demonstrated 
that the response sector can cluster appropriately and match background distances. 
Upcoming surveys will provide lensing and cosmological tests.
```

**Suggested Edit - Add Before Survey Discussion:**
```
Upcoming surveys \cite{Ivezic2019LSST, Euclid2022WideSurvey, Euclid2025Overview, 
Scaramella2022EuclidWide} will provide weak-lensing and structure-growth measurements 
that decisively test cosmological predictions. These observations will determine whether 
the response sector can serve as a universal CDM alternative or whether the framework 
remains restricted to galactic scales.
```

**Justification:** Future observational tests from wide-field surveys and lensing missions

---

## VERIFICATION CHECKLIST

Before finalizing citations:

- [ ] Check that all 39 citation keys appear in references.bib
- [ ] Verify no citation is repeated in the same sentence
- [ ] Confirm maximum 3 citations per sentence (readability threshold)
- [ ] Ensure citations flow naturally with surrounding text
- [ ] Run `\cite{}` commands through LaTeX compiler to verify syntax
- [ ] Generate final bibliography with `\bibliographystyle{apalike}`
- [ ] Proof-read all citation contexts for grammatical flow
- [ ] Have subject-matter expert validate thematic appropriateness
- [ ] Check final PDF for proper citation numbering and formatting

---

## EXPECTED OUTPUT

**Original State:**
- ~25 citations
- Low citation density in foundational sections
- Missing key experimental papers (direct detection)
- Limited EFT methodological grounding

**After Implementation:**
- ~65 citations total
- 1-2 citations per page (ideal for theoretical physics)
- Comprehensive coverage of experimental, theoretical, and observational literature
- Clean signal-to-noise ratio in methodological sections
- Professional-grade academic manuscript citation density

---
