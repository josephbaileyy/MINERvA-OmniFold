#!/usr/bin/env python3
"""Reco-level corner plot: pairwise correlations of the five observables.

Advisor request on the control-distribution figure (sec_experiment): show the
correlations between the observables, not just the marginals. Lower triangle =
POT-scaled MC (signal+background) pairwise density with the weighted Pearson r
for MC and the unweighted r for data annotated; diagonal = the 1D marginals
(data points over MC), duplicating the control figure at thumbnail size so the
corner is self-contained.

Correlations and densities are computed inside the plotted range (wide catch
bins dropped, as in the control figure).

  python plot_control_corner.py [--omnifile runEventLoopOmniFold_5D_MEFHC.root]

Writes products/5d/control_corner.png and .pdf.

--dump-arrays writes every value the figure draws (each panel's histogram contents and the two Pearson r) after
filling; --from-arrays draws from such a file without ROOT; --print-style draws in the note's print style
(note_print_style.py; director 2026-11-13). With none of them the output is unchanged.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os
import sys

import numpy as np

# OI-136: root derived from __file__, never the hardcoded cluster root
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

AXES = ["pt", "pz", "eavail", "q3", "W"]
LABELS = {"pt": r"$p_T$ (GeV/c)", "pz": r"$p_\parallel$ (GeV/c)",
          "eavail": r"$E_{\mathrm{avail}}$ (GeV)", "q3": r"$q_3$ (GeV)", "W": r"$W$ (GeV)"}
SUFFIX = {"pt": "", "pz": "_pz", "eavail": "_eavail", "q3": "_q3", "W": "_W"}


def edges_for(ax):
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und
    if ax == "pt":
        return np.asarray(u2d.PT_EDGES, float)
    if ax == "pz":
        return np.asarray(u2d.PZ_EDGES, float)
    return np.asarray(und.EXTRA_AXES[ax]["edges"], float)


def show_edges(ax):
    """Plotted edges: drop the wide catch bin, as in the control figure."""
    e = edges_for(ax)
    return e[:-1] if e[-1] >= 99 else e


def wpearson(x, y, w):
    """Weighted Pearson correlation."""
    sw = w.sum()
    mx, my = (w * x).sum() / sw, (w * y).sum() / sw
    cxy = (w * (x - mx) * (y - my)).sum() / sw
    sx = np.sqrt((w * (x - mx) ** 2).sum() / sw)
    sy = np.sqrt((w * (y - my) ** 2).sum() / sw)
    return cxy / (sx * sy)


def load(args):
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.EnableImplicitMT(16)

    f = ROOT.TFile.Open(args.omnifile)
    pot_scale = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal()
    f.Close()
    print(f"[corner] POT scale (data/mc) = {pot_scale:.6f}")

    def grab(tree, prefix, passcol, wcol):
        d = ROOT.RDataFrame(tree, args.omnifile).Filter(passcol)
        cols = [f"{prefix}{SUFFIX[a]}" for a in AXES] + ([wcol] if wcol else [])
        arr = d.AsNumpy(cols)
        out = {a: arr[f"{prefix}{SUFFIX[a]}"] for a in AXES}
        out["w"] = arr[wcol] if wcol else np.ones_like(out["pt"])
        return out

    data = grab("data", "measured", "measured_pass", None)
    sig = grab("mc_signal_reco", "sim", "sim_pass", "w_reco")
    bkg = grab("mc_background", "sim_background", "sim_background_pass", "w_bkg")
    mc = {a: np.concatenate([sig[a], bkg[a]]) for a in AXES}
    mc["w"] = np.concatenate([sig["w"], bkg["w"]]) * pot_scale
    print(f"[corner] data {len(data['pt']):,}  mc(sig+bkg) {len(mc['pt']):,} rows")
    return data, mc


def panels(data, mc):
    """Every value the corner figure draws: per panel, its histogram(s) and, below the diagonal, the two Pearson r."""
    arr = {}
    n = len(AXES)
    for a in AXES:
        arr[f"edges_{a}"] = show_edges(a)
    for i in range(n):
        for j in range(i + 1):
            ax_x, ax_y = AXES[j], AXES[i]
            ex = arr[f"edges_{ax_x}"]
            if i == j:
                arr[f"hm_{ax_x}"], _ = np.histogram(mc[ax_x], bins=ex, weights=mc["w"])
                arr[f"hd_{ax_x}"], _ = np.histogram(data[ax_x], bins=ex)
            else:
                ey = arr[f"edges_{ax_y}"]
                inw_mc = ((mc[ax_x] >= ex[0]) & (mc[ax_x] < ex[-1]) &
                          (mc[ax_y] >= ey[0]) & (mc[ax_y] < ey[-1]))
                inw_d = ((data[ax_x] >= ex[0]) & (data[ax_x] < ex[-1]) &
                         (data[ax_y] >= ey[0]) & (data[ax_y] < ey[-1]))
                arr[f"H_{ax_x}_{ax_y}"], _, _ = np.histogram2d(mc[ax_x][inw_mc], mc[ax_y][inw_mc],
                                                               bins=[ex, ey], weights=mc["w"][inw_mc])
                arr[f"rmc_{ax_x}_{ax_y}"] = np.float64(wpearson(mc[ax_x][inw_mc], mc[ax_y][inw_mc],
                                                                mc["w"][inw_mc]))
                arr[f"rd_{ax_x}_{ax_y}"] = np.float64(wpearson(data[ax_x][inw_d], data[ax_y][inw_d],
                                                               data["w"][inw_d]))
    return arr


def draw(arr, outdir, print_style=False):
    """The corner figure from panels()' arrays. print_style: the note's print style (sizes for the printed width)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    from matplotlib.ticker import MaxNLocator

    n = len(AXES)
    if print_style:
        for _a in _pathlib.Path(__file__).resolve().parents:
            if (_a / "note_print_style.py").exists():
                _sys.path.insert(0, str(_a)); break
        import note_print_style
        note_print_style.apply()
        FIGC, MSC, F_LEG, F_R, F_LAB, F_TK = note_print_style.figsize(0.92, 0.94), 1.6, 8.3, 6.5, 8.3, 7.0
    else:
        FIGC, MSC, F_LEG, F_R, F_LAB, F_TK = (3.2 * n, 3.0 * n), 2.5, 8, 9, 11, None
    fig, axs = plt.subplots(n, n, figsize=FIGC)
    for i in range(n):          # row = y variable
        for j in range(n):      # col = x variable
            A = axs[i, j]
            if j > i:
                A.set_visible(False)
                continue
            ax_x, ax_y = AXES[j], AXES[i]
            ex = arr[f"edges_{ax_x}"]
            if F_TK is not None:
                A.tick_params(which="both", labelsize=F_TK)
            if i == j:
                # diagonal: 1D marginal, data over MC
                hm, hd = arr[f"hm_{ax_x}"], arr[f"hd_{ax_x}"]
                ctr, wid = 0.5 * (ex[:-1] + ex[1:]), np.diff(ex)
                A.bar(ctr, hm, width=wid, color="tab:blue", alpha=0.55,
                      label="MC (sig+bkg)")
                A.errorbar(ctr, hd, yerr=np.sqrt(hd), fmt="ko", ms=MSC,
                           label="Data")
                A.set_yscale("log")
                if i == 0 and print_style:  # in the empty upper triangle, so that it covers no data
                    fig.legend(*A.get_legend_handles_labels(), fontsize=F_LEG, loc="upper right",
                               bbox_to_anchor=(0.97, 0.95), frameon=False)
                elif i == 0:
                    A.legend(fontsize=F_LEG, loc="upper right")
            else:
                ey = arr[f"edges_{ax_y}"]
                H = arr[f"H_{ax_x}_{ax_y}"]
                pos = H[H > 0]
                A.pcolormesh(ex, ey, H.T, cmap=technote_style.SEQ_CMAP,
                             norm=LogNorm(vmin=pos.min(), vmax=pos.max()))
                r_mc, r_d = arr[f"rmc_{ax_x}_{ax_y}"], arr[f"rd_{ax_x}_{ax_y}"]
                A.text(0.97, 0.95,
                       f"$r_{{\\rm MC}}$={r_mc:+.2f}\n$r_{{\\rm data}}$={r_d:+.2f}",
                       transform=A.transAxes, ha="right", va="top", fontsize=F_R,
                       bbox=dict(fc="white", alpha=0.75, ec="none"))
                print(f"[corner] {ax_y:7s} vs {ax_x:7s}  r_mc={r_mc:+.3f}  "
                      f"r_data={r_d:+.3f}")
            if i == n - 1:
                A.set_xlabel(LABELS[ax_x], fontsize=F_LAB)
                # prune the shared-boundary ticks so adjacent panels' end/start
                # numbers (e.g. p_|| "60" | E_avail "0") don't collide under the
                # tight wspace of a corner grid
                A.xaxis.set_major_locator(MaxNLocator(nbins=4, prune="both"))
            else:
                A.tick_params(labelbottom=False)
            if j == 0 and i > 0:
                A.set_ylabel(LABELS[ax_y], fontsize=F_LAB)
                A.yaxis.set_major_locator(MaxNLocator(nbins=4, prune="both"))
            elif j > 0:
                # which="both": the diagonal marginals are sub-decade log axes
                # whose MINOR tick labels (2x10^5, 3x10^5, ...) otherwise survive
                # the default labelleft=False (which="major") and bleed left into
                # the neighbouring panel's r-annotation box.
                A.tick_params(which="both", labelleft=False)
    fig.subplots_adjust(hspace=0.06, wspace=0.06)
    technote_style.minerva_tag(axs[0, 0])

    base = os.path.join(outdir, "control_corner")
    fig.savefig(base + ".png", dpi=140, bbox_inches="tight")
    fig.savefig(base + ".pdf", bbox_inches="tight")
    print(f"[corner] wrote {base}.png / .pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_MEFHC.root")
    ap.add_argument("--outdir", default="products/5d")
    ap.add_argument("--dump-arrays", default=None, help="write every drawn value to this .npz after filling")
    ap.add_argument("--from-arrays", default=None, help="draw from this .npz (no ROOT)")
    ap.add_argument("--print-style", action="store_true", help="draw in the note's print style")
    args = ap.parse_args()
    if args.from_arrays:
        with np.load(args.from_arrays, allow_pickle=False) as z:
            arr = {k: z[k] for k in z.files}
    else:
        data, mc = load(args)
        arr = panels(data, mc)
    if args.dump_arrays:
        np.savez(args.dump_arrays, **arr)
        print(f"[corner] wrote {args.dump_arrays}")
    draw(arr, args.outdir, args.print_style)


if __name__ == "__main__":
    main()
