#!/usr/bin/env python3
"""Acceptance tests for `gate6_floor_statistics.py` -- the executable form of the Leg F rule.

WHAT AXIS THIS BATTERY COVERS, named because a battery that does not name its axis gets mistaken
for coverage it does not have (BEN-119). Four axes:

  1. THE FROZEN NUMBERS. `0.05`, `0.10`, `0.1740029887300910` are asserted against the
     predeclaration's own text and recomputed from the committed member operands, so a later edit
     that "tidies" one is a test failure rather than a silent change of what the floor measures.
  2. THE VERDICT BOUNDARIES, exercised AT the thresholds, because `<=` vs `<` at `0.05` and `>=` vs
     `>` at `0.1740...` is the whole difference between two verdicts.
  3. REFUSAL TO VERDICT: n<5, an invalid draw, and a partial set must all fail to produce a verdict.
     This is the mechanised form of `do_not_select_passing_subset`, and it is the property most
     likely to be quietly relaxed by a future edit under schedule pressure.
  4. EACH VALIDITY CLAUSE INDEPENDENTLY, passing on good input and failing on one degradation at a
     time -- so a clause that is silently satisfied by anything is caught.

STATED GAPS, at the foot of the file rather than left to be discovered.
"""
import importlib.util
import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "nd-unfolding/pet/gate6_floor_statistics.py"
PREDECL = REPO / "docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md"

_spec = importlib.util.spec_from_file_location("gate6_floor_statistics", MODULE_PATH)
fs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fs)

PREDECL_TEXT = PREDECL.read_text(encoding="utf-8")

# The five committed member values at iteration 2 (VL116-VL120). Only the max and min are quoted in
# the predeclaration; the three interior values do not affect max-min, so they are placeholders here
# and the test asserts only what the threshold actually depends on.
MEMBER_V_ITER2 = [
    fs.S_RANGE_2_MAX,
    fs.S_RANGE_2_MIN,
    0.9806897311812962,   # member 1, the one converged member
    0.95,
    0.90,
]


def traj(v0, v1, v2, tiers=fs.TIER_PATTERN, repro_zero=True):
    """A minimal trajectory receipt with only the fields the rule is allowed to read."""
    return {
        "R": fs.R_REQUIRED,
        "reproduction_gate": {
            "increment1": {"rel_dev": 0.0 if repro_zero else 1e-9},
            "push_prev": {"rel_dev": 0.0},
            "push_final": {"rel_dev": 0.0},
        },
        "trajectory": [
            {"iteration": 0, "end_to_end_achieved_over_required": v0,
             "checkpoint_tier_step1": tiers[0]},
            {"iteration": 1, "end_to_end_achieved_over_required": v1,
             "checkpoint_tier_step1": tiers[1]},
            {"iteration": 2, "end_to_end_achieved_over_required": v2,
             "checkpoint_tier_step1": tiers[2]},
        ],
    }


def five(v2_values):
    """Draw id -> (v0, v1, v2) with only iteration 2 varied, for verdict-boundary tests."""
    return {j + 1: (1.0, 1.0, v) for j, v in enumerate(v2_values)}


# ------------------------------------------------------------------ axis 1: the frozen numbers


def test_frozen_thresholds_match_the_predeclaration_text():
    assert "F_range[2] ≤ 0.05" in PREDECL_TEXT
    assert "0.1740029887300910" in PREDECL_TEXT
    assert fs.THRESH_SEED_RANGE == 0.05
    assert fs.BAND == 0.10
    assert fs.THRESH_PROCESS_RANGE == 0.1740029887300910


