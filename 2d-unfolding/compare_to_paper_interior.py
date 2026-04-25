#!/usr/bin/env python3
"""Compare full-stats 2D OmniFold result to arXiv:2106.16210 on the
INTERIOR of the fiducial phase space only.

Paper reports d^2 sigma / (dp_T dp_||) within theta_mu < 20 deg. Bins
straddling that boundary receive efficiency-driven suppression in the
paper's analysis that our OmniFold does not replicate, producing
O(10^2) sigma pulls that inflate the full-covariance chi^2. This script
masks bins where the worst-case corner (pt_high / p||_low) violates
pt/p|| < tan(20 deg), leaving only the physics-bulk bins and reporting
stat-only / flux / muon-E / total chi^2 on that reduced set.

Companion to `compare_to_paper_fullcov.py` (which reports the full-mask
7342/205 result dominated by edge bins).
"""
import argparse
import math
import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ANC_DIR = "/pscratch/sd/j/josephrb/MINERvA101/Documents/minerva_paper_anc"
DEFAULT_OURS = "/pscratch/sd/j/josephrb/MINERvA101/Documents/2d_crossSection_omnifold_MEHFC_5iter.root"
DEFAULT_OUT = "/pscratch/sd/j/josephrb/MINERvA101/Documents/compare_MEHFC_paper_interior.png"

N_PT, N_PZ = 14, 16
N = N_PT * N_PZ

# Paper bin edges (from bin_mapping.txt, authoritative — NOT the TH2D axis labels)
PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]

THETA_MAX_DEG = 20.0
TAN_THETA_MAX = math.tan(math.radians(THETA_MAX_DEG))


def tm_to_np(tm):
    n = tm.GetNrows()
    a = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            a[i, j] = tm(i, j)
    return a


def fill_paper(h):
    """Paper TH2D: x=p||(16), y=pt(14). gid = (ptb-1)*16 + (pzb-1)."""
    v = np.zeros(N)
    for ix in range(1, N_PZ + 1):
        for iy in range(1, N_PT + 1):
            gid = (iy - 1) * N_PZ + (ix - 1)
            v[gid] = h.GetBinContent(ix, iy)
    return v


def fill_ours(h):
    """Our TH2D: x=pt(14), y=p||(16)."""
    v = np.zeros(N)
    for ix in range(1, N_PT + 1):
        for iy in range(1, N_PZ + 1):
            gid = (ix - 1) * N_PZ + (iy - 1)
            v[gid] = h.GetBinContent(ix, iy)
    return v


def interior_mask():
    """True for bins where pt_high / p||_low <= tan(20 deg).

    This is the strict-interior criterion — the WORST corner of the bin
    (max pt, min p||) still lies inside the fiducial, so paper-side
    efficiency suppression should be minimal.
    """
    m = np.zeros(N, dtype=bool)
    for ptb in range(1, N_PT + 1):
        pt_hi = PT_EDGES[ptb]          # high edge of this pt bin
        for pzb in range(1, N_PZ + 1):
            pz_lo = PZ_EDGES[pzb - 1]  # low edge of this p|| bin
            gid = (ptb - 1) * N_PZ + (pzb - 1)
            m[gid] = (pt_hi / pz_lo) <= TAN_THETA_MAX
    return m


