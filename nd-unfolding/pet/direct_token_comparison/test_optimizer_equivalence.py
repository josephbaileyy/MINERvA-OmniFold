"""Adversarial tests for the approved gate using preserved GPU evidence."""

from __future__ import annotations

import copy
import io
from pathlib import Path
import tarfile
from typing import Any

import numpy as np
import pytest

import compatibility_preflight as original
from optimizer_equivalence import key_bias_index, validate


@pytest.fixture(scope="module")
def evidence() -> tuple[Any, list[dict[str, Any]], list[dict[str, Any]]]:
    """Restore the captured failing case without starting a training job."""
    root = Path(__file__).parent
    with tarfile.open(
        root / "execution_runs/20260915-optimizer/payload.tar.gz"
    ) as archive:
        files = {m.name: archive.extractfile(m).read() for m in archive if m.isfile()}

    def arrays(name: str) -> dict[str, Any]:
        with np.load(
            io.BytesIO(files["capture/masked-direct/" + name]), allow_pickle=False
        ) as data:
            return dict(data)

    norm, cases = original.fixtures()
    model = original.candidate.build_comparison(norm, routing="direct")
    model(cases["masked"])
    traces = []
    replays = []
    for label in ("cpu", "candidate"):
        traces.append(
            {
                "states": [arrays(f"{label}/state-{i}.npz") for i in range(3)],
                "initial": arrays(f"{label}/eager.npz"),
                "repeated": arrays(f"{label}/repeated.npz"),
                "graph": arrays(f"{label}/graph.npz"),
                "second": arrays(f"{label}/second.npz"),
                "prediction": arrays(f"{label}/prediction.npz")["prediction"],
                "instrumentation_exact": True,
            }
        )
        replays.append(
            {
                "initial": arrays("initial-weights.npz"),
                "gradients": [
                    {
                        f"gradient_{i}": traces[-1][phase][f"gradient_{i}"]
                        for i in range(42)
                    }
                    for phase in ("initial", "second")
                ],
                "cpu": [arrays(f"replay-{label}-cpu/step-{i}.npz") for i in (1, 2)],
                "candidate": [
                    arrays(f"replay-{label}-candidate/step-{i}.npz") for i in (1, 2)
                ],
                "float64": [arrays(f"float64-{label}-{i}.npz") for i in (1, 2)],
            }
        )
    return model, traces, replays


def test_captured_key_bias_failure_is_explained(evidence: Any) -> None:
    model, traces, replays = evidence
    result = validate(model, traces, replays, exact_cpu=False)
    assert result["terminal"] == "PASS"
    assert result["key_bias_index"] == 27
    assert result["raw_key_bias_max_abs_by_step"][1] > 1e-5
    assert result["common_operand_max_abs"] < 3e-8
    with pytest.raises(AssertionError):
        validate(model, traces, replays, exact_cpu=True)


@pytest.mark.parametrize(
    "corruption",
    [
        "ordinary_weight",
        "query_bias",
        "gradient",
        "prediction",
        "slot",
        "operand",
        "initial_operand",
        "replay",
        "native_parity",
        "float64",
        "missing_step",
        "missing_tensor",
        "nonfinite_bias",
        "missing_origin",
        "repeatability",
        "graph",
    ],
)
def test_corruption_rejects(evidence: Any, corruption: str) -> None:
    model, source, replay_source = evidence
    traces, replays = copy.deepcopy((source, replay_source))
    if corruption in ("ordinary_weight", "query_bias"):
        key = "weight_0" if corruption == "ordinary_weight" else "weight_25"
        traces[1]["states"][2][key].flat[0] += 0.1
    elif corruption == "gradient":
        traces[1]["second"]["gradient_27"].flat[0] += 0.1
    elif corruption == "prediction":
        traces[1]["prediction"].flat[0] += 0.1
    elif corruption == "slot":
        replays[1]["candidate"][1]["slot_4"].flat[0] += 0.1
    elif corruption == "operand":
        # Break the alias to the source derivative deliberately.
        replays[1]["gradients"][0]["gradient_0"] = (
            replays[1]["gradients"][0]["gradient_0"].copy() + 0.1
        )
    elif corruption == "initial_operand":
        replays[1]["initial"]["weight_0"].flat[0] += 0.1
    elif corruption == "replay":
        replays[0]["cpu"][1]["weight_27"].flat[0] += 0.1
    elif corruption == "native_parity":
        traces[1]["instrumentation_exact"] = False
    elif corruption == "float64":
        replays[1]["float64"][1]["weight_27"].flat[0] += 0.1
    elif corruption == "missing_step":
        replays[0]["candidate"].pop()
    elif corruption == "missing_tensor":
        traces[1]["states"][1].pop("slot_4")
    elif corruption == "nonfinite_bias":
        traces[1]["states"][1]["weight_27"].flat[0] = np.nan
    elif corruption == "missing_origin":
        traces.pop()
    elif corruption == "repeatability":
        traces[1]["repeated"]["gradient_27"].flat[0] += 1e-9
    else:
        traces[1]["graph"]["gradient_27"].flat[0] += 0.1
    with pytest.raises((ValueError, AssertionError)):
        validate(model, traces, replays, exact_cpu=False)


def test_query_cannot_impersonate_key(
    evidence: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    model, _, _ = evidence
    monkeypatch.setattr(model.attention, "_key_dense", model.attention.query_dense)
    with pytest.raises(ValueError):
        key_bias_index(model)


@pytest.mark.parametrize(
    "corruption",
    [
        "missing_case",
        "duplicate_case",
        "wrong_shape",
        "wrong_index",
        "cpu_only",
        "wrong_policy",
        "legacy_gate",
    ],
)
def test_receipt_rejects_incomplete_or_wrong_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corruption: str
) -> None:
    """Incomplete case coverage cannot release calibration even with a PASS label."""
    import json
    import amended_preflight as amended

    monkeypatch.setattr(amended, "hashes", lambda: {})
    monkeypatch.setattr(amended, "runtime_versions", lambda: {})
    models = [
        {
            "case": case,
            "routing": route,
            "gate": {
                "terminal": "PASS",
                "key_bias_index": 27,
                "key_bias_shape": [4, 8],
            },
            "device": "/GPU:0",
        }
        for case in original.CASES
        for route in ("pooled", "direct")
    ]
    receipt = {
        "terminal": "PASS",
        "gate": amended.GATE,
        "mode": "gpu",
        "code_sha256": {},
        "versions": {},
        "precision_policy": dict(amended.runner.PRECISION_POLICY),
        "tolerance": {"atol": original.ATOL, "rtol": original.RTOL},
        "models": models,
    }
    if corruption == "missing_case":
        models.pop()
    elif corruption == "duplicate_case":
        models[-1] = models[0]
    elif corruption == "wrong_shape":
        models[0]["gate"]["key_bias_shape"] = [2, 16]
    elif corruption == "wrong_index":
        models[0]["gate"]["key_bias_index"] = 25
    elif corruption == "cpu_only":
        receipt["mode"] = "cpu"
    elif corruption == "wrong_policy":
        receipt["precision_policy"]["tf32_enabled"] = True
    else:
        receipt["gate"] = "unamended"
    (tmp_path / "preflight.json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        amended.verify_receipt(tmp_path)
