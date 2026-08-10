#!/usr/bin/env python3
"""Is the ~4.4% marginalisation difference a LADDER or a coincidence of two points?

Measured:  5D->4D (drop W)      median |rel| = 4.43%   [this lane, 2026-08-09]
Quoted:    3D->2D (drop eavail) ~4.4% per-bin scatter  [sec_3d.tex:81]
Missing:   4D->3D (drop q3)     <- this script, from products that ALREADY EXIST

Two points could be coincidence. Three rungs at the same magnitude would make it a measured,
roughly dimension-independent property of marginalising an unfolded distribution rather than
something peculiar to the fifth axis.

Read-only. No production. Every input is a frozen central product already on disk.
"""
import os, sys, hashlib
import numpy as np
sys.path.insert(0, "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding")
os.chdir("/pscratch/sd/j/josephrb/MINERvA-OmniFold")
import ROOT
from p4_project_4d import canonical_edges

E = canonical_edges()                      # pt, pz, eavail, q3, W
NB = [len(np.asarray(e)) - 1 for e in E]

FILES = {
    "5d": "nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root",
    "4d": "nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root",
    "3d": "3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root",
}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def flat(path, key="hXSecND_flat"):
    f = ROOT.TFile.Open(path)
    h = f.Get(key)
    if not h:
        f.Close(); raise SystemExit(f"missing {key} in {path}")
    v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]); f.Close(); return v


for k, p in FILES.items():
    print(f"INPUT {k}: {p}  size={os.path.getsize(p)}  sha256={sha(p)}")

def th3_flat(path, key="hXSec3D"):
    """The 3D product stores a TH3D, not hXSecND_flat. Flatten to C order (pt, pz, eavail) to
    match the ND convention used by the 4D/5D products."""
    f = ROOT.TFile.Open(path)
    h = f.Get(key)
    if not h:
        f.Close(); raise SystemExit(f"missing {key} in {path}")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    a = np.empty((nx, ny, nz), dtype=float)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                a[i, j, k] = h.GetBinContent(i + 1, j + 1, k + 1)
    f.Close()
    print(f"  (TH3D {key} axes = {nx} x {ny} x {nz})")
    return a.ravel()

x = {}
for k, pth in FILES.items():
    x[k] = th3_flat(pth) if k == "3d" else flat(pth)
for k, v in x.items():
    print(f"  {k}: len={v.size} nonzero={(v>0).sum()} sum={v.sum():.6e}")


def rung(hi_key, lo_key, hi_dims, drop_axis, label):
    """Width-weighted marginalisation of `drop_axis` from the higher-dim central, compared to the
    independently unfolded lower-dim central on the lower-dim reported support."""
    hi, lo = x[hi_key], x[lo_key]
    grid = hi.reshape(hi_dims)
    w = np.diff(np.asarray(E[drop_axis], float))
    shape = [1] * len(hi_dims); shape[drop_axis] = w.size
    marg = (grid * w.reshape(shape)).sum(axis=drop_axis).ravel()
    m = lo > 0
    if marg.size != lo.size:
        print(f"\n{label}: SHAPE MISMATCH marg={marg.size} lo={lo.size} -- skipped")
        return
    live = (marg != 0.0) & m
    rel = np.abs(marg[live] - lo[live]) / np.abs(lo[live])
    print(f"\n=== {label} ===")
    print(f"  lower-dim reported bins {int(m.sum())}; comparable (marg nonzero) {int(live.sum())}; "
          f"unreachable {int((m & (marg == 0)).sum())}")
    print(f"  median |rel| = {np.median(rel):.4%}")
    print(f"  p90 = {np.percentile(rel,90):.4%}   p99 = {np.percentile(rel,99):.4%}   "
          f"max = {rel.max():.4%}")
    print(f"  integral ratio = {marg[live].sum()/lo[live].sum():.6f}")
    return float(np.median(rel))


r54 = rung("5d", "4d", NB, 4, "5D -> 4D  (drop W)")
r43 = rung("4d", "3d", NB[:4], 3, "4D -> 3D  (drop q3)")

print("\n" + "=" * 66)
print("LADDER")
print("=" * 66)
print(f"  5D -> 4D (drop W)      median |rel| = {r54:.4%}" if r54 else "  5D->4D n/a")
print(f"  4D -> 3D (drop q3)     median |rel| = {r43:.4%}" if r43 else "  4D->3D n/a")
print(f"  3D -> 2D (drop eavail) ~4.4%   [quoted at sec_3d.tex:81, not recomputed here]")
