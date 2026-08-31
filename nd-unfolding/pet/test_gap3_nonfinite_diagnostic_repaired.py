#!/usr/bin/env python3
"""Tests for the repaired GAP-3 non-finite-energy diagnostic contract."""

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
LAUNCHER_PATH = PET_DIR / "sbatch_gap3_nonfinite_diagnostic_repaired.sh"
PREDECLARATION_PATH = (
    REPO_ROOT
    / "docs/orchestration/"
    "PREDECLARATION-20260831-gate6-gap3-nonfinite-diagnostic-repaired.md"
)
PROPOSAL_PATH = (
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-nonfinite-diagnostic-repaired-proposal-20260831.json"
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
    REPO_ROOT
    / "docs/orchestration/"
    "PREDECLARATION-20260830-gate6-gap3-nonfinite-diagnostic.md": (
        "679ea7f9d10f1c5f5fa1e6b9fd4ca818175070dadd69c5073a8bf63a435ecf59"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-nonfinite-diagnostic-proposal-20260830.json": (
        "3229afc3828e3b3e9db356ce685bdc0c3156ff79118f5e82e62814288e66ebf9"
    ),
    PET_DIR / "sbatch_gap3_nonfinite_diagnostic.sh": (
        "c84871436a9f03a0c1f6b927a3a321c682b497d0d0473b8b1101cc3e551951d7"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-nonfinite-diagnostic-launch-57743781.json": (
        "f43a8c45c1ca5e8a35cd1da4dcfa5e62363b78c75a21395b7f09b8f9412c696e"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-nonfinite-diagnostic-terminal-57743781.json": (
        "a0220ef3fcb375fdc783ef550922816669cc785a06683b569a5e9668171cbdd0"
    ),
    REPO_ROOT
    / "docs/orchestration/state/"
    "gate6-gap3-nonfinite-mapping-repair-proposal-20260831.json": (
        "b59569787c088f80f5c03d3e356cc212e823ba010f7bc4c89a5c2f84d667c358"
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


DIAGNOSTIC = _load_module(DIAGNOSTIC_PATH, "gap3_nonfinite_repaired_test")


def test_preserved_failed_artifacts_are_unchanged() -> None:
    for path, expected in PRESERVED_HASHES.items():
        assert DIAGNOSTIC.sha256_file(path) == expected


def test_real_entry_predicates_and_mapping_regressions() -> None:
    keep, selected, pass_truth = DIAGNOSTIC.evaluate_signal_predicates(
        -9999.0,
        -9999.0,
        0,
        0.2756309263353958,
        5.606105907302817,
    )
    assert (keep, selected, pass_truth) == (True, False, True)

    try:
        DIAGNOSTIC.map_prefixes_from_predicates(
            [(10_152_799, selected, keep)], [10_152_799]
        )
    except RuntimeError as error:
        assert str(error) == "affected source entry 10152799 is not selected"
    else:
        raise AssertionError("the historical mapping contradiction did not fail")

    rows = (
        (10_152_798, True, True),
        (10_152_799, selected, keep),
        (10_152_800, True, True),
    )
    npz_rows, kept_rows = DIAGNOSTIC.map_prefixes_from_predicates(
        rows, [10_152_800]
    )
    assert npz_rows == [2]
    assert kept_rows == 3


def test_exact_stable_sort_and_nonfinite_classes() -> None:
    energies = [2.0, math.nan, math.inf, 2.0, -math.inf, 1.0]
    ranked = DIAGNOSTIC.production_sort((energies, range(len(energies))))
    assert ranked[:, 1].astype(int).tolist() == [2, 0, 3, 5, 4, 1]
    assert DIAGNOSTIC.classify_nonfinite(math.nan) == "nan"
    assert DIAGNOSTIC.classify_nonfinite(math.inf) == "positive_infinity"
    assert DIAGNOSTIC.classify_nonfinite(-math.inf) == "negative_infinity"


def test_root_vector_materialization_avoids_array_protocol() -> None:
    class RootVectorFixture:
        def __init__(self) -> None:
            self.values = (1.0, math.nan, math.inf, -math.inf)

        def __len__(self) -> int:
            return len(self.values)

        def __iter__(self):
            return iter(self.values)

        def __array__(self, *_args, **_kwargs):
            raise OverflowError("ROOT vector buffer conversion failed")

    materialized = DIAGNOSTIC.materialize_float64_vector(RootVectorFixture())
    assert materialized.shape == (4,)
    assert np.isfinite(materialized).tolist() == [True, False, False, False]


def test_signal_mapping_is_streaming_and_implicit_mt_is_absent() -> None:
    source = DIAGNOSTIC_PATH.read_text(encoding="utf-8")
    assert "gap3diag.scan_inventory" in source
    assert "result.affected.push_back" in source
    assert "result.kept_rows" in source
    assert "RDataFrame" not in source
    assert "AsNumpy" not in source
    assert "kept_payload" not in source
    assert "ROOT.EnableImplicitMT" not in source
    assert "ROOT.DisableImplicitMT" in source
    assert 'choices=(1,)' in source
    assert "complete_kept_index_materialized" in source


def test_production_loader_and_model_paths_are_bound() -> None:
    path = DIAGNOSTIC.inspect_source_paths(REPO_ROOT)
    assert all(path["checks"].values())
    assert path["energy_gt_zero_guard_present"] is False
    assert path["actual_energy_mask_predicate"] == (
        "energy != 0 after loader nonfinite-to-zero sanitization"
    )
    assert path["token_removed_before_model_call"] is False
    assert path["initial_dense_encoding_precedes_body_mask"] is True
    assert path["first_body_attention_has_padding_key_mask"] is False


def test_launchable_proposal_and_artifact_bindings() -> None:
    proposal = json.loads(PROPOSAL_PATH.read_text(encoding="utf-8"))
    assert proposal["status"] == "AUTHORIZED_PENDING_PREFLIGHT"
    assert proposal["authorization"]["launchable"] is True
    assert proposal["authorization"]["maximum_submissions"] == 1
    assert proposal["authorization"]["automatic_retry"] is False
    assert proposal["authorization"]["unchanged_retry"] is False
    assert proposal["resources"] == {
        "constraint": "cpu",
        "allocated_cpus": 18,
        "source_identity_threads": 1,
        "root_implicit_multithreading": False,
        "walltime_hours": 2,
        "cpu_hour_allocation_ceiling": 36,
        "memory_gib": 32,
        "gpus": 0,
        "nodes": 1,
        "tasks": 1,
    }
    bindings = proposal["artifact_bindings"]
    for key, path in (
        ("diagnostic", DIAGNOSTIC_PATH),
        ("predeclaration", PREDECLARATION_PATH),
        ("test", Path(__file__).resolve()),
    ):
        assert bindings[key]["digest"] == f"sha256:{DIAGNOSTIC.sha256_file(path)}"
    assert proposal["mapping"]["complete_kept_index_materialized"] is False
    assert "do_not_authorize_further_compute" in proposal["non_authorization"]


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


def test_positive_and_negative_resource_guards() -> None:
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
        assert "[gap3-nfd-repaired][FAIL]" in rejected.stderr


def test_launcher_contract() -> None:
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
    assert "OMP_NUM_THREADS=1" in launcher
    assert "ROOT_MAX_THREADS=1" in launcher
    assert "--threads 1" in launcher
    assert "mnv_guarded_run.py" in launcher
    assert "NONFINITE-DIAGNOSTIC-REPAIRED-20260831-ONE-SCAN" in launcher


if __name__ == "__main__":
    test_preserved_failed_artifacts_are_unchanged()
    test_real_entry_predicates_and_mapping_regressions()
    test_exact_stable_sort_and_nonfinite_classes()
    test_root_vector_materialization_avoids_array_protocol()
    test_signal_mapping_is_streaming_and_implicit_mt_is_absent()
    test_production_loader_and_model_paths_are_bound()
    test_launchable_proposal_and_artifact_bindings()
    test_positive_and_negative_resource_guards()
    test_launcher_contract()
    print("PASS: repaired GAP-3 non-finite diagnostic contract tests")
