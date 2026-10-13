"""Reviewer's independent reproduction (does not import the owner's code)."""
import sys, json, numpy as np, uproot
IN = sys.argv[1]
SH = (14, 16, 7, 7, 6)
def load(fn):
    z = np.load(f"{IN}/{fn}", allow_pickle=False)
    e = [np.asarray(z["edges_" + k], float) for k in ("pt", "pz", "eavail", "q3", "W")]
    dv = np.ones(SH)
    for i, ed in enumerate(e):
        s = [1] * 5; s[i] = -1
        dv = dv * np.diff(ed).reshape(s)
    return np.asarray(z["xsec_flat"], float).reshape(SH) * dv, e, dv
P = {}
for k, fn in [("TuneV1", "mnvtune_v1_xsec5d.npz"), ("GENIE_CV", "genie_cv_xsec5d_full.npz"),
              ("GENIE_MEC", "genie_mec_xsec5d_full.npz"), ("NuWro", "nuwro_cv_xsec5d_full.npz"),
              ("GiBUU", "gibuu_cv_xsec5d_fluxfix.npz")]:
    P[k], E, dv = load(fn)
    if k != "TuneV1":
        pass
print("edges:", [list(np.round(x, 3)) for x in E[2:]])
print("pt", list(E[0])); print("pz", list(E[1]))
f = uproot.open(f"{IN}/xsec_5d_MEFHC_5iter_lgbm.root")
D = np.asarray(f["hXSecND_flat"].values(), float).reshape(SH) * dv
eA, eW = E[2], E[4]
Alo = eA[:-1][None, None, :, None, None]; Wlo = eW[:-1][None, None, None, None, :]
Ahi = eA[1:][None, None, :, None, None]; Whi = eW[1:][None, None, None, None, :]
C = np.broadcast_to((Alo >= 0.8 - 1e-9) & (Wlo >= 1.8 - 1e-9), SH)
M = np.broadcast_to((Wlo >= 1.4 - 1e-9) & (Whi <= 1.8 + 1e-9) & (Alo > -1), SH)
OV = np.broadcast_to((Alo >= 3 - 1e-9) | (Wlo >= 3 - 1e-9), SH)
print("data total", D.sum(), "corner", D[C].sum(), "C frac", D[C].sum() / D.sum())
out = {}
for k, X in P.items():
    Rt = D.sum() / X.sum(); RC = D[C].sum() / X[C].sum(); RM = D[M].sum() / X[M].sum()
    Rn = D[C & ~OV].sum() / X[C & ~OV].sum(); Ro = D[C & OV].sum() / X[C & OV].sum()
    out[k] = dict(Rt=Rt, RC=RC, rhoC=RC / Rt, RM=RM, rhoM=RM / Rt, RC_noovf=Rn, RC_ovf=Ro,
                  rhoC_noovf=Rn / Rt, rhoC_ovf=Ro / Rt, ovf_share_C=X[C & OV].sum() / X[C].sum(),
                  dshape_C=(D[C].sum() - X[C].sum() * Rt) * 1e40, dshape_Cov=(D[C & OV].sum() - X[C & OV].sum() * Rt) * 1e40,
                  dshape_M=(D[M].sum() - X[M].sum() * Rt) * 1e40, fC=X[C].sum() / X.sum())
    print(k, {a: round(b, 4) for a, b in out[k].items()})
# S20 with my own bound: E_nu <= E_mu_max + omega_max, omega from (M+w)^2 <= W^2+q3^2+m^2
mmu, Mn = 0.1056584, 0.939565
pth, pzh, q3h, Wh = E[0][1:], E[1][1:], E[3][1:], E[4][1:]
Emu = np.sqrt(pth[:, None] ** 2 + pzh[None, :] ** 2 + mmu ** 2)
om = np.sqrt(q3h[:, None] ** 2 + Wh[None, :] ** 2 + mmu ** 2) - Mn
B = Emu[:, :, None, None, None] + om[None, None, None, :, :] + 0 * D
S = B < 20
print("S20 cells", S.sum(), "data frac total/C/M", D[S].sum() / D.sum(), D[S & C].sum() / D[C].sum(), D[S & M].sum() / D[M].sum())
# with the proton mass instead (struck-proton W definition) -> sensitivity
omp = np.sqrt(q3h[:, None] ** 2 + Wh[None, :] ** 2 + mmu ** 2) - 0.938272
Sp = (Emu[:, :, None, None, None] + omp[None, None, None, :, :] + 0 * D) < 20
print("S20 with M_p: cells", Sp.sum(), "changed", (Sp != S).sum())
for k, X in P.items():
    Rt = D[S].sum() / X[S].sum(); RC = D[S & C].sum() / X[S & C].sum(); RM = D[S & M].sum() / X[S & M].sum()
    print(" S20", k, "Rt %.4f rhoC %.4f lnrhoM %.4f" % (Rt, RC / Rt, np.log(RM / Rt)))
json.dump(out, open(sys.argv[2], "w"), indent=1)
