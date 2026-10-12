"""Read-only: hXSec2D of the LightGBM seedscan seeds 1-10 and their sha256 (2d-closeout A-2)."""
import hashlib, json, sys
import ROOT
P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/seedscan_lgbm"
res = {}
for s in range(1, 11):
    path = f"{P}/2d_xsec_MEFHC_5iter_lgbm_seed{s}.root"
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    f = ROOT.TFile.Open(path, "READ")
    x = f.Get("hXSec2D")
    res[s] = {"path": path, "sha256": h,
              "vals": [[repr(x.GetBinContent(i, j)) for j in range(1, 17)] for i in range(1, 15)]}
    f.Close()
json.dump(res, open(sys.argv[1], "w"), indent=1)
print("wrote", sys.argv[1])
