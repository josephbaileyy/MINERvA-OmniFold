"""The floor on EXACTLY the 63 OI-126 tail cells.

COMPARABILITY: the family figure is median RELATIVE SD (0.6712). My earlier floor numbers were
range/mean, which is a DIFFERENT statistic. Both are reported here, and only rel_sd is
comparable to the family's.
"""
import glob
import json

import numpy as np

NPP = 19
REC = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/"
       "p5a-nominal-vs-cstat-family-percell-20260815.json")
PAT = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/"
       "replicas/*/extraction/GATE5_REPLICA_XSEC.npz")
D = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_floor_42_0"

d = json.load(open(REC))
ratio = np.array(d["per_cell_ratio"], float)
X = np.array([np.load(p, allow_pickle=True)["xsec"].ravel(order="C") for p in sorted(glob.glob(PAT))])
idx = np.flatnonzero((X > 0).all(axis=0))
assert idx.size == ratio.size == 257
tail = idx[ratio > 1.5]
assert tail.size == 63

F = []
for n in (2, 3, 4, 5):
    z = np.load(f"{D}/draw_{n}/pet_fullevent_floor_draw{n}_weights.npz", allow_pickle=True)
    F.append(np.asarray(z["central_vector"]))
    z.close()
F = np.array(F)


def stats(cells, label):
    A = F[:, cells]
    mu = A.mean(0)
    rsd = A.std(0, ddof=1) / mu
    rng = (A.max(0) - A.min(0)) / mu
    print(f"  {label:34s} n={len(cells):3d}  median rel_sd {np.median(rsd):.4%}   "
          f"median range/mean {np.median(rng):.4%}")
    return float(np.median(rsd))


print("FLOOR (4 draws, GPU-nondeterminism at fixed seeds) on the OI-126 sets:")
t = stats(tail, "the 63 ratio>1.5 TAIL cells")
live = F.mean(0) > 0
nont = [c for c in np.flatnonzero(live) if c not in set(tail.tolist())]
e = stats(nont, "everywhere else (floor-live)")
stats(list(np.flatnonzero(live)), "all floor-live cells")

print("\nFAMILY (50 replicas), from Joseph's receipt, NOT recomputed here:")
print(f"  median_family_rel_sd_in_tail     {d['the_tail']['median_family_rel_sd_in_tail']:.4%}")
print(f"  median_family_rel_sd_elsewhere   {d['the_tail']['median_family_rel_sd_elsewhere']:.4%}")

print("\nLIKE-FOR-LIKE, median relative sd, same 63 cells:")
print(f"  family (n=50)  {d['the_tail']['median_family_rel_sd_in_tail']:.4%}")
print(f"  floor  (n=4)   {t:.4%}")
print("  RATIO family/floor = "
      f"{d['the_tail']['median_family_rel_sd_in_tail'] / t:.2f}x")
print("\nTRAP 1 STILL APPLIES: n=4 against n=50. An sd from four draws is a noisy estimate; "
      "\nthe direction of any bias is NOT established here and this ratio is indicative only.")
