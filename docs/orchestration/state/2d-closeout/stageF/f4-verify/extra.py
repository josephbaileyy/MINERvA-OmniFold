#!/usr/bin/env python3
"""F4 extra checks: independent provenance read of every replica, duplicate-vector scan, panel crossing,
C0_cv vs E_U. Read-only."""
import json
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
OUT = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/out"
EU = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
CVOMNI = "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root"
P1 = "3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578"
VD = sys.argv[1]


def read(path):
    f = ROOT.TFile.Open(path)
    h = f.Get("hXSec2D")
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])
    meta = {k: f.Get(k).GetTitle() if f.Get(k) else None for k in ("runConfig", "p1Streams", "driverSha256")}
    f.Close()
    return a, meta


eu, _ = read(EU)
rep = (eu > 0).reshape(-1)
res = {"bad": [], "dups": {}, "crossing_mismatch": []}
spec = ([(f"2dc_P_S1_{n:03d}", 42, n, "three") for n in range(1, 301)]
        + [(f"2dc_P_S2_{n:03d}", 42, n, "bkg") for n in range(1, 101)]
        + [(f"2dc_P_S4B_s{s}_{n:02d}", s, n, "three") for s in (45, 48, 51, 54) for n in range(1, 21)])
vecs, sums = {}, {}
for name, s, n, st in spec:
    a, m = read(f"{OUT}/{name}/xsec.root")
    vecs[name] = a.reshape(-1)[rep]
    rc = json.loads(m["runConfig"])
    ps = json.loads(m["p1Streams"])
    sums[name] = ps.get("sum")
    want = {"seed": s, "bootstrap_seed": n, "bootstrap_streams": st, "omnifile": CVOMNI, "universe": None,
            "iters": 5, "estimator": "lgbm", "bkg_mode": "purity"}
    bad = {k: rc.get(k) for k, v in want.items() if rc.get(k) != v}
    if m["driverSha256"] != P1:
        bad["driver"] = m["driverSha256"]
    if ps.get("bootstrap_seed") != n or ps.get("streams") != st or ps.get("unit_factors") is not False:
        bad["p1Streams"] = ps
    if bad:
        res["bad"].append([name, bad])
for fam in ("2dc_P_S1_", "2dc_P_S2_", "2dc_P_S4B_"):
    names = [k for k in vecs if k.startswith(fam)]
    X = np.stack([vecs[k] for k in names])
    seen = {}
    d = []
    for k, row in zip(names, X):
        key = row.tobytes()
        if key in seen:
            d.append([seen[key], k])
        seen[key] = k
    res["dups"][fam] = {"n": len(names), "identical_pairs": d}
# all 480 vectors distinct from each other
allX = np.stack(list(vecs.values()))
res["n_distinct_all"] = len({r.tobytes() for r in allX})
# crossing: S4B_s{s}_{n} draws the same bootstrap resample as S1_{n} (same p1Streams sums)
for s in (45, 48, 51, 54):
    for n in range(1, 21):
        if sums[f"2dc_P_S4B_s{s}_{n:02d}"] != sums[f"2dc_P_S1_{n:03d}"]:
            res["crossing_mismatch"].append([s, n])
# S2 (bkg-only stream): data and mc sums are the unweighted counts?
s2 = [sums[f"2dc_P_S2_{n:03d}"] for n in range(1, 101)]
res["s2_sum_examples"] = s2[:2]
cv, _ = read(f"{OUT}/2dc_P_C0_cv/xsec.root")
c = cv.reshape(-1)[rep]
x = eu.reshape(-1)[rep]
res["C0_cv_vs_E_U_max_rel"] = float(np.max(np.abs(c - x) / np.abs(x)))
res["S1_mean_vs_E_U_median_rel"] = float(np.median(np.abs(np.stack([vecs[f'2dc_P_S1_{n:03d}'] for n in range(1, 301)]).mean(0) - x) / x))
json.dump(res, open(f"{VD}/extra_result.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items()}, default=str)[:4000])
