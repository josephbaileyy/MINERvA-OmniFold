"""Render the deck's two figures directly from the frozen receipts.

Nothing is hardcoded: every plotted value is read from a receipt at run time, so a
figure cannot drift away from the number it illustrates. Two presentation choices are
deliberate and are drawn, not omitted:

* the typed-object cap-binding fraction is an interval, so it is drawn as an interval;
* the per-arm cost ratios are compared against the measurement's own resolution floor,
  estimated from the arm-A/arm-B null contrast, which is shaded behind the bars. A bar
  inside that band is not a measured difference.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OURS = "#1f4e79"
THEIRS = "#a6611a"
MUTED = "#999999"


def cap_figure(budget: dict, out: Path) -> None:
    """How often each project's token cap binds, and what ours discards."""
    fig, (left, right) = plt.subplots(1, 2, figsize=(9.2, 3.5))
    rows = budget["rows"]
    labels = [r["role"].upper() for r in rows]
    x = range(len(rows))

    cluster = [r["cluster_cloud"]["binds"] for r in rows]
    low = [r["typed_objects"]["binds_at_least"] for r in rows]
    high = [r["typed_objects"]["binds_at_most"] for r in rows]

    width = 0.34
    left.bar([i - width / 2 for i in x], cluster, width, color=OURS,
             label=f"ours: clusters, cap {budget['our_cap']}")
    left.bar([i + width / 2 for i in x], high, width, color=THEIRS, alpha=0.35)
    left.bar([i + width / 2 for i in x], low, width, color=THEIRS,
             label=f"Gregor: typed objects, cap {budget['typed_cap']} (interval)")
    for i, (lo, hi) in enumerate(zip(low, high)):
        left.plot([i + width / 2, i + width / 2], [lo, hi], color="k", lw=1.2)
        left.plot([i + width / 2], [hi], marker="_", color="k", ms=10)
    for i, v in enumerate(cluster):
        left.text(i - width / 2, v + 0.02, f"{v:.0%}", ha="center", fontsize=9)
    left.set_xticks(list(x))
    left.set_xticklabels(labels)
    left.set_ylim(0, 1.18)
    left.set_ylabel("fraction of events where the cap binds")
    left.set_title("The cap binds far more often for us", fontsize=10)
    left.legend(fontsize=7.5, loc="upper left", framealpha=1.0)

    med = [r["cluster_cloud"]["discarded_energy_share_median"] for r in rows]
    right.bar(labels, med, 0.45, color=OURS)
    for i, v in enumerate(med):
        right.text(i, v + 0.012, f"{v:.0%}", ha="center", fontsize=9)
    right.set_ylim(0, 0.65)
    right.set_ylabel("median share of non-muon\ncluster energy discarded")
    right.set_title("What our 12-token cap throws away", fontsize=10)
    right.text(0.5, 0.92, "bounds how much the cap COULD matter;\n"
                          "does not establish predictive importance",
               transform=right.transAxes, ha="center", va="top",
               fontsize=7.5, color=MUTED, style="italic")

    for axis in (left, right):
        axis.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, 0.005,
             "Unselected, unweighted tuple entries: 17,930 data (1B) + 186,439 MC (1A). "
             "Not the selected population.",
             ha="center", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(out, dpi=200)
    plt.close(fig)


def cost_figure(cost: dict, out: Path) -> None:
    """Per-arm GPU cost relative to the incumbent, against the resolution floor."""
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5), sharey=True)
    arms = ["B", "C", "D"]
    names = {"B": "B  typed,\npooled", "C": "C  typed,\nindividual",
             "D": "D  aggregate\noverflow"}
    panels = [("mean_multiplicity", "operating point (14 objects)"),
              ("tail_multiplicity", "tail (87 objects)")]

    # Resolution floor: arm B is computationally identical to arm A in the pooled
    # configuration, so its departure from 1.0 measures the noise, not an effect.
    floor = max(abs(cost["cost_summary"][key]["B"]["train_ratio_to_A"] - 1.0)
                for key, _ in panels)

    for axis, (key, title) in zip(axes, panels):
        summary = cost["cost_summary"][key]
        x = range(len(arms))
        width = 0.36
        train = [summary[a]["train_ratio_to_A"] for a in arms]
        infer = [summary[a]["inference_ratio_to_A"] for a in arms]
        axis.axhspan(1 - floor, 1 + floor, color=MUTED, alpha=0.25, zorder=0)
        axis.axhline(1.0, color="k", lw=0.8, zorder=1)
        axis.bar([i - width / 2 for i in x], train, width, color=OURS,
                 label="training", zorder=2)
        axis.bar([i + width / 2 for i in x], infer, width, color=THEIRS,
                 label="inference", zorder=2)
        for i, (t, f) in enumerate(zip(train, infer)):
            axis.text(i - width / 2, t + 0.03, f"{t:.2f}", ha="center", fontsize=8)
            axis.text(i + width / 2, f + 0.03, f"{f:.2f}", ha="center", fontsize=8)
        axis.set_xticks(list(x))
        axis.set_xticklabels([names[a] for a in arms], fontsize=8)
        axis.set_title(title, fontsize=10)
        axis.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("cost relative to arm A (incumbent)")
    axes[0].set_ylim(0, 2.15)
    axes[0].legend(fontsize=8, loc="upper left")
    fig.text(0.5, 0.055,
             f"Grey band: ±{floor:.1%}, the resolution of this measurement, estimated "
             "from the arm-A/arm-B null contrast. A bar inside it is not a difference.",
             ha="center", fontsize=7.5, color=MUTED, style="italic")
    fig.text(0.5, 0.008,
             "One A100, TF32 off, determinism on, float32. Cost is cost: "
             "a cheaper arm is not a better one.",
             ha="center", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.085, 1, 1))
    fig.savefig(out, dpi=200)
    plt.close(fig)


def main() -> None:
    """Render both figures from their receipts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=Path, required=True)
    parser.add_argument("--cost", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    cap_figure(json.loads(args.budget.read_text()), args.outdir / "fig-cap.png")
    cost_figure(json.loads(args.cost.read_text()), args.outdir / "fig-cost.png")
    print(f"wrote {args.outdir}/fig-cap.png and {args.outdir}/fig-cost.png")


if __name__ == "__main__":
    main()
