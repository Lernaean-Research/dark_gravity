# DOCX v5.1 → LaTeX v5.0.5.7 Integration Report
# Comprehensive Extraction and Merge Strategy

**Generated:** February 27, 2026  
**Source Document:** Kitcey_2026_Intrinsic_Response_Sector_DM_Candidacy.v5.1.docx  
**Target Document:** manuscript_overleaf.tex (v5.0.5.7)

---

## EXTRACTION SUMMARY

### Document Statistics Comparison

| Metric | Current v5.0.5.7 (LaTeX) | New v5.1 (DOCX) | Delta |
|--------|--------------------------|-----------------|-------|
| **Total Words** | 13,952 | 1,290 | -12,662 |
| **Sections** | 79 (complete manuscript) | 4 (partial extract) | N/A |
| **Paragraphs** | ~1,617 lines | 38 paragraphs | N/A |
| **Unique Citations** | 50 | Not quantified | TBD |
| **Tables** | Multiple | 0 | N/A |
| **Figures** | Multiple | 1 (referenced) | +1 |

### Nature of v5.1 Document

**Critical Finding:** The v5.1 DOCX is **NOT a complete manuscript** but rather a **targeted revision document** containing:
- **Abstract** (revised)
- **Keywords** (expanded)
- **Section 1: Introduction** (concluding paragraph revised)
- **Section 5: Results** (major restructuring with new subsections)
- **Section 6.5: Cross-Validation** (expanded content)
- **Section 9.4: Strengths** (completely rewritten)

**Interpretation:** This is a precision strike update focusing on strengthening the **Bayesian model comparison** and **cross-validation** narrative, addressing reviewer/collaborator feedback requesting more rigorous statistical comparisons vs. standard NFW/Burkert halo models.

---

## NEW CONTENT ADDITIONS (Ordered by Section)

### [1] Abstract — Major Revision
**Type:** Content Addition + Technical Enhancement  
**Size:** ~180 words (full abstract)  
**Key Changes:**
- **ADDED:** Explicit BIC comparison statement: "we demonstrate that this 1-parameter response model is strongly preferred by BIC over standard 2-parameter NFW and Burkert dark matter halo models in over 90% of the SPARC sample"
- **ADDED:** Cross-validation performance metric: "5-fold cross-validation shows the response model has significantly lower out-of-sample prediction error (mean RMSE = 3.1 km/s) than the NFW model (mean RMSE = 4.9 km/s)"
- **REMOVED:** Cymatics reference (citations to Rossing, Tuan, Bender-Orszag removed from abstract)
- **REMOVED:** Reference to "Appendix D" spectral harmonics discussion
- **EMPHASIS SHIFT:** From "very strong improvement over baryons-only" to "strongly preferred over NFW/Burkert halos"

**Current v5.0.5.7 Abstract (excerpt):**
> "Applied to 175 galaxies from the SPARC database, the one-parameter closure yields very strong improvement over baryons-only for 92% of systems and passes BIC overfitting rejection in 97%. The baryonic Tully--Fisher relation is recovered as an empirical consequence (Spearman r_s = 0.95). A cymatics-inspired extension explores oscillatory signatures..."

**v5.1 Revised Abstract (excerpt):**
> "Applied to 175 galaxies from the SPARC database, this model yields very strong improvement over a baryons-only model for 92% of systems and passes a Bayesian Information Criterion (BIC) overfitting test in 97% of cases. Crucially, we demonstrate that this 1-parameter response model is strongly preferred by BIC over standard 2-parameter NFW and Burkert dark matter halo models in over 90% of the SPARC sample. Further, 5-fold cross-validation shows the response model has significantly lower out-of-sample prediction error (mean RMSE = 3.1 km/s) than the NFW model (mean RMSE = 4.9 km/s)..."

**Integration Point:** Replace existing abstract (lines 206-213 in manuscript_overleaf.tex)

---

### [2] Keywords — Minor Addition
**Type:** Keyword Expansion  
**Size:** +2 keywords  
**Changes:**
- **ADDED:** "Bayesian model comparison"
- **ADDED:** "cross-validation"
- **REMOVED:** None (all previous keywords retained)

**Current v5.0.5.7:**
> galaxy rotation curves, dark matter alternatives, dark matter candidates, dark matter identity, general relativity, gravitation, effective field theory, response-sector stress--energy, boundary-layer physics, SPARC database, falsification criteria

**v5.1:**
> galaxy rotation curves, dark matter alternatives, dark matter candidates, dark matter identity, general relativity, gravitation, effective field theory, response-sector stress--energy, boundary-layer physics, SPARC database, falsification criteria, Bayesian model comparison, cross-validation.

**Integration Point:** Line 219 in manuscript_overleaf.tex (after abstract)

---

### [3] Section 1: Introduction — Concluding Paragraph Revision
**Type:** Wording Revision + Emphasis Shift  
**Size:** ~100 words (final paragraph)  
**Nature of Revision:** Technical Clarification + Forward Reference  

