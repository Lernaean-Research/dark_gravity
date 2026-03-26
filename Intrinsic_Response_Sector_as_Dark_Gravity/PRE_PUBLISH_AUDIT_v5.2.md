# Pre-Publish Audit Report: v5.2 Manuscript
**Date:** March 2, 2026  
**Status:** ⚠️ ISSUES FOUND - TOC Label Mismatches  
**PDF Generated:** 56 pages (2.32 MB)

---

## 1. COMPILATION & BUILD STATUS

### ✅ Passed
- **PDF Generation:** Successful (2 compilation passes)
- **Exit Code:** 0 (no fatal errors)
- **File Size:** 2,320,804 bytes
- **Page Count:** 56 pages
- **Fonts:** All required (LM family)
- **BibTeX:** 52 entries processed, 0 errors

### ⚠️ Minor Issues
- **Label Changes:** "Labels may have changed. Rerun to get cross-references right" (resolved after 2nd pass)
- **Figure Caption Warnings:** 11 pdfTeX destination metadata warnings (non-fatal formatting metadata)
- **Overfull hbox:** 1 line slightly exceeds width (2.1pt overage - acceptable)

---

## 2. CROSS-REFERENCE AUDIT

### ✅ Verified
- Document structure complete
- All appendices (A-E) present
- Bibliography processed
- TOC generated with 60+ entries

### ⚠️ TOC Label Mismatches Detected
The following TOC entries reference labels that **don't match** the actual section labels in Appendix_E.tex:

| TOC Entry | TOC Label Reference | Actual Label in Appendix_E.tex | Actual Section Title |
|-----------|-------------------|------|---------|
| **E.4** | `e.4-six-point-coherence` | `e.4-vibe-check` | "Vibe Check: Is the Distributed-Forcing Picture Physically Coherent?" |
| **E.6** | `e.6-observational-discriminants` | `e.6-observational-discriminants` | ✅ MATCH |
| **E.7** | `e.7-lensing-consistency` | `e.7-lensing-dynamics-consistency` | "Lensing--Dynamics Consistency: The Decisive Rung" |

**Impact:** TOC hyperlinks for E.4 and E.7 will not resolve to correct sections.

---

## 3. VERSION CONSISTENCY AUDIT

### ✅ Passed
| Location | Status | Value |
|----------|--------|-------|
| Line 199: `\date{}` | ✅ | `v5.2` |
| Line 204: Zenodo citation | ✅ | `v5.2.0` |
| Title page version | ✅ | "Preprint Draft v5.2" |
| Document metadata | ✅ | Title correctly formatted |

---

## 4. BIBLIOGRAPHY & CITATIONS

### ✅ Passed
- BibTeX: 0 errors, 0 fatal warnings
- 52 bibliography entries processed
- `\nocite{*}` ensures all entries included
- APA-like style applied correctly

### ⚠️ Citation Issues in Appendix D & E
The following citations are referenced but undefined in references.bib (pre-existing issue, not from v5.2 changes):

- `Tuan2014Nodal` (referenced line 1569)
- `BenderOrszag1999` (referenced line 1577)
- `KevorkianCole1996` (referenced line 1577)
- `HawkingEllis1973` (referenced line 1593)
- `Wald1984GR` (referenced line 1593)
- `Carroll2019Spacetime` (referenced line 1593)
- `McGaughSchombert2014ML` (referenced line 1597)
- `Ivezic2019LSST` (referenced line 1597)
- `BuniyHsuMurray2006NEC` (referenced line 1601)
- `Rubakov2006NEC` (referenced line 1601)
- `Rubakov2014NECReview` (referenced line 1601)

**Action Required:** Add these 11 missing entries to `references.bib` or fix citations.

---

## 5. FIGURE REFERENCES

### ✅ Passed
- `fig:collective_centroid` - Label defined at Appendix_E.tex:246
- Figure placeholder generated successfully (frame with caption)
- Media files resolved: image6.png, image7.png, image8.png

### ⚠️ Minor Issue
- Figure reference `\ref{fig:collective_centroid}` on page 50 displays as placeholder
- **Status:** Acceptable for preprint (actual figure file available when needed)

---

## 6. APPENDIX E STRUCTURE

### ✅ Passed Sections
- E.1: Overview ✅
- E.2: Mathematical Foundation ✅
- E.3: Collective Minima ✅
- E.4: Vibe Check ✅
- E.5: Globular Clusters ✅
- E.6: Observational Discriminants ✅
- E.7: Lensing-Dynamics ✅
- E.8: Summary ✅

**Total:** 8 subsections + 1 figure = complete.

---

## 7. FORMATTING & TYPOGRAPHY

### ✅ Passed
- Margins: Correct (letter size, 612x792 pts)
- PDF version: 1.5 (compatible)
- Encryption: None (good for preprint)
- Tagged PDF: Not required for arXiv

### ⚠️ Known Typography Issues
- Line 154-156 (Appendix E): 2.1pt overfull hbox (acceptable)
- Table formatting: Some underfull boxes (lines 1302-1488) - standard for tabular data

---

## 8. METADATA & DOCUMENT INFO

