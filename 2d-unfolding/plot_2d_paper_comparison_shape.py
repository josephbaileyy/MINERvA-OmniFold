#!/usr/bin/env python3
"""Slice-grid and pull-map plots for the self-normalized 2D shape comparison.

Reads the output of `normalize_xsec_shape.py` and produces:
  * MEFHC_5iter_xsec_paper_pt_slices_shape.png  (4x4 p_T slices)
  * MEFHC_5iter_xsec_paper_pz_slices_shape.png  (4x4 p_|| slices)
  * MEFHC_5iter_pull_interior_shape.png         (185-bin shape pull map)

Mirrors `plot_2d_paper_comparison.py`'s 4x4 slice layout but plots
unit-area shape rather than absolute cross section. The total flux scale
cancels by construction, so any residual disagreement is shape-only and
not the 16.6% normalization deficit.

Per-panel chi^2 in the slice grids uses the shape diagonal of the
propagated covariance for simplicity; the headline shape chi^2/ndf
(full off-diagonal cov) is reported by `normalize_xsec_shape.py` and
should be added to the slide title.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os

import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


N_PT, N_PZ = 14, 16
N = N_PT * N_PZ

DEFAULT_SHAPE_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter_shape.root"
DEFAULT_OUT_PREFIX = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/MEFHC_5iter"


def tm_to_np(tm):
    n = tm.GetNrows()
    a = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            a[i, j] = tm(i, j)
    return a


def panel_arrays_y_at_x(h, ix):
    """Return centers/edges/values along y at fixed x bin ix."""
    ny = h.GetNbinsY()
    centers = np.array([h.GetYaxis().GetBinCenter(j) for j in range(1, ny + 1)])
    widths = np.array([h.GetYaxis().GetBinWidth(j)  for j in range(1, ny + 1)])
    edges = np.array([h.GetYaxis().GetBinLowEdge(j) for j in range(1, ny + 2)])
    vals = np.array([h.GetBinContent(ix, j) for j in range(1, ny + 1)])
    return centers, widths, edges, vals


def panel_arrays_x_at_y(h, iy):
    """Return centers/edges/values along x at fixed y bin iy."""
    nx = h.GetNbinsX()
    centers = np.array([h.GetXaxis().GetBinCenter(i) for i in range(1, nx + 1)])
    widths = np.array([h.GetXaxis().GetBinWidth(i)  for i in range(1, nx + 1)])
    edges = np.array([h.GetXaxis().GetBinLowEdge(i) for i in range(1, nx + 2)])
    vals = np.array([h.GetBinContent(i, iy) for i in range(1, nx + 1)])
    return centers, widths, edges, vals


def gid_x_y(ptb, pzb):
    return (ptb - 1) * N_PZ + (pzb - 1)


def slice_chi2(s_o, s_p, C, gids):
    """Per-panel chi^2 using only the diagonal of C (panel-local)."""
    diag = np.array([C[g, g] for g in gids])
    mask = (diag > 0) & np.isfinite(s_o) & np.isfinite(s_p)
    if not np.any(mask):
        return 0.0, 0
    d = s_o[mask] - s_p[mask]
    sig = np.sqrt(diag[mask])
    return float(np.sum((d / sig) ** 2)), int(mask.sum())


def draw_pt_slices(h_ours, h_paper, C, niter, out, suptitle):
    """4x4 panel grid. Each panel = shape vs p_|| at fixed p_T bin (1..N_PT).
    There are 14 p_T bins: 14 panels filled, 2 empty in 4x4."""
    fig, axes = plt.subplots(4, 4, figsize=(4 * 4, 3.3 * 4), squeeze=False)
    fig.subplots_adjust(hspace=0.38, wspace=0.30)

    total_chi2, total_ndf = 0.0, 0
    for idx in range(4 * 4):
        r, c = divmod(idx, 4)
        ax = axes[r][c]
        ptb = idx + 1
        if ptb > N_PT:
            ax.set_visible(False)
            continue
        centers, widths, edges, vals_o = panel_arrays_y_at_x(h_ours, ptb)
        _, _, _, vals_p = panel_arrays_y_at_x(h_paper, ptb)
        gids = np.array([gid_x_y(ptb, j) for j in range(1, N_PZ + 1)])
        diag = np.array([C[g, g] for g in gids])
        sig = np.where(diag > 0, np.sqrt(diag), 0.0)

        chi2, ndf = slice_chi2(vals_o, vals_p, C, gids)
        total_chi2 += chi2
        total_ndf += ndf

        mx = max(np.nanmax(vals_o) if vals_o.size else 0.0,
                 np.nanmax(vals_p) if vals_p.size else 0.0)
        scale = 1.0 / mx if mx > 0 else 1.0
        if mx > 0:
            exp = int(np.floor(np.log10(mx)))
            scale_str = rf"$\times 10^{{{-exp}}}$"
        else:
            scale_str = ""

        ax.errorbar(centers, vals_o * scale, yerr=sig * scale,
                    xerr=widths / 2, fmt="ko", markersize=2.5,
                    linewidth=0.9, capsize=1.5, label="OmniFold (shape)",
                    zorder=3)
        ax.stairs(vals_p * scale, edges, color="C3", linewidth=1.2,
                  label="Paper (shape)", zorder=2)

        ax.set_xlim(edges[0], edges[-1])
        ax.set_ylim(0, 1.4)
        from_pt = h_ours.GetXaxis().GetBinLowEdge(ptb)
        to_pt = h_ours.GetXaxis().GetBinUpEdge(ptb)
        ax.set_title(f"$p_T \\in [{from_pt:.2f}, {to_pt:.2f}]$ GeV/c",
                     fontsize=8, pad=3)
        ax.tick_params(labelsize=7)

        note = scale_str
        if ndf > 0:
            note = f"{scale_str}\n" + rf"$\chi^2/n={chi2:.1f}/{ndf}$"
        ax.text(0.97, 0.97, note, transform=ax.transAxes,
                ha="right", va="top", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.8))

        if r == 3:
            ax.set_xlabel(r"$p_{||}$ (GeV/c)", fontsize=8)
        if c == 0:
            ax.set_ylabel("scaled shape", fontsize=7)

    axes[0][0].legend(fontsize=7, loc="lower right")
    if total_ndf > 0:
        sup = (suptitle + rf"   |   panel-diag $\chi^2/n = "
               rf"{total_chi2:.1f}/{total_ndf} = "
               rf"{total_chi2/total_ndf:.2f}$")
    else:
        sup = suptitle
    fig.suptitle(sup, fontsize=11, y=0.995)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def draw_pz_slices(h_ours, h_paper, C, niter, out, suptitle):
    """4x4 panel grid. Each panel = shape vs p_T at fixed p_|| bin (1..N_PZ).
    There are 16 p_|| bins: all 16 panels filled."""
    fig, axes = plt.subplots(4, 4, figsize=(4 * 4, 3.3 * 4), squeeze=False)
    fig.subplots_adjust(hspace=0.38, wspace=0.30)

    total_chi2, total_ndf = 0.0, 0
    for idx in range(4 * 4):
        r, c = divmod(idx, 4)
        ax = axes[r][c]
        pzb = idx + 1
        centers, widths, edges, vals_o = panel_arrays_x_at_y(h_ours, pzb)
        _, _, _, vals_p = panel_arrays_x_at_y(h_paper, pzb)
        gids = np.array([gid_x_y(i, pzb) for i in range(1, N_PT + 1)])
        diag = np.array([C[g, g] for g in gids])
        sig = np.where(diag > 0, np.sqrt(diag), 0.0)

        chi2, ndf = slice_chi2(vals_o, vals_p, C, gids)
        total_chi2 += chi2
        total_ndf += ndf

        mx = max(np.nanmax(vals_o) if vals_o.size else 0.0,
                 np.nanmax(vals_p) if vals_p.size else 0.0)
        scale = 1.0 / mx if mx > 0 else 1.0
        if mx > 0:
            exp = int(np.floor(np.log10(mx)))
            scale_str = rf"$\times 10^{{{-exp}}}$"
        else:
            scale_str = ""

        ax.errorbar(centers, vals_o * scale, yerr=sig * scale,
                    xerr=widths / 2, fmt="ko", markersize=2.5,
                    linewidth=0.9, capsize=1.5, label="OmniFold (shape)",
                    zorder=3)
        ax.stairs(vals_p * scale, edges, color="C3", linewidth=1.2,
                  label="Paper (shape)", zorder=2)

        ax.set_xlim(edges[0], edges[-1])
        ax.set_ylim(0, 1.4)
        from_pz = h_ours.GetYaxis().GetBinLowEdge(pzb)
        to_pz = h_ours.GetYaxis().GetBinUpEdge(pzb)
        ax.set_title(f"$p_{{||}} \\in [{from_pz:.1f}, {to_pz:.1f}]$ GeV/c",
                     fontsize=8, pad=3)
        ax.tick_params(labelsize=7)

        note = scale_str
        if ndf > 0:
            note = f"{scale_str}\n" + rf"$\chi^2/n={chi2:.1f}/{ndf}$"
        ax.text(0.97, 0.97, note, transform=ax.transAxes,
                ha="right", va="top", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.8))

        if r == 3:
            ax.set_xlabel(r"$p_T$ (GeV/c)", fontsize=8)
        if c == 0:
            ax.set_ylabel("scaled shape", fontsize=7)

    axes[0][0].legend(fontsize=7, loc="lower right")
    if total_ndf > 0:
        sup = (suptitle + rf"   |   panel-diag $\chi^2/n = "
               rf"{total_chi2:.1f}/{total_ndf} = "
               rf"{total_chi2/total_ndf:.2f}$")
    else:
        sup = suptitle
    fig.suptitle(sup, fontsize=11, y=0.995)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def draw_pull_map(h_ours, h_paper, C_shape_185, chi2_185, ndf_185, out, suptitle):
    """Pull map: (s_ours - s_paper) / sqrt(C_shape diagonal), 185-bin interior."""
    diff = np.zeros((N_PT, N_PZ))
    pull = np.full((N_PT, N_PZ), np.nan)
    for ptb in range(1, N_PT + 1):
        for pzb in range(1, N_PZ + 1):
            gid = gid_x_y(ptb, pzb)
            so = h_ours.GetBinContent(ptb, pzb)
            sp = h_paper.GetBinContent(ptb, pzb)
            d = so - sp
            sig2 = C_shape_185[gid, gid]
            if sig2 > 0 and (so != 0 or sp != 0):
                pull[ptb - 1, pzb - 1] = d / np.sqrt(sig2)

    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    im = axs[0].imshow(
        pull.T, aspect="auto", origin="lower", cmap="RdBu_r",
        vmin=-5, vmax=5, extent=[0, N_PT, 0, N_PZ])
    axs[0].set_xlabel("p_T bin index")
    axs[0].set_ylabel("p_|| bin index")
    axs[0].set_title("Shape pull map (185-bin interior)")
    plt.colorbar(im, ax=axs[0], label="pull (s_ours - s_paper) / sigma_shape")

    pulls_used = pull[np.isfinite(pull)]
    axs[1].hist(pulls_used, bins=30, color="steelblue", edgecolor="black")
    axs[1].axvline(0, color="k", ls="--", lw=0.8)
    axs[1].set_xlabel("shape pull")
    axs[1].set_ylabel("bins")
    axs[1].set_title("Shape pull distribution (185-bin interior)")
    if pulls_used.size:
        mu, sd = pulls_used.mean(), pulls_used.std()
        axs[1].text(
            0.03, 0.95,
            f"mean={mu:.2f}\nrms ={sd:.2f}\n"
            f"chi2/ndf = {chi2_185/ndf_185:.2f}",
            transform=axs[1].transAxes, va="top", family="monospace",
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="gray"))

    fig.suptitle(suptitle, fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shape-root", default=DEFAULT_SHAPE_ROOT)
    ap.add_argument("--prefix", default=DEFAULT_OUT_PREFIX)
    ap.add_argument("--niter", type=int, default=5)
    args = ap.parse_args()

    f = ROOT.TFile.Open(args.shape_root)
    h_o_205 = f.Get("hXSec2D_shape_205")
    h_p_205 = f.Get("hXSecPaper2D_shape_205")
    h_o_185 = f.Get("hXSec2D_shape_185")
    h_p_185 = f.Get("hXSecPaper2D_shape_185")
    for h in (h_o_205, h_p_205, h_o_185, h_p_185):
        h.SetDirectory(0)
    C_205 = tm_to_np(f.Get("CShape205_total"))
    C_185 = tm_to_np(f.Get("CShape185_total"))
    chi2_205 = float(f.Get("chi2_shape_205_total").GetVal())
    ndf_205 = int(f.Get("ndf_shape_205").GetVal())
    chi2_185 = float(f.Get("chi2_shape_185_total").GetVal())
    ndf_185 = int(f.Get("ndf_shape_185").GetVal())
    f.Close()

    suptitle_pt = (f"Self-normalized shape, slices in $p_T$ "
                   f"({args.niter} iter)   |   "
                   f"205-bin shape $\\chi^2/n = "
                   f"{chi2_205:.1f}/{ndf_205} = {chi2_205/ndf_205:.2f}$")
    suptitle_pz = (f"Self-normalized shape, slices in $p_{{||}}$ "
                   f"({args.niter} iter)   |   "
                   f"205-bin shape $\\chi^2/n = "
                   f"{chi2_205:.1f}/{ndf_205} = {chi2_205/ndf_205:.2f}$")
    suptitle_pull = (f"Self-normalized shape pull (185-bin interior)   |   "
                     f"$\\chi^2/n = "
                     f"{chi2_185:.1f}/{ndf_185} = {chi2_185/ndf_185:.2f}$")

    draw_pt_slices(h_o_205, h_p_205, C_205, args.niter,
                   f"{args.prefix}_xsec_paper_pt_slices_shape.png",
                   suptitle_pt)
    draw_pz_slices(h_o_205, h_p_205, C_205, args.niter,
                   f"{args.prefix}_xsec_paper_pz_slices_shape.png",
                   suptitle_pz)
    draw_pull_map(h_o_185, h_p_185, C_185, chi2_185, ndf_185,
                  f"{args.prefix}_pull_interior_shape.png",
                  suptitle_pull)


if __name__ == "__main__":
    main()
