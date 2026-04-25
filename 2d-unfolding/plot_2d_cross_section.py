#!/usr/bin/env python3
"""
Plot double-differential cross section d^2 sigma / (dp_T dp_||) from
2D OmniFold unfolding, matching the panel layout of arXiv:2106.16210 Fig. 13.

Reads the output of unfold_2d_omnifold_unbinned.py.

Created: 2026-04-17
"""

import argparse
import math
import os
from array import array

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)


# Paper binning
PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]

N_PT = len(PT_EDGES) - 1  # 14
N_PZ = len(PZ_EDGES) - 1  # 16


def th2_to_slices(h2d, axis):
    """Extract 1D slices from a TH2D along one axis.

    axis="pt": for each p_T bin, extract the p_|| distribution
    axis="pz": for each p_|| bin, extract the p_T distribution
    Returns list of (label, TH1D) tuples.
    """
    slices = []
    if axis == "pt":
        for ix in range(1, h2d.GetNbinsX() + 1):
            lo = h2d.GetXaxis().GetBinLowEdge(ix)
            hi = h2d.GetXaxis().GetBinUpEdge(ix)
            label = f"{lo:.2f} < p_T < {hi:.2f}"
            proj = h2d.ProjectionY(f"slice_pt_{ix}", ix, ix, "e")
            proj.SetDirectory(0)
            slices.append((label, proj))
    elif axis == "pz":
        for iy in range(1, h2d.GetNbinsY() + 1):
            lo = h2d.GetYaxis().GetBinLowEdge(iy)
            hi = h2d.GetYaxis().GetBinUpEdge(iy)
            label = f"{lo:.1f} < p_|| < {hi:.1f}"
            proj = h2d.ProjectionX(f"slice_pz_{iy}", iy, iy, "e")
            proj.SetDirectory(0)
            slices.append((label, proj))
    return slices


