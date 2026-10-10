import json, sys, ROOT
out = {"root": ROOT.gROOT.GetVersion(), "files": {}}
for path in sys.argv[1:]:
    f = ROOT.TFile.Open(path)
    rec = {"compression": f.GetCompressionSettings(), "trees": {}, "keys": []}
    for k in f.GetListOfKeys():
        rec["keys"].append([k.GetName(), k.GetClassName()])
        if k.GetClassName() == "TTree":
            t = f.Get(k.GetName())
            br = []
            for b in t.GetListOfBranches():
                leaves = b.GetListOfLeaves()
                lt = leaves.At(0).GetTypeName() if leaves.GetEntries() else "?"
                br.append([b.GetName(), lt, int(b.GetZipBytes()), int(b.GetTotBytes())])
            rec["trees"][k.GetName()] = {"entries": int(t.GetEntries()), "branches": br}
    out["files"][path] = rec
    f.Close()
json.dump(out, sys.stdout)
