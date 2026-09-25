"""Review r2: estimator response to the departures, per EW cell, vs the truth ratio; diag vs ordinary."""
import json, glob, sys, os
import numpy as np
DEP = "/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517"
sys.path.insert(0, DEP + "/nd-unfolding")
import s5c_coverage as sc
R = "/pscratch/sd/j/josephrb/s5n-20260925/runs/"
U, names = sc.reported_functionals(json.load(open(DEP + "/docs/orchestration/state/s5c/contract.json")))
U = U[:42]
def L(pat):
    fs = sorted(f for f in glob.glob(R + pat) if "partial" not in f)
    xs = np.array([U @ np.load(f)["xsec_flat"] for f in fs]); xt = np.array([U @ np.load(f)["xtrue_flat"] for f in fs])
    seeds = [json.loads(str(np.load(f)["meta"]))["pseudo_seed"] for f in fs]
    return xs, xt, seeds
nx, nt, _ = L("dev/nominal_a0_s*.npz")
ex, et, es = L("dev/eavail_shape_a1_s*.npz")
qx, qt, qs = L("dev/q3_given_eavail_w_a0.3_s*.npz")
tc = json.load(open(R + "truth/truth_check.json"))["departures"]
re = np.array(tc["eavail_shape"]["M1_ratio"][:42])
print("EW  ie iw | r_truth(full) xt_dep/xt_nom | xs_dep/xs_nom(estimator) | resid% | nonresponse(1/r-1)% | q3: xt ratio, xs ratio")
for i in range(42):
    print(f"EW{i:<3d}{i//6:2d}{i%6:3d} | {re[i]:.4f} {et[:,i].mean()/nt[:,i].mean():.4f} | {ex[:,i].mean()/nx[:,i].mean():.4f} | {100*(ex[:,i]/et[:,i]-1).mean():7.2f} | {100*(1/re[i]-1):7.2f} | {qt[:,i].mean()/nt[:,i].mean():.4f} {qx[:,i].mean()/nx[:,i].mean():.4f}")
# diag
for tag, pat, ordx, ordt, ords in (("eavail", "diag/diag_prior_eavail_shape_a1_s*.npz", ex, et, es), ("q3", "diag/diag_prior_q3_given_eavail_w_a0.3_s*.npz", qx, qt, qs)):
    dx, dt, ds = L(pat)
    print("== diag", tag, ds)
    for j, s in enumerate(ds):
        k = ords.index(s) if s in ords else None
        print(" seed", s, "xt equal to ordinary product:", None if k is None else bool(np.array_equal(dt[j], ordt[k])))
        dres = dx[j] / dt[j] - 1
        print("  diag resid% max|.|", round(100*np.max(np.abs(dres)),2), " diag xs / nominal-mean xs: max|.-1|%", round(100*np.max(np.abs(dx[j]/nx.mean(0)-1)),2))
        if tag == "eavail":
            print("  max |diag resid - (1/r-1)| pp", round(100*np.max(np.abs(dres-(1/re-1))),3))
        if k is not None:
            print("  ordinary resid% same seed, EW2,EW29,EW41:", [round(100*(ordx[k][i]/ordt[k][i]-1),2) for i in (2,29,41)], " diag:", [round(100*dres[i],2) for i in (2,29,41)])
