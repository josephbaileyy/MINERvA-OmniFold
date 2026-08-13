"""The adopted annealed-LR estimator, as a FACTORY so both the nominal and replica drivers share one
implementation.

WHY A FACTORY AND NOT A MODULE-LEVEL CLASS. Extracted from `train_fullevent_nominal.py`'s `main()`
2026-08-13, where it was `class _AnnealedMultiFold(MultiFold)` at line 423. It closed over THREE
`main()` locals and each one forces a design constraint:

  MultiFold          `from omnifold import PET, MultiFold` at main() line 374 -- so the BASE CLASS is
                     not available at module scope. Hoisting that import here would make this module
                     unimportable without TensorFlow, turning a failure inside main() into an
                     import-time failure for everything that touches the module. Array 56832077 died
                     at 51s on exactly that ModuleNotFoundError. So the base class is PASSED IN and
                     the imports stay lazy.
  tf                 `import tensorflow as tf` at main() line 373. Same reason: passed in.
  _fit_lr_records    `= []` at main() line 421, and this is the one that matters. It is not plumbing,
                     it is THE EVIDENCE CHANNEL: main() fails closed at :461 if it is empty ("the
                     anneal interception never fired, so this run cannot be declared annealed"),
                     validates every entry against base_lr/annealed_lr at :465, and builds
                     `lr_policy_realized` with n_fits_base_lr / n_fits_annealed at :614-619 -- the
                     "2 base + 4 annealed" that 56563761's receipt reports.

**REBINDING THAT LIST WOULD PRODUCE A RUN THAT ANNEALS CORRECTLY AND REPORTS THE ANNEAL WRONGLY.**
The estimator would be identical and its receipt false, which is worse than a drifted estimator
because a drifted estimator eventually shows up in the physics and a false receipt does not. So the
records list is an explicit per-call parameter, and `test_annealed_estimator.py` asserts that two
factory calls do NOT share one -- the failure mode that only appears when a replica campaign calls
this fifty times, and which a single-call test cannot see.

WHAT THIS DOES NOT CHANGE: the LR policy itself, which lives in the caller's `LR_POLICY_ANNEALED` and
is validated by the caller. This module intercepts fit-time compilation and records what the
optimizer actually did; it does not decide the schedule.
"""
from __future__ import annotations

import functools

__all__ = ["make_annealed_multifold"]


def make_annealed_multifold(MultiFold, tf, records):
    """Return an annealed subclass of `MultiFold`, recording realized fit-time LRs into `records`.

    MultiFold : the base class, passed in because it is not importable at module scope without TF.
    tf        : the tensorflow module, passed in for the same reason.
    records   : a list this call's class appends {"iteration", "learning_rate"} dicts to. MUST be
                supplied per call -- there is deliberately no default, because a mutable default
                would be shared across every call and is the exact rebinding hazard this factory
                exists to prevent.

    The engine's own anneal is dead: `omnifold.py` calls `CompileModels(fixed=True)` after each
    iteration, but `RunModel` recompiles the trained clone at full `self.LR` immediately before every
    `fit()`. This subclass forces `fixed=True` on the fit-time recompile once past `self.start`,
    which is what makes the adopted policy take effect.
    """
    if records is None:
        raise ValueError(
            "make_annealed_multifold: `records` must be an explicit list. A shared or defaulted "
            "accumulator would make the receipt's n_fits_base_lr / n_fits_annealed wrong while the "
            "run still annealed correctly -- see this module's docstring.")

    class _AnnealedMultiFold(MultiFold):
        @functools.wraps(MultiFold.__init__)
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self._ann_iter = 0
            self._inside_fit_compile = False

        def CompileModel(self, model, num_steps, fixed=False):
            eff = bool(fixed)
            if self._inside_fit_compile and self._ann_iter > self.start:
                eff = True
            out = super().CompileModel(model, num_steps, fixed=eff)
            if self._inside_fit_compile:
                records.append(
                    {"iteration": int(self._ann_iter),
                     "learning_rate": float(tf.keras.backend.get_value(
                         model.optimizer.learning_rate))})
            return out

        def RunModel(self, labels, weights, iteration, model, stepn, NTRAIN=1000, cached=False):
            self._ann_iter = int(iteration)
            self._inside_fit_compile = True
            try:
                return super().RunModel(labels, weights, iteration, model, stepn, NTRAIN, cached)
            finally:
                self._inside_fit_compile = False

    return _AnnealedMultiFold
