"""VL100 under a shape-corrected fold-forward: reproduction, correction scan, receipt.

Emits `RECEIPT-vl100-shape-corrected-foldforward-20260815.json` from committed operands only, so
the receipt is reproducible without cluster access:

  nd-unfolding/pet/annealed_shape_validation/NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-56552326.json
  docs/orchestration/state/vl100-foldforward-shape-test-20260814.json        (lane D's receipt)
  docs/orchestration/state/vl100-own-run-foldforward-20260815.json           (probe-vl100-own-run-foldforward)
  docs/orchestration/state/vl100-nominal-residual-field-20260815.json        (probe-vl100-nominal-residual-field)

WHY A FAMILY AND NOT A POINT. The recorded fold-forward quantity has NO per-cell reference -- R is
a single scalar (`step1_class_ratio`). So the record does not determine the sign or the magnitude
of a per-cell correction, and picking one and asserting it would be a choice presented as a
measurement. The correction is scanned:

    h_corr[c] proportional to h_unfolded[c] * (q[c]/<q>)**alpha,  then re-unit-normalized

WHICH FIELD q. Two candidates, and the choice is decided by an identity rather than a preference:

  (a) q = ratio[c], lane D's per-cell fold-forward ratio. REJECTED. By D's own definition ratio[c]
      is the w_reco-weighted mean of `push` in cell c; h_unfolded[c]/h_prior[c] is the
      w_truth-weighted mean of the SAME push in the SAME cell. They agree to Pearson 0.9997+.
      Dividing ratio[c] out therefore returns h_unfolded to h_prior -- a de-unfolding, whose
      recovery is 0 by construction. Demonstrated below rather than argued.
  (b) q = ratio[c] / (h_unfolded[c]/h_prior[c]). ADOPTED. The only content of ratio[c] that
      h_unfolded does not already carry: the weight-leg / population (acceptance-side) part.

Both are reported. Because h is re-unit-normalized after the correction, any alpha-independent
overall scale in q divides out and only its SHAPE enters -- which is the property under test.
"""
import hashlib
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLO = os.path.join(ROOT, "nd-unfolding/pet/annealed_shape_validation",
                   "NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-56552326.json")
DLANE = os.path.join(HERE, "vl100-foldforward-shape-test-20260814.json")
OWN = os.path.join(HERE, "vl100-own-run-foldforward-20260815.json")
NOMQ = os.path.join(HERE, "vl100-nominal-residual-field-20260815.json")
OUT = os.path.join(HERE, "RECEIPT-vl100-shape-corrected-foldforward-20260815.json")
ADOPTED = 0.49458240000000003
NC = 285


def l1(a, b):
    return float(np.abs(np.asarray(a, float) - np.asarray(b, float)).sum())


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


c = json.load(open(CLO))
dl = json.load(open(DLANE))
own = json.load(open(OWN))
nq = json.load(open(NOMQ))

h_prior = np.array(c["h_prior"], float)
h_target = np.array(c["h_target"], float)
h_unfold = np.array(c["h_unfolded"], float)
h_untilt = np.array(c["h_untilted"], float)
gap = l1(h_prior, h_target)
w = h_target / h_target.sum()

# the unfolding's own per-cell correction
u = np.full(NC, np.nan)
ok = h_prior > 0
u[ok] = h_unfold[ok] / h_prior[ok]


def normalize_field(q, reduction_mask):
    """q -> multiplicative field with mean 1 over the reduction; 1.0 where q is undefined."""
    m = np.isfinite(q) & (q > 0)
    red = m & reduction_mask
    f = np.where(m, q / float(q[red].mean()), 1.0)
    return np.where(np.isfinite(f) & (f > 0), f, 1.0), m, red


def recovery(alpha, f):
    h = h_unfold * (f ** alpha)
    h = h / h.sum()
    return 1.0 - l1(h, h_target) / gap


def distortion(alpha, f):
    """h_target-weighted relative sd of the applied field: a scale-free size for the correction."""
    g = f ** alpha
    m = float((w * g).sum())
    return float(np.sqrt((w * (g - m) ** 2).sum()) / m)


