import sys, json, csv, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
ST = "/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state"
w = np.load(ST + "/ibu-chi2-20261123/wstest/wsplit_a1.npz"); A, M4 = w["A"], w["M4"]
z = np.load(SC + "/priortest/in/signed_data.npz"); M0, T0 = z["response"], z["prior"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
area = np.load(ST + "/ibu-chi2-20261123/truthtest/vectors.npz")["area"]
f = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root")
N = cpf.flatten_ours(f.Get("hDataReco2D")); B0 = cpf.flatten_ours(f.Get("hBkgReco2D"))
fp = ROOT.TFile.Open("/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
Ci = np.linalg.pinv(C[np.ix_(mask, mask)]); D = lambda x: float((x - pub)[mask] @ Ci @ (x - pub)[mask]) / 205
mx = lambda a, b: float(np.max(np.abs(a - b)) / np.max(np.abs(b)))
ctl = {"C-CV-T": mx(A.sum(1), T0), "C-CV-M": mx(M4.sum(2), M0)}
# flux ratio per gen5d band
g = json.load(open(ST + "/s5p/gen5d/gen5d-fluxfix.json"))
def find(o, key):
    if isinstance(o, dict):
        if key in o: return o
        for x in o.values():
            r = find(x, key)
            if r: return r
    elif isinstance(o, list):
        for x in o:
            r = find(x, key)
            if r: return r
blk = find(g, "shape_ratio_bands"); Phi = blk["Phi_t_0_100_m2_per_POT"]
mat = {(b["E_lo"], b["E_hi"]): b["frac_phi_t"] * Phi for b in blk["shape_ratio_bands"]}
V = np.array([[float(x) for x in r] for r in list(csv.reader(open(SC + "/dl-flux/MINERvA_Flux_pdg14_500MeVBins.csv")))[1:]])
vint = lambda a, b: float((V[:, 2] * (V[:, 1] - V[:, 0]))[(V[:, 0] >= a - 1e-9) & (V[:, 1] <= b + 1e-9)].sum())
ctl["C-PHI"] = abs(Phi / vint(0, 100) - 0.9959) <= 1e-3
band = lambda a, b: vint(a, b) / sum(m for (lo, hi), m in mat.items() if lo >= a - 1e-9 and hi <= b + 1e-9)
EE = [0, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 30, 50, 80, np.inf]
bands = [(0.5, 2), (2, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 50), (50, 100)]
r = []
for lo, hi in zip(EE[:-1], EE[1:]):
    if lo == 0: r.append(band(0, 5)); continue
    if lo >= 80: r.append(band(50, 100)); continue
    c = 0.5 * (lo + hi); a, b = next(bb for bb in bands if bb[0] <= c < bb[1]); r.append(band(a, b))
r = np.array(r); wab = np.concatenate([np.repeat(r, 10), [1.0]])
Tp, Mp = A @ wab, M4 @ wab
ship = np.zeros(224)
for line in open("/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"):
    if line.lower().startswith("p|"): continue
    pz, pt, s = line.strip().split(","); ship[(int(pt)-1)*16 + int(pz)-1] = float(s)
ipt, ipz = np.divmod(np.arange(224), 16)
def shape(m, reg):
    return float(((ship*area)[reg].sum() / (m*area)[reg].sum()) / ((ship*area)[mask].sum() / (m*area)[mask].sum()) - 1)
truth = {}
for k, reg in {"COL40": mask & (ipz == 15), "COL20": mask & (ipz == 14), "ROW0": mask & (ipt == 0)}.items():
    sb, sa = shape(T0 * F, reg), shape(Tp * F, reg); truth[k] = dict(s_before=sb, s_after=sa, kappa=(sb - sa) / sb)
cls = lambda k: "FLUX-MAJOR" if k >= .5 else "FLUX-PARTIAL" if k >= .2 else "FLUX-MINOR"
tpub = np.where(mask, pub / np.where(F > 0, F, 1), ur10)
def R(M, T): return np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
s0 = 0.21240500334472884
f0 = R(M0, T0) @ tpub; e2 = N + s0 * (M0 @ ((tpub / np.where(T0 > 0, T0, 1))**2)); wgt = np.where(f0 > 0, f0**2 / e2, 0)
use = N > 0; REG = {"COL": use & (ipz == 15), "ROW": use & (ipt == 0)}; y = N - B0
def S(fo):
    rr = np.where(fo > 0, y / np.where(fo > 0, fo, 1) - 1, 0); gg = np.sum(wgt[use] * rr[use]) / np.sum(wgt[use])
    return {k: float(np.sum(wgt[m] * rr[m]) / np.sum(wgt[m]) - gg) for k, m in REG.items()}
def dag(M, T, yy, K=10):
    Rm = R(M, T); eff = Rm.sum(0); u = T.copy()
    for _ in range(K):
        fold = Rm @ u; ratio = np.divide(yy, fold, out=np.zeros_like(yy), where=fold > 0)
        u = np.divide(u * (Rm.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
    return u
ok = ctl["C-CV-T"] <= 1e-9 and ctl["C-CV-M"] <= 1e-9 and ctl["C-PHI"]
out = dict(controls=ctl, controls_pass=ok, r_per_Enu_bin=dict(zip([f"{a}-{b}" for a, b in zip(EE[:-1], EE[1:])], r.tolist())),
           truth=truth, S_before=S(f0), S_after=S(R(Mp, Tp) @ tpub),
           D10_before=D(F * dag(M0, T0, y)), D10_after=D(F * dag(Mp, Tp, y)),
           reading=("STOP" if not ok else {k: cls(truth[k]["kappa"]) for k in ("COL40", "ROW0")}))
print(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
