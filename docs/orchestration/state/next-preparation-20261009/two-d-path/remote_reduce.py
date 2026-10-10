"""Read-only login-node reduction for the two-d-path design (no training, no event loop).

Run from the Perlmutter canonical checkout root after `source setup_salloc_env.sh`:
    python3 - < remote_reduce.py > remote_reduce.json

It reads existing 2D products and the two omnifiles and prints one JSON document:
per-cell widths of the adopted blocks, the existing centrals, and per-column float64 digests (no values) of the
CV-level branches in the CV omnifile and in the universe omnifile (row-order identity).
It writes nothing on the cluster.
"""
import hashlib
import json
import os
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.ROOT.DisableImplicitMT()

BASE = "2d-unfolding"
PRODUCTS = {
    "E_C": f"{BASE}/2d_crossSection_omnifold_MEFHC_5iter.root",
    "CV42_universe_file": f"{BASE}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
    **{f"seed{s}": f"{BASE}/seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed{s}.root" for s in range(1, 11)},
}
COV = {
    "universe": (f"{BASE}/uq/universe_stage2_MEFHC_full_matcorr_fluxfix/"
                 "uq_universe_covariance_full_matcorr_fluxfix.root", "hSigma_universe_total"),
    "boot_vl170": (f"{BASE}/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root", "hStd2D"),
    "ml": (f"{BASE}/uq/seedscan_lgbm_ml/uq_covariance_ml.root", "hStd2D"),
}
OMNI = {
    "cv_file": f"{BASE}/runEventLoopOmniFold_MEFHC.root",
    "universe_file": f"{BASE}/runEventLoopOmniFold_MEFHC_universes_full.root",
}
CV_BRANCHES = {
    "mc_signal_reco": ["sim", "sim_pz", "sim_pass", "w_reco", "MC", "MC_pz", "w_truth"],
    "mc_truth_denom": ["MC", "MC_pz", "w_truth"],
    "data": ["measured", "measured_pz", "measured_pass"],
    "mc_background": ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"],
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def th2(path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)])
    f.Close()
    return a


out = {"host": os.uname().nodename, "cwd": os.getcwd(), "products": {}, "cov": {}, "omnifile_columns": {}}

centrals = {}
for key, path in PRODUCTS.items():
    centrals[key] = th2(path, "hXSec2D")
    out["products"][key] = {"path": path, "sha256": sha256_file(path), "bytes": os.path.getsize(path)}

sig = {}
for key, (path, name) in COV.items():
    sig[key] = th2(path, name)
    out["cov"][key] = {"path": path, "object": name, "sha256": sha256_file(path)}

reported = centrals["E_C"] > 0
masks = {
    "E_C>0": reported,
    "CV42>0": centrals["CV42_universe_file"] > 0,
    "seed1>0": centrals["seed1"] > 0,
    "sigma_universe>0": sig["universe"] > 0,
    "sigma_boot>0": sig["boot_vl170"] > 0,
}
out["mask_counts"] = {k: int(v.sum()) for k, v in masks.items()}
out["masks_equal_to_E_C"] = {k: bool((v == reported).all()) for k, v in masks.items()}

idx = np.argwhere(reported)  # row-major (pT bin, pz bin), the paper's GlobalID order
out["cells"] = [[int(i), int(j)] for i, j in idx]
for key, a in centrals.items():
    out.setdefault("central", {})[key] = [float(a[i, j]) for i, j in idx]
for key, a in sig.items():
    out.setdefault("sigma_abs", {})[key] = [float(a[i, j]) for i, j in idx]

for fkey, path in OMNI.items():
    f = ROOT.TFile.Open(path)
    rec = {}
    for tree, branches in CV_BRANCHES.items():
        t = f.Get(tree)
        rec[tree] = {"entries": int(t.GetEntries()), "columns": {}}
        for b in branches:
            t.SetBranchStatus("*", 0)
            t.SetBranchStatus(b, 1)
            arr = ROOT.RDataFrame(t).AsNumpy([b])[b]
            if arr.dtype.kind == "S":  # char/bool branches arrive as one-byte strings
                arr = arr.astype("S1").view(np.uint8)
            elif arr.dtype.kind == "O":
                arr = np.fromiter((ord(v) if isinstance(v, (bytes, str)) else int(v) for v in arr),
                                  dtype=np.int64, count=len(arr))
            arr = np.ascontiguousarray(arr.astype(np.float64))
            # digest only: no event values or sums of the data leave the cluster
            rec[tree]["columns"][b] = {"sha256_float64": hashlib.sha256(arr.tobytes()).hexdigest()}
            del arr
        t.SetBranchStatus("*", 1)
    out["omnifile_columns"][fkey] = {"path": path, "trees": rec}
    f.Close()

json.dump(out, sys.stdout, indent=1, sort_keys=True)
sys.stdout.write("\n")
