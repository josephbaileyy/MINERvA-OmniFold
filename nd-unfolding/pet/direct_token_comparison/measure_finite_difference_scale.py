"""Measure the achievable finite-difference accuracy, to set a tolerance from data.

A finite-difference gradient check needs a tolerance, and asserting one is how a
guard ends up either firing on every correct run or never firing at all. Central
differences in float32 trade two errors against each other: truncation falls as
``h^2`` while cancellation in ``L(x+h) - L(x-h)`` grows as ``eps/h``, so the accuracy
curve is V-shaped and its floor -- not a round number -- is what a tolerance must
respect.

This sweeps the step size, reports the relative error against the analytic gradient
at each step, and records where the floor is and how wide the plateau around it is.
The frozen criterion is then set above the measured floor with margin, and the step
size is set at the measured optimum rather than guessed.

Parameters with tiny gradients are reported separately rather than dropped: their
relative error is dominated by the denominator and says nothing about correctness,
which is why the criterion applies only above a gradient floor that this measures too.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
from typing import Any

import numpy as np

STEPS = (3e-1, 1e-1, 3e-2, 1e-2, 5e-3, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5)


def _install(checkout: Path) -> None:
    """Put the checkout's modules first."""
    for root in (
        checkout / "nd-unfolding" / "pet" / "direct_token_comparison",
        checkout / "nd-unfolding" / "pet",
    ):
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        sys.path.insert(0, str(root))


def build(modules: dict[str, Any], width: tuple[int, ...], rows: int, routing: str):
    """Build one model and its inputs at a uniform typed width."""
    fourarm, typed = modules["fourarm"], modules["typed"]
    adapter, runner = modules["adapter"], modules["runner"]
    comparison, tf = modules["comparison"], modules["tf"]
    counts = np.tile(np.asarray(width, dtype=np.int64), (rows, 1))
    batch = fourarm.build_variable_typed_batch(typed, counts, seed=2401)
    rng = np.random.default_rng(2401)
    event = rng.normal(size=(rows, 13)).astype(np.float32)
    inputs = dict(adapter.prepare_keras_inputs(batch, event))
    inputs.update(
        generic_values=rng.normal(size=(rows, 12, 5)).astype(np.float32),
        generic_mask=np.ones((rows, 12), dtype=bool),
    )
    truth = rng.normal(size=(rows, 2)).astype(np.float32)
    target = np.exp(0.4 * np.tanh(truth[:, 0] * truth[:, 1])).astype(np.float32)
    norm = typed.fit_frozen_normalization_for_smoke(
        batch, fit_inventory_row_selection_digest=runner.digest_arrays([truth])
    )
    tf.keras.utils.set_random_seed(2401)
    model = comparison.build_comparison(norm, routing=routing)
    model(inputs)
    return model, inputs, target


def loss_of(modules: dict[str, Any], model: Any, inputs: Any, target: Any) -> float:
    """Mean squared error, accumulated in float64.

    The forward pass stays float32 -- that is the thing under test -- but summing the
    residuals in float64 removes an accumulation error that would otherwise be
    charged to the gradient.
    """
    tf = modules["tf"]
    predicted = np.asarray(model(inputs, training=False), dtype=np.float64).reshape(-1)
    del tf
    return float(np.mean((predicted - np.asarray(target, dtype=np.float64)) ** 2))


def analytic_gradients(modules: dict[str, Any], model: Any, inputs: Any, target: Any):
    """Return the analytic gradient of the same loss."""
    tf = modules["tf"]
    labels = tf.convert_to_tensor(np.asarray(target, dtype=np.float32).reshape(-1, 1))
    with tf.GradientTape() as tape:
        predicted = model(inputs, training=False)
        loss = tf.reduce_mean((tf.reshape(predicted, (-1, 1)) - labels) ** 2)
    return [np.asarray(g) for g in tape.gradient(loss, model.trainable_weights)]


