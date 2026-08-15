"""What the measured sigma implies for the Exponential(1) vs Poisson(1) decision boundary.

Read-only, local, derived entirely from the committed sigma probe output. Emits the feasibility receipt.
"""
import json, math, hashlib
import numpy as np

SIG = "docs/orchestration/state/probe-oi126-band-Rpush-sigma-20260815.json"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
d = json.load(open(SIG))
s = d["summary"]
sd, mean = s["sd_ddof1"], s["mean"]
PC = np.array(d["INGREDIENTS_per_replica_per_column_median_R_push"])   # (50, 6), cols 10..15

n_for = lambda dist: math.ceil((1.96 * sd / dist) ** 2) if dist > 0 else None

# (a) predicts the Exponential arm lands where the Poisson arm is (same mean, same variance);
# (b) predicts it collapses toward 1. Boundary B must be far enough from BOTH truths.
A_TRUTH, B_TRUTH = mean, 1.0
boundaries = {}
for Bv in (1.5, 2.0, 2.298, 2.5, 3.0, 4.0):
    da, db = abs(A_TRUTH - Bv), abs(B_TRUTH - Bv)
    boundaries[str(Bv)] = {"distance_to_a_truth": da, "distance_to_b_truth": db,
                           "n_to_confirm_a": n_for(da), "n_to_confirm_b": n_for(db),
                           "n_required_worst_side": max(n_for(da) or 10**9, n_for(db) or 10**9)}
opt = (A_TRUTH + B_TRUTH) / 2.0

# indicative only: a TIGHTER band, cols 11-14, using median-of-column-medians per replica.
# This is a DIFFERENT statistic from median-over-cells and is labelled as such, not substituted.
tight = np.median(PC[:, 1:5], axis=1)
full_colmed = np.median(PC, axis=1)

