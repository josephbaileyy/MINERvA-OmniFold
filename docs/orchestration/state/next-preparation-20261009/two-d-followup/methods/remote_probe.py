"""Read-only login-node probe for two-d-followup Task A item 4 (no training, no event loop, no unfold).

Run from the Perlmutter canonical checkout root after `source setup_salloc_env.sh`:
    python3 - < remote_probe.py > remote_probe.json

Reads saved 2D products and weight columns of the current universe omnifile. Emits digests,
counts, ratios and bin indices only: no data-event value, sum or count leaves the cluster.
"""
import hashlib
import json
import os
import re
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
B = "2d-unfolding"
UNI = f"{B}/runEventLoopOmniFold_MEFHC_universes_full.root"
ADOPTED = f"{B}/uq/universe_sweep_fluxfix"
PN = f"{B}/uq/purity_newomni"
CV42 = f"{B}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
PN_CV = f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root"
HISTS = ["hBkgReco2D", "hMeasSub2D", "hMeasTrain2D", "hTruth2D", "hUnfold2D", "hEffNum", "hEffDen",
         "hOFInputTruth2D", "hOFTruthDenom2D", "hXSec2D"]  # hDataReco2D compared, values not emitted
PARAMS = ["dataPOT", "mcPOT", "potScale", "nIterations", "fluxIntegral_m2_per_POT", "nNucleons"]


def arr(path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    if not h:
        f.Close()
        return None
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])
    f.Close()
    return a


def params(path):
    f = ROOT.TFile.Open(path)
    out = {}
    for p in PARAMS:
        o = f.Get(p)
        out[p] = float(o.GetVal()) if o else None
    keys = sorted(k.GetName() for k in f.GetListOfKeys())
    f.Close()
    return out, keys


def compare_products(a, b):
    """Which saved histograms and parameters differ between two products (max relative difference)."""
    pa, ka = params(a)
    pb, kb = params(b)
    out = {"params_equal": {p: pa[p] == pb[p] for p in PARAMS}, "keys_equal": ka == kb, "hist_max_rel_diff": {}}
    for h in HISTS + ["hDataReco2D"]:
        x, y = arr(a, h), arr(b, h)
        if x is None or y is None:
            out["hist_max_rel_diff"][h] = None
            continue
        den = np.maximum(np.abs(y), 1e-300)
        out["hist_max_rel_diff"][h] = float(np.max(np.abs(x - y) / den * (np.abs(y) > 0))) if np.any(y) else float(np.max(np.abs(x)))
    return out


def column(tree, name):
    tree.SetBranchStatus("*", 0)
    tree.SetBranchStatus(name, 1)
    a = ROOT.RDataFrame(tree).AsNumpy([name])[name].astype(np.float64)
    tree.SetBranchStatus("*", 1)
    return np.ascontiguousarray(a)


res = {"host": os.uname().nodename}

# 1. May / July zero-change universes against their CVs: which saved inputs differ?
res["adopted_EtaNCEL_0_vs_CV42"] = compare_products(f"{ADOPTED}/2d_xsec_MEFHC_5iter_lgbm_uni_full_EtaNCEL_0.root", CV42)
res["adopted_EtaNCEL_0_vs_MaNCEL_0"] = compare_products(f"{ADOPTED}/2d_xsec_MEFHC_5iter_lgbm_uni_full_EtaNCEL_0.root",
                                                        f"{ADOPTED}/2d_xsec_MEFHC_5iter_lgbm_uni_full_MaNCEL_0.root")
