#!/usr/bin/env python3
"""Project the (E_avail, q3) double-differential data/GENIE ratio from the 4D CV.

The 4D driver saves the unfolded counts (hUnfoldND) but not the GENIE prior. The
prior numerator is prior_nd = histnd(truth-pass kinematics, w_truth); the unfolded
numerator is unfold_nd = histnd(truth-pass, step2_w*w_truth). Their ratio cancels
efficiency (completeness), flux, POT and nucleon normalization -> it is exactly the
bin-by-bin data/GENIE pull (the "excess"). We recompute prior_nd from the merged 4D
omnifile (matching the saved hUnfoldND's POT scaling), divide, and marginalize to
(E_avail, q3), q3, and E_avail. No frozen product is touched; outputs are new files.

Opt-in (note figure style, group C family 5): --omni, --cv and --out name the inputs and the output (their defaults are
the paths this script always used); --dump-arrays FILE.npz writes every drawn value after the read; --from-arrays
FILE.npz draws from such a dump (no RDataFrame; the module still imports the drivers for the grid, which import ROOT).
With no option, the figure is drawn as before.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import os
import sys
import numpy as np
import argparse

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
# OI-136: root derived from __file__, never the hardcoded cluster root
_CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(_CODE_ROOT, "2d-unfolding"), os.path.join(_CODE_ROOT, "nd-unfolding")):
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

def fill(omni, cv):
    """The prior and unfolded 4D counts, their ratio and its marginals: everything the figure draws."""
    import ROOT
    # ---- GENIE prior numerator from the omnifile (truth-pass, w_truth, POT-scaled) ----
    f = ROOT.TFile.Open(omni)
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    f.Close()
    print(f"[pot] data={data_pot:.4e} mc={mc_pot:.4e} scale={pot_scale:.4e}")

    ROOT.EnableImplicitMT()
    df = ROOT.RDataFrame("mc_signal_reco", omni)
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
    fc = ROOT.TFile.Open(cv)
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
    return {"ratio_eq": ratio_eq, "r_q3": r_q3, "r_ea": r_ea, "q3_e": q3_e, "ea_e": ea_e}


def draw(arr, out):
    ratio_eq, r_q3, r_ea, q3_e, ea_e = (arr[k] for k in ("ratio_eq", "r_q3", "r_ea", "q3_e", "ea_e"))
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
    technote_style.minerva_tag(ax[0])
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"\n[wrote] {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omni", default=OMNI, help="the merged 4D omnifile (default: the path this script always read)")
    ap.add_argument("--cv", default=CV, help="the 4D CV product (default: the path this script always read)")
    ap.add_argument("--out", default=f"{_REPO}/nd-unfolding/q3_excess_projection.png")
    ap.add_argument("--dump-arrays", default=None, help="write every drawn value to this .npz after the read")
    ap.add_argument("--from-arrays", default=None, help="draw from this .npz (no RDataFrame)")
    args = ap.parse_args()
    if args.from_arrays:
        with np.load(args.from_arrays) as z:
            arr = {k: z[k] for k in z.files}
    else:
        arr = fill(args.omni, args.cv)
        if args.dump_arrays:
            np.savez(args.dump_arrays, **arr)
    draw(arr, args.out)


if __name__ == "__main__":
    main()
