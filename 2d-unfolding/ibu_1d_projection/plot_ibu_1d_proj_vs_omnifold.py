#!/usr/bin/env python3
"""3-way overlay: IBU on 1D projection of 2D inputs vs. OmniFold-2D 1D
projection vs. paper 1D projection.

For each axis (p_T, p_||):
  - Top panel: dσ/dx absolute overlay.
  - Bottom panel: ratio to paper.
"""


import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT


def th1d_to_arrays(h):
    n = h.GetNbinsX()
    edges = np.array([h.GetXaxis().GetBinLowEdge(i + 1) for i in range(n)]
                     + [h.GetXaxis().GetBinUpEdge(n)])
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = edges[1:] - edges[:-1]
    vals = np.array([h.GetBinContent(i + 1) for i in range(n)])
    errs = np.array([h.GetBinError(i + 1) for i in range(n)])
    return edges, centers, widths, vals, errs


def project_paper_th2d(h, axis):
    """Project paper hXSecPaper2D (d²σ/(dpT dp||) in cm²/(GeV/c)²) onto
    axis ∈ {'pt','pz'} by summing over the orthogonal axis with bin
    widths. The paper TH2D has axes pt × p|| (x is p_T per the file we
    use; verify with axis title)."""
    nx = h.GetNbinsX()
    ny = h.GetNbinsY()
    xt = (h.GetXaxis().GetTitle() or "").lower()
    # Paper file convention: x = p_T (14), y = p_|| (16)
    if nx == 14 and ny == 16:
        pt_axis, pz_axis = h.GetXaxis(), h.GetYaxis()
        pt_n, pz_n = nx, ny
        get = lambda ipt, ipz: h.GetBinContent(ipt, ipz)
        get_err = lambda ipt, ipz: h.GetBinError(ipt, ipz)
    elif nx == 16 and ny == 14:
        pt_axis, pz_axis = h.GetYaxis(), h.GetXaxis()
        pt_n, pz_n = ny, nx
        get = lambda ipt, ipz: h.GetBinContent(ipz, ipt)
        get_err = lambda ipt, ipz: h.GetBinError(ipz, ipt)
    else:
        raise RuntimeError(f"Unexpected paper TH2D shape: {nx}x{ny}")

    if axis == "pt":
        edges = np.array([pt_axis.GetBinLowEdge(i + 1) for i in range(pt_n)]
                         + [pt_axis.GetBinUpEdge(pt_n)])
        vals = np.zeros(pt_n)
        errs = np.zeros(pt_n)
        for i in range(1, pt_n + 1):
            v, e2 = 0.0, 0.0
            for j in range(1, pz_n + 1):
                dpz = pz_axis.GetBinWidth(j)
                v += get(i, j) * dpz
                e2 += (get_err(i, j) * dpz) ** 2
            vals[i - 1] = v
            errs[i - 1] = np.sqrt(e2)
    else:
        edges = np.array([pz_axis.GetBinLowEdge(i + 1) for i in range(pz_n)]
                         + [pz_axis.GetBinUpEdge(pz_n)])
        vals = np.zeros(pz_n)
        errs = np.zeros(pz_n)
        for j in range(1, pz_n + 1):
            v, e2 = 0.0, 0.0
            for i in range(1, pt_n + 1):
                dpt = pt_axis.GetBinWidth(i)
                v += get(i, j) * dpt
                e2 += (get_err(i, j) * dpt) ** 2
            vals[j - 1] = v
            errs[j - 1] = np.sqrt(e2)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = edges[1:] - edges[:-1]
    return edges, centers, widths, vals, errs


def safe_ratio(num_v, num_e, den_v):
    r = np.zeros_like(num_v)
    re = np.zeros_like(num_v)
    mask = den_v > 0
    r[mask] = num_v[mask] / den_v[mask]
    re[mask] = num_e[mask] / den_v[mask]
    return r, re


