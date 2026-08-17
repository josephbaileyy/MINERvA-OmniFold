"""OI-126 Q3 TEST 1 (scalar): is there a one-signed gap between refine(E[w]) and E[refine(w)]?

PREDECLARED BEFORE RUNNING ALL 50, and derivable rather than guessed:

Stay-Positive is a projection onto the non-negative cone. `max(0, .)` is CONVEX, so Jensen
gives  E[refine(w)] >= refine(E[w])  --  i.e.

    PREDICTION:  mean_i sum(replica_target_i)  >=  sum(nominal_target),  a POSITIVE gap.

A zero gap refutes (c) at the total level. A NEGATIVE gap would refute the convexity argument
itself and would be the more interesting outcome, so it is recorded as reachable rather than
treated as impossible.

SIGN AND MAGNITUDE ARE REPORTED SEPARATELY per the dispatch: the sign is the Jensen signature
and is the claim; the magnitude is a different claim and is not the signature.

Read-only. 51 arrays, one pass each, mmap'd. No unfolding, no training, no GPU, nothing
written inside the promoted arm.
"""
import json

import numpy as np

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
NOM = f"{R}/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
REP = f"{R}/nd-unfolding/pet/fullevent_cstat_n50/replicas/replica_%02d/target/GATE5_REPLICA_TARGET.npy"

nom = np.asarray(np.load(NOM, mmap_mode="r"), dtype=np.float64)
s_nom = float(nom.sum())
n_rows = nom.size
print(f"nominal target : {NOM.split('/')[-1]}  rows {n_rows}  sum {s_nom:.12e}")

sums, mins, nz = [], [], []
for i in range(50):
    a = np.asarray(np.load(REP % i, mmap_mode="r"), dtype=np.float64)
    if a.size != n_rows:
        raise SystemExit(f"replica {i}: {a.size} rows != nominal {n_rows}")
    sums.append(float(a.sum()))
    mins.append(float(a.min()))
    nz.append(int((a == 0).sum()))
    del a
S = np.array(sums)
mean_rep = float(S.mean())
gap = mean_rep - s_nom

print(f"replicas       : n={S.size}  mean sum {mean_rep:.12e}")
print(f"                 min {S.min():.12e}  max {S.max():.12e}  sd {S.std(ddof=1):.6e}")
print(f"\n=== TEST 1 ===")
print(f"  sum(nominal)                 {s_nom:.12e}")
print(f"  mean_i sum(replica_i)        {mean_rep:.12e}")
print(f"  GAP  mean_rep - nominal      {gap:+.6e}")
print(f"  SIGN                         {'POSITIVE (Jensen direction)' if gap > 0 else ('NEGATIVE (against Jensen)' if gap < 0 else 'ZERO')}")
print(f"  magnitude, relative          {gap / s_nom:+.6%}   <- a DIFFERENT claim from the sign")

# how many individual replicas sit above the nominal -- a sign test, distribution-free
above = int((S > s_nom).sum())
print(f"\n  replicas with sum > nominal  {above} of 50   "
      f"(binomial p under 50/50: {'<1e-6' if above >= 45 or above <= 5 else 'not extreme'})")
se = S.std(ddof=1) / np.sqrt(S.size)
print(f"  gap / SE(mean)               {gap / se:+.2f}   (SE {se:.4e})")
print(f"  all targets non-negative     {all(m >= 0 for m in mins)}   "
      f"(min over all replicas {min(mins):.3e})")
print(f"  median exact-zero rows/replica {int(np.median(nz))} of {n_rows} "
      f"({np.median(nz) / n_rows:.2%})  -- where the projection bit")

out = {"what": "OI-126 Q3 Test 1: refine(E[w]) vs E[refine(w)] at the total level",
       "predeclared_sign": "POSITIVE (E[refine(w)] >= refine(E[w]) by Jensen; max(0,.) convex)",
       "sum_nominal": s_nom, "mean_replica_sum": mean_rep, "gap": gap,
       "gap_relative": gap / s_nom, "sign": "POSITIVE" if gap > 0 else ("NEGATIVE" if gap < 0 else "ZERO"),
       "replicas_above_nominal": above, "n_replicas": int(S.size),
       "gap_over_SE_of_mean": gap / se, "replica_sum_sd": float(S.std(ddof=1)),
       "rows": n_rows, "all_non_negative": bool(all(m >= 0 for m in mins)),
       "median_zero_rows_per_replica": int(np.median(nz)),
       "replica_sums": sums}
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(out, indent=1, sort_keys=True))
