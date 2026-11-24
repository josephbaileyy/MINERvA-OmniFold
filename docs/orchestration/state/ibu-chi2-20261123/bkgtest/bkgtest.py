import sys, json, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
z = np.load(SC + "/priortest/in/signed_data.npz"); M, T, yr = z["response"], z["prior"], z["refined_y"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root")
N = cpf.flatten_ours(f.Get("hDataReco2D")); B = cpf.flatten_ours(f.Get("hBkgReco2D"))
R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
fo = R @ np.where(mask, pub / np.where(F > 0, F, 1), ur10)
ipt, ipz = np.divmod(np.arange(224), 16)
def block(sel):
    sel = sel & (N > 0)
    K = 1 + (yr - fo)[sel].sum() / B[sel].sum()
    cls = "WRONG-SIGN" if K < 1 else "PLAUSIBLE" if K <= 1.5 else "INTERMEDIATE" if K <= 3 else "EXCLUDED"
    return dict(cells=int(sel.sum()), sum_N=float(N[sel].sum()), sum_B=float(B[sel].sum()), B_over_N_pct=100 * float(B[sel].sum() / N[sel].sum()),
                gap_y_minus_f=float((yr - fo)[sel].sum()), gap_over_B=float((yr - fo)[sel].sum() / B[sel].sum()), K=float(K), reading=cls,
                C_Y_refined_over_NminusB=float(yr[sel].sum() / (N - B)[sel].sum()),
                per_cell=[dict(ipt=int(i), ipz=int(j), B_over_N_pct=round(100 * B[c] / N[c], 2), K=round(1 + (yr[c] - fo[c]) / B[c], 2) if B[c] > 0 else None)
                          for c, i, j in zip(np.flatnonzero(sel), ipt[sel], ipz[sel])])
print(json.dumps(dict(primary_pz_40_60=block(ipz == 15), secondary_pt_0_007=block(ipt == 0)), indent=1))
