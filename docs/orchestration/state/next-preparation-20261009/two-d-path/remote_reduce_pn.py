"""Read-only login-node reduction of the July seed-42 `purity_newomni` sweep (no training, no event loop).

Run from the Perlmutter canonical checkout root after `source setup_salloc_env.sh`:
    python3 - < remote_reduce_pn.py > remote_reduce_pn.json

For the 205 reported cells it prints, as JSON: the sweep CV's hXSec2D, the per-band and total
diagonal widths in the MAT convention used by uq/analyze_universes.py (each band centred on its
own universe mean, biased 1/N, plus the 1.4 % normalization rank-1 term), whether Flux universes
carry their own flux integral and whether non-Flux universes vary the background prediction, and
the file dates of the inputs this design depends on. It writes nothing on the cluster.
"""
import hashlib
import json
import os
import sys
import time

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

B = "2d-unfolding"
PN = f"{B}/uq/purity_newomni"
LIST = f"{B}/uq/universes_full_list.txt"
REF = {
    "E_C": f"{B}/2d_crossSection_omnifold_MEFHC_5iter.root",
    "CV42_fluxfix": f"{B}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
    "seed1": f"{B}/seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed1.root",
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    f = ROOT.TFile.Open(path)
    out = {}
    for name in ("hXSec2D", "hBkgReco2D"):
        h = f.Get(name)
        out[name] = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())]
                              for i in range(h.GetNbinsX())])
    for p in ("fluxIntegral_m2_per_POT",):
        o = f.Get(p)
        out[p] = float(o.GetVal()) if o else None
    f.Close()
    return out


def stamp(path):
    st = os.stat(path)
    return {"path": path, "bytes": st.st_size,
            "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime))}


res = {"host": os.uname().nodename}
cv = read(f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root")
reported = read(REF["E_C"])["hXSec2D"] > 0
idx = np.argwhere(reported)
res["cells"] = [[int(i), int(j)] for i, j in idx]
res["pn_cv_sha256"] = sha(f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root")
res["pn_cv_xsec"] = [float(cv["hXSec2D"][i, j]) for i, j in idx]
for k, p in REF.items():
    res.setdefault("ref_xsec", {})[k] = [float(read(p)["hXSec2D"][i, j]) for i, j in idx]

universes = [ln.strip() for ln in open(LIST) if ln.strip() and not ln.startswith("#")]
bands = {}
missing = []
flux_int = {}
bkg_dev = {}
for u in universes:
    band, uidx = u.rsplit(":", 1)
    path = f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_{band}_{uidx}.root"
    if not os.path.exists(path):
        missing.append(u)
        continue
    r = read(path)
    bands.setdefault(band, []).append(r["hXSec2D"][reported])
    flux_int.setdefault(band, []).append(r["fluxIntegral_m2_per_POT"])
    dev = np.abs(r["hBkgReco2D"] - cv["hBkgReco2D"])
    bkg_dev.setdefault(band, []).append(float(dev.max() / max(cv["hBkgReco2D"].max(), 1e-300)))

x_cv = cv["hXSec2D"][reported]
var_tot = (0.014 * x_cv) ** 2
res["band_sigma_rel_median_pct"] = {}
res["band_sigma_abs"] = {}
res["pair_asymmetry"] = {}
for band, rows in bands.items():
    a = np.array(rows)
    v = ((a - a.mean(axis=0)) ** 2).mean(axis=0)  # MAT: centred on the universe mean, 1/N
    var_tot += v
    res["band_sigma_rel_median_pct"][band] = float(np.median(np.sqrt(v) / x_cv) * 100)
    res["band_sigma_abs"][band] = [float(s) for s in np.sqrt(v)]
    if len(rows) == 2:  # a +/-1 sigma pair: half-difference h and common displacement A from the CV
        res["pair_asymmetry"][band] = {"h_abs": [float(s) for s in np.abs(a[0] - a[1]) / 2],
                                       "A_abs": [float(s) for s in np.abs((a[0] + a[1]) / 2 - x_cv)]}
bkg0 = read(f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Flux_0.root")["hBkgReco2D"]
k = np.unravel_index(np.argmax(np.abs(bkg0 - cv["hBkgReco2D"])), bkg0.shape)
res["flux0_bkg_max_change_cell"] = {"reco_cell": [int(k[0]), int(k[1])],
                                    "is_cv_bkg_max_cell": bool(cv["hBkgReco2D"][k] == cv["hBkgReco2D"].max()),
                                    "rel_change": float(bkg0[k] / cv["hBkgReco2D"][k] - 1)}
res["sigma_universe_total_abs"] = [float(s) for s in np.sqrt(var_tot)]
res["n_universes_read"] = sum(len(v) for v in bands.values())
res["n_bands"] = len(bands)
res["missing_universes"] = missing
res["cv_flux_integral"] = cv["fluxIntegral_m2_per_POT"]
res["flux_universe_flux_integral_distinct_from_cv"] = {
    b: int(sum(1 for f in v if f is not None and f != cv["fluxIntegral_m2_per_POT"]))
    for b, v in flux_int.items() if b.endswith("Flux")}
res["max_rel_bkg_change_vs_cv_by_band"] = {b: float(max(v)) for b, v in bkg_dev.items()}

stamps = [f"{B}/runEventLoopOmniFold_MEFHC.root", f"{B}/runEventLoopOmniFold_MEFHC_universes_full.root",
          REF["E_C"], REF["CV42_fluxfix"], REF["seed1"], f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root",
          f"{B}/uq/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_MaRES_0.root"]
res["file_stamps"] = [stamp(p) for p in stamps if os.path.exists(p)]
env = os.path.expanduser("~/.conda/envs/root_6_28/lib/python3.11/site-packages")
res["env_dist_info_stamps"] = [stamp(os.path.join(env, d)) for d in sorted(os.listdir(env))
                               if d.endswith(".dist-info") and d.split("-")[0].lower()
                               in ("scikit_learn", "lightgbm", "numpy", "scipy", "threadpoolctl")]
json.dump(res, sys.stdout, indent=1, sort_keys=True)
sys.stdout.write("\n")
