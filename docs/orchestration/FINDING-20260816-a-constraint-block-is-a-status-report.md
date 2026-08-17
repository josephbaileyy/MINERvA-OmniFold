# FINDING 2026-08-16 — a constraint block is a status report, and it goes stale like any other

**`BEN-303`.** Filed by the mediator, about the mediator. Lane B supplied the corroborating step records
and the sharper account of why it was invisible.

## What happened

For roughly five hours the mediator ended every dispatch with a constraint footer containing the line:

> *"no scancel/scontrol — allocation `57128458` is held and idle, leave it up"*

It was sent to four lanes, repeatedly, in the block whose whole purpose is to state binding facts.

**`57128458` had TIMED OUT at `18:37:31`**, three hours after it started. Measured:

```
sacct -j 57128458   TIMEOUT   03:00:03   ended 2026-08-16T18:37:31
squeue              57142574  claude-hold  RUNNING   started 2026-08-16T20:04:51
```

A *different* allocation had been running since `20:04`. Lane B's `hRowIndex4D` readback, whose receipt
named `57128458`, actually ran in `57142574.1` — confirmed from the step records:

```
57142574 .0 20:04:56  29s   C4/C5 content-identity probe
         .1 20:16:40  12s   the hRowIndex4D readback        <-- the run in question
         .2 20:17:43   9s   5D key listing
         .3 20:18:40  14s   hRowIndex5D extension
```

**No measured value was affected. The products were read, not the queue. The defect is attribution.**

## The rule that was already written, and where it did not reach

`BEN-027`: *every ID, rank, count and queue name in a status report must come from a command run in the
same turn.* The mediator **wrote that rule into a dozen dispatch footers on the same night** and did not
apply it to the one fact those footers were asserting.

> **A constraint block is a status report.** It looks like policy — stable, restated, boilerplate — and
> policy is the one thing readers do not re-derive. **Any measurement embedded in boilerplate inherits
> the boilerplate's credibility and none of its own freshness.**

The general form, which reaches past footers:

> **A job id in a receipt is a measurement, not a label.** Bind a claim to the thing that can be
> re-derived, and re-derive it in the turn you assert it.

## Why nobody caught it: the tooling was good

`AGENTS.md` documents that `alloc_run.sh` **auto-requests a fresh allocation when the previous 3-hour
one has expired.** So every dispatch succeeded, every run completed, and nothing failed in a way that
would prompt a re-check.

> **A stale id survives precisely when the tooling is good.** An expired allocation that *broke* a run
> would have been caught in seconds. One that is silently and correctly replaced leaves a wrong id in a
> receipt **with no symptom at all.**

Same family as two other findings from the same night — the sweep's `|| true` false positive and the
colour-rendering assertion (`BEN-345`): **the failure mode is the absence of a symptom, not the presence
of one.**

## Division of the error, recorded as the lanes settled it

The mediator claimed the larger share on the grounds that it amplified the fact to four lanes. **Lane B
declined that framing and it is right:** B generated the false fact and put it in a **receipt**, which is
the durable artifact a future reader trusts; footers are transient. Both are `BEN-027`. The genuinely
new half is the mediator's — **that dispatch footers carry measurements at all.**

## THE RULE

> **Before restating a constraint that contains an ID, a count or a queue name, re-derive it. If it is
> too expensive to re-derive every time, it does not belong in boilerplate — put a pointer to the
> command there instead of the answer.**

Corroboration that fell out of the same check, worth its own line: `57128458.0` is recorded **FAILED
after 6 s**, which is the dispatch that died on node-local `/tmp` (`BEN-347`) — **the step record
confirms that account independently of the log that reported it**, which is a better class of evidence
than a log quoting itself.

Related: `BEN-027`, `BEN-228`, `BEN-347`, `BEN-345`, `BEN-344`, `BEN-302`.
