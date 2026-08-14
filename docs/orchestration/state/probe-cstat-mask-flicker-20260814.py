"""Mask flicker across the Gate-5 replica family: is the reported set a per-replica draw?

Lane D, OI-121. READ-ONLY -- opens each GATE5_REPLICA_XSEC.npz, reads `xsec`, writes nothing.

THE HAZARD (predeclaration sec 5). extract_fullevent_replica.py:192-196 monkey-patches
completeness_2d so the replica's signal Poisson factor multiplies the weights INSIDE the
completeness computation. The reporting mask `comp > 0` is therefore drawn per replica. A
thinly-populated cell reported in replica 7 and masked to a hard 0.0 in replica 23 contributes
MASK FLICKER, not statistical variance of the cross section -- and both builders would compute
the identical wrong variance from the identical vectors and agree perfectly.

I predicted the flicker would sit on the staircase boundary (rows 12-14 at the low-p_parallel
edge), because those are the thinly-populated cells whose comp > 0 is one draw from flipping.
That prediction is recorded here BEFORE the measurement so it can be wrong.

PREDECLARED:
  F1  n_replicas_reported per cell        expect: mostly 0 or N, some intermediate
  F2  union vs intersection               expect: |intersection| <= 262 <= |union|
  F3  flicker cells (0 < n < N) located   expect: on the rows 12-14 staircase boundary
  F4  variance inflation from flicker     expect: confined to the flicker cells
"""
import glob
import json
import os
import sys

import numpy as np

ROOT = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/"
        "replicas/*/extraction/GATE5_REPLICA_XSEC.npz")
N_PT, N_PP = 15, 19
N_CELLS = N_PT * N_PP
NOMINAL_ZEROS = ([12 * N_PP + 0] + [13 * N_PP + j for j in range(7)]
                 + [14 * N_PP + j for j in range(15)])

files = sorted(glob.glob(ROOT))
print(f"=== mask flicker across the Gate-5 replica family ===")
print(f"products found: {len(files)}")
if len(files) < 50:
    print(f"*** PARTIAL FAMILY: {len(files)} of 50. This is a DRY RUN and its numbers are NOT "
          f"the family's. Flicker can only INCREASE with more replicas. ***")
if not files:
    sys.exit("no products yet")

X, ids = [], []
for f in files:
    with np.load(f, allow_pickle=True) as z:
        X.append(np.asarray(z["xsec"], float).ravel())
        ids.append(int(z["replica_index"]) if "replica_index" in z.files else -1)
X = np.array(X)
N = X.shape[0]
print(f"stacked: {X.shape}  replica_index range {min(ids)}..{max(ids)}, "
      f"{len(set(ids))} distinct")
assert X.shape[1] == N_CELLS, X.shape

rep = X > 0                                     # per-replica reported set
n_reported = rep.sum(axis=0)                    # per cell, how many replicas reported it

union = n_reported > 0
inter = n_reported == N
flick = (n_reported > 0) & (n_reported < N)

print(f"\n-- F1/F2 --")
print(f"  union        : {int(union.sum())} cells reported by >= 1 replica")
print(f"  intersection : {int(inter.sum())} cells reported by ALL {N}")
print(f"  nominal      : 262 (the committed nominal extraction)")
print(f"  FLICKER CELLS: {int(flick.sum())}  (0 < n < {N})")

print(f"\n-- F3: where are they? --")
if flick.any():
    for c in np.flatnonzero(flick):
        i, j = c // N_PP, c % N_PP
        onstair = c in NOMINAL_ZEROS or (i >= 12)
        print(f"  cell {c:3d} = (i_pt={i:2d}, i_pp={j:2d})  reported in {n_reported[c]:2d}/{N}"
              f"   {'on the rows-12-14 boundary' if onstair else '*** NOT on the boundary ***'}")
else:
    print("  none -- the reported set is IDENTICAL across every replica in this sample.")
    print("  The hazard is real in the code path and EMPTY in the data, so far.")

print(f"\n-- F4: variance attributable to flicker --")
var = X.var(axis=0, ddof=1) if N > 1 else np.zeros(N_CELLS)
if flick.any():
    # recompute each flicker cell's variance over ONLY the replicas that reported it
    for c in np.flatnonzero(flick):
        v_all = float(np.var(X[:, c], ddof=1))
        sub = X[rep[:, c], c]
        v_rep = float(np.var(sub, ddof=1)) if sub.size > 1 else float("nan")
        ratio = (v_all / v_rep) if v_rep and np.isfinite(v_rep) and v_rep > 0 else float("inf")
        print(f"  cell {c:3d}: var(all {N}) = {v_all:.4e}   var(reporting {sub.size} only) = "
              f"{v_rep:.4e}   inflation x{ratio:.2f}")
else:
    print("  n/a -- no flicker cells.")

print(f"\n  cells with nonzero variance: {int((var > 0).sum())}")
print(f"  cells identically zero in all {N}: {int((n_reported == 0).sum())}")

out = {
    "what": "mask-flicker measurement across the Gate-5 C_stat replica family",
    "PARTIAL": len(files) < 50,
    "n_products_read": int(N),
    "replica_indices": sorted(set(ids)),
    "n_union": int(union.sum()),
    "n_intersection": int(inter.sum()),
    "n_nominal_reference": 262,
    "n_flicker_cells": int(flick.sum()),
    "flicker_cells": [{"flat": int(c), "i_pt": int(c) // N_PP, "i_pparallel": int(c) % N_PP,
                       "n_replicas_reported": int(n_reported[c])}
                      for c in np.flatnonzero(flick)],
    "n_replicas_reported_per_cell": n_reported.tolist(),
    "prediction_recorded_before_measurement":
        "flicker, if any, sits on the rows 12-14 low-p_parallel staircase boundary",
    "SCOPE": ("read-only; opens each product's `xsec` and nothing else. Reported set is taken as "
              "(xsec > 0), which is the operationally correct definition for a covariance -- a "
              "cell zero in every replica gives a null row and column regardless of why."),
    "source_glob": ROOT,
    "measured_files": [os.path.basename(os.path.dirname(os.path.dirname(f))) for f in files],
}
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(out, indent=1, sort_keys=True))
