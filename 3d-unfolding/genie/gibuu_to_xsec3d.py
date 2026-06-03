#!/usr/bin/env python3
"""Histogram GiBUU FinalEvents.dat into d^3 sigma/(dpT dp|| dEavail) on the
analysis binning, for overlay on the unfolded OmniFold result.

GiBUU (NOvA CVMFS v2019) writes one row per final-state particle to
FinalEvents.dat (15 cols):
  1:Run 2:Event 3:ID 4:Charge 5:perweight 6-8:position 9:E 10:px 11:py 12:pz
  13:history 14:production_ID 15:enu
- The outgoing muon is GiBUU ID 902 (charge -1 for nu_mu CC); its 4-momentum is
  cols 9-12. neutrino is along +z (same convention as the GENIE/NuWro readers,
  no beam tilt) so pT=hypot(px,py), p||=pz.
- The INITIAL struck nucleon is written with perweight=0; final-state hadrons
  carry the (event-constant) perweight. So we take perweight from the muon row
  and build the final-state hadron list from perweight!=0, non-lepton rows.
- GiBUU IDs -> PDG: nucleon ID=1 (ch+1->2212 p, 0->2112 n); pion ID=101
  (ch+1->211, -1->-211, 0->111); photon ID=999->22. Eavail uses the same
  CVUniverse::GetEAvailableTrue() rule as the other readers (proton KE, pi+- E-m,
  pi0/gamma E).

Normalisation (per nucleon, GiBUU convention): GiBUU bakes the 1/numEnsembles
factor into perweight, so for ONE complete run sum_events(perweight) is already
the flux-averaged cross section in 10^-38 cm^2/nucleon (verified: a single
numEnsembles=4000 run gives sum=3.68, matching the ~3.7 NuWro/GENIE ME value).
Combining M identically-configured independent runs (one FinalEvents.dat each,
num_runs_SameEnergy=1) just averages them, so
  dsigma/dx[bin] = (sum perweight in bin)/M/dV * 1e-38 ,   M = number of files.
(numEnsembles is read only for a sanity print, not the normalisation.)

Output mirrors the unfold file (hXSec3D, hXSec2D, hXSec_pt/pz/eavail).

Run in the analysis env (root_6_28):
  python gibuu_to_xsec3d.py --finalevents work_gibuu/FinalEvents.dat \
      --jobcard work_gibuu/gibuu_mefhc_numu.job --out gibuu_cv_xsec3d.root
"""
import argparse
import glob
import os
import re
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import unfold_3d_omnifold_unbinned as u3d
from xsec_3d import project_eavail_marginal, project_axis

PT = np.asarray(u3d.PT_EDGES, float)
PZ = np.asarray(u3d.PZ_EDGES, float)
EA = np.asarray(u3d.EAVAIL_EDGES, float)
MASS_PI, MASS_P = 0.135, 0.93827
MUON_IDS = (901, 902, 903)


