# Independent review: premise-(B) durability, `8b89ff36..68a3da8a`

**Owner:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Subject:** `8b89ff3601…` → **`68a3da8a47535976f5e74895ef42f4dac8c084cd`**, 2 commits, +372/−10.
`a71087e3` verified unamended (tree `51583946`); `main` `9dba1194`.

**Eligibility:** this object answers **my own** finding, and I remain eligible to review it. I named
a requirement with two disjuncts — *either the guard covers the claim path wherever it is touched,
or (B) is restated to what the guards establish* — and declined to name a mechanism. They
implemented both disjuncts; `FILESYSTEM_MUTATIONS` is not my design. My partial recusal on the
**ordering choice** (previous record) is unaffected and does not reach this object.

**VERDICT: the finding is CLOSED. The guard now matches the premise, and I reproduced the power
control myself. ONE NEW FINDING: the stated cost of violating (B) is correct for the case it
describes and incomplete for the other — and the omitted case is an authorization bypass, not a
refusal.**

**NOT CITABLE FOR:** landing, launch, spend, or anything on Lustre. `R4` suspended; Gate 2 FAIL.

---

## §1 — My finding is closed, and I reproduced the power control rather than accepting it

`FILESYSTEM_MUTATIONS` is genuinely operand-keyed — `(function, callee, operand expressions)` with a
per-entry rationale — and its three entries are exactly the three calls my own whole-module sweep
found (`_atomic_write_json`'s `os.replace` and `os.unlink` of its own temp; `recover_task`'s
`os.replace` of the partial output into evidence). Keying on the **operand** is the right move and it
is what survives the constraint that killed the module-wide ban: the question was never *does this
module delete* but *does it delete **that***.

**The power control, run by me with my own mutant** — the same `_tidy_claims` helper I used to
demonstrate the gap:

| | result |
|---|---|
| baseline, operand-keyed inventory | **OK** |
| `_tidy_claims` added, operand-keyed inventory | **FAILED — detected** |
| `_tidy_claims` added, seven-name recovery ban | **OK — slips past** |
| restored | **OK** |

So the paired claim holds exactly: the new guard catches what the old one could not, and the arm
demonstrating that is a measurement in the suite rather than an assertion in a commit body.

**Pinned in both directions** on the `METER_PRIVATE_DEPENDENCIES` precedent, so a *removed* entry
fails too — which is the arm that stops the inventory quietly shrinking to match a future edit.

**Their three self-caught items all check out.**

1. **The blind-spot arm is real and asserts the blindness.** It uses the exact invented rewording
   that failed their first over-general power arm — *"A claim, once written, will always still be
   there…"* — and `assertFalse`s that the pin matches it. It also carries the right instruction:
   *"if this now matches, the verb family was widened — update the recorded boundary rather than
   deleting this arm."* Narrowing the claim to what the pin does, and making the residual an
   executable arm rather than a caveat, is the correct handling; widening the verb list is the
   losing game they say it is, because the next paraphrase picks the next word.
2. **The exemption is counted.** `assertEqual(len(exempted), 1)` — exactly one line may mark itself
   as quoting the withdrawn wording, so exemptions cannot multiply into a way of keeping the old
   phrasing alive. That was the part worth verifying and it is there.
3. **`PREMISE_PROSE_LINES = 21`**, the measured value, not the guessed 22.

**"No behaviour change in the second commit" verified independently:** executable AST of
`z_precursor.py` at `689e2cb6` and `68a3da8a`, docstrings stripped, is **IDENTICAL**.

**Counts verified, not relayed:** read_ordering **26 OK** (3 added), recovery **65 OK**, ownership
**89 OK**, precursor **123 OK**.

**The withdrawal reaching the paraphrasing site is the right catch and the right method.** A
withdrawal that reaches the site that *states* a rule but not the site that *paraphrases* it is a
failure shape this campaign has paid for before; sweeping by subject-plus-verb-family rather than by
the keyword set that missed it, and then pinning the population, is what stops the next paraphrase
needing a reviewer.

---

## §2 — NEW FINDING: the stated cost of violating (B) is incomplete, in the direction that matters

The record bounds the cost of an outside deletion as: *a legitimately claimed product reads as
unclaimed, so the clause **refuses** — it resurrects the original symptom and fails closed*, and *no
deletion can make the clause **admit** a foreign product, because admitting requires a claim to
exist and deleting one never creates one.*

**Both halves are true, and I confirmed the first by execution. But they describe one of two states,
and the design itself distinguishes them.** `verify_task_ownership`'s own docstring says
*"(claim present, product present) means this task already ran to completion while (claim present,
product absent) means an attempt died before publishing; those call for different actions."*

Measured, with the real fixture:

```
claim deleted, product PRESENT  -> REFUSES  ("holds 1 product(s) whose basename this campaign
                                              DECLARES but which NO task ... has CLAIMED")
claim deleted, product ABSENT   -> ADMITTED
```

**In the pre-publication state a deleted claim is not a refusal — it is an authorization bypass.**
The fresh attempt runs as if it were the first: it takes a new `O_EXCL` claim, clause 9 has no
product to object to, and `campaign-recover` with its per-attempt approval is never entered. That is
precisely the act **Joseph's verbatim prohibition names**: *"Do not implement recovery by deleting a
claim and pretending the first attempt never existed."* The bounded-cost sentence, as written, makes
that act sound like a self-correcting nuisance.

**Severity.** Not a defect in any guard — it requires the prohibited act, and `FILESYSTEM_MUTATIONS`
now stops the module doing it. What is wrong is the **stated cost**, and stated costs are load-bearing
here because they tell a future operator how bad a stray `rm` is. One who reads "it just refuses,
fails closed" may treat a deleted claim as recoverable by re-running, which in the pre-publication
state silently produces an unapproved attempt wearing a first-attempt identity.

**Requirement, not a remedy:** the bound must cover both states, or be scoped explicitly to clause 7.
I am not naming a mechanism.

---

## §3 — On the recusal, and what remains withheld

The peer reports carrying my partial recusal to Joseph verbatim, instructing the owner not to change
the ordering on account of it nor re-argue it into certification, and disclosing that **it amplified
my pointer and is therefore not independent of the ordering choice either**. That is the correct
handling of all three: the label belongs to Joseph to resolve, and a second non-independent party is
better declared than discovered.

**Still withheld, unchanged and not re-attempted** (cluster dead: rc=255, sshproxy certificate
Sep 13 08:42, controlmasters empty): cross-client `O_EXCL` on Lustre; `os.mkdir` EEXIST on Lustre, a
different primitive to which my single-client measurement does **not** transfer; `JobRequeue`; and
the remaining suites of the six/eight-suite totals. Questions 3–7 remain Joseph's.
