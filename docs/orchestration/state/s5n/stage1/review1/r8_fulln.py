"""Review round 2 (targeted): full-n recomputation of C1, C2, C3-C6 and the signal-only departure diagnostic."""
import json, glob, math, sys, os
import numpy as np
DEP = "/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517"
sys.path.insert(0, DEP + "/nd-unfolding")
import s5c_coverage as sc
R = "/pscratch/sd/j/josephrb/s5n-20260925/runs/"; H = os.path.dirname(os.path.abspath(__file__))
U, names = sc.reported_functionals(json.load(open(DEP + "/docs/orchestration/state/s5c/contract.json")))
ix = {n: i for i, n in enumerate(names)}; HW = ["EW5", "EW11", "EW17", "EW23", "EW29", "EW35", "EW41"]
def load(f):
    z = np.load(f, allow_pickle=False); d = {"xs": np.asarray(z["xsec_flat"], float), "meta": json.loads(str(z["meta"]))}
    if "xtrue_flat" in z.files: d["xt"] = np.asarray(z["xtrue_flat"], float)
    return d
O = {}
bf = [R + f"sigma/boot_b{b}.npz" for b in range(1, 201)]
assert all(os.path.exists(f) for f in bf)
Rb = np.array([U @ load(f)["xs"] for f in bf]); sig = Rb.std(0, ddof=1)
bseeds = {load(f)["meta"]["bootstrap_seed"] for f in bf}; O["sigma"] = {"n": len(bf), "distinct_seeds": len(bseeds),
    "all_pseudo_seed_349999": all(load(f)["meta"]["pseudo_seed"] == 349999 for f in bf[:5] + bf[-5:])}
def stats(files):
    P = [load(f) for f in files]; fh = np.array([U @ p["xs"] for p in P]); ft = np.array([U @ p["xt"] for p in P])
    rel = (fh - ft) / ft; pull = (fh - ft) / sig; n = len(P)
    m, se = rel.mean(0), rel.std(0, ddof=1) / math.sqrt(n); t = m / se; mu, sd = pull.mean(0), pull.std(0, ddof=1)
    c68, c95 = np.mean(np.abs(pull) <= 1, 0), np.mean(np.abs(pull) <= 1.96, 0)
    k = int(np.argmax(np.abs(t)))
    return {"n": n, "distinct_seeds": len({p["meta"]["pseudo_seed"] for p in P}), "max_abs_t": round(float(np.abs(t).max()), 2), "argmax_t": names[k],
            "argmax_rel_pct": round(100 * m[k], 3), "argmax_mean_pull": round(float(mu[k]), 2),
            "n_t_gt_3p6": int((np.abs(t) > 3.6).sum()), "n_pull_gt_half_and_t_gt_3": int(((np.abs(mu) > 0.5) & (np.abs(t) > 3)).sum()),
            "pooled_cov68": round(float(np.mean(np.abs(pull) <= 1)), 4), "pooled_cov95": round(float(np.mean(np.abs(pull) <= 1.96)), 4),
            "min_cov68": round(float(c68.min()), 3), "min_cov95": round(float(c95.min()), 3),
            "n_functionals_cov68_zero": int((c68 == 0).sum()),
            "pull_sd_median_min_max": [round(float(np.median(sd)), 3), round(float(sd.min()), 3), round(float(sd.max()), 3)],
            "highW_rel_pct": {nm: round(100 * m[ix[nm]], 3) for nm in HW}, "max_abs_rel_pct": round(100 * float(np.abs(m).max()), 2),
            "argmax_rel": names[int(np.argmax(np.abs(m)))]}, rel, fh, ft, P
G = {}
for tag, pat in (("nominal", "nominal_a0_s*.npz"), ("eavail", "eavail_shape_a1_s*.npz"), ("q3", "q3_given_eavail_w_a0.3_s*.npz")):
    G[tag] = stats(sorted(glob.glob(R + "dev/" + pat)))
    O[tag] = G[tag][0]
