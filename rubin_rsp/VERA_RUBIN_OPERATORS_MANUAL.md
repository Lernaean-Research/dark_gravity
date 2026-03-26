# Vera Rubin RSP Operators Manual

## Document Purpose
This manual describes how to operate `rubin_rsp/RSP_IRS_KSL_Gated_Roadmap.ipynb` on the Vera Rubin Science Platform (RSP) in a falsification-first, audit-ready way.

Primary goals:
- Run transfer and photometry gates with explicit provenance.
- Prevent placeholder or synthetic outputs from being misreported as scientific passes.
- Produce outputs that are applicable to falsifiers and reproducible by independent operators.

## Scope
This manual covers:
- Gate 0 through Gate 4 notebook operations.
- Strict falsifier mode behavior.
- Operational run order.
- Artifact interpretation.
- Troubleshooting and data-integrity controls.

This manual does not define new theory or alter gate criteria. It explains how to execute the existing notebook safely and honestly.

## System Under Operation
- Notebook: `rubin_rsp/RSP_IRS_KSL_Gated_Roadmap.ipynb`
- Canonical output directory: `rubin_rsp/out`
- Canonical data directory: `rubin_rsp/data`
- Independent SPARC coordinate reference: `rubin_rsp/data/sparc175_reference_independent.csv`

## Design Intent (Operationally)
The notebook is a staged gate pipeline:
1. Configure environment and reproducibility controls.
2. Validate SPARC-to-Rubin transfer behavior (Gate 0.5).
3. Validate host-photometry signal and robustness (Gate 1 and Gate 2).
4. Prepare weak-lensing and AGN follow-on channels (Gate 3 and Gate 4 plans).

The notebook is designed so a failed gate is a stop condition. No gate should be treated as passed if provenance is synthetic or ambiguous.

## Falsifier-Grade Policy
The notebook now enforces strict behavior by default:
- `strict_falsifier_mode = True`
- `allow_synthetic_data = False`
- `dry_run = True` by default for plumbing only

Consequences:
- Synthetic overlap is blocked for Gate 0.5 in strict mode.
- Gate 0.5 pass is blocked unless overlap provenance is `live_tap` from the current run.
- Gate 1 and Gate 2 pass claims are blocked unless data provenance is `live_tap`.
- Summary pass fields are forced to `False` unless provenance is live and run mode is non-dry.

If you need plumbing-only checks, you may enable synthetic mode intentionally, but those runs are not falsifier-grade and must never be represented as scientific confirmation.

## Preconditions for Live Rubin Operation
Before live execution:
1. Rubin account and data authorization are active.
2. TAP endpoint is reachable from runtime.
3. DR table names are confirmed in current schema.
4. Required Python packages are available (`pyvo`, `astropy`, `astroquery`, `pandas`, `numpy`).
5. SPARC reference file exists (preferred independent table).

## Critical Configuration (Cell 3)
In normal scientific operation, set:
- `cfg.dry_run = False`
- Keep `cfg.strict_falsifier_mode = True`
- Keep `cfg.allow_synthetic_data = False`

Only change table names if schema differs:
- `cfg.phot_table`
- `cfg.lens_table`
- `cfg.agn_table`

Do not disable strict mode for publication-grade claims.

## Cell-by-Cell Operational Runbook
Use this run order for a full honest run.

### Phase A: Core setup and registration
1. Run Cell 3 (config + canonical path detection).
2. Run Cell 4 (preregistration scaffold output).

Expected artifacts:
- `rubin_rsp/out/preregistered_plan.json`

### Phase B: Gate 0.5 transfer pathway
3. Run Cell 6 (SPARC reference loader).
4. Run Cell 7 (reference builder definitions).
5. Run Cell 8 (safe reference execution path).
6. Run Cell 10 (overlap generation).
7. Run Cell 11 (transfer metrics).

Expected behavior in strict mode:
- If `cfg.dry_run = True`: overlap generation will refuse synthetic creation.
- If `cfg.dry_run = False`: overlap should be generated from TAP and marked `live_tap`.

Expected artifacts:
- `rubin_rsp/out/gate05_sparc_reference_build_report.json`
- `rubin_rsp/out/gate05_overlap_generation_report.json`
- `rubin_rsp/out/gate05_transfer_metrics.json`
- `rubin_rsp/data/sparc_rubin_overlap.csv` (live runs)

Gate 0.5 pass criteria:
- `n_overlap >= 20`
- `abs(rho) >= 0.40`
- sign matches expected sign
- provenance must be `live_tap` to count as falsifier-grade

### Phase C: Gate 1 and Gate 2
8. Run Cell 12 (query builders).
9. Run Cell 13 (photometry fetch).
10. Run Cell 14 (Gate 1 metrics).
11. Run Cell 15 (Gate 2 robustness).

