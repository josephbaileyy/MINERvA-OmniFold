#!/usr/bin/env python3
"""Localize the high-E_avail excess in W: unfolded data vs the GENIE CV prediction.

Open question 6 is a +2.2 sigma excess in the high-E_avail region of the unfolded data
relative to the generator prediction. With W (hadronic invariant mass) now a validated 5th
OmniFold axis, this script tests *where in W* that excess sits -- i.e. whether the missing
strength is a high-W (deep-inelastic) modeling deficit.

Method (reuses the EXACT unfold normalization, no re-unfolding):
  * unfolded data d^5 sigma  : read hXSecND_flat from the frozen 5D product and reshape.
  * GENIE CV prediction      : the generator's own true cross section = the POT-scaled
    mc_truth_denom spectrum (full truth phase space, so completeness == 1) pushed through
    the SAME xsec_nd.extract_cross_section_nd with the SAME flux / POT / nucleons / edges.
    (mc_truth_denom IS the GENIE CV model OmniFold starts from -- the prior.)
  * both are marginalized to (E_avail, W) via project_marginal and compared bin-by-bin:
    ratio = data/CV, excess = data - CV, and the W-breakdown of the excess within each
    E_avail band.

This is the data-vs-generator analog of the 3D generator-band test, restricted to the CV
generator and the new (E_avail, W) plane. Extending it to NuWro/GiBUU needs those generators
run through the W observable (a separate, larger effort) -- see 3d-unfolding/genie/.

  python excess_eavail_W.py            # defaults to the frozen 5D product + omnifile
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import ROOT  # noqa: E402
import unfold_2d_omnifold_unbinned as u2d  # noqa: E402
import unfold_nd_omnifold_unbinned as und  # noqa: E402
from xsec_nd import extract_cross_section_nd, project_marginal, project_axis  # noqa: E402

ROOT.gROOT.SetBatch(True)


def build_gen_prediction(omnifile, axis_names, edges, verbose=True):
    """GENIE CV true cross section in the 5D binning, from mc_truth_denom."""
    f = ROOT.TFile.Open(omnifile, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {omnifile}")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS
    pt_edges = u2d.PT_EDGES
    flux_bins, _ = u2d.load_flux_bins(f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root",
                                      "pTmu_reweightedflux_integrated", pt_edges)
    pt_lo, pt_hi = pt_edges[0], pt_edges[-1]
    pz_lo, pz_hi = u2d.PZ_EDGES[0], u2d.PZ_EDGES[-1]

    # truth branches for (pt, pz, *extras): driver convention
    extras = [dict(und.EXTRA_AXES[a], name=a) for a in axis_names]
    br = ["MC", "MC_pz"] + [ax["truth"] for ax in extras] + ["w_truth"]
    t = f.Get("mc_truth_denom")
    cols = ROOT.RDataFrame(t).AsNumpy(br)
    pt = cols["MC"].astype(float); pz = cols["MC_pz"].astype(float)
    ex = [cols[ax["truth"]].astype(float) for ax in extras]
    w = cols["w_truth"].astype(float)

    # gate (rectangle + theta_mu<20deg) + finiteness + sane weight, vectorized to match
    # collect_truth_denom_nd exactly
    finite = np.isfinite(pt) & np.isfinite(pz) & np.isfinite(w) & (w >= 0) & (w < 1e4)
    for a in ex:
        finite &= np.isfinite(a)
    theta = np.arctan2(pt, pz)
    gate = (pt >= pt_lo) & (pt <= pt_hi) & (pz >= pz_lo) & (pz <= pz_hi) \
        & (theta < u2d.MAX_MUON_THETA_RAD)
    keep = finite & gate
    if verbose:
        print(f"[gen] truth_denom kept={keep.sum()} / {keep.size} "
              f"(dropped {(~keep).sum()}); pot_scale={pot_scale:.6g}")

    cols_nd = [pt[keep], pz[keep]] + [a[keep] for a in ex]
    denom_nd, _ = und.histnd(cols_nd, w[keep] * pot_scale, edges)
    gen_xsec, _ = extract_cross_section_nd(denom_nd, np.ones_like(denom_nd),
                                           np.asarray(flux_bins, float),
                                           data_pot, n_nucleons, edges)
    f.Close()
    return gen_xsec


def load_data_xsec(xsec5d, shape):
    f = ROOT.TFile.Open(xsec5d, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {xsec5d}")
    h = f.Get("hXSecND_flat")
    flat = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    return flat.reshape(shape)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_MEFHC.root")
    ap.add_argument("--xsec5d", default="products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--axes", default="eavail,q3,W")
    ap.add_argument("--out", default="products/5d/excess_eavail_W.root")
    ap.add_argument("--png", default="products/5d/excess_eavail_W.png")
    args = ap.parse_args()

    axis_names = [a.strip() for a in args.axes.split(",")]
    extras = [dict(und.EXTRA_AXES[a], name=a) for a in axis_names]
    edges = [u2d.PT_EDGES, u2d.PZ_EDGES] + [ax["edges"] for ax in extras]
    shape = tuple(len(e) - 1 for e in edges)
    # axis indices in the 5D tensor: 0 pt, 1 pz, 2 eavail, 3 q3, 4 W
    i_eav = 2 + axis_names.index("eavail")
    i_W = 2 + axis_names.index("W")
    eav_e = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
    W_e = np.asarray(und.EXTRA_AXES["W"]["edges"], float)

    data_xsec = load_data_xsec(args.xsec5d, shape)
    gen_xsec = build_gen_prediction(args.omnifile, axis_names, edges)

    # marginalize both to (eavail, W): drop every other axis
    drop = [a for a in range(len(edges)) if a not in (i_eav, i_W)]
    md = project_marginal(data_xsec, edges, drop_axes=drop)   # dsigma/(deav dW)
    mg = project_marginal(gen_xsec, edges, drop_axes=drop)
    # ensure (eavail, W) order
    if i_eav > i_W:
        md, mg = md.T, mg.T
    dvol = np.outer(np.diff(eav_e), np.diff(W_e))
    sig_d = md * dvol     # sigma per (eavail, W) cell
    sig_g = mg * dvol
    tot_d, tot_g = sig_d.sum(), sig_g.sum()

    # 1D dsigma/dEavail (integrate W too) -- the open-question-6 projection
    e_eav, y_eav_d = project_axis(data_xsec, edges, i_eav)
    _, y_eav_g = project_axis(gen_xsec, edges, i_eav)
    sd_eav = y_eav_d * np.diff(e_eav)   # sigma per eavail band
    sg_eav = y_eav_g * np.diff(e_eav)

    print(f"\n[total] data={tot_d:.4e}  GENIE-CV={tot_g:.4e}  data/CV={tot_d/tot_g:.4f}")
    print(f"\n=== dsigma/dEavail: data vs GENIE CV (open question 6) ===")
    print(f"  {'Eavail band':14s} {'data':>11s} {'CV':>11s} {'data/CV':>9s} {'excess(=d-CV)':>13s} {'%oftot_excess':>13s}")
    exc_eav = sd_eav - sg_eav
    tot_exc = exc_eav[exc_eav > 0].sum()
    for i in range(len(sd_eav)):
        frac = 100 * exc_eav[i] / tot_exc if tot_exc > 0 else 0.0
        print(f"  {eav_e[i]:.1f}-{eav_e[i+1]:<8.1f} {sd_eav[i]:11.3e} {sg_eav[i]:11.3e} "
              f"{sd_eav[i]/sg_eav[i]:9.3f} {exc_eav[i]:+13.3e} {frac:12.1f}%")

    print(f"\n=== WHERE the excess lives in W (data/CV ratio per E_avail x W cell) ===")
    hdr = "  eav\\W      " + "".join(f"{W_e[j]:>4.1f}-{W_e[j+1]:>5.1f} " for j in range(len(W_e)-1))
    print(hdr)
    for i in range(sig_d.shape[0]):
        row = "".join(
            f"{(sig_d[i,j]/sig_g[i,j]) if sig_g[i,j]>0 else float('nan'):>10.2f} "
            for j in range(sig_d.shape[1]))
        print(f"  {eav_e[i]:.1f}-{eav_e[i+1]:<5.1f}{row}")

    print(f"\n=== excess sigma (data-CV) per cell, % of total POSITIVE excess ===")
    exc = sig_d - sig_g
    pos = exc[exc > 0].sum()
    print(hdr)
    for i in range(exc.shape[0]):
        row = "".join(f"{100*exc[i,j]/pos:>10.1f} " if pos > 0 else "      nan " for j in range(exc.shape[1]))
        print(f"  {eav_e[i]:.1f}-{eav_e[i+1]:<5.1f}{row}")
    # high-Eavail (>=0.8) fraction of positive excess, and its W>1.8 share
    hi = eav_e[:-1] >= 0.8
    exc_hi = exc[hi]
    hi_pos = exc_hi[exc_hi > 0].sum()
    W_hi = W_e[:-1] >= 1.8
    hi_highW = exc_hi[:, W_hi][exc_hi[:, W_hi] > 0].sum()
    print(f"\n[summary] high-Eavail (>=0.8 GeV) carries {100*hi_pos/pos:.1f}% of the positive excess;")
    print(f"          of THAT, {100*hi_highW/hi_pos:.1f}% sits at W>=1.8 GeV (DIS/transition).")

    # --- plot ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axx = plt.subplots(1, 3, figsize=(16, 4.6))
    # (a) dsigma/dEavail data vs CV
    ec = 0.5 * (e_eav[:-1] + e_eav[1:])
    axx[0].step(range(len(y_eav_d)), y_eav_d, where="mid", label="unfolded data")
    axx[0].step(range(len(y_eav_g)), y_eav_g, where="mid", ls="--", label="GENIE CV")
    axx[0].set_yscale("log"); axx[0].set_xlabel("E_avail bin"); axx[0].set_ylabel("dsigma/dEavail")
    axx[0].set_title("data vs GENIE CV (E_avail)"); axx[0].legend()
    # (b) data/CV ratio heatmap
    im1 = axx[1].imshow(sig_d / np.where(sig_g > 0, sig_g, np.nan), origin="lower",
                        aspect="auto", cmap="RdBu_r", vmin=0.5, vmax=1.5)
    axx[1].set_title("data/CV ratio  (E_avail x W)")
    axx[1].set_xlabel("W bin"); axx[1].set_ylabel("E_avail bin"); fig.colorbar(im1, ax=axx[1])
    # (c) excess sigma heatmap
    im2 = axx[2].imshow(exc, origin="lower", aspect="auto", cmap="RdBu_r",
                        vmin=-np.abs(exc).max(), vmax=np.abs(exc).max())
    axx[2].set_title("excess sigma  (data - CV)")
    axx[2].set_xlabel("W bin"); axx[2].set_ylabel("E_avail bin"); fig.colorbar(im2, ax=axx[2])
    technote_style.minerva_tag(axx[0])
    fig.tight_layout(); fig.savefig(args.png, dpi=110)
    print(f"\n[OK] wrote {args.png}")

    # --- root ---
    fo = ROOT.TFile.Open(args.out, "RECREATE"); fo.cd()
    def _th2(name, arr, title):
        h = u2d.make_th2d(name, title, list(eav_e), list(W_e))
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                h.SetBinContent(i + 1, j + 1, float(arr[i, j]))
        h.Write()
    _th2("hData2D", md, "unfolded data dsigma/(dEavail dW);Eavail (GeV);W (GeV)")
    _th2("hGenCV2D", mg, "GENIE CV dsigma/(dEavail dW);Eavail (GeV);W (GeV)")
    _th2("hExcess2D", exc, "excess sigma (data-CV);Eavail (GeV);W (GeV)")
    fo.Close()
    print(f"[OK] wrote {args.out}")


if __name__ == "__main__":
    main()
