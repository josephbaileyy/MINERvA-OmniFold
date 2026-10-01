"""s5p recompute lane: missing-experiment sensitivity of the joint decisions (report side, read-only).

NOT part of the reviewed evaluator or comparer (reviewed commit ``0142a228``); it changes no primary output, rule or
label and gates nothing. It reads the recompute's ``recompute.json`` and the seed disposition
``seed-disposition.json`` (``s5p_recompute_seed_disposition.py``) and bounds every claim p-value and the Holm family
over the experiments that were submitted and are missing. The Holm-with-determinacy procedure and the Clopper-Pearson
interval are IMPORTED from the reviewed ``s5p_recompute`` (95% level, ``CP_LEVEL``; the 99.5% look interval of the
stopping rule is not used here), never re-implemented.

Model. A null with retained count k and size B, and L missing experiments of the bounded population: each variant's
count can rise by 0..L, so the claim count k' (the largest over the frozen variants) lies in [k, k + L] at size
B' = B + L. Worst p (k + L + 1) / (B + L + 1); best p (k + 1) / (B + L + 1).

Populations (per null; the same L for both tests):

* ``a_interrupted``: interrupted seeds (the outcome-suspect class) plus every not-established seed;
* ``b_all_lost``: every submitted-and-missing seed plus every not-established seed.

Not-established seeds (not yet run, no log without a scheduler state, unaccounted) are counted as lost in both: fail
closed. Not-submitted seeds (no meter admission, e.g. a budget-refused batch) are excluded: amendment 7 makes p valid
at the B reached, and they are not draws of the ensemble.

Certificate (group separation, step-aware). With R the primary rejections, every rejection in R holds under EVERY
assignment of the missing experiments if
(i) max over R of the worst p < min over the tests outside R of the best p, so that R occupies the first |R| Holm steps
    in some order; and
(ii) for each i in R, its worst 95% CP upper end < alpha / (m - s_min(i)). Here s_min(i) is the number of other R
    tests whose worst p is strictly below i's best p: they always precede it, so its step is at least s_min(i). Its
    upper end never exceeds the worst one, and every earlier step is an R test that is also rejected.
The simpler condition "every R test's worst upper end < alpha / m" (s_min = 0 for all) is also sufficient and is
reported as ``simple_alpha_over_m``. It is stricter: it fails even with no missing experiment once a rejection is
made at a later Holm step with a larger threshold. Holm with determinacy is NOT monotone in k, so without the
certificate the corner and one-at-a-time runs below are reported as "not proven extremal" and nothing is concluded
from them.

Power. The missing power experiments bound each count c over n present as [c / (n + L), (c + L) / (n + L)]. The
effect of missing NULL experiments on power is not bounded here (it needs each alternative's count).

Exit: 0 written and complete; 3 written but INCOMPLETE (a terminal or coherence condition failed, listed in
``incomplete``); 2 an input is missing or unreadable.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

NOT_ESTABLISHED = ("submitted_task_not_yet_run", "submitted_task_no_log_unverified", "submitted_unaccounted")
TOL = 1e-12


def _R():
    import s5p_recompute  # the reviewed module, deployed beside this file
    return s5p_recompute


def null_losses(disp_null: dict) -> dict:
    c = disp_null.get("counts", {})
    unknown = sum(c.get(k, 0) for k in NOT_ESTABLISHED)
    return {"interrupted": c.get("submitted_interrupted", 0), "lost_work": disp_null.get("lost_work", 0),
            "not_established": unknown, "not_submitted": disp_null.get("not_submitted", 0),
            "L": {"a_interrupted": c.get("submitted_interrupted", 0) + unknown,
                  "b_all_lost": disp_null.get("lost_work", 0) + unknown}}


def bound(k: int, B: int, L: int) -> dict:
    R = _R()
    if B == 0:  # not calibrated (A9): p = 1 stays; no draw exists to bound
        return {"worst": {"k": 0, "B": 0, "p": 1.0}, "best": {"k": 0, "B": 0, "p": 1.0}}
    Bp = B + L
    out = {}
    for name, kk in (("worst", k + L), ("best", k)):
        lo, hi = R.cp_interval(kk, Bp, R.CP_LEVEL)
        out[name] = {"k": kk, "B": Bp, "p": (kk + 1) / (Bp + 1), "interval": [lo, hi]}
    return out


def coherence(rec: dict, alpha: float) -> list[str]:
    """The quantities bounded are the recompute's own: claim = largest variant count; p = (k + 1) / (B + 1); the
    family decisions reproduce from the entries."""
    R, bad, entries = _R(), [], []
    for key, n in rec["nulls"].items():
        for t in R.TESTS:
            tr = n["tests"][t]
            if tr.get("not_calibrated"):
                entries.append({"test": f"{key}:{t}", "p": tr["p"], "k": tr["k"], "B": tr["B"]})
                continue
            ks = [v["k"] for v in tr["variants"].values()]
            if tr["k"] != max(ks):
                bad.append(f"{key}:{t} claim k {tr['k']} != max variant k {max(ks)}")
            if abs(tr["p"] - (tr["k"] + 1) / (tr["B"] + 1)) > TOL:
                bad.append(f"{key}:{t} p != (k + 1) / (B + 1)")
            if tr["B"] != n["B"]:
                bad.append(f"{key}:{t} B {tr['B']} != null B {n['B']}")
            entries.append({"test": f"{key}:{t}", "p": tr["p"], "k": tr["k"], "B": tr["B"]})
    again = [d["decision"] for d in R.holm_determined(entries, alpha)]
    if again != [d["decision"] for d in rec["family"]["decisions"]]:
        bad.append("family decisions do not reproduce from the claim entries")
    return bad


def certify(tests: list[str], per: dict, rejected: list[str], alpha: float) -> dict:
    """The group-separation certificate (module docstring) over a family of ``tests`` with bounds ``per``."""
    if not rejected:
        return {"holds": None, "note": "no primary rejection: nothing to certify"}
    m = len(tests)
    outside = [t for t in tests if t not in rejected]
    max_worst_R = max(per[t]["worst"]["p"] for t in rejected)
    min_best_out = min((per[t]["best"]["p"] for t in outside), default=float("inf"))
    sep = max_worst_R < min_best_out
    steps = {}
    for t in rejected:
        s_min = sum(1 for j in rejected if j != t and per[j]["worst"]["p"] < per[t]["best"]["p"])
        thr = alpha / (m - s_min)
        steps[t] = {"s_min": s_min, "threshold": thr, "worst_upper": per[t]["worst"]["interval"][1],
                    "ok": per[t]["worst"]["interval"][1] < thr}
    simple = all(per[t]["worst"]["interval"][1] < alpha / m for t in rejected)
    return {"separation": sep, "max_worst_p_R": max_worst_R, "min_best_p_outside": min_best_out,
            "per_rejection": steps, "step_aware": all(v["ok"] for v in steps.values()),
            "simple_alpha_over_m": sep and simple, "alpha_over_m": alpha / m,
            "holds": sep and all(v["ok"] for v in steps.values())}


def family_runs(entries: list[dict], per: dict, alpha: float) -> dict:
    """Holm at the corners and one test at a time (labelled: not proven extremal)."""
    R = _R()
    pick = lambda which: [dict(e, **{x: per[e["test"]][which][x] for x in ("k", "B", "p")}) for e in entries]  # noqa
    runs = {"all_worst": pick("worst"), "all_best": pick("best")}
    for e in entries:
        runs[f"worst_only:{e['test']}"] = [dict(x, **{y: per[x["test"]]["worst" if x["test"] == e["test"] else "best"][y]
                                                     for y in ("k", "B", "p")}) for x in entries]
        runs[f"best_only:{e['test']}"] = [dict(x, **{y: per[x["test"]]["best" if x["test"] == e["test"] else "worst"][y]
                                                    for y in ("k", "B", "p")}) for x in entries]
    return {name: {d["test"]: d["decision"] for d in R.holm_determined(ents, alpha)} for name, ents in runs.items()}


def evaluate_bounds(rec: dict, disp: dict) -> dict:
    R = _R()
    alpha = float(rec["alpha_family"])
    incomplete = []
    for key, n in rec["nulls"].items():
        cal = n.get("calibration", {})
        if not cal.get("final_status_present"):
            incomplete.append(f"{key}: no final status (production not terminal)")
        if cal.get("count_matches_final_B") is not True:
            incomplete.append(f"{key}: product count does not match the final status B")
        dn = disp.get("nulls", {}).get(key)
        if dn is None:
            incomplete.append(f"{key}: no seed disposition")
        elif dn.get("recompute_missing_seeds_equal") is not True:
            incomplete.append(f"{key}: the disposition's missing seeds differ from the recompute's")
    incomplete += coherence(rec, alpha)
    losses = {k: null_losses(disp.get("nulls", {}).get(k, {})) for k in rec["nulls"]}
    for k, ls in losses.items():
        if ls["not_established"]:
            incomplete.append(f"{k}: {ls['not_established']} not-established seeds (counted as lost: fail closed)")
    entries = [{"test": f"{key}:{t}", "p": n["tests"][t]["p"], "k": n["tests"][t]["k"], "B": n["tests"][t]["B"]}
               for key, n in rec["nulls"].items() for t in R.TESTS]
    primary = {d["test"]: d["decision"] for d in rec["family"]["decisions"]}
    rejected = [e["test"] for e in entries if primary[e["test"]] == "rejected"]
    m = len(entries)
    out = {"schema": "s5p-recompute-missingness-bounds/1", "not_part_of_reviewed_code": True,
           "gates_nothing": True, "alpha_family": alpha, "m": m, "holm_level": R.CP_LEVEL,
           "primary_rejections": rejected, "losses": losses, "populations": {}, "power": {}}
    for pop in ("a_interrupted", "b_all_lost"):
        per = {e["test"]: bound(e["k"], e["B"], losses[e["test"].split(":")[0]]["L"][pop]) for e in entries}
        cert = certify([e["test"] for e in entries], per, rejected, alpha)
        runs = family_runs(entries, per, alpha)
        changed = sorted({f"{name}:{t}" for name, dec in runs.items() for t, d in dec.items() if d != primary[t]})
        out["populations"][pop] = {
            "per_test": per, "certificate": cert,
            "verdict": ("every primary rejection holds under every assignment (certified)" if cert["holds"] else
                        "no primary rejection" if cert["holds"] is None else
                        "NOT certified: see the runs (not proven extremal); route to the owner"),
            "runs_not_proven_extremal": runs, "decisions_changed_in_runs": changed}
    for sk, pw in rec.get("power", {}).items():
        dp = disp.get("power", {}).get(sk, {})
        c = dp.get("counts", {})
        unknown = sum(c.get(k, 0) for k in NOT_ESTABLISHED)
        L = dp.get("lost_work", 0) + unknown
        n = int(pw.get("n_present", 0))
        rec_p = {"n_present": n, "n_declared": pw.get("n_declared"), "lost_work": dp.get("lost_work", 0),
                 "not_established": unknown, "not_submitted": dp.get("not_submitted", 0), "L": L,
                 "admitted": dp.get("admitted", True)}
        if unknown:
            incomplete.append(f"power {sk}: {unknown} not-established seeds (counted as lost: fail closed)")
        for t in R.TESTS:
            for lvl, rules in (pw.get(t) or {}).items():
                for rule, v in rules.items():
                    cnt = int(v["count"])
                    rec_p.setdefault(t, {}).setdefault(lvl, {})[rule] = {
                        "count": cnt, "power": v["power"],
                        "bounds": [cnt / (n + L), (cnt + L) / (n + L)] if n + L else None}
        rec_p["null_missingness_effect"] = "not bounded here (needs each alternative's count)"
        out["power"][sk] = rec_p
    out["incomplete"] = incomplete
    out["status"] = "INCOMPLETE" if incomplete else "complete"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--recompute", required=True)
    ap.add_argument("--disposition", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        rec, disp = json.load(open(a.recompute)), json.load(open(a.disposition))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    out = evaluate_bounds(rec, disp)
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for pop, r in out["populations"].items():
        print(f"{pop}: {r['verdict']}; decisions changed in runs: {len(r['decisions_changed_in_runs'])}")
    print(f"status {out['status']}" + "".join(f"\n  - {x}" for x in out["incomplete"]))
    return 3 if out["incomplete"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
