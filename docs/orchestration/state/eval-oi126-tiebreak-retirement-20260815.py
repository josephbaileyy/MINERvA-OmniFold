"""Close out the proposed measured-leg-statistics tiebreak with the measured reason it was not run.

Combines the per-column zero fractions with the per-column R_xsec from the push/extraction probe, both
already committed, and emits the retirement receipt. Read-only, local, no cluster access.
"""
import json, hashlib, math
import numpy as np

ZF = "docs/orchestration/state/probe-oi126-zero-fraction-per-column-20260815.json"
PV = "docs/orchestration/state/probe-oi126-push-vs-extraction-20260815.json"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
z = json.load(open(ZF)); p = json.load(open(PV))
E1 = z["exp_minus_1"]

cond = {r["i_pparallel"]: r for r in z["CONDITIONAL_on_nominal_gt_0"]["per_column"]}
raw = {r["i_pparallel"]: r for r in z["per_column"]}
rx = {r["i_pparallel"]: r for r in p["per_pparallel_column"]}

# per-column significance of the conditional fraction against the Poisson atom, 6 independent draws
rows = []
for j, c in cond.items():
    if c["mean_zero_fraction"] is None:
        continue
    n = c["n_rows_nominal_gt_0"]
    se = math.sqrt(E1 * (1 - E1) / n) / math.sqrt(6)
    rows.append({"i_pparallel": j, "pparallel_bin": raw[j]["pparallel_bin"],
                 "n_measured_rows_nominal_gt_0": n,
                 "conditional_zero_fraction": c["mean_zero_fraction"],
                 "rel_deviation_from_exp_minus_1": c["rel_deviation"],
                 "n_sigma": (c["mean_zero_fraction"] - E1) / se,
                 "median_R_xsec": rx[j]["median_R_xsec"] if j in rx else None,
                 "median_R_push": rx[j]["median_R_push"] if j in rx else None})

zs = [abs(r["n_sigma"]) for r in rows]
# THE TIEBREAK'S OWN PREMISE, tested directly: does the effect track measured-leg row count?
pair = [(r["n_measured_rows_nominal_gt_0"], r["median_R_xsec"]) for r in rows if r["median_R_xsec"]]
ln_n = np.log([a for a, _ in pair]); ln_r = np.log([b for _, b in pair])
pear = float(np.corrcoef(ln_n, ln_r)[0, 1])
sr = lambda v: np.argsort(np.argsort(v))
spear = float(np.corrcoef(sr(ln_n), sr(ln_r))[0, 1])