**Current v5.0.5.7 (lines ~458-463):**
> "This paper develops an inverse-GR alternative consistent with the Discussion framing in §9: we retain standard GR on the left-hand side and ask what effective stress--energy must appear on the right-hand side if we do not assume particulate CDM. The organizing equation is G_μν = 8πG(T_bar + T_resp), where T_resp is defined as the effective response sector required by the observed phenomenology. This definition is ontologically agnostic; we do not claim spacetime is literally a fluid or solid, only that it admits an EFT/constitutive response closure."

**v5.1 Revised:**
> "This paper develops an inverse-GR alternative consistent with the Discussion framing in §9: we retain standard GR on the left-hand side and ask what effective stress--energy must appear on the right-hand side if we do not assume particulate CDM. The organizing equation is G_μν = 8πG(T_bar + T_resp), where T_resp is defined as the effective response sector required by the observed phenomenology. **We show that a simple, one-parameter closure for T_resp not only explains galactic rotation curves but does so more efficiently and with greater predictive accuracy than standard two-parameter dark matter halo models.**"

**Rationale:** Sets expectation for BIC/cross-validation results presented in Section 5. More assertive/confident framing.

**Integration Point:** Replace final paragraph of Section 1 (around line 458-463)

---

### [4] Section 5 — MAJOR RESTRUCTURING + NEW CONTENT

#### Current v5.0.5.7 Section 5 Structure:
```
5. Results Across 175 SPARC Galaxies
   5.1 Global Fit Performance
   5.2 Representative Galaxy Diagnostics
   5.3 Emergent Baryonic Tully-Fisher Relation
   5.4 Fitted vs. Robust Amplitude Comparison
   5.5 Mass-to-Light Ratio Sensitivity
   5.6 Oscillatory Signatures and Negative-Q Galaxies
```

#### Proposed v5.1 Section 5 Structure:
```
5. Results Across 175 SPARC Galaxies
   5.1 Model Selection via Bayesian Information Criterion (NEW)
   5.2 Out-of-Sample Predictive Performance (NEW)
   5.3 Mass-to-Light Ratio Sensitivity (MOVED from 5.5)
```

**MAJOR CHANGE:** v5.1 proposes collapsing 6 subsections into 3, with 2 entirely new subsections (5.1, 5.2) focused on statistical comparison.

---

#### [4a] NEW SUBSECTION: 5.1 Model Selection via Bayesian Information Criterion

**Type:** New Subsection (Complete Addition)  
**Size:** ~450 words  
**Content Overview:**
- **Motivation:** Addresses criticism that comparison to "baryons-only" is a strawman; provides rigorous comparison to NFW and Burkert halos
- **Methodology:** BIC comparison across 4 models:
  1. Baryons-only (k=0)
  2. Response Sector (k=1)
  3. NFW Halo (k=2)
  4. Burkert Halo (k=2)
- **Key Results:**
  - Response model: median ΔBIC = -71.3
  - NFW model: median ΔBIC = -54.3
  - Burkert model: median ΔBIC = -57.3
  - Response preferred over NFW in **91%** of galaxies
  - Response strongly preferred (ΔBIC < -2) over NFW in **77%** of galaxies
  - Response preferred over Burkert in **92%** of galaxies

**Full Text Extract (from v5.1):**
> "To address the critical question of whether the response-sector model provides a more compelling description of the data than standard alternatives, we perform a comprehensive model comparison using the Bayesian Information Criterion (BIC). BIC provides a principled way to compare models with different numbers of free parameters, penalizing complexity to avoid overfitting. We compare four models for each of the 175 SPARC galaxies:
> • Baryons-only (k=0): The baseline model with no free parameters (Y_disk fixed at 0.5 M☉/L☉).
> • Response Sector (k=1): The one-parameter (Q) boundary-layer response model.
> • NFW Halo (k=2): A standard two-parameter (M_vir, c) Navarro-Frenk-White dark matter halo added to the baryonic component.
> • Burkert Halo (k=2): A standard two-parameter (ρ_0, r_c) cored Burkert dark matter halo.
> 
> Figure 1 presents the primary results of this analysis. Panel (a) shows the distribution of ΔBIC (the change in BIC relative to the baryons-only model) for the three dark-gravity/dark-matter models. All three models provide a substantial improvement over the baryons-only baseline, with median ΔBIC values far below the threshold of -10, which indicates 'very strong' evidence for the better model. Notably, the 1-parameter response model achieves a median ΔBIC of -71.3, surpassing both the NFW (ΔBIC = -54.3) and Burkert (ΔBIC = -57.3) models.
> 
> Panels (b) and (c) show the direct comparison between the response model and the two halo models. The results are decisive: the response model is preferred over the NFW model (ΔBIC < 0) in 91% of galaxies and strongly preferred (ΔBIC < -2) in 77% of cases. The preference over the Burkert model is similarly strong (92% of cases). This directly addresses a key critique: the response model is not merely better than an obviously failing baseline; it is demonstrably more efficient and provides a better statistical fit than the standard 2-parameter halo models across the vast majority of the SPARC sample."

