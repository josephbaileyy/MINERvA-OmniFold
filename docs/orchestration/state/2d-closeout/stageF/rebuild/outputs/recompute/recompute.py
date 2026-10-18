"""Independent recomputation of 2D closeout numbers from pinned inputs."""
import hashlib, json, sys
import numpy as np
import ROOT

P = "/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz"
L = "/global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-term-20261016/playlist_term.npz"
EU = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
PA = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root"
PIN = {P: "6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc",
       L: "c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476",
       EU: "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c",
       PA: "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3"}
for f, h in PIN.items():
    got = hashlib.sha256(open(f, "rb").read()).hexdigest()
    assert got == h, (f, got)
    print("sha256 OK", f)
print("numpy", np.__version__, "ROOT", ROOT.gROOT.GetVersion())

NPT, NPZ = 14, 16
out = {}

# ---- E_U on the 224 grid, global id = pt*16+pz
f = ROOT.TFile.Open(EU)
h = f.Get("hXSec2D")
assert h.GetNbinsX() == NPT and h.GetNbinsY() == NPZ
eu224 = np.array([h.GetBinContent(pt + 1, pz + 1) for pt in range(NPT) for pz in range(NPZ)])
eu_err224 = np.array([h.GetBinError(pt + 1, pz + 1) for pt in range(NPT) for pz in range(NPZ)])
cells = np.flatnonzero(eu224 != 0)
print("E_U nonzero cells:", cells.size, "negative:", int((eu224 < 0).sum()))
x = eu224[cells]

# ---- Paper on the 224 grid. TH2D X = p||, Y = pT (verified by edges).
g = ROOT.TFile.Open(PA)
hp = g.Get("pt_pl_cross_section")
assert hp.GetNbinsX() == NPZ and hp.GetNbinsY() == NPT
assert abs(hp.GetXaxis().GetBinLowEdge(1) - 1.5) < 1e-9 and abs(hp.GetYaxis().GetBinLowEdge(NPT + 1) - 4.5) < 1e-9
pap224 = np.array([hp.GetBinContent(pz + 1, pt + 1) for pt in range(NPT) for pz in range(NPZ)])
pap_err224 = np.array([hp.GetBinError(pz + 1, pt + 1) for pt in range(NPT) for pz in range(NPZ)])

def tm(name):
    m = g.Get(name)
    n = m.GetNrows()
    return np.array([[m(i, j) for j in range(n)] for i in range(n)])
TOT = tm("TotalCovariance"); STAT = tm("StatOnlyCovariance")
rep = np.flatnonzero(np.diag(STAT) > 0)
print("paper reported cells (diag StatOnly>0):", rep.size, "equal to E_U cells:", np.array_equal(rep, cells))
assert np.array_equal(rep, cells)
print("paper xsec nonzero cells equal:", np.array_equal(np.flatnonzero(pap224 != 0), cells))
# cross-check covariance diag vs TH2D errors (orientation check)
d_tot = np.sqrt(np.diag(TOT))[cells]; e_h = pap_err224[cells]
print("paper TH2D err / sqrt(diag Total): min %.6g max %.6g" % ((e_h / d_tot).min(), (e_h / d_tot).max()))
d_st = np.sqrt(np.diag(STAT))[cells]
print("paper TH2D err / sqrt(diag Stat):  min %.6g max %.6g" % ((e_h / d_st).min(), (e_h / d_st).max()))
# transposed-orientation control: reading paper with X=pT must not match
pap_T = np.array([hp.GetBinContent(pt + 1, pz + 1) if (pt < NPZ and pz < NPT) else 0 for pt in range(NPT) for pz in range(NPZ)])
print("paper/E_U ratio median (correct orientation): %.4f ; (transposed read) median %.4f"
      % (np.median(pap224[cells] / x), np.median(pap_T[cells] / x)))
p = pap224[cells]
Tp = TOT[np.ix_(cells, cells)]; Sp = STAT[np.ix_(cells, cells)]

