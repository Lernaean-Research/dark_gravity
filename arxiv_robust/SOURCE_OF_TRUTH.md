# Source of truth (arxiv_robust)

This LaTeX project is intended to be the **clean, robust arXiv submission source**.

## Pinned inputs

See `SOURCE_MANIFEST.json`.

- The **PDF** is the authoritative visual/semantic reference.
- The **DOCX** is only a convenience for extracting raw text and headings.

## Working rule

If the LaTeX draft disagrees with the PDF on math, wording, or section structure, **the PDF wins**.

## Next step

Run the DOCX extractor to produce a scratch dump you can port into curated section files:

```powershell
cd arxiv_robust
python .\scripts\extract_docx_to_scratch.py
```

Then manually migrate content into `sections/*.tex` while fixing equations and citations properly.
