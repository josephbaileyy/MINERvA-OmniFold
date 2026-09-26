#!/usr/bin/env python3
"""Review round 2 (independent): recompute K1-K5, development_exit, A1-A5 and the verdict of
contract amendment 3 from the cached U@f (r2_cache.npz) plus B0 references. Does not import the
campaign's analysis code (U came from s5c_coverage.reported_functionals in r2_load.py)."""
import glob
import hashlib
import json
import math
import re
import sys

import numpy as np

sys.dont_write_bytecode = True
DEPLOY = "/pscratch/sd/j/josephrb/s5e-20260925/deploy/2f958652/nd-unfolding"
sys.path.insert(0, DEPLOY)
import s5c_coverage as sc  # U only
import project_cov_nd as pc

R2 = "/pscratch/sd/j/josephrb/s5e-20260925/review2"
IN = R2 + "/inputs"
S5N = "/pscratch/sd/j/josephrb/s5n-20260925/runs"
DIAG = "/pscratch/sd/j/josephrb/s5e-20260925/runs/diag"
U, names = sc.reported_functionals(json.load(open(IN + "/s5c_contract.json")))
am = json.load(open(IN + "/contract-amendment-3-candidate-R-and-assessment.json"))
cr = am["criteria"]
C = np.load(R2 + "/r2_cache.npz")
keys = [k for k in C.files if k.startswith("f|")]
NEW = 42


def uf(path, want_t=False):
    z = np.load(path, allow_pickle=False)
    f = U @ np.asarray(z["xsec_flat"], float)
    if want_t:
        return f, U @ np.asarray(z["xtrue_flat"], float)
    return f


def group(prefix):
    ks = sorted(k[2:] for k in keys if k[2:].rsplit("/", 1)[0] == prefix)
    return ks


def seed_of(k):
    return int(re.search(r"_s(\d+)$", k).group(1))


# ---- sigma (R, dev experiment 700000, 100 replicas)
sig_keys = group("dev/sigma")
bs = sorted(int(re.search(r"boot_b(\d+)$", k).group(1)) for k in sig_keys)
assert bs == list(range(1, 101)), bs
reps = np.array([C["f|dev/sigma/boot_b%d" % b] for b in range(1, 101)])
sig = reps.std(0, ddof=1)
out = {"sigma_boot_seeds": [bs[0], bs[-1], len(bs)]}
hashes = [bytes(C["h|dev/sigma/boot_b%d" % b]) for b in range(1, 101)]
out["sigma_replicas_distinct"] = len(set(hashes))
base700 = C["f|dev/k1_R/nominal_a0_s700000"]
out["sigma_rep_equal_to_unbootstrapped_700000"] = int(sum(np.array_equal(r, base700) for r in reps))
out["k5_b16_replicas"] = {b: {"finite": bool(np.all(np.isfinite(C["f|dev/sigma/boot_b%d" % b]))),
                              "max_abs_z_vs_other_reps": float(np.max(np.abs(C["f|dev/sigma/boot_b%d" % b] - np.delete(reps, b - 1, 0).mean(0)) / np.delete(reps, b - 1, 0).std(0, ddof=1)))}
                          for b in range(16, 21)}
out["sigma_rel_pct_EW_median"] = float(np.median(100 * sig[:NEW] / np.abs(reps.mean(0)[:NEW])))


def point(ks):
    F = np.array([C["f|" + k] for k in ks])
    T = np.array([C["t|" + k] for k in ks])
    rel = (F - T) / T
    pull = (F - T) / sig
    n = len(ks)
    m = rel.mean(0)
    se = rel.std(0, ddof=1) / math.sqrt(n)
    return {"n": n, "rel": rel, "pull": pull, "m": m, "se": se, "t": m / se, "mp": pull.mean(0), "psd": pull.std(0, ddof=1),
            "F": F, "T": T, "seeds": [seed_of(k) for k in ks]}


