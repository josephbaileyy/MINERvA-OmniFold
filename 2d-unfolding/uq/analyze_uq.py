#!/usr/bin/env python3
"""Poisson-bootstrap covariance rollup for the 2D OmniFold UQ campaign.

Reads N replica ROOT files (2d_xsec_<DSET>_5iter_<EST>_boot{i}.root),
each containing hXSec2D (and hXSec_pt / hXSec_pz projections), and
computes:

  - per-bin mean and std across replicas (d^2sigma/dpT/dpz)
  - per-bin relative spread std/mean over the paper-reported bins
  - full 205x205 covariance over the paper-reported bins, with
    positive-definiteness check via Cholesky
  - 1D projection covariances (pT 14x14, pz 16x16)
  - total cross-section mean +/- std across replicas

Writes summary numbers to stdout and renders:
  - uq_spread_2d.png    per-bin rel-spread heatmap
  - uq_band_pt.png      pT projection with mean+std band
  - uq_band_pz.png      pz projection with mean+std band
  - uq_corr_2d.png      205x205 correlation matrix heatmap

Also writes a ROOT file uq_covariance.root with:
  - hMean2D, hStd2D, hRel2D (TH2D)
  - hCov2D_reported (TH2D, N_reported x N_reported)
"""

import argparse
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT


PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])


