#!/usr/bin/env python3
"""OI-126 availability check, v2: the EXACT training population and the artifact's OWN cell mask.

v1 used pass_reco as a proxy for the training subset and my own band intersection. Both are
now taken from the replica artifact itself, because v1 showed the answer FLIPS with the
population: on the full 49.2M-row inventory the band looks sparser, on pass_reco it looks
richer. A conclusion that depends on which population you pick must be computed on the one the
estimator actually consumes -- `mc_indices` -- and the band on the mask the artifact publishes
-- `reported_bin_mask`.

READ-ONLY. No training, no unfolding, no GPU, nothing inside the promoted arm.
NO REDUCTION BEFORE REPORTING: per-cell arrays emitted in full.
"""
import json
import os
import sys

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
sys.path.insert(0, os.path.join(REPO, "nd-unfolding/pet"))
import fullevent_fps_dataloader as fe  # noqa: E402

INPUTS = os.path.join(REPO, "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
REPLICA = os.path.join(
    REPO, "nd-unfolding/pet/fullevent_cstat_n50/replicas/replica_00/training/"
    "GATE5_REPLICA_WEIGHTS.npz")
OUT = "/tmp/mnv_oi126_occupancy2.json"

with np.load(REPLICA) as r:
    imc = np.asarray(r["mc_indices"], np.int64)
    sig_full = np.asarray(r["sig_bootstrap_factor_full"], np.float64)
    mask = np.asarray(r["reported_bin_mask"]).astype(bool).ravel()
    e_pt = np.asarray(r["edges_pt"], float)
    e_pl = np.asarray(r["edges_pparallel"], float)
    bin_order = str(np.asarray(r["bin_order"]).item())

# The artifact's OWN edges must equal the loader's canonical ones, or the cell index this
# script builds is not the cell index the artifact's mask indexes. Asserted, not assumed.
assert np.allclose(e_pt, fe.CANONICAL_PT_EDGES), "edges_pt differs from the canonical grid"
assert np.allclose(e_pl, fe.CANONICAL_PPARALLEL_EDGES), "edges_pparallel differs"
N_PT, N_PL = e_pt.size - 1, e_pl.size - 1
N_CELLS = N_PT * N_PL
assert mask.size == N_CELLS, f"reported_bin_mask {mask.size} != {N_CELLS}"

with np.load(INPUTS) as d:
    ts = np.asarray(d["truth_scalars"][:, [fe.SCALAR_COLS["pt"], fe.SCALAR_COLS["pparallel"]]],
                    np.float64)
n_rows = ts.shape[0]
pt_bin = np.clip(np.digitize(ts[:, 0], e_pt) - 1, 0, N_PT - 1)
pl_bin = np.clip(np.digitize(ts[:, 1], e_pl) - 1, 0, N_PL - 1)
cell_all = (pt_bin * N_PL + pl_bin).astype(np.int64)
del ts, pt_bin, pl_bin

cell = cell_all[imc]
sig = sig_full[imc]

col = np.arange(N_CELLS) % N_PL
is_band = (col >= 10) & (col <= 15)          # 6-20 GeV, committed definition
band_q = is_band & mask                      # intersected with the artifact's quotable mask

n_rows_cell = np.bincount(cell, minlength=N_CELLS).astype(np.int64)
sum_w = np.bincount(cell, sig, minlength=N_CELLS)
sum_w2 = np.bincount(cell, sig * sig, minlength=N_CELLS)
nz = np.bincount(cell, (sig > 0).astype(float), minlength=N_CELLS)
with np.errstate(divide="ignore", invalid="ignore"):
    n_eff = np.where(sum_w2 > 0, sum_w * sum_w / sum_w2, 0.0)
    surv = np.where(n_rows_cell > 0, nz / n_rows_cell, np.nan)
live = n_rows_cell > 0

A, B = live & band_q, live & mask & ~is_band


def q(x, m):
    v = x[m]
    return {"n_cells": int(m.sum()), "min": float(v.min()), "q25": float(np.percentile(v, 25)),
            "median": float(np.median(v)), "q75": float(np.percentile(v, 75)),
            "max": float(v.max())}


out = {
    "schema": "oi126-band-mc-occupancy-v2",
    "question": ("Poisson(1) thinning is uniform IN SHARE, so a band-confined effect needs a LOCAL "
                 "AMPLIFIER, and the only one available is MC sparsity. Is the 6-20 GeV band the "
                 "sparse end of the grid?"),
    "provenance": {
        "inputs_npz": INPUTS, "replica": REPLICA,
        "population": "mc_indices from the replica artifact -- the EXACT training subset",
        "band": "p_parallel cols 10-15 (6-20 GeV) INTERSECTED with the artifact's reported_bin_mask",
        "comparison_set": "quotable cells OUTSIDE the band (mask & ~is_band)",
        "edges_source": "the artifact's own edges_pt/edges_pparallel, ASSERTED equal to the loader's",
        "bin_order": bin_order,
        "n_inventory_rows": int(n_rows), "n_training_rows": int(imc.size),
        "n_quotable_cells": int(mask.sum()),
    },
    "counts": {"live_band_quotable_cells": int(A.sum()),
               "live_quotable_cells_outside_band": int(B.sum())},
    "VERDICT_OPERANDS_rows_per_cell": {"BAND": q(n_rows_cell, A), "OUTSIDE": q(n_rows_cell, B)},
    "n_eff_after_thinning_per_cell": {"BAND": q(n_eff, A), "OUTSIDE": q(n_eff, B)},
    "uniformity_of_thinning": {
        "expected_surviving_fraction_1_minus_1_over_e": 0.6321205588285577,
        "BAND_median_surviving": float(np.nanmedian(surv[A])),
        "OUTSIDE_median_surviving": float(np.nanmedian(surv[B])),
    },
    "NOT_REDUCED_per_cell_arrays": {
        "cell_is_band_quotable": A.tolist(),
        "cell_is_quotable_outside_band": B.tolist(),
        "n_rows_unthinned": n_rows_cell.tolist(),
        "n_eff_after_thinning": [round(x, 4) for x in n_eff.tolist()],
        "surviving_distinct_fraction": [None if np.isnan(x) else round(x, 6)
                                        for x in surv.tolist()],
    },
}
with open(OUT, "w") as f:
    json.dump(out, f, indent=1)

print(f"wrote {OUT}")
print(f"training rows {imc.size} of {n_rows} inventory; quotable cells {int(mask.sum())}")
print(f"live band-quotable cells {int(A.sum())}   live quotable outside band {int(B.sum())}")
print("\nROWS PER CELL (the amplifier operand):")
for k in ("BAND", "OUTSIDE"):
    v = out["VERDICT_OPERANDS_rows_per_cell"][k]
    print(f"  {k:8} n={v['n_cells']:3}  min {v['min']:.0f}  q25 {v['q25']:.0f}  "
          f"median {v['median']:.0f}  q75 {v['q75']:.0f}  max {v['max']:.0f}")
u = out["uniformity_of_thinning"]
print(f"\nsurviving distinct fraction  BAND {u['BAND_median_surviving']:.5f}  "
      f"OUTSIDE {u['OUTSIDE_median_surviving']:.5f}  expected {0.6321205588285577:.5f}")