**Figure Reference:** "Figure 1" — Six-panel comprehensive model comparison figure (referenced but NOT included in DOCX extract)

**Integration Point:** Insert as new Section 5.1, before current "5.1 Global Fit Performance" (which may be demoted or merged)

---

#### [4b] NEW SUBSECTION: 5.2 Out-of-Sample Predictive Performance

**Type:** New Subsection (Complete Addition)  
**Size:** ~200 words  
**Content Overview:**
- **Methodology:** 5-fold cross-validation for each galaxy
- **Metric:** Root-mean-square error (RMSE) on held-out test sets
- **Key Results:**
  - **Response model:** mean RMSE = **3.1 km/s**
  - **NFW model:** mean RMSE = **4.9 km/s**
  - Response model shows **significantly lower variance** in prediction error
- **Interpretation:** Response model captures underlying physics with greater fidelity, not just fitting noise

**Full Text Extract (from v5.1):**
> "To move beyond goodness-of-fit and assess the predictive power of the models, we performed a 5-fold cross-validation for each galaxy, as described in §6.5. This test evaluates how well a model trained on a subset of the data can predict the held-out data points. As shown in Figure 1(d), the response model demonstrates superior out-of-sample predictive accuracy. Its mean root-mean-square error (RMSE) is 3.1 km/s, significantly lower and with smaller variance than the NFW model's mean RMSE of 4.9 km/s. This result closes a critical gap identified in previous versions of this work and provides strong evidence that the response model is not just fitting noise but is capturing the underlying physical relationship with greater fidelity and predictive power than the NFW halo."

**Integration Point:** Insert as new Section 5.2, immediately after new Section 5.1

---

#### [4c] MOVED SUBSECTION: 5.3 Mass-to-Light Ratio Sensitivity

**Type:** Content Reorganization + Minor Additions  
**Current Location:** Section 5.5 (lines 685-688)  
**New Location:** Section 5.3  
**Size:** ~150 words (expanded from ~100 words)

**Current v5.0.5.7 (Section 5.5):**
> "Sweeping Υ_disk across {0.3, 0.4, 0.5, 0.6, 0.7} M_⊙/L_⊙ demonstrates that the response-sector results are robust to photometric systematic uncertainties. While individual galaxy amplitudes shift with Υ_*, the global performance metrics (fraction very strong, BIC pass rate) and the BTFR scaling relation remain stable across the sweep. The median fractional change in Q_est across the Υ_* range is ~15%, small compared to the dynamic range of Q itself (~10³)."

**v5.1 Revision (expanded for Section 5.3):**
> "A potential ambiguity in our BIC calculation is the treatment of the stellar mass-to-light ratio (Υ_*). To address this, we performed a sensitivity analysis by re-running the BIC comparison for the response model across a range of fixed Υ_* values from [0.3 to 0.7].
> 
> Figure 1(e) shows that while the model performance peaks near the baseline value of 0.5, the response model remains strongly preferred over the baryons-only model across the entire range. This demonstrates that our conclusions are robust and not an artifact of a single, fine-tuned Υ_* value."

**Rationale for Move:** Places sensitivity analysis immediately after BIC comparison (5.1) and cross-validation (5.2), forming a coherent statistical validation block before qualitative galaxy diagnostics.

**Integration Point:** Move content from current Section 5.5 to new Section 5.3 position

---

### [5] Section 6.5: Out-of-Sample Cross-Validation — Content Expansion

**Type:** Content Addition + Technical Detail  
**Current Size:** ~50 words (placeholder)  
**New Size:** ~150 words (detailed methodology)

**Current v5.0.5.7 (Section 6.5, line 729-732):**
> "\subsection{Step 5: Out-of-Sample Cross-Validation}
> [Content placeholder - subsection exists but minimal detail]"

**v5.1 Expanded Content:**
> "The decisive test of a model's predictive power is its ability to generalize to unseen data. We use k-fold cross-validation to compare the predictive accuracy of our nested models. For each galaxy, the data is partitioned into 5 folds. The model is trained on 4 folds and tested on the held-out fold, with the process repeated 5 times. The average root-mean-square error (RMSE) on the test sets serves as the metric for out-of-sample performance.
> 
> As reported in §5.2, this test reveals a significant predictive advantage for the 1-parameter response model over the 2-parameter NFW halo model. This result provides strong support for the hypothesis that the intrinsic-response structure is a more fundamental and predictive feature than a fitted dark matter halo."

**Rationale:** Provides methodological grounding for claims made in new Section 5.2. Establishes cross-validation as a formal validation ladder step.

**Integration Point:** Expand existing Section 6.5 (line 729) with detailed methodology

---

### [6] Section 9.4: Strengths of the Current Work — Complete Rewrite

**Type:** Major Revision (Substantial Content Replacement)  
**Current Size:** ~180 words (list of 5 contributions)  
**New Size:** ~120 words (single unified statement)

