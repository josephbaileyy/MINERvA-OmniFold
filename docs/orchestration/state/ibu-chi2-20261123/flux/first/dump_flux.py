import json, os, sys, ROOT
ROOT.gROOT.SetBatch(True)
for lib in ("libMAT", "libMAT-MINERvA"):
    r = ROOT.gSystem.Load(lib)
    if r < 0: print(json.dumps({"load_fail": lib})); sys.exit(2)
B = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib/data/flux"
w = {}
for line in open("/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"):
    p = line.split()
    if len(p) == 3 and p[0] == "Flux": w[int(p[1])] = float(p[2])
out = {"w": [w[i] for i in range(100)]}
for per in ("1D", "1M", "1N"):
    f = ROOT.TFile.Open(f"{B}/flux-g4numiv6-pdg14-minervame{per}_rearrangedUniverses.root")
    keys = [k.GetName() for k in f.GetListOfKeys()]
    h = f.Get("flux_E_cvweighted") or f.Get(keys[0])
    ax = h.GetXaxis(); n = h.GetNbinsX()
    d = {"keys": keys, "hist": h.GetName(), "edges": [ax.GetBinLowEdge(i) for i in range(1, n + 2)],
         "cv": [h.GetBinContent(i) for i in range(1, n + 1)], "bands": [str(s) for s in h.GetVertErrorBandNames()]}
    b = h.GetVertErrorBand("Flux")
    if b:
        d["n_univ"] = b.GetNHists()
        d["univ"] = [[b.GetHist(u).GetBinContent(i) for i in range(1, n + 1)] for u in range(b.GetNHists())]
    out[per] = d
print(json.dumps(out))
