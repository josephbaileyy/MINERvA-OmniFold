#!/usr/bin/env python3
"""Universe-covariance rollup for the 3D OmniFold UQ campaign.

3D analogue of ../../2d-unfolding/uq/analyze_universes.py. Consumes a CV 3D
unfold and N per-(band,idx) universe unfolds produced by
`unfold_3d_omnifold_unbinned.py --universe BAND:IDX`, reading the full
`hXSec3D` (TH3D, pT x p|| x E_avail) from each. Computes:

  - Per-(band,idx) delta = xsec3d_universe - xsec3d_cv  (bin-by-bin, flattened
    in C order over (pt, pz, ea))
  - Per-band covariance, uniform N >= 2 (MAT-conformant; matches
    PlotUtils/MnvVertErrorBand::CalcCovMx -- biased sample cov, mean-centered,
    1/N): C_band = (1/N) sum_u (X_u - <X>)(X_u - <X>)^T
  - Optional flat rank-1 normalization band via --add-norm SIGMA (0.014 for the
    1.4% target-nucleon counting uncertainty; Aliaga NIM 1305.5199).
  - Total = sum of per-band covariances (bands uncorrelated).

The reporting set is the 3D bins with nonzero CV xsec (drops empty/under-filled
grid cells). Covariances are on those reported bins, flattened consistently.

Outputs (under --outdir):
  - uq_universe_3d_summary.txt        per-band + grouped relative sigma
  - uq_universe_3d_band_{pt,pz,eavail}.png   grouped 1D sigma per axis
  - uq_universe_3d_covariance.root    hCov_universe3d_total + per-band +
        hSigma_universe3d_total (TH3D of per-bin sqrt(diag) over the full grid)

Usage:
  python uq_3d/analyze_universes_3d.py \
      --cv xsec_3d_MEFHC_5iter_lgbm.root \
      --glob 'uq_3d/universe_sweep/3d_xsec_*_uni_full_*.root' \
      --add-norm 0.014 --outdir uq_3d/universe_stage2_3d/
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

ROOT.gROOT.SetBatch(True)

# Filename pattern: 3d_xsec_<...>_uni_full_<BAND>_<IDX>.root  (also matches _uni_)
UNI_RE = re.compile(r".*_uni(?:_full)?_(?P<band>[A-Za-z0-9_]+?)_(?P<idx>\d+)\.root$")

CATEGORY_ORDER = [
    "Flux",
    "Models",
    "Normalization",
    "Statistical",
    "Hadronic response",
    "Muon reconstruction",
]


def category_for_band(band):
    """Map MINERvA universe bands into compact plot categories (same as 2D)."""
    clean = band[len("full_"):] if band.startswith("full_") else band
    if clean == "Flux":
        return "Flux"
    if clean == "__Normalization_flat":
        return "Normalization"
    if (clean.startswith("Fr") or clean.startswith("MFP_") or
            clean.startswith("GEANT_")):
        return "Hadronic response"
    if (clean.startswith("Muon_") or clean.startswith("BeamAngle") or
            clean in {"MuonResolution", "MinosEfficiency"}):
        return "Muon reconstruction"
    return "Models"


def _axis_edges(ax):
    return np.array([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])


def load_xsec3d(path, want_edges=False):
    rf = ROOT.TFile.Open(path)
    if not rf or rf.IsZombie():
        sys.exit(f"[FAIL] cannot open {path}")
    h = rf.Get("hXSec3D")
    if not h:
        sys.exit(f"[FAIL] hXSec3D missing in {path}")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    a = np.zeros((nx, ny, nz))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            for iz in range(1, nz + 1):
                a[ix - 1, iy - 1, iz - 1] = h.GetBinContent(ix, iy, iz)
    edges = None
    if want_edges:
        edges = (_axis_edges(h.GetXaxis()), _axis_edges(h.GetYaxis()),
                 _axis_edges(h.GetZaxis()))
    rf.Close()
    return (a, edges) if want_edges else a


def parse_universe_path(path):
    m = UNI_RE.match(os.path.basename(path))
    return (m.group("band"), int(m.group("idx"))) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", required=True, help="CV 3D unfold ROOT (no --universe).")
    ap.add_argument("--glob", required=True,
                    help="Glob for universe 3D unfold ROOTs.")
    ap.add_argument("--add-norm", type=float, default=0.0,
                    help="Add a flat fully-correlated rank-1 normalization band: "
                         "C += (SIGMA*cv)(SIGMA*cv)^T. 0.014 = paper 1.4%% "
                         "target-nucleon counting uncertainty.")
    ap.add_argument("--legacy-pair-formula", action="store_true",
                    help="Diagnostic: revert N=2 bands to 0.5*(D0 D0^T+D1 D1^T).")
    ap.add_argument("--outdir", default="uq_3d/universe_stage2_3d")
    ap.add_argument("--out-root", default="uq_universe_3d_covariance.root")
    ap.add_argument("--bootstrap-cov", nargs="+", default=None,
                    metavar="ROOT[:HIST]",
                    help="One or more extra covariances (from build_bootstrap_cov_3d.py) "
                         "to block-sum into the combined budget C_syst + sum(extras), "
                         "e.g. the statistical (hCov_stat3d_reported) and ML/seedscan "
                         "(hCov_ml3d_reported) covs. Each is 'path' (default hist "
                         "hCov_stat3d_reported) or 'path:hist'. Must share the same "
                         "reported-bin flattening (same --cv).")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    cv, (pt_e, pz_e, ea_e) = load_xsec3d(args.cv, want_edges=True)
    NX, NY, NZ = cv.shape
    print(f"[INFO] CV xsec3d from {args.cv}  shape={cv.shape}")

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
        by_band[band].append((idx, load_xsec3d(p) - cv, p))

    if not by_band:
        sys.exit("[FAIL] no usable universe ROOTs.")

    print(f"\n[INFO] {len(paths)} universe ROOTs across {len(by_band)} bands:")
    for band in sorted(by_band):
        idxs = sorted(i for i, _, _ in by_band[band])
        print(f"  {band:30s} n={len(idxs):3d}")

    # Reporting set: 3D bins with nonzero CV xsec.
    reported_mask = cv > 0
    reported_flat = reported_mask.ravel(order="C")
    n_reported = int(reported_flat.sum())
    print(f"\n[INFO] n_reported = {n_reported} of {NX*NY*NZ} 3D bins")

    band_cov = {}
    total_cov = np.zeros((n_reported, n_reported))

    for band, entries in sorted(by_band.items()):
        deltas = [d.ravel(order="C")[reported_flat]
                  for _, d, _ in sorted(entries, key=lambda t: t[0])]
        D = np.stack(deltas, axis=0)  # (N_idx, n_reported)
        N_u = D.shape[0]
        if N_u < 2:
            print(f"  [skip] band {band} has only {N_u} universes — need >= 2.")
            continue
        if args.legacy_pair_formula and N_u == 2:
            cov = 0.5 * (np.outer(D[0], D[0]) + np.outer(D[1], D[1]))
            mode = "legacy_pair_sumsq"
        else:
            Z = D - D.mean(axis=0, keepdims=True)
            cov = (Z.T @ Z) / N_u
            mode = f"mat_mean_centered(N={N_u})"
        band_cov[band] = cov
        total_cov += cov
        diag = np.sqrt(np.maximum(np.diag(cov), 0))
        cv_rep = cv.ravel(order="C")[reported_flat]
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(cv_rep > 0, diag / cv_rep, 0)
        print(f"  [band {band:25s} {mode:18s}] "
              f"sqrt-trace={np.sqrt(max(np.trace(cov), 0)):.3e}, "
              f"median rel={100*np.median(rel):.3f}%, max rel={100*np.max(rel):.3f}%")

    cv_rep = cv.ravel(order="C")[reported_flat]

    if args.add_norm > 0:
        sigma = float(args.add_norm)
        v = sigma * cv_rep
        norm_cov = np.outer(v, v)
        band_cov["__Normalization_flat"] = norm_cov
        total_cov += norm_cov
        print(f"  [band {'__Normalization_flat':25s} rank1_norm(sigma={sigma:.4f})] "
              f"sqrt-trace={np.sqrt(max(np.trace(norm_cov), 0)):.3e}")

    def _cond_and_rank(mat, rcond=1e-12):
        ev = np.linalg.eigvalsh(0.5 * (mat + mat.T))
        ev_pos = ev[ev > ev.max() * rcond] if ev.size else ev
        cond = (ev.max() / ev_pos.min()) if ev_pos.size else float("inf")
        return cond, int(ev_pos.size)

    cond, rank = _cond_and_rank(total_cov)
    total_diag = np.sqrt(np.maximum(np.diag(total_cov), 0))
    with np.errstate(divide="ignore", invalid="ignore"):
        total_rel = np.where(cv_rep > 0, total_diag / cv_rep, 0)
    print(f"\n[TOTAL universe 3D] sqrt-trace={np.sqrt(max(np.trace(total_cov), 0)):.3e}")
    print(f"                     cond={cond:.3e}, rank={rank}/{total_cov.shape[0]}")
    print(f"                     median rel={100*np.median(total_rel):.3f}%, "
          f"p84={100*np.percentile(total_rel, 84):.3f}%, "
          f"max={100*np.max(total_rel):.3f}%")

    # --- optional block-sum with extra (stat / ML) covariances ---
    combined_cov = None
    comb_rel = None
    if args.bootstrap_cov:
        combined_cov = total_cov.copy()
        for spec in args.bootstrap_cov:
            bpath, bhist = (spec.rsplit(":", 1) if ":" in spec
                            else (spec, "hCov_stat3d_reported"))
            bf = ROOT.TFile.Open(bpath)
            if not bf or bf.IsZombie():
                sys.exit(f"[FAIL] cannot open extra cov {bpath}")
            bh = bf.Get(bhist)
            if not bh:
                sys.exit(f"[FAIL] hist {bhist!r} missing in {bpath}")
            nb = bh.GetNbinsX()
            extra = np.array([[bh.GetBinContent(i + 1, j + 1) for j in range(nb)]
                              for i in range(nb)])
            bf.Close()
            if extra.shape != total_cov.shape:
                sys.exit(f"[FAIL] extra cov {bpath}:{bhist} shape {extra.shape} != "
                         f"universe cov shape {total_cov.shape} — mismatched reported "
                         f"binning (run build_bootstrap_cov_3d.py with the same --cv).")
            combined_cov += extra
            print(f"  [+ block-summed {bpath}:{bhist}  "
                  f"sqrt-trace={np.sqrt(max(np.trace(extra), 0)):.3e}]")
        comb_diag = np.sqrt(np.maximum(np.diag(combined_cov), 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            comb_rel = np.where(cv_rep > 0, comb_diag / cv_rep, 0)
        ccond, crank = _cond_and_rank(combined_cov)
        print(f"\n[COMBINED syst+extras 3D] sqrt-trace="
              f"{np.sqrt(max(np.trace(combined_cov), 0)):.3e}")
        print(f"                          cond={ccond:.3e}, rank={crank}/{combined_cov.shape[0]}")
        print(f"                          median rel={100*np.median(comb_rel):.3f}%, "
              f"p84={100*np.percentile(comb_rel, 84):.3f}%, "
              f"max={100*np.max(comb_rel):.3f}%")

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

    def make_sigma_th3d(name, title, sigma_flat):
        full = np.zeros(NX * NY * NZ)
        full[reported_flat] = sigma_flat
        full3d = full.reshape(NX, NY, NZ, order="C")
        h = ROOT.TH3D(name, title, NX, pt_e, NY, pz_e, NZ, ea_e)
        for ix in range(NX):
            for iy in range(NY):
                for iz in range(NZ):
                    h.SetBinContent(ix + 1, iy + 1, iz + 1, float(full3d[ix, iy, iz]))
        h.Write()

    make_cov_h("hCov_universe3d_total",
               "Universe-only 3D covariance, reported bins", total_cov)
    make_sigma_th3d("hSigma_universe3d_total",
                    "Universe-only sqrt(diag) over reported 3D bins", total_diag)
    for band, cov in band_cov.items():
        make_cov_h(f"hCov_universe3d_{band}", f"Universe 3D covariance ({band})", cov)
    if combined_cov is not None:
        make_cov_h("hCov_combined3d_total",
                   "Combined syst+stat 3D covariance, reported bins", combined_cov)
        make_sigma_th3d("hSigma_combined3d_total",
                        "Combined syst+stat sqrt(diag) over reported 3D bins",
                        np.sqrt(np.maximum(np.diag(combined_cov), 0)))
    rf_out.Close()
    print(f"\n[wrote] {out_root}")

    # --- grouped per-axis sigma projections (quadrature of diagonal; approx) ---
    def project_axis_sigma(cov_mat, axis):
        full = np.zeros(NX * NY * NZ)
        full[reported_flat] = np.sqrt(np.maximum(np.diag(cov_mat), 0))
        full3d = full.reshape(NX, NY, NZ, order="C")
        keep = tuple(a for a in (0, 1, 2) if a != axis)
        return np.sqrt(np.sum(full3d ** 2, axis=keep))

    group_cov = {cat: np.zeros_like(total_cov) for cat in CATEGORY_ORDER}
    for band, cov in band_cov.items():
        group_cov[category_for_band(band)] += cov
    active = [(c, group_cov[c]) for c in CATEGORY_ORDER if np.trace(group_cov[c]) > 0]
    grouped_total = sum((cov for _, cov in active), np.zeros_like(total_cov))

    AXES = [(0, pt_e, r"$p_T$ (GeV/c)", "pt"),
            (1, pz_e, r"$p_{||}$ (GeV/c)", "pz"),
            (2, ea_e, r"$E_{avail}$ (GeV)", "eavail")]
    for axis, edges, xlabel, tag in AXES:
        centers = 0.5 * (edges[:-1] + edges[1:])
        fig, ax = plt.subplots(figsize=(8, 5))
        for category, cov in active:
            ax.step(centers, project_axis_sigma(cov, axis), where="mid",
                    label=category, lw=1.5)
        ax.step(centers, project_axis_sigma(grouped_total, axis), where="mid",
                color="k", lw=2, label="TOTAL")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("grouped 1D sigma (cm$^2$/nucleon, per-axis)")
        ax.set_title(f"MEFHC 3D grouped uncertainty, {tag} projection")
        ax.legend(fontsize=8, loc="best", ncol=2)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        outp = os.path.join(args.outdir, f"uq_universe_3d_band_{tag}.png")
        fig.savefig(outp, dpi=140)
        plt.close(fig)
        print(f"[wrote] {outp}")

    # --- summary file ---
    summary = os.path.join(args.outdir, "uq_universe_3d_summary.txt")
    with open(summary, "w") as fh:
        fh.write("Universe 3D-covariance summary\n")
        fh.write(f"CV: {args.cv}\nglob: {args.glob}\n")
        fh.write(f"n_reported 3D bins: {n_reported} of {NX*NY*NZ}\n")
        fh.write(f"total cond={cond:.3e} rank={rank}/{total_cov.shape[0]}\n\n")
        fh.write("Per-band median / max relative sigma over reported bins:\n")
        for band, cov in sorted(band_cov.items()):
            diag = np.sqrt(np.maximum(np.diag(cov), 0))
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(cv_rep > 0, diag / cv_rep, 0)
            fh.write(f"  {band:30s} median={100*np.median(rel):.3f}%  "
                     f"max={100*np.max(rel):.3f}%\n")
        fh.write("\nGrouped median relative sigma:\n")
        for category, cov in active:
            diag = np.sqrt(np.maximum(np.diag(cov), 0))
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(cv_rep > 0, diag / cv_rep, 0)
            fh.write(f"  {category:22s} median={100*np.median(rel):.3f}%  "
                     f"max={100*np.max(rel):.3f}%\n")
        fh.write(f"\nTotal universe median rel={100*np.median(total_rel):.3f}%  "
                 f"max={100*np.max(total_rel):.3f}%\n")
    print(f"[wrote] {summary}")


if __name__ == "__main__":
    main()
