#!/usr/bin/env python3
"""P2-G2 universe choice and the re-declared Flux sigma_band, from inputs only (before any pilot job).

  python select_flux.py <out.json>        (NERSC login node, after setup_salloc_env.sh; reads only)

Rule (AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md §2, P2-G2): the Flux universe with the largest median
|c_off - 1| over the 205 reported cells, c_off = hOFCompleteness2D of that universe's July product (the production
driver's completeness, i.e. run a's), max also quoted. Cells: E_U hXSec2D > 0, C order over (pT, p_par), as in
analyze_p5.py. Ties are impossible to the printed precision; argmax on the float median is used.

sigma_band for the 100-universe Flux band (re-declared for P2-G2; P5's |j0 - j1|/2 is a two-universe rule):
  the per-cell weighted standard deviation of the July Flux_0..99 hXSec2D about their weighted mean, with the
  nu-e + IMD constraint weights (the C04-repaired construction adopted as VL175: MAT CalcCovMx with weights; first
  100 'Flux' rows of sorted_NuEConstraint_FHC_RHC_IMD.txt). The unweighted 1/N std and the RMS about the July CV
  are reported alongside, not used.
Floor: sigma_band >= 1e-3 x E_U CV (P5's floor definition, unchanged).
Also writes, for the chosen universe: its July product (the G-c completeness reference) and per-cell sigma_band and
sigma_ML (sqrt diag of the pinned ML covariance hCov2D_reported) in cell order, for analyze_g2.py.
"""
import hashlib
import json
import os
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
D2 = f"{R}/2d-unfolding"
PN = f"{D2}/uq/purity_newomni"
CV_EU = f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
CV_J = f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root"
ML = f"{D2}/uq/seedscan_lgbm_ml/uq_covariance_ml.root"
CONS = f"{R}/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
PIN = {"E_U": (CV_EU, "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"),
       "ml_covariance": (ML, "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9"),
       "july_cv": (CV_J, "b8457af7")}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def arr(path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    if not h:
        raise SystemExit(f"REFUSE: missing {name} in {path}")
    a = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                  for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return a


def stats(v):
    v = np.asarray(v)
    return {"median": float(np.median(v)), "p84": float(np.percentile(v, 84)), "max": float(np.max(v)),
            "min": float(np.min(v))}


out = {"what": "P2-G2 Flux universe choice and re-declared sigma_band (inputs only)", "inputs": {}}
for role, (p, want) in PIN.items():
    got = sha(p)
    if not got.startswith(want):
        raise SystemExit(f"REFUSE: {p} sha256 {got} does not match the pin {want}")
    out["inputs"][role] = {"path": p, "sha256": got}
cv2 = arr(CV_EU, "hXSec2D")
m = (cv2 > 0).ravel()
cv = cv2.ravel()[m]
if m.sum() != 205:
    raise SystemExit(f"REFUSE: {m.sum()} reported cells, expected 205")
out["cells"] = [[int(i), int(j)] for i, j in np.argwhere(cv2 > 0)]
fml = ROOT.TFile.Open(ML)
hml = fml.Get("hCov2D_reported")
sig_ml = np.sqrt(np.array([hml.GetBinContent(i + 1, i + 1) for i in range(hml.GetNbinsX())]))
fml.Close()
if sig_ml.size != 205:
    raise SystemExit("REFUSE: ML covariance is not 205 x 205")

flux = {}
for k in range(100):
    p = f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Flux_{k}.root"
    if not os.path.exists(p):
        raise SystemExit(f"REFUSE: missing July product {p}")
    flux[k] = {"path": p, "sha256": sha(p), "c": arr(p, "hOFCompleteness2D").ravel()[m],
               "x": arr(p, "hXSec2D").ravel()[m]}
out["flux_sweep_digest"] = hashlib.sha256("".join(flux[k]["sha256"] for k in range(100)).encode()).hexdigest()
rows = []
for k, e in flux.items():
    dc = np.abs(e["c"] - 1)
    rows.append({"idx": k, "median_abs_c_minus_1": float(np.median(dc)), "max_abs_c_minus_1": float(dc.max()),
                 "sha256": e["sha256"]})
rows.sort(key=lambda r: -r["median_abs_c_minus_1"])
out["rank_by_median_top10"] = rows[:10]
out["rank_by_max_top5"] = sorted(rows, key=lambda r: -r["max_abs_c_minus_1"])[:5]
choice = rows[0]["idx"]

cons = {}
with open(CONS) as fc:
    for line in fc:
        t = line.split()
        if len(t) == 3 and t[0] == "Flux":
            cons.setdefault(int(t[1]), float(t[2]))
w = np.array([cons[k] for k in range(100)])
out["inputs"]["constraint"] = {"path": CONS, "sha256": sha(CONS), "n": 100, "sum": float(w.sum()),
                               "n_eff": float(w.sum() ** 2 / (w ** 2).sum())}
X = np.stack([flux[k]["x"] for k in range(100)])
mu = (w[:, None] * X).sum(0) / w.sum()
s_mat = np.sqrt(((X - mu) ** 2 * w[:, None]).sum(0) / w.sum())
xj = arr(CV_J, "hXSec2D").ravel()[m]
alt = {"unweighted_std_1overN": X.std(axis=0, ddof=0), "rms_about_july_cv": np.sqrt(((X - xj) ** 2).mean(0))}
floor = s_mat >= 1e-3 * cv
out["choice"] = {
    "universe": f"Flux:{choice}", "band": "Flux", "index": int(choice),
    "median_abs_c_minus_1": rows[0]["median_abs_c_minus_1"], "max_abs_c_minus_1": rows[0]["max_abs_c_minus_1"],
    "constraint_weight": float(w[choice]), "constraint_weight_mean": float(w.mean()),
    "july_product": {"path": flux[choice]["path"], "sha256": flux[choice]["sha256"]},
    "median_rel_shift_vs_july_cv": float(np.median(np.abs(flux[choice]["x"] / xj - 1))),
}
out["sigma_band"] = {
    "definition": "weighted std of July Flux_0..99 hXSec2D about the weighted mean, nu-e+IMD constraint weights",
    "per_cell": [float(v) for v in s_mat], "over_cv": stats(s_mat / cv),
    "floor": "sigma_band >= 1e-3 x E_U CV", "n_floored": int(floor.sum()),
    "sigma_ml_over_sigma_band": stats(sig_ml / s_mat),
    "noise_only_median_r1": float(np.median(0.954 * sig_ml / s_mat)),
    "alternatives_reported_not_used": {k: {"over_cv": stats(v / cv), "n_floored": int((v >= 1e-3 * cv).sum()),
                                           "sigma_ml_over_sigma_band": stats(sig_ml / v)} for k, v in alt.items()},
}
out["sigma_ml"] = {"per_cell": [float(v) for v in sig_ml], "over_cv": stats(sig_ml / cv)}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps({"choice": out["choice"], "n_floored": out["sigma_band"]["n_floored"],
                  "sigma_band_over_cv": out["sigma_band"]["over_cv"],
                  "sigma_ml_over_sigma_band": out["sigma_band"]["sigma_ml_over_sigma_band"],
                  "top5": [(r["idx"], round(r["median_abs_c_minus_1"], 5), round(r["max_abs_c_minus_1"], 4))
                           for r in rows[:5]]}, indent=1))
