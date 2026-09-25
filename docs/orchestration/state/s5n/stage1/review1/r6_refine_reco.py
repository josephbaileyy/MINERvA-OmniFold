"""Review r6: independent rebuild of nominal experiments and of the real-data signed sample; refit the
Stay-Positive refinement (driver function) and compare, per reco J/EW cell, refined vs signed vs the
pseudo-data's own signal-only counts."""
import json, sys, os, time
import numpy as np
DEP = "/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517"
sys.path.insert(0, DEP + "/nd-unfolding"); sys.path.insert(0, DEP + "/2d-unfolding")
import s5c_unfold, s5n_pseudo, s5c_coverage as sc
HERE = os.path.dirname(os.path.abspath(__file__))
THREADS = int(os.environ.get("R6_THREADS", "8"))
inputs = s5c_unfold.load_inputs("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz")
bz = np.load("/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz", allow_pickle=True)
bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
edges = inputs["edges"]
U, names = sc.reported_functionals(json.load(open(DEP + "/docs/orchestration/state/s5c/contract.json")))
IND = (U > 0).astype(float)
M64 = (1 << 64) - 1
def my_half(n, key):  # independent splitmix64 parity
    z = (np.arange(n, dtype=np.uint64) ^ np.uint64(key))
    with np.errstate(over="ignore"):
        z = z + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    return (z & np.uint64(1)) == 1
def infid(x):
    m = np.ones(len(x), bool)
    for k, e in enumerate(edges): m &= (x[:, k] >= e[0]) & (x[:, k] < e[-1])
    return m
def cellsum(x, w):
    h, _ = np.histogramdd(np.asarray(x, float), bins=edges, weights=w); return IND @ h.ravel()
import unfold_2d_omnifold_unbinned as u2d
out = {}
for seed in (300000, 300001):
    key = (seed * 0x9E3779B1 + 0x5C5C) % (2**61 - 1)
    n = inputs["MCgen"].shape[0]; is_b = my_half(n, key)
    is_c = my_half(len(bkg["bkg_w"]), key ^ 0xB6D5E1A7C3F29041)
    rng = np.random.default_rng(seed)
    br = is_b & inputs["pass_reco"]
    nsig = rng.poisson(2.0 * inputs["w_reco"][br]).astype(float)
    mb = rng.poisson(2.0 * bkg["bkg_w"][is_c]).astype(float)
    sx = inputs["MCreco"][br]; bx = bkg["bkg_reco"][is_c]; tx = bkg["bkg_reco"][~is_c]; tw = 2.0 * bkg["bkg_w"][~is_c]
    # theirs
    exp, _, info = s5n_pseudo.build_pseudo(inputs, bkg, "nominal", 0.0, key, seed)
    feat_t, sw_t, _, _ = s5n_pseudo.signed_sample(exp)
    ks, kb, kt = (nsig > 0) & infid(sx), (mb > 0) & infid(bx), infid(tx)
    feat = np.concatenate([sx[ks], bx[kb], tx[kt]]).astype(float); sw = np.concatenate([nsig[ks], mb[kb], -tw[kt]])
    same = bool(np.array_equal(feat, feat_t) and np.array_equal(sw, sw_t))
    params = {"random_state": 45, **s5c_unfold.config_params("deterministic", THREADS)}
    t0 = time.time()
    w_ref, g, frac = u2d.refine_stay_positive(feat, sw, estimator="lgbm", device="cpu", params=params)
    ns = int(ks.sum())
    S = cellsum(sx[ks], nsig[ks])                      # pseudo-data signal counts (what an ideal subtraction leaves)
    Sexp = cellsum(inputs["MCreco"][br][infid(inputs["MCreco"][br])], 2.0 * inputs["w_reco"][br][infid(inputs["MCreco"][br])])
    Bc = cellsum(bx[kb], mb[kb]); T = cellsum(tx[kt], tw[kt]); Rf = cellsum(feat, w_ref); Sg = cellsum(feat, sw)
    out[seed] = {"independent_build_equals_s5n_build": same, "n_signed": len(sw), "refined_sum": float(w_ref.sum()),
                 "meta_refined_sum_reference": None, "seconds": round(time.time() - t0, 1), "threads": THREADS,
                 "S": S.tolist(), "Sexp": Sexp.tolist(), "Bc": Bc.tolist(), "T": T.tolist(), "R": Rf.tolist(), "Sg": Sg.tolist()}
    print(seed, "build equal:", same, "refined_sum", w_ref.sum(), "t", round(time.time() - t0, 1), flush=True)
# real data
obs = inputs["measured"]; ko = infid(obs); tk = infid(bkg["bkg_reco"])
feat = np.concatenate([obs[ko], bkg["bkg_reco"][tk]]).astype(float); sw = np.concatenate([np.ones(int(ko.sum())), -np.asarray(bkg["bkg_w"], float)[tk]])
w_ref, g, frac = u2d.refine_stay_positive(feat, sw, estimator="lgbm", device="cpu", params={"random_state": 45, **s5c_unfold.config_params("deterministic", THREADS)})
out["data"] = {"refined_sum": float(w_ref.sum()), "D": cellsum(obs[ko], np.ones(int(ko.sum()))).tolist(),
               "B": cellsum(bkg["bkg_reco"][tk], np.asarray(bkg["bkg_w"], float)[tk]).tolist(), "R": cellsum(feat, w_ref).tolist()}
# purity weights on data per cell, for comparison
pw = inputs["measured_weights"]
out["data"]["P"] = cellsum(obs, pw).tolist()
json.dump({"names": names, **{str(k): v for k, v in out.items()}}, open(HERE + "/r6_refine_reco.json", "w"))
print("done")
