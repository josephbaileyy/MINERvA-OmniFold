"""Run reproducible synthetic OmniFold routing comparisons without ROOT access.

This deliberately has no real-input mode: release, object associations, selection,
weights and normalization must be resolved before a real-source driver is bound.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from numpy.typing import NDArray

import numpy as np

import typed_descriptor_keras as adapter
import typed_descriptors as typed
from typed_token_comparison import build_comparison


def digest_arrays(arrays: list[NDArray[Any]]) -> str:
    """Hash ordered dtype, shape and contiguous bytes."""
    digest = hashlib.sha256()
    for array in arrays:
        digest.update(str((array.dtype.str, array.shape)).encode())
        digest.update(np.ascontiguousarray(array).tobytes())
    return digest.hexdigest()


def make_fixture(
    rows: int, seed: int
) -> tuple[Any, NDArray[Any], NDArray[Any], NDArray[Any]]:
    """Build dimensionless synthetic objects with a noisy two-object conditional."""
    rng = np.random.default_rng(seed)
    truth = rng.normal(size=(rows, 2)).astype(np.float32)
    reco = truth + rng.normal(0, 0.15, size=truth.shape)
    collections: dict[str, list[list[dict[str, Any]]]] = {}
    for contract in typed.FAMILY_CONTRACTS:
        family_rows = []
        for row in range(rows):
            objects = []
            for index in range(2 if contract.name == "prongs" else 1):
                fields = {
                    field.name: ([1.0] * field.width if field.width > 1 else 1.0)
                    for field in contract.fields
                }
                if contract.name == "prongs":
                    fields.update(
                        raw_pid=3 if index == 0 else 8,
                        charge=2 if index == 0 else 0,
                        score=1.0,
                        mass=105.658 if index == 0 else 938.272,
                        time=float(reco[row, index]),
                    )
                objects.append(fields)
            family_rows.append(objects)
        collections[contract.name] = family_rows
    provenance = typed.RowProvenance(
        source_file_ordinal=np.ones(rows, dtype=np.uint32),
        source_tree=np.full(rows, typed.SourceTree.MASTER_ANA_DEV, dtype=np.uint8),
        source_entry=np.arange(rows, dtype=np.uint64),
    )
    batch = typed.build_descriptor_batch(
        provenance=provenance,
        photon_rows=collections["photons"],
        blob_rows=collections["blobs"],
        prong_rows=collections["prongs"],
    )
    # These inputs have no access to the injected two-prong conditional.
    event = rng.normal(size=(rows, 13)).astype(np.float32)
    generic = rng.normal(size=(rows, 12, 5)).astype(np.float32)
    return batch, event, generic, truth


def select_inputs(
    inputs: dict[str, NDArray[Any]], rows: NDArray[Any]
) -> dict[str, NDArray[Any]]:
    """Select rows and rebase packed token segments without dropping objects."""
    selected = {
        key: inputs[key][rows]
        for key in (adapter.DETECTOR_INPUT_KEY, "generic_values", "generic_mask")
    }
    for contract in typed.FAMILY_CONTRACTS:
        prefix = contract.name
        segment = inputs[f"{prefix}_segment_ids"]
        starts = np.searchsorted(segment, rows, side="left")
        ends = np.searchsorted(segment, rows, side="right")
        indices = np.concatenate(
            [np.arange(start, end) for start, end in zip(starts, ends)]
        )
        for suffix in ("values", "masks", "token_mask"):
            selected[f"{prefix}_{suffix}"] = inputs[f"{prefix}_{suffix}"][indices]
        selected[f"{prefix}_segment_ids"] = np.repeat(
            np.arange(len(rows), dtype=np.int32), ends - starts
        )
        for suffix in ("counts", "enabled"):
            selected[f"{prefix}_{suffix}"] = inputs[f"{prefix}_{suffix}"][rows]
    return selected


def diagnostics(prediction: NDArray[Any], target: NDArray[Any]) -> dict[str, Any]:
    """Report closure, tails and ESS; retain uncapped weights as the primary result."""
    if np.any(prediction <= 0) or not np.all(np.isfinite(prediction)):
        raise ValueError("Non-positive or non-finite prediction")
    tail = target >= np.quantile(target, 0.9)

    def ess(weights: NDArray[Any]) -> float:
        return float(weights.sum() ** 2 / np.square(weights).sum())

    return {
        "rows": len(target),
        "tail_rows": int(tail.sum()),
        "log_ratio_rmse": float(np.sqrt(np.mean(np.log(prediction / target) ** 2))),
        "normalization_ratio": float(prediction.sum() / target.sum()),
        "ess": ess(prediction),
        "target_ess": ess(target),
        "tail_ess": ess(prediction[tail]),
        "tail_target_ess": ess(target[tail]),
        "quantiles": np.quantile(prediction, [0.5, 0.99, 0.999, 1]).tolist(),
        "cap_diagnostics": {
            str(cap): {
                "count": int(np.sum(prediction > cap)),
                "weight_mass_fraction": float(
                    prediction[prediction > cap].sum() / prediction.sum()
                ),
                "ess": ess(np.minimum(prediction, cap)),
            }
            for cap in (10, 30)
        },
    }


def train_ratio(
    model: Any,
    inputs: Any,
    negative: NDArray[Any],
    positive: NDArray[Any],
    *,
    epochs: int,
    batch_size: int,
    seed: int,
    packed: bool,
) -> list[float]:
    """Fit weighted BCE with equal sampling priors and no per-class normalization."""
    tf = adapter.require_tensorflow()
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

    @tf.function(reduce_retracing=True)  # type: ignore[untyped-decorator]
    def step(features: Any, weight0: Any, weight1: Any) -> Any:
        with tf.GradientTape() as tape:
            logits = tf.reshape(model(features, training=True), [-1])
            loss = tf.reduce_mean(
                weight0 * tf.nn.softplus(logits) + weight1 * tf.nn.softplus(-logits)
            )
        gradients = tape.gradient(loss, model.trainable_variables)
        tf.debugging.assert_all_finite(loss, "Non-finite loss")
        for gradient in gradients:
            tf.debugging.assert_all_finite(gradient, "Non-finite gradient")
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))
        return loss

    rng = np.random.default_rng(seed)
    history = []
    for _ in range(epochs):
        order = rng.permutation(len(negative))
        losses = []
        for start in range(0, len(order), batch_size):
            rows = order[start : start + batch_size]
            features = select_inputs(inputs, rows) if packed else inputs[rows]
            losses.append(float(step(features, negative[rows], positive[rows])))
        history.append(float(np.mean(losses)))
    return history


def predict_ratio(
    model: Any, inputs: Any, *, packed: bool, batch_size: int
) -> NDArray[Any]:
    """Evaluate odds without clipping and reject overflow."""
    size = len(inputs[adapter.DETECTOR_INPUT_KEY]) if packed else len(inputs)
    parts = []
    for start in range(0, size, batch_size):
        rows = np.arange(start, min(start + batch_size, size))
        features = select_inputs(inputs, rows) if packed else inputs[rows]
        logits = np.asarray(model(features, training=False)).reshape(-1)
        if np.any(np.abs(logits) > 50) or not np.all(np.isfinite(logits)):
            raise ValueError("Log-odds outside [-50,50]; stop without clipping")
        parts.append(np.exp(logits.astype(np.float64)))
    return np.asarray(np.concatenate(parts), dtype=np.float32)


def run(args: argparse.Namespace) -> dict[str, Any]:
    """Run both routes with identical rows, initialization, truth network and budgets."""
    tf = adapter.require_tensorflow()
    started = time.monotonic()
    training_batch, training_event, training_generic, training_truth = make_fixture(
        args.rows, 2401
    )
    test_batch, test_event, test_generic, test_truth = make_fixture(
        args.test_rows, 2402
    )
    norm = typed.fit_frozen_normalization_for_smoke(
        training_batch,
        fit_inventory_row_selection_digest=digest_arrays([training_truth]),
    )
    train_inputs = adapter.prepare_keras_inputs(training_batch, training_event)
    test_inputs = adapter.prepare_keras_inputs(test_batch, test_event)
    for inputs, generic in (
        (train_inputs, training_generic),
        (test_inputs, test_generic),
    ):
        inputs.update(
            generic_values=generic, generic_mask=np.ones(generic.shape[:2], dtype=bool)
        )

    def target(truth: NDArray[Any]) -> NDArray[Any]:
        if args.mode == "ordinary":
            return np.ones(len(truth), dtype=np.float32)
        return np.asarray(
            np.exp(0.4 * np.tanh(truth[:, 0] * truth[:, 1])), dtype=np.float32
        )

    train_target, test_target = target(training_truth), target(test_truth)
    if args.mode == "shuffle":
        np.random.default_rng(2403).shuffle(train_target)
        # Shuffling removes the conditional in expectation, preserving its mass.
        test_target = np.full_like(test_target, float(train_target.mean()))
    results = {}
    initial_reco = None
    initial_truth = None
    for routing in ("pooled", "direct"):
        tf.keras.utils.set_random_seed(args.seed)
        model = build_comparison(norm, routing=routing)
        model(select_inputs(train_inputs, np.arange(min(2, args.rows))))
        truth_model = tf.keras.Sequential(
            [
                tf.keras.layers.Input((2,)),
                tf.keras.layers.Dense(32, activation="tanh"),
                tf.keras.layers.Dense(32, activation="tanh"),
                tf.keras.layers.Dense(1),
            ]
        )
        if initial_reco is None:
            initial_reco = model.get_weights()
            initial_truth = truth_model.get_weights()
        else:
            model.set_weights(initial_reco)
            truth_model.set_weights(initial_truth)
        push = np.ones(args.rows, dtype=np.float32)
        trajectories = []
        for iteration in range(args.iterations):
            # Controlled reset at each fit: all arms follow the same policy.
            model.set_weights(initial_reco)
            truth_model.set_weights(initial_truth)
            fit_start = time.monotonic()
            reco_losses = train_ratio(
                model,
                train_inputs,
                push,
                train_target,
                epochs=args.epochs,
                batch_size=args.batch_size,
                seed=args.seed + iteration,
                packed=True,
            )
            reco_fit_seconds = time.monotonic() - fit_start
            pull = push * predict_ratio(
                model, train_inputs, packed=True, batch_size=args.batch_size
            )
            fit_start = time.monotonic()
            truth_losses = train_ratio(
                truth_model,
                training_truth,
                np.ones_like(push),
                pull,
                epochs=args.epochs,
                batch_size=args.batch_size,
                seed=args.seed + iteration,
                packed=False,
            )
            truth_fit_seconds = time.monotonic() - fit_start
            push = predict_ratio(
                truth_model, training_truth, packed=False, batch_size=args.batch_size
            )
            heldout = predict_ratio(
                truth_model, test_truth, packed=False, batch_size=args.batch_size
            )
            metrics = diagnostics(heldout, test_target)
            metrics.update(
                reco_loss_history=reco_losses,
                truth_loss_history=truth_losses,
                reco_fit_seconds=reco_fit_seconds,
                truth_fit_seconds=truth_fit_seconds,
            )
            projections = {}
            for axis in range(2):
                bins = np.digitize(test_truth[:, axis], [-2, -1, 0, 1, 2])
                expected = np.bincount(bins, weights=test_target, minlength=6)
                observed = np.bincount(bins, weights=heldout, minlength=6)
                projections[str(axis)] = {
                    "counts": np.bincount(bins, minlength=6).tolist(),
                    "target": expected.tolist(),
                    "predicted": observed.tolist(),
                    "relative_l1": float(
                        np.abs(observed - expected).sum() / expected.sum()
                    ),
                }
            metrics["truth_projections"] = projections
            trajectories.append(metrics)
        np.savez(
            args.output.with_suffix(f".{routing}.npz"),
            push=push,
            heldout=heldout,
            target=test_target,
            truth=test_truth,
        )
        model.save(args.output.with_suffix(f".{routing}.keras"))
        truth_model.save(args.output.with_suffix(f".{routing}.truth.keras"))
        assert initial_truth is not None
        results[routing] = {
            "parameters": model.count_params(),
            "initial_reco_sha256": digest_arrays(initial_reco),
            "initial_truth_sha256": digest_arrays(initial_truth),
            "iterations": trajectories,
            "final_fold_forward_sum_w_push_reco": float(push.sum()),
            "final_fold_forward_sum_w_reco": float(args.rows),
            "n_pass_reco": args.rows,
            "final_push_sha256": digest_arrays([push]),
        }
    return {
        "evidence_class": "synthetic-method-development",
        "terminal": "COMPLETE",
        "code_sha256": {
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_bytes()
            ).hexdigest()
            for name in (
                "run_typed_token_comparison.py",
                "typed_token_comparison.py",
                "typed_descriptor_keras.py",
                "typed_descriptors.py",
            )
        },
        "normalization_sha256": hashlib.sha256(
            json.dumps(
                adapter.frozen_normalization_to_config(norm), sort_keys=True
            ).encode()
        ).hexdigest(),
        "artifacts": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in args.output.parent.glob(args.output.stem + ".*")
            if path.suffix in (".keras", ".npz")
        },
        "mode": args.mode,
        "seed": args.seed,
        "training_rows": args.rows,
        "test_rows": args.test_rows,
        "iterations": args.iterations,
        "epochs_per_fit": args.epochs,
        "batch_size": args.batch_size,
        "wall_seconds": time.monotonic() - started,
        "schema_digest": typed.descriptor_schema_digest(),
        "input_sha256": digest_arrays([train_inputs[k] for k in sorted(train_inputs)]),
        "truth_sha256": digest_arrays([training_truth, test_truth]),
        "selection": "synthetic all-pass, no background or native misses",
        "results": results,
        "non_claims": [
            "No real-source validation",
            "No publication adoption",
            "No uncertainty construction or coverage",
            "No Gate-6 work",
        ],
    }


def main() -> None:
    """Parse a synthetic-only run card and write a new result file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=128)
    parser.add_argument("--test-rows", type=int, default=64)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--mode", choices=("ordinary", "injected", "shuffle"), default="ordinary"
    )
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name in ("rows", "test_rows", "epochs", "iterations", "batch_size"):
        if getattr(args, name) < 1:
            parser.error(f"{name} must be positive")
    if (
        args.output.exists()
        or list(args.output.parent.glob(args.output.stem + ".*.npz"))
        or list(args.output.parent.glob(args.output.stem + ".*.keras"))
    ):
        parser.error("output already exists")
    try:
        receipt = run(args)
    except Exception as error:
        with args.output.open("x") as stream:
            json.dump(
                {
                    "terminal": "FAILED",
                    "error": str(error),
                    "error_type": type(error).__name__,
                },
                stream,
                indent=2,
            )
        raise
    with args.output.open("x") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
