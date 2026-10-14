"""Per-playlist reco-level yields for the proxy R = (D - k B) / (k S), k = POT_d / POT_mc, on two grids.

Usage: python -I proxy_hists.py <dir with runEventLoopOmniFold_<PL>.root> <out.npz> <out.json>

Same inputs, cuts and weights as the prior ref_shape.py (May per-playlist CV event-loop outputs):
  D = data tree (measured, measured_pz), all rows; S = mc_signal_reco with sim_pass == 1, weight w_reco, reco
  (sim, sim_pz); B = mc_background with sim_background_pass == 1, weight w_bkg.
Grids: the triage/proxy 10 x 10 grid, and the 14 x 16 analysis grid (uq/reported_cells.py). Rows = p_T.
Stores sum w and sum w^2 so the MC statistical error can be formed. The proxy grid is an exact coarsening of the
analysis grid (every proxy edge is an analysis edge); this is checked.
"""
import hashlib
import json
import os
import sys

import numpy as np
import ROOT

d, out_npz, out_json = sys.argv[1:4]
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
GRIDS = {
    "proxy": (np.array([0, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5]),
              np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60])),
    "ana": (np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]),
            np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])),
}
for a, b in zip(GRIDS["proxy"], GRIDS["ana"]):
    assert all(np.isclose(e, b).any() for e in a), "proxy grid is not a coarsening of the analysis grid"


def h2(g, x, y, w=None):
    return np.histogram2d(x, y, list(GRIDS[g]), weights=w)[0]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


save, meta = {}, {}
for pl in PLS:
    fn = f"{d}/runEventLoopOmniFold_{pl}.root"
    f = ROOT.TFile.Open(fn)
    potmc, potd = f.Get("mcPOTUsed").GetVal(), f.Get("dataPOTUsed").GetVal()
    f.Close()
    D = ROOT.RDataFrame("data", fn).AsNumpy(["measured", "measured_pz"])
    S = ROOT.RDataFrame("mc_signal_reco", fn).Define("sp", "(int)sim_pass").Filter("sp == 1").AsNumpy(
        ["sim", "sim_pz", "w_reco"])
    B = ROOT.RDataFrame("mc_background", fn).Define("bp", "(int)sim_background_pass").Filter("bp == 1").AsNumpy(
        ["sim_background", "sim_background_pz", "w_bkg"])
    for g in GRIDS:
        save[f"{pl}__{g}__D"] = h2(g, D["measured"], D["measured_pz"])
        save[f"{pl}__{g}__S"] = h2(g, S["sim"], S["sim_pz"], S["w_reco"])
        save[f"{pl}__{g}__S2"] = h2(g, S["sim"], S["sim_pz"], S["w_reco"] ** 2)
        save[f"{pl}__{g}__B"] = h2(g, B["sim_background"], B["sim_background_pz"], B["w_bkg"])
        save[f"{pl}__{g}__B2"] = h2(g, B["sim_background"], B["sim_background_pz"], B["w_bkg"] ** 2)
    meta[pl] = {"path": os.path.realpath(fn), "sha256": sha(fn), "pot_data": potd, "pot_mc": potmc,
                "n_data": int(len(D["measured"])), "n_sig_pass": int(len(S["sim"])), "n_bkg_pass": int(len(B["w_bkg"]))}
    print(pl, meta[pl]["n_data"], meta[pl]["n_sig_pass"], flush=True)
for g, (a, b) in GRIDS.items():
    save[f"edges__{g}__pt"], save[f"edges__{g}__pz"] = a, b
np.savez(out_npz, **save)
json.dump(meta, open(out_json, "w"), indent=1)