def make_panel(ax_top, ax_bot, axis_label, edges,
               ibu, ibu_e, omf, omf_e, paper, paper_e, centers, widths):
    # Top: absolute curves
    ax_top.errorbar(centers, ibu, yerr=ibu_e, fmt="o", ms=4,
                    color="tab:red", label="IBU on 2D-projection",
                    zorder=4)
    ax_top.errorbar(centers, omf, yerr=omf_e, fmt="s", ms=4,
                    color="tab:blue",
                    label="OmniFold 2D (1D projection)",
                    zorder=3)
    ax_top.errorbar(centers, paper, yerr=paper_e, fmt="^", ms=4,
                    color="black", label="Paper (2D projection)",
                    zorder=2)
    ax_top.set_ylabel(rf"d$\sigma$/d{axis_label} (cm$^2$/(GeV/c)/nucleon)")
    ax_top.legend(loc="best", fontsize=9)
    ax_top.grid(True, alpha=0.3)
    ax_top.set_xlim(edges[0], edges[-1])

    # Bottom: ratio to paper
    r_ibu, re_ibu = safe_ratio(ibu, ibu_e, paper)
    r_omf, re_omf = safe_ratio(omf, omf_e, paper)
    ax_bot.errorbar(centers, r_ibu, yerr=re_ibu, fmt="o", ms=4,
                    color="tab:red", label="IBU/paper")
    ax_bot.errorbar(centers, r_omf, yerr=re_omf, fmt="s", ms=4,
                    color="tab:blue", label="OmniFold/paper")
    ax_bot.axhline(1.0, color="black", lw=0.8)
    ax_bot.set_xlabel(axis_label)
    ax_bot.set_ylabel("Ratio to paper")
    ax_bot.set_ylim(0.5, 1.3)
    ax_bot.legend(loc="best", fontsize=9)
    ax_bot.grid(True, alpha=0.3)
    ax_bot.set_xlim(edges[0], edges[-1])


def plot_axis(axis, ibu_path, omf_path, paper_path, out_png):
    f_ibu = ROOT.TFile.Open(ibu_path)
    h_ibu = f_ibu.Get("crossSection")
    if not h_ibu:
        raise RuntimeError(f"crossSection not in {ibu_path}")
    edges, centers, widths, ibu_v, ibu_e = th1d_to_arrays(h_ibu)
    f_ibu.Close()

    f_om = ROOT.TFile.Open(omf_path)
    h_omf = f_om.Get("hXSec_pt" if axis == "pt" else "hXSec_pz")
    _, _, _, omf_v, omf_e = th1d_to_arrays(h_omf)
    f_om.Close()

    f_p = ROOT.TFile.Open(paper_path)
    h_paper = f_p.Get("pt_pl_cross_section")
    if not h_paper:
        raise RuntimeError(f"pt_pl_cross_section not in {paper_path}")
    _, _, _, paper_v, paper_e = project_paper_th2d(h_paper, axis)
    f_p.Close()

    label = r"$p_T$ (GeV/c)" if axis == "pt" else r"$p_{||}$ (GeV/c)"
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(8, 7),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    fig.suptitle(
        f"IBU-on-2D-projection vs OmniFold-2D vs paper — d$\\sigma$/d"
        f"{label}", y=0.995, fontsize=11)
    make_panel(ax_top, ax_bot, label, edges,
               ibu_v, ibu_e, omf_v, omf_e, paper_v, paper_e,
               centers, widths)
    fig.tight_layout()
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    print(f"[wrote] {out_png}")

    # Print headline numbers.
    paper_total = float((paper_v * widths).sum())
    omf_total = float((omf_v * widths).sum())
    ibu_total = float((ibu_v * widths).sum())
    print(f"  paper integral   = {paper_total:.4e}")
    print(f"  OmniFold-2D 1D   = {omf_total:.4e}  (ratio {omf_total/paper_total:.3f})")
    print(f"  IBU-on-projection = {ibu_total:.4e}  (ratio {ibu_total/paper_total:.3f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ibu-pt", default="pTmu_crossSection.root")
    ap.add_argument("--ibu-pz", default="pZmu_crossSection.root")
    ap.add_argument("--omnifold-2d",
                    default="../2d_crossSection_omnifold_MEFHC_5iter.root")
    ap.add_argument("--paper-2d",
                    default="../minerva_paper_anc/"
                            "cov_ptpl_minerva_inclusive_6GeV.root")
    ap.add_argument("--out-pt", default="MEFHC_5iter_ibu_1d_proj_pt.png")
    ap.add_argument("--out-pz", default="MEFHC_5iter_ibu_1d_proj_pz.png")
    args = ap.parse_args()

    ROOT.gROOT.SetBatch(True)
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.gSystem.Load("libMAT")

    print(f"[plot] p_T axis ({args.ibu_pt})")
    plot_axis("pt", args.ibu_pt, args.omnifold_2d, args.paper_2d,
              args.out_pt)
    print(f"[plot] p_|| axis ({args.ibu_pz})")
    plot_axis("pz", args.ibu_pz, args.omnifold_2d, args.paper_2d,
              args.out_pz)


if __name__ == "__main__":
    main()
