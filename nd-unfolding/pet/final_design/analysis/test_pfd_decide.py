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
             "push_p999": 2.5, "final_truth_weight_ess_over_n": 0.8,
             "n_nonfinite_pull_all_rows": 0, "n_negative_pull_all_rows": 0, "pull_max": 2.0,
             "pull_min": 0.5}}]}
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
    assert res["ranking"]["eligible"] == [] and res["ranking"]["outcome"].startswith("CONTINUE")
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


def edit_stability(decl, stem, drop=(), **fields):
    """Rewrite the stability block of the candidate's run whose score file is `<stem>.json`."""
    run = next(x for x in decl["runs"] if x["score"].endswith(f"/{stem}.json"))
    d = json.loads(open(run["score"]).read())
    st = d["iterations"][0]["stability"]
    st.update(fields)
    for f in drop:
        st.pop(f)
    open(run["score"], "w").write(json.dumps(d))
    return d["run_name"]


def test_N1_reports_the_step1_pull_weights_without_gating_them(tmp_path):
    """N1 tests E9's final truth weights (protocol section 4); the step-1 pull is reported beside
    it (numbers, never a Part), and a run without the pull record reports null, not INCOMPLETE."""
    good = dc.evaluate(evidence({"A": make_candidate(tmp_path, "A")}))["eligibility"]["A"]
    n1 = good["verdicts"]["N1"]
    assert n1["verdict"] == "PASS" and n1["numbers"]["max_pull_over_runs"] == 2.0
    assert n1["numbers"]["runs_with_nonfinite_or_negative_pull"] == []
    assert n1["numbers"]["pull_note"] == dc.PULL_NOTE
    assert not any("pull" in p["label"] for p in n1["parts"])
    for name, stem, fields in (("B", "e3_5", {"n_negative_pull_all_rows": 1, "pull_min": -0.1}),
                               ("C", "null_2", {"n_nonfinite_pull_all_rows": 4}),
                               ("D", "d4d_0", {"pull_max": 1.0e6})):
        decl = make_candidate(tmp_path, name)
        run = edit_stability(decl, stem, **fields)
        v = dc.evaluate(evidence({name: decl}))["eligibility"][name]["verdicts"]["N1"]
        assert v["verdict"] == "PASS" and v["parts"] == n1["parts"], name   # verdict unchanged
        if name == "D":
            assert v["numbers"]["max_pull_over_runs"] == 1.0e6
            assert v["numbers"]["max_push_over_runs"] == 3.0
        else:
            assert v["numbers"]["runs_with_nonfinite_or_negative_pull"] == [run]
    decl = make_candidate(tmp_path, "F")
    run = edit_stability(decl, "e4_3", drop=("n_negative_pull_all_rows",))
    v = dc.evaluate(evidence({"F": decl}))["eligibility"]["F"]
    assert v["verdicts"]["N1"]["verdict"] == "PASS" and v["status"] == "ELIGIBLE"
    nums = v["verdicts"]["N1"]["numbers"]
    assert nums["runs_lacking_pull_fields"] == [run] and nums["max_pull_over_runs"] is None
    assert nums["runs_with_nonfinite_or_negative_pull"] is None


