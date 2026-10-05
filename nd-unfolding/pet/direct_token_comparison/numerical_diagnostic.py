"""Capture pooled-encoder numerical differences without authorizing training.

Every operation writes its operands and result before comparison. Float64 local
references use the exact float32 operands; propagated MLP references start from
the exact CPU prepared float32 features and copied float32 weights.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
import sys
import tarfile
import time
from typing import Any
from unittest.mock import patch

import numpy as np

PET_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PET_ROOT))

import compatibility_preflight as preflight  # noqa: E402
import typed_descriptor_keras as adapter  # noqa: E402
import typed_token_comparison as candidate  # noqa: E402
from calibration_measure import runtime_versions  # noqa: E402

ATOL = preflight.ATOL
RTOL = preflight.RTOL
UNIT_ROUNDOFF = 2.0**-24


def write_json(path: Path, value: Any) -> None:
    """Close an atomic JSON receipt; never serialize nonfinite measurements."""
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def digest(path: Path) -> str:
    """Return the SHA-256 of closed artifact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(directory: Path) -> None:
    """Bind all closed diagnostic artifacts except the manifest itself."""
    write_json(
        directory / "artifact-manifest.json",
        {
            str(path.relative_to(directory)): digest(path)
            for path in sorted(directory.rglob("*"))
            if path.is_file() and path.name != "artifact-manifest.json"
        },
    )


def verify_seal(directory: Path) -> None:
    """Reject missing, changed or unlisted files before reducing evidence."""
    expected = json.loads((directory / "artifact-manifest.json").read_text())
    observed = {
        str(path.relative_to(directory)): digest(path)
        for path in directory.rglob("*")
        if path.is_file() and path.name != "artifact-manifest.json"
    }
    if expected != observed:
        raise ValueError(f"Artifact inventory mismatch: {directory.name}")


def array_hash(values: list[Any]) -> str:
    """Fingerprint dtype, shape and bytes of ordered arrays."""
    hasher = hashlib.sha256()
    for value in values:
        array = np.asarray(value)
        hasher.update(str((array.dtype.str, array.shape)).encode())
        hasher.update(array.tobytes())
    return hasher.hexdigest()


def save_errors(path: Path, left: Any, right: Any) -> dict[str, Any]:
    """Save operands, elementwise errors, fixed thresholds and failing indices.

    The acceptance mask reproduces the historical ``np.isclose(left, right)``
    calculation in its native dtype. Float64 error/threshold arrays are also
    stored for analysis, so native rounding of the threshold remains visible.
    """
    left, right = np.asarray(left), np.asarray(right)
    if left.shape != right.shape:
        np.savez(path, left=left, right=right)
        return {
            "shape_mismatch": True,
            "left_shape": list(left.shape),
            "right_shape": list(right.shape),
            "passes": False,
        }
    left64, right64 = left.astype(np.float64), right.astype(np.float64)
    with np.errstate(invalid="ignore", over="ignore", divide="ignore"):
        error = np.abs(left64 - right64)
        signed_error = left64 - right64
        threshold64 = ATOL + RTOL * np.abs(right64)
        threshold_native = ATOL + RTOL * np.abs(right)
        finite = np.isfinite(left) & np.isfinite(right)
        within = np.isclose(left, right, atol=ATOL, rtol=RTOL) & finite
        indices = np.argwhere(~within)
        unequal = (left != right) | ~finite
        normalized_error = error / threshold64
        relative_error = error / np.abs(right64)
    np.savez(
        path,
        left=left,
        right=right,
        signed_error=signed_error,
        absolute_error=error,
        threshold_native=threshold_native,
        threshold_float64=threshold64,
        normalized_error=normalized_error,
        relative_error_to_right=relative_error,
        finite=finite,
        within_tolerance=within,
        failing_indices=indices,
        unequal_indices=np.argwhere(unequal),
    )
    return {
        "elements": int(left.size),
        "failing_elements": int(indices.shape[0]),
        "unequal_elements": int(np.count_nonzero(unequal)),
        "maximum_absolute_error": float(error.max(initial=0)) if finite.all() else None,
        "maximum_error_over_threshold": (
            float(normalized_error.max(initial=0)) if finite.all() else None
        ),
        "passes": bool(within.all()),
        "finite": bool(finite.all()),
    }


