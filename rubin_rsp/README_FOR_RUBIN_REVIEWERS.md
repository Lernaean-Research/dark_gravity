# Quick Reference: How to Review This Rubin Access Request

This document is a one-page executive summary for Rubin TAC/data-access reviewers.

## The Science Question

**What we're trying to learn:** Whether the same uniform galaxy-scale phenomenology currently fit by Lambda CDM can be explained as an intrinsic spacetime response (IRS) rather than as an independent cold dark matter component.

**Specifically:** This program does not assume first-order phenomenology must differ. IRS is being evaluated as an elegant candidate fit to the current CDM-consistent observational baseline, but with alternate causality. The key question is therefore causal interpretation under matched phenomenology, not curve-shape novelty by itself.

**Why this matters:** If two frameworks fit similar observables, the decision shifts to cross-domain adjudication: consistency across channels, parameter economy, cosmological compatibility, and external evidence (including direct-detection status). Rubin is used to tighten this adjudication by reducing uncertainty and systematics in the galaxy-scale evidence layer.

## Why Rubin Is The Only Tool That Can Answer This

- **Scale:** Rubin's 500k+ galaxies let us split data into discovery and validation sets large enough to be meaningful (70k / 30k). SPARC's 200 galaxies cannot. Small samples drown out real signals in statistical noise.
- **Homogeneity:** One photometric pipeline across all galaxies eliminates the confusion of multi-survey stitching. SPARC mixes five surveys; we cannot tell real physics from calibration artifacts.
- **Breadth:** Rubin gives us photometry, weak lensing, and time-domain variability in one survey. This lets us test IRS predictions on three independent physics channels, not just photometry alone.

**Bottom line:** Without Rubin, causal adjudication remains statistically weak and ambiguous. With Rubin, it becomes high-leverage and auditable.

## Our Plan: Progressive Gates With Explicit Stopping Rules

We test the IRS hypothesis across five sequential gates, each with a clear pass/fail criterion:

| Gate          | Test                | What We're Asking                                            | Fails If...                                                          |
| ------------- | ------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------- |
| **0.5** | Transfer validation | Can we translate the IRS metric from SPARC to Rubin?         | Correlation drops below 0.40 or sign flips                           |
| **1**   | Core hypothesis     | Does compactness correlate with IRS response at Rubin scale? | Validation correlation < 0.15 or sign mismatch                       |
| **2**   | Robustness          | Is the signal real or noise from random label shuffling?     | Null correlations too strong or bootstrap CI includes zero           |
| **3**   | Lensing channel     | Do weak-lensing profiles match IRS predictions?              | No directional consistency across redshift bins                      |
| **4**   | Variability channel | Are high-response hosts enriched in AGN variability?         | No significant enrichment or randomization test shows it's by chance |

**Critical rule:** If any gate fails, we stop. We do not tune thresholds to make it pass. We publish the null result. This is falsification-first, not confirmation-seeking.

---

## What You're Reviewing

A **research program with locked-in thresholds and staged decision points** designed to test whether IRS framework predictions match Rubin observations. We are requesting access to execute Gates 0.5–2 on live Rubin data (photometry only, fast). Gates 3–4 are contingent on Gates 1–2 passing.

## Objective Applicability Audit (IRS Objectives vs Rubin Capability)

Grading scale:

- `A` = excellent fit (Rubin is a primary enabler)
- `B` = strong fit with caveats
- `C` = partial fit (Rubin contributes but cannot resolve alone)
- `D` = weak fit for this objective

