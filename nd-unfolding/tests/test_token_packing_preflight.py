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
        json.dumps({"terminal": "PASS", "models": models})
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
