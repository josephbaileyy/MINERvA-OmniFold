"""Compute a powered-closure reference ceiling, and show why one cannot be inherited.

The powered closure's recovery is scored against a *reference ceiling*: a model of the
fraction of an injected truth-level displacement that is reachable after ``k`` OmniFold
iterations, given each cell's reco acceptance.

**IT IS A REFERENCE MODEL, NOT A PROVEN BOUND.** The construction assumes the only route
to a cell's displacement is data entering through that cell's acceptance. It is not an
upper limit on attainable recovery: `omnifold.py:218-220` lets a smooth learner transport
a tilt *across* cells, and BEN-038 measured a band whose signed response was
``E_w[r] = 1.0333`` -- above the value this model calls reachable. So a recovery figure
is quoted *relative to a reference*, exceeding it is possible, and the model is graded
ASSUMED in `FINDING-20260806-niter4-decision.md`. Nothing here may be cited as a ceiling
in the sense of a bound. For a cell with acceptance ``a`` the
uncorrected prior weight after ``k`` iterations is ``(1-a)**k``, so the attainable
fraction is ``1 - (1-a)**k``, and the ceiling is the weighted mean of that over cells:

    ceiling(k, w) = sum_b w_b * (1 - (1 - a_b)**k) / sum_b w_b

**The weight is not free.** For an L1 shape statistic the weight each cell carries is its
injected displacement ``|prior_b - target_b|`` -- so the ceiling is a property of the
*injection*, not of the grid. Change the injected variable and the displacement field
moves, and the ceiling moves with it.

This module exists to make that quantitative rather than cautionary. ``ceiling`` computes
the number; ``weighting_sensitivity`` reports it under several weightings so a reader can
see the range. On the committed extended-FPS acceptance map at ``k=3`` that range is
**0.017 to 0.973** -- essentially the whole interval -- which is why the pT injection's
adopted ceiling may not be carried over to an ``E_avail`` injection.

Validation, so this is not a second implementation of a rule nobody checked: with
``w = truth mass`` the function reproduces the committed
``ideal_recovery_percell_truthmass_weighted_by_k`` field of
``products/pet/fullevent_fps/acceptance_map_fullevent_fps.json`` to machine precision at
k = 1..4. ``verify_against_product`` performs that check and is exercised by the tests.

NOT a substitute for the real thing: the displacement field of an actual injection is
computable only from the input npz, which this module never reads. It takes a weight
field as an argument and says so.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

# The committed field this module validates itself against.
PRODUCT_FIELD = "ideal_recovery_percell_truthmass_weighted_by_k"
VALIDATION_TOLERANCE = 1e-12


def attainable_fraction(acceptance: Sequence[float], iterations: int) -> np.ndarray:
    """Per-cell ``1 - (1-a)**k``: the fraction of a displacement k iterations can reach."""
    if iterations < 1:
        raise ValueError(f"iterations must be >= 1, got {iterations}")
    a = np.asarray(acceptance, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("acceptance must be one-dimensional")
    if not np.all(np.isfinite(a)):
        raise ValueError("acceptance contains non-finite values")
    if np.any(a < 0.0) or np.any(a > 1.0):
        raise ValueError("acceptance must lie in [0, 1]")
    return 1.0 - (1.0 - a) ** int(iterations)


def ceiling(
    acceptance: Sequence[float],
    weights: Sequence[float],
    iterations: int,
) -> float:
    """Weighted-mean attainable fraction: the reference ceiling for one weighting.

    ``weights`` is the per-cell weight the *scoring statistic* applies. For an L1 shape
    criterion that is the injected displacement, which is why this is an argument and
    not a constant.
    """
    w = np.asarray(weights, dtype=np.float64)
    a = np.asarray(acceptance, dtype=np.float64)
    if w.shape != a.shape:
        raise ValueError(f"weights shape {w.shape} != acceptance shape {a.shape}")
    if not np.all(np.isfinite(w)):
        raise ValueError("weights contain non-finite values")
    if np.any(w < 0.0):
        raise ValueError("weights must be non-negative")
    total = float(w.sum())
    if total <= 0.0:
        raise ValueError("weights sum to zero; the ceiling is undefined")
    return float((w * attainable_fraction(a, iterations)).sum() / total)


def weighting_sensitivity(
    acceptance: Sequence[float],
    truth_mass: Sequence[float],
    iterations: int,
) -> dict[str, float]:
    """The ceiling under several weightings, to expose how much it depends on them.

    None of these is the ceiling for a real injection. They bracket it. The point of the
    bracket is that it is wide, so an inherited ceiling is not a conservative choice --
    it is an arbitrary one.
    """
    a = np.asarray(acceptance, dtype=np.float64)
    m = np.asarray(truth_mass, dtype=np.float64)
    populated = (m > 0).astype(np.float64)
    return {
        "truth_mass": ceiling(a, m, iterations),
        "uniform_over_populated_cells": ceiling(a, populated, iterations),
        "mass_times_one_minus_acceptance": ceiling(a, m * (1.0 - a), iterations),
        "mass_times_acceptance": ceiling(a, m * a, iterations),
        "mass_in_cells_with_acceptance_at_least_half": ceiling(
            a, np.where(a >= 0.5, m, 0.0), iterations
        ),
        "mass_in_cells_with_acceptance_below_five_percent": ceiling(
            a, np.where(a < 0.05, m, 0.0), iterations
        ),
    }


def verify_against_product(product: Mapping[str, Any]) -> dict[str, Any]:
    """Reproduce the committed truth-mass ceiling curve, or fail loudly.

    A reimplementation of a rule is only trustworthy if it reproduces a number somebody
    else committed. This is that check, and the tests run it.
    """
    a = product["acceptance_cells_pt_major"]
    m = product["truth_mass_cells_pt_major"]
    reference = product[PRODUCT_FIELD]
    checked: dict[str, Any] = {}
    for key, expected in reference.items():
        got = ceiling(a, m, int(key))
        deviation = abs(got - float(expected))
        checked[key] = {
            "recomputed": got,
            "product": float(expected),
            "deviation": deviation,
            "agrees": deviation <= VALIDATION_TOLERANCE,
        }
    failures = sorted(k for k, v in checked.items() if not v["agrees"])
    if failures:
        raise ValueError(
            f"recomputed ceiling disagrees with {PRODUCT_FIELD} at k={failures}; "
            "refusing to report a calibration this implementation cannot reproduce"
        )
    return checked


def main() -> None:
    """Validate against the committed product and report the weighting sensitivity."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance-map", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    product = json.loads(args.acceptance_map.read_text())
    validation = verify_against_product(product)
    sensitivity = weighting_sensitivity(
        product["acceptance_cells_pt_major"],
        product["truth_mass_cells_pt_major"],
        args.iterations,
    )
    values = list(sensitivity.values())

    receipt = {
        "scope": (
            "reference-model calibration procedure and its sensitivity to the scoring "
            "weight. NOT a reference for any particular injection -- the displacement "
            "field of a real injection is computable only from the input npz, which this "
            "module never reads."
        ),
        "reference_model_not_a_proven_bound": (
            "This construction assumes displacement reaches a cell only through that "
            "cell's acceptance. It is NOT an upper limit: omnifold.py:218-220 lets a "
            "smooth learner transport a tilt across cells, and BEN-038 measured a band at "
            "E_w[r] = 1.0333, above the modelled reachable value. Recovery is quoted "
            "relative to a reference; exceeding it is possible. Graded ASSUMED in "
            "FINDING-20260806-niter4-decision.md."
        ),
        "acceptance_map": {
            "path": str(args.acceptance_map),
            "n_cells": len(product["acceptance_cells_pt_major"]),
            "git_head": product.get("git_head"),
            "inputs_sha256": product.get("inputs_sha256"),
        },
        "iterations": args.iterations,
        "self_validation_against_product": validation,
        "ceiling_by_weighting": sensitivity,
        "range": {"min": min(values), "max": max(values), "spread": max(values) - min(values)},
        "conclusion": (
            "At these iterations the ceiling spans nearly the whole unit interval purely "
            "as a function of where the injected displacement sits. An inherited ceiling "
            "is therefore arbitrary rather than conservative, and a new injection "
            "variable requires a newly calibrated ceiling."
        ),
        "not_ratified": [
            "No reference value here is adopted for any endpoint.",
            "The scoring domain for an E_avail injection is an open scientific choice.",
            "Neither the tolerance nor the seed scatter of the pT endpoint transfers.",
        ],
    }
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"self-validation against {PRODUCT_FIELD}: PASS "
          f"(k={sorted(validation, key=int)})")
    for name, value in sensitivity.items():
        print(f"  {name:48s} {value:.6f}")
    print(f"range {min(values):.6f} .. {max(values):.6f} "
          f"(spread {max(values) - min(values):.6f})")


if __name__ == "__main__":
    main()
