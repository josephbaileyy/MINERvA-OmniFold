#!/usr/bin/env python3
"""PET (point cloud) vs GBDT (scalars) unfolded-shape comparison -- the Phase-3 question.

Does unfolding on the per-hadron POINT CLOUD change the result vs the (pt,pz,eavail,q3)
SCALARS? minerva_pet_dataloader.py --save-weights saves the PET gen push weights + the mc
subsample indices; this bins the PET-reweighted truth events (by their truth_scalars from
of_inputs_pc.npz) into the 4D axes, area-normalizes the 1D projections, and overlays them on
the frozen GBDT 4D result (products/4d/xsec_4d_MEFHC_5iter_lgbm.root). Area-normalized because the PET
run is on a subsample (shape comparison, not absolute normalization).

  python pet_vs_gbdt.py --pet products/pet/pet_weights.npz --pc of_inputs_pc.npz \
      --gbdt products/4d/xsec_4d_MEFHC_5iter_lgbm.root --out products/pet/pet_vs_gbdt.png
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ROOT

ROOT.gROOT.SetBatch(True)
AXES = ["pt", "pz", "eavail", "q3"]
_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"


def _edges(h):
    ax = h.GetXaxis()
    return np.array([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])


def run_absolute(args, pc, edges, idx, w_push, wt, ptru):
    """Absolute (non-area-normalized) PET cross section, reusing the exact GBDT machinery.

    Bins the PET push weights into the 4D axes, scales the subsample back to the
    full generator (the push weights cover only a random subsample), and runs them
    through xsec_nd.extract_cross_section_nd with the same flux / POT / nucleons and the GBDT's
    own completeness (completeness depends only on MC+binning, not on the reweighting), so
    the PET result is directly comparable bin-by-bin to the frozen GBDT 4D product.
    For --closure (pseudo-data = MC reco) completeness=1 and the reference is the MC truth.
    """
    for p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
        if p not in sys.path:
            sys.path.insert(0, p)
    import unfold_2d_omnifold_unbinned as u2d  # noqa: E402
    import unfold_nd_omnifold_unbinned as und  # noqa: E402
    from xsec_nd import extract_cross_section_nd, project_axis, total_xsec  # noqa: E402

    edges_f = [np.asarray(e, float) for e in edges]
    shape = tuple(len(e) - 1 for e in edges_f)
    ts = pc["truth_scalars"][idx]                       # (N,4) truth pt,pz,eavail,q3
    m = ptru
    cols = [ts[m, 0], ts[m, 1], ts[m, 2], ts[m, 3]]
    w_unf = (w_push * wt)[m]
    unfold_nd, _ = und.histnd(cols, w_unf, edges_f)

    # The PET push weights exist only for a random subsample (mc_indices), but
    # extract_cross_section_nd divides by the FULL data POT. Scale the binned
    # truth back to the full generator (inverse sampling fraction, by prior truth
    # weight) so the absolute normalisation is comparable to the full-stats GBDT
    # result; without this sigma is low by ~N_full/N_sub.
    sub_pass_sum = float(wt[ptru].sum())
    full_pass_sum = float(pc["w_truth"][pc["pass_truth"]].sum())
    subsample_scale = full_pass_sum / sub_pass_sum
    unfold_nd *= subsample_scale

    data_pot = float(pc["data_pot"])
    n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS
    flux, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, edges_f[0])
    flux = np.asarray(flux, float)

    if args.closure:
        completeness = np.ones(shape)
    else:
        fg = ROOT.TFile.Open(args.gbdt)
        hc = fg.Get("hCompletenessND_flat")
        comp_flat = np.array([hc.GetBinContent(i + 1) for i in range(hc.GetNbinsX())])
        fg.Close()
        completeness = comp_flat.reshape(shape, order="C")

    xsec, _ = extract_cross_section_nd(unfold_nd, completeness, flux,
                                       data_pot, n_nucleons, edges_f)
    tot = total_xsec(xsec, edges_f)
    tag = "closure" if args.closure else "4D"
    print(f"[absolute] PET total sigma ({tag}) = {tot:.4g} cm^2/nucleon "
          f"(n_truthpass={int(m.sum())}, subsample_scale={subsample_scale:.3f}, "
          f"data_pot={data_pot:.4g})")

    if args.closure:
        ref_nd, _ = und.histnd(cols, wt[m], edges_f)
        ref_nd *= subsample_scale  # same scale on both sides: recovered/truth invariant
        ref_xsec, _ = extract_cross_section_nd(ref_nd, completeness, flux,
                                               data_pot, n_nucleons, edges_f)
        ref_tot = total_xsec(ref_xsec, edges_f)
        print(f"[closure] MC-truth total sigma = {ref_tot:.4g}; "
              f"recovered/truth = {tot/ref_tot:.4f}")
        print(f"{'axis':8s} closure recovered/truth median |diff|")
        for ai, nm in enumerate(AXES):
            _, yr = project_axis(xsec, edges_f, ai)
            _, yt = project_axis(ref_xsec, edges_f, ai)
            d = np.where(yt > 0, np.abs(yr - yt) / yt, 0.0)
            print(f"{nm:8s} {100*np.median(d[yt > 0]):.2f}%")
    else:
        f = ROOT.TFile.Open(args.gbdt)
        fig, axs = plt.subplots(2, 2, figsize=(11, 8))
        print(f"{'axis':8s} PET vs GBDT ABSOLUTE: median |diff|")
        for ai, (nm, axp) in enumerate(zip(AXES, axs.ravel())):
            e, y = project_axis(xsec, edges_f, ai)
            c = 0.5 * (e[:-1] + e[1:])
            hg = f.Get(f"hXSec_{nm}")
            gb = np.array([hg.GetBinContent(i + 1) for i in range(hg.GetNbinsX())])
            d = np.where(gb > 0, np.abs(y - gb) / gb, 0.0)
            print(f"{nm:8s} {100*np.median(d[gb > 0]):.2f}%")
            axp.step(c, y, where="mid", label="PET (point cloud)", lw=2)
            axp.step(c, gb, where="mid", label="GBDT (scalars)", lw=2, ls="--")
            axp.set_xlabel(nm); axp.set_ylabel("dσ/dx (cm²/nucleon)")
            axp.legend(fontsize=8); axp.set_title(f"{nm}: PET vs GBDT (absolute)")
        hgpt = f.Get("hXSec_pt"); ept = _edges(hgpt)
        gbpt = np.array([hgpt.GetBinContent(i + 1) for i in range(hgpt.GetNbinsX())])
        tot_gbdt = float((gbpt * np.diff(ept)).sum())
        f.Close()
        print(f"[absolute] GBDT total sigma = {tot_gbdt:.4g}; PET/GBDT = {tot/tot_gbdt:.4f}")
        fig.suptitle("PET (point cloud) vs GBDT (scalars): ABSOLUTE 4D cross section")
        fig.tight_layout(); fig.savefig(args.out, dpi=130)
        print(f"[OK] wrote {args.out}")

    fo = ROOT.TFile.Open(args.pet_out, "RECREATE"); fo.cd()
    ROOT.TParameter("double")("dataPOT", data_pot).Write()
    ROOT.TParameter("double")("totalXSec", tot).Write()
    und.write_thnd(fo, xsec, None, "hXSecND", "PET d^{4}#sigma", edges_f, AXES)
    for ai, nm in enumerate(AXES):
        e, y = project_axis(xsec, edges_f, ai)
        und.numpy_to_th1d(e, y, f"hXSec_{nm}", f"d#sigma/d{nm}").Write()
    fo.Close()
    print(f"[OK] wrote {args.pet_out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pet", required=True, help="minerva_pet_dataloader --save-weights npz")
    ap.add_argument("--pc", default="of_inputs_pc.npz")
    ap.add_argument("--gbdt", default="products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--out", default="products/pet/pet_vs_gbdt.png")
    ap.add_argument("--absolute", action="store_true",
                    help="produce the ABSOLUTE (non-area-normalized) PET cross section via "
                         "xsec_nd.extract_cross_section_nd + the GBDT completeness, and "
                         "compare absolute spectra/total sigma to the GBDT result.")
    ap.add_argument("--closure", action="store_true",
                    help="absolute mode on a PET closure run (pseudo-data=MC reco): "
                         "completeness=1, reference = MC truth (recovered/truth should be ~1).")
    ap.add_argument("--mcfile",
                    default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root",
                    help="MC file holding the integrated flux histogram (absolute mode).")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--pet-out", default="products/pet/xsec_4d_PET_absolute.root",
                    help="output ROOT for the absolute PET cross section (absolute mode).")
    args = ap.parse_args()

    pet = np.load(args.pet)
    pc = np.load(args.pc, allow_pickle=True)
    w_push = pet["w_push"]; idx = pet["mc_indices"]
    edges = [pc[f"edges_{i}"] for i in range(4)]
    ts = pc["truth_scalars"][idx]          # (nsub, 4) truth pt,pz,eavail,q3 of the PET subsample
    wt = pc["w_truth"][idx]
    ptru = pc["pass_truth"][idx]
    # PET unfolded truth weight = push * prior; keep truth-pass events
    m = ptru
    sample = ts[m]; w = (w_push * wt)[m]

    if args.absolute:
        run_absolute(args, pc, edges, idx, w_push, wt, ptru)
        return

    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    f = ROOT.TFile.Open(args.gbdt)
    print(f"{'axis':8s} {'PET vs GBDT shape: median |diff|':40s}")
    for ai, (nm, axp) in enumerate(zip(AXES, axs.ravel())):
        e = np.asarray(edges[ai], float)
        c = 0.5 * (e[:-1] + e[1:]); wbin = np.diff(e)
        pet_h, _ = np.histogram(sample[:, ai], bins=e, weights=w)
        pet_d = pet_h / wbin                                      # COUNT -> density dN/dx
        pet_n = pet_d / (pet_d * wbin).sum()                      # area-normalized density
        # (GBDT hXSec_* is already a density; PET must be divided by bin width too, else
        #  the wide catch bins make a count-vs-density mismatch look like a huge discrepancy)
        hg = f.Get(f"hXSec_{nm}")
        gb = np.array([hg.GetBinContent(i + 1) for i in range(hg.GetNbinsX())])
        gb_n = gb / (gb * np.diff(_edges(hg))).sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            d = np.where(gb_n > 0, np.abs(pet_n - gb_n) / gb_n, 0.0)
        print(f"{nm:8s} {100*np.median(d[gb_n>0]):.2f}%")
        axp.step(c, pet_n, where="mid", label="PET (point cloud)", lw=2)
        axp.step(c, gb_n, where="mid", label="GBDT (scalars)", lw=2, ls="--")
        axp.set_xlabel(nm); axp.set_ylabel("area-norm dσ/dx"); axp.legend(fontsize=8)
        axp.set_title(f"{nm}: PET vs GBDT (shape)")
    f.Close()
    fig.suptitle("Phase-3: does the point cloud change the unfolded shape vs scalars?")
    fig.tight_layout(); fig.savefig(args.out, dpi=130)
    print(f"[OK] wrote {args.out}")
    print("  small %/bin across axes => the point cloud reproduces the scalar GBDT result")
    print("  (no extra information captured at these features); large => the cloud matters.")


if __name__ == "__main__":
    main()
