import sys, json, ROOT
out = {}
for fn in sys.argv[2:]:
    f = ROOT.TFile.Open(fn)
    r = {}
    for k in ("mcPOTUsed", "dataPOTUsed"):
        o = f.Get(k); r[k] = o.GetVal() if o else None
    for t in ("data", "mc_signal_reco", "mc_background", "mc_truth_denom"):
        o = f.Get(t); r["n_" + t] = int(o.GetEntries()) if o else None
    out[fn] = r
    f.Close()
    print(fn, r, flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