def test_N1_truth_weight_gates_still_fire(tmp_path):
    for name, stem, fields, rule in (
            ("A", "e3_5", {"n_negative_truth_passing": 1}, "all weights finite and non-negative"),
            ("B", "null_2", {"n_nonfinite_truth_passing": 2}, "all weights finite and non-negative"),
            ("C", "d4d_0", {"push_max": 150.0}, "max weight in every run")):
        decl = make_candidate(tmp_path, name)
        run = edit_stability(decl, stem, **fields)
        v = dc.evaluate(evidence({name: decl}))["eligibility"][name]["verdicts"]["N1"]
        assert v["verdict"] == "FAIL", (name, v)
        assert not next(p for p in v["parts"] if p["label"] == rule)["passes"]
        if name != "C":
            assert v["numbers"]["runs_nonfinite_or_negative"] == [run]
    decl = make_candidate(tmp_path, "D")
    for r in range(N_FINAL):                         # median ESS/n over the E0 replicates
        edit_stability(decl, f"e0_{r}", final_truth_weight_ess_over_n=0.1)
    v = dc.evaluate(evidence({"D": decl}))["eligibility"]["D"]["verdicts"]["N1"]
    assert v["verdict"] == "FAIL" and v["numbers"]["median_ess_over_n"] == 0.1


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
    assert rk["cost_order"] == ["S", "L"]
    ni = rk["pairs"][0]["non_inferior_6.5_small"]
    e0 = next(p for p in ni["parts"] if " E0 " in p["label"])
    assert e0["lb"] == pytest.approx(-0.02 + 1e-4, abs=1e-9) and e0["passes"]
    assert ni["verdict"] == "PASS"
    assert rk["outcome"] == "SELECTED" and rk["selected"] == "S" and rk["by"].startswith("6.6.2")


def test_non_inferiority_fails_just_below_margin_and_on_cost(tmp_path):
    a = 0.05 / 2 / 2
    sdv = 0.004
    halfw = stats.t.ppf(1 - a, N_FINAL - 1) * sdv / np.sqrt(N_FINAL)
    L, S = pair(tmp_path, -0.02 + halfw - 1e-4, sdv, (1.0, 1.05, 0.95, 1.0))
    ni = dc.evaluate(evidence({"L": L, "S": S}))["ranking"]["pairs"][0]["non_inferior_6.5_small"]
    assert ni["verdict"] in ("FAIL", "CONTINUE")
    assert not next(p for p in ni["parts"] if " E0 " in p["label"])["passes"]
    (tmp_path / "x").mkdir()
    L, S = pair(tmp_path / "x", -0.001, sdv, (3.0, 3.1, 2.9, 3.0))   # cost ratio ~1.33
    rk = dc.evaluate(evidence({"L": L, "S": S}))["ranking"]
    cost = next(p for p in rk["pairs"][0]["non_inferior_6.5_small"]["parts"] if "cost" in p["label"])
    # equivalent but < 2x cheaper: never a 6.5 (cost) selection; the brief's step 3 applies
    # (reproducibility tie-break, then cost) -- the large model does not win by default either
    assert not cost["passes"] and rk["by"].startswith("6.6.3")


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
    pr = rk["pairs"][0]
    assert pr["materially_better_large"]["verdict"] != "PASS"
    assert pr["materially_better_small"]["verdict"] != "PASS"
    assert pr["equivalent"]["verdict"] == "PASS"


def test_comparable_and_2x_cheaper_small_wins_over_slightly_better_large(tmp_path):
    """Item 3(c), ruled by the goal text: a smaller package that is non-inferior (6.5) and >= 2x
    cheaper is selected even when the larger one is statistically better by less than the margin;
    the larger package wins only when 6.5 fails and it is materially better."""
    L = make_candidate(tmp_path, "L", cost=(4.0, 4.2, 3.8, 4.0), vals={"E0": 0.80})
    S = make_candidate(tmp_path, "S", cost=(1.0, 1.05, 0.95, 1.0), vals={"E0": 0.79})
    rk = dc.evaluate(evidence({"L": L, "S": S}))["ranking"]
    assert rk["selected"] == "S" and rk["by"].startswith("6.6.2")
    (tmp_path / "far").mkdir()
    L2 = make_candidate(tmp_path / "far", "L", cost=(4.0, 4.2, 3.8, 4.0), vals={"E0": 0.85})
    S2 = make_candidate(tmp_path / "far", "S", cost=(1.0, 1.05, 0.95, 1.0), vals={"E0": 0.79})
    rk = dc.evaluate(evidence({"L": L2, "S": S2}))["ranking"]
    assert rk["selected"] == "L" and rk["by"].startswith("6.6.1 (larger")


