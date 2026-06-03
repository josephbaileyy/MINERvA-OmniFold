#!/usr/bin/env python3
"""Build the 3D statistical covariance from the Poisson(1) bootstrap replicas.

The bootstrap band (`build_bootstrap_band_3d.py`) only stores per-axis std
histograms; the 3D systematic rollup (`analyze_universes_3d.py`) needs the stat
contribution as a FULL covariance on the same reported-bin flattening so the two
block-sum into the total error budget C_total = C_syst + C_stat (+ C_ML).

This reads the N bootstrap replicas' `hXSec3D` (each a joint data+MC Poisson(1)
draw, the 3D driver's --bootstrap-seed mode) and forms the sample covariance over
the reported bins (cv>0), using the IDENTICAL mask + C-order flatten that
analyze_universes_3d.py uses (same --cv file), so the matrices are bin-for-bin
aligned. Normalization is np.cov default (1/(N-1), unbiased), matching the 2D
analyze_uq.py convention.

Output (under --outdir, default uq_3d/):
  <out-root>  (default uq_cov_stat_3d.root) containing:
    hCov_stat3d_reported   TH2D  n_reported x n_reported  (block-sum partner)
    hSigma_stat3d_total    TH3D  per-bin sqrt(diag) over the full grid

Usage:
  python uq_3d/build_bootstrap_cov_3d.py \
      --cv xsec_3d_MEFHC_5iter_lgbm.root \
      --replicas 'uq_3d/xsec_3d_boot*.root' \
      --outdir uq_3d/ --out-root uq_cov_stat_3d.root
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)


def _axis_edges(ax):
    return np.array([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])


def load_xsec3d(path, want_edges=False):
    rf = ROOT.TFile.Open(path)
    if not rf or rf.IsZombie():
        sys.exit(f"[FAIL] cannot open {path}")
    h = rf.Get("hXSec3D")
    if not h:
        sys.exit(f"[FAIL] hXSec3D missing in {path}")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    a = np.zeros((nx, ny, nz))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            for iz in range(1, nz + 1):
                a[ix - 1, iy - 1, iz - 1] = h.GetBinContent(ix, iy, iz)
    edges = None
    if want_edges:
        edges = (_axis_edges(h.GetXaxis()), _axis_edges(h.GetYaxis()),
                 _axis_edges(h.GetZaxis()))
    rf.Close()
    return (a, edges) if want_edges else a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", default="xsec_3d_MEFHC_5iter_lgbm.root",
                    help="CV 3D unfold (defines reported-bin mask cv>0; must be "
                         "the SAME --cv passed to analyze_universes_3d.py).")
    ap.add_argument("--replicas", default="uq_3d/xsec_3d_boot*.root",
                    help="Glob for the replica ROOTs (hXSec3D each): bootstrap "
                         "replicas (statistical) or seedscan trials (ML).")
    ap.add_argument("--label", default="stat3d",
                    help="Covariance label -> hCov_<label>_reported / "
                         "hSigma_<label>_total. 'stat3d' (bootstrap, default) or "
                         "'ml3d' (seedscan GBDT stochasticity).")
    ap.add_argument("--outdir", default="uq_3d")
    ap.add_argument("--out-root", default="uq_cov_stat_3d.root")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    cv, (pt_e, pz_e, ea_e) = load_xsec3d(args.cv, want_edges=True)
    NX, NY, NZ = cv.shape
    reported_mask = cv > 0
    reported_flat = reported_mask.ravel(order="C")
    n_reported = int(reported_flat.sum())
    print(f"[INFO] CV {args.cv} shape={cv.shape}, n_reported={n_reported} "
          f"of {NX*NY*NZ}")

    files = sorted(glob.glob(args.replicas))
    if not files:
        sys.exit(f"[FAIL] no replicas matched {args.replicas}")

    rows = []
    skipped = 0
    for fn in files:
        rf = ROOT.TFile.Open(fn)
        if not rf or rf.IsZombie() or not rf.Get("hXSec3D"):
            skipped += 1
            if rf:
                rf.Close()
            continue
        rf.Close()
        a = load_xsec3d(fn).ravel(order="C")[reported_flat]
        if not np.all(np.isfinite(a)):
            skipped += 1
            continue
        rows.append(a)
    X = np.array(rows)  # (nrep, n_reported)
    nrep = X.shape[0]
    if nrep < 2:
        sys.exit(f"[FAIL] need >= 2 valid replicas, got {nrep} (skipped {skipped})")
    print(f"[INFO] {nrep} valid replicas (skipped {skipped})")

    # Sample covariance, np.cov default (1/(nrep-1)); rowvar over bins.
    cov = np.cov(X, rowvar=False)
    cov = np.atleast_2d(cov)

    diag = np.sqrt(np.maximum(np.diag(cov), 0))
    cv_rep = cv.ravel(order="C")[reported_flat]
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(cv_rep > 0, diag / cv_rep, 0)
    ev = np.linalg.eigvalsh(0.5 * (cov + cov.T))
    rank = int((ev > ev.max() * 1e-12).sum()) if ev.size else 0
    print(f"[{args.label} cov 3D] sqrt-trace = {np.sqrt(max(np.trace(cov), 0)):.3e}")
    print(f"              median rel = {100*np.median(rel):.3f}%, "
          f"p84 = {100*np.percentile(rel, 84):.3f}%, "
          f"max = {100*np.max(rel):.3f}%")
    print(f"              rank = {rank}/{n_reported}  "
          f"(<= nrep-1 = {nrep-1}; sample cov is rank-limited by replica count)")

    cov_name = f"hCov_{args.label}_reported"
    sig_name = f"hSigma_{args.label}_total"
    out_root = os.path.join(args.outdir, args.out_root)
    rf_out = ROOT.TFile.Open(out_root, "RECREATE")
    h = ROOT.TH2D(cov_name,
                  f"3D {args.label} covariance, reported bins",
                  n_reported, 0, n_reported, n_reported, 0, n_reported)
    for i in range(n_reported):
        for j in range(n_reported):
            h.SetBinContent(i + 1, j + 1, float(cov[i, j]))
    h.Write()

    full = np.zeros(NX * NY * NZ)
    full[reported_flat] = diag
    full3d = full.reshape(NX, NY, NZ, order="C")
    hs = ROOT.TH3D(sig_name,
                   f"3D {args.label} sqrt(diag) over reported bins",
                   NX, pt_e, NY, pz_e, NZ, ea_e)
    for ix in range(NX):
        for iy in range(NY):
            for iz in range(NZ):
                hs.SetBinContent(ix + 1, iy + 1, iz + 1, float(full3d[ix, iy, iz]))
    hs.Write()
    rf_out.Close()
    print(f"[wrote] {out_root}  ({cov_name} + {sig_name})")
    print(f"[INFO] block-sum into the systematic rollup with "
          f"analyze_universes_3d.py --bootstrap-cov {out_root}:{cov_name}")


if __name__ == "__main__":
    main()
