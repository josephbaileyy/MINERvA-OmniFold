#!/usr/bin/env python3
"""CPU-only contract checks for the authorized Gate-6 GAP 1 launcher."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DERIVER = REPO / "docs/orchestration/derive_gate6_full_inventory_proposal.py"
PROPOSAL_PATH = REPO / "docs/orchestration/state/gate6-full-inventory-proposal-20260830.json"
LAUNCHER = REPO / "nd-unfolding/pet/submit_gate6_full_inventory_members.sh"
REMAP = REPO / "nd-unfolding/pet/gate6_full_inventory_root_remap.py"

SPEC = importlib.util.spec_from_file_location("derive_gate6_full_inventory", DERIVER)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_proposal_is_exact_deterministic_render():
    proposal = json.loads(PROPOSAL_PATH.read_text(encoding="utf-8"))
    assert proposal == MODULE.build_proposal()


def test_exact_five_members_and_five_a100_hour_ceiling():
    proposal = MODULE.build_proposal()
    assert [item["member"] for item in proposal["member_artifacts"]] == [1, 2, 3, 4, 5]
    assert proposal["measurement"]["inference_rows_total"] == 245_764_425
    assert proposal["resources"]["gpu_array"] == "1-5%5"
    assert proposal["resources"]["allocated_a100_hours"] == 5.0


def test_prohibitions_and_non_publication_boundary_are_exact():
    proposal = MODULE.build_proposal()
    assert proposal["prohibitions_applied"] == {key: True for key in MODULE.PROHIBITIONS}
    assert proposal["C_ML"] is None
    assert proposal["publication_result"] is False
    assert proposal["authorization"]["no_retraining"] is True
    assert proposal["authorization"]["unchanged_retry_authorized"] is False


def test_launcher_splits_gpu_and_cpu_stages_and_has_no_training_command():
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "--array=1-5%5" in text
    assert "--time=01:00:00" in text
    assert "--dependency=\"aftercorr:${PUSH_JOB}\"" in text
    assert "--constraint='gpu&hbm80g'" in text
    assert "--constraint=cpu" in text
    assert "--stage push" in text and "--stage xsec" in text
    assert "train_fullevent_nominal.py" not in text
    assert "--allow" not in text
    assert subprocess.run(["bash", "-n", str(LAUNCHER)], check=False).returncode == 0


def test_remap_is_in_process_under_oi136_and_maps_exactly_two_insertions():
    env = os.environ.copy()
    env["G6_GAP1_CODE_ROOT"] = str(REPO)
    env["G6_GAP1_EXPECTED_HEAD"] = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    cp = subprocess.run(
        [
            os.sys.executable,
            str(REPO / "nd-unfolding/mnv_guarded_run.py"),
            "--expect-root",
            str(REPO),
            "--",
            str(REMAP),
            "--help",
        ],
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )
    assert cp.returncode == 0, cp.stderr
    assert cp.stderr.count("[gap1-root-remap]") == 2
    assert "IMPORT TREE VIOLATION" not in cp.stderr
    assert "distinct checkout roots: 1" in cp.stderr
