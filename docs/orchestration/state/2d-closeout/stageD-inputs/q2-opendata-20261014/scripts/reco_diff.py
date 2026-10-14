"""Distribution of reco differences on shared K in MasterAnaDev, and per-subrun Truth counts for chosen subruns.
Usage: python -I reco_diff.py <local_path> <remote_url> <subrun>[,<subrun>...]"""
import sys
import numpy as np
import ROOT

KEY = ["mc_run", "mc_subrun", "mc_nthEvtInFile"]
RECO = ["MasterAnaDev_muon_P", "MasterAnaDev_muon_theta", "MasterAnaDev_muon_E", "MasterAnaDev_minos_trk_p"]

def load(src, tree, cols):
    f = ROOT.TFile.Open(src)
    have = {b.GetName() for b in f.Get(tree).GetListOfBranches()}
    f.Close()
    cols = [c for c in cols if c in have]
    return {k: np.asarray(v) for k, v in ROOT.RDataFrame(tree, src).AsNumpy(cols).items()}

def pack(d):
    return d["mc_run"].astype(np.int64) * 10**10 + d["mc_subrun"].astype(np.int64) * 10**5 + d["mc_nthEvtInFile"].astype(np.int64)

loc, rem, subs = sys.argv[1], sys.argv[2], [int(s) for s in sys.argv[3].split(",")]
A, B = load(loc, "MasterAnaDev", KEY + RECO), load(rem, "MasterAnaDev", KEY + RECO)
_, ia, ib = np.intersect1d(pack(A), pack(B), return_indices=True)
for c in RECO:
    if c not in A or c not in B:
        print(c, "missing in", "local" if c not in A else "remote"); continue
    a, b = A[c][ia], B[c][ib]
    rel = np.abs(a - b) / np.maximum(np.maximum(np.abs(a), np.abs(b)), 1e-300)
    rel[(a == b)] = 0.0
    print(f"{c}: n={len(a)} identical={np.mean(a == b):.4f} rel>1e-9={np.mean(rel > 1e-9):.4f} rel>1e-6={np.mean(rel > 1e-6):.4f} "
          f"rel>1e-3={np.mean(rel > 1e-3):.4f} rel>1e-2={np.mean(rel > 1e-2):.4f} rel>0.1={np.mean(rel > 0.1):.4f} "
          f"median_rel_among_differing={np.median(rel[rel > 0]) if (rel > 0).any() else 0:.3g} "
          f"sign_or_sentinel_flip={(np.sign(a) != np.sign(b)).sum()}")
T = {s: load(x, "Truth", KEY) for s, x in (("local", loc), ("remote", rem))}
for s in subs:
    print("Truth subrun", s, {k: int((v["mc_subrun"] == s).sum()) for k, v in T.items()},
          "max nthEvtInFile", {k: int(v["mc_nthEvtInFile"][v["mc_subrun"] == s].max()) for k, v in T.items()})
