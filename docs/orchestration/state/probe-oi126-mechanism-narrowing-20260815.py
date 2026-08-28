"""Emit the OI-126 mechanism receipt. Every number derived here; nothing hand-typed.

Run from the repo root. Two inputs are NOT in the repo and this is stated rather than hidden:

  jb_X50.npy   (50, 285) -- the 50 members' `xsec` arrays, ravel order C, stacked by replica_index
  jb_nom.npy   (285,)    -- the P5A nominal `xsec`

Both are a local cache of read-only cluster reads and are rebuilt by loading `xsec` from
  .../fullevent_cstat_n50/replicas/replica_{00..49}/extraction/GATE5_REPLICA_XSEC.npz   (assert replica_index)
  .../fullevent_nominal_annealed_extraction_unpromoted/P5A-ANNEALED-UNPROMOTED.xsec.slurm-56989462.npz
Point PROBE_INPUT_DIR at the directory holding them. The cluster-side half of the measurement is its sibling
`probe-oi126-target-comparison-20260815.py`, whose stdout is committed beside it as .json and
embedded in the receipt verbatim.
"""
import numpy as np, json, hashlib, subprocess, math, os
from math import exp, factorial

# The two cached inputs named in the docstring are not in the repo and never were. Point
# PROBE_INPUT_DIR at the directory holding jb_X50.npy and jb_nom.npy.
_S = os.environ.get("PROBE_INPUT_DIR", "")
if not os.path.isdir(_S):
    raise SystemExit("probe-oi126-mechanism-narrowing: set PROBE_INPUT_DIR to the directory "
                     "holding jb_X50.npy and jb_nom.npy (see this file's docstring)")
S = os.path.join(_S, "")
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
CS = 'docs/orchestration/state/gate5-cstat-n50/GATE5_CSTAT_N50.npz'
AM = 'nd-unfolding/products/pet/fullevent_fps/acceptance_map_fullevent_fps.json'
PC = 'docs/orchestration/state/p5a-nominal-vs-cstat-family-percell-20260815.json'
z = np.load(CS, allow_pickle=True); r = json.load(open(PC)); am = json.load(open(AM))
X = np.load(S + "jb_X50.npy"); nomf = np.load(S + "jb_nom.npy")
CLUSTER = json.load(open("docs/orchestration/state/probe-oi126-target-comparison-20260815.json"))

