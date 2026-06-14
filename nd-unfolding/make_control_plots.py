#!/usr/bin/env python3
"""Reco-level control plots + migration/resolution figures for the analysis note.

Two products from the CV 5D omnifile (no universe branches needed):

  products/5d/control_plots.png        -- POT-scaled reco-level data vs MC(sig+bkg)
                                          per axis (pT, pz, E_avail, q3, W), with ratio
  products/5d/migration_resolution.png -- per-axis truth-vs-reco migration map
                                          (column-normalised) + fractional resolution

Streams with RDataFrame (no event arrays in memory), so it runs on a login node.

  python make_control_plots.py [--omnifile runEventLoopOmniFold_5D_MEFHC.root]
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

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
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


def main():
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.EnableImplicitMT(16)

    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_MEFHC.root")
    ap.add_argument("--outdir", default="products/5d")
    args = ap.parse_args()

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

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # ---------------- control plots ----------------
    fig, axs = plt.subplots(2, 5, figsize=(22, 7), sharex="col",
                            gridspec_kw=dict(height_ratios=[3, 1], hspace=0.05))
    summary = {}
    for i, ax in enumerate(AXES):
        e = edges_for(ax)
        # drop the wide catch bin from the visible axis (keep it in the numbers)
        nshow = len(e) - 2 if e[-1] >= 99 else len(e) - 1
        dat, derr = th1_np(h_data[ax].GetValue())
        sig, _ = th1_np(h_sig[ax].GetValue())
        bkg, _ = th1_np(h_bkg[ax].GetValue())
        mc = (sig + bkg) * pot_scale
        summary[ax] = (dat.sum(), mc.sum())
        ctr = 0.5 * (e[:-1] + e[1:])
        wid = np.diff(e)
        A = axs[0, i]
        A.bar(ctr[:nshow], (bkg * pot_scale)[:nshow], width=wid[:nshow],
              color="tab:orange", alpha=0.7, label="MC background")
        A.bar(ctr[:nshow], (sig * pot_scale)[:nshow], width=wid[:nshow],
              bottom=(bkg * pot_scale)[:nshow], color="tab:blue", alpha=0.55,
              label="MC signal (MnvTune v1)")
        A.errorbar(ctr[:nshow], dat[:nshow], yerr=derr[:nshow], fmt="ko",
                   ms=3.5, label="Data")
        A.set_yscale("log")
        A.set_title(LABELS[ax])
        if i == 0:
            A.set_ylabel("events (POT-scaled)")
            A.legend(fontsize=8)
        R = axs[1, i]
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(mc > 0, dat / mc, np.nan)
            re = np.where(mc > 0, derr / mc, np.nan)
        R.errorbar(ctr[:nshow], r[:nshow], yerr=re[:nshow], fmt="ko", ms=3.5)
        R.axhline(1.0, color="gray", lw=0.8)
        R.set_ylim(0.75, 1.25)
        R.set_xlabel(LABELS[ax])
        if i == 0:
            R.set_ylabel("data / MC")
    fig.suptitle("Reco-level control distributions, ME FHC (selection of the analysis; "
                 "wide catch bins not drawn)", y=0.98)
    out1 = os.path.join(args.outdir, "control_plots.png")
    fig.savefig(out1, dpi=140, bbox_inches="tight")
    plt.close(fig)
    for ax in AXES:
        d, m = summary[ax]
        print(f"[ctrl] {ax:7s} data={d:.0f} mc(sig+bkg)={m:.0f} data/mc={d/m:.4f}")
    print(f"[ctrl] wrote {out1}")

    # ---------------- migration + resolution ----------------
    fig, axs = plt.subplots(2, 5, figsize=(22, 8))
    for i, ax in enumerate(AXES):
        e = edges_for(ax)
        n = len(e) - 1
        H = h_mig[ax].GetValue()
        M = np.array([[H.GetBinContent(ix + 1, iy + 1) for iy in range(n)]
                      for ix in range(n)])  # [truth, reco]
        colsum = M.sum(axis=1, keepdims=True)
        Mn = np.where(colsum > 0, M / colsum, 0.0)
        nshow = n - 1 if e[-1] >= 99 else n
        A = axs[0, i]
        im = A.imshow(Mn[:nshow, :nshow].T, origin="lower", cmap="viridis",
                      vmin=0, vmax=1, aspect="auto",
                      extent=(0, nshow, 0, nshow))
        A.plot([0, nshow], [0, nshow], "w--", lw=0.7)
        A.set_title(LABELS[ax])
        A.set_xlabel("truth bin")
        if i == 0:
            A.set_ylabel("reco bin")
        diag = np.diag(Mn)[:nshow]
        A.text(0.04, 0.92, f"diag median {np.median(diag):.2f}",
               color="w", fontsize=8, transform=A.transAxes)
        fig.colorbar(im, ax=A, fraction=0.046)
        axs[1, i].bar(np.arange(nshow) + 0.5, diag, width=0.9, color="tab:blue")
        axs[1, i].set_ylim(0, 1)
        axs[1, i].set_xlabel(f"{LABELS[ax]} truth bin")
        if i == 0:
            axs[1, i].set_ylabel("P(reco bin = truth bin)")
        print(f"[mig] {ax:7s} diagonal P median={np.median(diag):.3f} "
              f"min={diag.min():.3f} max={diag.max():.3f}")
    fig.suptitle("Truth$\\to$reco migration (column-normalised; analysis binning) "
                 "and diagonal purity per truth bin", y=0.99)
    out2 = os.path.join(args.outdir, "migration_resolution.png")
    fig.savefig(out2, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[mig] wrote {out2}")


if __name__ == "__main__":
    main()