def reference_operation(kind: str, a: Any, b: Any, rows: int = 4) -> tuple[Any, Any]:
    """Evaluate a primitive in float64 and an illustrative FP32 roundoff bound.

    Bounds assume ordinary full-significand FP32 arithmetic, no overflow or
    underflow, and exact supplied operands. They are diagnostic error-budget
    components, not substitute acceptance criteria or bounds for TF32.
    """
    a64 = np.asarray(a, np.float64)
    b64 = np.asarray(b, np.float64)
    if kind == "matmul":
        count = a64.shape[-1]
        gamma = count * UNIT_ROUNDOFF / (1 - count * UNIT_ROUNDOFF)
        return a64 @ b64, gamma * (np.abs(a64) @ np.abs(b64))
    if kind == "add":
        return a64 + b64, UNIT_ROUNDOFF * (np.abs(a64) + np.abs(b64))
    if kind == "subtract":
        return a64 - b64, UNIT_ROUNDOFF * (np.abs(a64) + np.abs(b64))
    if kind == "divide":
        result = a64 / b64
        return result, UNIT_ROUNDOFF * np.abs(result)
    if kind == "relu":
        return np.maximum(a64, 0), np.zeros_like(a64)
    if kind == "mask":
        result = np.where(np.asarray(b, bool)[:, None], a64, 0)
        return result, np.zeros_like(result)
    if kind == "pool":
        segment = np.asarray(b, np.int32)
        result = np.zeros((rows, a64.shape[-1]), np.float64)
        absolute = np.zeros_like(result)
        np.add.at(result, segment, a64)
        np.add.at(absolute, segment, np.abs(a64))
        counts = np.bincount(segment, minlength=rows)
        operations = np.maximum(counts - 1, 0)[:, None]
        pool_gamma = operations * UNIT_ROUNDOFF / (1 - operations * UNIT_ROUNDOFF)
        return result, pool_gamma * absolute
    raise ValueError(f"Unknown primitive: {kind}")


class Capture:
    """Persist each primitive and replay it with common CPU operands."""

    def __init__(self, directory: Path, tf: Any, common: Path | None = None) -> None:
        directory.mkdir(parents=True, exist_ok=False)
        self.directory = directory
        self.tf = tf
        self.common = common
        self.nodes: list[dict[str, Any]] = []

    def record(self, name: str, kind: str, a: Any, b: Any, output: Any) -> Any:
        """Write evidence before any numerical assertion can stop the worker."""
        a_array, b_array, result = np.asarray(a), np.asarray(b), np.asarray(output)
        path = self.directory / f"{name}.npz"
        # Persist raw tensors first, even if reference construction later fails.
        np.savez(path, a=a_array, b=b_array, output=result)
        reference64, bound = reference_operation(kind, a_array, b_array)
        arrays = {
            "a": a_array,
            "b": b_array,
            "output": result,
            "reference64": reference64,
            "ordinary_fp32_bound": bound,
        }
        if self.common is not None:
            with np.load(self.common / path.name, allow_pickle=False) as common:
                shared_a, shared_b = common["a"], common["b"]
            shared_output = self.apply(kind, shared_a, shared_b)
            arrays.update(
                shared_a=shared_a,
                shared_b=shared_b,
                shared_output=np.asarray(shared_output),
            )
        np.savez(path, **arrays)
        self.nodes.append(
            {
                "name": name,
                "kind": kind,
                "file": path.name,
                "shape": list(result.shape),
                "dtype": result.dtype.str,
                "device": output.device,
            }
        )
        write_json(self.directory / "index.json", self.nodes)
        return output

    def apply(self, kind: str, a: Any, b: Any) -> Any:
        tf = self.tf
        a = tf.convert_to_tensor(a)
        if kind == "matmul":
            return tf.keras.ops.matmul(a, tf.convert_to_tensor(b))
        if kind == "add":
            return tf.keras.ops.add(a, tf.convert_to_tensor(b))
        if kind == "subtract":
            return tf.subtract(a, b)
        if kind == "divide":
            return tf.divide(a, b)
        if kind == "relu":
            return tf.nn.relu(a)
        if kind == "mask":
            return tf.where(tf.convert_to_tensor(b)[:, None], a, 0.0)
        if kind == "pool":
            return tf.math.unsorted_segment_sum(a, tf.cast(b, tf.int32), 4)
        raise ValueError(kind)