out = {
 "what": "Retirement of the proposed measured-leg-statistics tiebreak for OI-126, with the measured reason.",
 "status": "THE TIEBREAK IS RETIRED AND WAS NOT RUN. Refused on review by the Assistant as second "
           "key-holder under Joseph's standing grant; the mediator concurred; this lane concurs and the "
           "design was this lane's own.",
 "ingredients": {"zero_fraction_probe": {"path": ZF, "sha256": sha(ZF)},
                 "push_vs_extraction_probe": {"path": PV, "sha256": sha(PV)}},
 "REASON_1_the_discriminating_variable_is_a_CONSTANT_BY_CONSTRUCTION": {
   "claim": "the tiebreak leaned on 'given 36.8% of measured rows carry zero weight'. That is not a "
            "measurement: it is the zero atom of Poisson(1), exp(-1).",
   "exp_minus_1": E1,
   "measured_pooled_conditional": z["CONDITIONAL_on_nominal_gt_0"]["pooled"],
   "measured_pooled_raw": z["summary"]["pooled_zero_fraction"],
   "per_column_max_abs_rel_deviation_conditional": z["CONDITIONAL_on_nominal_gt_0"]["max_abs_rel_deviation"],
   "n_columns": len(rows),
   "max_abs_n_sigma_over_columns": max(zs),
   "expected_max_abs_z_for_that_many_independent_draws": 2.2,
   "verdict": "CONSTANT. Every populated p_parallel column sits within 1.9 sigma of exp(-1) and the "
              "largest deviation is at the smallest column, which is what noise looks like. So the "
              "zero-support fraction cannot discriminate anything: it is identical in every column and "
              "every replica by construction."},
 "REASON_2_the_raw_estimator_would_have_MANUFACTURED_the_hypothesis": {
   "note": "this is the part worth keeping and it was nearly missed",
   "contaminant": "a row whose NOMINAL weight is already 0 (Stay-Positive clipped) is 0 in every replica "
                  "whatever its Poisson multiplicity, so it is not evidence about the bootstrap",
   "nominal_zero_rows_total": z["nominal_zero_rows_total"],
   "raw_max_abs_rel_deviation": z["summary"]["max_abs_rel_deviation_from_exp_minus_1"],
   "raw_worst_column": z["summary"]["column_with_max_deviation"],
   "conditional_max_abs_rel_deviation": z["CONDITIONAL_on_nominal_gt_0"]["max_abs_rel_deviation"],
   "why_it_matters": "the RAW fraction shows an excess that grows as the column gets smaller -- an "
                     "n-dependent structure with the same qualitative shape as the hypothesis the tiebreak "
                     "was hunting. Conditioning on nominal>0 removes it. An unvalidated version of this "
                     "probe would have produced a FALSE POSITIVE pointing the way its author expected."},
 "REASON_3_the_premise_fails_on_its_own_regressor": {
   "note": "the row counts the tiebreak would have regressed on are now measured, so its premise is "
           "testable rather than arguable",
   "pearson_log_n_vs_log_R_xsec": pear,
   "spearman_log_n_vs_log_R_xsec": spear,
   "illustration": "p_parallel[5,6) has the MOST measured rows of any column and R_xsec ~1.17; [8,9) has "
                   "~4x fewer rows and R_xsec ~4.6; [60,120) has ~96x fewer than [5,6) and R_xsec ~0.52",
   "verdict": "the effect is NOT monotone in measured-leg row count and reverses sign at high "
              "p_parallel while row count falls throughout. A statistics-scaling story predicts "
              "monotonicity; the data do not show it."},
 "REASON_4_it_did_not_separate_the_branches_anyway": (
   "under (a) a genuinely unstable estimator is most unstable where information is scarce; under (b) the "
   "pathology of zero-weight rows is also worst where rows are fewest. SAME SIGN, SAME SHAPE, BOTH "
   "BRANCHES. The test would have confirmed that sensitivity is measured-leg-driven, which neither branch "
   "disputes. This argument is the Assistant's and it is correct."),
 "MY_OWN_ERROR_NAMED": ("the invalidating operand was already in this lane's own committed receipt -- "
   "state/RECEIPT-20260815-oi126-mechanism-narrowing.json records exp_minus_1 and a measured ratio to it "
   "of 1.000726 -- and the tiebreak was then designed around that same constant as though it were a "
   "variable. Third instance in one day of BEN-340's shape: a quantity used for something its operands "
   "do not support, with the derivation never attempted."),
 "WHAT_REPLACES_IT_not_authorized_not_this_lane": (
   "a variance-matched, zero-free perturbation: Exponential(1) and Poisson(1) both have mean 1 and "
   "variance 1 and differ in exactly P(X=0) = 0 vs exp(-1). Rebuild one replica with Exponential(1) data "
   "weights and re-run the 21-second push/extraction read. Band R_push staying near 5 implies "
   "variance-driven, i.e. (a); collapsing toward 1 implies zero-support-driven, i.e. (b). Opposite "
   "predictions on one axis, which is what this lane's design lacked. The Assistant's, ~7.8 GPU-h, "
   "blocked on whether a non-pinned override point exists, NOT AUTHORIZED, and to be predeclared with a "
   "numeric two-sided boundary in which UNRESOLVED does not default to (a)."),
 "INSTRUMENT_CONTROLS_that_ran_before_the_measurement": {
   "C1_split_point": z["C1_split_point_control"],
   "C2_structure": {k: z["C2_structure_control"][k] for k in
                    ("min", "max", "max_over_min", "criterion", "structure_detected")},
   "why": "the expected answer was 'constant at exp(-1)', which a MIS-ORDERED row->coordinate map would "
          "also produce, since permuting a constant-rate Bernoulli field still gives exp(-1) per bin. "
          "Both controls had to pass before the constancy could be believed rather than assumed."},
 "per_column": rows,
}
P = "docs/orchestration/state/RECEIPT-20260815-oi126-tiebreak-retirement.json"
open(P, "w").write(json.dumps(out, indent=1) + "\n")
print("columns:", len(rows), " max |z| = %.2f" % max(zs))
print("conditional pooled %.8f vs exp(-1) %.8f  (rel %+.2e)"
      % (z["CONDITIONAL_on_nominal_gt_0"]["pooled"], E1,
         z["CONDITIONAL_on_nominal_gt_0"]["pooled"] / E1 - 1))
print("raw max rel dev %.5f -> conditional %.5f"
      % (z["summary"]["max_abs_rel_deviation_from_exp_minus_1"],
         z["CONDITIONAL_on_nominal_gt_0"]["max_abs_rel_deviation"]))
print("pearson/spearman log n vs log R_xsec: %.3f / %.3f" % (pear, spear))
print("written", P)
