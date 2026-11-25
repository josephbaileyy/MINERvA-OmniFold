# Local scorer for the corrected-edge rebuild (DECLARATION sha 8b4a978b...). Reads fetched/rebuild.npz.
import sys, json, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
ST = "/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state/ibu-chi2-20261123"
Z = np.load(SC + "/rerun/fetched/rebuild.npz"); s = float(Z["pot_scale"])
P = np.load(ST + "/evloop/results/ibuchi_products.npz")
v = np.load(SC + "/priortest/vectors.npz"); F0, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
fp = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
Ci = np.linalg.pinv(C[np.ix_(mask, mask)]); Dist = lambda x: float((x - pub)[mask] @ Ci @ (x - pub)[mask]) / 205
PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
PT = {"OLD": np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]),
      "E": np.array([0,0.075,0.15,0.25,0.325,0.40,0.475,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50])}
area = {X: np.array([(e[i+1]-e[i])*(PZ[j+1]-PZ[j]) for i in range(14) for j in range(16)]) for X, e in PT.items()}
k = (F0 * area["OLD"])[mask]; ctl = {"C-FAC": float((k.max() - k.min()) / k.mean())}
Fx = {"OLD": F0, "E": F0 * area["OLD"] / area["E"]}
mx = lambda a, b: float(np.max(np.abs(a - b)) / np.max(np.abs(b)))
ctl.update({"C-OLD-M": mx(Z["OLD_M"], P["BASE_M"]), "C-OLD-T": mx(Z["OLD_T"], P["T"]), "C-OLD-B": mx(Z["OLD_B"], P["BASE_B"]), "C-OLD-N": mx(Z["OLD_N"], P["BASE_N"])})
def R(M, T): return np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
def dag(M, T, y, K=10):
    Rm = R(M, T); eff = Rm.sum(0); u = T.copy()
    for _ in range(K):
        fold = Rm @ u; ratio = np.divide(y, fold, out=np.zeros_like(y), where=fold > 0)
        u = np.divide(u * (Rm.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
    return u
ipt, ipz = np.divmod(np.arange(224), 16)
def stats(M, T, N, B, t):
    f0 = R(M, T) @ t; e2 = N + s * (M @ ((t / np.where(T > 0, T, 1))**2)); wgt = np.where(f0 > 0, f0**2 / np.where(e2 > 0, e2, 1), 0)
    use = N > 0; y = N - B; r = np.where(f0 > 0, y / np.where(f0 > 0, f0, 1) - 1, 0)
    g = np.sum(wgt[use] * r[use]) / np.sum(wgt[use])
    S = {"COL": float(np.sum((wgt * r)[use & (ipz == 15)]) / np.sum(wgt[use & (ipz == 15)]) - g),
         "ROW": float(np.sum((wgt * r)[use & (ipt == 0)]) / np.sum(wgt[use & (ipt == 0)]) - g)}
    S["cols"] = [float(np.sum((wgt * r)[use & (ipz == j)]) / np.sum(wgt[use & (ipz == j)]) - g) for j in range(16)]
    S["rows"] = [float(np.sum((wgt * r)[use & (ipt == i)]) / np.sum(wgt[use & (ipt == i)]) - g) for i in range(14)]
    return S
out = {"controls": ctl}
res = {}
for X in ("OLD", "E"):
    M, T, B, N = Z[f"{X}_M"], Z[f"{X}_T"], Z[f"{X}_B"], Z[f"{X}_N"]
    u = dag(M, T, N - B); tpub = np.where(mask, pub / np.where(Fx[X] > 0, Fx[X], 1), u)
    res[X] = {"D10": Dist(Fx[X] * u), "S_pub": stats(M, T, N, B, tpub), "S_own": stats(M, T, N, B, u)}
    if X == "E":
        eps_in = np.divide(M.sum(0), T, out=np.zeros(224), where=T > 0); eps_any = np.divide(M.sum(0) + Z["E_Mflow"], T, out=np.zeros(224), where=T > 0)
        t_any = np.where(eps_any > 0, u * eps_in / np.where(eps_any > 0, eps_any, 1), u)
        res["E"]["D10_any"] = Dist(Fx[X] * t_any); res["E"]["S_any"] = stats(M, T, N, B, t_any)
        res["E"]["eps_col15_in_any"] = [float((M.sum(0)[ipz == 15]).sum() / T[ipz == 15].sum()), float(((M.sum(0) + Z["E_Mflow"])[ipz == 15]).sum() / T[ipz == 15].sum())]
out["results"] = res
ok = ctl["C-FAC"] <= 1e-9 and all(ctl[k] <= 1e-9 for k in ("C-OLD-M", "C-OLD-T", "C-OLD-B", "C-OLD-N")) and abs(res["OLD"]["D10"] - 0.96136) <= 1e-4
if not ok: out["reading"] = "STOP"
else:
    Sp, Sa = res["E"]["S_pub"]["cols"], res["E"]["S_any"]["cols"]
    row = "ROW-CLOSED" if abs(res["E"]["S_pub"]["ROW"]) <= 0.02 else "ROW-OPEN"
    if abs(Sp[15] - Sa[15]) <= abs(Sp[15]) / 3 and abs(Sp[14] - Sa[14]) <= 0.01: ov = "OVERFLOW-EXPLAINS"
    elif np.sign(Sa[15]) == np.sign(Sp[15]) and abs(Sa[15]) >= 0.3 * abs(Sp[15]): ov = "OVERFLOW-PARTIAL"
    else: ov = "OVERFLOW-NO"
    out["reading"] = {"row": row, "overflow": ov}
print(json.dumps(out, indent=1))