| Objective                                                                                              | Rubin Capability Leveraged                                           | Grade        | Rationale                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Primary objective: reproducible IRS-host correlation with out-of-sample validation and null robustness | Scale + homogeneous photometry + reproducible catalog access         | **A**  | Rubin directly solves small-N and cross-survey heterogeneity limits that otherwise undermine stable validation and adversarial null testing.      |
| Secondary objective: SPARC-to-Rubin transfer before scaling                                            | Cross-survey overlap + coordinate consistency                        | **B**  | Rubin supports transfer checks, but overlap quality depends partly on external SPARC-Rubin cross-matching and not Rubin alone.                    |
| Gate 0.5 transfer validation                                                                           | Overlap cardinality + matching fidelity                              | **B-** | Strong as a fail-fast control, but sensitivity is dominated by overlap/sample mapping constraints rather than Rubin depth.                        |
| Gate 1 core host-photometry trend                                                                      | High-N photometry, quality masks, uniform calibrations               | **A**  | This is Rubin's strongest regime: large uniform samples allow decisive discovery/validation splits with reduced systematic ambiguity.             |
| Gate 2 adversarial robustness (shuffle + bootstrap)                                                    | Large N + stable measurement pipeline                                | **A-** | Rubin makes robustness testing statistically powerful; remaining limitation is inferential scope (robustness does not by itself prove ontology).  |
| Gate 3 weak-lensing extension                                                                          | Shear products + redshift quality + binning depth                    | **B+** | Rubin is well-suited for independent gravity-channel tests, but interpretation depends on careful shear calibration and selection controls.       |
| Gate 4 AGN variability extension                                                                       | Time-domain cadence + host cross-linking                             | **B**  | Rubin's cadence and depth are strong, but AGN selection and host-association uncertainties can dilute clean causal interpretation.                |
| Core causal objective: IRS vs Lambda CDM adjudication under matched phenomenology                      | Cross-channel consistency with low-systematics galaxy-scale evidence | **C+** | Rubin can strongly tighten galaxy-scale adjudication, but cannot alone resolve final ontology if both frameworks match first-order phenomenology. |
| Integrity objective: falsification-grade, no post-hoc tuning                                           | Preregistration lock + provenance gating + fail-closed logic         | **A**  | Current architecture is audit-strong: lock hash, explicit provenance, and conjunction-based eligibility rules are reviewer-verifiable.            |
| TAC suitability objective: constrained and responsible data access                                     | Staged request scope + minimal query/export policy                   | **A-** | The access plan is appropriately scoped and phased; maintain the same minimization discipline for Gate 3/4 requests.                              |

**Sanity-check conclusion:** Rubin is an excellent platform for high-quality galaxy-scale adjudication of IRS objectives (especially Gates 1–2), but it is one layer of evidence. Final causal preference between IRS and Lambda CDM remains a cross-domain inference requiring consistency with cosmological, cluster-scale, and laboratory constraints.

---

## Why We Lock Thresholds Before Running Analysis

**The problem:** Researchers often test many hypotheses and publish the ones that "work." This inflates false-positive rates. A real effect that should appear 5% of the time by chance can appear 50% after tuning.

**Our solution:** We lock all thresholds in a preregistration artifact *before* loading any real data. A cryptographic hash ensures the lock is auditable. If we change a threshold later, the hash no longer matches—and the mismatch is detectible.

**Result:** Reviewers can verify we did not tune thresholds after seeing results.

## How to Verify Integrity in 3 Steps

### Step 1: Check Claim Eligibility

- Open `run_summary.json` (generated after running the notebook on live data).
- Verify:
  - `dry_run = false` (we used real data, not plumbing checks)
  - `strict_falsifier_mode = true` (we enforced real-data requirements)
  - `falsifier_grade = true` (all gate passes are empirical, not synthetic)
  - All required gate passes are `true`
- **If any is false:** The result is not claimed as empirical evidence.

### Step 2: Verify Preregistration Lock

- Read `preregistered_plan.json`: note the hypotheses and thresholds.
  - H1: Validation correlation ≥ 0.15
  - H2: Null shuffle effect ≤ 0.05
  - Stop conditions: specific N cutoffs, sign-consistency rules
- Read `access_request_gameplan.json`: find the preregistration lock hash.
- **If the hash does not match a recomputation of current thresholds:** Thresholds were changed after gate evaluation (fraud indicator).

### Step 3: Confirm Data Provenance

- In each gate artifact (`gate05_transfer_metrics.json`, `gate1_metrics.json`, `gate2_robustness.json`), verify:
  - `data_mode = "live_tap"` (not `"synthetic"` or `"none"`)
  - `falsifier_grade = true`
  - Sample sizes match preregistered minimums
- **If any gate shows `data_mode != "live_tap"`:** That gate's result is not claimed for empirical support.

---

## Reference Materials

