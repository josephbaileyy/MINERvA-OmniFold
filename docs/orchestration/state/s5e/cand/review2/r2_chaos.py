#!/usr/bin/env python3
"""Review round 2: is the rounding-probe movement a component the bootstrap already carries?
Compares the jitter spread with (data sigma^2 - pseudo sigma^2) per functional, and measures the
B0 edge-safe jitter on the noise-free asimov construction against the pseudo-experiment sigma."""
import json, sys, numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, "/pscratch/sd/j/josephrb/s5e-20260925/deploy/2f958652/nd-unfolding")
import s5c_coverage as sc
R2 = "/pscratch/sd/j/josephrb/s5e-20260925/review2"; DIAG = "/pscratch/sd/j/josephrb/s5e-20260925/runs/diag"
U, names = sc.reported_functionals(json.load(open(R2 + "/inputs/s5c_contract.json")))
C = np.load(R2 + "/r2_cache.npz"); Z = np.load(R2 + "/r2_nominal_pulls.npz")
sig, dsig, b0sig = Z["sig"], Z["dsig"], Z["b0sig"]
j1, j2, up = (C["f|assess/data/" + k] for k in ("data_R_jitteredge1", "data_R_jitteredge2", "data_R_upcast"))
uf = lambda p: U @ np.asarray(np.load(p, allow_pickle=False)["xsec_flat"], float)
out = {}
sj2 = 0.5 * (j1 - j2) ** 2                      # per-functional estimate of the jitter variance (1 draw)
sj2b = ((j1 - up) ** 2 + (j2 - up) ** 2) / 2    # alternative: each draw vs the unperturbed run
ex = dsig ** 2 - sig ** 2
out["jitter_sd_over_dsig_rms_(j1-j2)"] = float(np.sqrt(np.mean(sj2 / dsig ** 2)))
out["jitter_sd_over_dsig_rms_(j-up)"] = float(np.sqrt(np.mean(sj2b / dsig ** 2)))
out["sqrt(1 - sig^2/dsig^2)_rms"] = float(np.sqrt(np.mean(np.clip(ex, 0, None) / dsig ** 2)))
out["frac_functionals_dsig_gt_sig"] = float(np.mean(dsig > sig))
out["dsig_over_sig_median_all153"] = float(np.median(dsig / sig))
# pooled regression of jitter variance on the excess, through the origin (relative units)
x, y = ex / dsig ** 2, sj2b / dsig ** 2
out["slope_jittervar_on_excessvar_(rel)"] = float((x * y).sum() / (x * x).sum())
out["corr_jittervar_excessvar_(rel)"] = float(np.corrcoef(x, y)[0, 1])
out["spearman_rank_corr"] = float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])
# B0 asimov (noise-free MC construction): edge-safe jitter vs upcast, against the pseudo sigma
try:
    a_up = uf(f"{DIAG}/asimov/asimov_eavail_upcast.npz"); a_j = uf(f"{DIAG}/rep/rep_asimov_eavail_jitteredge1.npz")
    a_b0 = uf(f"{DIAG}/asimov/asimov_b0_eavail.npz")
    d = np.abs(a_j - a_up)
    out["B0_asimov_eavail_jitter"] = {"upcast_equals_b0": bool(np.array_equal(a_up, a_b0)),
        "over_B0_pseudo_sigma_median": float(np.median(d / b0sig)), "max": float(np.max(d / b0sig)),
        "over_R_pseudo_sigma_median": float(np.median(d / sig)), "rel_pct_median": 100 * float(np.median(d / np.abs(a_up))),
        "rel_pct_max": 100 * float(np.max(d / np.abs(a_up)))}
    m = json.loads(str(np.load(f"{DIAG}/rep/rep_asimov_eavail_jitteredge1.npz", allow_pickle=False)["meta"]))
    out["B0_asimov_jitter_meta"] = {k: m.get(k) for k in ("construction", "coords", "jitter_f32", "jitter_mode", "truth", "amplitude")}
except Exception as e:
    out["asimov_error"] = repr(e)
# data vs pseudo event statistics context
out["pull_sd_nominal_pooled_implied_if_jitter_uncovered_(pseudo units)"] = float(np.sqrt(1 + np.median(sj2b / sig ** 2)))
json.dump(out, open(R2 + "/r2_chaos.json", "w"), indent=1)
print(json.dumps(out, indent=1))
