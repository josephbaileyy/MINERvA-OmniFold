"""PET command wiring and fail-closed stage boundaries; no training or ROOT jobs."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from production.minerva_production import pet
from production.minerva_production.storage import ROOT, digest


@pytest.mark.parametrize(
    "stage,config,runtime,native_stage",
    [
        ("infer", {"weights": "/data/training/weights.npz"}, "tensorflow", "push"),
        (
            "extract",
            {"push": "/data/inference/push.npz", "mcfile": "/data/flux.root"},
            "ROOT",
            "xsec",
        ),
    ],
)
def test_extraction_plans(
    stage: str, config: dict[str, Any], runtime: str, native_stage: str, tmp_path: Path
) -> None:
    plan = pet.plan(config, tmp_path / "events.npz", tmp_path / "out", stage)
    argv = plan["argv"]
    assert argv[1:6] == [
        str(ROOT / "nd-unfolding/mnv_guarded_run.py"),
        "--expect-root",
        str(ROOT),
        "--",
        str(ROOT / "nd-unfolding/pet/extract_fullevent_fps.py"),
    ]
    assert argv[argv.index("--stage") + 1] == native_stage
    assert plan["runtime"] == runtime
    assert plan["missing_paths"]
    assert "--allow-overwrite" not in argv and "--step2-checkpoint" not in argv
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("stage", ["infer", "extract"])
def test_stage_runtime_and_inventory_binding(
    stage: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    events = tmp_path / "events.npz"
    events.write_bytes(b"small opaque event inventory")
    source = tmp_path / "source.npz"
    np.savez(source, inputs_sha256="wrong inventory")
    flux = tmp_path / "flux.root"
    flux.touch()
    config = (
        {"weights": str(source)}
        if stage == "infer"
        else {"push": str(source), "mcfile": str(flux)}
    )
    output = tmp_path / "out"
    plan = pet.plan(config, events, output, stage)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    with pytest.raises(ValueError, match="requires the .* environment"):
        pet.run(plan, output)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    with pytest.raises(ValueError, match="input digest differs"):
        pet.run(plan, output)
    assert not output.exists()


@pytest.mark.parametrize("stage", ["infer", "extract"])
@pytest.mark.parametrize("marker_valid", [True, False])
def test_native_completion_is_required(
    stage: str, marker_valid: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    events = tmp_path / "events.npz"
    events.write_bytes(b"opaque event inventory")
    source = tmp_path / "source.npz"
    np.savez(source, inputs_sha256=digest(events))
    flux = tmp_path / "flux.root"
    flux.touch()
    config = (
        {"weights": str(source)}
        if stage == "infer"
        else {"push": str(source), "mcfile": str(flux)}
    )
    output = tmp_path / "out"
    plan = pet.plan(config, events, output, stage)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    calls = []

    def native_stage(argv: list[str], **kwargs: Any) -> None:
        calls.append((argv, kwargs))
        for name in plan["products"]:
            product = output / name
            product.write_bytes(b"native product stand-in")
            if product.suffix == ".npz":
                (output / (name + ".done")).write_text(
                    json.dumps(
                        {
                            "size": product.stat().st_size if marker_valid else -1,
                            "mtime": int(product.stat().st_mtime),
                        }
                    )
                )

    monkeypatch.setattr(pet.subprocess, "run", native_stage)
    monkeypatch.setattr(pet, "provenance", lambda: {"revision": "a" * 40})
    if not marker_valid:
        with pytest.raises(ValueError, match="incompatible native completion marker"):
            pet.run(plan, output)
        assert (
            json.loads((output / "production.json").read_text())["status"] == "started"
        )
        return
    pet.run(plan, output)
    record = json.loads((output / "production.json").read_text())
    assert record["status"] == "complete"
    assert set(record["product_sha256"]) == set(plan["products"])
    assert calls == [(plan["argv"], {"check": True, "cwd": ROOT / "nd-unfolding/pet"})]
    with pytest.raises(FileExistsError, match="fresh namespace"):
        pet.run(plan, output)


def test_refuses_policy_override(tmp_path: Path) -> None:
    for extra in (
        {"subsample_agreement_tol": 1.0},
        {"step2_checkpoint": "other"},
        {"chunk": 0},
    ):
        with pytest.raises(ValueError):
            pet.plan(
                {"weights": "weights.npz", **extra},
                tmp_path / "events.npz",
                tmp_path / "out",
                "infer",
            )
