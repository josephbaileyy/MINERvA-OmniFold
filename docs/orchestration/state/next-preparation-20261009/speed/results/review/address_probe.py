"""Reviewer probe (F15): after the pinned loader runs, does an ACTIVE branch keep a non-null address?"""
import os, sys
Q = sys.argv[1]; path = sys.argv[2]
sys.path.append(os.path.join(Q, "bench"))
import pinned, ROOT
DRV = pinned.load_driver(); BS = pinned.load_proto("branch_status")
LO_HI = (DRV.PT_EDGES[0], DRV.PT_EDGES[-1], DRV.PZ_EDGES[0], DRV.PZ_EDGES[-1])
f = ROOT.TFile.Open(path); u = f.Get("mc_signal_reco")
names = BS.signal_branches(True, None, u)
BS.restrict_active_branches(u, [n for n in names if n != "w_reco"])
DRV.collect_signal_arrays_2d(u, *LO_HI, 0.212405, use_weights=True)
for b in ("w_truth", "w_reco", "MC"):
    null = ROOT.gInterpreter.ProcessLine(f"((TTree*){ROOT.addressof(u)})->GetBranch(\"{b}\")->GetAddress() == nullptr;")
    print(b, "status", u.GetBranchStatus(b), "address is nullptr:", bool(null))
