"""Is the replica target's zero-weight fraction constant at e^-1 in EVERY p_parallel column?

Read-only, no allocation. Emits one JSON object on stdout.

WHY THIS PROBE VALIDATES ITSELF FIRST. The expected answer is "constant at e^-1", and a MIS-ORDERED
row->coordinate map would produce exactly that answer for the wrong reason: permuting a constant-rate
Bernoulli field still gives e^-1 in every bin. So a bare "constant" result from an unvalidated map is
worthless. Two positive controls run BEFORE the measurement and are reported whether they pass or fail:

  C1 SPLIT-POINT. The target is asserted to be [data rows | bkg rows]. Data entered at +1 and background
     at -w_bkg*pot_scale before Stay-Positive, so the two blocks must be DISTINGUISHABLE. If their weight
     distributions are indistinguishable, the concatenation assumption is unsupported and the per-column
     result must not be believed.
  C2 STRUCTURE. Per-column mean NOMINAL target weight must NOT be flat. A scrambled map washes physics
     out to a constant, so measurable column-to-column structure is evidence the map carries real
     coordinates. Flatness => the map is suspect and the null is uninterpretable.

Neither control can prove the map correct. They can catch it being wrong, which is the asymmetry that
matters here.
"""
import numpy as np, json

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
INP = R + "/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
NOM = R + "/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
B = R + "/pet/fullevent_cstat_n50/replicas"
CANON_PL = np.array([0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0,
                     20.0, 40.0, 60.0, 120.0])
NPL = len(CANON_PL) - 1
N_DATA, N_BKG = 4116128, 564591
E1 = float(np.exp(-1))
out = {"schema": "oi126-zero-fraction-per-column-v1", "exp_minus_1": E1,
       "why": "test whether the Poisson(1) zero atom is column-dependent; it is the variable the proposed "
              "tiebreak would have relied on"}

n = np.load(NOM)
out["target_rows"] = int(n.shape[0])
out["assumed_layout"] = "[data rows | bkg rows]"
out["n_data_full"], out["n_bkg_full"] = N_DATA, N_BKG
out["layout_lengths_consistent"] = bool(N_DATA + N_BKG == n.shape[0])

f = np.load(INP, allow_pickle=True)
ms = f["measured_scalars"]; bs = f["bkg_reco_scalars"]
out["measured_scalars_shape"] = list(ms.shape); out["bkg_reco_scalars_shape"] = list(bs.shape)
pl = np.concatenate([np.ascontiguousarray(ms[:, 1]), np.ascontiguousarray(bs[:, 1])])
del ms, bs
out["coord_length_matches_target"] = bool(pl.shape[0] == n.shape[0])
assert out["layout_lengths_consistent"] and out["coord_length_matches_target"]

# ---- C1 SPLIT-POINT CONTROL --------------------------------------------------------------------
d_blk, b_blk = n[:N_DATA], n[N_DATA:]
q = [1, 25, 50, 75, 99]
out["C1_split_point_control"] = {
  "data_block": {"mean": float(d_blk.mean()), "n_zero": int((d_blk == 0).sum()),
                 "percentiles": [float(x) for x in np.percentile(d_blk, q)]},
  "bkg_block":  {"mean": float(b_blk.mean()), "n_zero": int((b_blk == 0).sum()),
                 "percentiles": [float(x) for x in np.percentile(b_blk, q)]},
  "mean_ratio_bkg_over_data": float(b_blk.mean() / d_blk.mean()),
  "criterion": "the two blocks must be DISTINGUISHABLE; mean ratio within 1% of 1.0 and matching "
               "percentiles would mean the concatenation assumption is unsupported"}
out["C1_split_point_control"]["blocks_distinguishable"] = bool(
    abs(b_blk.mean() / d_blk.mean() - 1.0) > 0.01)

i_pl = np.clip(np.searchsorted(CANON_PL, pl, side="right") - 1, 0, NPL - 1)
inr = (pl >= CANON_PL[0]) & (pl < CANON_PL[-1])
out["rows_inside_pparallel_grid"] = int(inr.sum())
out["rows_outside_pparallel_grid"] = int((~inr).sum())

# ---- C2 STRUCTURE CONTROL ----------------------------------------------------------------------
cnt = np.bincount(i_pl[inr], minlength=NPL).astype(float)
sum_nom = np.bincount(i_pl[inr], weights=n[inr], minlength=NPL)
with np.errstate(invalid="ignore", divide="ignore"):
    mean_nom = np.where(cnt > 0, sum_nom / np.maximum(cnt, 1), np.nan)
