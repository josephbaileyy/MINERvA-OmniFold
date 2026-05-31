#!/usr/bin/env python3
"""Histogram generator truth events into d^3 sigma/(dpT dp|| dEavail) on the
analysis binning, for overlay on the unfolded OmniFold result.

Pipeline (generator-agnostic via gst_reader.READERS):
  1. read CC events; muon (pT, p||) from the final lepton (neutrino is +z in
     gevgen, so these are already beam-frame -- no tilt rotation);
  2. truth Eavail replicating CVUniverse::GetEAvailableTrue()
     (gamma: +E; pi+-: +E-0.135; pi0: +E; proton: +E-0.93827 GeV);
  3. apply the truth phase space (theta_mu<20, pT<4.5, 1.5<p||<60) and bin onto
     PT/PZ/EAVAIL_EDGES;
  4. normalise to d^3 sigma per nucleon:
        --norm splines (default): <sigma_CC>/nucleon (xsec_graphs (x) flux, /13
                                  for CH) x (N_bin/N_cc_total) / (dpT dp|| dEavail)
        --norm shape  : area-normalised to --shape-total (default 1) -- a
                        normalisation-independent shape cross-check.

Output mirrors the unfold file (hXSec3D, Eavail-marginal hXSec2D,
hXSec_pt/pz/eavail) so overlay tooling is shared.

Run in the analysis env (root_6_28).
"""
import argparse
import os
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # 3d-unfolding/
sys.path.insert(0, HERE)
import unfold_3d_omnifold_unbinned as u3d           # binning + helpers (imports u2d)
from xsec_3d import project_eavail_marginal, project_axis
from gst_reader import READERS

PT_EDGES = np.asarray(u3d.PT_EDGES, float)
PZ_EDGES = np.asarray(u3d.PZ_EDGES, float)
EAVAIL_EDGES = np.asarray(u3d.EAVAIL_EDGES, float)
in_ps = u3d.u2d.in_truth_phase_space                # theta_mu<20 + rectangle

MASS_PI_PM = 0.135      # GeV, matches CVUniverse mass_pion=135 MeV
MASS_P = 0.93827        # GeV, matches CVUniverse mass_proton=938.27 MeV
N_NUCLEONS_CH = 13.0    # C(12) + H(1)


def eavail_true(fs):
    """Replicate CVUniverse::GetEAvailableTrue() on a final-state list (GeV)."""
    r = 0.0
    for pdg, E, _px, _py, _pz in fs:
        a = abs(pdg)
        if pdg == 22:        r += E
        elif a == 211:       r += E - MASS_PI_PM
        elif pdg == 111:     r += E
        elif pdg == 2212:    r += E - MASS_P
    return r


