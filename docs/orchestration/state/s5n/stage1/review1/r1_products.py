"""Independent review r1: recompute s5n Stage-1 statistics from the products."""
import json, glob, math, sys, os
import numpy as np
DEP = "/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517"
sys.path.insert(0, DEP + "/nd-unfolding")
import s5c_coverage as sc, project_cov_nd as pc
R = "/pscratch/sd/j/josephrb/s5n-20260925/runs/"
OUT = {}
con = json.load(open(DEP + "/docs/orchestration/state/s5c/contract.json"))
U, names = sc.reported_functionals(con)
OUT["n_functionals"] = len(names)
AX = ["pt", "pz", "eavail", "q3", "W"]
E = [np.asarray(pc.AXIS_EDGES[a], float) for a in AX]
shape = tuple(len(e) - 1 for e in E)
W = [np.diff(e) for e in E]
# --- independent EW projection: sum over pt,pz,q3 of xs * widths ---
def my_ew(x):
    x = x.reshape(shape)
    v = x * W[0][:, None, None, None, None] * W[1][None, :, None, None, None] * W[3][None, None, None, :, None]
    return v.sum(axis=(0, 1, 3)).ravel()  # (eavail,W) flattened ie*6+iw
def my_total(x):
    x = x.reshape(shape)
    v = x.copy()
    for k in range(5):
        s = [None] * 5; s[k] = slice(None); v = v * W[k][tuple(s)]
    return v.sum()
def load(f):
    z = np.load(f, allow_pickle=False)
    d = {"xs": np.asarray(z["xsec_flat"], float), "meta": json.loads(str(z["meta"]))}
    if "xtrue_flat" in z.files: d["xt"] = np.asarray(z["xtrue_flat"], float)
    return d
ref = load(R + "c2/c2_rep_a.npz")
ew_theirs = U[:42] @ ref["xs"]; ew_mine = my_ew(ref["xs"])
OUT["EW_projection_check_max_rel"] = float(np.max(np.abs(ew_theirs / ew_mine - 1)))
OUT["total_check_rel"] = float((U[-1] @ ref["xs"]) / my_total(ref["xs"]) - 1)
OUT["EW_all_ones_is_plain_sum"] = bool(np.allclose(U[42], 1.0))
idx = {n: i for i, n in enumerate(names)}
# --- sigma from available bootstrap replicas ---
bfiles = sorted(glob.glob(R + "sigma/boot_b*.npz"), key=lambda s: int(s.split("boot_b")[1][:-4]))
bfiles = [f for f in bfiles if "partial" not in f]
Rb = np.array([U @ load(f)["xs"] for f in bfiles])
sig = Rb.std(0, ddof=1)
OUT["sigma_n_replicas"] = len(bfiles)
OUT["sigma_boot_seeds"] = [int(f.split("boot_b")[1][:-4]) for f in bfiles]
xt_sigma_exp = load(bfiles[0])["xt"]
OUT["sigma_rel_median_pct"] = 100 * float(np.median(sig / np.abs(U @ xt_sigma_exp)))
# sigma stability: first half vs second half of replicas
h = len(bfiles) // 2
s1, s2 = Rb[:h].std(0, ddof=1), Rb[h:].std(0, ddof=1)
OUT["sigma_half_ratio_median"] = float(np.median(s1 / s2))
# --- C0 ---
c0 = np.load(R + "c0/c0_purity_d1_split_s4.npz"); d1 = np.load("/pscratch/sd/j/josephrb/s5c-20260924/runs/d1/d1_split_s4.npz")
OUT["C0"] = {"xsec_bitwise": bool(np.array_equal(c0["xsec_flat"], d1["xsec_flat"])),
             "xtrue_bitwise": bool(np.array_equal(c0["xtrue_flat"], d1["xtrue_flat"])),
             "max_abs_diff_xsec": float(np.max(np.abs(c0["xsec_flat"] - d1["xsec_flat"]))),
             "dtype": [str(c0["xsec_flat"].dtype), str(d1["xsec_flat"].dtype)],
             "d1_meta_keys": sorted(json.loads(str(d1["meta"])).keys())[:40]}
