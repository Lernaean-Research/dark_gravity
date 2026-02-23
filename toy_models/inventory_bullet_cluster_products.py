"""Inventory Bullet Cluster HEASARC products present on disk.

This script is *not* a reduction pipeline. It answers the concrete question:
"Where in the downloaded datasets are the files one would use to derive the
1D radial profiles needed by `cluster_profile_q_est.py`?"

It scans a local staging root like:
  toy_models/data/bullet_cluster/raw/heasarc/

and writes a short report:
  toy_models/out_cluster_fetch/bullet_cluster/local_products_inventory.md

The report highlights:
- Chandra Level-2 event files (`*evt2*.fits*`) and related aspect/GTI products
- XMM PPS products (event lists, images, exposure maps, spectra/response)

Those are the *inputs* to deriving:
- gas density profile / gas mass profile -> M_bar(<r)
- hydrostatic mass profile (optional) -> M_tot(<r)

Note: gravitational lensing mass profiles typically require optical/IR imaging
and shear catalogs (not contained in these X-ray archives).
"""

from __future__ import annotations

import argparse
import glob
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PatternGroup:
    title: str
    patterns: tuple[str, ...]


CHANDRA_GROUPS: list[PatternGroup] = [
    PatternGroup(
        "Chandra primary (typical Level-2 science products)",
        (
            "primary/*evt2*.fits*",
            "primary/*asol*.fits*",
            "primary/*bpix*.fits*",
            "primary/*fov1*.fits*",
            "primary/*full_img2*.fits*",
            "primary/*cntr_img2*.fits*",
        ),
    ),
    PatternGroup(
        "Chandra secondary (supporting calibration / aspect / L1 products)",
        (
            "secondary/*evt1*.fits*",
            "secondary/*flt1*.fits*",
            "secondary/*msk1*.fits*",
            "secondary/*mtl1*.fits*",
            "secondary/aspect/*osol1*.fits*",
            "secondary/aspect/*aqual1*.fits*",
        ),
    ),
    PatternGroup(
        "Chandra misc",
        (
            "00README",
            "oif.fits",
            "axaf*.pdf*",
        ),
    ),
]

XMM_GROUPS: list[PatternGroup] = [
    PatternGroup(
        "XMM PPS (pipeline products)",
        (
            "PPS/*EVENLI*.FTZ",
            "PPS/*IMAGE_*.FTZ",
            "PPS/*EXPMAP*.FTZ",
            "PPS/*SRCLI_*.FTZ",
            "PPS/*SBSPEC*.FTZ",
            "PPS/*RSPMAT*.FTZ",
            "PPS/*SUMMAR*.HTM",
            "PPS/*PPSDAT*.HTM",
        ),
    ),
    PatternGroup(
        "XMM other",
        (
            "ODF/*",
            "om_mosaic/*.fits*",
        ),
    ),
]


def find_hits(root: Path, patterns: Iterable[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for pat in patterns:
        hits = sorted(glob.glob(str(root / pat)))
        out[pat] = [h.replace("\\", "/") for h in hits]
    return out


def md_escape(s: str) -> str:
    return s.replace("`", "\\`")


def md_report(chandra_dirs: list[Path], xmm_dirs: list[Path]) -> str:
    lines: list[str] = []
    lines.append("# Bullet Cluster: local HEASARC product inventory")
    lines.append("")
    lines.append("This report is an *inventory* of downloaded products, not a reduction.")
    lines.append("")

    def section(header: str):
        lines.append(f"## {header}")
        lines.append("")

    section("Chandra (by ObsID)")
    if not chandra_dirs:
        lines.append("No Chandra ObsID directories found.")
    for d in sorted(chandra_dirs, key=lambda p: p.name):
        lines.append(f"### ObsID {md_escape(d.name)}")
        lines.append("")
        for g in CHANDRA_GROUPS:
            lines.append(f"**{g.title}**")
            hits = find_hits(d, g.patterns)
            for pat, files in hits.items():
                lines.append(f"- `{pat}`: {len(files)}")
                for f in files[:8]:
                    lines.append(f"  - `{md_escape(f)}`")
                if len(files) > 8:
                    lines.append(f"  - ... (+{len(files)-8} more)")
            lines.append("")

    section("XMM (by ObsID)")
    if not xmm_dirs:
        lines.append("No XMM ObsID directories found.")
    for d in sorted(xmm_dirs, key=lambda p: p.name):
        lines.append(f"### ObsID {md_escape(d.name)}")
        lines.append("")
        for g in XMM_GROUPS:
            lines.append(f"**{g.title}**")
            hits = find_hits(d, g.patterns)
            for pat, files in hits.items():
                lines.append(f"- `{pat}`: {len(files)}")
                for f in files[:8]:
                    lines.append(f"  - `{md_escape(f)}`")
                if len(files) > 8:
                    lines.append(f"  - ... (+{len(files)-8} more)")
            lines.append("")

    section("What these products give you")
    lines.append(
        "To run `cluster_profile_q_est.py` apples-to-apples with SPARC, you need a 1D profile of either "
        "`(v_tot_kms, v_bar_kms)` or `(M_tot_Msun, M_bar_Msun)` vs radius."
    )
    lines.append("")
    lines.append(
        "- **Baryons (M_bar)**: can be derived from X-ray surface brightness + spectral temperature/metallicity "
        "(gas density profile + gas mass). That uses event lists + exposure maps + responses/spectra products."
    )
    lines.append(
        "- **Total (M_tot)**: can be obtained either from (a) lensing mass models (usually from optical/IR data, "
        "not included here) or (b) hydrostatic equilibrium using X-ray density+temperature gradients (uses these X-ray products)."
    )
    lines.append("")
    lines.append(
        "**Important limitation**: A Bullet-Cluster *lensing* test (2D mass centroid offsets) requires lensing mass maps/shear catalogs "
        "from optical/IR imaging. The HEASARC X-ray downloads do not contain those; they support the gas (baryon) side strongly."
    )
    lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--raw-root",
        default="toy_models/data/bullet_cluster/raw/heasarc",
        help="Local staging root with subfolders chandra/ and xmm/",
    )
    ap.add_argument(
        "--out-md",
        default="toy_models/out_cluster_fetch/bullet_cluster/local_products_inventory.md",
    )
    args = ap.parse_args(argv)

    raw_root = Path(args.raw_root)
    chandra_root = raw_root / "chandra"
    xmm_root = raw_root / "xmm"

    chandra_dirs = [p for p in chandra_root.iterdir()] if chandra_root.exists() else []
    chandra_dirs = [p for p in chandra_dirs if p.is_dir()]

    xmm_dirs = [p for p in xmm_root.iterdir()] if xmm_root.exists() else []
    xmm_dirs = [p for p in xmm_dirs if p.is_dir()]

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(md_report(chandra_dirs, xmm_dirs), encoding="utf-8")

    print(f"Wrote {out_md}")
    print(f"Chandra ObsIDs: {len(chandra_dirs)}")
    print(f"XMM ObsIDs: {len(xmm_dirs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