def flux_avg_sigma_cc_per_nucleon(graphs_file, flux_file, flux_hist):
    """<sigma_CC>_nucleon for CH = (sigma_CC[C12] + sigma_CC[H1]) flux-averaged,
    /13. Reads GENIE xsec_graphs.root (tot_cc TGraphs) and the flux TH1.
    Returns (value_cm2, info_str). GENIE graphs are in 1e-38 cm^2."""
    fg = ROOT.TFile.Open(graphs_file)
    if not fg or fg.IsZombie():
        raise RuntimeError(f"cannot open xsec graphs {graphs_file}")

    def find_tot_cc(species):
        # directory names look like 'nu_mu_C12'; graph 'tot_cc'
        for k in fg.GetListOfKeys():
            nm = k.GetName()
            if species in nm and nm.startswith("nu_mu"):
                d = fg.Get(nm)
                g = d.Get("tot_cc") if hasattr(d, "Get") else None
                if g:
                    return g
        return None

    gC = find_tot_cc("C12")
    gH = find_tot_cc("H1")
    if gC is None or gH is None:
        raise RuntimeError("tot_cc graphs for C12/H1 not found in xsec_graphs")

    fx = ROOT.TFile.Open(flux_file)
    h = fx.Get(flux_hist)
    num = den = 0.0
    for b in range(1, h.GetNbinsX() + 1):
        E = h.GetBinCenter(b)
        phi = h.GetBinContent(b)
        if phi <= 0 or E <= 0:
            continue
        sig_ch = gC.Eval(E) + gH.Eval(E)     # 1e-38 cm^2 per CH molecule
        num += sig_ch * phi
        den += phi
    fx.Close(); fg.Close()
    sigma_ch = (num / den) if den > 0 else 0.0          # 1e-38 cm^2 / CH
    sigma_nucleon = sigma_ch / N_NUCLEONS_CH * 1.0e-38  # cm^2 / nucleon
    return sigma_nucleon, f"<sigmaCC>_CH={sigma_ch:.3f}e-38 cm^2, /13 nucleon"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gst", required=True, help="generator gst file")
    ap.add_argument("--generator", default="genie", choices=list(READERS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--norm", choices=["splines", "shape"], default="splines")
    ap.add_argument("--graphs", default=None,
                    help="GENIE xsec_graphs.root (default: from $GENIE_SPLINES dir)")
    ap.add_argument("--flux", default=os.environ.get("GENIE_FLUX"))
    ap.add_argument("--flux-hist", default=os.environ.get("GENIE_FLUX_HIST",
                                                          "flux_E_unweighted"))
    ap.add_argument("--shape-total", type=float, default=1.0)
    args = ap.parse_args()

    reader = READERS[args.generator]
    pt, pz, ea = [], [], []
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
        pt.append(p_t); pz.append(p_z); ea.append(eavail_true(ev["fs"]))
    pt, pz, ea = map(lambda x: np.asarray(x, float), (pt, pz, ea))
    print(f"[genie_to_xsec3d] CC events={n_cc}, in phase space={pt.size}")
    if pt.size == 0:
        raise SystemExit("no events in phase space")

    counts, _ = np.histogramdd(np.column_stack([pt, pz, ea]),
                               bins=[PT_EDGES, PZ_EDGES, EAVAIL_EDGES])
    dpt = np.diff(PT_EDGES)[:, None, None]
    dpz = np.diff(PZ_EDGES)[None, :, None]
    dea = np.diff(EAVAIL_EDGES)[None, None, :]
    widths = dpt * dpz * dea

    if args.norm == "splines":
        graphs = args.graphs or os.path.join(
            os.path.dirname(os.environ["GENIE_SPLINES"]), "xsec_graphs.root")
        sigma_nuc, info = flux_avg_sigma_cc_per_nucleon(
            graphs, args.flux, args.flux_hist)
        xsec3d = sigma_nuc * (counts / n_cc) / widths   # cm^2/nucleon / (GeV/c)^2 / GeV
        print(f"[genie_to_xsec3d] norm=splines: {info}; "
              f"<sigmaCC>/nucleon={sigma_nuc:.4e} cm^2; "
              f"in-PS fraction={pt.size/n_cc:.4f}")
    else:
        # area-normalise so the width-integral equals shape_total
        norm = args.shape_total / counts.sum()
        xsec3d = counts * norm / widths
        print(f"[genie_to_xsec3d] norm=shape: area-normalised to {args.shape_total}")

    marg2d = project_eavail_marginal(xsec3d, EAVAIL_EDGES)
    _, x_pt = project_axis(xsec3d, PT_EDGES, PZ_EDGES, EAVAIL_EDGES, "pt")
    _, x_pz = project_axis(xsec3d, PT_EDGES, PZ_EDGES, EAVAIL_EDGES, "pz")
    _, x_ea = project_axis(xsec3d, PT_EDGES, PZ_EDGES, EAVAIL_EDGES, "eavail")
    total = (xsec3d * widths).sum()
    print(f"[genie_to_xsec3d] total sigma (in PS) = {total:.4e} cm^2/nucleon")

    fout = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th3d(xsec3d, None, "hXSec3D",
                      "GENIE d^{3}#sigma/(dp_{T}dp_{||}dE_{avail});"
                      "p_{T} (GeV/c);p_{||} (GeV/c);E_{avail} (GeV)",
                      PT_EDGES, PZ_EDGES, EAVAIL_EDGES).Write()
    u3d.numpy_to_th2d(marg2d, None, "hXSec2D",
                      "GENIE Eavail-marginal;p_{T} (GeV/c);p_{||} (GeV/c)",
                      PT_EDGES, PZ_EDGES).Write()
    u3d.numpy_to_th1d(PT_EDGES, x_pt, "hXSec_pt", "GENIE d#sigma/dp_{T}").Write()
    u3d.numpy_to_th1d(PZ_EDGES, x_pz, "hXSec_pz", "GENIE d#sigma/dp_{||}").Write()
    u3d.numpy_to_th1d(EAVAIL_EDGES, x_ea, "hXSec_eavail",
                      "GENIE d#sigma/dE_{avail}").Write()
    ROOT.TParameter("double")("nCCtotal", float(n_cc)).Write()
    fout.Close()
    print(f"[genie_to_xsec3d] wrote {args.out}")


if __name__ == "__main__":
    main()
