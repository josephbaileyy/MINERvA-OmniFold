"""Read-only: per-playlist POT and flux, and omnifile tree entry counts (2d-closeout A-2)."""
import json, os, sys
import ROOT

P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
PL = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
res = {"playlists": {}, "trees": {}}
for pl in PL:
    row = {}
    for kind in ("Data", "MC"):
        path = f"{P}/baseline_flux/runEventLoop{kind}_{pl}.root"
        f = ROOT.TFile.Open(path, "READ")
        d = {"keys": [[k.GetName(), k.GetClassName()] for k in f.GetListOfKeys()], "params": {}}
        for name, cls in d["keys"]:
            if cls.startswith("TParameter"):
                d["params"][name] = repr(f.Get(name).GetVal())
        h = f.Get("pTmu_reweightedflux_integrated")
        if h:
            d["flux"] = [repr(h.GetBinContent(i)) for i in range(1, h.GetNbinsX() + 1)]
            d["flux_edges"] = [h.GetXaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)]
        f.Close()
        row[kind] = d
    res["playlists"][pl] = row
for k, path in {"E_U_omnifile": f"{P}/runEventLoopOmniFold_MEFHC_universes_full.root",
                "XR_omnifile": "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root"}.items():
    f = ROOT.TFile.Open(path, "READ")
    res["trees"][k] = {t: int(f.Get(t).GetEntries()) for t in ("mc_truth_denom", "mc_signal_reco", "mc_background", "data")}
    f.Close()
json.dump(res, open(sys.argv[1], "w"), indent=1)
print("wrote", sys.argv[1])
