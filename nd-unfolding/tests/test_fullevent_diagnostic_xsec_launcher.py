#!/usr/bin/env python3
"""Static regression checks for the split-environment diagnostic continuation."""
from pathlib import Path


ND_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ND_ROOT / "pet" / "sbatch_fullevent_diagnostic_xsec_resume.sh"


def test_launcher_runs_only_root_stage_and_reuses_push():
    text = LAUNCHER.read_text()
    assert "--stage xsec" in text
    assert "--stage all" not in text
    assert "--stage push" not in text
    assert "module load tensorflow" not in text
    assert "DIAG_PUSH_JOB_ID" in text
    assert "PUSH_OUT=" in text and "${DIAG_PUSH_JOB_ID}" in text
    assert "--allow-overwrite" not in text


def test_launcher_preflights_pyroot_and_quarantine_proof():
    text = LAUNCHER.read_text()
    assert 'source "${REPO}/setup_salloc_env.sh"' in text
    assert '"$ROOT_PY" -c \'import ROOT, numpy; assert ROOT.gROOT\'' in text
    assert 'm.get("publication_gate_rejects_this") is True' in text
    assert 'm.get("publication_gate_rejects_this_on_physics_alone") is True' in text
    assert "total_sigma_cm2_per_nucleon" not in text
    assert "no numerical result reported" in text


if __name__ == "__main__":
    test_launcher_runs_only_root_stage_and_reuses_push()
    test_launcher_preflights_pyroot_and_quarantine_proof()
    print("PASS: diagnostic xsec continuation is environment-split and quarantined")
