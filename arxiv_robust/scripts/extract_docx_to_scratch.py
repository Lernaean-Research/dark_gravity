import argparse
import json
import re
from pathlib import Path


def _latex_escape(text: str) -> str:
    # Conservative escaping for plain text paragraphs.
    # Leave backslashes alone (sometimes DOCX text contains LaTeX already).
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = "".join(replacements.get(ch, ch) for ch in text)
    return out


def _heading_level(paragraph_style_name: str) -> int | None:
    # Word styles often look like: "Heading 1", "Heading 2", etc.
    m = re.match(r"^Heading\s+(\d+)\b", paragraph_style_name or "")
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _tex_heading(cmd: str, title: str) -> str:
    title = title.strip()
    if not title:
        return ""
    return f"\\{cmd}{{{_latex_escape(title)}}}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract DOCX headings + text into arxiv_robust/scratch for manual porting.")
    parser.add_argument(
        "--manifest",
        default=str(Path(__file__).resolve().parents[1] / "SOURCE_MANIFEST.json"),
        help="Path to arxiv_robust SOURCE_MANIFEST.json",
    )
    parser.add_argument(
        "--docx",
        default=None,
        help="Override DOCX path (defaults to manifest).",
    )
    parser.add_argument(
        "--outdir",
        default=None,
        help="Output directory (defaults to arxiv_robust/scratch).",
    )

    args = parser.parse_args()

    arxiv_dir = Path(__file__).resolve().parents[1]
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    docx_rel = manifest["source_of_truth"]["docx"]
    docx_path = Path(args.docx) if args.docx else (arxiv_dir / docx_rel).resolve()

    outdir = Path(args.outdir) if args.outdir else (arxiv_dir / "scratch")
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        from docx import Document  # python-docx
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "python-docx is required. Install it in your environment (pip install python-docx)."
        ) from exc

    doc = Document(str(docx_path))

    outline_lines: list[str] = []
    body_lines: list[str] = []

    body_lines.append("% AUTO-GENERATED SCRATCH DUMP")
    body_lines.append("% Source: " + str(docx_path))
    body_lines.append("% This file is intended for manual copy/edit into sections/*.tex")
    body_lines.append("")

    for para in doc.paragraphs:
        raw = para.text or ""
        text = raw.strip()
        if not text:
            continue

        style_name = getattr(getattr(para, "style", None), "name", "")
        level = _heading_level(style_name)

        if level is not None:
            indent = "  " * max(0, level - 1)
            outline_lines.append(f"{indent}- {text}")

            if level == 1:
                heading = _tex_heading("section", text)
            elif level == 2:
                heading = _tex_heading("subsection", text)
            elif level == 3:
                heading = _tex_heading("subsubsection", text)
            else:
                heading = _tex_heading("paragraph", text)

            if heading:
                body_lines.append(heading)
                body_lines.append("")
            continue

        # Regular paragraph
        body_lines.append(_latex_escape(text))
        body_lines.append("")

    (outdir / "outline.md").write_text("\n".join(outline_lines) + "\n", encoding="utf-8")
    (outdir / "body_dump.tex").write_text("\n".join(body_lines) + "\n", encoding="utf-8")

    print(f"Wrote: {outdir / 'outline.md'}")
    print(f"Wrote: {outdir / 'body_dump.tex'}")


if __name__ == "__main__":
    main()
