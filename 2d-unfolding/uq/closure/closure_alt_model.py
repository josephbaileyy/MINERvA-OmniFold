#!/usr/bin/env python3
"""Alternative-model closure (Stage-1 plan deliverable #4).

Injects an alternative-model bias into the closure pseudo-data using
one of the MINERvA universe-weight columns as the alt-model proxy.
The CV response (mc_signal_reco weighted by CV w_truth / w_reco) is
kept unchanged. A correctly unbiased OmniFold should recover the
alt-model truth marginal even though the response was trained at CV.

Plan-original spec: "hand-rolled `Rvx1pi → 0` / `MEC → 0` weight
twist". The current omnifile carries the GENIE knob universes
{MaCCQE, Rvp1pi, Rvn1pi, MinosEfficiency, Muon_Energy_MINOS} plus
the 100-universe Flux PPFX ensemble. The closest available
hand-rolled twist using the existing dump is MaCCQE:0 (the +1σ
MaCCQE universe) or Rvp1pi:0 / Rvn1pi:0 (±1σ single-pion knobs)
— these correspond to well-defined alt-model shifts comparable in
size to the plan-original MEC→0 / Rvx1pi→0 weight twists.

Mechanics:
  - The unfold is called with --closure --closure-alt-universe BAND:IDX.
    Inside the unfold:
      - CV w_truth / w_reco are loaded normally so the response stays
        at CV.
      - Additional w_truth_alt / w_reco_alt columns are loaded from
        the corresponding universe branches.
      - In closure mode, measured_weights is REPLACED by w_reco_alt
        (instead of CV w_reco). The reference histogram hTruthAlt2D
        (and its cross-section counterpart hTruthAltXSec2D) is built
        from truth weighted by w_truth_alt.
  - Residuals are computed as (hXSec2D - hTruthAltXSec2D) /
    hTruthAltXSec2D over the 205 paper-reported bins of the (14 x 16)
    grid.

Default smoke target: 1A omnifile, lgbm 5-iter, MaCCQE:0 alt model,
seed 42. Runtime ~2 min on a live interactive allocation at 128 CPU.

Stage-1 acceptance threshold: median |residual| <= 2.0 % per bin.
A correctly unbiased OmniFold should not leak alt-model -> CV
response mismatch into the truth marginal at the percent level,
because the alt-model bias is contained on truth-side features
(pT, pz) which OmniFold sees directly. The threshold is looser than
the truth-reweight closure (1.5 %) to absorb the larger amplitude
of typical GENIE knobs vs the controlled gauss_pt/tilt_pz shapes.
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
        "--closure-alt-universe", args.alt_universe,
        "--out", args.out,
    ]
    print(f"[closure-alt] launching unfold:\n  {' '.join(cmd)}")
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
    ap.add_argument("--alt-universe", default="MaCCQE:0",
                    help="Alt-model BAND:IDX. Default MaCCQE:0 (the +1sigma "
                         "MaCCQE universe, equivalent to a hand-rolled GENIE "
                         "QE-axial-mass twist). Other useful choices: "
                         "Rvp1pi:0, Rvn1pi:0 (single-pion sector), or "
                         "Flux:42 (PPFX universe, broader but smaller "
                         "amplitude).")
    ap.add_argument("--threshold-median", type=float, default=0.02,
                    help="Pass condition: median per-bin |residual| <= this. "
                         "Default 2 percent. Set higher for large-amplitude "
                         "alt models that produce >5 percent truth-marginal "
                         "shifts.")
    ap.add_argument("--out",
                    default=None,
                    help="Output ROOT from the unfold. Default derived from "
                         "--alt-universe.")
    ap.add_argument("--skip-unfold", action="store_true",
                    help="Skip the unfold; just analyze an existing --out.")
    args = ap.parse_args()

    if args.out is None:
        tag = args.alt_universe.replace(":", "_")
        args.out = (f"{DEFAULT_DOCS}/uq/closure/"
                    f"2d_xsec_1A_5iter_lgbm_closure_alt_{tag}.root")

    if not args.skip_unfold:
        run_unfold(args)

    f = ROOT.TFile.Open(args.out)
    if not f or f.IsZombie():
        sys.exit(f"[FAIL] could not open {args.out}")
    hXSec = f.Get("hXSec2D")
    hRef = f.Get("hTruthAltExtrapolatedXSec2D")
    hAltFull = f.Get("hTruthAltXSec2D")
    hCV = f.Get("hTruthXSec2D")
    if not hXSec or not hRef:
        sys.exit("[FAIL] hXSec2D / hTruthAltExtrapolatedXSec2D missing in "
                 "output ROOT (rerun the unfold; --closure-alt-universe "
                 "must produce the in-acceptance extrapolation in the output)")

    unfolded = th2_to_array(hXSec)
    ref = th2_to_array(hRef)
    print(f"[closure-alt] hXSec2D integral                     = "
          f"{hXSec.Integral():.6e}")
    print(f"[closure-alt] hTruthAltExtrapolatedXSec2D integral = "
          f"{hRef.Integral():.6e}  (in-accept extrapolation target)")
    if hAltFull:
        print(f"[closure-alt] hTruthAltXSec2D integral             = "
              f"{hAltFull.Integral():.6e}  (full alt-truth, NOT the unfold "
              f"target)")
    if hCV:
        print(f"[closure-alt] hTruthXSec2D integral                = "
              f"{hCV.Integral():.6e}  (CV truth, for comparison)")
        alt_vs_cv = (hRef.Integral() - hCV.Integral()) / hCV.Integral()
        print(f"[closure-alt] in-accept alt vs CV integral rel diff = "
              f"{alt_vs_cv*100:+.3f} %  (in-accept bias size)")

    reported = (ref > 0)
    n_rep = int(reported.sum())
    if n_rep == 0:
        sys.exit("[FAIL] no reported bins in hTruthAltXSec2D")
    rel = np.zeros_like(ref)
    rel[reported] = (unfolded[reported] - ref[reported]) / ref[reported]
    abs_rel = np.abs(rel[reported])

    median = float(np.median(abs_rel))
    p84 = float(np.percentile(abs_rel, 84))
    p_max = float(np.max(abs_rel))
    print(f"\n[closure-alt] |residual| stats over {n_rep} reported bins")
    print(f"  median = {median*100:.3f} %")
    print(f"  p84    = {p84*100:.3f} %")
    print(f"  max    = {p_max*100:.3f} %")

    signed = rel[reported]
    print(f"  signed mean = {signed.mean()*100:+.3f} %  "
          f"std = {signed.std(ddof=1)*100:.3f} %")

    threshold = args.threshold_median
    status = "PASS" if median <= threshold else "FAIL"
    print(f"\n[closure-alt] STATUS: {status} "
          f"(threshold median <= {threshold*100:.2f} %)")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
