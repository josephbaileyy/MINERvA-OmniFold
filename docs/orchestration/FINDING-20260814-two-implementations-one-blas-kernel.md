# FINDING 2026-08-14 — two implementations, one BLAS kernel: agreement without independence

**BEN-188.** Lane D (comparator), while calibrating the `OI-121` `C_stat` comparator's tolerance.
Probe: [`state/probe-cstat-tolerance-calibration-20260814.py`](state/probe-cstat-tolerance-calibration-20260814.py).
Predeclaration: [`COMPARATOR-PREDECLARATION-20260814-cstat.md`](COMPARATOR-PREDECLARATION-20260814-cstat.md) §1.3a, §4.C.

## What happened

`OI-121`'s design rests on one premise: *two implementations written blind to each other, agreeing
element-wise, is a far stronger claim than a reviewer nodding at one.* That is correct, and it is
why the design is worth its cost. But it quantifies over **implementations**, and the artifacts it
actually compares are **outputs**.

Calibrating the comparator's tolerance — checking it would not false-alarm on two *correct* builds —
meant computing one sample covariance four legitimately different ways and comparing all six pairs:

| pair | worst correlation-scaled disagreement |
|---|---|
| `np.cov` vs `Xc.T @ Xc` | 2.217e-16 |
| `np.cov` vs `np.einsum` | 2.217e-16 |
| `np.cov` vs sum-of-outer-products | 6.256e-16 |
| **`Xc.T @ Xc` vs `np.einsum`** | **0.000e+00 — bit-identical** |
| `Xc.T @ Xc` vs sum-of-outer-products | 4.171e-16 |
| `np.einsum` vs sum-of-outer-products | 4.171e-16 |

`Xc.T @ Xc` and `np.einsum("ki,kj->ij", Xc, Xc)` are different source text, different API, different
mental model. They agreed **to the last bit**, because NumPy dispatches both to the same BLAS
`dgemm`. Not "agreed within tolerance" — *identical*.

## Why this is the dangerous shape

An element-wise comparison of these two would report the strongest possible result: **zero
disagreement across all 81,225 entries.** Every metric in the harness is at its floor. There is no
diagnostic anywhere in the comparison that distinguishes this from two genuinely independent
computations that happen to be correct.

And the failure is silent in the direction that matters. A *disagreement* is loud and gets
investigated. **Perfect agreement is the outcome everyone wants**, and it is exactly what a
collapsed independence premise produces. The record ends up stronger than its evidence — which is
this campaign's recurring failure and, not incidentally, the declared specialty of the `codex` judge
`OI-121` routes its output to.

> **Check:** an agreement-between-implementations argument is only as strong as the claim that two
> **computations** occurred. Two authors is not two computations. Before treating agreement as
> evidence, establish that the two artifacts were not produced by the same underlying kernel,
> library call, or copied snippet.

## What it does not mean

It does not mean `OI-121`'s design is wrong. Dual construction still catches the things it was
chosen to catch — a `ddof` slip, a bin-order mismatch, a mis-globbed member list, a wrong centring —
because those are decisions made *above* the kernel and two builders make them independently.

What collapses is the claim's **reach**. If both implementations bottom out in
`np.cov(X, rowvar=False, ddof=1)`, their agreement is evidence about the calling code and about
float64 determinism, and it is **no evidence at all** about whether the covariance formula is the
right one. That distinction has to be stated when the result is reported, or the result overclaims.

## Remedy, and why the comparator cannot apply it

The natural check — read both implementations and see whether they genuinely differ — is closed to
me twice over. My constraints forbid reading either builder's code, and reading it would end my
ability to referee the two artifacts. **So the remedy has to work without anyone breaking a
constraint:**

1. Each builder's artifact carries a **`method_declaration`** — one line naming its core
   computation. Cheap to write, impossible to fill in honestly while hiding a shared one-liner.
2. The **judge**, not the comparator, rules on whether two genuinely different computations occurred.
   The judge is already reading for "the record is stronger than its evidence," which is precisely
   this.
3. The comparator reports agreement **conditioned** on that ruling, rather than as an unqualified
   claim.

`method_declaration` is in the artifact contract at predeclaration §6.

**The judge seat is empty as of 2026-08-14** — both `codex` accounts are out of quota (personal
until 2026-08-20, school out of workspace credits), verified by the orchestrator by dispatching and
reading the errors rather than assuming. **The requirement stays in the contract anyway.** A
declaration costs a builder one line and is worth capturing before anyone can rule on it; the
alternative is asking for it later, after both builders have moved on, when any answer is
reconstruction rather than record. **The ruling is not rehomed to the comparator** — adjudicating
whether two computations occurred means reading both builds, which is exactly what this role must
not do. So the remedy is currently **filed and unowned**, which is the honest state of it, and the
empty seat is with Joseph.

## Family

- `BEN-173` — a positive control on one artifact and none on its sibling.
- `BEN-186` — a check whose input was built by the code it re-derives with.
- **`BEN-188`** — two implementations whose agreement is guaranteed by a shared kernel.

`BEN-186` and `BEN-188` are the same defect at different scales. In `BEN-186` an assertion's argument
came from the code the assertion re-derives with, so the check could not disagree. Here, **an entire
verification design's two inputs come from the same kernel, so the design cannot disagree.** Both are
found by asking *where did this operand actually come from* — one call frame away in the first case,
one library dispatch away in the second, and invisible at the comparison site in both.
