# BEN-243 — absence of an objection is not a resolution

**Filed:** 2026-08-14 by lane B (Gate 6), about its own record-keeping, on the same day as `BEN-241`
and sharing its root. **Cost:** one retracted section; caught by the mediator within the hour, not by me.

## What happened

`REQUIREMENTS-20260814-cstat-assembly-conventions.md` §3.1 recorded a genuine conflict I had found and
surfaced deliberately: my requirement put `C_stat` on `(n_reported, n_reported)`, lane D's committed
comparator predeclaration (`:168`) required `(285,285)`. Surfacing it was the assignment — the mediator
had asked for exactly this, *"before two builders start, not discovered by D at comparison time."*

The mediator then relayed that D had read the requirements and was realigning its harness to
`(n_reported, n_reported)`. I wrote the section's epitaph:

> **RESOLVED IN FAVOUR OF `(n_reported, n_reported)`.** … the reconciliation I proposed below was not
> adopted, and the simpler resolution won.

**That was D's position for about twenty minutes.** D reconsidered and proposed a third option — emit
**both** forms — which the mediator endorsed to C, and which is better than either original on the
merits. My "resolved" was a snapshot of a transient state, written into a committed document as an
outcome.

## Why the third option is better, since the record should say what I got wrong about

If only the full `(285,285)` form is compared while the **published** object is the reduced one, the
reduction is verified by nobody — and the reduction is exactly the operation D and I had *independently*
flagged as error-prone, because the reported index set is contiguous only within rows
(`[0..227] + [229..246] + [254..265] + [281..284]`). *"The comparison passed"* would be a true statement
about an object that is not the deliverable. **That is `BEN-185`'s shape**: a property proved on the
wrong object, reported inside a passing suite.

So the sequence was: I raised a real conflict, conceded it too early, and the eventual answer landed
**closer to my original position than to the version I conceded to**. Conceding fast is not the same as
being wrong, and it is not a virtue when it removes a live option from the record.

## The root, and why this is the same finding as `BEN-241`

`BEN-241`, four hours earlier: I claimed a predeclaration did not exist because my search did not find
it, and built a blocking finding on the claim. Its lesson was *an absence claim needs a stated search
that would have found the thing.*

This one is the same operation on a different object:

| | absent thing | what I concluded |
|---|---|---|
| `BEN-241` | a document my `grep` missed | it does not exist |
| `BEN-243` | an objection nobody had raised yet | the question is settled |

Both are **treating the absence of a visible counter-position as a positive result.** The first is about
evidence, the second about consensus, and the second is the more insidious because there is no search I
could have run — the counter-position did not exist yet. There is no amount of diligence at time *T*
that establishes what a peer will think at *T + 20 min*.

## The rule

**A disagreement is closed by the DECIDER, not by the last party to concede.**

Concretely, for any conflict recorded between lanes:

- Write `**STATUS: OPEN, awaiting <X>'s ruling**` and **name X**. Here X is lane C, which owns the spec;
  neither D nor I had standing to close it, and D's realignment was a concession, not a ruling.
- Record each party's position with its origin, as a table, so a third proposal is an *addition* rather
  than a rewrite.
- Never write a resolution on the strength of a relayed position. A relay is a snapshot; a ruling is an
  artifact.
- **Retracting a premature closure costs one edit. Defending one costs the record** — and a closed
  section stops attracting the attention that would have produced the third option.

## What made it recoverable

The mediator flagged it explicitly as time-sensitive, in terms — *"I would rather you not record a
concession that the record may contradict in an hour"* — and noted that the outcome might land closer to
my original proposal than to the version I had conceded to. **That is the correction working the way the
campaign intends**, and it is the second time today the same lane pair caught this class in each other's
work; the mediator's own error (proposing the file I had just quoted as the comparison arm) was the
mirror image, an implication neither of us was carrying.

Also worth recording: **D disclosed unprompted that its harness was already written for `(285,285)`, so
it was not neutral, and then argued for the option that costs it rework** — *"the published object should
be the verified object, and my convenience is not a reason to verify the intermediate instead."* An
interest declared and then argued against is stronger evidence than a position with no interest at all,
and it is why D's third proposal should carry more weight than my second thoughts.

## Related

- `BEN-241` — the same operation on a missing document; filed the same day, by the same lane.
- `BEN-185` — a property proved on the wrong object, reported inside a passing suite; the reason the
  third proposal is better than either of the first two.
- `BEN-189` — why the full-grid form needs absolute rather than relative eigenvalue metrics.
- `BEN-201` — a retraction that lands in the index but not at the point of use is not a retraction;
  which is why §3.1 was reopened in place rather than annotated elsewhere.
- `OI-121` — the dual-build authorization this conflict arose under, since superseded (one builder).
