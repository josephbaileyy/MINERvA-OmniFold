"""Fail-closed contracts for deterministic packing preflight evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "pet/direct_token_comparison")
)
import compatibility_preflight as preflight  # noqa: E402


def test_exact_packing_and_cpu_integer_placement() -> None:
    tf = preflight.adapter.require_tensorflow()
    result = preflight.packing_checks(tf, "/CPU:0")
    assert result["exact_comparisons"] == 16
    assert result["max_abs"] == 0
    assert result["invalid_cases_rejected"] == 4


@pytest.fixture
def receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(preflight, "code_hashes", lambda: {"candidate": "current"})
    monkeypatch.setattr(preflight, "runtime_versions", lambda: {"tensorflow": "2.16.2"})
    models = [
        {"case": case, "routing": route, "device": "/device:GPU:0"}
        for case in preflight.CASES
        for route in ("pooled", "direct")
    ]
    names = {f"{case}.npz" for case in preflight.CASES}
    names.update(
        f"{case}-{route}.{suffix}"
        for case in preflight.CASES
        for route in ("pooled", "direct")
        for suffix in ("keras", "npy")
    )
    for name in names:
        (tmp_path / name).write_bytes(b"fixture")
    (tmp_path / "reload.json").write_text(
        json.dumps(
            {
                "terminal": "PASS",
                "models": models,
                "precision_policy": preflight.runner.PRECISION_POLICY,
            }
        )
    )
    artifacts = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in tmp_path.iterdir()
    }
    record = {
        "terminal": "PASS",
        "mode": "gpu",
        "code_sha256": preflight.code_hashes(),
        "versions": preflight.runtime_versions(),
        "models": models,
        "artifacts": artifacts,
        "determinism": True,
        "precision_policy": preflight.runner.PRECISION_POLICY,
        "cpu_oracle_sha256": preflight.REFERENCE_SHA,
    }
    (tmp_path / "preflight.json").write_text(json.dumps(record))
    return tmp_path


def test_complete_receipt_contract(receipt: Path) -> None:
    assert preflight.verify_receipt(receipt)["terminal"] == "PASS"


@pytest.mark.parametrize(
    "key,value",
    [
        ("terminal", "INCOMPLETE"),
        ("mode", "cpu"),
        ("code_sha256", {}),
        ("versions", {}),
        ("models", []),
        ("artifacts", {}),
        ("determinism", False),
        ("cpu_oracle_sha256", "wrong"),
    ],
)
def test_reject_incomplete_or_stale_receipt(
    receipt: Path, key: str, value: Any
) -> None:
    path = receipt / "preflight.json"
    record = json.loads(path.read_text())
    record[key] = value
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        preflight.verify_receipt(receipt)


def test_reject_changed_artifact(receipt: Path) -> None:
    (receipt / "empty-direct.keras").write_bytes(b"changed")
    with pytest.raises(ValueError, match="artifact mismatch"):
        preflight.verify_receipt(receipt)


@pytest.mark.parametrize(
    "policy", [{}, {**preflight.runner.PRECISION_POLICY, "tf32_enabled": True}]
)
def test_reject_wrong_precision_receipt(receipt: Path, policy: dict[str, Any]) -> None:
    path = receipt / "preflight.json"
    record = json.loads(path.read_text())
    record["precision_policy"] = policy
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="determinism/oracle"):
        preflight.verify_receipt(receipt)


def test_reject_reload_precision_even_with_matching_hash(receipt: Path) -> None:
    path = receipt / "reload.json"
    record = json.loads(path.read_text())
    record["precision_policy"]["tf32_enabled"] = True
    path.write_text(json.dumps(record))
    parent = receipt / "preflight.json"
    outer = json.loads(parent.read_text())
    outer["artifacts"]["reload.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
    parent.write_text(json.dumps(outer))
    with pytest.raises(ValueError, match="reload"):
        preflight.verify_receipt(receipt)


def test_precision_setup_and_drift_detection() -> None:
    tf = preflight.adapter.require_tensorflow()
    tf.config.experimental.enable_tensor_float_32_execution(True)
    assert preflight.runner.configure_precision() == preflight.runner.PRECISION_POLICY
    tf.config.experimental.enable_tensor_float_32_execution(True)
    try:
        with pytest.raises(RuntimeError, match="Precision policy mismatch"):
            preflight.runner.precision_settings()
    finally:
        preflight.runner.configure_precision()


def test_mixed_precision_is_rejected() -> None:
    tf = preflight.adapter.require_tensorflow()
    original = tf.keras.mixed_precision.global_policy()
    tf.keras.mixed_precision.set_global_policy("mixed_float16")
    try:
        with pytest.raises(RuntimeError, match="Precision policy mismatch"):
            preflight.runner.configure_precision()
    finally:
        tf.keras.mixed_precision.set_global_policy(original)
        preflight.runner.configure_precision()


def test_runner_configures_before_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse

    tf = preflight.adapter.require_tensorflow()
    tf.config.experimental.enable_tensor_float_32_execution(True)

    def fixture(*args: Any) -> Any:
        assert (
            preflight.runner.precision_settings() == preflight.runner.PRECISION_POLICY
        )
        raise LookupError("fixture boundary")

    monkeypatch.setattr(preflight.runner, "make_fixture", fixture)
    with pytest.raises(LookupError, match="fixture boundary"):
        preflight.runner.run(argparse.Namespace(rows=4))


@pytest.mark.parametrize(
    "name", ["calibration.json", "measurement.json", "environment.json"]
)
def test_calibration_rejects_policy_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    import evaluate_calibration as evaluator

    monkeypatch.setattr(evaluator, "verify_receipt", lambda path: {})
    (tmp_path / "terminal.txt").write_text("COMPLETE")
    (tmp_path / "exit-code.txt").write_text("0")
    (tmp_path / "tests.log").write_text("69 passed, 10 subtests passed")
    for guard in ("tests-guard.json", "preflight-guard.json", "guard.json"):
        (tmp_path / guard).write_text(
            json.dumps({"verdict": "REPOSITORY-ORIGINS-INSPECTED", "allow": []}) + "\n"
        )
    measured = tmp_path / "measurement"
    measured.mkdir()
    for filename in ("calibration.json", "measurement.json", "environment.json"):
        policy = dict(preflight.runner.PRECISION_POLICY)
        if filename == name:
            policy["tf32_enabled"] = True
        (measured / filename).write_text(json.dumps({"precision_policy": policy}))
    with pytest.raises(ValueError, match="precision policy"):
        evaluator.evaluate(tmp_path, 100, 395)
