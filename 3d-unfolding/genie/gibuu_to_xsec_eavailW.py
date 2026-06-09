#!/usr/bin/env python3
"""Histogram GiBUU FinalEvents.dat into d^2 sigma/(dEavail dW) for the (E_avail, W)
generator band (open question 6: the high-E_avail DIS-tail excess localised in W).

GiBUU's FinalEvents.dat carries everything experimenter's W needs -- the per-event
neutrino energy is column 15 (event-constant), and the outgoing muon (GiBUU ID 902)
gives Emu/theta_mu from its 4-momentum (cols 9-12). So W replicates
CVUniverse::GetTrueExperimentersW() with no regeneration beyond the existing
FinalEvents.dat:

    Q2 = 4 Enu Emu sin^2(theta_mu/2);  W = sqrt(M_n^2 + 2(Enu-Emu)M_n - Q2)   [GeV]

Eavail + the GiBUU perweight normalisation (per nucleon, /numEnsembles baked in,
averaged over M run files) are identical to gibuu_to_xsec3d.py. Output mirrors
gen_to_xsec_eavailW.py (hXSec_eavailW, hXSec_eavail, hXSec_W, nCCtotal) so the
overlay_eavailW_band.py path is shared.

  python gibuu_to_xsec_eavailW.py --finalevents 'work_gibuu_arr/task*/FinalEvents.dat' \
      --out gibuu_cv_xsec_eavailW.root
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
import unfold_3d_omnifold_unbinned as u3d           # binning helpers (numpy_to_th*)

EAVAIL_EDGES = np.asarray([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0], float)
W_EDGES = np.asarray([0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0], float)
PT = np.asarray(u3d.PT_EDGES, float)
PZ = np.asarray(u3d.PZ_EDGES, float)
MASS_PI, MASS_P, M_NUCLEON, M_MU = 0.135, 0.93827, 0.939565, 0.105658
MUON_IDS = (901, 902, 903)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--finalevents", required=True, help="glob for FinalEvents.dat file(s)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    files = sorted(glob.glob(args.finalevents))
    if not files:
        raise SystemExit(f"no FinalEvents files match {args.finalevents}")
    norm_total = float(len(files))

    ea_l, w_l, W_l, ptkeep, pzkeep = [], [], [], [], []
    n_events = 0
    for fn in files:
        d = np.loadtxt(fn, comments="#")
        if d.ndim == 1:
            d = d[None, :]
        run = d[:, 0].astype(np.int64); ev = d[:, 1].astype(np.int64)
        pid = d[:, 2].astype(int); ch = d[:, 3].astype(int)
        pw = d[:, 4]; E = d[:, 8]; px = d[:, 9]; py = d[:, 10]; pz = d[:, 11]
        enu = d[:, 14]

        key = run * 10_000_000 + ev
        ukey, inv = np.unique(key, return_inverse=True)
        nev = ukey.size
        n_events += nev

        lep = np.isin(pid, MUON_IDS)
        pt_e = np.full(nev, np.nan); pz_e = np.full(nev, np.nan)
        emu_e = np.full(nev, np.nan); enu_e = np.full(nev, np.nan); w_e = np.zeros(nev)
        li = inv[lep]
        pt_e[li] = np.hypot(px[lep], py[lep]); pz_e[li] = pz[lep]
        emu_e[li] = E[lep]; enu_e[li] = enu[lep]; w_e[li] = pw[lep]

        # Eavail per CVUniverse::GetEAvailableTrue() (same as gibuu_to_xsec3d.py)
        had = (pw != 0) & (~lep)
        econ = np.zeros(d.shape[0])
        m = had & (pid == 1) & (ch == 1);           econ[m] = E[m] - MASS_P
        m = had & (pid == 101) & (np.abs(ch) == 1); econ[m] = E[m] - MASS_PI
        m = had & (pid == 101) & (ch == 0);         econ[m] = E[m]
        m = had & (pid == 999);                     econ[m] = E[m]
        ea_e = np.zeros(nev); np.add.at(ea_e, inv, econ)

        # experimenter's W from Enu (col 15) + muon (Emu, theta wrt +z)
        pmu = np.sqrt(np.clip(emu_e**2 - M_MU**2, 0, None))
        with np.errstate(invalid="ignore", divide="ignore"):
            costh = np.clip(pz_e / pmu, -1.0, 1.0)
            theta = np.arccos(costh)
            q2 = 4.0 * enu_e * emu_e * np.sin(theta / 2.0) ** 2
            w2 = M_NUCLEON**2 + 2.0 * (enu_e - emu_e) * M_NUCLEON - q2
            W_e = np.where(w2 > 0, np.sqrt(np.clip(w2, 0, None)), 0.0)

        ok = np.isfinite(pt_e) & (w_e > 0) & np.isfinite(enu_e)
        ea_l.append(ea_e[ok]); w_l.append(w_e[ok]); W_l.append(W_e[ok])
        ptkeep.append(pt_e[ok]); pzkeep.append(pz_e[ok])   # for the phase-space gate

    ea = np.concatenate(ea_l); w = np.concatenate(w_l); W = np.concatenate(W_l)
    pt = np.concatenate(ptkeep); pz = np.concatenate(pzkeep)
    print(f"[gibuu_eavailW] files(runs)={len(files)} events={n_events} with-muon={ea.size}")

    # truth phase space: rectangle + theta_mu < 20 deg
    m = ((pt >= PT[0]) & (pt <= PT[-1]) & (pz >= PZ[0]) & (pz <= PZ[-1])
         & (np.arctan2(pt, pz) < u3d.u2d.MAX_MUON_THETA_RAD))
    ea, w, W = ea[m], w[m], W[m]
    print(f"[gibuu_eavailW] in phase space = {ea.size}")

    counts, _ = np.histogramdd(np.column_stack([ea, W]), bins=[EAVAIL_EDGES, W_EDGES], weights=w)
    dea = np.diff(EAVAIL_EDGES)[:, None]; dw = np.diff(W_EDGES)[None, :]
    widths = dea * dw
    xsec = counts / norm_total / widths * 1.0e-38          # cm^2/nucleon / GeV^2
    x_ea = (xsec * dw).sum(axis=1)
    x_w = (xsec * dea).sum(axis=0)
    total = (xsec * widths).sum()
    print(f"[gibuu_eavailW] total sigma (in PS) = {total:.4e} cm^2/nucleon")

    fo = ROOT.TFile.Open(args.out, "RECREATE")
    u3d.numpy_to_th2d(xsec, None, "hXSec_eavailW",
                      "GiBUU d^{2}#sigma/(dE_{avail}dW);E_{avail} (GeV);W (GeV)",
                      EAVAIL_EDGES, W_EDGES).Write()
    u3d.numpy_to_th1d(EAVAIL_EDGES, x_ea, "hXSec_eavail", "GiBUU d#sigma/dE_{avail}").Write()
    u3d.numpy_to_th1d(W_EDGES, x_w, "hXSec_W", "GiBUU d#sigma/dW").Write()
    ROOT.TParameter("double")("nCCtotal", float(n_events)).Write()
    fo.Close()
    print(f"[gibuu_eavailW] wrote {args.out}")


if __name__ == "__main__":
    main()
