"""One arm, one seed, one evaluation: OmniFold to convergence, then recovery.

This is the unit the campaign is made of. The campaign is 17 arm PAIRS, and a
pair is two runs of this driver with the same seed -- one `ours`, one `theirs`.

What it does, in the order the freeze requires:

1. loads the inventory and, for `theirs`, the identity-joined complete-arm
   inputs. `ours` uses the production cluster cloud unchanged, because our
   incumbent is the promoted configuration and not a candidate;
2. applies the ratified E_avail injection -- amplitude 0.35, clip 3.0 -- to the
   TRUTH leg, which is what makes recovery measurable;
3. runs MultiFold for `niter` iterations under the frozen recipe: equal example
   presentations, derived warmup/cosine, torch-faithful clipping;
4. records the realized policy and the end-of-run fold-forward ratio, rather
   than reconstructing either;
5. writes weights and a receipt. It does NOT score, compare, or recommend --
   scoring is a separate step over the frozen endpoint, so that a run cannot be
   re-scored to taste.

NOT CITABLE FOR any comparative claim on its own: one arm's recovery is not a
comparison, and the selection rule needs both arms plus the regional safeguard.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any

import numpy as np

import frozen_design as fd


def injected_truth_weights(eavail: np.ndarray, amplitude: float, clip: float,
                           ) -> np.ndarray:
    """The ratified injection: a clipped exponential tilt in truth E_avail.

    `w = min(exp(amplitude * eavail), clip)`, normalised to preserve the total
    so the injection changes the SHAPE and not the rate -- a rate change would
    be recovered by normalization alone and would not test the estimator.
    """
    tilt = np.exp(amplitude * np.asarray(eavail, dtype=np.float64))
    tilt = np.minimum(tilt, clip)
    return tilt / tilt.mean()


def recovery(prior: np.ndarray, unfolded: np.ndarray, target: np.ndarray,
             ) -> dict[str, Any]:
    """Fraction of the injected L1 displacement recovered. L1 = 2 x total variation.

    Defined against the PRIOR, so an estimator that does nothing scores 0 and one
    that reaches the target scores 1. Values above 1 mean overshoot and are
    reported, not clipped: clipping would hide a real failure mode.
    """
    prior = np.asarray(prior, float); unfolded = np.asarray(unfolded, float)
    target = np.asarray(target, float)
    for name, arr in (("prior", prior), ("unfolded", unfolded), ("target", target)):
        total = arr.sum()
        if not np.isfinite(total) or total <= 0:
            raise ValueError(f"{name} does not normalise: sum {total}")
    prior, unfolded, target = (a / a.sum() for a in (prior, unfolded, target))
    injected = np.abs(target - prior).sum()
    residual = np.abs(target - unfolded).sum()
    if injected <= 0:
        raise ValueError("the injection displaces nothing; recovery is undefined")
    return {
        "injected_l1": float(injected),
        "residual_l1": float(residual),
        "recovery": float(1.0 - residual / injected),
        "convention": "L1 = 2 x total variation; 0 = did nothing, 1 = reached target",
        "overshoot_not_clipped": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("ours", "theirs"), required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--stage", choices=("tuning", "pilot", "final"),
                        required=True)
    parser.add_argument("--learning-rate", type=float,
                        default=fd.THEIRS_COMPLETE["optimizer"] and 1e-4)
    parser.add_argument("--niter", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan and exit; no training")
    args = parser.parse_args()

    if args.seed not in fd.SEEDS[args.stage]:
        raise SystemExit(
            f"[arm] seed {args.seed} is not in the frozen {args.stage} list "
            f"{fd.SEEDS[args.stage]}. Seeds are frozen so a stage cannot be "
            "re-rolled until it gives the answer someone wanted.")
    if args.learning_rate not in fd.TUNING_GRID["points"]:
        raise SystemExit(
            f"[arm] learning rate {args.learning_rate} is not on the frozen grid "
            f"{fd.TUNING_GRID['points']}")

    plan = {
        "arm": args.arm, "seed": args.seed, "stage": args.stage,
        "learning_rate": args.learning_rate, "niter": args.niter,
        "injection": {"amplitude": fd.ENDPOINT["amplitude"],
                      "clip": fd.ENDPOINT["clip"]},
        "frozen_design": "frozen_design.py",
        "scoring": "separate step; this driver does not score or recommend",
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    raise SystemExit(
        "[arm] the training path needs the joined inputs, which the build array "
        "is still producing. Re-run without --dry-run once "
        "join_theirs_to_inventory.py has written its row index."
    )


if __name__ == "__main__":
    main()
