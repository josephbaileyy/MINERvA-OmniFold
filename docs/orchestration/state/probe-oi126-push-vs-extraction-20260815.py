"""OI-126: is the p_parallel deficit in the TRAINING or in the EXTRACTION?

Read-only. Emits one JSON object on stdout. Thresholds are NOT evaluated here -- this script reports
the operands and the predeclared statistics; the reading is applied against
docs/orchestration/PREDECLARATION-20260815-oi126-push-vs-extraction.md (committed at 449ec52, before
this ran) so the criteria cannot be chosen after the fact.

Run inside a salloc on a cpu node (~3 GB resident, a few core-minutes).
"""
import numpy as np, json, hashlib

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
INP = R + "/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
NOMP = R + "/pet/fullevent_nominal_annealed_extraction_unpromoted/P5A-ANNEALED-UNPROMOTED.push.slurm-56978466.npz"
NOMX = R + "/pet/fullevent_nominal_annealed_extraction_unpromoted/P5A-ANNEALED-UNPROMOTED.xsec.slurm-56989462.npz"
REPP = R + "/pet/fullevent_cstat_n50/replicas/replica_00/extraction/GATE5_REPLICA_FULL_PUSH.npz"
REPX = R + "/pet/fullevent_cstat_n50/replicas/replica_00/extraction/GATE5_REPLICA_XSEC.npz"

CANON_PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30.0])
CANON_PL = np.array([0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0,
                     20.0, 40.0, 60.0, 120.0])
NPL = len(CANON_PL) - 1          # 19
NPT = len(CANON_PT) - 1          # 15
out = {"schema": "oi126-push-vs-extraction-v1",
       "predeclaration": "docs/orchestration/PREDECLARATION-20260815-oi126-push-vs-extraction.md at 449ec52"}

# ---- xsec arrays (the end-to-end quantity) -------------------------------------------------
zx_n = np.load(NOMX, allow_pickle=True); zx_r = np.load(REPX, allow_pickle=True)
assert np.allclose(zx_n["edges_pt"], CANON_PT) and np.allclose(zx_n["edges_pparallel"], CANON_PL)
assert np.allclose(zx_r["edges_pt"], CANON_PT) and np.allclose(zx_r["edges_pparallel"], CANON_PL)
xn = zx_n["xsec"].ravel(); xr = zx_r["xsec"].ravel()
out["edges_asserted_canonical"] = True
out["replica_index_checked"] = int(zx_r["replica_index"])

# ---- pushes -------------------------------------------------------------------------------
zp_n = np.load(NOMP, allow_pickle=True); zp_r = np.load(REPP, allow_pickle=True)
wpn = zp_n["w_push"]; wpr = zp_r["w_push"]
mi_n = zp_n["mc_indices"]; mi_r = zp_r["mc_indices"]
out["n_rows_push"] = int(wpn.shape[0])
out["mc_indices_identical_between_arms"] = bool(mi_n.shape == mi_r.shape and np.array_equal(mi_n, mi_r))
out["mc_indices_is_identity"] = bool(np.array_equal(mi_n, np.arange(mi_n.shape[0])))
assert out["mc_indices_identical_between_arms"], "arms disagree on mc_indices; alignment required"

# ---- truth coordinates and weights --------------------------------------------------------
f = np.load(INP, allow_pickle=True)
ts = f["truth_scalars"]
pt = np.ascontiguousarray(ts[:, 0]); pl = np.ascontiguousarray(ts[:, 1])
del ts
wt = f["w_truth"]
pass_truth = f["pass_truth"].astype(bool)
out["n_signal_rows"] = int(pt.shape[0])
out["n_pass_truth"] = int(pass_truth.sum())
assert pt.shape[0] == wpn.shape[0], "push length != signal rows"

# rows are the FULL ordered signal sample when mc_indices is the identity; otherwise reorder
if not out["mc_indices_is_identity"]:
    pt = pt[mi_n]; pl = pl[mi_n]; wt = wt[mi_n]; pass_truth = pass_truth[mi_n]

