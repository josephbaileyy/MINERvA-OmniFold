#!/usr/bin/env python3
"""Gate 6 Leg F -- apply the PREDECLARED across-process floor rule to the `(42,0)` draws.

This script is the executable form of
`docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md`. It exists because that
rule was fixed before any draw existed, and the only way a fixed rule stays fixed is if the code
that applies it is written from the document rather than from the data.

**THE THRESHOLDS BELOW ARE FROZEN.** `0.05`, `0.10` and `0.1740029887300910` were declared before
draw 2 finished. They are not re-derived here and must not be adjusted now that draws exist -- that
is the whole value of a predeclaration. `_verify_frozen_threshold_against_member_receipts` checks
the frozen process-determined threshold against the committed member trajectories and FAILS CLOSED
on a mismatch; that is a transcription check, not a recomputation, and it can only reject.

**VALIDITY IS SEPARATE FROM THE VERDICT**, and every one of the eight clauses is mandatory. Any
invalid draw means this leg reports `n < 5` and reaches NO VERDICT. It does not proceed on the
survivors: selecting a survivor set is the shape `do_not_select_passing_subset` forbids.

**GATE 6 IS NOT UNBLOCKED BY ANY OUTPUT OF THIS SCRIPT.** All five prohibitions at `19585b7`
remain live. This script never writes `C_ML`, never moves a central value, never re-verdicts a
Gate-6 member, and never selects a subset. It emits one JSON receipt and an exit code.

Exit codes, so a caller cannot mistake "not yet" for "nothing to see":
  0  a verdict was reached (all five draws present and valid)
  3  INCOMPLETE -- fewer than five draws present; statistics reported as provisional, no verdict
  4  INVALID -- a draw is present but fails a validity clause; no verdict, and this is a defect
  5  a FROZEN premise failed (threshold transcription, or the checkpoint-tier homogeneity the
     predeclaration's like-for-like claim rests on). Escalate; do not paper over.

Usage on the cluster (numpy comes from `module load tensorflow/2.15.0`):

  python3 gate6_floor_statistics.py \
      --floor-dir  nd-unfolding/pet/fullevent_floor_42_0 \
      --member1-dir nd-unfolding/pet/fullevent_ml_ensemble/member_1 \
      --member-trajectory-glob 'nd-unfolding/pet/fullevent_ml_ensemble/member_*/trajectory/STEP1_TRAJECTORY.slurm-*.json' \
      --json docs/orchestration/state/gate6-floor-replication-result-56863958.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------------------------------
# FROZEN CONSTANTS. Every one is quoted from the predeclaration. Do not edit to fit a draw.
# --------------------------------------------------------------------------------------------------

#: Branch 1 needs the range at or under the Gate-4 nominal fold-forward deviation bar. Pre-existing
#: scale in this problem; not invented for this test.
THRESH_SEED_RANGE = 0.05

#: Branch 1 also needs every draw inside the Gate-6 band. `0.10` is the iteration-0 verdict-label
#: cut at `step1_increment_trajectory.py:299` (BEN-121 records that its provenance is a label cut,
#: which is a known weakness of the band and is NOT a licence to move it here).
BAND = 0.10

#: Branch 2 needs the range at or above half the committed five-member spread at iteration 2.
THRESH_PROCESS_RANGE = 0.1740029887300910

#: The operands the frozen threshold was computed from, so the number can be contradicted.
S_RANGE_2_MAX = 1.1014828481277632
S_RANGE_2_MIN = 0.7534768706675813

#: Draw 1 is the EXISTING member_1 artifact, reused and not retrained. Its committed value.
V_DRAW1_ITER2 = 0.9806897311812962

#: `R` is subsample-invariant and shared, so it is identical across draws by construction.
R_REQUIRED = 1.1240802949941018

#: The one policy every draw runs. Read off member 1's own artifact when the predeclaration was
#: written, not from a constant -- and then frozen here so a drift is a failure, not a surprise.
POLICY_REQUIRED = {
    "estimator_seed": 42,
    "subsample_seed": 0,
    "niter": 3,
    "epochs": 8,
    "train_events": 2000000,
    "batch_size": 512,
}

TARGET_SHA = "544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"

#: Eight `*.weights.h5` files: step1 and step2 at iterations 0, 1, 2, plus the two BEN-043 `_final`
#: weights at iteration 2. Counting every file in the directory gives 14 (the `.pkl` histories); the
#: clause is about checkpoints, so it counts `*.weights.h5`.
N_CHECKPOINTS_REQUIRED = 8

#: The like-for-like premise: iterations 0 and 1 read best-epoch, iteration 2 reads `_final`. If a
#: draw departs from this, `F_range` is no longer a clean across-process comparison and the
#: predeclaration's own statement about it is void.
TIER_PATTERN = ("best-epoch", "best-epoch", "final(BEN-043)")

ITERATIONS = (0, 1, 2)
DRAWS_REQUIRED = (1, 2, 3, 4, 5)
VERDICT_ITERATION = 2

PROHIBITIONS = [
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
]


class PremiseFailure(Exception):
    """A frozen premise did not hold. Never caught to continue; only to report and exit 5."""


# --------------------------------------------------------------------------------------------------
# Pure functions. Everything below takes parsed data, so the tests exercise the rule without IO.
# --------------------------------------------------------------------------------------------------


def _verify_frozen_threshold_against_member_receipts(member_v_iter2):
    """Transcription check on the FROZEN threshold. Can only reject, never adjust.

    `member_v_iter2` is the five committed member values at iteration 2, in any order."""
    if len(member_v_iter2) != 5:
        raise PremiseFailure(
            f"expected 5 committed member values to check the frozen threshold against, "
            f"got {len(member_v_iter2)}"
        )
    hi, lo = max(member_v_iter2), min(member_v_iter2)
    if hi != S_RANGE_2_MAX or lo != S_RANGE_2_MIN:
        raise PremiseFailure(
            "the committed member spread at iteration 2 is not the one the frozen threshold was "
            f"computed from: max {hi!r} vs declared {S_RANGE_2_MAX!r}, min {lo!r} vs declared "
            f"{S_RANGE_2_MIN!r}. The threshold is frozen; escalate rather than recompute."
        )
    recomputed = 0.5 * (hi - lo)
    # The predeclared literal is the SIXTEEN-DECIMAL RENDERING of 0.5*(max-min), not the bit-exact
    # double: 0.5*(hi-lo) is 0.17400298873009096 and the literal parses to 0.174002988730091, one
    # step apart (delta 5.55e-17). Comparing at 16 decimals is how the launcher battery checks it
    # too, so the two files agree on what "the threshold" means. Bit equality would be the wrong
    # check here -- it would fail on a correctly transcribed number -- but the raw delta is reported
    # so the claim can be contradicted rather than taken on trust.
    if f"{recomputed:.16f}" != f"{THRESH_PROCESS_RANGE:.16f}":
        raise PremiseFailure(
            f"frozen threshold {THRESH_PROCESS_RANGE!r} does not equal 0.5*(max-min) = "
            f"{recomputed!r} from the committed member receipts -- transcription error"
        )
    delta = THRESH_PROCESS_RANGE - recomputed
    if abs(delta) > 1e-15:
        raise PremiseFailure(
            f"frozen threshold and recomputed half-range agree to 16 decimals but differ by "
            f"{delta!r}, which is larger than one float step -- investigate"
        )
    return {
        "frozen_literal_governs": THRESH_PROCESS_RANGE,
        "recomputed_from_member_receipts": recomputed,
        "delta_frozen_minus_recomputed": delta,
        "agree_to_16_decimals": True,
        "bit_identical": THRESH_PROCESS_RANGE == recomputed,
        "note": "the frozen literal is 1 float step ABOVE the recomputed half-range, so the "
                "process-determined branch is very slightly stricter than the exact half-range. "
                "5.55e-17 against a 0.174 threshold; it cannot change any verdict.",
        "member_max_iter2": hi,
        "member_min_iter2": lo,
        "member_range_iter2": hi - lo,
    }


def read_v(traj, iteration):
    """The one field the predeclaration allows: numeric `end_to_end_achieved_over_required`.

    Rejects bools (which are ints in Python and would silently pass a numeric check), strings, and
    non-finite values. A NaN that reached `max`/`min` would poison the range silently."""
    entries = [e for e in traj.get("trajectory", []) if e.get("iteration") == iteration]
    if len(entries) != 1:
        raise ValueError(
            f"expected exactly one trajectory entry for iteration {iteration}, got {len(entries)}"
        )
    v = entries[0].get("end_to_end_achieved_over_required")
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(
            f"iteration {iteration}: end_to_end_achieved_over_required is {v!r} "
            f"({type(v).__name__}), not a number"
        )
    v = float(v)
    if not math.isfinite(v):
        raise ValueError(f"iteration {iteration}: end_to_end_achieved_over_required is {v!r}")
    return v


def read_tiers(traj):
    return tuple(
        next(e for e in traj["trajectory"] if e.get("iteration") == k).get("checkpoint_tier_step1")
        for k in ITERATIONS
    )


def floor_statistics(values_by_draw):
    """`F_range[k] = max_j v[j,k] - min_j v[j,k]` and `F_sd[k]` with ddof=1, at k in {0,1,2}.

    `values_by_draw` maps draw id -> (v0, v1, v2). sd is computed in plain Python so this file has
    no numpy dependency for the statistic itself -- numpy is needed only to compare `mc_indices`."""
    stats = {}
    n = len(values_by_draw)
    for k in ITERATIONS:
        col = [values_by_draw[j][k] for j in sorted(values_by_draw)]
        rng = max(col) - min(col)
        if n >= 2:
            mean = sum(col) / n
            sd = math.sqrt(sum((x - mean) ** 2 for x in col) / (n - 1))
        else:
            mean, sd = (col[0] if col else float("nan")), None
        stats[k] = {
            "n": n,
            "values_by_draw": {str(j): values_by_draw[j][k] for j in sorted(values_by_draw)},
            "max": max(col),
            "min": min(col),
            "mean": mean,
            "F_range": rng,
            "F_sd_ddof1": sd,
            "d_by_draw": {str(j): abs(values_by_draw[j][k] - 1.0) for j in sorted(values_by_draw)},
        }
    return stats


def apply_verdict(stats):
    """The frozen three-way rule, at iteration 2 only. Requires the complete valid set of five.

    Branch 1 needs BOTH its conditions. If they disagree -- range under 0.05 but a draw outside the
    band -- the verdict is FLOOR_INTERMEDIATE, as the predeclaration states explicitly."""
    s = stats[VERDICT_ITERATION]
    if s["n"] != len(DRAWS_REQUIRED):
        raise ValueError(
            f"apply_verdict requires all {len(DRAWS_REQUIRED)} draws; got n={s['n']}. "
            "Verdicting on a subset is what do_not_select_passing_subset forbids."
        )
    rng = s["F_range"]
    all_in_band = all(d <= BAND for d in s["d_by_draw"].values())
    if rng <= THRESH_SEED_RANGE and all_in_band:
        verdict = "FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED"
    elif rng >= THRESH_PROCESS_RANGE:
        verdict = "FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED"
    else:
        verdict = "FLOOR_INTERMEDIATE"
    return {
        "verdict": verdict,
        "evaluated_at_iteration": VERDICT_ITERATION,
        "F_range": rng,
        "branch1_range_condition_met": rng <= THRESH_SEED_RANGE,
        "branch1_band_condition_met": all_in_band,
        "branch2_condition_met": rng >= THRESH_PROCESS_RANGE,
        "thresholds_frozen": {
            "seed_determined_range_max": THRESH_SEED_RANGE,
            "band": BAND,
            "process_determined_range_min": THRESH_PROCESS_RANGE,
        },
    }


def branches_excluded_by_monotonicity(partial_stats):
    """What a PARTIAL set of valid draws already rules out, without verdicting.

    `max - min` over a set is non-decreasing when draws are added, so a partial `F_range[2]` is a
    lower bound on the final one. If that lower bound already exceeds `0.05`, branch 1 is
    unreachable no matter what the missing draws return. Likewise a partial `F_range[2]` at or above
    the process threshold already satisfies branch 2's condition.

    This is a DEDUCTION FROM THE FROZEN RULE, not a new rule: it moves no threshold, reaches no
    verdict, and selects no subset -- it is only valid because every draw in `partial_stats` is
    valid, so all of them are in the final set too."""
    rng = partial_stats[VERDICT_ITERATION]["F_range"]
    out = {
        "partial_F_range_iter2_is_a_lower_bound_on_the_final_value": rng,
        "why_valid": "max-min is non-decreasing under adding draws, and every draw here is valid, "
                     "so every one of them is in the final set",
        "excluded": [],
        "already_satisfied": [],
        "still_a_verdict": False,
    }
    if rng > THRESH_SEED_RANGE:
        out["excluded"].append("FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED")
    if rng >= THRESH_PROCESS_RANGE:
        out["already_satisfied"].append("FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED")
    return out


# --------------------------------------------------------------------------------------------------
# The eight validity clauses. Each returns (ok, ingredients) -- never a bare verdict (BEN-077).
# --------------------------------------------------------------------------------------------------


TARGET_PROV_RE = re.compile(r'"target_provenance"\s*:\s*"([A-Z_]+)"')
TARGET_SHA_RE = re.compile(r'"target_sha256"\s*:\s*"([0-9a-f]{64})"')
IDENTITY_RE = re.compile(r"\[g6-floor\] data identity verified: inputs ([0-9a-f]+) target ([0-9a-f]+)")


def clause1_completed(sacct_state, sacct_exit, done_marker_present):
    ok = sacct_state == "COMPLETED" and sacct_exit == "0:0" and bool(done_marker_present)
    return ok, {"sacct_state": sacct_state, "sacct_exit_code": sacct_exit,
                "completion_marker_present": bool(done_marker_present)}


def clause2_target_provenance(log_text):
    """`target_provenance` PASS against the canonical receipt, with target `544b2f6a...`.

    The driver prints this block to stdout and writes no separate provenance receipt, so the log IS
    the artifact here. Fail closed when the log is missing or the block is absent -- an unverifiable
    clause is a failed clause."""
    if not log_text:
        return False, {"reason": "stdout log absent or empty; clause cannot be verified"}
    prov = TARGET_PROV_RE.search(log_text)
    sha = TARGET_SHA_RE.search(log_text)
    ident = IDENTITY_RE.search(log_text)
    ing = {
        "target_provenance": prov.group(1) if prov else None,
        "target_sha256_in_log": sha.group(1) if sha else None,
        "target_sha256_required": TARGET_SHA,
        "launcher_preflight_identity_line_present": bool(ident),
        "launcher_preflight_target_prefix": ident.group(2) if ident else None,
    }
    ok = (
        prov is not None and prov.group(1) == "PASS"
        and sha is not None and sha.group(1) == TARGET_SHA
        and ident is not None and TARGET_SHA.startswith(ident.group(2))
    )
    return ok, ing


def clause3_realized_policy(seed_policy_from_artifact):
    """Read OFF THE ARTIFACT, never from the launch command -- that is the point of the clause."""
    got = {k: seed_policy_from_artifact.get(k) for k in POLICY_REQUIRED}
    mismatches = {k: (got[k], POLICY_REQUIRED[k]) for k in POLICY_REQUIRED
                  if got[k] != POLICY_REQUIRED[k]}
    return not mismatches, {"realized": got, "required": dict(POLICY_REQUIRED),
                            "mismatches": mismatches}


def clause4_class_ratio(r_from_artifact, r_from_trajectory):
    """Exact equality. `R` is subsample-invariant and shared, so any difference means a different
    target or a different inventory -- there is no tolerance to spend here."""
    ok = r_from_artifact == R_REQUIRED and r_from_trajectory == R_REQUIRED
    return ok, {"R_from_artifact": r_from_artifact, "R_from_trajectory_receipt": r_from_trajectory,
                "R_required_exactly": R_REQUIRED}


def clause5_mc_indices(equal_to_member1, n_rows, n_differing):
    ok = bool(equal_to_member1) and n_differing == 0
    return ok, {"array_equal_to_member1": bool(equal_to_member1), "n_rows": n_rows,
                "n_differing_rows": n_differing}


def clause6_gates(gate_verdict, gate_bi_pass, gate_a1_bit_exact, gate_a2_bit_exact,
                  repro_rel_devs):
    """Gate A/B PASS with exact MC-index and truth-normalization identity, and the within-job
    decomposition reproduction gate PASS."""
    repro_ok = bool(repro_rel_devs) and all(
        d is not None and abs(d) == 0.0 for d in repro_rel_devs.values()
    )
    ok = (gate_verdict == "GATE_AB_PASSED" and bool(gate_bi_pass)
          and bool(gate_a1_bit_exact) and bool(gate_a2_bit_exact) and repro_ok)
    return ok, {"gate_verdict": gate_verdict, "gate_Bi_pass": bool(gate_bi_pass),
                "gate_A1_mc_indices_bit_exact": bool(gate_a1_bit_exact),
                "gate_A2_truth_norm_bit_exact": bool(gate_a2_bit_exact),
                "reproduction_gate_rel_dev": dict(repro_rel_devs),
                "reproduction_gate_all_zero": repro_ok}


def clause7_checkpoints(weights_h5_names, all_output_paths_by_draw, this_draw):
    """Exactly eight checkpoints in the draw's OWN isolated `w_nominal`, and no output path shared
    with another draw."""
    n = len(weights_h5_names)
    others = set()
    for j, paths in all_output_paths_by_draw.items():
        if j != this_draw:
            others |= set(paths)
    shared = sorted(set(all_output_paths_by_draw.get(this_draw, [])) & others)
    ok = n == N_CHECKPOINTS_REQUIRED and not shared
    return ok, {"n_weights_h5": n, "required": N_CHECKPOINTS_REQUIRED,
                "checkpoints": sorted(weights_h5_names),
                "paths_shared_with_another_draw": shared}


def clause8_execution_environment(env):
    """The OI-15 residual: a draw without persisted execution identity cannot serve as an
    across-process data point, because nothing records which process it was."""
    exe = (env or {}).get("execution", {})
    required = ["host", "gpu_identity", "slurm_job_id", "slurm_array_job_id", "slurm_array_task_id",
                "science_head_at_runtime", "code_head_at_runtime"]
    missing = [k for k in required if not exe.get(k)]
    digests = (env or {}).get("bound_digests", {})
    digest_missing = [k for k in ["inputs_npz", "target_npy", "driver", "loader", "engine"]
                      if not digests.get(k)]
    ok = not missing and not digest_missing and digests.get("target_npy") == TARGET_SHA
    return ok, {"present": {k: exe.get(k) for k in required}, "missing_execution_fields": missing,
                "missing_bound_digests": digest_missing,
                "bound_target_npy": digests.get("target_npy")}


# --------------------------------------------------------------------------------------------------
# IO. Kept in one place so everything above is testable without a filesystem.
# --------------------------------------------------------------------------------------------------


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _one(paths, what):
    paths = sorted(paths)
    if len(paths) != 1:
        raise ValueError(f"expected exactly one {what}, found {len(paths)}: {paths}")
    return paths[0]


def _read_text_or_none(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def collect_draw(draw, floor_dir, member1_indices, sacct, all_output_paths):
    """Gather one new draw (2..5) and evaluate all eight clauses. Returns a per-draw record."""
    d = Path(floor_dir) / f"draw_{draw}"
    rec = {"draw": draw, "dir": str(d), "present": d.is_dir()}
    if not rec["present"]:
        rec["clauses"] = {}
        rec["valid"] = False
        rec["reason"] = "draw directory absent"
        return rec, None, None

    traj = _load_json(_one(glob.glob(str(d / "STEP1_TRAJECTORY.slurm-*.json")), "trajectory receipt"))
    gate = _load_json(_one(glob.glob(str(d / "GATE_AB_PUSH_PROVENANCE.slurm-*.json")), "gate receipt"))
    decomp = _load_json(_one(glob.glob(str(d / "STEP1_DECOMPOSITION.slurm-*.json")), "decomposition"))
    env = _load_json(_one(glob.glob(str(d / "EXECUTION_ENVIRONMENT.slurm-*.json")), "env sidecar"))
    npz_path = _one(glob.glob(str(d / f"pet_fullevent_floor_draw{draw}_weights.npz")), "weights npz")
    done = Path(npz_path + ".done").is_file()
    log = _read_text_or_none(Path(floor_dir) / "logs" / f"g6_floor_{sacct.get('array_job_id')}_{draw}.out")

    import numpy as np  # local: only this clause needs numpy
    z = np.load(npz_path, allow_pickle=True)
    policy = z["seed_policy"].item()
    r_artifact = float(z["step1_class_ratio"])
    idx = z["mc_indices"]
    if member1_indices is None:
        eq, n_diff = False, -1
    else:
        eq = idx.shape == member1_indices.shape and bool(np.array_equal(idx, member1_indices))
        n_diff = 0 if eq else (
            int((idx != member1_indices).sum()) if idx.shape == member1_indices.shape else -1
        )

    h5 = [p.name for p in (d / "w_nominal").glob("*.weights.h5")]
    repro = {k: v.get("rel_dev") for k, v in traj.get("reproduction_gate", {}).items()}

    clauses = {}
    clauses["1_completed"] = clause1_completed(sacct.get("state"), sacct.get("exit_code"), done)
    clauses["2_target_provenance"] = clause2_target_provenance(log)
    clauses["3_realized_policy"] = clause3_realized_policy(policy)
    clauses["4_class_ratio"] = clause4_class_ratio(r_artifact, traj.get("R"))
    clauses["5_mc_indices"] = clause5_mc_indices(eq, int(idx.shape[0]), n_diff)
    clauses["6_gates"] = clause6_gates(
        gate.get("verdict"), gate.get("gate_B", {}).get("Bi_pass"),
        gate.get("gate_A", {}).get("A1_mc_indices_bit_exact"),
        gate.get("gate_A", {}).get("A2_truth_norm_bit_exact"), repro)
    clauses["7_checkpoints"] = clause7_checkpoints(h5, all_output_paths, draw)
    clauses["8_execution_environment"] = clause8_execution_environment(env)

    rec["clauses"] = {k: {"ok": ok, "ingredients": ing} for k, (ok, ing) in clauses.items()}
    rec["valid"] = all(ok for ok, _ in clauses.values())
    rec["failed_clauses"] = [k for k, (ok, _) in clauses.items() if not ok]
    rec["decomposition_verdict_field_is_not_a_validity_clause"] = decomp.get("verdict")
    rec["execution"] = (env or {}).get("execution", {})
    tiers = read_tiers(traj)
    return rec, tuple(read_v(traj, k) for k in ITERATIONS), tiers


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--floor-dir", required=True)
    ap.add_argument("--member1-dir", required=True,
                    help="fullevent_ml_ensemble/member_1 -- draw 1, reused NOT retrained")
    ap.add_argument("--member-trajectory-glob", required=True,
                    help="all five committed member trajectories, to check the frozen threshold")
    ap.add_argument("--sacct-json", required=True,
                    help='JSON: {"array_job_id":"56863958","tasks":{"2":{"state":"COMPLETED",'
                         '"exit_code":"0:0"}, ...}} -- produced from sacct in the same turn (BEN-027)')
    ap.add_argument("--json", required=True)
    args = ap.parse_args(argv)

    out = {
        "schema": "gate6-leg-F-floor-statistics-v1",
        "predeclaration": "docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md",
        "prohibitions_still_live": PROHIBITIONS,
        "gate6_unblocked_by_any_outcome": False,
        "c_ml_construction_allowed": False,
        "this_leg_does_not": [
            "re-verdict any Gate-6 member, including member 3",
            "calibrate the best-epoch vs _final checkpoint-tier gap (that is Leg 0, unauthorized)",
            "attribute variance between estimator init and subsample (that is Leg X)",
            "license C_ML, move the central, start Leg 2, or select a subset",
        ],
    }

    try:
        member_files = sorted(glob.glob(args.member_trajectory_glob))
        member_v = [read_v(_load_json(p), VERDICT_ITERATION) for p in member_files]
        out["frozen_threshold_check"] = _verify_frozen_threshold_against_member_receipts(member_v)
        out["frozen_threshold_check"]["member_receipts"] = member_files

        import numpy as np
        m1_npz = _one(glob.glob(str(Path(args.member1_dir) / "*_weights.npz")), "member 1 npz")
        member1_indices = np.load(m1_npz, allow_pickle=True)["mc_indices"]
        m1_traj = _load_json(
            _one(glob.glob(str(Path(args.member1_dir) / "trajectory" / "STEP1_TRAJECTORY.slurm-*.json")),
                 "member 1 trajectory"))
        v1 = tuple(read_v(m1_traj, k) for k in ITERATIONS)
        if v1[VERDICT_ITERATION] != V_DRAW1_ITER2:
            raise PremiseFailure(
                f"draw 1 (member_1) iteration-2 value is {v1[VERDICT_ITERATION]!r}, not the "
                f"predeclared {V_DRAW1_ITER2!r}. Draw 1 must not have been retrained."
            )
        tiers = {1: read_tiers(m1_traj)}

        sacct = _load_json(args.sacct_json)
        all_paths = {}
        for j in DRAWS_REQUIRED[1:]:
            dd = Path(args.floor_dir) / f"draw_{j}"
            all_paths[j] = sorted(str(p) for p in dd.glob("*")) if dd.is_dir() else []

        values, records = {1: v1}, []
        out["draw_1"] = {"source": "EXISTING member_1 artifact, reused unmodified, NOT retrained",
                         "trajectory_receipt": m1_traj and str(_one(
                             glob.glob(str(Path(args.member1_dir) / "trajectory"
                                           / "STEP1_TRAJECTORY.slurm-*.json")), "member 1 trajectory")),
                         "v": list(v1)}
        for j in DRAWS_REQUIRED[1:]:
            task = (sacct.get("tasks") or {}).get(str(j), {})
            task.setdefault("array_job_id", sacct.get("array_job_id"))
            rec, v, tier = collect_draw(j, args.floor_dir, member1_indices,
                                        {**task, "array_job_id": sacct.get("array_job_id")},
                                        all_paths)
            records.append(rec)
            if rec["present"] and rec["valid"]:
                values[j] = v
                tiers[j] = tier
            elif rec["present"]:
                tiers[j] = tier
        out["draws"] = records

        bad_tiers = {j: list(t) for j, t in tiers.items() if tuple(t) != TIER_PATTERN}
        out["premise_checks"] = {
            "checkpoint_tier_homogeneity": {
                "required_pattern": list(TIER_PATTERN),
                "observed": {str(j): list(t) for j, t in sorted(tiers.items())},
                "ok": not bad_tiers,
                "why_it_matters": "the predeclaration's like-for-like claim is that every draw reads "
                                  "iterations 0/1 from best-epoch and iteration 2 from _final. If a "
                                  "draw departs, F_range mixes tiers and that claim is void.",
            }
        }
        if bad_tiers:
            raise PremiseFailure(f"checkpoint-tier pattern differs by draw: {bad_tiers}")

        present = [r["draw"] for r in records if r["present"]]
        invalid = [r["draw"] for r in records if r["present"] and not r["valid"]]
        out["inventory"] = {"draws_required": list(DRAWS_REQUIRED),
                           "draws_present": [1] + present,
                           "draws_valid": sorted(values),
                           "draws_invalid": invalid,
                           "n": len(values)}

        if invalid:
            out["statistics"] = None
            out["verdict"] = "NO_VERDICT_INVALID_DRAW"
            out["why"] = ("a present draw failed a mandatory validity clause. This leg reports n<5 "
                          "and reaches no verdict; proceeding on the survivors is the shape "
                          "do_not_select_passing_subset forbids.")
            rc = 4
        elif len(values) < len(DRAWS_REQUIRED):
            stats = floor_statistics(values)
            out["provisional_statistics"] = {str(k): v for k, v in stats.items()}
            out["verdict"] = "NO_VERDICT_INCOMPLETE"
            out["why"] = (f"{len(values)} of {len(DRAWS_REQUIRED)} draws present and valid. The "
                          "statistics above are PROVISIONAL and are not a verdict.")
            out["deduction_from_the_frozen_rule"] = branches_excluded_by_monotonicity(stats)
            rc = 3
        else:
            stats = floor_statistics(values)
            out["statistics"] = {str(k): v for k, v in stats.items()}
            out.update(apply_verdict(stats))
            rc = 0
    except PremiseFailure as exc:
        out["verdict"] = "PREMISE_FAILURE"
        out["why"] = str(exc)
        rc = 5

    Path(args.json).write_text(json.dumps(out, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": out.get("verdict"), "json": args.json, "exit": rc}, indent=1))
    return rc


if __name__ == "__main__":
    sys.exit(main())
