#!/usr/bin/env python3
"""Compare full-stats 2D OmniFold result to arXiv:2106.16210 with the
paper's published covariance matrix.

The paper's ancillary data release (arXiv:2106.16210v4/anc) provides
the measured cross section as a TH2D and four TMatrixT<double>
covariance matrices: Total, StatOnly, Flux, MuonEnergyScale — all with
bin axes p||(16) × pt(14) and global indexing (Ptbin-1)*16 + (P||bin-1).

Reports chi^2/ndf against our OmniFold result (`hXSec2D` in
`2d_crossSection_omnifold_MEFHC_5iter.root`) for each covariance, plus
per-bin pulls. Unreported bins (zero diagonal in StatOnlyCov) are
dropped from both sides and the covariance inverted via pseudo-inverse
on the reduced block.

Optionally, pass `--omnifold-cov <ROOT>:<HIST>` (repeatable) to add
OmniFold-derived covariances (bootstrap from `uq/analyze_uq.py` and/or
systematic universes from `uq/analyze_universes.py`) to the paper's
TotalCovariance. The combined chi^2/ndf is reported alongside the
paper-cov-only number so the apples-to-apples comparison the
paper-cov-only chi^2 cannot make becomes available.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ANC_DIR = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc"
DEFAULT_OURS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root"
DEFAULT_OUT_PREFIX = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/MEFHC_5iter"

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
        print(f"  {tag:30s}  chi2 = {chi2:12.2f}   ndf = {ndf:3d}   chi2/ndf = {chi2/ndf:7.3f}")
    return chi2, ndf, mask


def chi2_lognormal(ours_v, paper_v, cov, tag, report=True):
    """Log-normal chi^2 (Ruterbories Table I, Peelle's Pertinent Puzzle).

    r_i = log(ours_i / paper_i);  V_log[i,j] = V[i,j] / (paper_i * paper_j)
    chi^2_log = r^T pinv(V_log) r, evaluated on reported bins only.
    """
    diag = np.diag(cov)
    mask = (diag > 0) & (ours_v > 0) & (paper_v > 0)
    n_keep = int(mask.sum())
    x = paper_v[mask]
    r = np.log(ours_v[mask] / x)
    C = cov[np.ix_(mask, mask)]
    V_log = C / np.outer(x, x)
    Vinv = np.linalg.pinv(V_log)
    chi2 = float(r @ Vinv @ r)
    if report:
        print(f"  {tag:30s}  chi2_log = {chi2:12.2f}   ndf = {n_keep:3d}   "
              f"chi2/ndf = {chi2/n_keep:7.3f}")
    return chi2, n_keep


def load_omnifold_cov(spec, reported_mask):
    """Load an OmniFold 205x205 covariance from `<ROOT>:<HIST>` and
    promote it to the 224-bin global grid by zero-padding unreported
    bins. analyze_uq.py / analyze_universes.py both flatten row-major
    over (pt, pz), matching the paper's gid = (ptbin-1)*16 + (pzbin-1)
    convention, so the i-th OmniFold reported bin maps to the i-th True
    entry of `reported_mask`."""
    if ":" not in spec:
        raise SystemExit(f"--omnifold-cov expects ROOT:HIST, got: {spec!r}")
    path, hname = spec.rsplit(":", 1)
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] could not open OmniFold cov ROOT: {path}")
    h = f.Get(hname)
    if not h:
        raise SystemExit(f"[FAIL] hist '{hname}' missing in {path}")
    n_rep = int(reported_mask.sum())
    if h.GetNbinsX() != n_rep or h.GetNbinsY() != n_rep:
        raise SystemExit(
            f"[FAIL] {path}:{hname} is {h.GetNbinsX()}x{h.GetNbinsY()}, "
            f"expected {n_rep}x{n_rep} (paper reported bins)")
    small = np.empty((n_rep, n_rep))
    for i in range(n_rep):
        for j in range(n_rep):
            small[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close()
    cov224 = np.zeros((N, N))
    idx = np.where(reported_mask)[0]
    cov224[np.ix_(idx, idx)] = small
    sqrt_trace = float(np.sqrt(np.trace(small)))
    print(f"  [omnifold-cov] {path}:{hname}  shape={small.shape}  "
          f"sqrt(trace)={sqrt_trace:.3e}")
    return cov224, f"{hname}"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ours", default=DEFAULT_OURS,
                    help="Path to our 2D cross-section ROOT file (contains hXSec2D)")
    ap.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX,
                    help="Prefix for output PNGs (suffix _pull_full.png is appended)")
    ap.add_argument("--omnifold-cov", action="append", default=[],
                    metavar="ROOT:HIST",
                    help="Add an OmniFold 205x205 covariance (from "
                         "uq/analyze_uq.py or uq/analyze_universes.py) "
                         "to the paper's TotalCovariance. Repeatable. "
                         "Example: --omnifold-cov "
                         "uq/bootstrap_MEFHC_50/uq_covariance_MEFHC_50.root:hCov2D_reported")
    ap.add_argument("--log-normal", action="store_true",
                    help="Also report log-normal chi^2/ndf alongside the "
                         "standard chi^2 (paper Table I parity). r=log(ours/paper); "
                         "V_log[i,j]=V[i,j]/(x_i*x_j).")
    ap.add_argument("--subtract-stat", action="store_true",
                    help="Use (TotalCov - StatOnlyCov) as the paper baseline "
                         "for the combined chi^2 so our bootstrap C_boot is "
                         "not double-counted against the paper's stat block. "
                         "Stat-only and PAPER (full cov) chi^2 lines are "
                         "unaffected; only the combined number changes.")
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
    chi2_tot,  _, _           = chi2_with_cov(diff, cov_total, "PAPER (stat+syst)")

    # Optional: add OmniFold covs (bootstrap and/or systematic universes)
    # to the paper TotalCov. ndf is unchanged (same 205 reported bins).
    chi2_combined = None
    chi2_combined_log = None
    if args.subtract_stat:
        cov_combined = cov_total - cov_stat
        baseline_tag = "paper(syst-only) "
    else:
        cov_combined = cov_total.copy()
        baseline_tag = "paper "
    omnifold_tags = []
    if args.omnifold_cov:
        print(f"\n=== adding OmniFold covariances"
              f"{' (paper stat subtracted)' if args.subtract_stat else ''} ===")
        for spec in args.omnifold_cov:
            cov224, tag = load_omnifold_cov(spec, mask)
            cov_combined = cov_combined + cov224
            omnifold_tags.append(tag)
        chi2_combined, _, _ = chi2_with_cov(
            diff, cov_combined,
            "COMBINED (" + baseline_tag + "+ " + " + ".join(omnifold_tags) + ")")

    if args.log_normal:
        print(f"\n=== log-normal chi^2 (paper Table I parity) ===")
        chi2_lognormal(ours_v, paper_v, cov_total, "PAPER (stat+syst)")
        if chi2_combined is not None:
            chi2_combined_log, _ = chi2_lognormal(
                ours_v, paper_v, cov_combined,
                "COMBINED (" + baseline_tag + "+ omnifold)")

    # Per-bin pull = (ours - paper) / sqrt(diag). Use combined cov when
    # OmniFold covs were added so the pull reflects the same total error
    # used in the headline chi^2.
    sig = np.sqrt(np.diag(cov_combined))
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
    headline = (
        f"mean={mu:.2f}\nrms ={sd:.2f}\n"
        f"$\\chi^2$/ndf paper = {chi2_tot/ndf_stat:.2f}"
        + (f"\n$\\chi^2$/ndf comb. = {chi2_combined/ndf_stat:.2f}"
           if chi2_combined is not None else "")
    )
    axs[1].text(0.03, 0.95, headline,
                transform=axs[1].transAxes, va="top", family="monospace",
                bbox=dict(facecolor="white", alpha=0.85, edgecolor="gray"))

    fig.suptitle("Full-stats 2D OmniFold vs arXiv:2106.16210 Fig. 13", fontsize=11)
    fig.tight_layout()
    out = f"{OUT_PREFIX}_pull_full.png"
    fig.savefig(out, dpi=130)
    print(f"\nwrote {out}")

    # Also print a condensed table for the run log
    print("\nSummary for run log:")
    print(f"  reported bins: {int(mask.sum())}")
    print(f"  chi^2/ndf  stat only        : {chi2_stat/ndf_stat:.3f}")
    print(f"  chi^2/ndf  flux only        : {chi2_flux/ndf_stat:.3f}")
    print(f"  chi^2/ndf  muon E scale     : {chi2_mes/ndf_stat:.3f}")
    print(f"  chi^2/ndf  PAPER (full cov) : {chi2_tot/ndf_stat:.3f}")
    if chi2_combined is not None:
        print(f"  chi^2/ndf  COMBINED         : {chi2_combined/ndf_stat:.3f}"
              f"   (added: {', '.join(omnifold_tags)}"
              f"{', paper stat subtracted' if args.subtract_stat else ''})")
    if args.log_normal and chi2_combined_log is not None:
        print(f"  chi^2/ndf  COMBINED (log-N) : {chi2_combined_log/ndf_stat:.3f}")
    print(f"  pull mean / rms             : {mu:.3f} / {sd:.3f}")


if __name__ == "__main__":
    main()
