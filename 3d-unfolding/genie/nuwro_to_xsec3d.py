#!/usr/bin/env python3
"""Histogram NuWro flat-observable trees (from nuwro_to_flat.C) into
d^3 sigma/(dpT dp|| dEavail) on the analysis binning, for overlay on the
unfolded result.

NuWro normalisation: each event's `weight` is the flux-averaged total CC cross
section PER NUCLEON (constant, in cm^2). The differential is therefore
  dsigma/dx[bin] = (sum of weights in bin) / N_total / dV
where N_total = total CC events generated (across all input files). Truth Eavail
was computed in the converter to match CVUniverse::GetEAvailableTrue().

Run in the analysis env (root_6_28):
  python nuwro_to_xsec3d.py --flat 'work_nuwro/*/nuwro_flat.root' --out nuwro_cv_xsec3d.root
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
from xsec_3d import project_eavail_marginal, project_axis

PT, PZ, EA = (np.asarray(u3d.PT_EDGES, float), np.asarray(u3d.PZ_EDGES, float),
              np.asarray(u3d.EAVAIL_EDGES, float))
in_ps = u3d.u2d.in_truth_phase_space


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", required=True,
                    help="glob for nuwro_flat.root file(s)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    files = sorted(glob.glob(args.flat))
    if not files:
        raise SystemExit(f"no files match {args.flat}")
    pt, pz, ea, w = [], [], [], []
    n_total = 0
    for fn in files:
        f = ROOT.TFile.Open(fn)
        nt = f.Get("nTotal")
        n_total += int(nt.GetVal()) if nt else 0
        t = f.Get("nuwro_obs")
        a = t.AsMatrix(columns=["cc", "pt", "pz", "eavail", "weight"]) \
            if hasattr(t, "AsMatrix") else None
        if a is None:
            df = ROOT.RDataFrame("nuwro_obs", fn)
            d = df.AsNumpy(["cc", "pt", "pz", "eavail", "weight"])
            cc, p_t, p_z, e_a, ww = (d["cc"], d["pt"], d["pz"], d["eavail"], d["weight"])
        else:
            cc, p_t, p_z, e_a, ww = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        f.Close()
        sel = cc.astype(bool)
        pt.append(p_t[sel]); pz.append(p_z[sel]); ea.append(e_a[sel]); w.append(ww[sel])
    pt, pz, ea, w = map(np.concatenate, (pt, pz, ea, w))
    print(f"[nuwro] files={len(files)} N_total(CC gen)={n_total} kept={pt.size}")

    # truth phase space
    m = np.array([in_ps(a, b, PT[0], PT[-1], PZ[0], PZ[-1])
                  for a, b in zip(pt, pz)])
    pt, pz, ea, w = pt[m], pz[m], ea[m], w[m]
    print(f"[nuwro] in phase space={pt.size}")

    wsum, _ = np.histogramdd(np.column_stack([pt, pz, ea]),
                             bins=[PT, PZ, EA], weights=w)
    w2, _ = np.histogramdd(np.column_stack([pt, pz, ea]),
                           bins=[PT, PZ, EA], weights=w * w)
    dV = (np.diff(PT)[:, None, None] * np.diff(PZ)[None, :, None]
          * np.diff(EA)[None, None, :])
    xsec3d = wsum / n_total / dV          # cm^2/nucleon / (GeV/c)^2 / GeV
    xerr = np.sqrt(w2) / n_total / dV
    total = (xsec3d * dV).sum()
    print(f"[nuwro] flux-avg <sigmaCC>/nucleon = {w.mean():.4e} cm^2; "
          f"total sigma (in PS) = {total:.4e} cm^2/nucleon")

    marg = project_eavail_marginal(xsec3d, EA)
    dea = np.diff(EA)[None, None, :]
    marg_err = np.sqrt(((xerr * dea) ** 2).sum(axis=2))
    _, x_pt = project_axis(xsec3d, PT, PZ, EA, "pt")
    _, x_pz = project_axis(xsec3d, PT, PZ, EA, "pz")
    _, x_ea = project_axis(xsec3d, PT, PZ, EA, "eavail")

    fo = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th3d(xsec3d, xerr, "hXSec3D",
                      "NuWro d^{3}#sigma;p_{T} (GeV/c);p_{||} (GeV/c);E_{avail} (GeV)",
                      PT, PZ, EA).Write()
    u3d.numpy_to_th2d(marg, marg_err, "hXSec2D",
                      "NuWro Eavail-marginal;p_{T} (GeV/c);p_{||} (GeV/c)", PT, PZ).Write()
    u3d.numpy_to_th1d(PT, x_pt, "hXSec_pt", "NuWro d#sigma/dp_{T}").Write()
    u3d.numpy_to_th1d(PZ, x_pz, "hXSec_pz", "NuWro d#sigma/dp_{||}").Write()
    u3d.numpy_to_th1d(EA, x_ea, "hXSec_eavail", "NuWro d#sigma/dE_{avail}").Write()
    fo.Close()
    print(f"[nuwro] wrote {args.out}")


if __name__ == "__main__":
    main()