def test_process_threshold_is_half_the_committed_member_range_to_sixteen_decimals():
    """Recomputed from the operands, not trusted from the prose. Same check the launcher battery
    makes -- duplicated deliberately, because these are two different files that could drift apart.

    NOT bit equality: the predeclared literal is the 16-decimal rendering of `0.5*(max-min)`, and
    the two doubles are one step apart (5.55e-17). Asserting `==` here would fail on a correctly
    transcribed threshold, which is how this test was written first."""
    recomputed = 0.5 * (fs.S_RANGE_2_MAX - fs.S_RANGE_2_MIN)
    assert f"{recomputed:.16f}" == f"{fs.THRESH_PROCESS_RANGE:.16f}" == "0.1740029887300910"
    assert abs(recomputed - fs.THRESH_PROCESS_RANGE) < 1e-15
    assert str(fs.S_RANGE_2_MAX) in PREDECL_TEXT
    assert str(fs.S_RANGE_2_MIN) in PREDECL_TEXT


def test_frozen_threshold_check_accepts_the_committed_spread():
    got = fs._verify_frozen_threshold_against_member_receipts(MEMBER_V_ITER2)
    assert got["agree_to_16_decimals"] is True
    assert got["bit_identical"] is False          # documented, not hidden
    assert abs(got["delta_frozen_minus_recomputed"]) < 1e-15


def test_frozen_threshold_check_rejects_a_different_member_spread():
    """If the member receipts ever stop being the ones the threshold came from, that is an
    escalation, not a recomputation."""
    with pytest.raises(fs.PremiseFailure) as e:
        fs._verify_frozen_threshold_against_member_receipts(
            [1.5, 0.5, 0.9806897311812962, 0.95, 0.90])
    assert "frozen" in str(e.value)


def test_frozen_threshold_check_rejects_the_wrong_number_of_members():
    with pytest.raises(fs.PremiseFailure):
        fs._verify_frozen_threshold_against_member_receipts(MEMBER_V_ITER2[:4])


def test_draw1_value_and_policy_are_the_predeclared_ones():
    assert fs.V_DRAW1_ITER2 == 0.9806897311812962
    assert str(fs.V_DRAW1_ITER2) in PREDECL_TEXT
    assert fs.R_REQUIRED == 1.1240802949941018
    assert fs.POLICY_REQUIRED == {"estimator_seed": 42, "subsample_seed": 0, "niter": 3,
                                  "epochs": 8, "train_events": 2000000, "batch_size": 512}


def test_checkpoint_count_is_eight_weights_files_not_fourteen_directory_entries():
    """The real `w_nominal` holds 14 files: 8 `.weights.h5` and 6 `.pkl` histories. A clause that
    counted directory entries would be satisfied by 14 and would also be satisfied by 8 `.pkl`s and
    6 checkpoints."""
    assert fs.N_CHECKPOINTS_REQUIRED == 8
    real = [
        "OmniFold_fe_nominal_nominal_iter0_step1.weights.h5",
        "OmniFold_fe_nominal_nominal_iter0_step2.weights.h5",
        "OmniFold_fe_nominal_nominal_iter1_step1.weights.h5",
        "OmniFold_fe_nominal_nominal_iter1_step2.weights.h5",
        "OmniFold_fe_nominal_nominal_iter2_step1.weights.h5",
        "OmniFold_fe_nominal_nominal_iter2_step1_final.weights.h5",
        "OmniFold_fe_nominal_nominal_iter2_step2.weights.h5",
        "OmniFold_fe_nominal_nominal_iter2_step2_final.weights.h5",
    ]
    ok, ing = fs.clause7_checkpoints(real, {2: ["a"], 3: ["b"]}, 2)
    assert ok and ing["n_weights_h5"] == 8


# ------------------------------------------------------------------ axis 2: verdict boundaries


def stats_at(f_range, ds, n=5):
    """Hand-build the minimal stats dict `apply_verdict` reads, so the COMPARISON OPERATORS can be
    exercised AT the thresholds.

    Why not drive it through values: `0.05` and `0.10` are not the difference of any two doubles
    near `1.0`. `1.05 - 1.0` is `0.050000000000000044` and `abs(1.10 - 1.0)` is
    `0.10000000000000009`, both strictly greater than the threshold, so a value-driven "exactly at
    the boundary" test silently tests the just-over case instead -- which is how the first version of
    these three tests failed. `<=` vs `<` at the boundary is a real risk in the rule and it is only
    testable at the predicate. The value-driven tests below cover the wiring."""
    return {2: {"n": n, "F_range": f_range,
                "d_by_draw": {str(i + 1): d for i, d in enumerate(ds)}}}


