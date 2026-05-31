#!/usr/bin/env python3
"""Convert the MINERvA ME FHC numu flux histogram (a PlotUtils::MnvH1D, which
GENIE cannot read -> its integral reads as zero and flux sampling fails) into a
plain ROOT TH1D that gevgen's GCylindTH1Flux driver reads correctly.

Writes two files (both consumed downstream; run this once before generating):
  - flux_mefhc_numu.root:flux_numu          full 0-100 GeV (GENIE; setup_genie.sh)
  - flux_mefhc_numu_nuwro.root:flux_numu    same hist restricted to [0.5,50] GeV
    (NuWro; setup_nuwro.sh -- NuWro's flux-driven phase crashes on the extreme
    flux edges, so the tails are zeroed)
To swap to the PPFX-reweighted flux, change SRC_FILE/SRC_HIST.

Run ONCE in the analysis env (root_6_28, which has the MnvH1D dictionary):
  python make_flux_for_genie.py
"""
import array
import os
import ROOT

FLUXDIR = ("/cvmfs/minerva.opensciencegrid.org/minerva/"
           "CentralizedFluxAndReweightFiles/MATFluxAndReweightFiles/flux")
SRC_FILE = f"{FLUXDIR}/flux-g4numiv6-pdg14-minervame1D1M1NWeightedAve.root"
SRC_HIST = "flux_E_unweighted"
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "flux_mefhc_numu.root")
OUT_HIST = "flux_numu"


def main():
    ROOT.gROOT.SetBatch(True)
    ROOT.gErrorIgnoreLevel = ROOT.kError
    fin = ROOT.TFile.Open(SRC_FILE)
    src = fin.Get(SRC_HIST)
    if not src:
        raise SystemExit(f"hist {SRC_HIST} not in {SRC_FILE}")
    n = src.GetNbinsX()
    # copy edges + contents into python, then close the source (avoids
    # cross-file object-ownership teardown crashes with MnvH1D)
    edges = array.array("d", [src.GetBinLowEdge(i) for i in range(1, n + 2)])
    vals = [src.GetBinContent(i) for i in range(1, n + 1)]
    integral = src.Integral()
    fin.Close()

    fout = ROOT.TFile.Open(OUT_FILE, "RECREATE")
    h = ROOT.TH1D(OUT_HIST, "MINERvA ME FHC #nu_{#mu} flux;E_{#nu} (GeV);flux",
                  n, edges)
    for i, v in enumerate(vals, start=1):
        h.SetBinContent(i, float(v))
    h.SetDirectory(fout)
    h.Write()
    out_integral = h.Integral()
    fout.Close()
    print(f"[make_flux] wrote {OUT_FILE}:{OUT_HIST}  nbins={n} "
          f"range=[{edges[0]},{edges[-1]}] GeV  integral={out_integral:.4e} "
          f"(source MnvH1D integral={integral:.4e})")

    # NuWro variant: same GeV hist but with bins outside [0.5,50] GeV zeroed.
    # NuWro's flux-driven test-event phase crashes on the extreme flux edges
    # (sub-threshold low-E / far tail); restricting avoids it (see setup_nuwro.sh).
    NUWRO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "flux_mefhc_numu_nuwro.root")
    LO, HI = 0.5, 50.0
    fn = ROOT.TFile.Open(NUWRO_FILE, "RECREATE")
    hn = ROOT.TH1D(OUT_HIST, "MINERvA ME FHC numu flux (GeV, restricted for "
                   "NuWro);E_{#nu} (GeV);flux", n, edges)
    kept = 0
    for i, v in enumerate(vals, start=1):
        c = 0.5 * (edges[i - 1] + edges[i])
        if LO <= c <= HI:
            hn.SetBinContent(i, float(v)); kept += 1
    hn.SetDirectory(fn)
    hn.Write()
    nuwro_integral = hn.Integral()
    fn.Close()
    print(f"[make_flux] wrote {NUWRO_FILE}:{OUT_HIST}  ({kept}/{n} bins in "
          f"[{LO},{HI}] GeV, integral={nuwro_integral:.4e}) for NuWro")


if __name__ == "__main__":
    main()
