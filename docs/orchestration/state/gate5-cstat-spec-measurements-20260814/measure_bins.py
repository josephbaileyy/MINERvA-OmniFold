"""Measure the ACTUAL covaried object: shape, binning, units, and how many bins carry signal.

The spec's rank clause turns on this number and nothing else, so it is measured off a real
completed replica artifact rather than quoted from AGENTS.md's paper edges.
"""
import glob, json, os
import numpy as np

ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas"
xs = sorted(glob.glob(os.path.join(ROOT, "replica_*/extraction/*.npz")))
print(f"npz files found: {len(xs)}")
for p in xs[:6]:
    print("  ", p.replace(ROOT, "..."), os.path.getsize(p))

# pick the xsec (not push) artifacts
xsecs = [p for p in xs if "push" not in os.path.basename(p).lower()]
print(f"\nnon-push candidates: {len(xsecs)}")
if not xsecs:
    raise SystemExit("no xsec artifact yet")

p = xsecs[0]
print(f"\n=== reading {p} ===")
with np.load(p, allow_pickle=True) as z:
    print("keys:", sorted(z.files))
    x = np.asarray(z["xsec"], float)
    e0 = np.asarray(z["edges_pt"], float)
    e1 = np.asarray(z["edges_pparallel"], float)
    print(f"\nxsec.shape      = {x.shape}   dtype={x.dtype}")
    print(f"xsec.size       = {x.size}   <-- THE DIMENSION C_stat WOULD HAVE")
    print(f"edges_pt        n={e0.size} -> {e0.size-1} bins: {e0.tolist()}")
    print(f"edges_pparallel n={e1.size} -> {e1.size-1} bins: {e1.tolist()}")
    print(f"product of bins = {(e0.size-1)*(e1.size-1)}")
    print(f"\ntotal_sigma     = {float(np.asarray(z['total_sigma_cm2_per_nucleon'])):.6e}")
    print(f"replica_index   = {int(np.asarray(z['replica_index']))}")
    print(f"bootstrap_seed  = {int(np.asarray(z['bootstrap_seed']))}")
    print(f"xsec_schema     = {str(np.asarray(z['xsec_schema']))}")
    nz = int(np.count_nonzero(x))
    print(f"\nnonzero bins    = {nz} of {x.size}   ({100.0*nz/x.size:.1f}%)")
    print(f"exactly-zero    = {x.size - nz}  <-- zero-variance directions if zero in EVERY replica")
    print(f"finite          = {int(np.isfinite(x).sum())} of {x.size}")
    print(f"min/max nonzero = {x[x>0].min():.6e} / {x.max():.6e}")
    tel = z["extraction_telemetry"].item()
    print(f"\ntelemetry keys: {sorted(tel)[:40]}")
    for k in sorted(tel):
        if any(s in k.lower() for s in ("mask","report","bin","unit","nucleon","flux","complete")):
            v = tel[k]
            print(f"  {k} = {str(v)[:160]}")
