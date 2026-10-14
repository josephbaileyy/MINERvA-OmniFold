import sys, json, ROOT
ROOT.gROOT.SetBatch(True)
p = sys.argv[1]
f = ROOT.TFile.Open(p, "READ")
out = {"path": p}
for k in f.GetListOfKeys():
    o = k.ReadObj()
    if o.InheritsFrom("TTree"):
        out[k.GetName()] = {"entries": int(o.GetEntries()), "branches": [b.GetName() for b in o.GetListOfBranches()]}
print(json.dumps(out))
