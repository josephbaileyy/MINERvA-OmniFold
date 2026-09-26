#!/usr/bin/env python3
"""Review round 2: did the withheld deformations change the truth as their ratio files imply?
Per 5D cell, mean xtrue under W_k over mean xtrue at nominal (fresh assessment seeds) against the
ratio's prediction c * rho(cell) (a = 1); in-grid integrated cross section preserved."""
import json, sys, numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, "/pscratch/sd/j/josephrb/s5e-20260925/deploy/2f958652/nd-unfolding")
import project_cov_nd as pc
R2 = "/pscratch/sd/j/josephrb/s5e-20260925/review2"
AX = ["pt", "pz", "eavail", "q3", "W"]
edges = [np.asarray(pc.AXIS_EDGES[a], float) for a in AX]
shape = tuple(len(e) - 1 for e in edges)
vol = np.ones(shape)
for d, e in enumerate(edges):
    vol = vol * np.diff(e).reshape([-1 if i == d else 1 for i in range(5)])
X = np.load(R2 + "/r2_xtrue_full.npz")
nom = X["assess__nominal"].reshape(-1, *shape)
out = {"n_nominal": nom.shape[0]}
nm = nom.mean(0)
nse = nom.std(0, ddof=1) / np.sqrt(nom.shape[0])
def pred(kind):
    if kind in ("W1", "gibuu"):
        f = {"W1": "eavail-ratio-nuwro-over-genie.json", "gibuu": "eavail-ratio-gibuu-over-genie.json"}[kind]
        r = json.load(open(f"{R2}/inputs/{f}"))
        assert np.allclose(r["eavail_edges"], edges[2])
        rho = np.asarray(r["shape_ratio"])
        return rho.reshape(1, 1, -1, 1, 1) * np.ones(shape)
    f = {"W2": "w2-genie-mec-over-cv-eavailW.json", "W3": "w3-nuwro-over-genie-pt-pz-eavail.json"}[kind]
    r = json.load(open(f"{R2}/inputs/{f}"))
    axes = r["axes"]
    for a, e in zip(axes, r["edges"]):
        assert np.allclose(e, edges[a]), a
    rho = np.asarray(r["shape_ratio"]).reshape([shape[a] for a in axes])
    full = np.ones(shape)
    sl = [None] * 5
    for a in axes: sl[a] = slice(None)
    return (rho[tuple(sl)] * full), r["stats"]
for kind, key in (("gibuu", "assess__eavail_gibuu"), ("W1", "assess__W1"), ("W2", "assess__W2"), ("W3", "assess__W3")):
    w = X[key].reshape(-1, *shape)
    wm = w.mean(0); wse = w.std(0, ddof=1) / np.sqrt(w.shape[0])
    p = pred(kind); stats = None
    if isinstance(p, tuple): p, stats = p
    good = (nm > 0) & (wm > 0) & (nse / np.where(nm > 0, nm, 1) < 0.01) & (wse / np.where(wm > 0, wm, 1) < 0.01)
    obs = wm[good] / nm[good]
    # the constant c is fixed by the in-grid total; estimate it as the weighted ratio of obs to rho
    wts = (nm * vol)[good]
    c = np.sum(wts * obs) / np.sum(wts * p[good])
    resid = obs / (c * p[good]) - 1
    tot_nom = float((nm * vol).sum()); tot_w = float((wm * vol).sum())
    out[kind] = {"n_cells_tested": int(good.sum()), "c_fit": float(c),
                 "rel_resid_median_abs": float(np.median(np.abs(resid))), "rel_resid_max_abs": float(np.max(np.abs(resid))),
                 "corr(obs, c*rho)": float(np.corrcoef(obs, c * p[good])[0, 1]),
                 "obs_ratio_range": [float(obs.min()), float(obs.max())], "rho_range_tested": [float(p[good].min()), float(p[good].max())],
                 "fraction_cells_changed_by_gt_2pct": float(np.mean(np.abs(obs - 1) > 0.02)),
                 "ingrid_total_ratio_W_over_nominal": tot_w / tot_nom,
                 "ingrid_total_nominal_seed_sd_rel": float((nom * vol).sum(axis=(1, 2, 3, 4, 5)).std(ddof=1) / tot_nom),
                 "ratio_file_stats": stats}
    # the total-preservation check in units of its seed noise
    tn = (nom * vol).reshape(nom.shape[0], -1).sum(1); tw = (w * vol).reshape(w.shape[0], -1).sum(1)
    out[kind]["ingrid_total_diff_over_se"] = float((tw.mean() - tn.mean()) / np.sqrt(tw.var(ddof=1) / len(tw) + tn.var(ddof=1) / len(tn)))
json.dump(out, open(R2 + "/r2_truth.json", "w"), indent=1)
print(json.dumps(out, indent=1))
