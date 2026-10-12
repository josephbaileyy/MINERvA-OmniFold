"""Read-only: per-universe background/training-input variation in the July sweep vs its CV,
and reco-level background-template statistics and purity from the CV. Writes JSON to argv[2]."""
import glob, hashlib, json, os, re, sys
import numpy as np
import ROOT

d = sys.argv[1]
out = sys.argv[2]
cvf = sys.argv[3]

def arr(f, name, err=False):
    h = f.Get(name)
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    v = np.array([[h.GetBinError(i, j) if err else h.GetBinContent(i, j)
                   for j in range(1, ny + 1)] for i in range(1, nx + 1)])
    return v.ravel()

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

names = ["hBkgReco2D", "hMeasTrain2D", "hDataReco2D", "hXSec2D"]
fcv = ROOT.TFile.Open(cvf)
cv = {n: arr(fcv, n) for n in names}
D = cv["hDataReco2D"]; B = cv["hBkgReco2D"]; eB = arr(fcv, "hBkgReco2D", err=True)
x = cv["hXSec2D"]
rep = x > 0  # reported truth cells (same binning, used only as a mask label)
recomask = D > 0
p = np.where(D > 0, np.clip((D - B) / np.where(D > 0, D, 1), 0, None), np.nan)
r = {"cv_file": cvf, "cv_sha256": sha(cvf),
     "reco_bins_D_pos": int(recomask.sum()),
     "purity": {"min": float(np.nanmin(p[recomask])), "p16": float(np.nanpercentile(p[recomask], 16)),
                "median": float(np.nanmedian(p[recomask])), "max": float(np.nanmax(p[recomask])),
                "n_below_0p9": int((p[recomask] < 0.9).sum()), "n_below_0p8": int((p[recomask] < 0.8).sum())},
     "eB_over_sqrtD": {}, "bkg_frac_total": float(B[recomask].sum() / D[recomask].sum())}
q = eB[recomask] / np.sqrt(D[recomask])
r["eB_over_sqrtD"] = {"median": float(np.median(q)), "p84": float(np.percentile(q, 84)),
                      "max": float(q.max()), "n_gt_0p1": int((q > 0.1).sum()), "n": int(q.size)}
# effective MC background sample size per bin: (sum w)^2/sum w^2 = (B/eB)^2
neff = np.where(eB[recomask] > 0, (B[recomask] / np.where(eB[recomask] > 0, eB[recomask], 1)) ** 2, np.nan)
r["bkg_neff_per_bin"] = {"min": float(np.nanmin(neff)), "median": float(np.nanmedian(neff))}
# Inflation of the reco-level stat variance of the subtracted target if template stats were added:
# var_total/var_data = 1 + eB^2/D  (data Poisson var = D)
infl = np.sqrt(1 + q ** 2)
r["sigma_inflation_reco_if_added"] = {"median": float(np.median(infl)), "max": float(infl.max())}
# Bootstrap-with-frozen-purity scale on the data stream: sd of sum_i b_i * p = p*sqrt(D) vs sqrt(D)
r["purity_scaled_data_stream_ratio"] = {"median": float(np.nanmedian(p[recomask])),
                                        "min": float(np.nanmin(p[recomask]))}
r["cells"] = {"D": D.tolist(), "B": B.tolist(), "eB": eB.tolist()}

uni = {}
for f in sorted(glob.glob(os.path.join(d, "2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root"))):
    tag = re.sub(r".*_uni_full_(.*)\.root", r"\1", f)
    if tag == "CV":
        continue
    fu = ROOT.TFile.Open(f)
    row = {}
    for n in ["hBkgReco2D", "hMeasTrain2D", "hDataReco2D"]:
        if not hasattr(fu.Get(n), "GetNbinsX"):
            row[n] = {"bitwise_equal": None, "max_rel": None, "missing": True}
            continue
        a = arr(fu, n)
        same = bool(np.array_equal(a, cv[n]))
        den = np.where(cv[n] != 0, np.abs(cv[n]), 1.0)
        row[n] = {"bitwise_equal": same, "max_rel": float(np.max(np.abs(a - cv[n]) / den))}
    fu.Close()
    uni[tag] = row
r["universes"] = uni
band = lambda t: t.rsplit("_", 1)[0]
summ = {}
for t, row in uni.items():
    b = band(t)
    s = summ.setdefault(b, {"n": 0, "bkg_equal": 0, "train_equal": 0, "data_equal": 0, "bkg_max_rel": 0.0})
    s["n"] += 1
    s["bkg_equal"] += bool(row["hBkgReco2D"]["bitwise_equal"])
    s["train_equal"] += bool(row["hMeasTrain2D"]["bitwise_equal"])
    s["data_equal"] += bool(row["hDataReco2D"]["bitwise_equal"])
    s["bkg_max_rel"] = max(s["bkg_max_rel"], row["hBkgReco2D"]["max_rel"] or 0.0)
r["by_band"] = summ
r["n_universes"] = len(uni)
r["n_bkg_bitwise_equal_to_cv"] = sum(bool(v["hBkgReco2D"]["bitwise_equal"]) for v in uni.values())
r["n_missing"] = sorted(t for t, v in uni.items() if v["hBkgReco2D"].get("missing"))
json.dump(r, open(out, "w"), indent=1, sort_keys=True)
print("wrote", out, "universes", len(uni), "bkg-equal", r["n_bkg_bitwise_equal_to_cv"])
