import hashlib, json, sys
import numpy as np, ROOT
want = json.load(open(sys.argv[1]))
bad = 0
for p, s in want.items():
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    bad += h != s
print("runs", len(want), "sha mismatches", bad)
eu = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
print("E_U", hashlib.sha256(open(eu, "rb").read()).hexdigest())
O = "/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/out"
def g(p, n):
    f = ROOT.TFile.Open(p); h = f.Get(n)
    a = np.array([[h.GetBinContent(i+1, j+1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())]); f.Close(); return a
for X in ("PA", "PB", "PC"):
    T0 = g(f"{O}/pu_{X}_s42/xsec.root", "hTruth2D"); C0 = g(f"{O}/pu_{X}_s42/xsec.root", "hOFCompleteness2D")
    dT = [np.nanmax(np.abs(g(f"{O}/pu_{X}_b{i:02d}/xsec.root", "hTruth2D")[T0 > 0] / T0[T0 > 0] - 1)) for i in (1, 2)]
    dC = [np.nanmax(np.abs(g(f"{O}/pu_{X}_b{i:02d}/xsec.root", "hOFCompleteness2D")[C0 > 0] / C0[C0 > 0] - 1)) for i in (1, 2)]
    print(X, "boot max|dT/T|", dT, "max|dc/c|", dC)
