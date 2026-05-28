#!/usr/bin/env python3
"""Quick ours-only chi^2 with a user-supplied OmniFold covariance.

Loads our MEFHC CV xsec, the paper xsec, optionally adds a bootstrap
cov to the universe cov, then reports chi^2/ndf on the 205 reported
bins via direct inverse (no pseudo-inverse). Diagnoses condition
number and effective rank.

Usage:
  python uq/_ours_only_chi2.py \
    --universe-cov uq/universe_stage2_MEFHC_full_shrunk_005/uq_universe_covariance_full_shrunk_005.root \
    [--universe-hist hCov_universe_total] \
    [--bootstrap-cov uq/bootstrap_MEFHC_300/uq_covariance_boot300.root] \
    [--bootstrap-hist hCov2D_reported]
"""
import argparse
import numpy as np
import ROOT


ANC = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc"
OURS_DEFAULT = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/"
                "2d_crossSection_omnifold_MEFHC_5iter.root")
N_PT, N_PZ, N = 14, 16, 14 * 16


def tmatrix_to_numpy(m):
    n = m.GetNrows()
    a = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            a[i, j] = m(i, j)
    return a


def flatten_paper(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    x_is_pt = (nx == N_PT)
    v = np.zeros(N)
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
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    assert nx == N_PT and ny == N_PZ, f"ours shape: {nx}x{ny}"
    v = np.zeros(N)
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            gid = (ix - 1) * N_PZ + (iy - 1)
            v[gid] = h.GetBinContent(ix, iy)
    return v


def cov_th2_to_numpy(h):
    n = h.GetNbinsX()
    a = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            a[i, j] = h.GetBinContent(i + 1, j + 1)
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe-cov", required=True)
    ap.add_argument("--universe-hist", default="hCov_universe_total")
    ap.add_argument("--bootstrap-cov", default=None)
    ap.add_argument("--bootstrap-hist", default="hCov2D_reported")
    ap.add_argument("--ours", default=OURS_DEFAULT)
    args = ap.parse_args()

    # Paper TotalCov is on 224 bins; the reported-bins mask is set by
    # rows/cols with nonzero stat-only diag.
    fp = ROOT.TFile.Open(f"{ANC}/cov_ptpl_minerva_inclusive_6GeV.root")
    h_paper = fp.Get("pt_pl_cross_section")
    cov_stat = tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    paper_v = flatten_paper(h_paper)
    mask = np.diag(cov_stat) > 0
    n_rep = int(mask.sum())
    print(f"[paper] reported bins: {n_rep}/224")

    fo = ROOT.TFile.Open(args.ours)
    h_ours = fo.Get("hXSec2D")
    ours_v = flatten_ours(h_ours)
    diff_full = ours_v - paper_v
    diff = diff_full[mask]
    print(f"[diff] sum reported = {diff.sum():.3e}, max |.| = {np.abs(diff).max():.3e}")

    # Load universe cov on reported bins.
    fu = ROOT.TFile.Open(args.universe_cov)
    hu = fu.Get(args.universe_hist)
    if not hu:
        raise SystemExit(f"missing {args.universe_hist} in {args.universe_cov}")
    Cu = cov_th2_to_numpy(hu)
    assert Cu.shape == (n_rep, n_rep), f"cov shape {Cu.shape} != ({n_rep},{n_rep})"
    print(f"[universe cov] shape={Cu.shape}, sqrt(trace)={np.sqrt(Cu.trace()):.3e}")

    C = Cu.copy()
    tag = "universe-only"
    if args.bootstrap_cov:
        fb = ROOT.TFile.Open(args.bootstrap_cov)
        hb = fb.Get(args.bootstrap_hist)
        if not hb:
            raise SystemExit(f"missing {args.bootstrap_hist} in {args.bootstrap_cov}")
        Cb = cov_th2_to_numpy(hb)
        if Cb.shape != Cu.shape:
            raise SystemExit(f"shape mismatch: boot {Cb.shape} vs uni {Cu.shape}")
        print(f"[boot cov] shape={Cb.shape}, sqrt(trace)={np.sqrt(Cb.trace()):.3e}")
        C = Cu + Cb
        tag = "universe + bootstrap"

    Cs = 0.5 * (C + C.T)
    evals = np.linalg.eigvalsh(Cs)
    cond = evals.max() / max(evals[evals > evals.max() * 1e-15].min(), 1e-300)
    rank_at_1em12 = int((evals > evals.max() * 1e-12).sum())
    print(f"[{tag}] cond={cond:.3e}  rank(>1e-12*max)={rank_at_1em12}/{n_rep}")

    # Direct inverse chi^2 (no pseudo-inverse).
    try:
        Cinv = np.linalg.inv(Cs)
        chi2 = float(diff @ Cinv @ diff)
        print(f"[{tag}] direct inverse: chi^2 = {chi2:.3f},  ndf = {n_rep},  "
              f"chi^2/ndf = {chi2 / n_rep:.3f}")
    except np.linalg.LinAlgError as e:
        print(f"[{tag}] direct inverse failed: {e}")

    # Also: per-bin pull rms (no inverse needed).
    sigma = np.sqrt(np.maximum(np.diag(Cs), 0))
    pulls = np.where(sigma > 0, diff / sigma, 0.0)
    print(f"[{tag}] per-bin pull:  mean = {pulls.mean():.3f},  rms = {pulls.std():.3f}")


if __name__ == "__main__":
    main()
