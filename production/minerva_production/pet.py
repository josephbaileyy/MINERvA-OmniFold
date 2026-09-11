"""Guarded adapter for the retained full-event diagnostic training contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .storage import ROOT, code_identity, digest, read_json


def plan(config: dict[str, Any], input_path: Path, output: Path) -> dict[str, Any]:
    """Resolve explicit PET inputs and training policy without importing TensorFlow."""
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
        "resolved_config": resolved,
        "argv": argv,
        "missing_paths": [str(path) for path in required_paths if not path.is_file()],
        "scientific_status": "PET diagnostic/method development; central/statistical pairing declined",
        "environment": "TensorFlow training; ROOT extraction is a separate process using extract_fullevent_fps.py",
        "requirements": [
            "Certified target/row inventory and Gate-3 bindings are checked by the retained driver.",
            "The checkout guard refuses any legacy import from another checkout.",
            "No PET uncertainty construction or Gate-6 action is exposed.",
        ],
    }


def run(resolved_plan: dict[str, Any], output: Path) -> None:
    """Invoke guarded training and retain its native completion/evidence formats."""
    import importlib.util

    if resolved_plan["missing_paths"]:
        raise ValueError(f"PET prerequisites missing: {resolved_plan['missing_paths']}")
    if importlib.util.find_spec("tensorflow") is None:
        raise ValueError(
            "PET training requires the TensorFlow environment; ROOT-only Python cannot train"
        )
    if output.exists():
        raise FileExistsError(
            f"{output}: PET outputs require a fresh namespace; native evidence is never overwritten"
        )
    output.mkdir(parents=True)
    record = {**resolved_plan, "status": "started", "code": code_identity()}
    (output / "production.json").write_text(json.dumps(record, indent=2))
    subprocess.run(resolved_plan["argv"], check=True, cwd=ROOT / "nd-unfolding/pet")
    weights = output / "weights.npz"
    marker = read_json(output / "weights.npz.done")
    if marker.get("size") != weights.stat().st_size or marker.get("mtime") != int(
        weights.stat().st_mtime
    ):
        raise ValueError(
            "PET trainer did not leave a compatible native completion marker"
        )
    record.update({"status": "complete", "weights_sha256": digest(weights)})
    (output / "production.json").write_text(json.dumps(record, indent=2))
