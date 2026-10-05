"""UNREVIEWED diagnostic (not the verdict): compare production joint-evaluate leaves the reviewed comparer leaves
unresolved, wherever the recompute independently supplies the same quantity."""
import json, math, sys, collections
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute/nd-unfolding")
import s5p_recompute as R
j = json.load(open("joint-evaluate.json")); m = json.load(open("recompute.json")); c = json.load(open("compare.json"))
VN = {"0.0": "c=0", "0.5": "c=0.5", "1.0": "c=1", "m1+2": "m1=+2", "m1-2": "m1=-2", "m1+3": "m1=+3", "m1-3": "m1=-3"}
res = collections.defaultdict(lambda: [0, 0, []])
def cmp(cls, a, b, where, tol=1e-9):
    ok = (a == b) if isinstance(a, (str, bool)) or a is None or b is None else \
         (all(abs(x - y) <= tol * max(1, abs(y)) for x, y in zip(a, b)) and len(a) == len(b)) if isinstance(a, list) else abs(a - b) <= tol * max(1, abs(b))
    r = res[cls]; r[0 if ok else 1] += 1
    if not ok: r[2].append((where, a, b))
for key, pt in j["tests"].items():
    mn = m["nulls"][key]; B = mn["B"]
    for fam, mfield in (("variants", None), ("robustness_variants", "robust_kappa3_replace_kappa2")):
        for vname, rec in pt.get(fam, {}).items():
            for t in R.TESTS:
                if t not in rec: continue
                mt = mn["tests"][t]; src = mt if mfield is None else mt[mfield]
                v = src["variants"][VN[vname]]
                cmp("variant B", rec[t]["B"], B, f"{key}/{fam}/{vname}/{t}")
                cmp("variant CP95 interval", rec[t]["tail_interval"], list(R.cp_interval(v["k"], B, 0.95)), f"{key}/{fam}/{vname}/{t}")
                cmp("variant level", rec[t]["level"], 0.95, f"{key}/{fam}/{vname}/{t}")
            if vname == "0.0":
                for t in R.TESTS:
                    s = mn["null_T_summary"][t]
                    cmp("c=0 null T median", rec[f"null_T_{t}_median"], s["median"], f"{key}/{t}", 1e-7)
                    cmp("c=0 null T sd", rec[f"null_T_{t}_sd"], s["sd"], f"{key}/{t}", 1e-7)
    ps = mn.get("process_shift", {})
    for f in ("a", "se", "magnitude", "bias_norm_W", "n_pairs"):
        if f in pt.get("shift", {}): cmp(f"shift {f}", pt["shift"][f], ps[f], key, 1e-7)
    for t in R.TESTS:
        for slot in (t, f"{t}_robust"):
            if slot in pt and "tail_interval" in pt[slot]:
                cmp("claim CP95 interval", pt[slot]["tail_interval"], list(R.cp_interval(pt[slot]["k"], pt[slot]["B"], 0.95)), f"{key}/{slot}")
# classical Holm adjusted p and reject, from the recompute's claim p
ents = [(f"{k}:{t}", m["nulls"][k]["tests"][t]["p"]) for k in j["tests"] for t in R.TESTS]
order = sorted(range(len(ents)), key=lambda i: ents[i][1]); mx, adj = 0.0, {}
for step, i in enumerate(order):
    mx = max(mx, min(1.0, (len(ents) - step) * ents[i][1])); adj[ents[i][0]] = mx
mine_dec = {d["test"]: d for d in m["family"]["decisions"]}
for test, hp in j["holm_point"].items():
    cmp("holm_point p_raw", hp["p_raw"], dict(ents)[test], test)
    cmp("holm_point p_holm (classical)", hp["p_holm"], adj[test], test)
    cmp("holm_point reject", hp["reject"], mine_dec[test].get("holm_point") == "rejected", test)
for sk, pw in j["power"].items():
    if sk == "levels":
        cmp("power levels", list(pw), [0.05, 0.005], "levels"); continue
    mp = m["power"][sk]
    cmp("power set n", pw["n"], mp["n_present"], sk); cmp("power set declared", pw["declared"], mp["n_declared"], sk)
    cmp("power set incomplete", pw["incomplete"], not mp["complete"], sk)
    for t in R.TESTS:
        for lvl, rules in pw[t].items():
            for rule, v in rules.items():
                if "n" in v: cmp("power n", v["n"], mp["n_present"], f"{sk}/{t}/{lvl}/{rule}")
                if "B" in v: cmp("power B", v["B"], mp["B_null"], f"{sk}/{t}/{lvl}/{rule}")
                if "alpha" in v: cmp("power alpha", v["alpha"], float(lvl), f"{sk}/{t}/{lvl}/{rule}")
out = {k: {"agree": v[0], "disagree": v[1], "examples": v[2][:3]} for k, v in sorted(res.items())}
json.dump(out, open("unmapped-diagnostic.json", "w"), indent=1, default=str)
for k, v in out.items(): print(f"{k:32s} agree {v['agree']:4d} disagree {v['disagree']:3d}", v["examples"][:1] if v["disagree"] else "")
