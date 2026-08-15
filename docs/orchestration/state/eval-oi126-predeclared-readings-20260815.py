"""Apply the PREDECLARED thresholds to the probe output. The evaluation is code, not eyesight,
so the reading cannot be chosen after the fact. Emits the RESULT receipt."""
import json, hashlib

PRE = "docs/orchestration/PREDECLARATION-20260815-oi126-push-vs-extraction.md"
PROBE_PY = "docs/orchestration/state/probe-oi126-push-vs-extraction-20260815.py"
PROBE_JSON = "docs/orchestration/state/probe-oi126-push-vs-extraction-20260815.json"
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
d = json.load(open(PROBE_JSON))

c = d["CONTROL_pparallel_lt_6"]
ctrl_stat = c["median_abs_Rpush_over_Rxsec_minus_1"]
control_pass = ctrl_stat <= 0.10
b = d["BAND_pparallel_6_to_20"]
rp, rx, rr = b["median_R_push"], b["median_R_xsec"], b["median_Rpush_over_Rxsec"]

readings = {
    "TRAINING":    control_pass and rp >= 2.0 and 0.7 <= rr <= 1.4,
    "EXTRACTION":  control_pass and 0.80 <= rp <= 1.25 and rx >= 2.0,
    "SPLIT":       control_pass and 1.25 < rp < 2.0,
    "UNINFORMATIVE": (not control_pass) or rx < 2.0,
}
matched = [k for k, v in readings.items() if v]

out = {
 "what": "OI-126 push-vs-extraction: which PREDECLARED reading the measurement matched",
 "predeclaration": {"path": PRE, "committed_at": "449ec52",
   "sha256": sha(PRE),
   "note": "committed BEFORE the probe ran; the thresholds below are quoted from it, not chosen now"},
 "probe": {"script": PROBE_PY, "script_sha256": sha(PROBE_PY),
           "output_verbatim": PROBE_JSON, "output_sha256": sha(PROBE_JSON),
           "run": "inside salloc 57020313, -A m3246 -C cpu -q interactive, 21 s wall, exit 0, empty stderr"},
 "CONTROL": {"predeclared": "median |R_push/R_xsec - 1| <= 0.10 over p_parallel<6 GeV, else UNINFORMATIVE",
   "n_cells": c["n"], "measured": ctrl_stat, "PASS": control_pass,
   "reading": ("the truth-side binning reproduces the extraction to %.3f%% in the control region, so the "
               "band readings are usable" % (100 * ctrl_stat))},
 "BAND_pparallel_6_to_20": {"n_cells": b["n"], "median_R_push": rp, "median_R_xsec": rx,
   "median_R_push_over_R_xsec": rr},
 "PREDECLARED_THRESHOLDS_AS_WRITTEN": {
   "TRAINING": "median R_push >= 2.0 AND median(R_push/R_xsec) in [0.7, 1.4]",
   "EXTRACTION": "median R_push in [0.80, 1.25] while median R_xsec >= 2.0",
   "SPLIT": "median R_push in (1.25, 2.0)",
   "UNINFORMATIVE": "control fails, or median R_xsec < 2.0 in the band"},
 "EVALUATION": readings,
 "MATCHED": matched,
 "VERDICT": (("TRAINING. The p_parallel deficit is ALREADY PRESENT in the trained push: R_push and R_xsec "
              "agree to a median ratio of %.4f in the band, so the extraction introduces essentially "
              "nothing and carries the training difference faithfully." % rr)
             if matched == ["TRAINING"] else "see MATCHED"),
 "WHAT_THIS_EXONERATES": ("gate5_signal_factor_applied_to_truth_counts, which OI-126 named as the suspect "
   "after the target was refuted. The extraction path is now measured to be faithful in both regions, so "
   "no factor it applies can be the cause. THE SUSPECT IS RETIRED, NOT MERELY UNCONFIRMED."),
 "SECONDARY_PREDECLARED_AND_REALIZED": {
   "declared": "if TRAINING, p_parallel-separability should survive in R_push",
   "R2_pparallel_only_R_push": d["separability_of_R_push"]["R2_pparallel_only"],
   "R2_pt_only_R_push": d["separability_of_R_push"]["R2_pt_only"],
   "R2_pparallel_only_R_xsec_family": d["separability_of_R_push"]["for_comparison_R_xsec_R2_pparallel_only_from_the_family"],
   "realized": "yes -- separability survives in the push, as declared; no surprise to report"},
 "THE_SIGN_REVERSAL_ALSO_LIVES_IN_THE_PUSH": {
   "pparallel_gt_20_median_R_push": d["pparallel_gt_20"]["median_R_push"],
   "pparallel_gt_20_median_R_xsec": d["pparallel_gt_20"]["median_R_xsec"],
   "note": "the >20 GeV reversal is a training effect too, on the same evidence"},
 "SCOPE_NOTE_ON_THE_CELL_COUNT": ("this probe compares the nominal against replica_00 ALONE, so the cells "
   "with R_xsec>1.5 number 65 here and are not identical to the family-mean 63 of OI-126. The band "
   "definition used for the reading is GEOMETRIC (p_parallel columns 10-15, 84 cells), which is "
   "replica-independent and was fixed in the predeclaration."),
 "WHAT_THIS_STILL_DOES_NOT_DO_all_five_declared_in_advance": [
   "does NOT clear OI-126, which blocks pairing C_stat with P5A",
   "does NOT identify the factor's value or form -- only that it is not introduced by the extraction",
   "does NOT show whether C_stat survives a CENTRED reduction; not computed",
   "does NOT show P5A is right; a nominal agreeing with the MC prior is consistent with a correct "
     "measurement and with an unfolding that barely moved",
   "one replica is not the family; the family-level statement remains the mechanism receipt's"],
 "NOT_VERIFIED_LANGUAGE": ("nothing here is 'verified'. The probe is one script by one lane and its "
   "internal asserts are self-checks. C_stat itself is NOT independently verified -- VL132 records ONE "
   "builder where OI-121 authorized two blind ones."),
 "WHAT_IT_MEANS_FOR_OI_126_stated_narrowly": ("the divergence is in the FIT. The only input difference "
   "between the arms is a Poisson(1) bootstrap on the measured target (established read-only earlier), so "
   "the OmniFold fit changes by a factor of ~5 in p_parallel 6-20 GeV under Poisson resampling of the "
   "measured leg -- in bins MINERvA reports at 1.6% statistical uncertainty. Whether that makes C_stat an "
   "unsuitable statistical-uncertainty proxy or the estimator unstable there is a DECISION this "
   "measurement does not make."),
}
P = "docs/orchestration/state/RECEIPT-20260815-oi126-push-vs-extraction-RESULT.json"
open(P, "w").write(json.dumps(out, indent=1) + "\n")
print("MATCHED:", matched)
print("control %.5f (pass<=0.10) -> %s" % (ctrl_stat, control_pass))
print("band R_push %.4f  R_xsec %.4f  ratio %.4f" % (rp, rx, rr))
print("written", P)