def prepare_features(encoder: Any, inputs: dict[str, Any], capture: Capture) -> Any:
    """Expose normalization primitives with exact parity to the unchanged adapter."""
    tf = capture.tf
    prefix = encoder.family_name
    values = tf.convert_to_tensor(inputs[f"{prefix}_values"], tf.float32)
    masks = tf.convert_to_tensor(inputs[f"{prefix}_masks"], tf.bool)
    token_mask = tf.convert_to_tensor(inputs[f"{prefix}_token_mask"], tf.bool)
    offsets, offset = {}, 0
    for field in encoder.contract.fields:
        offsets[field.name] = offset
        offset += field.width
    prepared, validity = [], []
    offset = 0
    for field in encoder.contract.fields:
        raw = values[:, offset : offset + field.width]
        valid = masks[:, offset : offset + field.width] & token_mask[:, None]
        if field.valid_when is not None:
            source_name, codes = field.valid_when
            source_offset = offsets[source_name]
            matches = tf.equal(
                values[:, source_offset : source_offset + 1, None],
                tf.constant(codes, tf.float32),
            )
            valid &= masks[:, source_offset : source_offset + 1] & tf.reduce_any(
                matches, -1
            )
        if field.kind == "continuous":
            if field.standardize:
                mean = tf.constant(
                    encoder.family_normalization.means[field.name], tf.float32
                )
                scale = tf.constant(
                    encoder.family_normalization.scales[field.name], tf.float32
                )
                safe = tf.where(valid, raw, mean)
                difference = capture.record(
                    f"{prefix}.prepare.{field.name}.subtract",
                    "subtract",
                    safe,
                    mean,
                    safe - mean,
                )
                normalized = capture.record(
                    f"{prefix}.prepare.{field.name}.divide",
                    "divide",
                    difference,
                    scale,
                    difference / scale,
                )
            else:
                normalized = tf.where(valid, raw, 0.0)
            prepared.append(normalized)
        else:
            matches = tf.equal(
                raw[..., None], tf.constant(field.categories, tf.float32)
            )
            unknown = ~tf.reduce_any(matches, -1, keepdims=True)
            categorical = tf.concat([matches, unknown], -1) & valid[..., None]
            prepared.append(
                tf.reshape(tf.cast(categorical, tf.float32), (tf.shape(values)[0], -1))
            )
        validity.append(tf.cast(valid, tf.float32))
        offset += field.width
    result = tf.concat(prepared + validity, 1)
    actual = encoder.prepare_features(values, masks, token_mask)
    np.savez(
        capture.directory / f"{prefix}.prepared.npz",
        traced=np.asarray(result),
        actual=np.asarray(actual),
    )
    return result


def capture_model(
    model: Any, inputs: dict[str, Any], capture: Capture
) -> dict[str, Any]:
    """Trace the actual Dense calls, then separate masking and segment pooling."""
    tf = capture.tf
    ops = importlib.import_module("keras.src.layers.core.dense").ops
    pools, parity = [], {}
    for encoder in model.encoders:
        prefix = encoder.family_name
        features = prepare_features(encoder, inputs, capture)
        x = features
        for index, layer in enumerate(encoder.token_mlp.layers):
            base = f"{prefix}.dense{index}"
            original_matmul, original_add = ops.matmul, ops.add

            def matmul(a: Any, b: Any) -> Any:
                return capture.record(
                    base + ".matmul", "matmul", a, b, original_matmul(a, b)
                )

            def add(a: Any, b: Any) -> Any:
                return capture.record(base + ".bias", "add", a, b, original_add(a, b))

            # Capture shared-operand replays outside the patched dispatch to
            # avoid recursively intercepting the diagnostic's own operations.
            common = capture.common
            capture.common = None
            with patch.object(ops, "matmul", matmul), patch.object(ops, "add", add):
                x = layer(x)
            capture.common = common
            if common is not None:
                for suffix in ("matmul", "bias"):
                    path = capture.directory / f"{base}.{suffix}.npz"
                    with np.load(path, allow_pickle=False) as saved:
                        arrays = dict(saved)
                    with np.load(common / path.name, allow_pickle=False) as saved:
                        shared_a, shared_b = saved["a"], saved["b"]
                    arrays.update(
                        shared_a=shared_a,
                        shared_b=shared_b,
                        shared_output=np.asarray(
                            capture.apply(
                                "matmul" if suffix == "matmul" else "add",
                                shared_a,
                                shared_b,
                            )
                        ),
                    )
                    np.savez(path, **arrays)
            with np.load(
                capture.directory / f"{base}.bias.npz", allow_pickle=False
            ) as saved:
                before_activation = saved["output"]
            capture.record(base + ".relu", "relu", before_activation, np.float32(0), x)
        active = (
            np.asarray(inputs[f"{prefix}_token_mask"])
            & np.asarray(inputs[f"{prefix}_enabled"])[inputs[f"{prefix}_segment_ids"]]
        )
        masked = capture.record(
            prefix + ".mask", "mask", x, active, tf.where(active[:, None], x, 0.0)
        )
        pool = capture.record(
            prefix + ".pool",
            "pool",
            masked,
            inputs[f"{prefix}_segment_ids"],
            tf.math.unsorted_segment_sum(masked, inputs[f"{prefix}_segment_ids"], 4),
        )
        pools.append(pool[:, None, :])
        with np.load(
            capture.directory / f"{prefix}.prepared.npz", allow_pickle=False
        ) as saved:
            parity[prefix + ".prepare"] = bool(
                np.array_equal(saved["traced"], saved["actual"])
            )
        actual_mlp = encoder.token_mlp(features)
        np.savez(
            capture.directory / f"{prefix}.mlp-parity.npz",
            traced=np.asarray(x),
            actual=np.asarray(actual_mlp),
        )
        parity[prefix + ".mlp"] = bool(
            np.array_equal(np.asarray(x), np.asarray(actual_mlp))
        )
    actual_cloud, mask, counts = model.route_tokens(inputs)
    traced_cloud = tf.concat(pools, 1)
    np.savez(
        capture.directory / "route.npz",
        actual=np.asarray(actual_cloud),
        traced=np.asarray(traced_cloud),
        mask=np.asarray(mask),
        counts=np.asarray(counts),
    )
    parity["route"] = bool(
        np.array_equal(np.asarray(actual_cloud), np.asarray(traced_cloud))
    )
    write_json(capture.directory / "parity.json", parity)
    return parity


