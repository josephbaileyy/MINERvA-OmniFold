# FINDING 2026-08-13 — Reading SOME artifact is not reading the one that GOVERNS the decision

**`BEN-205`.** Infrastructure block (`200-209`). **Attributed to the mediator
(`personal-orchestrator`), self-reported, filed by lane A at its request.** Lane A's contribution was
catching it, not committing it.

## What happened

Lane A's BEN block `190-199` was exhausted, so the mediator allocated it a new range. Before granting,
it did the responsible thing and **checked an artifact**: `max(existing) = BEN-204`, recomputed from
`FINDINGS.md` rather than taken from a handoff. Correct, and correctly read.

It then granted lane A **`210-219`**, deliberately skipping `205-209` as a buffer against anyone
mid-flight in the `200-204` block.

**But it never opened the block table** — the six-row table at the top of `FINDINGS.md` that assigns
ranges to lanes, which is the artifact the decision actually turns on. That table read:

```
| repo infrastructure (ledgers, read path, dispatch machinery) | `200+` |
```

**`200+` is open-ended and therefore contains `210-219`.** So an infrastructure writer computing
`max(existing)+1` — the exact idiom the table forbids in bold, and which the ledger records as having
failed four times, twice while the failing agent was reading the rule — would allocate `205`, then
`206`, and eventually land squarely inside lane A's new block.

**The allocation would have manufactured the very collision its buffer was designed to prevent.** The
buffer reasoned about *arithmetic* (who might be mid-flight near 204) when the hazard was in
*allocation* (an unbounded range that swallows any block placed above it). Only a closed range fixes
that, and closing it is one word.

Caught by lane A before the block was used, and fixed in the same commit that first used it:
infrastructure is now `200-209`, with `220+` marked unallocated.

## Why this is NOT BEN-212, and the difference is the whole finding

`BEN-212` is *a status field is not an artifact* — lane A read assignment off **lane names in a
`ListAgents` listing** and spawned a duplicate delegate. There the object consulted was **not an
artifact at all**; it was a cheap, derived, non-authoritative status string.

Here **both objects were real artifacts**, both were correctly read, and one of them was simply not
the one that governs. `max(existing)` is a genuine measurement of a genuine file. It is just not the
thing that decides whether a range is safe to hand out.

**This matters because the two have different remedies, and the remedy for `BEN-212` does not catch
`BEN-205`.** "Read the artifact, not the sentence about the artifact" — the standing rule — is fully
satisfied by what the mediator did. So is "recompute, never narrate." An agent could obey every
sourcing discipline this repo has written down and still make this error.

## The check

**Ask which artifact GOVERNS this decision, not whether an artifact was checked.**

For an allocation specifically: the governing artifact is the one defining the *space* being allocated
from, not the one reporting current *occupancy*. Occupancy tells you what is taken; the schema tells
you what may be given. `max(existing)` answers the first question and is silent on the second.

A cheap executable form, since a check costs zero and a convention costs tokens forever: **before
granting a range, assert the target range is disjoint from every other row in the block table** —
which fails immediately against an unbounded `200+` and forces the bound to be stated.

## Related

- `BEN-080` / `BEN-082` — the id-collision family. This is that shape **caught before it fired**
  rather than diagnosed after, which is the one instance of it the ledger did not previously have.
- `BEN-212` — the status-field sibling, same night, different object class.
- `BEN-105` — counts the `max(existing)+1` instances.
