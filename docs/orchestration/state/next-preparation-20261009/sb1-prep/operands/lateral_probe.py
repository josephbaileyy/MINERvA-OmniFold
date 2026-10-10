import json, sys, ROOT, numpy as np
path = sys.argv[1]; N = 20000
f = ROOT.TFile.Open(path)
out = {}
pairs = {"mc_truth_denom": [("pT_truth_{s}", "MC"), ("pz_truth_{s}", "MC_pz"), ("w_truth_{s}", "w_truth")],
         "mc_signal_reco": [("MC_{s}", "MC"), ("MC_pz_{s}", "MC_pz"), ("sim_{s}", "sim"), ("sim_pz_{s}", "sim_pz"),
                            ("w_truth_{s}", "w_truth"), ("w_reco_{s}", "w_reco")],
         "mc_background": [("sim_background_{s}", "sim_background"), ("sim_background_pz_{s}", "sim_background_pz"),
                           ("w_bkg_{s}", "w_bkg")]}
for band in ("BeamAngleX_0", "MuonResolution_0", "Muon_Energy_MINOS_0", "Muon_Energy_MINERvA_0", "Flux_0", "GEANT_Neutron_0"):
    for tree, pp in pairs.items():
        t = f.Get(tree)
        for a, b in pp:
            a = a.format(s=band)
            if not t.GetBranch(a):
                out[f"{band}/{tree}/{a}"] = "absent"; continue
            d = ROOT.RDataFrame(t).Range(N).AsNumpy([a, b])
            x, y = d[a], d[b]
            fin = np.isfinite(x) & np.isfinite(y)
            out[f"{band}/{tree}/{a}"] = {"n": int(x.size), "frac_differs": float(np.mean(x[fin] != y[fin])),
                                         "median_rel": float(np.median(np.abs(x[fin]-y[fin])/np.maximum(np.abs(y[fin]),1e-300)))}
json.dump(out, sys.stdout, indent=0)
