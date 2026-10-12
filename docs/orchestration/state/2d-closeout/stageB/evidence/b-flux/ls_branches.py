import ROOT, sys
f = ROOT.TFile.Open(sys.argv[1])
for k in f.GetListOfKeys():
    o = k.ReadObj()
    print(k.GetName(), o.ClassName(), (o.GetEntries() if o.InheritsFrom("TTree") else ""))
    if o.InheritsFrom("TTree"):
        names = [b.GetName() for b in o.GetListOfBranches()]
        flux = [n for n in names if "Flux" in n]
        mu = [n for n in names if "Muon_Energy" in n]
        print("  nbranches", len(names), "flux", flux[:3], len(flux), "muonE", mu[:6])
        print("  nonuniverse", [n for n in names if not n.startswith(("w_truth_","w_reco_","w_bkg_","pT_","pz_","q3_","W_","MC_","sim_"))][:80])
