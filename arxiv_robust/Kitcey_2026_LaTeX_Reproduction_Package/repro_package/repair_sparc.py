# -*- coding: utf-8 -*-
"""
repair_sparc.py
===============
One-shot repair of sparc_analysis.py corruption sites.
Run once; verify SYNTAX OK; delete this script.

Usage:
    python repair_sparc.py
"""
import ast
import re
import sys
from pathlib import Path

SRC  = Path("sparc_analysis.py")
DEST = Path("sparc_analysis.py")  # overwrite in place
BACKUP = Path("sparc_analysis_ARCHIVE_20260506.py")

assert BACKUP.exists(), "Archive missing — abort"
src = SRC.read_text(encoding="utf-8")
original = src  # keep for diff check

fixes = []

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 — Remove the duplicate chi_prime_disk_kernel definition.
#          The function is defined twice identically. Keep only the second copy
#          (which follows response_model_curve in logical order).
#          Strategy: remove everything from the FIRST 'def chi_prime_disk_kernel'
#          up to (but not including) the SECOND 'def chi_prime_disk_kernel'.
# ─────────────────────────────────────────────────────────────────────────────
marker_first  = "\ndef chi_prime_disk_kernel("
idx1 = src.find(marker_first)
idx2 = src.find(marker_first, idx1 + 1)
if idx1 != -1 and idx2 != -1:
    src = src[:idx1] + src[idx2:]
    fixes.append("FIX 1: removed duplicate chi_prime_disk_kernel definition")
else:
    fixes.append("FIX 1 skipped: no duplicate found (already clean)")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 — kfold_cv_nydk: remove two stray lines injected before its return.
#          Stray: `r_disk  = fit_response_disk_ydisk(gal)` and `pass`
#          appearing at wrong indent inside the except block.
# ─────────────────────────────────────────────────────────────────────────────
OLD2 = (
    "        except Exception:\n"
    "        r_disk  = fit_response_disk_ydisk(gal)    # disk-kernel, k=2 (Option B)\n"
    "            pass\n"
)
NEW2 = "        except Exception:\n            pass\n"
if OLD2 in src:
    src = src.replace(OLD2, NEW2, 1)
    fixes.append("FIX 2: removed stray lines from kfold_cv_nydk")
else:
    fixes.append("FIX 2 skipped: stray lines not found (already clean)")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3 — kfold_cv_disk_ydisk:
#   a) Remove orphaned dict-entry lines injected into the function body.
#   b) Fix the mangled return statement.
#   c) Remove the spurious duplicate CV-loop block that follows the mangled return.
#   d) Prepend the missing `def kfold_cv_fsig` signature before its orphaned body.
# ─────────────────────────────────────────────────────────────────────────────

# 3a: Remove orphaned dict entries (6 lines) between the comment and cu_te
OLD3a = (
    "        # Disk-kernel model (Option B: \u03c3 from SBdisk photometry)\n"
    "        \"bic_disk\":            r_disk[\"bic\"],\n"
    "        \"chi2_disk\":           r_disk[\"chi2\"],\n"
    "        \"dbic_disk\":           dbic_disk,\n"
    "        \"dbic_disk_vs_nfw\":    dbic_disk_vs_nfw,\n"
    "        \"dbic_disk_vs_nydk\":   dbic_disk_vs_nydk,\n"
    "        \"Y_disk_disk_fit\":     r_disk.get(\"Y_disk\", float(\"nan\")),\n"
    "        cu_te = chi_unit[test_idx]\n"
)
NEW3a = "        cu_te = chi_unit[test_idx]\n"
if OLD3a in src:
    src = src.replace(OLD3a, NEW3a, 1)
    fixes.append("FIX 3a: removed orphaned dict entries from kfold_cv_disk_ydisk body")
else:
    fixes.append("FIX 3a skipped: orphaned dict entries not found")

# 3b+c+d: Fix the mangled return and the spurious CV block that follows it,
#          and insert the missing def line for kfold_cv_fsig.
#          The mangled line ends with: None6 models)...")
#          Everything from that line through `cv_disk = np.array([x for x in cv_disk\n`
#          and then `    V_obs    = gal["V_obs"]\n` (start of orphaned fsig body)
#          is replaced with:
#            - clean return for disk_ydisk
#            - def kfold_cv_fsig signature + docstring + alpha init + R/V_obs lines
MANGLED_RETURN = "    return float(np.mean(cv_errors)) if cv_errors else None6 models)...\")\n"
FSIG_BODY_START = "    V_obs    = gal[\"V_obs\"]\n"

