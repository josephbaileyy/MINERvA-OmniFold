#!/usr/bin/env python3
"""Reported-cell identity on the adopted 2D products, and _ours_only_chi2 old vs new.

--prod is a local copy of these 2d-unfolding paths, read-only from Perlmutter
(digests checked against ki84-adopt-20261006/sha256sums_2d-unfolding_uq.txt
and recompute_2d_budget.json before use):
  uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root           (VL170 band)
  uq/bootstrap_MEFHC_300/uq_covariance_boot300.root                 (VL162 band)
  uq/seedscan_lgbm_ml/uq_covariance_ml.root                         (ML block)
  uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root                      (matched CV)
  uq/universe_stage2_MEFHC_full_matcorr_fluxfix{,_vl170}/uq_universe_covariance_full_matcorr_fluxfix.root
  2d_crossSection_omnifold_MEFHC_5iter.root                         (frozen central)
  minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root            (paper)

Part 1 prints every operand's reported-cell set under the rule its producer or
consumer uses, and whether each equals the paper's. Part 2 runs the pinned and
the edited _ours_only_chi2.py on the adopted VL172 universe file and the VL170
bootstrap, which is step (4) of uq/rollup_vl170_adoption.sh.
"""
import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO / "2d-unfolding" / "uq"))
import reported_cells as rc  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prod", required=True, type=Path)
    ap.add_argument("--old-uq", required=True, type=Path)
    a = ap.parse_args()
    import ROOT
    ROOT.gROOT.SetBatch(True)
    P = a.prod

    def grid(path, name, rule):
        f = ROOT.TFile.Open(str(P / path))
        arr = rc.grid_hist_to_array(f.Get(name))
        f.Close()
        return rc.reported_indices(rule(arr))

    sets = {}
    f = ROOT.TFile.Open(str(P / "minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root"))
    m = f.Get("StatOnlyCovariance")
    sets["paper StatOnly diag > 0 (ROOT)"] = np.flatnonzero(
        np.array([m(i, i) for i in range(m.GetNrows())]) > 0)
    f.Close()
    diag = np.zeros(rc.N_CELLS)
    with open(REPO / "2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV_stat.txt") as fh:
        r = csv.reader(fh)
        next(r)
        for i, j, v in r:
            if i == j:
                diag[int(i)] = float(v)
    sets["paper StatOnly diag > 0 (tracked txt)"] = np.flatnonzero(diag > 0)
    for tag, path in (("VL170", "uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"),
                      ("VL162", "uq/bootstrap_MEFHC_300/uq_covariance_boot300.root"),
                      ("ML seedscan", "uq/seedscan_lgbm_ml/uq_covariance_ml.root")):
        sets[f"{tag} hMean2D > 0 (analyze_uq rule)"] = grid(path, "hMean2D", lambda x: x > 0)
    sets["matched CV hXSec2D > 0 (analyze_universes rule)"] = grid(
        "uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root", "hXSec2D", lambda x: x > 0)
    sets["frozen central hXSec2D > 0 (Fig. 6/7 rule)"] = grid(
        "2d_crossSection_omnifold_MEFHC_5iter.root", "hXSec2D", lambda x: x > 0)
    for tag, d in (("VL172", "_vl170"), ("VL162", "")):
        sets[f"{tag} universe hSigma_universe_total > 0 (proxy)"] = grid(
            f"uq/universe_stage2_MEFHC_full_matcorr_fluxfix{d}/uq_universe_covariance_full_matcorr_fluxfix.root",
            "hSigma_universe_total", lambda x: x > 0)

    ref = sets["paper StatOnly diag > 0 (ROOT)"]
    print("part 1: reported-cell sets (n, equal to paper StatOnly cell by cell)")
    for k, v in sets.items():
        print(f"  {k:55s} n={v.size:3d}  equal={np.array_equal(v, ref)}")
    for k in ("VL170 hMean2D > 0 (analyze_uq rule)", "VL162 hMean2D > 0 (analyze_uq rule)"):
        rc.require_same_cells(sets["matched CV hXSec2D > 0 (analyze_universes rule)"], sets[k],
                              "matched CV", k)
    print("  analyze_universes guard on the adopted inputs (CV vs VL170/VL162 bootstrap): accepts")

    print("part 2: _ours_only_chi2.py on the VL172 universe file and the VL170 bootstrap")
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import _ours_only_chi2 as oo; "
            "oo.ANC = sys.argv[2]; sys.argv = ['_ours_only_chi2.py'] + sys.argv[3:]; oo.main()")
    args = [str(P / "minerva_paper_anc"), "--ours", str(P / "2d_crossSection_omnifold_MEFHC_5iter.root"),
            "--universe-cov",
            str(P / "uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root"),
            "--bootstrap-cov", str(P / "uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root")]
    env = dict(os.environ, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", VECLIB_MAXIMUM_THREADS="2")
    outs = {}
    for tag, uq in (("old", a.old_uq), ("new", REPO / "2d-unfolding" / "uq")):
        p = subprocess.run([sys.executable, "-c", code, str(uq)] + args, env=env,
                           capture_output=True, text=True)
        outs[tag] = p
        print(f"  [{tag}] rc={p.returncode}")
    old = outs["old"].stdout.replace(str(P), "<PROD>").splitlines()
    new = outs["new"].stdout.replace(str(P), "<PROD>").splitlines()
    print("  lines only in new:", [l for l in new if l not in old])
    print("  lines only in old:", [l for l in old if l not in new])
    print("  new stdout:")
    for l in new:
        print("    " + l)


if __name__ == "__main__":
    main()
