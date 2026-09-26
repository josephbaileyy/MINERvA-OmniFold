"""decide.py on synthetic score documents: eligibility, INCOMPLETE, sequential looks,
non-inferiority edges, ranking and tie-break."""
from __future__ import annotations

import copy
import json

import numpy as np
import pytest
from scipy import stats

import decide as dc
import score_design as sd

N_FINAL, N_STRESS = 24, 8
LIBRARY = ["D1_p0.350", "D1_m0.350", "D4c_p_up", "D3_p0.35", "D4d_n_up",
           "R1_x1.05+D1_p0.350", "R1_x0.95+D1_p0.350"]
INJ = [-0.015, -0.014, -0.026, -0.034, -0.031, -0.016, 0.136]
Z24 = (lambda z: (z - z.mean()) / z.std(ddof=1))(np.random.default_rng(99).normal(size=N_FINAL))

BASE = {"E0": 0.70, "low_acceptance": 0.30, "moderate": 0.60, "good": 0.80, "E3": 0.60,
        "E4": 0.35, "E5": 0.35, "D4d": 0.30, "R1": 0.0}


def doc(path, case, rep, k, h, stab=None):
    c = sd.classify_case(case)
    d = {"run_name": path.stem, "case": {"case": c["case"], "natural": c["natural"]},
         "identity": {"prior_rows_sha256": f"p{rep}", "pseudo_rows_sha256": f"a{rep}"},
         "provenance": {"receipt": {"complete": True}},
         "iterations": [{"k": k, "histograms": h, "stability": stab or {
             "n_nonfinite_truth_passing": 0, "n_negative_truth_passing": 0, "push_max": 3.0,
             "push_p999": 2.5, "final_truth_weight_ess_over_n": 0.8}}]}
    path.write_text(json.dumps(d))
    return str(path)


def H(rec, inj=0.27, res=None):
    res = inj * (1 - rec) if res is None else res
    return {"recovery": rec if inj >= sd.UNDEFINED_BELOW else None, "recovery_raw": rec,
            "injected_l1": inj, "residual_l1": res}


def make_candidate(tmp, name, vals=None, sd_=0.02, k=3, cost=(1.0, 1.1, 0.9, 1.0),
                   seed_sd=0.01, coverage=True, drop_case=None, offsets=None):
    """Per-replicate endpoint value = vals[endpoint] + sd_ * Z24[rep] + offsets[endpoint][rep]."""
    vals = {**BASE, **(vals or {})}
    offsets = offsets or {}
    d = tmp / name
    d.mkdir()
    runs = []

    def v(ep, r):
        return vals[ep] + sd_ * Z24[r] + (offsets.get(ep, np.zeros(N_FINAL))[r])

    for r in range(N_FINAL):
        e0 = v("E0", r)
        h = {"eavail": {**H(e0), "injected_per_bin": INJ,
                        "moved_per_bin": [0.7 * x for x in INJ]}}
        for reg in ("low_acceptance", "moderate", "good"):
            h[f"eavail@{reg}"] = H(v(reg, r))
        runs.append({"score": doc(d / f"e0_{r}.json", "D1_p0.350", r, k, h), "replicate": f"r{r}"})
        runs.append({"score": doc(d / f"e3_{r}.json", "D1_m0.350", r, k,
                                  {"eavail": H(v("E3", r))}), "replicate": f"r{r}"})
        runs.append({"score": doc(d / f"e4_{r}.json", "D4c_p_up", r, k,
                                  {"eavail": H(0.0, 0.03, 0.03), "eavail_x_proton": H(v("E4", r), 0.35)}),
                     "replicate": f"r{r}"})
        runs.append({"score": doc(d / f"e5_{r}.json", "D3_p0.35", r, k,
                                  {"eavail": H(0.3, 0.06), "eavail_x_q3": H(v("E5", r), 0.3)}),
                     "replicate": f"r{r}"})
    for r in range(N_STRESS):
        runs.append({"score": doc(d / f"d4d_{r}.json", "D4d_n_up", r, k,
                                  {"eavail": H(0.0, 0.005, 0.008),
                                   "eavail_x_neutron": H(v("D4d", r), 0.16)}), "replicate": f"r{r}"})
        for rc, shift in (("R1_x1.05+D1_p0.350", 0.05), ("R1_x0.95+D1_p0.350", -0.05)):
            runs.append({"score": doc(d / f"{rc[:7]}_{r}.json", rc, r, k,
                                      {"eavail": H(v("E0", r) + shift + vals["R1"])}),
                         "replicate": f"r{r}"})
        runs.append({"score": doc(d / f"null_{r}.json", "null", r, k,
                                  {"eavail": H(0.0, 0.004, 0.006),
                                   "eavail_x_proton": H(0.0, 0.015, 0.02)}), "replicate": f"r{r}"})
    if drop_case:
        runs = [x for x in runs if json.loads(open(x["score"]).read())["case"]["case"] != drop_case]
    seed_runs = []
    for g in range(2):
        for s in range(4):
            x = vals["E0"] + seed_sd * [-1.5, -0.5, 0.5, 1.5][s]
            seed_runs.append({"score": doc(d / f"seed{g}{s}.json", "D1_p0.350", 100 + g, k,
                                           {"eavail": H(x)}), "replicate": f"d{g}", "seed": s})
    decl = {"k": k, "runs": runs, "seed_runs": seed_runs, "provenance_complete": True,
            "cost": {"gpu_hours_per_unfolding": list(cost), "unfoldings_per_result": 6}}
    if coverage:
        cv = {"candidate": name, "k": k, "dev_eavail": {"levels": {"0.95": {
            "per_bin_mean_half_width": [0.01] * 7}}},
              "rules": {r: {"verdict": "PASS", "rule": r} for r in ("C1", "C2", "C3", "C4", "C5")}}
        (d / "coverage.json").write_text(json.dumps(cv))
        decl["coverage"] = str(d / "coverage.json")
    return decl


