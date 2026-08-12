# AUTHORIZATION RECORD — scope for the 6.0 TB ignored set (2026-08-12)

**Why this file exists.** The cluster inventory Joseph reviewed covered **0.045%** of the uncommitted
bytes: `git status --untracked-files=all` does not report ignored files and `.gitignore:2` is `*.root`, so
2.77 GB visible against **6,001,191,458,767 B / 19,570 files** actual. His own inventory instruction named
that flag. This records the scope decision that followed.

## THIS IS AN APPROVAL BY REFERENCE, AND IT IS A WEAKER INSTRUMENT THAN THE 12:2x ONE

His four words carry his authority. **They do not carry their own referent.** What he approved is the
mediator's prose — `[MEDIATOR]`-class text he **endorsed** rather than text he **authored**. The mediator
flagged this itself and asked that it be recorded this way.

**Consequence, stated so no lane resolves it locally:** if the referent's wording turns out ambiguous,
**the ambiguity is the mediator's, not Joseph's**, and resolution routes back through the mediator to him.
This must not be read as Joseph specifying the scope himself.

Compare `AUTHORIZATION-20260812-worktree-confirm-and-oi17-probe.md`, where he wrote the operative words.
There, the text *was* the instruction. Here, the text is an endorsement pointing at someone else's text.

## The authorization, verbatim and complete

> Yes do your suggestion

**Transcription:** same chain and same attestation as the prior receipt — transcribed by
`personal-orchestrator`, session `5f7d4b75-b1dd-4c6e-8f95-912b3b045c66`, from Joseph's typed message;
Session A copy-pasted it and **cannot see the original**. The mediator verified the prior receipt
character-for-character by sha256 and is expected to do the same here.

## THE REFERENT — the mediator's recommendation, reproduced as he read it. `[MEDIATOR]`-CLASS.

> **Recommendation: B now, C as the written disposition for the remainder, and A never.** The publication
> depends on a small named set, and that set is what needs digests and off-scratch copies before freeze.
> The rest is either regenerable — in which case C is the correct statement — or it isn't, and the way to
> find that out is to enumerate the ignored set *by name and size* without hashing it. That's cheap (a
> directory walk, no reads) and turns "6 TB of unknown" into "a list you can eyeball for anything that
> shouldn't be there." If something surprising shows up, it gets promoted into B's set individually.
>
> What I'd avoid is A. Ten hours of I/O to digest bulk that's regenerable by design buys protection you
> don't need, and it's the option that feels thorough rather than the one that's targeted.

Option definitions as he read them: **A** = full byte-level census of the 6.0 TB by lane and protection
status. **B** = targeted census of just the quoted products. **C** = declare the ignored set explicitly out
of scope.

## What is authorized, in execution order

**1. The metadata walk — FIRST, and it gates the rest.** Enumerate the ignored set **by name and size
only**. No hashing, no file reads, metadata only. Must use an enumeration that can see the set —
`--ignored=matching` or an equivalent walk — because `-uall` **demonstrably cannot**, reproduced in a
throwaway repo by both A and the mediator independently. Output is a **reviewable list, not a verdict**.

**2. B — the targeted census.** Digests for the **quoted products**: the set the publication actually
depends on. **Enumerate that set explicitly and by name BEFORE acting on it**, derived from
`VALIDATION_LEDGER.md` and the analysis note **rather than by judgement**, and report the list. The adopted
covariance `nd-unfolding/uq_5d/unified_throw_cov_5d.root` is already in it and already digested by the
2026-08-12 probe: `038c6132…`, 2,677,168,123 B, mtime `2026-07-13T09:15:41Z` — it had **no digest before
that probe** and is `.gitignore`d, so it never appeared in any inventory.

**3. C — the written disposition for the remainder**, after the walk is reviewed. Record it as a
**decision, not a silence**. **And record its weakness in the same breath: C asserts regenerability that
has NOT been verified.** Write it as **ASSUMED with the operand stated**, never as established — an
assumption recorded as a property is the exact shape this campaign keeps catching, and `CLAIMS.md`'s
vocabulary already distinguishes `ASSUMED` from `CITED` from `VERIFIED-*`.

**4. A is DECLINED.** No full hashing census of 6.0 TB.

**5. Promotion path.** Anything surprising in the walk is promoted into B's set **individually**, and each
promotion goes to the mediator **before** it is acted on.

## THE COPY BOUND — the mediator's own gap, recorded against the mediator by its request

The referent says *"digests and off-scratch copies"* **without bounding the storage**, and Joseph approved
it as written. The mediator disclosed this against itself: it had flagged the copy question to him twice as
*"the expensive half"* and then wrote a recommendation that folded it in unbounded.

- **Digests are unconditional. Do them.**
- **Copies are NOT authorized unbounded.** Home is ~40 GB and has run tight; the adopted covariance alone
  is 2.68 GB and a quoted set of several such objects could exceed it.
- **Report the total size of the quoted set before copying anything.**
- **Destination is almost certainly HPSS, not home** — this repo already runs digest-verified HPSS
  protection (240/240 on P3F-PET), so use the existing path and its existing verification discipline
  rather than inventing a destination.
- **If the set does not fit the intended destination, STOP and return to the mediator.** That is a storage
  decision Joseph has not made, and an under-specification is not a licence to make it for him.

## Unchanged and NOT authorized by this

The cluster tree stays under the eight-verb no-touch list — the walk is a metadata read and nothing else.
No salvage before Joseph's review. No adoption of anything, including the `.prehm`, which **failed on the
merits** (pre-remediation construction: `sqrt_tr_unified` −7.62% against adopted where BEN-033 records
−2.62% for the 122-throw case, and 6 keys against 9, missing the remediation's own additions). No cluster
worktree until `p4_evidence.py` is fixed and power-tested.
