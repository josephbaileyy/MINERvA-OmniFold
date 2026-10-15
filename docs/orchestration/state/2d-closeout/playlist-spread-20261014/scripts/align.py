import sys, numpy as np, ROOT
fn = sys.argv[1]
a = ROOT.RDataFrame("mc_truth_denom", fn).AsNumpy(["MC", "MC_pz", "w_truth"])
b = ROOT.RDataFrame("mc_signal_reco", fn).AsNumpy(["MC", "MC_pz", "w_truth"])
print(fn, len(a["MC"]), len(b["MC"]), all(np.array_equal(a[k], b[k]) for k in a), a["w_truth"].sum(), b["w_truth"].sum(),
      "MC range", float(b["MC"].min()), float(b["MC"].max()), "MCpz range", float(b["MC_pz"].min()), float(b["MC_pz"].max()))
