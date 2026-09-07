# RECORD 2026-09-08 — the Z operand-schema assignment, the BLOCK it first returned, and the PASS
# that followed, written down together with the implementation that carries them

**Status:** landed with the implementation at `afac9edb`. **This record does not close the
operand-schema finding.**

## 0. What this is, and what it is not

This is a **record of an assignment as it was supplied**, together with the review history of the
change that answers it. It is **not a fresh ruling by the decision owner**, and nothing in it should
be read as one.

**Provenance, stated because it is the whole basis for trusting the text below.** The assignment
reached the integration lane from the **coordinating session**, which received it in the decision
owner's own handover to that session. The integration lane did **not** receive it from him directly
and did not witness the handover. Attributed, not asserted.

**Why it is written here at all.** Until this file, the operand-schema finding existed **nowhere in
this repository** — no tracked document matched it and no `FINDINGS.md` row mentioned it. Its only
statement lived in conversation. A finding that is fixed but never written down leaves a reader of
the log able to see the repair and unable to see what it repaired. That gap is the reason for this
record, and closing it is the only thing this record does.

## 1. The assignment, verbatim as supplied

> Close the operand-persistence schema finding with a bounded writer/reader change. Version the
> persisted null-operand format and bind its producer/code identity to the declared construction.
> Make the existing load_null_operands helper validate the supported schema and required semantics
> before returning operands. Missing, unsupported, or incompatible versions must fail explicitly;
> never infer current format from the presence of familiar keys. A writer identity is provenance,
> not proof of correctness. Add positive round-trip tests and negative tests for missing/unknown
> versions, incompatible metadata, missing operands, and malformed shapes/types. Preserve the
> scientific boundaries as WITHHELD.

The sentence that names the defect precisely is *"never infer current format from the presence of
familiar keys"*: the reader accepted three unversioned arrays on key presence alone, so any producer
that happened to write those three names was treated as writing the current format.

## 2. Round 1 — BLOCK, on two reproducible defects

The first independent review of the delta at `00df4dba` returned **BLOCK**, on two defects that the
reviewer reproduced rather than argued:

| | |
|---|---|
| 1 | the declaration's own **construction object was bound to nothing** — it was carried but never checked |
| 2 | a **nonempty closure dict admitted a null digest**, so the container was checked instead of its contents |

Both were returned to the author rather than patched by the reviewer. Note the shape they share, and
it is the same shape as the finding itself: *a check on the object one layer nearer to hand than the
one that mattered.* The format was versioned, and the thing the version described was not.

## 3. Round 2 — PASS, on the repair at `afac9edb`

A **fresh independent reviewer**, not the one who returned the BLOCK, measured the repair and
returned **PASS**:

- **44 focused tests pass.**
- The **original construction mutations** and the **null-digest mutations** now **refuse** — the two
  round-1 defects have positive controls, not just fixes.
- A **valid unfamiliar `blob:`-provenance operand round-trips**, so the new strictness rejects
  wrongness rather than unfamiliarity.
- **Predicate reconstruction and all scientific boundaries unchanged.**
- Reviewer worktree clean.

**Broad comparison, as sets rather than counts:** `00df4dba` against `8c939996` gave **exactly the
same 13 failures**, 2753 passed and 6 skipped. The Z suite at the repair: **250 passed, 1 skipped**,
re-measured by the integration lane on the merged tree and agreeing.

**Non-blocking limitation, carried deliberately and NOT re-reviewed:** module ids are enforced
**nonblank**, not strictly trimmed as a comment in the code claims. This is a wording limitation
recorded so the next reader finds it here rather than rediscovering it; the coordinating session
directed explicitly that it must not trigger another broad review.

## 4. What this record does NOT do

- It **does not close the operand-schema finding.** Landing a fix and closing a finding are separate
  acts with separate owners, and the second belongs to the decision owner.
- It **adopts nothing scientifically**, changes **no numerical criterion**, and grants **no
  production permission**.
- The **four scientific boundaries remain WITHHELD.**
- It **arms nothing.** `docs/orchestration/state/r5-meter-receipt.json` is absent, with 0 commits
  touching it on any ref.
