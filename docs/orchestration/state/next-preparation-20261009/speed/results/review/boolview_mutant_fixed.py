"""Reviewer probe: does removing the bool->uint8 view change the columnar prototype's output?"""
import os, sys, types
import numpy as np
Q = sys.argv[1]; tree_path = sys.argv[2]
sys.path.append(os.path.join(Q, "bench"))
import pinned
import ROOT
DRV = pinned.load_driver(); BS = pinned.load_proto("branch_status"); VL = pinned.load_proto("vector_loader")
LO_HI = (DRV.PT_EDGES[0], DRV.PT_EDGES[-1], DRV.PZ_EDGES[0], DRV.PZ_EDGES[-1]); POT = 0.212405
KEYS = ("truth_pt", "truth_pz", "reco_pt", "reco_pz", "pass_reco", "pass_truth", "w_truth", "w_reco")
src = open(VL.__file__).read()
old = "        raw = raw.view(np.uint8)\n"; assert src.count(old) == 1
mod = types.ModuleType("vl_noview"); exec(compile(src.replace(old, "        pass\n"), "vl_noview", "exec"), mod.__dict__)
f = ROOT.TFile.Open(tree_path); t = f.Get("mc_signal_reco")
ref = DRV.collect_signal_arrays_2d(t, *LO_HI, POT, use_weights=True)
f.Close()
f = ROOT.TFile.Open(tree_path); t = f.Get("mc_signal_reco")
names = BS.signal_branches(True, None, t)
got = mod.collect_signal_arrays_columnar(t, (*names[:4], names[5], names[6]), *LO_HI, POT, use_weights=True)
print('branch tuple passed', (*names[:4], names[5], names[6]), ' (cycle-0 probe passed', tuple(names[:6]), ')')
f.Close(); f = ROOT.TFile.Open(tree_path); t = f.Get('mc_signal_reco')
good = VL.collect_signal_arrays_columnar(t, (*names[:4], names[5], names[6]), *LO_HI, POT, use_weights=True)
print('keys differing for UNMUTATED prototype (control):', [k for k in KEYS if ref[k].tobytes() != good[k].tobytes()])
f.Close(); f = ROOT.TFile.Open(tree_path); t = f.Get("mc_signal_reco")
raw = np.asarray(ROOT.RDataFrame(t).AsNumpy(["sim_pass"])["sim_pass"])
print("AsNumpy sim_pass dtype", raw.dtype, "byte==2 rows", int((raw.view(np.uint8) == 2).sum()))
print("keys differing WITHOUT the view:", [k for k in KEYS if ref[k].tobytes() != got[k].tobytes() or ref[k].dtype != got[k].dtype])
