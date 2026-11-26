#!/usr/bin/env python3
"""regenA amendment A2: per-bin ratios of the 1D projections, ours / published, as compare_to_models.project() makes them.

It reads, and changes nothing. It imports compare_to_models from the clone given by --module-dir (2d-unfolding/ of that
clone) and calls that commit's own flatten_th2d / flatten_ours / project, the way that commit's main() does:
  - 903fb78b (RE-2 part C's deploy; the note's sec3_twod.tex:11 literals): project(vec, mask, axis), with the module's
    PT_EDGES/PZ_EDGES used for both sides;
  - e766ee52 (main after #1318/#1319): project(vec, mask, axis, *edges), with each side's own TH2D axes (th2d_edges).
Output JSON: per-bin ratios for axis pt (14 bins) and pz (16 bins), plus the literal checks of AMENDMENT-A2.txt.
"""
import argparse, importlib, inspect, json, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--module-dir", required=True)
ap.add_argument("--ours", required=True)
ap.add_argument("--paper", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
sys.path.insert(0, a.module_dir); sys.path.insert(1, a.module_dir + "/uq")
import ROOT
cm = importlib.import_module("compare_to_models")
fp = ROOT.TFile.Open(a.paper); h_paper = fp.Get("pt_pl_cross_section")
cov_stat = cm.tmatrix_to_numpy(fp.Get("StatOnlyCovariance")); data_v = cm.flatten_th2d(h_paper)
fo = ROOT.TFile.Open(a.ours); h_ours = fo.Get("hXSec2D"); ours_v = cm.flatten_ours(h_ours)
mask = np.diag(cov_stat) > 0
takes_edges = len(inspect.signature(cm.project).parameters) > 3
out = {"module_file": cm.__file__, "project_takes_edges": takes_edges, "n_reported": int(mask.sum()), "ratios": {}}
for axis in ("pt", "pz"):
    if takes_edges:
        ours_edges, paper_edges = cm.th2d_edges(h_ours), cm.th2d_edges(h_paper)
        _, y_o = cm.project(ours_v[mask], mask, axis, *ours_edges); _, y_d = cm.project(data_v[mask], mask, axis, *paper_edges)
    else:
        _, y_o = cm.project(ours_v[mask], mask, axis); _, y_d = cm.project(data_v[mask], mask, axis)
    r = np.where(y_d != 0, y_o / np.where(y_d != 0, y_d, 1), np.nan)
    out["ratios"][axis] = [float(x) for x in r]
pt, pz = np.array(out["ratios"]["pt"]), np.array(out["ratios"]["pz"])
interior = np.concatenate([pt[1:-1], pz[:-2]])
out["literals"] = {
    "pt_lowest_2dp": round(float(pt[0]), 2), "pt_highest_2dp": round(float(pt[-1]), 2),
    "pz_second_highest_2dp": round(float(pz[-2]), 2), "pz_highest_2dp": round(float(pz[-1]), 2),
    "max_abs_dev_other_bins": float(np.nanmax(np.abs(interior - 1))),
    "max_abs_dev_other_bins_pct_int": int(round(100 * float(np.nanmax(np.abs(interior - 1))))),
}
L = out["literals"]
out["note_literals_reproduced"] = {
    "0.97 lowest pT": L["pt_lowest_2dp"] == 0.97, "1.04 highest pT": L["pt_highest_2dp"] == 1.04,
    "1.06 and 0.93 in the two highest p||": sorted([L["pz_second_highest_2dp"], L["pz_highest_2dp"]]) == [0.93, 1.06],
    "within 2% elsewhere": L["max_abs_dev_other_bins_pct_int"] <= 2,
}
json.dump(out, open(a.out, "w"), indent=1); print(json.dumps({"literals": L, "reproduced": out["note_literals_reproduced"]}, indent=1))
