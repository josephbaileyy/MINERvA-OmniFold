#!/usr/bin/env python3
"""Validate the corrected combined 4D covariance + emit a compact JSON summary."""
import json, sys
import numpy as np
import ROOT

BASE = "uq_4d/corrected"
CV = "products/4d/xsec_4d_MEFHC_5iter_lgbm.root"


def th2(h):
    n = h.GetNbinsX()
    b = np.frombuffer(h.GetArray(), dtype=np.float64, count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)
    return b[1:n + 1, 1:n + 1].T.copy()


def sqrt_tr(M):
    return float(np.sqrt(max(np.trace(M), 0.0)))


fc = ROOT.TFile.Open(CV); hx = fc.Get("hXSecND_flat")
xf = np.array([hx.GetBinContent(i + 1) for i in range(hx.GetNbinsX())]); fc.Close()
rep = xf > 0
cvr = xf[rep]
n_rep = int(rep.sum())

f = ROOT.TFile.Open(f"{BASE}/universe_stage2_4d/uq_universe_4d_covariance_combined.root")
Ccomb = th2(f.Get("hCov_combined4d_total"))
Csyst = th2(f.Get("hCov_universe4d_total"))
f.Close()
fs = ROOT.TFile.Open(f"{BASE}/uq_cov_stat_4d.root"); Cstat = th2(fs.Get("hCov_stat4d_reported")); fs.Close()
fm = ROOT.TFile.Open(f"{BASE}/uq_cov_mlsplit_4d.root"); Cml = th2(fm.Get("hCov_mlsplit4d_reported")); fm.Close()

res = {"reported_bins": n_rep, "expected_bins": 4830}
ok = n_rep == 4830
for name, M in [("combined", Ccomb), ("syst", Csyst), ("stat", Cstat), ("ml", Cml)]:
    dimok = M.shape == (n_rep, n_rep)
    symm = float(np.abs(M - M.T).max())
    fin = bool(np.all(np.isfinite(M)))
    ev = np.linalg.eigvalsh(0.5 * (M + M.T))
    psd = bool(ev[0] >= -1e-10 * ev[-1])
    diag = np.sqrt(np.clip(np.diag(M), 0, None))
    medrel = float(np.median(np.where(cvr > 0, diag / cvr, 0.0)))
    res[name] = {"dim_ok": dimok, "sqrt_tr": sqrt_tr(M), "median_rel_pct": 100 * medrel,
                 "symm_maxabs": symm, "finite": fin, "min_eig": float(ev[0]),
                 "min_over_max": float(ev[0] / ev[-1]), "psd_ok": psd,
                 "rank_1e-12": int((ev > ev.max() * 1e-12).sum())}
    ok = ok and dimok and fin and psd
res["ALL_OK"] = bool(ok)
with open(f"{BASE}/uq_universe_4d_covariance_combined.summary.json", "w") as fh:
    json.dump(res, fh, indent=2)
print(json.dumps(res, indent=2))
print(f"[VALIDATE] combined 4D corrected: ALL_OK={ok}")
