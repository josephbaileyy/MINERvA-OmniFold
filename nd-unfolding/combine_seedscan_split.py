#!/usr/bin/env python3
"""Combine train/test-split OmniFold runs -> ensemble-mean CV + ML-split covariance.

Reads the per-split res_split_*.npz (seedscan_split.py), computes:
  - the ensemble-mean cross section (the defensible central value, prepub item #2),
  - the ML-split covariance C_mlsplit over reported bins (CV>0), sample-cov over runs,
  - per-axis relative spread, and a comparison of sqrt(trace) to the existing
    seedscan ML cov (uq_cov_ml_3d.root:hCov_ml3d_reported) if given.
Writes uq_cov_mlsplit_3d.root (hCov_mlsplit3d_reported + hMean_* projections).

  python combine_seedscan_split.py --glob 'seedscan_split/res_split_*.npz' \
      --cv ../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root \
      --compare-ml ../3d-unfolding/uq_3d/uq_cov_ml_3d.root:hCov_ml3d_reported
"""
import argparse
import glob

import numpy as np
import ROOT
from replica_manifest import load_replica_manifest

ROOT.gROOT.SetBatch(True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="seedscan_split/res_split_*.npz")
    ap.add_argument("--cv", default="../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root",
                    help="frozen CV (TH3D hXSec3D) defining the reported-bin mask.")
    ap.add_argument("--compare-ml", default="",
                    help="existing ML cov 'path:hist' to compare sqrt-trace against.")
    ap.add_argument("--out", default="uq_cov_mlsplit_3d.root")
    ap.add_argument("--expected-ids", default="1-24",
                    help="required inclusive split id range LO-HI")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.glob))
    if not paths:
        raise SystemExit(f"[FAIL] no runs matched {args.glob}")
    lo, hi = (int(v) for v in args.expected_ids.split("-", 1))
    X, ids = load_replica_manifest(paths, set(range(lo, hi + 1)))
    totals = []
    for p in paths:
        with np.load(p, allow_pickle=False) as z:
            value = float(z["total_xsec"])
            if not np.isfinite(value):
                raise SystemExit(f"[FAIL] {p}: non-finite total_xsec")
            totals.append(value)
    print(f"[INFO] {len(paths)} split runs, full nbins={X.shape[1]}")
    print(f"[INFO] total xsec across runs: mean={np.mean(totals):.4e} "
          f"std={np.std(totals, ddof=1):.2e} ({100*np.std(totals,ddof=1)/np.mean(totals):.3f}%)")

    # reported mask from the frozen CV
    f = ROOT.TFile.Open(args.cv)
    h = f.Get("hXSec3D")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    cv = np.array([[[h.GetBinContent(ix, iy, iz) for iz in range(1, nz + 1)]
                    for iy in range(1, ny + 1)] for ix in range(1, nx + 1)])
    f.Close()
    rep = (cv > 0).ravel(order="C")
    if X.shape[1] != rep.size:
        raise SystemExit(f"[FAIL] run nbins {X.shape[1]} != CV nbins {rep.size}")
    Xr = X[:, rep]
    cv_rep = cv.ravel(order="C")[rep]
    mean = Xr.mean(axis=0)

    Z = Xr - mean
    cov = (Z.T @ Z) / (Xr.shape[0] - 1)     # unbiased sample cov = ML-split band
    diag = np.sqrt(np.maximum(np.diag(cov), 0))
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(cv_rep > 0, diag / cv_rep, 0)
    st = np.sqrt(max(np.trace(cov), 0))
    print(f"[ML-split cov] sqrt-trace={st:.3e}  median rel={100*np.median(rel):.3f}%  "
          f"max rel={100*np.max(rel):.3f}%")
    # ensemble-mean vs frozen CV (the headline-CV shift the ensemble mean implies)
    with np.errstate(divide="ignore", invalid="ignore"):
        shift = np.where(cv_rep > 0, (mean - cv_rep) / cv_rep, 0)
    print(f"[ensemble-mean vs frozen CV] median |shift|={100*np.median(np.abs(shift)):.3f}%  "
          f"max={100*np.max(np.abs(shift)):.3f}%")

    if args.compare_ml:
        cp, _, ch = args.compare_ml.partition(":")
        ch = ch or "hCov_ml3d_reported"
        cf = ROOT.TFile.Open(cp)
        chh = cf.Get(ch)
        if chh:
            n = chh.GetNbinsX()
            other = np.array([[chh.GetBinContent(i + 1, j + 1) for j in range(n)]
                              for i in range(n)])
            cf.Close()
            print(f"[compare] existing ML cov {ch}: sqrt-trace="
                  f"{np.sqrt(max(np.trace(other),0)):.3e}  "
                  f"(ML-split/ML sqrt-trace ratio = {st/np.sqrt(max(np.trace(other),0)):.2f})")
        else:
            print(f"[compare] hist {ch} not found in {cp}")

    out = ROOT.TFile.Open(args.out, "RECREATE")
    n = cov.shape[0]
    hc = ROOT.TH2D("hCov_mlsplit3d_reported", "ML train/test-split covariance (reported)",
                   n, 0, n, n, 0, n)
    for i in range(n):
        for j in range(n):
            hc.SetBinContent(i + 1, j + 1, float(cov[i, j]))
    hc.Write()
    out.Close()
    print(f"[wrote] {args.out}")


if __name__ == "__main__":
    main()
