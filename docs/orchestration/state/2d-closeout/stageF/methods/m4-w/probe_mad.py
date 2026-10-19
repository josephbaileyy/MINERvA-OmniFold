"""Q1/Q2 decomposition on a MasterAnaDev truth tuple (has mc_incomingPartVec, mc_targetNucleon).

Truth theta as MAT GetThetalepTrue: p3lep.RotateX(numi_beam_angle_rad=-0.05887).Theta().
Measures: angle between the true neutrino direction and that fixed axis; truth-W residual
W_true - W_pred(pT,p||,q3) with per-event M and with M_bar; and the same with theta measured
from the true neutrino direction (control: should be ~0 apart from M)."""
import json, sys
import numpy as np
import ROOT
sys.path.insert(0, sys.argv[2])
import common as C

ROOT.gErrorIgnoreLevel = ROOT.kError
fn = sys.argv[1]
out = sys.argv[3]
A = -0.05887
df = ROOT.RDataFrame("Truth", fn)
defs = {"kx": "mc_incomingPartVec[0]", "ky": "mc_incomingPartVec[1]", "kz": "mc_incomingPartVec[2]",
        "kE": "mc_incomingPartVec[3]", "lx": "mc_primFSLepton[0]", "ly": "mc_primFSLepton[1]",
        "lz": "mc_primFSLepton[2]", "lE": "mc_primFSLepton[3]", "vx": "mc_vtx[0]", "vy": "mc_vtx[1]",
        "vz": "mc_vtx[2]"}
for k, v in defs.items():
    df = df.Define(k, v)
cols = list(defs) + ["mc_Q2", "mc_incomingE", "mc_targetNucleon", "mc_current", "mc_incoming", "mc_intType"]
d = df.Filter("mc_current==1 && mc_incoming==14").AsNumpy(cols)
d = {k: np.asarray(v, float) for k, v in d.items()}
n_cc = d["kx"].size

def rotx(x, y, z, a):
    return x, y * np.cos(a) - z * np.sin(a), y * np.sin(a) + z * np.cos(a)

lx, ly, lz = rotx(d["lx"], d["ly"], d["lz"], A)
p = np.sqrt(lx ** 2 + ly ** 2 + lz ** 2)
th_b = np.arccos(np.clip(lz / p, -1, 1))
pt_b, pz_b = p * np.sin(th_b), p * np.cos(th_b)
kx, ky, kz = rotx(d["kx"], d["ky"], d["kz"], A)
kmag = np.sqrt(kx ** 2 + ky ** 2 + kz ** 2)
alpha = np.arccos(np.clip(kz / kmag, -1, 1))           # nu direction vs MAT theta axis
kx0, ky0, kz0 = d["kx"], d["ky"], d["kz"]
alpha_det = np.arccos(np.clip(kz0 / kmag, -1, 1))      # nu direction vs detector z
# muon angle wrt the TRUE neutrino direction
cos_nu = (d["lx"] * kx0 + d["ly"] * ky0 + d["lz"] * kz0) / (p * kmag)
th_nu = np.arccos(np.clip(cos_nu, -1, 1))
pt_nu, pz_nu = p * np.sin(th_nu), p * np.cos(th_nu)

# signal: fiducial truth vertex + muon phase space (beam-axis theta, as the analysis)
# MAT-MINERvA utilities/TargetUtils.cxx:34-46 IsInHexagon, transcribed
ls = 850. * 2 / np.sqrt(3); sl = (ls / 2) / 850.
xp, yp = np.abs(d["vx"]), np.abs(d["vy"])
hexok = (xp ** 2 + yp ** 2 < 850. ** 2) | ((xp <= 850.) & (yp * yp < ls / 2)) | ((xp <= 850.) & (yp < ls - xp * sl))
fid = (d["vz"] > 5980) & (d["vz"] < 8422) & hexok
ps = (pt_b >= 0) & (pt_b <= 4500) & (pz_b >= 1500) & (pz_b <= 60000) & (np.arctan2(pt_b, pz_b) < np.deg2rad(20))
sig = fid & ps

