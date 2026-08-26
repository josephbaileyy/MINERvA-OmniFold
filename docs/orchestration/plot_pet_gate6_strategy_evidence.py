#!/usr/bin/env python3
"""Plot only committed PET Gate-6 evidence for the 2026-08-25 strategy review.

This is a read-only diagnostic renderer.  It does not apply a new gate, alter an
existing verdict, select members, or consume uncommitted training products.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/pet-gate6-strategy-mpl")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[2]
MEMBER_RECEIPT = REPO / "docs/orchestration/state/gate6-member-trajectories-result-56847059.json"
FLOOR_RECEIPT = REPO / "docs/orchestration/state/gate6-floor-replication-result-56863958.json"
ARCHIVED_LOG = (
    REPO
    / "docs/orchestration/runs/gate6traj-reconcile-56847059/logs/log_fe_nominal_nominal.txt"
)
DEFAULT_OUTPUT_DIR = REPO / "docs/orchestration/figures"
PROHIBITIONS = [
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
]


def load_evidence() -> dict:
    """Load and cross-check the three committed sources used by the figures."""
    members = json.loads(MEMBER_RECEIPT.read_text(encoding="utf-8"))
    floor = json.loads(FLOOR_RECEIPT.read_text(encoding="utf-8"))
    log_text = ARCHIVED_LOG.read_text(encoding="utf-8")

    if members["family_verdict"] != "BLOCK_GATE6_ML_ENSEMBLE":
        raise ValueError("member receipt no longer carries the blocked family verdict")
    if members["prohibitions_applied"] != PROHIBITIONS:
        raise ValueError("member-receipt prohibitions changed; refusing to render")
    if floor["prohibitions_still_live"] != PROHIBITIONS:
        raise ValueError("floor-receipt prohibitions changed; refusing to render")
    if floor["verdict"] != "FLOOR_INTERMEDIATE" or floor["gate6_unblocked_by_any_outcome"]:
        raise ValueError("floor receipt no longer has the expected non-licensing result")

    member_values = np.asarray(
        [m["end_to_end_achieved_over_required"] for m in members["members"]], dtype=float
    )
    floor_values = np.asarray(
        [
            [float(floor["statistics"][str(i)]["values_by_draw"][str(d)]) for i in range(3)]
            for d in range(1, 6)
        ],
        dtype=float,
    )
    floor_range = np.asarray(
        [float(floor["statistics"][str(i)]["F_range"]) for i in range(3)], dtype=float
    )
    floor_sd = np.asarray(
        [float(floor["statistics"][str(i)]["F_sd_ddof1"]) for i in range(3)], dtype=float
    )

    losses = np.asarray(
        [float(x) for x in re.findall(r"^Last val loss ([0-9.eE+-]+)$", log_text, re.MULTILINE)],
        dtype=float,
    )
    if losses.shape != (6,):
        raise ValueError(f"expected six logged validation-loss entries, found {len(losses)}")

    if not np.array_equal(floor_values[0], member_values[0]):
        raise ValueError("fixed-policy draw 1 no longer equals the reused Gate-6 member-1 trajectory")

    return {
        "member_values": member_values,
        "floor_values": floor_values,
        "floor_range": floor_range,
        "floor_sd": floor_sd,
        "reco_loss_entry": losses[0::2],
        "truth_loss_entry": losses[1::2],
    }


def _stamp(fig: plt.Figure) -> None:
    fig.text(
        0.5,
        0.012,
        "EXPLORATORY READOUT OF COMMITTED ARTIFACTS — GATE 6 REMAINS BLOCKED; "
        "NO MEMBER IS RECLASSIFIED",
        ha="center",
        va="bottom",
        fontsize=9,
        weight="bold",
        color="#8b1a1a",
    )


def plot_trajectories(evidence: dict, output_dir: Path) -> Path:
    iterations = np.arange(3)
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.0), sharex=True, sharey=True)

    for member, values in enumerate(evidence["member_values"], start=1):
        axes[0].plot(iterations, values, marker="o", linewidth=1.8, label=f"member {member}")
    axes[0].set_title("Gate-6 varied seed/subsample family")
    axes[0].legend(ncol=2, fontsize=8)

    for draw, values in enumerate(evidence["floor_values"], start=1):
        axes[1].plot(iterations, values, marker="o", linewidth=1.8, label=f"draw {draw}")
    axes[1].set_title("Fixed policy (42, 0), independent-process draws")
    axes[1].legend(ncol=2, fontsize=8)

    for ax in axes:
        ax.axhspan(0.9, 1.1, color="#c7e9c0", alpha=0.35, label="historical ±10% band")
        ax.axhline(1.0, color="black", linewidth=1.0, linestyle="--")
        ax.set_xticks(iterations)
        ax.set_xlabel("OmniFold iteration (zero based)")
        ax.grid(alpha=0.22)
    axes[0].set_ylabel(r"achieved / required normalization, $v_k$")
    fig.suptitle("Existing PET normalization trajectories", fontsize=14)
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    _stamp(fig)

    path = output_dir / "PET-GATE6-20260825-existing-trajectories.png"
    fig.savefig(path, dpi=180, metadata={"Software": "plot_pet_gate6_strategy_evidence.py"})
    plt.close(fig)
    return path


def plot_diagnostics(evidence: dict, output_dir: Path) -> Path:
    iterations = np.arange(3)
    fig, axes = plt.subplots(1, 3, figsize=(15.8, 4.9))

    for member, values in enumerate(evidence["member_values"], start=1):
        axes[0].plot(iterations, np.abs(values - 1.0), marker="o", linewidth=1.7,
                     label=f"member {member}")
    axes[0].axhline(0.1, color="#8b1a1a", linestyle="--", linewidth=1.0)
    axes[0].set_title("Historical absolute-deviation reading")
    axes[0].set_ylabel(r"$|v_k-1|$")
    axes[0].legend(ncol=2, fontsize=7)

    axes[1].plot(iterations, evidence["floor_range"], marker="o", label="range")
    axes[1].plot(iterations, evidence["floor_sd"], marker="s", label="sample SD")
    axes[1].set_yscale("log")
    axes[1].set_title("Fixed-policy process dispersion")
    axes[1].set_ylabel("dispersion across five draws")
    axes[1].legend(fontsize=8)

    axes[2].plot(iterations, evidence["reco_loss_entry"], marker="o", label="reco / step 1")
    axes[2].plot(iterations, evidence["truth_loss_entry"], marker="s", label="truth / step 2")
    axes[2].set_title("Single archived log: first val-loss entry")
    axes[2].set_ylabel("weighted validation loss")
    axes[2].legend(fontsize=8)
    axes[2].text(
        0.02,
        0.02,
        "Not best/final loss; engine logs\nhist.history['val_loss'][0]",
        transform=axes[2].transAxes,
        fontsize=8,
        va="bottom",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )

    for ax in axes:
        ax.set_xticks(iterations)
        ax.set_xlabel("OmniFold iteration (zero based)")
        ax.grid(alpha=0.22)
    fig.suptitle("What the committed diagnostics do—and do not—measure", fontsize=14)
    fig.tight_layout(rect=(0, 0.07, 1, 0.93))
    _stamp(fig)

    path = output_dir / "PET-GATE6-20260825-existing-diagnostics.png"
    fig.savefig(path, dpi=180, metadata={"Software": "plot_pet_gate6_strategy_evidence.py"})
    plt.close(fig)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate sources without rendering")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    evidence = load_evidence()
    if args.check:
        print("PASS: committed PET Gate-6 evidence and exact prohibitions are internally consistent")
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for path in (
        plot_trajectories(evidence, args.output_dir),
        plot_diagnostics(evidence, args.output_dir),
    ):
        print(path.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
