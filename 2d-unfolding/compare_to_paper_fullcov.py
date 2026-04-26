#!/usr/bin/env python3
"""Compare full-stats 2D OmniFold result to arXiv:2106.16210 with the
paper's published covariance matrix.

The paper's ancillary data release (arXiv:2106.16210v4/anc) provides
the measured cross section as a TH2D and four TMatrixT<double>
covariance matrices: Total, StatOnly, Flux, MuonEnergyScale — all with
bin axes p||(16) × pt(14) and global indexing (Ptbin-1)*16 + (P||bin-1).

Reports chi^2/ndf against our OmniFold result (`hXSec2D` in
`2d_crossSection_omnifold_MEHFC_5iter.root`) for each covariance, plus
per-bin pulls. Unreported bins (zero diagonal in StatOnlyCov) are
dropped from both sides and the covariance inverted via pseudo-inverse
on the reduced block.
"""
import argparse
import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ANC_DIR = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc"
DEFAULT_OURS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/2d_crossSection_omnifold_MEHFC_5iter.root"
DEFAULT_OUT_PREFIX = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/compare_MEHFC_paper"

# Paper's global index: GlobalID = (Ptbin - 1) * 16 + (P||bin - 1)
# Ptbin runs 1..14, P||bin runs 1..16  →  N = 14*16 = 224 bins.
N_PT = 14
N_PZ = 16
N = N_PT * N_PZ


def tmatrix_to_numpy(tm):
    n = tm.GetNrows()
    arr = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            arr[i, j] = tm(i, j)
    return arr


def flatten_th2d(h):
    """Paper convention: x = p||bin (1..16), y = pt bin (1..14); but
    paper's TH2D is stored as pt_pl_cross_section with:
      x-axis labelled Pt, y-axis labelled P||  (TBD — check at load).
    We look it up from axis titles to be safe."""
    xt = (h.GetXaxis().GetTitle() or "").lower()
    yt = (h.GetYaxis().GetTitle() or "").lower()
    nx = h.GetNbinsX()
    ny = h.GetNbinsY()
    print(f"[paper TH2D] xaxis='{xt}' (nbinsX={nx})  yaxis='{yt}' (nbinsY={ny})")

    v = np.zeros(N)
    # Determine which axis is pt. Paper binning: 14 pt, 16 p||.
    # The paper convention says global = (ptbin-1)*16 + (pzbin-1).
    x_is_pt = (nx == N_PT)
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            if x_is_pt:
                ptb, pzb = ix, iy
            else:
                ptb, pzb = iy, ix
            gid = (ptb - 1) * N_PZ + (pzb - 1)
            v[gid] = h.GetBinContent(ix, iy)
    return v


def flatten_ours(h):
    """Our hXSec2D: x = pt (14), y = p|| (16)."""
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    assert nx == N_PT and ny == N_PZ, f"ours shape: {nx}x{ny}"
    v = np.zeros(N)
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            gid = (ix - 1) * N_PZ + (iy - 1)
            v[gid] = h.GetBinContent(ix, iy)
    return v