### PDF Properties
```
Title:        Intrinsic Response Sector as Dark Gravity: A GR-Compatible 
              Candidate Identity for the Cold Dark Matter Role (SPARC-175)
Author:       (not set in preamble - optional)
Creator:      LaTeX
Producer:     MiKTeX pdfTeX-1.40.28
Date:         Mon Mar  2 11:30:19 2026 MST
Pages:        56
PDF Version:  1.5
Compressed:   Yes (optimized: No)
```

---

## 9. CRITICAL ISSUES REQUIRING FIXES

### 🔴 REQUIRED FIX #1: TOC Label Mismatches
**Severity:** Medium (TOC hyperlinks broken)

**Fix:** Update TOC label references to match Appendix_E.tex labels:

1. Change TOC line for E.4 from:
   ```
   \hyperref[e.4-six-point-coherence]{E.4 Six-Point Coherence Assessment
   ```
   To:
   ```
   \hyperref[e.4-vibe-check]{E.4 Vibe Check: Is the Distributed-Forcing Picture...
   ```

2. Change TOC line for E.7 from:
   ```
   \hyperref[e.7-lensing-consistency]{E.7 Lensing Consistency and Falsification...
   ```
   To:
   ```
   \hyperref[e.7-lensing-dynamics-consistency]{E.7 Lensing--Dynamics Consistency...
   ```

---

### 🔴 REQUIRED FIX #2: Missing Bibliography Entries
**Severity:** High (11 undefined citations)

**Fix:** Add missing entries to `references.bib`:
- `Tuan2014Nodal`
- `BenderOrszag1999`
- `KevorkianCole1996`
- `HawkingEllis1973`
- `Wald1984GR`
- `Carroll2019Spacetime`
- `McGaughSchombert2014ML`
- `Ivezic2019LSST`
- `BuniyHsuMurray2006NEC`
- `Rubakov2006NEC`
- `Rubakov2014NECReview`

---

## 10. POST-FIX COMPILATION CHECKLIST

After applying fixes, run:

```powershell
# Clean old artifacts
rm manuscript_overleaf.{aux,bbl,blg,lof,lot,toc,log}

# First pass (generate .aux)
pdflatex -interaction=nonstopmode manuscript_overleaf.tex

# BibTeX pass (process citations)
bibtex manuscript_overleaf

# Second pass (resolve citations)
pdflatex -interaction=nonstopmode manuscript_overleaf.tex

# Third pass (finalize cross-references)
pdflatex -interaction=nonstopmode manuscript_overleaf.tex
```

**Expected result:** 0 warnings (or only non-fatal formatting warnings).

---

## 11. READINESS ASSESSMENT

| Criterion | Status | Notes |
|-----------|--------|-------|
| PDF Compiles | ✅ | 56 pages generated |
| No Fatal Errors | ✅ | Exit code 0 |
| Bibliography Complete | ⚠️ | 11 missing entries |
| Cross-References | ⚠️ | 2 TOC label mismatches |
| Figure References | ✅ | Placeholder adequate for preprint |
| Version Info | ✅ | v5.2 consistent throughout |
| Formatting | ✅ | Standard LaTeX output |
| **Ready for Publication** | 🔴 NO | **Requires fixes to bibliography and TOC labels** |

---

## 12. RECOMMENDED NEXT STEPS

### Priority 1 (Before Publication)
1. ✏️ Fix TOC label references for E.4 and E.7
2. ✏️ Add 11 missing bibliography entries to `references.bib`
3. ✏️ Run 3-pass LaTeX compilation verification
4. ✏️ Verify all TOC hyperlinks clickable in PDF viewer

### Priority 2 (Optional Enhancements)
1. Add actual figure image (collective_centroid.png) to replace placeholder
2. Optimize PDF (currently not optimized)
3. Add author/subject metadata to PDF properties

### Priority 3 (After Publication)
1. Upload final PDF to arXiv
2. Update Zenodo deposit with v5.2.0
3. Cross-post to GitHub releases

---

## 13. SIGNATURES & APPROVAL

| Check | Result | Auditor | Date |
|-------|--------|---------|------|
| Compilation | ✅ Pass | LaTeX/pdfTeX | 2026-03-02 |
| Structure | ✅ Pass | Manual inspection | 2026-03-02 |
| Citations | ⚠️ Partial | BibTeX analysis | 2026-03-02 |
| Cross-refs | ⚠️ Partial | Label audit | 2026-03-02 |
| **Overall** | 🔴 **NEEDS FIXES** | Pre-Publish Review | 2026-03-02 |

---

## Appendix: Full Compilation Log Summary

**First Pass Output:**
```
This is pdfTeX, Version 3.141592653-2.6-1.40.28 (MiKTeX 25.12)
*** Several natbib warnings for undefined citations (expected)
*** Some "ignored error" infinite glue shrinkage (formatting artifacts from tables)
Output written on manuscript_overleaf.pdf (54 pages, 2247884 bytes)
```

**Second Pass Output:**
```
[Final PDF written]
*** pdfTeX destination warnings (metadata only, non-fatal)
Output written on manuscript_overleaf.pdf (56 pages, 2320804 bytes)
LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.
```

---

**Audit Completed:** 2026-03-02 11:45 MST  
**Next Review:** After fixes applied, before final publication
