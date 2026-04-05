# Zenodo Publishing Guide: Three Extension Preprints Linked to v5.1

Date: 2026-04-04
Workspace root: D:\#Documents\#Publication\Spacetime_Mechanics

This guide provides a complete, execution-ready workflow to publish the three audited documents as Zenodo preprints that are explicitly linked as extensions of your existing IRS/SPARC v5.1 preprint.

---

## 0) Scope and target files

Base preprint already published (provided by you):
- D:\#Documents\#Publication\Spacetime_Mechanics\Kitcey_2026_Intrinsic_Response_Sector_DM_Candidacy.v.5.1.0..pdf

Three extension documents (sources identified in workspace):
- D:\#Documents\#Publication\Spacetime_Mechanics\Dark_Gravity_2.0\Work\KITCEY_2026_Intrinsic_Response_Sector_as_Dark_Gravity_II.v.1.3.0.pdf
- D:\#Documents\#Publication\Spacetime_Mechanics\Dark_Gravity_2.0\Work\IRS_13_Companion_Stage_Closure_Analysis.pdf
- D:\#Documents\#Publication\Spacetime_Mechanics\Dark_Gravity_2.0\Work\ROBUST_METHODS_RESULTS_IMPLICATIONS_STAGE0_TO_15_Zenodo.pdf

Corresponding audited source files:
- D:\#Documents\#Publication\Spacetime_Mechanics\Dark_Gravity_2.0\Work\KITCEY_2026_Intrinsic_Response_Sector_as_Dark_Gravity_II.v.1.3.0.tex
- D:\#Documents\#Publication\Spacetime_Mechanics\Dark_Gravity_2.0\Work\IRS_13_Companion_Stage_Closure_Analysis.tex
- D:\#Documents\#Publication\Spacetime_Mechanics\Dark_Gravity_2.0\Work\ROBUST_METHODS_RESULTS_IMPLICATIONS_STAGE0_TO_15_Zenodo.tex

Important DOI note:
- Your internal docs reference v5.1 DOI 10.5281/zenodo.18799081.
- CITATION.cff in Spacetime_Mechanics__git currently contains DOI 10.5281/zenodo.18778895.
- Resolve this before publishing by confirming the correct target record in Zenodo.

---

## 1) Recommended publication strategy

Recommended model: publish each of the three documents as its own Zenodo record, each linked to the base v5.1 record via Related identifiers.

Why this is best:
- Each extension gets its own DOI and can be cited independently.
- The chain of evidence remains readable.
- Future revisions of one extension do not force republishing the others.

Relation to set in Zenodo metadata for each extension:
- Relation: Is supplement to
- Identifier: DOI of the base v5.1 record

Optional additional relation:
- Is part of (if you create a collection-level concept record)

---

## 2) Preflight checklist (must pass before upload)

1. Confirm PDF artifacts exist and open correctly.
2. Verify citation completeness gate.
3. Verify document metadata and title page consistency.
4. Prepare checksums for archival integrity.
5. Freeze upload package folder.

### 2.1 Verify citation policy gate

Run from workspace root in PowerShell:

```powershell
Set-Location "D:\#Documents\#Publication\Spacetime_Mechanics"
./Dark_Gravity_2.0/check_citations.ps1
```

Acceptance criteria:
- No unresolved citation keys
- No missing DOI for cited entries unless explicitly marked
- No bibliography generation errors

### 2.2 Build/confirm PDFs

Known existing PDFs:
- KITCEY_2026_Intrinsic_Response_Sector_as_Dark_Gravity_II.v.1.3.0.pdf
- IRS_13_Companion_Stage_Closure_Analysis.pdf
- ROBUST_METHODS_RESULTS_IMPLICATIONS_STAGE0_TO_15_Zenodo.pdf

### 2.3 Produce checksums for all upload files

```powershell
Set-Location "D:\#Documents\#Publication\Spacetime_Mechanics\Dark_Gravity_2.0\Work"
Get-FileHash "KITCEY_2026_Intrinsic_Response_Sector_as_Dark_Gravity_II.v.1.3.0.pdf" -Algorithm SHA256
Get-FileHash "IRS_13_Companion_Stage_Closure_Analysis.pdf" -Algorithm SHA256
Get-FileHash "ROBUST_METHODS_RESULTS_IMPLICATIONS_STAGE0_TO_15_Zenodo.pdf" -Algorithm SHA256
```

Save the output into a manifest file named:
- zenodo_extension_sha256_manifest.txt

---

## 3) Prepare upload package folders

