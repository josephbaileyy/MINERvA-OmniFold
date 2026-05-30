#!/usr/bin/env python3
"""Anatomy of the ours-vs-paper chi^2 tension for 2D OmniFold (arXiv:2106.16210).

Central values agree: sigma_tot(ours)/sigma_tot(paper) = 1.011, median bin
ratio 1.006, and the per-bin pull RMS against the paper covariance is only
0.598 (< 1). Yet the paper-covariance chi^2/ndf is 3.66. A diagonal-only chi^2
would be ~(0.598)^2 ~ 0.36, so the entire tension lives in the OFF-DIAGONAL /
small-eigenvalue structure of the published TotalCov (rank 204/205,
cond ~1.5e12). This script decomposes that chi^2 to localize the tension in
eigen-space and in kinematic space and to decide between:

  (1) a real physics shape difference (high-p|| tails),
  (2) an artifact of inverting an ill-conditioned published covariance,
  (3) a residual methodological offset (iteration / flux-shape / acceptance).

Track A - eigenmode anatomy: V = sum_k lambda_k u_k u_k^T; project the residual
          r = ours - paper onto each mode; per-mode chi^2 = (u_k.r)^2 / lambda_k.
          Diagonal-vs-full crux comparison; rank-truncation + rcond scans.
Track B - kinematic localization: dominant eigenvectors mapped onto the 14x16
          (pT, p||) grid; per-bin chi^2-contribution map; marginal chi^2 by pT
          band and p|| band; normalization-vs-shape split.

Runs on the frozen production ROOT + paper ancillary. No re-unfold.

Reuses loaders / chi^2 from compare_to_paper_fullcov.py (single source of truth
for the paper bin indexing gid = (ptbin-1)*16 + (pzbin-1) and the 205 reported
bins, diag(StatOnlyCov) > 0).
"""
import argparse
import os
import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from compare_to_paper_fullcov import (
    ANC_DIR, DEFAULT_OURS, N, N_PT, N_PZ,
    tmatrix_to_numpy, flatten_th2d, flatten_ours, chi2_with_cov,
)

DEFAULT_OUT_PREFIX = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/tension"


def load_model(path):
    """Paper MINERvA Tune v1 prediction CSV: P||bin,Ptbin,model_cross_section.
    Returns a length-N (224) vector on the global grid."""
    v = np.zeros(N)
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.lower().startswith("p||"):
                continue
            pzb, ptb, xs = line.split(",")
            gid = (int(ptb) - 1) * N_PZ + (int(pzb) - 1)
            v[gid] = float(xs)
    return v