def evidence(cands, decision_set=None, **kw):
    ev = {"stage": "TEST", "look": 1, "looks_planned": 2, "n_final": N_FINAL,
          "n_stress": N_STRESS, "library": LIBRARY, "candidates": cands,
          "decision_set": decision_set or list(cands)}
    ev.update(kw)
    return ev


def test_good_candidate_is_eligible_and_selected(tmp_path):
    res = dc.evaluate(evidence({"A": make_candidate(tmp_path, "A")}))
    e = res["eligibility"]["A"]
    assert e["status"] == "ELIGIBLE", (e["failed"], e["incomplete"], e["continue"])
    assert res["ranking"]["outcome"] == "SELECTED" and res["ranking"]["selected"] == "A"
    u1 = e["verdicts"]["U1"]
    x = np.array(list(u1["numbers"]["per_replicate"].values()))
    a = 0.05 / 1 / 2                                           # m = 1, two looks
    want = x.mean() - stats.t.ppf(1 - a, x.size - 1) * stats.sem(x)
    assert u1["numbers"]["t"]["lb"] == pytest.approx(want, abs=1e-13)
    assert u1["parts"][1]["threshold"] == pytest.approx(0.5559785254924289)
    assert e["verdicts"]["B2"]["numbers"]["cases_below_3F"] == ["D4d_n_up"]
    assert e["verdicts"]["B4"]["verdict"] == "PASS"
    assert e["verdicts"]["N2"]["numbers"]["pooled_within_draw_sd"] == pytest.approx(
        0.01 * np.std([-1.5, -0.5, 0.5, 1.5], ddof=1))


def test_missing_evidence_is_incomplete_never_eligible(tmp_path):
    res = dc.evaluate(evidence({"A": make_candidate(tmp_path, "A", coverage=False)}))
    e = res["eligibility"]["A"]
    assert e["status"] == "INCOMPLETE" and set(e["incomplete"]) == {"C1", "C2", "C3", "C4", "C5"}
    assert res["ranking"]["eligible"] == [] and "YET" in res["ranking"]["outcome"]
    res = dc.evaluate(evidence({"B": make_candidate(tmp_path, "B", drop_case="D4d_n_up")}))
    assert "B1" in res["eligibility"]["B"]["incomplete"]
    ev = evidence({"C": make_candidate(tmp_path, "C")})
    ev["candidates"]["C"]["provenance_complete"] = False
    assert dc.evaluate(ev)["eligibility"]["C"]["status"] == "INCOMPLETE"
    ev = evidence({"D": make_candidate(tmp_path, "D")}, library=LIBRARY[:-1])
    assert "B4" in dc.evaluate(ev)["eligibility"]["D"]["incomplete"]   # needs both R1 signs


