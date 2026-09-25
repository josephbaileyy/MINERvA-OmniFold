"""Review r4: per-axis reco-vs-gen migration on pass_reco rows (robust)."""
import json, os
import numpy as np
from scipy.stats import spearmanr
d = np.load("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", allow_pickle=True)
pr = d["pass_reco"]; gen = d["MCgen"][pr]; reco = d["MCreco"][pr]; w = d["w_reco"][pr].astype(float)
edges = [np.asarray(d[f"edges_{i}"], float) for i in range(5)]
ax = ["pt", "pz", "eavail", "q3", "W"]
O = {}
ing = np.ones(len(w), bool); inr = np.ones(len(w), bool)
for k, e in enumerate(edges):
    ing &= (gen[:, k] >= e[0]) & (gen[:, k] <= e[-1]); inr &= (reco[:, k] >= e[0]) & (reco[:, k] < e[-1])
O["frac_gen_in_grid"] = float(ing.mean()); O["frac_reco_in_window"] = float(inr.mean())
O["gen_min_per_col"] = [float(gen[:, k].min()) for k in range(5)]; O["gen_max_per_col"] = [float(gen[:, k].max()) for k in range(5)]
O["reco_min_per_col"] = [float(reco[:, k].min()) for k in range(5)]; O["reco_max_per_col"] = [float(reco[:, k].max()) for k in range(5)]
m = ing & inr
rng = np.random.default_rng(1); s = rng.choice(np.flatnonzero(m), 300000, replace=False)
for k, a in enumerate(ax):
    e = edges[k]
    ig = np.clip(np.searchsorted(e, gen[m, k], side="right") - 1, 0, e.size - 2)
    ir = np.clip(np.searchsorted(e, reco[m, k], side="right") - 1, 0, e.size - 2)
    M = np.zeros((e.size - 1, e.size - 1)); np.add.at(M, (ig, ir), w[m])
    O[a] = {"spearman": float(spearmanr(gen[s, k], reco[s, k]).correlation),
            "pearson_in_grid": float(np.corrcoef(gen[s, k], reco[s, k])[0, 1]),
            "diag_frac_weighted": float(np.trace(M) / M.sum()),
            "purity_per_reco_bin": [round(float(M[i, i] / M[:, i].sum()), 3) for i in range(e.size - 1)],
            "stability_per_gen_bin": [round(float(M[i, i] / M[i, :].sum()), 3) for i in range(e.size - 1)]}
json.dump(O, open(os.path.dirname(os.path.abspath(__file__)) + "/r4_migration.json", "w"), indent=1)
print(json.dumps(O, indent=1))
