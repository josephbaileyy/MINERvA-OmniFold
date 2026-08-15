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
            })
            if correct:
                if ratio is None or not ratio > 0:
                    raise SystemExit(f"[ff] iteration {i}: fold-forward ratio is {ratio!r}; the "
                                     f"scale-only correction is undefined (fail closed)")
                factor = R / ratio
                # ONE scalar over every row -- the shape of push is untouched by construction.
                self.weights_push = np.asarray(self.weights_push, np.float64) * factor
                after = float((w[pr] * np.asarray(self.weights_push, np.float64)[pr]).sum() / den)
                records[-1]["applied_correction_factor"] = factor
                records[-1]["reco_weighted_mean_push_after_correction"] = after
            return super().RunStep1(i)

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
        rep["fold_forward_composed_with_annealed_arm"] = True
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
    print(f"[ff] arm={arm} recorded {len(ff_records)} iterations into {out}")
    for r in ff_records:
        print(f"[ff]   iteration {r['iteration']}: ratio={r['reco_weighted_mean_push']!r} "
              f"R={r['step1_class_ratio']!r} dev={r['deviation_from_R']!r}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
