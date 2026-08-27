#!/usr/bin/env python3
"""CPU-only contract and archive controls for PET-v2 changed retry 3."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PET = REPO / "nd-unfolding/pet"
DERIVER = REPO / "docs/orchestration/derive_pet_v2_equivalence_changed_retry3.py"
PROPOSAL_PATH = REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry3-proposal-20260826.json"
ATTEMPT_PATH = REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry2-attempt-57629029.json"
SUBMISSION_PATH = REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry3-submission-57644535.json"
ARCHIVE = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas/replica_00/target/GATE5_REPLICA_TARGET.npy")
ARCHIVE_RECEIPT = ARCHIVE.with_name("GATE5_REPLICA_TARGET_RECEIPT.json")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DERIVE = load_module("derive_pet_v2_changed_retry3", DERIVER)
TARGET = load_module("materialize_pet_v2_retry3", PET / "materialize_pet_v2_equivalence_target_retry3.py")
PROPOSAL = json.loads(PROPOSAL_PATH.read_text(encoding="utf-8"))
ATTEMPT = json.loads(ATTEMPT_PATH.read_text(encoding="utf-8"))
SUBMISSION = json.loads(SUBMISSION_PATH.read_text(encoding="utf-8"))


def test_retry3_proposal_is_exact_deterministic_render():
    assert PROPOSAL == DERIVE.build_proposal()


def test_retry2_attempt_is_preserved_as_zero_gpu_invalid_machinery():
    assert ATTEMPT["status"] == "INVALID_OR_INCOMPLETE_WEIGHTED_TARGET_REPRODUCIBILITY"
    assert ATTEMPT["target_scheduler_terminal"] == {
        "elapsed": "01:33:20", "end_utc": "2026-08-26T23:11:07Z",
        "exit_code": "1:0", "job_id": "57629029", "state": "FAILED",
    }
    assert ATTEMPT["resource_consumption"]["a100_hours"] == 0.0
    assert ATTEMPT["runtime_evidence"]["scientific_quantity_measured"] is False
    assert all(not item["allocated"] for item in ATTEMPT["cancelled_downstream"].values())
    assert ATTEMPT["C_stat"] is None and ATTEMPT["C_ML"] is None


def test_retry3_submission_is_one_changed_nonautomatic_chain():
    assert SUBMISSION["schema"] == "pet-v2-equivalence-changed-retry3-submission-v1"
    assert SUBMISSION["status"] == "SUBMITTED"
    assert SUBMISSION["head"] == "edccb7285b9ef8a995b70c6beceebb04d4fc2745"
    assert SUBMISSION["proposal_sha256"] == (
        "650b3425844be03cd3e0a00bf1289b0ae0d5c8556049815f9e7197038b6d12b4"
    )
    assert SUBMISSION["jobs"] == {
        "target": "57644535", "training_array": "57644536",
        "evaluation": "57644537", "validation": "57644538",
    }
    assert SUBMISSION["prior_target_job"] == "57629029"
    assert SUBMISSION["changed_retry_number"] == 3
    assert SUBMISSION["automatic_retry"] is False
    assert SUBMISSION["unchanged_retry"] is False
    assert SUBMISSION["C_stat"] is None and SUBMISSION["C_ML"] is None


def test_archived_weighted_target_and_receipt_are_exact_operands():
    target, receipt, values = TARGET.validate_archive(ARCHIVE, ARCHIVE_RECEIPT)
    assert target == ARCHIVE.resolve()
    assert receipt == ARCHIVE_RECEIPT.resolve()
    assert values.shape == (4680719,)
    assert values.dtype == np.float32
    assert TARGET.sha256_file(target) == TARGET.WEIGHTED_SHA256


def test_two_call_refiner_reuses_weighted_then_calls_literal_once():
    class FE:
        @staticmethod
        def inventory_order_hash(_value):
            return TARGET.SIGNED_TARGET_HASH

    archive = np.asarray([0.0, 1.0, 2.0], np.float32)
    literal_calls = []

    def literal(feat, signed, **kwargs):
        literal_calls.append((np.asarray(feat).copy(), np.asarray(signed).copy(), kwargs))
        return np.asarray([3.0, 4.0], np.float64)

    refiner = TARGET.make_archive_then_literal(FE, archive, literal)
    first = refiner(np.zeros((3, 2)), np.ones(3), random_state=45)
    second = refiner(np.zeros((2, 2)), np.ones(2), random_state=45)
    assert np.array_equal(first, archive.astype(np.float64))
    assert np.array_equal(second, np.asarray([3.0, 4.0]))
    assert refiner.calls["count"] == 2
    assert len(literal_calls) == 1
    try:
        refiner(np.zeros((1, 2)), np.ones(1))
    except SystemExit as exc:
        assert "unexpected third refinement call" in str(exc)
    else:
        raise AssertionError("third refinement call did not fail closed")


def test_retry3_controller_is_hash_bound_and_has_no_srun():
    controller = PET / "submit_pet_v2_equivalence_changed_retry3.sh"
    text = controller.read_text(encoding="utf-8")
    assert "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY3-20260826" in text
    assert "materialize_pet_v2_equivalence_target_retry3.py" in text
    assert "train_pet_v2_equivalence_retry1.py" in text
    assert "evaluate_pet_v2_equivalence_retry1.py" in text
    assert "validate_pet_v2_equivalence_result_retry3.py" in text
    assert TARGET.WEIGHTED_SHA256 in text
    assert TARGET.RECEIPT_SHA256 in text
    assert "--constraint='gpu&hbm80g'" in text
    assert "PETV2_PREFLIGHT_ONLY" in text
    assert not any(line.lstrip().startswith("srun ") for line in text.splitlines())
    assert subprocess.run(["bash", "-n", str(controller)], check=False).returncode == 0


def test_retry3_hashes_resources_and_prohibitions_are_frozen():
    assert PROPOSAL["authorization"]["changed_retries_authorized"] is True
    assert PROPOSAL["authorization"]["unchanged_retry_authorized"] is False
    assert PROPOSAL["archived_weighted_operand"]["sha256"] == TARGET.WEIGHTED_SHA256
    assert PROPOSAL["resource_estimate"]["consumed_by_failed_attempts"] == {
        "a100_hours": 0.0, "cpu_node_hours": 1.6925,
    }
    assert PROPOSAL["resource_estimate"]["remaining_total_envelope"]["cpu_node_hours"] == 3.3075
    assert PROPOSAL["prohibitions_applied"] == {key: True for key in DERIVE.PROHIBITIONS}
    assert PROPOSAL["existing_gate6_results_remain_blocked"] is True
    assert PROPOSAL["C_stat"] is None and PROPOSAL["C_ML"] is None
    for item in PROPOSAL["guarded_executable_operands"]["future_required_operands"]:
        assert DERIVE._sha256(REPO / item["path"]) == item["sha256"]


def test_retry3_validator_changes_only_contract_identity():
    text = (PET / "validate_pet_v2_equivalence_result_retry3.py").read_text(encoding="utf-8")
    assert "validate_pet_v2_equivalence_result_retry1 as validator" in text
    assert "changed-retry3-independent-readback-v1" in text
    assert "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY3-20260826" in text
