"""Read-only: the May (pre-rescale) Flux universe products' saved inputs against CV42. Prints JSON."""
import glob, hashlib, json, os
import numpy as np
import ROOT
P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
CV = f"{P}/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
H = ["hDataReco2D", "hBkgReco2D", "hMeasTrain2D", "hTruth2D", "hOFInputTruth2D", "hEffNum", "hEffDen", "hOFTruthDenom2D", "hFlux_pt"]


def arrs(p):
    f = ROOT.TFile.Open(p, "READ"); out = {}
    for h in H:
        o = f.Get(h)
        if o:
            if o.InheritsFrom("TH2"):
                out[h] = np.array([[o.GetBinContent(i, j) for j in range(o.GetNbinsY() + 2)] for i in range(o.GetNbinsX() + 2)])
            else:
                out[h] = np.array([o.GetBinContent(i) for i in range(o.GetNbinsX() + 2)])
    f.Close(); return out


cv = arrs(CV)
res = {"n": 0, "equal_counts": {h: 0 for h in H}, "truth_maxrel": [], "files_sha256": {}}
for p in sorted(glob.glob(f"{P}/2d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_*.root")):
    a = arrs(p); res["n"] += 1
    res["files_sha256"][os.path.basename(p)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    for h in H:
        if h in a and np.array_equal(a[h], cv[h]):
            res["equal_counts"][h] += 1
    m = cv["hTruth2D"] != 0
    res["truth_maxrel"].append(float(np.max(np.abs(a["hTruth2D"][m] - cv["hTruth2D"][m]) / np.abs(cv["hTruth2D"][m]))))
res["truth_maxrel_min_max"] = [min(res["truth_maxrel"]), max(res["truth_maxrel"])]
del res["truth_maxrel"]
print(json.dumps(res, indent=1, sort_keys=True))
