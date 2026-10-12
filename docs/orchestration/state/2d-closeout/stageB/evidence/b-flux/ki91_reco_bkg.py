"""Read-only: in mc_signal_reco, w_reco_Flux_u/w_reco vs w_truth_Flux_u/w_truth; in mc_background,
w_bkg_Flux_u/w_bkg spread; and Muon_Energy_MINOS / MINERvA event-weight ratios to CV."""
import sys, json, numpy as np, ROOT
pl = sys.argv[1]; n = int(sys.argv[2])
t = f"/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_{pl}_universes_full.root"
fo = ROOT.TFile.Open(t); res = {"playlist": pl}
tr = fo.Get("mc_signal_reco")
cols = ["w_truth","w_reco"] + [f"w_truth_Flux_{u}" for u in range(100)] + [f"w_reco_Flux_{u}" for u in range(100)]
names = [b.GetName() for b in tr.GetListOfBranches()]
mu = [c for c in names if c.startswith(("w_truth_Muon_Energy","w_reco_Muon_Energy"))]
a = ROOT.RDataFrame(tr).Range(n).AsNumpy(cols + mu)
wt, wr = a["w_truth"].astype(float), a["w_reco"].astype(float)
ok = (wt != 0) & (wr != 0)
Rt = np.stack([a[f"w_truth_Flux_{u}"] for u in range(100)],1)[ok]/wt[ok,None]
Rr = np.stack([a[f"w_reco_Flux_{u}"] for u in range(100)],1)[ok]/wr[ok,None]
res["reco_vs_truth_flux_ratio_max_rel"] = float(np.max(np.abs(Rr/Rt-1)))
for c in mu:
    base = wt if c.startswith("w_truth") else wr
    r = a[c][ok].astype(float)/base[ok]
    res[c] = {"min": float(r.min()), "max": float(r.max()), "frac_ne_1": float(np.mean(np.abs(r-1) > 1e-12)), "mean": float(r.mean())}
json.dump(res, open(f"ki91_reco_muonE_{pl}.json","w"), indent=1); print(json.dumps(res, indent=1))
