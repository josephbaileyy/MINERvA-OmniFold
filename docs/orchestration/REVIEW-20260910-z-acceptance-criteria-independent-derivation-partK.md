# PART K — the F6 / reviewer-F3 convergence, and F6's predicate does not reach it

**Owner:** independent-assessment lane. **Base of measurement:** `6f24fb00`.
**Written before rev. 3**, so that a clause citing `assessor-F6` is not written against a reading of
F6 that F6 does not support.

**CITABLE FOR:** §K.2's scope delimitation of my own `F6`, and §K.3's named gap.
**NOT CITABLE FOR:** anything about `s_proj`, §4.3 or `A-7`. Out of slice; see §K.4.

---

## K.1 — THE CONVERGENCE IS REAL AT THE LEVEL OF THE HAZARD

Relayed: the mathematical reviewer's `F3` measured that at Z's sparsity, `s_proj` on a functional with
negligible overlap with `range(C)` splits three ways over 500 trials — 349 aborting while blaming the
operand, 4 aborting with the message §4.3 claims, and **147 not aborting at all, passing `base > 0` on
a round-off positive and dividing by it.**

`F6`'s grounding re-verified at `6f24fb00`, since another lane is now citing it:
`eavailW_covariance.py:410-413` reads *"a zero variance does not look like missing data — it looks
like a very good measurement, and any chi2 or significance built on it divides by it."* The fail-open
is at `:425-432`, and its warning is gated on `if _ew_empty.size` — i.e. it fires **only** for rows
receiving no reported 5D bin.

**One hazard, measured twice from opposite ends: a variance that is positive only by round-off, read
as a real measurement.** The counting discipline is right — two independent measurements of one
hazard, not two hazards.

**And `F6`'s own text already carries the structural point one level over**, which is why the
convergence is more than coincidence: `F6` says the existing warning *"does not cover the case `F-I`
opens"*, because `:429`'s condition is **exactly-empty** while `F-I` reaches near-zero at a **fully
populated** row. Exactly-zero versus round-off-positive is that same distinction, relocated.

## K.2 — BUT `F6` DOES NOT COVER `F3`'s COHORT, AND I WILL NOT LET IT BE READ THAT WAY

`F6` verbatim, as committed at `c695f209`:

> **F6.** **A released projected row** with zero or near-zero variance must be **refused or marked at
> the point of release**.

**Its subject is a released projected row and its predicate is the point of release.** `s_proj` is an
**acceptance statistic** evaluated during grading; it is not a released product. So `F6`'s predicate
never reaches `s_proj`'s internal baseline, and the step from *"`F6` requires the round-off case to be
caught at the point of release"* — true — to *"`F6` covers `F3`'s 147-cohort"* does not follow.

This is the correction I gave the coordinator about the sharing-structure finding, now applied to my
own item: **a real finding routed to a stage whose predicate does not cover it.** I would rather run
my own criterion over my own requirement than have it cited one stage too wide, and being the
beneficiary of the over-extension is exactly why I have to say so.

## K.3 — THE GAP THAT FOLLOWS, NAMED AND NOT SOLVED

If `F6` stops at the release point and `A-7`'s abort claim is exact only for an exactly-zero baseline,
then **a round-off-positive baseline inside an acceptance statistic is covered by neither** — wrong
stage for one, wrong condition for the other. That is a gap in the requirement set, not in either
finding, and it is the kind that survives review precisely because each half looks covered from the
other's side.

**I am not proposing the requirement that closes it.** Naming it is assessment; supplying it would
spend this lane's verdict on `A-7`, which is the trade Part E priced and §J.2 already declined once.
Whoever writes it should not be me.

## K.4 — NOT ASSESSED

- **Reviewer `F3`'s 500-trial split** (349 / 4 / 147) — not re-run and not verified. §4.3, `s_proj`
  and the `δ_proj` core are routed away from me; §K.1 accepts the convergence at the hazard level on
  the strength of `F6`'s half, which is mine, and takes no view on the measurement that is not.
- **Whether `s_proj` is ever released** in any form — if a future scope makes it a released quantity,
  `F6`'s predicate would reach it and §K.2 would need revisiting. Not measured.
- **`A-7`** in any respect, including its withdrawal.
