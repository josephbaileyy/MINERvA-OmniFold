#!/usr/bin/env python3
"""P1 entry-to-row mapping control on a synthetic mc_background tree (login node, seconds).

  python test_rows_mapping.py --d2 D2 --report REPORT.json

On the CV omnifile every mc_background entry passes and is filled (658,227 rows = 658,227 entries), so a
refill indexed by row position instead of tree entry would be invisible there. This builds a 12-entry tree
with rejected entries (sim_background_pass = 0, non-finite and out-of-range weights) and out-of-grid rows,
and checks: the recorded entries are exactly the filled ones; B* from p1_refill_bkg_2d equals a by-hand sum
of b[entry] * w * pot per cell; a row-position refill (the wrong mapping) gives a different B*.
"""
import argparse
import importlib.util
import json
import os
import sys
from array import array

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d2", required=True)
    ap.add_argument("--report", required=True)
    a = ap.parse_args()
    import ROOT
    ROOT.gROOT.SetBatch(True)
    spec = importlib.util.spec_from_file_location("driver_p1", os.path.join(a.d2, "driver_p1.py"))
    drv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drv)
    #            pt,    pz,  pass, w
    rows = [(0.10, 3.2, 1, 1.0), (0.20, 3.3, 0, 2.0), (0.30, 4.1, 1, 3.0), (5.00, 4.2, 1, 4.0),
            (0.10, 3.2, 1, float("nan")), (0.60, 7.5, 1, 5.0), (0.10, 3.2, 1, 2e6), (0.31, 4.15, 1, 6.0),
            (0.10, 70.0, 1, 7.0), (0.20, 3.3, 0, 8.0), (0.12, 3.25, 1, 9.0), (0.65, 7.6, 1, 10.0)]
    t = ROOT.TTree("mc_background", "synthetic")
    pt, pz, ps, w = array("d", [0.]), array("d", [0.]), array("B", [0]), array("d", [0.])
    t.Branch("sim_background", pt, "sim_background/D")
    t.Branch("sim_background_pz", pz, "sim_background_pz/D")
    t.Branch("sim_background_pass", ps, "sim_background_pass/b")
    t.Branch("w_bkg", w, "w_bkg/D")
    for r in rows:
        pt[0], pz[0], ps[0], w[0] = r
        t.Fill()
    pot = 0.5
    h = drv.make_th2d("hB", "B", drv.PT_EDGES, drv.PZ_EDGES)
    *_, rec = drv.fill_bkg_reco_2d(t, h, pot, pt_lo=drv.PT_EDGES[0], pt_hi=drv.PT_EDGES[-1],
                                   pz_lo=drv.PZ_EDGES[0], pz_hi=drv.PZ_EDGES[-1], return_fill_rows=True)
    want_entries = [0, 2, 3, 5, 7, 8, 10, 11]
    b = np.array([2., 5., 0., 3., 7., 1., 4., 2., 6., 9., 1., 3.])
    hs = drv.p1_refill_bkg_2d("hBs", "B*", rec, b, drv.PT_EDGES, drv.PZ_EDGES)
    by_hand = drv.make_th2d("hBh", "B* by hand", drv.PT_EDGES, drv.PZ_EDGES)
    for e in want_entries:
        by_hand.Fill(rows[e][0], rows[e][1], b[e] * (rows[e][3] * pot))
    wrong = drv.make_th2d("hBw", "row-position refill", drv.PT_EDGES, drv.PZ_EDGES)
    for k, (x, y, wp) in enumerate(zip(rec["pt"], rec["pz"], rec["w_pot"])):
        wrong.Fill(float(x), float(y), b[k] * float(wp))
    n = h.GetNcells()
    arr = lambda hh: np.array([hh.GetBinContent(i) for i in range(n)])
    rep = {"recorded_entries": rec["entry"].tolist(), "want_entries": want_entries,
           "entries_ok": rec["entry"].tolist() == want_entries,
           "w_pot_ok": rec["w_pot"].tolist() == [rows[e][3] * pot for e in want_entries],
           "refill_equals_by_hand": bool(np.array_equal(arr(hs), arr(by_hand))),
           "row_position_refill_differs": bool(not np.array_equal(arr(wrong), arr(by_hand))),
           "refill_b1_equals_fill": bool(np.array_equal(
               arr(drv.p1_refill_bkg_2d("h1", "b1", rec, np.ones(len(rows)), drv.PT_EDGES, drv.PZ_EDGES)), arr(h))),
           "n_out_of_grid_rows": int(sum(1 for e in want_entries if rows[e][0] >= drv.PT_EDGES[-1]
                                         or rows[e][1] >= drv.PZ_EDGES[-1]))}
    rep["PASS"] = all(rep[k] for k in ("entries_ok", "w_pot_ok", "refill_equals_by_hand",
                                       "row_position_refill_differs", "refill_b1_equals_fill"))
    with open(a.report, "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
    print(json.dumps(rep, indent=1))
    return 0 if rep["PASS"] else 2


if __name__ == "__main__":
    sys.exit(main())
