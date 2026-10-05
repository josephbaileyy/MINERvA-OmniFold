"""build_evidence.py: declaration + scored FB runs -> decide.py evidence, with the declared draw cuts."""
from __future__ import annotations

import json

import decide as dc
import build_evidence as be
from test_pfd_decide import H, doc


def write(tmp, stage, cand, rep, case, k, hist, member=None):
    tag = "" if case == "D1_p0.350" and stage == "S4F" else f"-{case.replace('+', '_')}"
    name = f"{stage}-{cand}-FB{rep}{tag}" + (f"-b{member}" if member else "")
    doc(tmp / f"{name}.design_scores.json", case, rep, k, hist)


def test_cuts_and_decide_round_trip(tmp_path):
    f, s = tmp_path / "s4f", tmp_path / "s4s"
    f.mkdir(); s.mkdir()
    for cand, k in (("AK5", 5), ("BK4", 4)):
        for r in range(6):
            write(f, "S4F", cand, r, "D1_p0.350", k, {"eavail": {**H(0.8), "injected_per_bin": [0.0] * 7,
                                                           "moved_per_bin": [0.0] * 7}})
            write(f, "S4F", cand, r, "D1_m0.350", k, {"eavail": H(0.7)})
        for r in range(5):
            write(s, "S4S", cand, r, "D4c_p_up", k, {"eavail": H(0.0, 0.03, 0.03),
                                                     "eavail_x_proton": H(0.3, 0.35)})
            write(s, "S4S", cand, r, "null", k, {"eavail": H(0.0, 0.004, 0.006)})
        write(s, "S4S", cand, 0, "D4c_p_up", k, {"eavail": H(0.0, 0.03, 0.03)}, member=1)
    decl = {"decision_set": ["AK5", "BK4"], "anchors": [], "bonferroni_m": 2, "look": 1,
            "looks_planned": 2, "n_final": 4, "n_stress": 2, "n_required": {"D4c_p_up": 3},
            "library": ["D4c_p_up", "null"], "note": "x"}
    dp = tmp_path / "decl.json"; dp.write_text(json.dumps(decl))
    out = tmp_path / "ev.json"
    be.main(["--declaration", str(dp), "--scores", str(f), str(s), "--out", str(out)])
    ev = json.loads(out.read_text())
    a = ev["candidates"]["AK5"]
    per = {}
    for r in a["runs"]:
        d = json.loads(open(r["score"]).read()); per.setdefault(dc.canonical_case(d["case"]["case"]), set()).add(r["replicate"])
    assert per["D1_p0.350"] == {f"FB{i}" for i in range(4)}           # n_final = 4
    assert per["D4c_p_up"] == {"FB0", "FB1", "FB2"}                    # n_required 3
    assert per["null"] == {"FB0", "FB1"}                               # n_stress 2
    assert a["k"] == 5 and ev["candidates"]["BK4"]["k"] == 4
    assert all("-b" not in r["score"] for r in a["runs"])              # coverage members excluded
    assert len(ev["unused_rows"]) == 2 * (2 + 2 + 2 + 3)
    for name, d in ev["candidates"].items():                           # decide loads the evidence
        c = dc.Candidate(name, d)
        assert not c.problems and set(c.cases) == {"D1_p0.350", "D1_m0.350", "D4c_p_up", "null"}


def test_look_two_doubles_the_final_cut(tmp_path):
    f = tmp_path / "s4f"; f.mkdir()
    for r in range(10):
        write(f, "S4F", "AK5", r, "D1_p0.350", 5, {"eavail": H(0.8)})
    decl = {"decision_set": ["AK5"], "n_final": 4, "n_stress": 2, "library": []}
    dp = tmp_path / "decl.json"; dp.write_text(json.dumps(decl))
    out = tmp_path / "ev.json"
    be.main(["--declaration", str(dp), "--scores", str(f), "--look", "2", "--out", str(out)])
    assert len(json.loads(out.read_text())["candidates"]["AK5"]["runs"]) == 8