def grid_from_reported(vec_red, mask):
    """Scatter a length-n_reported vector back onto a (N_PT, N_PZ) grid
    (nan in unreported cells) using the global mask."""
    out = np.full((N_PT, N_PZ), np.nan)
    idx = np.where(mask)[0]
    for k, gid in enumerate(idx):
        out[gid // N_PZ, gid % N_PZ] = vec_red[k]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ours", default=DEFAULT_OURS,
                    help="2D cross-section ROOT (hXSec2D). Default: frozen 5-iter production.")
    ap.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX,
                    help="Prefix for output PNGs and tension_report.txt.")
    ap.add_argument("--top", type=int, default=6,
                    help="How many dominant eigen-modes to map kinematically.")
    ap.add_argument("--model", default=os.path.join(
                        ANC_DIR, "model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"),
                    help="MINERvA Tune v1 model CSV for the dominant-bin overlay.")
    args = ap.parse_args()

    lines = []   # mirror stdout into tension_report.txt

    def emit(s=""):
        print(s)
        lines.append(s)

    # ---- load paper + ours (reuse compare_to_paper_fullcov conventions) -----
    fp = ROOT.TFile.Open(f"{ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    h_paper = fp.Get("pt_pl_cross_section")
    cov_total = tmatrix_to_numpy(fp.Get("TotalCovariance"))
    cov_stat = tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    paper_v = flatten_th2d(h_paper)

    fo = ROOT.TFile.Open(args.ours)
    ours_v = flatten_ours(fo.Get("hXSec2D"))

    mask = np.diag(cov_stat) > 0           # 205 reported bins
    n = int(mask.sum())
    d = (ours_v - paper_v)[mask]           # residual on reported bins
    V = cov_total[np.ix_(mask, mask)]
    diagV = np.diag(V)
    paper_red = paper_v[mask]

    emit("=" * 72)
    emit("TENSION ANATOMY  -  2D OmniFold vs arXiv:2106.16210")
    emit("=" * 72)
    emit(f"ours = {args.ours}")
    emit(f"reported bins: {n}   sigma_tot(ours)/sigma_tot(paper) = "
         f"{ours_v[mask].sum() / paper_red.sum():.4f}")

    # ---- Track A: crux - diagonal vs full -----------------------------------
    chi2_full, ndf, _ = chi2_with_cov(ours_v - paper_v, cov_total,
                                      "full pinv (reproduce 3.66)", report=False)
    chi2_diag = float(np.sum(d ** 2 / diagV))
    pull = d / np.sqrt(diagV)
    emit("")
    emit("--- Track A: the crux (off-diagonal vs diagonal) ---")
    emit(f"  diagonal-only chi2/ndf = {chi2_diag / n:7.3f}   "
         f"(= per-bin pull RMS^2 = {pull.std()**2:.3f}; mean pull {pull.mean():+.3f})")
    emit(f"  full-cov   chi2/ndf    = {chi2_full / n:7.3f}")
    emit(f"  => {chi2_full / chi2_diag:.1f}x inflation comes purely from the "
         f"off-diagonal / small-eigenvalue structure of TotalCov.")

    # ---- Track A: eigenmode decomposition -----------------------------------
    # V symmetric PSD -> eigh. Ascending eigenvalues; columns are eigenvectors.
    lam, U = np.linalg.eigh(V)
    lam_max = lam.max()
    c = U.T @ d                              # projection coefficients c_k = u_k . r
    rcond = 1e-15                            # numpy pinv default (relative)
    keep = lam > rcond * lam_max            # modes pinv retains
    contrib = np.where(keep, c ** 2 / np.where(keep, lam, 1.0), 0.0)
    chi2_modes = float(contrib.sum())
    emit("")
    emit("--- Track A: eigenmode decomposition of the paper-cov chi2 ---")
    emit(f"  cond(V) = {lam_max / lam[lam > 0].min():.2e}   "
         f"rank(lam>0) = {int((lam > 0).sum())}/{n}   "
         f"modes kept by pinv (rcond={rcond:.0e}) = {int(keep.sum())}")
    emit(f"  sum_k c_k^2/lambda_k = {chi2_modes:.4f}  vs  pinv chi2 = "
         f"{chi2_full:.4f}   (rel diff {abs(chi2_modes - chi2_full)/chi2_full:.2e})")

    # Rank the modes by their chi^2 contribution. lam_rank: 0 = smallest lambda.
    order = np.argsort(contrib)[::-1]
    lam_rank = np.argsort(np.argsort(lam))   # 0..n-1, 0 = smallest lambda
    emit("")
    emit("  top contributing modes (lam_rank 0 = smallest eigenvalue):")
    emit("   rank  lam/lam_max   lam_rank   eigpull=c/sqrt(lam)   chi2_contrib   cum/chi2")
    cum = 0.0
    for j, k in enumerate(order[:15]):
        cum += contrib[k]
        emit(f"   {j:4d}  {lam[k]/lam_max:10.3e}   {lam_rank[k]:5d}/{n}   "
             f"{c[k]/np.sqrt(lam[k]):+12.2f}        {contrib[k]:9.2f}     "
             f"{cum/chi2_modes:6.3f}")
    # Are the dominant contributors small-lambda (artifact) or large (physical)?
    top5 = order[:5]
    frac_small = float(np.mean(lam_rank[top5] < n * 0.1))
    emit(f"  fraction of top-5 contributors in the smallest-10%% lambda band: "
         f"{frac_small:.2f}")
    emit(f"  chi2 share from the 10 smallest-lambda modes: "
         f"{contrib[lam_rank < 10].sum()/chi2_modes:6.3f}")

    # ---- Track A: rank-truncation + rcond scans -----------------------------
    emit("")
    emit("--- Track A: rank-truncation scan (keep r largest-lambda modes) ---")
    emit("    r      chi2/ndf")
    # keep modes ordered by lambda descending
    lam_desc = np.argsort(lam)[::-1]
    for r in [5, 10, 20, 50, 100, 150, 180, 200, n]:
        sel = lam_desc[:r]
        sel = sel[lam[sel] > rcond * lam_max]
        chi2_r = float(np.sum(c[sel] ** 2 / lam[sel]))
        emit(f"  {r:4d}     {chi2_r / n:8.3f}")
    emit("  (monotone; a late jump near r=n means the tension rides on the "
         "smallest-lambda / least-determined directions.)")

    emit("")
    emit("--- Track A: pinv rcond sensitivity ---")
    emit("    rcond      chi2/ndf   modes_kept")
    for rc in [1e-15, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2]:
        kp = lam > rc * lam_max
        chi2_rc = float(np.sum(c[kp] ** 2 / lam[kp]))
        emit(f"  {rc:7.0e}     {chi2_rc / n:8.3f}    {int(kp.sum()):4d}")

    # ---- Track B: normalization vs shape split ------------------------------
    Vinv = np.linalg.pinv(V)
    u_norm = paper_red / np.linalg.norm(paper_red)     # "scale the spectrum" dir
    d_norm = (u_norm @ d) * u_norm
    d_shape = d - d_norm
    chi2_norm = float(d_norm @ Vinv @ d_norm)
    chi2_shape = float(d_shape @ Vinv @ d_shape)
    chi2_cross = float(2 * d_norm @ Vinv @ d_shape)
    emit("")
    emit("--- Track B: normalization (along paper spectrum) vs shape split ---")
    emit(f"  chi2_norm  = {chi2_norm:8.2f}  ({chi2_norm/n:.3f}/ndf)   "
         f"[overall scale; sigma_tot ratio {ours_v[mask].sum()/paper_red.sum():.4f}]")
    emit(f"  chi2_shape = {chi2_shape:8.2f}  ({chi2_shape/n:.3f}/ndf)")
    emit(f"  chi2_cross = {chi2_cross:8.2f}   (norm+shape+cross = "
         f"{(chi2_norm+chi2_shape+chi2_cross):.2f} vs full {chi2_full:.2f})")
    emit("  (chi2 is not additive across a non-Vinv-orthogonal split; cross "
         "term reported for closure. Shape dominates -> not a pure normalization.)")

    # ---- Track B: per-bin chi^2 contribution + marginals --------------------
    Vinv_d = Vinv @ d
    per_bin = d * Vinv_d                      # sum = chi2_full
    pt_idx = np.array([np.where(mask)[0][k] // N_PZ for k in range(n)])
    pz_idx = np.array([np.where(mask)[0][k] % N_PZ for k in range(n)])
    emit("")
    emit("--- Track B: marginal chi^2 by p|| band (pz bin, low->high p||) ---")
    emit("    pz_bin   n_bins   chi2_sum   frac")
    for j in range(N_PZ):
        sel = pz_idx == j
        if sel.any():
            emit(f"  {j:6d}   {int(sel.sum()):6d}   {per_bin[sel].sum():9.2f}   "
                 f"{per_bin[sel].sum()/chi2_full:6.3f}")
    emit("  marginal chi^2 by p_T band (pt bin, low->high p_T):")
    emit("    pt_bin   n_bins   chi2_sum   frac")
    for i in range(N_PT):
        sel = pt_idx == i
        if sel.any():
            emit(f"  {i:6d}   {int(sel.sum()):6d}   {per_bin[sel].sum():9.2f}   "
                 f"{per_bin[sel].sum()/chi2_full:6.3f}")

    # ---- Track C bridge: model overlay in the dominant-mode bins ------------
    if args.model and os.path.exists(args.model):
        model_v = load_model(args.model)[mask]
        # bins most loaded by the single largest-contribution eigenvector
        kdom = order[0]
        w = np.abs(U[:, kdom])
        big = np.argsort(w)[::-1][:12]
        emit("")
        emit(f"--- Track C bridge: top-12 bins of dominant mode (lam_rank "
             f"{lam_rank[kdom]}/{n}) ---")
        emit("   pt_bin pz_bin    ours        paper       Tune_v1    "
             "ours/paper  |ours-mod|<|paper-mod|?")
        closer = 0
        for k in big:
            o, p, m = d[k] + paper_red[k], paper_red[k], model_v[k]
            nearer = abs(o - m) < abs(p - m)
            closer += nearer
            emit(f"   {pt_idx[k]:5d} {pz_idx[k]:5d}   {o:.3e}  {p:.3e}  "
                 f"{m:.3e}   {o/p:8.4f}   {'YES' if nearer else 'no'}")
        emit(f"  ours closer to Tune v1 than paper in {closer}/12 dominant-mode "
             f"bins (frames tension as IBU-vs-OmniFold regularization).")

    # ---- plots --------------------------------------------------------------
    _plots(lam, lam_max, contrib, order, U, d, per_bin, mask, args, n,
           chi2_modes)

    # ---- write report -------------------------------------------------------
    rpt = f"{args.out_prefix}_report.txt"
    with open(rpt, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    emit("")
    emit(f"wrote {rpt}")


def _plots(lam, lam_max, contrib, order, U, d, per_bin, mask, args, n, chi2_modes):
    # (1) eigenvalue spectrum + cumulative chi^2 (modes sorted by contribution)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    axs[0].semilogy(np.sort(lam / lam_max)[::-1], ".-", ms=4)
    axs[0].set_xlabel("mode (largest -> smallest lambda)")
    axs[0].set_ylabel("lambda / lambda_max")
    axs[0].set_title("Paper TotalCov eigenvalue spectrum (205 reported bins)")
    axs[0].grid(alpha=0.3)
    cum = np.cumsum(contrib[order]) / chi2_modes
    axs[1].plot(np.arange(1, n + 1), cum, ".-", ms=4)
    axs[1].axhline(0.9, color="r", ls="--", lw=0.8, label="90% of chi^2")
    axs[1].set_xlabel("modes ranked by chi^2 contribution")
    axs[1].set_ylabel("cumulative chi^2 fraction")
    axs[1].set_title("How few modes carry the chi^2")
    axs[1].legend(); axs[1].grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(f"{args.out_prefix}_spectrum.png", dpi=130)
    plt.close(fig)

    # (2) dominant eigenvector kinematic maps
    ntop = min(args.top, n)
    ncol = 3
    nrow = int(np.ceil(ntop / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 3.4 * nrow),
                            squeeze=False)
    lam_rank = np.argsort(np.argsort(lam))
    for j in range(nrow * ncol):
        ax = axs[j // ncol][j % ncol]
        if j >= ntop:
            ax.axis("off"); continue
        k = order[j]
        g = grid_from_reported(U[:, k], mask)
        vmax = np.nanmax(np.abs(g))
        im = ax.imshow(g.T, aspect="auto", origin="lower", cmap="RdBu_r",
                       vmin=-vmax, vmax=vmax, extent=[0, N_PT, 0, N_PZ])
        ax.set_title(f"mode #{j} (lam_rank {lam_rank[k]}/{n}, "
                     f"chi2 {contrib[k]:.0f})", fontsize=9)
        ax.set_xlabel("p_T bin"); ax.set_ylabel("p_|| bin")
        plt.colorbar(im, ax=ax)
    fig.suptitle("Eigenvectors carrying the chi^2 tension, mapped to (p_T, p_||)")
    fig.tight_layout(); fig.savefig(f"{args.out_prefix}_mode_maps.png", dpi=130)
    plt.close(fig)

    # (3) per-bin chi^2 contribution heatmap
    fig, ax = plt.subplots(figsize=(7, 5))
    g = grid_from_reported(per_bin, mask)
    vmax = np.nanpercentile(np.abs(g), 99)
    im = ax.imshow(g.T, aspect="auto", origin="lower", cmap="RdBu_r",
                   vmin=-vmax, vmax=vmax, extent=[0, N_PT, 0, N_PZ])
    ax.set_xlabel("p_T bin"); ax.set_ylabel("p_|| bin")
    ax.set_title("Per-bin chi^2 contribution  r_i (V^-1 r)_i  (sum = chi^2)")
    plt.colorbar(im, ax=ax, label="chi^2 contribution")
    fig.tight_layout(); fig.savefig(f"{args.out_prefix}_chi2_map.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