def test_range_exactly_at_the_seed_threshold_is_seed_determined():
    v = fs.apply_verdict(stats_at(fs.THRESH_SEED_RANGE, [0.0, 0.0, 0.0, 0.0, 0.0]))
    assert v["branch1_range_condition_met"] is True
    assert v["verdict"] == "FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED"


def test_range_one_float_step_over_the_seed_threshold_is_not_seed_determined():
    over = math.nextafter(fs.THRESH_SEED_RANGE, 1.0)
    v = fs.apply_verdict(stats_at(over, [0.0] * 5))
    assert v["branch1_range_condition_met"] is False
    assert v["verdict"] == "FLOOR_INTERMEDIATE"


def test_range_just_over_the_seed_threshold_via_real_values_is_not_seed_determined():
    v = fs.apply_verdict(fs.floor_statistics(five([1.0, 1.0, 1.0, 1.0, 1.0501])))
    assert v["branch1_range_condition_met"] is False
    assert v["verdict"] == "FLOOR_INTERMEDIATE"


def test_range_exactly_at_the_process_threshold_is_process_determined():
    v = fs.apply_verdict(stats_at(fs.THRESH_PROCESS_RANGE, [0.2] * 5))
    assert v["branch2_condition_met"] is True
    assert v["verdict"] == "FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED"


def test_range_one_float_step_under_the_process_threshold_is_intermediate():
    under = math.nextafter(fs.THRESH_PROCESS_RANGE, 0.0)
    v = fs.apply_verdict(stats_at(under, [0.2] * 5))
    assert v["branch2_condition_met"] is False
    assert v["verdict"] == "FLOOR_INTERMEDIATE"


def test_range_just_under_the_process_threshold_via_real_values_is_intermediate():
    v = fs.apply_verdict(fs.floor_statistics(five([1.0, 1.0, 1.0, 1.0, 1.0 + 0.17])))
    assert v["verdict"] == "FLOOR_INTERMEDIATE"


def test_small_range_but_a_draw_outside_the_band_is_intermediate_not_seed_determined():
    """The predeclaration says this explicitly: if branch 1's two conditions disagree, the verdict
    is INTERMEDIATE. A tight cluster sitting 20% off 1.0 is reproducible AND wrong."""
    v = fs.apply_verdict(fs.floor_statistics(five([1.20, 1.21, 1.20, 1.21, 1.20])))
    assert v["branch1_range_condition_met"] is True
    assert v["branch1_band_condition_met"] is False
    assert v["verdict"] == "FLOOR_INTERMEDIATE"


def test_band_boundary_is_inclusive():
    v = fs.apply_verdict(stats_at(0.0, [fs.BAND] * 5))
    assert v["branch1_band_condition_met"] is True
    assert v["verdict"] == "FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED"


def test_band_one_float_step_outside_is_not_inclusive():
    v = fs.apply_verdict(stats_at(0.0, [0.0, 0.0, 0.0, 0.0, math.nextafter(fs.BAND, 1.0)]))
    assert v["branch1_band_condition_met"] is False
    assert v["verdict"] == "FLOOR_INTERMEDIATE"


def test_a_single_draw_outside_the_band_is_enough_to_fail_branch1():
    v = fs.apply_verdict(stats_at(0.0, [0.0, 0.0, 0.0, 0.0, 0.2]))
    assert v["branch1_band_condition_met"] is False


def test_the_three_branches_are_mutually_exclusive_over_a_sweep():
    seen = set()
    for extra in [0.0, 0.01, 0.05, 0.06, 0.17, fs.THRESH_PROCESS_RANGE, 0.30]:
        v = fs.apply_verdict(fs.floor_statistics(five([1.0, 1.0, 1.0, 1.0, 1.0 + extra])))
        seen.add(v["verdict"])
        flags = [v["verdict"] == "FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED",
                 v["verdict"] == "FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED",
                 v["verdict"] == "FLOOR_INTERMEDIATE"]
        assert sum(flags) == 1
    assert len(seen) == 3, f"the sweep should reach all three branches, reached {seen}"


