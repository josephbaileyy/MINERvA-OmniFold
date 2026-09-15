"""Run the approved key-bias gate on frozen original-sequence initial weights."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

import numpy as np

import compatibility_preflight as original
from calibration_measure import runtime_versions
import typed_descriptor_keras as adapter
import typed_token_comparison as candidate
from optimizer_diagnostic import float64_adam, replay, save_arrays, trace
from optimizer_equivalence import validate
import run_typed_token_comparison as runner

GATE = "key-bias-common-operands-v1"


def hashes() -> dict[str, str]:
    """Bind the original scientific code and the complete amended gate."""
    base = Path(__file__).resolve().parent
    names = [
        "amended_preflight.py",
        "optimizer_equivalence.py",
        "optimizer_diagnostic.py",
        "freeze_preflight_initialization.py",
    ]
    return {
        **original.code_hashes(),
        **{
            f"direct_token_comparison/{n}": hashlib.sha256(
                (base / n).read_bytes()
            ).hexdigest()
            for n in names
        },
    }


def inventory(directory: Path) -> dict[str, str]:
    """Hash every closed output except the enclosing receipt itself."""
    return {
        str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(directory.rglob("*"))
        if p.is_file() and p != directory / "preflight.json"
    }


def verify_receipt(directory: Path, *, require_gpu: bool = True) -> dict[str, Any]:
    """Reject incomplete, changed, unbound or non-GPU amended preflights."""
    receipt: dict[str, Any] = json.loads((directory / "preflight.json").read_text())
    expected = {(c, r) for c in original.CASES for r in ("pooled", "direct")}
    if receipt.get("terminal") != "PASS" or receipt.get("gate") != GATE:
        raise ValueError("Complete amended preflight required")
    if require_gpu and receipt.get("mode") != "gpu":
        raise ValueError("GPU preflight required")
    if receipt["code_sha256"] != hashes() or receipt["versions"] != runtime_versions():
        raise ValueError("Amended preflight code/runtime mismatch")
    if receipt["precision_policy"] != runner.PRECISION_POLICY or receipt[
        "tolerance"
    ] != {"atol": original.ATOL, "rtol": original.RTOL}:
        raise ValueError("Preflight precision/tolerance changed")
    rows = receipt["models"]
    if len(rows) != 8 or {(r["case"], r["routing"]) for r in rows} != expected:
        raise ValueError("Incomplete amended coverage")
    if any(
        r["gate"]["terminal"] != "PASS"
        or r["gate"]["key_bias_index"] != 27
        or r["gate"]["key_bias_shape"] != [4, 8]
        or (require_gpu and "GPU:0" not in r["device"])
        for r in rows
    ):
        raise ValueError("Invalid model gate or device")
    if receipt["artifacts"] != inventory(directory):
        raise ValueError("Amended artifact inventory mismatch")
    required = (
        {f"{c}.npz" for c in original.CASES}
        | {f"{c}-{r}.{ext}" for c, r in expected for ext in ("keras", "npy")}
        | {"reload.json", "initialization/bundle.json"}
    )
    for case, route in expected:
        stem = f"{case}-{route}"
        required.add(f"{stem}/gate.json")
        for label in ("cpu", "candidate"):
            required.update(
                f"{stem}/{label}/{name}"
                for name in (
                    "state-0.npz",
                    "state-1.npz",
                    "state-2.npz",
                    "eager.npz",
                    "repeated.npz",
                    "graph.npz",
                    "second.npz",
                    "prediction.npz",
                    "variables.json",
                    "device.json",
                )
            )
            required.update(
                f"{stem}/{label}-{suffix}.npz" for suffix in ("tokens", "oracle")
            )
            for step in (1, 2):
                required.add(f"{stem}/float64-{label}-{step}.npz")
                required.update(
                    f"{stem}/replay-{label}-{device}/step-{step}.npz"
                    for device in ("cpu", "candidate")
                )
            role = "reference" if label == "cpu" else "candidate"
            required.add(f"initialization/initial/{stem}-{role}.npz")
    if not required.issubset(receipt["artifacts"]):
        raise ValueError("Required artifacts missing")
    original.verify_receipt(directory / "initialization/baseline", require_gpu=False)
    initialization = directory / "initialization"
    bundle = json.loads((initialization / "bundle.json").read_text())
    expected_bundle = {
        str(p.relative_to(initialization)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in initialization.rglob("*")
        if p.is_file() and p.name != "bundle.json"
    }
    if (
        bundle["terminal"] != "PASS"
        or len(bundle["rows"]) != 16
        or bundle["files"] != expected_bundle
    ):
        raise ValueError("Incomplete frozen initialization")
    reload = json.loads((directory / "reload.json").read_text())
    if (
        reload["terminal"] != "PASS"
        or reload["precision_policy"] != runner.PRECISION_POLICY
        or len(reload["models"]) != 8
        or {(r["case"], r["routing"]) for r in reload["models"]} != expected
    ):
        raise ValueError("Fresh reload incomplete")
    if require_gpu and any("GPU:0" not in r["device"] for r in reload["models"]):
        raise ValueError("Fresh reload was not on GPU")
    return receipt


def load_arrays(path: Path) -> dict[str, Any]:
    """Read only named numeric arrays from the closed initialization bundle."""
    with np.load(path, allow_pickle=False) as source:
        return dict(source)


def main() -> None:
    """Capture complete paired evidence before applying the amended gate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "gpu"), required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    before = hashes()
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
        if len(affinity) < 8:
            raise RuntimeError("Eight application CPUs required")
        os.sched_setaffinity(0, affinity[:8])
    versions = runtime_versions()
    bundle = json.loads((args.bundle / "bundle.json").read_text())
    if (
        bundle["terminal"] != "PASS"
        or bundle["recipe"] != "original-cpu-preflight-including-checkpoint-reload"
        or len(bundle["rows"]) != 16
        or bundle["code_sha256"] != original.code_hashes()
    ):
        raise ValueError("Invalid initialization recipe")
    actual_bundle = {
        str(p.relative_to(args.bundle)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in args.bundle.rglob("*")
        if p.is_file() and p.name != "bundle.json"
    }
    if bundle["files"] != actual_bundle:
        raise ValueError("Initialization bundle changed")
    original.verify_receipt(args.bundle / "baseline", require_gpu=False)
    shutil.copytree(args.bundle, args.output / "initialization")
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
        raise RuntimeError("Exactly one A100 required")
    else:
        tf.config.experimental.set_memory_growth(devices[0], True)
    device = "/GPU:0" if args.device == "gpu" else "/CPU:0"
    packing = original.packing_checks(tf, device)
    norm, generated = original.fixtures()
    reference = original.original_module()
    current_type = candidate.comparison_model_type()
    rows = []
    for case in original.CASES:
        inputs = load_arrays(args.bundle / "baseline" / f"{case}.npz")
        if inputs.keys() != generated[case].keys():
            raise ValueError("Frozen fixture inventory differs")
        for key in inputs:
            actual, expected = inputs[key], generated[case][key]
            if (
                actual.shape != expected.shape
                or actual.dtype != expected.dtype
                or actual.tobytes() != expected.tobytes()
            ):
                raise ValueError(
                    "Frozen raw fixture differs, including masked sentinels"
                )
        np.savez(args.output / f"{case}.npz", **inputs)
        for route in ("pooled", "direct"):
            stem = f"{case}-{route}"
            folder = args.output / stem
            folder.mkdir()
            frozen = load_arrays(args.bundle / "initial" / f"{stem}-reference.npz")
            frozen_candidate = load_arrays(
                args.bundle / "initial" / f"{stem}-candidate.npz"
            )
            weights = [frozen[f"weight_{i}"] for i in range(len(frozen))]
            for key in frozen:
                original.compare(frozen[key], frozen_candidate[key], exact=True)
            with tf.device("/CPU:0"):
                old = reference.build_comparison(norm, routing=route)
                old(inputs)
                old.set_weights(weights)
            with tf.device(device):
                new = candidate.build_comparison(norm, routing=route)
                new(inputs)
                new.set_weights(weights)
            traces = []
            for label, model, target in (
                ("cpu", old, "/CPU:0"),
                ("candidate", new, device),
            ):
                # Captured initial, gradients, slots and weights survive any later assertion.
                captured = trace(tf, model, inputs, target, folder / label)
                model.set_weights(weights)
                with tf.device(target):
                    tokens = model.route_tokens(inputs)
                save_arrays(
                    folder / f"{label}-tokens.npz",
                    {f"token_{i}": v for i, v in enumerate(tokens)},
                )
                oracle = original.exercise(tf, model, inputs, target)
                save_arrays(
                    folder / f"{label}-oracle.npz",
                    {
                        **{f"weight_{i}": v for i, v in enumerate(oracle["weights"])},
                        "prediction": oracle["prediction"],
                    },
                )
                for i, v in enumerate(oracle["weights"]):
                    original.compare(
                        v, captured["states"][2][f"weight_{i}"], exact=True
                    )
                original.compare(
                    oracle["prediction"], captured["prediction"], exact=True
                )
                captured["instrumentation_exact"] = True
                captured["device"] = oracle["device"]
                traces.append(captured)
            replays = []
            for label, captured in zip(("cpu", "candidate"), traces):
                gradients = [
                    [captured[phase][f"gradient_{i}"] for i in range(42)]
                    for phase in ("initial", "second")
                ]
                cpu = replay(
                    tf, weights, gradients, "/CPU:0", folder / f"replay-{label}-cpu"
                )
                gpu = replay(
                    tf, weights, gradients, device, folder / f"replay-{label}-candidate"
                )
                high = [
                    save_arrays(
                        folder / f"float64-{label}-{step}.npz",
                        {f"weight_{i}": v for i, v in enumerate(values)},
                    )
                    for step, values in enumerate(float64_adam(weights, gradients), 1)
                ]
                replays.append(
                    {
                        "initial": frozen,
                        "gradients": [
                            {f"gradient_{i}": v for i, v in enumerate(g)}
                            for g in gradients
                        ],
                        "cpu": cpu,
                        "candidate": gpu,
                        "float64": high,
                    }
                )
            a, b = (
                load_arrays(folder / f"{label}-tokens.npz")
                for label in ("cpu", "candidate")
            )
            if a.keys() != b.keys():
                raise ValueError("Token inventory differs")
            for i, key in enumerate(a):
                original.compare(a[key], b[key], exact=i > 0 or args.device == "cpu")
            gate = validate(new, traces, replays, exact_cpu=args.device == "cpu")
            tf.keras.utils.get_custom_objects()[
                "minerva_pet>TypedTokenComparison"
            ] = current_type
            new.save(args.output / f"{stem}.keras")
            np.save(args.output / f"{stem}.npy", traces[1]["prediction"])
            with tf.device(device):
                restored = tf.keras.models.load_model(args.output / f"{stem}.keras")
                original.compare(restored(inputs), traces[1]["prediction"], exact=True)
                for a, b in zip(restored.get_weights(), new.get_weights()):
                    original.compare(a, b, exact=True)
            row = {
                "case": case,
                "routing": route,
                "gate": gate,
                "device": traces[1]["device"],
            }
            (folder / "gate.json").write_text(json.dumps(row, indent=2) + "\n")
            rows.append(row)
            print(json.dumps(row), flush=True)
    subprocess.run(
        [
            sys.executable,
            str(Path(original.__file__).resolve()),
            "--device",
            args.device,
            "--output",
            str(args.output.resolve()),
            "--reload-only",
        ],
        check=True,
    )
    if hashes() != before:
        raise ValueError("Source changed during preflight")
    receipt = {
        "terminal": "PASS",
        "gate": GATE,
        "mode": args.device,
        "code_sha256": before,
        "versions": versions,
        "precision_policy": runner.precision_settings(),
        "tolerance": {"atol": original.ATOL, "rtol": original.RTOL},
        "packing": packing,
        "models": rows,
        "artifacts": inventory(args.output),
    }
    (args.output / "preflight.json").write_text(json.dumps(receipt, indent=2) + "\n")
    verify_receipt(args.output, require_gpu=args.device == "gpu")


if __name__ == "__main__":
    main()
