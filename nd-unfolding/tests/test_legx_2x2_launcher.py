#!/usr/bin/env python3
"""Acceptance tests for Gate 6 Leg X -- the `{42,46}x{0,4}` 2x2 launcher.

WHAT AXIS THIS BATTERY COVERS, named because a battery that does not name its axis gets mistaken for
coverage it does not have (BEN-119). Four axes, gaps stated at the bottom:

  1. EXECUTION of the guards that run before the hardcoded cluster paths are touched -- so they are
     tested by running them, not by reading them. The cell-range guard, the anti-diagonal guard and
     THE SEQUENCING GATE all live here. The sequencing gate is the one that matters most: "the floor
     runs first" is Joseph's standing instruction and Lane B's own argument, and this battery is what
     makes it a mechanism instead of a promise.
  2. THE SEQUENCING GATE'S REJECTION SET, exercised against real receipt shapes -- absent, partial
     (`n<5`), an invalid draw present, a non-terminal verdict, and a missing or zero `F_sd[2]`. A gate
     that only rejects the absent case is the gate that lets a partial floor through.
  3. SOURCE TEXT for the pins, the policy and the threshold, because the digests cannot be executed
     off-cluster and a wrong digest costs three GPU-hours to discover.
  4. COMPILABILITY of the embedded Python, because a syntax error in a heredoc surfaces only AFTER
     training completes -- three hours in, on a job that then dies with nothing measured.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LAUNCHER = REPO / "nd-unfolding/pet/sbatch_pet_fullevent_legx_2x2_array.sh"
PREDECL = REPO / "docs/orchestration/PREDECLARATION-20260813-gate6-legX-2x2.md"

SRC = LAUNCHER.read_text(encoding="utf-8")
PREDECL_TEXT = PREDECL.read_text(encoding="utf-8")

# Repeated here so a later edit that "tidies" one is a test failure, not a silent change to what the
# 2x2 compares. Same digests Leg F binds -- cells A and B trained under exactly these.
TARGET_SHA = "544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
INPUTS_SHA = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
DRIVER_SHA = "91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc"
LOADER_SHA = "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
ENGINE_SHA = "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
R_COMMON = "1.1240802949941018"
T_CRIT_4DF = "2.7764451051977987"


def run_cell(cell, floor_result=None):
    """Run the launcher with CELL_ID set, capturing everything. Off-cluster it dies at the first
    hardcoded path; what we assert is WHICH guard fired and in what order."""
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": str(Path.home()), "CELL_ID": str(cell)}
    if floor_result is not None:
        env["G6_LEGX_FLOOR_RESULT"] = str(floor_result)
    return subprocess.run(["bash", str(LAUNCHER)], capture_output=True, text=True, env=env, timeout=120)


def floor_receipt(tmpdir, n=5, invalid=None, verdict="FLOOR_INTERMEDIATE", sd=0.03):
    p = Path(tmpdir) / "floor.json"
    body = {
        "inventory": {"n": n, "draws_invalid": invalid or []},
        "verdict": verdict,
        "statistics": {"0": {"F_sd_ddof1": 0.3}, "1": {"F_sd_ddof1": 0.1},
                       "2": {"F_sd_ddof1": sd}},
    }
    p.write_text(json.dumps(body), encoding="utf-8")
    return p


# --------------------------------------------------------- axis 1: guards that run before any path


def test_cell_range_guard_refuses_zero_and_three():
    for bad in (0, 3, 5, 99):
        r = run_cell(bad)
        assert r.returncode == 3, f"cell {bad} should be refused, got rc={r.returncode}"
        assert "cell must be 1 or 2" in r.stderr


def test_cell_range_guard_names_why_the_diagonal_cells_are_excluded():
    """The message has to say the two existing cells are NOT retrained, or the next reader tries 3."""
    r = run_cell(3)
    assert "ALREADY EXIST" in r.stderr and "NOT retrained" in r.stderr


def test_both_real_cells_pass_the_range_guard_negative_control():
    """Without this the range test would pass on a launcher that refuses EVERY cell."""
    for good in (1, 2):
        r = run_cell(good)
        assert "cell must be 1 or 2" not in r.stderr
        assert r.returncode != 3 or "hash mismatch" in r.stderr


def test_the_anti_diagonal_guard_exists_and_is_defence_in_depth():
    """If the cell table is later mis-edited to a diagonal pair, a second independent check refuses.
    Executed via the table today; asserted in source because the table would have to be edited to
    reach it, and editing the file under test is what the mutation battery does instead."""
    assert 'is a DIAGONAL cell that already exists as a committed Gate-6 member' in SRC
    assert re.search(r'\[\[ "\$EST" == "42" && "\$SUB" == "0" \]\]', SRC)
    assert re.search(r'\[\[ "\$EST" == "46" && "\$SUB" == "4" \]\]', SRC)


def test_single_rank_is_enforced():
    assert "launcher is single-rank" in SRC
    assert 'SLURM_NTASKS:-1' in SRC


# --------------------------------------------------- axis 2: the sequencing gate's rejection set


@pytest.mark.needs_tmpdir
def test_sequencing_gate_refuses_an_absent_floor_receipt():
    with tempfile.TemporaryDirectory() as td:
        r = run_cell(1, floor_result=Path(td) / "does-not-exist.json")
        assert r.returncode == 2
        assert "THE FLOOR RUNS FIRST" in r.stderr


@pytest.mark.needs_tmpdir
def test_sequencing_gate_refuses_a_partial_floor():
    """The case that actually happened: 3 of 5 draws in, statistics present and provisional."""
    with tempfile.TemporaryDirectory() as td:
        p = floor_receipt(td, n=3, verdict="NO_VERDICT_INCOMPLETE")
        r = run_cell(1, floor_result=p)
        assert r.returncode == 2
        assert "n=3" in (r.stdout + r.stderr)


@pytest.mark.needs_tmpdir
def test_sequencing_gate_refuses_a_floor_with_an_invalid_draw():
    with tempfile.TemporaryDirectory() as td:
        p = floor_receipt(td, n=5, invalid=[4], verdict="NO_VERDICT_INVALID_DRAW")
        r = run_cell(1, floor_result=p)
        assert r.returncode == 2
        assert "invalid draws" in (r.stdout + r.stderr)


@pytest.mark.needs_tmpdir
def test_sequencing_gate_refuses_a_non_terminal_verdict_even_at_n_equals_5():
    """n=5 with no FLOOR_* verdict is the shape a premature or crashed run leaves behind."""
    with tempfile.TemporaryDirectory() as td:
        p = floor_receipt(td, n=5, verdict="PREMISE_FAILURE")
        r = run_cell(1, floor_result=p)
        assert r.returncode == 2
        assert "not a terminal FLOOR_" in (r.stdout + r.stderr)


@pytest.mark.needs_tmpdir
def test_sequencing_gate_refuses_a_missing_or_zero_sigma():
    with tempfile.TemporaryDirectory() as td:
        for sd in (0.0, None):
            p = floor_receipt(td, sd=sd)
            r = run_cell(1, floor_result=p)
            assert r.returncode == 2, f"F_sd[2]={sd!r} must be refused"
            assert "cannot be formed" in (r.stdout + r.stderr)


@pytest.mark.needs_tmpdir
def test_sequencing_gate_ACCEPTS_a_closed_floor_and_prints_the_mde():
    """The negative control. Without it every test above would pass on a gate that refuses
    everything, which is the failure mode a rejection-only battery cannot see."""
    with tempfile.TemporaryDirectory() as td:
        p = floor_receipt(td, n=5, verdict="FLOOR_INTERMEDIATE", sd=0.03)
        r = run_cell(1, floor_result=p)
        out = r.stdout + r.stderr
        assert "floor CLOSED" in out
        assert "F_sd[2]=0.03" in out
        assert "0.0832933531559" in out           # 2.7764451051977987 * 0.03, printed not asserted
        assert r.returncode != 2                   # it got past the gate; it dies later, on paths


@pytest.mark.needs_tmpdir
def test_sequencing_gate_accepts_every_terminal_floor_verdict():
    """All three predeclared verdicts supply a sigma, including the one that attributes nothing."""
    for v in ("FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED",
              "FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED", "FLOOR_INTERMEDIATE"):
        with tempfile.TemporaryDirectory() as td:
            r = run_cell(1, floor_result=floor_receipt(td, verdict=v))
            assert "floor CLOSED" in (r.stdout + r.stderr), v


def test_the_gate_runs_before_mkdir_the_writer_lock_and_the_module_load():
    """Ordering matters: a premature submission must cost seconds, not three GPU-hours, and must leave
    NOTHING behind. `mkdir` is in this chain because the first version of the launcher ran it first --
    which meant the gate never executed off-cluster at all, and a refused submission still created an
    empty cell directory. This assertion is what caught it."""
    gate = SRC.index("Leg F result receipt absent")
    mkdir = SRC.index('mkdir -p "${LEGXDIR}/logs"')
    lock = SRC.index("flock -n 9")
    module = SRC.index("module load tensorflow")
    train = SRC.index("STAGE 1/4 TRAIN")
    assert gate < mkdir < lock < module < train


def test_the_gate_warns_against_pointing_it_at_a_partial_receipt():
    """The obvious workaround is an env var, and the message names it."""
    assert "Do not work around this by pointing G6_LEGX_FLOOR_RESULT at a partial receipt" in SRC


# ------------------------------------------------------------------- axis 3: pins, policy, threshold


def test_every_bound_digest_is_the_one_cells_A_and_B_trained_under():
    for sha in (TARGET_SHA, INPUTS_SHA, DRIVER_SHA, LOADER_SHA, ENGINE_SHA):
        assert sha in SRC, sha
    assert SRC.count(ENGINE_SHA) >= 3          # science engine, code engine, sidecar record


def test_the_two_cells_are_the_off_diagonal_ones():
    assert re.search(r"1\)\s*EST=42;\s*SUB=4", SRC)
    assert re.search(r"2\)\s*EST=46;\s*SUB=0", SRC)


def test_the_existing_members_are_read_only_references():
    assert "member_1/pet_fullevent_ml_member1_weights.npz" in SRC
    assert "member_5/pet_fullevent_ml_member5_weights.npz" in SRC
    assert "cells A and B are read-only references" in SRC
    assert "output path collides with a committed Gate-6 member" in SRC


def test_gate5_code_root_is_never_referenced():
    assert "gate6traj-reconcile-56847059" not in SRC, (
        "GATE5_CODE_ROOT must not appear: it is named for a completed job so it reads as disposable, "
        "and touching it fails 21 queued targets and 40 held trainings")


def test_the_readout_restriction_and_its_reason_are_in_the_launcher_not_only_the_predeclaration():
    """The peer's requirement: a reader six months from now sees an unreplicated 2x2 and assumes
    nobody noticed. The reason has to travel with the code, not only with the document."""
    assert "READ AT ITERATION 2 ONLY" in SRC
    assert "89.6%" in SRC and "15.1%" in SRC
    assert "THE RESTRICTION IS WHAT MAKES THE" in SRC
    assert "Sure, do iteration 2." in SRC
    # The word alone is not enough: it also appears in the sidecar key, so a mutation that deleted the
    # closing notice the OPERATOR reads still passed an earlier version of this test.
    assert 'echo "[g6-legx] EFFECTS ARE READ AT ITERATION 2 ONLY.' in SRC
    assert '"iterations_0_and_1_are_computed_but_INELIGIBLE": true' in SRC
    assert SRC.count("INELIGIBLE") >= 2


def test_iterations_0_and_1_are_not_suppressed_from_the_receipt():
    """Deleting them would hide the caveat instead of stating it."""
    assert "This launcher does not filter them -- suppressing them would hide the caveat" in SRC


def test_the_prohibitions_and_the_not_a_step_toward_cml_statement_are_present():
    for p in ["do_not_select_passing_subset", "do_not_construct_C_ML", "do_not_move_central",
              "do_not_start_leg_2", "do_not_retry_unchanged"]:
        assert p in SRC, p
    assert '"c_ml_construction_allowed": false' in SRC
    assert '"is_a_step_toward_c_ml": false' in SRC
    assert "Gate 6 remains BLOCKED at 19585b7" in SRC


def test_nice_and_the_self_cap_keep_gate_5_ahead():
    assert "#SBATCH --nice=10000" in SRC
    assert "--array=1-2%1" in SRC


def test_the_threshold_multiplier_is_the_t_value_at_four_degrees_of_freedom():
    """4 df because sigma comes from Leg F's FIVE draws. A gaussian 1.96 would be optimistic and a
    round 2 unmotivated; both are the kind of number that gets chosen after seeing the data.

    EVERY occurrence is checked, not just one. A mutation replacing only the FIRST of the launcher's
    two occurrences -- the one in the failure message, leaving the arithmetic correct -- passed an
    earlier version of this test that asserted mere presence. Half-substituted constants are exactly
    the drift a receipt is supposed to make impossible."""
    from statistics import NormalDist
    assert SRC.count(T_CRIT_4DF) == 2, (
        f"expected the t(4) multiplier twice in the launcher (message + arithmetic), "
        f"found {SRC.count(T_CRIT_4DF)}")
    assert T_CRIT_4DF in PREDECL_TEXT
    assert "t_{0.975, 4}" in PREDECL_TEXT
    for wrong in (f"{NormalDist().inv_cdf(0.975)!r}", "1.959963984540054", "1.96 *", "2.0 * sd"):
        assert wrong not in SRC, f"a non-t(4) multiplier appears in the launcher: {wrong}"
    assert abs(float(T_CRIT_4DF) - NormalDist().inv_cdf(0.975)) > 0.8


def test_the_predeclaration_names_one_primary_effect_and_two_secondary():
    assert "PRIMARY quantity" in PREDECL_TEXT
    assert PREDECL_TEXT.count("SECONDARY") >= 2
    assert "Exactly one effect carries a verdict" in PREDECL_TEXT


def test_the_predeclaration_publishes_the_mde_with_a_null_result():
    """BEN-213: pre-registration is not power. A null must ship the sensitivity it had."""
    assert "ESTIMATOR_INIT_EFFECT_NOT_RESOLVED_AT_MDE" in PREDECL_TEXT
    assert "BEN-213" in PREDECL_TEXT
    assert "It is *not* \"there is no estimator-seed effect.\"" in PREDECL_TEXT


def test_the_predeclaration_denies_what_this_leg_cannot_establish():
    for phrase in ["does not license `C_ML`", "does not support any claim at iteration 0 or 1",
                   "does not calibrate the best-epoch", "with any power"]:
        assert phrase in PREDECL_TEXT, phrase


def test_the_predeclaration_admits_it_is_weaker_than_leg_f_s():
    """Two of four cells already existed when the rule was written. Saying so is the point."""
    assert "weaker than Leg F's" in PREDECL_TEXT


def test_the_subsample_axis_positive_control_is_stated_with_its_measurement():
    assert "1,999,982" in PREDECL_TEXT
    assert "not a 2x2" in SRC


# ------------------------------------------------------------------- axis 4: embedded Python compiles


def test_embedded_python_heredocs_compile():
    """The heredoc delimiter does NOT end its line here -- `<<'PY' || die ...` -- so the pattern must
    not assume it does. That assumption made this test find zero blocks in the Leg F battery."""
    blocks = re.findall(r"<<'PY'[^\n]*\n(.*?)\nPY\n", SRC, re.S)
    assert len(blocks) == 2, f"expected 2 embedded python blocks, found {len(blocks)}"
    for i, b in enumerate(blocks):
        compile(b, f"<embedded-{i}>", "exec")


def test_the_validity_block_checks_subsample_equality_BY_LEVEL_not_globally():
    """Leg F could demand equality with member 1 because every draw shared subsample_seed=0. Leg X
    cannot: half its cells are at subsample_seed=4, so a global check would reject correct cells."""
    block = re.findall(r"<<'PY'[^\n]*\n(.*?)\nPY\n", SRC, re.S)[1]
    assert "same, other = (imc_sub0, imc_sub4) if sub == 0 else (imc_sub4, imc_sub0)" in block
    assert "the subsample axis does not move and this is not a 2x2" in block
    assert "np.array_equal(imc, same)" in block and "np.array_equal(imc, other)" in block


def test_the_validity_block_requires_R_exactly():
    block = re.findall(r"<<'PY'[^\n]*\n(.*?)\nPY\n", SRC, re.S)[1]
    assert R_COMMON in block
    assert "if R != R_COMMON:" in block


def test_the_validity_block_reads_the_realized_policy_off_the_artifact():
    block = re.findall(r"<<'PY'[^\n]*\n(.*?)\nPY\n", SRC, re.S)[1]
    assert 'z["seed_policy"].item()' in block
    assert "realized seeds" in block
    for field in ("niter", "epochs", "train_events", "batch_size"):
        assert field in block


# --------------------------------------------------------------------------------------------------
# STATED GAPS -- named here rather than left to be discovered.
#
#   1. The digests are asserted PRESENT IN TEXT, not matched against files. Off-cluster the files do
#      not exist; the launcher's own sha256sum comparison is the executable check and it fails closed.
#   2. The four-stage pipeline is never executed off-cluster: Mac TF 2.16 / Keras 3 cannot load the
#      vendored Keras-2 PET net, so stages 1-4 are covered only by running them on the cluster.
#   3. The anti-diagonal guard is asserted in source, not executed, because reaching it requires
#      editing the cell table -- which is what a mutation run does instead of a test.
#   4. NO TEST ASSERTS THE EFFECT ARITHMETIC. `E_est`, `E_sub`, `E_int` and the threshold live in the
#      predeclaration; the code that computes them does not exist yet and will need its own battery,
#      including the `Var(E) = sigma^2` algebra and the free-sensitivity variant at `Var = 0.8 sigma^2`.
#   5. The read-only protection of members 1 and 5 is a path-collision check plus a text scan, not a
#      filesystem permission. A launcher edited to write elsewhere into member_1/ would pass.
# --------------------------------------------------------------------------------------------------
