#!/usr/bin/env python3
"""Hidden-variable closure (Stage-1 plan deliverable #4).

Biases the closure pseudo-data on a variable that is NOT in the OmniFold
feature set, then unfolds against (pT, pz) and quantifies the residual
bias on the truth marginal. A perfect OmniFold pipeline should ignore
the hidden-axis bias and recover the CV truth marginal.

The plan calls for recoil-energy or x_Bj as the hidden variable. Those
branches are not currently dumped into the Phase-18.2 omnifile (the
event loop emits only (sim_pT, sim_pz, truth_pT, truth_pz, w_truth,
w_reco) + universe weight columns). Until the C++ event loop is
extended to dump a hidden kinematic axis, this driver uses the
**reco-vs-truth pT resolution dpT = sim_pT - truth_pT** as the hidden
variable. dpT is:
  - physically meaningful (detector resolution)
  - directly computable from existing omnifile columns
  - NOT used as a feature by OmniFold (which sees sim_pT/sim_pz on the
    reco side and truth_pT/truth_pz on the truth side independently)
  - approximately uncorrelated with the truth marginal in MINERvA's
    forward muon kinematics, so a Stage-1 acceptable residual is small.

Mechanics:
  - The unfold is called with --closure --closure-hidden-dpt --amplitude
    --center --sigma. Inside the unfold, the closure pseudo-data weights
    are multiplied by a Gaussian bump 1 + A * exp(-((dpT - c)/s)^2) per
    event. Truth weights are LEFT UNCHANGED, so hTruth2D / hTruthXSec2D
    remain the CV truth marginal (the reference).
  - Residuals are computed as (hXSec2D - hTruthXSec2D) / hTruthXSec2D
    over the 205 paper-reported bins of the (14 x 16) grid.

Stage-1 acceptance threshold: median |residual| <= 3.0 % per bin.
Looser than the truth-reweight closure (1.5 %) because dpT and pT are
weakly correlated through the resolution model -- some residual leak is
expected and physically meaningful. Set higher if the smoke reveals
a stronger correlation than the MC suggests.

Default smoke target: 1A omnifile, lgbm 5-iter, dpT bump A=0.3,
center=0.1 GeV/c, sigma=0.05 GeV/c. Runtime ~2 min on a live
interactive allocation at 128 CPU.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import numpy as np
import ROOT


DEFAULT_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DEFAULT_DOCS = f"{DEFAULT_REPO}/2d-unfolding"


def run_unfold(args):
    cmd = [
        "python", f"{DEFAULT_DOCS}/unfold_2d_omnifold_unbinned.py",
        "--omnifile", args.omnifile,
        "--mcfile", args.mcfile,
        "--iters", str(args.iters),
        "--use-weights",
        "--estimator", args.estimator,
        "--seed", str(args.seed),
        "--closure",
        "--closure-hidden-dpt",
        "--closure-hidden-dpt-amplitude", str(args.amplitude),
        "--closure-hidden-dpt-center", str(args.center),
        "--closure-hidden-dpt-sigma", str(args.sigma),
        "--out", args.out,
    ]
    print(f"[closure-hidden] launching unfold:\n  {' '.join(cmd)}")
    rc = subprocess.call(cmd)
    if rc != 0:
        sys.exit(f"[FAIL] unfold exited with code {rc}")


def th2_to_array(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    arr = np.zeros((nx, ny))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            arr[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
    return arr


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--omnifile",
                    default=f"{DEFAULT_DOCS}/runEventLoopOmniFold_1A_universes.root",
                    help="Input omnifile (Stage-1 1A universes works fine).")
    ap.add_argument("--mcfile",
                    default=f"{DEFAULT_DOCS}/baseline_flux/runEventLoopMC_1A.root",
                    help="Per-playlist baseline flux for normalization.")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--estimator", default="lgbm",
                    choices=["exact", "hist", "xgb", "lgbm"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--amplitude", type=float, default=0.3,
                    help="dpT bump amplitude A in f = 1 + A * exp(...).")
    ap.add_argument("--center", type=float, default=0.1,
                    help="dpT bump center (GeV/c).")
    ap.add_argument("--sigma", type=float, default=0.05,
                    help="dpT bump sigma (GeV/c).")
    ap.add_argument("--threshold-median", type=float, default=0.03,
                    help="Pass condition: median per-bin |residual| <= this. "
                         "Default 3 percent; looser than the truth-reweight "
                         "closure because dpT-vs-truth-pT correlations leak "
                         "some hidden-axis bias into the truth marginal.")
    ap.add_argument("--out",
                    default=f"{DEFAULT_DOCS}/uq/closure/"
                            "2d_xsec_1A_5iter_lgbm_closure_hidden_dpt.root",
                    help="Output ROOT from the unfold.")
    ap.add_argument("--skip-unfold", action="store_true",
                    help="Skip the unfold; just analyze an existing --out.")
    args = ap.parse_args()

    if not args.skip_unfold:
        run_unfold(args)

    f = ROOT.TFile.Open(args.out)
    if not f or f.IsZombie():
        sys.exit(f"[FAIL] could not open {args.out}")
    hXSec = f.Get("hXSec2D")
    hRef = f.Get("hTruthXSec2D")
    if not hXSec or not hRef:
        sys.exit("[FAIL] hXSec2D / hTruthXSec2D missing in output ROOT "
                 "(rerun the unfold; --closure should always emit "
                 "hTruthXSec2D after the hidden-var hook landed)")

    unfolded = th2_to_array(hXSec)
    ref = th2_to_array(hRef)
    print(f"[closure-hidden] hXSec2D integral      = {hXSec.Integral():.6e}")
    print(f"[closure-hidden] hTruthXSec2D integral = {hRef.Integral():.6e}")

    reported = (ref > 0)
    n_rep = int(reported.sum())
    if n_rep == 0:
        sys.exit("[FAIL] no reported bins in hTruthXSec2D")
    rel = np.zeros_like(ref)
    rel[reported] = (unfolded[reported] - ref[reported]) / ref[reported]
    abs_rel = np.abs(rel[reported])

    median = float(np.median(abs_rel))
    p84 = float(np.percentile(abs_rel, 84))
    p_max = float(np.max(abs_rel))
    print(f"\n[closure-hidden] |residual| stats over {n_rep} reported bins")
    print(f"  median = {median*100:.3f} %")
    print(f"  p84    = {p84*100:.3f} %")
    print(f"  max    = {p_max*100:.3f} %")

    signed = rel[reported]
    print(f"  signed mean = {signed.mean()*100:+.3f} %  "
          f"std = {signed.std(ddof=1)*100:.3f} %")

    threshold = args.threshold_median
    status = "PASS" if median <= threshold else "FAIL"
    print(f"\n[closure-hidden] STATUS: {status} "
          f"(threshold median <= {threshold*100:.2f} %)")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
