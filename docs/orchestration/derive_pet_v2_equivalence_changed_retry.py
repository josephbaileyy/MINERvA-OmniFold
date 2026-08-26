#!/usr/bin/env python3
"""Derive the non-launchable PET-v2 changed-retry proposal after job 57620796.

This script reads committed first-party receipts and current candidate sources.  It performs no
PET work and has no scheduler/submission path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PRIOR_PROPOSAL = (
    REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-proposal-20260825.json"
)
ATTEMPT = (
    REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-attempt-57620796.json"
)
OUTPUT = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry-proposal-20260826.json"
)
EXPECTED_PRIOR_PROPOSAL_SHA256 = (
    "314ef43d627066b19f1e8992d33ac4d0a6d7d4a1123adfb19ef463a29437bd9c"
)
EXPECTED_ATTEMPT_SHA256 = (
    "6574dbf6fd5ed15b11fe7d3f6ca7994e873c9aa988405f50d2d2904e4085369c"
)
OLD_LOADER_SHA256 = "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
RETRY_EXECUTABLES = (
    "nd-unfolding/pet/materialize_pet_v2_equivalence_target_retry1.py",
    "nd-unfolding/pet/train_pet_v2_equivalence_retry1.py",
    "nd-unfolding/pet/evaluate_pet_v2_equivalence_retry1.py",
    "nd-unfolding/pet/validate_pet_v2_equivalence_result_retry1.py",
    "nd-unfolding/pet/submit_pet_v2_equivalence_changed_retry.sh",
)
RETRY_SUPPORT = (
    "nd-unfolding/pet/pet_v2_equivalence_root_remap.py",
)
PROHIBITIONS = (
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
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
        raise RuntimeError(f"bound receipt drift: {path}: {observed} != {expected_sha256}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_proposal() -> dict:
    prior = _load_bound(PRIOR_PROPOSAL, EXPECTED_PRIOR_PROPOSAL_SHA256)
    attempt = _load_bound(ATTEMPT, EXPECTED_ATTEMPT_SHA256)
    if attempt["status"] != "INVALID_OR_INCOMPLETE_GUARD_REFUSAL":
        raise RuntimeError("attempt is not the pre-materialization guard refusal")
    if attempt["prohibitions_applied"] != list(PROHIBITIONS):
        raise RuntimeError("attempt prohibitions drifted")
    if attempt["resource_consumption"]["a100_hours"] != 0.0:
        raise RuntimeError("attempt unexpectedly consumed A100 time")

    prior_contract = prior["guarded_execution_contract"]
    required_sources = {
        path: _sha256(REPO / path)
        for path in prior_contract["required_current_sources"]
    }
    if required_sources["nd-unfolding/pet/fullevent_fps_dataloader.py"] != OLD_LOADER_SHA256:
        raise RuntimeError("receipt-bound loader was altered instead of preserved")
    for item in prior_contract["future_required_operands"]:
        required_sources[item["path"]] = _sha256(REPO / item["path"])
    future_operands = [
        {
            "path": path,
            "sha256": _sha256(REPO / path),
            "status": "IMPLEMENTED_TESTED_HASH_BOUND",
        }
        for path in RETRY_EXECUTABLES
    ]
    support_sources = {
        path: _sha256(REPO / path)
        for path in prior_contract["new_support_sources"]
    }
    support_sources.update({path: _sha256(REPO / path) for path in RETRY_SUPPORT})

    consumed_cpu = float(attempt["resource_consumption"]["cpu_node_hours"])
    cpu_ceiling = float(prior["authorized_resource_ceiling"]["cpu_node_hours"])
    a100_ceiling = float(prior["authorized_resource_ceiling"]["a100_hours"])
    proposal = {
        "schema": "pet-v2-fixed-draw-equivalence-changed-retry-proposal-v1",
        "contract_id": "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY1-20260826",
        "status": "BLOCKED_AWAITING_JOSEPH_CHANGED_RETRY_AUTHORIZATION",
        "launchable": False,
        "compute_decision": "DO_NOT_SUBMIT_CHANGED_RETRY_WITHOUT_NEW_EXPLICIT_AUTHORIZATION",
        "scope": prior["scope"],
        "prior_authorization_is_exhausted": True,
        "authorization": {
            "authorized_by": None,
            "authorization_token": None,
            "retry_authorized": False,
            "decision_required": (
                "Joseph must explicitly authorize this named changed retry after reviewing the "
                "guard refusal, code change, tests, frozen operands, and remaining resource request"
            ),
        },
        "failed_attempt": {
            "receipt": str(ATTEMPT.relative_to(REPO)),
            "receipt_sha256": EXPECTED_ATTEMPT_SHA256,
            "target_job": attempt["submission"]["jobs"]["target"],
            "classification": attempt["terminal_interpretation"]["classification"],
            "scientific_quantity_measured": False,
            "a100_hours": 0.0,
        },
        "changed_operand": {
            "measured_source": "nd-unfolding/pet/fullevent_fps_dataloader.py",
            "measured_source_sha256_preserved": OLD_LOADER_SHA256,
            "measured_failure": (
                "the executed loader inserted the primary-checkout nd-unfolding directory at "
                "sys.path position 0, so its lazy pet_bootstrap import resolved outside the "
                "immutable execution root and the OI-136 guard refused before materialization"
            ),
            "repair": (
                "preserve the receipt-bound loader bytes and run the frozen target/training/evaluation "
                "operands through retry-specific wrappers whose narrow sys.path adapter maps only the "
                "known primary-checkout root to the same relative path under PETV2_CODE_ROOT; the "
                "ordinary OI-136 guard remains installed and refuses every other checkout escape"
            ),
            "new_executable_paths": list(RETRY_EXECUTABLES),
            "new_support_paths": list(RETRY_SUPPORT),
            "scientific_policy_change": False,
            "sampling_or_training_change": False,
        },
        "measured_quantity": prior["measured_quantities"],
        "controls": {
            "fixed_draw": prior["fixed_draw"],
            "frozen_training_policy": prior["frozen_training_policy"],
            "determinism_and_same_arm_controls": prior[
                "determinism_and_same_arm_controls"
            ],
            "threshold_derivation": prior["threshold_derivation"],
            "terminal_classification": prior["terminal_classification"],
            "only_changed_axis": "process-local checkout-root remap before frozen PET operands execute",
        },
        "guarded_executable_operands": {
            "required_current_sources": required_sources,
            "future_required_operands": future_operands,
            "new_support_sources": support_sources,
            "runtime_head": (
                "one exact clean non-primary detached checkout containing these hashes; supplied "
                "without a default and recorded in any later submission receipt"
            ),
            "new_output_namespace": (
                "mandatory and absent before any later submission; the failed attempt directory "
                "is evidence and must not be reused or altered"
            ),
            "guard": prior_contract["guard_prefix"],
            "no_srun": True,
            "no_automatic_or_unchanged_retry": True,
        },
        "resource_estimate": {
            "method": prior["resource_evidence"]["derivation"],
            "changed_retry_request_if_authorized": {
                "expected_a100_hours_rounded": prior["authorized_resource_ceiling"][
                    "expected_total_a100_hours_rounded"
                ],
                "a100_hour_ceiling": a100_ceiling,
                "cpu_node_hour_ceiling": cpu_ceiling,
                "hardware": "three parallel single-GPU A100-SXM4-80GB arms after one CPU target",
            },
            "already_consumed": {
                "cpu_node_hours": consumed_cpu,
                "a100_hours": 0.0,
            },
            "remaining_original_numeric_envelope": {
                "cpu_node_hours": cpu_ceiling - consumed_cpu,
                "a100_hours": a100_ceiling,
            },
            "numeric_envelope_is_not_authorization": True,
        },
        "entry_tests_required_before_any_later_submission": [
            "guarded retry wrapper remaps the known primary-root insert and lazy pet_bootstrap resolves inside the candidate checkout",
            "the receipt-bound loader and both production bindings remain byte-intact",
            "all original PET-v2 operand/predeclaration tests pass",
            "exact ROOT worker shell contract passes",
            "clean detached checkout, proposal/source hashes, external input hashes, flux suppliers, "
            "hardware constraint, prohibitions, new output namespace, and scheduler are rechecked",
        ],
        "prohibitions_applied": {key: True for key in PROHIBITIONS},
        "existing_gate6_results_remain_blocked": True,
        "success_interpretation": (
            "classify only the predeclared fixed-draw push and extracted-projection contrasts after "
            "same-arm validity; it is one estimator-equivalence diagnostic at operational resolution"
        ),
        "failure_interpretation": (
            "INVALID_OR_INCOMPLETE supports only diagnosis/redesign; no automatic, unchanged, or "
            "unapproved changed retry"
        ),
        "what_every_terminal_result_cannot_authorize": list(dict.fromkeys(
            prior["what_every_terminal_result_cannot_authorize"]
            + [
                "cannot erase or reinterpret the failed 57620796 guard receipt",
                "cannot spend the remaining numeric resource envelope without Joseph's new decision",
            ]
        )),
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
            raise SystemExit("changed-retry proposal differs from deterministic derivation")
        print("PASS: changed-retry proposal is current and non-launchable")
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