def propagated_reference(
    model: Any, inputs: dict[str, Any], trace: Path, output: Path
) -> None:
    """Save a float64 MLP/pool chain anchored to unchanged float32 operands."""
    result = {}
    for encoder in model.encoders:
        prefix = encoder.family_name
        with np.load(trace / f"{prefix}.prepared.npz", allow_pickle=False) as saved:
            x = saved["actual"].astype(np.float64)
        error_bound = np.zeros_like(x)
        for index, layer in enumerate(encoder.token_mlp.layers):
            base = f"{prefix}.dense{index}"
            kernel, bias = (
                np.asarray(weight).astype(np.float64) for weight in layer.get_weights()
            )
            product, local_bound = reference_operation("matmul", x, kernel)
            count = x.shape[-1]
            gamma = count * UNIT_ROUNDOFF / (1 - count * UNIT_ROUNDOFF)
            error_bound = (
                error_bound @ np.abs(kernel)
                + local_bound
                + gamma * (error_bound @ np.abs(kernel))
            )
            result[base + ".matmul"] = product
            result[base + ".matmul.bound"] = error_bound.copy()
            x = product + bias
            error_bound += UNIT_ROUNDOFF * (
                np.abs(product) + error_bound + np.abs(bias)
            )
            result[base + ".bias"] = x
            result[base + ".bias.bound"] = error_bound.copy()
            x = np.maximum(x, 0)
            result[base + ".relu"] = x
            result[base + ".relu.bound"] = error_bound.copy()
        active = (
            inputs[f"{prefix}_token_mask"]
            & inputs[f"{prefix}_enabled"][inputs[f"{prefix}_segment_ids"]]
        )
        x = np.where(active[:, None], x, 0)
        error_bound = np.where(active[:, None], error_bound, 0)
        result[prefix + ".mask"] = x
        result[prefix + ".mask.bound"] = error_bound.copy()
        pooled, bound = reference_operation("pool", x, inputs[f"{prefix}_segment_ids"])
        summed_error, _ = reference_operation(
            "pool", error_bound, inputs[f"{prefix}_segment_ids"]
        )
        result[prefix + ".pool"] = pooled
        counts = np.bincount(inputs[f"{prefix}_segment_ids"], minlength=4)
        operations = np.maximum(counts - 1, 0)[:, None]
        gamma_pool = operations * UNIT_ROUNDOFF / (1 - operations * UNIT_ROUNDOFF)
        result[prefix + ".pool.bound"] = (
            bound + summed_error + gamma_pool * summed_error
        )
    np.savez(output, **result)


