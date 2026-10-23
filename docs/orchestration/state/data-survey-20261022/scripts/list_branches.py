"""List every TTree and its branches (name, leaf type) in one ROOT file. Metadata only: no entry is read.
argv: URL_OR_PATH OUT_JSON"""
import json
import sys

import ROOT

ROOT.gROOT.SetBatch(True)
url, out = sys.argv[1], sys.argv[2]
f = ROOT.TFile.Open(url, "READ")
if not f or f.IsZombie():
    raise SystemExit(f"STOP: cannot open {url}")
res = {"file": url, "size_bytes": int(f.GetSize()), "trees": {}, "bytes_read": None}
for k in f.GetListOfKeys():
    if k.GetClassName() != "TTree":
        res.setdefault("other_keys", []).append([k.GetName(), k.GetClassName()])
        continue
    t = f.Get(k.GetName())
    br = []
    for b in t.GetListOfBranches():
        leaves = b.GetListOfLeaves()
        lt = leaves.At(0).GetTypeName() if leaves.GetEntries() else ""
        br.append([b.GetName(), lt, int(leaves.GetEntries())])
    res["trees"][k.GetName()] = {"entries": int(t.GetEntries()), "n_branches": len(br), "branches": br}
res["bytes_read"] = int(f.GetBytesRead())
f.Close()
json.dump(res, open(out, "w"), indent=0)
print(url, {t: (v["entries"], v["n_branches"]) for t, v in res["trees"].items()}, "bytes_read", res["bytes_read"])
