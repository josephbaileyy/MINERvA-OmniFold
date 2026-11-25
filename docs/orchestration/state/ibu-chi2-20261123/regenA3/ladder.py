#!/usr/bin/env python3
"""regenA amendment A3: the REF-C2C1 IBU ladder, D_IBU(K) for every stored K, on our pT edges (OLD) and the paper's (E).

It reads, and changes nothing. D_IBU(K) = chi2/ndf of IBU's K-iteration cross section against the published result under
its TotalCovariance, through compare_to_paper_fullcov.chi2_with_cov: the call REF-C2C1's read makes
(ref_c2c1_read.py:106-109). The inputs are Tier 1's committed c2_central.npz units (xsec at ks = 1,2,3,4,5,10,15,20).
The macro definitions follow make_values_fived16.py:1758-1765.
"""
import argparse, hashlib, io, json, sys
import numpy as np

ap = argparse.ArgumentParser()
for k in ("module-dir", "release", "npz-old", "npz-e", "readout", "score", "out"):
    ap.add_argument("--" + k, required=True)
a = ap.parse_args()
sys.path.insert(0, a.module_dir)
import ROOT
import compare_to_paper_fullcov as cpf

sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
f = ROOT.TFile.Open(a.release)
pub = cpf.flatten_th2d(f.Get("pt_pl_cross_section"))
cov = cpf.tmatrix_to_numpy(f.Get("TotalCovariance"))
f.Close()


def dist(x):
    chi2, ndf, _ = cpf.chi2_with_cov(np.asarray(x, float) - pub, cov, "", report=False)
    return chi2 / ndf, ndf


def macros(ek, d_er):
    mid = {k: x for k, x in ek.items() if 2 <= k <= 15}
    lo, hi = min(mid, key=mid.get), max(mid, key=mid.get)
    m = {"c2c1-dibu": ek[10], "c2c1-dibu-k5": ek[5], "c2c1-dibu-k1": ek[1], "c2c1-dibu-k20": ek[20],
         "c2c1-dibu-mid-lo": mid[lo], "c2c1-dibu-mid-hi": mid[hi], "c2c1-der": d_er}
    return m, {"mid_lo_K": lo, "mid_hi_K": hi, "max_mid_below_D_ER": mid[hi] < d_er, "rho_K10": ek[10] / d_er}


def boundary(x):  # distance to the nearest 2-decimal rounding boundary (x.xx5)
    return float(abs(x * 100 - (np.floor(x * 100) + 0.5)) / 100)


score = json.load(io.StringIO(open(a.score).read().split("\n", 1)[1]))
r2 = json.load(open(a.readout))
out = {"inputs": {p: sha(getattr(a, p.replace("-", "_"))) for p in ("release", "npz-old", "npz-e", "readout", "score")},
       "module": cpf.__file__, "module_sha256": sha(cpf.__file__), "sets": {}}
for name, path in (("old", a.npz_old), ("e", a.npz_e)):
    z = np.load(path, allow_pickle=True)
    ks = [int(k) for k in z["ks"]]
    ek, ndfs = {}, set()
    for i, k in enumerate(ks):
        ek[k], n = dist(z["xsec"][i]); ndfs.add(n)
    d_er = score["results"][name]["D_ER"]
    m, extra = macros(ek, d_er)
    out["sets"][name] = {"ks": ks, "ndf": sorted(ndfs), "D_IBU_every_K": {str(k): v for k, v in ek.items()},
                         "D_ER_from_score_out": d_er, "macros_full": m, "macros_2dp": {k: f"{v:.2f}" for k, v in m.items()},
                         "min_distance_to_2dp_boundary": {k: boundary(v) for k, v in m.items()}, **extra}

# Controls (AMENDMENT-A3.txt)
o, e = out["sets"]["old"], out["sets"]["e"]
c = {}
c["C-NDF"] = o["ndf"] == [205] and e["ndf"] == [205]
c["C-KS"] = o["ks"] == e["ks"] == [1, 2, 3, 4, 5, 10, 15, 20]
rel = lambda x, y: abs(x / y - 1)
t1 = {(s, k): rel(out["sets"][s]["D_IBU_every_K"][str(k)], score["results"][s][f"D_IBU_K{k}"]) for s in ("old", "e") for k in (5, 10)}
c["C-T1"] = {"max_rel": max(t1.values()), "pass": max(t1.values()) <= 1e-12}
r2k = {int(k): v for k, v in r2["D_IBU_every_K"].items()}
rr = {k: rel(o["D_IBU_every_K"][str(k)], r2k[k]) for k in o["ks"]}
r2m, _ = macros(r2k, r2["D_E_R"])
same2 = {k: f"{v:.2f}" == o["macros_2dp"][k] for k, v in r2m.items()}
c["C-R2"] = {"rel_by_K": {str(k): v for k, v in rr.items()}, "max_rel": max(rr.values()), "prints_equal": same2,
             "read2_prints": {k: f"{v:.2f}" for k, v in r2m.items()},
             "pass": max(rr.values()) <= 1e-6 and all(same2.values()) and sorted(r2k) == o["ks"]}
c["C-BOUNDARY"] = {s: min(out["sets"][s]["min_distance_to_2dp_boundary"].values()) for s in ("old", "e")}
c["C-BOUNDARY"]["clear"] = min(c["C-BOUNDARY"]["old"], c["C-BOUNDARY"]["e"]) > 1e-6  # descriptive, not a stop
ok = c["C-NDF"] and c["C-KS"] and c["C-T1"]["pass"] and c["C-R2"]["pass"]
out.update(controls=c, controls_pass=ok, reading="READ" if ok else "STOP")
json.dump(out, open(a.out, "w"), indent=1)
print(json.dumps({"controls_pass": ok, "C-BOUNDARY": c["C-BOUNDARY"], "old": o["macros_2dp"], "e": e["macros_2dp"],
                  "e_mid_K": [e["mid_lo_K"], e["mid_hi_K"]], "e_max_mid_below_D_ER": e["max_mid_below_D_ER"]}, indent=1))
