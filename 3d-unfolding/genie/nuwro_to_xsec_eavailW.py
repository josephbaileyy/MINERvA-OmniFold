#!/usr/bin/env python3
"""Histogram NuWro flat-observable trees (nuwro_to_flat.C, now with a W branch)
into d^2 sigma/(dEavail dW) on the analysis binning, for the (E_avail, W) band.

Mirrors nuwro_to_xsec3d.py normalisation (per-event `weight` = flux-averaged total
CC sigma per nucleon; dsigma/dx = sum_w_in_bin / N_total / dV) but bins on
(EAVAIL_EDGES, W_EDGES) -- identical to gen_to_xsec_eavailW.py (GENIE) so the
generator overlay is shared.

  python nuwro_to_xsec_eavailW.py --flat 'work_nuwro_*/nuwro_flat.root' \
      --out nuwro_cv_xsec_eavailW.root
"""
import argparse
import glob
import os
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import unfold_3d_omnifold_unbinned as u3d

EAVAIL_EDGES = np.asarray([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0], float)
W_EDGES = np.asarray([0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0], float)
PT = np.asarray(u3d.PT_EDGES, float)
PZ = np.asarray(u3d.PZ_EDGES, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", required=True, help="glob for nuwro_flat.root file(s)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    files = sorted(glob.glob(args.flat))
    if not files:
        raise SystemExit(f"no files match {args.flat}")
    ea, w, wt = [], [], []
    n_total = 0
    for fn in files:
        f = ROOT.TFile.Open(fn)
        nt = f.Get("nTotal")
        n_total += int(nt.GetVal()) if nt else 0
        f.Close()
        d = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(
            ["cc", "pt", "pz", "eavail", "W", "weight"])
        sel = d["cc"].astype(bool)
        ea.append(d["eavail"][sel]); w.append(d["W"][sel]); wt.append(d["weight"][sel])
        # phase-space gate uses pt/pz too
        ea[-1] = ea[-1];
        ptv = d["pt"][sel]; pzv = d["pz"][sel]
        m = (np.isfinite(ptv) & np.isfinite(pzv) & np.isfinite(w[-1])
             & (ptv >= PT[0]) & (ptv <= PT[-1]) & (pzv >= PZ[0]) & (pzv <= PZ[-1])
             & (np.arctan2(ptv, pzv) < u3d.u2d.MAX_MUON_THETA_RAD)
             & (w[-1] >= 0) & (w[-1] < 1e4))
        ea[-1] = ea[-1][m]; w[-1] = w[-1][m]; wt[-1] = wt[-1][m]
    ea = np.concatenate(ea); w = np.concatenate(w); wt = np.concatenate(wt)
    print(f"[nuwro_eavailW] files={len(files)} N_total(CC gen)={n_total} in-PS={ea.size}")
    if ea.size == 0:
        raise SystemExit("no events in phase space")

    wsum, _ = np.histogramdd(np.column_stack([ea, w]), bins=[EAVAIL_EDGES, W_EDGES], weights=wt)
    w2, _ = np.histogramdd(np.column_stack([ea, w]), bins=[EAVAIL_EDGES, W_EDGES], weights=wt * wt)
    dea = np.diff(EAVAIL_EDGES)[:, None]
    dw = np.diff(W_EDGES)[None, :]
    widths = dea * dw
    xsec = wsum / n_total / widths             # cm^2/nucleon / GeV^2
    xerr = np.sqrt(w2) / n_total / widths
    x_ea = (xsec * dw).sum(axis=1)
    x_w = (xsec * dea).sum(axis=0)
    total = (xsec * widths).sum()
    print(f"[nuwro_eavailW] flux-avg <sigmaCC>/nucleon={wt.mean():.4e} cm^2; "
          f"total sigma(in PS)={total:.4e}")

    fo = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th2d(xsec, xerr, "hXSec_eavailW",
                      "NuWro d^{2}#sigma/(dE_{avail}dW);E_{avail} (GeV);W (GeV)",
                      EAVAIL_EDGES, W_EDGES).Write()
    u3d.numpy_to_th1d(EAVAIL_EDGES, x_ea, "hXSec_eavail", "NuWro d#sigma/dE_{avail}").Write()
    u3d.numpy_to_th1d(W_EDGES, x_w, "hXSec_W", "NuWro d#sigma/dW").Write()
    ROOT.TParameter("double")("nCCtotal", float(n_total)).Write()
    fo.Close()
    print(f"[nuwro_eavailW] wrote {args.out}")


if __name__ == "__main__":
    main()