mm = mean_nom[cnt > 0]
out["C2_structure_control"] = {
  "per_column_mean_nominal_weight": [None if np.isnan(v) else float(v) for v in mean_nom],
  "min": float(np.nanmin(mm)), "max": float(np.nanmax(mm)),
  "max_over_min": float(np.nanmax(mm) / np.nanmin(mm)),
  "criterion": "must NOT be flat; a scrambled map washes column structure out to a constant",
  "structure_detected": bool(np.nanmax(mm) / np.nanmin(mm) > 1.10)}

# ---- THE MEASUREMENT ---------------------------------------------------------------------------
# KNOWN CONTAMINANT OF THIS ESTIMATOR, quantified rather than assumed away: a row whose NOMINAL weight
# is already 0 (Stay-Positive clipped) is 0 in every replica whatever its Poisson multiplicity. Those rows
# are not evidence about the bootstrap. The conditional fraction over rows with nominal > 0 is the
# well-posed test of the Poisson atom; the raw fraction is reported beside it.
nz = (n == 0) & inr
nzc = np.bincount(i_pl[nz], minlength=NPL).astype(float)
pos = (n > 0) & inr
posc = np.bincount(i_pl[pos], minlength=NPL).astype(float)
out["nominal_zero_rows_per_column"] = [int(v) for v in nzc]
out["nominal_zero_rows_total"] = int(nz.sum())
out["contaminant_note"] = ("rows with nominal weight 0 are zero in EVERY replica by construction; they "
                           "inflate the raw per-column zero fraction most where the column has fewest rows")

per_rep, per_rep_cond = [], []
for i in range(6):
    a = np.load(f"{B}/replica_{i:02d}/target/GATE5_REPLICA_TARGET.npy")
    z = (a == 0) & inr
    zc = np.bincount(i_pl[z], minlength=NPL).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(cnt > 0, zc / np.maximum(cnt, 1), np.nan)
    zcond = np.bincount(i_pl[(a == 0) & pos], minlength=NPL).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        fcond = np.where(posc > 0, zcond / np.maximum(posc, 1), np.nan)
    per_rep.append(frac); per_rep_cond.append(fcond)
    del a
FC = np.array(per_rep_cond)
mean_cond = np.nanmean(FC, axis=0)
gc = ~np.isnan(mean_cond)
out["CONDITIONAL_on_nominal_gt_0"] = {
  "per_column": [{"i_pparallel": int(j), "n_rows_nominal_gt_0": int(posc[j]),
                  "mean_zero_fraction": None if np.isnan(mean_cond[j]) else float(mean_cond[j]),
                  "rel_deviation": None if np.isnan(mean_cond[j]) else float(mean_cond[j] / E1 - 1.0)}
                 for j in range(NPL)],
  "max_abs_rel_deviation": float(np.nanmax(np.abs(mean_cond[gc] / E1 - 1.0))),
  "column_with_max_deviation": int(np.nanargmax(np.abs(mean_cond / E1 - 1.0))),
  "pooled": float(np.nansum(FC * posc) / (6 * posc[gc].sum()))}
F = np.array(per_rep)                                  # (6, NPL)
mean_frac = np.nanmean(F, axis=0)
out["per_column"] = [
  {"i_pparallel": int(j), "pparallel_bin": [float(CANON_PL[j]), float(CANON_PL[j + 1])],
   "n_measured_rows": int(cnt[j]),
   "mean_zero_fraction_over_6_replicas": None if np.isnan(mean_frac[j]) else float(mean_frac[j]),
   "deviation_from_exp_minus_1": None if np.isnan(mean_frac[j]) else float(mean_frac[j] - E1),
   "rel_deviation": None if np.isnan(mean_frac[j]) else float(mean_frac[j] / E1 - 1.0),
   "sd_across_replicas": None if np.isnan(F[:, j]).all() else float(np.nanstd(F[:, j], ddof=1))}
  for j in range(NPL)]
good = ~np.isnan(mean_frac)
out["summary"] = {
  "n_columns_with_rows": int(good.sum()),
  "max_abs_rel_deviation_from_exp_minus_1": float(np.nanmax(np.abs(mean_frac[good] / E1 - 1.0))),
  "column_with_max_deviation": int(np.nanargmax(np.abs(mean_frac / E1 - 1.0))),
  "pooled_zero_fraction": float(np.nansum(np.array([np.nansum(F[k] * cnt) for k in range(6)]))
                                / (6 * cnt.sum())),
  "binomial_1sigma_on_smallest_column": float(np.sqrt(E1 * (1 - E1) / max(cnt[good].min(), 1))),
  "smallest_column_n": int(cnt[good].min())}
out["INGREDIENTS_per_replica_per_column_zero_fraction"] = [
  [None if np.isnan(v) else float(v) for v in row] for row in F]
out["INGREDIENTS_measured_rows_per_column"] = [int(v) for v in cnt]
print(json.dumps(out))
