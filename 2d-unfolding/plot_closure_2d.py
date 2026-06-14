#!/usr/bin/env python3
"""Closure diagnostic plots for 2D OmniFold (playlist 1A).

Reads 2d_crossSection_omnifold_5iter_closure.root and produces:
  - closure_2d_ratio_heatmap.png : per-bin hUnfold / hTruth
  - closure_2d_projection_pt.png : 1D p_T projection, unfolded vs truth (ratio panel)
  - closure_2d_projection_pz.png : 1D p_|| projection, unfolded vs truth (ratio panel)
  - closure_2d_ratio_hist.png    : histogram of per-bin ratios
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, TwoSlopeNorm
import ROOT


def h2_to_arrays(h):
    nx = h.GetNbinsX()
    ny = h.GetNbinsY()
    xedges = np.array([h.GetXaxis().GetBinLowEdge(i) for i in range(1, nx + 2)])
    yedges = np.array([h.GetYaxis().GetBinLowEdge(i) for i in range(1, ny + 2)])
    vals = np.array([[h.GetBinContent(i, j) for j in range(1, ny + 1)]
                     for i in range(1, nx + 1)])
    return xedges, yedges, vals


def h1_to_arrays(h):
    n = h.GetNbinsX()
    edges = np.array([h.GetXaxis().GetBinLowEdge(i) for i in range(1, n + 2)])
    vals = np.array([h.GetBinContent(i) for i in range(1, n + 1)])
    errs = np.array([h.GetBinError(i) for i in range(1, n + 1)])
    return edges, vals, errs


def step_plot(ax, edges, vals, **kw):
    ax.stairs(vals, edges, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile",
                    default="2d_crossSection_omnifold_5iter_closure.root")
    ap.add_argument("--prefix", default="closure_2d")
    args = ap.parse_args()

    f = ROOT.TFile.Open(args.infile)
    hU = f.Get("hUnfold2D")
    hT = f.Get("hTruth2D")
    pot_scale = f.Get("potScale").GetVal()
    niter = int(f.Get("nIterations").GetVal())

    print(f"pot_scale = {pot_scale:.6f}  (1/pot_scale = {1/pot_scale:.4f})")
    print(f"nIterations = {niter}")

    xedges, yedges, U = h2_to_arrays(hU)
    _, _, T = h2_to_arrays(hT)

    # Closure observable: hUnfold / hTruth.
    # Both histograms are filled with pot-scaled w_truth in
    # unfold_2d_omnifold_unbinned.py, so they sit at data POT and ratio
    # directly. (Pre-fix the ratio had a pot_scale factor to compensate
    # for a buggy hUnfold2D that was ~1/pot_scale too large; the fix
    # removed that bug, so no correction is needed here now.)
    T_scaled = T
    with np.errstate(divide="ignore", invalid="ignore"):
        R = np.where(T_scaled > 0, U / T_scaled, np.nan)

    # 1) ratio heatmap
    fig, ax = plt.subplots(figsize=(9, 6))
    norm = TwoSlopeNorm(vmin=0.5, vcenter=1.0, vmax=2.0)
    pm = ax.pcolormesh(xedges, yedges, R.T, cmap="RdBu_r", norm=norm,
                       shading="flat")
    cbar = fig.colorbar(pm, ax=ax, extend="both")
    cbar.set_label(r"$N_{\rm unfold} / N_{\rm truth}$")
    ax.set_xlabel(r"$p_T$ (GeV/c)")
    ax.set_ylabel(r"$p_{||}$ (GeV/c)")
    ax.set_title(f"2D closure: per-bin unfolded/truth ratio ({niter} iter, 1A)")
    # annotate bins
    xcen = 0.5 * (xedges[:-1] + xedges[1:])
    ycen = 0.5 * (yedges[:-1] + yedges[1:])
    for i, xc in enumerate(xcen):
        for j, yc in enumerate(ycen):
            if np.isnan(R[i, j]):
                continue
            txt = f"{R[i, j]:.2f}"
            ax.text(xc, yc, txt, ha="center", va="center", fontsize=5,
                    color="black")
    fig.tight_layout()
    out = f"{args.prefix}_ratio_heatmap.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")
    plt.close(fig)

    # 2) 1D projections (p_T and p_||)
    for axis, label, edges in [("x", r"$p_T$ (GeV/c)", xedges),
                                ("y", r"$p_{||}$ (GeV/c)", yedges)]:
        if axis == "x":
            U1 = U.sum(axis=1)
            T1 = T_scaled.sum(axis=1)
        else:
            U1 = U.sum(axis=0)
            T1 = T_scaled.sum(axis=0)
        # avoid div by zero
        ratio = np.where(T1 > 0, U1 / T1, np.nan)

        fig, (a0, a1) = plt.subplots(2, 1, figsize=(8, 6), sharex=True,
                                      gridspec_kw={"height_ratios": [3, 1]})
        step_plot(a0, edges, T1, color="C3", linewidth=2,
                  label="MC truth")
        step_plot(a0, edges, U1, color="k", linewidth=2,
                  label="OmniFold unfolded")
        a0.set_ylabel("Events / bin")
        a0.set_yscale("log")
        a0.legend(loc="best", fontsize=9)
        a0.set_title(f"Closure {axis}-projection "
                     f"({niter} iter, playlist 1A)")
        a0.grid(alpha=0.3)

        step_plot(a1, edges, ratio, color="k", linewidth=1.5)
        a1.axhline(1.0, color="C3", linestyle="--", linewidth=1)
        a1.set_ylim(0.8, 1.3)
        a1.set_xlabel(label)
        a1.set_ylabel("Unfold / Truth")
        a1.grid(alpha=0.3)

        fig.tight_layout()
        suffix = "pt" if axis == "x" else "pz"
        out = f"{args.prefix}_projection_{suffix}.png"
        fig.savefig(out, dpi=150)
        print(f"wrote {out}")
        plt.close(fig)

    # 3) ratio distribution
    vals = R[~np.isnan(R)].flatten()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(vals, bins=np.linspace(0.5, 2.5, 41), color="C0", alpha=0.75,
            edgecolor="k")
    ax.axvline(1.0, color="C3", linewidth=2,
               label=f"median = {np.median(vals):.3f}")
    ax.axvline(np.median(vals), color="C2", linestyle="--", linewidth=1.5)
    ax.set_xlabel(r"per-bin $N_{\rm unfold}/(N_{\rm truth}/\mathrm{pot\_scale})$")
    ax.set_ylabel("# bins")
    ax.set_title(f"Closure ratio distribution (N={len(vals)} bins, "
                 f"{niter} iter)")
    ax.grid(alpha=0.3)
    # summary text box
    within5 = int(np.sum(np.abs(vals - 1) < 0.05))
    within10 = int(np.sum(np.abs(vals - 1) < 0.10))
    within20 = int(np.sum(np.abs(vals - 1) < 0.20))
    stats = (f"mean   = {vals.mean():.3f}\n"
             f"median = {np.median(vals):.3f}\n"
             f"std    = {vals.std():.3f}\n"
             f"|r-1|<5%  : {within5}/{len(vals)}\n"
             f"|r-1|<10% : {within10}/{len(vals)}\n"
             f"|r-1|<20% : {within20}/{len(vals)}")
    ax.text(0.98, 0.98, stats, transform=ax.transAxes, ha="right", va="top",
            family="monospace", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))
    ax.legend(loc="upper left")
    fig.tight_layout()
    out = f"{args.prefix}_ratio_hist.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")
    plt.close(fig)

    f.Close()


if __name__ == "__main__":
    main()
