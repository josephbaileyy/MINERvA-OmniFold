"""Side-by-side: this lane's crosscheck.json vs the campaign's frozen-s.json (agreed frozen-S definitions)."""
import json, collections, sys
# usage: <campaign frozen-s.json> <this lane crosscheck.json> <out.json>
c = json.load(open(sys.argv[1])); m = json.load(open(sys.argv[2]))
VN = lambda n: {"0.0": "c=0", "0.5": "c=0.5", "1.0": "c=1"}.get(n, n.replace("m1", "m1="))
res = collections.defaultdict(lambda: [0, []])
def chk(cls, a, b, where, tol=None):
    ok = (abs(a - b) <= tol * max(1, abs(b))) if tol is not None and a is not None and b is not None else a == b
    res[cls][0] += ok
    if not ok: res[cls][1].append((where, a, b))
for key, ct in c["tests"].items():
    mt = m["nulls"][key]
    for vn, rec in ct["per_variant"].items():
        mv = VN(vn)
        for t in ("total", "shape"):
            cr, mr = rec[t], mt["tests"][t]["per_variant"].get(mv)
            if mr is None: res["variant present"][1].append((key, vn)); continue
            chk("k_frozen", mr["k_frozen"], cr["k_frozen"], f"{key}/{vn}/{t}")
            chk("k_recovered", mr["k_recovered"], cr["k_recovered"], f"{key}/{vn}/{t}")
            chk("B_frozen", mt["B"], cr["B_frozen"], f"{key}/{vn}/{t}")
            chk("M_recovered", mt["M"], cr["M_recovered"], f"{key}/{vn}/{t}")
            chk("M_residual = 0", 0, cr["M_residual"], f"{key}/{vn}/{t}")
            chk("T_obs", mt["tests"][t]["T_obs"], cr["T_obs"], f"{key}/{t}", 1e-9)
            chk("max_recovered_T", mr["max_recovered_T"], cr["max_recovered_T"], f"{key}/{vn}/{t}", 1e-9)
    for t, fr in ct["frozen_reproduced"].items():
        chk("frozen_reproduced (k, B) vs terminal claim", [mt["tests"][t]["claims"]["claim"]["k_frozen_claim"], mt["B"]], list(fr), f"{key}/{t}")
    for t in ("total", "shape"):
        for cf, mf in (("claim", "claim"), ("robust_keep_both", "kappa3_keep_both"), ("robust_replace", "kappa3_replace")):
            cc, mc = ct["complete_set"][t][cf], mt["tests"][t]["claims"][mf]
            chk(f"complete-set claim k/B/p ({cf})", [mc["k_prime_claim"], mc["B_prime"]], [cc["k"], cc["B"]], f"{key}/{t}")
            chk(f"complete-set claim p ({cf})", mc["p_resolved"], cc["p"], f"{key}/{t}", 1e-12)
for cf, mf in (("decisions_complete_set", "decisions_resolved_claim"), ("decisions_complete_set_kappa3_replace", "decisions_resolved_kappa3_replace"),
               ("decisions_complete_set_kappa3_keep_both", "decisions_resolved_kappa3_keep_both")):
    md = {d["test"]: d for d in m["family"][mf]}
    for test, cd in c[cf].items():
        for f in ("decision", "k", "B"):
            chk(f"{cf} {f}", md[test][f], cd[f], test)
        for f in ("p", "threshold"):
            chk(f"{cf} {f}", md[test][f], cd[f], test, 1e-12)
        chk(f"{cf} interval", md[test]["interval"][1], cd["interval"][1], test, 1e-12)
for test, lab in c["labels_complete_set"].items():
    chk("labels_complete_set", m["family"]["labels_resolved"][test], lab, test)
RULE = {"unshifted": "rank_unshifted", "claim_rule": "rank_claim", "claim_rule_determined": "determined_claim"}
for sk, cp in c["power"].items():
    if sk == "levels": continue
    mp = m["power"][sk]
    chk("power n complete", mp["n_complete"], cp["complete_set"]["n"], sk); chk("power n frozen", mp["n_retained"], cp["frozen"]["n"], sk)
    chk("power M_recovered", mp["n_recovered"], cp["M_recovered"], sk)
    for which, mkey in (("complete_set", "complete_set"), ("frozen", "retained_only")):
        for t in ("total", "shape"):
            for lvl, rules in cp[which][t].items():
                for rule, v in rules.items():
                    mv = mp[mkey][t][lvl][RULE[rule]]
                    chk(f"power {which} power", mv["power"], v["power"], f"{sk}/{t}/{lvl}/{rule}", 1e-12)
                    if "interval" in v: chk(f"power {which} interval", mv["interval"][1], v["interval"][1], f"{sk}/{t}/{lvl}/{rule}", 1e-12)
total_ok = sum(v[0] for v in res.values()); total_bad = sum(len(v[1]) for v in res.values())
for k, (n, bad) in sorted(res.items()): print(f"{k:52s} agree {n:4d}  differ {len(bad)}", bad[:2] if bad else "")
print(f"TOTAL agree {total_ok}, differ {total_bad}")
json.dump({k: {"agree": v[0], "differ": v[1]} for k, v in res.items()} | {"total": {"agree": total_ok, "differ": total_bad}},
          open(sys.argv[3], "w"), indent=1, default=str)
