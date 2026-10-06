import json
C = json.load(open("/Users/josephbailey/local-research/MINERvA-OmniFold-publication-20261005/docs/publication/w1/W1-RESULT-20261006.json"))
M = json.load(open("repro-result.json"))
pmap = {"ptpl": "P_ptpl", "eW": "P_eW"}
diffs, n_claim, n_var, seen = [], 0, 0, set()
for rd, crd in zip(("a", "b"), C["readings"]):
    assert crd["npz_sha256"] == M[rd]["npz_sha256"], rd
    for tk, cv in crd["tests"].items():
        key, s, pr = tk.split(":")
        mine = M[rd]["tests"][key][pmap[pr]]
        seen.add((rd, key, s, pr))
        if cv["cells"] != mine["cells"]: diffs.append((rd, tk, "cells", cv["cells"], mine["cells"]))
        for f in ("k", "B", "p"):
            n_claim += 1
            if cv["claim"][f] != mine[s][f]: diffs.append((rd, tk, f, cv["claim"][f], mine[s][f]))
        if set(cv["variants"]) != set(mine["variants"]): diffs.append((rd, tk, "variant-names", sorted(cv["variants"]), sorted(mine["variants"])))
        for vn, p in cv["variants"].items():
            n_var += 1
            if vn not in mine["variants"] or mine["variants"][vn][s]["p"] != p: diffs.append((rd, tk, vn, p, mine["variants"].get(vn, {}).get(s)))
mine_all = {(rd, k, s, pr) for rd in M for k in M[rd]["tests"] for s in ("total", "shape") for pr in ("ptpl", "eW")}
print("tests in claim:", len(seen), "in mine:", len(mine_all), "missing from claim:", sorted(mine_all - seen))
print("claim fields compared:", n_claim, "variant p compared:", n_var, "diffs:", len(diffs))
for d in diffs: print(d)
# criterion (mine)
q = []
for key in M["a"]["tests"]:
    for s in ("total", "shape"):
        ok = all(M[rd]["tests"][key][P][s]["p"] >= 0.05 for rd in ("a", "b") for P in ("P_ptpl", "P_eW"))
        q.append((key, s, ok))
print("qualifying (G,t):", [x for x in q if x[2]])
print("claimed criterion all false:", all(not v["joint_beyond_matched_coarse_projections"] for v in C["criterion"].values()), len(C["criterion"]))
