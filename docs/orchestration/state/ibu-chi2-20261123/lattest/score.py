import sys, json, glob, os, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
L = {os.path.basename(p)[:-4]: np.load(p) for p in glob.glob(SC + "/lattest/lat/*.npz")}
z = np.load(SC + "/priortest/in/signed_data.npz"); M0, T0 = z["response"], z["prior"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root")
N = cpf.flatten_ours(f.Get("hDataReco2D")); B0 = cpf.flatten_ours(f.Get("hBkgReco2D"))
fp = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
Ci = np.linalg.pinv(C[np.ix_(mask, mask)]); D = lambda x: float((x - pub)[mask] @ Ci @ (x - pub)[mask]) / 205
cv = L["CV"]; mx = lambda a, b: float(np.max(np.abs(a - b)) / np.max(np.abs(b)))
ctl = {"C-CV-M": mx(cv["M"], M0), "C-CV-T": mx(cv["T"], T0), "C-CV-B": float(np.max(np.abs(cv["B"] - B0)[B0 > 0] / B0[B0 > 0]))}
ctl["C-TRUTH"] = max(mx(L[k]["T"], cv["T"]) for k in L)
ok = all(val <= 1e-9 for val in ctl.values())
tpub = np.where(mask, pub / np.where(F > 0, F, 1), ur10)
def R(M, T): return np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
s = float(cv["pot_scale"]); Tcv = cv["T"]
f0 = R(cv["M"], Tcv) @ tpub
e2 = N + s * (cv["M"] @ ((tpub / np.where(Tcv > 0, Tcv, 1))**2)); wgt = np.where(f0 > 0, f0**2 / e2, 0)
ipt, ipz = np.divmod(np.arange(224), 16)
REG = {"COL": (ipz == 15) & (N > 0), "ROW": (ipt == 0) & (N > 0)}
def dag(M, T, y, K=10):
    Rm = R(M, T); eff = Rm.sum(0); u = T.copy()
    for _ in range(K):
        fold = Rm @ u; ratio = np.divide(y, fold, out=np.zeros_like(y), where=fold > 0)
        u = np.divide(u * (Rm.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
    return u
res = {}
for k, d in L.items():
    fo = R(d["M"], d["T"]) @ tpub; y = N - d["B"]; r = np.where(fo > 0, y / np.where(fo > 0, fo, 1) - 1, 0)
    res[k] = {reg: float(np.sum(wgt[m] * r[m]) / np.sum(wgt[m])) for reg, m in REG.items()}
    res[k]["D10_signed"] = D(F * dag(d["M"], d["T"], y)); res[k]["fold_G"] = float(np.sum(((y - fo)**2 / e2)[REG["COL"] | (N > 0)]) / int((N > 0).sum()))
def band(b, reg):
    ym, y0, yp = res[f"{b}_0"][reg], res["CV"][reg], res[f"{b}_1"][reg]
    c = np.polyfit([-1, 0, 1], [ym, y0, yp], 2); roots = [x.real for x in np.roots(c) if abs(x.imag) < 1e-12 and abs(x.real) <= 3]
    sig = min(roots, key=abs) if roots else None
    red = max(1 - abs(ym) / abs(y0), 1 - abs(yp) / abs(y0))
    cls = ("CLOSES-2" if abs(sig) <= 2 else "CLOSES-3") if sig is not None else ("MOVES" if red >= 0.3 else "NO-EFFECT")
    return dict(idx0_pct=100 * ym, cv_pct=100 * y0, idx1_pct=100 * yp, sigma_star=sig, best_1sig_reduction=red, reading=cls)
bands = ("Muon_Energy_MINOS", "MuonResolution", "Muon_Energy_MINERvA", "BeamAngleX", "BeamAngleY")
out = dict(controls=ctl, controls_pass=ok,
           readings={f"{reg}:{b}" + (" (primary)" if (reg == "COL" and b in bands[:2]) or (reg == "ROW" and b in bands[3:]) else ""): band(b, reg)
                     for reg in ("COL", "ROW") for b in bands} if ok else "STOP",
           D10_signed={k: round(res[k]["D10_signed"], 4) for k in sorted(res)})
print(json.dumps(out, indent=1, default=float))