def test_brief_order_cheaper_leader_still_gets_6_5(tmp_path):
    """Item 3(a): a cheaper package that also leads on mean is chosen by 6.5 (or 6.6.1), never by
    the 6.6.3 tie-break when the saving is >= 2x."""
    L = make_candidate(tmp_path, "L", cost=(4.0, 4.2, 3.8, 4.0), seed_sd=0.001)
    S = make_candidate(tmp_path, "S", cost=(1.0, 1.05, 0.95, 1.0), seed_sd=0.004,
                       offsets={"E0": 0.001 + 0.003 * Z24})
    rk = dc.evaluate(evidence({"L": L, "S": S}))["ranking"]
    assert rk["selected"] == "S" and not rk["by"].startswith("6.6.3")


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


# ------------------------------------------------------------------------------------------- #
# Section 6.6 item 3(v): a practical default for a pair unresolved at the final look
# ------------------------------------------------------------------------------------------- #
LABEL_3V = ("recommended default under the goal's burden-of-proof rule; scientific superiority "
            "and equivalence not established")


def unresolved_pair(tmp_path, l_offsets=None, s_offsets=None, l_cost=(1.5, 1.6, 1.4, 1.5),
                    s_cost=(1.0, 1.05, 0.95, 1.0)):
    """Cheaper S and costlier L (cost ratio ~1.5 < 2, so 6.5 fails on cost). The E0 difference
    S - L is -0.01 + 0.05 z: neither materially better, not equivalent (LB(S - L) < -0.02), and
    at one look (alpha 0.05/2) no E0 bound is decisive either way."""
    tmp_path.mkdir(exist_ok=True)
    L = make_candidate(tmp_path, "L", cost=l_cost, offsets=l_offsets)
    S = make_candidate(tmp_path, "S", cost=s_cost,
                       offsets={"E0": -0.01 + 0.05 * Z24, **(s_offsets or {})})
    return L, S


def test_final_look_unresolved_pair_defaults_to_the_costlier_package(tmp_path):
    L, S = unresolved_pair(tmp_path)
    rk = dc.evaluate(evidence({"L": L, "S": S}, looks_planned=1))["ranking"]
    assert rk["outcome"] == "UNRESOLVED_WITH_DEFAULT" and rk["default"] == "L"
    assert "selected" not in rk and rk["label"] == LABEL_3V and "3(v)" in rk["default_rule"]
    pr = rk["pairs"][0]
    assert pr["default"] == "L" and pr["label"] == LABEL_3V
    for v in ("materially_better_large", "materially_better_small", "equivalent",
              "non_inferior_6.5_small"):
        assert pr[v]["verdict"] == "FAIL", v
    inf_ = pr["practical_default"]["decisive_inferiority"]
    assert set(inf_) == {"E0", "moderate", "good", "E3", "E4", "E5"}
    # the recorded UB is the one-sided t bound at the 6.6.1 level on the paired difference
    x = -0.01 + 0.05 * Z24
    half = stats.t.ppf(1 - 0.05 / 2 / 1, N_FINAL - 1) * x.std(ddof=1) / np.sqrt(N_FINAL)
    assert inf_["E0"]["cheaper_minus_costlier"]["ub"] == pytest.approx(x.mean() + half, abs=1e-12)
    assert inf_["E0"]["costlier_minus_cheaper"]["ub"] == pytest.approx(-x.mean() + half, abs=1e-12)
    assert not any(r["cheaper_decisively_inferior"] or r["costlier_decisively_inferior"]
                   for r in inf_.values())


