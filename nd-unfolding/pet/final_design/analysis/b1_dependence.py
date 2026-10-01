"""B1 under within-draw dependence: a report-only interpretation of the frozen B1 verdicts (PROTOCOL-20260925
section 6.2 and Amendment 2c item 5). Nothing here changes a verdict or a decision file.

B1's unit is (case, draw) with a defined recovery on the case's natural histogram; failure = R < 0. Its frozen
bound treats the units as independent, but the cases of one draw share pseudodata and prior events. `decide.py`
reports a replicate-cluster companion (draws with any failure / draws), but its draws do not test one panel: draws
0 .. n_S-1 carry every library case, while the extra draws of the n_required cases (D4c up, D3 +0.35; draws
n_S .. N-1) carry only those two. A Bernoulli "any failure" over unequal panels is not a bound on full-library draw
failure. This tool tabulates the panel of every draw and gives the companion on the COMMON panel (the draws that
carry every declared case), with the extended-panel draws reported separately.

    python b1_dependence.py --evidence ../results/final/evidence_look1.json --out b1_dependence_look1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inference as inf  # noqa: E402
from decide import Candidate, Rules, g_natural, historical_floors  # noqa: E402


def draw_key(r: str) -> int:
    return int(str(r).removeprefix("FB"))


def analyse(rules: Rules, c: Candidate) -> dict:
    alpha = rules.alpha_for("B1")
    cases = rules.library()
    table: dict[int, dict] = {}
    for case in cases:
        for r, x in c.values(rules.lib_case(c, case), g_natural()).items():
            t = table.setdefault(draw_key(r), {"cases_scored": [], "cases_defined": [], "failed": {}})
            t["cases_scored"].append(case)
            if x is not None:
                t["cases_defined"].append(case)
                if x < 0:
                    t["failed"][case] = float(x)
    common = [d for d, t in sorted(table.items()) if set(t["cases_scored"]) == set(cases)]
    extended = [d for d in sorted(table) if d not in common]

    def companion(draws: list[int]) -> dict:
        n, f = len(draws), sum(1 for d in draws if table[d]["failed"])
        units = sum(len(table[d]["cases_defined"]) for d in draws)
        fails = sum(len(table[d]["failed"]) for d in draws)
        out = {"draws": [f"FB{d}" for d in draws], "n_draws": n, "draws_with_a_failure": f,
               "units": units, "unit_failures": fails}
        if n:
            out["cp_upper_draw_any_failure"] = inf.clopper_pearson(f, n, alpha)[1]
            out["cp_upper_if_no_draw_failed"] = inf.clopper_pearson(0, n, alpha)[1]
        return out

    com, ext = companion(common), companion(extended)
    reaches = com.get("cp_upper_if_no_draw_failed", 1.0) <= 0.10
    return {
        "frozen_B1": {k: rules.B1(c).numbers[k] for k in ("units", "failures", "cp_upper", "replicate_cluster")},
        "frozen_B1_verdict": rules.B1(c).verdict,
        "per_draw": {f"FB{d}": {"n_cases_scored": len(t["cases_scored"]), "n_cases_defined": len(t["cases_defined"]),
                                "panel": "common" if d in common else "extended (" + ", ".join(sorted(set(t["cases_scored"]))) + ")",
                                "failed": t["failed"]} for d, t in sorted(table.items())},
        "common_panel": com,
        "extended_panel": ext,
        "original_companion_limitation": "decide.py's replicate_cluster pools common-panel and extended-panel draws; "
                                         "its 'any failure' units test different panels, so its CP bound is not a "
                                         "bound on full-library draw failure (reported unchanged in the decision file)",
        "dependence_aware_le_0.10_established": False,
        "interpretation": (
            f"B1 PASSes under its frozen independence-based bound. Under within-draw dependence, a failure "
            f"probability <= 0.10 is not established: on the common panel ({com['n_draws']} draws carrying every "
            f"declared case) {com['draws_with_a_failure']} draw(s) have a failure (one-sided {1 - alpha:.3f} CP upper "
            f"{com.get('cp_upper_draw_any_failure', float('nan')):.3f}); even with no failing draw the bound would be "
            f"{com.get('cp_upper_if_no_draw_failed', float('nan')):.3f}"
            + (", so the panel cannot support the claim at any outcome" if not reaches else "")
            + ". This is an interpretation limit of the n_S = 8 library, not a regrade."),
        "alpha_one_sided": alpha,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    ev = json.loads(a.evidence.read_text())
    rules = Rules(ev, historical_floors())
    out = {"schema": "pet-final-design/b1-dependence/1", "evidence": str(a.evidence), "report_only": True,
           "candidates": {}}
    for name in ev["decision_set"]:
        c = Candidate(name, ev["candidates"][name])
        out["candidates"][name] = analyse(rules, c)
        r = out["candidates"][name]
        print(name, r["frozen_B1_verdict"], "| common panel", r["common_panel"]["draws_with_a_failure"], "/",
              r["common_panel"]["n_draws"], "draws, CP", round(r["common_panel"]["cp_upper_draw_any_failure"], 3),
              "| extended", r["extended_panel"]["draws_with_a_failure"], "/", r["extended_panel"]["n_draws"])
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
