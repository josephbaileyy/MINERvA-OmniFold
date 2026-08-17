#!/usr/bin/env python3
"""UNPREDECLARED EXTENSION, reported as a MEASUREMENT and not as a gate result.

The rebuilt 5D candidate carries hRowIndex5D (49 keys vs the 47 the Aug-10 audits saw). It exists only
because the authorized stages-4-6 run made this a "FUTURE build" in the sense of
p4_build_components.py:213-215. It has never been verified. Same instrument as the 4D readback, same
independent derivation (nonzero of the 5D central support -- grid shape only, no widths, no p4_lib).

READ-ONLY: the 39.4 GiB file is opened READ and only two keys are touched; no digest of it is taken
before/after because a 2x40 GB hash is not free -- so this leg does NOT prove read-onlyness the way the
4D check did, and says so rather than implying otherwise.
"""
import hashlib
import numpy as np
import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kFatal
BASE = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
CAND = f"{BASE}/active_universe_5d/standard/candidate/std_final5_candidate.root"
CEN5 = (f"{BASE}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root", "hXSecND_flat")
NB5 = 65856


def th1(path, key):
    f = ROOT.TFile.Open(path, "READ")
    h = f.Get(key)
    n = int(h.GetNbinsX())
    a = np.array([h.GetBinContent(i + 1) for i in range(n)], dtype=np.float64)
    f.Close()
    return a


print("reading hRowIndex5D out of the closed 5D candidate...")
f = ROOT.TFile.Open(CAND, "READ")
h = f.Get("hRowIndex5D")
if not h:
    raise SystemExit("hRowIndex5D absent")
n = int(h.GetNbinsX())
raw = np.array([h.GetBinContent(i + 1) for i in range(n)], dtype=np.float64)
cov = f.Get("hCov_stdcombined5d_total_candidate")
cn = int(cov.GetNbinsX())
f.Close()
idx = raw.astype(np.int64)

x5 = th1(*CEN5)
m5 = x5 > 0
eff5 = np.nonzero(m5)[0].astype(np.int64)

print(f"  hRowIndex5D bins      = {n}")
print(f"  covariance dimension  = {cn}")
print(f"  independent nonzero(m5) size = {eff5.size}   (5D grid {x5.size} == {NB5}: {x5.size == NB5})")
print(f"  integral contents     = {bool(np.all(raw == np.floor(raw)))}")
print(f"  strictly increasing   = {bool(np.all(np.diff(idx) > 0))}")
print(f"  range                 = [{int(idx.min())}, {int(idx.max())}] < {NB5}")
agree = (idx.size == eff5.size) and bool(np.array_equal(idx, eff5))
print(f"  EQUALS independently derived 5D index set : {agree}")
if not agree and idx.size == eff5.size:
    d = int(np.count_nonzero(idx != eff5))
    first = int(np.nonzero(idx != eff5)[0][0])
    print(f"    {d} of {idx.size} differ; first row {first}: stored {int(idx[first])} vs {int(eff5[first])}")
print(f"  sha256 of read-back int64 array = "
      f"{hashlib.sha256(np.ascontiguousarray(idx).tobytes()).hexdigest()}")
mut = idx.copy(); mut[7] += 1
print(f"  MUTATION CONTROL (row 7 {int(idx[7])} -> {int(mut[7])}) fires: "
      f"{not np.array_equal(mut, eff5)}")