def prepare_testing_import() -> None:
    """Use NumPy's missing-probe fallback under the existing import guard."""
    if platform.machine() != "x86_64" and shutil.which("lscpu") is not None:
        raise RuntimeError("Optional SVE probe cannot be disabled on this platform")
    guarded_run = subprocess.run

    def without_optional_probe(command: Any, *args: Any, **kwargs: Any) -> Any:
        if command == "lscpu":
            raise FileNotFoundError("Optional SVE probe unavailable")
        return guarded_run(command, *args, **kwargs)

    with patch("subprocess.run", side_effect=without_optional_probe):
        importlib.import_module("numpy.testing")


def configure(mode: str, device: str) -> tuple[Any, dict[str, Any]]:
    """Configure one process before numerical work and record precision policy."""
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
        if len(affinity) < 8:
            raise RuntimeError("Eight application CPUs are required")
        os.sched_setaffinity(0, affinity[:8])
    prepare_testing_import()
    versions = runtime_versions()
    tf = adapter.require_tensorflow()
    tf.config.threading.set_intra_op_parallelism_threads(7)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.experimental.enable_op_determinism()
    tf.config.experimental.enable_tensor_float_32_execution(mode == "on")
    details = {}
    devices = tf.config.list_physical_devices("GPU")
    if device == "cpu":
        tf.config.set_visible_devices([], "GPU")
    else:
        if len(devices) != 1:
            raise RuntimeError("Exactly one GPU is required")
        details = tf.config.experimental.get_device_details(devices[0])
        if "A100" not in details.get("device_name", ""):
            raise RuntimeError("Expected A100")
        tf.config.experimental.set_memory_growth(devices[0], True)
    internal_config = importlib.import_module("tensorflow.python.framework.config")
    settings = {
        "versions": versions,
        "requested_device": device,
        "source_sha256": {
            **preflight.code_hashes(),
            "numerical_diagnostic.py": digest(Path(__file__)),
        },
        "python": sys.version,
        "application_affinity": (
            sorted(os.sched_getaffinity(0))
            if hasattr(os, "sched_getaffinity")
            else None
        ),
        "pid": os.getpid(),
        "tf32_requested": mode,
        "tf32_enabled": tf.config.experimental.tensor_float_32_execution_enabled(),
        "determinism_enabled": internal_config.is_op_determinism_enabled(),
        "mixed_precision_global_policy": tf.keras.mixed_precision.global_policy().name,
        "floatx": tf.keras.backend.floatx(),
        "tensorflow_build": tf.sysconfig.get_build_info(),
        "device_details": details,
        "environment": {
            key: os.environ.get(key)
            for key in (
                "TF_DETERMINISTIC_OPS",
                "CUBLAS_WORKSPACE_CONFIG",
                "NVIDIA_TF32_OVERRIDE",
                "TF_ENABLE_ONEDNN_OPTS",
                "CUDA_VISIBLE_DEVICES",
            )
        },
    }
    return tf, settings


def prepare(output: Path, tf: Any) -> None:
    """Recover archived inputs and reconstruct, save and label one weight set."""
    source = Path(__file__).parent / "execution_runs/20260913-compatibility/preserved"
    manifest = json.loads((source / "preservation.json").read_text())
    if digest(source / "payload.tar.gz") != manifest["archive_sha256"]:
        raise ValueError("Historical archive mismatch")
    with tarfile.open(source / "payload.tar.gz") as archive:
        stream = archive.extractfile("attempt/preflight/nominal.npz")
        assert stream is not None
        payload = stream.read()
    if (
        hashlib.sha256(payload).hexdigest()
        != manifest["files"]["attempt/preflight/nominal.npz"]["sha256"]
    ):
        raise ValueError("Historical input mismatch")
    (output / "inputs.npz").write_bytes(payload)
    with np.load(output / "inputs.npz", allow_pickle=False) as saved:
        inputs = dict(saved)
    tf.keras.utils.set_random_seed(1701)
    candidate.comparison_model_type()
    preflight.packing_checks(tf, "/CPU:0")
    original = preflight.original_module()
    norm, fixtures = preflight.fixtures()
    with tf.device("/CPU:0"):
        model = original.build_comparison(norm, routing="pooled")
        model(inputs)
    weights = model.get_weights()
    np.savez(
        output / "weights.npz", **{f"w{i}": weight for i, weight in enumerate(weights)}
    )
    write_json(output / "model-config.json", model.get_config())
    fixture_exact = array_hash([inputs[key] for key in sorted(inputs)]) == array_hash(
        [fixtures["nominal"][key] for key in sorted(inputs)]
    )
    receipt = {
        "historical_inputs_exact": fixture_exact,
        "input_sha256": digest(output / "inputs.npz"),
        "weights_sha256": digest(output / "weights.npz"),
        "weights_array_sha256": array_hash(weights),
        "parameters": model.count_params(),
        "normalization": model.normalization_config,
        "weight_shapes": [list(weight.shape) for weight in weights],
        "weight_dtypes": [str(weight.dtype) for weight in weights],
        "historical_weights": "Not saved by job 58240587; these are a seed-1701 recipe reconstruction, not verified original bytes",
    }
    write_json(output / "bundle.json", receipt)
    if not fixture_exact or model.count_params() != 17329:
        raise AssertionError(
            "Bundle reconstruction integrity failure; saved evidence retained"
        )


