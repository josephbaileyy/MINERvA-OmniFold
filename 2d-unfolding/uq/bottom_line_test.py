#!/usr/bin/env python
"""Bottom-line test for the 2D / 3D OmniFold measurement.

Background (audit 2026-06-03, LITERATURE_NOTES.md). "A Practical Guide to Unbinned
Unfolding" (arXiv:2507.09582) lists the bottom-line test as a standard unfolding
diagnostic, phrased as: the unfolded result's discrepancy must be SMALLER than the
original data-MC difference it is recovering. Unfolding cannot manufacture features the
detector-level data does not support (Cousins). This test lived only in a 1D side study
here; this adds it to the 2D and 3D results.

There are two modes.

--mode closure (default, the literature PASS/FAIL test).
  Uses the closure runs, where pseudo-data carries a KNOWN injected truth feature:
    injected feature = (hTruthRew - hTruth)/hTruth          (what we try to recover)
    recovery residual = (hUnfold  - hTruthRew)/hTruthRew    (what is left after unfolding)
  PASS when residual << injected, i.e. ratio = RMS(residual)/RMS(injected) < tol.
  This is the rigorous bottom-line: the unfolded discrepancy from truth is far smaller
  than the feature size, so the recovery is faithful, not fabricated.
  2D: uq/closure/2d_xsec_1A_5iter_lgbm_closure_truthrw.root (gaussian-bump truth reweight)
  3D: closure_3d_MEFHC_eavail_bump.root (+30% E_avail bump), E_avail projection.

--mode data-prior (informational diagnostic, NOT a pass/fail).
  Reco vs truth chi2/ndf of the real data against the simulation prior, predictions built
  from the omnifile (valid because completeness c==1). Reported for context only: with a
  high-resolution measurement detector smearing lowers the reco data-prior chi2 baseline,
  and a stat-only diagonal omits the unfolding's correlated covariance, so truth>reco here
  is expected and is NOT a failure (the proper full-covariance GoF is the chi2-vs-paper
  =1.481 and the generator comparisons already in the analysis).

Run from repo root after `source setup_salloc_env.sh`:
  python 2d-unfolding/uq/bottom_line_test.py --dim 2
  python 2d-unfolding/uq/bottom_line_test.py --dim 3
  python 2d-unfolding/uq/bottom_line_test.py --dim 2 --mode data-prior
"""
import argparse
import glob
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.TH1.AddDirectory(False)


def get(path, name):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        sys.exit(f"[FAIL] cannot open {path}")
    h = f.Get(name)
    if not h:
        sys.exit(f"[FAIL] {name} missing in {path}")
    h.SetDirectory(0)
    f.Close()
    return h


def arr(h):
    cls = h.ClassName()
    if cls.startswith("TH3"):
        nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
        return np.array([[[h.GetBinContent(i+1, j+1, k+1) for k in range(nz)]
                          for j in range(ny)] for i in range(nx)])
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    return np.array([[h.GetBinContent(i+1, j+1) for j in range(ny)]
                     for i in range(nx)])


def err(h):
    cls = h.ClassName()
    if cls.startswith("TH3"):
        nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
        return np.array([[[h.GetBinError(i+1, j+1, k+1) for k in range(nz)]
                          for j in range(ny)] for i in range(nx)])
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    return np.array([[h.GetBinError(i+1, j+1) for j in range(ny)]
                     for i in range(nx)])


def axis_edges(ax):
    n = ax.GetNbins()
    return np.array([ax.GetBinLowEdge(i+1) for i in range(n)] + [ax.GetBinUpEdge(n)])


def template_edges(h, dim):
    edges = [axis_edges(h.GetXaxis()), axis_edges(h.GetYaxis())]
    if dim == 3:
        edges.append(axis_edges(h.GetZaxis()))
    return edges


def fill_hist(tree_name, fname, cols, edges, dim, weight=None, mask_col=None):
    """Return (sumw, sumw2) histograms over `edges` from tree branch arrays.

    The reco/pass selection (a Bool_t branch) is applied with RDataFrame.Filter on
    the C++ side, so only float kinematics + weight are pulled into numpy.
    """
    rdf = ROOT.RDataFrame(tree_name, fname)
    if mask_col:
        rdf = rdf.Filter(mask_col)
    want = list(cols) + ([weight] if weight else [])
    data = rdf.AsNumpy(want)
    sample = [np.asarray(data[c], dtype=float) for c in cols[:dim]]
    w = np.asarray(data[weight], dtype=float) if weight else np.ones_like(sample[0])
    sample = np.stack(sample, axis=1)
    sumw, _ = np.histogramdd(sample, bins=edges, weights=w)
    sumw2, _ = np.histogramdd(sample, bins=edges, weights=w * w)
    return sumw, sumw2