def c3(p):
    bt = np.abs(p["t"]) > cr["C3"]["t_crit"]
    bp = (np.abs(p["mp"]) > cr["C3"]["mean_pull_max"]) & (np.abs(p["t"]) > cr["C3"]["t_with_pull"])
    return {"max_abs_t": float(np.abs(p["t"]).max()), "argmax_t": names[int(np.abs(p["t"]).argmax())],
            "n_t_gt_3.6": int(bt.sum()), "n_pull_and_t": int(bp.sum()), "max_abs_mean_pull": float(np.abs(p["mp"]).max()),
            "pass": bool(not bt.any() and not bp.any())}


def ewsum(p):
    ew = np.abs(p["m"][:NEW])
    return {"ew_median_abs_pct": 100 * float(np.median(ew)), "ew_max_abs_pct": 100 * float(ew.max()), "ew_argmax": f"EW{int(ew.argmax())}"}


def calib(p):
    n = p["n"]
    se = 1 / math.sqrt(2 * (n - 1))
    frac = float(np.mean((p["psd"] < 1 - 3 * se) | (p["psd"] > 1 + 3 * se)))
    pooled = float(p["pull"].std(ddof=1))
    nr, q = reps.shape[0], NEW
    Cv = np.cov(reps[:, :q], rowvar=False, ddof=1)
    h = (nr - q - 2) / (nr - 1)
    Ci = np.linalg.inv(Cv)
    r = (p["F"] - p["T"])[:, :q]
    d2 = np.einsum("ij,jk,ik->i", r, Ci, r)
    lo, hi = cr["calibration"]["mahalanobis_mean_window_times_p"]
    return {"pooled_pull_sd": pooled, "frac_outside_3se": frac, "n_outside": int(round(frac * len(p["psd"]))), "se": se,
            "maha_mean_hartlap": float(h * d2.mean()), "maha_mean_raw": float(d2.mean()), "maha_median_hartlap": float(h * np.median(d2)),
            "hartlap": h, "window": [lo * q, hi * q],
            "pass": bool(0.9 <= pooled <= 1.1 and frac <= 0.1 and lo * q <= h * d2.mean() <= hi * q)}


# ---- B0 s5n references
b0 = {}
for nm, pat in (("eavail", "eavail_shape_a1_s*.npz"), ("q3", "q3_given_eavail_w_a0.3_s*.npz")):
    fs = sorted(glob.glob(f"{S5N}/dev/{pat}"))
    FT = [uf(f, True) for f in fs]
    F = np.array([a for a, _ in FT]); T = np.array([b for _, b in FT])
    rel = (F - T) / T
    m = rel.mean(0)
    b0[nm] = {"n": len(fs), "seeds": [int(re.search(r"_s(\d+)\.npz", f).group(1)) for f in fs],
              "ew_median_abs_pct": 100 * float(np.median(np.abs(m[:NEW]))), "ew_max_abs_pct": 100 * float(np.abs(m[:NEW]).max())}
    metas = [json.loads(str(np.load(f, allow_pickle=False)["meta"])) for f in fs[:3]]
    b0[nm]["meta_sample"] = [(mm.get("truth"), mm.get("amplitude"), (mm.get("eavail_ratio_sha256") or "")[:8], mm.get("refinement", {}).get("classifier_params", {}).get("n_estimators")) for mm in metas]
out["B0_s5n"] = {k: {kk: (vv if kk != "seeds" else [min(vv), max(vv)]) for kk, vv in v.items()} for k, v in b0.items()}

