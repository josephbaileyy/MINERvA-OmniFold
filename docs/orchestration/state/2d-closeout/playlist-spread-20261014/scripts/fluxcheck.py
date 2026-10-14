import sys, json, ROOT
ROOT.gSystem.Load("libMAT")
B = sys.argv[1]
out = {}
f = ROOT.TFile.Open(B + "/runEventLoopMC_MEFHC.root")
out["MEFHC"] = {"DataPOTUsedForFluxWeighting": f.Get("DataPOTUsedForFluxWeighting").GetVal(), "POTUsed": f.Get("POTUsed").GetVal(),
                "fluxSource": f.Get("fluxSource").GetTitle(), "flux_sum_m2_per_pot": sum(f.Get("pTmu_reweightedflux_integrated").GetBinContent(i) for i in range(1, f.Get("pTmu_reweightedflux_integrated").GetNbinsX() + 1))}
f.Close()
for pl in "1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P".split():
    fd = ROOT.TFile.Open(f"{B}/runEventLoopData_{pl}.root"); fm = ROOT.TFile.Open(f"{B}/runEventLoopMC_{pl}.root")
    h = fm.Get("pTmu_reweightedflux_integrated")
    out[pl] = {"data_POTUsed": fd.Get("POTUsed").GetVal(), "mc_POTUsed": fm.Get("POTUsed").GetVal(),
               "flux_sum_m2_per_pot": sum(h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1))}
    print(pl, out[pl], flush=True)
print(out["MEFHC"])
json.dump(out, open(sys.argv[2], "w"), indent=1)
