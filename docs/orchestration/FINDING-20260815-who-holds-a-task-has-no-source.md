# BEN-300 — The holder of a task is a hand-maintained fact with no machine-derivable source

**Filed by:** the mediator (`personal-orchestrator`), against itself.
**Formulation:** lane A's, and better than the mediator's first attempt. Attributed deliberately —
see *Why the framing matters* below.
**Date:** 2026-08-15.

## What happened

Leg 0 was dispatched twice. First to a one-shot `claude -p` lane, which produced `692c6bd`
(the `--checkpoint-tier` flag, its regression test, and a new launcher). Then — while that lane was
still running — to lane A, which had *already* been holding Leg 0 from an earlier dispatch in the
same session.

A independently re-implemented the same flag, wrote its own regression test, and independently
rediscovered the three-launcher pin problem. When `692c6bd` landed first, A dropped its work
(`git reset --hard origin/main`) rather than merge two implementations of one function.

**Cost: ~40 minutes of a lane's time, zero of the repo's.** Nothing of A's survived and nothing
needed to; `692c6bd` was strictly more complete.

## The mediator's first framing, and why it is useless

*"I failed to check who held the task."*

That is the narrow reading and it produces a resolution — *check first* — against a thing there is
no way to check. **There is no file in this repo that records who currently holds a task.** Not
`LIVE-STATE.md` (generated, and its blockers array is hand-authored input — `OI-73`), not
`OPEN_ITEMS.md` (items, not holders), not `FINDINGS.md`, not the RUN_LOGs. `ListAgents` reports
which sessions are *alive*, never what they are *doing*.

So the instruction "check first" cannot be complied with, and a rule nobody can follow is not a rule.

## Why the framing matters

Every other stale-fact failure this campaign has recorded had a **wrong source that could be
checked**: a stale line number (`grep -n` derives it), a stale free-list (`grep` derives it), a
`MANIFEST` row claiming a hand-authored input is generated (the script derives it), a bare digest in
prose (`sha256sum` derives it). All of `BEN-228`'s instances share that property — the fact was
machine-derivable and somebody wrote it down instead.

**This one has no source at all.** It is `BEN-228` one level up: not a stale index *of documents*
but a stale index *of who is doing what*, with nothing to derive it from. The remedy for `BEN-228`
— *derive, do not narrate* — has no purchase here, because there is nothing to derive from.

## Enabling conditions, measured

* Sessions are killed and respawned without notice — twice tonight, four lanes at a time, on a
  memory-constrained machine. A respawned lane keeps its **name** and loses nothing visible, so
  `ListAgents` showing `A - ORCHESTRATOR` says nothing about whether the A that accepted a task is
  the A now listed.
* One-shot `claude -p` lanes do not appear in `ListAgents` at all while running.
* A dispatch is a message, and messages are not durable state. The only record that lane A held
  Leg 0 was in lane A's own context, which is exactly the thing that does not survive a kill.

## What would actually close it

Not stated as a recommendation, because the mediator has not costed it and it touches shared
control-plane infrastructure:

* a task-holder file under `docs/orchestration/state/` written at dispatch and cleared at report,
  so the holder becomes machine-derivable and `BEN-228`'s remedy applies; **or**
* accept the duplication as cheap. It cost 40 minutes and produced an *independent
  re-derivation* of `692c6bd`'s central design decisions — the flag defaulting to today's
  behaviour, and the three-pin problem — which is corroboration nobody paid extra for.

The second option is not a joke. Two lanes independently reaching the same design is evidence, and
this campaign spends real effort manufacturing exactly that.

## Attribution

The mediator caused the duplication and reported it as its own failure. **Lane A supplied the
correct diagnosis**, unprompted, in the same message in which it reported losing the work — that
the holder of a task is a hand-maintained fact with no machine-derivable source, and that the
mediator could not have derived it from where it sat. That is the formulation this row carries.

## The general form — why a fact with no source survives being wrong

Unifies `BEN-228` (a hand-maintained index of a machine-derivable fact goes stale silently) and
`BEN-244` (a stale blocker produces no error and no symptom, only work that never starts):

> **Consensus among restatements of a single source is not corroboration** — whether the
> restatements are citations, index cells, or two lanes each believing they hold a task.

This is what makes the class survive review. Lane A nearly filed a duplicate `BEN-229` row because
**two independent-looking statements agreed** that a finding had no ledger row — `FINDINGS.md`'s
index cell and the finding file's own header, 200 lines apart. They read as mutual confirmation and
were two copies of one claim, with **one author and one moment of truth between them**. The stale
Gate-4 blocker had eleven such copies and three readers, including this mediator, each of whom
checked and found agreement.

For a task holder the count is two — the dispatcher's belief and the lane's — and they are not
independent either: both derive from the same dispatch message, which is not durable state.

**Operational form:** before treating agreement as evidence, ask whether the agreeing statements
have *separate origins*. If they trace to one act, one author, or one moment, they are one
statement written down more than once, and the count is 1.

## A tell, supplied by lane A

> *A claim that cannot be wrong at the next reading is usually a claim about the wrong object.*

`BEN-229` v1 said *"`sacct` is not authoritative for an array that has not started"* — satisfied by
every reading available when it was written, which is why it felt finished. The corrected form is
per **task** (invisible from split until start), and it is falsifiable: it says what the next
reading will show. **A mechanism tells you what you would see somewhere you have not looked; a
symptom only tells you what you already saw.**

Recorded here rather than in `BEN-229` because lane A declined to write a competing version of a
line it knew this lane held — an application of this finding, twenty minutes after it was filed.
