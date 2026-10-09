#!/usr/bin/env python3
"""Reviewer's independent pairing reductions (lane A claims). Own code; uproot only.

python3 -I rc_pairing.py OPS_DIR > rc_pairing.json
Does not import any repository module.
"""
import glob
import json
import os
import re
import sys

import numpy as np
import uproot

OPS = sys.argv[1]
B = os.path.join(OPS, "MINERvA-OmniFold/2d-unfolding")
ANC = os.path.join(B, "minerva_paper_anc")
REPO_ANC = sys.argv[2]  # repo copy of paper txts (bin_mapping.txt)
FR = os.path.join(OPS, "fluxraw")
out = {}


def th(path, name="hXSec2D"):
    h = uproot.open(path)[name]
    return h.values(flow=False), h.axis(0).edges(), h.axis(1).edges()


def vals(path, name):
    return uproot.open(path)[name].values(flow=False)


def pct(a):
    a = np.asarray(a, float)
    return dict(median=float(np.median(a)), p84=float(np.percentile(a, 84)), max=float(a.max()))


# ---------- paper GlobalID from bin_mapping.txt (not from a formula)
rows = [l.split(",") for l in open(os.path.join(REPO_ANC, "bin_mapping.txt")).read().strip().split("\n")[1:]]
gid_of = {}  # (ipt, ipz) 0-based -> gid
for r in rows:
    g, pzb, ptb = int(r[0]), int(r[1]), int(r[2])
    gid_of[(ptb - 1, pzb - 1)] = g
out["bin_mapping_n"] = len(gid_of)
out["gid_equals_rowmajor_pt_major"] = all(g == a * 16 + b for (a, b), g in gid_of.items())

# paper ROOT stat diag, paper TH2D
pr = uproot.open(os.path.join(ANC, "cov_ptpl_minerva_inclusive_6GeV.root"))
def tm(name):
    m = pr[name]
    n = int(m.member("fNrows"))
    return np.asarray(m.member("fElements")).reshape(n, n)
Pstat = tm("StatOnlyCovariance")
Ptot = tm("TotalCovariance")
out["paper_matrix_dim"] = Pstat.shape[0]
# also the stat text file
stat_txt = np.zeros(224)
for l in open(os.path.join(ANC, "cov_ptpl_minerva_inclusive_6GeV_stat.txt")).read().strip().split("\n")[1:]:
    i, j, c = l.split(",")
    if i == j:
        stat_txt[int(i)] = float(c)

xc, ex, ey = th(os.path.join(B, "2d_crossSection_omnifold_MEFHC_5iter.root"))
x42, ex2, ey2 = th(os.path.join(B, "uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"))
out["central_shape"] = list(xc.shape)
# confirm axis 0 = pT by comparing to bin_mapping edges
pt_lo = sorted({float(r[5]) for r in rows}); pz_lo = sorted({float(r[3]) for r in rows})
out["axis0_is_pt"] = bool(np.allclose(ex[:-1], pt_lo) and np.allclose(ey[:-1], pz_lo))
out["cv42_edges_same"] = bool(np.array_equal(ex, ex2) and np.array_equal(ey, ey2))

def to_gid(a2):
    v = np.zeros(224)
    for (a, b), g in gid_of.items():
        v[g] = a2[a, b]
    return v

reps = glob.glob(os.path.join(OPS, "ki84-rebuild-20261006/replicas/*_boot*.root"))
reps = sorted(reps, key=lambda p: int(re.search(r"boot(\d+)\.root$", p).group(1)))
out["n_replicas"] = len(reps)
out["replica_seeds_1_300"] = [int(re.search(r"boot(\d+)\.root$", p).group(1)) for p in reps] == list(range(1, 301))
R = np.stack([to_gid(th(p)[0]) for p in reps])  # (300, 224) in GlobalID order
seedf = sorted(glob.glob(os.path.join(B, "seedscan_lgbm/*_seed*.root")), key=lambda p: int(re.search(r"seed(\d+)\.root$", p).group(1)))
out["seedscan_files"] = [os.path.basename(p) for p in seedf]
S = np.stack([to_gid(th(p)[0]) for p in seedf])

XC = to_gid(xc); X42 = to_gid(x42)
masks = {
    "central>0": XC > 0, "cv42>0": X42 > 0, "vl170_mean>0": R.mean(0) > 0,
    "seedscan_mean>0": S.mean(0) > 0, "paper_root_statdiag>0": np.diag(Pstat) > 0,
    "paper_txt_statdiag>0": stat_txt > 0,
}
ref = masks["paper_root_statdiag>0"]
out["mask_counts"] = {k: int(v.sum()) for k, v in masks.items()}
out["mask_equal_paper"] = {k: bool(np.array_equal(v, ref)) for k, v in masks.items()}
M = ref
n = int(M.sum())
# the producers' reported index = row-major ravel of (pt,pz) restricted to mask; since gid==rowmajor this is ascending gid
order = np.flatnonzero(M)

