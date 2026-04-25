#!/usr/bin/env python3
"""Paper-Fig.-13-style comparison of 2D OmniFold cross section vs MC truth.

Reproduces the visual format of arXiv:2106.16210 Fig. 13:
  - 4x4 panel grid of p_T slices (each panel: d^2 sigma vs p_||)
  - 4x4 panel grid of p_|| slices (each panel: d^2 sigma vs p_T)
  - Each panel scaled so max value ~1, scale factor annotated
  - Per-panel chi^2/ndf (statistical only) annotated
  - Global chi^2/ndf shown in figure title

Takes the OmniFold output ROOT file; compares hXSec2D to hXSecTruth2D
(MC truth passed through the same flux / nucleon / efficiency
normalization as the unfolded result, so differences come only from
the data vs MC prior).
"""
import argparse
import os

import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_2d_cross_section import (PT_EDGES, PZ_EDGES, th2_to_slices,
                                    compute_truth_xsec_2d,
                                    load_flux_bins_for_truth)


def panel_arrays(h):
    n = h.GetNbinsX()
    centers = np.array([h.GetBinCenter(i) for i in range(1, n + 1)])
    widths = np.array([h.GetBinWidth(i) for i in range(1, n + 1)])
    edges = np.array([h.GetXaxis().GetBinLowEdge(i) for i in range(1, n + 2)])
    vals = np.array([h.GetBinContent(i) for i in range(1, n + 1)])
    errs = np.array([h.GetBinError(i) for i in range(1, n + 1)])
    return centers, widths, edges, vals, errs


def panel_chi2(vals, errs, truth):
    """Return (chi2, ndf) for bins with positive truth and positive err."""
    mask = (truth > 0) & (errs > 0)
    if not np.any(mask):
        return 0.0, 0
    d = vals[mask] - truth[mask]
    e = errs[mask]
    return float(np.sum((d / e) ** 2)), int(mask.sum())


