# Rubin Data Access Science Case and Audit

## Purpose
This document is intended for Rubin Observatory / Rubin Science Platform (RSP) review. It explains:
1. What science is being pursued with Rubin data access.
2. Why Rubin data are necessary for a falsifiable test.
3. How the current notebook pipeline enforces scientific honesty.
4. Current audit findings, residual risks, and mitigation actions.

## Science Program Summary
The program is a falsification-first test of an intrinsic response sector (IRS) framework, with later extension to a KSL variability channel.

Primary scientific objective:
- Test whether an IRS-derived proxy shows reproducible, non-random relationships with host photometric structure in Rubin data.

Secondary objective:
- Transfer-validation against SPARC-derived priors before scaling to fully Rubin-native samples.

Planned progression:
- Gate 0.5: SPARC to Rubin transfer test.
- Gate 1: Host-photometry trend detection.
- Gate 2: Adversarial null and bootstrap robustness.
- Gate 3: Weak-lensing extension.
- Gate 4: AGN variability channel.

## Why Rubin Data Access Is Required
Rubin data provide the survey scale, homogeneous photometric quality, and cadence needed for stringent falsification rather than anecdotal fitting.

Rubin access is needed to:
- Query large, uniform samples over controlled redshift ranges.
- Perform cross-system transfer checks between known SPARC targets and Rubin-observed objects.
- Execute robust null tests and bootstrap inference on sufficiently large N.
- Extend from photometric trends to weak-lensing and time-domain variability channels.

Without Rubin-level data volume and consistency, key falsifier tests become underpowered or biased by heterogeneous multi-survey assembly.

## Testable Hypotheses and Falsifiers
Pre-registered hypotheses currently encoded in `rubin_rsp/out/preregistered_plan.json`:
- H1: `spearman_rho(irs_proxy, compactness_proxy)` exceeds a threshold in validation data.
- H2: Label-shuffle null correlations remain near zero.

Explicit falsifier posture:
- Failure of H1 in validation split is a stop condition.
- Failure of H2 robustness is a stop condition.
- Insufficient sample size is a stop condition.

The pipeline is designed to fail closed when provenance is not live.

## Data Use Plan on Rubin (Operational)
Notebook under operation:
- `rubin_rsp/RSP_IRS_KSL_Gated_Roadmap.ipynb`

Current configured table targets:
- Photometry: `dr1.object`
- Shear/lensing planning: `dr1.shape_measurements`
- Time-domain AGN planning: `dr1.source`

Representative query patterns:
- Photometry features by redshift and quality constraints.
- Cone-match overlap between uploaded SPARC coordinates and Rubin objects.
- Shear and time-domain feature extraction in later gates.

These are scientific analysis queries, not bulk exfiltration workflows.

## Integrity Controls Already Implemented
As implemented in notebook and operator manual:
- Strict falsifier mode defaults on.
- Synthetic data disallowed by default.
- Gate 0.5 synthetic overlap generation blocked in strict mode.
- Gate 0.5 pass blocked unless overlap provenance is `live_tap` in current run.
- Gate 1/2 summary pass reporting blocked unless provenance is `live_tap`.
- Canonical pathing used for output and data directories.

Operational manual:
- `rubin_rsp/VERA_RUBIN_OPERATORS_MANUAL.md`

## Robust Audit Findings
Audit scope:
- Notebook structure and execution state.
- Manual consistency with implementation.
- Output artifact consistency in `rubin_rsp/out`.

### Findings (ordered by severity)
1. Medium: Artifact-level readiness does not by itself imply falsifier-grade readiness.
- File: `rubin_rsp/out/run_summary.json`
- Observation: artifact readiness can be true while `falsifier_grade` is false.
- Risk: operational confusion between "files exist" and "science-grade evidence".
- Current containment: summary explicitly reports `falsifier_grade` and data provenance.
- Recommended action: treat `falsifier_grade=true` as the only readiness criterion for scientific claims.

2. Low: Gate 3 and Gate 4 are still planning artifacts, not executed science outputs.
- Files: `rubin_rsp/out/gate3_plan.json`, `rubin_rsp/out/gate4_plan.json`
- Observation: status is `not_started`.
- Risk: scope misunderstanding if presented as completed analyses.
- Recommended action: represent these as planned extensions contingent on earlier live gate passes.

### Remediated Integrity Gap
- Files: `rubin_rsp/out/gate1_metrics.json`, `rubin_rsp/out/gate2_robustness.json`
- Resolution: legacy pass-style artifacts were replaced by strict fail-closed records that include `data_mode`, `falsifier_grade`, `integrity_status`, and explicit reasons.
- Result: Gate 1/2 standalone artifacts now align with `run_summary.json` and cannot be misread as live falsifier-grade passes.

### Audit Conclusion
The current framework is scientifically defensible for Rubin access because it is explicitly falsification-oriented, provenance-aware, and hardened against placeholder pass claims. The key remaining requirement is live execution (`dry_run=false`) before reporting empirical support.

## Current State Snapshot (from outputs)
- `rubin_rsp/out/run_summary.json` reports:
  - `dry_run: true`
  - `strict_falsifier_mode: true`
  - `falsifier_grade: false`
  - effective gate passes: false
- `rubin_rsp/out/gate05_overlap_generation_report.json` reports dry-run blocked synthetic overlap in strict mode.
- `rubin_rsp/out/gate05_transfer_metrics.json` correctly reports gate fail in strict mode without live overlap.

This is the correct and honest state prior to Rubin live access execution.

## Scientific Defense for Rubin Access Request
This project is not requesting Rubin access to confirm a favored model by tuning. It requests access to attempt falsification through:
- pre-registered hypotheses,
- explicit stop conditions,
- strict provenance controls,
- and multi-stage adversarial testing (transfer, null, bootstrap, then lensing/time-domain).

Rubin data are central because the falsifier tests require both scale and uniformity. The requested access directly supports robust hypothesis testing, not exploratory cherry-picking.

## Required Next Actions Before Claiming Empirical Support
1. Set `cfg.dry_run = False` in the notebook.
2. Run Gate 0.5 to Gate 2 on live TAP data.
3. Confirm output provenance fields indicate `live_tap`.
4. Confirm `run_summary.json` has `falsifier_grade = true` before any claim of support.
5. Verify Gate 1 and Gate 2 provenance fields remain `live_tap` after live reruns.

## Files Referenced in this Audit
- `rubin_rsp/RSP_IRS_KSL_Gated_Roadmap.ipynb`
- `rubin_rsp/VERA_RUBIN_OPERATORS_MANUAL.md`
- `rubin_rsp/out/preregistered_plan.json`
- `rubin_rsp/out/gate05_overlap_generation_report.json`
- `rubin_rsp/out/gate05_transfer_metrics.json`
- `rubin_rsp/out/gate1_metrics.json`
- `rubin_rsp/out/gate2_robustness.json`
- `rubin_rsp/out/gate3_plan.json`
- `rubin_rsp/out/gate4_plan.json`
- `rubin_rsp/out/run_summary.json`
