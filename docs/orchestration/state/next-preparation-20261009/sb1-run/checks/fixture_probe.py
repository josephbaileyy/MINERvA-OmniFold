"""Re-check test_boundaries_present's properties on a fixture written by ROOT 6.28 (sb1-run probe)."""
import math, sys, tempfile, os
import numpy as np
sys.path.insert(0, sys.argv[1])           # the package's tests/ directory (read only)
import make_fixture_omnifile as mk
import ROOT
d = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
path = os.path.join(d, "fixture.root")
mk.write_fixture(path, rows=6000, extra=12)           # the suite's own fixture parameters
f = ROOT.TFile.Open(path)
c = ROOT.RDataFrame(f.Get("mc_signal_reco")).AsNumpy(["MC", "MC_pz", "w_truth", "w_reco", "sim_pass"])
sp = c["sim_pass"]
print("sim_pass dtype from AsNumpy:", sp.dtype, type(sp[0]).__name__ if sp.size else None)
# per-row read of the UChar_t pass flag, the way the pinned loader reads it
t = f.Get("mc_signal_reco"); from array import array
buf = array("B", [0]); t.SetBranchStatus("*", 0); t.SetBranchStatus("sim_pass", 1); t.SetBranchAddress("sim_pass", buf)
flags = np.array([ (t.GetEntry(i), buf[0])[1] for i in range(t.GetEntries())], dtype=np.uint8)
pt, pz = c["MC"], c["MC_pz"]; fin = np.isfinite(pt) & np.isfinite(pz) & (pz > 0)
near = np.abs(np.arctan2(pt[fin], pz[fin]) - math.radians(20.0)) < 1e-14
out = {"near_20deg_rows": int(near.sum()), "sim_pass_eq_2": int((flags == 2).sum()),
       "sim_pass_values": sorted(set(flags.tolist()))}
for k in ("w_truth", "w_reco"):
    w = c[k]; out[k] = {"eq_1e4": int((w == 1e4).sum()), "eq_below_1e4": int((w == np.nextafter(1e4, 0)).sum()),
                        "nonfinite": int((~np.isfinite(w)).sum()), "negative": int((w < 0).sum())}
out["neg_zero_MC"] = int(((pt == 0.0) & np.signbit(pt)).sum())
b = ROOT.RDataFrame(f.Get("mc_background")).AsNumpy(["w_bkg"])["w_bkg"]
out["w_bkg_1e6_edges"] = int((b == 1e6).sum()) + int((b == np.nextafter(1e6, 0)).sum())
dd = ROOT.RDataFrame(f.Get("data")).AsNumpy(["measured"])["measured"]
out["data_abs_gt_1e3"] = int((np.abs(dd) > 1e3).sum())
ok = (out["near_20deg_rows"] > 20 and out["sim_pass_eq_2"] > 0 and out["neg_zero_MC"] > 0 and out["w_bkg_1e6_edges"] > 1
      and out["data_abs_gt_1e3"] > 0 and all(out[k]["eq_1e4"] > 0 and out[k]["eq_below_1e4"] > 0 and out[k]["nonfinite"] > 0 and out[k]["negative"] > 0 for k in ("w_truth", "w_reco")))
print(out); print("ROOT", ROOT.gROOT.GetVersion(), "numpy", np.__version__, "BOUNDARIES", "PRESENT" if ok else "MISSING")
f.Close(); import shutil; shutil.rmtree(d)
