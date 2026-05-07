import argparse
import re
from pathlib import Path


def normalize_heading_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^[-*]\s+", "", text)
    # Strip leading numbering like "2.1" or "9.9.4" or "C.3"
    text = re.sub(r"^(?:\d+|[A-Z])(?:[\.:]\d+)+(?:\.)?\s+", "", text)
    # Strip leading top-level numbering like "2." or "10."
    text = re.sub(r"^\d+\s*[\.)]\s*", "", text)
    return text.strip()


def parse_outline(outline_path: Path) -> dict[str, list[tuple[int, str]]]:
    # Returns mapping: top-level title -> list of (level, title) for nested headings.
    lines = outline_path.read_text(encoding="utf-8").splitlines()
    tree: dict[str, list[tuple[int, str]]] = {}

    current_top: str | None = None

    for line in lines:
        if not line.strip():
            continue
        if not line.lstrip().startswith("-"):
            continue

        # indentation: 0 spaces => top-level, 2 => child, 4 => grandchild...
        indent = len(line) - len(line.lstrip(" "))
        level = indent // 2

        raw = normalize_heading_text(line)
        if not raw:
            continue

        key = raw.strip().lower()
        if level == 0:
            # Skip non-content headings
            if key in {
                "abstract",
                "table of contents",
                "tables",
                "table of figures",
                "discussion references",
                "references",
            }:
                current_top = None
                continue
            # Reject sentence-like accidental lines
            if len(raw) > 140:
                current_top = None
                continue

            current_top = raw
            tree.setdefault(current_top, [])
            continue

        if current_top is None:
            continue

        # Only keep up to subsubsection level (1=sub,2=subsub)
        if level > 2:
            continue

        tree[current_top].append((level, raw))

    return tree


def stub_is_minimal(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    meaningful = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("%")]
    # Expect just \section{...} optionally followed by nothing else.
    if len(meaningful) <= 1 and any(ln.startswith("\\section{") for ln in meaningful):
        return True
    if len(meaningful) == 2 and meaningful[0].startswith("\\section{") and meaningful[1].startswith("\\appendix"):
        return True
    # Also allow section + a single TODO comment treated as meaningful? (it starts with % so excluded)
    if len(meaningful) == 1 and meaningful[0].startswith("\\section{"):
        return True
    return False


def extract_section_title_from_file(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^\\section\{(.*)\}\s*$", s)
        if m:
            return m.group(1)
        return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Add subsection skeletons to minimal section stubs.")
    parser.add_argument(
        "--outline",
        default=str(Path(__file__).resolve().parents[1] / "scratch" / "outline.md"),
        help="Path to outline.md",
    )
    parser.add_argument(
        "--sections-dir",
        default=str(Path(__file__).resolve().parents[1] / "sections"),
        help="Directory containing section .tex files",
    )

    args = parser.parse_args()

    outline_path = Path(args.outline)
    sections_dir = Path(args.sections_dir)

    tree = parse_outline(outline_path)

    updated = 0
    skipped = 0

    for section_file in sorted(sections_dir.glob("[0-9][0-9]_*.tex")):
        if not stub_is_minimal(section_file):
            skipped += 1
            continue

        title = extract_section_title_from_file(section_file)
        if not title:
            skipped += 1
            continue

        # Match by normalized (strip numbering) against outline keys.
        norm = re.sub(r"^\d+\s*[\.)]\s*", "", title).strip()

        # Outline top-level might also omit numbering already; so try direct match.
        children = tree.get(norm)
        if children is None:
            children = tree.get(title)
        if children is None:
            # For appendices, keep as-is.
            skipped += 1
            continue

        lines: list[str] = []
        lines.append(f"\\section{{{title}}}")
        lines.append("")
        lines.append("% TODO: Port text/equations into each subsection; verify against the PDF.")
        lines.append("")

        for level, child_title in children:
            child_clean = normalize_heading_text(child_title)
            if not child_clean:
                continue
            if level == 1:
                lines.append(f"\\subsection{{{child_clean}}}")
                lines.append("")
                lines.append("% TODO")
                lines.append("")
            elif level == 2:
                lines.append(f"\\subsubsection{{{child_clean}}}")
                lines.append("")
                lines.append("% TODO")
                lines.append("")

        section_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        updated += 1

    print(f"Updated: {updated}")
    print(f"Skipped (already edited/unmatched): {skipped}")


if __name__ == "__main__":
    main()
