#!/usr/bin/env python3
"""Tests for the GAP-3 non-finite-energy diagnostic contract."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType

import numpy as np


PET_DIR = Path(__file__).resolve().parent
REPO_ROOT = PET_DIR.parents[1]
DIAGNOSTIC_PATH = PET_DIR / "diagnose_gap3_nonfinite_energy.py"
LAUNCHER_PATH = PET_DIR / "sbatch_gap3_nonfinite_diagnostic.sh"
PROPOSAL_PATH = (
    REPO_ROOT
    / "docs/orchestration/state/gate6-gap3-nonfinite-diagnostic-proposal-20260830.json"
)
PRESERVED_HASHES = {
    REPO_ROOT
    / "docs/orchestration/"
    "PREDECLARATION-20260830-gate6-gap3-reco-truncation-changed-retry1.md": (
        "fc1772058469a34293ba1d8a162c1fe3b6cd3c2ade6c7bd31a65a39bda06c648"
    ),
    PET_DIR / "sbatch_gap3_reco_truncation_changed_retry1.sh": (
        "ffadc05bd186d950b718be3f7e4e8d9e9a9563b771ea2cb3097cc6e933cd16db"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-reco-truncation-changed-retry1-launch-57729539.json": (
        "48a638a593eed9e3ebe9c9fc62da6c6e721816aa1bf4c49c4c2a18e229403015"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-reco-truncation-changed-retry1-terminal-57729539.json": (
        "42e2609ebc8c7cf4c0a9b501935b9df94a18549f5deae9e78c12b1a9cd1d09ef"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-reco-truncation-changed-retry1-result-57729539.json.gz": (
        "7c8ff0dc0baa4fd03d29534a2a24558f7705d2e9cd914aa219e528071e0cbf6e"
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


DIAGNOSTIC = _load_module(DIAGNOSTIC_PATH, "gap3_nonfinite_diagnostic_test")


def test_preserved_invalid_result_artifacts_are_unchanged() -> None:
    for path, expected in PRESERVED_HASHES.items():
        assert DIAGNOSTIC.sha256_file(path) == expected


def test_exact_production_stable_sort_and_nonfinite_classes() -> None:
    energies = [2.0, math.nan, math.inf, 2.0, -math.inf, 1.0]
    source_index = list(range(len(energies)))
    ranked = DIAGNOSTIC.production_sort((energies, source_index))
    assert ranked[:, 1].astype(int).tolist() == [2, 0, 3, 5, 4, 1]
    assert DIAGNOSTIC.classify_nonfinite(math.nan) == "nan"
    assert DIAGNOSTIC.classify_nonfinite(math.inf) == "positive_infinity"
    assert DIAGNOSTIC.classify_nonfinite(-math.inf) == "negative_infinity"
    assert DIAGNOSTIC.classify_nonfinite(1.0) is None


def test_padding_and_source_to_npz_mapping() -> None:
    padded = DIAGNOSTIC.production_pad(([2.0, 1.0], [20.0, 10.0]), cap=3)
    np.testing.assert_array_equal(
        padded,
        np.asarray([[2.0, 20.0], [1.0, 10.0], [0.0, 0.0]], np.float32),
    )
    kept = np.asarray([1, 3, 8, 11], dtype=np.uint64)
    assert DIAGNOSTIC.npz_row_for_source_entry(kept, 8) == 2
    try:
        DIAGNOSTIC.npz_row_for_source_entry(kept, 7)
    except RuntimeError:
        pass
    else:
        raise AssertionError("unretained source entry did not fail closed")


def test_hash_bound_production_mask_path() -> None:
    path = DIAGNOSTIC.inspect_source_paths(REPO_ROOT)
    assert all(path["checks"].values())
    assert path["energy_gt_zero_guard_present"] is False
    assert path["token_removed_before_model_call"] is False
    assert path["initial_dense_encoding_precedes_body_mask"] is True
    assert path["first_body_attention_has_padding_key_mask"] is False


def test_proposal_scope_resources_and_denominator_rule() -> None:
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
    assert proposal["authorization"]["further_retry"] is False
    assert proposal["expected_counts"]["nonfinite_raw_energy_entries"] == {
        "signal": 1687,
        "data": 456,
        "background": 223,
        "total": 2366,
    }
    assert proposal["frozen_diagnostic"]["denominator_pass_recommendation"] == (
        "FINITE_POSITIVE_PET_ELIGIBLE_CLUSTERS"
    )
    assert "do_not_retrain" in proposal["non_authorization"]


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
        f"Features={fields['features']} TresPerTask={fields['tres_per_task']}"
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


def test_positive_and_negative_launcher_resource_guards() -> None:
    accepted = _validate_resource_fixture(_resource_fixture())
    assert accepted.returncode == 0, accepted.stderr
    invalid = (
        _resource_fixture(num_cpus="8", cpus_per_task="8", tres_per_task="cpu=8"),
        _resource_fixture(time_limit="04:00:00"),
        _resource_fixture(req_tres="billing=18,cpu=18,mem=64G,node=1"),
        _resource_fixture(req_tres="billing=18,cpu=18,mem=32G,node=1,gres/gpu=1"),
        _resource_fixture(features="gpu"),
    )
    for job_spec in invalid:
        rejected = _validate_resource_fixture(job_spec)
        assert rejected.returncode == 3
        assert "[gap3-nfd-launch][FAIL]" in rejected.stderr


def test_launcher_directives_and_authorization_token() -> None:
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")
    for directive in (
        "#SBATCH --constraint=cpu",
        "#SBATCH --cpus-per-task=18",
        "#SBATCH --mem=32G",
        "#SBATCH --time=02:00:00",
        "#SBATCH --no-requeue",
    ):
        assert directive in launcher
    assert "#SBATCH --gres" not in launcher
    assert "OMP_NUM_THREADS=18" in launcher
    assert "ROOT_MAX_THREADS=18" in launcher
    assert "PET-G6-GAP3-NONFINITE-DIAGNOSTIC-20260830-ONE-SCAN" in launcher


if __name__ == "__main__":
    test_preserved_invalid_result_artifacts_are_unchanged()
    test_exact_production_stable_sort_and_nonfinite_classes()
    test_padding_and_source_to_npz_mapping()
    test_hash_bound_production_mask_path()
    test_proposal_scope_resources_and_denominator_rule()
    test_positive_and_negative_launcher_resource_guards()
    test_launcher_directives_and_authorization_token()
    print("PASS: GAP-3 non-finite diagnostic contract tests")