# ---- development
K1 = point(group("dev/k1_R"))
K1b = point(group("dev/k1_B0"))
assert K1["seeds"] == K1b["seeds"] == list(range(700000, 700020))
pd = K1["rel"] - K1b["rel"]
pt = pd.mean(0) / (pd.std(0, ddof=1) / math.sqrt(pd.shape[0]))
K2 = point(group("dev/k2")); K3 = point(group("dev/k3"))
assert K2["seeds"] == list(range(701000, 701020)) and K3["seeds"] == list(range(702000, 702020))
tol = cr["departure_not_worse_relative"]
dev = {"K1_R": {**c3(K1), **ewsum(K1), "pooled_pull_sd": float(K1["pull"].std(ddof=1))},
       "K1_B0": {**c3(K1b), **ewsum(K1b)},
       "paired_R_minus_B0": {"max_abs_t": float(np.abs(pt).max()), "max_abs_mean_pct": 100 * float(np.abs(pd.mean(0)).max())}}
for nm, p, ref in (("K2", K2, b0["eavail"]), ("K3", K3, b0["q3"])):
    s = ewsum(p)
    dev[nm] = {**s, "b0_median": ref["ew_median_abs_pct"], "b0_max": ref["ew_max_abs_pct"],
               "median_ratio": s["ew_median_abs_pct"] / ref["ew_median_abs_pct"], "max_ratio": s["ew_max_abs_pct"] / ref["ew_max_abs_pct"],
               "not_worse": bool(s["ew_median_abs_pct"] <= (1 + tol) * ref["ew_median_abs_pct"] and s["ew_max_abs_pct"] <= (1 + tol) * ref["ew_max_abs_pct"]),
               "strictly_improves_both": bool(s["ew_median_abs_pct"] < ref["ew_median_abs_pct"] and s["ew_max_abs_pct"] < ref["ew_max_abs_pct"])}
kb = C["f|dev/k4/k4_base"]
dev["K4"] = {nm: {"max_over_sigma": float(np.max(np.abs(C["f|dev/k4/" + nm] - kb) / sig)), "bitwise": bool(np.array_equal(C["f|dev/k4/" + nm], kb))}
             for nm in ("k4_seed43", "k4_perm1", "k4_perm2")}
dev["K4"]["base_vs_K1_700000_bitwise"] = bool(np.array_equal(kb, base700))
dev["K4"]["base_vs_K1_700000_max_over_sigma"] = float(np.max(np.abs(kb - base700) / sig))
dev["K5"] = calib(K1)
dev["development_exit_as_amended"] = bool(dev["K1_R"]["pass"] and dev["K2"]["not_worse"] and dev["K3"]["not_worse"])
dev["development_exit_original_contract_text"] = bool(dev["K1_R"]["pass"] and dev["K2"]["strictly_improves_both"] and dev["K3"]["strictly_improves_both"])
out["development"] = dev

# ---- assessment
P = {}
spans = {"nominal": (800000, 40), "eavail_gibuu": (801000, 20), "q3": (802000, 20), "W1": (803000, 20), "W2": (804000, 20), "W3": (805000, 20)}
for k, (s0, n) in spans.items():
    P[k] = point(group("assess/" + k))
    assert P[k]["seeds"] == list(range(s0, s0 + n)), (k, P[k]["seeds"][:3])
