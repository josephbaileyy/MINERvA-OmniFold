# PET-v2 fixed-draw equivalence changed retry 3 — predeclaration

## Decision state

**Contract:** `PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY3-20260826`

**State:** `AUTHORIZED_READY_CHANGED_RETRY`

Joseph authorized evidence-backed changed retries for this frozen fixed-draw diagnostic, including
the instruction to keep fixing failures until the diagnostic works. This is not authorization for
an unchanged retry, scientific tuning, a larger family, or work beyond the existing five CPU
node-hour and 18 A100-hour total envelope.

The executable contract is
[`pet-v2-fixed-draw-equivalence-changed-retry3-proposal-20260826.json`](state/pet-v2-fixed-draw-equivalence-changed-retry3-proposal-20260826.json).

## Preserved retry-2 result and diagnosis

Target `57629029` passed the retry-2 authorization, target-only import, and checkout-root controls.
It completed both weighted and literal Stay-Positive fits, then failed closed because its rebuilt
weighted target had SHA-256 `ecc893…f0d0`, not the frozen Gate-5 seed-50000 digest
`13d465…0c03`. The exact attempt is preserved in
[`pet-v2-fixed-draw-equivalence-changed-retry2-attempt-57629029.json`](state/pet-v2-fixed-draw-equivalence-changed-retry2-attempt-57629029.json).

The two arrays have identical shape, `float32` dtype, and zero count. Their sums differ by
`0.00784214695886476` on about `1.125e6`; 99% of absolute row differences are at most
`4.76837158203125e-7`, but 1,141,467 rows differ and the largest absolute row difference is
`0.06442590430378914`. This establishes failure of byte reproducibility in that fresh process. It
does not establish a settled mechanism. The byte-digest guard is retained, not loosened.

Retry 2 consumed `1.5555555555555556` CPU node-hours and zero A100-hours. The three impossible
dependency jobs were cancelled with zero allocation. Across failed attempts, consumption is
`1.6925` CPU node-hours and zero A100-hours.

## Only changed axis

Retry 3 does not refit the weighted target. It reads the existing Gate-5 replica-00 target only
after exact checks of its file hash and size, owning receipt hash, seed, G2 input hash,
signed-inventory hash, shape, dtype, finiteness, and non-negativity. It byte-copies that target into
the new namespace, where the unchanged digest guard still requires `13d465…0c03`.

The original paired-target driver then performs only the canonical literal delete/duplicate
Stay-Positive fit. A two-call control proves that the first refiner call returns the archived
weighted operand and the second invokes the unchanged canonical literal refiner exactly once. The
training and evaluation operands remain the retry-1 files byte-for-byte.

This freezes the actual weighted estimand more strictly than a numerically close rebuild. It does
not classify the retry-2 rebuild as acceptable and does not reinterpret any historical family.

## Measured quantity and controls

The question remains whether, for fixed Poisson draw seed 50000, finite-batch training with
multiplicities as weights and retained zero-weight rows is operationally equivalent to literal
delete/duplicate resampling. Arms remain `W_A`, `W_B`, and `L`. All draw, target, unique-event split,
feature, mask, loss normalization, three-iteration schedule, eight reco/eight truth epochs, batch
size, patience, learning rates, Adam-state, deterministic-environment, and one-A100-80GB controls
remain frozen.

Primary event-push and global plus three `p_parallel` projection distances are unchanged. The
same-arm cap remains `S=0.0251`, cross-arm materiality remains `M=0.0502`, and terminal ordering
remains `INVALID_OR_NOISY`, equivalence at operational resolution, material difference in this
fixed draw, then mixed/unresolved.

## Resources

The remaining envelope is `3.3075` CPU node-hours and 18 A100-hours. Retry 3's target is estimated
at 0.75 CPU node-hours from historical one-fit job `56857246` (0.6525 node-hours), rounded upward
for hash/copy/flux work. Expected full A100 use remains 13 hours, below the 18-hour ceiling. A target
failure prevents A100 work. These estimates authorize no additional campaign or suggested sample
count.

## Interpretation and non-authorization

A valid terminal result classifies only the predeclared fixed-draw push and projection contrasts
after the same-arm control. Ordinary closure remains distinct from equivalence, and neither is
coverage. A machinery failure supports only preservation, diagnosis, and a distinct changed retry
inside this frozen scope and remaining envelope.

Every terminal result preserves:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

It cannot establish valid PET uncertainty or interval coverage; construct or adopt `C_stat`,
`C_ML`, a covariance, or a central value; authorize a coverage campaign, larger family,
convergence tuning, Gate 6, or Leg 2; alter the note or publication claims; erase any failed
attempt; or generalize beyond this seed and frozen PET-v2 policy. Existing Gate 6 remains blocked.