enu, emu = d["mc_incomingE"], d["lE"]
q0 = enu - emu
q3 = np.sqrt(d["mc_Q2"] + q0 ** 2)
M = C.struck_mass(d["mc_targetNucleon"])
W_true = C.w_cvu(M, enu, emu, th_b)                    # CVUniverse truth W (beam-axis theta)
mmu_gen = np.sqrt(np.maximum(emu ** 2 - p ** 2, 0))
res = {"file": fn, "n_cc_numu": int(n_cc), "n_signal": int(sig.sum()),
       "lepton_mass_from_tuple_MeV": C.summarize(mmu_gen[sig]),
       "Enu_branch_vs_vecE_maxabs": float(np.max(np.abs(enu - d["kE"]))),
       "alpha_nu_vs_MAT_axis_mrad": C.summarize(1e3 * alpha[sig]),
       "alpha_nu_vs_detector_z_mrad": C.summarize(1e3 * alpha_det[sig]),
       "W_true_nan_frac": float(np.isnan(W_true[sig]).mean())}
s = sig
for lab, Muse in (("M_struck", M), ("M_bar", np.full_like(M, C.M_BAR))):
    Wp, disc, enu_p = C.w_pred(pt_b, pz_b, q3, Muse, mmu=mmu_gen)
    r = W_true - Wp
    res[f"resid_beamaxis_{lab}"] = C.summarize(r[s])
    res[f"resid_beamaxis_{lab}_disc_neg"] = int((disc[s] < 0).sum())
    res[f"enu_pred_minus_true_{lab}"] = C.summarize((enu_p - enu)[s])
    ok = s & np.isfinite(W_true) & np.isfinite(Wp)
    res[f"fine_bin_change_frac_{lab}"] = float((C.wbin(W_true[ok], C.W_FINE) != C.wbin(Wp[ok], C.W_FINE)).mean())
    res[f"J_bin_change_frac_{lab}"] = float((C.wbin(W_true[ok], C.W_J) != C.wbin(Wp[ok], C.W_J)).mean())
# control: theta from the true nu direction everywhere
W_true_nu = C.w_cvu(M, enu, emu, th_nu)
Wp_nu, disc_nu, _ = C.w_pred(pt_nu, pz_nu, q3, M, mmu=mmu_gen)
res["control_resid_nuaxis_M_struck"] = C.summarize((W_true_nu - Wp_nu)[s])
# residual vs alpha and vs (pT) bins
r = W_true - C.w_pred(pt_b, pz_b, q3, M, mmu=mmu_gen)[0]
qa = np.quantile(alpha[s], [0, .25, .5, .75, .95, 1])
res["resid_vs_alpha_quartiles"] = []
for lo, hi in zip(qa[:-1], qa[1:]):
    m = s & (alpha >= lo) & (alpha <= hi)
    res["resid_vs_alpha_quartiles"].append({"alpha_mrad": [1e3 * lo, 1e3 * hi], **C.summarize(r[m])})
# linear sensitivity: dW per unit alpha (finite difference: rotate nu axis by +/- in y-z)
res["targetNucleon_counts"] = {str(int(k)): int(v) for k, v in zip(*np.unique(d["mc_targetNucleon"][s], return_counts=True))}
PTE = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5]) * 1000
PZE = np.array([1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60]) * 1000
psn = (pt_nu <= 4500) & (pz_nu >= 1500) & (pz_nu <= 60000) & (np.arctan2(pt_nu, pz_nu) < np.deg2rad(20))
res["axis_choice_effect"] = {
    "pT_beam_minus_pT_nu_MeV": C.summarize((pt_b - pt_nu)[s]),
    "pz_beam_minus_pz_nu_MeV": C.summarize((pz_b - pz_nu)[s]),
    "frac_fine_pT_bin_change": float((np.digitize(pt_b[s], PTE) != np.digitize(pt_nu[s], PTE)).mean()),
    "frac_fine_pz_bin_change": float((np.digitize(pz_b[s], PZE) != np.digitize(pz_nu[s], PZE)).mean()),
    "n_signal_beamaxis": int(s.sum()), "n_signal_nuaxis": int((fid & psn).sum()),
    "n_ps_disagree": int((s != (fid & psn)).sum())}
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res, indent=1))