**Current v5.0.5.7 (Section 9.4, lines 821-838):**
> "The primary contributions of this paper are:
> (i) a mathematical framework (inverse-GR → response-sector closure) that makes the 'alternative to CDM' concept precise within standard GR;
> (ii) systematic testing against 175 galaxies that span ~10⁴ in luminosity;
> (iii) independent confirmation of fitted amplitudes by a robust estimator;
> (iv) explicit falsification criteria stated in advance; and
> (v) a domain-partitioned roadmap that acknowledges what is and is not claimed."

**v5.1 Complete Replacement:**
> "The primary strength of this work is the demonstration that a simple, 1-parameter constitutive closure for an effective stress-energy tensor can describe galactic rotation curves with **higher statistical preference** and **greater predictive accuracy** than standard 2-parameter dark matter halos. The BIC comparison across 175 SPARC galaxies is not ambiguous: the response model is not only better than a baryons-only model, it is substantially better than NFW and Burkert models in the majority of cases. The cross-validation results reinforce this conclusion: the response model generalizes better to unseen data, suggesting it captures more of the true underlying physics. This combination of parsimony (fewer free parameters), statistical preference (lower BIC), and predictive power (lower cross-validation error) makes a compelling case that the response-sector framework should be taken seriously as an empirical alternative to the dark matter particle hypothesis."

**Rationale for Rewrite:** 
- **Emphasis Shift:** From methodological rigor → empirical superiority over standard models
- **Tone Change:** More assertive/confident
- **Focus Narrowing:** Emphasizes BIC and cross-validation as the headline result

**Integration Point:** Replace entire Section 9.4 content (lines 821-838)

---

## REVISIONS TO EXISTING CONTENT

### [R1] Abstract: Cymatics Reference Removal
**Section:** Abstract (lines 206-213)  
**Revision Type:** Content Removal  
**Current Excerpt:**
> "...The baryonic Tully--Fisher relation is recovered as an empirical consequence (Spearman r_s = 0.95). \citep{Rossing1982Chladni, Tuan2014Nodal, BenderOrszag1999} A cymatics-inspired extension explores oscillatory signatures in residuals as eigenmodes of a linearized response operator, providing a spectral taxonomy for response morphologies and predicting higher-harmonic content in galaxies with sharp baryonic gradients (Appendix D)."

**Revised (v5.1):**
> "...The baryonic Tully--Fisher relation is recovered as an empirical consequence (Spearman r_s = 0.95). [END ABSTRACT]"

**Rationale:** De-emphasizes speculative cymatics analogy to focus abstract on rigorous statistical comparison. Appendix D content remains but is not highlighted in abstract.

---

### [R2] Section 1 Introduction: Confidence Boost
**Section:** Introduction final paragraph (lines 458-463)  
**Revision Type:** Wording + Emphasis  
**Nature:** Replace passive descriptor ("ontologically agnostic") with assertive claim ("does so more efficiently")  

**Current:**
> "This definition is ontologically agnostic; we do not claim spacetime is literally a fluid or solid, only that it admits an EFT/constitutive response closure."

**Revised (v5.1):**
> "[Previous sentence retained] We show that a simple, one-parameter closure for T_resp not only explains galactic rotation curves but does so more efficiently and with greater predictive accuracy than standard two-parameter dark matter halo models."

**Rationale:** Converts Introduction from "here's what we're trying" to "here's what we successfully demonstrated."

---

## CONTENT TO PRESERVE (Unchanged in v5.1)

The following sections from v5.0.5.7 are **NOT addressed** in the v5.1 partial update and should be retained as-is:

### Sections 2-4 (Theory, Methods, Data)
- Section 2: From Phenomenology to Effective Source (complete)
- Section 3: Minimal Response-Sector Model Specification (complete)
- Section 4: Data and Pipeline (complete)

### Section 5 Subsections (Partial Retention/Reorganization)
**Sections to KEEP but potentially renumber:**
- Current 5.2 Representative Galaxy Diagnostics → May become 5.4 or merged
- Current 5.3 Emergent BTFR → May become 5.5 or merged  
- Current 5.4 Fitted vs. Robust → May become 5.6 or merged
- Current 5.6 Oscillatory Signatures → Retain but renumber

**Note:** v5.1 does not provide replacement text for these; they should be preserved but renumbered to accommodate new 5.1-5.3.

### Sections 6-9 (Partial Modification)
- **Section 6.1-6.4, 6.6:** Unchanged (retain)
- **Section 6.5:** Expand with v5.1 content
- **Section 7:** Falsification Criteria (unchanged)
- **Section 8:** Lensing and Cosmology (unchanged)
- **Section 9.1-9.3, 9.5-9.10:** Unchanged (retain)
- **Section 9.4:** Replace with v5.1 content

### Sections 10-Appendices
- Section 10: Conclusion (unchanged)
- Appendix A: Symbol Glossary (unchanged)
- Appendix B: Per-Galaxy Summary Table (unchanged)
- Appendix C: Cluster morphology / HFF (unchanged)
- Appendix D: Spectral Harmonics (unchanged, though de-emphasized in abstract)

---

## RECOMMENDED MERGE STRATEGY

