import numpy as np, ROOT, os
ROOT.gROOT.SetBatch(True)
UQ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
def sq(p, n):
    f = ROOT.TFile.Open(p); h = f.Get(n)
    if not h: return None
    k = h.GetNbinsX(); a = np.array([[h.GetBinContent(i+1, j+1) for j in range(k)] for i in range(k)]); f.Close(); return a
fx = f"{UQ}/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root"
U = sq(fx, "hCov_universe_total"); N = sq(fx, "hCov_universe___Normalization_flat")
print("fluxfix adopted sqrt tr (no norm) =", np.sqrt(np.trace(U - N)))
pre = f"{UQ}/universe_stage2_MEFHC_full_matcorr/uq_universe_covariance_full_matcorr.root"
if os.path.exists(pre):
    P = sq(pre, "hCov_universe_total"); PN = sq(pre, "hCov_universe___Normalization_flat")
    print("pre-fluxfix matcorr sqrt tr =", np.sqrt(np.trace(P)), "norm present:", PN is not None)
    import hashlib; print("sha", hashlib.sha256(open(pre,'rb').read()).hexdigest())
