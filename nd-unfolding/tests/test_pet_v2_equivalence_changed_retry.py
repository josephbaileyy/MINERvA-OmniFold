#!/usr/bin/env python3
"""CPU-only checks for the authorized PET-v2 changed-retry proposal."""

import importlib.util
import json
import os
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DERIVER = REPO / "docs/orchestration/derive_pet_v2_equivalence_changed_retry.py"
PROPOSAL_PATH = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry-proposal-20260826.json"
)
ATTEMPT_PATH = (
    REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-attempt-57620796.json"
)

SPEC = importlib.util.spec_from_file_location("derive_pet_v2_changed_retry", DERIVER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PROPOSAL = json.loads(PROPOSAL_PATH.read_text(encoding="utf-8"))
ATTEMPT = json.loads(ATTEMPT_PATH.read_text(encoding="utf-8"))


def test_changed_retry_receipt_is_exact_deterministic_render():
    assert PROPOSAL == MODULE.build_proposal()


def test_failed_attempt_is_guard_only_and_used_no_gpu():
    assert ATTEMPT["status"] == "INVALID_OR_INCOMPLETE_GUARD_REFUSAL"
    assert ATTEMPT["runtime_evidence"]["target_artifact_published"] is False
    assert ATTEMPT["runtime_evidence"]["scientific_quantity_measured"] is False
    assert ATTEMPT["resource_consumption"]["a100_hours"] == 0.0
    assert ATTEMPT["submission"]["no_retry_path"] is True
    assert ATTEMPT["C_stat"] is None and ATTEMPT["C_ML"] is None


def test_changed_retry_has_one_exact_explicit_human_authorization():
    assert PROPOSAL["status"] == "AUTHORIZED_READY_CHANGED_RETRY"
    assert PROPOSAL["launchable"] is True
    assert PROPOSAL["authorization"] == {
        "authorized_by": "Joseph",
        "authorized_at_utc": MODULE.AUTHORIZATION_TIME_UTC,
        "authorization_source": (
            "Joseph's explicit user message 'I authorize it', received immediately after the "
            "named changed-retry scope and preflight-before-submission sequence were restated"
        ),
        "authorization_token": MODULE.AUTHORIZATION_TOKEN,
        "retry_authorized": True,
        "authorized_action": (
            "one CPU target, three dependent single-A100-80GB arms, one CPU evaluation, and "
            "one read-only CPU validation for this named contract only, conditional on every "
            "guard and preflight passing"
        ),
        "no_further_retry": True,
    }
    assert PROPOSAL["compute_decision"] == (
        "AUTHORIZED_CONDITIONAL_SUBMISSION_AFTER_ALL_CHANGED_RETRY_PREFLIGHTS"
    )
    assert PROPOSAL["prior_authorization_is_exhausted"] is True


def test_only_changed_axis_is_retry_specific_checkout_root_remap():
    change = PROPOSAL["changed_operand"]
    assert change["measured_source_sha256_preserved"] == MODULE.OLD_LOADER_SHA256
    assert MODULE._sha256(REPO / change["measured_source"]) == MODULE.OLD_LOADER_SHA256
    assert change["new_executable_paths"] == list(MODULE.RETRY_EXECUTABLES)
    assert change["new_support_paths"] == list(MODULE.RETRY_SUPPORT)
    assert change["scientific_policy_change"] is False
    assert change["sampling_or_training_change"] is False
    assert PROPOSAL["controls"]["only_changed_axis"] == (
        "process-local checkout-root remap before frozen PET operands execute"
    )
    for item in PROPOSAL["guarded_executable_operands"]["future_required_operands"]:
        assert MODULE._sha256(REPO / item["path"]) == item["sha256"]


def test_retry_controller_is_separate_fail_closed_and_has_no_srun():
    controller = REPO / "nd-unfolding/pet/submit_pet_v2_equivalence_changed_retry.sh"
    text = controller.read_text(encoding="utf-8")
    assert "AUTHORIZED_READY_CHANGED_RETRY" in text
    assert "explicit Joseph authorization" in text
    assert "materialize_pet_v2_equivalence_target_retry1.py" in text
    assert "train_pet_v2_equivalence_retry1.py" in text
    assert "evaluate_pet_v2_equivalence_retry1.py" in text
    assert "validate_pet_v2_equivalence_result_retry1.py" in text
    assert "--constraint='gpu&hbm80g'" in text
    assert "PETV2_PREFLIGHT_ONLY" in text
    assert not any(line.lstrip().startswith("srun ") for line in text.splitlines())
    assert subprocess.run(["bash", "-n", str(controller)], check=False).returncode == 0


def test_guarded_retry_target_wrapper_remaps_before_frozen_operand_import():
    env = os.environ.copy()
    env["PETV2_CODE_ROOT"] = str(REPO)
    env["PETV2_EXPECTED_HEAD"] = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    cp = subprocess.run(
        [
            os.sys.executable,
            str(REPO / "nd-unfolding/mnv_guarded_run.py"),
            "--expect-root", str(REPO),
            "--",
            str(REPO / "nd-unfolding/pet/materialize_pet_v2_equivalence_target_retry1.py"),
            "--help",
        ],
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )
    assert cp.returncode == 0, cp.stderr
    assert cp.stderr.count("[pet-v2-root-remap]") == 2
    assert "IMPORT TREE VIOLATION" not in cp.stderr


def test_thresholds_same_arm_and_resource_numbers_are_frozen():
    threshold = PROPOSAL["controls"]["threshold_derivation"]
    assert threshold["same_arm_validity_cap_S"] == 0.0251
    assert threshold["cross_arm_materiality_margin_M"] == 0.0502
    determinism = PROPOSAL["controls"]["determinism_and_same_arm_controls"]
    assert determinism["same_arm"].startswith("W_A and W_B")
    assert "A100-SXM4-80GB" in determinism["hardware"]
    resource = PROPOSAL["resource_estimate"]
    assert resource["already_consumed"]["a100_hours"] == 0.0
    assert resource["changed_retry_request_if_authorized"]["expected_a100_hours_rounded"] == 13.0
    assert resource["changed_retry_request_if_authorized"]["a100_hour_ceiling"] == 18.0
    assert resource["numeric_envelope_is_not_authorization"] is True


def test_every_result_preserves_exact_prohibitions_and_non_authorizations():
    assert PROPOSAL["prohibitions_applied"] == {
        key: True for key in MODULE.PROHIBITIONS
    }
    assert PROPOSAL["existing_gate6_results_remain_blocked"] is True
    cannot = PROPOSAL["what_every_terminal_result_cannot_authorize"]
    for key in MODULE.PROHIBITIONS:
        assert key in cannot
    assert any("interval coverage" in item for item in cannot)
    assert any("this one explicitly authorized changed retry" in item for item in cannot)
    assert PROPOSAL["C_stat"] is None and PROPOSAL["C_ML"] is None
