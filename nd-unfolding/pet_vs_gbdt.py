#!/usr/bin/env python3
"""PET (point cloud) vs GBDT (scalars) unfolded-shape comparison -- the Phase-3 question.

Does unfolding on the per-hadron POINT CLOUD change the result vs the (pt,pz,eavail,q3)
SCALARS? minerva_pet_dataloader.py --save-weights saves the PET gen push weights + the mc
subsample indices; this bins the PET-reweighted truth events (by their truth_scalars from
of_inputs_pc.npz) into the 4D axes, area-normalizes the 1D projections, and overlays them on
the frozen GBDT 4D result (xsec_4d_MEFHC_5iter_lgbm.root). Area-normalized because the PET
run is on a subsample (shape comparison, not absolute normalization).

  python pet_vs_gbdt.py --pet pet_weights.npz --pc of_inputs_pc.npz \
      --gbdt xsec_4d_MEFHC_5iter_lgbm.root --out pet_vs_gbdt.png
"""
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ROOT

ROOT.gROOT.SetBatch(True)
AXES = ["pt", "pz", "eavail", "q3"]


def _edges(h):
    ax = h.GetXaxis()
    return np.array([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pet", required=True, help="minerva_pet_dataloader --save-weights npz")
    ap.add_argument("--pc", default="of_inputs_pc.npz")
    ap.add_argument("--gbdt", default="xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--out", default="pet_vs_gbdt.png")
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
