"""apply_finalist_rule.py on synthetic development tables: completeness, K*, S-N1 at K*, the
between-design step (tilt, 0.02 tie, D4d, cost), incomplete members, fallback, challengers."""
from __future__ import annotations

import apply_finalist_rule as ar

LAB = {s: lab for s, (lab, _, _) in ar.SCREENS.items()}
GOOD_N1 = {"n": 8, "n_F": 2, "max_push": 20.0, "max_pull": 15.0, "max_frac_nonpositive": 0.0,
           "median_push_ess_over_n_F": 0.6, "median_push_p999_F": 4.0}


def table(designs: dict) -> dict:
    """designs: {cand: {k: (dev, d1, topo, d4d[, n]) }, ...}; optional '_n1': {k: overrides}."""
    tab: dict = {ar.STABILITY: {}}
    for c, spec in designs.items():
        for k in range(2, 7):
            v = spec.get(k)
            for i, s in enumerate(("S-U1", "S-U3", "S-U4", "S-B2")):
                cell = ({"mean": v[i], "n": v[4] if len(v) > 4 else 2} if v
                        else {"mean": None, "n": 0})
                tab.setdefault(LAB[s], {}).setdefault(c, {})[str(k)] = cell
            tab[ar.STABILITY].setdefault(c, {})[str(k)] = (
                {**GOOD_N1, **spec.get("_n1", {}).get(k, {})} if v else {"n": 0})
    return tab


PASS = (0.90, 0.80, 0.30, 0.015)


def run(designs, cost=None):
    res = ar.apply(table(designs))
    return res, {p: ar.choose(res, p, cost) for p in ("compact", "large")}


def test_kstar_is_smallest_passing_k_within_tie_and_single_draw_is_incomplete():
    res, _ = run({"H2S1": {2: (0.5, 0.8, 0.3, 0.01), 3: (0.89, 0.8, 0.3, 0.01),
                           4: PASS, 5: (0.95, 0.8, 0.3, 0.01, 1), 6: (0.905, 0.8, 0.3, 0.01)}})
    r = res["H2S1"]
    assert [x["status"] for x in r["rows"]] == ["fail", "PASS", "PASS", "incomplete", "PASS"]
    assert r["Kstar"] == 3                      # 0.89 is within 0.02 of the best passing 0.905


def test_s_n1_fails_at_kstar_only_and_counts_as_one_failed_screen():
    res, ch = run({"H2S1": {k: PASS for k in range(2, 7)},
                   "L128S1": {**{k: PASS for k in range(2, 6)},
                              "_n1": {2: {"max_pull": 5.5e5}}},
                   "L64S1": {k: (0.85, 0.8, 0.3, 0.015) for k in range(2, 6)}})
    assert res["L128S1"]["Kstar"] == 2 and res["L128S1"]["S-N1_at_Kstar"]["failed"] == ["max_pull"]
    assert not res["L128S1"]["passes_all_at_Kstar"]
    assert ch["large"]["finalist"] == "L64S1"   # the higher-tilt design fails S-N1 at its K*


def test_s_n1_silent_on_good_tails():
    res, _ = run({"H2S1": {k: PASS for k in range(2, 7)}})
    assert res["H2S1"]["S-N1_at_Kstar"]["status"] == "PASS"


def test_tie_broken_by_d4d_then_cost():
    d = {"L128S1": {k: (0.913, 0.8, 0.3, 0.018) for k in range(2, 6)},
         "P2preS1": {k: (0.905, 0.8, 0.3, 0.015) for k in range(2, 6)},
         "L64S1": {k: (0.85, 0.8, 0.3, 0.001) for k in range(2, 6)}}
    _, ch = run(d)
    assert ch["large"]["finalist"] == "P2preS1"   # tied within 0.02; lower D4d; L64S1 not tied
    d["P2preS1"] = {k: (0.905, 0.8, 0.3, 0.018) for k in range(2, 6)}
    _, ch = run(d)
    assert ch["large"]["status"] == "needs cost" and ch["large"]["tied"] == ["L128S1", "P2preS1"]
    _, ch = run(d, cost={"L128S1": 0.9, "P2preS1": 2.1})
    assert ch["large"]["finalist"] == "L128S1"


