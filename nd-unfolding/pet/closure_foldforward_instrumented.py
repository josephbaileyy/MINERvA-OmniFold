#!/usr/bin/env python3
"""Powered closure with the fold-forward RECORDED per iteration -- OI-125 / BEN-312.

WHY THIS IS A SEPARATE MODULE AND NOT AN EDIT TO THE CLOSURE DRIVER. That was the first attempt and
the repo refused it, correctly. `closure_powered_truth_reweight.py` hashes to
`a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48`, and that value is pinned by FOUR
launchers (`sbatch_powered_closure.sh`, `sbatch_powered_closure_stability_repeat.sh`,
`sbatch_powered_closure_budget_probe.sh`, `sbatch_finalize_annealed_shape_validation.sh`) and bound by
run receipts -- including `NONQUOTABLE-DIAGNOSTIC.INDEPENDENT_VALIDATION.slurm-56562169.json`, whose
`hash:source-driver` check reads that exact digest. An in-place edit turned two tests red
(`test_hash_bindings::test_no_new_broken_hash_bindings` and
`test_powered_closure_preflight::…code_pins_are_discoverable…`: *"pin is stale"*) and would have made
the 47/47 validation un-re-derivable at HEAD. **Repinning to make it pass is prohibited while
receipts bind it** (BEN-270, and `docs/orchestration/HANDOFF-20260815-0455Z.md`'s `OI-123` note).

So this follows the pattern the campaign already uses for exactly this problem:
`closure_powered_annealed_lr.py` adds the LR anneal without touching the engine OR the driver, by
rebinding `omnifold.MultiFold` to a subclass and then calling `cpt.main`. This module does the same
for the fold-forward, and composes with that one.

WHAT IT RECORDS, and why per iteration. `RunStep1(i)` consumes
`weights_push * mc_weight_reco * mc.pass_reco` as its MC-class weight, where `weights_push` is
whatever `RunStep2(i-1)` left (all ones at `i == start`). That IS the fold-forward, measured at the
point of consumption. The fold-forward acts in iterations 2 and 3 of 3, so ONE END-OF-RUN SCALAR
CANNOT SAY WHICH ITERATION DRIFTED -- which is why `OI-125` is a defect rather than a formatting
preference, and why iteration 0 is reported but is not a measurement of the estimator (`push == 1`
there makes its deviation `|1/R - 1|` by construction).

PURELY ADDITIVE. It reads two arrays per iteration and delegates. No weight, model or metric changes,
so an instrumented arm MUST reproduce an uninstrumented one within the measured draw spread
(`sd 0.000820128` over three draws). That reproduction is the control on any run using this; see
`docs/orchestration/PROPOSAL-20260815-instrumented-and-corrected-foldforward-closure.md`.

NOT AUTHORIZED TO RUN. `p3f-pet-gate4-nominal-promotion-56563761.json` lists *"any recovery run"*
under `scope_PROMOTED_IS_NOT_PROCEED.NOT_authorized` and requires a fresh authorization from Joseph.
This module exists so that the decision is about a reviewed instrument, not a promise.

    python3 -u closure_foldforward_instrumented.py --json <out.json> --artifact <out.npz> \
        --weights-folder <dir> [--annealed] [... any closure_powered_truth_reweight flag]
"""
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ND = os.path.dirname(_HERE)
_REPO = os.environ.get("MNV_REPO") or os.path.dirname(_ND)
for _p in (os.path.join(_REPO, "omnifold_nn"), _ND, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def step1_class_ratio(data, mc):
    """R for THIS closure, computed from ITS OWN loaders. Never inherited from loader meta.

    R is the step-1 class ratio `RunStep1` implicitly compares against: the data class carries
    `data.weight * data.pass_reco`, the MC class `weights_push * mc_weight_reco * mc.pass_reco`, so at
    `push == 1` the ratio of class totals is

        sum(data.weight[data.pass_reco]) / sum(mc_weight_reco[mc.pass_reco])

    DO NOT take this from `meta["target"]["step1_class_ratio"]`. That describes the NOMINAL target;
    this closure builds `pdata` from half A with an injected tilt and `mcB` from half B, so the meta's
    R is another configuration's number. Inheriting it would restate a quantity measured elsewhere as
    if it were this run's -- the same class of error as `BEN-312`, one field over, where the
    quarantine manifest's `weights_path` named another run and its `recomputed_from` field then
    truthfully asserted rigour about the wrong target.

    Reco leg per D1, with the single-leg fallback `MultiFold.Unfold` itself uses.
    """
    d_w = np.asarray(data.weight, np.float64)
    d_pr = np.asarray(data.pass_reco).astype(bool)
    m_leg = getattr(mc, "weight_reco", None)
    m_w = np.asarray(mc.weight if m_leg is None else m_leg, np.float64)
    m_pr = np.asarray(mc.pass_reco).astype(bool)
    num, den = float(d_w[d_pr].sum()), float(m_w[m_pr].sum())
    if not den > 0:
        raise SystemExit("[ff] step-1 MC class total is not positive; the class ratio is undefined "
                         "(fail closed)")
    return num / den


def install_fold_forward_recorder(base, correct=False):
    """Return `(subclass_of_base, records)` recording the fold-forward entering each iteration.

    `correct=False` is ARM 0: record only, change nothing. `correct=True` is ARM 1: additionally
    rescale `weights_push` by the single scalar `R / ratio` BEFORE step 1 consumes it, so the
    fold-forward conserves the step-1 class ratio.

    THE CORRECTION IS SCALE-ONLY, PREDECLARED, AND THAT IS NOT A STYLE CHOICE. A per-cell correction
    built from `push` would be dividing out the unfolding's own per-cell output -- `ratio[c]` agrees
    with `h_unfolded[c]/h_prior[c]` at Pearson 0.99973/0.99987 -- which is a DE-UNFOLDING and returns
    recovery to ~0 by construction (BEN-310, measured at -0.000808). A later reader will be tempted to
    "improve" this to per-cell; `test_correction_is_a_pure_scalar` is the guard. Refuse it unless a
    per-cell reference exists in the record, which as of 2026-08-15 it does not: R is one scalar.

    Order matters and is tested. The rescale happens BEFORE `super().RunStep1(i)`, because that is
    where the engine reads `weights_push`; applied afterwards it would change no training at all and
    arm 1 would be a silent no-op. The RECORDED ratio stays the PRE-correction measurement, so arm 1
    still measures the fold-forward rather than only its own fixed point.

    SUBCLASSES THE CLASS IT IS HANDED, and that is the load-bearing property, not a style choice.
    `closure_powered_annealed_lr.py` rebinds `omnifold.MultiFold` to its `AnnealedMultiFold` before
    the driver resolves the name, so a recorder that derived from the engine class directly would sit
    BESIDE the anneal instead of on top of it and silently un-anneal the run -- the same silent no-op
    that driver's docstring was written to prevent, one layer down. Composition gives MRO
    recorder -> annealed -> engine. Power-tested: a variant deriving from a hardcoded ancestor turns
    `test_recorder_subclasses_the_base_it_is_handed` red.
    """
    records = []
    step2_records = []

    class FoldForwardRecordingMultiFold(base):
        def RunStep1(self, i):
            leg = getattr(self, "mc_weight_reco", None)
            if leg is None:                      # mirrors Unfold's own single-leg fallback
                leg = self.mc.weight
            w = np.asarray(leg, np.float64)
            push = np.asarray(self.weights_push, np.float64)
            pr = np.asarray(self.mc.pass_reco).astype(bool)
            num = float((w[pr] * push[pr]).sum())
            den = float(w[pr].sum())
            ratio = (num / den) if den > 0 else None
            R = step1_class_ratio(self.data, self.mc)
            records.append({
                "iteration": int(i),
                "sum_w_push_reco": num,
                "sum_w_reco": den,
                "reco_weighted_mean_push": ratio,
                "n_pass_reco": int(pr.sum()),
                "step1_class_ratio": R,
                "deviation_from_R": (abs(ratio / R - 1.0) if ratio is not None else None),
                "push_entering_this_iteration_left_by": (
                    "initialization (all ones)" if i == getattr(self, "start", 0)
                    else f"RunStep2({int(i) - 1})"),
                "correction_requested": bool(correct),
                "applied_correction_factor": None,
                "reco_weighted_mean_push_after_correction": None,
                # CAPTURED SO THE ANNEAL ATTESTATION IS NOT SELF-REFERENTIAL. `self.LR` is the
                # engine's own base rate (omnifold.py:127, defaulted to 1e-4 at :57 and never
                # overridden by closure_powered_truth_reweight.py's MultiFold call), and `self.start`
                # is the iteration boundary the anneal keys on (omnifold.py:115). Reading them from
                # the live instance is what lets `attest_anneal_took_effect` compare observed fit
                # rates against a DECLARED value instead of against the maximum of its own records --
                # see that function for why the difference matters. BEN-317.
                "engine_declared_LR": float(getattr(self, "LR", float("nan"))),
                "anneal_start": int(getattr(self, "start", 0)),
            })
            if correct:
                if ratio is None or not ratio > 0:
                    raise SystemExit(f"[ff] iteration {i}: fold-forward ratio is {ratio!r}; the "
                                     f"scale-only correction is undefined (fail closed)")
                factor = R / ratio
                # ONE scalar over every row -- the shape of push is untouched by construction.
                # DTYPE IS PRESERVED, AND THIS COST A FAILED TASK AND ~2 MINUTES OF GPU.
                # `weights_push` is float32 (omnifold.py:164,168). `factor` is a Python float, so
                # `array * factor` promotes to float64; the engine then packs the weights into
                # column 1 of y_true (omnifold.py:360, np.stack) and
                # net.weighted_binary_crossentropy:13 multiplies them against float32 logits, which
                # dies inside a tf.function with `Input 'y' of 'Mul' Op has type float64`. Job
                # 57012031_3 died exactly there, in ITERATION 1 / RUNNING STEP 1 -- the first place
                # the corrected weights meet the loss.
                #
                # THE TRAP WAS ALREADY DOCUMENTED, in the docstring of the driver this module wraps
                # ("FLOAT32 INTO THE ENGINE", closure_powered_truth_reweight.py), which even asserts
                # the dtype of the two LOADER weight arrays. Nothing asserted it for `weights_push`,
                # because that array is engine-internal and nothing outside the engine had ever
                # written to it. This module is the first thing that does.
                prev = np.asarray(self.weights_push)
                corrected = (prev * factor).astype(prev.dtype, copy=False)
                if corrected.dtype != prev.dtype:
                    raise SystemExit(f"[ff] iteration {i}: correction changed weights_push dtype "
                                     f"{prev.dtype} -> {corrected.dtype}; the engine's loss "
                                     f"requires float32 (fail closed)")
                self.weights_push = corrected
                after = float((w[pr] * np.asarray(self.weights_push, np.float64)[pr]).sum() / den)
                records[-1]["applied_correction_factor"] = factor
                records[-1]["reco_weighted_mean_push_after_correction"] = after
            return super().RunStep1(i)

        def RunStep2(self, i):
            """Record the push RunStep2 LEAVES, which is the only way the end-of-run value is seen.

            WHY THIS HOOK EXISTS AND THE RunStep1 ONE IS NOT ENOUGH. `Unfold` is
            `for i in range(start, niter): RunStep1(i); RunStep2(i); CompileModels(fixed=True)`
            (omnifold.py:172-177), and `RunStep2` assigns `self.weights_push` at :220. So the
            RunStep1 hook, which records at the point of CONSUMPTION, sees the pushes left by
            initialisation, `RunStep2(0)` and `RunStep2(1)` -- and **the push left by
            `RunStep2(niter-1)` is consumed by nothing and recorded by no row.** That last one is
            the quantity `OI-125` is about, because
            `closure_powered_truth_reweight.py:332-333` takes `of.weights_push` AFTER `Unfold()`
            returns, and `train_fullevent_nominal.py:576-577` computes the nominal's fold-forward
            the same way. Reading the last RunStep1 row instead gives 0.981165 against a predicted
            1.011418 -- a ~105-draw-sd 'disagreement' with the sign of ratio-1 flipped, which is an
            artefact of the substitution (BEN-360, VL134).

            BIT-IDENTITY WITH WHAT THE DRIVER PERSISTS IS THE POINT, and it holds because nothing
            between this hook and the driver's read touches the array: the loop's trailing
            `CompileModels(fixed=True)` only recompiles models. Asserted rather than reasoned in
            `test_the_final_capture_is_BIT_IDENTICAL_to_what_the_driver_persists`, which also shows
            a pre-delegation capture FAILING the same assertion so the test has power (BEN-314).

            The first `niter-1` of these rows DUPLICATE RunStep1 rows by construction -- the push
            `RunStep2(i)` leaves is exactly the push `RunStep1(i+1)` consumes -- and that redundancy
            is deliberate: it is a free internal cross-check, gated in `main`. It holds for BOTH
            arms, because the RunStep1 row records the PRE-correction measurement (the record is
            appended before `if correct:` runs).
            """
            out = super().RunStep2(i)
            rec = self._ff_reduce(int(i))
            rec["hook"] = "RunStep2"
            rec["push_recorded_here_was_left_by"] = f"RunStep2({int(i)})"
            rec["is_end_of_run_push"] = bool(int(i) == int(getattr(self, "niter", -1)) - 1)
            step2_records.append(rec)
            return out

        def _ff_reduce(self, i):
            """The reduction, in ONE place so both hooks cannot drift apart.

            Extracted 2026-08-16 rather than copied: two hooks computing 'the same' fold-forward from
            two blocks of similar arithmetic is how the overlapping rows would silently stop agreeing,
            and the cross-check that compares them would then be comparing two implementations
            instead of two points in time.
            """
            leg = getattr(self, "mc_weight_reco", None)
            if leg is None:
                leg = self.mc.weight
            w = np.asarray(leg, np.float64)
            push = np.asarray(self.weights_push, np.float64)
            pr = np.asarray(self.mc.pass_reco).astype(bool)
            num = float((w[pr] * push[pr]).sum())
            den = float(w[pr].sum())
            ratio = (num / den) if den > 0 else None
            R = step1_class_ratio(self.data, self.mc)
            return {
                "iteration": int(i),
                "sum_w_push_reco": num,
                "sum_w_reco": den,
                "reco_weighted_mean_push": ratio,
                "n_pass_reco": int(pr.sum()),
                "step1_class_ratio": R,
                "deviation_from_R": (abs(ratio / R - 1.0) if ratio is not None else None),
                "engine_declared_LR": float(getattr(self, "LR", float("nan"))),
                "anneal_start": int(getattr(self, "start", 0)),
            }

    FoldForwardRecordingMultiFold.FOLD_FORWARD_STEP2_RECORDS = step2_records
    return FoldForwardRecordingMultiFold, records


FOLD_FORWARD_NOTE = (
    "Recorded at the point of CONSUMPTION: RunStep1(i) takes weights_push * mc_weight_reco * "
    "mc.pass_reco as its MC-class weight, so iteration i reports the push RunStep2(i-1) left. At "
    "i=0 push is all ones, which makes that row's deviation |1/R - 1| BY CONSTRUCTION and not a "
    "measurement of the estimator -- read iterations 1 and 2. Reco leg per D1. step1_class_ratio is "
    "derived from THIS run's pdata/mcB and is NOT meta['target']['step1_class_ratio'], which "
    "describes the nominal target rather than this A/B split with an injected tilt (BEN-312). The "
    "closure driver itself is UNMODIFIED and still hashes to its pinned "
    "a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48."
)


def annotate_nonquotability(rep, json_path, artifact_path=None):
    """Carry non-quotability as a FIELD, not only in the filename and `artifact.path`.

    THE GAP THIS CLOSES. Every product this module has written so far says NONQUOTABLE-DIAGNOSTIC in
    two places -- the report's own basename and the `.npz` path echoed at `artifact.path` -- and
    NOWHERE ELSE. A consumer that loads the JSON and keys off fields (which is what a consumer
    should do; `build_cstat_gate5_n50.FORBIDDEN_SUBSTR` keying off a filename substring is the
    fragile form, not the model) sees a report with a `recovery` and no marking at all. The six
    receipts of 2026-08-15 are left as they are -- they are the record -- so this affects future
    ones only.

    `label` IS THE FIELD AND THAT IS NOT AN ARBITRARY CHOICE: `pet_diagnostic_quarantine.
    require_quotable:156` already refuses any manifest whose `label` is `DIAGNOSTIC_LABEL`, and
    `fps_provenance:297` requires `PUBLICATION_LABEL` before it will treat one as publication. So
    the key is one an existing consumer acts on, rather than a new boolean nobody reads.

    AND THE FLAG IS NOT THE MECHANISM. That module's docstring is explicit that writing
    `publication_gate_rejects_this: true` is a CLAIM and that its gate therefore recomputes the
    physics instead of reading the flag -- hand-flipping the boolean, moving the file, or stripping
    the marker must all fail to make a product quotable. Nothing here weakens that: this records
    two separable things, (a) that a product of THIS module is non-quotable by construction, which
    is true of the module rather than of any run, and (b) whether the filename marker is actually
    present, which is MEASURED off the paths and may read false. They are kept apart so a false (b)
    cannot be hidden by a true (a).
    """
    label, marker, source = "nonquotable-diagnostic", "NONQUOTABLE-DIAGNOSTIC", "local literal"
    try:
        import pet_diagnostic_quarantine as pdq
        label, marker = pdq.DIAGNOSTIC_LABEL, pdq.FILENAME_MARKER
        source = "pet_diagnostic_quarantine.DIAGNOSTIC_LABEL/FILENAME_MARKER"
    except Exception as exc:          # login-safe path: say which copy of the name was used
        source = f"local literal ({type(exc).__name__} importing pet_diagnostic_quarantine)"

    rep["label"] = label
    rep["nonquotable"] = True
    rep["nonquotability"] = {
        "label": label,
        "label_source": source,
        "filename_marker": marker,
        "marker_in_report_filename": marker in os.path.basename(json_path or ""),
        "marker_in_artifact_path": marker in os.path.basename(artifact_path or ""),
        "why": ("a product of closure_foldforward_instrumented.py is an unpromoted DIAGNOSTIC "
                "closure: it is not a publication estimate, it designates nothing quotable, and no "
                "authorization in this campaign has ever made one quotable. The two marker booleans "
                "above are MEASURED off the paths this run actually wrote and are not part of that "
                "claim."),
        "enforced_by": ("pet_diagnostic_quarantine.require_quotable rejects on `label`; it does NOT "
                        "trust this field for the converse -- it recomputes the fold-forward "
                        "deviation from the weights artifact, so clearing these fields does not "
                        "make anything quotable."),
    }
    return rep


def rename_retired_recovery_bar_field(rep):
    """Rename `recovery_criteria_met` so a JSON-only reader cannot mistake it for the verdict.

    Identical in intent and wording to `closure_powered_annealed_lr.py:196-207`, which does this for
    the runs it drives. This module composes with that one but calls only its
    `install_annealed_multifold`, never its `main`, so its rename never reaches a report written
    here -- all six products of 2026-08-15 carry the un-renamed field, inherited from
    `closure_powered_truth_reweight.py:362-365`.

    The value is the pinned driver's self-report against its own hardcoded
    `RESIDUAL_OVER_GAP_MAX = 0.20` (`closure_powered_truth_reweight.py:105`), i.e. the
    `recovery >= 0.80` bar CLM-012 RETIRED on 2026-08-09. Renaming rather than correcting is the
    point: editing a criterion inside a hash-pinned closure to make a check pass is the prohibited
    act, and it is unnecessary because the authoritative evaluation re-derives the spectra and reads
    the adopted threshold from FROZEN.

    Safe to rename, checked rather than assumed (2026-08-15): no non-test module reads
    `recovery_criteria_met`; `is_powered_closure` IS read (`validate_pet_nominal_gate4:722`) and is
    left untouched. Idempotent, so composing with the annealed wrapper's rename cannot double-apply.
    """
    if "recovery_criteria_met" not in rep:
        return rep
    rep["recovery_criteria_met_AGAINST_RETIRED_0p80_BAR_NOT_THE_VERDICT"] = rep.pop(
        "recovery_criteria_met")
    rep["recovery_criteria_met_field_note"] = (
        "RENAMED from `recovery_criteria_met` by closure_foldforward_instrumented.py. The value is "
        "the closure driver's self-report against its own hardcoded recovery >= 0.80 "
        "(closure_powered_truth_reweight.py:105) -- the bar CLM-012 RETIRED on 2026-08-09. It is "
        "NOT the verdict, and neither is the sibling `verdict` field, which the same driver derives "
        "from the same retired literal. The authoritative evaluation is "
        "validate_pet_nominal_gate4.check_powered_closure, which re-derives the spectra and reads "
        "the ADOPTED threshold from FROZEN; `metrics.recovery` is the number to evaluate.")
    return rep


def attest_anneal_took_effect(lr_records, declared_lr, start, niter=None):
    """Prove the anneal TOOK EFFECT, not that the install function was called. Fails closed.

    WHY THIS EXISTS AS A SECOND IMPLEMENTATION. `closure_powered_annealed_lr.py` already has
    `assert_anneal_took_effect` (`:112`), and it is reachable only from that module's own `main`
    (`:178`). This module deliberately bypasses that `main` -- it drives `cpt.main` so the fold-forward
    recorder can compose over the anneal -- so the guard never ran for the six products of
    2026-08-15, and their receipts recorded only `fold_forward_composed_with_annealed_arm: True`.
    **That boolean is True even when `fit_lr_records` is EMPTY**, which is precisely the state the
    sibling guard exists to refuse. An un-annealed run was indistinguishable from an annealed one in
    the receipt. BEN-317, BEN-312's family.

    THIS VERSION IS STRICTLY STRONGER THAN THE SIBLING, AND THE DIFFERENCE IS ONE ARGUMENT.
    The sibling derives its reference rate from the data it is checking --
    `base_lr = max(r["learning_rate"] for r in lr_records)` (`:177`) -- so whatever the highest
    observed rate happens to be BECOMES the standard the rest are judged against. That catches an
    empty record list and a wrong PATTERN; it cannot catch a globally wrong base rate, because a run
    at 10x every intended rate produces a perfectly self-consistent record set.

    Here `declared_lr` is the engine's own `self.LR`, captured off the live instance by the recorder
    (`omnifold.py:127`; the default 1e-4 at `:57`, which
    `closure_powered_truth_reweight.py:328-331` does not override). Comparing observed rates against a
    value the engine DECLARED rather than one the records IMPLY is what closes that hole.

    THE RESIDUE, NAMED RATHER THAN LEFT FOR A LATER READER TO FIND: `declared_lr` is read at runtime,
    so if the engine's own default were changed, the observed rate and the reference would move
    together and this check would still pass. That is a much smaller exposure than the sibling's --
    it requires an edit to a hash-pinned engine rather than any accident of a run -- and
    `omnifold.py` is pinned by the launcher's `G0`, so such an edit cannot reach a run of this
    configuration without breaking the gate first. It is NOT zero, and the check reports
    `engine_declared_LR` so a reader can compare it against `1e-4` themselves.

    `ANNEALED_LR` is a literal in the sibling module (`:47`) and is checked directly, so the annealed
    leg has no equivalent residue.
    """
    import closure_powered_annealed_lr as cpa

    if not lr_records:
        raise SystemExit(
            "[ff] the anneal produced NO fit-time LR records, so nothing proves it took effect. "
            "This is the state closure_powered_annealed_lr.py:114-115 fails closed on, and a "
            "receipt asserting `composed_with_annealed_arm` without it would be unfalsifiable "
            "(fail closed -- BEN-317).")
    if declared_lr is None or not np.isfinite(declared_lr) or declared_lr <= 0:
        raise SystemExit(
            f"[ff] the engine's declared base learning rate is {declared_lr!r}; without it this "
            f"attestation would have to derive its own reference from the records it is checking, "
            f"which cannot detect a globally wrong rate (fail closed -- BEN-317).")

    problems, n_base, n_annealed = [], 0, 0
    for r in lr_records:
        annealed_expected = int(r["iteration"]) > int(start)
        want = cpa.ANNEALED_LR if annealed_expected else float(declared_lr)
        got = float(r["learning_rate"])
        if np.isclose(got, want, rtol=cpa.LR_ASSERT_RTOL, atol=1e-12):
            n_annealed += 1 if annealed_expected else 0
            n_base += 0 if annealed_expected else 1
        else:
            problems.append(
                f"iteration {r['iteration']} step {r['step']}: lr={got!r}, expected "
                f"{want!r} ({'annealed' if annealed_expected else 'base'} leg, start={start})")
    if problems:
        raise SystemExit(
            "[ff] THE ANNEAL DID NOT TAKE EFFECT AS INTENDED:\n  " + "\n  ".join(problems)
            + f"\nReference base rate is the engine's DECLARED self.LR = {declared_lr!r}, not the "
              f"maximum of these records. Refusing to annotate a report whose configuration is not "
              f"the predeclared one (fail closed -- BEN-317).")

    # Fit COUNT is recorded and cross-checked, but only the RATES are fatal. Two fits per iteration
    # (step 1 and step 2) is what the engine does and what run 56552326's proof shows -- 6 records at
    # niter=3 -- so a departure is worth surfacing loudly. It is not raised, because this function runs
    # AFTER a multi-hour GPU run: a false refusal here would discard a good run's annotation over a
    # count whose invariance across every future engine path this lane has not established. The rates
    # are what the predeclaration is about, and they fail closed above.
    expected = (2 * int(niter)) if niter else None
    proof = {
        "pass": True,
        "n_fits_at_base_lr": n_base,
        "n_fits_at_annealed_lr": n_annealed,
        "n_records": len(lr_records),
        "engine_declared_LR": float(declared_lr),
        "annealed_LR": float(cpa.ANNEALED_LR),
        "assert_rtol": float(cpa.LR_ASSERT_RTOL),
        "anneal_start": int(start),
        "niter": (int(niter) if niter else None),
        "expected_n_records_at_two_fits_per_iteration": expected,
        "n_records_matches_two_per_iteration": (
            None if expected is None else bool(len(lr_records) == expected)),
        "reference_rate_source": (
            "the engine's DECLARED self.LR, captured off the live MultiFold instance by the "
            "fold-forward recorder (omnifold.py:127) -- NOT max(records), which is what "
            "closure_powered_annealed_lr.py:177 uses and which cannot detect a globally wrong rate"),
        "residual_exposure": (
            "declared_lr is read at runtime, so an edit to the ENGINE's own default would move the "
            "observed rate and the reference together and still pass. omnifold.py is G0-pinned, so "
            "such an edit cannot reach a run of this configuration without breaking the gate first. "
            "Not zero; engine_declared_LR is reported so a reader can check it against 1e-4."),
        "records": list(lr_records),
    }
    print(f"[ff] ANNEAL ATTESTED: {n_base} fit(s) at the engine's declared "
          f"{declared_lr:g} (iteration<={start}), {n_annealed} at {cpa.ANNEALED_LR:g}; "
          f"{len(lr_records)} records"
          + ("" if expected is None else f", expected {expected} at niter={niter}"))
    return proof


def main(argv=None):
    """Run the powered closure with the recorder installed, then inject the records into its report.

    The report is written inside `cpt.main`, which this module must not edit, so the records are
    merged into the JSON afterwards -- the same post-hoc rewrite `closure_powered_annealed_lr.py`
    performs on the same file for its LR-policy fields.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    annealed = "--annealed" in argv
    if annealed:
        argv.remove("--annealed")
    correct = "--correct-fold-forward" in argv
    if correct:
        argv.remove("--correct-fold-forward")
    arm = "arm1_corrected" if correct else "arm0_instrumented_only"

    import closure_powered_truth_reweight as cpt
    import omnifold as of_pkg

    if not hasattr(of_pkg, "MultiFold"):
        raise SystemExit("[ff] omnifold package does not export MultiFold; cannot install the "
                         "recorder (fail closed)")

    original = of_pkg.MultiFold
    base = original
    lr_records = None
    if annealed:
        # Compose, do not replace: the anneal subclass first, the recorder on top of it.
        import closure_powered_annealed_lr as cpa
        base, lr_records = cpa.install_annealed_multifold()

    recorder, ff_records = install_fold_forward_recorder(base, correct=correct)
    of_pkg.MultiFold = recorder
    try:
        rc = cpt.main(argv)
    finally:
        of_pkg.MultiFold = original

    # Locate the report the driver just wrote, from the same argv it was given.
    out = None
    for k, tok in enumerate(argv):
        if tok == "--json" and k + 1 < len(argv):
            out = argv[k + 1]
        elif tok.startswith("--json="):
            out = tok.split("=", 1)[1]
    if out is None or not os.path.exists(out):
        raise SystemExit(f"[ff] cannot find the driver's report to annotate (--json {out!r}); the "
                         f"fold-forward records would be lost (fail closed)")

    with open(out) as fh:
        rep = json.load(fh)
    if not ff_records:
        raise SystemExit("[ff] no fold-forward records were captured -- the recorder never saw a "
                         "RunStep1, so it was not installed on the class the driver resolved "
                         "(fail closed)")
    niter = ((rep.get("configuration") or {}).get("niter"))
    if niter is not None and len(ff_records) != int(niter):
        raise SystemExit(f"[ff] recorded {len(ff_records)} iterations, report says niter={niter} "
                         f"(fail closed)")
    rep["fold_forward_per_iteration"] = ff_records
    rep["step1_class_ratio"] = ff_records[0]["step1_class_ratio"]

    # ---- THE END-OF-RUN PUSH, WHICH NO RunStep1 ROW CAN SEE (BEN-360/VL134) --------------------
    s2 = list(getattr(recorder, "FOLD_FORWARD_STEP2_RECORDS", []) or [])
    if not s2:
        raise SystemExit("[ff] no post-RunStep2 records were captured, so the END-OF-RUN push -- the "
                         "quantity OI-125 is about -- is absent. The RunStep2 hook did not fire, so "
                         "this report would repeat the substitution BEN-360 documents (fail closed).")
    if niter is not None and len(s2) != int(niter):
        raise SystemExit(f"[ff] {len(s2)} post-RunStep2 records for niter={niter} (fail closed)")

    # THE OVERLAP GATE. The push RunStep2(i) leaves IS the push RunStep1(i+1) consumes, so those rows
    # must agree EXACTLY -- same array, same reduction, two points in time. Holds for both arms
    # because the RunStep1 row is the PRE-correction measurement. A disagreement means one hook is
    # reading at the wrong moment, which is the failure this pairing exists to make impossible.
    by_iter = {int(r["iteration"]): r for r in ff_records}
    mismatches = []
    for r in s2:
        nxt = by_iter.get(int(r["iteration"]) + 1)
        if nxt is None:
            continue
        a, b = r["reco_weighted_mean_push"], nxt["reco_weighted_mean_push"]
        if a != b:
            mismatches.append(f"RunStep2({r['iteration']}) left {a!r} but "
                              f"RunStep1({nxt['iteration']}) consumed {b!r}")
    if mismatches:
        raise SystemExit("[ff] THE TWO HOOKS DISAGREE ON THE SAME PUSH:\n  " + "\n  ".join(mismatches)
                         + "\nOne of them is reading at the wrong moment; the end-of-run value cannot "
                           "be trusted either (fail closed).")

    end = [r for r in s2 if r.get("is_end_of_run_push")]
    if len(end) != 1:
        raise SystemExit(f"[ff] {len(end)} records claim to be the end-of-run push, expected exactly "
                         f"1 (fail closed)")
    rep["fold_forward_post_step2_per_iteration"] = s2
    rep["fold_forward_end_of_run"] = dict(end[0], **{
        "why_this_is_the_quantity_OI_125_NEEDS": (
            "closure_powered_truth_reweight.py:332-333 takes of.weights_push AFTER Unfold(), and "
            "train_fullevent_nominal.py:576-577 computes the nominal's fold-forward the same way, so "
            "the nominal's 0.736746 is an END-OF-RUN scalar. The last fold_forward_per_iteration row "
            "is the push entering the FINAL iteration, one step earlier, and substituting it gives a "
            "~105-draw-sd disagreement with the sign of ratio-1 flipped (BEN-360, VL134)."),
        "recorded_not_reconstructed": (
            "This value is recorded BY THE RUN. VL134 is the same quantity RE-REDUCED by a reader "
            "from the persisted weights_push, twice and to 1e-13 -- a re-reduction of a persisted "
            "array, not an approximation. This row does not validate VL134 and must not be compared "
            "to it as a check: the driver takes no seed flag, so a later run is a NEW sample."),
        "overlap_cross_check": (
            f"{len(s2) - 1} of these rows duplicate fold_forward_per_iteration rows by construction "
            f"and were gated to EXACT equality before this report was written."),
    })
    rep["fold_forward_note"] = FOLD_FORWARD_NOTE
    rep["fold_forward_instrumented_by"] = os.path.basename(__file__)
    rep["fold_forward_arm"] = arm
    rep["fold_forward_correction_applied"] = bool(correct)
    rep["fold_forward_correction_form"] = (
        "SCALE-ONLY: one scalar R/ratio per iteration, applied to weights_push BEFORE step 1 "
        "consumes it. Predeclared; a per-cell variant is refused (BEN-310 -- a per-cell field built "
        "from push is the unfolding's own output, so dividing it out is a de-unfolding)."
        if correct else "none; arm 0 records only and changes no weight, model or metric")
    if lr_records is not None:
        # The boolean stays, because it answers a different question -- WAS the anneal composed -- and
        # a reader looking for it should still find it. It is no longer the only evidence, and it is
        # no longer written before the proof: `attest_anneal_took_effect` raises on the empty-records
        # state that used to leave this `True` with nothing behind it (BEN-317).
        rep["fold_forward_composed_with_annealed_arm"] = True
        rep["anneal_lr_proof"] = attest_anneal_took_effect(
            lr_records,
            declared_lr=ff_records[0].get("engine_declared_LR"),
            start=ff_records[0].get("anneal_start", 0),
            niter=niter)
        rep["fold_forward_composed_with_annealed_arm_note"] = (
            "This boolean records that install_annealed_multifold() was CALLED. It is NOT the "
            "attestation -- read `anneal_lr_proof`, which is absent if the anneal could not be "
            "proven because this module now fails closed rather than writing an unbacked True. The "
            "six products of 2026-08-15 predate that guard and carry the boolean ALONE; they are "
            "BOUNDED, NOT ATTESTED, and nothing here retro-attests them (BEN-317).")
    annotate_nonquotability(rep, out, artifact_path=(rep.get("artifact") or {}).get("path"))
    rename_retired_recovery_bar_field(rep)
    tmp = out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(rep, fh, indent=2)
    os.replace(tmp, out)

    # Verify the write rather than trusting it -- seven tools reported success over failure in one
    # day on this campaign.
    with open(out) as fh:
        back = json.load(fh)
    if len(back.get("fold_forward_per_iteration") or []) != len(ff_records):
        raise SystemExit("[ff] the annotated report does not read back with its fold-forward "
                         "records (fail closed)")
    # The two annotations above are the ones a JSON-only consumer keys off, so they are verified on
    # the bytes rather than on the dict that was serialized.
    if not back.get("nonquotable") or not back.get("nonquotability"):
        raise SystemExit("[ff] the annotated report does not read back as non-quotable; a consumer "
                         "parsing this JSON would see an unmarked result (fail closed)")
    if "recovery_criteria_met" in back:
        raise SystemExit("[ff] the retired-0.80-bar field read back under its original name, where "
                         "it will be mistaken for the verdict (fail closed)")
    print(f"[ff] arm={arm} recorded {len(ff_records)} iterations into {out}")
    print(f"[ff] report marked label={back.get('label')!r} nonquotable=True; the retired-0.80-bar "
          f"self-report was renamed away from `recovery_criteria_met`")
    for r in ff_records:
        print(f"[ff]   iteration {r['iteration']}: ratio={r['reco_weighted_mean_push']!r} "
              f"R={r['step1_class_ratio']!r} dev={r['deviation_from_R']!r}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