m0 = json.loads(str(c0["meta"])); md = json.loads(str(d1["meta"]))
OUT["C0"]["seeds"] = {"c0": [m0.get("pseudo_seed"), m0.get("split_key"), m0.get("config")], "d1": [md.get("pseudo_seed"), md.get("split_key"), md.get("config"), md.get("truth")]}
# --- C2 ---
c2 = {k: load(R + f"c2/{k}.npz") for k in ("c2_rep_a", "c2_rep_b", "c2_seed43", "c2_perm1")}
fa = U @ c2["c2_rep_a"]["xs"]
OUT["C2"] = {"rep_bitwise": bool(np.array_equal(c2["c2_rep_a"]["xs"], c2["c2_rep_b"]["xs"])),
             "seed43_bitwise": bool(np.array_equal(c2["c2_rep_a"]["xs"], c2["c2_seed43"]["xs"])),
             "seed43_refine_random_state": c2["c2_seed43"]["meta"]["refinement"]["classifier_params"]["random_state"],
             "seed43_refined_sum_equal": c2["c2_seed43"]["meta"]["refinement"]["refined_sum"] == c2["c2_rep_a"]["meta"]["refinement"]["refined_sum"],
             "perm_refined_sum_rel": c2["c2_perm1"]["meta"]["refinement"]["refined_sum"] / c2["c2_rep_a"]["meta"]["refinement"]["refined_sum"] - 1,
             "perm_max_shift_over_sigma": float(np.max(np.abs(U @ c2["c2_perm1"]["xs"] - fa) / sig)),
             "perm_argmax": names[int(np.argmax(np.abs(U @ c2["c2_perm1"]["xs"] - fa) / sig))],
             "perm_median_shift_over_sigma": float(np.median(np.abs(U @ c2["c2_perm1"]["xs"] - fa) / sig))}
# --- grid points ---
def stats(files, tag):
    P = [load(f) for f in files]
    fh = np.array([U @ p["xs"] for p in P]); ft = np.array([U @ p["xt"] for p in P])
    rel = (fh - ft) / ft; pull = (fh - ft) / sig
    n = len(P); mean = rel.mean(0); se = rel.std(0, ddof=1) / math.sqrt(n); t = mean / se
    mu, sd = pull.mean(0), pull.std(0, ddof=1)
    worst = np.argsort(-np.abs(t))[:16]
    o = {"n": n, "seeds": [p["meta"]["pseudo_seed"] for p in P], "max_abs_t": float(np.max(np.abs(t))),
         "argmax_t": names[int(np.argmax(np.abs(t)))], "n_t_gt_3p6": int(np.sum(np.abs(t) > 3.6)),
         "n_half_sigma_and_t_gt_3": int(np.sum((np.abs(mu) > 0.5) & (np.abs(t) > 3))),
         "pooled_cov68": float(np.mean(np.abs(pull) <= 1)), "pooled_cov95": float(np.mean(np.abs(pull) <= 1.96)),
         "pull_sd_median": float(np.median(sd)), "pull_sd_q10_q90": [float(np.quantile(sd, .1)), float(np.quantile(sd, .9))],
         "pull_sd_pooled_centered": float(np.sqrt(np.mean((pull - mu) ** 2) * n / (n - 1))),
         "worst": [(names[i], round(100 * mean[i], 3), round(100 * se[i], 3), round(t[i], 2), round(mu[i], 2), round(sd[i], 2)) for i in worst],
         "highW": {nm: (round(100 * mean[idx[nm]], 3), round(100 * se[idx[nm]], 3), round(t[idx[nm]], 2), round(mu[idx[nm]], 2)) for nm in ["EW5", "EW11", "EW17", "EW23", "EW29", "EW35", "EW41", "EW_all_ones", "total_integrated"]},
         "max_abs_mean_rel_pct": float(100 * np.max(np.abs(mean))), "argmax_rel": names[int(np.argmax(np.abs(mean)))]}
    return o, rel, pull, fh, ft, P
pts = {}
RAW = {}
for tag, pat in (("nominal", "nominal_a0_s*.npz"), ("eavail", "eavail_shape_a1_s*.npz"), ("q3", "q3_given_eavail_w_a0.3_s*.npz")):
    files = sorted(f for f in glob.glob(R + "dev/" + pat) if "partial" not in f)
    o, rel, pull, fh, ft, P = stats(files, tag)
    pts[tag] = o; RAW[tag] = (rel, pull, fh, ft, P)
