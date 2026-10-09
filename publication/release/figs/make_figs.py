#!/usr/bin/env python3
"""Regenerate the article's Figs. 1-3 from the released arrays (numpy + matplotlib only).

Same quantities as the committed producers (2d-unfolding/compare_to_models.py, compare_to_paper_fullcov.py,
nd-unfolding/excess_eavail_W.py, 3d-unfolding/genie/overlay_eavailW_band.py). Since 2026-10-08 the article prints
this script's output directly (docs/analysis-note/figures/paper_fig1_validation.pdf, paper_fig2_joint.pdf and
paper_fig3_generators.pdf are copies of fig1_validation.pdf, fig2_joint_localization.pdf and
fig3_generator_context.pdf), so a release built from this version regenerates the printed figures, not only
their quantities.
Fig. 1's inset prints two median relative uncertainties. "Published" is recomputed from the arrays. "This work"
(the VL170/VL172 2D budget) is not in the arrays, so it is read from the article's values.tex (macro uqMedian) when
--values is given; without --values the inset says it is not in the arrays.

  python3 make_figs.py --npz fig_arrays.npz --outdir figs_out [--values values.tex]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

GENS = ("GENIE-CV", "GENIE+MEC", "NuWro", "GiBUU")


def grid(vec, mask, n_pt=14, n_pz=16):
    g = np.full((n_pt, n_pz), np.nan)
    idx = np.where(mask)[0]
    g[idx // n_pz, idx % n_pz] = vec[idx]
    return g


def projections(vec, mask, pt_e, pz_e):
    g = np.nan_to_num(grid(vec, mask))
    return (g * np.diff(pz_e)[None, :]).sum(1), (g * np.diff(pt_e)[:, None]).sum(0)


LABEL = {"GENIE-CV": "GENIE CV", "GENIE+MEC": "GENIE + MEC", "NuWro": "NuWro 21.09", "GiBUU": "GiBUU 2019"}
COLORS = {"GENIE-CV": "#2a78d6", "GENIE+MEC": "#eb6834", "NuWro": "#1baf7a", "GiBUU": "#4a3aa7"}
PUBLISHED = "Published (PRD 104, 092007)"
PDF_META = {"CreationDate": None}  # no timestamp: the same versions give the same bytes


def style() -> None:
    """Journal-size type: the figures are drawn at the width they are printed."""
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm", "font.size": 8,
                         "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
                         "legend.fontsize": 7.5, "axes.linewidth": 0.6, "pdf.fonttype": 42})


def projection_jacobians(mask, pt_e, pz_e, n_pt=14, n_pz=16):
    """Linear maps from the flattened 2D density vector to its p_T and p_parallel projections."""
    j_pt, j_pz = np.zeros((n_pt, n_pt * n_pz)), np.zeros((n_pz, n_pt * n_pz))
    for k in np.where(mask)[0]:
        i, j = divmod(k, n_pz)
        j_pt[i, k] = np.diff(pz_e)[j]
        j_pz[j, k] = np.diff(pt_e)[i]
    return j_pt, j_pz


def edge_ticks(ax, axis, edges, every=2):
    """Equal-size cells on an index axis, labelled with the physical bin edges."""
    pos = np.arange(len(edges))
    keep = [i for i in pos if i % every == 0 or i == pos[-1]]
    lab = [f"{edges[i]:g}" for i in keep]
    (ax.set_xticks if axis == "x" else ax.set_yticks)(keep)
    (ax.set_xticklabels if axis == "x" else ax.set_yticklabels)(lab, rotation=0)


def fig1(z, out: Path, uq_median: str | None = None):
    """Two-dimensional reproduction: p_T and p_parallel projections with ratios to the published result and its
    uncertainty band, the published-sigma residual map on the reported grid, and the inset numbers."""
    m = z["mask_reported"].astype(bool)
    pt_e, pz_e = z["pt_edges"], z["pz_edges"]
    cov = z["cov_total"]
    j_pt, j_pz = projection_jacobians(m, pt_e, pz_e)
    fig = plt.figure(figsize=(7.0, 6.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[2.0, 0.9], hspace=0.08, wspace=0.28,
                          left=0.08, right=0.97, top=0.985, bottom=0.53)
    gb = fig.add_gridspec(1, 2, wspace=0.28, left=0.08, right=0.97, top=0.43, bottom=0.07)
    panels = ((j_pt, pt_e, r"$p_T$ (GeV/$c$)", 1e-38, r"$d\sigma/dp_T$ ($10^{-38}$ cm$^2$ (GeV/$c$)$^{-1}$ nucleon$^{-1}$)", "linear"),
              (j_pz, pz_e, r"$p_\parallel$ (GeV/$c$)", 1e-39, r"$d\sigma/dp_\parallel$ ($10^{-39}$ cm$^2$ (GeV/$c$)$^{-1}$ nucleon$^{-1}$)", "log"))
    for col, (jac, edges, xlab, unit, ylab, xscale) in enumerate(panels):
        top = fig.add_subplot(gs[0, col]); bot = fig.add_subplot(gs[1, col], sharex=top)
        pub = jac @ z["paper_v"]; sig = np.sqrt(np.diag(jac @ cov @ jac.T))
        ours = jac @ z["ours_v"]; tune = jac @ z["tune_v1_v"]
        top.stairs((pub + sig) / unit, edges, baseline=(pub - sig) / unit, fill=True, color="0.82", lw=0,
                   label=r"published $\pm1\sigma$")
        top.stairs(pub / unit, edges, color="k", lw=1.4, label=PUBLISHED)
        top.stairs(ours / unit, edges, color="#c0392b", lw=1.2, ls="--", label="This work (OmniFold)")
        top.stairs(tune / unit, edges, color="#2a78d6", lw=1.0, label="MINERvA Tune v1")
        top.set_ylabel(ylab, fontsize=7.5); top.set_ylim(bottom=0); top.tick_params(labelbottom=False)
        rel = sig / pub
        bot.stairs(1 + rel, edges, baseline=1 - rel, fill=True, color="0.82", lw=0)
        bot.axhline(1.0, color="k", lw=0.8)
        bot.stairs(ours / pub, edges, color="#c0392b", lw=1.2, ls="--", baseline=None)
        bot.stairs(tune / pub, edges, color="#2a78d6", lw=1.0, baseline=None)
        bot.set_ylim(0.7, 1.3); bot.set_ylabel("ratio to\npublished", fontsize=7.5); bot.set_xlabel(xlab)
        top.set_xscale(xscale); top.set_xlim(edges[0], edges[-1])
        if xscale == "log":
            bot.set_xticks([2, 3, 5, 10, 20, 40, 60]); bot.set_xticklabels(["2", "3", "5", "10", "20", "40", "60"])
            bot.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        if col == 0:
            top.legend(frameon=False, loc="upper right")
    # residual map on the reported grid (equal-size cells, physical edges as labels)
    ax = fig.add_subplot(gb[0, 0])
    d = np.sqrt(np.where(np.diag(cov) > 0, np.diag(cov), np.nan))
    pull = (z["ours_v"] - z["paper_v"]) / d
    g = grid(np.where(m, pull, np.nan), m)
    lim = 3.0
    im = ax.pcolormesh(np.arange(15), np.arange(17), g.T, cmap="RdBu_r", vmin=-lim, vmax=lim, shading="flat")
    ax.set_facecolor("0.93")
    edge_ticks(ax, "x", pt_e); edge_ticks(ax, "y", pz_e)
    ax.set_xlabel(r"$p_T$ (GeV/$c$), bin edges"); ax.set_ylabel(r"$p_\parallel$ (GeV/$c$), bin edges")
    cb = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.06)
    cb.set_label(r"(OmniFold $-$ published)$/\sigma_{\mathrm{published}}$", fontsize=7.5)
    # inset numbers
    tx = fig.add_subplot(gb[0, 1]); tx.axis("off")
    p = pull[m]
    pubmed = 100.0 * float(np.median(d[m] / z["paper_v"][m]))
    ours_txt = f"{uq_median}%" if uq_median else "not in these arrays"
    tx.text(0.08, 0.80, "Median relative uncertainty", fontsize=9, weight="bold")
    tx.text(0.12, 0.66, f"This work    {ours_txt}\nPublished    {pubmed:.2f}%", fontsize=9, va="top", linespacing=1.5)
    tx.text(0.08, 0.36, r"Published-$\sigma$ standardized residuals", fontsize=9, weight="bold")
    tx.text(0.12, 0.22, f"mean = {p.mean():.3f},  RMS = {p.std():.3f}  ({m.sum()} bins)", fontsize=9, va="top")
    fig.savefig(out / "fig1_validation.pdf", metadata=PDF_META); plt.close(fig)


def fig2(z, out: Path):
    """Joint (E_avail, W) central value relative to MINERvA Tune v1: per-cell ratio and cell-integrated difference,
    stacked for a single column, with each cell's value printed."""
    ee, we = z["eavail_edges"], z["W_edges"]
    area = np.outer(np.diff(ee), np.diff(we))
    ratio = z["hData2D"] / np.where(z["hGenCV2D"] > 0, z["hGenCV2D"], np.nan)
    diff = (z["hData2D"] - z["hGenCV2D"]) * area / 1e-40
    fig, axs = plt.subplots(2, 1, figsize=(3.4, 5.4), gridspec_kw={"hspace": 0.32, "left": 0.17, "right": 0.86,
                                                                   "top": 0.98, "bottom": 0.08})
    vmax = float(np.ceil(np.nanmax(np.abs(diff))))
    spec = ((ratio, "RdBu_r", 0.5, 1.5, "unfolded / MINERvA Tune v1", "{:.2f}"),
            (diff, "RdBu_r", -vmax, vmax, r"unfolded $-$ Tune v1 per cell ($10^{-40}$ cm$^2$/nucleon)", "{:.1f}"))
    for ax, (val, cmap, lo, hi, clab, fmt) in zip(axs, spec):
        im = ax.pcolormesh(np.arange(len(we)), np.arange(len(ee)), val, cmap=cmap, vmin=lo, vmax=hi, shading="flat")
        for i in range(val.shape[0]):
            for j in range(val.shape[1]):
                v = val[i, j]
                if np.isfinite(v):
                    v = 0.0 if abs(v) < 0.05 and fmt == "{:.1f}" else v   # no "-0.0"
                    strong = abs((v - (lo + hi) / 2) / ((hi - lo) / 2)) > 0.6
                    ax.text(j + 0.5, i + 0.5, fmt.format(v), ha="center", va="center", fontsize=6.3,
                            color="w" if strong else "k")
        ax.set_xticks(np.arange(len(we))); ax.set_xticklabels([f"{x:g}" for x in we])
        ax.set_yticks(np.arange(len(ee))); ax.set_yticklabels([f"{x:g}" for x in ee])
        ax.set_xlabel(r"$W$ (GeV), bin edges"); ax.set_ylabel(r"$E_{\mathrm{avail}}$ (GeV), bin edges")
        cb = fig.colorbar(im, ax=ax, pad=0.03, fraction=0.07); cb.set_label(clab, fontsize=7)
        cb.ax.tick_params(labelsize=6.5)
    fig.savefig(out / "fig2_joint_localization.pdf", metadata=PDF_META); plt.close(fig)


