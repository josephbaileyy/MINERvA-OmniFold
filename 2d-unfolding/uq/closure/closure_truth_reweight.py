#!/usr/bin/env python3
"""Truth-reweight closure (Stage-1 plan deliverable #4).

Applies a known multiplicative reweight `f(pT_truth, pz_truth)` to the
closure pseudo-data (MC reco weighted by truth-side f) AND to the truth
reference (MC truth weighted by the same f). A correctly unbiased
OmniFold pipeline should map the reco-side pseudo-data shift back into
the matching reweighted truth.

This script drives `unfold_2d_omnifold_unbinned.py --closure
--closure-reweight ...`, then compares the unfolded 2D cross section
`hXSec2D` to the reweighted-truth reference `hTruthRewXSec2D` (both
written to the unfold's output ROOT by the same normalization
machinery, so they share units).

Reports:
  - Per-bin residual (unfolded - ref) / ref over the 205 paper-reported
    bins of the (14 x 16) grid.
  - Median, p84, max relative residual.
  - Whether the median is within a configurable threshold; default is
    1.5 % per-bin, comfortably above the n=10 MEFHC seedscan median of
    0.36 % and the 1A-only ~0.79 % per-bin ML noise floor.

Default smoke target: 1A omnifile, lgbm 5-iter, gauss_pt bump (A=0.2,
sigma=0.1, pt0=0.4 GeV/c). Runtime ~2 min on a live interactive
allocation at 128 CPU.
"""
from __future__ import annotations

import argparse
import os
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
        "--closure-reweight", args.shape,
        "--closure-reweight-amplitude", str(args.amplitude),
        "--closure-reweight-sigma", str(args.sigma),
        "--closure-reweight-pt0", str(args.pt0),
        "--closure-reweight-alpha", str(args.alpha),
        "--closure-reweight-pz-ref", str(args.pz_ref),
        "--out", args.out,
    ]
    print(f"[closure] launching unfold:\n  {' '.join(cmd)}")
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
    ap.add_argument("--shape", default="gauss_pt",
                    choices=["gauss_pt", "tilt_pz"])
    ap.add_argument("--amplitude", type=float, default=0.2)
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--pt0", type=float, default=0.4)
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--pz-ref", type=float, default=5.0)
    ap.add_argument("--threshold-median", type=float, default=0.015,
                    help="Pass condition: median per-bin |residual| <= this. "
                         "Default 1.5 percent; comfortably above the 1A ML "
                         "noise floor of ~0.79 percent.")
    ap.add_argument("--out",
                    default=f"{DEFAULT_DOCS}/uq/closure/"
                            "2d_xsec_1A_5iter_lgbm_closure_truthrw.root",
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
    hRef = f.Get("hTruthRewXSec2D")
    if not hXSec or not hRef:
        sys.exit("[FAIL] hXSec2D / hTruthRewXSec2D missing in output ROOT")

    unfolded = th2_to_array(hXSec)
    ref = th2_to_array(hRef)
    print(f"[closure] hXSec2D integral         = {hXSec.Integral():.6e}")
    print(f"[closure] hTruthRewXSec2D integral = {hRef.Integral():.6e}")

    reported = (ref > 0)
    n_rep = int(reported.sum())
    if n_rep == 0:
        sys.exit("[FAIL] no reported bins in hTruthRewXSec2D")
    rel = np.zeros_like(ref)
    rel[reported] = (unfolded[reported] - ref[reported]) / ref[reported]
    abs_rel = np.abs(rel[reported])

    median = float(np.median(abs_rel))
    p84 = float(np.percentile(abs_rel, 84))
    p_max = float(np.max(abs_rel))
    print(f"\n[closure] |residual| stats over {n_rep} reported bins")
    print(f"  median = {median*100:.3f} %")
    print(f"  p84    = {p84*100:.3f} %")
    print(f"  max    = {p_max*100:.3f} %")

    # Mean signed residual: should be near zero. A large non-zero mean
    # indicates a systematic bias rather than ML noise.
    signed = rel[reported]
    print(f"  signed mean = {signed.mean()*100:+.3f} %  "
          f"std = {signed.std(ddof=1)*100:.3f} %")

    threshold = args.threshold_median
    status = "PASS" if median <= threshold else "FAIL"
    print(f"\n[closure] STATUS: {status} "
          f"(threshold median <= {threshold*100:.2f} %)")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
