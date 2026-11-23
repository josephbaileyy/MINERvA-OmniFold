import sys, json, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
d = json.load(open(SC + "/oflow/split.json")); FP, FV, OT = (np.array(d[k]) for k in ("FAKE_PS", "FAKE_VTX", "OTHER"))
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root")
N = cpf.flatten_ours(f.Get("hDataReco2D")); B = cpf.flatten_ours(f.Get("hBkgReco2D"))
cbkg = float(np.max(np.abs(FP + FV + OT - B)[B > 0] / B[B > 0]))
z = np.load(SC + "/priortest/in/signed_data.npz"); M, T, yr = z["response"], z["prior"], z["refined_y"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
fo = R @ np.where(mask, pub / np.where(F > 0, F, 1), ur10)
ipt, ipz = np.divmod(np.arange(224), 16)
def col(j):
    sel = (ipz == j) & (N > 0); gap = float((yr - fo)[sel].sum())
    K = 1 + gap / FP[sel].sum()
    return dict(gap=gap, sum_B=float(B[sel].sum()), frac_FAKE_PS=float(FP[sel].sum() / B[sel].sum()), frac_FAKE_VTX=float(FV[sel].sum() / B[sel].sum()),
                frac_OTHER=float(OT[sel].sum() / B[sel].sum()), FAKE_PS_over_N_pct=100 * float(FP[sel].sum() / N[sel].sum()), K_PS=K,
                per_cell_K=[round(1 + (yr[c] - fo[c]) / FP[c], 2) if FP[c] > 0 else None for c in np.flatnonzero(sel)])
p, s = col(15), col(14)
cls = "EXCLUDED" if p["K_PS"] > 3 else "INTERMEDIATE" if p["K_PS"] > 1.5 else "PLAUSIBLE" if p["K_PS"] > 1 else "WRONG-SIGN"
out = dict(C_SAME=d["C_SAME"], C_BKG_max_rel=cbkg, C_BKG=cbkg <= 1e-6, primary_pz_40_60=p, secondary_pz_20_40=s,
           reading=cls if (d["C_SAME"] and cbkg <= 1e-6) else "STOP",
           scale=("SCALE-CONSISTENT" if abs(s["K_PS"] - p["K_PS"]) <= 0.5 else "SCALE-INCONSISTENT"),
           other_columns_frac_FAKE_PS=[round(float(FP[ipz == j].sum() / max(B[ipz == j].sum(), 1e-30)), 3) for j in range(16)])
print(json.dumps(out, indent=1))
