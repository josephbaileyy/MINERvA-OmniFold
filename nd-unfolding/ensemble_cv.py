#!/usr/bin/env python3
"""NTRIAL ensemble-mean central value from the train/test-split trials.

Implements the ensemble-mean-CV convention used by rhuang1/OmnifoldT2K (NTRIAL) and the
ViniciusMikuni/omnifold n_ensemble path, and recommended by the T2K (2504.06857) /
Practical-Guide (2507.09582) papers: instead of a single OmniFold run, run the procedure
NTRIAL times with independent train/test splits and take the ENSEMBLE MEAN as the central
value, with the trial spread as the (defensible) ML/optimization uncertainty.

Our train/test-split seedscan (#4, seedscan_split.py) already produced the NTRIAL trials
(seedscan_split/res_split_*.npz, each a full unfold on an independent 80% split). This
reads them and emits the ensemble-mean cross section as the CV product, plus the per-bin
ensemble spread. No new compute -- the trials exist.

  python ensemble_cv.py --glob 'seedscan_split/res_split_*.npz' \
      --cv ../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root --out ensemble_cv_3d.root

Note (NN path): the vendored MLP/PET (omnifold_nn_core) needs feature standardization
(_StandardScaler, already applied) before ensembling; the GBDT path is scale-free. The
ensembling math here is identical for either engine -- only the per-trial unfold differs.
"""
import argparse
import glob

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="seedscan_split/res_split_*.npz")
    ap.add_argument("--cv", default="../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root",
                    help="frozen single-run CV (TH3D hXSec3D), for the reported mask "
                         "+ ensemble-vs-single comparison.")
    ap.add_argument("--out", default="ensemble_cv_3d.root")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.glob))
    if not paths:
        raise SystemExit(f"[FAIL] no trials matched {args.glob}")
    flats = np.stack([np.load(p)["xsec_flat"] for p in paths], axis=0)  # (N, nbins_full)
    shape = tuple(int(x) for x in np.load(paths[0])["shape"])
    N = flats.shape[0]
    print(f"[INFO] {N} NTRIAL split trials; full nbins={flats.shape[1]} shape={shape}")

    # single-run frozen CV (reported mask)
    f = ROOT.TFile.Open(args.cv)
    h = f.Get("hXSec3D")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    cv = np.array([h.GetBinContent(ix, iy, iz)
                   for ix in range(1, nx + 1) for iy in range(1, ny + 1)
                   for iz in range(1, nz + 1)])
    f.Close()
    rep = cv > 0

    mean = flats.mean(axis=0)                 # ensemble-mean CV (full grid)
    std = flats.std(axis=0, ddof=1)           # ensemble spread
    mean_rep, std_rep, cv_rep = mean[rep], std[rep], cv[rep]
    with np.errstate(divide="ignore", invalid="ignore"):
        spread_rel = np.where(mean_rep > 0, std_rep / mean_rep, 0)
        shift = np.where(cv_rep > 0, (mean_rep - cv_rep) / cv_rep, 0)
    print(f"[ensemble-mean CV] reported bins={int(rep.sum())}")
    print(f"  ensemble spread (ML band): median {100*np.median(spread_rel):.3f}%  "
          f"p84 {100*np.percentile(spread_rel,84):.3f}%  max {100*np.max(spread_rel):.3f}%")
    print(f"  ensemble-mean vs frozen single-run CV: median |shift| "
          f"{100*np.median(np.abs(shift)):.3f}%  max {100*np.max(np.abs(shift)):.3f}%")

    # write ensemble-mean CV + spread back onto the 3D grid (same binning as hXSec3D)
    out = ROOT.TFile.Open(args.out, "RECREATE")
    xe = [h.GetXaxis().GetBinLowEdge(i) for i in range(1, nx + 2)] if False else None
    mean3d = mean.reshape(shape, order="C")
    std3d = std.reshape(shape, order="C")
    # reuse the CV hist binning
    fcv = ROOT.TFile.Open(args.cv); hcv = fcv.Get("hXSec3D")
    hm = hcv.Clone("hXSec3D_ensembleMean"); hm.Reset()
    hs = hcv.Clone("hSigma3D_ensembleSpread"); hs.Reset()
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                hm.SetBinContent(ix + 1, iy + 1, iz + 1, float(mean3d[ix, iy, iz]))
                hs.SetBinContent(ix + 1, iy + 1, iz + 1, float(std3d[ix, iy, iz]))
    out.cd(); hm.Write(); hs.Write()
    ROOT.TParameter("int")("n_trials", N).Write()
    out.Close(); fcv.Close()
    print(f"[wrote] {args.out}: hXSec3D_ensembleMean + hSigma3D_ensembleSpread (n_trials={N})")
    print("  -> use hXSec3D_ensembleMean as the NTRIAL ensemble central value; the spread "
          "is C_ML's diagonal (full cov in uq_cov_mlsplit_3d.root).")


if __name__ == "__main__":
    main()
