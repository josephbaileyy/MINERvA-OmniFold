"""Dump structural metadata of one ROOT file (local path or root:// URL) to JSON. Read-only.

Usage: python -I meta.py <url-or-path> <out.json>
Records: top-level keys (name, class, cycle), file creation/modification date, compression,
and per TTree: entries, branch count, every leaf-branch name with its zipped/total bytes.
"""
import json, sys, time
import ROOT

def walk(br, out):
    sub = br.GetListOfBranches()
    if sub.GetEntries() == 0:
        out[br.GetName()] = [int(br.GetZipBytes("*")), int(br.GetTotBytes("*")), br.GetTitle()]
    else:
        out[br.GetName()] = [int(br.GetZipBytes("")), int(br.GetTotBytes("")), br.GetTitle()]
        for b in sub:
            walk(b, out)

url, outp = sys.argv[1], sys.argv[2]
t0 = time.time()
f = ROOT.TFile.Open(url, "READ")
if not f or f.IsZombie():
    sys.exit(f"OPEN FAILED: {url}")
rec = {"url": url, "size": int(f.GetSize()), "end": int(f.GetEND()),
       "created": f.GetCreationDate().AsSQLString(), "modified": f.GetModificationDate().AsSQLString(),
       "compress": int(f.GetCompressionSettings()), "version": int(f.GetVersion()),
       "keys": [], "trees": {}}
for k in f.GetListOfKeys():
    rec["keys"].append([k.GetName(), k.GetClassName(), int(k.GetCycle()), k.GetTitle(),
                        k.GetDatime().AsSQLString()])
for name, cls, cyc, *_ in rec["keys"]:
    if cls != "TTree":
        continue
    t = f.Get(f"{name};{cyc}")
    brs = {}
    for b in t.GetListOfBranches():
        walk(b, brs)
    rec["trees"][f"{name};{cyc}"] = {
        "entries": int(t.GetEntries()), "n_top_branches": int(t.GetListOfBranches().GetEntries()),
        "n_all_branches": len(brs), "zipbytes": int(t.GetZipBytes()), "totbytes": int(t.GetTotBytes()),
        "branches": brs}
rec["seconds"] = round(time.time() - t0, 1)
json.dump(rec, open(outp, "w"))
print(url, "size", rec["size"], "keys", [(k[0], k[1], k[2]) for k in rec["keys"]], "sec", rec["seconds"])
for tn, tv in rec["trees"].items():
    print("  ", tn, "entries", tv["entries"], "branches", tv["n_top_branches"], tv["n_all_branches"], "zip", tv["zipbytes"])
