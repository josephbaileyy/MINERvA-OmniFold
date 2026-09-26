#!/usr/bin/env python3
"""Review round 2 (independent): load every s5e candidate product, audit its meta, and cache U@f.

Reads only. Writes r2_cache.npz and r2_integrity.json into the review2 directory.
"""
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np

sys.dont_write_bytecode = True
DEPLOY = "/pscratch/sd/j/josephrb/s5e-20260925/deploy/2f958652/nd-unfolding"
sys.path.insert(0, DEPLOY)
import s5c_coverage as sc  # U only

R2 = "/pscratch/sd/j/josephrb/s5e-20260925/review2"
IN = R2 + "/inputs"
RUNS = "/pscratch/sd/j/josephrb/s5e-20260925/runs"
S5N = "/pscratch/sd/j/josephrb/s5n-20260925/runs"

U, names = sc.reported_functionals(json.load(open(IN + "/s5c_contract.json")))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
RATIO_SHA = {k: sha(f"{IN}/{f}") for k, f in {
    "gibuu": "eavail-ratio-gibuu-over-genie.json", "W1": "eavail-ratio-nuwro-over-genie.json",
    "W2": "w2-genie-mec-over-cv-eavailW.json", "W3": "w3-nuwro-over-genie-pt-pz-eavail.json"}.items()}

DIRS = {"dev/k1_R": "R", "dev/k1_B0": "B0", "dev/k2": "R", "dev/k3": "R", "dev/k4": "R", "dev/sigma": "R",
        "assess/nominal": "R", "assess/eavail_gibuu": "R", "assess/q3": "R", "assess/W1": "R", "assess/W2": "R",
        "assess/W3": "R", "assess/a3": "R", "assess/data": "R", "assess/data/boot": "R"}
EXPECT = {"dev/k1_R": ("nominal", 0.0, None, (700000, 700019)), "dev/k1_B0": ("nominal", 0.0, None, (700000, 700019)),
          "dev/k2": ("eavail_shape", 1.0, "gibuu", (701000, 701019)), "dev/k3": ("q3_given_eavail_w", 0.3, None, (702000, 702019)),
          "dev/k4": ("nominal", 0.0, None, (700000, 700000)), "dev/sigma": ("nominal", 0.0, None, (700000, 700000)),
          "assess/nominal": ("nominal", 0.0, None, (800000, 800039)), "assess/eavail_gibuu": ("eavail_shape", 1.0, "gibuu", (801000, 801019)),
          "assess/q3": ("q3_given_eavail_w", 0.3, None, (802000, 802019)), "assess/W1": ("eavail_shape", 1.0, "W1", (803000, 803019)),
          "assess/W2": ("ratio_nd", 1.0, "W2", (804000, 804019)), "assess/W3": ("ratio_nd", 1.0, "W3", (805000, 805019)),
          "assess/a3": ("nominal", 0.0, None, (800000, 800000))}

cache, rows, problems = {}, [], []
xtrue_full = {}
for d, cand in DIRS.items():
    files = sorted(glob.glob(f"{RUNS}/cand/{d}/*.npz"))
    for p in files:
        z = np.load(p, allow_pickle=False)
        m = json.loads(str(z["meta"]))
        key = d + "/" + os.path.basename(p)[:-4]
        x = np.asarray(z["xsec_flat"], float)
        cache["f|" + key] = U @ x
        if "xtrue_flat" in z.files:
            xt = np.asarray(z["xtrue_flat"], float)
            cache["t|" + key] = U @ xt
            if d.startswith("assess/") and d.split("/")[1] in ("nominal", "eavail_gibuu", "W1", "W2", "W3"):
                xtrue_full.setdefault(d, []).append(xt)
        cache["h|" + key] = np.frombuffer(hashlib.sha256(x.tobytes()).digest(), dtype=np.uint8)
        cs = m.get("code_sha256", {})
        ref = m.get("refinement", {}) or {}
        cp = ref.get("classifier_params", {}) or {}
        ep = m.get("estimator_params") or []
        row = {"key": key, "schema": m.get("schema"), "candidate": cs.get("candidate"), "override": cs.get("candidate_refine_override"),
               "ref_n_est": cp.get("n_estimators"), "ref_leaves": cp.get("num_leaves"), "ref_rs": cp.get("random_state"),
               "ref_lr": cp.get("learning_rate"), "ref_threads": cp.get("num_threads"), "ref_bcsc": cp.get("bin_construct_sample_cnt"),
               "est_seed": m.get("estimator_seed"), "est_rs": [e.get("random_state") for e in ep],
               "est_nest": sorted({e.get("n_estimators") for e in ep}), "est_leaves": sorted({e.get("num_leaves") for e in ep}),
               "iters": m.get("iters"), "truth": m.get("truth"), "amplitude": m.get("amplitude"), "pseudo_seed": m.get("pseudo_seed"),
               "bootstrap_seed": m.get("bootstrap_seed"), "permute_seed": m.get("permute_seed"), "data": m.get("data"),
               "ratio_sha": m.get("eavail_ratio_sha256"), "npz_sha": m.get("input_npz_sha256"), "bkg_sha": m.get("bkg_dump_sha256"),
               "bkg_mode": m.get("bkg_mode"), "job": m.get("slurm_job"), "step": m.get("slurm_step"),
               "s5e_candidate_sha": cs.get("s5e_candidate.py"), "s5n_pseudo_sha": cs.get("s5n_pseudo.py"),
               "finite": bool(np.all(np.isfinite(x))), "nonzero": int(np.count_nonzero(x)), "has_xtrue": "xtrue_flat" in z.files,
               "meta_keys": sorted(m.keys()) if d == "assess/data" else None}
        if d == "assess/data":
            row["meta_excerpt"] = {k: m[k] for k in m if k not in ("code_sha256", "estimator_params")}
        rows.append(row)
        # checks
        exp = EXPECT.get(d)
        want_c = "B0" if d == "dev/k1_B0" else "R"
        if d != "assess/data" or os.path.basename(p) == "data_R.npz":
            if row["candidate"] != want_c:
                problems.append((key, "candidate", row["candidate"]))
            want = (400, 31) if want_c == "R" else (100, 8)
            if (row["ref_n_est"], row["ref_leaves"]) != want:
                problems.append((key, "refine params", row["ref_n_est"], row["ref_leaves"]))
        if exp:
            tr, amp, rk, (lo, hi) = exp
            if row["truth"] != tr or row["amplitude"] != amp:
                problems.append((key, "truth/amp", row["truth"], row["amplitude"]))
            if rk and row["ratio_sha"] != RATIO_SHA[rk]:
                problems.append((key, "ratio sha", row["ratio_sha"]))
            if not rk and row["ratio_sha"] not in (None,):
                problems.append((key, "unexpected ratio sha", row["ratio_sha"]))
            ps = row["pseudo_seed"]
            if ps is None or not (lo <= ps <= hi):
                problems.append((key, "pseudo seed", ps))
            mm = re.search(r"_s(\d+)$", key)
            if mm and int(mm.group(1)) != ps:
                problems.append((key, "filename seed", ps))
np.savez_compressed(R2 + "/r2_cache.npz", **cache, names=np.array(names))
np.savez_compressed(R2 + "/r2_xtrue_full.npz", **{k.replace("/", "__"): np.array(v) for k, v in xtrue_full.items()})
json.dump({"ratio_sha": RATIO_SHA, "rows": rows, "problems": problems}, open(R2 + "/r2_integrity.json", "w"), indent=1, default=str)
print("files", len(rows), "problems", len(problems))
for pr in problems[:50]:
    print(pr)
