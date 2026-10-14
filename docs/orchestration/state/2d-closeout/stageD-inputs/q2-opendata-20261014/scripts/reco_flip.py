"""Characterise MasterAnaDev_muon_P differences on shared K: sentinel flips vs value changes.
Usage: python -I reco_flip.py <local_path> <remote_url>"""
import sys
import numpy as np
import ROOT
KEY = ["mc_run", "mc_subrun", "mc_nthEvtInFile"]
C = ["MasterAnaDev_muon_P", "MasterAnaDev_minos_trk_p", "MasterAnaDev_minos_trk_is_ok", "muon_is_minos_match_track",
     "truth_reco_isMinosMatchTrack", "MasterAnaDev_minos_trk_quality"]
def load(src):
    f = ROOT.TFile.Open(src); have = {b.GetName() for b in f.Get("MasterAnaDev").GetListOfBranches()}; f.Close()
    return {k: np.asarray(v) for k, v in ROOT.RDataFrame("MasterAnaDev", src).AsNumpy(KEY + [c for c in C if c in have]).items()}
pk = lambda d: d["mc_run"].astype(np.int64) * 10**10 + d["mc_subrun"].astype(np.int64) * 10**5 + d["mc_nthEvtInFile"].astype(np.int64)
A, B = load(sys.argv[1]), load(sys.argv[2])
_, ia, ib = np.intersect1d(pk(A), pk(B), return_indices=True)
a, b = A["MasterAnaDev_muon_P"][ia], B["MasterAnaDev_muon_P"][ib]
va = np.unique(a[a <= 0], return_counts=True); vb = np.unique(b[b <= 0], return_counts=True)
print("local non-positive muon_P (value, count):", list(zip(va[0][:5].tolist(), va[1][:5].tolist())))
print("remote non-positive muon_P (value, count):", list(zip(vb[0][:5].tolist(), vb[1][:5].tolist())))
both = (a > 0) & (b > 0)
print("both real:", int(both.sum()), "identical among both real:", float(np.mean(a[both] == b[both])))
print("real local -> nonpositive remote:", int(((a > 0) & (b <= 0)).sum()), "| nonpositive local -> real remote:", int(((a <= 0) & (b > 0)).sum()))
for c in C[2:]:
    for nm, D, i in (("local", A, ia), ("remote", B, ib)):
        if c in D:
            x = D[c][i]
            print(c, nm, "values", dict(zip(*[v.tolist() for v in np.unique(x, return_counts=True)])) if len(np.unique(x)) < 8 else "many")