i_pt = np.clip(np.searchsorted(CANON_PT, pt, side="right") - 1, 0, NPT - 1)
i_pl = np.clip(np.searchsorted(CANON_PL, pl, side="right") - 1, 0, NPL - 1)
inr = pass_truth & (pt >= CANON_PT[0]) & (pt < CANON_PT[-1]) & (pl >= CANON_PL[0]) & (pl < CANON_PL[-1])
cell = (i_pt * NPL + i_pl)[inr]
out["n_rows_binned"] = int(inr.sum())
out["n_pass_truth_outside_grid"] = int(pass_truth.sum() - inr.sum())

wtb = wt[inr]
T_n = np.bincount(cell, weights=wtb * wpn[inr], minlength=NPT * NPL)
T_r = np.bincount(cell, weights=wtb * wpr[inr], minlength=NPT * NPL)
out["sum_T_nominal"] = float(T_n.sum()); out["sum_T_replica"] = float(T_r.sum())
out["global_T_ratio"] = float(T_n.sum() / T_r.sum())

# ---- domain: the 257 quotable cells, further restricted to xsec_rep00 > 0 ------------------
cs = np.load(R + "/pet/fullevent_cstat_n50/cstat/GATE5_CSTAT_N50.npz", allow_pickle=True)
ciq = cs["cell_index"][cs["quotable_mask"]]
ok = (xr[ciq] > 0) & (T_r[ciq] > 0) & (xn[ciq] > 0) & (T_n[ciq] > 0)
cells = ciq[ok]
out["n_quotable"] = int(ciq.shape[0]); out["n_used"] = int(cells.shape[0])
out["n_dropped_nonpositive"] = int(ciq.shape[0] - cells.shape[0])
out["flicker_cells_excluded"] = cs["cell_index"][~cs["quotable_mask"]].tolist()

R_push = T_n[cells] / T_r[cells]
R_xsec = xn[cells] / xr[cells]
col = cells % NPL
ctrl = col <= 9
band = (col >= 10) & (col <= 15)
band63 = band & (R_xsec > 1.5)

med = lambda a: float(np.median(a)) if a.size else None
out["CONTROL_pparallel_lt_6"] = {
    "n": int(ctrl.sum()), "median_R_push": med(R_push[ctrl]), "median_R_xsec": med(R_xsec[ctrl]),
    "median_abs_Rpush_over_Rxsec_minus_1": med(np.abs(R_push[ctrl] / R_xsec[ctrl] - 1.0)),
    "predeclared_pass_iff_le": 0.10}
for lab, sel in [("BAND_pparallel_6_to_20", band), ("BAND_cells_with_Rxsec_gt_1p5", band63),
                 ("pparallel_gt_20", col >= 16)]:
    out[lab] = {"n": int(sel.sum()), "median_R_push": med(R_push[sel]),
                "median_R_xsec": med(R_xsec[sel]),
                "median_Rpush_over_Rxsec": med(R_push[sel] / R_xsec[sel])}
out["per_pparallel_column"] = [
    {"i_pparallel": int(j), "pparallel_bin": [float(CANON_PL[j]), float(CANON_PL[j + 1])],
     "n_cells": int((col == j).sum()), "median_R_push": med(R_push[col == j]),
     "median_R_xsec": med(R_xsec[col == j])} for j in range(NPL) if (col == j).sum()]
# separability of the push deficit, same decomposition as the xsec one
lr = np.log(R_push); rws = cells // NPL; gmean = lr.mean()
fj = {j: lr[col == j].mean() - gmean for j in np.unique(col)}
gi = {i: lr[rws == i].mean() - gmean for i in np.unique(rws)}
sst = float(((lr - gmean) ** 2).sum())
out["separability_of_R_push"] = {
    "R2_pparallel_only": float(1 - ((lr - np.array([gmean + fj[c % NPL] for c in cells])) ** 2).sum() / sst),
    "R2_pt_only": float(1 - ((lr - np.array([gmean + gi[c // NPL] for c in cells])) ** 2).sum() / sst),
    "for_comparison_R_xsec_R2_pparallel_only_from_the_family": 0.8683}
out["INGREDIENTS_per_cell"] = {"cell": cells.tolist(),
                               "T_nominal": T_n[cells].tolist(), "T_replica": T_r[cells].tolist(),
                               "xsec_nominal": xn[cells].tolist(), "xsec_replica": xr[cells].tolist()}
print(json.dumps(out))
