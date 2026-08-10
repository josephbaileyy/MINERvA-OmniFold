#!/usr/bin/env python3
"""D2 powered closure run under the INTENDED learning-rate anneal — the shape validation.

Authorized by Joseph 2026-08-09/10. Reading fixed in advance:
`docs/orchestration/PREDECLARATION-20260810-annealed-shape-validation.md`.

WHAT THIS TESTS. Restoring the engine's intended (but dead) per-iteration LR anneal took the fold-forward
deficit from -34.46% to -1.17%. The worry is that it does so by UNDER-UPDATING: a 10x smaller learning
rate after iteration 0 moves the classifier less, which would hold the normalization near its already-good
iteration-1 value while failing to transport the SHAPE information later iterations exist to add.
Normalization would improve precisely because less is happening. The D2 powered closure is a shape
measure over cells and is insensitive to a pure normalization fix by construction, so it is the right
instrument.

HOW THE ANNEAL IS APPLIED — WITHOUT EDITING THE ENGINE. `omnifold.py` calls
`CompileModels(fixed=True)` after each iteration, but `RunModel` recompiles the trained clone at full
`self.LR` immediately before every `fit()`, so the anneal is dead (see KNOWN_ISSUES 2026-08-09). This
module subclasses `MultiFold` and overrides `CompileModel` to force `fixed=True` at FIT TIME for
iterations > start, mirroring the other lane's verified `diagnose_step1_annealed_lr.py`. The engine file
is read-only here and its sha256 is recorded in the report.

THE ANNEAL IS PROVEN, NOT ASSUMED. Every fit-time learning rate is read back off
`model.optimizer.learning_rate` and asserted against the intended pattern (`LR` at iteration 0, `1e-5`
after). A mismatch is a hard failure. Without this the run could report "annealing does not help" when
the anneal never happened — which is exactly the silent no-op I flagged before the other lane's arm ran,
and which their control guarded the same way.

    python3 -u closure_powered_annealed_lr.py --json <out.json> --artifact <out.npz> \
        --weights-folder <dir> [--max-events N]
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
for _p in (_HERE, _REPO, os.path.join(os.path.dirname(_REPO), "omnifold_nn")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ARM = "powered_closure_warm_fixed_annealed_lr"
ANNEALED_LR = 1e-5          # engine's get_optimizer(min_learning_rate=1e-5) when fixed=True
LR_ASSERT_RTOL = 1e-5


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def install_annealed_multifold():
    """Return a MultiFold subclass that makes the intended anneal effective, and its LR record list.

    Deliberately a SUBCLASS rather than a monkey-patch of the engine module: the closure script builds
    `MultiFold(...)` by name, so we hand it the subclass and `omnifold.py` itself is never mutated.
    """
    import tensorflow as tf
    from omnifold import MultiFold as BaseMultiFold

    fit_lr_records = []

    class AnnealedMultiFold(BaseMultiFold):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self._ann_iteration = 0
            self._ann_stepn = 0
            self._inside_fit_compile = False

        def CompileModel(self, model, num_steps, fixed=False):
            effective_fixed = bool(fixed)
            # Force ONLY the fit-time compile, and only after the first iteration. Forcing
            # CompileModels too would be harmless (it targets untrained objects) but would muddy the
            # record of what was actually applied.
            if self._inside_fit_compile and self._ann_iteration > self.start:
                effective_fixed = True
            out = super().CompileModel(model, num_steps, fixed=effective_fixed)
            if self._inside_fit_compile:
                lr = float(tf.keras.backend.get_value(model.optimizer.learning_rate))
                fit_lr_records.append({
                    "iteration": int(self._ann_iteration),
                    "step": int(self._ann_stepn),
                    "requested_fixed": bool(fixed),
                    "effective_fixed": bool(effective_fixed),
                    "learning_rate": lr,
                })
            return out

        def RunModel(self, labels, weights, iteration, model, stepn, NTRAIN=1000, cached=False):
            self._ann_iteration = int(iteration)
            self._ann_stepn = int(stepn)
            self._inside_fit_compile = True
            try:
                return super().RunModel(labels, weights, iteration, model, stepn, NTRAIN, cached)
            finally:
                self._inside_fit_compile = False

    return AnnealedMultiFold, fit_lr_records


def assert_anneal_took_effect(records, base_lr, start=0):
    """Hard-fail unless every fit ran at the intended rate. The run is worthless otherwise."""
    if not records:
        raise SystemExit("[annealed] no fit-time LR records: the interception never fired (fail closed)")
    problems = []
    for r in records:
        want = base_lr if r["iteration"] <= start else ANNEALED_LR
        got = r["learning_rate"]
        if not np.isclose(got, want, rtol=LR_ASSERT_RTOL, atol=1e-12):
            problems.append(f"iter {r['iteration']} step {r['step']}: lr={got!r} want {want!r}")
    if problems:
        raise SystemExit("[annealed] the anneal did NOT take effect as intended:\n  "
                         + "\n  ".join(problems)
                         + "\nRefusing to report a shape result the configuration does not support.")
    n_base = sum(1 for r in records if r["iteration"] <= start)
    n_ann = len(records) - n_base
    print(f"[annealed] LR pattern VERIFIED: {n_base} fit(s) at {base_lr:g} (iteration<={start}), "
          f"{n_ann} at {ANNEALED_LR:g}")
    return {"n_fits_base_lr": n_base, "n_fits_annealed": n_ann, "base_lr": base_lr,
            "annealed_lr": ANNEALED_LR, "records": records}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--weights-folder", required=True)
    ap.add_argument("--max-events", type=int, default=None)
    ap.add_argument("--inputs", default=None)
    a, passthrough = ap.parse_known_args(argv)

    import closure_powered_truth_reweight as cpt

    engine_path = os.path.join(os.path.dirname(_REPO), "omnifold_nn", "omnifold", "omnifold.py")
    engine_sha = _sha256(engine_path) if os.path.exists(engine_path) else None

    Annealed, lr_records = install_annealed_multifold()

    # Hand the closure our subclass by name. It resolves MultiFold from its own module globals
    # (`from omnifold import PET, MultiFold` inside main), so patch that binding rather than the engine.
    # The closure does `from omnifold import PET, MultiFold` INSIDE its main(), so it resolves the
    # name from the package at call time -- patching the package attribute before invoking it is
    # sufficient, and the engine module itself stays untouched.
    import omnifold as of_pkg
    if not hasattr(of_pkg, "MultiFold"):
        raise SystemExit("[annealed] omnifold package does not export MultiFold; cannot apply the "
                         "anneal without editing the engine (fail closed)")
    original = of_pkg.MultiFold
    of_pkg.MultiFold = Annealed
    base_lr = None
    try:
        argv2 = ["--json", a.json, "--artifact", a.artifact,
                 "--weights-folder", a.weights_folder] + list(passthrough)
        if a.max_events is not None:
            argv2 += ["--max-events", str(a.max_events)]
        if a.inputs:
            argv2 += ["--inputs", a.inputs]
        print(f"[annealed] arm={ARM}")
        print(f"[annealed] engine sha256={engine_sha} (READ-ONLY; not edited)")
        print(f"[annealed] invoking closure: {' '.join(argv2)}")
        rc = cpt.main(argv2)
    finally:
        of_pkg.MultiFold = original

    if lr_records:
        base_lr = max(r["learning_rate"] for r in lr_records)
    lr_proof = assert_anneal_took_effect(lr_records, base_lr, start=0)

    # Annotate the closure's own report in place -- additively, never overwriting its measurements.
    with open(a.json) as fh:
        rep = json.load(fh)

    # ---- MAKE THE OUTPUT SELF-DECLARING (Joseph, 2026-08-10) --------------------------------------
    # closure_powered_truth_reweight.py:105 hardcodes RESIDUAL_OVER_GAP_MAX = 0.20, i.e. the
    # `recovery >= 0.80` bar that CLM-012 RETIRED. Its `recovery_criteria_met` therefore reads FALSE for
    # a result the adopted criterion passes, and a reader will take it for the verdict.
    #
    # The fix is to LABEL THE OUTPUT, not to correct the threshold: editing a criterion inside a closure
    # to make a check pass is the prohibited act, and it is unnecessary because
    # validate_pet_nominal_gate4.check_powered_closure re-derives the spectra and reads the adopted
    # value from FROZEN. Same move as `publication_gate_rejects_this` and
    # `..._FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE`: rename the field so it cannot be mistaken for the verdict.
    #
    # Safe to rename, checked rather than assumed: `recovery_criteria_met` is read by NOTHING -- it
    # appears only in test fixtures and comments. `is_powered_closure` IS read (validate:722) and is
    # left untouched.
    RETIRED_RECOVERY_BAR = 0.80
    stale = rep.pop("recovery_criteria_met", None)
    rep["recovery_criteria_met_AGAINST_RETIRED_0p80_BAR_NOT_THE_VERDICT"] = stale
    rep["recovery_criteria_met_field_note"] = (
        "RENAMED from `recovery_criteria_met` by closure_powered_annealed_lr.py. The value is the "
        f"closure driver's self-report against its own hardcoded recovery >= {RETIRED_RECOVERY_BAR} "
        "(closure_powered_truth_reweight.py:105) -- the bar CLM-012 RETIRED on 2026-08-09. It is NOT "
        "the Gate-4 verdict. The authoritative evaluation is "
        "validate_pet_nominal_gate4.check_powered_closure, which re-derives the spectra and reads the "
        "ADOPTED threshold from FROZEN. See `recovery_vs_adopted_criterion` below.")

    _rec = (rep.get("metrics") or {}).get("recovery")
    try:
        import validate_pet_nominal_gate4 as _g4
        _P = _g4.FROZEN["powered_closure"]
        _f, _ceil = _P["recovery_fraction_of_ceiling"], _P["acceptance_limited_ceiling"]
        _bar, _src = _f * _ceil, "validate_pet_nominal_gate4.FROZEN (adopted CLM-012)"
    except Exception as exc:                      # login-safe / import-failure path: say so, do not guess
        _f = _ceil = _bar = None
        _src = f"UNAVAILABLE ({type(exc).__name__}) -- adopted criterion NOT evaluated"
    rep["recovery_vs_adopted_criterion"] = {
        "recovery": _rec,
        "adopted_threshold": _bar,
        "f": _f, "ceiling": _ceil,
        "threshold_source": _src,
        "meets_adopted_criterion": (None if (_rec is None or _bar is None) else bool(_rec >= _bar)),
        "margin": (None if (_rec is None or _bar is None) else _rec - _bar),
        "is_this_the_verdict": ("PRIMARY criterion per "
                               "PREDECLARATION-20260810-annealed-shape-validation.md Amendment 1"),
    }
    rep["annealed_lr_arm"] = {
        "arm": ARM,
        "predeclaration": "docs/orchestration/PREDECLARATION-20260810-annealed-shape-validation.md",
        "engine_sha256": engine_sha,
        "engine_edited": False,
        "applied_via": "MultiFold subclass overriding CompileModel at fit time only",
        "lr_proof": lr_proof,
        "quotable": False,
        "note": ("SHAPE VALIDATION of the annealed configuration. Threshold NOT modified. A clean result "
                 "does NOT authorize editing omnifold.py -- that promotion is separate and Joseph's."),
    }
    with open(a.json, "w") as fh:
        json.dump(rep, fh, indent=2, default=str)
        fh.write("\n")
    print(f"[annealed] annotated {a.json}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
