import sys, json, numpy as np
from scipy.optimize import minimize_scalar, brentq
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
Ld = lambda k: np.load(f"{SC}/lattest/lat/{k}.npz")
C0, Cm, Cp = Ld("CV"), Ld("Muon_Energy_MINOS_0"), Ld("Muon_Energy_MINOS_1")
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root"); N = cpf.flatten_ours(f.Get("hDataReco2D"))
tpub = np.where(mask, pub / np.where(F > 0, F, 1), ur10)
q = lambda key, s: C0[key] + s * (Cp[key] - Cm[key]) / 2 + s**2 * (Cp[key] + Cm[key] - 2 * C0[key]) / 2
def R(M, T): return np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
s0 = float(C0["pot_scale"]); T0 = C0["T"]
e2 = N + s0 * (C0["M"] @ ((tpub / np.where(T0 > 0, T0, 1))**2))
ipt, ipz = np.divmod(np.arange(224), 16); use = N > 0
lo, hi = use & (ipz <= 13), use & (ipz >= 14)
def chi(sig, sel, ret=False):
    fo = R(q("M", sig), q("T", sig)) @ tpub; y = N - q("B", sig)
    c = np.sum((y * fo / e2)[sel]) / np.sum((fo**2 / e2)[sel])          # best global c
    x2 = float(np.sum(((y - c * fo)**2 / e2)[sel]))
    return (x2, c, fo, y) if ret else x2
def fit(sel):
    g = np.linspace(-4, 4, 161); vals = [chi(s, sel) for s in g]; s0_ = g[int(np.argmin(vals))]
    r = minimize_scalar(lambda s: chi(s, sel), bounds=(max(-4, s0_ - 0.1), min(4, s0_ + 0.1)), method="bounded")
    sh, xm = float(r.x), float(r.fun)
    def edge(d):
        try: return brentq(lambda s: chi(s, sel) - xm - 1, sh, sh + d * 4)
        except ValueError: return None
    a, b = edge(-1), edge(+1)
    return dict(sigma=sh, chi2_min=xm, chi2_at0=chi(0.0, sel), n=int(sel.sum()), lo_edge=a, hi_edge=b)
Flo, Fhi, Fall = fit(lo), fit(hi), fit(use)
sl, sh = Flo["sigma"], Fhi["sigma"]
reading = ("CONSISTENT-SCALE" if sl >= 1 and sh >= 1 and abs(sl - sh) <= 1 else
           "TOP-ONLY" if sh >= 1 and abs(sl) < 0.5 else "OTHER")
x2, c, fo, y = chi(Fall["sigma"], use, ret=True); r = np.where(fo > 0, y / (c * np.where(fo > 0, fo, 1)) - 1, 0)
wgt = np.where(fo > 0, fo**2 / e2, 0); g = np.sum(wgt[use] * r[use]) / np.sum(wgt[use])
cols = [round(100 * (np.sum((wgt * r)[use & (ipz == j)]) / np.sum(wgt[use & (ipz == j)]) - g), 2) for j in range(16)]
x0, c0, fo0, y0 = chi(0.0, use, ret=True); r0 = np.where(fo0 > 0, y0 / (c0 * np.where(fo0 > 0, fo0, 1)) - 1, 0)
g0 = np.sum(wgt[use] * r0[use]) / np.sum(wgt[use])
cols0 = [round(100 * (np.sum((wgt * r0)[use & (ipz == j)]) / np.sum(wgt[use & (ipz == j)]) - g0), 2) for j in range(16)]
print(json.dumps(dict(fit_lo=Flo, fit_hi=Fhi, fit_all=Fall, reading=reading, col_S_pct_at_sigma0=cols0, col_S_pct_at_sigma_all=cols), indent=1))
