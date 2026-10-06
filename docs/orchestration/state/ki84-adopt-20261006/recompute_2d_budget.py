"""Recompute the quoted 2D uncertainty budget from its covariance files, for VL162 and VL170.

Block sum C = C_universe (fluxfix sweep + 1.4 % norm) + C_boot (N = 300) + C_ML (lgbm seedscan, n = 10)
on the 205 reported bins; per-bin relative sigma = sqrt(diag C) / x with x the matched full-universe CV
(uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root), the convention of the 2026-05-29 block-sum table that
the note's 6.865 % (printed 6.87 %) comes from. Records the sha256 of every input. Read-only.

  python recompute_2d_budget.py     (Perlmutter, root_6_28 environment)
"""
import hashlib, json, os, sys
sys.dont_write_bytecode = True
import numpy as np

D = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
sys.path.insert(0, f"{D}/uq")
import analyze_uq as au  # noqa: E402
import ROOT  # noqa: E402
ROOT.gROOT.SetBatch(True)

U = "uq_universe_covariance_full_matcorr_fluxfix.root"
SETS = {
    "VL162": {"universe": f"{D}/uq/universe_stage2_MEFHC_full_matcorr_fluxfix/{U}",
              "boot": f"{D}/uq/bootstrap_MEFHC_300/uq_covariance_boot300.root"},
    "VL170": {"universe": f"{D}/uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/{U}",
              "boot": f"{D}/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"},
}
ML = f"{D}/uq/seedscan_lgbm_ml/uq_covariance_ml.root"
CV = f"{D}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cov(p, h):
    f = ROOT.TFile.Open(p)
    x = f.Get(h)
    n = x.GetNbinsX()
    a = np.array([[x.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
    f.Close()
    return a


def med(C, x):
    r = np.sqrt(np.diag(C)) / x
    return {"median_pct": float(100 * np.median(r)), "p84_pct": float(100 * np.percentile(r, 84)),
            "max_pct": float(100 * r.max()), "sqrt_trace": float(np.sqrt(np.trace(C)))}


f = ROOT.TFile.Open(CV)
x2 = au.th2_to_array(f.Get("hXSec2D"))
f.Close()
rep = x2 > 0
x = x2.ravel(order="C")[rep.ravel(order="C")]
Cml = cov(ML, "hCov2D_reported")
out = {"inputs": {"cv": {"path": CV, "sha256": sha(CV)}, "ml": {"path": ML, "sha256": sha(ML)}},
       "n_reported": int(rep.sum()), "x": "matched full-universe CV hXSec2D"}
for tag, s in SETS.items():
    Cu, Cc = cov(s["universe"], "hCov_universe_total"), cov(s["universe"], "hCov_combined")
    Cb = cov(s["boot"], "hCov2D_reported")
    out["inputs"][tag] = {k: {"path": p, "sha256": sha(p)} for k, p in s.items()}
    out[tag] = {"universe": med(Cu, x), "boot": med(Cb, x), "ml": med(Cml, x),
                "universe_plus_boot": med(Cu + Cb, x), "block_sum": med(Cu + Cb + Cml, x),
                "hCov_combined_minus_universe_minus_boot_max_rel":
                    float(np.abs(Cc - Cu - Cb).max() / np.abs(Cb).max())}
print(json.dumps({t: {k: round(v["median_pct"], 4) for k, v in out[t].items() if isinstance(v, dict)}
                  for t in SETS}, indent=1))
print(json.dumps({t: {k: v["sqrt_trace"] for k, v in out[t].items() if isinstance(v, dict)} for t in SETS}))
json.dump(out, open(os.path.join(os.getcwd(), "recompute_2d_budget.json"), "w"), indent=1)
