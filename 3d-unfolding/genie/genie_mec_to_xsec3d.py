#!/usr/bin/env python3
"""Histogram a GENIE 'Default+CCMEC' sample (Valencia 2p2h enabled) into
d^3 sigma/(dpT dp|| dEavail), for the GENIE-CV+MEC vs data overlay.

WHY A SEPARATE CONVERTER (normalisation): the base-CV converter
(genie_to_xsec3d.py --norm splines) divides by the flux-averaged tot_cc graph,
but in this spline set the Nieves-Simo-Vacas MEC channel is ABSENT from the
gspl2root tot_cc graph (mec_cc graph == 0), even though the MEC *spline* is
present and gevgen does generate MEC events. So tot_cc is the QE+RES+DIS+COH
("non-MEC") total only. The correct absolute normalisation for a MEC-inclusive,
flux-driven, unweighted sample anchors the non-MEC part to that known total:

  each unweighted event represents sigma_per_evt = sigma_tot^{MEC-incl}/N_cc.
  The non-MEC events (N_nonmec of them) must reproduce the known non-MEC total
  sigma_nonMEC/nucleon = tot_cc/13, so
     sigma_per_evt = (tot_cc/13) / N_nonmec ,
  and  dsigma/dx[bin] = (tot_cc/13) * counts_allmodes[bin] / N_nonmec / dV .

i.e. identical to the splines norm but dividing by the NON-MEC CC count instead
of all CC, which lifts the total by 1/(1-f_mec) and lets the MEC events add on
top in their (correctly sampled) dip shape. f_mec is reported as a cross-check.

Output mirrors the other converters (hXSec3D, hXSec2D, hXSec_pt/pz/eavail) plus
hXSec_eavail_nomec / hXSec_eavail_mec for the stacked breakdown.

Run in the analysis env (root_6_28).
"""
import argparse
import glob
import os
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import unfold_3d_omnifold_unbinned as u3d
from xsec_3d import project_eavail_marginal, project_axis
from genie_to_xsec3d import eavail_true, flux_avg_sigma_cc_per_nucleon

PT = np.asarray(u3d.PT_EDGES, float)
PZ = np.asarray(u3d.PZ_EDGES, float)
EA = np.asarray(u3d.EAVAIL_EDGES, float)
in_ps = u3d.u2d.in_truth_phase_space


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gst", required=True, help="glob for Default+CCMEC gst file(s)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--graphs", default=os.path.join(HERE, "xsec_graphs.root"))
    ap.add_argument("--flux", default=os.environ.get(
        "GENIE_FLUX", os.path.join(HERE, "flux_mefhc_numu.root")))
    ap.add_argument("--flux-hist", default=os.environ.get("GENIE_FLUX_HIST", "flux_numu"))
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    files = sorted(glob.glob(args.gst))
    if not files:
        raise SystemExit(f"no gst files match {args.gst}")

    # tot_cc (non-MEC) flux-avg per nucleon -- same anchor as the base CV
    sigma_nonmec, info = flux_avg_sigma_cc_per_nucleon(
        args.graphs, args.flux, args.flux_hist)

    pt_l, pz_l, ea_l, mec_l = [], [], [], []
    n_cc = n_nonmec = 0
    for fn in files:
        d = ROOT.RDataFrame("gst", fn).AsNumpy(
            ["cc", "mec", "pxl", "pyl", "pzl", "nf", "pdgf", "Ef"])
        cc = d["cc"].astype(bool)
        mec = d["mec"].astype(bool)
        n_cc += int(cc.sum())
        n_nonmec += int((cc & ~mec).sum())
        pt = np.hypot(d["pxl"], d["pyl"])
        pz = d["pzl"]
        inps = np.fromiter(
            (in_ps(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
             for a, b in zip(pt, pz)), dtype=bool, count=pt.size)
        sel = np.where(cc & inps)[0]
        for i in sel:
            nf = int(d["nf"][i])
            fs = [(int(d["pdgf"][i][j]), float(d["Ef"][i][j]), 0., 0., 0.)
                  for j in range(nf)]
            ea_l.append(eavail_true(fs))
            pt_l.append(float(pt[i])); pz_l.append(float(pz[i]))
            mec_l.append(bool(mec[i]))

    pt = np.asarray(pt_l); pz = np.asarray(pz_l); ea = np.asarray(ea_l)
    is_mec = np.asarray(mec_l)
    f_mec = (n_cc - n_nonmec) / n_cc
    print(f"[mec] files={len(files)} CC={n_cc} non-MEC={n_nonmec} "
          f"f_mec={100*f_mec:.2f}% ; {info}")
    print(f"[mec] in-PS={pt.size} (MEC in-PS={is_mec.sum()}); "
          f"sigma_nonMEC/nuc={sigma_nonmec:.4e} -> "
          f"sigma_MECincl/nuc={sigma_nonmec/(1-f_mec):.4e}")

    dV = (np.diff(PT)[:, None, None] * np.diff(PZ)[None, :, None]
          * np.diff(EA)[None, None, :])
    norm = sigma_nonmec / n_nonmec            # = sigma_per_evt (MEC-incl anchor)

    def hist3(mask):
        c, _ = np.histogramdd(np.column_stack([pt[mask], pz[mask], ea[mask]]),
                              bins=[PT, PZ, EA])
        return c * norm / dV
    xsec3d = hist3(np.ones(pt.size, bool))     # all modes (QE+RES+DIS+COH+MEC)
    xsec_nomec = hist3(~is_mec)
    xsec_mec = hist3(is_mec)
    total = (xsec3d * dV).sum()
    print(f"[mec] total sigma (in PS, MEC-incl) = {total:.4e} cm^2/nucleon")

    marg = project_eavail_marginal(xsec3d, EA)
    _, x_pt = project_axis(xsec3d, PT, PZ, EA, "pt")
    _, x_pz = project_axis(xsec3d, PT, PZ, EA, "pz")
    _, x_ea = project_axis(xsec3d, PT, PZ, EA, "eavail")
    _, x_ea_nomec = project_axis(xsec_nomec, PT, PZ, EA, "eavail")
    _, x_ea_mec = project_axis(xsec_mec, PT, PZ, EA, "eavail")

    fo = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th3d(xsec3d, None, "hXSec3D",
                      "GENIE+MEC d^{3}#sigma;p_{T} (GeV/c);p_{||} (GeV/c);E_{avail} (GeV)",
                      PT, PZ, EA).Write()
    u3d.numpy_to_th2d(marg, None, "hXSec2D",
                      "GENIE+MEC Eavail-marginal;p_{T} (GeV/c);p_{||} (GeV/c)", PT, PZ).Write()
    u3d.numpy_to_th1d(PT, x_pt, "hXSec_pt", "GENIE+MEC d#sigma/dp_{T}").Write()
    u3d.numpy_to_th1d(PZ, x_pz, "hXSec_pz", "GENIE+MEC d#sigma/dp_{||}").Write()
    u3d.numpy_to_th1d(EA, x_ea, "hXSec_eavail", "GENIE+MEC d#sigma/dE_{avail}").Write()
    u3d.numpy_to_th1d(EA, x_ea_nomec, "hXSec_eavail_nomec", "non-MEC part").Write()
    u3d.numpy_to_th1d(EA, x_ea_mec, "hXSec_eavail_mec", "MEC part").Write()
    ROOT.TParameter("double")("nCCtotal", float(n_cc)).Write()
    ROOT.TParameter("double")("fMEC", float(f_mec)).Write()
    fo.Close()
    print(f"[mec] wrote {args.out}")


if __name__ == "__main__":
    main()
