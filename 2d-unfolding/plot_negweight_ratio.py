#!/usr/bin/env python3
"""Per-bin negative-weight / binned-purity cross-section ratio (App. negweight).

Reads the matched-seed 2D unfolds (hXSec2D) produced by
unfold_2d_omnifold_unbinned.py with --bkg-mode {purity,negweight}, forms the
per-bin ratio, and draws it as a (p_||, p_T) heatmap with the technote diverging
colormap centered at unity. Bins where the purity cross section is negligible
are blanked. Output goes straight into the note's figures/ directory as a PDF.
"""
import sys as _sys
import pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

DEF = "HANDOFF_bkg_negweight/runs"
OUT = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/analysis-note/"
       "figures/negweight_ratio_2d.pdf")


def load(path, hname="hXSec2D"):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open {path}")
    h = f.Get(hname)
    if not h:
        raise RuntimeError(f"Missing {hname} in {path}")
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    arr = np.array([[h.GetBinContent(ix + 1, iy + 1)
                     for iy in range(ny)] for ix in range(nx)], dtype=float)
    xedges = np.array([h.GetXaxis().GetBinLowEdge(i + 1) for i in range(nx)]
                      + [h.GetXaxis().GetBinUpEdge(nx)], dtype=float)
    yedges = np.array([h.GetYaxis().GetBinLowEdge(i + 1) for i in range(ny)]
                      + [h.GetYaxis().GetBinUpEdge(ny)], dtype=float)
    f.Close()
    return arr, xedges, yedges  # arr[ipt, ipz], x=pT edges, y=pz edges


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--est", default="hist", help="estimator tag (hist|exact)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    pur, ptx, pzy = load(f"{DEF}/2d_xsec_purity_seed{args.seed}_{args.est}5.root")
    neg, _, _ = load(f"{DEF}/2d_xsec_negweight_seed{args.seed}_{args.est}5.root")

    floor = 1e-3 * pur.max()
    ratio = np.where(pur > floor, neg / np.where(pur > floor, pur, 1.0), np.nan)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    # arr is [ipt, ipz]; plot p_|| (pz) on x, p_T on y.
    fig, ax = plt.subplots(figsize=(4.8, 3.8))
    norm = TwoSlopeNorm(vmin=0.85, vcenter=1.0, vmax=1.15)
    mesh = ax.pcolormesh(pzy, ptx, np.ma.masked_invalid(ratio),
                         cmap=technote_style.DIV_CMAP, norm=norm,
                         shading="flat")
    ax.set_xlim(pzy[0], pzy[-1])
    ax.set_ylim(ptx[0], ptx[-1])
    ax.set_xlabel(r"p$_{||}$ (GeV/c)", fontsize=13)
    ax.set_ylabel(r"p$_T$ (GeV/c)", fontsize=13)
    ax.tick_params(axis="both", which="major", direction="in",
                   length=6, width=1.0, labelsize=11)
    ax.minorticks_on()

    cbar = fig.colorbar(mesh, ax=ax, pad=0.035, fraction=0.055,
                        extend="both")
    cbar.set_label("negative-weight / purity", fontsize=12)
    cbar.ax.tick_params(direction="in", length=4, labelsize=10)

    fig.tight_layout()
    fig.savefig(args.out, dpi=220)
    n_ok = int(np.isfinite(ratio).sum())
    print(f"[OK] wrote {args.out}  ({n_ok} populated bins, "
          f"median={np.nanmedian(ratio):.4f}, "
          f"min={np.nanmin(ratio):.4f}, max={np.nanmax(ratio):.4f})")


if __name__ == "__main__":
    main()