def test_incomplete_member_blocks_the_package():
    _, ch = run({"L128S1": {k: PASS for k in range(2, 6)},
                 "P2preS1": {2: PASS, 3: PASS, 4: (0.9, 0.8, 0.3, 0.015, 1), 5: PASS}})
    assert ch["large"]["finalist"] is None and ch["large"]["incomplete_members"] == ["P2preS1"]


def test_beyond_run_length_is_neither_evidence_nor_incompleteness():
    res, ch = run({"L64H2": {k: PASS for k in range(2, 5)}})     # run length 4
    assert [x["k"] for x in res["L64H2"]["rows"]] == [2, 3, 4]
    assert ch["large"]["finalist"] == "L64H2"


def test_fallback_fewest_failed_screens_and_unscreened_arm_excluded():
    _, ch = run({"L128S1": {k: (0.5, 0.3, 0.1, 0.05) for k in range(2, 6)},
                 "L64S1": {k: (0.9, 0.8, 0.1, 0.015) for k in range(2, 6)},
                 "L128H2E16": {k: PASS for k in range(2, 5)}})
    assert ch["large"]["finalist"] == "L64S1" and ch["large"]["status"].startswith("fallback: fails 1")


def test_challenger_condition():
    res, ch = run({"H2S1": {k: PASS for k in range(2, 7)},
                   "L128S1": {k: PASS for k in range(2, 6)},
                   "P2preS1": {k: (0.85, 0.8, 0.3, 0.015) for k in range(2, 6)},
                   "L64S1": {k: (0.85, 0.8, 0.3, 0.015) for k in range(2, 6)}})
    fins = [ch["compact"]["finalist"], ch["large"]["finalist"]]
    assert fins == ["H2S1", "L128S1"]
    assert ar.challengers(res, fins) == ["P2preS1"]   # L64S1 shares H2S1's representation/truth


def test_s_n2_gates_at_kstar_and_missing_n2_blocks_the_package():
    d = {"H2S1": {k: PASS for k in range(2, 7)}, "H2S1E16": {k: (0.85, 0.8, 0.3, 0.015)
                                                             for k in range(2, 6)}}
    tab = table(d)
    n2 = {"H2S1": {"k": 2, "pooled_within_draw_sd": 0.09},
          "H2S1E16": {"k": 2, "pooled_within_draw_sd": 0.04}}
    res = ar.apply(tab, n2, use_n2=True)
    assert res["H2S1"]["S-N2_at_Kstar"]["status"] == "fail" and not res["H2S1"]["passes_all_at_Kstar"]
    assert ar.choose(res, "compact", None)["finalist"] == "H2S1E16"
    # N2 measured at another k than K* is not evidence -> incomplete, package blocked
    res = ar.apply(tab, {**n2, "H2S1E16": {"k": 4, "pooled_within_draw_sd": 0.04}}, use_n2=True)
    ch = ar.choose(res, "compact", None)
    assert ch["finalist"] is None and "H2S1E16" in ch["incomplete_members"]
    # without --n2 the screen is off (the pre-3b rule)
    assert ar.choose(ar.apply(tab), "compact", None)["finalist"] == "H2S1"


def test_s_n2_failure_everywhere_falls_back_with_the_failure_counted():
    d = {"H2S1": {k: PASS for k in range(2, 7)}, "CS1": {k: (0.65, 0.8, 0.3, 0.015)
                                                         for k in range(2, 7)}}
    n2 = {"H2S1": {"k": 2, "pooled_within_draw_sd": 0.09},
          "CS1": {"k": 2, "pooled_within_draw_sd": 0.07}}
    ch = ar.choose(ar.apply(table(d), n2, use_n2=True), "compact", None)
    assert ch["finalist"] == "H2S1" and ch["status"].startswith("fallback: fails 1")
