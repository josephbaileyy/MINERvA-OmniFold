"""Guarded training, full-inventory inference and diagnostic PET extraction."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from .storage import ROOT, digest, provenance, read_json


def plan(
    config: dict[str, Any], input_path: Path, output: Path, stage: str = "train"
) -> dict[str, Any]:
    """Resolve explicit PET inputs and training policy without importing TensorFlow."""
    if stage in {"infer", "extract"}:
        return extraction_plan(config, input_path, output, stage)
    if stage != "train":
        raise ValueError(f"unsupported PET stage: {stage}")
    policy = {
        "estimator_seed": 42,
        "subsample_seed": 0,
        "niter": 3,
        "epochs": 8,
        "max_events": 2000000,
        "batch_size": 512,
    }
    required = {"target_npy", "target_receipt", "gate3_manifest"}
    if required - config.keys() or set(config) - (
        required | policy.keys() | {"representation", "background"}
    ):
        raise ValueError(
            "PET config requires target_npy, target_receipt, gate3_manifest and only supported training settings"
        )
    resolved = {
        **policy,
        "representation": "pet-fullevent-fps-v1",
        "background": "negweight-refined",
        **config,
    }
    if (
        resolved["representation"] != "pet-fullevent-fps-v1"
        or resolved["background"] != "negweight-refined"
    ):
        raise ValueError(
            "PET adapter requires full-event FPS v1 with the certified negweight-refined target"
        )
    for key, value in policy.items():
        if resolved[key] != value:
            raise ValueError(
                f"PET {key} must retain {value}; another training policy requires a separate supported path"
            )
    argv = [
        sys.executable,
        str(ROOT / "nd-unfolding/mnv_guarded_run.py"),
        "--expect-root",
        str(ROOT),
        "--",
        str(ROOT / "nd-unfolding/pet/train_fullevent_nominal.py"),
        "--inputs",
        str(input_path),
        "--out",
        str(output / "weights.npz"),
    ]
    required_paths = [input_path]
    for key in sorted(required):
        path = Path(resolved[key]).expanduser().resolve()
        resolved[key] = str(path)
        required_paths.append(path)
        argv += ["--" + key.replace("_", "-"), str(path)]
    for key in policy:
        argv += ["--" + key.replace("_", "-"), str(resolved[key])]
    return {
        "status": "plan-only",
        "stage": stage,
        "input": str(input_path),
        "products": ["weights.npz"],
        "runtime": "tensorflow",
        "resolved_config": resolved,
        "argv": argv,
        "missing_paths": [str(path) for path in required_paths if not path.is_file()],
        "scientific_status": "PET diagnostic/method development; central/statistical pairing declined",
        "environment": "TensorFlow training; use infer then extract in separate processes",
        "requirements": [
            "Certified target/row inventory and Gate-3 bindings are checked by the retained driver.",
            "The checkout guard refuses any legacy import from another checkout.",
            "No PET uncertainty construction or Gate-6 action is exposed.",
        ],
    }


def extraction_plan(
    config: dict[str, Any], input_path: Path, output: Path, stage: str
) -> dict[str, Any]:
    """Resolve retained extraction stages without importing either heavy runtime."""
    if stage == "infer":
        required = {"weights"}
        defaults: dict[str, Any] = {"chunk": 250000, "batch_size": 4096}
        products = ["push.npz"]
        runtime = "tensorflow"
    elif stage == "extract":
        required = {"push", "mcfile"}
        defaults = {
            "flux_hist": "pTmu_reweightedflux_integrated",
            "n_nucleons": 3.2353e30,
        }
        products = ["xsec.npz", "summary.json"]
        runtime = "ROOT"
    else:
        raise ValueError(f"unsupported extraction stage: {stage}")
    if required - config.keys() or set(config) - (required | defaults.keys()):
        raise ValueError(
            f"PET {stage} requires {sorted(required)} and supports {sorted(defaults)}"
        )
    resolved = {**defaults, **config}
    paths = [input_path]
    for key in sorted(required):
        path = Path(resolved[key]).expanduser().resolve()
        resolved[key] = str(path)
        paths.append(path)
    if stage == "infer":
        for key in defaults:
            if type(resolved[key]) is not int or resolved[key] <= 0:
                raise ValueError(f"PET {key} must be a positive integer")
    elif (
        not isinstance(resolved["n_nucleons"], (int, float))
        or not math.isfinite(resolved["n_nucleons"])
        or resolved["n_nucleons"] <= 0
        or not isinstance(resolved["flux_hist"], str)
        or not resolved["flux_hist"]
    ):
        raise ValueError(
            "PET extraction requires a positive nucleon count and named flux histogram"
        )
    argv = [
        sys.executable,
        str(ROOT / "nd-unfolding/mnv_guarded_run.py"),
        "--expect-root",
        str(ROOT),
        "--",
        str(ROOT / "nd-unfolding/pet/extract_fullevent_fps.py"),
        "--stage",
        "push" if stage == "infer" else "xsec",
        "--inputs",
        str(input_path),
    ]
    if stage == "infer":
        argv += [
            "--weights",
            resolved["weights"],
            "--push-out",
            str(output / "push.npz"),
        ]
    else:
        argv += [
            "--push-out",
            resolved["push"],
            "--mcfile",
            resolved["mcfile"],
            "--out",
            str(output / "xsec.npz"),
            "--summary",
            str(output / "summary.json"),
        ]
    for key in defaults:
        argv += ["--" + key.replace("_", "-"), str(resolved[key])]
    return {
        "status": "plan-only",
        "stage": stage,
        "input": str(input_path),
        "products": products,
        "runtime": runtime,
        "resolved_config": resolved,
        "argv": argv,
        "missing_paths": [str(path) for path in paths if not path.is_file()],
        "scientific_status": "PET diagnostic/method development; central/statistical pairing declined",
        "environment": f"{runtime}; stages never combine TensorFlow and ROOT in one process",
        "requirements": [
            "Full-inventory inference, native architecture and agreement checks remain in the retained extractor.",
            "The weights/push input digest must match the supplied full-event inventory.",
            "No checkpoint override, overwrite, PET covariance or Gate-6 operation is exposed.",
        ],
    }


def _input_binding(resolved_plan: dict[str, Any]) -> str:
    import numpy as np

    stage = resolved_plan["stage"]
    input_digest = digest(Path(resolved_plan["input"]))
    if stage != "train":
        key = "weights" if stage == "infer" else "push"
        with np.load(
            resolved_plan["resolved_config"][key], allow_pickle=True
        ) as archive:
            recorded = archive["inputs_sha256"].item()
        if recorded != input_digest:
            raise ValueError(
                f"PET {key} input digest differs from the full-event inventory"
            )
    return input_digest


def run(resolved_plan: dict[str, Any], output: Path) -> None:
    """Run one guarded stage and preserve native products and completion markers."""
    import importlib.util

    if resolved_plan["missing_paths"]:
        raise ValueError(f"PET prerequisites missing: {resolved_plan['missing_paths']}")
    runtime = resolved_plan["runtime"]
    if importlib.util.find_spec(runtime) is None:
        raise ValueError(
            f"PET {resolved_plan['stage']} requires the {runtime} environment"
        )
    if output.exists():
        raise FileExistsError(
            f"{output}: PET outputs require a fresh namespace; native evidence is never overwritten"
        )
    input_digest = _input_binding(resolved_plan)
    source_paths = [
        "production/minerva_production/pet.py",
        "production/minerva_production/storage.py",
        "production/unfold_pet.py",
        "nd-unfolding/mnv_guarded_run.py",
        str(Path(resolved_plan["argv"][5]).relative_to(ROOT)),
    ]
    output.mkdir(parents=True)
    record = {
        **resolved_plan,
        "status": "started",
        "provenance": provenance(),
        "entrypoint_sources": {path: digest(ROOT / path) for path in source_paths},
        "input_sha256": input_digest,
    }
    (output / "production.json").write_text(json.dumps(record, indent=2))
    subprocess.run(resolved_plan["argv"], check=True, cwd=ROOT / "nd-unfolding/pet")
    products = {}
    for name in resolved_plan["products"]:
        product = output / name
        if product.suffix == ".npz":
            marker = read_json(output / (name + ".done"))
            if marker.get("size") != product.stat().st_size or marker.get(
                "mtime"
            ) != int(product.stat().st_mtime):
                raise ValueError(
                    f"PET stage left an incompatible native completion marker: {name}"
                )
        products[name] = digest(product)
    record.update({"status": "complete", "product_sha256": products})
    (output / "production.json").write_text(json.dumps(record, indent=2))


def main(argv: list[str] | None = None) -> int:
    """Expose diagnostic PET stages without loading the scalar training runtime."""
    parser = argparse.ArgumentParser(
        description="Guarded PET diagnostic training, full-inventory inference and ROOT extraction."
    )
    parser.add_argument(
        "stage", choices=["train", "infer", "extract"], nargs="?", default="train"
    )
    parser.add_argument(
        "--config", required=True, type=Path, help="stage-specific JSON configuration"
    )
    parser.add_argument(
        "--input", required=True, type=Path, help="immutable full-event inventory NPZ"
    )
    parser.add_argument(
        "--output", required=True, type=Path, help="fresh stage output directory"
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="resolve prerequisites without loading arrays or writing outputs",
    )
    args = parser.parse_args(argv)
    try:
        output = args.output.expanduser().resolve()
        resolved = plan(
            read_json(args.config),
            args.input.expanduser().resolve(),
            output,
            args.stage,
        )
        if args.plan:
            print(json.dumps(resolved, indent=2))
        else:
            run(resolved, output)
        return 0
    except (
        ValueError,
        KeyError,
        OSError,
        ImportError,
        subprocess.CalledProcessError,
    ) as exc:
        parser.error(str(exc))
    return 2
