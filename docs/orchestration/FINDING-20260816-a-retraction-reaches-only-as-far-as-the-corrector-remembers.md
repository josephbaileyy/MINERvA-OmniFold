# FINDING 2026-08-16 — a retraction reaches only as far as the corrector's map of the corpus

**`BEN-302`.** Filed by the mediator, whose errors two of the three instances are. Lane B supplied the
sharpest formulation and the instance that proved the mechanism.

## The sequence, in one hour

1. Lane B, checking a successor instrument, finds the headline figure `~105 draw-sd` does not follow
   from its stated operands. Correct.
2. **The mediator "corrects" it and overshoots**, writing that the figure *"derives from nothing"* and
   that the sd yielding it, `0.000288`, *"appears in no artifact"* — **without grepping for it**
   (`6e05985`).
3. The Assistant lane recomputes `0.030252 / 2.889e-4 = 104.7` instead of accepting the retraction.
   The operand is in the receipt, in a field named `in_draw_sd_of_that_row`. **Mis-normalised, not
   fabricated.**
4. The mediator retracts the retraction and **enumerates the sites to fix from its own memory of where
   it had written the claim** (`0b1d33a`, `1f6bafa`), telling lane B about two.
5. **There were three.** The third was the `BEN-342` ledger row — **lane B's own**, carrying the
   mediator's wrong claim, in a file the mediator had edited twice that hour (`f386aa0`).

## The mechanism, which is not carelessness

A retraction is dispatched from the corrector's model of where the error went. **That model is complete
only for the sites the corrector wrote**, and an error's whole nature is that it gets repeated by
others. So the sites a retraction reliably misses are **exactly the ones that prove it spread** — the
error's own descendants in other lanes' documents.

Step 4 was performed carefully. The mediator *did* `grep` for the propagation — that is how the eight
sites were counted in the first place — and then, one turn later, enumerated the fix list from memory
instead of re-running it. **The tool was in hand and not used at the moment it mattered.**

## THE RULE

> **A correction is bounded by the corrector's map of the corpus. `git grep` is the only thing that
> isn't. Re-run the search at RETRACTION time, not only at DISCOVERY time — and re-run it after
> landing, because the corpus moved while you were correcting it.**

## The adjacent rule, which is lane B's and better than the mediator's wording

> **A null grep is evidence about the search, not about the world.**

**Three instances of that in this single session, in three different lanes:**

| lane | the false absence | how it was caught |
|---|---|---|
| mediator | *"`0.000288` appears in no artifact"* | the Assistant lane recomputed instead of accepting |
| lane B | *"the sd that would give 105 is stated nowhere"* — grepped the wrapper, the test and the predeclaration, **not the receipt** | the mediator's retraction, which was itself wrong |
| Assistant | two files reported `ABSENT ON BOTH TREES` from **guessed paths** | located them with `git ls-files` rather than believing the null |

**All three were caught by somebody running the search a second time. None was caught by a rule.**
Two of the three would otherwise have shipped a false absence into a committed document. **The
frequency is the finding**: this is not a lapse that a more careful lane avoids, it is what asserting a
negative costs when the search space is a 500-file corpus plus two divergent checkouts.

## Why this is not `BEN-228`

`BEN-228` is *derive at read time rather than narrating a fact*. This is one level up: **the corrector
did derive, then narrated the derivation's SCOPE.** The numbers were re-derived correctly at every step;
what was carried from memory was *the list of places the wrong number had reached*. A rule about
deriving values does not reach a claim about coverage.

Related: `BEN-315` (a null is evidence about the search), `BEN-342`, `BEN-360`, `BEN-361`, `BEN-228`,
`BEN-077`.