# Find position of the mangled return
idx_mangled = src.find(MANGLED_RETURN)
if idx_mangled != -1:
    # Find where the orphaned fsig body begins (V_obs line right after cv_disk fragment)
    # The spurious block ends with "cv_disk = np.array([x for x in cv_disk\n"
    # then the fsig body starts with indented "    V_obs    = gal["V_obs"]"
    # We replace from the mangled return through to (but not including) "    V_obs    ="
    idx_vsig = src.find(FSIG_BODY_START, idx_mangled)
    if idx_vsig != -1:
        replacement = (
            "    return float(np.mean(cv_errors)) if cv_errors else None\n"
            "\n"
            "\n"
            "def kfold_cv_fsig(gal, alpha=None, k_folds=5):\n"
            "    \"\"\"K-fold CV for IRS with prescribed \u03c3 = \u03b1\u00b7R_t"
            " (k=2: Q and \u03a5_disk free).\"\"\"\n"
            "    if alpha is None:\n"
            "        alpha = ALPHA_SIGMA\n"
            "    R        = gal[\"R\"]\n"
            "    V_obs    = gal[\"V_obs\"]\n"
        )
        src = src[:idx_mangled] + replacement + src[idx_vsig + len(FSIG_BODY_START):]
        fixes.append("FIX 3b: fixed mangled return + removed spurious CV block + added kfold_cv_fsig def")
    else:
        fixes.append("FIX 3b FAILED: could not find V_obs anchor after mangled return")
else:
    fixes.append("FIX 3b skipped: mangled return not found (already clean)")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4 — results.append({...}) dict: corrupted "bic_nfw" entry and interleaved
#          print statements. Replace from the corrupt bic_nfw line through the
#          resumption marker to inject the correct dict entries.
# ─────────────────────────────────────────────────────────────────────────────
# The corrupt block starts at: `        "bic_nfw":             r        mean CV`
# The block ends just before:  `        "dbic_rsig_vs_nfw":    dbic_rsig_vs_nfw,`
# (preceded by a mess of print statements; the dict resumes correctly there)

CORRUPT_BIC_NW_MARKER = "        \"bic_nfw\":             r        mean CV"
RESUME_MARKER         = "        \"dbic_rsig_vs_nfw\":    dbic_rsig_vs_nfw,\n"

idx_corrupt = src.find(CORRUPT_BIC_NW_MARKER)
idx_resume  = src.find(RESUME_MARKER)

if idx_corrupt != -1 and idx_resume != -1 and idx_corrupt < idx_resume:
    correct_entries = (
        "        \"bic_nfw\":             r_nfw[\"bic\"],\n"
        "        \"bic_bur\":             r_bur[\"bic\"],\n"
        "        \"bic_rsig\":            r_rsig[\"bic\"],\n"
        "        \"bic_rydk\":            r_rydk[\"bic\"],\n"
        "        \"bic_nydk\":            r_nydk[\"bic\"],\n"
        "        \"bic_rsyd\":            r_rsyd[\"bic\"],\n"
        "        \"dbic_resp\":           dbic_resp,\n"
        "        \"dbic_nfw\":            dbic_nfw,\n"
        "        \"dbic_bur\":            dbic_bur,\n"
        "        \"dbic_resp_vs_nfw\":    dbic_resp_vs_nfw,\n"
        "        \"dbic_resp_vs_bur\":    dbic_resp_vs_bur,\n"
        "        \"dbic_rsig\":           dbic_rsig,\n"
        "        \"dbic_rydk\":           dbic_rydk,\n"
        "        \"dbic_nydk\":           dbic_nydk,\n"
        "        \"dbic_rsyd\":           dbic_rsyd,\n"
        "        \"dbic_rsig_vs_nfw\":    dbic_rsig_vs_nfw,\n"
    )
    src = src[:idx_corrupt] + correct_entries + src[idx_resume + len(RESUME_MARKER):]
    fixes.append("FIX 4: replaced corrupted bic_nfw dict block with correct entries")