A = {"A1": c3(P["nominal"]), "A2": calib(P["nominal"])}
ab = C["f|assess/a3/a3_base"]
a3 = {nm: float(np.max(np.abs(C["f|assess/a3/" + nm] - ab) / sig)) for nm in ("a3_seed43", "a3_perm1", "a3_perm2")}
a3_bit = {nm: bool(np.array_equal(C["f|assess/a3/" + nm], ab)) for nm in ("a3_seed43", "a3_perm1", "a3_perm2")}
a3["base_vs_nominal_800000_bitwise"] = bool(np.array_equal(ab, C["f|assess/nominal/nominal_a0_s800000"]))
dR = C["f|assess/data/data_R"]; up = C["f|assess/data/data_R_upcast"]
j1 = C["f|assess/data/data_R_jitteredge1"]; j2 = C["f|assess/data/data_R_jitteredge2"]
dboot = np.array([C["f|assess/data/boot/boot_b%d" % b] for b in range(1, 101)])
dhash = [bytes(C["h|assess/data/boot/boot_b%d" % b]) for b in range(1, 101)]
dsig = dboot.std(0, ddof=1)
jm = np.maximum(np.abs(j1 - up), np.abs(j2 - up)) / dsig
A["A3"] = {"seed_perm_max_over_sigma": a3, "seed_perm_bitwise": a3_bit, "upcast_equals_data_R": bool(np.array_equal(up, dR)),
           "rounding_median": float(np.median(jm)), "rounding_max": float(jm.max()), "rounding_argmax": names[int(jm.argmax())],
           "rounding_n_gt_1": int((jm > 1).sum()), "rounding_EW_median": float(np.median(jm[:NEW])),
           "rounding_rel_pct_median": 100 * float(np.median(np.maximum(np.abs(j1 - up), np.abs(j2 - up)) / np.abs(up))),
           "rounding_rel_pct_max": 100 * float(np.max(np.maximum(np.abs(j1 - up), np.abs(j2 - up)) / np.abs(up))),
           "jit1_vs_jit2_median_over_dsig": float(np.median(np.abs(j1 - j2) / dsig)),
           "data_boot_distinct": len(set(dhash)), "data_boot_equal_to_data_R": int(sum(np.array_equal(r, dR) for r in dboot))}
A["A3"]["pass"] = bool(max(v for k, v in a3.items() if k.startswith("a3_")) <= cr["seed_movement_max_sigma"]
                       and A["A3"]["rounding_median"] <= cr["rounding_median_max_sigma"] and A["A3"]["rounding_max"] <= cr["rounding_max_sigma"])
# B0 rounding probe (diagnosis) on the same scale
b0up = uf(f"{DIAG}/drv/data_upcast.npz"); b0d = uf(f"{DIAG}/drv/data_b0.npz")
b0j1 = uf(f"{DIAG}/rep/rep_data_jitteredge1.npz"); b0j2 = uf(f"{DIAG}/rep/rep_data_jitteredge2.npz")
b0m = np.maximum(np.abs(b0j1 - b0up), np.abs(b0j2 - b0up))
A["B0_rounding_probe_diag"] = {"b0_upcast_equals_b0_data": bool(np.array_equal(b0up, b0d)),
                               "rel_pct_median": 100 * float(np.median(b0m / np.abs(b0up))), "rel_pct_max": 100 * float(np.max(b0m / np.abs(b0up))),
                               "over_R_data_sigma_median": float(np.median(b0m / dsig)), "over_R_data_sigma_max": float(np.max(b0m / dsig)),
                               "over_R_data_sigma_argmax": names[int(np.argmax(b0m / dsig))],
                               "fails_A3_bounds_on_R_data_sigma": bool(np.median(b0m / dsig) > 0.3 or np.max(b0m / dsig) > 1.0)}
for p_ in (f"{DIAG}/drv/data_upcast.npz", f"{DIAG}/rep/rep_data_jitteredge1.npz", f"{DIAG}/drv/data_b0.npz"):
    mm = json.loads(str(np.load(p_, allow_pickle=False)["meta"]))
    A["B0_rounding_probe_diag"].setdefault("metas", []).append({k: mm.get(k) for k in ("schema", "construction", "coords", "jitter_f32", "jitter_mode", "refine_capacity", "iters")} |
                                                                {"ref_nest": (mm.get("refinement") or {}).get("classifier_params", {}).get("n_estimators")})
# A4
adopted_cells = json.load(open(IN + "/bias_vs_adopted.json"))["cells"]
adopted = np.array([c["sigma_adopted_pct"] for c in adopted_cells]) / 100
# EW index -> (eavail, W) bins from U itself
shape = tuple(len(pc.AXIS_EDGES[a]) - 1 for a in sc.AXES)
idx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
align = []
for i in range(NEW):
    cells = np.flatnonzero(U[i] != 0)
    ee, ww = set(idx[2][cells].tolist()), set(idx[4][cells].tolist())
    align.append(ee == {adopted_cells[i]["eavail_bin"]} and ww == {adopted_cells[i]["W_bin"]} and adopted_cells[i]["cell"] == f"EW{i}")
