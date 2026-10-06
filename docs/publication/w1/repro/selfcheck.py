import json, numpy as np, sys
sys.path.insert(0, ".")
import repro
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold-publication-20261005/nd-unfolding")
import s5p_joint as sj
z = np.load(repro.IN + "reading_a_union.npz"); man = json.load(open(repro.IN + "reading_a_union.npz.manifest.json"))
for key in ["GiBUU_2019", "GENIE_2_12_10_CV"]:
    dom = z[f"dom__{key}"].astype(bool); n = int(dom.sum())
    r = repro.run_one(z, man, key, np.eye(n), dom)
    F, mu, var, V = z[f"F__{key}"], z[f"mu__{key}"], z[f"var__{key}"], z["V"]
    seeds = z[f"seeds__{key}"].astype(np.int64); S = z[f"S__{key}"]
    tt, ts = sj.statistics(F + 1.0 * S, mu, var, V, dom, man["nulls"][key]["surrogate_seed0"], seeds=seeds)
    to, so = sj.statistics(z["f_data"][None], mu, var, V, dom, 0, draw=False)
    print(key, r["variants"]["1.0"]["total"], {"k": int((tt >= to[0]).sum())}, r["variants"]["1.0"]["shape"], {"k": int((ts >= so[0]).sum())}, r["T_total_obs"], to[0])
