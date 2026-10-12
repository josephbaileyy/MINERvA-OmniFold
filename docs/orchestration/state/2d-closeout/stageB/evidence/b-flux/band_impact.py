"""Read-only impact of (a) nu-e constraint universe weights on the adopted Flux band and
(b) the missing Muon_Energy_MINOS flux-integral denominator, on the adopted sweep products."""
import json, hashlib, numpy as np, ROOT
ROOT.gSystem.Load("libMAT.so")
U = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
B = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux"
PL = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1P"]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def xs(p):
    f = ROOT.TFile.Open(p); h = f.Get("hXSec2D")
    a = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY()+1)] for i in range(1, h.GetNbinsX()+1)])
    f.Close(); return a
cvp = f"{U}/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"; cv = xs(cvp); m = cv > 0
res = {"cv": cvp, "cv_sha256": sha(cvp), "n_cells": int(m.sum())}
# weights and POT
pot, wts, minos = [], [], []
for pl in PL:
    f = ROOT.TFile.Open(f"{B}/runEventLoopMC_{pl}.root"); h = f.Get("pTmu_reweightedflux_integrated")
    fb = h.GetVertErrorBand("Flux"); wts.append([fb.GetUnivWgt(u) for u in range(100)])
    mb = h.GetLatErrorBand("Muon_Energy_MINOS") if h.HasLatErrorBand("Muon_Energy_MINOS") else h.GetVertErrorBand("Muon_Energy_MINOS")
    minos.append([mb.GetHist(u).GetBinContent(1) for u in range(2)] + [h.GetBinContent(1)])
    fd = ROOT.TFile.Open(f"{B}/runEventLoopData_{pl}.root"); pot.append(fd.Get("POTUsed").GetVal())
wts = np.array(wts); pot = np.array(pot); minos = np.array(minos)
res["univwgts_identical_across_playlists"] = bool(np.all(wts == wts[0]))
w = wts[0]
phi_cv = (minos[:,2] * pot).sum() / pot.sum()
phi_minos = (minos[:,:2] * pot[:,None]).sum(0) / pot.sum()
res["minos_flux_integral_ratio_u0_u1"] = (phi_minos / phi_cv).tolist()
# (a) Flux band
X = np.array([xs(f"{U}/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_{u}.root") for u in range(100)])
Xm = X[:, m]
s_unw = np.sqrt(((Xm - Xm.mean(0))**2).mean(0)) / cv[m]
mw = (w[:,None]*Xm).sum(0)/w.sum()
s_w = np.sqrt((w[:,None]*(Xm-mw)**2).sum(0)/w.sum()) / cv[m]
res["flux_band_unweighted_median_max"] = [float(np.median(s_unw)), float(s_unw.max())]
res["flux_band_weighted_median_max"] = [float(np.median(s_w)), float(s_w.max())]
res["flux_ratio_weighted_over_unweighted_median_min_max"] = [float(np.median(s_w/s_unw)), float((s_w/s_unw).min()), float((s_w/s_unw).max())]
res["flux_unweighted_mean_over_cv_median"] = float(np.median(Xm.mean(0)/cv[m]))
res["flux_weighted_mean_over_cv_median"] = float(np.median(mw/cv[m]))
# integral (reported-domain area-weighted)
f = ROOT.TFile.Open(cvp); h = f.Get("hXSec2D")
area = np.array([[h.GetXaxis().GetBinWidth(i)*h.GetYaxis().GetBinWidth(j) for j in range(1,h.GetNbinsY()+1)] for i in range(1,h.GetNbinsX()+1)])[m]
I = Xm @ area; Icv = cv[m] @ area
res["flux_integral_sigma_unweighted"] = float(I.std()/Icv)
Iw = (w*I).sum()/w.sum(); res["flux_integral_sigma_weighted"] = float(np.sqrt((w*(I-Iw)**2).sum()/w.sum())/Icv)
# (b) Muon_Energy_MINOS
M = np.array([xs(f"{U}/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_Muon_Energy_MINOS_{u}.root") for u in range(2)])[:, m]
s_old = np.abs(M[1]-M[0])/2/cv[m]
Mc = M / (phi_minos/phi_cv)[:,None]
s_new = np.abs(Mc[1]-Mc[0])/2/cv[m]
res["minos_band_adopted_median_max"] = [float(np.median(s_old)), float(s_old.max())]
res["minos_band_with_flux_denominator_median_max"] = [float(np.median(s_new)), float(s_new.max())]
res["minos_integral_shift_u0_u1_adopted"] = [float((M[u]@area)/Icv-1) for u in range(2)]
res["minos_integral_shift_u0_u1_with_denominator"] = [float((Mc[u]@area)/Icv-1) for u in range(2)]
json.dump(res, open("band_impact.json","w"), indent=1); print(json.dumps(res, indent=1))
