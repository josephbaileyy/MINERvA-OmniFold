#!/usr/bin/env python3
"""Paper-Fig.-5-style selection-efficiency heatmap.

The arXiv ancillary release used here does not include the paper's Fig. 5
efficiency TH2D.  This script therefore styles this analysis's `hEff2D`
to match the paper figure as closely as possible: p|| on x, pT on y,
ROOT-like warm palette, fixed 0..1 color scale, and compact typography.
"""


import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import math

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50],
                    dtype=float)
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0],
                    dtype=float)
TAN_THETA_MAX = math.tan(math.radians(20.0))


def load_efficiency(path, hist_name="hEff2D"):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open {path}")
    h = f.Get(hist_name)
    if not h:
        raise RuntimeError(f"Missing {hist_name} in {path}")
    arr = np.zeros((len(PT_EDGES) - 1, len(PZ_EDGES) - 1), dtype=float)
    for ipt in range(arr.shape[0]):
        for ipz in range(arr.shape[1]):
            arr[ipt, ipz] = h.GetBinContent(ipt + 1, ipz + 1)
    f.Close()
    return arr


def paper_like_cmap():
    import matplotlib.colors as mcolors

    # Close to the ROOT-style blue -> cyan/green -> yellow/orange -> red
    # palette used in the paper figure, with dark blue at zero and red at one.
    colors = [
        (0.02, 0.02, 0.55),
        (0.00, 0.35, 0.95),
        (0.28, 0.80, 0.95),
        (0.66, 0.86, 0.62),
        (0.88, 0.82, 0.42),
        (0.86, 0.58, 0.25),
        (0.74, 0.08, 0.03),
    ]
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "fig5_efficiency", colors, N=256)
    cmap.set_bad("white")
    return cmap


def mask_outside_theta(eff):
    """Mask bins entirely outside theta_mu < 20 deg.

    The paper's Fig. 5 appears to keep bins that partially overlap the
    allowed angular phase space.  A bin is therefore blanked only if even
    its most favorable corner, pt_low / pz_high, violates theta < 20 deg.
    """
    masked = eff.astype(float).copy()
    for ipt in range(len(PT_EDGES) - 1):
        pt_lo = PT_EDGES[ipt]
        for ipz in range(len(PZ_EDGES) - 1):
            pz_hi = PZ_EDGES[ipz + 1]
            if pt_lo / pz_hi > TAN_THETA_MAX:
                masked[ipt, ipz] = np.nan
    return masked


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--infile", default="2d_crossSection_omnifold_MEFHC_5iter.root")
    ap.add_argument("--hist", default="hEff2D")
    ap.add_argument("--out", default="MEFHC_5iter_eff_fig5.png")
    ap.add_argument("--no-theta-mask", action="store_true",
                    help="Do not blank bins outside theta_mu < 20 deg")
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    eff = load_efficiency(args.infile, args.hist)
    if not args.no_theta_mask:
        eff = mask_outside_theta(eff)

    fig, ax = plt.subplots(figsize=(4.8, 3.8))
    mesh = ax.pcolormesh(PZ_EDGES, PT_EDGES, eff,
                         cmap=paper_like_cmap(), vmin=0.0, vmax=1.0,
                         shading="flat")

    ax.set_xlim(PZ_EDGES[0], PZ_EDGES[-1])
    ax.set_ylim(PT_EDGES[0], PT_EDGES[-1])
    ax.set_xlabel(r"True p$_{||}$ (GeV/c)", fontsize=13)
    ax.set_ylabel(r"True p$_t$ (GeV/c)", fontsize=13)
    ax.tick_params(axis="both", which="major", direction="in",
                   length=6, width=1.0, labelsize=11)
    ax.tick_params(axis="both", which="minor", direction="in",
                   length=3, width=0.8)
    ax.minorticks_on()
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)

    cbar = fig.colorbar(mesh, ax=ax, pad=0.035, fraction=0.055)
    cbar.set_label("Efficiency", fontsize=13)
    cbar.set_ticks(np.linspace(0, 1, 11))
    cbar.ax.tick_params(direction="in", length=4, labelsize=10)

    fig.tight_layout()
    fig.savefig(args.out, dpi=220)
    print(f"[OK] wrote {args.out}")


if __name__ == "__main__":
    main()
