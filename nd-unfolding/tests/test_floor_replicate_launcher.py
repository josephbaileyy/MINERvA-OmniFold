#!/usr/bin/env python3
"""Acceptance tests for Gate 6 Leg F -- the across-process floor launcher.

WHAT AXIS THIS BATTERY COVERS, named because a battery that does not name its axis gets mistaken for
coverage it does not have (BEN-119). Three axes, and the gaps are stated at the bottom:

  1. EXECUTION of the guards that run before the hardcoded cluster paths are touched -- so they are
     tested by running them, not by reading them. This is where the member_1 protection lives.
  2. SOURCE TEXT for the pins and the policy, because the digests cannot be executed off-cluster and
     a wrong digest is the failure that costs three GPU-hours to discover.
  3. COMPILABILITY of the embedded Python, because a syntax error in a heredoc surfaces only AFTER
     training completes -- three hours in, on a job that then dies with nothing measured.
"""
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LAUNCHER = REPO / "nd-unfolding/pet/sbatch_pet_fullevent_floor_replicate_array.sh"
PREDECL = REPO / "docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md"

SRC = LAUNCHER.read_text(encoding="utf-8")

# The digests this leg binds. Every one was read off the cluster in the same turn the launcher was
# written; they are repeated here so a later edit that "tidies" one is a test failure, not a silent
# change of what the floor measures.
TARGET_SHA = "544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
INPUTS_SHA = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
DRIVER_SHA = "91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc"
LOADER_SHA = "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
ENGINE_SHA = "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
R_MEMBER1 = "1.1240802949941018"


def run_draw(draw, extra_env=None):
    """Run the launcher with DRAW_ID set, capturing everything. Returns CompletedProcess.

    The guards under test all fire before the first hardcoded /pscratch path is read, so this is a
    real execution test on a machine that has no cluster filesystem.
    """
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": "/tmp", "DRAW_ID": str(draw)}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(["bash", str(LAUNCHER)], env=env, capture_output=True, text=True)


# ---------------------------------------------------------------------------- axis 1: EXECUTION

def test_syntax_is_clean():
    assert subprocess.run(["bash", "-n", str(LAUNCHER)]).returncode == 0


@pytest.mark.parametrize("draw", [1, 0, 6, 42])
def test_refuses_draw_outside_2_to_5(draw):
    """Executed, not read. Draw 1 is the load-bearing case: member_1 must never be reopened."""
    p = run_draw(draw)
    assert p.returncode == 3, f"draw {draw} should exit 3, got {p.returncode}: {p.stderr}"
    assert "draw must be 2..5" in p.stderr


def test_refusing_draw_1_says_why_member_1_is_special():
    """The message has to name the reason, or the next person raises the bound to 1 and silently
    retrains the reference draw."""
    p = run_draw(1)
    assert "draw 1 is the existing member_1" in p.stderr
    assert "NOT retrained" in p.stderr


@pytest.mark.parametrize("draw", [2, 3, 4, 5])
def test_accepts_draws_2_through_5(draw):
    """NEGATIVE CONTROL for the range guard: it must not reject the draws it exists to admit.
    These get past the range check and then fail on the absent cluster filesystem, which is exactly
    where an off-cluster run should stop -- so the assertion is 'not exit 3 with the range message'."""
    p = run_draw(draw)
    assert not (p.returncode == 3 and "draw must be 2..5" in p.stderr), \
        f"draw {draw} was rejected by the range guard: {p.stderr}"


def test_refuses_multi_rank():
    p = run_draw(2, {"SLURM_NTASKS": "4"})
    assert p.returncode == 3
    assert "single-rank" in p.stderr


def test_single_rank_is_accepted():
    """NEGATIVE CONTROL for the rank guard."""
    p = run_draw(2, {"SLURM_NTASKS": "1"})
    assert not (p.returncode == 3 and "single-rank" in p.stderr)


# ------------------------------------------------------------------- axis 3: EMBEDDED PYTHON

def test_embedded_python_heredocs_compile():
    """A syntax error in the validity block surfaces only after training -- three GPU-hours in."""
    # The heredoc line carries a trailing `|| die ...`, so the delimiter is not end-of-line.
    blocks = re.findall(r"<<'PY'[^\n]*\n(.*?)\nPY\n", SRC, re.S)
    assert blocks, "expected at least one embedded python heredoc"
    for i, body in enumerate(blocks):
        compile(body, f"<heredoc {i}>", "exec")


def test_embedded_json_heredoc_is_validated_at_runtime():
    """The sidecar is built by shell interpolation, so it can emit invalid JSON. The launcher must
    check that itself rather than leaving a corrupt receipt behind."""
    assert "json.load(open(sys.argv[1]))" in SRC
    assert "is not valid JSON" in SRC


# ----------------------------------------------------------------------- axis 2: SOURCE TEXT

def test_policy_is_fixed_not_a_per_draw_table():
    """The whole leg is 'same policy, different process'. A case table over draws would make it the
    thing it is measuring against."""
    assert re.search(r"^EST=42$", SRC, re.M)
    assert re.search(r"^SUB=0$", SRC, re.M)
    assert "case \"$DRAW\"" not in SRC


def test_array_range_and_self_cap_are_2_to_5():
    assert "--array=2-5%2" in SRC, "the submit line must show the 2-5 range and the %2 self-cap"
    assert "#SBATCH --nice=10000" in SRC, "Gate 5 must outrank this leg at every scheduling decision"
    assert "#SBATCH --array" not in SRC, \
        "the array range belongs on the submit line, not baked in, so 1 cannot be included by default"


