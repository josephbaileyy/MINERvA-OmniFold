#!/usr/bin/env python3
"""Derive the authorized PET-v2 changed-retry-3 proposal deterministically."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PRIOR_PROPOSAL = REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry2-proposal-20260826.json"
PRIOR_SUBMISSION = REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry2-submission-57629029.json"
PRIOR_ATTEMPT = REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry2-attempt-57629029.json"
OUTPUT = REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry3-proposal-20260826.json"
EXPECTED_PRIOR_PROPOSAL_SHA256 = "ffa29bd36d5b2e9adcb6ca0d82d246cebc6e57950dcbb15e2840de9601757933"
EXPECTED_PRIOR_SUBMISSION_SHA256 = "889264a5fc85b6746037dedcc5bdcb683f7120bdcd5fd24e83bc7a81943b11da"
EXPECTED_PRIOR_ATTEMPT_SHA256 = "3e4bf9a44b51f55d21c76786470748b9b67a4aeb4f0d4d8e713eb0961e2e0e7e"
AUTHORIZATION_TOKEN = "JOSEPH-20260826-PETV2-CHANGED-RETRIES-UNTIL-COMPLETE"
PROHIBITIONS = (
    "do_not_select_passing_subset", "do_not_construct_C_ML", "do_not_move_central",
    "do_not_start_leg_2", "do_not_retry_unchanged",
)
RETRY3_EXECUTABLES = (
    "nd-unfolding/pet/materialize_pet_v2_equivalence_target_retry3.py",
    "nd-unfolding/pet/train_pet_v2_equivalence_retry1.py",
    "nd-unfolding/pet/evaluate_pet_v2_equivalence_retry1.py",
    "nd-unfolding/pet/validate_pet_v2_equivalence_result_retry3.py",
    "nd-unfolding/pet/submit_pet_v2_equivalence_changed_retry3.sh",
)
RETRY3_SUPPORT = (
    "nd-unfolding/pet/pet_v2_equivalence_common.py",
    "nd-unfolding/pet/pet_v2_equivalence_root_remap.py",
    "nd-unfolding/pet/pet_v2_target_package_bypass_retry2.py",
    "docs/orchestration/state/pet-v2-fixed-draw-equivalence-changed-retry2-attempt-57629029.json",
)


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_bound(path, expected):
    observed = _sha256(path)
    if observed != expected:
        raise RuntimeError(f"bound input drift: {path}: {observed} != {expected}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_proposal():
    prior = _load_bound(PRIOR_PROPOSAL, EXPECTED_PRIOR_PROPOSAL_SHA256)
    submission = _load_bound(PRIOR_SUBMISSION, EXPECTED_PRIOR_SUBMISSION_SHA256)
    attempt = _load_bound(PRIOR_ATTEMPT, EXPECTED_PRIOR_ATTEMPT_SHA256)
    if submission["jobs"]["target"] != "57629029":
        raise RuntimeError("retry-2 submission identity drift")
    if attempt["status"] != "INVALID_OR_INCOMPLETE_WEIGHTED_TARGET_REPRODUCIBILITY":
        raise RuntimeError("retry-2 failure classification drift")
    if attempt["resource_consumption"]["a100_hours"] != 0.0:
        raise RuntimeError("retry-2 unexpectedly consumed A100 time")
    if attempt["prohibitions_applied"] != list(PROHIBITIONS):
        raise RuntimeError("retry-2 prohibitions drift")

    controls = copy.deepcopy(prior["controls"])
    controls["only_changed_axis"] = (
        "consume the exact hash-bound historical Gate-5 seed-50000 weighted target and fit only "
        "the literal delete/duplicate representation; every training, metric, threshold, draw, "
        "split, feature, mask, schedule, and stopping control remains frozen"
    )
    required = {
        path: _sha256(REPO / path)
        for path in prior["guarded_executable_operands"]["required_current_sources"]
    }
    support = {path: _sha256(REPO / path) for path in RETRY3_SUPPORT}
    executables = [
        {"path": path, "sha256": _sha256(REPO / path),
         "status": "IMPLEMENTED_TESTED_HASH_BOUND"}
        for path in RETRY3_EXECUTABLES
    ]
    consumed_cpu = float(attempt["resource_consumption"]["cumulative_attempt_cpu_node_hours"])
    proposal = {
        "schema": "pet-v2-fixed-draw-equivalence-changed-retry3-proposal-v1",
        "contract_id": "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY3-20260826",
        "status": "AUTHORIZED_READY_CHANGED_RETRY",
        "launchable": True,
        "compute_decision": "AUTHORIZED_CHANGED_RETRIES_WITHIN_FROZEN_SCOPE_AND_TOTAL_CEILING",
        "scope": prior["scope"],
        "authorization": {
            "authorized_by": "Joseph",
            "authorization_source": (
                "Joseph's exact messages 'Retries are authorized' and 'okay if they fail again "
                "(maybe set a waker), keep fixing them until they work'"
            ),
            "authorization_token": AUTHORIZATION_TOKEN,
            "changed_retries_authorized": True,
            "unchanged_retry_authorized": False,
            "authorized_action": (
                "evidence-backed changed machinery retries for this one frozen fixed-draw "
                "diagnostic until it completes, within the existing total resource ceiling"
            ),
        },
        "failed_attempts": {
            "initial_guard_job": "57620796",
            "retry1_target_job": "57626676",
            "retry2_target_job": "57629029",
            "retry2_attempt_receipt": str(PRIOR_ATTEMPT.relative_to(REPO)),
            "retry2_attempt_receipt_sha256": EXPECTED_PRIOR_ATTEMPT_SHA256,
            "scientific_quantity_measured": False,
            "a100_hours": 0.0,
        },
        "changed_operand": {
            "measured_failure": (
                "retry 2 passed the import and checkout-root controls, then a fresh weighted "
                "GradientBoostingClassifier target rebuild differed from the frozen target digest"
            ),
            "measured_difference": attempt["diagnosis"],
            "settled_cause": False,
            "only_change": (
                "read and byte-copy the existing target only after its file hash, size, owning "
                "receipt hash, seed, input hash, signed-inventory hash, shape, dtype, finiteness, "
                "and non-negativity pass; skip its fresh refit and run the unchanged canonical "
                "literal refit once"
            ),
            "why_not_gate_relaxation": (
                "the output weighted target must still equal the original digest exactly; retry 3 "
                "removes the non-bit-reproducible reconstruction, not the digest requirement"
            ),
            "scientific_policy_change": False,
            "sampling_or_training_change": False,
        },
        "archived_weighted_operand": {
            "bootstrap_seed": 50000,
            "path": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas/replica_00/target/GATE5_REPLICA_TARGET.npy",
            "sha256": "13d46574b8f8e904aee0d544b33ce0f4fcd3fd5a119b0a2fd64071c70c650c03",
            "size_bytes": 18723004,
            "receipt_path": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas/replica_00/target/GATE5_REPLICA_TARGET_RECEIPT.json",
            "receipt_sha256": "ff081d44aad16971a2b812b493c78cbeef25254f497ec5533dec4698c7246fc4",
            "signed_target_hash": "446a392e898b8b1816151a6d8f3b90d2144bce75af6540ec8d984ebba751b44a",
            "read_only": True,
        },
        "measured_quantity": prior["measured_quantity"],
        "controls": controls,
        "guarded_executable_operands": {
            "required_current_sources": required,
            "future_required_operands": executables,
            "new_support_sources": support,
            "runtime_head": "one exact clean non-primary detached checkout at the pushed head",
            "new_output_namespace": "mandatory and absent; all earlier attempt directories remain immutable",
            "guard": prior["guarded_executable_operands"]["guard"],
            "no_srun": True,
            "no_automatic_or_unchanged_retry": True,
        },
        "resource_estimate": {
            "method": {
                **prior["resource_estimate"]["method"],
                "retry3_cpu_target_expected_node_hours": 0.75,
                "retry3_cpu_target_basis": (
                    "historical one-fit target job 56857246 used 0.6525 node-hours; retry 3 "
                    "performs one literal fit and hash/copy/flux work, rounded upward"
                ),
            },
            "authorized_total_envelope": prior["resource_estimate"]["authorized_total_envelope"],
            "consumed_by_failed_attempts": {"cpu_node_hours": consumed_cpu, "a100_hours": 0.0},
            "remaining_total_envelope": {"cpu_node_hours": 5.0 - consumed_cpu, "a100_hours": 18.0},
            "projected_after_retry3_target": {"cpu_node_hours_remaining": 5.0 - consumed_cpu - 0.75},
            "numeric_envelope_is_not_authorization_outside_this_scope": True,
        },
        "entry_tests_required_before_submission": [
            "retry-2 terminal evidence and zero-A100 accounting are hash-bound",
            "archived target and owning receipt pass exact hashes and semantic seed/input/signed-inventory controls",
            "guarded retry-3 target --help passes in the exact ROOT environment with one checkout root",
            "a synthetic two-call control proves archived weighted return first and unchanged canonical literal call second",
            "training/evaluation remain the unchanged retry-1 operands",
            "proposal/source hashes, five prohibitions, clean detached checkout, absent output, scheduler, and A100-80GB constraints pass",
        ],
        "prohibitions_applied": {key: True for key in PROHIBITIONS},
        "existing_gate6_results_remain_blocked": True,
        "success_interpretation": prior["success_interpretation"],
        "failure_interpretation": (
            "INVALID_OR_INCOMPLETE supports only preservation, diagnosis, and a distinct changed "
            "machinery retry within this frozen scope and remaining total ceiling"
        ),
        "what_every_terminal_result_cannot_authorize": prior["what_every_terminal_result_cannot_authorize"],
        "C_stat": None,
        "C_ML": None,
    }
    return proposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.check and args.write:
        raise SystemExit("--check and --write are mutually exclusive")
    proposal = build_proposal()
    rendered = json.dumps(proposal, indent=2, sort_keys=True) + "\n"
    if args.check:
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != proposal:
            raise SystemExit("retry-3 proposal differs from deterministic derivation")
        print("PASS: retry-3 proposal current and explicitly authorized")
    elif args.write:
        temporary = OUTPUT.with_name(OUTPUT.name + f".tmp.{os.getpid()}")
        temporary.write_text(rendered, encoding="utf-8")
        os.replace(temporary, OUTPUT)
        print(OUTPUT)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
