"""Apply dev/FINALIST_RULE-20260926.md mechanically to a DEV_TABLES json (dev/summarize_dev.py).

Screens: S-U1 development tilt >= 0.60, S-U3 D1 -0.35 >= 0.50, S-U4 D4c topology >= 0.25,
S-B2 D4d E_avail residual <= 0.021; K* = the smallest passing k whose development-tilt recovery is
within 0.02 of the best passing k. A k with any screen missing, or measured on fewer than the
manifests' 2 event draws (Amendment 2: the slot is frozen on complete evidence), is `incomplete`.

Addendum of 2026-09-26 (FINALIST_RULE-20260926.md, "Addendum"): the S-N1 stability screen at K*
only (the frozen section-6.3 N1 thresholds on the development runs' post-hoc weight tails), and the
between-design step of the rule (package membership; highest development tilt at K*; ties within
0.02 broken by the lower D4d residual, then the lower per-unfolding cost; the fewest-failed-screens
fallback; the challenger condition, reported).

    python apply_finalist_rule.py DEV_TABLES.json SCREENS.json [--cost COST.json]
"""
from __future__ import annotations

import argparse
import json
import math
import sys

SCREENS = {"S-U1": ("dev tilt R (F reps)", ">=", 0.60), "S-U3": ("D1 -0.35 R", ">=", 0.50),
           "S-U4": ("D4c topo (E x p) R", ">=", 0.25), "S-B2": ("D4d E_avail res L1", "<=", 0.021)}
KS = (2, 3, 4, 5, 6)
MIN_DRAWS = 2                  # every development manifest runs 2 event draws per case
STABILITY = "stability (screen-case runs; ESS/p99.9 over F reps)"
# S-N1 (addendum): section 6.3 N1's frozen thresholds on the post-hoc tails at k = K*
N1 = {"max_push": ("<=", 100.0), "max_pull": ("<=", 100.0), "max_frac_nonpositive": ("<=", 0.0),
      "median_push_ess_over_n_F": (">=", 0.20), "median_push_p999_F": ("<=", 10.0)}
TIE = 0.02
# iterations each development design was run for (configs/<stage>/*.json `iterations`): k beyond a
# design's run length is not evidence and not incompleteness ("k in {2..6} or its run length")
RUN_LENGTH = {"H1": 6, "H2": 6, "H2S1": 6, "CS1": 6, "L64H2": 4, "L128H2": 4, "L128H2E16": 4,
              "L64S1": 5, "L128S1": 5, "H2S1E16": 5, "L128S1E16": 5, "P2preS1": 5, "P2scrS1": 5,
              "P2preA1": 5, "P2scrA1": 5}
COMPACT = ("H1", "H2", "H2S1", "CS1", "H2S1E16")          # our PET, 47,041-parameter step 1
LARGE_PREFIXES = ("L64", "L128", "P2pre", "P2scr")          # enlarged step 1 or PET2
# (detector representation, truth step) for the challenger condition
TOK, SUM, P2 = "C tokens", "C tokens + reco summaries", "PET2 native 33 tokens"
ATTR = {"H1": (TOK, "PDG one-hot, annealed"), "CS1": (TOK, "raw PDG, constant"),
        "H2": (SUM, "PDG one-hot, annealed"), "H2S1": (SUM, "PDG one-hot, constant"),
        "H2S1E16": (SUM, "PDG one-hot, constant"), "L64H2": (SUM, "PDG one-hot, annealed"),
        "L128H2": (SUM, "PDG one-hot, annealed"), "L128H2E16": (SUM, "PDG one-hot, annealed"),
        "L64S1": (SUM, "PDG one-hot, constant"), "L128S1": (SUM, "PDG one-hot, constant"),
        "L128S1E16": (SUM, "PDG one-hot, constant"), "P2preS1": (P2, "PDG one-hot, constant"),
        "P2scrS1": (P2, "PDG one-hot, constant"), "P2preA1": (P2, "PDG one-hot, constant"),
        "P2scrA1": (P2, "PDG one-hot, constant")}


def _ok(v, op, th) -> bool:
    return v is not None and not math.isnan(v) and (v >= th if op == ">=" else v <= th)


def s_n1(tab: dict, c: str, k: int) -> dict:
    cell = tab.get(STABILITY, {}).get(c, {}).get(str(k), {})
    if not cell or cell.get("n", 0) == 0 or not cell.get("n_F"):
        return {"status": "incomplete", "values": cell}
    fails = [q for q, (op, th) in N1.items() if not _ok(cell.get(q), op, th)]
    return {"status": "fail" if fails else "PASS", "failed": fails,
            "values": {q: cell.get(q) for q in N1}}


def apply(tab: dict) -> dict:
    cands = sorted({c for lab, _, _ in SCREENS.values() for c in tab.get(lab, {})})
    out = {}
    for c in cands:
        rows = []
        for k in KS:
            if k > RUN_LENGTH.get(c, max(KS)):
                continue
            vals = {}
            for s, (lab, _, _) in SCREENS.items():
                cell = tab.get(lab, {}).get(c, {}).get(str(k), {})
                vals[s] = (cell.get("mean"), cell.get("n", 0))
            if any(v[0] is None or v[1] < MIN_DRAWS for v in vals.values()):
                rows.append({"k": k, "status": "incomplete", "values": vals})
                continue
            ok = all((vals[s][0] >= th) if op == ">=" else (vals[s][0] <= th)
                     for s, (_, op, th) in SCREENS.items())
            nfail = sum(not ((vals[s][0] >= th) if op == ">=" else (vals[s][0] <= th))
                        for s, (_, op, th) in SCREENS.items())
            rows.append({"k": k, "status": "PASS" if ok else "fail", "values": vals,
                         "n_failed": nfail})
        passing = {r["k"]: r["values"]["S-U1"][0] for r in rows if r["status"] == "PASS"}
        kstar = None
        if passing:
            best = max(passing.values())
            kstar = min(k for k, u in passing.items() if u >= best - TIE)
        n1 = s_n1(tab, c, kstar) if kstar is not None else None
        out[c] = {"rows": rows, "Kstar": kstar, "dev_tilt_at_Kstar": passing.get(kstar),
                  "S-N1_at_Kstar": n1,
                  "passes_all_at_Kstar": kstar is not None and n1["status"] == "PASS",
                  "D4d_at_Kstar": (next(r["values"]["S-B2"][0] for r in rows if r["k"] == kstar)
                                   if kstar is not None else None)}
    return out