res["pn_EtaNCEL_0_vs_pn_CV"] = compare_products(f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_EtaNCEL_0.root", PN_CV)
res["pn_NormNCRES_0_vs_pn_CV"] = compare_products(f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_NormNCRES_0.root", PN_CV)
res["CV42_vs_pn_CV"] = compare_products(CV42, PN_CV)
res["adopted_file_mtimes"] = {n: os.stat(f"{ADOPTED}/2d_xsec_MEFHC_5iter_lgbm_uni_full_{n}.root").st_mtime
                              for n in ("EtaNCEL_0", "MaNCEL_0", "NormNCRES_0", "MaRES_0")}
res["CV42_mtime"] = os.stat(CV42).st_mtime

# 2. Weight columns of the current universe omnifile.
f = ROOT.TFile.Open(UNI)
cols = {}
for tree in ("mc_signal_reco", "mc_background"):
    t = f.Get(tree)
    names = [b.GetName() for b in t.GetListOfBranches()]
    base = "w_truth" if tree == "mc_signal_reco" else "w_bkg"
    want = [n for n in names if re.match(rf"{base}_(Rvn1pi|Rvp1pi|EtaNCEL|MaNCEL|NormNCRES)_\d+$", n)]
    cv = column(t, base)
    rec = {}
    for n in want:
        w = column(t, n)
        r = np.divide(w, cv, out=np.ones_like(w), where=cv != 0) - 1.0
        rec[n] = {"sha256_float64": hashlib.sha256(w.tobytes()).hexdigest(),
                  "equal_to_cv": bool(np.array_equal(w, cv)),
                  "frac_rows_differing_from_cv": float(np.mean(w != cv)),
                  "rms_ratio_minus_1": float(np.sqrt(np.mean(r ** 2))), "max_abs_ratio_minus_1": float(np.max(np.abs(r)))}
    pairs = {}
    for i in (0, 1):
        a, b = f"{base}_Rvn1pi_{i}", f"{base}_Rvp1pi_{i}"
        if a in want and b in want:
            x, y = column(t, a), column(t, b)
            pairs[str(i)] = {"identical": bool(np.array_equal(x, y)), "frac_rows_differing": float(np.mean(x != y)),
                             "max_abs_diff_over_cv": float(np.max(np.abs(x - y) / np.maximum(np.abs(cv), 1e-300)))}
    cols[tree] = {"branches": rec, "Rvn1pi_vs_Rvp1pi": pairs, "entries": int(t.GetEntries())}
res["weights"] = cols

# 3. The Flux-background anomaly in the July sweep.
bcv = arr(PN_CV, "hBkgReco2D")
flux = []
for u in range(100):
    b = arr(f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Flux_{u}.root", "hBkgReco2D")
    d = np.abs(b - bcv)
    k = np.unravel_index(np.argmax(d), d.shape)
    rel = np.divide(b, bcv, out=np.ones_like(b), where=bcv > 0) - 1
    flux.append({"u": u, "max_abs_change_over_cv_max": float(d.max() / bcv.max()), "cell": [int(k[0]), int(k[1])],
                 "rel_change_at_cell": float(rel[k]), "max_abs_rel_change_any_cell_with_bkg": float(np.max(np.abs(rel[bcv > 0])))})
flux.sort(key=lambda r: -r["max_abs_change_over_cv_max"])
res["pn_flux_bkg_top5"] = flux[:5]
res["pn_flux_bkg_median_of_max"] = float(np.median([r["max_abs_change_over_cv_max"] for r in flux]))
t = f.Get("mc_background")
worst = flux[0]["u"]
cv = column(t, "w_bkg")
for u in sorted({worst, flux[len(flux) // 2]["u"]}):
    w = column(t, f"w_bkg_Flux_{u}")
    r = np.divide(w, cv, out=np.ones_like(w), where=cv != 0)
    res.setdefault("w_bkg_flux_ratio", {})[str(u)] = {
        "quantiles_0_1_50_99_100": [float(np.quantile(r, q)) for q in (0, 0.01, 0.5, 0.99, 1)],
        "n_ratio_gt_2": int(np.sum(r > 2)), "n_ratio_gt_10": int(np.sum(r > 10)), "n_ratio_lt_0": int(np.sum(r < 0)),
        "frac_cv_zero": float(np.mean(cv == 0))}
f.Close()
json.dump(res, sys.stdout, indent=1, sort_keys=True)
sys.stdout.write("\n")