# ------------------------------------------------------------------ axis 3: refusal to verdict


def test_apply_verdict_refuses_four_draws():
    with pytest.raises(ValueError) as e:
        fs.apply_verdict(fs.floor_statistics({1: (1.0, 1.0, 1.0), 2: (1.0, 1.0, 1.0),
                                              3: (1.0, 1.0, 1.0), 4: (1.0, 1.0, 1.0)}))
    assert "do_not_select_passing_subset" in str(e.value)


def test_apply_verdict_refuses_a_single_draw():
    with pytest.raises(ValueError):
        fs.apply_verdict(fs.floor_statistics({1: (1.0, 1.0, 1.0)}))


def test_monotonicity_deduction_excludes_branch1_but_is_not_a_verdict():
    """The live case as of the first wave: draws 1, 2 and 3 already span more than 0.05 at
    iteration 2, and `max-min` cannot shrink when draws 4 and 5 arrive."""
    partial = {1: (1.0, 1.0, 0.9806897311812962),
               2: (1.3772732412607531, 1.1103230946149727, 0.9955198662084275),
               3: (0.8400494065800533, 0.9356622502386326, 0.9431204794060756)}
    stats = fs.floor_statistics(partial)
    ded = fs.branches_excluded_by_monotonicity(stats)
    assert ded["still_a_verdict"] is False
    assert "FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED" in ded["excluded"]
    assert ded["already_satisfied"] == []
    assert stats[2]["F_range"] > fs.THRESH_SEED_RANGE
    assert stats[2]["F_range"] < fs.THRESH_PROCESS_RANGE


def test_monotonicity_deduction_excludes_nothing_when_the_partial_range_is_tight():
    stats = fs.floor_statistics({1: (1.0, 1.0, 1.00), 2: (1.0, 1.0, 1.01)})
    ded = fs.branches_excluded_by_monotonicity(stats)
    assert ded["excluded"] == [] and ded["already_satisfied"] == []


def test_monotonicity_deduction_can_confirm_branch2_early():
    stats = fs.floor_statistics({1: (1.0, 1.0, 1.0), 2: (1.0, 1.0, 1.0 + 0.5)})
    ded = fs.branches_excluded_by_monotonicity(stats)
    assert ded["already_satisfied"] == ["FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED"]
    assert ded["still_a_verdict"] is False


def test_range_is_monotone_under_adding_draws_which_is_what_the_deduction_rests_on():
    base = {1: (1.0, 1.0, 0.98), 2: (1.0, 1.0, 1.02)}
    r0 = fs.floor_statistics(base)[2]["F_range"]
    for extra in [0.99, 1.0, 1.05, 0.90]:
        grown = dict(base)
        grown[3] = (1.0, 1.0, extra)
        assert fs.floor_statistics(grown)[2]["F_range"] >= r0


# ------------------------------------------------------------------ axis 1/2 support: the statistic


def test_floor_statistics_arithmetic_against_hand_computation():
    vals = {1: (0.0, 0.0, 1.0), 2: (0.0, 0.0, 2.0), 3: (0.0, 0.0, 4.0)}
    s = fs.floor_statistics(vals)[2]
    assert s["F_range"] == 3.0
    assert s["mean"] == pytest.approx(7.0 / 3.0)
    # ddof=1: sqrt(((1-7/3)^2+(2-7/3)^2+(4-7/3)^2)/2) = sqrt(4.666.../2)
    assert s["F_sd_ddof1"] == pytest.approx(math.sqrt(((1 - 7 / 3) ** 2 + (2 - 7 / 3) ** 2
                                                       + (4 - 7 / 3) ** 2) / 2))
    assert s["d_by_draw"] == {"1": 0.0, "2": 1.0, "3": 3.0}


