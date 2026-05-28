#!/usr/bin/env python3
"""Universe-covariance rollup for the 2D OmniFold UQ campaign.

Consumes a CV unfold and N per-(band,idx) universe unfolds produced by
`unfold_2d_omnifold_unbinned.py --universe BAND:IDX`. Computes:

  - Per-(band,idx) delta = xsec_universe - xsec_cv  (bin-by-bin)
  - Per-band covariance, uniform N >= 2 (MAT-conformant; matches
    PlotUtils/MnvVertErrorBand::CalcCovMx — biased sample cov,
    mean-centered, 1/N normalization, no special pair case):
        C_band = (1/N) * sum_u (X_u - <X>_u) (X_u - <X>_u)^T
    For symmetric +/-1 sigma pairs this reduces to the legacy
    0.5*(D0 D0^T + D1 D1^T) only when (X_+ + X_-) = 2*X_CV.
  - Optional flat normalization band added at rollup time via
    --add-norm SIGMA (e.g. 0.014 for the 1.4 % target-nucleon
    counting uncertainty, Aliaga NIM 1305.5199, Ruterbories ref [7]).
  - Total universe covariance = sum of per-band covariances
    (assumes bands uncorrelated; matches MINERvA-101 construction
    minus the Bashyal flux<->Muon_Energy_MINOS cross-band block).
  - Optional combined covariance: + bootstrap covariance from
    uq_covariance.root (block-sum, independent components).

Outputs (under --outdir):
  - uq_universe_summary.txt     plain-text per-band trace, top bins
  - uq_universe_band_pt.png     pT projection of grouped uncertainty sigma
  - uq_universe_band_pz.png     pz projection of grouped uncertainty sigma
  - uq_universe_covariance.root containing hCov_universe_total +
        hCov_universe_<band> for each band, plus hSigma_universe_total
        (TH2D of per-bin sqrt(diag) of total universe cov).

Usage:
  python uq/analyze_universes.py \
      --cv 2d_xsec_1A_5iter_lgbm_cv.root \
      --glob "uq/2d_xsec_1A_5iter_lgbm_uni_*.root" \
      [--bootstrap-cov uq/uq_covariance.root] \
      [--outdir uq/universe_stage1/]
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT


PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])

# Filename pattern: 2d_xsec_<DSET>_<...>_uni_<BAND>_<IDX>.root
UNI_RE = re.compile(r".*_uni_(?P<band>[A-Za-z0-9_]+?)_(?P<idx>\d+)\.root$")

CATEGORY_ORDER = [
    "Flux",
    "Models",
    "Normalization",
    "Statistical",
    "Hadronic response",
    "Muon reconstruction",
]


def category_for_band(band):
    """Map MINERvA universe bands into compact plot categories."""
    clean = band
    if clean.startswith("full_"):
        clean = clean[len("full_"):]

    if clean == "Flux":
        return "Flux"
    if clean in {"NormDISCC", "NormNCRES"}:
        return "Normalization"
    if (clean.startswith("Fr") or clean.startswith("MFP_") or
            clean.startswith("GEANT_")):
        return "Hadronic response"
    if (clean.startswith("Muon_") or clean.startswith("BeamAngle") or
            clean in {"MuonResolution", "MinosEfficiency"}):
        return "Muon reconstruction"
    return "Models"


def th2_to_array(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.zeros((nx, ny))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            a[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
    return a


def load_xsec2d(path):
    rf = ROOT.TFile.Open(path)
    if not rf or rf.IsZombie():
        sys.exit(f"[FAIL] cannot open {path}")
    h = rf.Get("hXSec2D")
    if not h:
        sys.exit(f"[FAIL] hXSec2D missing in {path}")
    a = th2_to_array(h)
    rf.Close()
    return a


def parse_universe_path(path):
    m = UNI_RE.match(os.path.basename(path))
    if not m:
        return None
    return m.group("band"), int(m.group("idx"))


def load_bootstrap_cov(path):
    rf = ROOT.TFile.Open(path)
    if not rf or rf.IsZombie():
        sys.exit(f"[FAIL] cannot open bootstrap cov {path}")
    h = rf.Get("hCov2D_reported")
    if not h:
        sys.exit(f"[FAIL] hCov2D_reported missing in {path}")
    n = h.GetNbinsX()
    cov = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            cov[i, j] = h.GetBinContent(i + 1, j + 1)
    rf.Close()
    return cov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", required=True, help="CV unfold ROOT (no --universe).")
    ap.add_argument("--glob", required=True,
                    help="Glob for universe unfold ROOTs, e.g. 'uq/2d_xsec_*_uni_*.root'.")
    ap.add_argument("--bootstrap-cov", default=None,
                    help="Optional uq_covariance.root from analyze_uq.py "
                         "to block-sum into a combined error budget.")
    ap.add_argument("--shrinkage", type=float, default=0.0,
                    help="Ledoit-Wolf-style shrinkage intensity in [0,1] "
                         "applied to the summed universe covariance with a "
                         "diagonal target: S_hat = (1-lambda)*S + lambda*"
                         "diag(diag(S)). Default 0 (no shrinkage). lambda>0 "
                         "regularizes the rank-deficient null space at "
                         "controlled cost to bin-bin correlations. Diagonal "
                         "(per-bin variance) is preserved exactly.")
    ap.add_argument("--add-norm", type=float, default=0.0,
                    help="Add a flat fully-correlated rank-1 normalization "
                         "band: C += (SIGMA*cv)(SIGMA*cv)^T. Default 0 "
                         "(no norm band). Set to 0.014 for the paper's "
                         "1.4 %% target-nucleon counting uncertainty "
                         "(Aliaga NIM 1305.5199).")
    ap.add_argument("--legacy-pair-formula", action="store_true",
                    help="Diagnostic only: revert N=2 bands to the legacy "
                         "0.5*(D0 D0^T + D1 D1^T) CV-centered pair formula "
                         "for byte-level reproduction of pre-2026-05-28 "
                         "rollups. Default: MAT mean-centered 1/N uniformly.")
    ap.add_argument("--outdir", default=".",
                    help="Output directory for plots and ROOT.")
    ap.add_argument("--out-root", default="uq_universe_covariance.root",
                    help="Output ROOT filename (under --outdir).")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    cv = load_xsec2d(args.cv)
    NX, NY = cv.shape
    print(f"[INFO] CV xsec loaded from {args.cv}  shape={cv.shape}")

    paths = sorted(glob.glob(args.glob))
    if not paths:
        sys.exit(f"[FAIL] no files matched {args.glob}")

    by_band = defaultdict(list)
    for p in paths:
        parsed = parse_universe_path(p)
        if not parsed:
            print(f"  [skip] cannot parse band/idx from {p}")
            continue
        band, idx = parsed
        a = load_xsec2d(p)
        delta = a - cv
        by_band[band].append((idx, delta, p))

    if not by_band:
        sys.exit("[FAIL] no usable universe ROOTs.")

    print(f"\n[INFO] {len(paths)} universe ROOTs across {len(by_band)} bands:")
    for band in sorted(by_band):
        idxs = sorted(i for i, _, _ in by_band[band])
        print(f"  {band:30s} n={len(idxs):3d}  idx={idxs}")

    # Reporting set: bins with nonzero CV xsec (matches the 205 paper bins).
    reported_mask_2d = cv > 0
    reported_flat = reported_mask_2d.ravel(order="C")
    n_reported = int(reported_flat.sum())
    print(f"\n[INFO] n_reported = {n_reported} bins")

    band_cov = {}
    total_cov = np.zeros((n_reported, n_reported))

    for band, entries in sorted(by_band.items()):
        idxs = [i for i, _, _ in entries]
        deltas = []
        for _, d, _ in sorted(entries, key=lambda t: t[0]):
            deltas.append(d.ravel(order="C")[reported_flat])
        D = np.stack(deltas, axis=0)  # (N_idx, n_reported)
        N_u = D.shape[0]
        if N_u < 2:
            print(f"  [skip] band {band} has only {N_u} universes — need >= 2.")
            continue
        if args.legacy_pair_formula and N_u == 2:
            cov = 0.5 * (np.outer(D[0], D[0]) + np.outer(D[1], D[1]))
            mode = "legacy_pair_sumsq"
        else:
            # MAT MnvVertErrorBand::CalcCovMx: biased sample cov,
            # mean-centered, 1/N normalization, uniform N >= 2.
            Z = D - D.mean(axis=0, keepdims=True)
            cov = (Z.T @ Z) / N_u
            mode = f"mat_mean_centered(N={N_u})"
        band_cov[band] = cov
        total_cov += cov
        diag = np.sqrt(np.maximum(np.diag(cov), 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            cv_rep = cv.ravel(order="C")[reported_flat]
            rel = np.where(cv_rep > 0, diag / cv_rep, 0)
        print(f"  [band {band:25s} {mode:18s}] "
              f"sqrt-trace = {np.sqrt(max(np.trace(cov), 0)):.3e}, "
              f"median rel = {100*np.median(rel):.3f}%, "
              f"max rel = {100*np.max(rel):.3f}%")

    cv_rep = cv.ravel(order="C")[reported_flat]

    if args.add_norm > 0:
        sigma = float(args.add_norm)
        v = sigma * cv_rep
        norm_cov = np.outer(v, v)
        band_cov["__Normalization_flat"] = norm_cov
        total_cov += norm_cov
        diag = np.sqrt(np.maximum(np.diag(norm_cov), 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(cv_rep > 0, diag / cv_rep, 0)
        print(f"  [band {'__Normalization_flat':25s} rank1_norm(sigma={sigma:.4f})] "
              f"sqrt-trace = {np.sqrt(max(np.trace(norm_cov), 0)):.3e}, "
              f"median rel = {100*np.median(rel):.3f}%, "
              f"max rel = {100*np.max(rel):.3f}%")

    def _cond_and_rank(mat, rcond=1e-12):
        evals = np.linalg.eigvalsh(0.5 * (mat + mat.T))
        evals_pos = evals[evals > evals.max() * rcond] if evals.size else evals
        cond = (evals.max() / evals_pos.min()) if evals_pos.size else float("inf")
        return cond, int(evals_pos.size)

    cond_raw, rank_raw = _cond_and_rank(total_cov)
    print(f"\n[TOTAL universe (sample)] sqrt-trace = {np.sqrt(max(np.trace(total_cov), 0)):.3e}")
    print(f"                            cond  = {cond_raw:.3e}, rank = {rank_raw}/{total_cov.shape[0]}")

    # Optional shrinkage (path-b workaround for rank-deficient sample cov).
    # S_hat = (1-lambda) * S + lambda * diag(diag(S)). Preserves per-bin
    # variances exactly; only contracts off-diagonal correlations. Full
    # rank as long as every reported bin has at least one band contribution
    # on its diagonal, which holds by construction here.
    if args.shrinkage > 0:
        lam = float(args.shrinkage)
        if not 0.0 < lam <= 1.0:
            sys.exit(f"[FAIL] --shrinkage must be in (0,1], got {lam}")
        diag_target = np.diag(np.diag(total_cov))
        total_cov = (1.0 - lam) * total_cov + lam * diag_target
        cond_shr, rank_shr = _cond_and_rank(total_cov)
        print(f"[TOTAL universe (shrunk lam={lam:.3g})] "
              f"cond = {cond_shr:.3e}, rank = {rank_shr}/{total_cov.shape[0]}")

    total_diag = np.sqrt(np.maximum(np.diag(total_cov), 0))
    with np.errstate(divide="ignore", invalid="ignore"):
        total_rel = np.where(cv_rep > 0, total_diag / cv_rep, 0)
    print(f"[TOTAL universe] sqrt-trace = {np.sqrt(max(np.trace(total_cov), 0)):.3e}")
    print(f"                   median rel = {100*np.median(total_rel):.3f}%")
    print(f"                   p84    rel = {100*np.percentile(total_rel, 84):.3f}%")
    print(f"                   max    rel = {100*np.max(total_rel):.3f}%")

    # Optional bootstrap block-sum.
    boot_cov = None
    combined_cov = None
    if args.bootstrap_cov:
        boot_cov = load_bootstrap_cov(args.bootstrap_cov)
        if boot_cov.shape != total_cov.shape:
            print(f"[WARN] bootstrap cov shape {boot_cov.shape} != "
                  f"universe cov shape {total_cov.shape}; not combining.")
            boot_cov = None
        else:
            combined_cov = total_cov + boot_cov
            comb_diag = np.sqrt(np.maximum(np.diag(combined_cov), 0))
            with np.errstate(divide="ignore", invalid="ignore"):
                comb_rel = np.where(cv_rep > 0, comb_diag / cv_rep, 0)
            print(f"\n[COMBINED universe + bootstrap]")
            print(f"  median rel = {100*np.median(comb_rel):.3f}%")
            print(f"  p84    rel = {100*np.percentile(comb_rel, 84):.3f}%")
            print(f"  max    rel = {100*np.max(comb_rel):.3f}%")

    # --- ROOT outputs ---
    out_root = os.path.join(args.outdir, args.out_root)
    rf_out = ROOT.TFile.Open(out_root, "RECREATE")

    def make_cov_h(name, title, mat):
        n = mat.shape[0]
        h = ROOT.TH2D(name, title, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, float(mat[i, j]))
        h.Write()

    def make_sigma_th2d(name, title, sigma_flat):
        full = np.zeros(NX * NY)
        full[reported_flat] = sigma_flat
        full2d = full.reshape(NX, NY, order="C")
        h = ROOT.TH2D(name, title,
                      len(PT_EDGES) - 1, PT_EDGES,
                      len(PZ_EDGES) - 1, PZ_EDGES)
        for ix in range(NX):
            for iy in range(NY):
                h.SetBinContent(ix + 1, iy + 1, float(full2d[ix, iy]))
        h.Write()

    make_cov_h("hCov_universe_total",
               "Universe-only covariance, reported bins", total_cov)
    make_sigma_th2d("hSigma_universe_total",
                    "Universe-only sqrt(diag) over reported bins", total_diag)
    for band, cov in band_cov.items():
        make_cov_h(f"hCov_universe_{band}",
                   f"Universe covariance ({band})", cov)
    if combined_cov is not None:
        make_cov_h("hCov_combined",
                   "Universe + bootstrap covariance, reported bins",
                   combined_cov)
        make_sigma_th2d("hSigma_combined",
                        "Combined sqrt(diag) over reported bins",
                        np.sqrt(np.maximum(np.diag(combined_cov), 0)))
    rf_out.Close()
    print(f"\n[wrote] {out_root}")

    # --- grouped sigma projections ---
    # Project grouped covariance diagonals back to 2D, then sum over pz
    # and pt respectively to get compact pT and pz uncertainty views.
    def project_band_sigma(cov_mat, axis):
        full = np.zeros(NX * NY)
        full[reported_flat] = np.sqrt(np.maximum(np.diag(cov_mat), 0))
        full2d = full.reshape(NX, NY, order="C")
        # Per 1D bin: sum-in-quadrature over the orthogonal axis (rough
        # marginal — exact 1D projection variance requires projecting the
        # full covariance, but the diagonal gives a fast band-by-band view).
        return np.sqrt(np.sum(full2d ** 2, axis=axis))

    group_cov = {cat: np.zeros_like(total_cov) for cat in CATEGORY_ORDER}
    for band, cov in band_cov.items():
        group_cov[category_for_band(band)] += cov
    if boot_cov is not None:
        group_cov["Statistical"] += boot_cov

    active_groups = [
        (cat, group_cov[cat])
        for cat in CATEGORY_ORDER
        if np.trace(group_cov[cat]) > 0
    ]
    grouped_total_cov = np.zeros_like(total_cov)
    for _, cov in active_groups:
        grouped_total_cov += cov

    fig, ax = plt.subplots(figsize=(8, 5))
    pt_centers = 0.5 * (PT_EDGES[:-1] + PT_EDGES[1:])
    for category, cov in active_groups:
        ax.step(pt_centers, project_band_sigma(cov, axis=1),
                where="mid", label=category, lw=1.5)
    ax.step(pt_centers, project_band_sigma(grouped_total_cov, axis=1),
            where="mid", color="k", lw=2, label="TOTAL")
    ax.set_xlabel(r"$p_T$ (GeV/c)")
    ax.set_ylabel(r"grouped 1D sigma (cm$^2$/(GeV/c)/nucleon)")
    ax.set_title(r"MEFHC grouped uncertainty, $p_T$ projection")
    ax.legend(fontsize=8, loc="best", ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "uq_universe_band_pt.png"), dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    pz_centers = 0.5 * (PZ_EDGES[:-1] + PZ_EDGES[1:])
    for category, cov in active_groups:
        ax.step(pz_centers, project_band_sigma(cov, axis=0),
                where="mid", label=category, lw=1.5)
    ax.step(pz_centers, project_band_sigma(grouped_total_cov, axis=0),
            where="mid", color="k", lw=2, label="TOTAL")
    ax.set_xlabel(r"$p_{||}$ (GeV/c)")
    ax.set_ylabel(r"grouped 1D sigma (cm$^2$/(GeV/c)/nucleon)")
    ax.set_title(r"MEFHC grouped uncertainty, $p_{||}$ projection")
    ax.legend(fontsize=8, loc="best", ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(args.outdir, "uq_universe_band_pz.png"), dpi=140)
    plt.close(fig)
    print(f"[wrote] {os.path.join(args.outdir, 'uq_universe_band_pt.png')}")
    print(f"[wrote] {os.path.join(args.outdir, 'uq_universe_band_pz.png')}")

    # --- summary file ---
    summary = os.path.join(args.outdir, "uq_universe_summary.txt")
    with open(summary, "w") as fh:
        fh.write(f"Universe-covariance summary\n")
        fh.write(f"CV: {args.cv}\n")
        fh.write(f"glob: {args.glob}\n")
        fh.write(f"n_reported bins: {n_reported}\n\n")
        fh.write(f"Per-band median relative sigma over reported bins:\n")
        for band, cov in sorted(band_cov.items()):
            diag = np.sqrt(np.maximum(np.diag(cov), 0))
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(cv_rep > 0, diag / cv_rep, 0)
            fh.write(f"  {band:30s} median={100*np.median(rel):.3f}%  "
                     f"max={100*np.max(rel):.3f}%\n")
        fh.write(f"\nGrouped median relative sigma over reported bins:\n")
        for category, cov in active_groups:
            diag = np.sqrt(np.maximum(np.diag(cov), 0))
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(cv_rep > 0, diag / cv_rep, 0)
            fh.write(f"  {category:22s} median={100*np.median(rel):.3f}%  "
                     f"max={100*np.max(rel):.3f}%\n")
        fh.write(f"\nTotal universe median rel = {100*np.median(total_rel):.3f}%\n")
        fh.write(f"Total universe max    rel = {100*np.max(total_rel):.3f}%\n")
        if combined_cov is not None:
            fh.write(f"\nCombined (universe + bootstrap) median rel = "
                     f"{100*np.median(comb_rel):.3f}%\n")
            fh.write(f"Combined max rel = {100*np.max(comb_rel):.3f}%\n")
    print(f"[wrote] {summary}")


if __name__ == "__main__":
    main()
