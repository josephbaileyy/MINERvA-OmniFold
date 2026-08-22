# FINDING 2026-08-22 — a governing document instructed its own deletion, and it was router-inert for its whole life

**Filed by the publication close-out lane, on Joseph's ruling of 2026-08-22 (ruling 5), by the lane
that wrote the defective hold.** Subject:
[`HOLD-20260821-clause-c-verification.md`](HOLD-20260821-clause-c-verification.md).

**That file is preserved unchanged and must stay that way.** Do not delete it, do not rename it, and
do not edit it to record any of what follows. Its bytes are the evidence this finding is about. Its
lifecycle state is carried by [`MANIFEST-overrides.tsv`](MANIFEST-overrides.tsv), which now declares
it `ARCHIVAL / terminal` explicitly rather than by default.

## Half 1 — the hold instructs an action the retention convention forbids

The hold's `## Expiry` section ends:

> This hold ends when the clause (c) verifier files its verdict. […] If the verdict is filed and this
> file is still here, the hold has expired and the file is stale — **delete it.**

[`CONVENTION-document-retention.md`](CONVENTION-document-retention.md), under *What must not be
done*, states the opposite:

> **Do not move, rename, or delete** to express retirement. Paths are provenance.

The expiry condition **is** satisfied — the clause (c) verifier filed at `81905bba` on
`verdict/clausec-rerun-20260821`, after a first verdict at `33c0e0fa` on
`verdict/expiry-c-20260821`. So the instruction is live, reachable, and wrong. Two rules each correct
in its own scope, each unsafe under a precondition the other removes; this is the composition shape
the campaign keeps filing, and **both halves are mine** — I wrote the hold without reading the
convention that governs governing documents.

**The instruction is NOT disarmed in the file.** It cannot be, without editing bytes that are
preserved deliberately. `MANIFEST.tsv` gives the hold `read_policy=exact-path-only`, so a lane
reaches it by opening that exact path — and until this finding landed, nothing pointed from the hold
to any correction. **This document is the disarm, and it works only if the reader arrives here.**
That residual is stated rather than closed, and it is Joseph's to weigh.

## Half 2 — the hold was inert in the router from the moment it landed

Measured 2026-08-22 against `MANIFEST.tsv` at `57d9f3fb`, before any change in the commit that
carries this file:

| field | value | how it got there |
|---|---|---|
| `class` | `ARCHIVAL` | the generator's **default** — there was no override row |
| `event_status` | `terminal` | follows the default class |
| `immutable` | `yes` | `generate_manifest.py:238` — `ARCHIVAL` or `DEAD` maps to `yes` |
| `inbound_count` | `0` | nothing in the repository cited the path |

A repository-wide grep for `HOLD-20260821` over `*.md`, `*.py`, `*.tsv` and `*.sh` returned exactly
two hits: the file itself, and its own `MANIFEST.tsv` row.

**What this does and does not mean.** It means the committed artifact was carried by the router as
concluded, uncited, immutable evidence for the whole of its life, and that no lane could have been
routed to it. It does **not** mean the hold was ineffective as coordination: the two lanes it
concerned did observe it, because it was relayed in cross-session socket traffic. That is the honest
description and it is also the problem — [`AGENTS.md`](../../AGENTS.md) states that a merely relayed
result is not quotable, and a freeze that lives in a socket cannot bind a lane that was not on the
call. **Nothing here should be read as a claim that the committed file bound anyone. It did not.**

The hold's own opening paragraph confesses that it "existed nowhere in the tree for roughly twenty
minutes." That confession understates the defect by scoping it to a window. The window was not the
gap.

## The general defect, which is not about this file

`generate_manifest.py` defaults new documents to `ARCHIVAL`. That default is deliberate and correct
for concluded records — the retention convention says the bias protects the read path.
`derive_immutable` then maps `ARCHIVAL` to `immutable=yes`. Therefore:

> **Any document that lands without an override row is born archival, terminal, immutable and
> uncited** — including one written that morning to constrain work in progress.

Obligation 2 of the retention convention (*"when you create a document a session must read, declare
it `LIVE` in the same commit"*) is the only thing standing between a new live document and that
state, and it is **unenforced prose**. `generate_manifest.py --check` fails when the tree and the
manifest disagree, which catches a document *missing from* the inventory. It cannot catch a live
document *defaulted into* archival, because that manifest is not stale — it is correct.

## Relation to `OI-70`, and why the fix differs

Filed against [`OI-70`](../OPEN_ITEMS.md) rather than as a new open item, per `PB-20`. `OI-70`'s
original instance is the **mirror image** of this one, and the distinction is the whole point:

| | `OI-70` original (`CONVENTION-verifying-a-check-is-deployed.md`) | this instance (the hold) |
|---|---|---|
| override row | present, `LIVE open` — **correct** | **absent** |
| generated `MANIFEST.tsv` | stale, disagreed with the input | **correct** |
| what was wrong | the generated file | the document's classification, with nothing wrong anywhere |
| does regeneration fix it | **yes**, and it did | **no** |

`OI-70` was filed on the premise "the input is right; only the generated file is stale." That premise
does not hold here, so the remedy recorded there does not reach this half. Repairing it needs a check
that knows a document is *supposed* to be live — which is a change to what the hook admits, and
therefore Joseph's, not a lane's.

## What landed with this finding

1. This document, declared `LIVE / open`.
2. An explicit `ARCHIVAL / terminal` override row for the hold, replacing the accidental default.
3. The `OI-70` amendment recording the second instance and the mirror-image cause.
4. **No change to the hold's bytes.**
