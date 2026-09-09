#!/usr/bin/env python3
"""Plot recorded repository activity and committed scientific receipt summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
FIGURES = HERE / "figures"
INK = "#182A35"
TEAL = "#147D83"
ORANGE = "#CB653C"
BLUE = "#547CA3"
GRAY = "#B5BCBF"
PAPER = "#FAF9F5"


def save_figure(figure: Any, name: str) -> None:
    """Save a figure as both a vector PDF and a high-resolution PNG."""
    for suffix in ("pdf", "png"):
        figure.savefig(FIGURES / f"{name}.{suffix}", dpi=220, facecolor=PAPER)
    plt.close(figure)


def plot_activity(metrics: dict[str, Any]) -> None:
    """Plot commit counts and path-touch shares without a causal breakpoint."""
    rows = metrics["monthly"]
    positions = np.arange(len(rows))
    labels = ["Apr*", "May", "Jun", "Jul", "Aug", "Sep 1–8*"]
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    counts = [row["nonmerge_commits"] for row in rows]
    bars = axes[0].bar(positions, counts, color=TEAL, width=0.64)
    for index in (0, 5):
        bars[index].set_hatch("///")
        bars[index].set_edgecolor(PAPER)
    axes[0].bar_label(bars, labels=[f"{value:,}" for value in counts], padding=6)
    axes[0].set_ylim(0, max(counts) * 1.2)
    axes[0].set_title("Recorded activity", loc="left", fontweight="bold", pad=15)
    axes[0].set_ylabel("Non-merge commits")
    groups = [
        "Analysis directories",
        "Orchestration directories",
        "Presentation / note",
        "Other paths",
    ]
    bottoms = np.zeros(len(rows))
    totals = np.array([sum(row[group] for group in groups) for row in rows])
    for group, color in zip(groups, (TEAL, ORANGE, BLUE, GRAY), strict=True):
        shares = np.array([row[group] for row in rows]) / totals * 100
        axes[1].bar(
            positions, shares, bottom=bottoms, color=color, label=group, width=0.64
        )
        if group == "Orchestration directories":
            for index in (3, 4, 5):
                axes[1].text(
                    index,
                    bottoms[index] + shares[index] / 2,
                    f"{shares[index]:.0f}%",
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                    fontsize=12,
                )
        bottoms += shares
    axes[1].set_title("Where files were touched", loc="left", fontweight="bold", pad=15)
    axes[1].set_ylabel("Share of commit/path touches (%)")
    axes[1].set_ylim(0, 100)
    axes[1].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=2,
        frameon=False,
        fontsize=9,
    )
    for axis in axes:
        axis.set_xticks(positions, labels)
        axis.spines[["top", "right"]].set_visible(False)
        axis.set_axisbelow(True)
        axis.grid(axis="y", alpha=0.15)
    save_figure(figure, "activity")


def plot_agreement(metrics: dict[str, Any]) -> None:
    """Plot cumulative central-value agreement counts over the fixed 205-bin mask."""
    science = metrics["scientific"]
    counts = science["agreement_counts"]
    denominator = science["agreement_n"]
    figure, axis = plt.subplots(figsize=(7, 3.5), layout="constrained")
    percents = np.array(counts) / denominator * 100
    bars = axis.barh([2, 1, 0], percents, color=[TEAL, BLUE, GRAY], height=0.52)
    axis.set_yticks([2, 1, 0], ["Within 5%", "Within 10%", "Within 20%"])
    for bar, count, percent in zip(bars, counts, percents, strict=True):
        axis.text(
            4,
            bar.get_y() + bar.get_height() / 2,
            f"{count}/{denominator} bins  ·  {percent:.1f}%",
            va="center",
            color="white" if count < 200 else INK,
            fontweight="bold",
            fontsize=14,
        )
    axis.set_xlim(0, 100)
    axis.set_xlabel("Cumulative share of reported bins (%)")
    axis.set_title(
        "How close are the central values?", loc="left", pad=14, fontweight="bold"
    )
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.set_axisbelow(True)
    axis.grid(axis="x", alpha=0.15)
    save_figure(figure, "agreement")


def plot_checkpoint(metrics: dict[str, Any]) -> None:
    """Plot event-level checkpoint disagreements from a historical diagnostic run."""
    quantiles = metrics["scientific"]["checkpoint_quantiles"]
    values = [100 * value for value in quantiles.values()]
    figure, axis = plt.subplots(figsize=(7, 3.8), layout="constrained")
    bars = axis.bar(
        ["Median", "90th percentile", "99th percentile", "Maximum"],
        values,
        color=[TEAL, BLUE, ORANGE, ORANGE],
        width=0.55,
    )
    axis.bar_label(
        bars,
        labels=[f"{value:.2f}%" if value < 1 else f"{value:.1f}%" for value in values],
        padding=7,
        fontsize=13,
    )
    axis.set_ylim(0, 103)
    axis.set_ylabel("Relative difference in event weight (%)")
    axis.set_title(
        "Stored weights versus saved-model inference",
        loc="left",
        pad=16,
        fontweight="bold",
        fontsize=14,
    )
    axis.spines[["top", "right"]].set_visible(False)
    axis.set_axisbelow(True)
    axis.grid(axis="y", alpha=0.15)
    save_figure(figure, "checkpoint")


def plot_scope(metrics: dict[str, Any]) -> None:
    """Show tracked Python file stock, explicitly treating it as a size measure."""
    rows = metrics["snapshots"]
    figure, axis = plt.subplots(figsize=(10, 4), layout="constrained")
    positions = np.arange(len(rows))
    bottoms = np.zeros(len(rows))
    for group, color in zip(
        [
            "Analysis directories",
            "Orchestration directories",
            "Presentation / note",
            "Other paths",
        ],
        [TEAL, ORANGE, BLUE, GRAY],
        strict=True,
    ):
        counts = np.array([row[group] for row in rows])
        axis.bar(
            positions, counts, bottom=bottoms, color=color, label=group, width=0.62
        )
        bottoms += counts
    for index, total in enumerate(bottoms):
        axis.text(index, total + 10, f"{int(total)}", ha="center", fontsize=13)
    axis.set_xticks(
        positions, ["Apr 30", "May 31", "Jun 30", "Jul 31", "Aug 31", "Sep 8"]
    )
    axis.set_ylim(0, max(bottoms) * 1.18)
    axis.set_ylabel("Tracked Python files")
    axis.legend(frameon=False, loc="upper left", fontsize=10)
    axis.spines[["top", "right"]].set_visible(False)
    axis.set_axisbelow(True)
    axis.grid(axis="y", alpha=0.15)
    save_figure(figure, "scope")


def plot_normalization() -> None:
    """Render the bin-area integration formula with mathematical typography."""
    figure = plt.figure(figsize=(12, 0.8))
    figure.text(
        0.5,
        0.45,
        r"$\sigma = \sum_{i,j}\;\left[\frac{d^2\sigma}{dp_T\,dp_{\parallel}}\right]_{ij}"
        r"\;\Delta p_{T,i}\;\Delta p_{\parallel,j}$",
        ha="center",
        va="center",
        color=TEAL,
        fontsize=28,
    )
    save_figure(figure, "normalization")


def plot_corner() -> None:
    """Plot recorded corner-integrated ratios without unadopted covariance bars."""
    rows = json.loads((HERE / "measurements/corner_comparison.json").read_text())[
        "records"
    ]
    figure, axis = plt.subplots(figsize=(10.8, 3.8), layout="constrained")
    ratios = [row["ratio"] for row in rows]
    positions = np.arange(len(rows))[::-1]
    axis.axvline(1, color=INK, linewidth=1.3, linestyle="--")
    axis.scatter(ratios, positions, s=115, color=[TEAL, ORANGE, BLUE, INK], zorder=3)
    for position, ratio in zip(positions, ratios, strict=True):
        axis.text(
            ratio + 0.025,
            position,
            f"{ratio:.3f}",
            va="center",
            fontsize=15,
            fontweight="bold",
        )
    axis.set_yticks(positions, [row["generator"] for row in rows], fontsize=14)
    axis.set_xlim(0.9, 1.8)
    axis.set_ylim(-0.6, 3.8)
    axis.text(1.015, 3.55, "Equal central values", fontsize=11, color=INK)
    axis.set_xlabel("Integrated unfolded data / generator", fontsize=14)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)
    axis.grid(axis="x", alpha=0.15)
    axis.set_axisbelow(True)
    save_figure(figure, "corner_comparison")


def main() -> None:
    """Build the summary figures from the frozen measurement file."""
    FIGURES.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 12,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "axes.facecolor": PAPER,
            "figure.facecolor": PAPER,
        }
    )
    metrics = json.loads((HERE / "measurements/metrics.json").read_text())
    plot_agreement(metrics)
    plot_activity(metrics)
    plot_checkpoint(metrics)
    plot_scope(metrics)
    plot_normalization()
    plot_corner()
    print(f"Wrote six PNG/PDF figures for revision {metrics['revision']}")


if __name__ == "__main__":
    main()
