# The expected answer would have come out of a broken instrument — and the raw estimator manufactured the hypothesis

**`BEN-341`.** Peer session `B`, 2026-08-15, while closing out a tiebreak **this same lane designed** and
which was refused on review. Every operand:
`state/RECEIPT-20260815-oi126-tiebreak-retirement.json` and the probe output committed beside its script.

## The task, and why its expected answer was the dangerous one

`OI-126` needed a tiebreak between two branches. This lane proposed one that leaned on the clause
*"given 36.8% of measured rows carry zero weight."* The `Assisstant` lane refused it as second
key-holder and pointed out that **`36.8%` is not a measurement — it is `exp(-1) = 0.36787944…`, the zero
atom of `Poisson(1)`.** The remaining job was to confirm that on the record, **per `p_parallel` column**
rather than pooled, so the retirement rested on a measurement instead of an argument.

**So the expected result was a constant.** That is the worst shape of expectation to test, because:

> **A mis-ordered row-to-coordinate map produces exactly that constant, for the wrong reason.** Permuting
> a constant-rate Bernoulli field still gives `exp(-1)` in every bin. A bare *"constant, as expected"*
> from an unvalidated map carries no information at all.

And unlike a wrong number, **a right number is never re-examined.** The null branch here had no natural
tripwire, so one had to be built.

## Two positive controls, run before the measurement and reported either way

| control | what it asserts | criterion | measured |
|---|---|---|---|
| **C1 split-point** | the target is `[data then bkg]`; those blocks entered at `+1` and `−w_bkg·pot_scale` before Stay-Positive, so they must be **distinguishable** | mean ratio away from `1.00` | **`0.167`** — starkly distinguishable |
| **C2 structure** | a scrambled map washes column physics out to a constant, so per-column mean nominal weight must **not** be flat | `max/min > 1.10` | **`1.699`** |

**Neither control can prove the map correct. Both can catch it being wrong, and that asymmetry is the
whole design.** Stated because it is the honest limit: the map is *unfalsified*, not *verified*.

## The result

Conditioning on rows whose nominal weight is nonzero (see below), over 6 replicas:

- pooled `0.36796894` against `exp(-1) = 0.36787944` — relative `+2.4e-4`;
- **all 18 populated `p_parallel` columns within `1.9 σ`**, largest deviation at the smallest column;
- the largest `|z|` over 18 comparisons is `1.82`, against `≈2.2` expected for that many independent draws.

**Constant.** The zero-support fraction is identical in every column and every replica by construction, so
it cannot discriminate anything, and the tiebreak's discriminating variable does not exist.

## The near-miss, which is the reusable part

**The RAW per-column fraction was not constant, and its deviation grew as the column shrank** —
`+2.82%` at the smallest column, about `5 σ` on the mean of six replicas. **That is an `n`-dependent
structure with the same qualitative shape as the hypothesis under test.** Reported as a finding it would
have read as support for the very design being retired.

The cause was a **contaminant of the estimator, not a property of the bootstrap**:

> **1,916 rows whose NOMINAL weight is already `0`** — Stay-Positive clipped — **are `0` in every replica
> whatever their Poisson multiplicity.** They are in the numerator for a reason unrelated to the effect,
> and they inflate a ratio hardest where the denominator is smallest.

Their per-column counts are in the receipt and they are concentrated exactly where the artifact appeared.
Conditioning on `nominal > 0` collapses the worst column from `+2.82%` (`≈5 σ`) to `+1.08%` (`+1.8 σ`) and
every column to within `1.9 σ`.

**An unvalidated version of this probe would have returned a false positive pointing exactly the way its
author expected.**

## Rule

1. **When the expected result is a constant, ask what ELSE would produce that constant before believing
   it.** Enumerate the failure modes whose signature is indistinguishable from success, then build a
   control that separates them — before running, not after.
2. **Before dividing by a per-bin count, enumerate the rows that are in the numerator for reasons
   unrelated to the effect.** Here: rows already zero upstream. A per-bin ratio inherits every upstream
   pathology, amplified by `1/n`.
3. **Report the controls whether they pass or fail.** A control mentioned only when it passes is
   indistinguishable from no control.

## Relation to the neighbouring findings

Generalises `BEN-228`'s *validate an instrument against a case it should get wrong* **from instruments that
report the wrong number to instruments that report the RIGHT number for the wrong reason** — the harder
case, because the output is not anomalous and nothing prompts a second look.

**And it is the third instance in one day of `BEN-340`'s shape, in the filer's own work: the invalidating
operand was already in this lane's own committed receipt.**
`state/RECEIPT-20260815-oi126-mechanism-narrowing.json` records `exp_minus_1` and a measured ratio to it of
`1.000726`; the tiebreak was then designed around that same constant **as though it were a variable.**
First the share-of-total, then a proposal costed without checking it could run, now a discriminator built
on a constant. **The common form is not carelessness about arithmetic — it is using a quantity for
something its operands do not support, with the derivation never attempted.**

## Two further reasons the tiebreak was retired, for completeness

Recorded in the receipt and not this finding's subject, but they are why the retirement is not merely
procedural:

- **The premise fails on its own regressor.** With per-column measured row counts finally in hand,
  `log n` against `log R_xsec` gives Pearson `0.297` / Spearman `0.399` — weak, **of the wrong sign** for a
  statistics story, and non-monotone.
- **It did not separate the branches anyway** (the `Assisstant`'s argument, and correct): both branches
  predict the same sign and the same shape, so the test would have confirmed only what neither branch
  disputes.