O["C3_pass"] = O["nominal"]["max_abs_t"] <= 3.6 and O["nominal"]["n_pull_gt_half_and_t_gt_3"] == 0
O["eavail"]["EW29_rel_pct"] = round(100 * G["eavail"][1].mean(0)[ix["EW29"]], 3)
O["q3"]["EW41_rel_pct"] = round(100 * G["q3"][1].mean(0)[ix["EW41"]], 3)
d1 = json.load(open(DEP + "/docs/orchestration/state/s5c/d1/d1_summary.json"))["groups"]["split_F2"]
O["purity_D1_highW_pct"] = {nm: round(100 * d1["mean_rel"][ix[nm]], 3) for nm in HW}
# C2 permutation with the full sigma
a_, p_ = load(R + "c2/c2_rep_a.npz"), load(R + "c2/c2_perm1.npz")
O["C2_perm_max_over_sigma"] = float(np.max(np.abs(U @ p_["xs"] - U @ a_["xs"]) / sig))
# C1: every negweight-refined product (incl. diag), content-checked, not only 'ran'
nw = sorted(glob.glob(R + "dev/*.npz") + glob.glob(R + "sigma/boot_b*.npz") + glob.glob(R + "c2/*.npz") + [R + "c7/data_negweight.npz"] + glob.glob(R + "diag/diag_prior_*.npz"))
bad = []
for f in nw:
    e = load(f)["meta"].get("refinement", {})
    ok = (e.get("ran") is True and e.get("n_negative", 0) > 0 and e.get("sum_negative", 0) < 0 and np.isfinite(e.get("refined_sum", np.nan))
          and 0 < e.get("n_eff_refined", 0) and "clipped_fraction" in e
          and e.get("classifier_params", {}).get("random_state") in (45, 46) and e["classifier_params"].get("deterministic") is True
          and e["classifier_params"].get("bin_construct_sample_cnt") == 2147483647 and e["classifier_params"].get("num_leaves") == 8)
    if not ok: bad.append(os.path.basename(f))
O["C1"] = {"n_checked": len(nw), "n_in_author_population(dev+sigma+c2+data)": len(nw) - len(glob.glob(R + "diag/diag_prior_*.npz")), "failing": bad}
# refinement evidence ranges over dev nominal
ev = [p["meta"]["refinement"] for p in G["nominal"][4]]
O["C1_nominal_ranges"] = {k: [float(min(e[k] for e in ev)), float(max(e[k] for e in ev))] for k in ("refined_over_signed", "clipped_fraction", "n_eff_refined")}
# signal-only departure diagnostic, paired by seed
D = {}
for tag, t, a in (("eavail", "eavail_shape", "1"), ("q3", "q3_given_eavail_w", "0.3")):
    rs, rb, xs_s, xs_b, same_xt, meta_ok = [], [], [], [], [], []
    for f in sorted(glob.glob(R + f"diag/diag_sigonly_{t}_a{a}_s*.npz")):
        seed = int(f.rsplit("_s", 1)[1][:-4]); s, b = load(f), load(R + f"dev/{t}_a{a}_s{seed}.npz")
        same_xt.append(bool(np.array_equal(s["xt"], b["xt"])))
        m = s["meta"]; meta_ok.append((m.get("no_background") is True, m["refinement"].get("ran") is False, m["refinement"].get("n_template_rows") == 0,
                                        m["experiment"]["pseudo_background_events"] == 0.0, m["split_key"] == b["meta"]["split_key"], m["code_sha256"]["s5n_pseudo.py"][:8]))
        rs.append((U @ s["xs"] - U @ s["xt"]) / (U @ s["xt"])); rb.append((U @ b["xs"] - U @ b["xt"]) / (U @ b["xt"]))
        xs_s.append(U @ s["xs"]); xs_b.append(U @ b["xs"])
    rs, rb = np.array(rs), np.array(rb); d = rs - rb
    nomx = G["nominal"][2].mean(0)
    k7 = ix["EW7"]
    D[tag] = {"n": len(rs), "xtrue_bitwise_equal_to_dev_same_seed": same_xt, "meta(no_bkg, not_refined, 0 tmpl, 0 bkg events, same split, code)": meta_ok,
              "sigonly_max_abs_mean_rel_pct": round(100 * float(np.abs(rs.mean(0)).max()), 2), "sigonly_argmax": names[int(np.argmax(np.abs(rs.mean(0))))],
              "bkgincl_same_seeds_max_abs_mean_rel_pct": round(100 * float(np.abs(rb.mean(0)).max()), 2),
              "max_abs_mean_diff_pp": round(100 * float(np.abs(d.mean(0)).max()), 2), "argmax_diff": names[int(np.argmax(np.abs(d.mean(0))))],
              "median_abs_mean_diff_pp": round(100 * float(np.median(np.abs(d.mean(0)))), 3),
              "max_abs_diff_over_its_se": round(float(np.max(np.abs(d.mean(0)) / (d.std(0, ddof=1) / math.sqrt(len(d))))), 1),
              "median_abs_mean_rel_sigonly_pct": round(100 * float(np.median(np.abs(rs.mean(0)))), 2),
              "spearman_like_corr_sigonly_vs_bkgincl": round(float(np.corrcoef(rs.mean(0), rb.mean(0))[0, 1]), 5),
              "EW7_unfolded_over_nominal_sigonly": round(float(np.mean([x[k7] for x in xs_s]) / nomx[k7]), 4),
              "EW7_truth_over_nominal": round(float(np.mean([x[k7] for x in G[tag][3][:len(rs)]]) / G["nominal"][3].mean(0)[k7]), 4)}
O["signal_only_diag"] = D
json.dump(O, open(H + "/r8_fulln.json", "w"), indent=1, default=str); print(json.dumps(O, indent=1, default=str))
