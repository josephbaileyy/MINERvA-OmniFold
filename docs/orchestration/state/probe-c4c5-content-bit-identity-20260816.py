#!/usr/bin/env python3
"""READ-ONLY. Do the REBUILT covariance objects have the same CONTENT as the ones the 2026-08-10
cross-object audit judged? If yes, that audit's `identity_verdict = ESTABLISHED` transfers to the
current products with zero compute and no new check is needed.

Convention and helpers replicated from 20260810T0630Z-cross-object-script.py:
  open READ (reject kRecovered) -> reshape(ny+2, nx+2) -> core = [1:-1,1:-1] float64 C-order
  -> sha256 over the raw bytes.
Writes nothing.
"""
import hashlib
import numpy as np
import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kFatal
BASE = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/candidate"

TARGETS = [
    ("C5 total", f"{BASE}/std_final5_candidate.root", "hCov_stdcombined5d_total_candidate",
     "f26b3bfeaaa2dce14a8c39e22795b85facb93d89e78b2c312fe28c3ba38dded4"),
    ("C4 stored", f"{BASE}/std_proj4d_candidate.root", "hCov_std_proj4d_candidate",
     "c1fe11b17e3c3819b3e3f4b089301dddf7871c7790b914dccc303f4914756cbf"),
]


def array_sha256(a):
    return hashlib.sha256(memoryview(np.ascontiguousarray(a)).cast("B")).hexdigest()


def open_root(path):
    f = ROOT.TFile.Open(str(path), "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open ROOT file: {path}")
    if f.TestBit(ROOT.TFile.kRecovered):
        f.Close()
        raise RuntimeError(f"ROOT file is marked recovered: {path}")
    return f


def root_buffer(h, dtype, count):
    try:
        return np.frombuffer(h.GetArray(), dtype=dtype, count=count)
    except Exception:
        view = h.GetArray()
        try:
            view.reshape((count,))
        except TypeError:
            view.reshape(count)
        arr = np.asarray(view, dtype=dtype)
        if arr.size < count:
            raise RuntimeError(f"ROOT buffer exposes {arr.size} cells; expected {count}")
        return arr[:count]


def th2_core(path, key):
    f = open_root(path)
    h = f.Get(key)
    if not h:
        f.Close()
        raise RuntimeError(f"missing {path}:{key}")
    dtype = np.float64 if h.InheritsFrom("TH2D") else np.float32
    nx, ny = int(h.GetNbinsX()), int(h.GetNbinsY())
    raw = root_buffer(h, dtype, (nx + 2) * (ny + 2))
    storage = raw.reshape(ny + 2, nx + 2)
    core = np.array(storage[1:-1, 1:-1], dtype=np.float64, order="C", copy=True)
    cls = h.ClassName()
    f.Close()
    return core, nx, ny, cls


ok = True
for label, path, key, expected in TARGETS:
    core, nx, ny, cls = th2_core(path, key)
    got = array_sha256(core)
    match = (got == expected)
    ok = ok and match
    print(f"{label:10s} {cls} {nx}x{ny}")
    print(f"           content sha256 now = {got}")
    print(f"           audited 2026-08-10 = {expected}")
    print(f"           {'MATCH -- content unchanged' if match else '*** DIFFERS -- content changed ***'}")
    print(f"           trace={float(np.trace(core)):.10e}  max|.|={float(np.max(np.abs(core))):.10e}")
    print()

print("VERDICT:", "BOTH CONTENTS UNCHANGED -- the 2026-08-10 ESTABLISHED identity transfers"
      if ok else "CONTENT CHANGED -- the prior verdict does NOT transfer; a re-run is warranted")