def chi2_with_cov(diff, cov, tag, report=True):
    """Restrict to bins with positive diagonal (reported), then invert."""
    diag = np.diag(cov)
    mask = diag > 0
    n_keep = int(mask.sum())
    d = diff[mask]
    C = cov[np.ix_(mask, mask)]
    # Use pseudo-inverse for robustness (paper's cov may be near-singular)
    Cinv = np.linalg.pinv(C)
    chi2 = float(d @ Cinv @ d)
    ndf = n_keep
    if report:
        print(f"  {tag:20s}  chi2 = {chi2:12.2f}   ndf = {ndf:3d}   chi2/ndf = {chi2/ndf:7.3f}")
    return chi2, ndf, mask


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ours", default=DEFAULT_OURS,
                    help="Path to our 2D cross-section ROOT file (contains hXSec2D)")
    ap.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX,
                    help="Prefix for output PNGs (suffix _pull_summary.png is appended)")
    args = ap.parse_args()
    global OURS, OUT_PREFIX
    OURS = args.ours
    OUT_PREFIX = args.out_prefix

    print(f"[paper] opening: {ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    fp = ROOT.TFile.Open(f"{ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    h_paper = fp.Get("pt_pl_cross_section")
    cov_total = tmatrix_to_numpy(fp.Get("TotalCovariance"))
    cov_stat = tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    cov_flux = tmatrix_to_numpy(fp.Get("FluxCovariance"))
    cov_mes = tmatrix_to_numpy(fp.Get("MuonEnergyScaleCovariance"))
    assert cov_total.shape == (N, N), f"cov shape {cov_total.shape} != ({N},{N})"

    paper_v = flatten_th2d(h_paper)
    n_reported = int((np.diag(cov_stat) > 0).sum())
    print(f"[paper] reported bins: {n_reported} / {N}")
    print(f"[paper] cross-section sum (reported bins): {paper_v.sum():.4e}")

    print(f"\n[ours] opening: {OURS}")
    fo = ROOT.TFile.Open(OURS)
    h_ours = fo.Get("hXSec2D")
    ours_v = flatten_ours(h_ours)
    print(f"[ours] cross-section sum (all bins): {ours_v.sum():.4e}")

    diff = ours_v - paper_v

    print(f"\n=== chi^2 comparisons (ours vs paper) ===")
    chi2_stat, ndf_stat, mask = chi2_with_cov(diff, cov_stat,  "stat only")
    chi2_flux, _, _           = chi2_with_cov(diff, cov_flux,  "flux only")
    chi2_mes,  _, _           = chi2_with_cov(diff, cov_mes,   "muon E scale only")
    chi2_tot,  _, _           = chi2_with_cov(diff, cov_total, "TOTAL (stat+syst)")

    # Per-bin pull = (ours - paper) / sqrt(total_diag)
    sig = np.sqrt(np.diag(cov_total))
    pull = np.zeros_like(diff)
    ok = (sig > 0)
    pull[ok] = diff[ok] / sig[ok]

    # Reshape to (pt, pz) for a heatmap (using reported mask → nan elsewhere)
    pull_map = np.full((N_PT, N_PZ), np.nan)
    for gid in range(N):
        if mask[gid]:
            ptb, pzb = gid // N_PZ, gid % N_PZ
            pull_map[ptb, pzb] = pull[gid]

    # Summary plot
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    im0 = axs[0].imshow(pull_map.T, aspect="auto", origin="lower",
                        cmap="RdBu_r", vmin=-5, vmax=5,
                        extent=[0, N_PT, 0, N_PZ])
    axs[0].set_xlabel("p_T bin")
    axs[0].set_ylabel("p_|| bin")
    axs[0].set_title(f"Per-bin pull (ours - paper) / sigma_total")
    plt.colorbar(im0, ax=axs[0], label="pull")

    axs[1].hist(pull[mask], bins=30, color="steelblue", edgecolor="black")
    axs[1].axvline(0, color="k", ls="--", lw=0.8)
    axs[1].set_xlabel("pull")
    axs[1].set_ylabel("bins")
    axs[1].set_title(f"Pull distribution ({int(mask.sum())} reported bins)")
    mu, sd = pull[mask].mean(), pull[mask].std()
    axs[1].text(0.03, 0.95,
                f"mean={mu:.2f}\nrms ={sd:.2f}\n$\\chi^2$/ndf total = {chi2_tot/ndf_stat:.2f}",
                transform=axs[1].transAxes, va="top", family="monospace",
                bbox=dict(facecolor="white", alpha=0.85, edgecolor="gray"))

    fig.suptitle("Full-stats 2D OmniFold vs arXiv:2106.16210 Fig. 13", fontsize=11)
    fig.tight_layout()
    out = f"{OUT_PREFIX}_pull_summary.png"
    fig.savefig(out, dpi=130)
    print(f"\nwrote {out}")

    # Also print a condensed table for the run log
    print("\nSummary for run log:")
    print(f"  reported bins: {int(mask.sum())}")
    print(f"  chi^2/ndf  stat only       : {chi2_stat/ndf_stat:.3f}")
    print(f"  chi^2/ndf  flux only       : {chi2_flux/ndf_stat:.3f}")
    print(f"  chi^2/ndf  muon E scale    : {chi2_mes/ndf_stat:.3f}")
    print(f"  chi^2/ndf  TOTAL (full cov): {chi2_tot/ndf_stat:.3f}")
    print(f"  pull mean / rms            : {mu:.3f} / {sd:.3f}")


if __name__ == "__main__":
    main()
