"""The lock audit's verdicts and the FINAL gate, in both directions (review round 2, findings 1-2).

Standard library + pytest only; no TensorFlow, no cluster. Each defect the reviewer constructed must
be caught, and a well-formed run must stay CLEAN.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import analyze_confirm as ac  # noqa: E402
import audit_locks as al  # noqa: E402

K = 10


def make_run(root: Path, name: str = "final-X-F0", *, segments=((0, 4, "101"), (5, 9, "102")),
             done: int = K - 1, status: str = "COMPLETE", fits=None, logs=("101", "102")) -> Path:
    run = root / name
    run.mkdir(parents=True)
    segs = [{"job": j, "first_iteration": a, "last_iteration": b} for a, b, j in segments]
    (run / "state.json").write_text(json.dumps({"completed_iteration": done, "segments": segs}))
    (run / "receipt.json").write_text(json.dumps({"config": {"iterations": K}, "segments": segs}))
    (run / "status.txt").write_text(status + "\n")
    if fits is None:
        fits = [(i, s) for i in range(done + 1) for s in (1, 2)]
    (run / "fits.jsonl").write_text("".join(json.dumps({"iteration": i, "step": s}) + "\n"
                                            for i, s in fits))
    for j in logs:
        (run / f"run-{j}.log").write_text("x")
    return run


def intervals(*jobs: str) -> dict:
    """Disjoint scheduler intervals (job n runs [1000 n, 1000 n + 10])."""
    return {j: (1000.0 * n, 1000.0 * n + 10) for n, j in enumerate(jobs, 1)}


def audit(run: Path, iv: dict) -> dict:
    # a driver's interval ends at its run log's last write: stamp each log inside its job
    for j, (start, _) in iv.items():
        log = run / f"run-{j}.log"
        if log.exists():
            os.utime(log, (start + 5, start + 5))
    return al.audit_run(run, iv)


def test_well_formed_complete_run_is_clean(tmp_path):
    run = make_run(tmp_path)
    r = audit(run, intervals("101", "102"))
    assert r["verdict"] == "clean", r


def test_complete_run_stopping_at_iteration_7_is_suspect(tmp_path):
    run = make_run(tmp_path, segments=((0, 4, "101"), (5, 7, "102")), done=7)
    assert audit(run, intervals("101", "102"))["verdict"] == "suspect"


def test_missing_final_fit_is_suspect(tmp_path):
    fits = [(i, s) for i in range(K) for s in (1, 2)][:-1]
    run = make_run(tmp_path, fits=fits)
    r = audit(run, intervals("101", "102"))
    assert r["verdict"] == "suspect" and r["fit_problems"], r


def test_duplicate_fit_is_suspect(tmp_path):
    fits = [(i, s) for i in range(K) for s in (1, 2)] + [(3, 2)]
    run = make_run(tmp_path, fits=fits)
    assert audit(run, intervals("101", "102"))["verdict"] == "suspect"


def test_job_without_scheduler_interval_is_unverifiable(tmp_path):
    run = make_run(tmp_path)
    assert audit(run, intervals("101"))["verdict"] == "unverifiable"


def test_no_scheduler_intervals_at_all_is_unverifiable(tmp_path):
    run = make_run(tmp_path)
    assert audit(run, {})["verdict"] == "unverifiable"


def test_executing_job_without_segment_is_unverifiable(tmp_path):
    run = make_run(tmp_path, logs=("101", "102", "103"))
    assert audit(run, intervals("101", "102", "103"))["verdict"] == "unverifiable"


def test_unfinished_run_with_live_iteration_is_clean(tmp_path):
    fits = [(i, s) for i in range(6) for s in (1, 2)] + [(6, 1)]
    run = make_run(tmp_path, segments=((0, 5, "101"),), done=5, status="INCOMPLETE", fits=fits,
                   logs=("101",))
    assert audit(run, intervals("101"))["verdict"] == "clean"



def test_two_drivers_alive_at_once_is_suspect(tmp_path):
    run = make_run(tmp_path)
    iv = {"101": (1000.0, 1100.0), "102": (1050.0, 1200.0)}   # 102 starts before 101's driver ends
    for j, t in (("101", 1080.0), ("102", 1150.0)):
        os.utime(run / f"run-{j}.log", (t, t))
    r = al.audit_run(run, iv)
    assert r["verdict"] == "suspect" and r["overlaps"], r

# ---- the FINAL gate --------------------------------------------------------------------------

def gate_fixture(tmp_path: Path, *, verdict="clean", audit_rows=("final-A-F0", "final-A-F1"),
                 receipt_complete=True, receipt_hash="h"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    manifest = tmp_path / "final.tsv"
    manifest.write_text("# name\tconfig\tconfig_hash\n" + "".join(
        f"final-A-F{i}\tfinal/final-A-F{i}.json\th\n" for i in range(2)))
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps({"runs": {f"final/{r}": {"verdict": verdict} for r in audit_rows}}))
    rec = tmp_path / "receipts"
    rec.mkdir()
    for i in range(2):
        (rec / f"final-A-F{i}.receipt.json").write_text(
            json.dumps({"complete": receipt_complete, "config_hash": receipt_hash}))
    final = {f"final-A-F{i}": {"k3": {"R": 0.3}, f"k{ac.KSTAR}": {"R": 0.5}} for i in range(2)}
    return final, manifest, audit, rec


def test_gate_complete_when_everything_is_clean(tmp_path):
    final, manifest, audit, rec = gate_fixture(tmp_path)
    assert ac.final_gate(final, manifest, audit, rec)["complete"] is True


def test_gate_refuses_without_an_audit(tmp_path):
    final, manifest, _, rec = gate_fixture(tmp_path)
    assert ac.final_gate(final, manifest, None, rec)["complete"] is False


def test_gate_refuses_a_row_the_audit_does_not_cover(tmp_path):
    final, manifest, audit, rec = gate_fixture(tmp_path, audit_rows=("final-A-F0",))
    g = ac.final_gate(final, manifest, audit, rec)
    assert g["complete"] is False and g["unaudited"] == ["final-A-F1"]


@pytest.mark.parametrize("verdict", ["suspect", "unverifiable", None])
def test_gate_refuses_a_row_that_is_not_clean(tmp_path, verdict):
    final, manifest, audit, rec = gate_fixture(tmp_path, verdict=verdict)
    assert ac.final_gate(final, manifest, audit, rec)["complete"] is False


def test_gate_refuses_an_incomplete_or_mismatched_receipt(tmp_path):
    final, manifest, audit, rec = gate_fixture(tmp_path, receipt_complete=False)
    assert ac.final_gate(final, manifest, audit, rec)["complete"] is False
    final, manifest, audit, rec = gate_fixture(tmp_path / "b", receipt_hash="other")
    assert ac.final_gate(final, manifest, audit, rec)["complete"] is False