Create a clean packaging area:

```powershell
Set-Location "D:\#Documents\#Publication\Spacetime_Mechanics"
New-Item -ItemType Directory -Force -Path ".\zenodo_uploads\2026-04-irs-extensions"
New-Item -ItemType Directory -Force -Path ".\zenodo_uploads\2026-04-irs-extensions\01_IRS_II"
New-Item -ItemType Directory -Force -Path ".\zenodo_uploads\2026-04-irs-extensions\02_IRS_13_Companion"
New-Item -ItemType Directory -Force -Path ".\zenodo_uploads\2026-04-irs-extensions\03_Robust_Methods"
```

Copy files:

```powershell
Copy-Item ".\Dark_Gravity_2.0\Work\KITCEY_2026_Intrinsic_Response_Sector_as_Dark_Gravity_II.v.1.3.0.pdf" ".\zenodo_uploads\2026-04-irs-extensions\01_IRS_II\"
Copy-Item ".\Dark_Gravity_2.0\Work\IRS_13_Companion_Stage_Closure_Analysis.pdf" ".\zenodo_uploads\2026-04-irs-extensions\02_IRS_13_Companion\"
Copy-Item ".\Dark_Gravity_2.0\Work\ROBUST_METHODS_RESULTS_IMPLICATIONS_STAGE0_TO_15_Zenodo.pdf" ".\zenodo_uploads\2026-04-irs-extensions\03_Robust_Methods\"
```

Add supporting files per package (recommended):
- LICENSE copy
- Short README specific to each extension
- SHA256 line for that package PDF

---

## 4) Zenodo metadata templates (copy into each record)

Replace BASE_DOI with your confirmed v5.1 DOI.

### 4.1 Record A: IRS II extension

Title:
- Intrinsic Response Sector as Dark Gravity II: Extended Framework and Cross-Scale Obligations (v1.3.0)

Upload type:
- Publication

Publication type:
- Preprint

Description (suggested):
- This preprint extends the IRS/SPARC v5.1 framework with formal obligations, scope boundaries, and expanded theoretical synthesis. It is published as a supplement to the base IRS/SPARC v5.1 preprint and should be read alongside that record.

Creators:
- Robert D. Kitcey (include ORCID)

Keywords:
- dark gravity
- intrinsic response sector
- galactic dynamics
- modified gravity
- SPARC
- galaxy rotation curves
- baryonic Tully-Fisher relation
- stress-energy tensor
- general relativity
- dark matter alternative
- phenomenology
- gravitational theory
- astrophysics

Access right:
- Open Access

License:
- Match your base preprint license for consistency (for example CC-BY-NC-ND-4.0 if that is what you intend)

Related identifiers:
- DOI BASE_DOI, relation = Is supplement to

Version:
- v1.3.0

Notes:
- Include checksum and build date.

### 4.2 Record B: IRS 13 companion extension

Title:
- IRS 13 Companion: Stage Closure Analysis for the Intrinsic Response Sector Program

Upload type:
- Publication

Publication type:
- Preprint

Description (suggested):
- This preprint serves as the companion stage-closure analysis to the IRS II manuscript. It clarifies closure status, scoped obligations, and the current boundary between established galactic-domain results and outstanding cross-scale program requirements. It is published as a supplement to the base IRS/SPARC v5.1 preprint.

Keywords:
- intrinsic response sector
- dark gravity
- stage closure
- theory constraints
- scope conditions
- closure analysis
- general relativity
- effective theory
- research program structure
- galactic phenomenology
- dark matter alternative
- scientific methodology

Related identifiers:
- DOI BASE_DOI, relation = Is supplement to

Version:
- v1.3.0 or the exact manuscript version shown in the PDF

### 4.3 Record C: Robust methods extension

Title:
- Robust Methods, Results, and Implications for IRS/Dark Gravity Stage 0-15 (Zenodo Release)

Upload type:
- Publication

Publication type:
- Preprint

Description (suggested):
- This preprint documents methods robustness checks, empirical constraints, and implication mapping for the IRS/Dark Gravity program. It is a methodological supplement to the base IRS/SPARC v5.1 preprint.

Keywords:
- dark gravity
- intrinsic response sector
- robust methods
- model comparison
- chi-squared analysis
- Bayesian information criterion
- SPARC
- galaxy rotation curves
- empirical validation
- reproducibility
- statistical inference
- phenomenology

Related identifiers:
- DOI BASE_DOI, relation = Is supplement to

Version:
- v1.0.0 (or current release tag you choose)

