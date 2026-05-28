#!/usr/bin/env python3
"""Verify uq/analyze_universes.py byte-for-byte against MAT's reference
implementation in MnvH1D::GetTotalErrorMatrix.

Loads the same per-universe 2D cross sections that analyze_universes.py
consumes, flattens to the 205-bin reported set, populates a PlotUtils
MnvH1D + MnvVertErrorBand per propagated band, then calls
MnvH1D::GetTotalErrorMatrix(includeStat=False, asFrac=False,
cov_area_normalize=False) and diffs element-wise against the Python
matcorr rollup (with --add-norm 0 so the comparison is band-by-band
identical).

Expected: max relative difference at numerical noise (1e-12 or smaller).
"""
import argparse
import glob
import os
import re
import sys
from collections import defaultdict

import numpy as np
import ROOT

UNI_RE = re.compile(r"2d_xsec_.*_uni_(?P<band>.+?)_(?P<idx>\d+)\.root$")


def th2_to_array(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.zeros((nx, ny))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            a[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
    return a


def load_xsec2d_flat(path, reported_flat):
    rf = ROOT.TFile.Open(path)
    if not rf or rf.IsZombie():
        sys.exit(f"[FAIL] cannot open {path}")
    h = rf.Get("hXSec2D")
    if not h:
        rf.Close()
        sys.exit(f"[FAIL] hXSec2D missing in {path}")
    a = th2_to_array(h).ravel(order="C")[reported_flat]
    rf.Close()
    return a


def parse_universe_path(path):
    m = UNI_RE.match(os.path.basename(path))
    if not m:
        return None
    return m.group("band"), int(m.group("idx"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cv", required=True, help="CV unfold ROOT.")
    ap.add_argument("--glob", required=True,
                    help="Glob for per-universe unfold ROOTs.")
    ap.add_argument("--python-cov",
                    default="uq/universe_stage2_MEFHC_full_matcorr/"
                            "uq_universe_covariance_full_matcorr.root",
                    help="ROOT file from analyze_universes.py with "
                         "hCov_universe_total (matcorr rollup; "
                         "MUST be the --add-norm 0 version for parity).")
    ap.add_argument("--python-cov-hist", default="hCov_universe_total",
                    help="Histogram name inside --python-cov.")
    ap.add_argument("--out", default="uq/matcorr_vs_mnvh1d.txt",
                    help="Text report destination.")
    args = ap.parse_args()

    rf = ROOT.TFile.Open(args.cv)
    h_cv2d = rf.Get("hXSec2D")
    cv2d = th2_to_array(h_cv2d)
    rf.Close()
    reported_2d = cv2d > 0
    reported_flat = reported_2d.ravel(order="C")
    n_rep = int(reported_flat.sum())
    cv_flat = cv2d.ravel(order="C")[reported_flat]
    print(f"[info] CV reported bins: {n_rep}")

    paths = sorted(glob.glob(args.glob))
    by_band = defaultdict(list)
    for p in paths:
        parsed = parse_universe_path(p)
        if not parsed:
            continue
        band, idx = parsed
        by_band[band].append((idx, p))
    print(f"[info] {len(paths)} universe ROOTs across {len(by_band)} bands")

    h_mnv = ROOT.PlotUtils.MnvH1D("hxs", "xs reported flat",
                                  n_rep, 0.0, float(n_rep))
    for i, v in enumerate(cv_flat):
        h_mnv.SetBinContent(i + 1, float(v))
        h_mnv.SetBinError(i + 1, 0.0)

    print(f"[info] populating {len(by_band)} MnvVertErrorBands...")
    skipped = []
    for band, entries in sorted(by_band.items()):
        entries = sorted(entries, key=lambda t: t[0])
        if len(entries) < 2:
            skipped.append((band, len(entries)))
            continue
        N_u = len(entries)
        h_mnv.AddVertErrorBand(band, N_u)
        veb = h_mnv.GetVertErrorBand(band)
        for u_idx, (_, p) in enumerate(entries):
            x_flat = load_xsec2d_flat(p, reported_flat)
            h_u = veb.GetHist(u_idx)
            for i, v in enumerate(x_flat):
                h_u.SetBinContent(i + 1, float(v))
                h_u.SetBinError(i + 1, 0.0)
    if skipped:
        print(f"[warn] skipped (N<2): {skipped}")

    print("[info] MnvH1D::GetTotalErrorMatrix(False, False, False) ...")
    tm = h_mnv.GetTotalErrorMatrix(False, False, False)
    n_raw = tm.GetNrows()
    # MAT TMatrixD includes under/overflow rows: dimension is nbins+2.
    assert n_raw == n_rep + 2, f"MnvH1D returned {n_raw}; expected {n_rep+2}"
    mat_full = np.empty((n_raw, n_raw))
    for i in range(n_raw):
        for j in range(n_raw):
            mat_full[i, j] = tm(i, j)
    mat_cov = mat_full[1:n_rep + 1, 1:n_rep + 1]

    print(f"[info] Python matcorr cov: {args.python_cov}:{args.python_cov_hist}")
    pf = ROOT.TFile.Open(args.python_cov)
    h_py = pf.Get(args.python_cov_hist)
    if not h_py:
        sys.exit(f"[FAIL] hist {args.python_cov_hist} missing in {args.python_cov}")
    if h_py.GetNbinsX() != n_rep:
        sys.exit(f"[FAIL] python cov is {h_py.GetNbinsX()}x{h_py.GetNbinsY()}; "
                 f"expected {n_rep}x{n_rep}")
    py_cov = np.empty((n_rep, n_rep))
    for i in range(n_rep):
        for j in range(n_rep):
            py_cov[i, j] = h_py.GetBinContent(i + 1, j + 1)
    pf.Close()

    diff = mat_cov - py_cov
    abs_diff = np.abs(diff)
    scale = max(abs(mat_cov).max(), abs(py_cov).max())
    rel = abs_diff / scale if scale > 0 else abs_diff
    max_abs = abs_diff.max()
    max_rel = rel.max()
    fro_mat = np.linalg.norm(mat_cov)
    fro_py = np.linalg.norm(py_cov)
    fro_diff = np.linalg.norm(diff)

    i_worst, j_worst = np.unravel_index(np.argmax(abs_diff), abs_diff.shape)

    report = [
        "MnvH1D::GetTotalErrorMatrix vs Python matcorr rollup",
        "=" * 60,
        f"n_reported               : {n_rep}",
        f"bands populated          : {h_mnv.GetNVertErrorBands()}",
        f"sqrt(trace) MAT          : {np.sqrt(max(np.trace(mat_cov),0)):.6e}",
        f"sqrt(trace) Python       : {np.sqrt(max(np.trace(py_cov),0)):.6e}",
        f"Frobenius norm (MAT)     : {fro_mat:.6e}",
        f"Frobenius norm (Python)  : {fro_py:.6e}",
        f"Frobenius norm (diff)    : {fro_diff:.6e}",
        f"max |diff|               : {max_abs:.6e}",
        f"max |diff| / max(|cov|)  : {max_rel:.3e}",
        f"worst element            : ({i_worst},{j_worst})  "
        f"MAT={mat_cov[i_worst,j_worst]:.6e}  Py={py_cov[i_worst,j_worst]:.6e}",
        "",
        "Verdict: " +
        ("PASS (consistent with numerical noise)" if max_rel < 1e-10
         else "FAIL (structured discrepancy — investigate)"),
    ]
    text = "\n".join(report)
    print("\n" + text)
    with open(args.out, "w") as fh:
        fh.write(text + "\n")
    print(f"\n[wrote] {args.out}")


if __name__ == "__main__":
    main()
