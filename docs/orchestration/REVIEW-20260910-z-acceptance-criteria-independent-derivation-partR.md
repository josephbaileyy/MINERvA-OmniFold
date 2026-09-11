# PART R — a routed QUESTION: under reuse, does A-7's statistic become a gate that cannot fail?

**Owner:** independent-assessment lane. **Code base:** `6f24fb00`. **No grade assigned.**

**THIS IS A QUESTION, NOT A FINDING.** `A-7` / `s_proj` / the `δ_proj` core are routed away from this
lane, and I am not assessing the statistic's construction, its boundary, or the designer's
measurement. What I am doing is composing **one relayed premise** with **one fact I measured**, and
routing the result — because it sits across two slices and therefore has no natural custodian.

> **⚠ ANSWERED AND WITHDRAWN, 2026-09-10 — §R.4. The answer is YES, and it resolves AGAINST the
> question.** The variation `s_proj` exists to detect **does** have support outside the reused blocks,
> so the population **can** exhibit the defect and `BEN-032` does not apply. §R.1's conjunction does
> not stand. Verified here, not relayed: `unified_throw_cov.py:434` reads `xx = z["xs"]` — **unfolded
> cross-sections** — and `:437-442` assigns those to `knob_x[band][idx]` for `kind == "knob"`. So the
> ~45 MAT bands are built from **per-member unfoldings**, not from the sample-covariance replicas
> (`:428-431` reads each slab's own `estimator_seed`/`draw_seed`). A real estimator-baseline effect
> therefore propagates into the bands: under the null the bands are identical and `s_proj = 0`, which
> is **correct reporting**; under the alternative the bands differ and the statistic **fires**.

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


## R.4 — THE ANSWER, AND WHAT SURVIVES IN A WEAKER FORM

**My half is withdrawn.** §R.2 named the condition that would dissolve the question — *"if the
member-to-member variation lives wholly in the blocks reuse holds fixed, the cancelling is correct
behaviour"* — and its converse was what my half needed. The mathematical reviewer answered it and I
verified the mechanism at `6f24fb00` rather than accepting the relay (see the banner above). The
population can exhibit the defect, so `BEN-032`'s definition does not reach it, and the class citation
that made the framing persuasive was apt on its face and wrong on the facts.

**RELAYED, NOT VERIFIED BY ME — what the reviewer says survives**, recorded because a struck question
that leaves a residue should not read as fully retired:

- **`B' = 0` is exactly false.** Bit-identity of the deterministic legs is a property of the
  summation route (`mii_anchor_comparator.py:241-246`), so the true reuse floor is the band-assembly
  reproducibility floor — of order ulps, not zero.
- **`B' ≤ δ_proj` still cannot fail on that branch, but for a BENIGN reason**: the ensemble
  contributes no noise because it is not resampled. So it is a **reporting** defect and not a
  soundness one — the check should read **not applicable** rather than **satisfied**. The reviewer has
  withdrawn its own *"a green state reachable without the work being done"* characterisation as right
  about the display and wrong about the substance.
- **The designer's sign is more right than it stated:** reuse strips the sampling noise from the
  difference while leaving the band variation, and the band variation is the **signal**. Reuse removes
  noise and keeps signal — best case, not a trap. Its enforceability then rests on the deterministic
  legs being **bit-reproducible**, a precondition rev. 7 acquired silently and which `F21` requires it
  to declare.

**Also relayed:** the reviewer raised and killed a candidate of its own — reading probe §13's
`C_det = A @ A.T  # identical across members` as assuming what A-7 exists to detect. It withdrew that
on the ground that `B'` is the **null** distribution, and the null asserts the offset has no real
effect, so member-invariant deterministic legs are the **correct** model of the null rather than a
smuggled assumption.

### R.4a — THE DETECTOR'S PRIOR ART IS STRICTER THAN ANY OF THE THREE OF US STATED

Verified at `6f24fb00` in `audit_gates_that_cannot_fail.py`:

- `:585-587` — a `--min-files` refusal whose help text names this exact class: *"a sweep that matches
  nothing reports success (**BEN-032 / SHELL_PIN_FLOOR idiom**)"*.
- `:592-593` — it **raises** rather than reporting: *"a detector failed its own power test; refusing to
  report a sweep whose detectors are not shown to fire (fail closed)"*.
- `:471-474` — an instance older than anything this exchange produced: a preprocessing step with no
  power arm *"silently blanked 95% of a file for eight days and every detector reported clean over the
  remains … the detectors were provably powerful over an input that was provably wrong."*

**So the repository already implements, and fails closed on, the rule the three of us spent seven-plus
instrument failures rediscovering.** Our can't-look-zero lesson should cite that file rather than stand
as new. That is the sharper form of this campaign's recurring law: **a document that catalogues a
failure shape is not protected from it — and here the *instrument* that enforces the rule existed while
three lanes violated it by hand.**

### R.4b — WHAT I WOULD KEEP FROM FILING IT ANYWAY

The composition was real and unowned — `(cause 6, Z)` owns reuse, `A-7` owns the statistic — and it
got an owner, a check and an answer inside one round. What killed it was **the one-line condition I
specified and declined to run from outside my slice**, which is the outcome §R.2 was written for. A
question that dies to its own named falsifier is a different object from one that dies to an argument,
and only the first kind is cheap to kill.