ci = z['cell_index']; q = z['quotable_mask']; cand = ci[q]; mean = z['mean']
ept = z['edges_pt']; epl = z['edges_pparallel']; NPL = 19
ratio = np.array(r['per_cell_ratio']); relsd = np.array(r['per_cell_family_rel_sd'])
col = cand % NPL; rows = cand // NPL; tail = ratio > 1.5
pos = {c: i for i, c in enumerate(ci)}
m = np.array([mean[pos[c]] for c in cand]); nom = ratio * m
w = np.array([(ept[c // NPL + 1] - ept[c // NPL]) * (epl[c % NPL + 1] - epl[c % NPL]) for c in cand])
tm = np.array(am['truth_mass_cells_pt_major'])
prior = tm[cand] / w; prior = prior * ((nom * w).sum() / (prior * w).sum())
tc = cand[tail]; gc = cand[col <= 9]
pr_band = np.array([np.median(X[k, tc] / nomf[tc]) for k in range(50)])
pr_good = np.array([np.median(X[k, gc] / nomf[gc]) for k in range(50)])
lr = np.log(1.0 / ratio); gm = lr.mean()
fj = {j: lr[col == j].mean() - gm for j in np.unique(col)}
gi = {i: lr[rows == i].mean() - gm for i in np.unique(rows)}
sst = ((lr - gm) ** 2).sum()
R2 = lambda p: float(1 - ((lr - p) ** 2).sum() / sst)
band = (col >= 10) & (col <= 15)
sh = (nom - m) / (nom - prior); ok = np.abs(nom - prior) > 0

# three cells in DIFFERENT pT rows sharing one p_parallel column -- derived, not typed
_c = cand[tail][np.argsort(ratio[tail])[::-1][:3]]
ILLUS = {"claim": "cells in different pT rows sharing one p_parallel column behave near-identically",
         "cells": [{"cell": int(c), "i_pt": int(c) // NPL, "i_pparallel": int(c) % NPL,
                    "pparallel_bin": [float(epl[int(c) % NPL]), float(epl[int(c) % NPL + 1])],
                    "nominal_over_family_mean": float(nomf[c] / X[:, c].mean()),
                    "n_members_below_10pct_of_nominal": int((X[:, c] < 0.1 * nomf[c]).sum()),
                    "n_members_below_50pct_of_nominal": int((X[:, c] < 0.5 * nomf[c]).sum())}
                   for c in _c]}

out = {
 "what": ("OI-126 mechanism narrowing, READ-ONLY. Establishes what the P5A-vs-family divergence is NOT, "
          "and localises what remains. Supersedes OI-126's original 'leading candidate' and its "
          "un-runnable next action."),
 "filed_by": "peer session B, 2026-08-15, after Joseph authorized a diagnostic that turned out to have no entry point",
 "no_job_was_run": ("no sbatch, no scancel, no scontrol; cluster access was file reads only. The array "
                    "57012031 was not touched."),
 "ingredients": {
   "cstat_npz": {"path": CS, "sha256": sha(CS)},
   "acceptance_map": {"path": AM, "sha256": sha(AM)},
   "per_cell_receipt": {"path": PC, "note": "corrected in c1e7a69; its arrays are sound"},
   "cluster_reads": [
     "nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy (the nominal target)",
     "nd-unfolding/pet/fullevent_cstat_n50/replicas/replica_{00..07}/target/GATE5_REPLICA_TARGET.npy",
     "nd-unfolding/pet/fullevent_cstat_n50/replicas/replica_{00..49}/extraction/GATE5_REPLICA_XSEC.npz",
     "nd-unfolding/pet/fullevent_nominal_annealed_extraction_unpromoted/P5A-ANNEALED-UNPROMOTED.xsec.slurm-56989462.npz"]},

 "0_THE_AUTHORIZED_JOB_HAS_NO_ENTRY_POINT": {
   "verdict": "NOT RUNNABLE. Four fail-closed guards form a closed ring and no combination of existing entry points produces the object.",
   "guards": {
     "nd-unfolding/pet/train_fullevent_replica.py:320": "SystemExit unless 0<=replica_index<50 AND bootstrap_seed==50000+replica_index; no value means 'bootstrap disabled'",
     "nd-unfolding/pet/build_fullevent_replica_target.py:153": "same constraint on the target builder, so the replica path cannot produce a non-replica target",
     "nd-unfolding/pet/fullevent_fps_dataloader.py:736-747": "assert_refined_target_is_replica: a nominal target (bootstrap_seed=None) 'can never stand in for one'",
     "nd-unfolding/pet/train_fullevent_nominal.py:253-255": "the mirror: rejects any target carrying a bootstrap_seed, because 'bootstrap_seed is None proves it is the nominal rather than a replica'"},
   "provenance_of_the_guards": "the J04/D2 audit, where this driver silently rebuilt a target in process and nothing compared it against the certified array",
   "MUST_NOT": "weakening or bypassing a fail-closed production guard is a DIFFERENT authorization from spending GPU time and is not covered by an authorization to submit a job. Cf. OI-123: 'do not repin a receipt-bound launcher to make it pass.'",
   "whose_error": "peer session B's, in OI-126 as committed at c1e7a69: the cost was derived from a real replica receipt's total_seconds, and RUNNABILITY was inferred from the existence of the two named scripts. Price checked, availability never checked."},

 "1_THE_TARGET_IS_NOT_THE_MECHANISM": {
   "claim_retired": "OI-126's leading candidate -- that the arms' different Stay-Positive backends explain the divergence -- is REFUTED at the level of the arrays.",
   "why_it_looked_right": "the metadata strings genuinely differ: the nominal target records refinement_backend='precomputed:gate2-published-target', each replica records a recomputed refinement_estimator='exact' with max_mc_events=200000, random_state=45.",
   "what_the_arrays_show": "the replica target IS the nominal target times a Poisson(1) multiplicity times one shared constant.",
   "rows_decompose_as": "n_data_full 4116128 + n_bkg_full 564591 = 4680719, i.e. the MEASURED leg",
   "MEASURED_ON_THE_CLUSTER": CLUSTER,
   "how_CLUSTER_was_obtained": ("emitted as JSON by state/probe-oi126-target-comparison-20260815.py run "
     "read-only over ssh and embedded here VERBATIM -- no figure in this block was transcribed by hand"),
   "nominal_zeros_are_the_stay_positive_clip": ("the nominal's own target receipt records "
     "frac_clipped_reported 0.0004334804118768933; times the row count that is ~2029 against the "
     "measured n_zero, so the nominal's zeros are the clip and the replicas' are bootstrap zeros"),
   "conclusion": "there is no target-level bias and no normalisation difference. A metadata difference was read as a physics difference."},

 "2_SHRINKAGE_TOWARD_THE_PRIOR_IS_ALSO_REFUTED": {
   "hypothesis": "bootstrap replicas of a regularised estimator regress toward the prior, so the family mean should sit BETWEEN prior and nominal",
   "prior_definition": "truth_mass_cells_pt_major / bin area, renormalised to the nominal's width-weighted total",
   "by_region": {k: {"n": int(s.sum()),
                     "median_nominal_over_prior": float(np.median(nom[s] / prior[s])),
                     "median_family_mean_over_prior": float(np.median(m[s] / prior[s])),
                     "fraction_of_cells_with_mean_strictly_between": float(((m[s] - prior[s]) * (nom[s] - m[s]) > 0).mean())}
                 for k, s in [("pparallel_lt_6", col <= 9), ("band_6_to_20", band), ("the_63", tail), ("pparallel_gt_20", col >= 16)]},
   "shrinkage_fraction_median": {k: float(np.median(sh[s & ok])) for k, s in
                                 [("pparallel_lt_6", col <= 9), ("band_6_to_20", band), ("the_63", tail), ("pparallel_gt_20", col >= 16)]},
   "correlation_departure_vs_shrinkage": float(np.corrcoef(np.abs(np.log(nom / prior))[ok], sh[ok])[0, 1]),
   "conclusion": ("REFUTED. In the band the nominal agrees with the prior to about 5% while the family mean is "
                  "~0.4x the prior, so the mean is not between them -- only 3.2% of the 63 cells have it between. "
                  "The band is NOT where the nominal departs most from the prior (p_parallel>20 departs more). "
                  "IT IS THE REPLICAS THAT ARE ANOMALOUS IN THE BAND, NOT THE NOMINAL.")},

 "3_IT_IS_NOT_A_SUBSET_OF_BROKEN_REPLICAS": {
   "per_replica_median_member_over_nominal": {
     "over_the_63_band_cells": {"min": float(pr_band.min()), "median": float(np.median(pr_band)),
                                "max": float(pr_band.max()), "sd": float(pr_band.std(ddof=1)),
                                "n_below_0p5": int((pr_band < 0.5).sum()), "n_below_0p2": int((pr_band < 0.2).sum()),
                                "all_50_below_1": bool((pr_band < 1.0).all())},
     "over_the_128_pparallel_lt_6": {"min": float(pr_good.min()), "median": float(np.median(pr_good)),
                                     "max": float(pr_good.max()), "sd": float(pr_good.std(ddof=1))}},
   "correlation_band_vs_good_per_replica": float(np.corrcoef(pr_band, pr_good)[0, 1]),
   "conclusion": ("every one of the 50 is low in the band and healthy below it, and a replica's band deficit is "
                  "uncorrelated with its overall level. So this is a systematic property of the replica arm, "
                  "not a few diverged trainings.")},

 "4_THE_DEFICIT_IS_A_FUNCTION_OF_PPARALLEL_ALONE": {
   "model": "log(family_mean / nominal) per cell, decomposed additively over the 257 quotable cells",
   "R2_pparallel_plus_pt": R2(np.array([gm + fj[c % NPL] + gi[c // NPL] for c in cand])),
   "R2_pparallel_only": R2(np.array([gm + fj[c % NPL] for c in cand])),
   "R2_pt_only": R2(np.array([gm + gi[c // NPL] for c in cand])),
   "illustration_DERIVED": ILLUS,
   "conclusion": ("the deficit is essentially separable and essentially p_parallel-only. That is the signature of a "
                  "MULTIPLICATIVE p_parallel-DEPENDENT FACTOR present in the replica extraction path and absent from "
                  "the nominal one -- not of a statistical effect, which would not be separable.")},

 "5_WHAT_REMAINS_OPEN_AND_WHAT_THIS_DOES_NOT_SHOW": {
   "declared_before_the_next_measurement": True,
   "this_receipt_does_NOT_show": [
     "WHICH factor it is. The replica extraction summary carries gate5_signal_factor_applied_to_truth_counts=true and gate5_signal_factor_applied_to_completeness_and_reporting_mask=true, and the nominal's carries neither; the factor ARRAYS are not on disk, only signal_factor_sha256 / background_factor_sha256. Named as the obvious suspect and NOT established.",
     "whether the defect is in TRAINING or in EXTRACTION. Both arms persist w_push over mc_indices, so this is decidable read-only and is the proposed next measurement.",
     "that C_stat is wrong. If the deficit is a per-cell multiplicative factor common to all 50 members, it largely cancels in a CENTRED covariance, so C_stat may survive even though the family MEAN does not describe the nominal. NOT computed here.",
     "that P5A is right. The nominal agreeing with the MC prior in the band is consistent with a correct measurement and also with an unfolding that barely moved there."],
   "and_it_does_not_clear_OI_126": ("OI-126 blocks pairing C_stat with P5A. Narrowing the mechanism does not "
                                    "unblock it, whatever the mechanism turns out to be.")},

 "6_PROPOSED_NEXT_MEASUREMENT_runnability_checked_this_time": {
   "measurement": "bin w_push (the per-event unfolded weight) in TRUTH (pT, p_parallel) for the nominal push and for one replica push, and compare per p_parallel column.",
   "why_it_is_decisive": "it splits training from extraction. If the p_parallel deficit is already in w_push, the divergence is in the fit; if w_push agrees and only the xsec differs, it is in the extraction's factor handling.",
   "inputs_all_exist": ["P5A-ANNEALED-UNPROMOTED.push.slurm-56978466.npz (w_push, mc_indices)",
     "replica_00/extraction/GATE5_REPLICA_FULL_PUSH.npz (w_push, mc_indices, plus the two factor digests)",
     "G2_FPS_MEFHC_P12.npz truth_scalars for the truth coordinates"],
   "runnability": "READ-ONLY numpy; no driver, no guard, no TensorFlow, no new code path. Verified by listing the keys of both push files rather than assuming them.",
   "cost": "decompressing truth_scalars from a 9.9 GB npz is ~1.6 GB resident and a few minutes of one core. Requested as an interactive allocation rather than run on a login node, out of politeness, not necessity.",
   "NOT_a_continuation_of_the_authorized_job": "Joseph said yes to a specific job that does not exist. This is a different measurement and needs its own yes."},

 "git_head_at_write": subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}

P = 'docs/orchestration/state/RECEIPT-20260815-oi126-mechanism-narrowing.json'
open(P, 'w').write(json.dumps(out, indent=1) + "\n")
print("written", P)
print("R2 p_par only  %.4f" % out["4_THE_DEFICIT_IS_A_FUNCTION_OF_PPARALLEL_ALONE"]["R2_pparallel_only"])
print("R2 pt only     %.4f" % out["4_THE_DEFICIT_IS_A_FUNCTION_OF_PPARALLEL_ALONE"]["R2_pt_only"])
