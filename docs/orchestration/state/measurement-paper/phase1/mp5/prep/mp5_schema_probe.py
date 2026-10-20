import sys, ROOT
ROOT.gErrorIgnoreLevel = ROOT.kError
for fn in sys.argv[1:]:
    f = ROOT.TFile.Open(fn)
    print("==", fn)
    for k in f.GetListOfKeys():
        o = k.ReadObj()
        if o.InheritsFrom("TTree"):
            br = [b.GetName() for b in o.GetListOfBranches()]
            print(" ", k.GetName(), o.GetEntries(), len(br), [b for b in br if not b.startswith(("w_uni", "uni_", "w_comp"))][:60])
        else:
            print(" ", k.GetName(), o.ClassName())