OUT["grid"] = pts
OUT["C3_pass"] = pts["nominal"]["max_abs_t"] <= 3.6 and pts["nominal"]["n_half_sigma_and_t_gt_3"] == 0
rel, pull = RAW["nominal"][0], RAW["nominal"][1]
claimed = ["J80", "J85", "J88", "J89", "J94", "J97", "J98", "J106", "J107", "J161", "J162", "J175"]
mean = rel.mean(0); se = rel.std(0, ddof=1) / math.sqrt(rel.shape[0])
OUT["C3_claimed_J"] = {j: (round(100 * mean[idx[j]], 3), round(mean[idx[j]] / se[idx[j]], 2), round(pull.mean(0)[idx[j]], 2)) if j in idx else None for j in claimed}
OUT["C3_t_gt_3p6_list"] = [(names[i], round(100 * mean[i], 3), round(mean[i] / se[i], 2)) for i in np.flatnonzero(np.abs(mean / se) > 3.6)]
# --- C8 ---
c8 = [load(f) for f in sorted(glob.glob(R + "c8/c8_signal_only_s*.npz"))]
r8 = np.array([(U @ p["xs"] - U @ p["xt"]) / (U @ p["xt"]) for p in c8])
m8, s8 = r8.mean(0), r8.std(0, ddof=1) / math.sqrt(len(c8))
OUT["C8"] = {"n": len(c8), "claimed_J": {j: (round(100 * m8[idx[j]], 3), round(100 * s8[idx[j]], 3)) for j in claimed},
             "highW": {nm: round(100 * m8[idx[nm]], 3) for nm in ["EW5", "EW11", "EW17", "EW23", "EW29", "EW35", "EW41"]},
             "refinement_ran": [p["meta"]["refinement"].get("ran") for p in c8],
             "n_template_rows": [p["meta"]["refinement"].get("n_template_rows") for p in c8]}
# --- C7 ---
dp, dn = load(R + "c7/data_purity.npz"), load(R + "c7/data_negweight.npz")
fp, fn = U @ dp["xs"], U @ dn["xs"]; rd = (fn - fp) / fp
o7 = np.argsort(-np.abs(rd))[:12]
OUT["C7"] = {"highW_pct": {nm: round(100 * rd[idx[nm]], 3) for nm in ["EW5", "EW11", "EW17", "EW23", "EW29", "EW35", "EW41"]},
             "total_pct": round(100 * rd[idx["total_integrated"]], 3), "median_abs_pct": round(100 * float(np.median(np.abs(rd))), 3),
             "max_abs_pct": round(100 * float(np.max(np.abs(rd))), 3), "argmax": names[int(np.argmax(np.abs(rd)))],
             "largest": [(names[i], round(100 * rd[i], 3)) for i in o7],
             "claimed_J_on_data_pct": {j: round(100 * rd[idx[j]], 3) for j in claimed},
             "refinement": {k: dn["meta"]["refinement"][k] for k in ("refined_over_signed", "clipped_fraction", "n_clipped", "clipped_signed_mass", "n_eff_refined", "n_eff_signed_abs", "sum_negative", "sum_positive")}}
try:
    import s5c_assemble
    drv = U @ s5c_assemble.read_flat(R + "c7/xsec_5d_driver_negweight_F2.root")
    drvp = U @ s5c_assemble.read_flat("/pscratch/sd/j/josephrb/s5c-20260924/runs/construction/xsec_5d_MEFHC_5iter_lgbm_F2.root")
    OUT["C7"]["driver_vs_npz_negweight_max_rel_pct"] = 100 * float(np.max(np.abs(drv / fn - 1)))
    OUT["C7"]["driver_vs_npz_negweight_argmax"] = names[int(np.argmax(np.abs(drv / fn - 1)))]
    OUT["C7"]["driver_vs_npz_purity_max_rel_pct"] = 100 * float(np.max(np.abs(drvp / fp - 1)))
    OUT["C7"]["driver_negw_minus_driver_purity_vs_npz_max_abs_diff_pp"] = 100 * float(np.max(np.abs((drv - drvp) / drvp - rd)))
except Exception as ex:
    OUT["C7"]["driver_error"] = repr(ex)
np.savez(os.path.dirname(os.path.abspath(__file__)) + "/r1_arrays.npz", sig=sig, rel_nom=RAW["nominal"][0], rel_eav=RAW["eavail"][0], rel_q3=RAW["q3"][0],
         pull_nom=RAW["nominal"][1], fn=fn, fp=fp, r8=r8, names=np.array(names))
json.dump(OUT, open(os.path.dirname(os.path.abspath(__file__)) + "/r1_products.json", "w"), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