### Phase 1: Abstract and Keywords (Low Risk)
**Order:** First edits, foundational tone-setting  
**Tasks:**
1. Replace abstract (lines 206-213) with v5.1 abstract
2. Append "Bayesian model comparison, cross-validation" to keywords (line 219)
3. **Validation:** Compile LaTeX, check for citation issues (Rossing/Tuan/BenderOrszag references may now be orphaned)

**Estimated Time:** 10 minutes  
**Risk Level:** Low (isolated change)

---

### Phase 2: Introduction Confidence Boost (Low Risk)
**Order:** Second edit, builds on abstract revision  
**Tasks:**
1. Replace final paragraph of Section 1 (lines 458-463) with v5.1 assertive framing
2. **Validation:** Ensure forward reference to §5 BIC results is accurate

**Estimated Time:** 5 minutes  
**Risk Level:** Low (single paragraph replacement)

---

### Phase 3: Section 5 Major Restructuring (High Risk)
**Order:** Third edit, most complex change  
**Tasks:**
1. **Renumber existing subsections:**
   - Current 5.1 Global Fit Performance → 5.4 (or merge into new 5.1)
   - Current 5.2 Representative Galaxy Diagnostics → 5.5
   - Current 5.3 Emergent BTFR → 5.6
   - Current 5.4 Fitted vs. Robust → 5.7
   - Current 5.5 Mass-to-Light → 5.3 (move up)
   - Current 5.6 Oscillatory Signatures → 5.8

2. **Insert NEW subsections:**
   - **5.1 Model Selection via BIC** (insert at line ~620)
     - Full text from v5.1 DOCX
     - Add placeholder for Figure 1 (6-panel BIC/cross-validation figure)
     - Note: Figure 1 currently points to conceptual schematic; may need renumbering
   
   - **5.2 Out-of-Sample Predictive Performance** (insert after new 5.1)
     - Full text from v5.1 DOCX
     - Cross-reference to §6.5 for methodology
   
   - **5.3 Mass-to-Light Ratio Sensitivity** (move from current 5.5)
     - Use expanded v5.1 text
     - Cross-reference to Figure 1(e) from new 5.1

3. **Resolve Figure References:**
   - v5.1 references "Figure 1" as a 6-panel comprehensive model comparison figure
   - Current manuscript_overleaf.tex Figure 1 is the conceptual schematic (line 456)
   - **Decision Point:** 
     - Option A: Renumber conceptual schematic as Figure 2, insert new BIC figure as Figure 1
     - Option B: Keep schematic as Figure 1, add BIC figure as Figure 1b or Figure 5A
   - **Recommendation:** Option A (renumber all figures; BIC comparison becomes new lead empirical figure)

4. **Table Management:**
   - Current Section 5.1 has Table 1 (Global fit performance)
   - v5.1 mentions "Figure 1(f): Summary table of key performance metrics"
   - **Decision:** Retain existing Table 1 in renumbered 5.4, add Figure 1(f) inline table in new 5.1

**Estimated Time:** 2-3 hours  
**Risk Level:** High (extensive cross-references, figure renumbering cascade)

**Critical Dependencies:**
- New Figure 1 (6-panel BIC/CV comparison) must be generated or provided
- All figure cross-references in Sections 6-10 must be updated if renumbering occurs

---

### Phase 4: Section 6.5 Cross-Validation Expansion (Medium Risk)
**Order:** Fourth edit, depends on Phase 3  
**Tasks:**
1. Expand Section 6.5 (line 729) with v5.1 detailed methodology
2. Ensure forward reference to Section 5.2 is accurate
3. **Validation:** Check that 5-fold CV description matches reported results

**Estimated Time:** 15 minutes  
**Risk Level:** Medium (methodology-results consistency check required)

---

### Phase 5: Section 9.4 Rewrite (Medium Risk)
**Order:** Fifth edit, final interpretive framing  
**Tasks:**
1. Replace Section 9.4 content (lines 821-838) with v5.1 unified strength statement
2. **Consider:** Whether to retain original 5-point list as a subsection (9.4.1 "Methodological Contributions") and add new text as 9.4.2 ("Empirical Superiority")
   - **Recommendation:** Full replacement (cleaner), but archive original 5-point list in comments for reference

**Estimated Time:** 10 minutes  
**Risk Level:** Medium (interpretive framing; may require peer/collaborator review)

---

### Phase 6: Validation and Version Update (Low Risk)
**Order:** Final phase  
**Tasks:**
1. Update version string in title/footer:
   - Current: "v5.0.5.7"
   - New: "v5.1.0" (major feature increment for BIC/CV addition)
2. Update Zenodo DOI reference if publishing new version
3. Full LaTeX compile and validation:
   - Check all `\ref{}` and `\cite{}` commands
   - Verify figure/table numbering consistency
   - Run spell-check
4. Generate PDF and compare with v5.0.5.7 PDF:
   - Verify no unintended content loss in preserved sections
   - Check figure placement and quality

**Estimated Time:** 30 minutes  
**Risk Level:** Low (mechanical checks)

