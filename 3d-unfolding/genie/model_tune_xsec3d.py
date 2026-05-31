#!/usr/bin/env python3
"""Extract the MINERvA Tune v1 3D prediction d^3sigma/(dpT dp|| dEavail) from the
event-loop MC truth.

Stage B, done the robust way: the analysis MC's mc_truth_denom carries w_truth =
the full MINERvA Tune v1 weight (flux CV x RPA x low-recoil 2p2h x non-resonant-pi
suppression -- mean ~0.83, not 1). Binning the truth weighted by w_truth and
normalising with the SAME flux/POT/nucleon machinery as the unfold gives the
tuned-GENIE differential cross section directly -- the exact tune used in the
analysis, with no fragile from-scratch reweight reimplementation. A model
prediction needs no efficiency/completeness correction (mc_truth_denom IS the
full truth), so completeness = 1.

Validation: the Eavail-marginal (hXSec2D) should reproduce the shipped ancillary
model_ptpl..._Tune_v1.txt (compare_to_models.py loads it).

Run in the analysis env (root_6_28):
  python model_tune_xsec3d.py --omnifile ../runEventLoopOmniFold_MEFHC_3D.root \
      --mcfile ../../2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root \
      --out model_tunev1_xsec3d.root
"""
import argparse
import os
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))      # 3d-unfolding/
import unfold_3d_omnifold_unbinned as u3d
from xsec_3d import extract_cross_section_3d, project_eavail_marginal, project_axis

PT, PZ, EA = (np.asarray(u3d.PT_EDGES, float), np.asarray(u3d.PZ_EDGES, float),
              np.asarray(u3d.EAVAIL_EDGES, float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default=os.path.join(os.path.dirname(HERE),
                    "runEventLoopOmniFold_MEFHC_3D.root"))
    ap.add_argument("--mcfile", default=os.path.join(os.path.dirname(HERE),
                    "..", "2d-unfolding", "baseline_flux", "runEventLoopMC_MEFHC.root"))
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--out", default=os.path.join(HERE, "model_tunev1_xsec3d.root"))
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    f = ROOT.TFile.Open(args.omnifile)
    t = f.Get("mc_truth_denom")
    data_pot, mc_pot, pot_scale = u3d.u2d.get_pot_scales(f)
    n_nuc = u3d.u2d.TRACKER_FIDUCIAL_N_NUCLEONS
    flux_bins, _ = u3d.u2d.load_flux_bins(args.mcfile, args.flux_hist, list(PT))
    flux = np.asarray(flux_bins, float)
    print(f"[model] POT data={data_pot:.4g} mc={mc_pot:.4g} scale={pot_scale:.6g}; "
          f"flux sum={flux.sum():.4g}")

    # truth (pT,p||,Eavail) weighted by the tune weight w_truth (POT-scaled)
    td = u3d.collect_truth_denom_3d(t, PT[0], PT[-1], PZ[0], PZ[-1], pot_scale,
                                    use_weights=True, verbose=True)
    counts, err = u3d.hist3d(td["truth_pt"], td["truth_pz"], td["truth_ea"],
                             td["w_truth"], PT, PZ, EA)
    f.Close()

    # model prediction: no efficiency/completeness correction (c=1)
    c1 = np.ones_like(counts)
    xsec3d, _ = extract_cross_section_3d(counts, c1, flux, data_pot, n_nuc, PT, PZ, EA)
    rel = np.zeros_like(counts); np.divide(err, counts, out=rel, where=counts > 0)
    xerr = np.abs(xsec3d) * rel

    marg = project_eavail_marginal(xsec3d, EA)
    dea = np.diff(EA)[None, None, :]
    marg_err = np.sqrt(((xerr * dea) ** 2).sum(axis=2))
    _, x_pt = project_axis(xsec3d, PT, PZ, EA, "pt")
    _, x_pz = project_axis(xsec3d, PT, PZ, EA, "pz")
    _, x_ea = project_axis(xsec3d, PT, PZ, EA, "eavail")
    total = (xsec3d * np.diff(PT)[:, None, None] * np.diff(PZ)[None, :, None]
             * np.diff(EA)[None, None, :]).sum()
    print(f"[model] MINERvA Tune v1 total sigma (in PS) = {total:.4e} cm^2/nucleon")

    fo = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th3d(xsec3d, xerr, "hXSec3D",
                      "MINERvA Tune v1 d^{3}#sigma;p_{T} (GeV/c);"
                      "p_{||} (GeV/c);E_{avail} (GeV)", PT, PZ, EA).Write()
    u3d.numpy_to_th2d(marg, marg_err, "hXSec2D",
                      "MINERvA Tune v1 Eavail-marginal;p_{T} (GeV/c);p_{||} (GeV/c)",
                      PT, PZ).Write()
    u3d.numpy_to_th1d(PT, x_pt, "hXSec_pt", "MINERvA Tune v1 d#sigma/dp_{T}").Write()
    u3d.numpy_to_th1d(PZ, x_pz, "hXSec_pz", "MINERvA Tune v1 d#sigma/dp_{||}").Write()
    u3d.numpy_to_th1d(EA, x_ea, "hXSec_eavail",
                      "MINERvA Tune v1 d#sigma/dE_{avail}").Write()
    fo.Close()
    print(f"[model] wrote {args.out}")


if __name__ == "__main__":
    main()
