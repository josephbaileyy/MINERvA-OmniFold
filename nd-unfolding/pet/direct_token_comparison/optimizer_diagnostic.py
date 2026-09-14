"""Save two-step Adam evidence before comparisons; never release training.

The unchanged preflight is the same-device instrumentation oracle. Historical
initial weights were not saved: the seed recipe is reconstructed once per case.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

import compatibility_preflight as preflight
from calibration_measure import runtime_versions
import run_typed_token_comparison as runner
import typed_descriptor_keras as adapter
import typed_token_comparison as candidate


def metrics(left: Any, right: Any) -> dict[str, Any]:
    """Measure the existing asymmetric tolerance without raising on mismatch."""
    left, right = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    if left.shape != right.shape or not (
        np.isfinite(left).all() and np.isfinite(right).all()
    ):
        raise ValueError("Nonfinite data or incompatible shapes")
    error = np.abs(left - right)
    budget = preflight.ATOL + preflight.RTOL * np.abs(right)
    worst = int(np.argmax(error / budget)) if error.size else 0
    return {
        "exact": bool(np.array_equal(left, right)),
        "failed": int(np.count_nonzero(error > budget)),
        "count": int(error.size),
        "max_abs": float(error.max(initial=0)),
        "max_budget_ratio": float((error / budget).max(initial=0)),
        "worst_flat_index": worst,
        "worst_left": float(left.flat[worst]) if error.size else None,
        "worst_right": float(right.flat[worst]) if error.size else None,
    }


def save_arrays(path: Path, values: dict[str, Any]) -> dict[str, Any]:
    """Close a named tensor snapshot before any numerical assessment."""
    arrays = {name: np.asarray(value).copy() for name, value in values.items()}
    np.savez(path, **arrays)
    return arrays


def snapshot(model: Any, optimizer: Any) -> dict[str, Any]:
    """Record all model variables and optimizer state, in their bound order."""
    return {
        **{f"weight_{i}": value.numpy() for i, value in enumerate(model.weights)},
        **{f"slot_{i}": value.numpy() for i, value in enumerate(optimizer.variables)},
    }


def trace(
    tf: Any, model: Any, inputs: dict[str, Any], device: str, output: Path
) -> dict[str, Any]:
    """Capture the preflight loss and eager/traced Adam steps on one device."""
    output.mkdir()
    with tf.device(device):
        tensors = {key: tf.convert_to_tensor(value) for key, value in inputs.items()}
        watched = [
            value
            for key, value in tensors.items()
            if value.dtype.is_floating
            and (key.endswith("_values") or key == adapter.DETECTOR_INPUT_KEY)
        ]
        optimizer = tf.keras.optimizers.Adam(0.001)
        optimizer.build(model.trainable_variables)
        (output / "variables.json").write_text(
            json.dumps(
                {
                    "weights": [
                        {
                            "path": v.path,
                            "shape": list(v.shape),
                            "trainable": v.trainable,
                        }
                        for v in model.weights
                    ],
                    "trainable_paths": [v.path for v in model.trainable_variables],
                    "optimizer": optimizer.get_config(),
                    "slots": [
                        {"path": v.path, "shape": list(v.shape)}
                        for v in optimizer.variables
                    ],
                },
                indent=2,
            )
            + "\n"
        )
        states = [save_arrays(output / "state-0.npz", snapshot(model, optimizer))]

        def differentiate() -> tuple[Any, Any, list[Any]]:
            with tf.GradientTape() as tape:
                tape.watch(watched)
                prediction = model(tensors, training=True)
                weights = tf.constant([[0.7], [1.2], [0.9], [1.4]])
                loss = tf.reduce_mean(
                    tf.nn.softplus(prediction) + weights * tf.nn.softplus(-prediction)
                )
            gradients = tape.gradient(loss, [*model.trainable_variables, *watched])
            if any(value is None for value in gradients):
                raise AssertionError("Disconnected gradient")
            return (
                prediction,
                loss,
                [tf.convert_to_tensor(value) for value in gradients],
            )

        def save_derivatives(name: str, result: Any) -> dict[str, Any]:
            return save_arrays(
                output / f"{name}.npz",
                {
                    "prediction": result[0],
                    "loss": result[1],
                    **{f"gradient_{i}": value for i, value in enumerate(result[2])},
                },
            )

        eager = differentiate()
        initial = save_derivatives("eager", eager)
        repeated = save_derivatives("repeated", differentiate())
        graph = save_derivatives("graph", tf.function(differentiate)())
        optimizer.apply_gradients(
            zip(eager[2][: len(model.trainable_variables)], model.trainable_variables)
        )
        states.append(save_arrays(output / "state-1.npz", snapshot(model, optimizer)))

        @tf.function  # type: ignore[untyped-decorator]
        def update() -> Any:
            prediction, loss, gradients = differentiate()
            optimizer.apply_gradients(
                zip(
                    gradients[: len(model.trainable_variables)],
                    model.trainable_variables,
                )
            )
            return prediction, loss, gradients

        second = save_derivatives("second", update())
        states.append(save_arrays(output / "state-2.npz", snapshot(model, optimizer)))
        predicted = model(tensors, training=False)
        if device == "/GPU:0" and "GPU:0" not in predicted.device:
            raise AssertionError("Diagnostic model did not execute on GPU")
        (output / "device.json").write_text(
            json.dumps({"prediction_device": predicted.device}) + "\n"
        )
        prediction = save_arrays(output / "prediction.npz", {"prediction": predicted})
        return {
            "initial": initial,
            "repeated": repeated,
            "graph": graph,
            "second": second,
            "states": states,
            "prediction": prediction["prediction"],
        }


def replay(
    tf: Any, initial: list[Any], gradients: list[list[Any]], device: str, output: Path
) -> list[dict[str, Any]]:
    """Replay identical gradient operands through fresh Adam state on a device."""
    output.mkdir()
    with tf.device(device):
        variables = [tf.Variable(value) for value in initial]
        optimizer = tf.keras.optimizers.Adam(0.001)
        optimizer.build(variables)
        states = []
        for step, values in enumerate(gradients):
            operands = [tf.convert_to_tensor(value) for value in values]
            if step == 0:
                optimizer.apply_gradients(zip(operands, variables))
            else:

                @tf.function  # type: ignore[untyped-decorator]
                def update() -> Any:
                    optimizer.apply_gradients(zip(operands, variables))
                    return optimizer.iterations

                update()
            states.append(
                save_arrays(
                    output / f"step-{step + 1}.npz",
                    {
                        **{f"weight_{i}": value for i, value in enumerate(variables)},
                        **{
                            f"slot_{i}": value
                            for i, value in enumerate(optimizer.variables)
                        },
                    },
                )
            )
        return states


def float64_adam(initial: list[Any], gradients: list[list[Any]]) -> list[list[Any]]:
    """Evaluate Adam's pinned formula in float64 on saved float32 operands.

    This is a numerical reference, not a replacement optimizer or error budget.
    The learning rate is the actual float32 optimizer variable's value.
    """
    weights = [np.asarray(v, dtype=np.float64).copy() for v in initial]
    momenta = [np.zeros_like(v) for v in weights]
    velocities = [np.zeros_like(v) for v in weights]
    states = []
    for step, values in enumerate(gradients, 1):
        alpha = float(np.float32(0.001)) * np.sqrt(1 - 0.999**step) / (1 - 0.9**step)
        for i, value in enumerate(values):
            gradient = np.asarray(value, dtype=np.float64)
            momenta[i] += (gradient - momenta[i]) * (1 - 0.9)
            velocities[i] += (gradient**2 - velocities[i]) * (1 - 0.999)
            weights[i] -= momenta[i] * alpha / (np.sqrt(velocities[i]) + 1e-7)
        states.append([v.copy() for v in weights])
    return states


def compare_maps(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Compare every named tensor and retain failed coordinates in source files."""
    if left.keys() != right.keys():
        raise ValueError("Tensor inventory differs")
    return {key: metrics(left[key], right[key]) for key in left}


