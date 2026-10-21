#!/usr/bin/env python3
"""Bin-content (incl. under/overflow) bitwise comparison of named TH1/TH2 objects in two ROOT files."""
import json, sys
import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)
a, b, names = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
fa, fb = ROOT.TFile.Open(a), ROOT.TFile.Open(b)
res = {}
def arr(h):
    n = h.GetNcells()
    return np.array([h.GetBinContent(i) for i in range(n)]), np.array([h.GetBinError(i) for i in range(n)])
for n in names:
    ha, hb = fa.Get(n), fb.Get(n)
    if not ha or not hb:
        res[n] = {"missing": [bool(ha), bool(hb)]}; continue
    (ca, ea), (cb, eb) = arr(ha), arr(hb)
    res[n] = {"contents_bitwise": bool(ca.shape == cb.shape and np.array_equal(ca, cb)),
              "errors_bitwise": bool(ea.shape == eb.shape and np.array_equal(ea, eb)),
              "max_abs_diff": float(np.max(np.abs(ca - cb))) if ca.shape == cb.shape else None}
print(json.dumps(res, indent=1))
sys.exit(0 if all(v.get("contents_bitwise") for v in res.values()) else 1)
