import sys, json, hashlib, numpy as np
REPO = "/Users/josephbailey/local-research/MINERvA-OmniFold"
sys.path.insert(0, REPO + "/2d-unfolding")
import ROOT
import compare_to_paper_fullcov as cpf
ER = "/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root"
PUB = "/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"
MOD = REPO + "/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"
ctl = {}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
ctl["C-SHA"] = sha(ER).startswith("a5c13fc3") and sha(PUB).startswith("6c6dce72")

f = ROOT.TFile.Open(ER)
def flat_err(h):
    v = np.zeros(cpf.N)
    for ix in range(1, 15):
        for iy in range(1, 17):
            v[(ix-1)*16 + iy-1] = h.GetBinError(ix, iy)
    return v
xs = cpf.flatten_ours(f.Get("hXSec2D")); un = cpf.flatten_ours(f.Get("hUnfold2D"))
tr = cpf.flatten_ours(f.Get("hTruth2D")); tre = flat_err(f.Get("hTruth2D"))
fp = ROOT.TFile.Open(PUB)
pub = cpf.flatten_th2d(fp.Get("pt_pl_cross_section")); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
mask = np.diag(C) > 0
Cr = C[np.ix_(mask, mask)]; Ci = np.linalg.pinv(Cr)
chi = lambda d: float(d[mask] @ Ci @ d[mask])

c_pub = chi(xs - pub); ctl["C-PUB"] = abs(c_pub/465.4152721915331 - 1) <= 1e-6
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50])
PZ = cpf.PZ_EDGES if hasattr(cpf, "PZ_EDGES") else np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
area = np.array([(PT[i+1]-PT[i])*(PZ[j+1]-PZ[j]) for i in range(14) for j in range(16)])
fac = xs/un
k = (fac*area)[mask]; ctl["C-FAC"] = (k.max()-k.min())/k.mean() <= 1e-9
m = tr*fac; sig = tre*fac

txt = {}; mod = np.zeros(cpf.N)
for line in open(MOD):
    if line.lower().startswith("p|"): continue
    pz, pt, s = line.strip().split(","); g = (int(pt)-1)*16 + int(pz)-1
    txt[g] = s; mod[g] = float(s)
fmt_ok = all((float(s) == 0) or (len(s.split("e")[0].replace(".","").lstrip("-")) == 3) for s in txt.values())
ctl["C-FMT"] = fmt_ok
ctl["C-CELLS"] = bool(np.array_equal(mod != 0, mask)) and int(mask.sum()) == 205

def r3(x):
    h = 10.0**(np.floor(np.log10(x)) - 2); return np.round(x/h)*h, h
S = 1 + np.arange(-1000, 1001)*1e-5
mm, ship = m[mask], mod[mask]
def mstar(t):
    x = S[:, None]*t[None, :]; r, h = r3(x)
    return int((np.abs(r - ship[None, :]) < 1e-3*h).sum(1).max())
def mstar_toy(t_ship):   # toy: shipped -> t_ship (rounded), scored against our m
    x = S[:, None]*mm[None, :]; r, h = r3(x)
    return int((np.abs(r - t_ship[None, :]) < 1e-3*h).sum(1).max())

M_obs = mstar(mm)
M1 = int(sum(f"{v:.2e}" == txt[g] or float(f"{v:.2e}") == float(txt[g]) for g, v in zip(np.where(mask)[0], mm)))
X_obs = chi(mod - m)/205
rng = np.random.default_rng(20261123); N = 2000
_, hm = r3(mm)
XA = np.array([float(u @ Ci @ u) for u in rng.uniform(-hm/2, hm/2, (N, mm.size))])/205
def toys(var):
    MB, XB = [], []
    for _ in range(N):
        t = mm + rng.normal(0, np.sqrt(var))
        ts, _h = r3(t); d = ts - mm
        MB.append(mstar_toy(ts)); XB.append(float(d @ Ci @ d)/205)
    return np.array(MB), np.array(XB)
MB1, XB1 = toys(sig[mask]**2); MB2, XB2 = toys(2*sig[mask]**2)
q = lambda a, p: float(np.quantile(a, p))
ctl["C-POW"] = q(MB1, .99) < 205 and q(XA, .99) < q(XB1, .01)

out = dict(controls=ctl, c_pub=c_pub, M_star_obs=M_obs, M_at_s1_string=M1, X_obs=X_obs,
  XA=dict(q01=q(XA,.01), med=q(XA,.5), q99=q(XA,.99)),
  B1=dict(M=dict(q01=q(MB1,.01), med=q(MB1,.5), q99=q(MB1,.99)), X=dict(q01=q(XB1,.01), med=q(XB1,.5), q99=q(XB1,.99))),
  B2=dict(M=dict(q01=q(MB2,.01), med=q(MB2,.5), q99=q(MB2,.99)), X=dict(q01=q(XB2,.01), med=q(XB2,.5), q99=q(XB2,.99))))
if not all(ctl.values()): out["reading"] = "STOP"
elif M_obs > q(MB1,.99) and X_obs <= q(XA,.99): out["reading"] = "SAME-MC"
elif X_obs > q(XB2,.99): out["reading"] = "SYSTEMATIC"
elif q(MB2,.01) <= M_obs <= q(MB1,.99) and q(XB1,.01) <= X_obs <= q(XB2,.99): out["reading"] = "DIFF-MC"
else: out["reading"] = "UNRESOLVED"
# descriptive
rel = (mod - m)/m
out["desc"] = dict(total_ratio_ship_over_ours=float((mod*area)[mask].sum()/(m*area)[mask].sum()),
  mc_rel_err_median=float(np.median((sig/m)[mask])), rel_resid_median_abs=float(np.median(np.abs(rel[mask]))),
  rel_resid_rms=float(np.sqrt(np.mean(rel[mask]**2))), pull_mcstat_rms=float(np.sqrt(np.mean(((mod-m)/sig)[mask]**2))),
  X_diag_only=float(np.sum(((mod-m)[mask])**2/np.diag(Cr)))/205)
np.savez("/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad/truthtest/vectors.npz",
  m=m, sig=sig, mod=mod, mask=mask, area=area)
print(json.dumps(out, indent=1, default=lambda o: o.item()))