---

## 5) Exact Zenodo UI workflow (repeat 3 times)

For each of the three extension records:

1. Sign in to Zenodo.
2. Click New upload.
3. Upload the PDF first.
4. Upload README and checksum file (optional but recommended).
5. Set Upload type to Publication.
6. Set Publication type to Preprint.
7. Fill title, authors, affiliations, ORCID, description.
8. Add keywords.
9. Set license and access rights.
10. Add Related identifier pointing to base v5.1 DOI with relation Is supplement to.
11. Set version.
12. Save draft.
13. Preview record page carefully.
14. Publish.
15. Copy minted DOI and concept DOI to your tracking table.

---

## 6) Post-publication linking and consistency updates

After all 3 records are published:

1. Update each extension description to include cross-links to the other two extension DOIs.
2. Update base v5.1 record description to include a new section:
   - Extensions:
     - DOI A
     - DOI B
     - DOI C
3. Update citation files in repository:
   - Spacetime_Mechanics__git/CITATION.cff
   - Any manuscript reference sections that list Zenodo versions
4. Update local project index docs:
   - README.md
   - REPRODUCIBILITY.md (if present in active publication repo)
   - SPARC audit docs where DOI pointers appear

---

## 7) Quality control gates before pressing Publish

Gate A: PDF quality
- Opens without errors
- Embedded fonts
- Correct title page and author block
- No visible broken equations/tables/figures

Gate B: Metadata integrity
- Title exactly matches PDF title
- Version string present and correct
- ORCID and creator names correct
- License consistent with policy

Gate C: Relationship integrity
- Related identifier uses confirmed base DOI
- Relation type is Is supplement to

Gate D: Citation integrity
- check_citations.ps1 passed
- Manuscript self-citations include correct DOI placeholders or final DOIs

Gate E: Reproducibility integrity
- SHA256 checksum recorded and archived
- Source TeX and build environment noted in README

---

## 8) Suggested record naming and versioning policy

Use stable semantic style:
- IRS II: v1.3.0 (already in filename)
- Robust Methods: v1.0.0
- KitState-Hilbert: v1.0.0

For later updates:
- Increment patch for typo-only changes: v1.3.1
- Increment minor for additional sections/figures: v1.4.0
- Increment major for structural reframe: v2.0.0

Keep filename and Zenodo version field synchronized.

---

## 9) DOI tracking table template

Create a local file named zenodo_extension_doi_registry.csv with columns:

- record_label
- file_name
- version
- zenodo_doi
- zenodo_concept_doi
- relation_target_doi
- publish_date
- sha256

Example rows:
- IRS_II, KITCEY_2026_Intrinsic_Response_Sector_as_Dark_Gravity_II.v.1.3.0.pdf, v1.3.0, TBD, TBD, BASE_DOI, 2026-04-04, TBD
- IRS_13_COMPANION, IRS_13_Companion_Stage_Closure_Analysis.pdf, v1.3.0, TBD, TBD, BASE_DOI, 2026-04-04, TBD
- ROBUST_METHODS, ROBUST_METHODS_RESULTS_IMPLICATIONS_STAGE0_TO_15_Zenodo.pdf, v1.0.0, TBD, TBD, BASE_DOI, 2026-04-04, TBD

---

## 10) Recommended publication order

1. Publish IRS II first (closest conceptual continuation from v5.1).
2. Publish IRS 13 Companion second (closure and program-boundary companion).
3. Publish Robust Methods third (empirical/methodological support).

Then update all descriptions to cross-link all four records (base + 3 extensions).

---

## 11) Final release checklist

- [ ] Base DOI confirmed (single authoritative value)
- [ ] All 3 PDFs present and checked
- [ ] Citation gate passed
- [ ] SHA256 manifest created
- [ ] 3 Zenodo drafts completed
- [ ] Related identifier set correctly on each
- [ ] All 3 records published
- [ ] DOI registry file updated
- [ ] Base record updated with extension DOI links
- [ ] CITATION and README files updated

---

## 12) Fast path summary (if you want minimum friction)

1. Confirm base DOI.
2. Confirm all three PDFs match the final audited builds.
3. Run check_citations.ps1.
4. Create three Zenodo uploads as Publication -> Preprint.
5. Set relation Is supplement to BASE_DOI for each.
6. Publish in order IRS II, IRS 13 Companion, Robust Methods.
7. Backfill DOI links across all records and local citation files.

This yields clean, citable, extension-linked preprints with strong archival hygiene and reproducibility provenance.
