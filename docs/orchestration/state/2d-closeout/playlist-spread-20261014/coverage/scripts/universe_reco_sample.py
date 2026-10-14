"""Reco-level proxy yields under every systematic universe, per playlist, on a light sample.

Usage: python -I universe_reco_sample.py <PL> <n_signal_entries or 0 for all> <out.npz> [first entry, default 0]

Input: /pscratch/.../2d-unfolding/runEventLoopOmniFold_<PL>_universes_full.root (the per-playlist universe
event-loop outputs that hadd into the production _universes_full omnifile).
For the first N entries of mc_signal_reco (sim_pass == 1) and ALL of mc_background (sim_background_pass == 1) it
fills, on the 10 x 10 proxy grid, the CV yield and the yield in every universe:
  vertical universe: weight w_reco_<band>_<i> (signal) / w_bkg_<band>_<i> (background), CV reco kinematics;
  lateral universe : the same weight with the shifted reco kinematics sim_<band>_<i>, sim_pz_<band>_<i>
                     (signal) / sim_background_<band>_<i>, sim_background_pz_<band>_<i> (background),
                     as unfold_2d_omnifold_unbinned.py does (_universe_kine_branches).
Weights that are not finite or outside [0, 1e4) are set to 0, as the producer drops them.
Also the full data yield. Only ratios universe/CV on the same events are used downstream.
"""
import sys

import numpy as np
import ROOT

pl, nsig, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
fn = f"/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_{pl}_universes_full.root"
PT = np.array([0, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5])
PZ = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60])
ROOT.gInterpreter.Declare("#include <cmath>")

f = ROOT.TFile.Open(fn)
potmc, potd = f.Get("mcPOTUsed").GetVal(), f.Get("dataPOTUsed").GetVal()
tsig, tbkg = f.Get("mc_signal_reco"), f.Get("mc_background")
sig_br = {b.GetName() for b in tsig.GetListOfBranches()}
bkg_br = {b.GetName() for b in tbkg.GetListOfBranches()}
n_sig_total, n_bkg_total = tsig.GetEntries(), tbkg.GetEntries()
f.Close()
unis = sorted(n[len("w_reco_"):] for n in sig_br if n.startswith("w_reco_"))


def model(name):
    return ROOT.RDF.TH2DModel(name, "", len(PT) - 1, PT, len(PZ) - 1, PZ)


def book(df, wcol_prefix, xcv, ycv, xlat, ylat, branches, tag):
    hs = {"CV": df.Histo2D(model(f"{tag}_CV"), xcv, ycv, "wcv")}
    lat = {}
    for u in unis:
        wb = f"{wcol_prefix}{u}"
        if wb not in branches:
            continue
        col = f"ww_{u}"
        df = df.Define(col, f"(std::isfinite({wb}) && {wb} >= 0 && {wb} < 1e4) ? (double){wb} : 0.0")
        xl, yl = xlat.format(u=u), ylat.format(u=u)
        if xl in branches and yl in branches:
            hs[u] = df.Histo2D(model(f"{tag}_{u}"), xl, yl, col)
            lat[u] = True
        else:
            hs[u] = df.Histo2D(model(f"{tag}_{u}"), xcv, ycv, col)
    return df, hs, lat


ds = ROOT.RDataFrame("mc_signal_reco", fn)
if nsig > 0:
    ds = ds.Range(start, start + nsig)
ds = ds.Define("sp", "(int)sim_pass").Filter("sp == 1").Define(
    "wcv", "(std::isfinite(w_reco) && w_reco >= 0 && w_reco < 1e4) ? w_reco : 0.0")
ds, HS, LAT = book(ds, "w_reco_", "sim", "sim_pz", "sim_{u}", "sim_pz_{u}", sig_br, "S")
cnt_s = ds.Count()

db = ROOT.RDataFrame("mc_background", fn).Define("bp", "(int)sim_background_pass").Filter("bp == 1").Define(
    "wcv", "(std::isfinite(w_bkg) && w_bkg >= 0 && w_bkg < 1e4) ? w_bkg : 0.0")
db, HB, LATB = book(db, "w_bkg_", "sim_background", "sim_background_pz", "sim_background_{u}",
                    "sim_background_pz_{u}", bkg_br, "B")
hd = ROOT.RDataFrame("data", fn).Histo2D(model("D"), "measured", "measured_pz")


def arr(h):
    h = h.GetValue()
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(len(PZ) - 1)] for i in range(len(PT) - 1)])


save = {"first_entry": start, "pot_mc": potmc, "pot_data": potd, "n_sig_entries_total": n_sig_total, "n_sig_entries_used":
        (min(nsig, n_sig_total) if nsig > 0 else n_sig_total), "n_bkg_entries_total": n_bkg_total,
        "universes": np.array(unis), "lateral": np.array(sorted(LAT)), "lateral_bkg": np.array(sorted(LATB))}
save["D"] = arr(hd)
for k, h in HS.items():
    save["S__" + k] = arr(h)
for k, h in HB.items():
    save["B__" + k] = arr(h)
save["n_sig_pass_used"] = cnt_s.GetValue()
missing_b = [u for u in unis if u not in HB]
save["bkg_universes_missing"] = np.array(missing_b)
np.savez(out, **save)
print(pl, "sig entries used", save["n_sig_entries_used"], "of", n_sig_total, "pass", save["n_sig_pass_used"],
      "universes", len(unis), "lateral", sorted(LAT), "bkg missing", len(missing_b), flush=True)
