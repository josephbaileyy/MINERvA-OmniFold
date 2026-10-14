"""Compare, on joined MC reco-tree rows, the scalar branches the production CV weight and the 2D variables read.
Usage: python -I wvars.py <local> <remote> <out.json>"""
import json
import sys

import numpy as np
import ROOT

KEY = ["mc_run", "mc_subrun", "mc_nthEvtInFile"]
V = ["numi_pot", "batch_structure", "reco_vertex_batch", "mc_incomingE", "mc_incoming", "mc_current", "mc_intType",
     "mc_Q2", "mc_w", "mc_targetNucleon", "mc_targetZ", "mc_resID", "mc_nFSPart", "mc_er_nPart",
     "MasterAnaDev_minos_trk_p", "MasterAnaDev_minos_trk_qp", "muon_thetaX", "muon_thetaY", "isMinosMatchTrack",
     "phys_n_dead_discr_pair_upstream_prim_track_proj", "MasterAnaDev_recoil_E", "blob_recoil_E_tracker", "blob_recoil_E_ecal"]


def load(src):
    f = ROOT.TFile.Open(src)
    H = {b.GetName() for b in f.Get("MasterAnaDev").GetListOfBranches()}
    f.Close()
    df = ROOT.RDataFrame("MasterAnaDev", src).Define("l0", "MasterAnaDev_leptonE[0]").Define("l1", "MasterAnaDev_leptonE[1]") \
        .Define("l2", "MasterAnaDev_leptonE[2]").Define("vz", "vtx[2]").Define("vx", "vtx[0]")
    cols = KEY + [c for c in V if c in H] + ["l0", "l1", "l2", "vz", "vx"]
    D = {k: np.asarray(v) for k, v in df.AsNumpy(cols).items()}
    D["K"] = D["mc_run"].astype(np.int64) * 10**11 + D["mc_subrun"].astype(np.int64) * 10**6 + D["mc_nthEvtInFile"].astype(np.int64)
    return D


A, B = load(sys.argv[1]), load(sys.argv[2])
uA, cA = np.unique(A["K"], return_counts=True)
uB, cB = np.unique(B["K"], return_counts=True)
single = np.intersect1d(uA[cA == 1], uB[cB == 1])
ia = np.searchsorted(A["K"], single, sorter=np.argsort(A["K"]))
ia = np.argsort(A["K"])[ia]
ib = np.argsort(B["K"])[np.searchsorted(B["K"], single, sorter=np.argsort(B["K"]))]
fid = (B["vz"][ib] >= 5980) & (B["vz"][ib] <= 8422) & (B["isMinosMatchTrack"][ib] == 1)
r = {"joined_single": int(len(single)), "joined_fid_matched": int(fid.sum())}
for c in V + ["l0", "l1", "l2", "vz", "vx"]:
    if c in A and c in B:
        x, y = A[c][ia], B[c][ib]
        r[c] = {"identical_all": float(np.mean(x == y)), "identical_fid_matched": float(np.mean(x[fid] == y[fid]))}
    else:
        r[c] = "missing in " + ("A" if c not in A else "B")
json.dump(r, open(sys.argv[3], "w"), indent=1)
print(json.dumps(r))
