# PART R — a routed QUESTION: under reuse, does A-7's statistic become a gate that cannot fail?

**Owner:** independent-assessment lane. **Code base:** `6f24fb00`. **No grade assigned.**

**THIS IS A QUESTION, NOT A FINDING.** `A-7` / `s_proj` / the `δ_proj` core are routed away from this
lane, and I am not assessing the statistic's construction, its boundary, or the designer's
measurement. What I am doing is composing **one relayed premise** with **one fact I measured**, and
routing the result — because it sits across two slices and therefore has no natural custodian.

---

## R.1 — THE COMPOSITION

**Premise 1 — RELAYED, NOT VERIFIED BY ME.** Rev. 7 at `3e7c3271` derives that `s_proj` is a function
of `C_k − C_0`, so byte-identical reused blocks cancel **exactly**, and measures `s_proj` as
**exactly `0.0`** for the reuse arm against `0.562%` for the regenerate arm — presented as the arms
differing *"by construction, not by degree."*

**Premise 2 — MEASURED.** `SPEC-20260906` §2.6c item 4 (`:1122-1125`): *"**The ensemble question is
OPEN and is named as open.** Whether Z reuses S's `stat_cov`/`ml_cov` digests or regenerates the
replicas is a **scientific** decision requiring a rationale … **This specification does not decide
it**, and §5 prices both."* So **reuse is a live branch that Joseph may choose.**

**The question.** If `s_proj` is exactly `0.0` on the reuse branch, then on that branch the statistic
proposed to control the stability of the released error bars **returns zero irrespective of anything
it is meant to detect.** That is the repo's own named failure class, and it has a detector:
`audit_gates_that_cannot_fail.py`, whose header lists **BEN-032 / BEN-025 — *"a check run over a
population that cannot exhibit the defect"*** — which is precisely the shape of a difference statistic
evaluated over members whose differing inputs have been reused byte-identically.

**The same fact reads two ways, and only one of them has been stated.** The designer's reading is
correct and useful: exact separation makes the two arms **discriminable**, which is a virtue. The
unstated reading is that on one of those two arms the statistic **cannot fail**. Both follow from the
same algebra; which one matters depends on a decision that is still open.

## R.2 — THE ONE THING THAT WOULD DISSOLVE IT, WHICH I CANNOT CHECK FROM HERE

If the member-to-member variation that `s_proj` exists to detect lives **wholly** in the blocks that
reuse holds fixed, then their cancelling is **correct behaviour** rather than a blind spot — the
statistic would be reporting, accurately, that nothing moved. `SPEC` §2.6b (`:1094`) records the
finalize launcher's own claim that *"`C_stat`/`C_ML` are #13-invariant → reuse existing"*, which points
that way.

**But if any part of that variation lives outside the reused blocks, an exact `0.0` cannot be
reporting it**, and the statistic is insensitive on that branch by construction.

**Which of those holds is inside the routed slice**, so I am not deciding it. It is a one-line check
for whoever holds `s_proj`: does the member family's variation have support outside the reused blocks?

## R.3 — WHY THIS IS FILED RATHER THAN MENTIONED

It is a composition of two lanes' open items — §2.6's reuse decision and A-7's adoption — and this
campaign has a catalogued shape for exactly that: **rulings from two lanes compose into defects, and
the composition belongs pinned in an artifact rather than in prose.** Neither slice owns it; the
reuse question is `(cause 6, Z)` and the statistic is A-7, and a question owned by nobody is the kind
that survives review.

**Routed to:** whoever holds `A-7` / `s_proj`, with the reuse branch's status as the trigger. **Not
asserted as a defect**, and it dissolves entirely under §R.2's condition.
