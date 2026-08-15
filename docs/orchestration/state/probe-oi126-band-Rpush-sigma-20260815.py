"""Within-arm replica-to-replica sigma of band R_push, over all 50 replicas. DESCRIPTIVE.

No hypothesis is predeclared: there is nothing here to be right or wrong about, only a number that was
missing. Read-only; emits one JSON object on stdout.

CONVENTIONS, DECLARED BECAUSE THEY ARE CHOICES AND NOT DEFAULTS
---------------------------------------------------------------
1. STATISTIC. Band R_push for replica k is the MEDIAN over the geometric band cells of
   T_nom(cell)/T_k(cell), with T_a(cell) = sum over pass_truth rows in cell of w_truth*w_push_a.
   The median-over-cells form is used because that is exactly the statistic whose single-draw value
   (5.0467 for replica_00) this measurement is putting a spread on. A mean-over-cells or a
   ratio-of-sums would be a different number and is reported alongside rather than substituted.
2. BAND. p_parallel columns 10-15 (6-20 GeV), all pT rows, intersected with the 257-cell quotable
   sub-block. Geometric and REPLICA-INDEPENDENT by construction, exactly as fixed in
   PREDECLARATION-20260815-oi126-push-vs-extraction.md -- so no replica can move its own denominator.
3. UNDEFINED RATIOS. A cell is dropped for a given replica iff T_nom<=0 or T_k<=0. Counts are reported
   per replica. This is the only exclusion applied and it is not effect-dependent.
4. THE BEN-341 CONTAMINANT DOES NOT REACH THIS SUM, and that is checked rather than asserted. The 1,916
   Stay-Positive-clipped zero-weight rows live in the MEASURED leg (4,680,719 data+bkg rows). This
   computation sums over the SIGNAL leg (49,152,885 MC rows). The two legs are disjoint arrays of
   different length; the probe asserts the length it actually indexed. Those rows act on w_push through
   TRAINING, not as terms in T_a -- so they cannot inflate a per-cell ratio the way they inflated the
   per-column zero fraction.
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
out = {"schema": "oi126-band-Rpush-sigma-v1", "descriptive_no_hypothesis_predeclared": True}

zn = np.load(NOMP, allow_pickle=True)
wpn = zn["w_push"]; mi_n = zn["mc_indices"]
out["n_signal_rows_indexed"] = int(wpn.shape[0])
out["mc_indices_is_identity_nominal"] = bool(np.array_equal(mi_n, np.arange(mi_n.shape[0])))

f = np.load(INP, allow_pickle=True)
ts = f["truth_scalars"]
pt = np.ascontiguousarray(ts[:, 0]); pl = np.ascontiguousarray(ts[:, 1]); del ts
wt = f["w_truth"]; pass_truth = f["pass_truth"].astype(bool)
assert pt.shape[0] == wpn.shape[0]
# convention 4: the measured leg is a DIFFERENT array of DIFFERENT length; assert we indexed the signal leg
out["measured_leg_rows_for_contrast"] = 4680719
out["signal_leg_is_not_the_measured_leg"] = bool(pt.shape[0] != 4680719)

i_pt = np.clip(np.searchsorted(CANON_PT, pt, side="right") - 1, 0, NPT - 1)
i_pl = np.clip(np.searchsorted(CANON_PL, pl, side="right") - 1, 0, NPL - 1)
inr = pass_truth & (pt >= CANON_PT[0]) & (pt < CANON_PT[-1]) & (pl >= CANON_PL[0]) & (pl < CANON_PL[-1])
cell = (i_pt * NPL + i_pl)[inr]
wtb = wt[inr]
del pt, pl, i_pt, i_pl, wt, pass_truth
T_n = np.bincount(cell, weights=wtb * wpn[inr], minlength=NPT * NPL)
del wpn

cs = np.load(R + "/pet/fullevent_cstat_n50/cstat/GATE5_CSTAT_N50.npz", allow_pickle=True)
ciq = cs["cell_index"][cs["quotable_mask"]]
col = ciq % NPL
band_cells = ciq[(col >= 10) & (col <= 15)]
out["n_band_cells"] = int(band_cells.shape[0])
out["band_definition"] = "p_parallel columns 10-15 intersected with the 257 quotable cells; geometric"

per_rep, per_rep_col, dropped, alt = [], [], [], []
for k in range(50):
    z = np.load(f"{B}/replica_{k:02d}/extraction/GATE5_REPLICA_FULL_PUSH.npz", allow_pickle=True)
    assert np.array_equal(z["mc_indices"], mi_n), f"replica {k} mc_indices differ from nominal"
    T_k = np.bincount(cell, weights=wtb * z["w_push"][inr], minlength=NPT * NPL)
    del z
    ok = (T_n[band_cells] > 0) & (T_k[band_cells] > 0)
    bc = band_cells[ok]
    r = T_n[bc] / T_k[bc]
    per_rep.append(float(np.median(r)))
    dropped.append(int((~ok).sum()))
    alt.append({"replica": k, "mean_over_cells": float(r.mean()),
                "ratio_of_sums": float(T_n[bc].sum() / T_k[bc].sum())})
    per_rep_col.append([float(np.median(T_n[band_cells[(band_cells % NPL) == j]] /
                                       T_k[band_cells[(band_cells % NPL) == j]]))
                        for j in range(10, 16)])
v = np.array(per_rep)
out["per_replica_band_R_push_MEDIAN_over_cells"] = per_rep
out["cells_dropped_per_replica"] = dropped
out["summary"] = {
  "n_replicas": int(v.shape[0]), "mean": float(v.mean()), "sd_ddof1": float(v.std(ddof=1)),
  "median": float(np.median(v)), "min": float(v.min()), "max": float(v.max()),
  "p10": float(np.percentile(v, 10)), "p90": float(np.percentile(v, 90)),
  "rel_sd": float(v.std(ddof=1) / v.mean()),
  "replica_00_value": per_rep[0],
  "replica_00_zscore_vs_family": float((per_rep[0] - v.mean()) / v.std(ddof=1)),
  "replica_00_percentile": float(100.0 * (v < per_rep[0]).mean()),
  "n_replicas_below_replica_00": int((v < per_rep[0]).sum())}
out["alternative_statistics_not_substituted"] = alt
PC = np.array(per_rep_col)          # (50, 6)
out["per_pparallel_column"] = [
  {"i_pparallel": 10 + t, "pparallel_bin": [float(CANON_PL[10 + t]), float(CANON_PL[11 + t])],
   "mean_over_50": float(PC[:, t].mean()), "sd_over_50": float(PC[:, t].std(ddof=1)),
   "rel_sd": float(PC[:, t].std(ddof=1) / PC[:, t].mean())} for t in range(6)]
out["is_the_spread_pparallel_structured"] = {
  "sd_by_column": [float(PC[:, t].std(ddof=1)) for t in range(6)],
  "rel_sd_by_column": [float(PC[:, t].std(ddof=1) / PC[:, t].mean()) for t in range(6)],
  "max_over_min_of_rel_sd": float(max(PC[:, t].std(ddof=1) / PC[:, t].mean() for t in range(6)) /
                                 min(PC[:, t].std(ddof=1) / PC[:, t].mean() for t in range(6)))}
out["INGREDIENTS_per_replica_per_column_median_R_push"] = [[float(x) for x in row] for row in PC]
print(json.dumps(out))
