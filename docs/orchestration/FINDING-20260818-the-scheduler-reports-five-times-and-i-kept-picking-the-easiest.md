# The scheduler reports several times and I kept picking the easiest one to get

**Lane E, 2026-08-18. `BEN-473`.** Three wrong numbers in one session, all from Slurm, all the same mistake:
I reached for the time quantity that was **cheapest to obtain** rather than the one the **question was
about**. Each was wrong by a large factor, each was caught by someone else or by a second look, and none of
the three looked wrong at the time.

| # | the question | what I used | what it should have been | error |
|---|---|---|---|---|
| 1 | how long does a task take? | `Elapsed` of tasks still **RUNNING** | `Elapsed` of **COMPLETED** tasks | 2.8× low (20 min vs 43) |
| 2 | what does the array cost? | wall-hours summed, labelled node-hours | wall-hours × `billing`/cores-per-node | 3.6× high (35.8 vs 10.0) |
| 3 | how long to drain 42 tasks? | `Elapsed` (run time) | `Start` deltas (dispatch rate) | 50–140× low (3 min vs 2.3–7 h) |

## Each one, and why it was plausible

**1. A running job's `Elapsed` is a LOWER BOUND on its duration, not an estimate of it.** I priced a
wait-vs-cancel decision from two tasks that were still running at 20 and 21 minutes. Both were past 39
minutes when I next looked; completed siblings ran 41:37–48:19. The decision had already been made on my
number.

**2. Wall-hours are not node-hours on a shared partition.** `50 × 43 min = 35.8` is correct arithmetic about
the wrong thing: `AllocTRES` reads `billing=36,cpu=36,node=1` of a 128-core node, so the charged figure is
`35.70 × 36/128 = 10.04`. `node=1` in `AllocTRES` means *one node was allocated*, not *one node was billed* —
which is exactly the phrase that makes the wrong reading feel supported.

**3. `Elapsed` says nothing about how fast an array DRAINS.** Tasks ran 7–11 seconds, so I said 42 remaining
would clear in "a couple of minutes". Dispatch is queue-limited: `Start` timestamps show tasks arriving in
**pairs about every 6.7 minutes despite `%10`** — 8 starts spanning 26m55s — giving 2.3 hours, and an
independent count 20 minutes apart gave ~7. The number I quoted was wrong by 50–140×, and a decision
(*don't spend an authorization to save three minutes*) rested entirely on it.

## The common structure, which is the point

In all three the wrong quantity was **one field away** from the right one, in the same `sacct` output, and the
right one required either a different filter (`--state=COMPLETED`), a second field (`AllocTRES`), or a
different column entirely (`Start` rather than `Elapsed`).

> **A scheduler reports at least five different times about a job — submit, start, end, elapsed, and the
> allocation it was billed for — and the cheapest to reach is almost never the one your question is about.**

And the tell is always the same: **the number came out convenient.** Instance 1 made waiting look cheap;
instance 3 made waiting look free; instance 2 made a rebuild look expensive and so made *not* rebuilding look
prudent. Three for three, the easy quantity flattered the answer I was already inclined toward.

## Why the failures don't look like failures

- `Elapsed` on a running job is not an error, a warning, or a null. It is a smaller true number.
- `35.8 node-hours` is arithmetically correct and dimensionally plausible.
- Neither is corrected by re-running the same command; only by asking a different question.

This is `my-recurring-failure-is-asymmetric-comparison`'s family with a scheduler as the instrument: I
compared two things measured under different conditions (running vs completed; allocated vs billed; run vs
dispatched) and believed the difference.

## The check to steal

Before quoting any scheduler-derived duration or cost:

1. **Name the question, then pick the field** — not the reverse. *"How long does a task take"*, *"what will
   this cost"*, and *"when will the queue clear"* are three questions with three different fields, and only
   the first is `Elapsed`.
2. **For a duration: filter to terminal states.** `sacct -X --state=COMPLETED`. A running task's elapsed is a
   lower bound and reads as an estimate.
3. **For a cost: read `AllocTRES`, and divide by the node.** On a `shared_*` partition the billed fraction is
   the whole story, and `node=1` does not mean you paid for a node.
4. **For a drain: read `Start` deltas, never `Elapsed`.** Dispatch rate and run time are unrelated, and under
   a `%N` throttle the realized concurrency can be far below `N`.
5. **When the number is convenient, re-derive it by a second route before acting.** All three of these were
   convenient, and that is the only warning any of them gave.

**Cross-references.** `my-recurring-failure-is-asymmetric-comparison` (the general form),
`BEN-027` (every count in a status report comes from a command run in the same turn — necessary and, as these
show, not sufficient: all three of mine *were* freshly measured), `BEN-471` (an exit code describes the
process, not the product — the same "read the field that answers your question" discipline applied to state
rather than to time), `BEN-472` (a watch armed on the wrong predicate).
