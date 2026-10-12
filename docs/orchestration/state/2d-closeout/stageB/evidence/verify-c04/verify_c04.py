#!/usr/bin/env python3
"""Independent read-only verification of C04 (nu-e constraint universe weights on the 2D Flux band)
and X01 (Muon_Energy_MINOS flux-integral denominator). Written from scratch by the verifier.

Reads only; writes one JSON next to this script.
"""
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load("libMAT.so")

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
B = f"{R}/2d-unfolding/baseline_flux"
UQ = f"{R}/2d-unfolding/uq"
PL = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
FLUXH = "pTmu_reweightedflux_integrated"
CVF = f"{UQ}/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
SWEEP = f"{UQ}/universe_sweep_fluxfix"
UNIV_ADOPTED = f"{UQ}/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root"
BOOT = f"{UQ}/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"
ML = f"{UQ}/seedscan_lgbm_ml/uq_covariance_ml.root"
FLUXBAND = f"{B}/flux_integral_universes_MEFHC.root"
CONSTRAINT = f"{R}/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_c04.json")

res = {"sha256": {}}


def sha(p):
    h = hashlib.sha256()
    with open(os.path.realpath(p), "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    d = h.hexdigest()
    res["sha256"][p] = d
    return d


def h2np(path, name="hXSec2D"):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    a = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                  for i in range(1, h.GetNbinsX() + 1)])
    ar = np.array([[h.GetXaxis().GetBinWidth(i) * h.GetYaxis().GetBinWidth(j)
                    for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return a, ar


def sq(path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    if not h:
        f.Close()
        return None
    n = h.GetNbinsX()
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
    f.Close()
    return a


def wcov(X, w=None):
    """Weighted mean-centred covariance, MAT CalcCovMx form (normalised by sum of weights)."""
    if w is None:
        w = np.ones(X.shape[0])
    w = np.asarray(w, float)
    mu = (w[:, None] * X).sum(0) / w.sum()
    Z = X - mu
    return (Z.T * w) @ Z / w.sum(), mu


# ------------------------------------------------------------------ flux inputs
keep = []
pot, cvs, unis, wts, minos, minos_kind = [], [], [], [], [], []
for pl in PL:
    p = f"{B}/runEventLoopMC_{pl}.root"
    sha(p)
    f = ROOT.TFile.Open(p)
    keep.append(f)
    h = f.Get(FLUXH)
    n = h.GetNbinsX()
    cvs.append(np.array([h.GetBinContent(i) for i in range(1, n + 1)]))
    fb = h.GetVertErrorBand("Flux")
    nu = fb.GetNHists()
    unis.append(np.array([[fb.GetHist(u).GetBinContent(i) for i in range(1, n + 1)] for u in range(nu)]))
    wv = fb.GetUnivWgts()
    wts.append(np.array([fb.GetUnivWgt(u) for u in range(nu)]) if wv else None)
    if h.HasLatErrorBand("Muon_Energy_MINOS"):
        mb = h.GetLatErrorBand("Muon_Energy_MINOS"); minos_kind.append("lat")
    elif h.HasVertErrorBand("Muon_Energy_MINOS"):
        mb = h.GetVertErrorBand("Muon_Energy_MINOS"); minos_kind.append("vert")
    else:
        mb = None; minos_kind.append(None)
    minos.append(np.array([[mb.GetHist(u).GetBinContent(i) for i in range(1, n + 1)]
                           for u in range(mb.GetNHists())]) if mb else None)
    pd = f"{B}/runEventLoopData_{pl}.root"
    sha(pd)
    fd = ROOT.TFile.Open(pd)
    pot.append(float(fd.Get("POTUsed").GetVal()))
    fd.Close()
    if pl == "1A":
        # MAT's own CalcCovMx on the stored band (uses whatever univ weights the band carries)
        cm = fb.CalcCovMx()
        res["mat_calccov_1A_flux_bin1_rel"] = float(np.sqrt(cm[1][1]) / cvs[-1][0])
        res["flux_1A_names"] = {"vert": [str(x) for x in h.GetVertErrorBandNames()],
                                "lat": [str(x) for x in h.GetLatErrorBandNames()]}

pot = np.array(pot)
W = pot.sum()
cvs = np.stack(cvs); unis = np.stack(unis)
res["flux_bins_constant_within_hist"] = bool(np.all(np.abs(cvs - cvs[:, :1]) <= 1e-12 * np.abs(cvs[:, :1])))
res["univwgts_present_all"] = all(w is not None for w in wts)
wts_arr = np.stack(wts)
res["univwgts_identical_across_playlists"] = bool(np.all(wts_arr == wts_arr[0]))
w = wts_arr[0]
res["univwgt_stats"] = {"n": int(w.size), "min": float(w.min()), "max": float(w.max()), "sum": float(w.sum()),
                        "n_eff": float(w.sum() ** 2 / (w ** 2).sum())}
# compare to the MPARAMFILES constraint file (first 100 Flux entries)
sha(CONSTRAINT)
cf = {}
for line in open(CONSTRAINT):
    t = line.split()
    if len(t) == 3 and t[0] == "Flux":
        cf[int(t[1])] = float(t[2])
cfw = np.array([cf[u] for u in range(w.size)])
res["univwgt_vs_constraint_file_max_absdiff"] = float(np.abs(cfw - w).max())
res["constraint_file_n_entries"] = len(cf)

phi_cv = cvs[:, 0] @ pot / W
phi_u = np.tensordot(pot, unis[:, :, 0], axes=([0], [0])) / W
res["flux_integral"] = {
    "phi_cv": float(phi_cv),
    "unweighted_mean_over_cv": float(phi_u.mean() / phi_cv),
    "weighted_mean_over_cv": float((w * phi_u).sum() / w.sum() / phi_cv),
    "sigma_unweighted_meancentred_rel": float(phi_u.std() / phi_cv),
    "sigma_weighted_rel": float(np.sqrt(wcov(phi_u[:, None], w)[0][0, 0]) / phi_cv),
    "sigma_unweighted_cvcentred_rel": float(np.sqrt(((phi_u - phi_cv) ** 2).mean()) / phi_cv),
}
# MAT CalcCovMx on a freshly built combined flux MnvH1D, with and without weights
nb = cvs.shape[1]
for tag, use_w in (("weighted", True), ("unweighted", False)):
    hm = ROOT.PlotUtils.MnvH1D(f"hphi_{tag}", "", nb, 0.0, float(nb))
    for i in range(nb):
        hm.SetBinContent(i + 1, float(phi_cv))
    hm.AddVertErrorBand("Flux", int(w.size))
    vb = hm.GetVertErrorBand("Flux")
    for u in range(w.size):
        for i in range(nb):
            vb.GetHist(u).SetBinContent(i + 1, float(phi_u[u]))
    if use_w:
        vec = ROOT.std.vector("double")()
        for x in w:
            vec.push_back(float(x))
        vb.SetUnivWgts(vec)
    cm = vb.CalcCovMx()
    res["flux_integral"][f"mat_calccovmx_{tag}_rel"] = float(np.sqrt(cm[1][1]) / phi_cv)

# the adopted combined flux band file
sha(FLUXBAND)
f = ROOT.TFile.Open(FLUXBAND)
hu = f.Get("hFluxUniv"); hc = f.Get("hFluxCV")
FU = np.array([[hu.GetBinContent(i + 1, u + 1) for i in range(hu.GetNbinsX())] for u in range(hu.GetNbinsY())])
FC = np.array([hc.GetBinContent(i + 1) for i in range(hc.GetNbinsX())])
f.Close()
res["fluxband_file_vs_mine"] = {"cv_max_rel": float(np.abs(FC - phi_cv).max() / phi_cv),
                                "univ_max_rel": float(np.abs(FU - phi_u[:, None]).max() / phi_cv)}

# Muon_Energy_MINOS flux integrals, POT-combined
res["minos_band_kind"] = minos_kind
mn = np.stack([m[:, 0] for m in minos])  # (12, 2)
phi_minos = pot @ mn / W
r_minos = phi_minos / phi_cv
res["minos_flux_ratio_u0_u1"] = r_minos.tolist()
res["minos_flux_ratio_per_playlist"] = {pl: (mn[k] / cvs[k, 0]).tolist() for k, pl in enumerate(PL)}

# ------------------------------------------------------------------ universe products
cv, area = h2np(CVF)
sha(CVF)
m = cv > 0
c = cv[m]; a = area[m]
I_cv = a @ c
res["n_cells"] = int(m.sum())
UNI_RE = re.compile(r"_uni_full_(?P<b>.+?)_(?P<i>\d+)\.root$")
bands = {}
for p in sorted(glob.glob(f"{SWEEP}/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root")):
    mm = UNI_RE.search(os.path.basename(p))
    if not mm:
        continue
    bands.setdefault(mm.group("b"), []).append((int(mm.group("i")), p))
res["n_universe_files"] = sum(len(v) for v in bands.values())
res["n_bands"] = len(bands)
X = {}
for b, lst in bands.items():
    lst.sort()
    X[b] = np.stack([h2np(p)[0][m] for _, p in lst])
# sha of the flux and MINOS universe files and the CV
for b in ("Flux", "Muon_Energy_MINOS"):
    hh = hashlib.sha256()
    for _, p in bands[b]:
        hh.update(sha(p).encode())
    res[f"sha256_of_{b}_file_shas"] = hh.hexdigest()

def rel(C):
    return np.sqrt(np.clip(np.diag(C), 0, None)) / c

def integ(C):
    return float(np.sqrt(max(a @ C @ a, 0)) / I_cv)

mine = {b: wcov(X[b])[0] for b in X}
norm = np.outer(0.014 * c, 0.014 * c)
U_mine = sum(mine.values()) + norm

# Control 1: per-band blocks and the universe total against the adopted product
sha(UNIV_ADOPTED)
ctrl = {}
maxrel = 0.0
for b, C in mine.items():
    A = sq(UNIV_ADOPTED, f"hCov_universe_full_{b}")
    if A is None:
        ctrl[f"missing_{b}"] = True
        continue
    maxrel = max(maxrel, float(np.abs(A - C).max() / np.abs(A).max()) if np.abs(A).max() > 0 else 0.0)
ctrl["per_band_max_rel_diff_vs_adopted"] = maxrel
Ut = sq(UNIV_ADOPTED, "hCov_universe_total")
ctrl["universe_total_max_rel_diff_vs_adopted"] = float(np.abs(Ut - U_mine).max() / np.abs(Ut).max())
An = sq(UNIV_ADOPTED, "hCov_universe___Normalization_flat")
ctrl["norm_block_present"] = An is not None
names = []
fa = ROOT.TFile.Open(UNIV_ADOPTED)
for k in fa.GetListOfKeys():
    names.append(k.GetName())
fa.Close()
ctrl["adopted_keys"] = names
ctrl["adopted_has_cross_block_key"] = any("cross" in s.lower() or "muone" in s.lower() for s in names)
# sum of adopted per-band blocks (+norm) equals adopted total => no extra cross block
S = np.zeros_like(Ut)
for s in names:
    if s.startswith("hCov_universe_") and s != "hCov_universe_total":
        S += sq(UNIV_ADOPTED, s)
ctrl["adopted_total_minus_sum_of_adopted_blocks_max_rel"] = float(np.abs(Ut - S).max() / np.abs(Ut).max())
ctrl["flux_band_unweighted_median"] = float(np.median(rel(mine["Flux"])))
ctrl["minos_band_median"] = float(np.median(rel(mine["Muon_Energy_MINOS"])))
ctrl["universe_total_median"] = float(np.median(rel(U_mine)))

sha(BOOT); sha(ML)
Cb = sq(BOOT, "hCov2D_reported")
Cml = sq(ML, "hCov2D_reported")
Hc = sq(UNIV_ADOPTED, "hCov_combined")
ctrl["hCov_combined_eq_univ_plus_boot_max_rel"] = float(np.abs(Hc - (Ut + Cb)).max() / np.abs(Hc).max())
tot0 = U_mine + Cb + Cml
ctrl["total_median_adopted_construction"] = float(np.median(rel(tot0)))
ctrl["total_median_without_ML"] = float(np.median(rel(U_mine + Cb)))
ctrl["total_integral_sigma"] = integ(tot0)
ctrl["boot_median"] = float(np.median(rel(Cb)))
ctrl["ml_median"] = float(np.median(rel(Cml)))
res["control"] = ctrl

# ------------------------------------------------------------------ C04: weighted flux band
XF = X["Flux"]
Cf_u, mu_u = wcov(XF)
Cf_w, mu_w = wcov(XF, w)
If = XF @ a
res["C04"] = {
    "flux_band_median_unweighted": float(np.median(rel(Cf_u))),
    "flux_band_median_weighted": float(np.median(rel(Cf_w))),
    "flux_band_max_unweighted": float(rel(Cf_u).max()),
    "flux_band_max_weighted": float(rel(Cf_w).max()),
    "flux_band_min_unweighted": float(rel(Cf_u).min()),
    "flux_band_min_weighted": float(rel(Cf_w).min()),
    "ratio_weighted_over_unweighted_median": float(np.median(rel(Cf_w) / rel(Cf_u))),
    "integral_sigma_unweighted": integ(Cf_u),
    "integral_sigma_weighted": integ(Cf_w),
    "universe_mean_over_cv_median_unweighted": float(np.median(mu_u / c)),
    "universe_mean_over_cv_median_weighted": float(np.median(mu_w / c)),
    "universe_mean_integral_over_cv_unweighted": float((a @ mu_u) / I_cv),
    "universe_mean_integral_over_cv_weighted": float((a @ mu_w) / I_cv),
    "flux_band_median_unweighted_cvcentred": float(np.median(np.sqrt(((XF - c) ** 2).mean(0)) / c)),
    "flux_band_median_weighted_cvcentred": float(np.median(np.sqrt((w[:, None] * (XF - c) ** 2).sum(0) / w.sum()) / c)),
}
# MAT path on the cross section: MnvH1D over the 205 reported cells with the Flux band and the univ weights
n = c.size
hx = ROOT.PlotUtils.MnvH1D("hxs_flux", "", n, 0.0, float(n))
for i in range(n):
    hx.SetBinContent(i + 1, float(c[i])); hx.SetBinError(i + 1, 0.0)
hx.AddVertErrorBand("Flux", int(w.size))
vb = hx.GetVertErrorBand("Flux")
for u in range(w.size):
    hu_ = vb.GetHist(u)
    for i in range(n):
        hu_.SetBinContent(i + 1, float(XF[u, i])); hu_.SetBinError(i + 1, 0.0)
tm = hx.GetTotalErrorMatrix(False, False, False)
Cmat_unw = np.array([[tm(i + 1, j + 1) for j in range(n)] for i in range(n)])
vec = ROOT.std.vector("double")()
for x in w:
    vec.push_back(float(x))
vb.SetUnivWgts(vec)
tm = hx.GetTotalErrorMatrix(False, False, False)
Cmat_w = np.array([[tm(i + 1, j + 1) for j in range(n)] for i in range(n)])
res["C04"]["mat_gettotalerrormatrix_unweighted_vs_numpy_max_rel"] = float(np.abs(Cmat_unw - Cf_u).max() / np.abs(Cf_u).max())
res["C04"]["mat_gettotalerrormatrix_weighted_vs_numpy_max_rel"] = float(np.abs(Cmat_w - Cf_w).max() / np.abs(Cf_w).max())
res["C04"]["mat_weighted_median"] = float(np.median(rel(Cmat_w)))

# ------------------------------------------------------------------ X01: MINOS denominator
XM = X["Muon_Energy_MINOS"]
XMc = XM / r_minos[:, None]
Cm0 = wcov(XM)[0]
Cm1 = wcov(XMc)[0]
res["X01"] = {
    "minos_band_median_adopted": float(np.median(rel(Cm0))),
    "minos_band_median_corrected": float(np.median(rel(Cm1))),
    "minos_integral_sigma_adopted": integ(Cm0),
    "minos_integral_sigma_corrected": integ(Cm1),
    "minos_integral_shift_u0_u1_adopted": [float(a @ XM[u] / I_cv - 1) for u in range(2)],
    "minos_integral_shift_u0_u1_corrected": [float(a @ XMc[u] / I_cv - 1) for u in range(2)],
}

# ------------------------------------------------------------------ diagnostic budgets (NOT QUOTABLE)
def budget(flux_C, minos_C):
    blocks = dict(mine)
    blocks["Flux"] = flux_C
    blocks["Muon_Energy_MINOS"] = minos_C
    Usys = sum(blocks.values()) + norm
    T = Usys + Cb + Cml
    return {"syst_median": float(np.median(rel(Usys))), "total_median": float(np.median(rel(T))),
            "total_p84": float(np.percentile(rel(T), 84)), "total_max": float(rel(T).max()),
            "syst_integral": integ(Usys), "total_integral": integ(T),
            "flux_median": float(np.median(rel(flux_C))), "minos_median": float(np.median(rel(minos_C)))}

res["diagnostic_NOT_QUOTABLE"] = {
    "adopted (unweighted flux, Phi_CV MINOS)": budget(Cf_u, Cm0),
    "C04 weighted flux only": budget(Cf_w, Cm0),
    "X01 MINOS Phi_u only": budget(Cf_u, Cm1),
    "C04 + X01": budget(Cf_w, Cm1),
}
# cross-block side check: the ours-only rank-2 cross block with rho=0.900 (rederive_flux_muonE_cross.py route B form)
def lead(C):
    ev, V = np.linalg.eigh(C)
    v = V[:, -1] * np.sign(V[np.argmax(np.abs(V[:, -1])), -1])
    return np.sqrt(max(ev[-1], 0)) * v
dfl = lead(Cf_u); de = lead(mine["Muon_Energy_MINOS"] + mine["Muon_Energy_MINERvA"])
Cx = 0.900 * (np.outer(dfl, de) + np.outer(de, dfl))
res["cross_block_side_check"] = {
    "total_median_with_rho0.9_cross_added": float(np.median(rel(tot0 + Cx))),
    "total_integral_with_rho0.9_cross_added": integ(tot0 + Cx),
}

json.dump(res, open(OUT, "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k != "sha256"}, indent=1, default=float))