def crossings(f, span=40.0):
    out = {}
    for sgn in (-1.0, 1.0):
        lo, hi = 0.0, sgn * span
        if (recovery(hi, f) >= ADOPTED) == (recovery(lo, f) >= ADOPTED):
            out[f"{sgn:+.0f}"] = f"no crossing within |alpha| <= {span:.0f}"
            continue
        for _ in range(300):
            mid = 0.5 * (lo + hi)
            if recovery(mid, f) >= ADOPTED:
                lo = mid
            else:
                hi = mid
        a = 0.5 * (lo + hi)
        out[f"{sgn:+.0f}"] = {"alpha_at_crossing": a, "amplitude_multiple_of_measured": abs(a),
                              "applied_distortion_at_crossing": distortion(a, f)}
    return out


def scan(f):
    return [{"alpha": a, "recovery": recovery(a, f), "margin_vs_adopted": recovery(a, f) - ADOPTED,
             "clears": bool(recovery(a, f) >= ADOPTED), "applied_distortion_rel_sd": distortion(a, f)}
            for a in (-4.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 4.0)]


g_own = own["own_run_truth_grid"]
r_own = np.array([np.nan if x is None else x for x in g_own["per_cell_ratio"]], float)
ne_own = np.array(g_own["per_cell_n_eff"], float)

# (a) the REJECTED field: D's ratio used directly, on VL100's own run
f_full, _, _ = normalize_field(r_own, np.array(g_own["per_cell_in_summary"], bool))
h_m1 = h_unfold * f_full ** -1.0
h_m1 /= h_m1.sum()

# (b) the ADOPTED field: the residual, on VL100's own run and on the nominal run
q_own = np.full(NC, np.nan)
mo = np.isfinite(r_own) & np.isfinite(u) & (u > 0)
q_own[mo] = r_own[mo] / u[mo]
f_own, m_own, red_own = normalize_field(q_own, ne_own >= 50)

q_nom = np.array([np.nan if x is None else x for x in nq["per_cell_q"]], float)
nea = np.array(nq["per_cell_ne_reco"], float)
neb = np.array(nq["per_cell_ne_truth"], float)
f_nom, m_nom, red_nom = normalize_field(q_nom, (nea >= 50) & (neb >= 50))


def field_stats(q, m, red):
    qq = q[red]
    return {"n_cells_with_q": int(m.sum()), "n_cells_in_reduction": int(red.sum()),
            "q_min": float(qq.min()), "q_max": float(qq.max()), "q_mean": float(qq.mean()),
            "q_rel_sd": float(qq.std(ddof=1) / qq.mean()),
            "h_target_mass_where_q_defined": float(h_target[m].sum()),
            "cells_given_factor_1_because_q_undefined": int((~m).sum()),
            "h_target_mass_in_those_cells": float(h_target[~m].sum())}


