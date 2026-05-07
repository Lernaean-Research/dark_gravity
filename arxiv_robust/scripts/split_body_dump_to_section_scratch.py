import argparse
import re
from pathlib import Path


def normalize_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"^\d+\s*[\.)]\s*", "", title)  # 1. Intro
    title = title.strip()
    return title


SKIP_NORMALIZED = {
    "Abstract",
    "Table of Contents",
    "Tables",
    "Table of Figures",
    "Discussion References",
    "References",
}


def extract_section_title_from_stub(path: Path) -> str | None:
    # Expect first non-empty line to be \section{...}
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
    parser = argparse.ArgumentParser(description="Split scratch/body_dump.tex into per-section scratch files.")
    parser.add_argument(
        "--body",
        default=str(Path(__file__).resolve().parents[1] / "scratch" / "body_dump.tex"),
        help="Path to scratch/body_dump.tex",
    )
    parser.add_argument(
        "--sections-dir",
        default=str(Path(__file__).resolve().parents[1] / "sections"),
        help="Path to curated sections directory",
    )
    parser.add_argument(
        "--outdir",
        default=str(Path(__file__).resolve().parents[1] / "scratch" / "by_section"),
        help="Output directory for per-section scratch files",
    )

    args = parser.parse_args()

    body_path = Path(args.body)
    sections_dir = Path(args.sections_dir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Build mapping from normalized stub title -> output filename
    stub_map: dict[str, Path] = {}
    for stub in sorted(sections_dir.glob("[0-9][0-9]_*.tex")):
        title = extract_section_title_from_stub(stub)
        if not title:
            continue
        norm = normalize_title(title)
        stub_map[norm] = stub

    # Outputs
    orphan_path = outdir / "_orphan_text.tex"
    orphan_path.write_text("% Orphan text (not mapped to a curated section)\n", encoding="utf-8")

    current_out: Path | None = None

    def write_line(target: Path, line: str) -> None:
        with target.open("a", encoding="utf-8", newline="\n") as f:
            f.write(line.rstrip("\n") + "\n")

    section_re = re.compile(r"^\\section\{(.*)\}\s*$")

    for line in body_path.read_text(encoding="utf-8").splitlines():
        m = section_re.match(line.strip())
        if m:
            raw_title = m.group(1)
            norm = normalize_title(raw_title)

            # Decide mapping
            if norm in SKIP_NORMALIZED:
                current_out = None
                write_line(orphan_path, f"% --- Skipped section: {raw_title} ---")
                continue

            # Some body_dump headings include numbering (e.g. "1. Introduction")
            # Our stubs omit numbering, so we match on normalized title.
            stub = stub_map.get(norm)
            if stub is None:
                current_out = None
                write_line(orphan_path, f"% --- Unmapped section: {raw_title} ---")
                continue

            # Create per-section scratch file named after the stub.
            out_path = outdir / stub.name
            out_path.write_text(
                "% AUTO-SPLIT from scratch/body_dump.tex\n"
                f"% Source section heading: {raw_title}\n\n",
                encoding="utf-8",
            )
            current_out = out_path
            continue

        # Non-section line: route to current output or orphans
        if current_out is not None:
            write_line(current_out, line)
        else:
            # Keep only non-empty orphan content (avoid huge whitespace)
            if line.strip():
                write_line(orphan_path, line)

    print(f"Wrote per-section scratch files under: {outdir}")
    print(f"Orphans: {orphan_path}")


if __name__ == "__main__":
    main()
