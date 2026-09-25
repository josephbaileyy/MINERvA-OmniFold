"""Review r3: operand checks on the input npz and background dump."""
import json, sys, os
import numpy as np
DEP = "/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517"
sys.path.insert(0, DEP + "/nd-unfolding")
import s5c_coverage as sc, project_cov_nd as pc
O = {}
d = np.load("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", allow_pickle=True)
O["files"] = d.files
for k in d.files:
    if k not in ("MCgen", "MCreco", "measured", "pass_reco", "pass_truth", "w_truth", "w_reco", "measured_weights", "denom_nd"):
        v = d[k]
        O["key_" + k] = (str(v)[:300] if v.size < 50 else f"array{v.shape}")
pr, pt = d["pass_reco"], d["pass_truth"]
wr, wt = d["w_reco"].astype(float), d["w_truth"].astype(float)
O["n_rows"] = int(pr.size); O["n_pass_reco"] = int(pr.sum()); O["n_pass_truth"] = int(pt.sum())
O["n_reco_not_truth"] = int((pr & ~pt).sum()); O["w_reco_sum_reco_not_truth_frac"] = float(wr[pr & ~pt].sum() / wr[pr].sum())
O["w_reco_eq_w_truth_frac"] = float(np.mean(wr[pr & pt] == wt[pr & pt]))
O["w_reco_stats"] = [float(np.min(wr[pr])), float(np.median(wr[pr])), float(np.max(wr[pr])), float(wr[pr].mean())]
lam = 2.0 * wr[pr]
O["overdispersion_sum_lam(1+lam)/sum_lam_all_pass_reco"] = float((lam * (1 + lam)).sum() / lam.sum())
O["mean_count_per_reco_row"] = float(lam.mean())
lam1 = wr[pr]
O["overdispersion_unit_weight_full_sample"] = float((lam1 * (1 + lam1)).sum() / lam1.sum())
mw = d["measured_weights"]; O["measured_weights_stats"] = [float(mw.min()), float(mw.max()), float(mw.sum()), int(mw.size)]
edges = [np.asarray(d[f"edges_{i}"], float) for i in range(int(d["nedges"]))]
O["edges_equal_pc"] = [bool(np.allclose(edges[i], pc.AXIS_EDGES[a])) for i, a in enumerate(["pt", "pz", "eavail", "q3", "W"])]
gen = d["MCgen"]; reco = d["MCreco"]
# column sanity: correlation of reco vs gen per column on pass_reco&pass_truth rows (sample)
rng = np.random.default_rng(0); s = rng.choice(np.flatnonzero(pr & pt), 200000, replace=False)
O["gen_reco_corr_per_col"] = [float(np.corrcoef(gen[s, k], reco[s, k])[0, 1]) for k in range(5)]
O["gen_col_medians"] = [float(np.median(gen[s, k])) for k in range(5)]
O["reco_col_medians"] = [float(np.median(reco[s, k])) for k in range(5)]
# background dump
b = np.load("/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz", allow_pickle=True)
bw = b["bkg_w"].astype(float); br = b["bkg_reco"].astype(float)
O["bkg_meta"] = json.loads(str(b["meta"]))
O["bkg_rows"] = int(bw.size); O["bkg_w_stats"] = [float(bw.min()), float(np.median(bw)), float(bw.max()), float(bw.sum())]
O["bkg_reco_col_medians"] = [float(np.median(br[:, k])) for k in range(5)]
bnd = b["bkg_nd"]
h, _ = np.histogramdd(br, bins=edges, weights=bw)
O["bkg_nd_equals_hist_bkg_reco"] = float(np.max(np.abs(h - bnd)))
meas = d["measured"].astype(float)
dat, _ = np.histogramdd(meas, bins=edges)
sig_mc, _ = np.histogramdd(reco[pr].astype(float), bins=edges, weights=wr[pr])
# J-cell (reco-space, same coarse partition as the truth functionals) background fraction
con = json.load(open(DEP + "/docs/orchestration/state/s5c/contract.json"))
U, names = sc.reported_functionals(con)
ind = (U > 0).astype(float)
bJ, dJ, sJ = ind @ bnd.ravel(), ind @ dat.ravel(), ind @ sig_mc.ravel()
# template MC-stat variance per reco J cell vs data Poisson variance
bw2, _ = np.histogramdd(br, bins=edges, weights=bw ** 2)
vJ = ind @ bw2.ravel()
np.savez(os.path.dirname(os.path.abspath(__file__)) + "/r3_bkgfrac.npz", bJ=bJ, dJ=dJ, sJ=sJ, vJ=vJ, names=np.array(names))
O["bkg_over_data_global"] = float(bnd.sum() / dat.sum())
fr = bJ / np.maximum(dJ, 1)
order = np.argsort(-fr)
O["bkg_frac_rank_top20"] = [(names[i], round(float(fr[i]), 4)) for i in order[:20]]
claimed = ["J80", "J85", "J88", "J89", "J94", "J97", "J98", "J106", "J107", "J161", "J162", "J175"]
idx = {n: i for i, n in enumerate(names)}
O["bkg_frac_claimed"] = {j: (round(float(fr[idx[j]]), 4), int(np.flatnonzero(order == idx[j])[0])) for j in claimed}
O["bkg_frac_median_all"] = float(np.median(fr))
O["template_var_over_data_var_global_pseudo(2x)"] = float(2 * bw2.sum() * 2 / (dat.sum()))
json.dump(O, open(os.path.dirname(os.path.abspath(__file__)) + "/r3_inputs.json", "w"), indent=1, default=str)
print(json.dumps(O, indent=1, default=str))