def chi2(diff, cov, mask, tag):
    diag = np.diag(cov)
    both = mask & (diag > 0)
    d = diff[both]
    C = cov[np.ix_(both, both)]
    Cinv = np.linalg.pinv(C)
    c = float(d @ Cinv @ d)
    n = int(both.sum())
    print(f"  {tag:22s}  chi2 = {c:10.2f}   ndf = {n:3d}   chi2/ndf = {c/n:6.3f}")
    return c, n, both


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ours", default=DEFAULT_OURS,
                    help="Path to our 2D cross-section ROOT file (contains hXSec2D)")
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="Output PNG path")
    args = ap.parse_args()
    global OURS, OUT
    OURS = args.ours
    OUT = args.out

    print(f"[paper] opening {ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    fp = ROOT.TFile.Open(f"{ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    paper = fill_paper(fp.Get("pt_pl_cross_section"))
    cov_tot = tm_to_np(fp.Get("TotalCovariance"))
    cov_sta = tm_to_np(fp.Get("StatOnlyCovariance"))
    cov_flx = tm_to_np(fp.Get("FluxCovariance"))
    cov_mes = tm_to_np(fp.Get("MuonEnergyScaleCovariance"))

    print(f"[ours]  opening {OURS}")
    fo = ROOT.TFile.Open(OURS)
    ours = fill_ours(fo.Get("hXSec2D"))

    diff = ours - paper

    m_int = interior_mask()
    m_rep = (np.diag(cov_sta) > 0)
    m_both = m_int & m_rep
    print(f"\n[masking]")
    print(f"  bins in strict interior (pt_hi/pz_lo <= tan20):  {m_int.sum()} / {N}")
    print(f"  bins reported by paper                        :  {m_rep.sum()} / {N}")
    print(f"  intersection                                  :  {m_both.sum()} / {N}")

    # Per-bin stats on the intersection
    ratio = np.where(paper > 0, ours / paper, np.nan)
    r_int = ratio[m_both]
    r_int = r_int[np.isfinite(r_int)]
    print(f"\n[interior ratio ours/paper, {len(r_int)} bins]")
    print(f"  median       = {np.median(r_int):.4f}")
    print(f"  mean         = {r_int.mean():.4f}")
    print(f"  5%  window   = {(np.abs(r_int-1)<0.05).mean()*100:5.1f}%")
    print(f"  10% window   = {(np.abs(r_int-1)<0.10).mean()*100:5.1f}%")
    print(f"  20% window   = {(np.abs(r_int-1)<0.20).mean()*100:5.1f}%")

    print(f"\n=== chi^2 on interior bins (strict: pt_hi/pz_lo <= tan(20)) ===")
    chi2(diff, cov_sta, m_int, "stat only")
    chi2(diff, cov_flx, m_int, "flux only")
    chi2(diff, cov_mes, m_int, "muon E scale only")
    c_tot, n_tot, used = chi2(diff, cov_tot, m_int, "TOTAL (stat+syst)")

    # Also report the "full reported" baseline for comparison
    print(f"\n=== chi^2 on ALL reported bins (edge-inclusive, for reference) ===")
    chi2(diff, cov_sta, m_rep, "stat only")
    chi2(diff, cov_tot, m_rep, "TOTAL")

    # Scan over p||_min to show where the chi^2 stabilizes.
    # pzb=1 (p||=1.5-2.0) is the MINOS range-out regime and inflates
    # chi^2 out of proportion — dropping it yields a physics-meaningful
    # number.
    print(f"\n=== chi^2 vs p||_min (strict-interior mask, paper-reported) ===")
    print(f"  {'p|| cut':>10} {'N':>4}   {'chi2':>10}   {'chi2/ndf':>8}   {'median':>7}   {'%<5%':>5}")
    for pz_min_idx in range(1, 7):
        m_scan = np.zeros(N, dtype=bool)
        for ptb in range(1, N_PT + 1):
            for pzb in range(pz_min_idx, N_PZ + 1):
                if PT_EDGES[ptb] / PZ_EDGES[pzb - 1] <= TAN_THETA_MAX:
                    m_scan[(ptb - 1) * N_PZ + (pzb - 1)] = True
        m_scan &= m_rep
        d = diff[m_scan]
        C = cov_tot[np.ix_(m_scan, m_scan)]
        c = float(d @ np.linalg.pinv(C) @ d)
        n = int(m_scan.sum())
        ratios = (ours / np.where(paper > 0, paper, 1))[m_scan & (paper > 0)]
        ratios = ratios[np.isfinite(ratios)]
        med = np.median(ratios)
        w5 = (np.abs(ratios - 1) < 0.05).mean() * 100
        print(f"  p||>={PZ_EDGES[pz_min_idx-1]:4.1f} {n:4d}   {c:10.2f}   {c/n:8.3f}   {med:7.4f}   {w5:4.1f}%")

    # Pull heatmap and histogram on interior mask
    sig = np.sqrt(np.diag(cov_tot))
    pull = np.where(sig > 0, diff / sig, 0.0)
    pull_map = np.full((N_PT, N_PZ), np.nan)
    for gid in range(N):
        if used[gid]:
            pull_map[gid // N_PZ, gid % N_PZ] = pull[gid]

    fig, axs = plt.subplots(1, 2, figsize=(13, 5))

    im = axs[0].imshow(
        pull_map.T,
        aspect="auto",
        origin="lower",
        cmap="RdBu_r",
        vmin=-5, vmax=5,
        extent=[0, N_PT, 0, N_PZ],
    )
    axs[0].set_xlabel("p_T bin index")
    axs[0].set_ylabel("p_|| bin index")
    axs[0].set_title(f"Interior-only pull map (N={int(used.sum())})")
    plt.colorbar(im, ax=axs[0], label="pull (ours - paper) / sigma_total")

    pulls_used = pull[used]
    axs[1].hist(pulls_used, bins=30, color="steelblue", edgecolor="black")
    axs[1].axvline(0, color="k", ls="--", lw=0.8)
    axs[1].set_xlabel("pull (ours - paper) / sigma_total")
    axs[1].set_ylabel("bins")
    axs[1].set_title(f"Interior-only pull distribution")
    mu, sd = pulls_used.mean(), pulls_used.std()
    axs[1].text(
        0.03, 0.95,
        f"mean={mu:.2f}\nrms ={sd:.2f}\nchi2/ndf = {c_tot/n_tot:.2f}",
        transform=axs[1].transAxes, va="top", family="monospace",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="gray"),
    )

    fig.suptitle(
        f"Full-stats 2D OmniFold vs arXiv:2106.16210, "
        f"interior fiducial only (pt_hi/pz_lo <= tan(20°) = {TAN_THETA_MAX:.3f})",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(OUT, dpi=130)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
