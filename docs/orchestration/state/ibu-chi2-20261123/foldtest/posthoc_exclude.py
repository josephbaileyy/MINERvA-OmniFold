# POST HOC, not declared: how much of the IBU K=10 distance sits in the two flagged regions?
import sys, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
fp = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
d = F * ur10 - pub; ipt, ipz = np.divmod(np.arange(224), 16)
for name, keep in [("all 205", mask), ("drop pT row 0", mask & (ipt != 0)), ("drop p|| 40-60", mask & (ipz != 15)),
                   ("drop both", mask & (ipt != 0) & (ipz != 15)), ("drop pT rows 0-1 and p|| 20-60", mask & (ipt > 1) & (ipz < 14))]:
    idx = np.flatnonzero(keep); x = d[idx]; chi = float(x @ np.linalg.pinv(C[np.ix_(idx, idx)]) @ x)
    print(f"{name:32s} n={idx.size:3d}  chi2={chi:7.2f}  chi2/n={chi/idx.size:.3f}")
