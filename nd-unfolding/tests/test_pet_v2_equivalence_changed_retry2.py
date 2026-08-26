#!/usr/bin/env python3
"""CPU-only contract and import controls for PET-v2 changed retry 2."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PET = REPO / "nd-unfolding/pet"
DERIVER = REPO / "docs/orchestration/derive_pet_v2_equivalence_changed_retry2.py"
PROPOSAL_PATH = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry2-proposal-20260826.json"
)
ATTEMPT_PATH = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry1-attempt-57626676.json"
)
SUBMISSION_PATH = (
    REPO
    / "docs/orchestration/state/"
    "pet-v2-fixed-draw-equivalence-changed-retry2-submission-57629029.json"
)
SPEC = importlib.util.spec_from_file_location("derive_pet_v2_changed_retry2", DERIVER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PROPOSAL = json.loads(PROPOSAL_PATH.read_text(encoding="utf-8"))
ATTEMPT = json.loads(ATTEMPT_PATH.read_text(encoding="utf-8"))
SUBMISSION = json.loads(SUBMISSION_PATH.read_text(encoding="utf-8"))


def test_retry2_proposal_is_exact_deterministic_render():
    assert PROPOSAL == MODULE.build_proposal()


def test_retry1_terminal_receipt_is_machinery_only_and_zero_gpu():
    assert ATTEMPT["status"] == "INVALID_OR_INCOMPLETE_TARGET_ENVIRONMENT"
    assert ATTEMPT["target_scheduler_terminal"]["state"] == "FAILED"
    assert ATTEMPT["target_scheduler_terminal"]["exit_code"] == "1:0"
    assert ATTEMPT["runtime_evidence"]["target_artifact_published"] is False
    assert ATTEMPT["runtime_evidence"]["scientific_quantity_measured"] is False
    assert ATTEMPT["resource_consumption"]["a100_hours"] == 0.0
    assert ATTEMPT["C_stat"] is None and ATTEMPT["C_ML"] is None
    assert all(item["allocated_cpus"] == 0 for item in ATTEMPT["cancelled_downstream"].values())


def test_retry2_submission_is_one_changed_nonautomatic_chain():
    assert SUBMISSION == {
        "C_ML": None,
        "C_stat": None,
        "automatic_retry": False,
        "changed_retry_number": 2,
        "head": "27df34afa195da31ed4c82accdb9a875c894c295",
        "host": "login21",
        "jobs": {
            "evaluation": "57629031",
            "target": "57629029",
            "training_array": "57629030",
            "validation": "57629032",
        },
        "prior_target_job": "57626676",
        "proposal_sha256": (
            "ffa29bd36d5b2e9adcb6ca0d82d246cebc6e57950dcbb15e2840de9601757933"
        ),
        "schema": "pet-v2-equivalence-changed-retry2-submission-v1",
        "status": "SUBMITTED",
        "submitted_at_utc": "2026-08-26T20:58:17.689065+00:00",
        "unchanged_retry": False,
    }


def test_authorization_allows_changed_but_never_unchanged_retries():
    assert PROPOSAL["status"] == "AUTHORIZED_READY_CHANGED_RETRY"
    assert PROPOSAL["launchable"] is True
    authorization = PROPOSAL["authorization"]
    assert authorization["authorized_by"] == "Joseph"
    assert authorization["authorization_token"] == MODULE.AUTHORIZATION_TOKEN
    assert authorization["changed_retries_authorized"] is True
    assert authorization["unchanged_retry_authorized"] is False
    assert "Retries are authorized" in authorization["authorization_source"]


def test_only_changed_axis_is_target_package_initializer_bypass():
    change = PROPOSAL["changed_operand"]
    assert change["target_dataloader_sha256_preserved"] == (
        "bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a"
    )
    assert change["scientific_policy_change"] is False
    assert change["sampling_or_training_change"] is False
    paths = [item["path"] for item in
             PROPOSAL["guarded_executable_operands"]["future_required_operands"]]
    assert paths == list(MODULE.RETRY2_EXECUTABLES)
    assert "nd-unfolding/pet/train_pet_v2_equivalence_retry1.py" in paths
    assert "nd-unfolding/pet/evaluate_pet_v2_equivalence_retry1.py" in paths
    for item in PROPOSAL["guarded_executable_operands"]["future_required_operands"]:
        assert MODULE._sha256(REPO / item["path"]) == item["sha256"]


def test_target_bypass_loads_exact_dataloader_without_tensorflow():
    code = (
        "import pathlib,sys; "
        f"sys.path.insert(0,{str(PET)!r}); "
        "import pet_v2_target_package_bypass_retry2 as b; "
        "cls=b.install_target_dataloader(); "
        "assert cls.__module__=='omnifold.dataloader'; "
        "assert 'tensorflow' not in sys.modules; "
        "assert pathlib.Path(sys.modules['omnifold.dataloader'].__file__).resolve()==b.DATALOADER.resolve()"
    )
    cp = subprocess.run([sys.executable, "-c", code], check=False, text=True,
                        capture_output=True)
    assert cp.returncode == 0, cp.stderr
    assert "PASS target-only package initializer bypass" in cp.stderr


def test_retry2_target_wrapper_keeps_root_remap_and_frozen_original():
    env = os.environ.copy()
    env["PETV2_CODE_ROOT"] = str(REPO)
    env["PETV2_EXPECTED_HEAD"] = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    cp = subprocess.run(
        [sys.executable, str(REPO / "nd-unfolding/mnv_guarded_run.py"),
         "--expect-root", str(REPO), "--",
         str(PET / "materialize_pet_v2_equivalence_target_retry2.py"), "--help"],
        env=env, check=False, text=True, capture_output=True,
    )
    assert cp.returncode == 0, cp.stderr
    assert cp.stderr.count("[pet-v2-root-remap]") == 2
    assert "[pet-v2-target-import] PASS" in cp.stderr
    assert "IMPORT TREE VIOLATION" not in cp.stderr


def test_retry2_controller_is_fail_closed_hash_bound_and_has_no_srun():
    controller = PET / "submit_pet_v2_equivalence_changed_retry2.sh"
    text = controller.read_text(encoding="utf-8")
    assert "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY2-20260826" in text
    assert "materialize_pet_v2_equivalence_target_retry2.py" in text
    assert "train_pet_v2_equivalence_retry1.py" in text
    assert "evaluate_pet_v2_equivalence_retry1.py" in text
    assert "validate_pet_v2_equivalence_result_retry2.py" in text
    assert "pet_v2_target_package_bypass_retry2.py" in text
    assert "--constraint='gpu&hbm80g'" in text
    assert "PETV2_PREFLIGHT_ONLY" in text
    assert not any(line.lstrip().startswith("srun ") for line in text.splitlines())
    assert subprocess.run(["bash", "-n", str(controller)], check=False).returncode == 0


def test_thresholds_resources_prohibitions_and_non_authorizations_stay_frozen():
    assert PROPOSAL["controls"]["threshold_derivation"]["same_arm_validity_cap_S"] == 0.0251
    assert PROPOSAL["controls"]["threshold_derivation"]["cross_arm_materiality_margin_M"] == 0.0502
    resource = PROPOSAL["resource_estimate"]
    assert resource["authorized_total_envelope"]["a100_hour_ceiling"] == 18.0
    assert resource["authorized_total_envelope"]["cpu_node_hour_ceiling"] == 5.0
    assert resource["consumed_by_failed_attempts"]["a100_hours"] == 0.0
    assert resource["consumed_by_failed_attempts"]["cpu_node_hours"] == (
        0.13694444444444442
    )
    assert PROPOSAL["prohibitions_applied"] == {
        key: True for key in MODULE.PROHIBITIONS
    }
    cannot = PROPOSAL["what_every_terminal_result_cannot_authorize"]
    for key in MODULE.PROHIBITIONS:
        assert key in cannot
    assert PROPOSAL["existing_gate6_results_remain_blocked"] is True
    assert PROPOSAL["C_stat"] is None and PROPOSAL["C_ML"] is None


def test_retry2_validator_changes_only_retry_contract_identity():
    wrapper = (PET / "validate_pet_v2_equivalence_result_retry2.py").read_text(
        encoding="utf-8"
    )
    assert "validate_pet_v2_equivalence_result_retry1 as validator" in wrapper
    assert "changed-retry2-independent-readback-v1" in wrapper
    assert "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY2-20260826" in wrapper
