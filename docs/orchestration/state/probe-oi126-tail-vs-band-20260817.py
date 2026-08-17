"""Do the 63 ratio>1.5 tail cells lie in p_parallel 6-20 GeV?

(a) 63 of 63 in bins 10-15  -> the determination's spatial description picks the same set
(b) fewer                    -> a tail count and a band count are two different 63s

The receipt publishes per_cell_ratio as a 257-list over `compared_all_members_positive`, and
does NOT publish the index->grid mapping. Reconstructed here as (X>0).all(axis=0) over the 50
replicas and VERIFIED against the receipt's own 257 before it is used for anything.
"""
import glob
import json

import numpy as np

NPP = 19
REC = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/"
       "p5a-nominal-vs-cstat-family-percell-20260815.json")
PAT = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/"
       "replicas/*/extraction/GATE5_REPLICA_XSEC.npz")

d = json.load(open(REC))
ratio = np.array(d["per_cell_ratio"], float)
claim = int(d["domain"]["compared_all_members_positive"])
print(f"receipt: per_cell_ratio len={ratio.size}  compared_all_members_positive={claim}")

f = sorted(glob.glob(PAT))
X = np.array([np.load(p, allow_pickle=True)["xsec"].ravel(order="C") for p in f])
print(f"replicas stacked: {X.shape}")

allpos = (X > 0).all(axis=0)
print(f"(X>0).all(axis=0) -> {int(allpos.sum())} cells   receipt says {claim}   "
      f"MATCH={int(allpos.sum()) == claim == ratio.size}")
if not (int(allpos.sum()) == claim == ratio.size):
    raise SystemExit("mapping NOT reconstructed; refusing to place the tail cells")

idx = np.flatnonzero(allpos)                 # array position k -> grid cell idx[k]
tail = idx[ratio > 1.5]
print(f"\ntail cells (ratio>1.5): {tail.size}   receipt says {d['the_tail']['n_cells_ratio_gt_1p5']}")

col = tail % NPP
inband = int(((col >= 10) & (col <= 15)).sum())
print(f"\n=== THE (a)/(b) CHECK ===")
print(f"  tail cells in p|| 6-20 (bins 10-15): {inband} of {tail.size}")
for lo, hi, lab in ((0, 9, "p||<6   bins 0-9"), (10, 15, "6-20    bins 10-15"),
                    (16, 18, ">20     bins 16-18")):
    n = int(((col >= lo) & (col <= hi)).sum())
    print(f"    {lab:20s} {n:3d}")
print(f"  distinct p|| bins occupied by the tail: {sorted(set(col.tolist()))}")
print(f"  distinct pT rows occupied by the tail : {sorted(set((tail // NPP).tolist()))}")

# step-3 discipline: how many survive the floor draws' mask, BEFORE any statistic
D = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_floor_42_0"
F = []
for n in (2, 3, 4, 5):
    z = np.load(f"{D}/draw_{n}/pet_fullevent_floor_draw{n}_weights.npz", allow_pickle=True)
    F.append(np.asarray(z["central_vector"]))
    z.close()
F = np.array(F)
flive = F.mean(0) > 0
surv = [c for c in tail if flive[c]]
print(f"\n=== STEP-3 DISCIPLINE: intersection reported BEFORE any statistic ===")
print(f"  floor draws live cells      : {int(flive.sum())}")
print(f"  tail cells live on the floor: {len(surv)} of {tail.size}  "
      f"(dropped {tail.size - len(surv)})")
