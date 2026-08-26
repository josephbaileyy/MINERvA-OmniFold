#!/usr/bin/env python3
"""Derive the authorized PET-v2 changed-retry-2 proposal deterministically."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PRIOR_PROPOSAL = (
    REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry-proposal-20260826.json"
)
PRIOR_SUBMISSION = (
    REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry-submission-57626676.json"
)
PRIOR_ATTEMPT = (
    REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry1-attempt-57626676.json"
)
OUTPUT = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry2-proposal-20260826.json"
)
EXPECTED_PRIOR_PROPOSAL_SHA256 = (
    "c1e63e90c720ef4b353e570c2a0735450712cc135850176cdb73ff4888acf43b"
)
EXPECTED_PRIOR_SUBMISSION_SHA256 = (
    "53a6edf2e2b83f3e302d801c46f9834367143387cff4928a6f4a87ee7c509713"
)
EXPECTED_PRIOR_ATTEMPT_SHA256 = (
    "923ca7456ff4a705dffb690f80522d54fa9a2cd9770d5be8e98417b0a1a963dd"
)
AUTHORIZATION_TOKEN = "JOSEPH-20260826-PETV2-CHANGED-RETRIES-AUTHORIZED"
AUTHORIZATION_RECORDED_AT_UTC = "2026-08-26T20:46:12Z"
PROHIBITIONS = (
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
)
RETRY2_EXECUTABLES = (
    "nd-unfolding/pet/materialize_pet_v2_equivalence_target_retry2.py",
    "nd-unfolding/pet/train_pet_v2_equivalence_retry1.py",
    "nd-unfolding/pet/evaluate_pet_v2_equivalence_retry1.py",
    "nd-unfolding/pet/validate_pet_v2_equivalence_result_retry2.py",
    "nd-unfolding/pet/submit_pet_v2_equivalence_changed_retry2.sh",
)
RETRY2_SUPPORT = (
    "nd-unfolding/pet/pet_v2_equivalence_common.py",
    "nd-unfolding/pet/pet_v2_equivalence_root_remap.py",
    "nd-unfolding/pet/pet_v2_target_package_bypass_retry2.py",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_bound(path: Path, expected_sha256: str) -> dict:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise RuntimeError(f"bound input drift: {path}: {observed} != {expected_sha256}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_proposal() -> dict:
    prior = _load_bound(PRIOR_PROPOSAL, EXPECTED_PRIOR_PROPOSAL_SHA256)
    submission = _load_bound(PRIOR_SUBMISSION, EXPECTED_PRIOR_SUBMISSION_SHA256)
    attempt = _load_bound(PRIOR_ATTEMPT, EXPECTED_PRIOR_ATTEMPT_SHA256)
    if submission["jobs"]["target"] != "57626676":
        raise RuntimeError("retry-1 submission identity drift")
    if attempt["status"] != "INVALID_OR_INCOMPLETE_TARGET_ENVIRONMENT":
        raise RuntimeError("retry-1 attempt is not the measured target-environment failure")
    if attempt["runtime_evidence"]["scientific_quantity_measured"] is not False:
        raise RuntimeError("retry-1 unexpectedly measured a scientific quantity")
    if attempt["resource_consumption"]["a100_hours"] != 0.0:
        raise RuntimeError("retry-1 unexpectedly consumed A100 time")
    if attempt["prohibitions_applied"] != list(PROHIBITIONS):
        raise RuntimeError("retry-1 prohibitions drift")

    required = {
        path: _sha256(REPO / path)
        for path in prior["guarded_executable_operands"]["required_current_sources"]
    }
    support = {path: _sha256(REPO / path) for path in RETRY2_SUPPORT}
    executables = [
        {"path": path, "sha256": _sha256(REPO / path),
         "status": "IMPLEMENTED_TESTED_HASH_BOUND"}
        for path in RETRY2_EXECUTABLES
    ]
    controls = copy.deepcopy(prior["controls"])
    controls["only_changed_axis"] = (
        "target-only bypass of the TensorFlow-importing omnifold package initializer while "
        "loading the identical hash-bound NumPy dataloader; root remap and all scientific "
        "operands remain unchanged"
    )
    consumed_cpu = float(attempt["resource_consumption"]["cumulative_attempt_cpu_node_hours"])
    proposal = {
        "schema": "pet-v2-fixed-draw-equivalence-changed-retry2-proposal-v1",
        "contract_id": "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY2-20260826",
        "status": "AUTHORIZED_READY_CHANGED_RETRY",
        "launchable": True,
        "compute_decision": "AUTHORIZED_CHANGED_RETRIES_WITHIN_FROZEN_SCOPE_AND_TOTAL_CEILING",
        "scope": prior["scope"],
        "authorization": {
            "authorized_by": "Joseph",
            "authorization_recorded_at_utc": AUTHORIZATION_RECORDED_AT_UTC,
            "authorization_source": (
                "Joseph's explicit user message 'Retries are authorized', after the retry-1 "
                "target-environment failure was reported"
            ),
            "authorization_token": AUTHORIZATION_TOKEN,
            "changed_retries_authorized": True,
            "unchanged_retry_authorized": False,
            "authorized_action": (
                "changed machinery retries needed to complete this one fixed-draw PET-v2 "
                "diagnostic, only while scientific controls and the total resource ceiling stay "
                "frozen; every attempt remains fail-closed and separately receipted"
            ),
        },
        "failed_attempts": {
            "initial_guard_job": "57620796",
            "retry1_target_job": "57626676",
            "retry1_attempt_receipt": str(PRIOR_ATTEMPT.relative_to(REPO)),
            "retry1_attempt_receipt_sha256": EXPECTED_PRIOR_ATTEMPT_SHA256,
            "scientific_quantity_measured": False,
            "a100_hours": 0.0,
        },
        "changed_operand": {
            "measured_failure": (
                "the ROOT Python 3.11 target process imported omnifold.dataloader; Python first "
                "executed omnifold/__init__.py, which imported TensorFlow even though the target "
                "uses only the NumPy DataLoader; that interpreter has ROOT but no TensorFlow"
            ),
            "positive_control": (
                "ordinary import fails with ModuleNotFoundError for tensorflow in the exact ROOT "
                "environment"
            ),
            "candidate_control": (
                "a target-only package shell loads dataloader.py at SHA-256 "
                "bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a, "
                "instantiates DataLoader, and leaves tensorflow absent"
            ),
            "only_change": (
                "install and verify that package shell in the target wrapper before running the "
                "unchanged target operand"
            ),
            "target_dataloader_sha256_preserved": (
                "bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a"
            ),
            "scientific_policy_change": False,
            "sampling_or_training_change": False,
        },
        "measured_quantity": prior["measured_quantity"],
        "controls": controls,
        "guarded_executable_operands": {
            "required_current_sources": required,
            "future_required_operands": executables,
            "new_support_sources": support,
            "runtime_head": (
                "one exact clean non-primary detached checkout containing these hashes; supplied "
                "without a default and recorded in the submission receipt"
            ),
            "new_output_namespace": (
                "mandatory and absent before submission; both earlier attempt directories remain "
                "immutable evidence"
            ),
            "guard": prior["guarded_executable_operands"]["guard"],
            "no_srun": True,
            "no_automatic_or_unchanged_retry": True,
        },
        "resource_estimate": {
            "method": prior["resource_estimate"]["method"],
            "authorized_total_envelope": {
                "expected_a100_hours_rounded": 13.0,
                "a100_hour_ceiling": 18.0,
                "cpu_node_hour_ceiling": 5.0,
                "hardware": "three parallel single-GPU A100-SXM4-80GB arms after one CPU target",
            },
            "consumed_by_failed_attempts": {
                "cpu_node_hours": consumed_cpu,
                "a100_hours": 0.0,
            },
            "remaining_total_envelope": {
                "cpu_node_hours": 5.0 - consumed_cpu,
                "a100_hours": 18.0,
            },
            "numeric_envelope_is_not_authorization_outside_this_scope": True,
        },
        "entry_tests_required_before_submission": [
            "ordinary omnifold.dataloader import fails on the measured TensorFlow initializer side effect",
            "target-only bypass imports the exact dataloader hash with TensorFlow absent",
            "guarded retry-2 target --help passes in the exact ROOT worker shell",
            "training and evaluation retain the unchanged retry-1 wrappers and TensorFlow interpreter",
            "all proposal/source/input/flux hashes, five prohibitions, output absence, clean detached checkout, scheduler, and A100-80GB constraint pass",
        ],
        "prohibitions_applied": {key: True for key in PROHIBITIONS},
        "existing_gate6_results_remain_blocked": True,
        "success_interpretation": prior["success_interpretation"],
        "failure_interpretation": (
            "INVALID_OR_INCOMPLETE supports only diagnosis and a scientifically unchanged, "
            "explicitly changed machinery retry within this authorization and total ceiling"
        ),
        "what_every_terminal_result_cannot_authorize": [
            *PROHIBITIONS,
            "cannot establish interval coverage or a valid PET uncertainty",
            "cannot establish ordinary closure beyond the measured fixed-draw projections",
            "cannot generalize equivalence beyond seed 50000 and this frozen PET-v2 policy",
            "cannot construct or adopt C_stat, C_ML, a total covariance or a central value",
            "cannot change a note, publication claim or PET diagnostic scope",
            "cannot authorize a coverage campaign, a larger family, convergence tuning, Leg 2, or Gate 6",
            "cannot erase or reinterpret either failed attempt receipt",
            "cannot authorize an unchanged retry or compute outside this fixed-draw diagnostic and total ceiling",
        ],
        "C_stat": None,
        "C_ML": None,
    }
    return proposal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.check and args.write:
        raise SystemExit("--check and --write are mutually exclusive")
    proposal = build_proposal()
    if args.check:
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != proposal:
            raise SystemExit("retry-2 proposal differs from deterministic derivation")
        print("PASS: retry-2 proposal is current and explicitly authorized")
        return 0
    rendered = json.dumps(proposal, indent=2, sort_keys=True) + "\n"
    if args.write:
        temporary = OUTPUT.with_name(OUTPUT.name + f".tmp.{os.getpid()}")
        temporary.write_text(rendered, encoding="utf-8")
        os.replace(temporary, OUTPUT)
        print(OUTPUT)
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