def sweep(
    modules: dict[str, Any],
    model: Any,
    inputs: Any,
    target: Any,
    gradients: list[np.ndarray],
    samples: int,
    seed: int,
) -> dict[str, Any]:
    """Compare central differences against the analytic gradient at each step size."""
    rng = np.random.default_rng(seed)
    variables = model.trainable_weights
    coordinates = []
    for _ in range(samples):
        index = int(rng.integers(len(variables)))
        flat = int(rng.integers(variables[index].numpy().size))
        coordinates.append((index, flat))

    rows: list[dict[str, Any]] = []
    for step in STEPS:
        errors: list[dict[str, float]] = []
        for index, flat in coordinates:
            variable = variables[index]
            original = variable.numpy()
            analytic = float(gradients[index].reshape(-1)[flat])
            scale = max(abs(float(original.reshape(-1)[flat])), 1.0)
            h = step * scale
            shifted = original.copy().reshape(-1)
            shifted[flat] += h
            variable.assign(shifted.reshape(original.shape))
            plus = loss_of(modules, model, inputs, target)
            shifted[flat] -= 2 * h
            variable.assign(shifted.reshape(original.shape))
            minus = loss_of(modules, model, inputs, target)
            variable.assign(original)
            numeric = (plus - minus) / (2 * h)
            errors.append(
                {
                    "analytic": analytic,
                    "numeric": numeric,
                    "absolute": abs(numeric - analytic),
                    "relative": abs(numeric - analytic) / max(abs(analytic), 1e-12),
                }
            )
        rows.append({"step": step, "errors": errors})
    return {"coordinates": len(coordinates), "sweep": rows}


def summarize(sweep_result: dict[str, Any], floors: tuple[float, ...]) -> dict[str, Any]:
    """Report, per gradient floor, the best step size and the error there."""
    report: dict[str, Any] = {}
    for floor in floors:
        per_step = []
        for row in sweep_result["sweep"]:
            kept = [e for e in row["errors"] if abs(e["analytic"]) >= floor]
            if not kept:
                continue
            relatives = sorted(e["relative"] for e in kept)
            per_step.append(
                {
                    "step": row["step"],
                    "kept": len(kept),
                    "median_relative": statistics.median(relatives),
                    "p90_relative": relatives[min(len(relatives) - 1, int(0.9 * len(relatives)))],
                    "max_relative": relatives[-1],
                }
            )
        if not per_step:
            continue
        best = min(per_step, key=lambda r: r["p90_relative"])
        report[f"floor_{floor:g}"] = {
            "per_step": per_step,
            "best_step": best["step"],
            "best_p90_relative": best["p90_relative"],
            "best_max_relative": best["max_relative"],
            "kept_coordinates": best["kept"],
        }
    return report


def main() -> None:
    """Sweep the step size and write the measured basis for the tolerance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=256)
    parser.add_argument("--samples", type=int, default=24)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    _install(args.checkout)
    import four_arm_representation as fourarm
    import typed_descriptor_keras as adapter
    import typed_descriptors as typed
    import typed_token_comparison as comparison

    import run_typed_token_comparison as runner

    modules = {
        "fourarm": fourarm,
        "typed": typed,
        "adapter": adapter,
        "runner": runner,
        "comparison": comparison,
        "tf": adapter.require_tensorflow(),
    }

    measured: dict[str, Any] = {}
    for label, width, routing in (
        ("pooled_small", (1, 4, 2), "pooled"),
        ("direct_small", (1, 4, 2), "direct"),
        ("direct_large", (0, 32, 2), "direct"),
    ):
        model, inputs, target = build(modules, width, args.rows, routing)
        gradients = analytic_gradients(modules, model, inputs, target)
        result = sweep(modules, model, inputs, target, gradients, args.samples, 7)
        measured[label] = {
            "width": list(width),
            "routing": routing,
            "summary": summarize(result, (0.0, 1e-4, 1e-3, 1e-2)),
        }
        for floor, block in measured[label]["summary"].items():
            print(
                f"{label} {floor}: best step {block['best_step']:.0e}, "
                f"p90 relative {block['best_p90_relative']:.3e}, "
                f"max {block['best_max_relative']:.3e}, "
                f"n={block['kept_coordinates']}",
                flush=True,
            )
    receipt = {
        "scope": "measured basis for the finite-difference tolerance; no learning claim",
        "rows": args.rows,
        "samples_per_configuration": args.samples,
        "steps_swept": list(STEPS),
        "configurations": measured,
        "note": (
            "Central differences in float32 have a V-shaped accuracy curve: truncation "
            "falls as h^2, cancellation grows as eps/h. The tolerance must sit above "
            "the measured floor, and the gradient floor exists because relative error "
            "on a near-zero gradient measures the denominator, not correctness."
        ),
    }
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
