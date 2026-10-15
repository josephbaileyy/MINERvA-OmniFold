import sys, json, ROOT
import numpy as np
ROOT.gROOT.SetBatch(True)
p = sys.argv[1]
f = ROOT.TFile.Open(p, "READ")
out = {"path": p, "keys": [k.GetName() for k in f.GetListOfKeys()]}
for tn in ("MasterAnaDev", "Truth"):
    t = f.Get(tn)
    names = [b.GetName() for b in t.GetListOfBranches()]
    out[tn] = sorted(n for n in names if any(s in n.lower() for s in ("overlay", "ovl", "mixed", "pileup", "data_run", "datarun")))
f.Close()
# ev_run/ev_subrun/ev_gate in MC: do they look like an overlay data gate?
a = ROOT.RDataFrame("Truth", p).Range(200000).AsNumpy(["ev_run", "ev_subrun", "ev_gate", "mc_run", "mc_subrun"])
out["truth_first200k"] = {k: [int(np.min(v)), int(np.max(v)), int(np.unique(v).size)] for k, v in a.items()}
print(json.dumps(out))
