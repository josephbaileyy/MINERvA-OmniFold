import sys, json, numpy as np
REPO = "/Users/josephbailey/local-research/MINERvA-OmniFold"
sys.path.insert(0, REPO + "/2d-unfolding")
import ROOT
import compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
V = np.load("/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state/ibu-chi2-20261123/truthtest/vectors.npz")
m, mod0, mask, area = V["m"], V["mod"], V["mask"], V["area"]
fp = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root")
C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance")); Ci = np.linalg.pinv(C[np.ix_(mask, mask)])
chi = lambda d: float(d[mask] @ Ci @ d[mask])
def load(name):
    v = np.zeros(cpf.N)
    for line in open(f"{SC}/dl-arxiv/anc/model_ptpl_minerva_inclusive_6GeV_{name}.txt"):
        if line.lower().startswith("p|") or not line.strip(): continue
        pz, pt, s = line.strip().split(","); v[(int(pt)-1)*16 + int(pz)-1] = float(s)
    return v
names = ["GENIE_2_12_6", "GENIE_2_12_6_and_QE_RPA", "GENIE_2_12_6_and_NonResPionTune_Only",
         "GENIE_2_12_6_and_Low_Recoil_Enhancement", "MINERvA_Tune_v1", "MINERvA_Tune_v1_Low_Q2_Pion_MINOS", "MINERvA_Tune_v2"]
mods = {n: load(n) for n in names}
ctl = {"C-MOD": bool(np.array_equal(mods["MINERvA_Tune_v1"], mod0)),
       "C-CELLS": all(bool(np.array_equal(v != 0, mask)) for v in mods.values()) and int(mask.sum()) == 205}
ipt, ipz = np.arange(224) // 16, np.arange(224) % 16
reg = {"COL40": mask & (ipz == 15), "COL20": mask & (ipz == 14), "ROW0": mask & (ipt == 0), "ALL": mask}
r = {n: {k: float((v*area)[w].sum() / (m*area)[w].sum()) for k, w in reg.items()} for n, v in mods.items()}
s = {n: {k: r[n][k]/r[n]["ALL"] - 1 for k in reg if k != "ALL"} for n in mods}
X = {n: chi(v - m)/205 for n, v in mods.items()}
e = {n: {k: r[n][k]/r["GENIE_2_12_6"][k] - 1 for k in reg} for n in names[1:4]}
def read(R):
    sT, sG = s["MINERvA_Tune_v1"][R], s["GENIE_2_12_6"][R]
    if np.sign(sG) == np.sign(sT) and abs(sG) >= 0.5*abs(sT): return "UPSTREAM"
    if abs(sG) <= 0.25*abs(sT): return "REWEIGHT"
    return "MIXED"
out = dict(controls=ctl, X=X, region_ratio=r, shape=s, variant_effect_vs_GENIE=e,
           closest=min(X, key=X.get))
out["reading"] = {R: read(R) for R in ["COL40", "ROW0"]} if all(ctl.values()) else "STOP"
print(json.dumps(out, indent=1))
