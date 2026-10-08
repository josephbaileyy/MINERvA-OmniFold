#!/usr/bin/env python3
"""Extra (beyond task 4): family-A decisions on the 0.5 grid, recomputed from the stored claim k with the SAME
holm_with_determinacy of kappa_repro.py (imported, not retyped). Usage: grid_decisions.py <worktree> <rc4> <results.json> <out.json>"""
import importlib.util, json, sys
wt, rc4, res, out = sys.argv[1:5]
sys.dont_write_bytecode = True
sys.argv = ["kappa_repro.py", wt, rc4, "/dev/null"]
spec = importlib.util.spec_from_file_location("kappa_repro", __file__.replace("grid_decisions.py", "kappa_repro.py"))
kr = importlib.util.module_from_spec(spec); spec.loader.exec_module(kr)
R = json.load(open(res))
Bs = {k: v["B"] for k, v in R["task2_frozen_family_A"]["0.0"].items()}
M = R["task4_monotonicity_frozen_family_A"]
dec = {}
for g in M["grid"]:
    ks = M["claim_k"][repr(g)]
    d = kr.holm_with_determinacy({k: {"k": ks[k], "B": Bs[k], "p": (ks[k] + 1) / (Bs[k] + 1)} for k in ks})
    dec[repr(g)] = {k: v["decision"] for k, v in d.items()}
regain = []
keys = list(Bs)
for key in keys:
    seq = [dec[repr(g)][key] for g in M["grid"]]
    lost = False
    for g, s in zip(M["grid"], seq):
        if s != "rejected": lost = True
        elif lost: regain.append((key, g))
json.dump({"decisions": dec, "returns_to_rejected": regain}, open(out, "w"), indent=1)
A = {"rejected": "R", "undetermined": "U", "not rejected": "N"}
for key in keys:
    print(f"{key:26s}", " ".join(A[dec[repr(g)][key]] for g in M["grid"]))
print("returns to rejected:", regain or "none")
