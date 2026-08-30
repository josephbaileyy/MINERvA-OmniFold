#!/usr/bin/env python3
"""Regression tests for the GAP-3 changed-retry contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType


PET_DIR = Path(__file__).resolve().parent
REPO_ROOT = PET_DIR.parents[1]
CORE_PATH = PET_DIR / "audit_reco_truncation.py"
WRAPPER_PATH = PET_DIR / "audit_reco_truncation_changed_retry1.py"
LAUNCHER_PATH = PET_DIR / "sbatch_gap3_reco_truncation_changed_retry1.sh"
PROPOSAL_PATH = (
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-reco-truncation-changed-retry1-proposal-20260830.json"
)
ORIGINAL_HASHES = {
    REPO_ROOT
    / "docs/orchestration/"
    "PREDECLARATION-20260830-gate6-gap3-reco-truncation-audit.md": (
        "b69c296a1bd9be426c8acf78bd1232b780bd3c9e2b0b7924d09d241feb8260fc"
    ),
    PET_DIR / "sbatch_gap3_reco_truncation_audit.sh": (
        "4c23d6a2e2ee770a424c92d8c9eda67ac56dc3c7b8265dfdc3add73fe4325cfe"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-reco-truncation-launch-57727806.json": (
        "ade8f8755fa8cab04934e3828c651a9b131fe0a029c144533b52a2b671acf8e9"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-reco-truncation-terminal-57727806.json": (
        "4fcb7a58102e2c3e9f41808bc9bb68e8884a24b4602eac79252476e3f42fbb80"
    ),
}


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CORE = _load_module(CORE_PATH, "gap3_original_core_test")
WRAPPER = _load_module(WRAPPER_PATH, "gap3_retry_wrapper_test")


def test_original_artifacts_are_unchanged() -> None:
    for path, expected in ORIGINAL_HASHES.items():
        assert CORE.sha256_file(path) == expected


def test_scientific_core_and_operands_are_reused() -> None:
    assert WRAPPER.CORE_RELATIVE_PATH == Path(
        "nd-unfolding/pet/audit_reco_truncation.py"
    )
    assert WRAPPER.THREADS == 18
    assert CORE.sha256_file(CORE_PATH) == (
        "671531dd6a43a03203d4a8024d5671a7b357edad6e1fa7ab9ad7e44a99ac1e1a"
    )
    assert CORE.CAP == 12
    assert CORE.EXPECTED_SELECTED_ROWS == {
        "signal": 20_573_521,
        "data": 4_116_128,
        "background": 564_591,
    }
    assert len(CORE.PT_EDGES) - 1 == 15
    assert len(CORE.PPARALLEL_EDGES) - 1 == 19
    assert len(CORE.EAVAIL_EDGES) - 1 == 7
    assert len(CORE.Q3_EDGES) - 1 == 7


def test_proposal_freezes_resources_and_retry_boundary() -> None:
    proposal = json.loads(PROPOSAL_PATH.read_text(encoding="utf-8"))
    assert proposal["resources"] == {
        "constraint": "cpu",
        "cpus": 18,
        "root_threads": 18,
        "walltime_hours": 2,
        "cpu_hour_allocation_ceiling": 36,
        "memory_gib": 32,
        "gpus": 0,
        "nodes": 1,
        "tasks": 1,
    }
    assert proposal["authorization"]["maximum_submissions"] == 1
    assert proposal["authorization"]["automatic_retry"] is False
    assert proposal["authorization"]["unchanged_retry"] is False
    assert proposal["authorization"]["further_retry"] is False
    assert proposal["change_control"]["scientific_operands_changed"] is False
    for name, config in CORE.INVENTORIES.items():
        frozen = proposal["populations"][name]
        assert frozen["tree"] == config["tree"]
        assert frozen["selection"] == config["selection"]
        assert frozen["weight"] == config["weight"]
        assert frozen["axes"] == config["axes"]
        assert frozen["expected_rows"] == CORE.EXPECTED_SELECTED_ROWS[name]
    scientific = proposal["scientific_contract"]
    assert scientific["cap"] == CORE.CAP
    assert scientific["pt_edges_gev"] == list(CORE.PT_EDGES)
    assert scientific["pparallel_edges_gev"] == list(CORE.PPARALLEL_EDGES)
    assert scientific["eavail_edges_gev"] == list(CORE.EAVAIL_EDGES)
    assert scientific["q3_edges_gev"] == list(CORE.Q3_EDGES)


def _resource_fixture(**replacements: str) -> str:
    fields = {
        "num_cpus": "18",
        "cpus_per_task": "18",
        "time_limit": "02:00:00",
        "req_tres": "billing=18,cpu=18,mem=32G,node=1",
        "features": "cpu",
        "tres_per_task": "cpu=18",
    }
    fields.update(replacements)
    return (
        f"JobId=123 NumCPUs={fields['num_cpus']} "
        f"CPUs/Task={fields['cpus_per_task']} "
        f"TimeLimit={fields['time_limit']} "
        f"ReqTRES={fields['req_tres']} "
        f"MinMemoryNode=32G Features={fields['features']} "
        f"TresPerTask={fields['tres_per_task']}"
    )


def _validate_resource_fixture(job_spec: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as fixture:
        fixture.write(job_spec)
        fixture.flush()
        return subprocess.run(
            [str(LAUNCHER_PATH), "--validate-job-spec-file", fixture.name],
            check=False,
            capture_output=True,
            text=True,
        )


def test_positive_launcher_resource_guard() -> None:
    result = _validate_resource_fixture(_resource_fixture())
    assert result.returncode == 0, result.stderr
    assert "resource fixture PASS" in result.stdout


def test_negative_launcher_resource_guards() -> None:
    invalid_specs = (
        _resource_fixture(num_cpus="8", cpus_per_task="8", tres_per_task="cpu=8"),
        _resource_fixture(time_limit="04:00:00"),
        _resource_fixture(req_tres="billing=18,cpu=18,mem=64G,node=1"),
        _resource_fixture(req_tres="billing=18,cpu=18,mem=32G,node=1,gres/gpu=1"),
        _resource_fixture(features="gpu"),
    )
    for job_spec in invalid_specs:
        result = _validate_resource_fixture(job_spec)
        assert result.returncode == 3
        assert "[gap3-r1-launch][FAIL]" in result.stderr


def test_launcher_directives_and_token() -> None:
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert "#SBATCH --constraint=cpu" in launcher
    assert "#SBATCH --cpus-per-task=18" in launcher
    assert "#SBATCH --mem=32G" in launcher
    assert "#SBATCH --time=02:00:00" in launcher
    assert "#SBATCH --no-requeue" in launcher
    assert "#SBATCH --gres" not in launcher
    assert "OMP_NUM_THREADS=18" in launcher
    assert "ROOT_MAX_THREADS=18" in launcher
    assert "--threads 18" in launcher
    assert (
        "PET-G6-GAP3-RECO-TRUNCATION-20260830-CHANGED-RETRY1-ONE-SCAN"
        in launcher
    )


if __name__ == "__main__":
    test_original_artifacts_are_unchanged()
    test_scientific_core_and_operands_are_reused()
    test_proposal_freezes_resources_and_retry_boundary()
    test_positive_launcher_resource_guard()
    test_negative_launcher_resource_guards()
    test_launcher_directives_and_token()
    print("PASS: GAP-3 changed-retry contract tests")