def main() -> None:
    """Capture all eight model/case pairs and common-operand update replays."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "gpu"), required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
        if len(affinity) < 8:
            raise RuntimeError("Eight application CPUs are required")
        os.sched_setaffinity(0, affinity[:8])
    versions = runtime_versions()
    tf = adapter.require_tensorflow()
    runner.configure_precision()
    tf.config.threading.set_intra_op_parallelism_threads(7)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    devices = tf.config.list_physical_devices("GPU")
    if args.device == "cpu":
        tf.config.set_visible_devices([], "GPU")
    elif len(devices) != 1 or "A100" not in tf.config.experimental.get_device_details(
        devices[0]
    ).get("device_name", ""):
        raise RuntimeError("Exactly one A100 is required")
    else:
        tf.config.experimental.set_memory_growth(devices[0], True)
    device = "/GPU:0" if args.device == "gpu" else "/CPU:0"
    (args.output / "environment.json").write_text(
        json.dumps(
            {
                "versions": versions,
                "precision": runner.precision_settings(),
                "device": device,
            },
            indent=2,
        )
        + "\n"
    )
    tf.keras.utils.set_random_seed(1701)
    norm, cases = preflight.fixtures()
    reference = preflight.original_module()
    pairs = []
    # Build in the frozen loop order before diagnostic-only models consume RNG.
    for case, inputs in cases.items():
        np.savez(args.output / f"{case}.npz", **inputs)
        for route in ("pooled", "direct"):
            with tf.device("/CPU:0"):
                old = reference.build_comparison(norm, routing=route)
                old(inputs)
            with tf.device(device):
                new = candidate.build_comparison(norm, routing=route)
                new(inputs)
                new.set_weights(old.get_weights())
            pairs.append((case, route, inputs, old, new))
    rows: list[dict[str, Any]] = []
    for case, route, inputs, old, new in pairs:
        directory = args.output / f"{case}-{route}"
        directory.mkdir()
        initial_weights = old.get_weights()
        save_arrays(
            directory / "initial-weights.npz",
            {f"weight_{i}": v for i, v in enumerate(initial_weights)},
        )
        traces = []
        instrumentation = []
        for label, model, target in (
            ("cpu", old, "/CPU:0"),
            ("candidate", new, device),
        ):
            captured = trace(tf, model, inputs, target, directory / label)
            traces.append(captured)
            model.set_weights(initial_weights)
            try:
                oracle = preflight.exercise(tf, model, inputs, target)
                checks = [
                    metrics(a, b)
                    for a, b in zip(
                        oracle["weights"],
                        [
                            captured["states"][2][f"weight_{i}"]
                            for i in range(len(initial_weights))
                        ],
                    )
                ]
                checks += [metrics(oracle["prediction"], captured["prediction"])]
                instrumentation.append(
                    {
                        "device": target,
                        "exact": all(c["exact"] for c in checks),
                        "checks": checks,
                    }
                )
            except AssertionError as error:
                instrumentation.append(
                    {"device": target, "exact": False, "oracle_failure": str(error)}
                )
        comparisons = {
            name: compare_maps(traces[0][name], traces[1][name])
            for name in ("initial", "second")
        }
        comparisons["weights"] = compare_maps(
            traces[0]["states"][2], traces[1]["states"][2]
        )
        replays = {}
        for label, captured, model in zip(("cpu", "candidate"), traces, (old, new)):
            initial_trainable = [
                initial_weights[next(i for i, w in enumerate(model.weights) if w is v)]
                for v in model.trainable_variables
            ]
            gradients = [
                [
                    captured[name][f"gradient_{i}"]
                    for i in range(len(model.trainable_variables))
                ]
                for name in ("initial", "second")
            ]
            cpu = replay(
                tf,
                initial_trainable,
                gradients,
                "/CPU:0",
                directory / f"replay-{label}-cpu",
            )
            gpu = replay(
                tf,
                initial_trainable,
                gradients,
                device,
                directory / f"replay-{label}-candidate",
            )
            high = float64_adam(initial_trainable, gradients)
            for step, values in enumerate(high, 1):
                save_arrays(
                    directory / f"float64-{label}-{step}.npz",
                    {f"weight_{i}": v for i, v in enumerate(values)},
                )
            replays[label] = {
                "common_operands": [compare_maps(a, b) for a, b in zip(cpu, gpu)],
                "float64_cpu": [
                    [metrics(a[f"weight_{i}"], value) for i, value in enumerate(values)]
                    for a, values in zip(cpu, high)
                ],
                "float64_candidate": [
                    [metrics(a[f"weight_{i}"], value) for i, value in enumerate(values)]
                    for a, values in zip(gpu, high)
                ],
            }
        row = {
            "case": case,
            "routing": route,
            "instrumentation": instrumentation,
            "comparisons": comparisons,
            "replays": replays,
            "repeatability": [
                {k: metrics(t["initial"][k], t["repeated"][k]) for k in t["initial"]}
                for t in traces
            ],
        }
        (directory / "analysis.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append(row)
        print(
            json.dumps(
                {
                    "case": case,
                    "routing": route,
                    "instrumentation_exact": all(r["exact"] for r in instrumentation),
                    "weight_failures": sum(
                        m["failed"]
                        for k, m in comparisons["weights"].items()
                        if k.startswith("weight_")
                    ),
                }
            ),
            flush=True,
        )
    files = {
        str(p.relative_to(args.output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(args.output.rglob("*"))
        if p.is_file()
    }
    (args.output / "receipt.json").write_text(
        json.dumps(
            {
                "terminal": "COMPLETE_DIAGNOSTIC",
                "precision": runner.precision_settings(),
                "rows": len(rows),
                "all_instrumentation_exact": all(
                    c["exact"] for r in rows for c in r["instrumentation"]
                ),
                "files": files,
                "training_authorized": False,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
