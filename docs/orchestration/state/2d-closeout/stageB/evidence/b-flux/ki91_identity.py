"""KI-91 exact identity test (read-only).

Rebuilds the MAT FluxReweighter exactly as both event loops configure it
(nu-e constraint on, 100 universes, nu_pdg 14) for one playlist, then:
 (F) flux-integral side: integrates its Flux-band universe u over [0,100] GeV
     and compares with universe u of the saved per-playlist flux MnvH1D;
 (E) event side: for each sampled truth-denominator event, solves for the Enu
     that reproduces w_truth_Flux_0/w_truth from FRW universe 0, then checks
     all 100 w_truth_Flux_u/w_truth against FRW universe u at that Enu.
 Control: the same E test with the omnifile columns cyclically shifted by one.
"""
import sys, json, hashlib, numpy as np, ROOT
ROOT.gSystem.Load("libMAT.so"); ROOT.gSystem.Load("libMAT-MINERvA.so")
pl = sys.argv[1]; nev = int(sys.argv[2])
B = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
frw = ROOT.PlotUtils.flux_reweighter(f"minervame{pl}", 14, True, 100)
h = frw.GetFluxReweighted(14)
band = h.GetVertErrorBand("Flux"); NU = band.GetNHists()
nb = h.GetNbinsX()
cen = np.array([h.GetBinCenter(i) for i in range(1, nb+1)])
lo = np.array([h.GetBinLowEdge(i) for i in range(1, nb+2)])
cvc = np.array([h.GetBinContent(i) for i in range(1, nb+1)])
U = np.array([[band.GetHist(u).GetBinContent(i) for i in range(1, nb+1)] for u in range(NU)])
res = {"playlist": pl, "NU": NU, "nbins": nb}
# (F) flux-integral side, exactly as GetIntegratedFluxReweighted does it
bmin, bmax = h.FindBin(0.0), h.FindBin(100.0)
fint = np.array([band.GetHist(u).Integral(bmin, bmax, "width") for u in range(NU)])
cvint = h.Integral(bmin, bmax, "width")
f = ROOT.TFile.Open(f"{B}/baseline_flux/runEventLoopMC_{pl}.root")
hs = f.Get("pTmu_reweightedflux_integrated"); bs = hs.GetVertErrorBand("Flux")
saved = np.array([bs.GetHist(u).GetBinContent(1) for u in range(NU)])
res["F_max_rel_saved_vs_frw_univ"] = float(np.max(np.abs(saved/fint - 1)))
res["F_rel_saved_vs_frw_cv"] = float(hs.GetBinContent(1)/cvint - 1)
sw = np.array([bs.GetUnivWgt(u) for u in range(NU)]); fw = np.array([band.GetUnivWgt(u) for u in range(NU)])
res["F_univwgt_max_abs_diff"] = float(np.max(np.abs(sw - fw)))
perm_best = [int(np.argmin(np.abs(saved[u]/fint - 1))) for u in range(NU)]
res["F_best_match_is_identity"] = bool(perm_best == list(range(NU)))
# (E) event side
t = f"{B}/runEventLoopOmniFold_{pl}_universes_full.root"
fo = ROOT.TFile.Open(t); tr = fo.Get("mc_truth_denom")
cols = ["w_truth"] + [f"w_truth_Flux_{u}" for u in range(NU)]
res["E_branch_type"] = tr.GetBranch("w_truth_Flux_0").GetLeaf("w_truth_Flux_0").GetTypeName()
rdf = ROOT.RDataFrame(tr).Range(nev)
a = rdf.AsNumpy(cols)
W = np.stack([a[c] for c in cols[1:]], axis=1).astype(float); w0 = a["w_truth"].astype(float)
ok = w0 != 0; R = W[ok] / w0[ok, None]
def interp(y, x):  # TH1::Interpolate between bin centres, clamped
    return np.interp(x, cen, y)
def solve(Rv):
    """Return (best max-rel residual, Enu) over every centre interval and both clamps."""
    best = (np.inf, None)
    for k in range(nb - 1):
        x0, x1 = cen[k], cen[k+1]
        a0, b0 = U[0, k], U[0, k+1] - U[0, k]; ac, bc = cvc[k], cvc[k+1] - cvc[k]
        den = Rv[0] * bc - b0
        if den == 0: continue
        s = (a0 - Rv[0] * ac) / den
        if not (-1e-9 <= s <= 1 + 1e-9): continue
        E = x0 + s * (x1 - x0)
        if E > 75.: continue
        g = np.array([interp(U[u], E) for u in range(NU)]) / interp(cvc, E)
        r = np.max(np.abs(Rv / g - 1))
        if r < best[0]: best = (r, E)
    return best
out = []; outc = []
for i in range(R.shape[0]):
    r, E = solve(R[i]); out.append((r, E))
    rc, _ = solve(np.roll(R[i], 1)); outc.append(rc)
resid = np.array([o[0] for o in out]); Es = np.array([o[1] if o[1] is not None else np.nan for o in out])
rc = np.array(outc)
res["E_n_events"] = int(R.shape[0])
res["E_unsolved"] = int(np.sum(~np.isfinite(resid)))
fr = resid[np.isfinite(resid)]
res["E_resid_max_median"] = [float(fr.max()), float(np.median(fr))] if fr.size else None
res["E_frac_resid_below_1e-9"] = float(np.mean(fr < 1e-9)) if fr.size else None
res["E_Enu_range"] = [float(np.nanmin(Es)), float(np.nanmax(Es))]
frc = rc[np.isfinite(rc)]
res["control_shift1_unsolved"] = int(np.sum(~np.isfinite(rc)))
res["control_shift1_resid_min_median"] = [float(frc.min()), float(np.median(frc))] if frc.size else None
res["omnifile_sha256_note"] = "not hashed here (multi-GB); path recorded"
res["omnifile"] = t
json.dump(res, open(f"ki91_identity_{pl}.json", "w"), indent=1)
print(json.dumps(res, indent=1))
