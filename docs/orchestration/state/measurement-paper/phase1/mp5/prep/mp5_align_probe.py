"""Tiny login-node probe: do the first rows of the 5D analysis omnifile's mc_truth_denom equal the G2 FPS 1A rows
restricted to the analysis phase space (row order and values)? Reads N rows of each."""
import sys, math, numpy as np, ROOT
ROOT.gErrorIgnoreLevel = ROOT.kError
N = int(sys.argv[3])
cols = ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth"]
a = ROOT.RDataFrame("mc_truth_denom", sys.argv[1]).Range(N).AsNumpy(cols)
b = ROOT.RDataFrame("mc_truth_denom", sys.argv[2]).Range(int(N * 1.8)).AsNumpy(cols + ["mc_run", "mc_subrun", "mc_nthEvtInFile", "mu_true_px", "mu_true_py", "mu_true_pz", "mu_true_E"])
th = np.arctan2(b["MC"], b["MC_pz"])
ps = (b["MC"] >= 0) & (b["MC"] <= 4.5) & (b["MC_pz"] >= 1.5) & (b["MC_pz"] <= 60) & (th < math.radians(20))
idx = np.where(ps)[0][:N]
print("5D rows", a["MC"].size, "G2 rows read", b["MC"].size, "G2 in-PS", ps.sum())
for c in cols:
    x, y = a[c], b[c][idx]
    eq = (x == y) | (np.isnan(x) & np.isnan(y))
    print(c, "equal", int(eq.sum()), "/", x.size, "first mismatch", int(np.argmin(eq)) if not eq.all() else -1)
p = np.sqrt(b["mu_true_px"]**2 + b["mu_true_py"]**2 + b["mu_true_pz"]**2)
print("mu_true pT (MeV) vs MC*1000 max abs diff", float(np.max(np.abs(np.hypot(b["mu_true_px"], b["mu_true_py"]) - 1000 * b["MC"]))))
print("mu_true pz vs MC_pz*1000 max abs diff", float(np.max(np.abs(b["mu_true_pz"] - 1000 * b["MC_pz"]))))
print("first ids", [(int(b["mc_run"][i]), int(b["mc_subrun"][i]), int(b["mc_nthEvtInFile"][i])) for i in range(3)])
