"""Exercise deterministic packing, differentiation and checkpoint compatibility.

CPU mode supplies local evidence only. GPU mode requires the pinned A100 runtime
and is a prerequisite for calibration, in a separate process with fresh seeds.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np

PET_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PET_ROOT))

import run_typed_token_comparison as runner  # noqa: E402
import typed_descriptor_keras as adapter  # noqa: E402
import typed_descriptors as typed  # noqa: E402
import typed_token_comparison as candidate  # noqa: E402
from calibration_measure import runtime_versions  # noqa: E402

REFERENCE_SHA = "905aac2dcad3eeb34dd4e21c2196af1ced6d2a58aaa68b7dc328ad737e332b95"
CASES = ("nominal", "variable", "masked", "empty")
ATOL = 1e-5
RTOL = 1e-4


def code_hashes() -> dict[str, str]:
    """Bind the candidate, preparation, oracle and smoke implementation."""
    names = (
        "typed_token_comparison.py",
        "typed_descriptor_keras.py",
        "typed_descriptors.py",
        "run_typed_token_comparison.py",
        "direct_token_comparison/compatibility_preflight.py",
        "direct_token_comparison/calibration_measure.py",
        "direct_token_comparison/reference/typed_token_comparison_cpu.py",
    )
    return {
        name: hashlib.sha256((PET_ROOT / name).read_bytes()).hexdigest()
        for name in names
    }


def compare(left: Any, right: Any, *, exact: bool = False) -> float:
    """Require finite equal-shaped arrays and report maximum absolute error."""
    left, right = np.asarray(left), np.asarray(right)
    if (
        left.shape != right.shape
        or not np.all(np.isfinite(left))
        or not np.all(np.isfinite(right))
    ):
        raise AssertionError("Nonfinite result or shape mismatch")
    valid = (
        np.array_equal(left, right)
        if exact
        else np.allclose(left, right, atol=ATOL, rtol=RTOL)
    )
    error = float(np.max(np.abs(left.astype(float) - right.astype(float)), initial=0))
    if not valid:
        raise AssertionError(f"Equivalence failed: exact={exact}, max_abs={error}")
    return error


def fixtures() -> tuple[Any, dict[str, dict[str, Any]]]:
    """Prepare four small cases without importing CPU-only pytest fixtures."""
    batch, event, generic, truth = runner.make_fixture(4, 2401)
    norm = typed.fit_frozen_normalization_for_smoke(
        batch, fit_inventory_row_selection_digest=runner.digest_arrays([truth])
    )
    nominal = adapter.prepare_keras_inputs(batch, event)
    nominal.update(generic_values=generic, generic_mask=np.ones((4, 12), bool))
    cases = {"nominal": nominal}
    for name in CASES[1:]:
        inputs = {key: value.copy() for key, value in nominal.items()}
        for family, lengths in zip(
            typed.FAMILY_CONTRACTS, ([0, 1, 3, 0], [2, 0, 90, 0], [0, 3, 1, 0])
        ):
            prefix = family.name
            sizes = (
                np.zeros(4, np.int32)
                if name == "empty"
                else np.asarray(lengths, np.int32)
            )
            segment = np.repeat(np.arange(4, dtype=np.int32), sizes)
            order = np.arange(len(segment)) % len(nominal[f"{prefix}_values"])
            for suffix in ("values", "masks", "token_mask"):
                inputs[f"{prefix}_{suffix}"] = nominal[f"{prefix}_{suffix}"][
                    order
                ].copy()
            inputs[f"{prefix}_segment_ids"] = segment
            if name == "masked":
                inputs[f"{prefix}_token_mask"][::2] = False
                inputs[f"{prefix}_masks"][::3] = False
                inputs[f"{prefix}_values"][~inputs[f"{prefix}_masks"]] = 123456.0
                inputs[f"{prefix}_enabled"][1] = False
            inputs[f"{prefix}_counts"] = np.bincount(
                segment, weights=inputs[f"{prefix}_token_mask"], minlength=4
            ).astype(np.float32)
        if name == "masked":
            inputs["generic_mask"][:, -3:] = False
            inputs["generic_values"][:, -3:] = np.nan
        cases[name] = inputs
    return norm, cases


def packing_checks(tf: Any, device: str) -> dict[str, Any]:
    """Compare values, masks and VJPs against the original CPU constructor."""
    errors: list[float] = []
    for lengths in ([], [0, 0, 0, 0], [0, 1, 3, 0], [2, 0, 90, 0]):
        segment = np.repeat(np.arange(len(lengths), dtype=np.int32), lengths)
        values = np.arange(len(segment) * 3, dtype=np.float32).reshape(-1, 3) / 7
        mask = np.arange(len(segment)) % 2 == 0
        results = []
        for original in (True, False):
            with tf.device("/CPU:0" if original else device):
                tensor = tf.convert_to_tensor(values)
                with tf.GradientTape() as tape:
                    tape.watch(tensor)
                    if original:
                        ragged = tf.RaggedTensor.from_value_rowids(
                            tensor, segment, nrows=len(lengths)
                        )
                    else:
                        ragged = tf.RaggedTensor.from_row_splits(
                            tensor, candidate.packed_row_splits(segment, len(lengths))
                        )
                    dense = ragged.to_tensor()
                    dense_mask = tf.RaggedTensor.from_row_splits(
                        mask, ragged.row_splits
                    ).to_tensor(default_value=False)
                    loss = tf.reduce_sum(
                        dense
                        * tf.reshape(
                            tf.cast(tf.range(tf.size(dense)), tf.float32),
                            tf.shape(dense),
                        )
                    )
                results.append(
                    (
                        ragged.row_splits,
                        dense,
                        dense_mask,
                        tf.convert_to_tensor(tape.gradient(loss, tensor)),
                    )
                )
        errors.extend(compare(left, right, exact=True) for left, right in zip(*results))
    graph = tf.function(candidate.packed_row_splits).get_concrete_function(
        tf.TensorSpec([None], tf.int32), tf.TensorSpec([], tf.int32)
    )
    operations = graph.graph.get_operations()
    if any("Bincount" in op.type for op in operations):
        raise AssertionError("Packing graph still contains Bincount")
    integer_ops = [
        op for op in operations if op.type in ("UnsortedSegmentSum", "Cumsum")
    ]
    if len(integer_ops) != 2 or any("CPU:0" not in op.device for op in integer_ops):
        raise AssertionError("Integer partition operations must be on CPU")
    rejected = 0
    for invalid_segment, rows in (([1, 0], 2), ([-1], 2), ([2], 2), ([], -1)):
        try:
            candidate.packed_row_splits(tf.constant(invalid_segment, tf.int32), rows)
        except (tf.errors.InvalidArgumentError, ValueError):
            rejected += 1
        else:
            raise AssertionError("Invalid partition accepted")
    return {
        "cases": 4,
        "exact_comparisons": len(errors),
        "max_abs": max(errors),
        "invalid_cases_rejected": rejected,
        "integer_operations": [
            {"type": op.type, "device": op.device} for op in integer_ops
        ],
    }


def original_module() -> Any:
    """Load the byte-identical frozen model solely as a CPU equivalence oracle."""
    path = Path(__file__).parent / "reference/typed_token_comparison_cpu.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != REFERENCE_SHA:
        raise ValueError("Frozen CPU oracle hash mismatch")
    spec = importlib.util.spec_from_file_location("packing_cpu_reference", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exercise(
    tf: Any, model: Any, inputs: dict[str, Any], device: str
) -> dict[str, Any]:
    """Run eager and traced weighted loss, input/parameter gradients and Adam."""
    with tf.device(device):
        tensors = {key: tf.convert_to_tensor(value) for key, value in inputs.items()}
        floating = [
            key
            for key, value in tensors.items()
            if value.dtype.is_floating
            and (key.endswith("_values") or key == adapter.DETECTOR_INPUT_KEY)
        ]
        watched = [tensors[key] for key in floating]
        optimizer = tf.keras.optimizers.Adam(0.001)
        optimizer.build(model.trainable_variables)

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

        eager = differentiate()
        repeated = differentiate()
        for left, right in zip(
            [eager[0], eager[1], *eager[2]], [repeated[0], repeated[1], *repeated[2]]
        ):
            compare(left, right, exact=True)
        traced = tf.function(differentiate)()
        graph_error = max(
            compare(left, right)
            for left, right in zip(
                [eager[0], eager[1], *eager[2]], [traced[0], traced[1], *traced[2]]
            )
        )
        input_gradients = dict(
            zip(floating, eager[2][len(model.trainable_variables) :])
        )
        for family in typed.FAMILY_CONTRACTS:
            prefix = family.name
            active = (
                inputs[f"{prefix}_token_mask"]
                & inputs[f"{prefix}_enabled"][inputs[f"{prefix}_segment_ids"]]
            )
            masked = ~inputs[f"{prefix}_masks"] | ~active[:, None]
            compare(
                np.asarray(input_gradients[f"{prefix}_values"])[masked],
                np.zeros(np.count_nonzero(masked)),
                exact=True,
            )
        generic_mask = ~np.broadcast_to(
            inputs["generic_mask"][:, :, None], inputs["generic_values"].shape
        )
        compare(
            np.asarray(input_gradients["generic_values"])[generic_mask],
            np.zeros(np.count_nonzero(generic_mask)),
            exact=True,
        )
        before = model.get_weights()
        optimizer.apply_gradients(
            zip(eager[2][: len(model.trainable_variables)], model.trainable_variables)
        )

        @tf.function
        def update() -> Any:
            _, loss, gradients = differentiate()
            optimizer.apply_gradients(
                zip(
                    gradients[: len(model.trainable_variables)],
                    model.trainable_variables,
                )
            )
            return loss

        update()
        after = model.get_weights()
        if all(np.array_equal(left, right) for left, right in zip(before, after)):
            raise AssertionError("Optimizer made no update")
        prediction = model(tensors, training=False)
        if device == "/GPU:0" and "GPU:0" not in prediction.device:
            raise AssertionError("Model output did not execute on GPU")
        return {
            "initial": [eager[0], eager[1], *eager[2]],
            "weights": after,
            "prediction": prediction,
            "graph_max_abs": graph_error,
            "device": prediction.device,
            "optimizer_iterations": int(optimizer.iterations),
        }


def verify_receipt(directory: Path, *, require_gpu: bool = True) -> dict[str, Any]:
    """Fail closed on incomplete, CPU-only, stale or altered preflight evidence."""
    receipt = json.loads((directory / "preflight.json").read_text())
    if receipt["terminal"] != "PASS" or (require_gpu and receipt["mode"] != "gpu"):
        raise ValueError("Complete GPU compatibility preflight is required")
    if (
        receipt["code_sha256"] != code_hashes()
        or receipt["versions"] != runtime_versions()
    ):
        raise ValueError("Preflight code/runtime mismatch")
    if {(row["case"], row["routing"]) for row in receipt["models"]} != {
        (case, route) for case in CASES for route in ("pooled", "direct")
    }:
        raise ValueError("Incomplete preflight coverage")
    expected_artifacts = {f"{case}.npz" for case in CASES} | {"reload.json"}
    expected_artifacts.update(
        f"{case}-{route}.{suffix}"
        for case in CASES
        for route in ("pooled", "direct")
        for suffix in ("keras", "npy")
    )
    if set(receipt["artifacts"]) != expected_artifacts or len(receipt["models"]) != 8:
        raise ValueError("Incomplete artifact inventory")
    if (
        receipt["determinism"] is not True
        or receipt["cpu_oracle_sha256"] != REFERENCE_SHA
    ):
        raise ValueError("Preflight determinism/oracle mismatch")
    if require_gpu and any("GPU:0" not in row["device"] for row in receipt["models"]):
        raise ValueError("Preflight model did not run on GPU")
    for name, digest in receipt["artifacts"].items():
        if (
            Path(name).name != name
            or hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest
        ):
            raise ValueError("Preflight artifact mismatch")
    reload_receipt = json.loads((directory / "reload.json").read_text())
    if reload_receipt["terminal"] != "PASS" or len(reload_receipt["models"]) != 8:
        raise ValueError("Fresh process reload did not pass")
    return receipt


def main() -> None:
    """Write PASS only after both routes complete every check and fresh reload."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "gpu"), required=True)
    parser.add_argument("--reload-only", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    initial_hashes = code_hashes()
    versions = runtime_versions()
    tf = adapter.require_tensorflow()
    tf.config.experimental.enable_op_determinism()
    tf.config.threading.set_intra_op_parallelism_threads(7)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    devices = tf.config.list_physical_devices("GPU")
    details = {}
    if args.device == "cpu":
        tf.config.set_visible_devices([], "GPU")
    else:
        if len(devices) != 1:
            raise RuntimeError("Exactly one GPU is required")
        details = tf.config.experimental.get_device_details(devices[0])
        if "A100" not in details.get("device_name", ""):
            raise RuntimeError("An A100 is required")
        tf.config.experimental.set_memory_growth(devices[0], True)
    device = "/GPU:0" if args.device == "gpu" else "/CPU:0"
    tf.keras.utils.set_random_seed(1701)
    current_type = candidate.comparison_model_type()
    if args.reload_only:
        rows = []
        for case in CASES:
            with np.load(args.output / f"{case}.npz", allow_pickle=False) as source:
                inputs = dict(source)
            for route in ("pooled", "direct"):
                stem = f"{case}-{route}"
                with tf.device(device):
                    model = tf.keras.models.load_model(args.output / f"{stem}.keras")
                    prediction = model(inputs)
                if args.device == "gpu" and "GPU:0" not in prediction.device:
                    raise AssertionError("Reload did not execute on GPU")
                error = compare(prediction, np.load(args.output / f"{stem}.npy"))
                rows.append(
                    {
                        "case": case,
                        "routing": route,
                        "max_abs": error,
                        "device": prediction.device,
                    }
                )
        (args.output / "reload.json").write_text(
            json.dumps({"terminal": "PASS", "models": rows}, indent=2) + "\n"
        )
        return
    args.output.mkdir(parents=True, exist_ok=False)
    packing = packing_checks(tf, device)
    reference = original_module()
    norm, cases = fixtures()
    rows = []
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
            if old.count_params() != new.count_params() or new.count_params() != 17329:
                raise AssertionError("Model parameter count changed")
            for left, right in zip(old.get_weights(), new.get_weights()):
                compare(left, right, exact=True)
            with tf.device("/CPU:0"):
                old_tokens = old.route_tokens(inputs)
            with tf.device(device):
                new_tokens = new.route_tokens(inputs)
            token_errors = [
                compare(left, right, exact=(index > 0 or args.device == "cpu"))
                for index, (left, right) in enumerate(zip(old_tokens, new_tokens))
            ]
            old_result = exercise(tf, old, inputs, "/CPU:0")
            new_result = exercise(tf, new, inputs, device)
            initial_error = max(
                compare(left, right, exact=args.device == "cpu")
                for left, right in zip(old_result["initial"], new_result["initial"])
            )
            weight_error = max(
                compare(left, right, exact=args.device == "cpu")
                for left, right in zip(old_result["weights"], new_result["weights"])
            )
            prediction_error = compare(
                old_result["prediction"],
                new_result["prediction"],
                exact=args.device == "cpu",
            )
            tf.keras.utils.get_custom_objects()[
                "minerva_pet>TypedTokenComparison"
            ] = current_type
            stem = f"{case}-{route}"
            new.save(args.output / f"{stem}.keras")
            np.save(args.output / f"{stem}.npy", new_result["prediction"])
            with tf.device(device):
                restored = tf.keras.models.load_model(args.output / f"{stem}.keras")
                reload_error = compare(
                    restored(inputs), new_result["prediction"], exact=True
                )
            for left, right in zip(restored.get_weights(), new.get_weights()):
                compare(left, right, exact=True)
            rows.append(
                {
                    "case": case,
                    "routing": route,
                    "parameters": new.count_params(),
                    "token_max_abs": max(token_errors),
                    "initial_output_loss_gradient_max_abs": initial_error,
                    "updated_weights_max_abs": weight_error,
                    "updated_prediction_max_abs": prediction_error,
                    "graph_max_abs": new_result["graph_max_abs"],
                    "reload_max_abs": reload_error,
                    "optimizer_updates": new_result["optimizer_iterations"],
                    "device": new_result["device"],
                }
            )
            print(json.dumps(rows[-1]), flush=True)
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--device",
            args.device,
            "--output",
            str(args.output.resolve()),
            "--reload-only",
        ],
        check=True,
    )
    artifacts = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in args.output.iterdir()
        if path.is_file()
    }
    if code_hashes() != initial_hashes:
        raise RuntimeError("Preflight source changed during execution")
    receipt = {
        "terminal": "PASS",
        "mode": args.device,
        "versions": versions,
        "tensorflow_build": tf.sysconfig.get_build_info(),
        "device_details": details,
        "determinism": True,
        "cpu_oracle_sha256": REFERENCE_SHA,
        "tolerance": {"cpu_equivalence": "exact", "gpu_atol": ATOL, "gpu_rtol": RTOL},
        "packing": packing,
        "models": rows,
        "artifacts": artifacts,
        "code_sha256": code_hashes(),
        "wall_seconds": time.monotonic() - started,
        "scope": "Synthetic compatibility only; no learning-performance conclusion",
    }
    (args.output / "preflight.json").write_text(
        json.dumps(receipt, indent=2, allow_nan=False) + "\n"
    )
    verify_receipt(args.output, require_gpu=args.device == "gpu")


if __name__ == "__main__":
    main()