---

## VERSIONING UPDATE POINTS

When incrementing to v5.1.0, update version strings at:

1. **Line 203** (versioned preprint reference):
   ```latex
   \noindent\textbf{Versioned preprint:} Kitcey, R. D. (2026). \emph{Intrinsic Response Sector as Dark Gravity: A GR-Compatible Candidate Identity for the Cold Dark Matter Role (SPARC-175)} (v5.1.0). Zenodo.\,\href{https://doi.org/10.5281/zenodo.[NEW_DOI]}{doi:10.5281/zenodo.[NEW_DOI]}
   ```

2. **DOCX Source Document:** Update internal version tag if maintained

3. **README.md or VERSION file:** If tracking manuscript versions

---

## INTEGRATION PRIORITY LEVELS

### Critical (Must Have for v5.1.0)
- [ ] Abstract revision (BIC/CV emphasis)
- [ ] New Section 5.1: BIC Model Comparison
- [ ] New Section 5.2: Cross-Validation Performance
- [ ] Section 9.4 rewrite (strengths)
- [ ] Version string update to v5.1.0

### High Priority (Should Have)
- [ ] Keywords expansion
- [ ] Introduction confidence boost
- [ ] Section 6.5 cross-validation detail
- [ ] Section 5.3 mass-to-light sensitivity (moved & expanded)
- [ ] Figure 1 six-panel BIC figure generation/insertion

### Medium Priority (Nice to Have)
- [ ] Section 5 subsection renumbering (for logical flow)
- [ ] Figure renumbering cascade (if new Figure 1 inserted)
- [ ] Consolidate overlapping content between old 5.1 and new 5.1

### Low Priority (Optional Polish)
- [ ] Archive original Section 9.4 in comments
- [ ] Add inline commentary on cymatics de-emphasis decision
- [ ] Generate supplementary material document for removed cymatics abstract content

---

## POTENTIAL CONFLICTS AND RESOLUTIONS

### Conflict 1: Figure 1 Numbering
**Issue:** v5.1 references "Figure 1" as a 6-panel BIC comparison. Current manuscript Figure 1 is the conceptual response-sector schematic.

**Resolution Options:**
- **Option A (Recommended):** Renumber all figures; BIC figure becomes new Figure 1, schematic becomes Figure 2. Update all cross-references.
- **Option B:** Keep schematic as Figure 1, insert BIC figure as Figure 1b or place later (Figure 5).
- **Option C:** Create a "Figure S1" supplementary figure for BIC comparison (less desirable—buries key result).

**Recommendation:** Option A. The BIC comparison is now the headline empirical result and deserves Figure 1 placement. The conceptual schematic can effectively introduce the Introduction section as Figure 2.

### Conflict 2: Section 5 Content Overlap
**Issue:** Current Section 5.1 "Global Fit Performance" reports 92% very strong improvement and 97% BIC pass rate. New Section 5.1 "BIC Model Comparison" reports the same statistics but in context of NFW/Burkert comparison.

**Resolution:**
- **Merge Approach:** Integrate Table 1 from current 5.1 into new 5.1 as comprehensive reporting.
- **Move Current 5.1:** Demote current 5.1 content to a brief paragraph in new 5.1 or fold into Section 5.2 Representative Diagnostics.

**Recommendation:** Merge — new 5.1 subsumes previous 5.1 content with expanded context.

### Conflict 3: Cymatics De-Emphasis
**Issue:** v5.1 removes cymatics reference from abstract, but Appendix D and Section 5.6 (Oscillatory Signatures) remain in manuscript.

**Resolution:**
- **Keep Appendix D and Section 5.6 unchanged** (they provide technical depth for interested readers).
- **Rationale:** Abstract is for broad audience; removing speculative analogy from abstract doesn't require removing technical detail from body/appendices.
- **Note for reviewers:** If a reviewer flags inconsistency, add brief transition in Section 5 intro: "Beyond statistical comparison, we explore oscillatory features in residuals (§5.8) with a cymatics-inspired eigenmode analysis detailed in Appendix D."

**Recommendation:** No conflict—accept de-emphasis in abstract while preserving technical content.

### Conflict 4: Introduction Final Paragraph Duplication
**Issue:** v5.1 adds assertive claim to Introduction that duplicates Abstract's new content.

**Resolution:**
- **Accept Duplication:** Abstract and Introduction serve different functions; reinforcement is acceptable.
- **Alternative:** If editors flag redundancy, shorten Introduction addition to: "We demonstrate this closure achieves both parsimony and predictive superiority (§5)."

**Recommendation:** Accept duplication — strengthens narrative coherence.

---

## MISSING ELEMENTS REQUIRING ATTENTION

### 1. Figure 1: Six-Panel BIC/Cross-Validation Figure
**Status:** Referenced in v5.1 text but NOT included in DOCX extract  
**Description (from v5.1 text):**
- **(a)** Distribution of ΔBIC for three models vs. baryons-only
- **(b)** Response vs. NFW direct comparison histogram
- **(c)** Response vs. Burkert direct comparison histogram
- **(d)** 5-fold cross-validation RMSE comparison (box plots or violin plots)
- **(e)** Mass-to-light ratio sensitivity (BIC vs. Υ_* sweep)
- **(f)** Summary table of key metrics

