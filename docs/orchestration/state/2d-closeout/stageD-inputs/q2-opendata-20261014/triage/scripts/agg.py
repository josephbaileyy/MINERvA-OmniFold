"""Aggregate pair.py outputs over all 1A files and compare the emulated selection to production counts.
Usage: python -I agg.py <triage_dir> <production_1A_root>"""
import glob
import json
import os
import sys

import numpy as np
import ROOT

d, prod = sys.argv[1], sys.argv[2]
out = {}
for kind, dirs in (("data", ["scan_data", "scan_data_rev"]), ("mc", ["scan_mc"])):
    recs = {}
    for sub in dirs:
        for fn in glob.glob(f"{d}/{sub}/*.json"):
            recs[os.path.basename(fn)] = json.load(open(fn))
    S = lambda k, i: sum(r[k][i] for r in recs.values())
    s = lambda k: sum(r[k] for r in recs.values())
    o = {"files": len(recs), "entries": [S("entries", 0), S("entries", 1)], "joined": s("joined"),
         "pot_used": [S("pot_used", 0), S("pot_used", 1)], "sel_total": [S("sel_total", 0), S("sel_total", 1)],
         "sel_both": s("sel_both"), "sel_A_only": s("sel_A_only"), "sel_B_only": s("sel_B_only"),
         "sel_unjoined": [S("sel_unjoined", 0), S("sel_unjoined", 1)],
         "n_is_ok_differs": s("n_is_ok_differs"), "n_is_ok_differs_in_fid": s("n_is_ok_differs_in_fid"),
         "n_is_ok_differs_in_fid_ang_and_matched": s("n_is_ok_differs_in_fid_ang_and_matched"),
         "min_identical_frac": {k: min(r.get(k, 1.0) for r in recs.values()) for k in
                                ("identical_frac_pl", "identical_frac_th", "identical_frac_vz", "identical_frac_MasterAnaDev_minos_trk_p")},
         "A_muonP_sentinel_among_A_selected": s("A_muonP_sentinel_among_A_selected"),
         "files_entries_differ": sorted((k[:-5], r["entries"], r["sel_total"]) for k, r in recs.items() if r["entries"][0] != r["entries"][1]),
         "files_pot_differ": sorted(k[:-5] for k, r in recs.items() if r["pot_used"][0] != r["pot_used"][1]),
         "files_sel_differ": sorted((k[:-5], r["sel_total"]) for k, r in recs.items() if r["sel_total"][0] != r["sel_total"][1])}
    o["sel_rel_change_new_vs_old"] = o["sel_total"][1] / o["sel_total"][0] - 1
    o["sel_per_pot_rel_change"] = (o["sel_total"][1] / o["pot_used"][1]) / (o["sel_total"][0] / o["pot_used"][0]) - 1
    out[kind] = o
# production counts for the emulation check
dfs = ROOT.RDataFrame("mc_signal_reco", prod).Define("p", "(int)sim_pass").Filter("p==1").Count()
dfb = ROOT.RDataFrame("mc_background", prod).Define("p", "(int)sim_background_pass").Filter("p==1").Count()
dfd = ROOT.RDataFrame("data", prod).Count()
f = ROOT.TFile.Open(prod)
out["production_1A"] = {"data_rows": int(dfd.GetValue()), "sig_pass_rows": int(dfs.GetValue()), "bkg_pass_rows": int(dfb.GetValue()),
                        "dataPOTUsed": f.Get("dataPOTUsed").GetVal(), "mcPOTUsed": f.Get("mcPOTUsed").GetVal()}
print(json.dumps(out, indent=1))