Expected strict behavior:
- In strict mode with `dry_run=True`, Cell 13 raises runtime error and blocks synthetic pass claims.
- In live mode, data mode should be `live_tap`.

Expected artifacts:
- `rubin_rsp/out/gate1_photometry_raw.csv`
- `rubin_rsp/out/gate1_metrics.json`
- `rubin_rsp/out/gate2_robustness.json`

Gate 1 pass criteria:
- `n_total >= min_n`
- `abs(rho_validation) >= min_abs_rho`
- provenance must be `live_tap`

Gate 2 pass criteria:
- `abs(mean_shuffle_rho) <= max_null_rho`
- provenance must be `live_tap`

### Phase D: Gate 3 and Gate 4 planning outputs
12. Run Cell 17 (Gate 3 plan artifact).
13. Run Cell 19 (Gate 4 plan artifact).

Expected artifacts:
- `rubin_rsp/out/gate3_plan.json`
- `rubin_rsp/out/gate4_plan.json`

### Phase E: Summary and readiness
14. Run Cell 20 (run summary).
15. Run Cell 21 (artifact readiness check).

Expected artifacts:
- `rubin_rsp/out/run_summary.json`

## Interpreting `run_summary.json`
Key fields:
- `falsifier_grade`: must be `true` for scientific pass claims.
- `data_provenance.gate05_data_mode`: should be `live_tap`.
- `data_provenance.gate1_gate2_data_mode`: should be `live_tap`.
- `gate_results`: effective pass values; these are forced to `false` if provenance is non-live.

Decision rule:
- Treat results as publishable gate evidence only when `falsifier_grade = true`.

## Artifact Reference Table
- `preregistered_plan.json`: prereg hypothesis and stop conditions.
- `gate05_sparc_reference_build_report.json`: coordinate source and coverage context.
- `gate05_overlap_generation_report.json`: overlap generation status and mode.
- `gate05_transfer_metrics.json`: transfer correlation and gate pass state.
- `gate1_photometry_raw.csv`: retrieved or generated photometry sample.
- `gate1_metrics.json`: discovery and validation trend metrics.
- `gate2_robustness.json`: null and bootstrap diagnostics.
- `gate3_plan.json`: weak-lensing implementation TODO state.
- `gate4_plan.json`: AGN variability implementation TODO state.
- `run_summary.json`: top-level operational truth summary.

## Honest Reporting Rules
Always report:
1. `dry_run` status.
2. `strict_falsifier_mode` status.
3. data mode per gate (`none`, `synthetic`, `live_tap`).
4. whether `falsifier_grade` is true.

Never report gate pass as scientific support when:
- any pass came from synthetic data,
- overlap came from stale files in strict mode,
- `falsifier_grade` is false.

## Troubleshooting

### Issue: Gate 0.5 metrics shows pass while dry run is active
Cause:
- old overlap file loaded historically.
Resolution:
- strict-mode guard now blocks this by requiring current-run `live_tap` mode.
- rerun Cell 10 then Cell 11.

### Issue: Gate 1 fetch fails in strict mode during dry run
Cause:
- expected strict behavior; synthetic is disabled.
Resolution:
- set `cfg.dry_run = False` and run with live TAP access.

### Issue: Readiness shows overlap missing despite file existing
Cause:
- non-canonical relative path checks.
Resolution:
- readiness now checks canonical `DATA_DIR` path.

### Issue: TAP query fails due to schema mismatch
Cause:
- table or column names differ from notebook defaults.
Resolution:
- verify schema in RSP browser and update `cfg.phot_table`, `cfg.lens_table`, `cfg.agn_table`.

### Issue: pyvo import or query runtime error
Cause:
- environment or package mismatch.
Resolution:
- install/repair `pyvo` and confirm kernel environment before rerun.

## Operator Checklist (Live Falsifier Run)
- Confirm Rubin authorization and endpoint access.
- Set `cfg.dry_run = False`.
- Keep strict mode on.
- Execute runbook phases A through E in order.
- Confirm `run_summary.json` reports:
  - `falsifier_grade: true`
  - gate data modes as `live_tap`
  - gate pass states from live provenance only.

## Change Control
When modifying this notebook operationally:
1. Preserve strict falsifier defaults.
2. Preserve canonical pathing via repo-root detection.
3. Re-run Gate 0.5, Gate 1, Gate 2, and summary cells.
4. Re-check artifact-level readiness and provenance fields.

## Minimal Operator Command Reference
Typical outputs are written automatically by notebook cells.
For quick filesystem verification in terminal:
```powershell
Get-ChildItem rubin_rsp/out
Get-ChildItem rubin_rsp/data
```

## Final Operational Principle
This pipeline is built for falsification pressure, not convenience. If provenance is not live and explicit, the correct operational state is fail/hold, not pass.
