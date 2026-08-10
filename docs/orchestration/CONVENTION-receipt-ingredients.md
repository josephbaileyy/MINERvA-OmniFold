# CONVENTION — every derived quantity ships with its ingredients

**Status: convention for this lane's receipts, adopted 2026-08-10 on Joseph's instruction.** Not a
suggestion and not merely a finding: a receipt that violates it is incomplete and should be regenerated.

## The rule

> **Every derived quantity in a receipt ships with the ingredients that let a reader recompute it —
> enough that the reported numbers CAN contradict each other.**

A verdict-only receipt is unfalsifiable. A receipt that publishes both a ratio and its operands can be
caught being wrong by anyone who does the division.

## Why it is a convention and not a preference

It is the only heuristic in BEN-077 that found a defect **without anyone suspecting one**. On 2026-08-10
Joseph could not reconstruct `ach/req = 0.8959` from the published `push` trajectory
(`1.121393 → 1.110901`, a factor `0.990644` against a required `1.002396`, i.e. `0.988`). He was not
auditing the metric; he was reading the numbers. The mismatch surfaced because the receipt carried
`push_prev`, `r1`, `pull` and `push` **separately** as well as the ratio built from them.

Had the receipt reported only `r1_achieved_over_required`, the defect — a first-leg average compared
against an end-to-end requirement, across an omitted `+4.22%` covariance term and a `+5.85%`
re-estimation term — would have been invisible, and the annealed arm would still be recorded as failing
its criterion by a wide margin instead of by 1.2% on a required move of 0.24%.

The other four instances in BEN-077 needed someone to go looking. This one needed only that the data be
present. **Redundancy is the cheapest detector available**, because the reader does not have to know what
they are looking for.

## What a compliant receipt carries

1. **Operands, not just results.** Any ratio, deviation or score publishes its numerator and denominator
   as separate fields. `dev_vs_R` ships with the sum, the count and `R`.
2. **The requirement's own definition.** Not just its value: what quantity it is a requirement *on*. This
   is what makes an achieved/required mismatch detectable — the pairing failure of BEN-077 is invisible
   unless both sides state their scope.
3. **Every intermediate stage of a multi-leg chain.** `push_prev → pull → push` publishes all three.
   Publishing only the endpoints hides which leg moved.
4. **Provenance tier per number.** Which checkpoint, which job, best-epoch vs `_final` (BEN-043). A number
   whose provenance differs from its neighbours' is not comparable to them, and only the receipt can say so.
5. **The tolerance AND its source.** `pet_diagnostic_quarantine` records
   `tolerance_source: "validate_pet_nominal_gate4.FROZEN"` for exactly this reason — a literal copied out
   of a frozen contract is a second copy that can go stale, and naming the source lets a reader check.
6. **Named non-comparability where it exists.** If a field must not be compared to a neighbour, say so *in
   the key*. The corrected trajectory harness ships
   `r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE` — ugly on purpose, because the previous
   short name is what let the comparison look reasonable.
7. **Label history when a verdict string changes.** `verdict_label_history` maps retired labels to current
   ones, so an older committed receipt stays interpretable rather than becoming a puzzle.

## What it costs, and the failure mode it replaces

Receipt size. Nothing else — these are kilobyte JSON files next to multi-hundred-megabyte artifacts.

The failure mode it replaces is the one this campaign keeps paying for: **a number that is correct,
reproducible, well-tested, and answering a different question than the one asked** (BEN-077). Every check
that operates *inside* one quantity passes. Only a reader holding two quantities can see the pairing fail —
and they can only hold two if the receipt published two.

## Related

- `FINDING-20260810-criteria-that-answer-a-different-question.md` / BEN-077 — the pattern this defends
  against, and the four instances
- BEN-070/071, BEN-076 — checks whose output does not depend on what they purport to measure
- BEN-072 — a gate mis-specified against a number it had itself already published, which is this rule
  failing in the other direction: the ingredient was there and nobody compared it