def worker(
    bundle: Path, output: Path, tf: Any, device: str, settings: dict[str, Any]
) -> None:
    """Capture three repeated CPU/target traces using exactly copied weights."""
    verify_seal(bundle)
    with np.load(bundle / "inputs.npz", allow_pickle=False) as saved:
        inputs = dict(saved)
    with np.load(bundle / "weights.npz", allow_pickle=False) as saved:
        weights = [saved[f"w{i}"] for i in range(len(saved.files))]
    config = json.loads((bundle / "model-config.json").read_text())
    original = preflight.original_module()
    records: dict[str, Any] = {}
    settings["layer_policies"] = {}
    for label, target, module in (
        ("cpu", "/CPU:0", original),
        ("target", "/GPU:0" if device == "gpu" else "/CPU:0", candidate),
    ):
        with tf.device(target):
            model = module.comparison_model_type().from_config(config)
            model.build({key: value.shape for key, value in inputs.items()})
            model.set_weights(weights)
            np.savez(
                output / f"{label}-copied-weights.npz",
                **{f"w{i}": value for i, value in enumerate(model.get_weights())},
            )
            settings["layer_policies"][label] = [
                {
                    "name": layer.name,
                    "compute_dtype": layer.compute_dtype,
                    "variable_dtype": layer.variable_dtype,
                    "activation": layer.get_config()["activation"],
                }
                for encoder in model.encoders
                for layer in encoder.token_mlp.layers
            ]
            write_json(output / "settings.json", settings)
            for repetition in range(3):
                capture = Capture(
                    output / f"{label}-{repetition}",
                    tf,
                    output / f"cpu-{repetition}" if label == "target" else None,
                )
                records[f"{label}-{repetition}"] = capture_model(model, inputs, capture)
            if label == "cpu":
                propagated_reference(
                    model, inputs, output / "cpu-0", output / "propagated64.npz"
                )
            records[label + "-weights-exact"] = array_hash(
                model.get_weights()
            ) == array_hash(weights)
    write_json(
        output / "capture.json",
        {
            "terminal": "CAPTURE_COMPLETE",
            "parity": records,
            "bundle_hashes": {
                name: digest(bundle / name)
                for name in ("inputs.npz", "weights.npz", "model-config.json")
            },
            "training_authorized": False,
        },
    )
    verify_seal(bundle)


def main() -> None:
    """Prepare or capture one process; error receipts never authorize training."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "capture"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--tf32", choices=("on", "off"), default="off")
    parser.add_argument("--device", choices=("cpu", "gpu"), default="cpu")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        tf, settings = configure(args.tf32, args.device)
        write_json(args.output / "settings.json", settings)
        if (
            not settings["determinism_enabled"]
            or settings["tf32_enabled"] != (args.tf32 == "on")
            or settings["mixed_precision_global_policy"] != "float32"
        ):
            raise RuntimeError("Unexpected precision or determinism configuration")
        if args.phase == "prepare":
            if args.device != "cpu":
                raise ValueError("Bundle preparation must use CPU")
            prepare(args.output, tf)
        else:
            if args.bundle is None:
                raise ValueError("Capture requires --bundle")
            worker(args.bundle, args.output, tf, args.device, settings)
        write_json(
            args.output / "terminal.json",
            {
                "terminal": "COMPLETE_DIAGNOSTIC",
                "wall_seconds": time.monotonic() - started,
                "calibration_authorized": False,
            },
        )
    except Exception as error:
        write_json(
            args.output / "terminal.json",
            {
                "terminal": "TECHNICAL_FAILURE",
                "error_type": type(error).__name__,
                "error": str(error),
                "wall_seconds": time.monotonic() - started,
                "calibration_authorized": False,
            },
        )
        raise
    finally:
        seal(args.output)


if __name__ == "__main__":
    main()
