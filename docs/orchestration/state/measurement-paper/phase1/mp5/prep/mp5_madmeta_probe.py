"""Metadata-only probe of one MAD AnaTuple's Truth tree: entries and compressed bytes of the branches MP-5(a) reads."""
import sys, ROOT
ROOT.gErrorIgnoreLevel = ROOT.kError
f = ROOT.TFile.Open(sys.argv[1]); t = f.Get("Truth")
need = ["mc_run", "mc_subrun", "mc_nthEvtInFile", "mc_incomingPartVec", "mc_primFSLepton", "mc_incomingE",
        "mc_targetNucleon", "mc_Q2", "mc_vtx", "mc_current", "mc_incoming"]
tot = 0
print("entries", t.GetEntries(), "file bytes", f.GetSize(), "truth tree zip", t.GetZipBytes())
for b in need:
    br = t.GetBranch(b)
    if not br:
        print("MISSING", b); continue
    z = br.GetZipBytes("*"); tot += z
    print(b, br.GetTitle(), "zip", z, "tot", br.GetTotBytes("*"))
print("sum zip bytes of needed branches", tot)
