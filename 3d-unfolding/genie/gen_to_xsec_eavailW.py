#!/usr/bin/env python3
"""Histogram generator truth events into d^2 sigma/(dEavail dW) on the analysis
binning, for the (E_avail, W) generator band vs the unfolded OmniFold result
(open question 6: the high-E_avail DIS-tail excess localised in W).

Same machinery as genie_to_xsec3d.py (generator-agnostic gst_reader, flux-averaged
sigma_CC/nucleon normalisation, truth phase space theta_mu<20 + pt/pz rectangle), but
bins on (EAVAIL_EDGES, W_EDGES) -- identical to the 5D OmniFold W axis
(unfold_nd_omnifold_unbinned.py "W"/"eavail").  W replicates
CVUniverse::GetTrueExperimentersW():

    Q2 = 4 Enu Emu sin^2(theta_mu/2)
    W  = sqrt(M_nucl^2 + 2 (Enu-Emu) M_nucl - Q2)        [GeV]

with M_nucl = M_n (CH is neutron-dominant for CC; M_n vs M_p differ 1.3 MeV, far
below the W bin widths).  theta_mu is the lepton angle wrt the beam (+z in gevgen).

Output mirrors products/5d/excess_eavail_W.root naming so the overlay is shared:
hXSec_eavailW (TH2, eavail x W), hXSec_eavail, hXSec_W, nCCtotal.

Run in the analysis env (root_6_28).  Example:
  python gen_to_xsec_eavailW.py --gst nuwro_cv.gst.root --generator nuwro \
      --out nuwro_cv_xsec_eavailW.root --graphs xsec_graphs.root \
      --flux flux_mefhc_numu.root --flux-hist flux_E_unweighted
"""
import argparse
import os
import sys

import numpy as np
import ROOT

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "3d-unfolding"))
import unfold_3d_omnifold_unbinned as u3d           # binning + helpers (imports u2d)
from gst_reader import READERS
from genie_to_xsec3d import eavail_true, flux_avg_sigma_cc_per_nucleon

# Analysis edges -- MUST match unfold_nd_omnifold_unbinned.py ("eavail", "W").
EAVAIL_EDGES = np.asarray([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0], float)
W_EDGES = np.asarray([0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0], float)
PT_EDGES = np.asarray(u3d.PT_EDGES, float)
PZ_EDGES = np.asarray(u3d.PZ_EDGES, float)
in_ps = u3d.u2d.in_truth_phase_space                # theta_mu<20 + rectangle

M_NUCLEON = 0.939565    # GeV, neutron (CC on CH is neutron-dominant)


def w_true(nu, lep, m_nucl=M_NUCLEON):
    """Replicate CVUniverse::GetTrueExperimentersW() (GeV). nu/lep are
    (E,px,py,pz) in GeV; neutrino along +z so theta_mu = angle wrt +z."""
    Enu = nu[0]
    Emu, pxl, pyl, pzl = lep
    pmu = float(np.sqrt(pxl * pxl + pyl * pyl + pzl * pzl))
    if pmu <= 0.0:
        return 0.0
    costh = max(-1.0, min(1.0, pzl / pmu))
    theta = float(np.arccos(costh))
    q2 = 4.0 * Enu * Emu * np.sin(theta / 2.0) ** 2
    w2 = m_nucl * m_nucl + 2.0 * (Enu - Emu) * m_nucl - q2
    return float(np.sqrt(w2)) if w2 > 0.0 else 0.0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gst", required=True, help="generator gst/truth-event file")
    ap.add_argument("--generator", default="genie", choices=list(READERS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--norm", choices=["splines", "shape"], default="splines")
    ap.add_argument("--graphs", default=None,
                    help="GENIE xsec_graphs.root (default: $GENIE_SPLINES dir)")
    ap.add_argument("--flux", default=os.environ.get("GENIE_FLUX"))
    ap.add_argument("--flux-hist", default=os.environ.get("GENIE_FLUX_HIST",
                                                          "flux_E_unweighted"))
    ap.add_argument("--shape-total", type=float, default=1.0)
    args = ap.parse_args()

    reader = READERS[args.generator]
    ea, w = [], []
    n_cc = 0
    for ev in reader(args.gst):
        if not ev["cc"]:
            continue
        n_cc += 1
        _, pxl, pyl, pzl = ev["lep"]
        p_t = float(np.hypot(pxl, pyl))
        p_z = float(pzl)
        if not in_ps(p_t, p_z, PT_EDGES[0], PT_EDGES[-1], PZ_EDGES[0], PZ_EDGES[-1]):
            continue
        ea.append(eavail_true(ev["fs"]))
        w.append(w_true(ev["nu"], ev["lep"]))
    ea = np.asarray(ea, float)
    w = np.asarray(w, float)
    print(f"[gen_eavailW] CC events={n_cc}, in phase space={ea.size}")
    if ea.size == 0:
        raise SystemExit("no events in phase space")

    counts, _ = np.histogramdd(np.column_stack([ea, w]),
                               bins=[EAVAIL_EDGES, W_EDGES])
    dea = np.diff(EAVAIL_EDGES)[:, None]
    dw = np.diff(W_EDGES)[None, :]
    widths = dea * dw

    if args.norm == "splines":
        graphs = args.graphs or os.path.join(
            os.path.dirname(os.environ["GENIE_SPLINES"]), "xsec_graphs.root")
        sigma_nuc, info = flux_avg_sigma_cc_per_nucleon(
            graphs, args.flux, args.flux_hist)
        xsec = sigma_nuc * (counts / n_cc) / widths     # cm^2/nucleon / GeV^2
        print(f"[gen_eavailW] norm=splines: {info}; "
              f"<sigmaCC>/nucleon={sigma_nuc:.4e} cm^2; "
              f"in-PS fraction={ea.size/n_cc:.4f}")
    else:
        norm = args.shape_total / counts.sum()
        xsec = counts * norm / widths
        print(f"[gen_eavailW] norm=shape: area-normalised to {args.shape_total}")

    x_ea = (xsec * dw).sum(axis=1)      # d sigma/dEavail (integrate W)
    x_w = (xsec * dea).sum(axis=0)      # d sigma/dW     (integrate Eavail)
    total = (xsec * widths).sum()
    print(f"[gen_eavailW] total sigma (in PS) = {total:.4e} cm^2/nucleon")

    fout = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th2d(xsec, None, "hXSec_eavailW",
                      f"{args.generator} d^{{2}}#sigma/(dE_{{avail}}dW);"
                      "E_{avail} (GeV);W (GeV)",
                      EAVAIL_EDGES, W_EDGES).Write()
    u3d.numpy_to_th1d(EAVAIL_EDGES, x_ea, "hXSec_eavail",
                      f"{args.generator} d#sigma/dE_{{avail}}").Write()
    u3d.numpy_to_th1d(W_EDGES, x_w, "hXSec_W",
                      f"{args.generator} d#sigma/dW").Write()
    ROOT.TParameter("double")("nCCtotal", float(n_cc)).Write()
    fout.Close()
    print(f"[gen_eavailW] wrote {args.out}")


if __name__ == "__main__":
    main()
