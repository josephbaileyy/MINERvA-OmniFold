"""build_pilot.py: S3P score documents -> sizing contrasts (paired small - large, NI margins, U1),
seed-variant runs excluded, unpaired draws refused."""
from __future__ import annotations

import json

import numpy as np
import pytest

import build_pilot as bp
import decide as dc
from test_pfd_decide import H, doc

VAL = {"H2S1": {"E0": 0.84, "moderate": 0.60, "good": 0.80, "E3": 0.60, "E4": 0.35, "E5": 0.30},
       "L128S1": {"E0": 0.83, "moderate": 0.61, "good": 0.78, "E3": 0.62, "E4": 0.40, "E5": 0.33}}


def write(tmp, cid, rep, bump=0.0, suffix="", pseudo=None):
    v = {ep: x + 0.01 * rep + bump for ep, x in VAL[cid].items()}
    stem = f"S3P-{cid}K5-DEV{rep}"
    hist = {"eavail": {**H(v["E0"]), "injected_per_bin": [0.0] * 7, "moved_per_bin": [0.0] * 7},
            "eavail@moderate": H(v["moderate"]), "eavail@good": H(v["good"])}
    doc(tmp / f"{stem}{suffix}.design_scores.json", "D1_p0.350", rep, 5, hist)
    if suffix:   # a seed-variant run exists only for the development tilt
        return
    doc(tmp / f"{stem}-D1_m0.350.design_scores.json", "D1_m0.350", rep, 5, {"eavail": H(v["E3"])})
    doc(tmp / f"{stem}-D4c_p_up.design_scores.json", "D4c_p_up", rep, 5,
        {"eavail": H(0.0, 0.03, 0.03), "eavail_x_proton": H(v["E4"], 0.35)})
    doc(tmp / f"{stem}-D3_p0.35.design_scores.json", "D3_p0.35", rep, 5,
        {"eavail": H(0.3, 0.06), "eavail_x_q3": H(v["E5"], 0.3)})
    if pseudo is not None:   # break the event pairing of the E0 run
        p = tmp / f"{stem}.design_scores.json"
        d = json.loads(p.read_text())
        d["identity"]["pseudo_rows_sha256"] = pseudo
        p.write_text(json.dumps(d))


def run(tmp):
    out_f, out_l = tmp / "f.json", tmp / "l.json"
    bp.main(["--scores", str(tmp), "--small", "H2S1:5", "--large", "L128S1:5", "--bonferroni-m", "2",
             "--final-out", str(out_f), "--library-out", str(out_l)])
    return json.loads(out_f.read_text()), json.loads(out_l.read_text())


def test_contrasts_are_paired_differences_with_protocol_margins(tmp_path):
    for r in range(4):
        write(tmp_path, "H2S1", r)
        write(tmp_path, "L128S1", r)
        # an N2 seed-variant run of the same draw with a very different value must not enter
        write(tmp_path, "H2S1", r, bump=0.5, suffix="-s1")
    fin, lib = run(tmp_path)
    assert fin["bonferroni_m"] == 2 and fin["looks_planned"] == 2
    got = {c["id"].split(" (")[0]: c for c in fin["contrasts"] + lib["contrasts"]}
    for ep in ("E0", "moderate", "good", "E3", "E4", "E5"):
        c = got[f"6.5 {ep}"]
        assert c["margin"] == dc.NI_MARGINS[ep] and c["kind"] == "ni"
        np.testing.assert_allclose(c["values"], [VAL["H2S1"][ep] - VAL["L128S1"][ep]] * 4, atol=1e-12)
    u1 = got["U1 H2S1"]
    assert u1["margin"] == dc.PROTOCOL_U1_FLOOR and u1["kind"] == "level"
    np.testing.assert_allclose(u1["values"], [0.84 + 0.01 * r for r in range(4)], atol=1e-12)
    assert {c["id"].split(" (")[0] for c in lib["contrasts"]} == {"6.5 E4", "6.5 E5"}


def test_unpaired_draws_are_refused(tmp_path):
    for r in range(3):
        write(tmp_path, "H2S1", r)
        write(tmp_path, "L128S1", r, pseudo="other" if r == 1 else None)
    with pytest.raises(ValueError, match="not event-paired"):
        run(tmp_path)


def test_missing_candidate_is_refused(tmp_path):
    for r in range(2):
        write(tmp_path, "H2S1", r)
    with pytest.raises(SystemExit, match="no S3P runs for L128S1"):
        run(tmp_path)
