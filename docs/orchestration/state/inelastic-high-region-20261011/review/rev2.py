"""Reviewer's independent decomposition, recoil shifts, emulation contrasts."""
import sys, json, numpy as np, uproot
IN = sys.argv[1]
SH = (14, 16, 7, 7, 6)
def load(fn):
    z = np.load(f"{IN}/{fn}", allow_pickle=False)
    e = [np.asarray(z["edges_" + k], float) for k in ("pt", "pz", "eavail", "q3", "W")]
    dv = np.einsum("a,b,c,d,e->abcde", *[np.diff(x) for x in e])
    return np.asarray(z["xsec_flat"], float).reshape(SH) * dv, e, dv
P = {}
for k, fn in [("TuneV1", "mnvtune_v1_xsec5d.npz"), ("GENIE_CV", "genie_cv_xsec5d_full.npz"),
              ("GENIE_MEC", "genie_mec_xsec5d_full.npz"), ("NuWro", "nuwro_cv_xsec5d_full.npz")]:
    P[k], E, dv = load(fn)
D = np.asarray(uproot.open(f"{IN}/xsec_5d_MEFHC_5iter_lgbm.root")["hXSecND_flat"].values(), float).reshape(SH) * dv
def Rv(fn):
    return np.asarray(np.load(f"{IN}/{fn}")["xsec_flat"], float).reshape(SH) * dv
RZ, RM4, RP4 = Rv("w2b/w2b_rrzero_b-_j-.npz"), Rv("w2b/w2b_rr0_b-_j-.npz"), Rv("w2b/w2b_rr1_b-_j-.npz")
RC0 = Rv("s5pdata/data_b-_j-.npz"); RJ = [Rv(f"s5pdata/data_b-_j{i}.npz") for i in (1, 2, 3)]
ew = np.zeros((7, 6), bool)
def mask(sel):  # sel over (A,W)
    return np.broadcast_to(sel[None, None, :, None, :], SH)
A_lo = E[2][:-1]; W_lo = E[4][:-1]
Cm = mask((A_lo[:, None] >= 0.8) & (W_lo[None, :] >= 1.8))
Mm = mask(np.ones((7, 1), bool) & ((W_lo >= 1.4) & (W_lo < 1.8))[None, :])
OV = mask((A_lo[:, None] >= 3) | (W_lo[None, :] >= 3))
# my implementation: move axes to (m=pt,pz ; a ; t=q3,W) explicitly with safe division, no fallback first
def safe(n, d):
    return np.divide(n, d, out=np.zeros_like(n), where=d > 0)
def steps(Dt, Pt, reg):
    k = Dt.sum() / Pt.sum()
    Pm = Pt.sum(axis=(2, 3, 4), keepdims=True); Dm = Dt.sum(axis=(2, 3, 4), keepdims=True)
    Pmt = Pt.sum(axis=2, keepdims=True); Dmt = Dt.sum(axis=2, keepdims=True)
    Pt_m = safe(Pmt, Pm); Pa_mt = safe(Pt, Pmt); Da_mt = safe(Dt, Dmt)
    seqI = [Pt * k, Dm * Pt_m * Pa_mt, Dmt * Pa_mt, Dt]
    seqP = [Pt * k, k * Pmt * Da_mt, Dm * Pt_m * Da_mt, Dt]
    sI = [x[reg].sum() for x in seqI]; sP = [x[reg].sum() for x in seqP]
    lI = np.diff(np.log(sI)); lP = np.diff(np.log(sP))
    lost = {"D_in_P_empty_m": float(Dm[Pm == 0].sum() / Dt.sum()), "D_in_P_empty_mt": float(Dmt[Pmt == 0].sum() / Dt.sum())}
    return {"incl_first(mu,t|mu,a|t)": np.round(lI, 4).tolist(), "part_first(a|t,mu,t|mu)": np.round(lP, 4).tolist(),
            "ln_rho": round(float(np.log(Dt[reg].sum() / Pt[reg].sum()) - np.log(k)), 4), "lost": lost}
