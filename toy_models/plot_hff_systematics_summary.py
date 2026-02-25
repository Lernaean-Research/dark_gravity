"""Plot compact summary of HFF κ–X-ray morphology systematics.

This script reads the already-generated per-team CSV grids and produces a simple
box/strip summary at ROI=100" for both clusters.

Outputs:
- toy_models/out_predictions/figures/hff_systematics_summary_roi100.png
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]

A2744_CSV = (
    ROOT
    / "toy_models"
    / "out_predictions"
    / "systematics"
    / "abell2744"
    / "systematics_summary.csv"
)
MACS0416_CSV = (
    ROOT
    / "toy_models"
    / "out_predictions"
    / "systematics"
    / "macs0416"
    / "systematics_summary.csv"
)

OUT_FIG = (
    ROOT
    / "toy_models"
    / "out_predictions"
    / "figures"
    / "hff_systematics_summary_roi100.png"
)


def _read_roi100_by_level(csv_path: Path) -> dict[int, list[float]]:
    by_level: dict[int, list[float]] = defaultdict(list)

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            roi = float(row["roi_radius_arcsec"])
            if not np.isclose(roi, 100.0):
                continue

            level = int(float(row["level_pct"]))
            sep = float(row["sep_arcsec"])
            by_level[level].append(sep)

    return dict(by_level)


def _add_box_and_points(ax: plt.Axes, by_level: dict[int, list[float]], title: str) -> None:
    levels = [95, 97, 99]
    data = [by_level.get(lvl, []) for lvl in levels]

    ax.boxplot(
        data,
        tick_labels=[str(lvl) for lvl in levels],
        showfliers=False,
        widths=0.55,
        medianprops={"linewidth": 2},
    )

    # Light jittered points (deterministic)
    rng = np.random.default_rng(0)
    for i, values in enumerate(data, start=1):
        if not values:
            continue
        x = rng.normal(loc=i, scale=0.06, size=len(values))
        ax.scatter(x, values, s=16, alpha=0.7)

    ax.set_title(title)
    ax.set_xlabel("Threshold percentile")
    ax.set_ylabel("κ–X-ray centroid separation (arcsec)")
    ax.grid(True, axis="y", alpha=0.25)


def main() -> None:
    a2744 = _read_roi100_by_level(A2744_CSV)
    macs = _read_roi100_by_level(MACS0416_CSV)

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    _add_box_and_points(axes[0], a2744, "Abell 2744 (ROI=100\")")
    _add_box_and_points(axes[1], macs, "MACS J0416.1−2403 (ROI=100\")")

    fig.suptitle("HFF κ–X-ray morphology operator: cross-team systematics", y=1.02)

    fig.savefig(OUT_FIG, dpi=200)
    plt.close(fig)

    print(f"Wrote: {OUT_FIG}")


if __name__ == "__main__":
    main()
