#!/usr/bin/env python3
"""Static safety checks for the Step-1 batch-to-interactive hedge controller."""
from pathlib import Path


ND_ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ND_ROOT / "pet" / "interactive_step1_trajectory_controller.sh"


def text():
    return CONTROLLER.read_text()


def test_allocation_and_namespace_are_proven_before_cancel():
    src = text()
    cancel = src.index('scancel "$BATCH_JOB"')
    assert src.index('"JobState=RUNNING"') < cancel
    assert src.index('"Features=gpu"') < cancel
    assert src.index('"gres/gpu=1"') < cancel
    assert src.index('batch_state="$(squeue') < cancel
    assert src.index('[[ "$batch_state" != "PENDING" ]]') < cancel
    assert src.index('[[ -e "$BATCH_OUT" || -e "$BATCH_RUNLOG" ]]') < cancel
    assert 'STEP1_TRAJECTORY.slurm-${ALLOC_JOB}.json' in src
    assert 'STEP1_TRAJECTORY.slurm-${BATCH_JOB}.json' in src


def test_cancellation_is_confirmed_before_compute_and_watch_transfer():
    src = text()
    cancel = src.index('scancel "$BATCH_JOB"')
    confirm = src.index('post_acct="$(sacct', cancel)
    run = src.index('srun --overlap', confirm)
    assert cancel < confirm < run
    assert '"$post_acct" != CANCELLED*' in src
    assert 'watch-disarm' in src[confirm:run]
    assert 'step1-traj-${BATCH_JOB}' in src[confirm:run]
    assert 'write_record "$ROUTE" running' in src[confirm:run]


def test_controller_fails_closed_and_writes_terminal_receipt():
    src = text()
    assert 'flock -n 9 || fail_terminal' in src
    assert 'terminal == "true"' in src
    assert 'action "RETAIN_BATCH"' not in src  # avoid malformed positional record calls
    assert '"RETAIN_BATCH"' in src
    assert '"INTERACTIVE_COMPLETE"' in src
    assert 'schema") == "pet-fullevent-step1-trajectory-v1"' in src


if __name__ == "__main__":
    test_allocation_and_namespace_are_proven_before_cancel()
    test_cancellation_is_confirmed_before_compute_and_watch_transfer()
    test_controller_fails_closed_and_writes_terminal_receipt()
    print("PASS: Step-1 interactive hedge is cancel-after-allocation and collision-isolated")