def test_sd_is_ddof1_not_population():
    s = fs.floor_statistics({1: (0, 0, 1.0), 2: (0, 0, 3.0)})[2]
    assert s["F_sd_ddof1"] == pytest.approx(math.sqrt(2.0))   # ddof=1 gives sqrt(2), ddof=0 gives 1


def test_statistics_are_reported_for_all_three_iterations():
    s = fs.floor_statistics({1: (1.0, 2.0, 3.0), 2: (1.5, 2.5, 3.5)})
    assert set(s) == {0, 1, 2}
    for k in (0, 1, 2):
        assert s[k]["F_range"] == pytest.approx(0.5)


def test_read_v_reads_only_the_allowed_field():
    t = traj(1.1, 1.2, 1.3)
    t["trajectory"][2]["push_dev_vs_R"] = 999.0       # the sibling field; must be ignored
    assert fs.read_v(t, 2) == 1.3


def test_read_v_rejects_a_bool_because_bools_are_ints_in_python():
    t = traj(1.1, 1.2, 1.3)
    t["trajectory"][2]["end_to_end_achieved_over_required"] = True
    with pytest.raises(ValueError) as e:
        fs.read_v(t, 2)
    assert "not a number" in str(e.value)


def test_read_v_rejects_a_string():
    t = traj(1.1, 1.2, 1.3)
    t["trajectory"][2]["end_to_end_achieved_over_required"] = "1.3"
    with pytest.raises(ValueError):
        fs.read_v(t, 2)


def test_read_v_rejects_nan_which_would_silently_poison_max_and_min():
    t = traj(1.1, 1.2, float("nan"))
    with pytest.raises(ValueError):
        fs.read_v(t, 2)


def test_read_v_rejects_a_missing_or_duplicated_iteration():
    t = traj(1.1, 1.2, 1.3)
    t["trajectory"].append(dict(t["trajectory"][2]))
    with pytest.raises(ValueError):
        fs.read_v(t, 2)
    t2 = traj(1.1, 1.2, 1.3)
    del t2["trajectory"][2]
    with pytest.raises(ValueError):
        fs.read_v(t2, 2)


def test_tier_pattern_is_the_one_the_real_receipts_carry():
    assert fs.TIER_PATTERN == ("best-epoch", "best-epoch", "final(BEN-043)")
    assert fs.read_tiers(traj(1, 1, 1)) == fs.TIER_PATTERN


# ------------------------------------------------------------------ axis 4: each validity clause


GOOD_LOG = (
    "[g6-floor] data identity verified: inputs fa6b346316024216 target 544b2f6a2451480a\n"
    '  "target_provenance": "PASS",\n'
    f'  "target_sha256": "{fs.TARGET_SHA}",\n'
    '  "receipt_status": "PASS",\n'
)


def test_clause1_passes_on_completed_and_fails_on_each_degradation():
    assert fs.clause1_completed("COMPLETED", "0:0", True)[0] is True
    assert fs.clause1_completed("FAILED", "0:0", True)[0] is False
    assert fs.clause1_completed("COMPLETED", "1:0", True)[0] is False
    assert fs.clause1_completed("COMPLETED", "0:0", False)[0] is False
    assert fs.clause1_completed(None, None, True)[0] is False


def test_clause2_passes_on_the_real_log_shape():
    ok, ing = fs.clause2_target_provenance(GOOD_LOG)
    assert ok is True
    assert ing["target_provenance"] == "PASS"
    assert ing["launcher_preflight_identity_line_present"] is True


def test_clause2_fails_closed_when_the_log_is_absent():
    """An unverifiable clause is a failed clause, not a skipped one."""
    assert fs.clause2_target_provenance(None)[0] is False
    assert fs.clause2_target_provenance("")[0] is False


def test_clause2_fails_on_a_different_target_digest():
    bad = GOOD_LOG.replace(fs.TARGET_SHA, "0" * 64)
    assert fs.clause2_target_provenance(bad)[0] is False


def test_clause2_fails_when_provenance_is_not_pass():
    assert fs.clause2_target_provenance(GOOD_LOG.replace('"PASS"', '"WARN"', 1))[0] is False


