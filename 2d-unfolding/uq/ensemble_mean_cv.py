#!/usr/bin/env python
"""Ensemble-mean central value + ML-stochasticity audit (2D or 3D).

Background (audit 2026-06-03, LITERATURE_NOTES.md). Published OmniFold practice
(T2K arXiv:2504.06857; Practical Guide arXiv:2507.09582, already cited in the 2D
driver) takes the *mean* over an ensemble of ML trials as the central value, which
de-noises the headline spectrum. This analysis instead keeps a single-seed central
value and uses the seed scan only to *measure* the ML band.

This script does two things, reusing the existing per-seed xsec ROOT files (no
re-unfolding):

  1. Builds the ensemble-mean cross section and writes it to a NEW *_ensemble.root
     (the frozen single-seed file is never touched).
  2. Audits the ML-stochasticity assumption: it compares the single-seed frozen CV
     to the seed-ensemble mean in units of the per-bin seed scatter. Because the
     driver's --seed only pins the GBDT random_state (not the train/test split),
     the seed band is expected to be a *lower bound* on the true ML stochasticity;
     a large frozen-vs-ensemble pull is the symptom.

Usage (run from repo root after `source setup_salloc_env.sh`):

  python 2d-unfolding/uq/ensemble_mean_cv.py \
      --frozen 2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root \
      --seeds  '2d-unfolding/seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed*.root' \
      --hist   hXSec2D \
      --out    2d-unfolding/uq/2d_crossSection_omnifold_MEFHC_5iter_ensemble.root

  python 2d-unfolding/uq/ensemble_mean_cv.py \
      --frozen 3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root \
      --seeds  '3d-unfolding/seedscan_3d/3d_xsec_MEFHC_5iter_lgbm_seed*.root' \
      --hist   hXSec3D \
      --out    3d-unfolding/xsec_3d_MEFHC_5iter_lgbm_ensemble.root
"""
import argparse
import glob
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)


def load_hist(path, name):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        sys.exit(f"[FAIL] cannot open {path}")
    h = f.Get(name)
    if not h:
        sys.exit(f"[FAIL] {name} missing in {path}")
    h.SetDirectory(0)
    f.Close()
    return h


def hist_to_array(h):
    """Flatten a TH1/TH2/TH3 over physical bins (drop under/overflow), C order."""
    nb = h.GetNcells()
    vals = np.array([h.GetBinContent(i) for i in range(nb)])
    # mask off under/overflow via the per-axis bin loop instead:
    cls = h.ClassName()
    if cls.startswith("TH3"):
        nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
        a = np.array([[[h.GetBinContent(ix + 1, iy + 1, iz + 1)
                        for iz in range(nz)] for iy in range(ny)]
                      for ix in range(nx)])
    elif cls.startswith("TH2"):
        nx, ny = h.GetNbinsX(), h.GetNbinsY()
        a = np.array([[h.GetBinContent(ix + 1, iy + 1)
                       for iy in range(ny)] for ix in range(nx)])
    else:
        nx = h.GetNbinsX()
        a = np.array([h.GetBinContent(ix + 1) for ix in range(nx)])
    return a


def write_like(template, name, data, out):
    """Clone template histogram, fill with `data`, write to open TFile `out`."""
    h = template.Clone(name)
    h.SetDirectory(0)
    cls = h.ClassName()
    if cls.startswith("TH3"):
        nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    h.SetBinContent(ix + 1, iy + 1, iz + 1, data[ix, iy, iz])
                    h.SetBinError(ix + 1, iy + 1, iz + 1, 0.0)
    elif cls.startswith("TH2"):
        nx, ny = h.GetNbinsX(), h.GetNbinsY()
        for ix in range(nx):
            for iy in range(ny):
                h.SetBinContent(ix + 1, iy + 1, data[ix, iy])
                h.SetBinError(ix + 1, iy + 1, 0.0)
    else:
        nx = h.GetNbinsX()
        for ix in range(nx):
            h.SetBinContent(ix + 1, data[ix])
            h.SetBinError(ix + 1, 0.0)
    out.cd()
    h.Write()
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen", required=True)
    ap.add_argument("--seeds", required=True, help="glob for per-seed xsec files")
    ap.add_argument("--hist", required=True, help="histogram name, e.g. hXSec2D / hXSec3D")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    seed_paths = sorted(glob.glob(args.seeds))
    if len(seed_paths) < 2:
        sys.exit(f"[FAIL] need >=2 seed files, found {len(seed_paths)} for {args.seeds}")

    frozen_h = load_hist(args.frozen, args.hist)
    cv = hist_to_array(frozen_h)
    seeds = np.stack([hist_to_array(load_hist(p, args.hist)) for p in seed_paths])
    n = seeds.shape[0]
    emean = seeds.mean(axis=0)
    estd = seeds.std(axis=0, ddof=1)

    m = cv > 0
    nbins = int(m.sum())
    rel_std = estd[m] / cv[m]                       # seed band (model-init only)
    rel_shift = (emean[m] - cv[m]) / cv[m]          # ensemble - frozen
    pull = np.abs(cv[m] - emean[m]) / (estd[m] + 1e-300)

    print(f"[INFO] hist={args.hist}  seeds={n}  reported bins (cv>0)={nbins}")
    print(f"[INFO] frozen file : {args.frozen}")
    print(f"[ML band]  seed-to-seed std/cv (model-init only):")
    print(f"           median={100*np.median(rel_std):.3f}%  "
          f"mean={100*rel_std.mean():.3f}%  max={100*rel_std.max():.3f}%")
    print(f"[ensemble-mean - frozen]  rel:")
    print(f"           median={100*np.median(rel_shift):+.3f}%  "
          f"mean={100*rel_shift.mean():+.3f}%  max|.|={100*np.abs(rel_shift).max():.3f}%")
    print(f"[under-dispersion check]  |frozen-ensemble|/seedstd (pull):")
    print(f"           median={np.median(pull):.2f}  p90={np.percentile(pull,90):.2f}  "
          f"max={pull.max():.2f}")
    if np.median(pull) > 2.0:
        print("           --> NOTE: frozen CV is many seed-sigma from the ensemble.")
        print("               This is EXPECTED if the frozen CV and the seed files use")
        print("               different estimators (e.g. the 2D production CV is the")
        print("               deterministic 'exact' GBT while these seeds are 'lgbm'):")
        print("               the pull then measures the cross-estimator shape difference,")
        print("               not ML stochasticity. Only compare same-estimator runs.")
        print("               (See LITERATURE_NOTES.md, ensemble-mean finding.)")

    out = ROOT.TFile.Open(args.out, "RECREATE")
    write_like(frozen_h, args.hist + "_ensemble", emean, out)
    write_like(frozen_h, args.hist + "_ensemble_std", estd, out)
    nparam = ROOT.TParameter("int")("nSeeds", n)
    nparam.Write()
    out.Close()
    print(f"[OK] wrote {args.out}  ({args.hist}_ensemble, {args.hist}_ensemble_std)")


if __name__ == "__main__":
    main()