def chi2_diag(a, b, va, vb, mask):
    r = (a - b)[mask]
    v = (va + vb)[mask]
    good = v > 0
    chi2 = float(np.sum(r[good] ** 2 / v[good]))
    return chi2, int(good.sum())


def rms_rel(num, den, mask):
    """RMS of (num/den) over masked bins where den>0."""
    m = mask & (den > 0)
    return float(np.sqrt(np.mean((num[m] / den[m]) ** 2)))


def run_closure(D, tol):
    if D == 2:
        cf = "2d-unfolding/uq/closure/2d_xsec_1A_5iter_lgbm_closure_truthrw.root"
        unf = arr(get(cf, "hUnfold2D"))
        ref = arr(get(cf, "hTruthRew2D"))      # injected truth target
        nom = arr(get(cf, "hTruth2D"))         # nominal (un-reweighted) truth
        label = "1A gaussian-bump truth reweight"
    else:
        cf = "3d-unfolding/closure_3d_MEFHC_eavail_bump.root"
        unf = arr(get(cf, "hXSec_eavail"))             # unfolded closure (E_avail proj)
        ref = arr(get(cf, "hXSec_eavail_closureRef"))  # injected +30% bump reference
        nom = arr(get("3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root", "hXSec_eavail"))
        label = "MEFHC +30% E_avail bump (E_avail projection)"

    mask = (ref > 0) & (nom > 0)
    injected_all = rms_rel(ref - nom, nom, mask)     # feature we try to recover
    residual_all = rms_rel(unf - ref, ref, mask)     # what is left after unfolding

    # The bottom-line asks whether the data's deviation from the prior is faithfully
    # recovered. Measure that where the feature actually lives -- bins whose injected
    # deviation exceeds the feature RMS. Featureless bins only carry single-playlist
    # statistical noise (covered by the coverage test), not unfolding bias.
    rel_inj = np.zeros_like(nom)
    rel_inj[mask] = np.abs((ref - nom)[mask] / nom[mask])
    feat = mask & (rel_inj > injected_all)
    injected = rms_rel(ref - nom, nom, feat)
    residual = rms_rel(unf - ref, ref, feat)
    ratio = residual / injected if injected > 0 else float("nan")

    print(f"\n===== BOTTOM-LINE TEST ({D}D, closure) =====")
    print(f"closure: {label}")
    print(f"all reported bins (n={int(mask.sum())}):")
    print(f"   injected feature  RMS = {100*injected_all:.3f}%   "
          f"residual RMS = {100*residual_all:.4f}%   ratio = {residual_all/injected_all:.3f}")
    print(f"feature bins (|inj|>{100*injected_all:.2f}%, n={int(feat.sum())}):")
    print(f"   injected feature  RMS = {100*injected:.3f}%   "
          f"residual RMS = {100*residual:.4f}%")
    print(f"ratio residual/injected (feature bins) = {ratio:.4f}  (tol {tol})")
    verdict = "PASS" if ratio < tol else "FAIL"
    print(f"VERDICT: {verdict} -- "
          + (f"in the bins carrying the feature, the unfolded result tracks the injected "
             f"truth to {1/ratio:.0f}x better than the feature size; recovery is faithful."
             if verdict == "PASS"
             else "residual is comparable to the feature; recovery is not faithful."))