def test_clause2_fails_without_the_launcher_preflight_line():
    stripped = "\n".join(l for l in GOOD_LOG.splitlines() if "data identity verified" not in l)
    assert fs.clause2_target_provenance(stripped)[0] is False


def test_clause3_reads_the_realized_policy_and_rejects_any_single_deviation():
    good = dict(fs.POLICY_REQUIRED, lr_policy={"schedule": "whatever"})
    assert fs.clause3_realized_policy(good)[0] is True
    for key, wrong in [("estimator_seed", 46), ("subsample_seed", 4), ("niter", 4),
                       ("epochs", 16), ("train_events", 1000000), ("batch_size", 256)]:
        ok, ing = fs.clause3_realized_policy(dict(good, **{key: wrong}))
        assert ok is False and key in ing["mismatches"]


def test_clause3_fails_on_a_missing_policy_field_rather_than_ignoring_it():
    partial = {k: v for k, v in fs.POLICY_REQUIRED.items() if k != "epochs"}
    ok, ing = fs.clause3_realized_policy(partial)
    assert ok is False and "epochs" in ing["mismatches"]


def test_clause4_requires_exact_equality_with_no_tolerance():
    assert fs.clause4_class_ratio(fs.R_REQUIRED, fs.R_REQUIRED)[0] is True
    nudged = math.nextafter(fs.R_REQUIRED, 2.0)
    assert nudged != fs.R_REQUIRED
    assert fs.clause4_class_ratio(nudged, fs.R_REQUIRED)[0] is False
    assert fs.clause4_class_ratio(fs.R_REQUIRED, nudged)[0] is False


def test_clause5_requires_array_equality_with_member1():
    assert fs.clause5_mc_indices(True, 2000000, 0)[0] is True
    assert fs.clause5_mc_indices(False, 2000000, 17)[0] is False
    assert fs.clause5_mc_indices(False, 2000000, -1)[0] is False
    # a "True" that arrives with differing rows is contradictory; the clause must not accept it
    assert fs.clause5_mc_indices(True, 2000000, 3)[0] is False


def test_clause6_requires_the_gate_verdict_and_zero_reproduction_deviation():
    repro = {"increment1": 0.0, "push_prev": 0.0, "push_final": 0.0}
    assert fs.clause6_gates("GATE_AB_PASSED", True, True, True, repro)[0] is True
    assert fs.clause6_gates("GATE_AB_FAILED", True, True, True, repro)[0] is False
    assert fs.clause6_gates("GATE_AB_PASSED", False, True, True, repro)[0] is False
    assert fs.clause6_gates("GATE_AB_PASSED", True, False, True, repro)[0] is False
    assert fs.clause6_gates("GATE_AB_PASSED", True, True, False, repro)[0] is False
    assert fs.clause6_gates("GATE_AB_PASSED", True, True, True, {})[0] is False
    assert fs.clause6_gates("GATE_AB_PASSED", True, True, True,
                            dict(repro, push_final=1e-12))[0] is False
    assert fs.clause6_gates("GATE_AB_PASSED", True, True, True,
                            dict(repro, push_final=None))[0] is False


def test_clause6_ignores_the_decomposition_verdict_field():
    """The real draws carry `"verdict": "INDETERMINATE"` in the decomposition receipt. That is the
    decomposition's own reading of the physics, not a validity signal, and a clause that keyed on it
    would invalidate every draw."""
    src = MODULE_PATH.read_text(encoding="utf-8")
    assert "decomposition_verdict_field_is_not_a_validity_clause" in src


def test_clause7_rejects_the_wrong_checkpoint_count_and_a_shared_path():
    eight = [f"c{i}.weights.h5" for i in range(8)]
    assert fs.clause7_checkpoints(eight, {2: ["p2"], 3: ["p3"]}, 2)[0] is True
    assert fs.clause7_checkpoints(eight[:7], {2: ["p2"]}, 2)[0] is False
    assert fs.clause7_checkpoints(eight + ["extra.weights.h5"], {2: ["p2"]}, 2)[0] is False
    ok, ing = fs.clause7_checkpoints(eight, {2: ["shared"], 3: ["shared"]}, 2)
    assert ok is False and ing["paths_shared_with_another_draw"] == ["shared"]


