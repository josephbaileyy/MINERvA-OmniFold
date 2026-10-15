#!/usr/bin/env python3
"""Per-period data-POT-weighted flux file, built with the pinned production combiner's reader and arithmetic.

    python3 build_flux.py PERIOD                 # PERIOD in PA, PB, PC, ALL -> $NS/flux/runEventLoopMC_<PERIOD>.root
    python3 build_flux.py --via-main PERIOD OUT  # equivalence test: the combiner's own main() (needs 1A in PERIOD)

Phi_eff[i] = sum_p Phi_p[i] POT_p,data / sum_p POT_p,data over the period's playlists only.

combine_flux_MEFHC.py (sha256 1fc5c1e9..., main c67dbdda) cannot be called unchanged for PB or PC: its main()
indexes playlist 1A for an audit print (combine_flux_MEFHC.py:99) and raises IndexError without it. So this
script imports the pinned module, reads every playlist with its read_playlist() (:35-65), and applies the same
expressions as main() (:85-96 combination, :108-126 output: plain TH1D 'pTmu_reweightedflux_integrated',
TParameter POTUsed = summed MC POT, DataPOTUsedForFluxWeighting = summed data POT). It adds a TNamed
'periodPlaylists'. Equivalence is tested two ways (verify_inputs.py and --via-main): ALL must equal the
production flux file d40aea69 bin by bin, and PA/ALL must equal the combiner's own main() output.
"""
import importlib.util
import os
import sys
from array import array

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import periods as PD  # noqa: E402


def load_combiner():
    PD.check_pin("combine_flux")
    spec = importlib.util.spec_from_file_location("combine_flux_MEFHC", PD.PINS["combine_flux"][0])
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)
    assert cf.BASE == PD.BASE_FLUX, cf.BASE
    return cf


def build(period, out):
    import ROOT
    cf = load_combiner()
    pls = PD.PERIODS[period]
    per = []
    ref_edges = None
    for p in pls:
        edges, contents, errors, pot_data, pot_mc = cf.read_playlist(p)
        if ref_edges is None:
            ref_edges = edges
        elif not np.allclose(edges, ref_edges):
            raise RuntimeError(f"bin edges mismatch in {p}")
        per.append(dict(playlist=p, contents=contents, errors=errors, pot_data=pot_data, pot_mc=pot_mc))
    n_bins = len(ref_edges) - 1
    pot_tot_data = sum(pp["pot_data"] for pp in per)
    pot_tot_mc = sum(pp["pot_mc"] for pp in per)
    weights = np.array([pp["pot_data"] for pp in per])
    contents_stack = np.stack([pp["contents"] for pp in per])
    errors_stack = np.stack([pp["errors"] for pp in per])
    combined_contents = (contents_stack.T @ weights) / pot_tot_data
    combined_err2 = ((errors_stack.T ** 2) @ (weights ** 2))
    combined_errors = np.sqrt(combined_err2) / pot_tot_data
    h_out = ROOT.TH1D(cf.HIST, "POT-weighted MEFHC flux (m^{-2}/POT)", n_bins, array("d", ref_edges))
    for i in range(n_bins):
        h_out.SetBinContent(i + 1, float(combined_contents[i]))
        h_out.SetBinError(i + 1, float(combined_errors[i]))
    h_out.SetDirectory(0)
    fout = ROOT.TFile.Open(out, "RECREATE")
    h_out.Write(cf.HIST)
    ROOT.TParameter("double")("POTUsed", pot_tot_mc).Write()
    ROOT.TParameter("double")("DataPOTUsedForFluxWeighting", pot_tot_data).Write()
    ROOT.TNamed("fluxSource", f"POT(data)-weighted combination of baseline_flux/runEventLoopMC_<{','.join(pls)}>.root:"
                f"{cf.HIST} (period {period}; period-unfold-20261014/scripts/build_flux.py)").Write()
    ROOT.TNamed("periodPlaylists", ",".join(pls)).Write()
    fout.Close()
    print(f"[build_flux] {period} {pls}: data POT {pot_tot_data:.6e}, mc POT {pot_tot_mc:.6e}, "
          f"flux sum {combined_contents.sum():.7e} -> {out}")


def via_main(period, out):
    cf = load_combiner()
    cf.PLAYLISTS = list(PD.PERIODS[period])   # main() reads the module globals at call time (:72, :116-117)
    cf.OUT = out
    cf.main()


if __name__ == "__main__":
    if sys.argv[1] == "--via-main":
        via_main(sys.argv[2], sys.argv[3])
    else:
        period = sys.argv[1]
        out = PD.flux_file(period)
        if os.path.exists(out):
            sys.exit(f"REFUSE: {out} exists")
        build(period, out)
        os.chmod(out, 0o440)