@pytest.mark.parametrize("sha", [TARGET_SHA, INPUTS_SHA, DRIVER_SHA, LOADER_SHA, ENGINE_SHA])
def test_bound_digests_present(sha):
    assert sha in SRC


def test_target_digest_is_the_one_the_members_consumed():
    """The canonical path was rebuilt by the Gate-5-driven Gate-2 re-run. It is byte-identical, and
    that is WHY no override is needed -- but if it ever stops being identical this pin must fail
    rather than quietly measure a floor against a different target."""
    assert TARGET_SHA in SRC
    assert "--precomputed-target-override" not in SRC, \
        "no override is used; the canonical path holds the certified bytes"


def test_validity_checks_R_and_subsample_against_member_1():
    """The two checks the predeclaration adds beyond the ensemble launcher's post-condition."""
    assert R_MEMBER1 in SRC, "R must be compared against member 1's exact value"
    assert "np.array_equal(imc, imc1)" in SRC, "the subsample must be array-equal to member 1's"
    assert "not a same-policy replicate" in SRC


def test_realized_policy_is_read_off_the_artifact_not_the_launch_command():
    assert 'z["seed_policy"].item()' in SRC
    assert "realized seeds" in SRC


def test_member_1_is_read_only():
    """member_1 may appear as a reference and must never be an output or a training target."""
    for line in SRC.splitlines():
        if "member_1" in line and "MEMBER1=" not in line and not line.strip().startswith("#"):
            assert "--out" not in line, f"member_1 must never be an --out target: {line}"
    assert re.search(r'^MEMBER1="', SRC, re.M)
    assert "$MEMBER1" not in SRC.split("--out")[1].split("\n")[0]


def test_gate5_code_root_is_never_referenced():
    """gate6traj-reconcile-56847059 is GATE5_CODE_ROOT; touching it fails 21 targets and 40
    trainings closed."""
    assert "gate6traj-reconcile-56847059" not in SRC


def test_no_allow_overwrite_and_refuses_existing_outputs():
    assert "--allow-overwrite" not in SRC
    assert "refusing to overwrite" in SRC
    assert "flock -n 9" in SRC


def test_prohibitions_are_recorded_in_the_sidecar():
    for p in ("do_not_select_passing_subset", "do_not_construct_C_ML", "do_not_move_central",
              "do_not_start_leg_2", "do_not_retry_unchanged"):
        assert p in SRC
    assert '"c_ml_construction_allowed": false' in SRC
    assert '"is_a_retry": false' in SRC


def test_execution_environment_identity_is_persisted():
    """The OI-15 residual: this is the field an across-process floor exists to expose."""
    for field in ("slurm_job_id", "slurm_array_task_id", '"host"', "gpu_identity",
                  "science_head_at_runtime", "code_head_at_runtime"):
        assert field in SRC
    assert "nvidia-smi --query-gpu=uuid" in SRC


def test_does_not_edit_the_pinned_driver():
    """The launcher exists precisely so train_fullevent_nominal.py is not touched."""
    assert "train_fullevent_nominal.py" in SRC          # it is invoked
    assert not re.search(r"(sed|patch|>|>>)\s*\S*train_fullevent_nominal\.py", SRC)


def test_predeclaration_exists_and_fixes_both_thresholds_numerically():
    """A verdict rule that is not numeric before the run is not predeclared."""
    text = PREDECL.read_text(encoding="utf-8")
    assert "F_range[2] ≤ 0.05" in text
    assert "0.1740029887300910" in text, "the process-determined threshold must be an absolute number"
    assert "FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED" in text
    assert "FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED" in text
    assert "FLOOR_INTERMEDIATE" in text


def test_predeclared_process_threshold_is_half_the_committed_member_range():
    """Recompute it rather than trust the prose -- the two must agree or one of them is wrong."""
    v_max, v_min = 1.1014828481277632, 0.7534768706675813
    assert f"{0.5 * (v_max - v_min):.16f}" == "0.1740029887300910"
    assert "0.1740029887300910" in PREDECL.read_text(encoding="utf-8")


def test_predeclaration_denies_what_this_leg_cannot_establish():
    text = PREDECL.read_text(encoding="utf-8")
    assert "does not re-verdict any Gate-6 member" in text
    assert "does not calibrate the checkpoint-tier gap" in text
    assert "does not license `C_ML`" in text


# --------------------------------------------------------------------------------- STATED GAPS
#
# NOT covered, and each is a real exposure rather than an oversight:
#
#  * The digests are asserted to be PRESENT IN THE TEXT, not to match the files -- those files are on
#    /pscratch and unreachable here. The launcher itself is the executable check, and it fails closed
#    before any GPU work. A wrong digest here fails the job in seconds, not silently.
#  * The four-stage pipeline is never executed. Mac TF 2.16/Keras 3 cannot load the vendored Keras-2
#    PET net, so any end-to-end test of it off-cluster would be a fiction.
#  * test_member_1_is_read_only is a text scan and would miss an indirection through a variable set
#    somewhere else in the file. The flock plus the refuse-to-overwrite loop are the real guards.
#  * Nothing here tests that the floor STATISTIC is computed correctly -- no such code exists yet. It
#    is written after the draws land, against the predeclared rule, and needs its own test then.