def test_failures_make_candidate_ineligible(tmp_path):
    res = dc.evaluate(evidence({"A": make_candidate(tmp_path, "A", vals={"E0": 0.40})}))
    assert res["eligibility"]["A"]["status"] == "INELIGIBLE"
    assert "U1" in res["eligibility"]["A"]["failed"]
    res = dc.evaluate(evidence({"B": make_candidate(tmp_path, "B", vals={"E4": 0.05})}))
    assert "U4" in res["eligibility"]["B"]["failed"]
    res = dc.evaluate(evidence({"C": make_candidate(tmp_path, "C", vals={"R1": 0.12})}))
    assert "B4" in res["eligibility"]["C"]["failed"]           # |E8| = 0.17 on x1.05
    res = dc.evaluate(evidence({"D": make_candidate(tmp_path, "D", seed_sd=0.05)}))
    assert "N2" in res["eligibility"]["D"]["failed"]
    res = dc.evaluate(evidence({"E": make_candidate(tmp_path, "E", vals={"D4d": -0.2},
                                                    sd_=0.3)}))
    b1 = res["eligibility"]["E"]["verdicts"]["B1"]
    assert b1["verdict"] == "FAIL" and b1["numbers"]["failures"] > 0


def test_sequential_straddle_continues_then_fails_at_look_two(tmp_path):
    fl = 0.5559785254924289
    c = make_candidate(tmp_path, "A", vals={"E0": fl + 0.004}, sd_=0.03)
    res1 = dc.evaluate(evidence({"A": c}))
    assert res1["eligibility"]["A"]["verdicts"]["U1"]["verdict"] == "CONTINUE"
    assert res1["eligibility"]["A"]["status"] == "CONTINUE"
    prev = tmp_path / "look1.json"
    prev.write_text(json.dumps(res1))
    res2 = dc.evaluate(evidence({"A": c}, look=2, previous=str(prev)))
    assert res2["eligibility"]["A"]["verdicts"]["U1"]["verdict"] == "FAIL"
    # resolved look-1 verdicts are carried, not re-decided
    assert res2["eligibility"]["A"]["verdicts"]["U3"].get("carried_from_look") == 1


def pair(tmp_path, e0_diff_mean, e0_diff_sd, cost_small, name_small="S"):
    large = make_candidate(tmp_path, "L", cost=(4.0, 4.2, 3.8, 4.0))
    small = make_candidate(tmp_path, name_small, cost=cost_small,
                           offsets={"E0": e0_diff_mean + e0_diff_sd * Z24})
    return large, small


def lb_of(mean, sdv, a):
    return mean - stats.t.ppf(1 - a, N_FINAL - 1) * sdv / np.sqrt(N_FINAL)


def test_non_inferiority_edges(tmp_path):
    a = 0.05 / 2 / 2
    sdv = 0.004
    halfw = stats.t.ppf(1 - a, N_FINAL - 1) * sdv / np.sqrt(N_FINAL)
    # small is worse by a margin that puts LB(small - large) just above -0.02 -> 6.5 holds
    L, S = pair(tmp_path, -0.02 + halfw + 1e-4, sdv, (1.0, 1.05, 0.95, 1.0))
    res = dc.evaluate(evidence({"L": L, "S": S}))
    rk = res["ranking"]
    assert rk["leader"] == "L"
    ni = rk["non_inferiority_6.5"]["S"]
    e0 = next(p for p in ni["parts"] if " E0 " in p["label"])
    assert e0["lb"] == pytest.approx(-0.02 + 1e-4, abs=1e-9) and e0["passes"]
    assert ni["verdict"] == "PASS"
    assert rk["outcome"] == "SELECTED" and rk["selected"] == "S" and rk["by"].startswith("6.6.2")


def test_non_inferiority_fails_just_below_margin_and_on_cost(tmp_path):
    a = 0.05 / 2 / 2
    sdv = 0.004
    halfw = stats.t.ppf(1 - a, N_FINAL - 1) * sdv / np.sqrt(N_FINAL)
    L, S = pair(tmp_path, -0.02 + halfw - 1e-4, sdv, (1.0, 1.05, 0.95, 1.0))
    ni = dc.evaluate(evidence({"L": L, "S": S}))["ranking"]["non_inferiority_6.5"]["S"]
    assert ni["verdict"] in ("FAIL", "CONTINUE")
    assert not next(p for p in ni["parts"] if " E0 " in p["label"])["passes"]
    (tmp_path / "x").mkdir()
    L, S = pair(tmp_path / "x", -0.001, sdv, (3.0, 3.1, 2.9, 3.0))   # cost ratio ~1.33
    rk = dc.evaluate(evidence({"L": L, "S": S}))["ranking"]
    cost = next(p for p in rk["non_inferiority_6.5"]["S"]["parts"] if "cost" in p["label"])
    assert not cost["passes"] and rk.get("selected") != "S"


