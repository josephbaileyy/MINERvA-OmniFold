"""Campaign GPU-hours from a measured profile receipt, computed rather than typed.

Every cost figure in this lane's documents has been arithmetic I did in prose, and
one of them was wrong by 1.6x before the realized-policy check caught it. This
turns a `profile_ported_step.py` receipt into the campaign table directly, so the
document quotes a computation and a reader can re-run it.

It imports the budget model from `calibrate_cost` rather than restating it. The
stage table is the one in `COST_UPDATE-20260919.md` §4 and is stated here once.

NOT CITABLE FOR any performance or adoption claim. This converts measured
throughput into projected hours under a stated budget; it measures nothing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from calibrate_cost import (
    DATA_LEG_FACTOR,
    EXAMPLES_PER_EVALUATION,
    INFERENCE_EXAMPLES_PER_EVALUATION,
)

# `COST_UPDATE-20260919.md` §4: 4 tuning + 4 variance-pilot + 1 controls + 8 final
# paired seeds. A "pair" is one evaluation of each arm.
CAMPAIGN_STAGES = {
    "tuning, 4 trials per arm": 4,
    "variance pilot, 4 paired seeds": 4,
    "controls (V2 fold-forward, V4, V5, V8, V9)": 1,
    "final comparison, 8 paired seeds": 8,
}
PAIRS = sum(CAMPAIGN_STAGES.values())
RETRY_ALLOWANCE = 0.25
CEILING_GPU_HOURS = 600.0


def _seconds_per_example(cell: dict[str, Any], section: str) -> float | None:
    block = cell.get("sections", {}).get(section)
    if not block or "step_seconds_median" not in block:
        return None
    return block["step_seconds_median"] / cell["batch"]


def evaluation_hours(train_seconds_per_example: float,
                     inference_seconds_per_example: float,
                     data_leg_factor: float = 1.0) -> dict[str, float]:
    """One arm's hours for one evaluation: fits plus reweighting plus validation."""
    fit = train_seconds_per_example * EXAMPLES_PER_EVALUATION * data_leg_factor / 3600.0
    inference = (inference_seconds_per_example
                 * INFERENCE_EXAMPLES_PER_EVALUATION * data_leg_factor / 3600.0)
    return {"fit_gpu_hours": fit, "inference_gpu_hours": inference,
            "evaluation_gpu_hours": fit + inference}


def campaign(pair_hours: float) -> dict[str, float]:
    subtotal = PAIRS * pair_hours
    return {
        "pairs": PAIRS,
        "gpu_hours_per_pair": pair_hours,
        "subtotal_gpu_hours": subtotal,
        "retries_gpu_hours": RETRY_ALLOWANCE * subtotal,
        "total_gpu_hours": (1.0 + RETRY_ALLOWANCE) * subtotal,
        "ceiling_gpu_hours": CEILING_GPU_HOURS,
        "fits_under_ceiling": (1.0 + RETRY_ALLOWANCE) * subtotal <= CEILING_GPU_HOURS,
    }


def project(receipt: dict[str, Any], theirs: str, ours: str, tokens: int,
            batch: int, data_leg_factor: float = 1.0,
            theirs_inference: str | None = None) -> dict[str, Any]:
    """Project one (their-variant, our-variant, tokens, batch) combination.

    `theirs_inference` exists because gradient accumulation is a TRAINING
    arrangement: the `accum4` variant has no forward cell, and inference for that
    arm is the same network without accumulation. It must be named rather than
    guessed, and it is recorded in the result.
    """
    cells = receipt["cells"]

    def need(variant: str, mode: str) -> dict[str, Any]:
        key = f"{variant}|{tokens}|{batch}|{mode}"
        cell = cells.get(key)
        if cell is None or cell.get("failed"):
            raise SystemExit(
                f"[project] {key} is absent or failed. A projection built on a "
                "missing cell would be a guess wearing a table."
            )
        return cell

    their_train = need(theirs, "train")
    their_infer = need(theirs_inference or theirs, "forward")
    our_train = need(ours, "train")
    our_infer = need(ours, "forward")

    train_section = ("virtual_batch_train"
                     if "virtual_batch_train" in their_train["sections"]
                     else "full_step")
    theirs_hours = evaluation_hours(
        _seconds_per_example(their_train, train_section),
        _seconds_per_example(their_infer, "forward"), data_leg_factor)
    ours_hours = evaluation_hours(
        _seconds_per_example(our_train, "full_step"),
        _seconds_per_example(our_infer, "forward"), data_leg_factor)
    pair = theirs_hours["evaluation_gpu_hours"] + ours_hours["evaluation_gpu_hours"]

    return {
        "theirs_variant": theirs, "ours_variant": ours,
        "theirs_inference_variant": theirs_inference or theirs,
        "tokens": tokens, "batch": batch,
        "their_train_section": train_section,
        "data_leg_factor": data_leg_factor,
        "ratio_train_per_example": (
            _seconds_per_example(their_train, train_section)
            / _seconds_per_example(our_train, "full_step")),
        "ratio_inference_per_example": (
            _seconds_per_example(their_infer, "forward")
            / _seconds_per_example(our_infer, "forward")),
        "theirs": theirs_hours, "ours": ours_hours,
        "campaign": campaign(pair),
        "stages": dict(CAMPAIGN_STAGES),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--theirs", default="optimised")
    parser.add_argument("--theirs-inference",
                        help="variant to take his inference from; accumulation is a "
                             "training arrangement and has no forward cell")
    parser.add_argument("--ours", default="ours_incumbent")
    parser.add_argument("--tokens", type=int, default=33)
    parser.add_argument("--batch", type=int, default=2048)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    receipt = json.loads(args.profile.read_text())
    result = {
        "assumed_data_leg": project(receipt, args.theirs, args.ours, args.tokens,
                                    args.batch, 1.0, args.theirs_inference),
        "neighbouring_product_data_leg": project(receipt, args.theirs, args.ours,
                                                 args.tokens, args.batch,
                                                 DATA_LEG_FACTOR,
                                                 args.theirs_inference),
        "data_leg_note": (
            "the second is the 5-D point-cloud product's measured data leg, which is "
            "a neighbouring product and not this schema; both are reported because "
            "neither is a reading of the fullevent data leg"
        ),
    }
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text + "\n")
    for name, block in (("assumed n_data = n_mc", result["assumed_data_leg"]),
                        ("n_data from the 5-D product",
                         result["neighbouring_product_data_leg"])):
        c = block["campaign"]
        print(f"{name}: pair {c['gpu_hours_per_pair']:.2f} GPU-h, "
              f"{c['pairs']} pairs + {int(100 * RETRY_ALLOWANCE)}% retries = "
              f"{c['total_gpu_hours']:.0f} against {c['ceiling_gpu_hours']:.0f} "
              f"({'FITS' if c['fits_under_ceiling'] else 'OVER'})")


if __name__ == "__main__":
    main()
