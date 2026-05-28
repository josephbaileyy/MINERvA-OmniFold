#!/usr/bin/env python3
"""Build a data-POT-weighted MEFHC flux histogram from per-playlist files.

`unfold_2d_omnifold_unbinned.py --mcfile X` reads `pTmu_reweightedflux_integrated`
from X and uses it as the per-POT flux Phi[i] in the cross-section formula
d^2sigma = U / (eff * Phi * N * dpT * dpZ). For combined data spanning 12
playlists, the effective per-POT flux is the data-POT-weighted average of
the per-playlist per-POT fluxes:

    Phi_eff[i]  =  sum_p ( Phi_p[i] * POT_p_data ) / sum_p POT_p_data

Phi_p is read from `baseline_flux/runEventLoopMC_<playlist>.root`
(pTmu_reweightedflux_integrated, units m^-2/POT). POT_p_data is read from
`baseline_flux/runEventLoopData_<playlist>.root` (POTUsed). The hadd of
per-playlist OmniFold event-loop outputs already sums dataPOTUsed across
playlists, so Phi_eff computed this way matches the dataPOT stored in
runEventLoopOmniFold_MEFHC.root.

Implementation note: the per-playlist flux histogram is a PlotUtils::MnvH1D,
which segfaults when cloned + outlived its source file under this ROOT
build. We read bin content/error into plain numpy arrays before the file
goes out of scope and rebuild the output as a plain TH1D.
"""
import numpy as np
import ROOT
from array import array

PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G",
             "1L", "1M", "1N", "1O", "1P"]
BASE = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux"
OUT = f"{BASE}/runEventLoopMC_MEFHC.root"
HIST = "pTmu_reweightedflux_integrated"


def read_playlist(playlist):
    """Return (edges, contents, errors, pot_data, pot_mc) for one playlist."""
    mc_path = f"{BASE}/runEventLoopMC_{playlist}.root"
    data_path = f"{BASE}/runEventLoopData_{playlist}.root"

    fmc = ROOT.TFile.Open(mc_path, "READ")
    if not fmc or fmc.IsZombie():
        raise RuntimeError(f"Could not open {mc_path}")
    h = fmc.Get(HIST)
    if not h:
        raise RuntimeError(f"{HIST} missing in {mc_path}")
    n = h.GetNbinsX()
    edges = np.array([h.GetBinLowEdge(i) for i in range(1, n + 2)], dtype=float)
    contents = np.array([h.GetBinContent(i) for i in range(1, n + 1)], dtype=float)
    errors = np.array([h.GetBinError(i) for i in range(1, n + 1)], dtype=float)
    pot_mc_par = fmc.Get("POTUsed")
    if not pot_mc_par:
        raise RuntimeError(f"POTUsed missing in {mc_path}")
    pot_mc = float(pot_mc_par.GetVal())

    fdata = ROOT.TFile.Open(data_path, "READ")
    if not fdata or fdata.IsZombie():
        raise RuntimeError(f"Could not open {data_path}")
    pot_data_par = fdata.Get("POTUsed")
    if not pot_data_par:
        raise RuntimeError(f"POTUsed missing in {data_path}")
    pot_data = float(pot_data_par.GetVal())

    # Don't close fmc/fdata explicitly — dropping them is fine under PyROOT
    # and dodges the MnvH1D close segfault.
    return edges, contents, errors, pot_data, pot_mc


def main():
    per_playlist = []  # list of dicts
    ref_edges = None

    for p in PLAYLISTS:
        edges, contents, errors, pot_data, pot_mc = read_playlist(p)
        if ref_edges is None:
            ref_edges = edges
        elif not np.allclose(edges, ref_edges):
            raise RuntimeError(f"bin edges mismatch in {p}: {edges} vs {ref_edges}")
        per_playlist.append(dict(
            playlist=p, contents=contents, errors=errors,
            pot_data=pot_data, pot_mc=pot_mc))

    n_bins = len(ref_edges) - 1
    pot_tot_data = sum(pp["pot_data"] for pp in per_playlist)
    pot_tot_mc = sum(pp["pot_mc"] for pp in per_playlist)

    print(f"[info] read {len(per_playlist)} playlists, {n_bins} pT bins")
    print(f"[info] total data POT = {pot_tot_data:.6e}")
    print(f"[info] total mc   POT = {pot_tot_mc:.6e}")

    weights = np.array([pp["pot_data"] for pp in per_playlist])
    contents_stack = np.stack([pp["contents"] for pp in per_playlist])  # (12, n)
    errors_stack = np.stack([pp["errors"] for pp in per_playlist])

    combined_contents = (contents_stack.T @ weights) / pot_tot_data
    combined_err2 = ((errors_stack.T ** 2) @ (weights ** 2))
    combined_errors = np.sqrt(combined_err2) / pot_tot_data

    # Audit print
    one_a_idx = [i for i, pp in enumerate(per_playlist) if pp["playlist"] == "1A"][0]
    one_a = contents_stack[one_a_idx]
    print(f"\n{'bin':>4} {'pT_low':>7} {'pT_high':>8} "
          f"{'1A':>12} {'MEFHC':>12} {'%diff':>7}")
    for i in range(n_bins):
        pct = 100.0 * (combined_contents[i] - one_a[i]) / one_a[i] if one_a[i] else 0.0
        print(f"{i+1:>4} {ref_edges[i]:>7.3f} {ref_edges[i+1]:>8.3f} "
              f"{one_a[i]:>12.4e} {combined_contents[i]:>12.4e} {pct:>+6.2f}%")

    # Build plain TH1D (not MnvH1D) for the output
    h_out = ROOT.TH1D(HIST, "POT-weighted MEFHC flux (m^{-2}/POT)",
                     n_bins, array("d", ref_edges))
    for i in range(n_bins):
        h_out.SetBinContent(i + 1, float(combined_contents[i]))
        h_out.SetBinError(i + 1, float(combined_errors[i]))
    h_out.SetDirectory(0)

    print(f"\n[info] writing {OUT}")
    fout = ROOT.TFile.Open(OUT, "RECREATE")
    h_out.Write(HIST)
    ROOT.TParameter("double")("POTUsed", pot_tot_mc).Write()
    ROOT.TParameter("double")("DataPOTUsedForFluxWeighting",
                              pot_tot_data).Write()
    ROOT.TNamed("fluxSource",
                f"POT(data)-weighted combination of "
                f"baseline_flux/runEventLoopMC_<1A..1P>.root:{HIST}"
                ).Write()
    fout.Close()
    print("[ok] done")


if __name__ == "__main__":
    main()
