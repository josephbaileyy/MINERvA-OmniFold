# FINDING 2026-08-14 — a receipt that re-derives perfectly and verifies nothing

**BEN-230.** Lane C (PET). Codex asked the question; codex was right and **I was wrong in writing,
beforehand, in a committed receipt.**

**One-line version:** mutate the data factor the *loader* applied, propagate it exactly as the loader
would, and the reconciler passes **57 of 57 checks** on a **13.6% shift in `R`** — because every
downstream number was recomputed from the mutated one, and **internal consistency is not power.**

## The question, and my wrong answer

Codex: *does any stage's validation actually have power over the data factor, or is it comparing the
builder to itself?*

I predicted, and committed to a receipt before testing:

> A sum-**changing** mutation **will** be caught — not by the factor-hash comparison, which is
> builder-vs-redraw and genuinely blind, but by `n_data_effective` and by `R`.

**That was wrong, and wrong in the direction that matters.** `n_data_effective` was in the tool only
as an *operand* of the R re-derivation. The loader computes `R` **from** `n_data_effective`
(`fullevent_fps_dataloader.py:971`), so a mutated factor yields a mutated `n_data_effective` and a
mutated `R` **that re-derive from each other exactly**. The R check confirms arithmetic the mutation
already made self-consistent.

I had the right observable and drew the wrong conclusion from it: I saw that `n_data_effective` is a
loader-side quantity and assumed a check therefore existed. **No check compared it to anything.**

## The measurement

Mutation: `+137` data counts on the loader-applied factor, propagated as the loader would
(`n_data_effective` → `numerator_signed_data` → `R` → `step1_measured_normalization` →
`step1_feed.normalized_sum`). `bootstrap.data_factor_sha256` left **untouched**, because that is the
*builder's* recomputation and the mutation is of what the *loader* applied.

```
BEFORE   n_data_effective 1010.0   R 1.25       verdict PASS   failures NONE
AFTER    n_data_effective 1147.0   R 1.42125    verdict PASS   failures NONE   57 checks passed
```

**A 13.6% shift in the class ratio, invisible.**

## The fix, and what it does and does not prove

`n_data_effective` breaks the circle only if something ties it *outside* the receipt's own arithmetic.
The loader computes it at `:951` as `float(df.sum())` from the array it actually received, shape-guarded
to `(n_data_rows,)` at `:949`, and it is persisted. So:

```python
c.eq("n_data_effective_equals_sum_of_REDRAWN_data_factor", float(n_eff), float(df.sum()))
```

Same mutation, after: **`FAIL`, on exactly that check and nothing else.** The R checks still do not
fire, and a test asserts they don't — claiming R caught it would misattribute the power.

**This is the only check anywhere with power over the loader's applied data factor.** Every other
data-factor check is two recomputations of one canonical stream agreeing by construction.

**What it proves:** same length (via the loader's shape guard) and same **sum**.
**What it does not:** identity. A permutation, or any sum-conserving change, still passes — and that
bound is a **test**, not a caveat, so nobody later reads the check as proving more. It is also real in
the live family: `replica_03` and `replica_08` share `n_data_effective = 4114512` with **different**
`data_factor_sha256`. Two real members this check cannot separate and the hash can.

## The fixture defect it exposed, which is why no test could have caught this

The new check failed on **every honest fixture** — 55 of 108 tests. Cause:
`_build_target_receipt` hardcoded `n_data_effective = 1010.0` against an `N_DATA` of `1000`. Internally
consistent, and **unrelated to the fixture's own data factors.**

So the fixture modelled a receipt whose effective count had no connection to its draw — precisely the
state the mutation creates. **The suite could not have exercised this class, because its fixtures were
already in it.** Fixed by deriving `n_data_effective = float(df.sum())` as the loader does. Third
fixture defect this repair has surfaced, after the missing training `.done` and the `mtime`-less
markers.

## Why I got it wrong, stated plainly

I reasoned from *where a quantity comes from* to *whether it is checked*. Those are different
questions, and the gap between them is exactly where this class lives. Writing the prediction down
before testing is what made the error visible instead of quietly absorbed — and it is the second time
today that recording a prediction caught me rather than flattered me, the first being the deployment
parity flip.

**The generalisation:**

> **A receipt whose numbers all re-derive is evidence of arithmetic, not of measurement.** Ask of every
> derived quantity: *what outside this receipt would have to change for this check to fail?* If the
> answer is nothing, the check is a tautology however many operands it publishes.

That is `BEN-077`'s ingredients rule one turn further on. Publishing operands lets a reader *recompute*
the verdict; it does not make the verdict *falsifiable*. Falsifiability needs an anchor the producer
did not also compute.

## Related

- `BEN-157` — the seven-defect audit this repair closes; item 6 is the ancestor of this one.
- `BEN-151` — the data stream as the one verified nowhere; its pessimism was corrected by
  `n_data_effective`, and this finding is the correction to that correction.
- `BEN-149` — a name that claims verification and thereby suppresses the check.
- `OI-60` — array identity, still open, producer-side, riding the next launcher.
- `OI-90` — `RUNS.tsv:296`'s wording, which this sharpens: the data half was never measured at runtime
  until now.
- [`state/gate5-data-factor-persistence-20260814.json`](state/gate5-data-factor-persistence-20260814.json)
  — where I recorded the wrong prediction, kept verbatim.
