#!/usr/bin/env python3
"""ML-stochasticity spread analysis for the MEFHC 5-iter seed scan.

Reads N trial ROOT files (2d_crossSection_omnifold_MEFHC_5iter_seed{i}.root),
each containing hXSec2D (and hXSec_pt / hXSec_pz projections), and computes:

  - per-bin mean and std across trials (d^2sigma/dpT/dpz)
  - per-bin relative spread std/mean over the 205 paper-reported bins
  - shape-only spread (each trial renormalized to its own total)
  - total cross-section mean +/- std across trials

Writes summary numbers to stdout and renders:
  - seedscan_spread_2d.png  (14x16 relative-spread heatmap)
  - seedscan_band_pt.png    (1D pT projection: mean band + per-trial lines)
  - seedscan_band_pz.png    (1D pz projection: mean band + per-trial lines)
"""


import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

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
    e = np.zeros((nx, ny))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            a[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
            e[ix - 1, iy - 1] = h.GetBinError(ix, iy)
    return a, e


def th1_to_array(h):
    n = h.GetNbinsX()
    a = np.zeros(n)
    e = np.zeros(n)
    for i in range(1, n + 1):
        a[i - 1] = h.GetBinContent(i)
        e[i - 1] = h.GetBinError(i)
    return a, e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob",
                    default="2d_crossSection_omnifold_MEFHC_5iter_seed*.root",
                    help="Glob for the N trial ROOT files.")
    ap.add_argument("--outdir", default=".",
                    help="Directory for png outputs.")
    args = ap.parse_args()

    files = sorted(glob.glob(args.glob))
    if not files:
        sys.exit(f"[FAIL] no files matched {args.glob}")
    print(f"[INFO] {len(files)} trial files:")
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
        a2, _ = th2_to_array(h2)
        apt, _ = th1_to_array(hpt)
        apz, _ = th1_to_array(hpz)
        xsec2d.append(a2)
        xsec_pt.append(apt)
        xsec_pz.append(apz)
        rf.Close()

    X = np.stack(xsec2d, axis=0)        # (N, 14, 16) in cm^2/(GeV/c)^2/nucleon
    Xpt = np.stack(xsec_pt, axis=0)     # (N, 14)
    Xpz = np.stack(xsec_pz, axis=0)     # (N, 16)
    N = X.shape[0]

    mean = X.mean(axis=0)
    std = X.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(mean > 0, std / mean, np.nan)

    # Reporting set: the 205 paper-reported bins are exactly the bins
    # with mean > 0 in our unfolded output (the 19 paper-unreported bins
    # also have OmniFold output = 0 because the truth gate suppresses
    # them at training).
    reported = mean > 0

    pt_w = np.diff(PT_EDGES)
    pz_w = np.diff(PZ_EDGES)
    dA = pt_w[:, None] * pz_w[None, :]            # (14, 16) bin area in (GeV/c)^2

    # Per-trial total cross section sigma_tot = sum_ij d2sigma/dpTdpz * dA.
    sigma_tot = (X * dA[None, :, :]).sum(axis=(1, 2))   # (N,)
    print()
    print("=== Total cross section across trials ===")
    print(f"  mean = {sigma_tot.mean():.6e} cm^2/nucleon")
    print(f"  std  = {sigma_tot.std(ddof=1):.6e} cm^2/nucleon "
          f"({100 * sigma_tot.std(ddof=1) / sigma_tot.mean():.3f}% rel)")
    print(f"  min  = {sigma_tot.min():.6e}")
    print(f"  max  = {sigma_tot.max():.6e}")

    print()
    print(f"=== Per-bin relative spread (std/mean), "
          f"{reported.sum()} paper-reported bins ===")
    rel_rep = rel[reported]
    print(f"  median = {np.median(rel_rep) * 100:.3f}%")
    print(f"  p16    = {np.percentile(rel_rep, 16) * 100:.3f}%")
    print(f"  p84    = {np.percentile(rel_rep, 84) * 100:.3f}%")
    print(f"  max    = {np.max(rel_rep) * 100:.3f}%")

    # Shape-only spread: renormalize each trial to its own sigma_tot.
    X_shape = X / sigma_tot[:, None, None]
    shape_mean = X_shape.mean(axis=0)
    shape_std = X_shape.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        shape_rel = np.where(shape_mean > 0, shape_std / shape_mean, np.nan)
    print()
    print(f"=== Shape-only relative spread (after dividing by per-trial "
          f"sigma_tot), {reported.sum()} paper-reported bins ===")
    sh = shape_rel[reported]
    print(f"  median = {np.median(sh) * 100:.3f}%")
    print(f"  p84    = {np.percentile(sh, 84) * 100:.3f}%")
    print(f"  max    = {np.max(sh) * 100:.3f}%")

    # 1D projection bands.
    pt_mean = Xpt.mean(axis=0)
    pt_std = Xpt.std(axis=0, ddof=1)
    pz_mean = Xpz.mean(axis=0)
    pz_std = Xpz.std(axis=0, ddof=1)
    print()
    print(f"=== 1D projection spread ===")
    print(f"  pT median rel spread = "
          f"{100 * np.median(pt_std / pt_mean):.3f}%")
    print(f"  pz median rel spread = "
          f"{100 * np.median(pz_std / pz_mean):.3f}%")

    # --- plots ---
    os.makedirs(args.outdir, exist_ok=True)

    # 2D rel-spread heatmap (only show finite cells, mask the rest).
    fig, ax = plt.subplots(figsize=(8, 6))
    Z = np.where(np.isfinite(rel), rel * 100, np.nan)
    pc = ax.pcolormesh(PT_EDGES, PZ_EDGES, Z.T,
                       cmap="viridis", shading="flat",
                       vmin=0, vmax=min(5.0, np.nanmax(Z)))
    cb = fig.colorbar(pc, ax=ax)
    cb.set_label("per-bin rel spread std/mean (%)")
    ax.set_xlabel(r"$p_T$ (GeV/c)")
    ax.set_ylabel(r"$p_{||}$ (GeV/c)")
    ax.set_title(f"MEFHC 5-iter seed scan ({N} trials): "
                 f"ML-stochasticity relative spread per bin "
                 f"({int(reported.sum())} reported bins)")
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "seedscan_spread_2d.png"), dpi=140)
    plt.close(fig)

    # 1D pT band.
    fig, ax = plt.subplots(figsize=(8, 5))
    pt_centers = 0.5 * (PT_EDGES[:-1] + PT_EDGES[1:])
    for i in range(N):
        ax.step(pt_centers, Xpt[i], where="mid", color="gray", alpha=0.5, lw=0.7)
    ax.errorbar(pt_centers, pt_mean, yerr=pt_std,
                fmt="o", ms=4, color="tab:red",
                label=f"mean +- std ({N} trials)")
    ax.set_xlabel(r"$p_T$ (GeV/c)")
    ax.set_ylabel(r"d$\sigma$/d$p_T$ (cm$^2$/(GeV/c)/nucleon)")
    ax.set_title(f"MEFHC 5-iter seed scan: $p_T$ projection")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "seedscan_band_pt.png"), dpi=140)
    plt.close(fig)

    # 1D pz band.
    fig, ax = plt.subplots(figsize=(8, 5))
    pz_centers = 0.5 * (PZ_EDGES[:-1] + PZ_EDGES[1:])
    for i in range(N):
        ax.step(pz_centers, Xpz[i], where="mid", color="gray", alpha=0.5, lw=0.7)
    ax.errorbar(pz_centers, pz_mean, yerr=pz_std,
                fmt="o", ms=4, color="tab:red",
                label=f"mean +- std ({N} trials)")
    ax.set_xlabel(r"$p_{||}$ (GeV/c)")
    ax.set_ylabel(r"d$\sigma$/d$p_{||}$ (cm$^2$/(GeV/c)/nucleon)")
    ax.set_title(f"MEFHC 5-iter seed scan: $p_{{||}}$ projection")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "seedscan_band_pz.png"), dpi=140)
    plt.close(fig)

    print()
    print(f"[wrote] {os.path.join(args.outdir, 'seedscan_spread_2d.png')}")
    print(f"[wrote] {os.path.join(args.outdir, 'seedscan_band_pt.png')}")
    print(f"[wrote] {os.path.join(args.outdir, 'seedscan_band_pz.png')}")


if __name__ == "__main__":
    main()