out = {
 "what": "feasibility of the Exponential(1) vs Poisson(1) decision boundary, given the measured "
         "within-arm sigma of band R_push",
 "status": "INPUT TO A PREDECLARATION THAT HAS NOT BEEN WRITTEN. Not an authorization, not a result about "
           "(a) vs (b), and this lane does not own the replacement instrument.",
 "ingredients": {"sigma_probe": {"path": SIG, "sha256": sha(SIG)}},
 "MEASURED_sigma": {"n_replicas": s["n_replicas"], "mean": mean, "sd_ddof1": sd, "rel_sd": s["rel_sd"],
   "median": s["median"], "min": s["min"], "max": s["max"], "p10": s["p10"], "p90": s["p90"],
   "statistic": "median over the 84 geometric band cells of T_nom/T_k; 0 cells dropped for any replica"},
 "FINDING_1_replica_00_IS_NOT_TYPICAL_AND_THIS_MOVES_THE_HYPOTHESIS": {
   "replica_00_band_R_push": s["replica_00_value"],
   "family_mean": mean, "family_median": s["median"],
   "replica_00_z": s["replica_00_zscore_vs_family"], "replica_00_percentile": s["replica_00_percentile"],
   "consequence": ("the 5.0467 that this lane reported from replica_00 alone, and that reached OI-126 and "
     "the push/extraction RESULT receipt, is a HIGH DRAW at the 70th percentile. The family-typical band "
     "R_push is 3.5969. Every downstream statement of the form 'the band effect is a factor of 5' should "
     "read 'a factor of ~3.6 on the family average, ranging 1.09 to 6.89 across the 50 draws'."),
   "what_it_does_NOT_change": ("the TRAINING-versus-EXTRACTION reading is untouched. That reading rests on "
     "R_push and R_xsec agreeing WITHIN replica_00 (ratio 1.0000) and on the control region, neither of "
     "which involves the family spread. A high draw in both arms of the same ratio cancels.")},
 "FINDING_2_the_proposed_boundary_sits_almost_ON_the_(a)_hypothesis": {
   "proposed_boundary": 4.0,
   "a_truth_as_now_measured": mean,
   "distance": abs(mean - 4.0),
   "n_required_to_confirm_a_at_that_boundary": n_for(abs(mean - 4.0)),
   "why_this_is_worse_than_the_asymmetry_already_found": ("the earlier concern assumed the (a) truth was "
     "~5.05, putting the 4.0 boundary 1.05 away. Measured, the (a) truth is 3.60, so the boundary is 0.40 "
     "away -- inside one quarter of a sigma. The Poisson arm ITSELF would cross a 4.0 boundary in a large "
     "fraction of draws, so a 4.0 boundary does not test (a) against (b), it tests draw luck.")},
 "FINDING_3_a_WELL_CENTRED_boundary_makes_it_affordable": {
   "optimal_boundary_midpoint_of_the_two_hypotheses": opt,
   "distance_each_side": abs(A_TRUTH - opt),
   "n_required_each_side": n_for(abs(A_TRUTH - opt)),
   "comparison": {"at_boundary_4p0": boundaries["4.0"]["n_required_worst_side"],
                  "at_boundary_1p5": boundaries["1.5"]["n_required_worst_side"],
                  "at_midpoint": n_for(abs(A_TRUTH - opt))},
   "caveat_stated_because_it_is_load_bearing": ("this uses the POISSON arm's sigma for both arms. Under (b) "
     "the Exponential arm would plausibly have a SMALLER spread, since the zero-support pathology is what "
     "is being removed; under (a) it should be similar. So 1.609 is the right sigma for the side that "
     "matters, but it is an ASSUMPTION about the untested arm and not a measurement of it. If the "
     "Exponential arm's sigma exceeds 1.609, n grows as sigma squared.")},
 "boundary_table": boundaries,
 "FINDING_4_the_band_is_not_uniform_and_column_15_dilutes_it": {
   "per_column": d["per_pparallel_column"],
   "observation": ("the effect peaks at p_parallel[8,9) with mean 6.57 and is ESSENTIALLY ABSENT at "
     "[15,20) with mean 1.105. Column 15 contributes 14 of the 84 band cells and pulls the band statistic "
     "toward the null, so the geometric band chosen for the training/extraction split -- correctly, since "
     "it had to be replica-independent and fixed in advance -- is not the most discriminating band for a "
     "two-hypothesis test."),
   "INDICATIVE_ONLY_tighter_band_cols_11_to_14": {
     "statistic": "median of the four column-medians per replica -- a DIFFERENT statistic from "
                  "median-over-cells, reported as indicative and NOT substituted for it",
     "mean": float(tight.mean()), "sd_ddof1": float(tight.std(ddof=1)),
     "rel_sd": float(tight.std(ddof=1) / tight.mean()),
     "same_statistic_over_all_six_columns_for_calibration": {
       "mean": float(full_colmed.mean()), "sd_ddof1": float(full_colmed.std(ddof=1))},
     "implied_midpoint_boundary": float((tight.mean() + 1.0) / 2),
     "implied_n_at_that_midpoint": math.ceil((1.96 * float(tight.std(ddof=1)) /
                                              abs(tight.mean() - (tight.mean() + 1.0) / 2)) ** 2),
     "caveat": ("re-scoping the band requires re-deriving median-over-CELLS on the new band, which is one "
                "more free run of the same probe. These numbers indicate whether that is worth doing; they "
                "are not the numbers a predeclaration should quote.")}},
 "FINDING_5_the_spread_is_pparallel_structured": {
   "rel_sd_by_column": d["is_the_spread_pparallel_structured"]["rel_sd_by_column"],
   "max_over_min": d["is_the_spread_pparallel_structured"]["max_over_min_of_rel_sd"],
   "answer": ("structured but mildly -- relative spread runs 0.30 to 0.57 across the six columns, a factor "
              "of 1.87, while the MEAN effect runs 1.11 to 6.57, a factor of 5.9. So the spread is far more "
              "uniform than the effect it accompanies.")},
 "WHAT_THIS_DOES_NOT_DECIDE": [
   "nothing about (a) versus (b); no perturbation arm was run",
   "nothing about whether the Exponential arm is affordable -- that is a cost question for its owner, "
     "given n and the per-replica GPU cost",
   "nothing about C_stat, which is untouched, and no family membership is claimed for any of this",
   "whether the tighter band is the right band; that is the instrument owner's call and needs one free re-run"],
}
P = "docs/orchestration/state/RECEIPT-20260815-oi126-boundary-feasibility.json"
open(P, "w").write(json.dumps(out, indent=1) + "\n")
print("sigma %.4f  mean %.4f  rel_sd %.4f" % (sd, mean, s["rel_sd"]))
print("replica_00 %.4f is at percentile %.0f (z %+.2f) -- NOT typical" %
      (s["replica_00_value"], s["replica_00_percentile"], s["replica_00_zscore_vs_family"]))
print("boundary 4.0 -> n >= %d (worst side)" % boundaries["4.0"]["n_required_worst_side"])
print("boundary 1.5 -> n >= %d (worst side)" % boundaries["1.5"]["n_required_worst_side"])
print("midpoint %.3f -> n >= %d each side" % (opt, n_for(abs(A_TRUTH - opt))))
print("tighter band cols11-14 (indicative): mean %.3f sd %.3f -> midpoint %.3f, n >= %d"
      % (tight.mean(), tight.std(ddof=1), (tight.mean() + 1) / 2,
         out["FINDING_4_the_band_is_not_uniform_and_column_15_dilutes_it"]
            ["INDICATIVE_ONLY_tighter_band_cols_11_to_14"]["implied_n_at_that_midpoint"]))
print("written", P)
