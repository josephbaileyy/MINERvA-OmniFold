# PET-v2 fixed-draw equivalence changed retry 2 — predeclaration

## Decision state

**Contract:** `PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY2-20260826`

**State:** `AUTHORIZED_READY_CHANGED_RETRY`

**Launchable:** `true` only after every committed hash, clean-checkout, interpreter, input, output,
scheduler, hardware, and no-submit preflight passes

Joseph explicitly stated **“Retries are authorized”** after retry 1's target-environment failure
was reported. This authorizes changed machinery retries needed to complete this one fixed-draw
diagnostic within the existing total resource ceiling. It does not authorize an unchanged or
automatic retry, a changed scientific policy, or any work outside this diagnostic.

The machine contract is
[`pet-v2-fixed-draw-equivalence-changed-retry2-proposal-20260826.json`](state/pet-v2-fixed-draw-equivalence-changed-retry2-proposal-20260826.json).

## Preserved failed attempt

Target `57626676` passed authorization and root-remap checks, loaded six observed repository modules
from the detached `9bbd26cc` checkout, then failed before target publication with
`ModuleNotFoundError: No module named 'tensorflow'`. Its exact terminal evidence is preserved in
[`pet-v2-fixed-draw-equivalence-changed-retry1-attempt-57626676.json`](state/pet-v2-fixed-draw-equivalence-changed-retry1-attempt-57626676.json).
No scientific quantity was measured, no A100 was allocated, and the three dependency-held jobs were
cancelled with zero allocation.

## Measured cause and only changed axis

The target runs in the ROOT Python 3.11 environment, which has ROOT and no TensorFlow. The training
environment is Python 3.9 with TensorFlow and no ROOT; combining their binary packages is not a safe
repair. Target materialization needs `DataLoader`, whose file imports only NumPy, but Python first
executes `omnifold/__init__.py`; that initializer imports the TensorFlow training engine.

Retry 2 changes only that import side effect:

- in the target process only, create an `omnifold` package shell rooted at the guarded checkout;
- load `omnifold/dataloader.py` at exact SHA-256
  `bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a`;
- fail if the file/hash differs, the package was already imported, or TensorFlow appears;
- run the unchanged target operand through the unchanged retry-1 checkout-root remap and OI-136
  guard;
- reuse the unchanged retry-1 training and evaluation wrappers in their TensorFlow environment.

The positive control reproduces the TensorFlow import failure in the exact ROOT environment. The
candidate control loads and instantiates the identical `DataLoader`, leaves TensorFlow absent, and
passes the guarded target `--help` path with all eight observed checkout modules under one root.

## Measured question and frozen controls

The question remains: for Poisson draw seed `50000`, is finite-batch training with multiplicities as
sample weights, including retained zero-weight rows, operationally equivalent to literal deletion
and duplication?

The three arms remain `W_A`, `W_B`, and `L`. The event-push distance and global plus three frozen
`p_parallel` projection distances are unchanged. So are the diagnostic payloads, fixed data/signal/
background factors, required class ratio `R=1.1253110723074478`, unique-event split, seeds, feature
contract, mask, target, loss normalization, three OmniFold iterations, eight reco/eight truth
epochs, batch size 512, patience 10, learning rates, new Adam per fit, warm-started model weights,
deterministic environment, and one A100-SXM4-80GB per arm.

The same-arm cap remains `S=0.0251`; the cross-arm materiality margin remains `M=0.0502`. Terminal
order remains:

1. `INVALID_OR_NOISY` on any failed control or any primary `D_same>S`;
2. `EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION` only when every primary
   `D_cross_max<=M`;
3. `MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW` only when a primary metric has both
   `D_cross_min>M` and `D_cross_min>2*D_same`;
4. `MIXED_OR_UNRESOLVED` otherwise.

## Resources and execution contract

The total authorization remains five CPU node-hours and 18 A100-hours. The two failed target
attempts consumed `0.13694444444444442` CPU node-hours cumulatively and zero A100-hours, leaving
`4.8630555555555555` CPU node-hours and 18 A100-hours. Expected complete A100 use remains 13 hours.
These numbers authorize nothing outside this fixed-draw diagnostic.

Retry 2 requires a new absent output namespace and one clean detached non-primary checkout at the
pushed implementation head. Every Python stage remains behind `mnv_guarded_run.py`; the controller
has no `srun`, automatic retry, or unchanged retry path. A failed target prevents all A100 work.

## Interpretation and non-authorization

A valid result classifies only the predeclared fixed-draw push and projection contrasts after the
same-arm control. A machinery failure authorizes only a changed machinery diagnosis/retry within
this frozen scope and total ceiling. Neither outcome can establish interval coverage, valid PET
uncertainty, ordinary closure beyond the measured projections, or equivalence beyond this seed and
policy.

Every terminal result preserves these exact prohibitions:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

It cannot construct or adopt `C_stat`, `C_ML`, a total covariance, or a central value; authorize a
coverage campaign, larger family, convergence tuning, Gate 6, or Leg 2; alter the note, publication
claims, or PET's diagnostic scope; erase either failed receipt; or authorize compute outside this
fixed-draw diagnostic and total ceiling. Existing Gate 6 remains blocked regardless.