md = np.max(np.abs(np.array([P[w]["m"][:NEW] for w in ("W1", "W2", "W3")])), axis=0)
which = np.argmax(np.abs(np.array([P[w]["m"][:NEW] for w in ("W1", "W2", "W3")])), axis=0)
inside = md <= adopted
A["A4"] = {"EW_alignment_all_ok": bool(all(align)), "n_inside": int(inside.sum()), "cells_inside": [f"EW{i}" for i in np.flatnonzero(inside)],
           "md_pct": (100 * md).round(3).tolist(), "argmax_deformation_counts": {w: int((which == j).sum()) for j, w in enumerate(("W1", "W2", "W3"))},
           "margin_min_over_inside_(adopted-md)/adopted": float(np.min((adopted - md)[inside] / adopted[inside])) if inside.any() else None,
           "n_inside_if_gibuu_q3_also_counted": int((np.max(np.abs(np.array([P[w]["m"][:NEW] for w in ("W1", "W2", "W3", "eavail_gibuu", "q3")])), 0) <= adopted).sum()),
           "n_inside_per_deformation": {w: int((np.abs(P[w]["m"][:NEW]) <= adopted).sum()) for w in ("W1", "W2", "W3", "eavail_gibuu", "q3")},
           "md_se_max_pct": 100 * float(np.max(np.array([P[w]["se"][:NEW] for w in ("W1", "W2", "W3")]))),
           "n_inside_within_2se_of_boundary": int(np.sum(np.abs(md - adopted) < 2 * np.max(np.array([P[w]["se"][:NEW] for w in ("W1", "W2", "W3")]), 0))),
           "pass_nonempty": bool(inside.any())}
# A5
b0reps = np.array([uf(f"{S5N}/sigma/boot_b{b}.npz") for b in range(1, 201)])
b0sig = b0reps.std(0, ddof=1)
ratio = sig[:NEW] / b0sig[:NEW]
m0 = json.loads(str(np.load(f"{S5N}/sigma/boot_b1.npz", allow_pickle=False)["meta"]))
A["A5"] = {"median": float(np.median(ratio)), "max": float(ratio.max()), "argmax": f"EW{int(ratio.argmax())}", "min": float(ratio.min()),
           "b0_sigma_meta": {k: m0.get(k) for k in ("pseudo_seed", "bootstrap_seed", "truth", "data")} | {"ref_nest": m0["refinement"]["classifier_params"]["n_estimators"]},
           "ratio_all153_median": float(np.median(sig / b0sig)), "ratio_all153_max": float(np.max(sig / b0sig)),
           "pass": bool(np.median(ratio) <= 1.25 and ratio.max() <= 2.0)}
A["data"] = {"R_minus_B0_median_abs_pct": 100 * float(np.median(np.abs(dR / b0d - 1))), "max_abs_pct": 100 * float(np.max(np.abs(dR / b0d - 1))),
             "argmax": names[int(np.argmax(np.abs(dR / b0d - 1)))], "R_minus_B0_over_dsig_median": float(np.median(np.abs(dR - b0d) / dsig)),
             "dsig_over_sig_EW_median": float(np.median(dsig[:NEW] / sig[:NEW])), "dsig_rel_pct_EW_median": 100 * float(np.median(dsig[:NEW] / np.abs(dR[:NEW])))}
A["verdict"] = "A_PASS_DEVELOPMENT_SCALE" if (A["A1"]["pass"] and A["A2"]["pass"] and A["A3"]["pass"] and A["A5"]["pass"] and A["A4"]["pass_nonempty"]) else "A_FAIL"
A["failed"] = [k for k in ("A1", "A2", "A3", "A5") if not A[k]["pass"]] + ([] if A["A4"]["pass_nonempty"] else ["A4"])
for k in ("eavail_gibuu", "q3", "W1", "W2", "W3", "nominal"):
    A.setdefault("points", {})[k] = {**ewsum(P[k]), **c3(P[k])}
