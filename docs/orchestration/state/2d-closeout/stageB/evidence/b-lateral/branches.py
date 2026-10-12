import ROOT, sys
for fn in sys.argv[1:]:
    f = ROOT.TFile.Open(fn)
    print("==", fn)
    for tn in ["mc_signal_reco", "mc_background", "mc_truth_denom", "data"]:
        t = f.Get(tn)
        names = [b.GetName() for b in t.GetListOfBranches()]
        sel = [n for n in names if ("MINOS_0" in n or "BeamAngleX_0" in n or n in ("sim","sim_pz","sim_pass","MC","MC_pz","w_reco","w_truth","id_run","id_subrun","id_nth","sim_background","sim_background_pz","sim_background_pass","w_bkg","pT_truth","pz_truth"))]
        print(tn, t.GetEntries(), len(names), sel[:40])
    for k in f.GetListOfKeys():
        if k.GetClassName().startswith("TParameter") or k.GetClassName()=="TNamed": 
            o=k.ReadObj(); print("  key", k.GetName(), getattr(o,"GetVal",lambda: o.GetTitle())())