def draw_grid(xsec_slices, truth_slices, axis_label, out, suptitle,
              nrows=4, ncols=4):
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.3 * nrows),
                              squeeze=False)
    fig.subplots_adjust(hspace=0.38, wspace=0.30)

    total_chi2 = 0.0
    total_ndf = 0

    for idx in range(nrows * ncols):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        if idx >= len(xsec_slices):
            ax.set_visible(False)
            continue
        label, h_xsec = xsec_slices[idx]
        _, h_truth = truth_slices[idx]

        centers, widths, edges, vals, errs = panel_arrays(h_xsec)
        _, _, _, truth, _ = panel_arrays(h_truth)

        chi2, ndf = panel_chi2(vals, errs, truth)
        total_chi2 += chi2
        total_ndf += ndf

        # Per-panel scale: normalize to max so all panels fit 0..1.4
        mx = max(np.nanmax(vals) if vals.size else 0.0,
                 np.nanmax(truth) if truth.size else 0.0)
        scale = 1.0 / mx if mx > 0 else 1.0
        # Format scale factor as "x 10^n" or similar
        if mx > 0:
            exp = int(np.floor(np.log10(mx)))
            scale_str = rf"$\times 10^{{{-exp}}}$"
        else:
            scale_str = ""

        ax.errorbar(centers, vals * scale, yerr=errs * scale,
                    xerr=widths / 2, fmt="ko", markersize=2.5,
                    linewidth=0.9, capsize=1.5, label="OmniFold", zorder=3)
        ax.stairs(truth * scale, edges, color="C3", linewidth=1.2,
                  label="MINERvA Tune v1 (MC truth)", zorder=2)

        ax.set_xlim(edges[0], edges[-1])
        ax.set_ylim(0, 1.4)
        ax.set_title(label, fontsize=8, pad=3)
        ax.tick_params(labelsize=7)

        # Annotate scale factor and chi2
        note = scale_str
        if ndf > 0:
            note = f"{scale_str}\n" + rf"$\chi^2/n={chi2:.1f}/{ndf}$"
        ax.text(0.97, 0.97, note, transform=ax.transAxes,
                ha="right", va="top", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.8))

        if r == nrows - 1:
            ax.set_xlabel(axis_label, fontsize=8)
        if c == 0:
            ax.set_ylabel("scaled $d^{2}\\sigma/(dp_{T}\\,dp_{||})$",
                          fontsize=7)

    axes[0][0].legend(fontsize=7, loc="lower right")
    total_line = ""
    if total_ndf > 0:
        total_line = (rf"   |   total stat $\chi^2/n = "
                      rf"{total_chi2:.1f}/{total_ndf} = "
                      rf"{total_chi2/total_ndf:.2f}$")
    fig.suptitle(suptitle + total_line, fontsize=11, y=0.995)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}  (chi2/ndf = "
          f"{total_chi2:.1f}/{total_ndf})")
    return total_chi2, total_ndf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile",
                    default="2d_crossSection_omnifold_MEHFC_5iter.root")
    ap.add_argument("--prefix", default="2d_paper_compare_MEHFC_5iter")
    ap.add_argument("--mcfile", default=None,
                    help="Fallback ROOT file for flux histogram when infile lacks hFlux_pt")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated",
                    help="Histogram name inside --mcfile for fallback flux loading")
    args = ap.parse_args()

    f = ROOT.TFile.Open(args.infile, "READ")
    hXSec2D = f.Get("hXSec2D")
    hTruth2D = f.Get("hTruth2D")
    hEff2D = f.Get("hEff2D")
    for h in [hXSec2D, hTruth2D, hEff2D]:
        h.SetDirectory(0)
    data_pot = float(f.Get("dataPOT").GetVal())
    n_nucleons = float(f.Get("nNucleons").GetVal())
    niter = int(f.Get("nIterations").GetVal())

    flux_bins, flux_source = load_flux_bins_for_truth(
        f, args.infile, args.mcfile, args.flux_hist)
    f.Close()
    print(f"[INFO] Truth-normalization flux source: {flux_source}")

    # Truth cross section (same normalization as hXSec2D)
    hXSecTruth2D = compute_truth_xsec_2d(hTruth2D, hEff2D, flux_bins,
                                          data_pot, n_nucleons)
    hXSecTruth2D.SetDirectory(0)

    # p_T slices (each panel is p_|| distribution for fixed p_T)
    xsec_pt = th2_to_slices(hXSec2D, "pt")
    truth_pt = th2_to_slices(hXSecTruth2D, "pt")
    c2_pt, n_pt = draw_grid(
        xsec_pt, truth_pt,
        axis_label=r"$p_{||}$ (GeV/c)",
        out=f"{args.prefix}_pt_slices.png",
        suptitle=(f"arXiv:2106.16210 Fig.13-style: slices in $p_T$ "
                  f"({niter} iter)"))

    # p_|| slices (each panel is p_T distribution for fixed p_||)
    xsec_pz = th2_to_slices(hXSec2D, "pz")
    truth_pz = th2_to_slices(hXSecTruth2D, "pz")
    c2_pz, n_pz = draw_grid(
        xsec_pz, truth_pz,
        axis_label=r"$p_T$ (GeV/c)",
        out=f"{args.prefix}_pz_slices.png",
        suptitle=(f"arXiv:2106.16210 Fig.13-style: slices in $p_{{||}}$ "
                  f"({niter} iter)"))

    # Summary
    print()
    print("=" * 60)
    print("Paper Fig. 13 comparison summary (statistical errors only)")
    print("=" * 60)
    print(f"input file: {args.infile}")
    print(f"nIterations = {niter}")
    print(f"p_T slices total chi2/ndf  = {c2_pt:.1f}/{n_pt}  "
          f"= {c2_pt/n_pt if n_pt else 0:.2f}")
    print(f"p_|| slices total chi2/ndf = {c2_pz:.1f}/{n_pz}  "
          f"= {c2_pz/n_pz if n_pz else 0:.2f}")
    print("NOTE: statistical-only chi2; paper uses full covariance.")


if __name__ == "__main__":
    main()
