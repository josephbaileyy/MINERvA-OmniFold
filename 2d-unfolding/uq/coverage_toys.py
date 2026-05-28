#!/usr/bin/env python3
"""Stage-1 plan deliverable #5: coverage check from toy MC.

Reads the N coverage-toy ROOTs produced by sbatch_coverage_toys_MEFHC.sh
(closure + bootstrap-seed combo). For each reported bin of the (14 x 16)
grid, computes:

  - per-bin bootstrap sigma   = stdev of `hXSec2D` across toys
  - per-bin truth             = mean of `hTruthXSec2D` across toys (= CV)
  - per-toy residual          = (unfolded - truth) / sigma
  - per-bin coverage          = fraction of toys with |residual| <= 1

Reports the overall coverage and the list of bins below the Stage-1
target of 65 %. A perfectly calibrated bootstrap covariance gives
~68.27 % coverage (1 sigma). Significantly higher coverage indicates
the band is conservative; significantly lower indicates undercoverage.

Default toy glob: uq/coverage/2d_xsec_MEFHC_5iter_lgbm_coverage_toy*.root
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

import numpy as np
import ROOT


def th2_to_array(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    arr = np.zeros((nx, ny))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            arr[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
    return arr


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--toy-glob",
        default="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/"
                "uq/coverage/2d_xsec_MEFHC_5iter_lgbm_coverage_toy*.root",
        help="Glob pattern for toy ROOTs.")
    ap.add_argument("--target", type=float, default=0.65,
                    help="Stage-1 coverage target. Default 0.65.")
    ap.add_argument("--out-summary", default=None,
                    help="Optional TXT file to dump the per-bin coverage "
                         "table.")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.toy_glob))
    if len(paths) < 2:
        sys.exit(f"[FAIL] need >= 2 toys, found {len(paths)} matching "
                 f"{args.toy_glob!r}")
    print(f"[coverage] loading {len(paths)} toys from {args.toy_glob}")

    unfolded_per_toy = []
    truth_per_toy = []
    for p in paths:
        f = ROOT.TFile.Open(p)
        if not f or f.IsZombie():
            sys.exit(f"[FAIL] could not open {p}")
        hu = f.Get("hXSec2D")
        ht = f.Get("hTruthXSec2D")
        if not hu or not ht:
            sys.exit(f"[FAIL] {p}: hXSec2D or hTruthXSec2D missing "
                     f"(coverage toys must run with --closure so "
                     f"hTruthXSec2D is always written)")
        unfolded_per_toy.append(th2_to_array(hu))
        truth_per_toy.append(th2_to_array(ht))
        f.Close()

    U = np.stack(unfolded_per_toy, axis=0)  # (N, nx, ny)
    T = np.stack(truth_per_toy, axis=0)
    n_toys = U.shape[0]
    print(f"[coverage] toy shape: {U.shape}")

    truth_mean = T.mean(axis=0)
    truth_spread = T.std(axis=0, ddof=1)
    unfolded_mean = U.mean(axis=0)
    sigma = U.std(axis=0, ddof=1)
    print(f"[coverage] truth-marginal spread across toys: "
          f"max={truth_spread.max():.3e}  (should be ~0 in closure with "
          f"MC weights only resampling stat noise)")

    reported = (truth_mean > 0)
    n_rep = int(reported.sum())
    print(f"[coverage] reported bins (truth_mean > 0): {n_rep}")

    # Per-bin coverage: fraction of toys with |unfolded - truth_mean| <= sigma.
    diff = U - truth_mean[None, :, :]
    abs_diff = np.abs(diff)
    sigma_safe = np.where(sigma > 0, sigma, np.inf)
    covered = (abs_diff <= sigma_safe[None, :, :]).astype(float)
    coverage = covered.mean(axis=0)
    coverage_reported = coverage[reported]
    print(f"\n[coverage] per-bin coverage stats over {n_rep} reported bins")
    print(f"  mean         = {coverage_reported.mean()*100:.2f} %")
    print(f"  median       = {np.median(coverage_reported)*100:.2f} %")
    print(f"  min          = {coverage_reported.min()*100:.2f} %")
    print(f"  frac >= 1sigma (~68.27%) target  = "
          f"{(coverage_reported >= 0.6827).mean()*100:.2f} %")
    print(f"  frac >= Stage-1 target ({args.target*100:.0f}%) = "
          f"{(coverage_reported >= args.target).mean()*100:.2f} %")

    # Per-toy summary residual: mean residual and mean |residual|/sigma
    rel_resid = diff / sigma_safe[None, :, :]
    per_toy_signed = []
    per_toy_abs = []
    for i in range(n_toys):
        r = rel_resid[i][reported]
        per_toy_signed.append(r.mean())
        per_toy_abs.append(np.abs(r).mean())
    per_toy_signed = np.array(per_toy_signed)
    per_toy_abs = np.array(per_toy_abs)
    print(f"\n[coverage] per-toy residual / sigma stats")
    print(f"  signed mean across toys  = {per_toy_signed.mean():+.3f} +/- "
          f"{per_toy_signed.std(ddof=1):.3f}")
    print(f"  |residual|/sigma mean    = {per_toy_abs.mean():.3f} "
          f"(should be ~0.798 = sqrt(2/pi) for a unit normal)")

    # List bins below the Stage-1 target.
    below = np.argwhere(reported & (coverage < args.target))
    print(f"\n[coverage] bins below {args.target*100:.0f}% target: "
          f"{below.shape[0]} of {n_rep}")
    if below.shape[0]:
        print("  (ix, iy)  coverage  sigma         truth_mean")
        for ix, iy in below:
            print(f"  ({ix:2d},{iy:2d})    "
                  f"{coverage[ix,iy]*100:6.2f}%  "
                  f"{sigma[ix,iy]:.3e}  "
                  f"{truth_mean[ix,iy]:.3e}")

    overall_pass = (coverage_reported >= args.target).mean() >= 0.95
    median_pass = np.median(coverage_reported) >= args.target
    status = "PASS" if (overall_pass and median_pass) else "REVIEW"
    print(f"\n[coverage] STATUS: {status}")
    print(f"  Pass requires: median >= {args.target*100:.0f}% AND >= 95% "
          f"of bins above {args.target*100:.0f}%")

    if args.out_summary:
        with open(args.out_summary, "w") as f:
            f.write(f"# Stage-1 #5 coverage summary (n_toys={n_toys})\n")
            f.write(f"# ix iy coverage sigma truth_mean unfolded_mean\n")
            nx, ny = coverage.shape
            for ix in range(nx):
                for iy in range(ny):
                    if not reported[ix, iy]:
                        continue
                    f.write(f"{ix} {iy} {coverage[ix,iy]:.4f} "
                            f"{sigma[ix,iy]:.6e} "
                            f"{truth_mean[ix,iy]:.6e} "
                            f"{unfolded_mean[ix,iy]:.6e}\n")
        print(f"[coverage] wrote summary to {args.out_summary}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
