import sys, json, hashlib, numpy as np
REPO = "/Users/josephbailey/local-research/MINERvA-OmniFold"; sys.path.insert(0, REPO + "/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
NPZ = SC + "/priortest/in/signed_data.npz"; PUB = "/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"
MOD = REPO + "/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
ctl = {"C-SHA": sha(NPZ).startswith("7a35b7e2") and sha(PUB).startswith("6c6dce72")}

def dagostini(M, T, y, ks, u0=None):   # ref_c2c1.py:262 at 853371c6, verbatim except the optional start u0
    R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
    eff = R.sum(axis=0)
    u = (T if u0 is None else u0).astype(float).copy()
    out = {}
    for k in range(1, max(ks) + 1):
        fold = R @ u
        ratio = np.divide(y, fold, out=np.zeros_like(y), where=fold > 0)
        u = np.divide(u * (R.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
        if k in ks: out[k] = u.copy()
    return out

z = np.load(NPZ); M, T, yr, ys, cells = z["response"], z["prior"], z["refined_y"], z["signed_y"], z["cells"]
ks = list(z["ks"]); RX, SX = z["refined_xsec"], z["signed_xsec"]
fp = ROOT.TFile.Open(PUB); pub = cpf.flatten_th2d(fp.Get("pt_pl_cross_section")); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
mask = np.diag(C) > 0; assert np.array_equal(np.flatnonzero(mask), np.sort(cells))
Ci = np.linalg.pinv(C[np.ix_(mask, mask)]); D = lambda x: float((x - pub)[mask] @ Ci @ (x - pub)[mask]) / 205

KALL = list(range(1, 21))
ur = dagostini(M, T, yr, KALL); us = dagostini(M, T, ys, KALL)
F = np.zeros(224); F[mask] = RX[ks.index(5)][mask] / ur[5][mask]
rel = lambda a, b: float(np.max(np.abs(a[mask] / b[mask] - 1)))
ctl["C-K10"] = rel(F * ur[10], RX[ks.index(10)]) <= 1e-8
ctl["C-SGN"] = max(rel(F * us[5], SX[ks.index(5)]), rel(F * us[10], SX[ks.index(10)])) <= 1e-8
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]); PZ = cpf.PZ_EDGES if hasattr(cpf,"PZ_EDGES") else np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
area = np.array([(PT[i+1]-PT[i])*(PZ[j+1]-PZ[j]) for i in range(14) for j in range(16)])
k = (F * area)[mask]; ctl["C-FAC"] = (k.max() - k.min()) / k.mean() <= 1e-9
Dr = {K: D(F * ur[K]) for K in KALL}; Ds = {K: D(F * us[K]) for K in KALL}
ctl["C-D"] = all(abs(a - b) <= 1e-5 for a, b in [(Dr[5], .829947), (Dr[10], 1.026575), (Ds[5], .815846), (Ds[10], .961361)])
scan_ok = all(round(Dr[K], 2) == v for K, v in zip([1,2,3,4,15,20], [3.95,1.59,1.08,0.90,1.52,2.16]))
tv = np.load(SC + "/truthtest/vectors.npz"); ctl["C-TRU"] = rel(T * F, tv["m"]) <= 1e-6

ship = np.zeros(224)
for line in open(MOD):
    if line.lower().startswith("p|"): continue
    pz, pt, s = line.strip().split(","); ship[(int(pt)-1)*16 + int(pz)-1] = float(s)
w = np.ones(224); w[mask] = ship[mask] / (T * F)[mask]; Tp = w * T
upr = dagostini(M * w[None, :], Tp, yr, KALL); ups = dagostini(M * w[None, :], Tp, ys, KALL)
Dpr = {K: D(F * upr[K]) for K in KALL}; Dps = {K: D(F * ups[K]) for K in KALL}
cls = lambda d, dp: (lambda f: "MAIN" if f >= .5 else "PARTIAL" if f >= .2 else "MINOR" if abs(f) < .2 else "AWAY")((d - dp) / d)
u0 = np.where(mask, pub / np.where(F > 0, F, 1), T)   # ceiling arm: prior = the published result
uc = dagostini(M, T, yr, [5, 10], u0=u0)
out = dict(controls=ctl, C_SCAN=scan_ok,
  primary=dict(D=Dr[10], Dp=Dpr[10], f=(Dr[10]-Dpr[10])/Dr[10], cls=cls(Dr[10], Dpr[10])),
  sec_signed_K10=dict(D=Ds[10], Dp=Dps[10], f=(Ds[10]-Dps[10])/Ds[10], cls=cls(Ds[10], Dps[10])),
  sec_refined_K5=dict(D=Dr[5], Dp=Dpr[5], f=(Dr[5]-Dpr[5])/Dr[5], cls=cls(Dr[5], Dpr[5])),
  scan_refined={K: [round(Dr[K], 4), round(Dpr[K], 4)] for K in KALL},
  ceiling_prior_is_published=dict(K5=D(F*uc[5]), K10=D(F*uc[10])),
  weights=dict(min=float(w[mask].min()), max=float(w[mask].max())),
  per_cell_change_K10_pct=dict(median_abs=float(np.median(np.abs(upr[10]/ur[10]-1)[mask])*100), max_abs=float(np.max(np.abs(upr[10]/ur[10]-1)[mask])*100)))
out["reading"] = "STOP" if not all(ctl.values()) else out["primary"]["cls"]
np.savez(SC + "/priortest/vectors.npz", F=F, ur10=ur[10], upr10=upr[10], pub=pub, mask=mask, w=w)
print(json.dumps(out, indent=1, default=lambda o: o.item()))