**Action Required:**
- **Generate figure from analysis pipeline** OR
- **Request figure file from collaborator/author** OR
- **Create placeholder and mark as TODO for figure generation**

**Priority:** **CRITICAL** — Figure 1 is central to new Section 5.1-5.2 narrative.

### 2. NFW and Burkert Halo Fit Results
**Status:** v5.1 references BIC comparison to NFW/Burkert but does NOT include fit methodology details  
**Missing Content:**
- NFW parameterization (M_vir, c) and fitting procedure
- Burkert parameterization (ρ_0, r_c) and fitting procedure
- BIC calculation formula and implementation

**Action Required:**
- **Check analysis pipeline scripts** for NFW/Burkert fitting code
- **If missing:** Implement fit routines and document in Section 4 (Data and Pipeline) or Section 5.1
- **Consider:** Adding Appendix E "Halo Model Comparison Methodology" with detailed fit specifications

**Priority:** **HIGH** — Methodology must be documented for reproducibility.

### 3. Cross-Validation Implementation Details
**Status:** v5.1 briefly describes 5-fold CV but lacks:
- Data partitioning strategy (random? stratified by galaxy type?)
- Fold assignments (fixed seeds? galaxy-specific?)
- Model retraining procedure (full χ² minimization per fold?)

**Action Required:**
- **Document CV implementation** in Section 6.5 (expanded in v5.1 but still brief)
- **Consider:** Add code availability statement or GitHub link

**Priority:** **MEDIUM** — Sufficient for v5.1.0 release, but should be expanded for journal submission.

### 4. Updated Per-Galaxy Table (Appendix B)
**Status:** If BIC and CV results are galaxy-specific, Appendix B may need new columns  
**Current Appendix B Columns:** Galaxy name, Q_est, Q_best, ΔBIC (baryons-only), other metrics

**Potential New Columns:**
- ΔBIC_NFW (response vs. NFW)
- ΔBIC_Burkert (response vs. Burkert)
- RMSE_CV (cross-validation error)

**Action Required:**
- **Regenerate Appendix B table** with expanded metrics OR
- **Add supplementary table** (Table S1) with BIC/CV comparison details

**Priority:** **LOW** — Can be deferred to post-v5.1.0 update if table generation is time-intensive.

---

## CITATION AUDIT

### Citations Potentially Removed (from Abstract)
- **Rossing1982Chladni** (cymatics reference)
- **Tuan2014Nodal** (cymatics reference)
- **BenderOrszag1999** (perturbation methods)

**Action Required:**
- Check if these citations appear elsewhere in manuscript body/appendices
- If orphaned, remove from references.bib (or keep with "unused" comment)

### Citations Potentially Added
- **NFW halo model:** Navarro, Frenk, & White (1996, 1997)
- **Burkert halo model:** Burkert (1995)
- **BIC methodology:** Schwarz (1978) or Kass & Raftery (1995)
- **Cross-validation:** Stone (1974) or Kohavi (1995)

**Action Required:**
- Add missing citations to references.bib
- Insert `\citep{}` commands in new Section 5.1-5.2 text

---

## FINAL INTEGRATION CHECKLIST

### Pre-Integration
- [ ] Backup current manuscript_overleaf.tex as manuscript_overleaf_v5.0.5.7_backup.tex
- [ ] Backup references.bib
- [ ] Commit current state to version control (git)

### Phase 1: Abstract & Keywords
- [ ] Replace abstract (lines 206-213)
- [ ] Remove cymatics sentence and citations
- [ ] Add BIC/CV sentences
- [ ] Append keywords (line 219)
- [ ] Compile LaTeX → check for errors

### Phase 2: Introduction
- [ ] Replace final paragraph (lines 458-463)
- [ ] Add assertive framing
- [ ] Compile LaTeX → check for errors

### Phase 3: Section 5 Restructuring
- [ ] Insert new Section 5.1 (BIC Model Comparison)
  - [ ] Add full v5.1 text (~450 words)
  - [ ] Add Figure 1 reference (placeholder if figure not ready)
  - [ ] Add NFW/Burkert citations
  - [ ] Add BIC methodology citation
- [ ] Insert new Section 5.2 (Cross-Validation)
  - [ ] Add full v5.1 text (~200 words)
  - [ ] Cross-reference to §6.5
  - [ ] Add cross-validation citations
- [ ] Move Section 5.5 → 5.3 (Mass-to-Light)
  - [ ] Replace text with expanded v5.1 version
  - [ ] Update internal figure reference to Figure 1(e)
- [ ] Renumber remaining subsections:
  - [ ] Current 5.1 → 5.4 (or merge into 5.1)
  - [ ] Current 5.2 → 5.5
  - [ ] Current 5.3 → 5.6
  - [ ] Current 5.4 → 5.7
  - [ ] Current 5.6 → 5.8