def th2_to_array(h):
    nx = h.GetNbinsX()
    ny = h.GetNbinsY()
    a = np.zeros((nx, ny))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            a[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
    return a


def th1_to_array(h):
    n = h.GetNbinsX()
    a = np.zeros(n)
    for i in range(1, n + 1):
        a[i - 1] = h.GetBinContent(i)
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob",
                    default="2d_xsec_*_boot*.root",
                    help="Glob for the N replica ROOT files.")
    ap.add_argument("--outdir", default=".",
                    help="Directory for png/root outputs.")
    ap.add_argument("--out-root", default="uq_covariance.root",
                    help="Output ROOT filename (under --outdir).")
    args = ap.parse_args()

    files = sorted(glob.glob(args.glob))
    if not files:
        sys.exit(f"[FAIL] no files matched {args.glob}")
    print(f"[INFO] {len(files)} replica files:")
    for f in files:
        print(f"  {f}")

    xsec2d = []
    xsec_pt = []
    xsec_pz = []
    for path in files:
        rf = ROOT.TFile.Open(path)
        if not rf or rf.IsZombie():
            sys.exit(f"[FAIL] could not open {path}")
        h2 = rf.Get("hXSec2D")
        hpt = rf.Get("hXSec_pt")
        hpz = rf.Get("hXSec_pz")
        if not h2 or not hpt or not hpz:
            sys.exit(f"[FAIL] missing hXSec hist(s) in {path}")
        xsec2d.append(th2_to_array(h2))
        xsec_pt.append(th1_to_array(hpt))
        xsec_pz.append(th1_to_array(hpz))
        rf.Close()

    X = np.stack(xsec2d, axis=0)        # (N, 14, 16)
    Xpt = np.stack(xsec_pt, axis=0)     # (N, 14)
    Xpz = np.stack(xsec_pz, axis=0)     # (N, 16)
    N, NX, NY = X.shape

    mean = X.mean(axis=0)
    std = X.std(axis=0, ddof=1) if N > 1 else np.zeros_like(mean)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(mean > 0, std / mean, np.nan)

    # Reporting set: bins with nonzero mean unfolded content (matches the
    # 205 paper-reported bins for the MEFHC pipeline). Flatten row-major
    # so the covariance index ordering is reproducible.
    reported = (mean > 0).ravel(order="C")
    n_reported = int(reported.sum())

    pt_w = np.diff(PT_EDGES)
    pz_w = np.diff(PZ_EDGES)
    dA = pt_w[:, None] * pz_w[None, :]            # (14, 16) bin area
    sigma_tot = (X * dA[None, :, :]).sum(axis=(1, 2))   # (N,)
    print()
    print("=== Total cross section across replicas ===")
    print(f"  mean = {sigma_tot.mean():.6e} cm^2/nucleon")
    if N > 1:
        print(f"  std  = {sigma_tot.std(ddof=1):.6e} cm^2/nucleon "
              f"({100 * sigma_tot.std(ddof=1) / sigma_tot.mean():.3f}% rel)")
    print(f"  min  = {sigma_tot.min():.6e}")
    print(f"  max  = {sigma_tot.max():.6e}")

    print()
    print(f"=== Per-bin relative spread (std/mean), "
          f"{n_reported} reported bins ===")
    rel_rep = rel.ravel(order="C")[reported]
    if N > 1:
        print(f"  median = {np.median(rel_rep) * 100:.3f}%")
        print(f"  p16    = {np.percentile(rel_rep, 16) * 100:.3f}%")
        print(f"  p84    = {np.percentile(rel_rep, 84) * 100:.3f}%")
        print(f"  max    = {np.max(rel_rep) * 100:.3f}%")

    # --- Covariance on the reported bins ---
    Xflat = X.reshape(N, NX * NY, order="C")          # (N, NX*NY)
    Xrep = Xflat[:, reported]                          # (N, n_reported)
    cov = np.cov(Xrep, rowvar=False) if N > 1 else np.zeros((n_reported, n_reported))
    with np.errstate(divide="ignore", invalid="ignore"):
        diag = np.sqrt(np.diag(cov))
        corr = cov / np.outer(diag, diag) if N > 1 else np.zeros_like(cov)
        corr = np.where(np.isfinite(corr), corr, 0.0)

    print()
    print(f"=== Covariance ({n_reported}x{n_reported}) ===")
    print(f"  trace = {np.trace(cov):.6e}")
    if N > 1:
        # Positive-definiteness via Cholesky. Add a tiny ridge if needed
        # to absorb numerical jitter at finite N (variance estimator is
        # only rank-(N-1) when N <= n_reported).
        try:
            np.linalg.cholesky(cov)
            print("  Cholesky: PASS (covariance is positive-definite)")
        except np.linalg.LinAlgError:
            jitter = 1e-12 * np.trace(cov) / max(n_reported, 1)
            try:
                np.linalg.cholesky(cov + jitter * np.eye(n_reported))
                print(f"  Cholesky: PASS with jitter={jitter:.3e} "
                      f"(rank-deficient at N={N} <= n_reported={n_reported}; "
                      "expected for small smoke replicas)")
            except np.linalg.LinAlgError:
                print("  Cholesky: FAIL (covariance not positive-definite)")
        if N <= n_reported:
            print(f"  [NOTE] N={N} <= n_reported={n_reported}: covariance is "
                  f"rank-deficient by construction; meaningful PD check "
                  f"requires N > n_reported (use eigenvalue threshold "
                  f"or pool replicas).")

    # --- 1D projection bands ---
    pt_mean = Xpt.mean(axis=0)
    pz_mean = Xpz.mean(axis=0)
    if N > 1:
        pt_std = Xpt.std(axis=0, ddof=1)
        pz_std = Xpz.std(axis=0, ddof=1)
        pt_cov = np.cov(Xpt, rowvar=False)
        pz_cov = np.cov(Xpz, rowvar=False)
    else:
        pt_std = np.zeros_like(pt_mean)
        pz_std = np.zeros_like(pz_mean)
        pt_cov = np.zeros((Xpt.shape[1], Xpt.shape[1]))
        pz_cov = np.zeros((Xpz.shape[1], Xpz.shape[1]))
    print()
    print(f"=== 1D projection spread ===")
    with np.errstate(divide="ignore", invalid="ignore"):
        print(f"  pT median rel spread = "
              f"{100 * np.median(np.where(pt_mean > 0, pt_std / pt_mean, 0)):.3f}%")
        print(f"  pz median rel spread = "
              f"{100 * np.median(np.where(pz_mean > 0, pz_std / pz_mean, 0)):.3f}%")

    # --- plots ---
    os.makedirs(args.outdir, exist_ok=True)

    # 2D rel-spread heatmap
    fig, ax = plt.subplots(figsize=(8, 6))
    Z = np.where(np.isfinite(rel), rel * 100, np.nan)
    vmax = min(20.0, np.nanmax(Z)) if np.isfinite(np.nanmax(Z)) else 5.0
    pc = ax.pcolormesh(PT_EDGES, PZ_EDGES, Z.T,
                       cmap="viridis", shading="flat",
                       vmin=0, vmax=vmax)
    cb = fig.colorbar(pc, ax=ax)
    cb.set_label("per-bin rel spread std/mean (%)")
    ax.set_xlabel(r"$p_T$ (GeV/c)")
    ax.set_ylabel(r"$p_{||}$ (GeV/c)")
    ax.set_title(f"Poisson bootstrap ({N} replicas): "
                 f"per-bin relative spread "
                 f"({n_reported} reported bins)")
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "uq_spread_2d.png"), dpi=140)
    plt.close(fig)

    # 1D pT band
    fig, ax = plt.subplots(figsize=(8, 5))
    pt_centers = 0.5 * (PT_EDGES[:-1] + PT_EDGES[1:])
    for i in range(N):
        ax.step(pt_centers, Xpt[i], where="mid", color="gray", alpha=0.5, lw=0.7)
    ax.errorbar(pt_centers, pt_mean, yerr=pt_std,
                fmt="o", ms=4, color="tab:red",
                label=f"mean +- std ({N} replicas)")
    ax.set_xlabel(r"$p_T$ (GeV/c)")
    ax.set_ylabel(r"d$\sigma$/d$p_T$ (cm$^2$/(GeV/c)/nucleon)")
    ax.set_title(f"Poisson bootstrap ({N} replicas): $p_T$ projection")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "uq_band_pt.png"), dpi=140)
    plt.close(fig)

    # 1D pz band
    fig, ax = plt.subplots(figsize=(8, 5))
    pz_centers = 0.5 * (PZ_EDGES[:-1] + PZ_EDGES[1:])
    for i in range(N):
        ax.step(pz_centers, Xpz[i], where="mid", color="gray", alpha=0.5, lw=0.7)
    ax.errorbar(pz_centers, pz_mean, yerr=pz_std,
                fmt="o", ms=4, color="tab:red",
                label=f"mean +- std ({N} replicas)")
    ax.set_xlabel(r"$p_{||}$ (GeV/c)")
    ax.set_ylabel(r"d$\sigma$/d$p_{||}$ (cm$^2$/(GeV/c)/nucleon)")
    ax.set_title(f"Poisson bootstrap ({N} replicas): $p_{{||}}$ projection")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "uq_band_pz.png"), dpi=140)
    plt.close(fig)

    # Correlation matrix heatmap
    if N > 1 and n_reported > 0:
        fig, ax = plt.subplots(figsize=(7, 6))
        pc = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1,
                       origin="lower", aspect="equal")
        cb = fig.colorbar(pc, ax=ax)
        cb.set_label("correlation")
        ax.set_xlabel("reported-bin index (row-major pT,pz)")
        ax.set_ylabel("reported-bin index")
        ax.set_title(f"Poisson bootstrap correlation "
                     f"({n_reported} bins, {N} replicas)")
        fig.tight_layout()
        fig.savefig(os.path.join(args.outdir, "uq_corr_2d.png"), dpi=140)
        plt.close(fig)

    # --- ROOT output: mean/std/rel TH2D, plus reported-bin covariance ---
    out_root = os.path.join(args.outdir, args.out_root)
    rf_out = ROOT.TFile.Open(out_root, "RECREATE")

    def make_th2d(name, title, arr):
        h = ROOT.TH2D(name, title,
                      len(PT_EDGES) - 1, PT_EDGES,
                      len(PZ_EDGES) - 1, PZ_EDGES)
        for ix in range(arr.shape[0]):
            for iy in range(arr.shape[1]):
                v = arr[ix, iy]
                if np.isfinite(v):
                    h.SetBinContent(ix + 1, iy + 1, float(v))
        return h

    hMean = make_th2d("hMean2D", "Poisson-bootstrap mean", mean)
    hStd = make_th2d("hStd2D", "Poisson-bootstrap stddev", std)
    hRel = make_th2d("hRel2D",
                     "Poisson-bootstrap rel spread (std/mean)",
                     np.where(np.isfinite(rel), rel, 0.0))
    hMean.Write()
    hStd.Write()
    hRel.Write()

    if n_reported > 0:
        hCov = ROOT.TH2D("hCov2D_reported",
                         "Poisson-bootstrap covariance over reported bins",
                         n_reported, 0, n_reported,
                         n_reported, 0, n_reported)
        for i in range(n_reported):
            for j in range(n_reported):
                hCov.SetBinContent(i + 1, j + 1, float(cov[i, j]))
        hCov.Write()
    rf_out.Close()
    print()
    print(f"[wrote] {os.path.join(args.outdir, 'uq_spread_2d.png')}")
    print(f"[wrote] {os.path.join(args.outdir, 'uq_band_pt.png')}")
    print(f"[wrote] {os.path.join(args.outdir, 'uq_band_pz.png')}")
    if N > 1 and n_reported > 0:
        print(f"[wrote] {os.path.join(args.outdir, 'uq_corr_2d.png')}")
    print(f"[wrote] {out_root}")


if __name__ == "__main__":
    main()
