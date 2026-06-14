#!/usr/bin/env python3
"""FPS acceptance study (pilot, 1A): how much truth rate lies outside the
published muon phase space, and where the detector acceptance dies.

Reads the MNV101_FULL_PHASE_SPACE omnifile (truth denominator = nu_mu CC in
the tracker fiducial, NO muon kinematic cuts) and reports, on the extended
(pT, p||) grid:

  - weighted truth-rate fractions inside/outside the published cuts
    (theta<20deg, 1.5<p||<60 GeV/c, pT<4.5 GeV/c), split by which cut fails;
  - the reco efficiency map  eff = sum_w(sim_pass) / sum_w(truth)  per cell;
  - the dead region (eff below threshold) and its truth-rate share.

  python fps_acceptance.py --omnifile runEventLoopOmniFold_5D_FPS_1A.root
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import math
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unfold_2d_omnifold_unbinned as u2d

# extended grid = the EXACT paper edges plus catch bins (pT>4.5; p||<1.5 split in
# two; p||>60), so the published-phase-space sub-block is bin-identical
PT_EXT = list(u2d.PT_EDGES) + [30.0]
PZ_EXT = [0.0, 0.75] + list(u2d.PZ_EDGES) + [120.0]
TAN20 = math.tan(math.radians(20.0))


def main():
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.EnableImplicitMT(8)

    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_FPS_1A.root")
    ap.add_argument("--out-png", default="products/5d/fps_acceptance_1A.png")
    ap.add_argument("--eff-floor", type=float, default=0.02,
                    help="cells below this efficiency count as 'dead'")
    args = ap.parse_args()

    pt_e = np.asarray(PT_EXT, float)
    pz_e = np.asarray(PZ_EXT, float)

    td = ROOT.RDataFrame("mc_truth_denom", args.omnifile)
    td = td.Define("theta_ok", f"MC < {TAN20} * MC_pz") \
           .Define("rect_ok", "MC < 4.5 && MC_pz > 1.5 && MC_pz < 60.0") \
           .Define("oldps", "theta_ok && rect_ok")

    tot = td.Sum("w_truth")
    n_in = td.Filter("oldps").Sum("w_truth")
    n_theta = td.Filter("rect_ok && !theta_ok").Sum("w_truth")
    n_pzlo = td.Filter("MC_pz <= 1.5").Sum("w_truth")
    n_pzhi = td.Filter("MC_pz >= 60.0").Sum("w_truth")
    n_pthi = td.Filter("MC >= 4.5 && MC_pz > 1.5 && MC_pz < 60.0").Sum("w_truth")

    m2t = ROOT.RDF.TH2DModel("truth2d", "", len(pt_e) - 1, pt_e, len(pz_e) - 1, pz_e)
    h_truth = td.Histo2D(m2t, "MC", "MC_pz", "w_truth")

    sig = ROOT.RDataFrame("mc_signal_reco", args.omnifile)
    m2r = ROOT.RDF.TH2DModel("reco2d", "", len(pt_e) - 1, pt_e, len(pz_e) - 1, pz_e)
    h_reco = sig.Filter("sim_pass").Histo2D(m2r, "MC", "MC_pz", "w_truth")

    T = tot.GetValue()
    print(f"[acc] weighted truth total (nu_mu CC, tracker fiducial): {T:.6g}")
    for nm, v in [("inside published PS", n_in), ("theta>20 (rect ok)", n_theta),
                  ("p||<1.5", n_pzlo), ("p||>60", n_pzhi),
                  ("pT>4.5 (p|| ok)", n_pthi)]:
        x = v.GetValue()
        print(f"[acc]   {nm:24s} {x:.6g}  ({100*x/T:.2f}%)")

    HT = np.array([[h_truth.GetBinContent(i + 1, j + 1) for j in range(len(pz_e) - 1)]
                   for i in range(len(pt_e) - 1)])
    HR = np.array([[h_reco.GetValue().GetBinContent(i + 1, j + 1) for j in range(len(pz_e) - 1)]
                   for i in range(len(pt_e) - 1)])
    eff = np.where(HT > 0, HR / HT, np.nan)
    dead = (HT > 0) & ((HR / np.maximum(HT, 1e-30)) < args.eff_floor)
    dead_rate = HT[dead].sum()
    print(f"[acc] dead cells (eff<{args.eff_floor}): {dead.sum()} of {(HT>0).sum()} "
          f"populated; truth-rate share {100*dead_rate/T:.2f}%")
    new = HT.sum() - n_in.GetValue()
    print(f"[acc] new rate outside published PS: {100*new/T:.2f}% of total")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(19, 5))
    X, Y = np.arange(len(pt_e)), np.arange(len(pz_e))
    im0 = axs[0].pcolormesh(X, Y, np.log10(np.maximum(HT, 1e-1)).T, cmap="viridis")
    im1 = axs[1].pcolormesh(X, Y, eff.T, cmap="viridis", vmin=0, vmax=0.7)
    im2 = axs[2].pcolormesh(X, Y, dead.astype(float).T, cmap="viridis", vmin=0, vmax=1)
    labels = [r"(a) truth rate (log$_{10}$)", "(b) reco efficiency",
              rf"(c) dead region (eff$<${args.eff_floor})"]
    for A, im, lab in zip(axs, [im0, im1, im2], labels):
        # mark the published phase-space boundary in bin coordinates
        ipt45 = np.searchsorted(pt_e, 4.5)
        ipz15, ipz60 = np.searchsorted(pz_e, 1.5), np.searchsorted(pz_e, 60.0)
        A.axvline(ipt45, color="cyan", lw=1.2)
        A.axhline(ipz15, color="cyan", lw=1.2)
        A.axhline(ipz60, color="cyan", lw=1.2)
        A.set_xlabel("pT bin (extended)")
        A.set_ylabel("p|| bin (extended)")
        fig.colorbar(im, ax=A, fraction=0.046, pad=0.04)
        technote_style.panel_label(A, lab)
    fig.subplots_adjust(wspace=0.55)  # keep each colorbar clear of the next panel's y-label
    os.makedirs(os.path.dirname(args.out_png), exist_ok=True)
    fig.savefig(args.out_png, dpi=140, bbox_inches="tight")
    print(f"[acc] wrote {args.out_png}")


if __name__ == "__main__":
    main()