out["assessment"] = A
# compare against committed receipts
dr = json.load(open(IN + "/dev_receipt.json")); ar = json.load(open(IN + "/assess_receipt.json"))
cmp = {"K1_max_abs_t": (dev["K1_R"]["max_abs_t"], dr["K1"]["R"]["max_abs_t"]),
       "K1_B0_max_abs_t": (dev["K1_B0"]["max_abs_t"], dr["K1"]["B0_same_seeds"]["max_abs_t"]),
       "paired_max_t": (dev["paired_R_minus_B0"]["max_abs_t"], dr["K1"]["paired_R_minus_B0"]["max_abs_t"]),
       "K2_med": (dev["K2"]["ew_median_abs_pct"], dr["K2_K3"]["K2"]["candidate"]["ew_median_abs_pct"]),
       "K2_max": (dev["K2"]["ew_max_abs_pct"], dr["K2_K3"]["K2"]["candidate"]["ew_max_abs_pct"]),
       "K3_med": (dev["K3"]["ew_median_abs_pct"], dr["K2_K3"]["K3"]["candidate"]["ew_median_abs_pct"]),
       "K3_max": (dev["K3"]["ew_max_abs_pct"], dr["K2_K3"]["K3"]["candidate"]["ew_max_abs_pct"]),
       "B0_eavail_med": (b0["eavail"]["ew_median_abs_pct"], dr["B0_reference_s5n"]["eavail"]["ew_median_abs_pct"]),
       "K5_maha": (dev["K5"]["maha_mean_hartlap"], dr["K5"]["calibration_on_K1"]["mahalanobis_mean"]),
       "A1_max_t": (A["A1"]["max_abs_t"], ar["points"]["nominal"]["max_abs_t"]),
       "A2_pooled": (A["A2"]["pooled_pull_sd"], ar["A2"]["pooled_pull_sd"]), "A2_frac": (A["A2"]["frac_outside_3se"], ar["A2"]["fraction_pull_sd_outside_3se"]),
       "A2_maha": (A["A2"]["maha_mean_hartlap"], ar["A2"]["mahalanobis_mean"]),
       "A3_med": (A["A3"]["rounding_median"], ar["A3"]["data_rounding_probe_over_data_sigma"]["median"]),
       "A3_max": (A["A3"]["rounding_max"], ar["A3"]["data_rounding_probe_over_data_sigma"]["max"]),
       "A4_n": (A["A4"]["n_inside"], ar["A4"]["n_useful_cells"]), "A4_md_maxdiff": (float(np.max(np.abs(100 * md - np.array(ar["A4"]["model_dependence_by_EW_pct"])))), 0.0),
       "A5_med": (A["A5"]["median"], ar["A5"]["sigma_R_over_sigma_B0_EW_median"]), "A5_max": (A["A5"]["max"], ar["A5"]["max"]),
       "data_med": (A["data"]["R_minus_B0_median_abs_pct"], ar["data"]["method_sensitivity_R_minus_B0_pct"]["median_abs"]),
       "sigma_rel_pct_maxdiff": (float(np.max(np.abs(100 * sig / np.abs(reps.mean(0)) - np.array(dr["sigma_rel_pct"])))), 0.0)}
out["receipt_comparison"] = {k: {"mine": a, "receipt": b, "abs_diff": abs(a - b)} for k, (a, b) in cmp.items()}
out["A4_scope_matches_receipt"] = A["A4"]["cells_inside"] == ar["A4"]["cells_model_dependence_within_adopted_sigma"]
np.savez_compressed(R2 + "/r2_nominal_pulls.npz", mp=P["nominal"]["mp"], psd=P["nominal"]["psd"], sig=sig, dsig=dsig, b0sig=b0sig, jm=jm, b0m=b0m)
json.dump(out, open(R2 + "/r2_recompute.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float)[:20000])
