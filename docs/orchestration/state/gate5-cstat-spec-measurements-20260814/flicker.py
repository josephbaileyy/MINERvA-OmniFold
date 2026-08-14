"""Is the reporting mask ACTUALLY replica-dependent, or only potentially so?

D confirmed the mechanism by reading extract_fullevent_replica.py:190-196 and
extract_fullevent_fps.py:517-518 and was explicit it had not measured an occurrence.
The 14 published members are enough to measure it, and to bound the per-cell flip rate.
"""
import glob, os
import numpy as np

ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas"
NOM = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/"
       "fullevent_diagnostic_nonquotable/NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.npz")
paths = sorted(glob.glob(os.path.join(ROOT, "replica_*/extraction/GATE5_REPLICA_XSEC.npz")))

X, tel_pop = [], []
for p in paths:
    with np.load(p, allow_pickle=True) as z:
        X.append(np.asarray(z["xsec"], float).ravel(order="C"))
        tel_pop.append(int(z["extraction_telemetry"].item()["n_cells_populated"]))
F = np.stack(X); N, D = F.shape
print(f"members {N}  cells {D}")

rep = F != 0.0                      # hard-zeroed unreported cells => nonzero == reported
n_rep = rep.sum(axis=0)             # per-cell count of replicas reporting it
print(f"\n--- per-cell n_replicas_reported over the {N} published members ---")
for k in sorted(set(n_rep.tolist())):
    print(f"  n_reported == {k:2d} : {int((n_rep==k).sum()):3d} cells")

flick = int(((n_rep > 0) & (n_rep < N)).sum())
print(f"\n*** cells reported in SOME but not ALL members: {flick} ***")
print(f"    reported in ALL {N}   : {int((n_rep==N).sum())}")
print(f"    reported in NONE      : {int((n_rep==0).sum())}")
print(f"    => mask flicker {'OCCURS' if flick else 'has NOT occurred in these members'}")

print(f"\n--- telemetry n_cells_populated per member (should equal reported count) ---")
print(f"  distinct values: {sorted(set(tel_pop))}")
print(f"  matches per-member nonzero count: "
      f"{[int(r.sum()) for r in rep] == tel_pop}")

print(f"\n--- union vs intersection, the two candidate domains ---")
union = int((n_rep > 0).sum()); inter = int((n_rep == N).sum())
print(f"  UNION        (reported in >=1) : {union} cells")
print(f"  INTERSECTION (reported in all) : {inter} cells")
print(f"  cells the intersection would discard: {union-inter}")
print(f"  rank ceiling at N=50 is 49, so against EITHER domain:")
for name, d in (("union", union), ("intersection", inter)):
    print(f"    {name:12s} D={d:3d}  D/49 = {d/49:.2f}x  singular={d>49}")

print(f"\n--- the reported-cell count D was asked to measure, incl. the nominal ---")
with np.load(NOM, allow_pickle=True) as z:
    nom = np.asarray(z["xsec"], float).ravel(order="C")
    ntel = z["extraction_telemetry"].item()
print(f"  nominal (NONQUOTABLE-DIAGNOSTIC) reported cells : {int((nom!=0).sum())}")
print(f"  nominal telemetry n_cells_populated             : {ntel.get('n_cells_populated')}")
print(f"  nominal n_cells_masked_zero_acceptance          : {ntel.get('n_cells_masked_zero_acceptance')}")
print(f"  nominal n_cells_no_denominator                  : {ntel.get('n_cells_no_denominator')}")
print(f"  nominal reported set == every replica's?        : "
      f"{all(np.array_equal(nom!=0, r) for r in rep)}")
