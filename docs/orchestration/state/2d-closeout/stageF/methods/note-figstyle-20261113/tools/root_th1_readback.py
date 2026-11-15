#!/usr/bin/env python3
"""Read every TH1 in a ROOT file into an .npz (note figure style, group C family 5; for the eavailW_band numerical check).

usage: python3 root_th1_readback.py <file.root> <out.npz>
Each TH1 key K becomes K__edges (the low edges and the last upper edge) and K__contents (bin contents 1..N), in double
precision as ROOT stores them. Run where PyROOT is available (the cluster); the comparison runs elsewhere from the npz."""
import sys
import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)
f = ROOT.TFile.Open(sys.argv[1])
out = {}
for key in f.GetListOfKeys():
    obj = key.ReadObj()
    if not obj.InheritsFrom("TH1") or obj.InheritsFrom("TH2"):
        continue
    n = obj.GetNbinsX(); ax = obj.GetXaxis()
    out[f"{key.GetName()}__edges"] = np.array([ax.GetBinLowEdge(i + 1) for i in range(n)] + [ax.GetBinUpEdge(n)])
    out[f"{key.GetName()}__contents"] = np.array([obj.GetBinContent(i + 1) for i in range(n)])
f.Close()
np.savez(sys.argv[2], **out)
print(f"[readback] {len(out) // 2} TH1 from {sys.argv[1]} -> {sys.argv[2]}: {sorted(k[:-10] for k in out if k.endswith('__contents'))}")
