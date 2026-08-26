#!/usr/bin/env python3
"""Deterministically derive the authorized PET-v2 equivalence proposal receipt.

This script performs no PET work and has no submission path.  It binds current
source hashes, replays arithmetic from committed Gate-6 floor evidence, and
summarizes read-only Slurm accounting captured in this predeclaration session.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[2]
DEFAULT_RECEIPT = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-proposal-20260825.json"
)
FLOOR_RECEIPT = (
    REPO / "docs/orchestration/state/gate6-floor-replication-result-56863958.json"
)
CONTRACT_ID = "PET-V2-FIXED-DRAW-EQUIVALENCE-PREDECLARATION-20260825"
AUTHORIZATION_TOKEN = "JOSEPH-20260826-PETV2-FIXED-DRAW-EQUIVALENCE-AUTHORIZED"
AUTHORIZED_PARENT_HEAD = "1f860f0c46d8f247bd81fde6a4b5dfad823d0ac0"
EXECUTED_IMPLEMENTATION_HEAD = "ed8244d3c9038c7f00dca3ddd6545266519ffd5a"

PROHIBITIONS = (
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
)

EXPECTED_SOURCE_SHA256 = {
    "omnifold_nn/omnifold/net.py":
        "f793e53749d5754e11a7877a743ed6090b45e941c29c6162927fce74894cb953",
    "omnifold_nn/omnifold/omnifold.py":
        "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa",
    "omnifold_nn/omnifold/dataloader.py":
        "bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a",
    "nd-unfolding/pet/fullevent_fps_dataloader.py":
        "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1",
    "nd-unfolding/pet/train_fullevent_replica.py":
        "c92c9cc06033f195ac48cddc86eea95a67b3038ae12fcffcd3cc966540b4e75f",
    "nd-unfolding/pet/train_fullevent_nominal.py":
        "91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc",
    "nd-unfolding/pet/annealed_estimator.py":
        "fdf6556ccd6d0c67883dbeb5d12235ade5625d842555870c92bfa51aaf90b1c2",
    "nd-unfolding/pet/build_fullevent_replica_target.py":
        "f5a6dd4b6b78ed199cc579cb319750f8989bbf74792dad58aefd6085bb7bd0c7",
    "nd-unfolding/pet_bootstrap.py":
        "d99243f868738a0c67e31b5361397f57a5b14af6ffa000bfacda1b4c2cbee49a",
    "nd-unfolding/mnv_guarded_run.py":
        "145711eb5a247faf7bb5643a47b0f8be6e7ac2f95de0c43c12d3de1105f544c7",
}

# Direct read-only `sacct -X` observations made 2026-08-26T02:53:57Z.  These are
# the elapsed seconds for all COMPLETED top-level records returned for the two
# historical arrays.  They are resource evidence, not a new scientific sample.
TARGET_ELAPSED_SECONDS = (
    2349, 2344, 2337, 2414, 2385, 2411, 2466, 2354, 2426, 2365,
    2366, 2371, 2371, 2317, 2367, 2317, 2411, 2363, 2403, 2343,
    2358, 2602, 2311, 2307, 2470, 2325, 2370, 2407, 2343, 2403,
    2348, 2352, 2335, 2309, 2334, 2383, 2770, 2342, 2331, 2354,
    2721, 2343, 2338, 2364, 2384, 2576, 2344, 2362, 2408, 2382,
)
TRAIN_ELAPSED_SECONDS = (
    10880, 10739, 10861, 10783, 10769, 10983, 10831, 10821, 10795, 11119,
    10801, 10742, 10814, 10885, 10870, 11002, 10728, 11008, 10763, 10849,
    10979, 10983, 10829, 10934, 10826, 10824, 10840, 10827, 10798, 11281,
    10889, 10752, 10873, 10830, 10828, 10755, 10940, 10866, 10915, 10959,
    10989, 11465, 10848, 10896, 10787, 10866, 11002, 10898, 10842, 10866,
)

FUTURE_OPERANDS = (
    "nd-unfolding/pet/materialize_pet_v2_equivalence_target.py",
    "nd-unfolding/pet/train_pet_v2_equivalence.py",
    "nd-unfolding/pet/evaluate_pet_v2_equivalence.py",
    "nd-unfolding/pet/validate_pet_v2_equivalence_result.py",
    "nd-unfolding/pet/submit_pet_v2_equivalence.sh",
)
NEW_SUPPORT_SOURCES = (
    "nd-unfolding/pet/pet_v2_equivalence_common.py",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_blob_sha256(head: str, path: str) -> str:
    """Hash a frozen source blob so an executed proposal stays reproducible after HEAD moves."""
    completed = subprocess.run(
        ["git", "show", f"{head}:{path}"],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
    )
    return hashlib.sha256(completed.stdout).hexdigest()


def _hash_array(value: np.ndarray) -> str:
    """Exact contract used by the current Gate-5 target builder."""
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
    digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def _rederive_fixed_draw_factors() -> dict:
    """Replay current first-party coherent streams without importing another checkout."""
    seed = 50000
    specifications = (
        (
            "data", 4116128, seed,
            "d151dd197c9662da4604c9609d761887d38437d510484efdf851c8de1028ca37",
            4118323, 1513511, 9,
        ),
        (
            "signal", 49152885, seed + 10_000_000,
            "892d1531b7db788a9782ce2dad470b1514b13c1f1f393af9a0f84f32ea68642f",
            49143888, 18087975, 10,
        ),
        (
            "background", 564591, seed + 20_000_000,
            "9e967dc2ff1a977c4940b83171204a41deb200e5d7c6ecb819c63c15c335e84e",
            564471, 207687, 8,
        ),
    )
    result = {}
    for name, n_rows, stream_seed, expected_sha, expected_sum, expected_zeros, expected_max in specifications:
        factor = np.random.default_rng(stream_seed).poisson(1.0, n_rows).astype(np.uint8)
        measured = {
            "n": int(factor.size),
            "sha256": _hash_array(factor),
            "sum": int(factor.sum(dtype=np.int64)),
            "zeros": int(np.count_nonzero(factor == 0)),
            "maximum": int(factor.max()),
        }
        expected = {
            "n": n_rows,
            "sha256": expected_sha,
            "sum": expected_sum,
            "zeros": expected_zeros,
            "maximum": expected_max,
        }
        if measured != expected:
            raise RuntimeError(f"fixed-draw {name} replay drifted: {measured} != {expected}")
        result[name] = measured
    return result


def source_hashes() -> dict[str, str]:
    observed = {
        name: _git_blob_sha256(EXECUTED_IMPLEMENTATION_HEAD, name)
        for name in EXPECTED_SOURCE_SHA256
    }
    if observed != EXPECTED_SOURCE_SHA256:
        mismatch = {
            name: {"expected": EXPECTED_SOURCE_SHA256[name], "observed": observed[name]}
            for name in EXPECTED_SOURCE_SHA256
            if observed[name] != EXPECTED_SOURCE_SHA256[name]
        }
        raise RuntimeError(f"source hash drift: {mismatch}")
    return observed


def _percentile(values: tuple[int, ...], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def _summary(values: tuple[int, ...]) -> dict:
    return {
        "n_completed": len(values),
        "minimum_seconds": min(values),
        "p25_seconds": _percentile(values, 0.25),
        "median_seconds": _percentile(values, 0.50),
        "mean_seconds": sum(values) / len(values),
        "p75_seconds": _percentile(values, 0.75),
        "maximum_seconds": max(values),
    }


def _floor_operands() -> dict:
    floor = json.loads(FLOOR_RECEIPT.read_text(encoding="utf-8"))
    detail = floor["_LANE_B_RESULT_RECEIPT"]
    if detail["VERDICT"] != "FLOOR_INTERMEDIATE":
        raise RuntimeError("Gate-6 floor receipt is no longer FLOOR_INTERMEDIATE")
    if detail["GATE_6_IS_NOT_UNBLOCKED"]["prohibitions_still_live"] != list(PROHIBITIONS):
        raise RuntimeError("Gate-6 floor prohibitions drifted")
    sd = float(detail["LEG_X_MDE_DERIVED_FROM_THIS_FLOOR"]["F_sd_ddof1"])
    same_arm_cap = math.ceil(sd * 10_000.0) / 10_000.0
    materiality_margin = round(2.0 * same_arm_cap, 4)
    return {
        "F_sd_ddof1": sd,
        "F_range": float(floor["F_range"]),
        "existing_single_effect_MDE": float(
            detail["LEG_X_MDE_DERIVED_FROM_THIS_FLOOR"]["MDE"]
        ),
        "same_arm_validity_cap_S": same_arm_cap,
        "cross_arm_materiality_margin_M": materiality_margin,
    }


def build_proposal() -> dict:
    sources = source_hashes()
    fixed_factors = _rederive_fixed_draw_factors()
    floor = _floor_operands()
    train_summary = _summary(TRAIN_ELAPSED_SECONDS)
    target_summary = _summary(TARGET_ELAPSED_SECONDS)

    maximum_train_hours = train_summary["maximum_seconds"] / 3600.0
    per_arm_with_overhead = maximum_train_hours * 1.25
    inference_hours_total = 3.0 * 14.0 / 60.0
    expected_a100_hours_unrounded = 3.0 * per_arm_with_overhead + inference_hours_total
    expected_a100_hours = float(math.ceil(expected_a100_hours_unrounded))

    future_operands = [
        {
            "path": path,
            "sha256": _git_blob_sha256(EXECUTED_IMPLEMENTATION_HEAD, path),
            "status": "IMPLEMENTED_TESTED_HASH_BOUND",
        }
        for path in FUTURE_OPERANDS
    ]
    support_sources = {
        path: _git_blob_sha256(EXECUTED_IMPLEMENTATION_HEAD, path)
        for path in NEW_SUPPORT_SOURCES
    }

    return {
        "schema": "pet-v2-fixed-draw-equivalence-proposal-v1",
        "contract_id": CONTRACT_ID,
        "status": "AUTHORIZED_READY",
        "launchable": True,
        "compute_decision": "AUTHORIZED_CONDITIONAL_SUBMISSION_AFTER_ALL_PREFLIGHTS",
        "scope": "PET_DIAGNOSTIC_AND_METHOD_DEVELOPMENT_ONLY",
        "authorization": {
            "authorized_by": "Joseph",
            "authorized_at_utc_date": "2026-08-26",
            "authorized_action": (
                "CPU target/readback work and the three A100 equivalence arms, only while all "
                "predeclared provenance, determinism, hardware, no-clobber, and dependency guards pass"
            ),
            "token": AUTHORIZATION_TOKEN,
            "authorized_parent_head": AUTHORIZED_PARENT_HEAD,
            "runtime_head_binding": (
                "controller requires one exact clean non-primary checkout HEAD and independently "
                "hash-checks this proposal plus all five executable operands at that HEAD"
            ),
            "automatic_or_unchanged_retry": False,
        },
        "authoritative_state_observation": {
            "observed_at_utc": "2026-08-26T06:44:00Z",
            "freshness_check": (
                "STALE :: Git: 06efa653, HEAD 1f860f0c, HEAD^ 10ad530d; "
                "no stale generated field used"
            ),
            "direct_alloc_run_status": "NO_ALLOCATION",
            "direct_squeue_pet_jobs": 0,
            "other_scheduler_record": "57575105 RUNNING cron on login33; unrelated",
            "gpu_inventory_note": "both hbm40g and hbm80g A100 nodes observed; future arm pins hbm80g",
        },
        "governing_gate6": {
            "family_verdict": "BLOCK_GATE6_ML_ENSEMBLE",
            "prohibitions_applied": {key: True for key in PROHIBITIONS},
            "existing_results_remain_blocked": True,
        },
        "fixed_draw": {
            "bootstrap_seed": 50000,
            "selection_rule": "first seed in predeclared Gate-5 50000..50049 range, selected by index not outcome",
            "source_G2_sha256": "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625",
            "source_G2_size_bytes": 9897374636,
            "existing_weighted_target_sha256": "13d46574b8f8e904aee0d544b33ce0f4fcd3fd5a119b0a2fd64071c70c650c03",
            "factor_contract": "sha256(dtype || JSON(shape) || contiguous raw bytes)",
            "factors": fixed_factors,
        },
        "frozen_training_policy": {
            "arms": {
                "W_A": "weighted multiplicities; retained zero-weight rows; independent process",
                "W_B": "exact duplicate of W_A policy in a second independent process",
                "L": "same draw literalized as delete k=0 and k copies for k>0",
            },
            "estimator_seed": 42,
            "subsample_seed": 0,
            "train_events_unique_before_literalization": 2000000,
            "niter": 3,
            "epochs_reco": 8,
            "epochs_truth": 8,
            "batch_size_rows": 512,
            "train_fraction": 0.8,
            "early_stopping_patience": 10,
            "early_stopping_can_fire_with_eight_epochs": False,
            "learning_rate": {
                "iteration_0": 0.0001,
                "iterations_1_and_2": 0.00001,
            },
            "optimizer": "new Adam state at every fit; model weights warm-start across iterations",
            "split": (
                "hash-bound unique-event train/validation membership assigned before any duplication; "
                "all copies inherit membership"
            ),
            "class_ratio": "one exact fixed-draw R computed before representation and required bit-identical in all arms",
            "required_class_ratio_R": 1.1253110723074478,
            "intervention_consequences_not_equalized": (
                "materialized row count, batches and optimizer updates per epoch, validation reductions, "
                "and gradient order"
            ),
        },
        "determinism_and_same_arm_controls": {
            "required_environment_before_interpreter_start": {
                "PYTHONHASHSEED": "42",
                "TF_DETERMINISTIC_OPS": "1",
                "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
            },
            "required_in_process_before_model_creation": [
                "tf.config.experimental.enable_op_determinism()",
                "tf.keras.utils.set_random_seed(42)",
                "tf.data deterministic options on every constructed dataset",
            ],
            "fallback": "NONE; unsupported deterministic operation or setup is INVALID_OR_INCOMPLETE",
            "hardware": "one NVIDIA A100-SXM4-80GB per arm; exact model and 80-GB class must match",
            "software": "same immutable checkout HEAD, conda lock, TensorFlow/CUDA/cuDNN versions and driver class",
            "same_arm": "W_A and W_B are fresh independent processes with identical inputs, policy, seeds and hashes",
            "why_same_arm_remains_required": (
                "deterministic mode is a PET-v2 policy control, not evidence that every operation or the "
                "historical estimator was deterministic"
            ),
        },
        "measured_quantities": {
            "distance_scalar": (
                "symrel(a,b)=2*abs(a-b)/(abs(a)+abs(b)); zero/zero is 0 and a one-sided zero is 2"
            ),
            "event_push_distance": (
                "D_push(A,B)=sum_i a_i*abs(p_i^A-p_i^B) / "
                "sum_i a_i*(abs(p_i^A)+abs(p_i^B))/2 over the same unique signal IDs; "
                "a_i is the nonnegative raw truth analysis weight times the fixed signal multiplicity "
                "and reporting mask, applied exactly once"
            ),
            "extracted_projection_distances": [
                "global reporting-mask total",
                "p_parallel < 6 GeV",
                "6 GeV <= p_parallel <= 20 GeV",
                "p_parallel > 20 GeV",
            ],
            "per_metric_controls": {
                "D_same": "D(W_A,W_B)",
                "D_cross_max": "max(D(W_A,L),D(W_B,L))",
                "D_cross_min": "min(D(W_A,L),D(W_B,L))",
            },
            "mandatory_diagnostics": [
                "target sums, zeros and class-ratio operands",
                "full train and validation loss histories for every reco/truth fit",
                "best/final epoch and best/final prediction discrepancy",
                "realized LR, update counts and early-stopping state",
                "iteration push vectors mapped to unique IDs",
                "response/calibration summaries in the predeclared projections",
                "truth/reco ESS, weight quantiles, maximum and cap occupancy",
            ],
        },
        "threshold_derivation": {
            "source": "docs/orchestration/state/gate6-floor-replication-result-56863958.json",
            **floor,
            "same_arm_formula": "S=ceil(F_sd_ddof1*10000)/10000",
            "materiality_formula": "M=2*S",
            "scope_limit": (
                "F_sd is an old no-draw global-scalar process measurement, not a regional push or "
                "projection noise calibration; S and M are operational resolution targets whose "
                "transfer must be validated by W_A versus W_B"
            ),
            "existing_MDE_is_annotation_not_gate": True,
        },
        "terminal_classification": {
            "order": [
                "INVALID_OR_NOISY",
                "EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION",
                "MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW",
                "MIXED_OR_UNRESOLVED",
            ],
            "INVALID_OR_NOISY": (
                "any provenance/determinism/split/identity/finite-output guard fails, or any primary "
                "D_same exceeds S=0.0251"
            ),
            "EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION": (
                "all controls valid, every primary D_same <= 0.0251, and every primary "
                "D_cross_max <= M=0.0502"
            ),
            "MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW": (
                "all controls valid and at least one primary metric has D_cross_min > 0.0502 and "
                "D_cross_min > 2*D_same, so L differs from both independent W executions"
            ),
            "MIXED_OR_UNRESOLVED": "every other valid result; no favorable default",
        },
        "resource_evidence": {
            "observed_at_utc": "2026-08-26T02:53:57Z",
            "target_array": {
                "job_id": 56857232,
                "query": "sacct -j 56857232 -X -n -P -o JobIDRaw,State,ElapsedRaw,AllocTRES%100",
                "allocation_each": "36 CPU, 64G, 1 node",
                "elapsed_seconds": list(TARGET_ELAPSED_SECONDS),
                "summary": target_summary,
            },
            "training_array": {
                "job_id": 56857233,
                "query": "sacct -j 56857233 -X -n -P -o JobIDRaw,State,ElapsedRaw,AllocTRES%100",
                "allocation_each": "1 A100, 32 CPU, 57472M, 1 node",
                "elapsed_seconds": list(TRAIN_ELAPSED_SECONDS),
                "summary": train_summary,
            },
            "derivation": {
                "maximum_historical_training_hours": maximum_train_hours,
                "determinism_and_literal_overhead_factor": 1.25,
                "per_arm_training_hours_with_overhead": per_arm_with_overhead,
                "three_arm_training_hours": 3.0 * per_arm_with_overhead,
                "inference_and_extraction_minutes_per_arm": 14,
                "three_arm_inference_hours": inference_hours_total,
                "expected_a100_hours_unrounded": expected_a100_hours_unrounded,
                "expected_a100_hours_rounded_up": expected_a100_hours,
            },
        },
        "authorized_resource_ceiling": {
            "paired_targets": (
                "1 CPU node, 36 CPU, 64G, 2h wall; rebuild weighted then literal target; the "
                "weighted output must reproduce sha256 13d46574... before dependencies release"
            ),
            "training_per_arm": "1 A100-SXM4-80GB, 32 CPU, 57472M, 6h wall",
            "training_arms": 3,
            "evaluation": "1 CPU node, 16 CPU, 64G, 2h wall after all three arms",
            "read_only_validation": "1 CPU node, 4 CPU, 8G, 0.5h wall after evaluation",
            "expected_total_a100_hours_rounded": expected_a100_hours,
            "a100_hours": 18,
            "cpu_node_hours": 5,
            "queue_excluded_critical_path_hours_if_arms_parallel": 10.5,
            "coverage_or_family_compute_authorized": False,
            "retry_authorized": False,
        },
        "guarded_execution_contract": {
            "immutable_root": (
                "PETV2_CODE_ROOT is mandatory, has no default, is a clean immutable checkout at the "
                "approved implementation commit, and may not be the primary checkout"
            ),
            "python_supplier": (
                "PETV2_PYTHON is mandatory, has no default, and is bound by resolved path, version "
                "and environment lock before preflight"
            ),
            "artifact_supplier": (
                "source G2, Gate-3 manifest, and the 12 per-playlist flux ROOTs are mandatory explicit "
                "paths outside the primary checkout; all are content- or manifest-verified and have no default"
            ),
            "guard_prefix": (
                "${PETV2_PYTHON} ${PETV2_CODE_ROOT}/nd-unfolding/mnv_guarded_run.py --expect-root "
                "${PETV2_CODE_ROOT} --"
            ),
            "subprocess_rule": (
                "each Python process that imports science modules is itself wrapped; a guarded parent "
                "does not cover a child interpreter"
            ),
            "required_current_sources": sources,
            "future_required_operands": future_operands,
            "new_support_sources": support_sources,
            "output_guards": [
                "new isolated output namespace per arm; refuse pre-existing nonempty target",
                "no shared checkpoint/history paths across arms",
                ("published arrays/receipts are atomic; completion markers bind size/mtime; the "
                 "receipt published last binds payload sha256 and terminal status"),
                "record HEAD, dirty-state refusal, source/input/target/factor/split hashes and GPU identity",
                "validator is read-only and cannot alter training artifacts",
            ],
            "authorization_guard": (
                "submission controller requires the literal Joseph authorization token, exact proposal "
                "digest, exact clean non-primary runtime HEAD, all five operand hashes, and the resource "
                "ceiling; any mismatch exits before sbatch"
            ),
            "conditional_launch_boundary": (
                "launchable means the controller may submit only after its complete preflight passes; "
                "it is not permission to bypass a failed source, interpreter, hardware, hash, no-clobber, "
                "dependency, determinism, or primary-checkout guard"
            ),
        },
        "what_every_terminal_result_cannot_authorize": [
            *PROHIBITIONS,
            "cannot establish interval coverage or a valid PET uncertainty",
            "cannot establish ordinary closure beyond the measured fixed-draw projections",
            "cannot generalize equivalence beyond seed 50000 and this frozen PET-v2 policy",
            "cannot construct or adopt C_stat, C_ML, a total covariance or a central value",
            "cannot change a note, publication claim or PET diagnostic scope",
            "cannot authorize a coverage campaign, a larger family, convergence tuning or further compute",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with the committed receipt")
    parser.add_argument("--write", action="store_true",
                        help="replace the deterministic proposal receipt atomically")
    args = parser.parse_args()
    if args.check and args.write:
        raise SystemExit("--check and --write are mutually exclusive")
    proposal = build_proposal()
    if args.check:
        committed = json.loads(DEFAULT_RECEIPT.read_text(encoding="utf-8"))
        if committed != proposal:
            raise SystemExit("committed proposal receipt differs from deterministic derivation")
        print("PASS: committed PET-v2 equivalence proposal receipt is current")
        return 0
    if args.write:
        rendered = json.dumps(proposal, indent=2, sort_keys=True) + "\n"
        temporary = DEFAULT_RECEIPT.with_suffix(DEFAULT_RECEIPT.suffix + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(DEFAULT_RECEIPT)
        print(f"WROTE: {DEFAULT_RECEIPT}")
        return 0
    print(json.dumps(proposal, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
