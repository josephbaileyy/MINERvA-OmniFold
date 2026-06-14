#!/usr/bin/env python3
"""Project the (E_avail, q3) double-differential data/GENIE ratio from the 4D CV.

The 4D driver saves the unfolded counts (hUnfoldND) but not the GENIE prior. The
prior numerator is prior_nd = histnd(truth-pass kinematics, w_truth); the unfolded
numerator is unfold_nd = histnd(truth-pass, step2_w*w_truth). Their ratio cancels
efficiency (completeness), flux, POT and nucleon normalization -> it is exactly the
bin-by-bin data/GENIE pull (the "excess"). We recompute prior_nd from the merged 4D
omnifile (matching the saved hUnfoldND's POT scaling), divide, and marginalize to
(E_avail, q3), q3, and E_avail. No frozen product is touched; outputs are new files.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import sys
import numpy as np
import ROOT

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if p not in sys.path:
        sys.path.insert(0, p)
import unfold_2d_omnifold_unbinned as u2d
import unfold_nd_omnifold_unbinned as und

OMNI = f"{_REPO}/nd-unfolding/runEventLoopOmniFold_4D_MEFHC.root"
CV = f"{_REPO}/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root"

pt_e = np.asarray(u2d.PT_EDGES, float); pz_e = np.asarray(u2d.PZ_EDGES, float)
ea_e = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
q3_e = np.asarray(und.EXTRA_AXES["q3"]["edges"], float)
edges = [pt_e, pz_e, ea_e, q3_e]
shape = tuple(len(e) - 1 for e in edges)
THMAX = u2d.MAX_MUON_THETA_RAD

# ---- GENIE prior numerator from the omnifile (truth-pass, w_truth, POT-scaled) ----
f = ROOT.TFile.Open(OMNI)
data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
f.Close()
print(f"[pot] data={data_pot:.4e} mc={mc_pot:.4e} scale={pot_scale:.4e}")

ROOT.EnableImplicitMT()
df = ROOT.RDataFrame("mc_signal_reco", OMNI)
cols = df.AsNumpy(["MC", "MC_pz", "MC_eavail", "MC_q3", "w_truth"])
pt = np.asarray(cols["MC"], float); pz = np.asarray(cols["MC_pz"], float)
ea = np.asarray(cols["MC_eavail"], float); q3 = np.asarray(cols["MC_q3"], float)
wt = np.asarray(cols["w_truth"], float) * pot_scale

fin = np.isfinite(pt) & np.isfinite(pz)
m = fin & (pt >= pt_e[0]) & (pt <= pt_e[-1]) & (pz >= pz_e[0]) & (pz <= pz_e[-1])
m &= (np.arctan2(np.where(fin, pt, 0.0), np.where(fin, pz, 1.0)) < THMAX)
print(f"[sel] truth-pass {m.sum()}/{m.size}")

prior_nd, _ = np.histogramdd(np.column_stack([pt[m], pz[m], ea[m], q3[m]]),
                             bins=edges, weights=wt[m])

# ---- unfolded counts (saved) ----
fc = ROOT.TFile.Open(CV)
h = fc.Get("hUnfoldND_flat")
unfold_flat = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
fc.Close()
unfold_nd = unfold_flat.reshape(shape, order="C")
print(f"[norm] sum unfold={unfold_nd.sum():.4e} sum prior={prior_nd.sum():.4e} "
      f"integrated data/GENIE={unfold_nd.sum()/prior_nd.sum():.4f}")


def marg(a, keep):  # sum over all axes except those in keep
    drop = tuple(i for i in range(4) if i not in keep)
    return a.sum(axis=drop)


# (E_avail, q3) double-differential ratio
u_eq = marg(unfold_nd, (2, 3)); p_eq = marg(prior_nd, (2, 3))
ratio_eq = np.full_like(u_eq, np.nan); nz = p_eq > 0; ratio_eq[nz] = u_eq[nz] / p_eq[nz]
# 1D q3 and E_avail
u_q3 = marg(unfold_nd, (3,)); p_q3 = marg(prior_nd, (3,)); r_q3 = u_q3 / p_q3
u_ea = marg(unfold_nd, (2,)); p_ea = marg(prior_nd, (2,)); r_ea = u_ea / p_ea

np.set_printoptions(precision=3, suppress=True)
print("\n=== data/GENIE ratio in (E_avail rows x q3 cols) ===")
print("E_avail edges:", ea_e.tolist())
print("q3 edges     :", q3_e.tolist())
print(ratio_eq)
print("\n=== q3 marginal data/GENIE ===");   print(np.column_stack([q3_e[:-1], q3_e[1:], r_q3]))
print("\n=== E_avail marginal data/GENIE ==="); print(np.column_stack([ea_e[:-1], ea_e[1:], r_ea]))

# ---- plot ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
# panel 1: 2D ratio heatmap (cap q3/eavail axes at the last finite edge for labels)
disp = ratio_eq.copy()
im = ax[0].imshow(disp, origin="lower", aspect="auto", cmap="RdBu_r",
                  norm=TwoSlopeNorm(vcenter=1.0, vmin=np.nanmin(disp), vmax=np.nanmax(disp)))
ax[0].set_xticks(range(len(q3_e) - 1)); ax[0].set_yticks(range(len(ea_e) - 1))
ax[0].set_xticklabels([f"{q3_e[i]:.1f}-{q3_e[i+1]:.1f}" for i in range(len(q3_e) - 1)], rotation=45, fontsize=7)
ax[0].set_yticklabels([f"{ea_e[i]:.1f}-{ea_e[i+1]:.1f}" for i in range(len(ea_e) - 1)], fontsize=7)
ax[0].set_xlabel("q3 [GeV]"); ax[0].set_ylabel("E_avail [GeV]")
ax[0].set_title("data / GENIE ratio  (E_avail, q3)")
for (r, c), v in np.ndenumerate(disp):
    if np.isfinite(v):
        ax[0].text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=6)
fig.colorbar(im, ax=ax[0], fraction=0.046)
# panel 2: q3 marginal
xc = 0.5 * (q3_e[:-1] + q3_e[1:]); xc[-1] = q3_e[-2] + 0.3
ax[1].step(range(len(r_q3)), r_q3, where="mid", color="k")
ax[1].axhline(1.0, ls="--", color="grey")
ax[1].set_xticks(range(len(r_q3)))
ax[1].set_xticklabels([f"{q3_e[i]:.1f}" for i in range(len(q3_e) - 1)], fontsize=7)
ax[1].set_xlabel("q3 [GeV] (low edge)"); ax[1].set_ylabel("data/GENIE"); ax[1].set_title("q3 marginal")
# panel 3: eavail marginal
ax[2].step(range(len(r_ea)), r_ea, where="mid", color="firebrick")
ax[2].axhline(1.0, ls="--", color="grey")
ax[2].set_xticks(range(len(r_ea)))
ax[2].set_xticklabels([f"{ea_e[i]:.1f}" for i in range(len(ea_e) - 1)], fontsize=7)
ax[2].set_xlabel("E_avail [GeV] (low edge)"); ax[2].set_ylabel("data/GENIE")
ax[2].set_title("E_avail marginal (cf. 3D excess)")
fig.tight_layout()
out = f"{_REPO}/nd-unfolding/q3_excess_projection.png"
fig.savefig(out, dpi=130)
print(f"\n[wrote] {out}")