# ---------- VL170 covariance: own two-pass sample covariance, ddof=1
Xr = R[:, M]
mu = Xr.mean(0)
Z = Xr - mu
C_S = Z.T @ Z / (Xr.shape[0] - 1)
Cs_st = vals(os.path.join(B, "uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"), "hCov2D_reported")
out["C_S_shape_stored"] = list(Cs_st.shape)
out["C_S_maxabs_rel"] = float(np.abs(C_S - Cs_st).max() / np.abs(Cs_st).max())
out["C_S_sqrt_trace"] = float(np.sqrt(np.trace(C_S)))
# ddof=0 alternative to show sensitivity
out["C_S_ddof0_vs_stored_maxrel"] = float(np.abs(C_S * 299 / 300 - Cs_st).max() / np.abs(Cs_st).max())
# check stored hMean2D / hStd2D
hm = to_gid(vals(os.path.join(B, "uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"), "hMean2D"))
out["stored_mean_vs_mine_maxrel"] = float(np.max(np.abs(hm[M] - mu) / mu))
sS = np.sqrt(np.diag(C_S))
out["C_S_median_rel_over_mean_pct"] = float(100 * np.median(sS / mu))
# completeness
cm = 0.0
for p in reps:
    c = vals(p, "hOFCompleteness2D"); t = vals(p, "hOFTruthDenom2D")
    cm = max(cm, float(np.abs(c[t > 0] - 1).max()))
out["replica_max_abs_c_minus_1"] = cm
c0 = vals(os.path.join(B, "2d_crossSection_omnifold_MEFHC_5iter.root"), "hOFCompleteness2D")
t0 = vals(os.path.join(B, "2d_crossSection_omnifold_MEFHC_5iter.root"), "hOFTruthDenom2D")
out["central_max_abs_c_minus_1"] = float(np.abs(c0[t0 > 0] - 1).max())

# ---------- ML covariance from 10 seedscan products
Sr = S[:, M]
Zs = Sr - Sr.mean(0)
C_ML = Zs.T @ Zs / (Sr.shape[0] - 1)
Cml_st = vals(os.path.join(B, "uq/seedscan_lgbm_ml/uq_covariance_ml.root"), "hCov2D_reported")
out["C_ML_maxabs_rel"] = float(np.abs(C_ML - Cml_st).max() / np.abs(Cml_st).max())
out["C_ML_sqrt_trace"] = float(np.sqrt(np.trace(C_ML)))

# ---------- Flux rescale at product level
fb = uproot.open(os.path.join(FR, "baseline_flux/flux_integral_universes_MEFHC.root"))
phcv = fb["hFluxCV"].values(flow=False)
phu = fb["hFluxUniv"].values(flow=False)  # (n_pt, nu)
out["flux_band_shape"] = [list(phcv.shape), list(phu.shape)]
SW = os.path.join(B, "uq/universe_sweep_fluxfix")
worst = 0.0; worst_unscaled = 0.0; nflux = 0
for u in range(phu.shape[1]):
    fx = os.path.join(SW, f"2d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_{u}.root")
    raw = os.path.join(FR, f"uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_{u}.root")
    a = th(fx)[0]; b = th(raw)[0]
    pred = b * (phcv / phu[:, u])[:, None]
    m = b != 0
    worst = max(worst, float(np.max(np.abs(a[m] - pred[m]) / np.abs(pred[m]))))
    worst_unscaled = max(worst_unscaled, float(np.max(np.abs(a[m] - b[m]) / np.abs(b[m]))))
    nflux += 1
out["flux_rescale_n"] = nflux
out["flux_rescale_max_rel_dev_from_phiCV_over_phiu"] = worst
out["flux_rescaled_vs_unscaled_max_rel_change"] = worst_unscaled
# is hFluxCV equal to central hFlux_pt (shape)?
hfp = vals(os.path.join(B, "2d_crossSection_omnifold_MEFHC_5iter.root"), "hFlux_pt")
out["hFluxCV_over_central_hFlux_pt"] = [float(v) for v in (phcv / hfp)[:3]]

# ---------- universe covariance, analyzer convention re-implemented from its documented text
pat = re.compile(r"_uni_(.+)_(\d+)\.root$")
bands = {}
allfiles = sorted(glob.glob(os.path.join(SW, "*_uni_full_*.root")))
nonmatch = []
for p in allfiles:
    m = pat.search(os.path.basename(p))
    if not m:
        nonmatch.append(os.path.basename(p)); continue
    bands.setdefault(m.group(1), []).append(to_gid(th(p)[0])[M])