# ---- npz inputs
z = np.load(P, allow_pickle=False)
pl = np.load(L, allow_pickle=False)
print("npz cells_x_EU == E_U on cells: maxabs rel diff %.3g" % np.max(np.abs(z["cells_x_EU"] / x - 1)))
print("playlist cells == E_U cells:", np.array_equal(pl["cells"], cells),
      " playlist x == E_U: maxrel %.3g" % np.max(np.abs(pl["x"] / x - 1)))
print("playlist F == functionals:", np.array_equal(pl["F"], z["functionals"]),
      "maxabs", np.max(np.abs(pl["F"] - z["functionals"])))
Fn = z["functionals"]; a = z["area"]
print("functionals row0 == area:", np.array_equal(Fn[0], a), "maxabs", np.max(np.abs(Fn[0] - a)))
# identify rows 1..14 as pT projections and 15..30 as p|| projections by support
pt_of = cells // NPZ; pz_of = cells % NPZ
for r in range(1, 31):
    s = Fn[r] != 0
    pts = np.unique(pt_of[s]); pzs = np.unique(pz_of[s])
    kind = "pT=%s" % pts.tolist() if pts.size == 1 else ("pz=%s" % pzs.tolist() if pzs.size == 1 else "MIXED")
    # check weights equal area restricted to the slice
    rel = np.max(np.abs(Fn[r][s] / a[s] - 1))
    print("  row %2d: n=%3d %s  max|f/area-1| on support=%.2g" % (r, s.sum(), kind, rel))
# does the sum of pT rows equal the area row?
print("sum rows1-14 == row0 maxabs:", np.max(np.abs(Fn[1:15].sum(0) - Fn[0])),
      " sum rows15-30 == row0 maxabs:", np.max(np.abs(Fn[15:31].sum(0) - Fn[0])))

covs = {
    "Q": z["total"] + pl["C_PL"],
    "total": z["total"],
    "universe": z["universe"],
    "stat": z["stat"],
    "c08": z["c08"],
    "C_PL": pl["C_PL"],
    "universe+stat": z["universe"] + z["stat"],
    "band_Flux": z["band_Flux"],
}
for k, C in covs.items():
    assert C.shape == (205, 205)
    print("%-14s asym max|C-C^T|/max|C| = %.3g" % (k, np.max(np.abs(C - C.T)) / np.max(np.abs(C))))

def relsig(C):
    s = 100 * np.sqrt(np.diag(C)) / x
    integ = 100 * np.sqrt(a @ C @ a) / (a @ x)
    proj = [100 * np.sqrt(fr @ C @ fr) / (fr @ x) for fr in Fn]
    return dict(median=float(np.median(s)), p84=float(np.percentile(s, 84)), max=float(np.max(s)),
                integral=integ, proj=[float(v) for v in proj])

out["sigma"] = {}
for k, C in covs.items():
    r = relsig(C)
    out["sigma"][k] = r
    print("%-14s median %.6f  p84 %.6f  max %.6f  integral %.6f  proj0 %.6f" %
          (k, r["median"], r["p84"], r["max"], r["integral"], r["proj"][0]))
    print("   pT proj  :", " ".join("%.4f" % v for v in r["proj"][1:15]))
    print("   pz proj  :", " ".join("%.4f" % v for v in r["proj"][15:31]))

def ranks(C):
    w = np.linalg.eigvalsh(0.5 * (C + C.T))
    lm = w.max()
    return int((w > 1e-10 * lm).sum()), int((w > 1e-12 * lm).sum()), float(lm), float(w.min())
out["ranks"] = {}
for k in ("universe", "universe+stat", "total", "Q"):
    r10, r12, lm, wmin = ranks(covs[k])
    out["ranks"][k] = [r10, r12]
    print("rank %-14s 1e-10: %d  1e-12: %d  (lmax %.4g, lmin %.4g)" % (k, r10, r12, lm, wmin))