GOOD_ENV = {
    "execution": {"host": "nid008264", "gpu_identity": "GPU-515c021e-...", "slurm_job_id": "56863959",
                  "slurm_array_job_id": "56863958", "slurm_array_task_id": "2",
                  "science_head_at_runtime": "683bdcca", "code_head_at_runtime": "4d96acf0"},
    "bound_digests": {"inputs_npz": "fa6b", "target_npy": fs.TARGET_SHA, "gate2_receipt": "8b85",
                      "driver": "9114", "loader": "e140", "engine": "3a20"},
}


def test_clause8_passes_on_the_real_sidecar_shape():
    assert fs.clause8_execution_environment(GOOD_ENV)[0] is True


def test_clause8_fails_on_each_missing_execution_field():
    for key in ["host", "gpu_identity", "slurm_job_id", "slurm_array_job_id",
                "slurm_array_task_id", "science_head_at_runtime", "code_head_at_runtime"]:
        env = json.loads(json.dumps(GOOD_ENV))
        del env["execution"][key]
        ok, ing = fs.clause8_execution_environment(env)
        assert ok is False and key in ing["missing_execution_fields"]


def test_clause8_fails_on_a_missing_or_wrong_bound_digest():
    env = json.loads(json.dumps(GOOD_ENV))
    del env["bound_digests"]["driver"]
    assert fs.clause8_execution_environment(env)[0] is False
    env2 = json.loads(json.dumps(GOOD_ENV))
    env2["bound_digests"]["target_npy"] = "0" * 64
    assert fs.clause8_execution_environment(env2)[0] is False


def test_clause8_fails_on_an_absent_sidecar():
    assert fs.clause8_execution_environment(None)[0] is False
    assert fs.clause8_execution_environment({})[0] is False


def test_there_are_exactly_eight_clause_functions_and_the_module_says_so():
    """Eight clauses are declared mandatory. A ninth added quietly, or a clause dropped, changes the
    rule after the fact."""
    names = sorted(n for n in dir(fs) if n.startswith("clause"))
    assert len(names) == 8, names
    assert [n.split("_")[0] for n in names] == [f"clause{i}" for i in range(1, 9)]


def test_the_module_states_the_prohibitions_and_the_non_establishments():
    src = MODULE_PATH.read_text(encoding="utf-8")
    for p in ["do_not_select_passing_subset", "do_not_construct_C_ML", "do_not_move_central",
              "do_not_start_leg_2", "do_not_retry_unchanged"]:
        assert p in src
    assert "gate6_unblocked_by_any_outcome" in src
    assert "re-verdict any Gate-6 member" in src


# --------------------------------------------------------------------------------------------------
# STATED GAPS -- named here rather than left to be discovered.
#
#   1. `collect_draw` and `main` are NOT executed by this battery. They need numpy, real `.npz`
#      artifacts and the cluster directory layout, and the 10 MB member-1 npz is not fetchable off
#      the cluster. Everything the RULE turns on is a pure function above and is executed; the IO
#      wrapper is covered only by running it on the cluster against the real draws.
#   2. Clause 2 parses stdout because the driver writes no separate provenance receipt. If the
#      driver's print format changes, this battery still passes and the clause starts failing
#      closed on real draws -- the safe direction, but it is a coupling to a log format.
#   3. The three interior committed member values are placeholders here. Only max and min affect the
#      frozen threshold, and those two are asserted against the predeclaration text; a wrong
#      interior value would not be caught, and does not matter for the threshold.
#   4. No test asserts what the FINAL verdict should be, deliberately: draws 4 and 5 do not exist
#      yet, and writing an expected verdict now is exactly the after-the-fact rule change the
#      predeclaration exists to prevent.
# --------------------------------------------------------------------------------------------------
