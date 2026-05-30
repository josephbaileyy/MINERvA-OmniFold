#!/usr/bin/env python3
"""Build the POT-weighted MEFHC per-universe flux integral band.

`combine_flux_MEFHC.py` collapses the per-playlist flux MnvH1D to a CV-only
TH1D, discarding the 100-universe PPFX `Flux` vert error band that each
per-playlist `baseline_flux/runEventLoopMC_<PL>.root` already carries. The
2D cross section divides by this flux integral per pT bin
(`extract_cross_section_2d`), and the universe unfolds use the *same* CV
flux in every flux universe, so the dominant flux term (sigma ~ 1/Phi, the
~5% fully-correlated normalization) is never propagated.

This script POT-weight-combines the per-universe flux integrals across the
12 playlists exactly as the CV is combined:

    Phi_u[i] = sum_p ( Phi_{p,u}[i] * POT_p^data ) / sum_p POT_p^data

and writes them, plus the CV, to a plain-ROOT file (no MnvH1D persistence,
sidestepping the clone/outlive segfault noted in combine_flux_MEFHC.py):

    hFluxCV    TH1D  [14 pT bins]            CV flux integral (m^-2/POT)
    hFluxUniv  TH2D  [14 pT x 100 universe]  per-universe flux integral

Consistency guard: hFluxCV must equal the existing CV TH1D
`pTmu_reweightedflux_integrated` in runEventLoopMC_MEFHC.root to ~1e-12.

Index convention: universe column u is PPFX universe u, the same physical
throw as `w_{truth,reco}_Flux_u` in the OmniFold omnifile (verified by
flux-integral vs event-weight ratio correlation, Pearson 0.96).
"""
import sys
import numpy as np
import ROOT
from array import array

BASE = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G",
             "1L", "1M", "1N", "1O", "1P"]
HIST = "pTmu_reweightedflux_integrated"
NU = 100
OUT = f"{BASE}/flux_integral_universes_MEFHC.root"


def main():
    cv_stack, uni_stack, pot_w = [], [], []
    edges = None
    for pl in PLAYLISTS:
        fmc = ROOT.TFile.Open(f"{BASE}/runEventLoopMC_{pl}.root")
        if not fmc or fmc.IsZombie():
            sys.exit(f"[FAIL] cannot open MC flux file for {pl}")
        h = fmc.Get(HIST)
        if not h:
            sys.exit(f"[FAIL] {HIST} missing in {pl}")
        n = h.GetNbinsX()
        e = np.array([h.GetBinLowEdge(i) for i in range(1, n + 2)])
        if edges is None:
            edges = e
        elif not np.allclose(e, edges):
            sys.exit(f"[FAIL] pT edge mismatch in {pl}")
        cv_stack.append(np.array([h.GetBinContent(i) for i in range(1, n + 1)]))
        fb = h.GetVertErrorBand("Flux")
        if not fb or fb.GetNHists() != NU:
            sys.exit(f"[FAIL] {pl} Flux band missing or != {NU} universes")
        uni_stack.append(np.array(
            [[fb.GetHist(u).GetBinContent(i) for i in range(1, n + 1)]
             for u in range(NU)]))
        fd = ROOT.TFile.Open(f"{BASE}/runEventLoopData_{pl}.root")
        pot_w.append(float(fd.Get("POTUsed").GetVal()))
        fmc.Close()
        fd.Close()

    pot_w = np.array(pot_w)
    W = pot_w.sum()
    n_pt = len(edges) - 1
    Phi_cv = (np.stack(cv_stack).T @ pot_w) / W                  # (n_pt,)
    Phi_u = np.tensordot(pot_w, np.stack(uni_stack), axes=([0], [0])) / W  # (NU,n_pt)

    # Consistency: combined CV must match the existing CV TH1D.
    fM = ROOT.TFile.Open(f"{BASE}/runEventLoopMC_MEFHC.root")
    hM = fM.Get(HIST)
    Phi_exist = np.array([hM.GetBinContent(i) for i in range(1, hM.GetNbinsX() + 1)])
    fM.Close()
    max_rel = np.abs(Phi_cv - Phi_exist).max() / np.abs(Phi_exist).max()
    print(f"[info] {len(PLAYLISTS)} playlists, {n_pt} pT bins, {NU} universes")
    print(f"[info] total data POT weight = {W:.6e}")
    print(f"[check] combined CV vs existing TH1D: max rel diff = {max_rel:.2e}")
    if max_rel > 1e-9:
        sys.exit(f"[FAIL] combined CV disagrees with existing TH1D ({max_rel:.2e})")

    ratio = Phi_cv[None, :] / Phi_u
    print(f"[info] per-universe norm spread std_u(Phi_cv/Phi_u): "
          f"median {np.median(ratio.std(axis=0)) * 100:.2f}% per pT")

    edges_arr = array("d", edges)
    hcv = ROOT.TH1D("hFluxCV", "POT-weighted MEFHC CV flux integral;"
                    "p_{T} (GeV/c);Flux (m^{-2}/POT)", n_pt, edges_arr)
    for i in range(n_pt):
        hcv.SetBinContent(i + 1, float(Phi_cv[i]))
    hcv.SetDirectory(0)
    huniv = ROOT.TH2D("hFluxUniv", "POT-weighted MEFHC per-universe flux integral;"
                      "p_{T} (GeV/c);PPFX universe", n_pt, edges_arr, NU, 0, NU)
    for u in range(NU):
        for i in range(n_pt):
            huniv.SetBinContent(i + 1, u + 1, float(Phi_u[u, i]))
    huniv.SetDirectory(0)

    fout = ROOT.TFile.Open(OUT, "RECREATE")
    hcv.Write()
    huniv.Write()
    ROOT.TParameter("double")("DataPOTWeight", W).Write()
    fout.Close()
    print(f"[wrote] {OUT}  (hFluxCV, hFluxUniv)")


if __name__ == "__main__":
    main()
