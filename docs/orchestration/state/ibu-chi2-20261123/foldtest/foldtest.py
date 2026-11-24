import sys, json, numpy as np
REPO = "/Users/josephbailey/local-research/MINERvA-OmniFold"; sys.path.insert(0, REPO + "/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
z = np.load(SC + "/priortest/in/signed_data.npz"); M, T, yr, ys = z["response"], z["prior"], z["refined_y"], z["signed_y"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root")
N = cpf.flatten_ours(f.Get("hDataReco2D")); B = cpf.flatten_ours(f.Get("hBkgReco2D"))
ctl = {"C-Y": float(np.max(np.abs((N - B) - ys) / np.maximum(np.abs(ys), 1))) <= 1e-9}
s = 0.212405
R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50])
PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
ipt, ipz = np.divmod(np.arange(224), 16)
L = np.log(0.5 * (PZ[ipz] + PZ[ipz + 1]))
t20 = np.tan(np.radians(20))
inside = PT[ipt + 1] / PZ[ipz] <= t20; beyond = PT[ipt] / PZ[ipz + 1] >= t20; crossed = ~inside & ~beyond
use = N > 0
def wmean(r, sg, sel): w = 1 / sg[sel]**2; m = np.sum(w * r[sel]) / w.sum(); return m, 1 / np.sqrt(w.sum())
def stats(y, t):
    fo = R @ t; ed2 = N; em2 = s * ((t / np.where(T > 0, T, 1))**2 @ M.T) * 0 + s * (M @ ((t / np.where(T > 0, T, 1))**2))
    e2 = ed2 + em2; u = use & (fo > 0)
    r = y / np.where(fo > 0, fo, 1) - 1; sg = np.sqrt(e2) / np.where(fo > 0, fo, 1)
    n = int(u.sum())
    Gd = float(np.sum((y - fo)[u]**2 / ed2[u])) / n; Gc = float(np.sum((y - fo)[u]**2 / e2[u])) / n
    w = 1 / sg[u]**2; X = np.vstack([np.ones(n), L[u]]).T
    cov = np.linalg.inv(X.T @ (w[:, None] * X)); beta = cov @ (X.T @ (w * r[u]))
    zP = beta[1] / np.sqrt(cov[1, 1])
    me, se = wmean(r, sg, u & crossed); mi, si = wmean(r, sg, u & inside); zE = (me - mi) / np.hypot(se, si)
    lo = u & (ipt <= 1); hi = u & (ipt > 1); ml, sl = wmean(r, sg, lo); mh, sh = wmean(r, sg, hi); zL = (ml - mh) / np.hypot(sl, sh)
    rows = [round(100 * wmean(r, sg, u & (ipt == i))[0], 2) for i in range(14)]
    cols = [round(100 * wmean(r, sg, u & (ipz == j))[0], 2) if np.any(u & (ipz == j)) else None for j in range(16)]
    return dict(n=n, G_data=Gd, G_comb=Gc, norm=float(y[u].sum() / fo[u].sum()), Ppar=dict(slope_pct_per_ln=100 * beta[1], z=zP),
                EDGE=dict(diff_pct=100 * (me - mi), z=zE, n=int((u & crossed).sum())), LOWPT=dict(diff_pct=100 * (ml - mh), z=zL),
                row_mean_r_pct=rows, col_mean_r_pct=cols, median_mc_over_data_err=float(np.median(np.sqrt(em2[u] / ed2[u])))), fo
tpub = np.where(mask, pub / np.where(F > 0, F, 1), ur10); tpubT = np.where(mask, pub / np.where(F > 0, F, 1), T)
P, fo = stats(yr, tpub)
tilt = 1 + 0.02 * (L - L.min()) / (L.max() - L.min())
Pt, _ = stats(fo * tilt, tpub); ctl["C-POW"] = abs(Pt["Ppar"]["z"]) > 3
def reading(P):
    flags = [k for k in ("Ppar", "EDGE", "LOWPT") if abs(P[k]["z"]) > 3]
    return ("PATTERNED: " + ",".join(flags)) if flags else ("CONSISTENT" if P["G_comb"] <= 1.5 else "MISFIT")
out = dict(controls=ctl, power_tilt_z=Pt["Ppar"]["z"], fully_beyond_theta_cells_excluded_from_EDGE=int((use & beyond).sum()),
  primary_refined=P, reading=reading(P) if all(ctl.values()) else "STOP",
  secondary_signed=dict(reading=reading(stats(ys, tpub)[0]), **{k: stats(ys, tpub)[0][k] for k in ("G_data","G_comb","norm","Ppar","EDGE","LOWPT")}),
  secondary_unreported_from_T=dict(reading=reading(stats(yr, tpubT)[0]), G_comb=stats(yr, tpubT)[0]["G_comb"]),
  own_fold_refined_ur10={k: stats(yr, ur10)[0][k] for k in ("G_data","G_comb","norm","Ppar","EDGE","LOWPT","row_mean_r_pct","col_mean_r_pct")})
print(json.dumps(out, indent=1, default=lambda o: o.item()))
