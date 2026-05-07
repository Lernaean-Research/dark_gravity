# arxiv_robust (clean LaTeX workflow)

This is a **fresh, hand-curated LaTeX project** intended to be the most robust path for an arXiv submission of a math-heavy physics paper.

## Why this is more robust

- Uses **pdfLaTeX + BibTeX + natbib** (numeric) — the lowest-friction arXiv path.
- Avoids `biblatex`/`biber` (feature-rich locally, but arXiv does not reliably run `biber`; you must ship a `.bbl`).
- Uses conservative packages with long track records.

## Fonts (arXiv-friendly defaults)

Default in `preamble.tex`:
- `lmodern` + `T1` encoding (clean, widely compatible, excellent math coverage).

Optional Times-like look:
- Uncomment `newtxtext` + `newtxmath` and comment out `lmodern`.

## Build

From repo root:

```powershell
cd arxiv_robust
latexmk -pdf -interaction=nonstopmode main.tex
```

Outputs go to `arxiv_robust/build/`.

## Next step: port content from v5.0.7

This project is meant to be **hand-curated**. The supported way to get started is to extract a scratch dump from the pinned DOCX, then migrate content into `sections/*.tex` while checking against the PDF.

Generate scratch files:

```powershell
cd arxiv_robust
python .\scripts\extract_docx_to_scratch.py
```

This writes:

- `arxiv_robust/scratch/outline.md` (heading outline)
- `arxiv_robust/scratch/body_dump.tex` (escaped plain text + LaTeX section commands)

Then copy/translate into `sections/` (especially equations + citations).

### Recommended workflow (repeatable)

1) Extract text + outline from the pinned DOCX:

```powershell
cd arxiv_robust
python .\scripts\extract_docx_to_scratch.py
```

2) Generate a curated section skeleton from `scratch/outline.md`:

```powershell
python .\scripts\generate_section_skeleton_from_outline.py
python .\scripts\add_subsection_skeletons_from_outline.py
```

3) Split the raw scratch dump into per-section scratch files:

```powershell
python -X utf8 .\scripts\split_body_dump_to_section_scratch.py
```

This creates `scratch/by_section/*.tex` as donors.

4) Port section-by-section:

- Open a curated file in `sections/` (e.g., `sections/10_introduction.tex`).
- Use the matching donor in `scratch/by_section/` for the raw paragraph text.
- Reconstruct equations directly from the PDF (DOCX extraction will drop/garble math).

### Unicode note

This project is pdfLaTeX-first. If you paste Unicode symbols from the DOCX/PDF (Greek letters, primes, etc.), ensure they compile. `preamble.tex` includes a conservative `newunicodechar` mapping for common physics symbols.

## arXiv upload zip

```powershell
./scripts/build_zip.ps1
```

This produces `arxiv_robust_upload.zip` at repo root containing:
- `main.tex`, `preamble.tex`, `macros.tex`
- `sections/*.tex`, `figures/` (as-is)
- `references.bib`
- `build/main.bbl` (preferred for arXiv reliability)

If you add figures, prefer PDF/PNG/JPG and keep filenames simple.
