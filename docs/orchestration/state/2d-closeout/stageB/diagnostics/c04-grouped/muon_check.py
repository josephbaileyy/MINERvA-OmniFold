import sys, numpy as np, ROOT
ROOT.gROOT.SetBatch(True)
sys.path.insert(0, sys.argv[1]); from analyze_universes import category_for_band
def cov(h):
    n = h.GetNbinsX(); return np.array([[h.GetBinContent(i+1, j+1) for j in range(n)] for i in range(n)])
def grp(p):
    f = ROOT.TFile.Open(p); g = {}; m = None
    for k in f.GetListOfKeys():
        n = k.GetName()
        if n.startswith("hCov_universe_") and n != "hCov_universe_total":
            b = n[14:]; d = np.diag(cov(f.Get(n)))
            g[b] = d
    f.Close(); return g
a, r = grp(sys.argv[2]), grp(sys.argv[3])
changed = [b for b in a if not np.array_equal(a[b], r[b])]
print("bands whose diagonal changed:", changed)
mu = lambda g: np.sqrt(sum(v for b, v in g.items() if category_for_band(b) == "Muon reconstruction"))
q = mu(r) / mu(a); m = np.sqrt(r["full_Muon_Energy_MINOS"] / a["full_Muon_Energy_MINOS"])
for nm, x in (("muon-reco sigma ratio", q), ("MINOS sigma ratio", m)):
    print(f"{nm}: min {x.min():.4f} median {np.median(x):.4f} max {x.max():.4f} frac>1 {np.mean(x>1):.3f}")