def test_materially_better_and_equivalence_tie_break(tmp_path):
    A = make_candidate(tmp_path, "A", vals={"E0": 0.75})
    B = make_candidate(tmp_path, "B", vals={"E0": 0.70})
    rk = dc.evaluate(evidence({"A": A, "B": B}))["ranking"]
    assert rk["outcome"] == "SELECTED" and rk["selected"] == "A" and rk["by"].startswith("6.6.1")
    (tmp_path / "eq").mkdir()
    C = make_candidate(tmp_path / "eq", "C", seed_sd=0.004)
    # a constant paired advantage (sd 0) is materially better, however small
    D0 = make_candidate(tmp_path / "eq", "D0", offsets={"E0": -1e-4 + 0 * Z24})
    rk = dc.evaluate(evidence({"C": C, "D0": D0}))["ranking"]
    assert rk["selected"] == "C" and rk["by"].startswith("6.6.1")
    # a noisy zero-mean difference: not materially better, equivalent within every 6.5 margin,
    # equal cost (saving < 2x) -> 6.6.3 tie-break by the smaller N2 seed sd
    D = make_candidate(tmp_path / "eq", "D", seed_sd=0.002, offsets={"E0": 0.003 * Z24})
    rk = dc.evaluate(evidence({"C": C, "D": D}))["ranking"]
    assert rk["outcome"] == "EQUIVALENT_TIE_BROKEN" and rk["selected"] == "D"
    assert rk["pairs"]["C vs D"]["materially_better"]["verdict"] != "PASS"
    assert rk["pairs"]["C vs D"]["equivalent"]["verdict"] == "PASS"


def test_unpaired_replicates_are_refused(tmp_path):
    A = make_candidate(tmp_path, "A")
    B = make_candidate(tmp_path, "B", vals={"E0": 0.75})
    for run in B["runs"]:
        d = json.loads(open(run["score"]).read())
        d["identity"]["pseudo_rows_sha256"] = "other"
        open(run["score"], "w").write(json.dumps(d))
    with pytest.raises(ValueError, match="event-paired"):
        dc.evaluate(evidence({"A": A, "B": B}))


def test_bonferroni_m_follows_declaration(tmp_path):
    A = make_candidate(tmp_path, "A")
    res = dc.evaluate(evidence({"A": A}, bonferroni_m=4))
    assert res["alpha_one_sided_per_bound"]["sequential_rules"] == pytest.approx(0.05 / 8)
    assert res["alpha_one_sided_per_bound"]["fixed_rules"] == pytest.approx(0.05 / 4)
    b1 = res["eligibility"]["A"]["verdicts"]["B1"]["numbers"]
    assert b1["alpha_one_sided"] == pytest.approx(0.05 / 4)


def test_cli_main_writes_strict_json(tmp_path):
    ev = tmp_path / "ev.json"
    ev.write_text(json.dumps(evidence({"A": make_candidate(tmp_path, "A")})))
    out = tmp_path / "decision.json"
    assert dc.main(["--evidence", str(ev), "--out", str(out)]) == 0
    res = json.loads(out.read_text())
    assert res["eligibility"]["A"]["status"] == "ELIGIBLE"
    import sizing
    pilot = tmp_path / "pilot.json"
    pilot.write_text(json.dumps({"contrasts": [
        {"id": "U1", "values": [0.70, 0.72, 0.69, 0.71], "margin": 0.5559785255}]}))
    assert sizing.main(["--pilot", str(pilot), "--out", str(tmp_path / "s.json")]) == 0
    assert json.loads((tmp_path / "s.json").read_text())["n_F"] == 24


def test_library_development_tilt_is_keyed_apart_from_final_e0(tmp_path):
    """S4F dev and S4S D1_p0.350 share a case id; they must not collide or pool (review ec475e7b)."""
    import json as _json
    import decide as _d

    def doc(name, case):
        return {"run_name": name, "case": {"case": case, "natural": "eavail"},
                "provenance": {"receipt": {"complete": True}},
                "identity": {"prior_rows_sha256": name, "pseudo_rows_sha256": name},
                "iterations": [{"k": 5, "histograms": {"eavail": {"recovery": 0.8}}}]}
    runs = []
    for stage, n in (("S4F", 24), ("S4S", 8)):
        for r in range(n):
            f = tmp_path / f"{stage}-X-FB{r}.json"
            f.write_text(_json.dumps(doc(f"{stage}-XK5-FB{r}", "D1_p0.350")))
            runs.append({"score": str(f), "replicate": f"FB{r}"})
    c = _d.Candidate("X", {"k": 5, "runs": runs})
    assert len(c.cases[_d.E0_CASE]) == 24
    assert len(c.cases[_d.LIBRARY_E0_KEY]) == 8
    assert _d.Rules.lib_case(c, _d.E0_CASE) == _d.LIBRARY_E0_KEY