# ---- chi2 vs paper
Q = covs["Q"]
d = x - p
print("units check: median paper/E_U = %.6f" % np.median(p / x))

def pinv_chi2(d, C, label):
    Cs = 0.5 * (C + C.T)
    v = np.linalg.pinv(Cs)
    c = float(d @ v @ d)
    # eigen-based cross-check with explicit cutoff 1e-15*lmax (numpy pinv default rcond)
    w, U = np.linalg.eigh(Cs)
    keep = np.abs(w) > 1e-15 * np.abs(w).max()
    y = U.T @ d
    c2 = float(np.sum(y[keep] ** 2 / w[keep]))
    print("%-26s chi2 %.4f  chi2/205 %.6f   (eig cross-check %.4f, kept %d, cond %.4g, nneg %d)" %
          (label, c, c / 205, c2, keep.sum(), np.abs(w).max() / np.abs(w).min(), int((w < 0).sum())))
    return c

out["chi2"] = {}
out["chi2"]["standard"] = pinv_chi2(d, Tp + Q, "standard (Tot+Q)")
out["chi2"]["stat_subtracted"] = pinv_chi2(d, Tp - Sp + Q, "stat-subtracted (Tot-Stat+Q)")
# log-normal: delta = ln(E_U) - ln(paper); C_ln = Tot_ij/(p_i p_j) + Q_ij/(x_i x_j)
assert np.all(x > 0) and np.all(p > 0)
dl = np.log(x) - np.log(p)
Cln_A = Tp / np.outer(p, p) + Q / np.outer(x, x)
out["chi2"]["lognormal_A"] = pinv_chi2(dl, Cln_A, "lognormal A (own-CV scaled)")
Cln_B = (Tp + Q) / np.outer(p, p)
out["chi2"]["lognormal_B"] = pinv_chi2(dl, Cln_B, "lognormal B (paper-scaled)")
Cln_C = (Tp + Q) / np.outer(x, x)
out["chi2"]["lognormal_C"] = pinv_chi2(dl, Cln_C, "lognormal C (E_U-scaled)")
Cln_D = (Tp + Q) / np.outer(np.sqrt(x * p), np.sqrt(x * p))
out["chi2"]["lognormal_D"] = pinv_chi2(dl, Cln_D, "lognormal D (geo-mean)")
Cln_E = np.log1p((Tp + Q) / np.outer(p, p))
out["chi2"]["lognormal_E"] = pinv_chi2(dl, Cln_E, "lognormal E log(1+C/pp)")
Cln_F = np.log1p(Tp / np.outer(p, p)) + np.log1p(Q / np.outer(x, x))
out["chi2"]["lognormal_F"] = pinv_chi2(dl, Cln_F, "lognormal F log1p each")

sd = np.sqrt(np.diag(Tp + Q))
pull = d / sd
out["pull"] = dict(mean=float(pull.mean()), rms=float(np.sqrt(np.mean(pull ** 2))), std=float(pull.std()))
print("pull mean %.6f  RMS %.6f  (std %.6f)" % (pull.mean(), np.sqrt(np.mean(pull ** 2)), pull.std()))

# ---- ours-only direct inverse
out["direct"] = {}
for k in ("Q", "universe+stat"):
    C = covs[k]
    c = float(d @ np.linalg.inv(C) @ d)
    cond = float(np.linalg.cond(C))
    cs = float(d @ np.linalg.inv(0.5 * (C + C.T)) @ d)
    cp = float(d @ np.linalg.pinv(0.5 * (C + C.T)) @ d)
    out["direct"][k] = dict(chi2=c, ndf=c / 205, cond=cond)
    print("direct inv %-14s chi2 %.4f chi2/205 %.6f cond %.6g   (sym-inv %.4f, pinv %.4f)" % (k, c, c / 205, cond, cs, cp))

json.dump(out, open("recompute_results.json", "w"), indent=1)
