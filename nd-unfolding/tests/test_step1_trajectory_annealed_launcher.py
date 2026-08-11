#!/usr/bin/env python3
"""Fail-closed routing tests for the annealed trajectory launcher."""

import os
import subprocess
from pathlib import Path


ND_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ND_ROOT / "pet" / "sbatch_step1_trajectory_annealed.sh"


def test_multi_rank_step_refuses_before_tensorflow_or_output():
    env = dict(os.environ)
    env.update({
        "SLURM_JOB_ID": "fixture",
        "SLURM_STEP_NUM_TASKS": "4",
        "SLURM_NTASKS": "4",
        "SLURM_PROCID": "0",
    })
    run = subprocess.run(
        ["bash", str(LAUNCHER)],
        cwd=ND_ROOT / "pet",
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert run.returncode == 64
    assert "single-rank launcher received tasks=4 procid=0" in run.stderr
    assert "TensorFlow" not in run.stdout + run.stderr


def test_rank_guard_precedes_environment_and_output_setup():
    text = LAUNCHER.read_text()
    guard = text.index('if [[ "$STEP_TASKS" != "1"')
    assert guard < text.index('REPO="/pscratch/')
    assert guard < text.index("module load tensorflow/2.15.0")
    assert guard < text.index('mkdir -p "$LOG_DIR"')