else:
    fixes.append(
        f"FIX 4 skipped/FAILED: corrupt={idx_corrupt}, resume={idx_resume} "
        "(markers not found or already clean)"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FIX 5 — Print section: `prin` + JSON dict entries spliced into print block.
#          Replace from the truncated `prin` through `    t(f"...` with correct
#          print statements.
# ─────────────────────────────────────────────────────────────────────────────
OLD5 = (
    "print(f\"Response(k=1) vs NFW(k=2):     median \u0394BIC = {df['dbic_resp_vs_nfw'].median():.1f}\")\n"
    "prin    \"disk_k2_mean_rmse\":        float(cv_disk.mean()),\n"
    "        \"disk_k2_std_rmse\":         float(cv_disk.std()),\n"
    "        \"disk_k2_vs_nfw_k2_delta\":  float((cv_nfw[:min(len(cv_disk),len(cv_nfw))] - cv_disk[:min(len(cv_disk),len(cv_nfw))]).mean()),\n"
    "        \"disk_k2_vs_nfw_k3_delta\":  float((cv_nydk[:min(len(cv_disk),len(cv_nydk))] - cv_disk[:min(len(cv_disk),len(cv_nydk))]).mean()),\n"
    "    },\n"
    "    \"disk_kernel_bic\": {\n"
    "        \"description\": \"IRS with kernel sourced by SBdisk+SBbul photometry (Option B, k=2)\",\n"
    "        \"median_dbic_vs_bar\":     float(df[\"dbic_disk\"].median()),\n"
    "        \"pass_rate_vs_bar\":       float((df[\"dbic_disk\"] < -10).mean()),\n"
    "        \"median_dbic_vs_nfw_k2\": float(df[\"dbic_disk_vs_nfw\"].median()),\n"
    "        \"irs_disk_favored_vs_nfw_k2_frac\": float((df[\"dbic_disk_vs_nfw\"] < 0).mean()),\n"
    "        \"median_dbic_vs_nfw_k3\": float(df[\"dbic_disk_vs_nydk\"].median()),\n"
    "        \"irs_disk_favored_vs_nfw_k3_frac\": float((df[\"dbic_disk_vs_nydk\"] < 0).mean()),\n"
    "        \"irs_disk_strong_vs_nfw_k3_frac\":  float((df[\"dbic_disk_vs_nydk\"] < -2).mean()),\n"
    "        \"nfw_strong_vs_disk_irs_frac\":     float((df[\"dbic_disk_vs_nydk\"] > 2).mean()),\n"
    "        \"ydisk_median\": float(df[\"Y_disk_disk_fit\"].median()),\n"
    "        \"cv_mean_rmse\": float(cv_disk.mean()),\n"
    "        \"cv_std_rmse\":  float(cv_disk.std()),\n"
    "    t(f\"  Response favored (\u0394BIC<0): {(df['dbic_resp_vs_nfw']<0).mean()*100:.1f}%\")\n"
)
NEW5 = (
    "print(f\"Response(k=1) vs NFW(k=2):     median \u0394BIC = {df['dbic_resp_vs_nfw'].median():.1f}\")\n"
    "print(f\"  Response favored (\u0394BIC<0): {(df['dbic_resp_vs_nfw']<0).mean()*100:.1f}%\")\n"
)
if OLD5 in src:
    src = src.replace(OLD5, NEW5, 1)
    fixes.append("FIX 5: removed JSON dict fragment spliced into print section")
else:
    fixes.append("FIX 5 FAILED: print section corruption pattern not found")

# ─────────────────────────────────────────────────────────────────────────────
# VERIFY
# ─────────────────────────────────────────────────────────────────────────────
print("\n".join(fixes))
print()

try:
    ast.parse(src)
    print("SYNTAX OK — writing repaired file to", DEST)
    DEST.write_text(src, encoding="utf-8")
    print(f"Done. Lines: {src.count(chr(10))}")
except SyntaxError as e:
    print(f"SYNTAX ERROR after repairs: line {e.lineno}: {e.msg}")
    print("File NOT written. Fix the repair script and retry.")
    # Write to a temp file for inspection
    Path("sparc_analysis_repaired_attempt.py").write_text(src, encoding="utf-8")
    print("Partial result written to sparc_analysis_repaired_attempt.py for inspection.")
    sys.exit(1)