# development arms without the full screen manifest (no D1 -0.35 / D4d rows) are not candidates
NOT_SCREENED = {"L128H2E16": "learning-curve arm (2 runs: F0, T0-D4c; no D1 -0.35 / D4d rows); "
                             "the 16-epoch large candidate is L128S1E16 (stage dev2T)"}


def package(c: str) -> str | None:
    if c in NOT_SCREENED:
        return None
    if c in COMPACT:
        return "compact"
    if c.startswith(LARGE_PREFIXES):
        return "large"
    return None


def choose(res: dict, pkg: str, cost: dict | None) -> dict:
    """The rule's between-design step for one package."""
    members = {c: r for c, r in res.items() if package(c) == pkg}
    passing = {c: r for c, r in members.items() if r["passes_all_at_Kstar"]}
    incomplete = sorted(c for c, r in members.items()
                        if any(x["status"] == "incomplete" for x in r["rows"])
                        or (r["S-N1_at_Kstar"] or {}).get("status") == "incomplete")
    if incomplete:
        return {"package": pkg, "finalist": None, "status": "incomplete evidence (Amendment 2)",
                "incomplete_members": incomplete, "passing_so_far": sorted(passing)}
    if passing:
        best = max(r["dev_tilt_at_Kstar"] for r in passing.values())
        tied = sorted(c for c, r in passing.items() if r["dev_tilt_at_Kstar"] >= best - TIE)
        steps = [f"highest development tilt {best:.4f}; within {TIE}: {tied}"]
        if len(tied) > 1:
            d4d = {c: passing[c]["D4d_at_Kstar"] for c in tied}
            low = min(d4d.values())
            tied = sorted(c for c in tied if d4d[c] == low)
            steps.append(f"lower D4d residual {d4d} -> {tied}")
        if len(tied) > 1:
            if not cost or any(c not in cost for c in tied):
                return {"package": pkg, "finalist": None, "status": "needs cost", "tied": tied,
                        "steps": steps, "incomplete_members": incomplete}
            low = min(cost[c] for c in tied)
            tied = sorted(c for c in tied if cost[c] == low)
            steps.append(f"lower per-unfolding cost -> {tied}")
        f = tied[0]
        return {"package": pkg, "finalist": f, "K": passing[f]["Kstar"], "status": "chosen",
                "steps": steps, "passing": sorted(passing), "incomplete_members": incomplete}
    # fallback: the design failing the fewest screens (failure carried into eligibility)
    cand = []
    for c, r in members.items():
        for x in r["rows"]:
            if x["status"] == "fail":
                cand.append((x["n_failed"], -x["values"]["S-U1"][0], c, x["k"]))
    for c, r in members.items():      # four screens pass at K* but S-N1 fails: one failed screen
        if r["Kstar"] is not None and not r["passes_all_at_Kstar"]:
            cand.append((1, -r["dev_tilt_at_Kstar"], c, r["Kstar"]))
    if not cand:
        return {"package": pkg, "finalist": None, "status": "closed or incomplete",
                "incomplete_members": incomplete}
    n, _, c, k = min(cand)
    return {"package": pkg, "finalist": c, "K": k, "status": f"fallback: fails {n} screen(s)",
            "incomplete_members": incomplete}


def challengers(res: dict, finalists: list[str]) -> list[str]:
    """Designs passing every screen that differ from BOTH finalists in detector representation
    or truth step (the rule's necessary condition for a third finalist; entry is not automatic)."""
    return sorted(c for c, r in res.items() if r["passes_all_at_Kstar"] and c not in finalists
                  and c in ATTR and all(ATTR[c] != ATTR.get(f) for f in finalists))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tables")
    ap.add_argument("out")
    ap.add_argument("--cost", help="JSON {candidate: A100-hours per unfolding} (tie-break only)")
    a = ap.parse_args(argv)
    res = apply(json.load(open(a.tables)))
    cost = json.load(open(a.cost)) if a.cost else None
    choice = {p: choose(res, p, cost) for p in ("compact", "large")}
    fins = [v["finalist"] for v in choice.values() if v.get("finalist")]
    doc = {"designs": res, "packages": choice, "challenger_condition_met_by": challengers(res, fins)}
    json.dump(doc, open(a.out, "w"), indent=1)
    for c, r in res.items():
        n1 = (r["S-N1_at_Kstar"] or {}).get("status")
        print(c, "K*", r["Kstar"], "dev", r["dev_tilt_at_Kstar"], "S-N1", n1,
              " ".join(f"k{x['k']}:{x['status']}" for x in r["rows"]))
    for p, v in choice.items():
        print(p, "->", v.get("finalist"), "K", v.get("K"), v["status"], v.get("steps", ""))
    print("challenger condition met by:", doc["challenger_condition_met_by"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