def plot_panel_grid(xsec_slices, truth_slices, nrows, ncols, xlabel, ylabel,
                     outname, title_prefix=""):
    """Draw a grid of panels, each showing one slice."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.5 * nrows),
                              squeeze=False)
    fig.subplots_adjust(hspace=0.35, wspace=0.30)

    for idx in range(nrows * ncols):
        row, col = divmod(idx, ncols)
        ax = axes[row][col]

        if idx >= len(xsec_slices):
            ax.set_visible(False)
            continue

        label, h_xsec = xsec_slices[idx]
        _, h_truth = truth_slices[idx]

        # Extract arrays from ROOT histograms
        nbins = h_xsec.GetNbinsX()
        centers = [h_xsec.GetBinCenter(i) for i in range(1, nbins + 1)]
        widths = [h_xsec.GetBinWidth(i) / 2 for i in range(1, nbins + 1)]
        vals = [h_xsec.GetBinContent(i) for i in range(1, nbins + 1)]
        errs = [h_xsec.GetBinError(i) for i in range(1, nbins + 1)]

        truth_vals = [h_truth.GetBinContent(i) for i in range(1, nbins + 1)]

        # Determine scale factor for display
        max_val = max(max(vals) if vals else 1, max(truth_vals) if truth_vals else 1)
        if max_val <= 0:
            max_val = 1

        ax.errorbar(centers, vals, yerr=errs, xerr=widths,
                     fmt='ko', markersize=2, linewidth=0.8, capsize=1.5,
                     label="OmniFold", zorder=3)

        # Truth / MC prediction as step histogram
        edges = [h_truth.GetXaxis().GetBinLowEdge(i) for i in range(1, nbins + 2)]
        ax.stairs(truth_vals, edges, color='red', linewidth=1.0,
                  label="MC truth", zorder=2)

        ax.set_title(label, fontsize=8, pad=3)
        ax.tick_params(labelsize=7)
        ax.set_xlim(edges[0], edges[-1])

        ymax = max_val * 1.4
        ax.set_ylim(0, ymax if ymax > 0 else 1)

        if row == nrows - 1:
            ax.set_xlabel(xlabel, fontsize=8)
        if col == 0:
            ax.set_ylabel(ylabel, fontsize=7)

    # Legend in first panel
    if len(xsec_slices) > 0:
        axes[0][0].legend(fontsize=6, loc="upper right")

    fig.suptitle(title_prefix, fontsize=10, y=0.99)
    fig.savefig(outname, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved {outname}")


def plot_1d_projection(h_xsec, h_truth, xlabel, ylabel, outname, title=""):
    """Plot a single 1D cross-section projection with ratio panel."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(7, 6),
                                          gridspec_kw={"height_ratios": [3, 1]},
                                          sharex=True)
    fig.subplots_adjust(hspace=0.05)

    nbins = h_xsec.GetNbinsX()
    centers = [h_xsec.GetBinCenter(i) for i in range(1, nbins + 1)]
    widths = [h_xsec.GetBinWidth(i) / 2 for i in range(1, nbins + 1)]
    vals = [h_xsec.GetBinContent(i) for i in range(1, nbins + 1)]
    errs = [h_xsec.GetBinError(i) for i in range(1, nbins + 1)]
    truth = [h_truth.GetBinContent(i) for i in range(1, nbins + 1)]
    edges = [h_xsec.GetXaxis().GetBinLowEdge(i) for i in range(1, nbins + 2)]

    ax_top.errorbar(centers, vals, yerr=errs, xerr=widths,
                     fmt='ko', markersize=4, linewidth=1, capsize=2,
                     label="OmniFold")
    ax_top.stairs(truth, edges, color='red', linewidth=1.2, label="MC truth")
    ax_top.set_ylabel(ylabel, fontsize=10)
    ax_top.legend(fontsize=9)
    ax_top.set_title(title, fontsize=11)
    ax_top.set_ylim(bottom=0)

    # Ratio
    ratios = []
    ratio_errs = []
    for v, e, t in zip(vals, errs, truth):
        if t > 0:
            ratios.append(v / t)
            ratio_errs.append(e / t)
        else:
            ratios.append(0)
            ratio_errs.append(0)

    ax_bot.errorbar(centers, ratios, yerr=ratio_errs, xerr=widths,
                     fmt='ko', markersize=4, linewidth=1, capsize=2)
    ax_bot.axhline(1.0, color='red', linewidth=1, linestyle='--')
    ax_bot.set_xlabel(xlabel, fontsize=10)
    ax_bot.set_ylabel("Data / MC", fontsize=10)
    ax_bot.set_ylim(0.7, 1.3)
    ax_bot.set_xlim(edges[0], edges[-1])

    fig.savefig(outname, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved {outname}")


def compute_truth_xsec_2d(hTruth2D, hEff2D, flux_bins, data_pot, n_nucleons):
    """Convert MC truth counts to cross section for comparison.

    `hTruth2D` is already a truth-space signal spectrum, so this uses the same
    post-efficiency normalization as the production `extract_cross_section_2d()`.
    """
    del hEff2D  # Retained for compatibility with existing callers.
    hXSec = hTruth2D.Clone("hXSecTruth2D")
    hXSec.Reset("ICES")
    nx = hTruth2D.GetNbinsX()
    for ix in range(1, nx + 1):
        dpt = hTruth2D.GetXaxis().GetBinWidth(ix)
        flux_i = float(flux_bins[ix - 1])  # m^-2/POT
        for iy in range(1, hTruth2D.GetNbinsY() + 1):
            dpz = hTruth2D.GetYaxis().GetBinWidth(iy)
            u = hTruth2D.GetBinContent(ix, iy)
            if flux_i > 0 and n_nucleons > 0 and data_pot > 0:
                denom = flux_i * n_nucleons * data_pot * dpt * dpz
                xsec = (u / denom) * 1.0e4  # m^-2 -> cm^-2
            else:
                xsec = 0.0
            hXSec.SetBinContent(ix, iy, xsec)
    return hXSec


def load_flux_bins_for_truth(f_result, result_path, mcfile=None,
                             flux_hist="pTmu_reweightedflux_integrated"):
    h_embedded = f_result.Get("hFlux_pt")
    if h_embedded:
        return (np.asarray([h_embedded.GetBinContent(i)
                            for i in range(1, h_embedded.GetNbinsX() + 1)],
                           dtype=float),
                "embedded hFlux_pt")

    mc_path = mcfile or os.path.join(os.path.dirname(os.path.abspath(result_path))
                                     or ".", "runEventLoopMC.root")
    f_mc = ROOT.TFile.Open(mc_path, "READ")
    if not f_mc or f_mc.IsZombie():
        raise RuntimeError(
            "Input file has no embedded hFlux_pt and "
            f"could not open fallback flux file {mc_path}")
    h_flux = f_mc.Get(flux_hist)
    if not h_flux:
        raise RuntimeError(f"Missing {flux_hist} in {mc_path}")
    flux_bins = np.asarray(
        [h_flux.GetBinContent(i) for i in range(1, h_flux.GetNbinsX() + 1)],
        dtype=float)
    f_mc.Close()
    return flux_bins, f"{mc_path}:{flux_hist}"


def main():
    ap = argparse.ArgumentParser(
        description="Plot 2D OmniFold cross-section results.")
    ap.add_argument("--infile", default="2d_crossSection_omnifold.root",
                     help="Input ROOT file from unfold_2d_omnifold_unbinned.py")
    ap.add_argument("--prefix", default="2d_xsec",
                     help="Output filename prefix")
    ap.add_argument("--mcfile", default=None,
                     help="Fallback ROOT file for flux histogram when infile lacks hFlux_pt")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated",
                     help="Histogram name inside --mcfile for fallback flux loading")
    args = ap.parse_args()

    f = ROOT.TFile.Open(args.infile, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open {args.infile}")

    hXSec2D = f.Get("hXSec2D")
    hTruth2D = f.Get("hTruth2D")
    hEff2D = f.Get("hEff2D")
    hXSec_pt = f.Get("hXSec_pt")
    hXSec_pz = f.Get("hXSec_pz")

    if not all([hXSec2D, hTruth2D, hEff2D, hXSec_pt, hXSec_pz]):
        raise RuntimeError("Missing required histograms in input file")

    # Detach from file
    for h in [hXSec2D, hTruth2D, hEff2D, hXSec_pt, hXSec_pz]:
        h.SetDirectory(0)

    # Read metadata for truth cross-section computation
    data_pot = float(f.Get("dataPOT").GetVal())
    n_nucleons = float(f.Get("nNucleons").GetVal())
    flux_bins, flux_source = load_flux_bins_for_truth(
        f, args.infile, args.mcfile, args.flux_hist)
    print(f"[INFO] Truth-normalization flux source: {flux_source}")

    # Compute truth cross section for comparison
    hXSecTruth2D = compute_truth_xsec_2d(hTruth2D, hEff2D, flux_bins,
                                          data_pot, n_nucleons)
    hXSecTruth2D.SetDirectory(0)

    # 1D truth projections
    from unfold_2d_omnifold_unbinned import project_xsec_1d
    hXSecTruth_pt = project_xsec_1d(hXSecTruth2D, "pt", PT_EDGES, PZ_EDGES)
    hXSecTruth_pt.SetName("hXSecTruth_pt")
    hXSecTruth_pz = project_xsec_1d(hXSecTruth2D, "pz", PT_EDGES, PZ_EDGES)
    hXSecTruth_pz.SetName("hXSecTruth_pz")

    f.Close()

    # --- Panel grid: p_T slices (each panel shows d^2sigma vs p_||) ---
    xsec_pt_slices = th2_to_slices(hXSec2D, "pt")
    truth_pt_slices = th2_to_slices(hXSecTruth2D, "pt")
    plot_panel_grid(
        xsec_pt_slices, truth_pt_slices,
        nrows=4, ncols=4,
        xlabel="p_{||} (GeV/c)",
        ylabel="d$^2\\sigma$/(dp$_T$dp$_{||}$)\n(cm$^2$/(GeV/c)$^2$/nucleon)",
        outname=f"{args.prefix}_pt_slices.png",
        title_prefix="CC inclusive: slices in p_T"
    )

    # --- Panel grid: p_|| slices (each panel shows d^2sigma vs p_T) ---
    xsec_pz_slices = th2_to_slices(hXSec2D, "pz")
    truth_pz_slices = th2_to_slices(hXSecTruth2D, "pz")
    plot_panel_grid(
        xsec_pz_slices, truth_pz_slices,
        nrows=4, ncols=4,
        xlabel="p$_T$ (GeV/c)",
        ylabel="d$^2\\sigma$/(dp$_T$dp$_{||}$)\n(cm$^2$/(GeV/c)$^2$/nucleon)",
        outname=f"{args.prefix}_pz_slices.png",
        title_prefix="CC inclusive: slices in p_{||}"
    )

    # --- 1D projections ---
    plot_1d_projection(
        hXSec_pt, hXSecTruth_pt,
        xlabel="p$_T$ (GeV/c)",
        ylabel="d$\\sigma$/dp$_T$ (cm$^2$/GeV/nucleon)",
        outname=f"{args.prefix}_projection_pt.png",
        title="CC inclusive: d$\\sigma$/dp$_T$ (OmniFold)"
    )

    plot_1d_projection(
        hXSec_pz, hXSecTruth_pz,
        xlabel="p$_{||}$ (GeV/c)",
        ylabel="d$\\sigma$/dp$_{||}$ (cm$^2$/GeV/nucleon)",
        outname=f"{args.prefix}_projection_pz.png",
        title="CC inclusive: d$\\sigma$/dp$_{||}$ (OmniFold)"
    )

    # --- Efficiency map ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6))
    npt = hEff2D.GetNbinsX()
    npz = hEff2D.GetNbinsY()
    # Match the paper's Fig. 5 convention: p_|| on x, p_T on y.
    eff_arr = np.zeros((npt, npz))
    for ix in range(1, npt + 1):
        for iy in range(1, npz + 1):
            eff_arr[ix - 1, iy - 1] = hEff2D.GetBinContent(ix, iy)

    im = ax.pcolormesh(PZ_EDGES, PT_EDGES, eff_arr, cmap="viridis",
                        vmin=0, vmax=1)
    fig.colorbar(im, ax=ax, label="Efficiency")
    ax.set_xlabel("p$_{||}$ (GeV/c)")
    ax.set_ylabel("p$_T$ (GeV/c)")
    ax.set_title("Selection efficiency (MC)")
    fig.savefig(f"{args.prefix}_efficiency.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved {args.prefix}_efficiency.png")


if __name__ == "__main__":
    main()
