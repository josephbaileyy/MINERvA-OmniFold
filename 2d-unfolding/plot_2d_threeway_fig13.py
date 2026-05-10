#!/usr/bin/env python3
"""Fig.-13-style three-way comparison.

Overlay published arXiv:2106.16210 data, this analysis's OmniFold result,
and the local MC-truth prediction from the OmniFold output.  The visual
layout follows the paper's Fig. 13: touching small multiples, panel-local
scale factors, shared outer labels, and legends in unused panels.
"""

import argparse
from array import array

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

from plot_2d_cross_section import (  # noqa: E402
    PT_EDGES,
    PZ_EDGES,
    compute_truth_xsec_2d,
    load_flux_bins_for_truth,
)


N_PT = len(PT_EDGES) - 1
N_PZ = len(PZ_EDGES) - 1
N = N_PT * N_PZ


def tmatrix_to_numpy(tm):
    arr = np.empty((tm.GetNrows(), tm.GetNcols()), dtype=float)
    for i in range(tm.GetNrows()):
        for j in range(tm.GetNcols()):
            arr[i, j] = tm(i, j)
    return arr


def paper_arrays(paper_file):
    """Return paper central values/errors in our TH2 convention: pt x pz."""
    f = ROOT.TFile.Open(paper_file, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open {paper_file}")
    h = f.Get("pt_pl_cross_section")
    cov_stat = tmatrix_to_numpy(f.Get("StatOnlyCovariance"))
    vals = np.zeros((N_PT, N_PZ), dtype=float)
    errs = np.zeros((N_PT, N_PZ), dtype=float)
    reported = np.zeros((N_PT, N_PZ), dtype=bool)

    # Ancillary TH2D convention: x=p|| (16), y=pT (14).
    # Covariance global index: (ptbin - 1) * 16 + (pzbin - 1).
    for ipt in range(N_PT):
        for ipz in range(N_PZ):
            gid = ipt * N_PZ + ipz
            vals[ipt, ipz] = h.GetBinContent(ipz + 1, ipt + 1)
            if cov_stat[gid, gid] > 0:
                errs[ipt, ipz] = np.sqrt(cov_stat[gid, gid])
                reported[ipt, ipz] = True
    f.Close()
    return vals, errs, reported


def th2_to_array(h):
    vals = np.zeros((N_PT, N_PZ), dtype=float)
    errs = np.zeros((N_PT, N_PZ), dtype=float)
    for ipt in range(N_PT):
        for ipz in range(N_PZ):
            vals[ipt, ipz] = h.GetBinContent(ipt + 1, ipz + 1)
            errs[ipt, ipz] = h.GetBinError(ipt + 1, ipz + 1)
    return vals, errs


def load_result(result_file, mcfile=None, flux_hist="pTmu_reweightedflux_integrated"):
    f = ROOT.TFile.Open(result_file, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open {result_file}")

    h_xsec = f.Get("hXSec2D")
    # MC truth display: prefer hOFTruthDenom2D (post-Phase-16 canonical
    # mc_truth_denom yield, 32.85M) over hTruth2D (mc_signal_reco subset,
    # 24.5M, ~0.745x low). hOFTruthDenom2D is the proper analogue of the
    # paper's MnvTune-v1 model curve.
    h_truth = f.Get("hOFTruthDenom2D")
    if not h_truth:
        h_truth = f.Get("hTruth2D")
        print("[WARN] hOFTruthDenom2D not found; falling back to hTruth2D "
              "(pre-Phase-16 subset truth).")
    h_eff = f.Get("hEff2D")
    if not all([h_xsec, h_truth, h_eff]):
        raise RuntimeError("Missing hXSec2D, hOFTruthDenom2D/hTruth2D, or hEff2D")
    for h in [h_xsec, h_truth, h_eff]:
        h.SetDirectory(0)

    data_pot = float(f.Get("dataPOT").GetVal())
    n_nucleons = float(f.Get("nNucleons").GetVal())
    flux_bins, flux_source = load_flux_bins_for_truth(
        f, result_file, mcfile, flux_hist)

    h_truth_xsec = compute_truth_xsec_2d(
        h_truth, h_eff, flux_bins, data_pot, n_nucleons)
    h_truth_xsec.SetDirectory(0)
    f.Close()

    omni, omni_err = th2_to_array(h_xsec)
    truth, _ = th2_to_array(h_truth_xsec)
    return omni, omni_err, truth, flux_source


def rounded_scale(values, target=3.4):
    mx = float(np.nanmax(values)) if values.size else 0.0
    if not np.isfinite(mx) or mx <= 0:
        return 1.0
    raw = target / (mx * 1.0e39)
    if raw <= 0:
        return 1.0
    if raw < 1:
        return round(raw, 1)
    if raw < 10:
        return round(raw, 1)
    if raw < 100:
        return round(raw, 1)
    return round(raw)


def compact_x(nbins):
    return np.arange(nbins + 1, dtype=float)


def tick_positions(edges, labels):
    edges = np.asarray(edges, dtype=float)
    labels = np.asarray(labels, dtype=float)
    return np.interp(labels, edges, np.arange(edges.size, dtype=float))


def stair_xy(edges, values):
    x = []
    y = []
    for i, val in enumerate(values):
        x.extend([edges[i], edges[i + 1]])
        y.extend([val, val])
    return np.asarray(x), np.asarray(y)


def setup_paper_axes(ax, row, col, nrows, ncols, nbins, ylim=(0, 4.2)):
    ax.set_xlim(0, nbins)
    ax.set_ylim(*ylim)
    ax.tick_params(direction="in", top=False, right=False, labelsize=8,
                   length=3, pad=2)
    if row != nrows - 1:
        ax.set_xticklabels([])
    if col != 0:
        ax.set_yticklabels([])
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)


def draw_panel(ax, x_edges, paper_y, paper_err, omni_y, omni_err, truth_y,
               title, scale):
    del x_edges
    nbins = len(paper_y)
    x_plot_edges = compact_x(nbins)
    centers = 0.5 * (x_plot_edges[:-1] + x_plot_edges[1:])
    half_widths = np.full(nbins, 0.5)
    factor = 1.0e39 * scale

    sx, sy = stair_xy(x_plot_edges, truth_y * factor)
    ax.plot(sx, sy, color="red", lw=1.6, label="MC truth")

    ax.errorbar(centers, paper_y * factor, yerr=paper_err * factor,
                xerr=half_widths, fmt="s", ms=2.5, color="black",
                ecolor="black", elinewidth=0.8, capsize=1.5,
                label="Paper data", zorder=3)
    ax.errorbar(centers, omni_y * factor, yerr=omni_err * factor,
                xerr=half_widths, fmt="o", ms=2.2, color="#1f77b4",
                ecolor="#1f77b4", elinewidth=0.8, capsize=1.3,
                label="OmniFold", zorder=4)

    ax.text(0.50, 0.96, title, transform=ax.transAxes,
            ha="center", va="top", fontsize=9)
    ax.text(0.92, 0.17, f"x {scale:g}", transform=ax.transAxes,
            ha="right", va="center", fontsize=9)


def draw_legend_panel(ax, handles, labels):
    ax.axis("off")
    ax.legend(handles, labels, loc="center", frameon=False, fontsize=10,
              ncol=1, handlelength=2.5)


def plot_pt_slices(fig, outer, paper, paper_err, reported,
                   omni, omni_err, truth):
    import matplotlib.pyplot as plt

    gs = outer.subgridspec(4, 4, wspace=0.0, hspace=0.0)
    handles = labels = None
    axes = []
    for ipt in range(16):
        row, col = divmod(ipt, 4)
        ax = fig.add_subplot(gs[row, col])
        axes.append(ax)
        if ipt >= N_PT:
            if handles is not None:
                draw_legend_panel(ax, handles, labels)
            else:
                ax.axis("off")
            continue

        mask = reported[ipt, :]
        vals_for_scale = np.r_[paper[ipt, mask], omni[ipt, :], truth[ipt, :]]
        scale = rounded_scale(vals_for_scale)
        title = f"{PT_EDGES[ipt]:.2f} < p_t < {PT_EDGES[ipt + 1]:.2f}"
        draw_panel(ax, PZ_EDGES, paper[ipt, :], paper_err[ipt, :],
                   omni[ipt, :], omni_err[ipt, :], truth[ipt, :],
                   title, scale)
        setup_paper_axes(ax, row, col, 4, 4, N_PZ)
        tick_labs = [4, 10, 20, 40, 60]
        ax.set_xticks(tick_positions(PZ_EDGES, tick_labs))
        ax.set_xticklabels([str(x) for x in tick_labs])
        if ipt == 0:
            handles, labels = ax.get_legend_handles_labels()

    return axes


def plot_pz_slices(fig, outer, paper, paper_err, reported,
                   omni, omni_err, truth):
    import matplotlib.pyplot as plt

    gs = outer.subgridspec(4, 4, wspace=0.0, hspace=0.0)
    axes = []
    for ipz in range(N_PZ):
        row, col = divmod(ipz, 4)
        ax = fig.add_subplot(gs[row, col])
        axes.append(ax)
        mask = reported[:, ipz]
        vals_for_scale = np.r_[paper[mask, ipz], omni[:, ipz], truth[:, ipz]]
        scale = rounded_scale(vals_for_scale)
        title = f"{PZ_EDGES[ipz]:.2f} < p_|| < {PZ_EDGES[ipz + 1]:.2f}"
        draw_panel(ax, PT_EDGES, paper[:, ipz], paper_err[:, ipz],
                   omni[:, ipz], omni_err[:, ipz], truth[:, ipz],
                   title, scale)
        setup_paper_axes(ax, row, col, 4, 4, N_PT)
        tick_labs = [0.4, 1.0, 1.5, 2.5, 4.5]
        ax.set_xticks(tick_positions(PT_EDGES, tick_labs))
        ax.set_xticklabels([str(x) for x in tick_labs])
    return axes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--infile", default="2d_crossSection_omnifold_MEHFC_5iter.root")
    ap.add_argument("--paper", default="minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root")
    ap.add_argument("--out", default="MEHFC_5iter_fig13.png")
    ap.add_argument("--mcfile", default=None)
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paper, paper_err, reported = paper_arrays(args.paper)
    omni, omni_err, truth, flux_source = load_result(
        args.infile, args.mcfile, args.flux_hist)
    print(f"[INFO] truth flux source: {flux_source}")

    fig = plt.figure(figsize=(10.4, 13.2))
    outer = fig.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.28,
                             left=0.11, right=0.98, bottom=0.07, top=0.98)

    plot_pt_slices(fig, outer[0], paper, paper_err, reported,
                   omni, omni_err, truth)
    plot_pz_slices(fig, outer[1], paper, paper_err, reported,
                   omni, omni_err, truth)

    fig.text(0.5, 0.505, "Muon Longitudinal Momentum (GeV/c)",
             ha="center", va="center", fontsize=15)
    fig.text(0.5, 0.035, "Muon Transverse Momentum (GeV/c)",
             ha="center", va="center", fontsize=15)
    fig.text(0.027, 0.755,
             r"$d^2\sigma/dp_t\,dp_{||}$ ($\times 10^{-39}$ cm$^2$/(GeV/c)$^2$/Nucleon)",
             rotation=90, ha="center", va="center", fontsize=14)
    fig.text(0.027, 0.285,
             r"$d^2\sigma/dp_t\,dp_{||}$ ($\times 10^{-39}$ cm$^2$/(GeV/c)$^2$/Nucleon)",
             rotation=90, ha="center", va="center", fontsize=14)

    fig.savefig(args.out, dpi=180)
    print(f"[OK] wrote {args.out}")


if __name__ == "__main__":
    main()
