import sys, json, numpy as np
from scipy.optimize import lsq_linear
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
REPO = "/Users/josephbailey/local-research/MINERvA-OmniFold"
w = np.load(SC + "/wstest/wsplit_a1.npz"); A, M4 = w["A"], w["M4"]
z = np.load(SC + "/priortest/in/signed_data.npz"); M0, T0 = z["response"], z["prior"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root")
N = cpf.flatten_ours(f.Get("hDataReco2D")); B0 = cpf.flatten_ours(f.Get("hBkgReco2D"))
fp = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
Ci = np.linalg.pinv(C[np.ix_(mask, mask)]); D = lambda x: float((x - pub)[mask] @ Ci @ (x - pub)[mask]) / 205
mx = lambda a, b: float(np.max(np.abs(a - b)) / np.max(np.abs(b)))
ctl = {"C-CV-T": mx(A.sum(1), T0), "C-CV-M": mx(M4.sum(2), M0)}
ship = np.zeros(224)
for line in open(REPO + "/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"):
    if line.lower().startswith("p|"): continue
    pz, pt, s = line.strip().split(","); ship[(int(pt)-1)*16 + int(pz)-1] = float(s)
NAB = A.shape[1]; free = NAB - 1                      # last bin: non-finite E_nu/Q2, weight fixed at 1
j = np.flatnonzero(mask); G = A[j][:, :free] * (F[j] / ship[j])[:, None]; const = A[j][:, free] * F[j] / ship[j]
lam = 1e-4; Aaug = np.vstack([G, np.sqrt(lam) * np.eye(free)]); baug = np.concatenate([1 - const, np.sqrt(lam) * np.ones(free)])
sol = lsq_linear(Aaug, baug, bounds=(0.2, 5.0)); wab = np.concatenate([sol.x, [1.0]])
Tp = A @ wab; Mp = M4 @ wab
ipt, ipz = np.divmod(np.arange(224), 16)
rat0 = np.where(mask, ship / np.where(T0 * F > 0, T0 * F, 1) - 1, np.nan); rat = np.where(mask, ship / np.where(Tp * F > 0, Tp * F, 1) - 1, np.nan)
fitq = dict(median_abs_before=float(np.nanmedian(np.abs(rat0))), median_abs_after=float(np.nanmedian(np.abs(rat))),
            row0_before=float(np.nanmean(rat0[ipt == 0])), row0_after=float(np.nanmean(rat[ipt == 0])),
            col15_before=float(np.nanmean(rat0[ipz == 15])), col15_after=float(np.nanmean(rat[ipz == 15])))
cfit = fitq["median_abs_after"] <= 0.01 and abs(fitq["row0_after"]) <= 0.02 and abs(fitq["col15_after"]) <= 0.02
tpub = np.where(mask, pub / np.where(F > 0, F, 1), ur10)
def R(M, T): return np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
s0 = float(np.load(SC + "/lattest/lat/CV.npz")["pot_scale"])
f0 = R(M0, T0) @ tpub; e2 = N + s0 * (M0 @ ((tpub / np.where(T0 > 0, T0, 1))**2)); wgt = np.where(f0 > 0, f0**2 / e2, 0)
use = N > 0; REG = {"COL": use & (ipz == 15), "ROW": use & (ipt == 0)}
y = N - B0
def S(fo):
    r = np.where(fo > 0, y / np.where(fo > 0, fo, 1) - 1, 0); g = np.sum(wgt[use] * r[use]) / np.sum(wgt[use])
    return {k: float(np.sum(wgt[m] * r[m]) / np.sum(wgt[m]) - g) for k, m in REG.items()}
Scv, Sw = S(f0), S(R(Mp, Tp) @ tpub)
def cls(a, b):
    if abs(b) > 1.3 * abs(a): return "WRONG-WAY"
    if abs(b) <= abs(a) / 3: return "EXPLAINS"
    return "PARTIAL" if 1 - abs(b) / abs(a) >= 0.3 else "NONE"
def dag(M, T, yy, K=10):
    Rm = R(M, T); eff = Rm.sum(0); u = T.copy()
    for _ in range(K):
        fold = Rm @ u; ratio = np.divide(yy, fold, out=np.zeros_like(yy), where=fold > 0)
        u = np.divide(u * (Rm.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
    return u
Dcv, Dw = D(F * dag(M0, T0, y)), D(F * dag(Mp, Tp, y)); fD = (Dcv - Dw) / Dcv
icls = "MAIN" if fD >= .5 else "PARTIAL" if fD >= .2 else "MINOR" if abs(fD) < .2 else "AWAY"
ok = all(x <= 1e-9 for x in ctl.values())
out = dict(controls=ctl, controls_pass=ok, C_FIT=cfit, fit=fitq, weight_range=[float(wab[:free].min()), float(wab[:free].max())],
           S_CV_pct={k: 100 * x for k, x in Scv.items()}, S_W_pct={k: 100 * x for k, x in Sw.items()},
           reading=("STOP" if not ok else "WEIGHT-MODEL-INADEQUATE" if not cfit else {k: cls(Scv[k], Sw[k]) for k in REG}),
           readings_if_inadequate_reported={k: cls(Scv[k], Sw[k]) for k in REG},
           IBU_K10=dict(D_cv=Dcv, D_w=Dw, f=fD, cls=icls))
print(json.dumps(out, indent=1))
