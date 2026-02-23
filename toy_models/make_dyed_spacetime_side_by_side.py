"""Create side-by-side comparison panels for dyed-spacetime outputs.

This is a lightweight utility to help interpret the dyed-fabric visualizations
across different normalization/extent choices.

Typical use (matches current sample outputs):
  python toy_models/make_dyed_spacetime_side_by_side.py \
    --names CamB,ESO563-G021 \
    --left-dir toy_models/out_spacetime_sample_pergal/png \
    --right-dir toy_models/out_spacetime_sample_fixed40/png \
    --out-dir toy_models/out_spacetime_side_by_side/png \
    --title-left "Per-galaxy extent" \
    --title-right "Fixed extent (±40 kpc; masked beyond data)"

You can also run it on the 3D proxy outputs by pointing at png_3d.

Requires: matplotlib.
"""

from __future__ import annotations

import argparse
import os
from typing import List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def _parse_names(s: str) -> List[str]:
    out: List[str] = []
    for part in (s or "").split(","):
        name = part.strip()
        if name:
            out.append(name)
    return out


def _read_png(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return mpimg.imread(path)


def _save_side_by_side(
    left_png: str,
    right_png: str,
    out_png: str,
    *,
    name: str,
    title_left: str,
    title_right: str,
    caption: Optional[str] = None,
    dpi: int = 180,
    interpolation: str = "nearest",
) -> None:
    L = _read_png(left_png)
    R = _read_png(right_png)

    fig = plt.figure(figsize=(12.8, 6.4), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1])

    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])

    ax0.imshow(L, interpolation=interpolation)
    ax1.imshow(R, interpolation=interpolation)

    for ax in (ax0, ax1):
        ax.set_axis_off()

    ax0.set_title(title_left, fontsize=12)
    ax1.set_title(title_right, fontsize=12)

    fig.suptitle(f"{name}: side-by-side comparison", fontsize=14)

    if caption:
        fig.text(0.5, 0.01, caption, ha="center", va="bottom", fontsize=10)

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    fig.savefig(out_png, dpi=int(dpi))
    plt.close(fig)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", required=True, help="Comma-separated list of galaxy names (file stem).")
    ap.add_argument("--left-dir", required=True, help="Directory containing left PNGs (named <galaxy>.png).")
    ap.add_argument("--right-dir", required=True, help="Directory containing right PNGs (named <galaxy>.png).")
    ap.add_argument("--out-dir", required=True, help="Output directory to write side-by-side PNGs.")
    ap.add_argument("--title-left", default="Left", help="Title for the left panel.")
    ap.add_argument("--title-right", default="Right", help="Title for the right panel.")
    ap.add_argument(
        "--suffix",
        default="",
        help="Optional suffix for output filenames, e.g. '_3d' when comparing 3D proxy renders.",
    )
    ap.add_argument("--dpi", type=int, default=180, help="Output DPI.")
    ap.add_argument(
        "--interp",
        choices=["nearest", "bilinear", "bicubic"],
        default="nearest",
        help="Interpolation used when displaying the input PNGs before saving.",
    )
    args = ap.parse_args(argv)

    names = _parse_names(args.names)
    if not names:
        raise SystemExit("No names provided")

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    caption = (
        "Left uses per-galaxy radial extent (panel fills its own R_data). "
        "Right uses a shared physical frame; outside the observed radius is masked."
    )

    for name in names:
        left_png = os.path.join(args.left_dir, f"{name}.png")
        right_png = os.path.join(args.right_dir, f"{name}.png")
        out_png = os.path.join(out_dir, f"{name}{args.suffix}_side_by_side.png")
        _save_side_by_side(
            left_png,
            right_png,
            out_png,
            name=name,
            title_left=args.title_left,
            title_right=args.title_right,
            caption=caption,
            dpi=args.dpi,
            interpolation=args.interp,
        )

    print(f"Wrote side-by-side PNGs to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