- [ ] Resolve Figure 1 conflict (renumber schematic if needed)
- [ ] Update all `\ref{results-...}` and `\hyperref[...]` labels
- [ ] Compile LaTeX → check for errors

### Phase 4: Section 6.5
- [ ] Expand Section 6.5 content (line 729)
- [ ] Add v5.1 CV methodology text
- [ ] Cross-reference to new Section 5.2
- [ ] Compile LaTeX → check for errors

### Phase 5: Section 9.4
- [ ] Replace Section 9.4 content (lines 821-838)
- [ ] (Optional) Archive original 5-point list in comments
- [ ] Compile LaTeX → check for errors

### Phase 6: Validation
- [ ] Update version string to v5.1.0 (line 203)
- [ ] Update Zenodo DOI if applicable
- [ ] Full LaTeX compile → resolve all errors/warnings
- [ ] Generate PDF
- [ ] Visual comparison with v5.0.5.7 PDF (check figure placement, no content loss)
- [ ] Spell-check
- [ ] Citation audit (verify all \citep{} commands resolve)
- [ ] Cross-reference audit (verify all \ref{} and \hyperref commands resolve)

### Post-Integration
- [ ] Commit v5.1.0 to version control
- [ ] Tag release: `git tag v5.1.0`
- [ ] Generate comparison document (v5.0.5.7 vs v5.1.0 diff)
- [ ] Update README/changelog
- [ ] (If applicable) Upload to Zenodo/arXiv

---

## TIMELINE ESTIMATE

| Phase | Task | Estimated Time | Priority |
|-------|------|----------------|----------|
| 1 | Abstract & Keywords | 10 min | Critical |
| 2 | Introduction | 5 min | Critical |
| 3 | Section 5 Restructuring | 2-3 hours | Critical |
| 4 | Section 6.5 Expansion | 15 min | High |
| 5 | Section 9.4 Rewrite | 10 min | Critical |
| 6 | Validation & Version Update | 30 min | Critical |
| **TOTAL** | **~3.5-4.5 hours** | **N/A** | **N/A** |

**Note:** Timeline assumes Figure 1 (BIC six-panel) is provided or generation takes <30 min. If figure requires extensive development/debugging, add 1-3 hours.

---

## COLLABORATOR REVIEW RECOMMENDATIONS

### Items Requiring PI/Lead Author Approval
1. **Section 9.4 complete rewrite** (changes interpretive framing; may benefit from co-author input)
2. **Figure 1 renumbering decision** (affects entire manuscript visual narrative)
3. **Cymatics de-emphasis** (confirm Appendix D remains valued despite abstract removal)
4. **Version increment to v5.1.0** (major feature addition; confirm changelog)

### Items Requiring Technical Validation
1. **BIC calculation methodology** (ensure NFW/Burkert fits are statistically sound)
2. **Cross-validation implementation** (ensure fold partitioning is appropriate for SPARC sample)
3. **RMSE comparison** (verify 3.1 km/s vs 4.9 km/s is significant given uncertainties)

---

## RISK ASSESSMENT SUMMARY

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Figure 1 unavailable** | Medium | High | Create placeholder; defer full integration to v5.1.1 |
| **NFW/Burkert fit methodology undocumented** | Medium | High | Add Appendix E or §5.1 subsection with fit details |
| **Cross-reference cascade errors** | High | Medium | Automated `\ref` audit script; careful manual review |
| **Version control merge conflicts** | Low | Medium | Work on clean branch; comprehensive backup before merge |
| **Reviewers flag over-assertive tone** | Medium | Low | Retain v5.0.5.7 conservative language as fallback in comments |

---

## CONCLUSION: RECOMMENDED INTEGRATION APPROACH

**Recommended Path:** **Incremental Integration with Figure Gate**

1. **Immediate (Phase 1-2):** Abstract, keywords, introduction (low-risk; <20 min)
2. **Figure Gate Decision Point:**
   - **IF Figure 1 available:** Proceed with full Phase 3 restructuring
   - **IF Figure 1 unavailable:** Implement "v5.1.0-beta" with placeholder; defer full release until figure ready
3. **Post-Figure (Phase 3-6):** Complete Section 5 restructuring, validation, release v5.1.0

**Rationale:** The BIC/CV narrative is the headline contribution of v5.1. Releasing without Figure 1 undermines the update's impact. Better to stage the release than to publish incomplete.

**Alternative (Aggressive Timeline):** If external deadline (conference, journal resubmission) requires immediate v5.1.0 release, proceed with full text integration and use a **simplified Figure 1** (e.g., 3-panel: ΔBIC distribution, Response vs. NFW, CV RMSE comparison) generated quickly from analysis pipeline. Defer 6-panel "publication-quality" figure to v5.1.1 patch.

---

**END OF REPORT**

*Generated by automated extraction pipeline: extract_docx_compare.py*  
*Report Format: Markdown*  
*Target Audience: Technical Editor, LaTeX Manuscript Maintainer*
