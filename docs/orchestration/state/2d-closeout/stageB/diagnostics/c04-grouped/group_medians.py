#!/usr/bin/env python3
"""Per-bin median relative sigma by category (205 reported cells, E_U denominator), adopted vs C04+X01-repaired rollup.

Grouping = analyze_universes.category_for_band (what plot_uncertainty_fig6_7_style.py imports), applied to every
hCov_universe_<band> of the rollup. Statistical = the rollup's own bootstrap block (hCov_combined - hCov_universe_total),
and, separately, the VL170 boot300 hCov2D_reported that the Fig. 6/7 producer adds.
'legacy' grouping reproduces the note's App. A wording: GENIE Norm* bands -> Normalization, the flat 1.4% -> Models.
  python group_medians.py <repo>/2d-unfolding/uq <adopted.root> <repaired.root> <out.json>
"""
import hashlib, json, os, sys
import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)
uq, adopted, repaired, out = sys.argv[1:5]
sys.path.insert(0, uq)
from analyze_universes import CATEGORY_ORDER, category_for_band
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
CV = f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
BOOT = f"{D2}/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"
BANDS = ["Muon_Energy_MINOS", "Muon_Energy_MINERvA", "MinosEfficiency", "Flux", "MaRES", "MvRES", "MaCCQE",
         "NormDISCC"]

def sha(p): return hashlib.sha256(open(os.path.realpath(p), "rb").read()).hexdigest()
def cov(h):
    n = h.GetNbinsX(); return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
f = ROOT.TFile.Open(CV); h = f.Get("hXSec2D")
cv = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())]).ravel()
f.Close(); cv = cv[cv > 0]; assert cv.size == 205
fb = ROOT.TFile.Open(BOOT); boot = cov(fb.Get("hCov2D_reported")); fb.Close()

def legacy(band):
    c = band[5:] if band.startswith("full_") else band
    if c == "__Normalization_flat": return "Models"
    if c.startswith("Norm"): return "Normalization"
    return category_for_band(band)

def med(C): return float(100 * np.median(np.sqrt(np.maximum(np.diag(C), 0)) / cv))
def one(path):
    f = ROOT.TFile.Open(path)
    bands = {k.GetName()[len("hCov_universe_"):]: cov(f.Get(k.GetName())) for k in f.GetListOfKeys()
             if k.GetName().startswith("hCov_universe_") and k.GetName() != "hCov_universe_total"}
    tot, comb = cov(f.Get("hCov_universe_total")), cov(f.Get("hCov_combined")); f.Close()
    stat_roll = comb - tot
    r = {"n_bands": len(bands), "sha256": sha(path)}
    for name, fn in (("current", category_for_band), ("legacy", legacy)):
        g = {c: np.zeros_like(tot) for c in CATEGORY_ORDER}
        for b, C in bands.items(): g[fn(b)] += C
        g["Statistical"] = g["Statistical"] + stat_roll
        r[f"grouped_{name}"] = {c: med(C) for c, C in g.items()}
    r["statistical_vl170_boot300"] = med(boot)
    r["statistical_rollup_bootstrap"] = med(stat_roll)
    r["statistical_rollup_eq_vl170_max_abs_rel"] = float(np.max(np.abs(stat_roll - boot)) / np.max(np.abs(boot)))
    r["bands"] = {b: med(bands["full_" + b]) for b in BANDS}
    r["universe_total"] = med(tot); r["combined"] = med(comb)
    r["band_sum_eq_total_max_abs_rel"] = float(np.max(np.abs(sum(bands.values()) - tot)) / np.max(np.abs(tot)))
    return r
res = {"what": "per-bin median relative sigma (%), 205 reported cells, E_U hXSec2D denominator",
       "cv": {"path": CV, "sha256": sha(CV)}, "boot": {"path": BOOT, "sha256": sha(BOOT)},
       "adopted": one(adopted), "repaired": one(repaired)}
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res, indent=1))