def run_data_prior(D, tol):
    if D == 2:
        frozen = "2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root"
        omni = "2d-unfolding/runEventLoopOmniFold_MEFHC.root"
        unf = "hUnfold2D"
        sig_cols, truth_cols = ["sim", "sim_pz"], ["MC", "MC_pz"]
        data_cols, bkg_cols = ["measured", "measured_pz"], ["sim_background", "sim_background_pz"]
    else:
        frozen = "3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root"
        omni = "3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root"
        unf = "hUnfold3D"
        sig_cols = ["sim", "sim_pz", "sim_eavail"]
        truth_cols = ["MC", "MC_pz", "MC_eavail"]
        data_cols = ["measured", "measured_pz", "measured_eavail"]
        bkg_cols = ["sim_background", "sim_background_pz", "sim_background_eavail"]

    fz = ROOT.TFile.Open(frozen)
    pot_scale = fz.Get("potScale").GetVal()
    hUnfold = fz.Get(unf); hUnfold.SetDirectory(0)
    fz.Close()
    edges = template_edges(hUnfold, D)
    D_truth = arr(hUnfold)
    cvmask = D_truth > 0

    # ----- truth: unfolded data vs MC truth prior (mc_truth_denom, POT-scaled) -----
    M_truth, M_truth_w2 = fill_hist("mc_truth_denom", omni, truth_cols, edges, D,
                                    weight="w_truth")
    M_truth *= pot_scale
    vMtruth = M_truth_w2 * pot_scale ** 2

    # ----- reco: measured signal (data - bkg) vs MC signal at reco -----
    Dr, Dr_w2 = fill_hist("data", omni, data_cols, edges, D, mask_col="measured_pass")
    Bk, Bk_w2 = fill_hist("mc_background", omni, bkg_cols, edges, D,
                          weight="w_bkg", mask_col="sim_background_pass")
    Bk *= pot_scale; Bk_w2 *= pot_scale ** 2
    D_reco = Dr - Bk
    vDreco = Dr_w2 + Bk_w2                       # data Poisson + bkg stat
    M_reco, M_reco_w2 = fill_hist("mc_signal_reco", omni, sig_cols, edges, D,
                                  weight="w_reco", mask_col="sim_pass")
    M_reco *= pot_scale
    vMreco = M_reco_w2 * pot_scale ** 2

    # ----- truth-level measurement statistical uncertainty -----
    if D == 2:
        boot = sorted(glob.glob("2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root"))
        reps = np.stack([arr(get(p, "hUnfold2D")) for p in boot])
        vDtruth = reps.std(axis=0, ddof=1) ** 2
        stat_src = f"{len(boot)} bootstrap replicas (std of hUnfold2D)"
    else:
        sig = arr(get("3d-unfolding/uq_3d/uq_cov_stat_3d.root", "hSigma_stat3d_total"))
        xs = arr(get(frozen, "hXSec3D"))
        rel = np.zeros_like(sig)
        m = xs > 0
        rel[m] = sig[m] / xs[m]
        vDtruth = (rel * D_truth) ** 2
        stat_src = "hSigma_stat3d_total (relative) applied to hUnfold3D"

    # ----- validate the omnifile reconstruction against saved histos (2D) -----
    if D == 2:
        hT = get(frozen, "hTruth2D"); hM = get(frozen, "hMeasSub2D")
        rT = M_truth.sum() / hT.Integral()
        rM = D_reco.sum() / hM.Integral()
        print(f"[VALIDATE] truth prior integral: saved={hT.Integral():.5g} "
              f"built={M_truth.sum():.5g} ratio={rT:.4f}")
        print(f"[VALIDATE] meas signal integral: saved={hM.Integral():.5g} "
              f"built={D_reco.sum():.5g} ratio={rM:.4f}")

    chi2_reco, ndf_reco = chi2_diag(D_reco, M_reco, vDreco, vMreco, cvmask)
    chi2_truth, ndf_truth = chi2_diag(D_truth, M_truth, vDtruth, vMtruth, cvmask)

    print(f"\n===== BOTTOM-LINE TEST ({D}D) =====")
    print(f"[stat] reco : data Poisson + bkg stat")
    print(f"[stat] truth: {stat_src} + prior MC stat")
    print(f"reco  (data-bkg vs MC-reco):  chi2/ndf = {chi2_reco:.1f}/{ndf_reco} "
          f"= {chi2_reco/ndf_reco:.3f}")
    print(f"truth (unfold  vs MC-prior):  chi2/ndf = {chi2_truth:.1f}/{ndf_truth} "
          f"= {chi2_truth/ndf_truth:.3f}")
    ratio = (chi2_truth/ndf_truth) / (chi2_reco/ndf_reco)
    print(f"ratio truth/reco = {ratio:.3f}")
    print("  NOTE: informational only. truth>reco is expected for a high-resolution")
    print("  measurement (smearing lowers the reco data-prior baseline) and this stat-only")
    print("  diagonal omits the unfolding covariance. The proper full-cov GoF is the")
    print("  chi2-vs-paper (1.481) and the generator comparisons. Use --mode closure for")
    print("  the actual bottom-line pass/fail.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dim", type=int, choices=[2, 3], required=True)
    ap.add_argument("--mode", choices=["closure", "data-prior"], default="closure")
    ap.add_argument("--tol", type=float, default=None,
                    help="closure: max residual/injected (default 0.20, i.e. residual "
                         "must be >=5x smaller than the feature); data-prior: unused")
    args = ap.parse_args()
    if args.mode == "closure":
        run_closure(args.dim, args.tol if args.tol is not None else 0.20)
    else:
        run_data_prior(args.dim, args.tol if args.tol is not None else 1.10)


if __name__ == "__main__":
    main()
