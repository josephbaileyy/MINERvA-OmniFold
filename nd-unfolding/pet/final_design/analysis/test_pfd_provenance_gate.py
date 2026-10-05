"""Section 10 provenance gate (independent review of f27d92d0, finding 1): verified bindings, not a declaration."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(HERE))
import build_evidence as be  # noqa: E402
import decide  # noqa: E402

RUN = STUDY / "results/final/scored_fb/S4F-H2S1T24K5-FB0.design_scores.json"
LOOK1 = STUDY / "freeze/COMPLETENESS-look1.tsv"
pytestmark = pytest.mark.skipif(not RUN.exists(), reason="look-1 scores not harvested")


def test_committed_run_is_bound_and_matches_its_record():
    ok, probs = be.provenance([{"score": str(RUN)}], be.completeness_digests([LOOK1]))
    assert ok and probs == []


def test_reviewers_counterexample_is_now_incomplete(tmp_path):
    """The review's in-memory counterexample: bindings stripped, receipt still 'complete'."""
    doc = json.loads(RUN.read_text())
    doc["provenance"] = {"receipt": {"complete": True}}
    doc["identity"] = {}
    f = tmp_path / RUN.name
    f.write_text(json.dumps(doc))
    ev = json.loads((STUDY / "results/final/evidence_look1.json").read_text())
    cand = decide.Candidate("H2S1T24K5", {"k": 5, "runs": [{"score": str(f), "replicate": "FB0", "stage": "S4F"}],
                                          "provenance_complete": True})
    v = decide.Rules(ev, decide.historical_floors()).provenance(cand).as_dict()
    assert v["verdict"] == "INCOMPLETE"
    assert any("config hash" in p for p in v["numbers"]["problems"])


def test_wrong_digest_or_missing_record_is_refused(tmp_path):
    good = be.completeness_digests([LOOK1])
    bad = dict(good, **{"S4F-H2S1T24K5-FB0": "0" * 64})
    ok, probs = be.provenance([{"score": str(RUN)}], bad)
    assert not ok and "receipt digest" in probs[0]
    ok, probs = be.provenance([{"score": str(RUN)}], {})
    assert not ok and "in no completeness record" in probs[0]


def test_committed_evidence_is_bound_end_to_end():
    """Every look-1 run and seed run of both finalists binds and matches the committed record."""
    ev = json.loads((STUDY / "results/final/evidence_look1.json").read_text())
    dg = be.completeness_digests([LOOK1])
    for name in ("H2S1T24K5", "L128S1T24K4"):
        c = ev["candidates"][name]
        ok, probs = be.provenance(c["runs"] + c.get("seed_runs", []), dg)
        assert ok, probs[:3]
