#!/usr/bin/env python3
"""Report the raw/clipped diagonal pair and the trace anchor out of a stamped product.

Exists so arm 4's REQUIRED behaviour -- a negative raw entry that stays ZERO in the clipped histogram
-- is read off the artifact rather than inferred from the gate passing.
"""
import argparse
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--member", required=True)
ap.add_argument("--bin", type=int, default=None)
a = ap.parse_args()
import ROOT
ROOT.gErrorIgnoreLevel = ROOT.kError
f = ROOT.TFile.Open(a.member)
out = {}
for name in ("hDiagCombinedOld", "hDiagCombinedOldRaw"):
    h = f.Get(name)
    if not h:
        print(f"[diag] {name}: ABSENT")
        continue
    n = h.GetNbinsX()
    arr = np.array([h.GetBinContent(i + 1) for i in range(n)], dtype=np.float64)
    out[name] = arr
    print(f"[diag] {name}: {n} bins  min={arr.min()!r}  negatives={int((arr < 0).sum())}  "
          f"sum={float(np.sum(arr))!r}")
for k in ("sqrt_tr_old", "sqrt_tr_new"):
    o = f.Get(k)
    print(f"[diag] {k} = {o.GetVal()!r}" if o else f"[diag] {k}: ABSENT")
if "hDiagCombinedOldRaw" in out:
    raw = out["hDiagCombinedOldRaw"]
    o = f.Get("sqrt_tr_old")
    if o:
        rec = float(np.sqrt(max(float(np.sum(raw)), 0.0)))
        st = float(o.GetVal())
        print(f"[diag] sqrt(sum(raw)) = {rec!r}")
        print(f"[diag] stamped        = {st!r}")
        print(f"[diag] BIT-EQUAL      = {rec == st}   (the gate compares at rtol=0.0)")
if a.bin is not None:
    for name, arr in out.items():
        print(f"[diag] {name}[{a.bin}] = {arr[a.bin]!r}")
f.Close()