out["universe_nonmatching"] = nonmatch
out["universe_bands"] = len(bands)
out["universe_count"] = sum(len(v) for v in bands.values())
out["universe_band_sizes"] = {k: len(v) for k, v in sorted(bands.items())}
x42m = X42[M]
def ucov(center="mean", denom="N", norm=0.014):
    C = np.zeros((n, n))
    for k, L in bands.items():
        D = np.stack(L) - x42m
        N = D.shape[0]
        Zb = D - D.mean(0) if center == "mean" else D
        C += Zb.T @ Zb / (N if denom == "N" else N - 1)
    v = norm * x42m
    return C + np.outer(v, v)
Ust = os.path.join(B, "uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root")
Cu_st = vals(Ust, "hCov_universe_total")
Cc_st = vals(Ust, "hCov_combined")
den = np.abs(Cu_st).max()
for tag, kw in {"mean_N_norm0.014(analyzer)": {}, "mean_Nminus1": dict(denom="N-1"),
                "cv_centered_N": dict(center="cv"), "no_norm": dict(norm=0.0),
                "norm_on_central_instead": None}.items():
    if kw is None:
        C = ucov(norm=0.0) + np.outer(0.014 * XC[M], 0.014 * XC[M])
    else:
        C = ucov(**kw)
    out[f"C_U_{tag}_maxabs_rel_vs_stored"] = float(np.abs(C - Cu_st).max() / den)
C_U = ucov()
# Flux band alone with and without rescale
fl_raw = np.stack([to_gid(th(os.path.join(FR, f"uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_{u}.root"))[0])[M] for u in range(100)]) - x42m
Zr = fl_raw - fl_raw.mean(0)
Cflux_raw = Zr.T @ Zr / 100
Cflux_st = vals(Ust, "hCov_universe_full_Flux")
D = np.stack(bands["full_Flux"]) - x42m; Zf = D - D.mean(0); Cflux = Zf.T @ Zf / 100
out["C_flux_mine_vs_stored_maxrel"] = float(np.abs(Cflux - Cflux_st).max() / np.abs(Cflux_st).max())
out["flux_sigma_median_rel_pct_rescaled_vs_unscaled"] = [float(100 * np.median(np.sqrt(np.diag(Cflux)) / x42m)), float(100 * np.median(np.sqrt(np.diag(Cflux_raw)) / x42m))]
out["combined_minus_U_minus_S_maxrel_of_S"] = float(np.abs(Cc_st - Cu_st - Cs_st).max() / np.abs(Cs_st).max())
out["norm_band_stored_key_present"] = any("Normalization" in k for k in uproot.open(Ust).keys())

# ---------- block-sum budget, two denominators
Ctot = C_U + C_S + C_ML
st = np.sqrt(np.diag(Ctot))
out["blocksum_median_rel_pct_den_cv42"] = float(100 * np.median(st / x42m))
out["blocksum_median_rel_pct_den_exact_central"] = float(100 * np.median(st / XC[M]))
out["blocksum_median_rel_pct_den_stored_mats_cv42"] = float(100 * np.median(np.sqrt(np.diag(Cu_st + Cs_st + Cml_st)) / x42m))

# ---------- central-value comparisons
sML = np.sqrt(np.diag(C_ML))
xcm = XC[M]; s1 = S[0, M]; sm = S.mean(0)[M]
def comp(a, b, label):
    z = np.abs(a - b) / sS
    zm = np.abs(a - b) / sML
    return dict(label=label, rel_pct=pct(100 * np.abs(a - b) / b), over_sigS=pct(z), over_sigML=pct(zm),
                n_gt1S=int((z > 1).sum()), n_gt2S=int((z > 2).sum()))
out["cmp"] = [comp(s1, xcm, "seed1 vs exact"), comp(sm, xcm, "seedmean vs exact"), comp(x42m, xcm, "cv42 vs exact"),
              comp(x42m, s1, "cv42 vs seed1"), comp(mu, s1, "VL170 mean vs seed1"),
              dict(label="exact vs seedmean / sigML", v=pct(np.abs(xcm - sm) / sML)),
              dict(label="sigML/sigS", v=pct(sML / sS))]
out["seed1_file_is"] = os.path.basename(seedf[0])
DA = np.diff(ex)[:, None] * np.diff(ey)[None, :]
out["total_xsec_central_cm2"] = float((xc * DA).sum())
print(json.dumps(out, indent=1))