def test_default_is_the_cheaper_only_when_the_costlier_alone_is_decisively_inferior(tmp_path):
    # costlier L decisively worse on E4 (S - L = +0.08, tight), S decisively worse on nothing
    L, S = unresolved_pair(tmp_path / "a", s_offsets={"E4": 0.08 + 0.001 * Z24})
    rk = dc.evaluate(evidence({"L": L, "S": S}, looks_planned=1))["ranking"]
    assert rk["outcome"] == "UNRESOLVED_WITH_DEFAULT" and rk["default"] == "S"
    e4 = rk["pairs"][0]["practical_default"]["decisive_inferiority"]["E4"]
    assert e4["costlier_decisively_inferior"] and not e4["cheaper_decisively_inferior"]
    # both decisively inferior somewhere (L on E4, S on E5): the costlier stays the default
    L, S = unresolved_pair(tmp_path / "b", s_offsets={"E4": 0.08 + 0.001 * Z24,
                                                      "E5": -0.08 + 0.001 * Z24})
    rk = dc.evaluate(evidence({"L": L, "S": S}, looks_planned=1))["ranking"]
    assert rk["outcome"] == "UNRESOLVED_WITH_DEFAULT" and rk["default"] == "L"
    # only the cheaper decisively inferior: the costlier
    L, S = unresolved_pair(tmp_path / "c", s_offsets={"E5": -0.08 + 0.001 * Z24})
    rk = dc.evaluate(evidence({"L": L, "S": S}, looks_planned=1))["ranking"]
    assert rk["outcome"] == "UNRESOLVED_WITH_DEFAULT" and rk["default"] == "L"


def test_default_needs_the_final_look_and_both_costs(tmp_path):
    L, S = unresolved_pair(tmp_path / "a")
    rk = dc.evaluate(evidence({"L": L, "S": S}))["ranking"]          # look 1 of 2
    assert rk["outcome"] == "CONTINUE" and "default" not in rk
    assert "practical_default" not in rk["pairs"][0]
    L, S = unresolved_pair(tmp_path / "b")
    del L["cost"]
    rk = dc.evaluate(evidence({"L": L, "S": S}, looks_planned=1))["ranking"]
    assert rk["outcome"] == "UNRESOLVED" and "default" not in rk
    assert "cost" in rk["reason"]


def test_default_at_look_two_of_two_and_never_for_an_ineligible_package(tmp_path):
    L, S = unresolved_pair(tmp_path / "a")
    ev = evidence({"L": L, "S": S})
    prev = tmp_path / "look1.json"
    prev.write_text(json.dumps(dc.evaluate(ev)))
    rk = dc.evaluate({**ev, "look": 2, "previous": str(prev)})["ranking"]
    assert rk["outcome"] == "UNRESOLVED_WITH_DEFAULT" and rk["default"] == "L"
    # the pair logic is reached only by ELIGIBLE packages; handled, not assumed
    ev = evidence({"L": L, "S": S}, looks_planned=1)
    rules = dc.Rules(ev, dc.historical_floors())
    cands = {n: dc.Candidate(n, d) for n, d in ev["candidates"].items()}
    con = dc.Contrasts(rules, cands)
    d = dc._pair_decision(rules, con, cands, {"S": "ELIGIBLE", "L": "INELIGIBLE"}, "S", "L")
    assert d.get("unresolved") and "default" not in d
    assert "ELIGIBLE" in d["practical_default"]["default_not_formed"]
    d = dc._pair_decision(rules, con, cands, {"S": "ELIGIBLE", "L": "ELIGIBLE"}, "S", "L")
    assert d["default"] == "L"


def test_a_defaulted_link_makes_the_whole_ranking_a_default(tmp_path):
    """S vs L is defaulted (L); the costliest X then beats L by 6.6.1. X is the default, never
    SELECTED: S vs X was never resolved."""
    L, S = unresolved_pair(tmp_path)
    X = make_candidate(tmp_path, "X", cost=(3.0, 3.1, 2.9, 3.0), vals={"E0": 0.80})
    rk = dc.evaluate(evidence({"L": L, "S": S, "X": X}, looks_planned=1))["ranking"]
    assert rk["cost_order"] == ["S", "L", "X"]
    assert [p.get("default") or p["winner"] for p in rk["pairs"]] == ["L", "X"]
    assert rk["pairs"][1]["by"].startswith("6.6.1 (larger")
    assert rk["outcome"] == "UNRESOLVED_WITH_DEFAULT" and rk["default"] == "X"
    assert "selected" not in rk and rk["discriminating_contrasts"] == ["S vs L"]
