#!/usr/bin/env python3
"""Rigorous 3D data-vs-generator goodness-of-fit with the full covariance.

The 3D UQ campaign produced the reported-bin covariance
`uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total`
(C_syst + C_stat + C_ML, 1431 x 1431, on the mask cv>0 / C-order ravel of
(pt,pz,eavail)). This script forms the chi^2 of each generator against the
unfolded data on that grid.

WHY NOT raw pinv: the covariance is built from a finite ensemble (187 universes
+ 100 bootstrap + 10 seed), so its rank (~247) is far below 1431 -- it has a
large null space. A raw inverse/pseudo-inverse either blows up or silently drops
the null directions (carrying the model residual there for free), which is the
mistake the UQ docs warn against. Instead we use a TRUNCATED-SPECTRAL chi^2:
eigendecompose C = sum_k lambda_k v_k v_k^T, keep the modes with
lambda_k > tol * lambda_max, and

    chi2 = sum_{k kept} (v_k . r)^2 / lambda_k ,   ndf = n_kept ,   r = data-model

This is the chi^2 in the subspace the data actually constrains. We also report
the fraction of ||r||^2 that lives OUTSIDE the kept subspace (unconstrained by
the covariance -- honest caveat), sweep the truncation to show stability, and
give the diagonal-only chi^2 as a reference. The per-axis projected chi^2
(overlay_generators_band.py, full-rank 14/16/6-bin covariances) is the stable,
interpretable companion to this full-3D number.

Run in the analysis env (root_6_28):
  python compare_3d_fullcov.py \
    --data ../xsec_3d_MEFHC_5iter_lgbm.root \
    --cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total \
    --generator GENIE-CV:genie_cv_xsec3d.root \
    --generator Tune-v1:model_tunev1_xsec3d.root \
    --generator NuWro:nuwro_cv_xsec3d.root \
    --out compare_3d_fullcov

Paths in --cov are resolved relative to the 3d-unfolding directory.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
_D3 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(path):
    if os.path.isabs(path) or os.path.exists(path):
        return path
    cand = os.path.join(_D3, path)
    return cand if os.path.exists(cand) else path


def load_xsec3d(path):
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"cannot open {path}")
    h = f.Get("hXSec3D")
    if not h:
        raise SystemExit(f"hXSec3D missing in {path}")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    a = np.zeros((nx, ny, nz))
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                a[ix, iy, iz] = h.GetBinContent(ix + 1, iy + 1, iz + 1)
    f.Close()
    return a


def load_cov(spec):
    path, _, hist = spec.partition(":")
    path = _resolve(path)
    hist = hist or "hCov_combined3d_total"
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(path)
    h = f.Get(hist)
    if not h:
        raise SystemExit(f"missing {hist} in {path}")
    n = h.GetNbinsX()
    C = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close()
    return C


def truncated_chi2(r, evals, evecs, tol):
    """chi^2 in the subspace of eigenmodes with lambda > tol*lambda_max.
    Returns (chi2, ndf, captured_fraction_of_r2)."""
    lmax = evals.max()
    keep = evals > tol * lmax
    proj = evecs.T @ r                      # components of r in the eigenbasis
    chi2 = float(np.sum(proj[keep] ** 2 / evals[keep]))
    r2 = float(r @ r)
    captured = float(np.sum(proj[keep] ** 2) / r2) if r2 > 0 else 1.0
    return chi2, int(keep.sum()), captured


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--cov",
                    default="uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total")
    ap.add_argument("--generator", action="append", default=[], metavar="LABEL:FILE")
    ap.add_argument("--tol", type=float, default=1e-10,
                    help="headline eigenvalue truncation (fraction of lambda_max)")
    ap.add_argument("--out", default="compare_3d_fullcov")
    args = ap.parse_args()

    data3d = load_xsec3d(args.data)
    mask = (data3d > 0).ravel(order="C")
    d = data3d.ravel(order="C")[mask]
    n_rep = d.size
    C = load_cov(args.cov)
    if C.shape != (n_rep, n_rep):
        raise SystemExit(f"cov is {C.shape}, data reported bins = {n_rep}")
    print(f"[INFO] reported bins = {n_rep}; cov {C.shape}")

    # one symmetric eigendecomposition, reused for every generator + tol
    C = 0.5 * (C + C.T)
    evals, evecs = np.linalg.eigh(C)
    evals = np.clip(evals, 0, None)
    lmax = evals.max()
    hard_rank = int((evals > 1e-12 * lmax).sum())
    diagC = np.diag(C)
    print(f"[INFO] cov sqrt-trace = {np.sqrt(C.trace()):.3e}, "
          f"hard rank (>1e-12) = {hard_rank}/{n_rep}")

    tol_sweep = [1e-6, 1e-8, 1e-10, 1e-12]
    gens = []
    for spec in args.generator:
        lab, _, path = spec.partition(":")
        m = load_xsec3d(_resolve(path)).ravel(order="C")[mask]
        gens.append((lab, m))

    print("\n=== FULL-3D truncated-spectral chi^2 (data vs generator) ===")
    print(f"    reported bins {n_rep}; r = data - model; ndf = n_kept eigenmodes")
    hdr = f"  {'generator':10s} " + "".join(f"  chi2/ndf@{t:.0e}" for t in tol_sweep) \
          + "   diag chi2/ndf   ||r||_out%"
    print(hdr)
    results = {}
    for lab, m in gens:
        r = d - m
        cells = []
        for t in tol_sweep:
            chi2, ndf, cap = truncated_chi2(r, evals, evecs, t)
            cells.append(f"{chi2/ndf:7.1f}({ndf})")
            if abs(t - args.tol) < 1e-30:
                results[lab] = (chi2, ndf, cap)
        # diagonal-only reference (ignores correlations)
        ok = diagC > 0
        chi2_diag = float(np.sum(r[ok] ** 2 / diagC[ok]))
        # headline captured fraction
        _, _, cap_h = truncated_chi2(r, evals, evecs, args.tol)
        line = f"  {lab:10s} " + "".join(f"  {c:>14s}" for c in cells)
        line += f"   {chi2_diag/int(ok.sum()):9.1f}   {100*(1-cap_h):7.2f}"
        print(line)

    print(f"\n  headline (tol={args.tol:.0e}): chi2/ndf and p-value (TMath.Prob)")
    for lab, (chi2, ndf, cap) in results.items():
        p = ROOT.TMath.Prob(chi2, ndf)
        print(f"    {lab:10s}  chi2/ndf = {chi2:9.1f}/{ndf} = {chi2/ndf:6.2f}"
              f"   p = {p:.2e}   (captures {100*cap:.1f}% of ||r||^2)")

    # ---- diagnostic plot: eigenvalue spectrum + chi2/ndf vs truncation ----
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    axs[0].semilogy(np.arange(1, n_rep + 1), evals[::-1] / lmax, ".", ms=3)
    axs[0].axhline(args.tol, color="r", ls="--", lw=1,
                   label=f"tol = {args.tol:.0e} (keep {results and list(results.values())[0][1]} modes)")
    axs[0].set_xlabel("eigenmode rank"); axs[0].set_ylabel(r"$\lambda/\lambda_{\max}$")
    axs[0].set_title("Covariance spectrum (rank-limited)")
    axs[0].legend(fontsize=8); axs[0].grid(alpha=0.3)
    fine = np.logspace(-13, -4, 40)
    colors = ["#C44E52", "#4C72B0", "#2ca02c", "#9467bd"]
    for i, (lab, m) in enumerate(gens):
        r = d - m
        y = [truncated_chi2(r, evals, evecs, t)[0] / max(truncated_chi2(r, evals, evecs, t)[1], 1)
             for t in fine]
        axs[1].semilogx(fine, y, color=colors[i % len(colors)], label=lab,
                        marker=technote_style.gen_marker(lab), markevery=5, ms=5)
    axs[1].axvline(args.tol, color="r", ls="--", lw=1)
    axs[1].set_xlabel("truncation tol"); axs[1].set_ylabel(r"$\chi^2/$ndf")
    axs[1].set_title("Goodness-of-fit vs truncation")
    axs[1].legend(fontsize=8); axs[1].grid(alpha=0.3)
    fig.tight_layout()
    out = f"{args.out}.png"
    fig.savefig(out, dpi=140)
    print(f"\n[wrote] {out}")


if __name__ == "__main__":
    main()
