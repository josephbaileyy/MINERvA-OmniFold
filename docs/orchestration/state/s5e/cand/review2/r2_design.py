#!/usr/bin/env python3
"""Review round 2: independent Clopper-Pearson/Bonferroni spot-check of next_design.json (no campaign code)."""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, norm
D = sys.argv[1]
nd = json.load(open(D + "/inputs/next_design.json")); ar = json.load(open(D + "/inputs/assess_receipt.json"))
def kmin(n, thr, a):
    # smallest k whose one-sided CP lower bound at level a exceeds thr
    ks = np.arange(n + 1)
    lo = np.where(ks == 0, 0.0, beta.ppf(a, np.maximum(ks, 1), n - ks + 1))
    ok = np.flatnonzero(lo > thr)
    return int(ok[0]) if ok.size else None
def assur(n, p, thr, m):
    k = kmin(n, thr, 0.05 / m)
    q = 0.0 if k is None else binom.sf(k - 1, n, p)
    return max(0.0, 1 - m * (1 - q)), q
out = {}
for (lab, thr, p) in (("68", 0.66, 0.6827), ("95", 0.94, 0.9545)):
    for m in (20, 42, 153, 60):
        row = {str(n): round(assur(n, p, thr, m)[0], 4) for n in (8000, 11422, 16000)}
        # smallest n reaching 0.8 by bisection on a coarse-to-fine grid
        lo, hi = 100, 100000
        while hi - lo > max(1, lo // 200):
            mid = (lo + hi) // 2
            if assur(mid, p, thr, m)[0] >= 0.8: hi = mid
            else: lo = mid
        row["n80_approx"] = hi
        out[f"{lab}_m{m}"] = row
# design coverage minimum in the A4 scope from the receipt's nominal pulls
nom = ar["points"]["nominal"]["per_functional"]; names = ar["functional_names"]
scope = [names.index(c) for c in ar["A4"]["cells_model_dependence_within_adopted_sigma"]]
def cov(mu, sd, z): return norm.cdf((z - mu) / sd) - norm.cdf((-z - mu) / sd)
c68 = [(cov(nom["mean_pull"][i], nom["pull_sd"][i], 1.0), names[i], nom["mean_pull"][i], nom["pull_sd"][i], nom["cov68"][i]) for i in scope]
c68.sort()
out["A4_scope_min_design_cov68"] = c68[:3]
out["empirical_cov68_of_that_cell_(40 exps)"] = c68[0][4]
allf = sorted((cov(nom["mean_pull"][i], nom["pull_sd"][i], 1.0), names[i], nom["pull_sd"][i]) for i in range(len(names)))
out["all153_min_design_cov68"] = allf[:3]
# pull-SD extreme-value context: expected max of 20 / 153 sample SDs at n=40 if the truth is 1
rng = np.random.default_rng(1)
sims = rng.standard_normal((4000, 153, 40)).std(axis=2, ddof=1)
out["null_P(max pull SD over 20 >= observed scope max)"] = float(np.mean(sims[:, :20].max(1) >= max(nom["pull_sd"][i] for i in scope)))
out["scope_max_pull_sd"] = max(nom["pull_sd"][i] for i in scope)
out["null_P(>=6 of 153 outside 1+-3SE)"] = float(np.mean(((sims < 1 - 3 / math.sqrt(78)) | (sims > 1 + 3 / math.sqrt(78))).sum(1) >= 6))
out["receipt_values"] = {k: nd["A_statistical_scope_coverage"]["A4_scope_EW_cells"][k]["n_for_80pct_assurance_exactly_nominal"] for k in ("68_nominal_only", "95_nominal_only", "68_nominal_plus_two_nuisance_points", "95_nominal_plus_two_nuisance_points")}
out["receipt_all42"] = {k: nd["A_statistical_scope_coverage"]["all_42_EW_cells"][k]["n_for_80pct_assurance_exactly_nominal"] for k in ("68_nominal_only", "95_nominal_only")}
out["receipt_all153"] = {k: nd["A_statistical_scope_coverage"]["all_153_functionals"][k]["n_for_80pct_assurance_exactly_nominal"] for k in ("68_nominal_only", "95_nominal_only")}
json.dump(out, open(D + "/r2_design.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
