"""Read-only: per-playlist flux integral MnvH1Ds, the combined universe file, universe weights."""
import ROOT, json, hashlib, numpy as np
ROOT.gSystem.Load("libMAT.so"); ROOT.gSystem.Load("libMAT-MINERvA.so")
B = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux"
PL = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1P"]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
out = {"files": {}, "playlists": {}}
pot = []; uni = []; cv = []
for pl in PL:
    p = f"{B}/runEventLoopMC_{pl}.root"; out["files"][p] = sha(p)
    f = ROOT.TFile.Open(p); h = f.Get("pTmu_reweightedflux_integrated")
    d = {"class": h.ClassName(), "vert": [str(x) for x in h.GetVertErrorBandNames()], "lat": [str(x) for x in h.GetLatErrorBandNames()]}
    fb = h.GetVertErrorBand("Flux")
    w = fb.GetUnivWgts()
    d["flux_nhists"] = fb.GetNHists()
    d["flux_univwgts_present"] = bool(w)
    if w:
        ww = np.array([fb.GetUnivWgt(i) for i in range(fb.GetNHists())])
        d["univwgt_min_max_sum"] = [ww.min(), ww.max(), ww.sum()]
        d["univwgt_first5"] = ww[:5].tolist()
    n = h.GetNbinsX()
    c = np.array([h.GetBinContent(i) for i in range(1, n+1)])
    U = np.array([[fb.GetHist(u).GetBinContent(i) for i in range(1, n+1)] for u in range(fb.GetNHists())])
    d["cv_bin1"] = c[0]; d["cv_all_bins_equal"] = bool(np.all(c == c[0]))
    d["flux_u_spread_unweighted_rel"] = float(U[:,0].std()/c[0])
    d["flux_u_mean_over_cv"] = float(U[:,0].mean()/c[0])
    if w:
        mw = (ww*U[:,0]).sum()/ww.sum(); d["flux_u_weighted_mean_over_cv"] = float(mw/c[0])
        d["flux_u_spread_weighted_rel"] = float(np.sqrt((ww*(U[:,0]-mw)**2).sum()/ww.sum())/c[0])
    # MAT CalcCovMx spread for band (uses weights if present)
    cov = fb.CalcCovMx(); d["mat_calccov_sigma_rel_bin1"] = float(np.sqrt(cov[1][1])/c[0])
    for name in ("Muon_Energy_MINOS","Muon_Energy_MINERvA","Muon_Energy"):
        band = h.GetLatErrorBand(name) if h.HasLatErrorBand(name) else (h.GetVertErrorBand(name) if h.HasVertErrorBand(name) else None)
        if band:
            d[name+"_integral_over_cv"] = [band.GetHist(u).GetBinContent(1)/c[0] for u in range(band.GetNHists())]
    out["playlists"][pl] = d
    fd = ROOT.TFile.Open(f"{B}/runEventLoopData_{pl}.root"); pot.append(fd.Get("POTUsed").GetVal())
    uni.append(U); cv.append(c)
pot = np.array(pot); W = pot.sum()
Phi_u = np.tensordot(pot, np.stack(uni), axes=([0],[0]))/W
Phi_cv = np.stack(cv).T @ pot / W
p = f"{B}/flux_integral_universes_MEFHC.root"; out["files"][p] = sha(p)
f = ROOT.TFile.Open(p); hu = f.Get("hFluxUniv"); hc = f.Get("hFluxCV")
FU = np.array([[hu.GetBinContent(i+1, u+1) for i in range(hu.GetNbinsX())] for u in range(hu.GetNbinsY())])
FC = np.array([hc.GetBinContent(i+1) for i in range(hc.GetNbinsX())])
out["combined"] = {"hFluxUniv_shape": list(FU.shape),
  "max_rel_recompute_vs_file_univ": float(np.abs(FU-Phi_u).max()/np.abs(FU).max()),
  "max_rel_recompute_vs_file_cv": float(np.abs(FC-Phi_cv).max()/np.abs(FC).max()),
  "spread_unweighted_rel_bin1": float(FU[:,0].std()/FC[0]),
  "mean_over_cv_bin1": float(FU[:,0].mean()/FC[0])}
pm = f"{B}/runEventLoopMC_MEFHC.root"; out["files"][pm] = sha(pm)
json.dump(out, open("flux_files.json","w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float)[:6000])
