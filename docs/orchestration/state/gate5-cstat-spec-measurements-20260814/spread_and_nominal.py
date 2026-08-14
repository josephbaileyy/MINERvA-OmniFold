"""Two questions the spec cannot be written without.

(1) Is an 18% total-xsec spread across statistical replicas credible, or is it an outlier /
    a sign the replica variance is dominated by NN training stochasticity rather than counting?
(2) Does a nominal extraction exist to centre on? Centring is a REAL choice only if it does.
"""
import glob, json, os
import numpy as np

ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas"
paths = sorted(glob.glob(os.path.join(ROOT, "replica_*/extraction/GATE5_REPLICA_XSEC.npz")))
tots, idx = [], []
for p in paths:
    with np.load(p, allow_pickle=True) as z:
        tots.append(float(np.asarray(z["total_sigma_cm2_per_nucleon"])))
        idx.append(int(np.asarray(z["replica_index"])))
t = np.array(tots)
print("=== (1) total_sigma per member, sorted by replica_index ===")
for i, v in sorted(zip(idx, tots)):
    print(f"  replica_{i:02d}  {v:.6e}   dev from mean {100*(v-t.mean())/t.mean():+7.3f}%")
print(f"\n  mean {t.mean():.6e}  sd(ddof=1) {t.std(ddof=1):.6e}")
print(f"  relative sd            = {100*t.std(ddof=1)/t.mean():.3f}%")
print(f"  (max-min)/mean         = {100*(t.max()-t.min())/t.mean():.3f}%")
print(f"  median abs dev / mean  = {100*np.median(np.abs(t-np.median(t)))/t.mean():.3f}%")
print("\n  scale references:")
print(f"    Poisson on n_data=4116128 -> {100/np.sqrt(4116128):.4f}%")
print(f"    Poisson on n_sig =49152885 -> {100/np.sqrt(49152885):.4f}%")
print("  => a counting-only spread would be ~0.05%; anything ~10% is NOT counting statistics.")

print("\n=== (2) hunt for a nominal (non-replica) extraction to centre on ===")
pats = [
 "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/**/*XSEC*.npz",
 "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/**/*xsec*.npz",
 "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/**/*xsec*.npz",
]
seen = set()
for pat in pats:
    for h in glob.glob(pat, recursive=True):
        if "fullevent_cstat_n50" in h or h in seen:
            continue
        seen.add(h)
print(f"  candidates outside the replica family: {len(seen)}")
for h in sorted(seen)[:25]:
    try:
        with np.load(h, allow_pickle=True) as z:
            keys = set(z.files)
            shp = np.asarray(z["xsec"]).shape if "xsec" in keys else None
            tot = float(np.asarray(z["total_sigma_cm2_per_nucleon"])) if "total_sigma_cm2_per_nucleon" in keys else None
            sch = str(np.asarray(z["xsec_schema"])) if "xsec_schema" in keys else "-"
        print(f"    {h}")
        print(f"      shape={shp} total={tot if tot is None else f'{tot:.6e}'} schema={sch}")
    except Exception as e:
        print(f"    {h}  [unreadable: {type(e).__name__}]")