out = {}
for k in P:
    for rn, reg in (("C", Cm), ("M", Mm), ("C_noovf", Cm & ~OV), ("C_ovf", Cm & OV)):
        out[f"{k}/{rn}"] = steps(D, P[k], reg)
        print(k, rn, out[f"{k}/{rn}"])
# partition-step dynamic range in C: P_pred(A>=0.8 | W>=1.8)
hiW = mask(np.ones((7, 1), bool) & (W_lo >= 1.8)[None, :])
for k in P:
    print("P(A>=0.8|W>=1.8)", k, round(P[k][Cm].sum() / P[k][hiW].sum(), 4), "max partition step ~", round(-np.log(P[k][Cm].sum() / P[k][hiW].sum()), 4))
# recoil shifts on ln rho_C (prediction independent), and steps
def lnrho(Dt, reg, Pt):
    return np.log(Dt[reg].sum() / Pt[reg].sum()) - np.log(Dt.sum() / Pt.sum())
G = P["GENIE_CV"]
for rn, reg in (("C", Cm), ("M", Mm)):
    z = lnrho(RZ, reg, G)
    print("recoil", rn, "dlnrho -4%", round(lnrho(RM4, reg, G) - z, 4), "+4%", round(lnrho(RP4, reg, G) - z, 4),
          "Rcentral-vs-prod", round(lnrho(RC0, reg, G) - lnrho(D, reg, G), 4), "rrzero-vs-Rcentral", round(z - lnrho(RC0, reg, G), 4),
          "jitters", [round(lnrho(j, reg, G) - lnrho(RC0, reg, G), 4) for j in RJ])
for k in ("GENIE_CV", "GENIE_MEC", "NuWro"):
    r = [np.exp(lnrho(x, Cm, P[k])) for x in (RZ, RM4, RP4)]
    print("linear rho_C shift", k, "d0 %.4f  -4%% %+.4f  +4%% %+.4f" % (r[0], r[1] - r[0], r[2] - r[0]))
    sZ = steps(RZ, P[k], Cm)["incl_first(mu,t|mu,a|t)"]; sM = steps(RM4, P[k], Cm)["incl_first(mu,t|mu,a|t)"]; sP = steps(RP4, P[k], Cm)["incl_first(mu,t|mu,a|t)"]
    print("  step shifts (mu, t|mu, a|t) -4%:", np.round(np.subtract(sM, sZ), 4), "+4%:", np.round(np.subtract(sP, sZ), 4))
# per-W ln rho and recoil shifts, GENIE CV
for j in range(6):
    reg = mask(np.ones((7, 1), bool) & (np.arange(6) == j)[None, :])
    print("W%d" % j, "frac %.3f" % (D[reg].sum() / D.sum()), "lnrho G %.3f T %.3f N %.3f" % tuple(lnrho(D, reg, P[x]) for x in ("GENIE_CV", "TuneV1", "NuWro")),
          "recoil %+.3f/%+.3f" % (lnrho(RM4, reg, G) - lnrho(RZ, reg, G), lnrho(RP4, reg, G) - lnrho(RZ, reg, G)))
# emulation
z = np.load(f"{IN}/r5b_tune_emulation.npz")
nom = np.asarray(z["nominal_cell_sigma"], float).reshape(SH); emu = np.asarray(z["emulated_cell_sigma"], float).reshape(SH)
print("emu nominal vs product maxrel", np.max(np.abs(nom[G > 0] / G[G > 0] - 1)), "nom where G==0:", nom[G == 0].sum())
print("emu total x", emu.sum() / nom.sum(), "Rtot", D.sum() / nom.sum(), D.sum() / emu.sum())
regs = {"C": Cm, "M": Mm}
for j in range(6):
    regs["W%d" % j] = mask(np.ones((7, 1), bool) & (np.arange(6) == j)[None, :])
for rn, reg in regs.items():
    print("emu", rn, "pred x %.4f" % (emu[reg].sum() / nom[reg].sum()), "lnrho %.4f -> %.4f" % (lnrho(D, reg, nom), lnrho(D, reg, emu)))
json.dump(out, open(sys.argv[2], "w"), indent=1, default=str)