def read_jobcard_norm(path):
    """Pull numEnsembles and num_runs_SameEnergy from a GiBUU jobcard."""
    nens = nruns = None
    if path and os.path.exists(path):
        txt = open(path).read()
        m = re.search(r"numEnsembles\s*=\s*(\d+)", txt)
        if m:
            nens = int(m.group(1))
        m = re.search(r"num_runs_SameEnergy\s*=\s*(\d+)", txt)
        if m:
            nruns = int(m.group(1))
    return nens, nruns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--finalevents", required=True,
                    help="glob for FinalEvents.dat file(s) (one per run dir)")
    ap.add_argument("--jobcard", default=None,
                    help="jobcard to read numEnsembles/num_runs (per file)")
    ap.add_argument("--nens", type=int, default=None, help="override numEnsembles")
    ap.add_argument("--nruns", type=int, default=None, help="override num_runs_SameEnergy")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    files = sorted(glob.glob(args.finalevents))
    if not files:
        raise SystemExit(f"no FinalEvents files match {args.finalevents}")

    pt_l, pz_l, ea_l, w_l = [], [], [], []
    n_events = 0
    nens_info, _ = read_jobcard_norm(args.jobcard) if args.jobcard else (args.nens, None)
    norm_total = float(len(files))   # M independent runs -> average; perweight already /numEnsembles
    for fi, fn in enumerate(files):
        d = np.loadtxt(fn, comments="#")
        if d.ndim == 1:
            d = d[None, :]
        run = d[:, 0].astype(np.int64); ev = d[:, 1].astype(np.int64)
        pid = d[:, 2].astype(int); ch = d[:, 3].astype(int)
        pw = d[:, 4]; E = d[:, 8]; px = d[:, 9]; py = d[:, 10]; pz = d[:, 11]

        key = run * 10_000_000 + ev
        ukey, inv = np.unique(key, return_inverse=True)
        nev = ukey.size
        n_events += nev

        lep = np.isin(pid, MUON_IDS)
        pt_e = np.full(nev, np.nan); pz_e = np.full(nev, np.nan); w_e = np.zeros(nev)
        li = inv[lep]
        pt_e[li] = np.hypot(px[lep], py[lep]); pz_e[li] = pz[lep]; w_e[li] = pw[lep]

        # Eavail contribution per final-state hadron row (perweight!=0, not lepton)
        had = (pw != 0) & (~lep)
        econ = np.zeros(d.shape[0])
        m = had & (pid == 1) & (ch == 1);            econ[m] = E[m] - MASS_P       # proton KE
        m = had & (pid == 101) & (np.abs(ch) == 1);  econ[m] = E[m] - MASS_PI      # pi+- (KE-ish, matches reader)
        m = had & (pid == 101) & (ch == 0);          econ[m] = E[m]                # pi0
        m = had & (pid == 999);                      econ[m] = E[m]                # photon
        ea_e = np.zeros(nev); np.add.at(ea_e, inv, econ)

        ok = np.isfinite(pt_e) & (w_e > 0)
        pt_l.append(pt_e[ok]); pz_l.append(pz_e[ok]); ea_l.append(ea_e[ok]); w_l.append(w_e[ok])

    pt, pz, ea, w = map(np.concatenate, (pt_l, pz_l, ea_l, w_l))
    print(f"[gibuu] files(runs)={len(files)} numEnsembles/run~{nens_info} "
          f"events={n_events} with-muon={pt.size} norm(avg over runs)={norm_total:.0f}")

    sigma_tot_all = w.sum() / norm_total
    print(f"[gibuu] flux-avg <sigmaCC>/nucleon (all, pre-PS) = {sigma_tot_all:.4e} "
          f"(x1e-38 cm^2) -- expect a few for MINERvA ME")

    # truth phase space: rectangle + theta_mu < 20 deg (vectorised mirror of in_ps)
    m = (np.isfinite(pt) & np.isfinite(pz)
         & (pt >= PT[0]) & (pt <= PT[-1]) & (pz >= PZ[0]) & (pz <= PZ[-1])
         & (np.arctan2(pt, pz) < u3d.u2d.MAX_MUON_THETA_RAD))
    pt, pz, ea, w = pt[m], pz[m], ea[m], w[m]
    print(f"[gibuu] in phase space = {pt.size}")

    wsum, _ = np.histogramdd(np.column_stack([pt, pz, ea]), bins=[PT, PZ, EA], weights=w)
    w2, _ = np.histogramdd(np.column_stack([pt, pz, ea]), bins=[PT, PZ, EA], weights=w * w)
    dV = (np.diff(PT)[:, None, None] * np.diff(PZ)[None, :, None] * np.diff(EA)[None, None, :])
    xsec3d = wsum / norm_total / dV * 1.0e-38          # cm^2/nucleon / (GeV/c)^2 / GeV
    xerr = np.sqrt(w2) / norm_total / dV * 1.0e-38
    total = (xsec3d * dV).sum()
    print(f"[gibuu] total sigma (in PS) = {total:.4e} cm^2/nucleon")

    marg = project_eavail_marginal(xsec3d, EA)
    dea = np.diff(EA)[None, None, :]
    marg_err = np.sqrt(((xerr * dea) ** 2).sum(axis=2))
    _, x_pt = project_axis(xsec3d, PT, PZ, EA, "pt")
    _, x_pz = project_axis(xsec3d, PT, PZ, EA, "pz")
    _, x_ea = project_axis(xsec3d, PT, PZ, EA, "eavail")

    fo = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th3d(xsec3d, xerr, "hXSec3D",
                      "GiBUU d^{3}#sigma;p_{T} (GeV/c);p_{||} (GeV/c);E_{avail} (GeV)",
                      PT, PZ, EA).Write()
    u3d.numpy_to_th2d(marg, marg_err, "hXSec2D",
                      "GiBUU Eavail-marginal;p_{T} (GeV/c);p_{||} (GeV/c)", PT, PZ).Write()
    u3d.numpy_to_th1d(PT, x_pt, "hXSec_pt", "GiBUU d#sigma/dp_{T}").Write()
    u3d.numpy_to_th1d(PZ, x_pz, "hXSec_pz", "GiBUU d#sigma/dp_{||}").Write()
    u3d.numpy_to_th1d(EA, x_ea, "hXSec_eavail", "GiBUU d#sigma/dE_{avail}").Write()
    ROOT.TParameter("double")("nEvents", float(n_events)).Write()
    fo.Close()
    print(f"[gibuu] wrote {args.out}")


if __name__ == "__main__":
    main()
