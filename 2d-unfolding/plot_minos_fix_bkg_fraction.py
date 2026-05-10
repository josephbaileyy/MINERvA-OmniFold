#!/usr/bin/env python3
"""Side-by-side 2D background-fraction heatmaps, pre-MINOS-fix vs post-fix.

Diagnostic plot for the slide deck: shows that the `IsMinosMatchMuon()`
patch (CVUniverse.h:107, 2026-04-25) brought the background fraction
from ~10% down to ~0.35% as a *bulk* effect, not concentrated in any
particular (p_T, p_||) region. This visually establishes that the
residual low-p_|| gradient seen in `MEHFC_5iter_pull_interior.png`
is NOT selection-driven.

For each playlist-1A event-loop ROOT (pre-fix, post-fix) we read the
`mc_signal_reco` and `mc_background` TTrees, fill weighted 2D histograms
on the paper binning using the reco kinematics (`sim`, `sim_pz`,
`sim_background`, `sim_background_pz`) and the per-event reweighter
weights (`w_reco`, `w_bkg`) restricted to events passing the reco
selection (`sim_pass`, `sim_background_pass`). Background fraction in a
bin is then `bkg / (bkg + signal)`.

Output: `MEHFC_5iter_minos_fix_bkg_fraction.png`.
"""
import argparse

import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
N_PT, N_PZ = len(PT_EDGES) - 1, len(PZ_EDGES) - 1

DEFAULT_PRE = "/pscratch/sd/j/josephrb/MINERvA101/Documents/runEventLoopOmniFold_1A.root"
DEFAULT_POST = "/pscratch/sd/j/josephrb/MINERvA101/Documents/runEventLoopOmniFold_1A_minos_fix.root"
DEFAULT_OUT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/MEHFC_5iter_minos_fix_bkg_fraction.png"


def fill_2d(tree, pt_branch, pz_branch, pass_branch, w_branch):
    """Sum-weighted 2D histogram on PT_EDGES x PZ_EDGES (reco selection only)."""
    h = np.zeros((N_PT, N_PZ))
    n_pass = 0
    n_total = tree.GetEntries()
    # Hand-loop in PyROOT; trees are O(1e6) entries — a few seconds each.
    tree.SetBranchStatus("*", 0)
    for b in (pt_branch, pz_branch, pass_branch, w_branch):
        tree.SetBranchStatus(b, 1)
    for i in range(n_total):
        tree.GetEntry(i)
        if not getattr(tree, pass_branch):
            continue
        pt = float(getattr(tree, pt_branch))
        pz = float(getattr(tree, pz_branch))
        w = float(getattr(tree, w_branch))
        if pt < PT_EDGES[0] or pt >= PT_EDGES[-1]:
            continue
        if pz < PZ_EDGES[0] or pz >= PZ_EDGES[-1]:
            continue
        ix = int(np.searchsorted(PT_EDGES, pt, side="right")) - 1
        iy = int(np.searchsorted(PZ_EDGES, pz, side="right")) - 1
        h[ix, iy] += w
        n_pass += 1
    tree.SetBranchStatus("*", 1)
    return h, n_pass, n_total


def load_summed(root_path):
    print(f"[load] {root_path}")
    f = ROOT.TFile.Open(root_path)
    t_sig = f.Get("mc_signal_reco")
    t_bkg = f.Get("mc_background")
    h_sig, n_sig_pass, n_sig = fill_2d(t_sig, "sim", "sim_pz", "sim_pass", "w_reco")
    print(f"  mc_signal_reco passing reco: {n_sig_pass}/{n_sig}  (sumW={h_sig.sum():.4e})")
    h_bkg, n_bkg_pass, n_bkg = fill_2d(t_bkg, "sim_background", "sim_background_pz",
                                        "sim_background_pass", "w_bkg")
    print(f"  mc_background passing reco : {n_bkg_pass}/{n_bkg}  (sumW={h_bkg.sum():.4e})")
    f.Close()
    return h_sig, h_bkg


def bkg_fraction(h_sig, h_bkg):
    denom = h_sig + h_bkg
    frac = np.where(denom > 0, h_bkg / denom, np.nan)
    overall = float(h_bkg.sum() / max(denom.sum(), 1e-30))
    return frac, overall


def draw(frac_pre, ovr_pre, frac_post, ovr_post, out):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5),
                             gridspec_kw={"wspace": 0.30})
    for ax, frac, overall, title in [
        (axes[0], frac_pre, ovr_pre,
         f"Pre-fix (educational stub)\noverall bkg = {ovr_pre*100:.2f}%"),
        (axes[1], frac_post, ovr_post,
         f"Post-fix (isMinosMatchTrack && _minos_trk_is_ok)\noverall bkg = {ovr_post*100:.2f}%"),
    ]:
        im = ax.imshow(
            frac.T, aspect="auto", origin="lower",
            cmap="magma_r", vmin=0, vmax=max(np.nanmax(frac_pre), 0.01),
            extent=[0, N_PT, 0, N_PZ])
        ax.set_xlabel("p_T bin index")
        ax.set_ylabel("p_|| bin index")
        ax.set_title(title, fontsize=10)
        cb = plt.colorbar(im, ax=ax, label="background fraction")

    fig.suptitle("Playlist 1A: background fraction by (p_T, p_||) bin "
                 "before and after MINOS-match patch",
                 fontsize=11, y=1.02)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pre", default=DEFAULT_PRE)
    ap.add_argument("--post", default=DEFAULT_POST)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    h_sig_pre, h_bkg_pre = load_summed(args.pre)
    h_sig_post, h_bkg_post = load_summed(args.post)

    frac_pre, ovr_pre = bkg_fraction(h_sig_pre, h_bkg_pre)
    frac_post, ovr_post = bkg_fraction(h_sig_post, h_bkg_post)
    print(f"\noverall background fraction: pre={ovr_pre*100:.3f}%  post={ovr_post*100:.3f}%")

    draw(frac_pre, ovr_pre, frac_post, ovr_post, args.out)


if __name__ == "__main__":
    main()
