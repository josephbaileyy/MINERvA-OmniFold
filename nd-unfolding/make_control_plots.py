#!/usr/bin/env python3
"""Reco-level control plots + migration/resolution figures for the analysis note.

Two products from the CV 5D omnifile (no universe branches needed):

  products/5d/control_plots.png        -- POT-scaled reco-level data vs MC(sig+bkg)
                                          per axis (pT, pz, E_avail, q3, W), with ratio
  products/5d/migration_resolution.png -- per-axis truth-vs-reco migration map
                                          (column-normalised) + fractional resolution

Streams with RDataFrame (no event arrays in memory), so it runs on a login node.

  python make_control_plots.py [--omnifile runEventLoopOmniFold_5D_MEFHC.root]
      [--dump-arrays FILE.npz] [--from-arrays FILE.npz] [--print-style]

--dump-arrays writes every value the figures draw (histogram contents and errors, edges, migration matrices, the POT
scale) after filling; --from-arrays draws from such a file without ROOT; --print-style draws in the note's print style
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
# branch suffix per axis ("" = the bare pT branch: measured/sim/sim_background/MC)
SUFFIX = {"pt": "", "pz": "_pz", "eavail": "_eavail", "q3": "_q3", "W": "_W"}


def edges_for(ax):
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und
    if ax == "pt":
        return np.asarray(u2d.PT_EDGES, float)
    if ax == "pz":
        return np.asarray(u2d.PZ_EDGES, float)
    return np.asarray(und.EXTRA_AXES[ax]["edges"], float)


def th1_np(h):
    n = h.GetNbinsX()
    vals = np.array([h.GetBinContent(i + 1) for i in range(n)])
    errs = np.array([h.GetBinError(i + 1) for i in range(n)])
    return vals, errs


def fill(args):
    """Every value the two figures draw, from the omnifile (one RDataFrame pass)."""
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.EnableImplicitMT(16)

    f = ROOT.TFile.Open(args.omnifile)
    pot_scale = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal()
    f.Close()
    print(f"[ctrl] POT scale (data/mc) = {pot_scale:.6f}")

    d_data = ROOT.RDataFrame("data", args.omnifile).Filter("measured_pass")
    d_sig = ROOT.RDataFrame("mc_signal_reco", args.omnifile).Filter("sim_pass")
    d_bkg = ROOT.RDataFrame("mc_background", args.omnifile).Filter("sim_background_pass")

    h_data, h_sig, h_bkg, h_mig = {}, {}, {}, {}
    for ax in AXES:
        e = edges_for(ax)
        # cap the catch bin for plotting (the last edge is 100 GeV)
        model = ROOT.RDF.TH1DModel(f"h_{ax}", "", len(e) - 1, e)
        h_data[ax] = d_data.Histo1D(model, f"measured{SUFFIX[ax]}")
        h_sig[ax] = d_sig.Histo1D(model, f"sim{SUFFIX[ax]}", "w_reco")
        h_bkg[ax] = d_bkg.Histo1D(model, f"sim_background{SUFFIX[ax]}", "w_bkg")
        m2 = ROOT.RDF.TH2DModel(f"m_{ax}", "", len(e) - 1, e, len(e) - 1, e)
        h_mig[ax] = d_sig.Histo2D(m2, f"MC{SUFFIX[ax]}", f"sim{SUFFIX[ax]}", "w_reco")

    arr = {"pot_scale": np.float64(pot_scale)}
    for ax in AXES:
        e = edges_for(ax)
        n = len(e) - 1
        arr[f"edges_{ax}"] = e
        arr[f"dat_{ax}"], arr[f"derr_{ax}"] = th1_np(h_data[ax].GetValue())
        arr[f"sig_{ax}"], arr[f"serr_{ax}"] = th1_np(h_sig[ax].GetValue())
        arr[f"bkg_{ax}"], arr[f"berr_{ax}"] = th1_np(h_bkg[ax].GetValue())
        H = h_mig[ax].GetValue()
        arr[f"mig_{ax}"] = np.array([[H.GetBinContent(ix + 1, iy + 1) for iy in range(n)]
                                     for ix in range(n)])  # [truth, reco]
    return arr


def draw(arr, outdir, print_style=False):
    """The two figures from fill()'s arrays. print_style: the note's print style (sizes for the printed width)."""
    pot_scale = arr["pot_scale"]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # ---------------- control plots ----------------
    # Layout: 3+2 blocks of (spectrum + ratio), sixth cell = legend + sample tag.
    # The figure is sized close to its printed width so in-figure font sizes
    # survive the \includegraphics scaling (the old 32-inch canvas printed at
    # ~3 pt). Fills are solid step-histograms (no per-bin bar seams).
    C_SIG = technote_style.GEN_COLORS["Tune"]   # signal = the fixed Tune blue
    C_BKG = "#DD8452"                           # background = solid warm orange
    C_EDGE = "#2F4B7C"                          # stack outline (darker signal blue)
    if print_style:
        for _a in _pathlib.Path(__file__).resolve().parents:
            if (_a / "note_print_style.py").exists():
                _sys.path.insert(0, str(_a)); break
        import note_print_style
        note_print_style.apply()
        FS_LAB, FS_TICK, FS_LEG, FS_TAG, FS_NOTE = 9.3, 8.3, 8.5, 8.3, 7.5
        FIG1, MS, ELW, LWO, LWG = note_print_style.figsize(0.99, 0.86), 2.6, 0.7, 0.7, 0.5
        GS1 = dict(hspace=0.34, wspace=0.30, left=0.09, right=0.985, top=0.97, bottom=0.09)
    else:
        FS_LAB, FS_TICK, FS_LEG = 16, 14, 16
        FS_TAG, FS_NOTE = FS_LAB - 2, FS_LAB - 4
        FIG1, MS, ELW, LWO, LWG = (13.5, 9.0), 4.8, 1.1, 1.0, 0.8
        GS1 = dict(hspace=0.30, wspace=0.24, left=0.065, right=0.985, top=0.97, bottom=0.075)

    fig = plt.figure(figsize=FIG1)
    outer = fig.add_gridspec(2, 3, **GS1)
    summary = {}
    handles = None
    for i, ax in enumerate(AXES):
        gs = outer[i // 3, i % 3].subgridspec(2, 1, height_ratios=[3, 1],
                                              hspace=0.05)
        A = fig.add_subplot(gs[0])
        R = fig.add_subplot(gs[1], sharex=A)
        e = arr[f"edges_{ax}"]
        # drop the wide catch bin from the visible axis (keep it in the numbers)
        nshow = len(e) - 2 if e[-1] >= 99 else len(e) - 1
        dat, derr = arr[f"dat_{ax}"], arr[f"derr_{ax}"]
        sig, serr = arr[f"sig_{ax}"], arr[f"serr_{ax}"]
        bkg, berr = arr[f"bkg_{ax}"], arr[f"berr_{ax}"]
        mc = (sig + bkg) * pot_scale
        summary[ax] = (dat.sum(), mc.sum())
        ctr = 0.5 * (e[:-1] + e[1:])

        # step-outline arrays for the visible bins
        xs = np.repeat(e[:nshow + 1], 2)[1:-1]
        y_bkg = np.repeat((bkg * pot_scale)[:nshow], 2)
        y_tot = np.repeat(mc[:nshow], 2)
        floor = max(np.min(y_bkg[y_bkg > 0], initial=np.inf) * 0.4, 1.0)
        h_b = A.fill_between(xs, floor, np.maximum(y_bkg, floor),
                             color=C_BKG, lw=0, label="MC background")
        h_s = A.fill_between(xs, np.maximum(y_bkg, floor), y_tot,
                             color=C_SIG, lw=0, label="MC signal (MnvTune v1)")
        A.plot(xs, y_bkg, color="white", lw=LWG)      # gap between stack segments
        A.plot(xs, y_tot, color=C_EDGE, lw=LWO)       # stack outline
        h_d = A.errorbar(ctr[:nshow], dat[:nshow], yerr=derr[:nshow],
                         fmt="o", color="k", ms=MS, elinewidth=ELW,
                         zorder=5, label="Data")
        if handles is None:
            handles = [h_d, h_s, h_b]
        A.set_yscale("log")
        A.set_xlim(e[0], e[nshow])
        top = np.max([y_tot.max(), dat[:nshow].max()])
        A.set_ylim(floor, top * 2.2)
        A.tick_params(axis="both", which="major", labelsize=FS_TICK)
        plt.setp(A.get_xticklabels(), visible=False)
        if i % 3 == 0:
            A.set_ylabel("Events (POT-scaled)", fontsize=FS_LAB)

        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(mc > 0, dat / mc, np.nan)
            re = np.where(mc > 0, derr / mc, np.nan)
            rel_mc = np.where(mc > 0, pot_scale * np.hypot(serr, berr) / mc, 0.0)
        R.fill_between(xs, np.repeat(1 - rel_mc[:nshow], 2),
                       np.repeat(1 + rel_mc[:nshow], 2),
                       color="0.85", lw=0, label="MC stat.")
        R.axhline(1.0, color="0.45", lw=0.9)
        R.errorbar(ctr[:nshow], r[:nshow], yerr=re[:nshow],
                   fmt="o", color="k", ms=MS, elinewidth=ELW, zorder=5)
        R.set_ylim(0.77, 1.30)
        R.set_yticks([0.8, 1.0, 1.2])
        R.set_xlabel(LABELS[ax], fontsize=FS_LAB)
        R.tick_params(axis="both", which="major", labelsize=FS_TICK)
        if i % 3 == 0:
            R.set_ylabel("Data / MC", fontsize=FS_LAB)

    if print_style:  # the spectrum and ratio y labels of each column on one line, so that they do not overlap
        fig.align_ylabels(fig.axes)
    # sixth cell: legend + dataset tag (titles are suppressed by house style)
    ax_leg = fig.add_subplot(outer[1, 2])
    ax_leg.axis("off")
    ax_leg.legend(handles=handles, labels=[h.get_label() for h in handles],
                  loc="center", fontsize=FS_LEG, frameon=False,
                  borderaxespad=0, handlelength=1.6)
    ax_leg.text(0.5, 0.13, r"MINERvA ME FHC, $1.06\times10^{21}$ POT",
                transform=ax_leg.transAxes, ha="center", va="center",
                fontsize=FS_TAG, color="0.25")
    ax_leg.text(0.5, 0.02, "wide catch bins not drawn",
                transform=ax_leg.transAxes, ha="center", va="center",
                fontsize=FS_NOTE, color="0.45")
    out1 = os.path.join(outdir, "control_plots.png")
    fig.savefig(out1, dpi=140, bbox_inches="tight")
    plt.close(fig)
    for ax in AXES:
        d, m = summary[ax]
        print(f"[ctrl] {ax:7s} data={d:.0f} mc(sig+bkg)={m:.0f} data/mc={d/m:.4f}")
    print(f"[ctrl] wrote {out1}")

    # ---------------- migration + resolution ----------------
    if print_style:
        FIG2, F_T, F_X, F_K, F_D, F_C = note_print_style.figsize(0.99, 0.56), 9.3, 7.5, 7.0, 6.5, 7.0
        fig, axs = plt.subplots(2, 5, figsize=FIG2, layout="constrained")
    else:
        FIG2, F_T, F_X, F_K, F_D, F_C = (32, 14), 17, 16, 14, 13, 12
        fig, axs = plt.subplots(2, 5, figsize=FIG2)
    for i, ax in enumerate(AXES):
        e = arr[f"edges_{ax}"]
        n = len(e) - 1
        M = arr[f"mig_{ax}"]  # [truth, reco]
        colsum = M.sum(axis=1, keepdims=True)
        Mn = np.where(colsum > 0, M / colsum, 0.0)
        nshow = n - 1 if e[-1] >= 99 else n
        A = axs[0, i]
        im = A.imshow(Mn[:nshow, :nshow].T, origin="lower", cmap="viridis",
                      vmin=0, vmax=1, aspect="auto",
                      extent=(0, nshow, 0, nshow))
        A.plot([0, nshow], [0, nshow], "w--", lw=0.7)
        A.set_title(LABELS[ax], fontsize=F_T)
        A.set_xlabel("truth bin", fontsize=F_X)
        A.tick_params(axis="both", which="major", labelsize=F_K)
        if i == 0:
            A.set_ylabel("reco bin", fontsize=F_X)
        diag = np.diag(Mn)[:nshow]
        A.text(0.04, 0.92, f"diag median {np.median(diag):.2f}",
               color="w", fontsize=F_D, transform=A.transAxes)
        if not print_style:  # print style: one colour bar for the row, below
            cb = fig.colorbar(im, ax=A, fraction=0.046)
            cb.ax.tick_params(labelsize=F_C)
        axs[1, i].bar(np.arange(nshow) + 0.5, diag, width=0.9, color="tab:blue")
        axs[1, i].set_ylim(0, 1)
        axs[1, i].set_xlabel(f"{LABELS[ax]} truth bin", fontsize=F_X)
        axs[1, i].tick_params(axis="both", which="major", labelsize=F_K)
        if i == 0:
            axs[1, i].set_ylabel("P(reco bin = truth bin)", fontsize=F_X)
        if print_style and i == len(AXES) - 1:
            cb = fig.colorbar(im, ax=axs[0, :], fraction=0.046, pad=0.02)
            cb.ax.tick_params(labelsize=F_C)
        print(f"[mig] {ax:7s} diagonal P median={np.median(diag):.3f} "
              f"min={diag.min():.3f} max={diag.max():.3f}")
    fig.suptitle("Truth$\\to$reco migration (column-normalised; analysis binning) "
                 "and diagonal purity per truth bin", y=0.99, fontsize=18)
    out2 = os.path.join(outdir, "migration_resolution.png")
    fig.savefig(out2, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[mig] wrote {out2}")


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
        arr = fill(args)
    if args.dump_arrays:
        np.savez(args.dump_arrays, **arr)
        print(f"[ctrl] wrote {args.dump_arrays}")
    draw(arr, args.outdir, args.print_style)


if __name__ == "__main__":
    main()