| Document                       | Location                                       | Use To...                                                                   |
| ------------------------------ | ---------------------------------------------- | --------------------------------------------------------------------------- |
| **Scientific case**      | Notebook Cell 1                                | Understand what question we're answering and why Rubin matters              |
| **Gate mechanics**       | Notebook Cell 2                                | See pass/fail criteria and mechanistic rationale for each threshold         |
| **Integrity controls**   | Notebook Cell 3                                | Understand how provenance gating and fail-closed logic prevent false claims |
| **Preregistration**      | `rubin_rsp/out/preregistered_plan.json`      | Verify thresholds were locked before analysis                               |
| **Gameplan**             | `rubin_rsp/out/access_request_gameplan.json` | Review data-access scope and governance rules                               |
| **Gate results**         | `rubin_rsp/out/gate*.json`                   | Inspect individual gate pass/fail and effect sizes                          |
| **Overall status**       | `rubin_rsp/out/run_summary.json`             | Determine claim eligibility at a glance                                     |
| **Operators manual**     | `rubin_rsp/VERA_RUBIN_OPERATORS_MANUAL.md`   | Step-by-step guide to running and interpreting the notebook                 |
| **Science case + audit** | `rubin_rsp/RUBIN_SCIENCE_CASE_AND_AUDIT.md`  | Author's own robust audit of implementation, risks, and mitigations         |

---

## Expected Artifacts After Live Execution

Once the author runs the notebook with `cfg.dry_run = False` on live Rubin TAP:

- `rubin_rsp/out/gate05_transfer_metrics.json` → `data_mode: live_tap`, `n_overlap` ≥ 20, `rho` ≥ 0.40 (or fails).
- `rubin_rsp/out/gate1_metrics.json` → `data_mode: live_tap`, `n_total` ≥ 5000, `rho_validation` ≥ 0.15 (or fails).
- `rubin_rsp/out/gate2_robustness.json` → `data_mode: live_tap`, `mean_shuffle_rho` abs ≤ 0.05 (or fails).
- `rubin_rsp/out/run_summary.json` → `falsifier_grade: true` iff all gates pass with live data.

If any gate fails, the program stops. Author must revise model assumptions and rerun. The failed run is retained in the record.

## Red Flags (What Should Concern)

- [ ] `falsifier_grade = true` but `dry_run = true` → Impossible state; reject submission.
- [ ] `falsifier_grade = false` but author claims empirical support anyway → Fraud signal.
- [ ] `data_mode = synthetic` in gate artifacts → Placeholder data labeled as real.
- [ ] Preregistration lock hash does not match recomputation → Thresholds changed after evaluation.
- [ ] Gate 1 failed but Gate 3/4 were still executed → Protocol violation.

## Green Lights (What Should Reassure)

- ✓ Preregistration lock hash in gameplan matches a recomputation of current thresholds.
- ✓ All gate artifacts carry `data_mode: live_tap`.
- ✓ `run_summary.json` reports `falsifier_grade: true` only if all gates pass on live data AND `dry_run = false`.
- ✓ Author has pre-written an audit document (`RUBIN_SCIENCE_CASE_AND_AUDIT.md`) acknowledging residual risks and mitigations.
- ✓ Any negative gate outcome is retained in output record and honestly reported.

## Questions to Ask the Author

1. **Why these specific thresholds?** (Point them to Section 3 of Cell 1: each threshold has a power/error-rate rationale.)
2. **What happens if Gate 1 passes but Gate 2 fails?** (Program stops; model is revised before any public claim. See Appendix A.)
3. **Can I audit the preregistration after the fact?** (Yes. The lock hash is immutable unless thresholds change. Mismatches are detected automatically.)
4. **Why three gates instead of one big test?** (Early stopping saves resources; each gate tests a different failure mode. See Section 5 of Cell 1.)

## Final Recommendation Template

**Approve data access if:**

- [ ] Preregistration lock hash is verifiable.
- [ ] Query scope is minimal (no bulk exports).
- [ ] Author acknowledges all gate failures are stopping conditions.
- [ ] All deliverable artifacts are present and describe data provenance explicitly.

**Conditional approval if:**

- [ ] Author agrees to preregister any post-hoc modifications and rerun from scratch.
- [ ] Author commits to publishing gate failures as valid outcomes.

**Reject if:**

- [ ] Author claims empirical support while `falsifier_grade = false`.
- [ ] Preregistration lock hash is unverifiable or post-hoc modifications are evident.
- [ ] Data minimization scope is violated (bulk exports, exploratory queries).

---

**Questions?** See `rubin_rsp/VERA_RUBIN_OPERATORS_MANUAL.md` for operational details or `rubin_rsp/RUBIN_SCIENCE_CASE_AND_AUDIT.md` for scientific rationale and audit findings.