def fig3(z, out: Path, name: str = "fig3_generator_context.pdf"):
    """The article's Fig. 3: unfolded E_avail and W projections (overflow bins omitted) with the four generator
    predictions, and the data-to-prediction ratio below each, so the quoted 7-39% shortfalls are visible."""
    ee, we = z["eavail_edges"], z["W_edges"]
    dea, dw = np.diff(ee)[:, None], np.diff(we)[None, :]
    fig, axs = plt.subplots(2, 2, figsize=(6.0, 4.1), sharex="col",
                            gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.06, "wspace": 0.48})
    ylab = r"cm$^2$ GeV$^{-1}$ nucleon$^{-1}$"
    for j, (edges, proj, lab, ytop) in enumerate((
            (ee, lambda a: (a * dw).sum(1), r"$E_{\mathrm{avail}}$ (GeV)", r"$d\sigma/dE_{\mathrm{avail}}$ (" + ylab + ")"),
            (we, lambda a: (a * dea).sum(0), r"$W$ (GeV)", r"$d\sigma/dW$ (" + ylab + ")"))):
        e = edges[:-1]                      # bin edges without the overflow bin
        c = 0.5 * (e[:-1] + e[1:])
        d = proj(z["hData2D"])[:-1]
        top, bot = axs[0, j], axs[1, j]
        for g in GENS:
            pg = proj(z[f"gen_{g}"])[:-1]
            top.stairs(pg, e, lw=1.4, color=COLORS[g], label=LABEL[g], baseline=None)
            bot.stairs(d / pg, e, lw=1.4, color=COLORS[g], baseline=None)
        top.plot(c, d, "o", color="#0b0b0b", ms=3.8, label="data (unfolded)", zorder=5)
        bot.axhline(1.0, color="0.5", lw=0.8)
        top.set_yscale("log"); top.set_ylabel(ytop)
        bot.set_ylabel("data / prediction"); bot.set_xlabel(lab)
        bot.set_ylim(0.8, 1.9)
    axs[0, 0].legend(frameon=False)
    fig.savefig(out / name, bbox_inches="tight", metadata=PDF_META); plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--values", type=Path, default=None, help="values.tex, for the printed \\uqMedian in Fig. 1")
    a = ap.parse_args(argv)
    uq = None
    if a.values:
        m = re.search(r"\\newcommand\{\\uqMedian\}\{([^}]*)\}", a.values.read_text())
        uq = m.group(1) if m else None
    a.outdir.mkdir(parents=True, exist_ok=True)
    style()
    z = np.load(a.npz, allow_pickle=False)
    fig1(z, a.outdir, uq); fig2(z, a.outdir); fig3(z, a.outdir)
    print("wrote", sorted(p.name for p in a.outdir.glob("fig*.pdf")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
