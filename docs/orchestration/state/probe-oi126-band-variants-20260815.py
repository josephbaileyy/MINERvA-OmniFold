"""Band-geometry variants for the Track A vote: does column 15 dilute the band statistic?

Read-only. Same statistic as the pinned one (per-replica MEDIAN over cells of T_nom/T_k) evaluated on
several band definitions, so the effect of including p_parallel[15,20) -- whose mean is 1.105, already at
the (b) hypothesis -- can be measured rather than estimated. Emits one JSON object on stdout.
"""
import numpy as np, json

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
INP = R + "/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
NOMP = R + "/pet/fullevent_nominal_annealed_extraction_unpromoted/P5A-ANNEALED-UNPROMOTED.push.slurm-56978466.npz"
B = R + "/pet/fullevent_cstat_n50/replicas"
CANON_PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30.0])
CANON_PL = np.array([0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0,
                     20.0, 40.0, 60.0, 120.0])
NPL, NPT = 19, 15

zn = np.load(NOMP, allow_pickle=True)
wpn = zn["w_push"]; mi_n = zn["mc_indices"]
f = np.load(INP, allow_pickle=True)
ts = f["truth_scalars"]
pt = np.ascontiguousarray(ts[:, 0]); pl = np.ascontiguousarray(ts[:, 1]); del ts
wt = f["w_truth"]; pass_truth = f["pass_truth"].astype(bool)
i_pt = np.clip(np.searchsorted(CANON_PT, pt, side="right") - 1, 0, NPT - 1)
i_pl = np.clip(np.searchsorted(CANON_PL, pl, side="right") - 1, 0, NPL - 1)
inr = pass_truth & (pt >= CANON_PT[0]) & (pt < CANON_PT[-1]) & (pl >= CANON_PL[0]) & (pl < CANON_PL[-1])
cell = (i_pt * NPL + i_pl)[inr]; wtb = wt[inr]
del pt, pl, i_pt, i_pl, wt, pass_truth
T_n = np.bincount(cell, weights=wtb * wpn[inr], minlength=NPT * NPL); del wpn

cs = np.load(R + "/pet/fullevent_cstat_n50/cstat/GATE5_CSTAT_N50.npz", allow_pickle=True)
ciq = cs["cell_index"][cs["quotable_mask"]]
col = ciq % NPL
VARIANTS = {"cols_10_15_PINNED": (10, 15), "cols_10_14": (10, 14), "cols_11_14": (11, 14),
            "cols_11_13": (11, 13), "cols_10_13": (10, 13)}
sets = {k: ciq[(col >= a) & (col <= b)] for k, (a, b) in VARIANTS.items()}
out = {"schema": "oi126-band-variants-v1",
       "statistic": "per-replica MEDIAN over the variant's cells of T_nom/T_k -- identical to the pinned "
                    "statistic, only the cell set differs",
       "n_cells": {k: int(v.shape[0]) for k, v in sets.items()},
       "per_replica": {k: [] for k in sets}}

for k in range(50):
    z = np.load(f"{B}/replica_{k:02d}/extraction/GATE5_REPLICA_FULL_PUSH.npz", allow_pickle=True)
    assert np.array_equal(z["mc_indices"], mi_n)
    T_k = np.bincount(cell, weights=wtb * z["w_push"][inr], minlength=NPT * NPL); del z
    for name, cs_ in sets.items():
        ok = (T_n[cs_] > 0) & (T_k[cs_] > 0)
        out["per_replica"][name].append(float(np.median(T_n[cs_][ok] / T_k[cs_][ok])))

out["summary"] = {}
for name, v in out["per_replica"].items():
    a = np.array(v)
    out["summary"][name] = {"n_cells": int(sets[name].shape[0]), "mean": float(a.mean()),
                            "sd_ddof1": float(a.std(ddof=1)), "median": float(np.median(a)),
                            "min": float(a.min()), "max": float(a.max()),
                            "rel_sd": float(a.std(ddof=1) / a.mean()),
                            "cohen_d_vs_midpoint": float((a.mean() - 1.0) / 2 / a.std(ddof=1)),
                            "cohen_d_vs_b_at_1p0_two_sample": float((a.mean() - 1.0) / a.std(ddof=1))}
print(json.dumps(out))