R = {
 "what": ("VL100 recomputed under a shape-corrected fold-forward, and whether the annealed arm "
          "still clears its adopted criterion."),
 "produced_by": ("peer Claude session (Opus 5), read-only. No job submitted, cancelled or "
                 "scontrol'd; the cluster was touched by two read-only python reads over ssh. "
                 "Authorized to land by the mediator (`personal-orchestrator`)."),
 "measured_utc_date": "2026-08-15",

 "VERDICT": (
  "TWO RESULTS, AND THE FIRST IS NOT THE MARGIN. (1) VL100's own run does not exhibit the "
  "fold-forward deficit at all -- measured ratio 1.011418 against the nominal run's 0.736746 -- so "
  "the closure that certifies the annealed arm does not exercise the failure mode, and is SILENT "
  "about it rather than reassuring. (2) The arm still clears: under the only well-posed correction "
  "recovery moves from 0.512603276 to 0.511140 / 0.513984, margin 0.016557 at worst; under the "
  "adversarial field taken from the run where the deficit lives, to 0.515176 / 0.509074, and 2.8x "
  "the measured amplitude is needed to break the criterion."),

 "WHAT_THIS_DOES_NOT_SAY": [
  "It does not close OI-71. Every correction computable from disk is POST-HOC and multiplicative on "
  "h_unfolded. The fold-forward acts in iterations 2 and 3 of 3, so a defect that mis-delivered "
  "weight DURING training is baked into `push` itself and no reweighting of h_unfolded can probe "
  "it. Only a retrained closure answers that, and none was submitted.",
  "It does not say the nominal run's 34% fold-forward deficit is benign or explained. That scalar "
  "discrepancy (ratio 0.736746250130697 vs R 1.1240802949941018, dev 0.3445786271570904) is "
  "untouched here. What is explained is its per-cell STRUCTURE, not its magnitude.",
  "It says nothing about the three hygiene quotability grounds -- not examined here, and not by "
  "lane D either.",
  "It does not say lane D's arithmetic is wrong. D's published numbers reproduce EXACTLY: rel_sd "
  "0.47021238590619524 to the last digit, global ratio to 1.5e-13. The arithmetic is not in "
  "question; the target is.",
  "The alignment control, the Pearson coefficients and the reproduction to 1.3e-10 are MEASUREMENTS "
  "MADE BY THIS SESSION and were not independently checked by the mediator, who verified only the "
  "arm error. They are shipped with their operands so they can be contradicted."],

 "reproduction_of_the_published_number": {
  "method": ("the producer's own definitions, closure_powered_truth_reweight.py:339-345, applied to "
             "the persisted 285-cell spectra"),
  "gap_L1_prior_target": gap,
  "floor_L1_prior_untilted": l1(h_prior, h_untilt),
  "residual_L1_unfolded_target": l1(h_unfold, h_target),
  "recovery_1_minus_residual_over_gap": 1.0 - l1(h_unfold, h_target) / gap,
  "published_recovery": c["metrics"]["recovery"],
  "abs_difference": abs((1.0 - l1(h_unfold, h_target) / gap) - c["metrics"]["recovery"]),
  "adopted_criterion": ADOPTED,
  "criterion_operands": {"f": 0.8, "acceptance_limited_ceiling": 0.618228,
                         "product": 0.8 * 0.618228},
  "margin": (1.0 - l1(h_unfold, h_target) / gap) - ADOPTED,
  "spectra_sums": {k: float(np.array(c[k], float).sum())
                   for k in ("h_prior", "h_target", "h_unfolded", "h_untilted")}},

 "alignment_control": {
  "why": ("`weights_push` is aligned to half B, whose global row ids are `dump_rows_b`. "
          "deterministic_halves returns SORTED index sets and mc_indices is sorted, so the pairing "
          "push[j] <-> dump_rows_b[j] is determined rather than guessed. If it is right, rebuilding "
          "the spectra from the artifact reproduces the published arrays."),
  "recovery_rebuilt_from_push_and_rows": (
   1.0 - l1(np.array(own["rebuilt"]["h_unfolded"], float), h_target)
   / l1(np.array(own["rebuilt"]["h_prior"], float), h_target)),
  "published": c["metrics"]["recovery"],
  "max_relative_deviation_over_cells_with_mass": float(np.max(
   np.abs(np.array(own["rebuilt"]["h_unfolded"], float)[h_unfold > 0] - h_unfold[h_unfold > 0])
   / h_unfold[h_unfold > 0])),
  "residual_explained_by": ("the loader rescales both weight legs in float32; per-element rounding "
                            "does not fully cancel under unit normalization, giving ~1e-9..1e-8 "
                            "relative. A WRONG pairing would move h_unfolded by of order its own "
                            "bin values (1e-3), not 1e-10.")},

 "scope_errors_in_the_falsification": {
  "run": {
   "D_decomposed": "nd-unfolding/pet/fullevent_nominal/pet_fullevent_nominal_weights.npz",
   "VL100_comes_from": "annealed_shape_validation job 56552326",
   "D_n_pass_reco": dl["n_pass_reco"],
   "closure_n_step1_a": c["samples"]["n_step1_a"],
   "closure_n_step1_b": c["samples"]["n_step1_b"],
   "closure_pass_reco_b_measured_here": own["counts"]["pass_reco_b"],
   "reading": ("837671 matches no closure half, so the decomposition is of neither. The GRID is "
               "VL100's; the WEIGHTS are another run's.")},
  "arm": {
   "found_by": "the mediator (`personal-orchestrator`); re-measured independently by this session",
   "pre_anneal": {"path": "nd-unfolding/pet/fullevent_nominal/pet_fullevent_nominal_weights.npz",
                  "sha256": "58f664cdef266d09cbae22a55698f6ff0059ecde4bef80681df9f907f2f51084",
                  "seed_policy_has_lr_policy_key": False,
                  "seed_policy_keys": ["batch_size", "epochs", "estimator_seed", "niter",
                                       "subsample_seed", "train_events"]},
   "promoted_annealed": {
    "path": "nd-unfolding/pet/fullevent_nominal_annealed/pet_fullevent_nominal_weights.npz",
    "sha256": "559a1020570929169a83e26dd9eea937bb34d6f4ecb230e332b792165ef6eb3e",
    "seed_policy_has_lr_policy_key": True,
    "lr_policy_schedule": "fit-time-anneal-after-iteration-0"},
   "reading": ("VL100 is the ANNEALED arm's recovery, and D's probe line 46 reads the PRE-ANNEAL "
               "arm's weights. Two sibling directories hold identically-named files. This is the "
               "fifth instance of that trap."),
   "the_remedy_already_exists": {
    "site": "nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh:153-182 (guard G1)",
    "mechanism": ("assert seed_policy.lr_policy.schedule == 'fit-time-anneal-after-iteration-0'. "
                  "The pre-anneal artifact has NO lr_policy key, so it fails loudly rather than "
                  "comparing unequal values -- and it catches a wrong arm whatever the path."),
    "timeline_CORRECTED": ("the guard landed at d184f95, 2026-08-14 19:56:51 -0400; D's "
                           "falsification is f4267b4, 19:50:07 -0400. The guard is 6m44s LATER, so "
                           "it was NOT available to D -- two lanes hit the same trap inside ten "
                           "minutes, one building the guard and one falling in. It WAS available to "
                           "every reader afterward, including the propagation into three places.")}}},

 "the_structural_result": {
  "claim": ("lane D's per-cell 'fold-forward ratio' is definitionally a per-cell weighted mean of "
            "`push` -- the reweighting function itself, binned. h_unfolded[c]/h_prior[c] is the "
            "same weighted mean over the other leg. They differ only by weight leg (w_reco vs "
            "w_truth) and population (pass_reco vs pass_truth), so they are ONE statement, not two."),
  "measured_on_the_run_D_decomposed": {
   "pearson_r": 0.9997339359499255, "spearman_r": 0.99937223322618,
   "D_field_rel_sd": 0.47021238590619524,
   "unfolding_correction_rel_sd": 0.4658785086788078,
   "ratio_of_the_two": {"min": 0.9331088530120111, "max": 1.0196253375899818,
                        "mean": 0.9903634143150898, "rel_sd": 0.014410233396475573}},
  "measured_on_VL100s_own_run": {
   "pearson_r": own["ratio_vs_unfolding_correction"]["pearson_r"],
   "spearman_r": own["ratio_vs_unfolding_correction"]["spearman_r"],
   "ratio_of_the_two": own["ratio_vs_unfolding_correction"]["ratio_x_over_y"]},
  "why_the_68x_framing_persuaded": ("the null it tests is 'push is flat across the grid', which is "
                                    "the negation of unfolding working at all. ANY real reweighting "
                                    "beats sampling noise by that factor, so the comparison cannot "
                                    "discriminate a deficit from the answer."),
  "consequence_dividing_it_out_is_a_de_unfolding": {
   "recovery_of_h_prior_by_construction": 1.0 - l1(h_prior, h_target) / gap,
   "recovery_at_alpha_minus_1_using_D_field_on_VL100s_own_run": recovery(-1.0, f_full),
   "L1_of_that_result_to_h_prior": l1(h_m1, h_prior),
   "L1_of_h_unfolded_to_h_prior": l1(h_unfold, h_prior),
   "fraction_of_the_unfoldings_own_distance_remaining": l1(h_m1, h_prior) / l1(h_unfold, h_prior),
   "reading": ("the operation returns the unfolded spectrum to within 2.4% of the prior, whose "
               "recovery is 0 by construction. That is a de-unfolding, not a correction.")},
  "the_two_runs_fields_are_nearly_uncorrelated": {
   "pearson_r": 0.140996, "spearman_r": 0.194938,
   "reading": ("a shared fold-forward DEFECT would make them agree; each being dominated by its own "
               "learned reweighting would not.")}},

 "VL100s_own_run_does_not_exercise_the_deficit": {
  "measured_fold_forward_ratio_own_run": g_own["global_ratio_all_pass_reco"],
  "nominal_run_recorded_ratio": dl["recorded"]["ratio"],
  "nominal_run_R": dl["recorded"]["R"],
  "nominal_run_dev": dl["recorded"]["dev_abs"],
  "receipt_chain_hole": ("the closure recorded NO step1_class_ratio and NO fold_forward scalars -- "
                         "not in NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-56552326.json, "
                         "not in PREFLIGHT.slurm-56552326.json, not in the 47/47 "
                         "INDEPENDENT_VALIDATION.slurm-56562169.json. So NO dev can be formed for "
                         "VL100's run from the record at all. The 1.011418 above is a measurement "
                         "made by this session, not a recorded value. Filed as OI-125."),
  "reading": ("a validation that does not reproduce the fold-forward behaviour of the run producing "
              "the physics is SILENT about that failure mode, not reassuring about it. This is "
              "upstream of whether the margin clears.")},

 "correction_family": {
  "applied_as": ("h_corr[c] proportional to h_unfolded[c] * (q[c]/<q>)**alpha, re-unit-normalized. "
                 "alpha=0 is as published; alpha=-1 divides the measured field out; alpha=+1 "
                 "applies it again. Cells where q is undefined get factor 1.0."),
  "why_a_family": ("the recorded fold-forward quantity has no per-cell reference (R is one scalar), "
                   "so neither the sign nor the magnitude of a per-cell correction is determined by "
                   "the record."),
  "distortion_metric": "h_target-weighted relative sd of the applied multiplicative field",
  "adopted_field": ("q = ratio[c] / (h_unfolded[c]/h_prior[c]) -- the only content of ratio[c] that "
                    "h_unfolded does not already carry"),
  "rejected_field": ("q = ratio[c] directly -- rejected because it is a de-unfolding, demonstrated "
                     "under the_structural_result above, not asserted")},

 "results": {
  "adopted_field_VL100_own_run": {
   "field_stats": field_stats(q_own, m_own, red_own), "scan": scan(f_own),
   "criterion_crossings": crossings(f_own)},
  "adopted_field_NOMINAL_run_ADVERSARIAL": {
   "note": ("the nominal run is where the 34% deficit actually lives, and its residual field is 2.8x "
            "the amplitude of the closure's own -- so this is the adversarial application"),
   "field_stats": field_stats(q_nom, m_nom, red_nom), "scan": scan(f_nom),
   "criterion_crossings": crossings(f_nom)},
  "margin_headroom": {
   "margin": (1.0 - l1(h_unfold, h_target) / gap) - ADOPTED,
   "reading": ("the margin is thin in absolute terms -- an adversarially-aligned shape distortion of "
               "a few percent consumes it -- but the MEASURED residual field is 0.52% (own run) to "
               "1.44% (nominal run), a factor of 2.8 to 11 below the crossing.")}},

 "artifacts_read": [
  {"path": os.path.relpath(CLO, ROOT), "sha256": sha256(CLO)},
  {"path": os.path.relpath(DLANE, ROOT), "sha256": sha256(DLANE)},
  {"path": os.path.relpath(OWN, ROOT), "sha256": sha256(OWN)},
  {"path": os.path.relpath(NOMQ, ROOT), "sha256": sha256(NOMQ)},
  {"path": ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/annealed_shape_validation/"
            "NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-56552326.npz"),
   "sha256_declared_by_producer": c["artifact"]["sha256"],
   "note": "read remotely; hash not recomputed by this session"},
  {"path": ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal/"
            "pet_fullevent_nominal_weights.npz"),
   "sha256": "58f664cdef266d09cbae22a55698f6ff0059ecde4bef80681df9f907f2f51084",
   "note": "the run lane D decomposed; PRE-ANNEAL arm"},
  {"path": ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/"
            "G2_FPS_MEFHC_P12.npz"),
   "sha256_declared_by_closure": c["source"]["inputs_sha256"],
   "note": "read remotely; hash not recomputed by this session"}],
}

with open(OUT, "w") as fh:
    json.dump(R, fh, indent=1, sort_keys=True)
    fh.write("\n")
print(f"wrote {OUT}")
print(f"  recovery reproduced : {R['reproduction_of_the_published_number']['recovery_1_minus_residual_over_gap']!r}")
print(f"  published           : {R['reproduction_of_the_published_number']['published_recovery']!r}")
print(f"  worst margin |alpha|<=1, own field    : "
      f"{min(s['margin_vs_adopted'] for s in R['results']['adopted_field_VL100_own_run']['scan'] if abs(s['alpha']) <= 1)!r}")
print(f"  worst margin |alpha|<=1, adversarial  : "
      f"{min(s['margin_vs_adopted'] for s in R['results']['adopted_field_NOMINAL_run_ADVERSARIAL']['scan'] if abs(s['alpha']) <= 1)!r}")
