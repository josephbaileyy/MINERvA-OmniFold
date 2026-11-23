# ibuchi local scorer: C-REPRO, C-KIN/C-ANG (from ana.json), declared readings. Reads the fetched products.
import sys, json, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
P = np.load(SC + "/evloop/fetched/ibuchi_products.npz"); A = json.load(open(SC + "/evloop/fetched/ana.json"))
z = np.load(SC + "/priortest/in/signed_data.npz"); M0, T0 = z["response"], z["prior"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root"); Nref = cpf.flatten_ours(f.Get("hDataReco2D")); Bref = cpf.flatten_ours(f.Get("hBkgReco2D"))
fp = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
Ci = np.linalg.pinv(C[np.ix_(mask, mask)]); Dist = lambda x: float((x - pub)[mask] @ Ci @ (x - pub)[mask]) / 205
mx = lambda a, b: float(np.max(np.abs(a - b)) / np.max(np.abs(b)))
rl = lambda a, b: float(np.max(np.abs(a - b)[b > 0] / b[b > 0]))
T = P["T"]; ctl = {"C-REPRO-M": mx(P["BASE_M"], M0), "C-REPRO-T": mx(T, T0), "C-REPRO-B": rl(P["BASE_B"], Bref), "C-REPRO-N": rl(P["BASE_N"], Nref)}
cnt = {"n_sig": A["n_sig"] == 32849103, "n_bkg": A["n_bkg"] == 658227}
kin = {k: A[k] for k in A if k.startswith("C_KIN") or k.startswith("C_ANG")}
ok = all(x <= 1e-9 for x in ctl.values()) and all(cnt.values()) and all(x <= 1e-9 for x in kin.values())
out = dict(controls=ctl, counts=cnt, kin_ang=kin, controls_pass=ok, ana=A)
if not ok:
    out["reading"] = "STOP"; print(json.dumps(out, indent=1, default=float)); raise SystemExit
tpub = np.where(mask, pub / np.where(F > 0, F, 1), ur10)
def R(M, Tt): return np.divide(M, Tt[None, :], out=np.zeros_like(M), where=Tt[None, :] > 0)
s = float(A["pot_scale"]); NB, BB, MB = P["BASE_N"], P["BASE_B"], P["BASE_M"]
f0 = R(MB, T) @ tpub; e2 = NB + s * (MB @ ((tpub / np.where(T > 0, T, 1))**2)); wgt = np.where(f0 > 0, f0**2 / e2, 0)
ipt, ipz = np.divmod(np.arange(224), 16); use = NB > 0
REG = {"COL": use & (ipz == 15), "ROW": use & (ipt == 0)}
def stats(M, N, B):
    fo = R(M, T) @ tpub; y = N - B; r = np.where(fo > 0, y / np.where(fo > 0, fo, 1) - 1, 0)
    g = np.sum(wgt[use] * r[use]) / np.sum(wgt[use])
    S = {k: float(np.sum(wgt[m] * r[m]) / np.sum(wgt[m]) - g) for k, m in REG.items()}
    S["cols"] = [float(np.sum((wgt * r)[use & (ipz == j)]) / np.sum(wgt[use & (ipz == j)]) - g) for j in range(16)]
    c = np.sum((y * fo / e2)[use]) / np.sum((fo**2 / e2)[use]); S["chi2"] = float(np.sum(((y - c * fo)**2 / e2)[use]))
    return S
def dag(M, N, B, K=10):
    y = N - B; Rm = R(M, T); eff = Rm.sum(0); u = T.copy()
    for _ in range(K):
        fold = Rm @ u; ratio = np.divide(y, fold, out=np.zeros_like(y), where=fold > 0)
        u = np.divide(u * (Rm.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
    return Dist(F * u)
def cls(a, b):
    if abs(b) > 1.3 * abs(a): return "WRONG-WAY"
    if abs(b) <= abs(a) / 3: return "EXPLAINS"
    return "PARTIAL" if 1 - abs(b) / abs(a) >= 0.3 else "NONE"
S0 = stats(MB, NB, BB); res = {"BASE": dict(S=S0, D10=dag(MB, NB, BB), totN=float(NB.sum()), totM=float(MB.sum()))}
for k in ("SEL", "MAD"):
    Sk = stats(P[k + "_M"], P[k + "_N"], P[k + "_B"])
    res[k] = dict(S=Sk, D10=dag(P[k + "_M"], P[k + "_N"], P[k + "_B"]), totN=float(P[k + "_N"].sum()), totM=float(P[k + "_M"].sum()),
                  COL=cls(S0["COL"], Sk["COL"]), ROW=cls(S0["ROW"], Sk["ROW"]))
def scan1(name, H, d):
    chi = np.array([stats(MB, H[i], BB)["chi2"] for i in range(len(d))]); i0 = int(np.argmin(chi))
    inside = d[chi <= chi[i0] + 1]; Sd = stats(MB, H[i0], BB); dh = float(d[i0])
    colmove = max(abs(Sd["cols"][j] - S0["cols"][j]) for j in range(14))
    red = 1 - abs(Sd["COL"]) / abs(S0["COL"])
    best_any = max(1 - abs(stats(MB, H[i], BB)["COL"]) / abs(S0["COL"]) for i in range(len(d)))
    c = ("EXPLAINS" if (abs(dh) <= 0.03 and abs(Sd["COL"]) <= abs(S0["COL"]) / 3 and colmove <= 0.01) else "PARTIAL" if red >= 0.3 else "NONE")
    return dict(d_hat=dh, interval=[float(inside.min()), float(inside.max())], at_edge=bool(i0 in (0, len(d) - 1)), S=Sd, colmove_lt20=colmove,
                COL=c, ROW=cls(S0["ROW"], Sd["ROW"]), D10=dag(MB, H[i0], BB), best_COL_reduction_any_d=best_any)
res["CURV"] = scan1("CURV", P["scanC"], P["scan_d"]); res["RANGE"] = scan1("RANGE", P["scanR"], P["scan_d"])
a = P["scan_a"]; HA = P["scanA"]; chiA = np.array([[stats(MB, HA[i, j], BB)["chi2"] for j in range(len(a))] for i in range(len(a))])
i0, j0 = np.unravel_index(np.argmin(chiA), chiA.shape); SA = stats(MB, HA[i0, j0], BB)
cA = ("EXPLAINS" if (abs(a[i0]) <= 0.002 and abs(a[j0]) <= 0.002 and abs(SA["ROW"]) <= abs(S0["ROW"]) / 3) else "PARTIAL" if 1 - abs(SA["ROW"]) / abs(S0["ROW"]) >= 0.3 else "NONE")
res["ANG"] = dict(dx=float(a[i0]), dy=float(a[j0]), at_edge=bool(i0 in (0, len(a) - 1) or j0 in (0, len(a) - 1)), S=SA, ROW=cA, D10=dag(MB, HA[i0, j0], BB))
colx = [k for k in ("SEL", "MAD", "CURV") if res[k]["COL"] == "EXPLAINS"]; rowx = [k for k in ("ANG", "SEL", "MAD") if res[k]["ROW"] == "EXPLAINS"]
comb = lambda L: ("consistent with " + L[0]) if len(L) == 1 else ("not separable among " + ", ".join(L)) if L else "none of the tested"
out.update(results=res, COL_statement=comb(colx), ROW_statement=comb(rowx), reading="READ")
print(json.dumps(out, indent=1, default=float))
