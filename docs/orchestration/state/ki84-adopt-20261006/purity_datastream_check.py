"""DESCRIPTIVE, POST HOC (KNOWN_ISSUES 85): does background purity explain the per-bin pull RMS < 1 of the
VL169 toys scored against the VL170 band, and where does the excess width sit?

Step 1, Perlmutter login node (read-only), writes purity_fdata.json next to this file's run directory:
    python purity_datastream_check.py --extract
  purity p_b = max(0, (D - B) / D) per reco bin from the mean over the 300 VL170 replicas of hDataReco2D and
  hBkgReco2D (the production --bkg-mode purity down-weight); f_data = relative variance of the data-only split
  bootstrap (uq/boot_data/, 200 replicas; its stream never touched w_truth, so KNOWN_ISSUES 84 did not affect
  it) over VL170's relative variance. The reco-bin purity is used at the same (pT, pz) index as the truth bin.
Step 2, locally (numpy only):
    python purity_datastream_check.py
  compares the observed per-bin toy RMS with sqrt(1 - f + f p) (purity mode: fixed p narrows the band's data
  part), 1/sqrt(f/p + 1 - f) (the reviewer's hypothesis), and sqrt(1 - f + f r/p) (adding the data/MC size
  ratio r = prod_mean / T), and solves RMS^2 = 1 - f + f g for the toy-to-band data-variance ratio g.
"""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PFD = HERE / "purity_fdata.json"


def extract():
    sys.path.insert(0, "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq")
    import glob
    import analyze_uq as au
    import ROOT
    ROOT.gROOT.SetBatch(True)

    def stack(files, names):
        out = {n: [] for n in names}
        for p in files:
            f = ROOT.TFile.Open(p)
            for n in names:
                out[n].append(au.th2_to_array(f.Get(n)))
            f.Close()
        return {n: np.stack(v) for n, v in out.items()}
    new = stack([f"/pscratch/sd/j/josephrb/ki84-rebuild-20261006/replicas/2d_xsec_MEFHC_5iter_lgbm_boot{s}.root"
                 for s in range(1, 301)], ["hXSec2D", "hDataReco2D", "hBkgReco2D"])
    dfiles = sorted(glob.glob("/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/boot_data/"
                              "2d_xsec_MEFHC_5iter_lgbm_boot*.root"))
    dat = stack(dfiles, ["hXSec2D", "hOFCompleteness2D"])
    X, Xd = new["hXSec2D"], dat["hXSec2D"]
    m, s, md, sd = X.mean(0), X.std(0, ddof=1), Xd.mean(0), Xd.std(0, ddof=1)
    rep = m > 0
    D, B = new["hDataReco2D"].mean(0), new["hBkgReco2D"].mean(0)
    p = np.where(D > 0, np.clip((D - B) / np.where(D > 0, D, 1), 0, None), np.nan)
    f = np.full(m.shape, np.nan)
    f[rep] = ((sd[rep] / md[rep]) ** 2) / ((s[rep] / m[rep]) ** 2)
    out = {"purity_reco": np.nan_to_num(p, nan=-1).tolist(), "f_data": np.nan_to_num(f, nan=-1).tolist(),
           "n_data_split": len(dfiles),
           "data_split_completeness_range": [float(dat["hOFCompleteness2D"][:, rep].min()),
                                             float(dat["hOFCompleteness2D"][:, rep].max())],
           "data_split_mean_over_vl170_median": float(np.median(md[rep] / m[rep]))}
    json.dump(out, open("purity_fdata.json", "w"))
    print({k: v for k, v in out.items() if not isinstance(v, list)})


def analyse():
    sys.path.insert(0, str(REPO / "2d-unfolding/uq/coverage_fixed_truth"))
    import score_coverage as sc
    j = json.loads(PFD.read_text())
    d = np.load(REPO / "docs/orchestration/state/coverage-2d-20261005/interim.npz")
    b = json.loads((REPO / "docs/orchestration/state/ki84-rebuild-20261006/vl170_band.json").read_text())
    rep = d["reported"]
    U = d["U"][(d["toy_index"] >= 1) & (d["toy_index"] <= 100)]
    P = np.array(j["purity_reco"])[rep]
    F = np.clip(np.array(j["f_data"])[rep], 0, 1)
    r = (d["prod_mean"] / d["T"])[rep]

    def rms(mean, sigma):
        z = sc.standardized_residuals(U, d["T"], np.array(mean), np.array(sigma), rep)
        return np.sqrt((z * z).mean(0))
    obs, obs162 = rms(b["mean_vl170"], b["sigma_vl170"]), rms(d["prod_mean"], d["prod_sigma"])

    def summ(x):
        return {"median": float(np.median(x)), "p16": float(np.percentile(x, 16)),
                "p84": float(np.percentile(x, 84)), "corr_with_observed": float(np.corrcoef(x, obs)[0, 1])}
    ok = F > 0.2
    g = (obs[ok] ** 2 - 1 + F[ok]) / F[ok]
    out = {"label": "DESCRIPTIVE, POST HOC; no verdict role",
           "inputs": {k: v for k, v in j.items() if not isinstance(v, list)},
           "purity_quantiles": dict(zip(("p0", "p5", "p16", "p50", "p84", "p100"),
                                        np.percentile(P, [0, 5, 16, 50, 84, 100]).tolist())),
           "f_data_quantiles": dict(zip(("p0", "p16", "p50", "p84", "p100"),
                                        np.percentile(F, [0, 16, 50, 84, 100]).tolist())),
           "observed_rms_vl170": summ(obs),
           "pred_purity_mode": summ(np.sqrt(1 - F + F * P)),
           "pred_reviewer_1_over_sqrt_f_over_p": summ(1 / np.sqrt(F / P + 1 - F)),
           "pred_with_data_over_mc_size": summ(np.sqrt(1 - F + F * r / P)),
           "implied_g_bins_f_gt_0p2": {"n": int(ok.sum()), "median": float(np.median(g)),
                                       "p16": float(np.percentile(g, 16)), "p84": float(np.percentile(g, 84))},
           "corr_rms_f": float(np.corrcoef(obs, F)[0, 1]),
           "by_f": {}}
    for lo, hi in ((0, 0.4), (0.4, 0.7), (0.7, 1.01)):
        k = (F >= lo) & (F < hi)
        out["by_f"][f"{lo}-{hi}"] = {"n": int(k.sum()), "rms_vl170_median": float(np.median(obs[k])),
                                     "rms_vl162_median": float(np.median(obs162[k]))}
    (HERE / "purity_datastream_check.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "inputs"}, indent=1))


if __name__ == "__main__":
    extract() if "--extract" in sys.argv else analyse()
