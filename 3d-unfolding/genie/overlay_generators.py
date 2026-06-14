#!/usr/bin/env python3
"""Overlay generator predictions on the unfolded 3D OmniFold result.

Reads the unfolded result and one or more generator predictions (all in the
shared hXSec_pt / hXSec_pz / hXSec_eavail / hXSec2D schema) and draws the three
1D projections with the generators overlaid on the unfolded data estimate. The
Eavail panel is the headline: a model comparison on an axis with no published
reference.

Run in the analysis env (root_6_28):
  python overlay_generators.py \
    --unfolded ../xsec_3d_MEFHC_5iter_lgbm.root \
    --generator GENIE-CV:genie_cv_xsec3d.root \
    --out genie_vs_unfolded
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT


def th1_to_arrays(h):
    n = h.GetNbinsX()
    edges = np.array([h.GetBinLowEdge(i) for i in range(1, n + 2)])
    cen = 0.5 * (edges[:-1] + edges[1:])
    val = np.array([h.GetBinContent(i) for i in range(1, n + 1)])
    err = np.array([h.GetBinError(i) for i in range(1, n + 1)])
    return edges, cen, val, err


def load(path):
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"cannot open {path}")
    out = {ax: th1_to_arrays(f.Get(f"hXSec_{ax}")) for ax in ("pt", "pz", "eavail")}
    f.Close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unfolded", required=True)
    ap.add_argument("--generator", action="append", default=[],
                    metavar="LABEL:FILE", help="repeatable")
    ap.add_argument("--out", default="genie_vs_unfolded")
    args = ap.parse_args()

    unf = load(args.unfolded)
    gens = []
    for spec in args.generator:
        lab, _, path = spec.partition(":")
        gens.append((lab, load(path)))

    axes = [("pt", r"$p_T$ (GeV/c)", r"$d\sigma/dp_T$"),
            ("pz", r"$p_\parallel$ (GeV/c)", r"$d\sigma/dp_\parallel$"),
            ("eavail", r"$E_{\rm avail}$ (GeV)", r"$d\sigma/dE_{\rm avail}$")]
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
    colors = ["#C44E52", "#4C72B0", "#2ca02c", "#9467bd"]
    for ax, (key, xlab, ylab) in zip(axs, axes):
        edges, cen, val, err = unf[key]
        # for the eavail axis, drop the wide catch bin from the view
        sl = slice(0, len(val) - 1) if key == "eavail" else slice(0, len(val))
        ax.errorbar(cen[sl], val[sl], yerr=err[sl], fmt="o", ms=4, color="k",
                    capsize=2, label="unfolded OmniFold (this work)", zorder=5)
        for i, (lab, g) in enumerate(gens):
            ge, gc, gv, gerr = g[key]
            ax.stairs(gv[sl], np.append(edges[sl.start:sl.stop],
                                        edges[(sl.stop)]),
                      color=colors[i % len(colors)], lw=2, label=lab)
        ax.set_xlabel(xlab); ax.set_ylabel(ylab + r" (cm$^2$/.../nucleon)")
        ax.grid(alpha=0.3)
        if key == "eavail":
            ax.legend(fontsize=8)
    fig.suptitle("Unfolded 3D result vs generator predictions "
                 "(1D projections; Eavail catch bin omitted)")
    fig.tight_layout()
    out = f"{args.out}.png"
    fig.savefig(out, dpi=140)
    print(f"[overlay] wrote {out}")


if __name__ == "__main__":
    main()
