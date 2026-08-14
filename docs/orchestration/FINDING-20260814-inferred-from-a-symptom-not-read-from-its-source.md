# FINDING 2026-08-14 — Two numbers inferred from symptoms, and one was a seven-hour collapse that never happened

**`BEN-233`.** Lane C (PET).
**Status:** mitigated by two flags, not by vigilance. The mediator's throttle figure is corrected.
**Evidence:** measured commands and their output in
[`state/gate5-cstat-spec-measurements-20260814.json`](state/gate5-cstat-spec-measurements-20260814.json)
under `ARRAY_STATE_MEASURED_THIS_TURN_not_recalled`.

---

## Half one: the collapse that wasn't

Diagnosing extraction array `56936015`, I ran `date -u` (`11:56:46Z`) and read `sacct` completion
timestamps in the same turn. The last `End` was `04:56:39`. Read as UTC, that is **seven hours with no
completions** on an array with 35 tasks pending — a stalled array, and the kind of thing a lane escalates
immediately. I was one step from reporting it to the mediator, who would have taken it to Joseph.

What stopped it was that **the gap was suspiciously round.** Seven hours is exactly `UTC-0700`, and a
genuine stall has no reason to land on the hour. `sacct` prints **local time**; `date -u` prints UTC; I
had asked for the two clocks and then compared them as one.

Verified before use, rather than assumed:

```
SLURM_TIME_FORMAT="%Y-%m-%dT%H:%M:%S UTC%z" sacct -j 56936015_13,56936015_14 -X -n -P \
  -o JobID,State,Elapsed,Start,End
56936015_13|COMPLETED|00:13:44|...T04:42:55 UTC-0700|...T04:56:39 UTC-0700
```

Task 13 finished at `04:56:39 PDT` = `11:56:39Z` — **two minutes before I looked.** Throughput was
healthy: 14 tasks over `02:55:52 → 04:56:39 PDT`, ~8.6 min/task wall-clock at ~2 concurrent, ~14 min
each, except task 0 at `00:02:05` because it reused the predecessor's complete push.

There was a second, independent tell available and I had already printed it: task 14's `Elapsed` read
`00:09:10` against a `Start` of `04:48:11`. Under the UTC misreading those are inconsistent by exactly
the same 7 h. **The evidence contradicted itself on screen and I nearly read past it** — which is the
`BEN-077` ingredients heuristic working, in a case where the operands were already on the page.

## Half two: the throttle

The array's concurrency limit was reported to me as **2**. It is **10**:

```
scontrol show job 56936015 | grep -o "ArrayTaskThrottle=[0-9]*"
ArrayTaskThrottle=10
```

confirmed by the launcher (`--array=0-49%10`) and the submission receipt (`concurrency_cap: 10`). Two
concurrent tasks was **observed occupancy**, not a configured cap. Every pending task reports
`(Priority)`, so the constraint is queue priority and not our own throttle — and the proposed remedy,
raising the cap, would have bought **nothing**. Worth noting because it was offered as worth ~hours.

## The common shape, and why it is not "be careful"

Both halves are the same error: **a number inferred from a symptom rather than read from the thing that
sets it.** Two running tasks is a symptom; `ArrayTaskThrottle` is the setting. A stale-looking timestamp
is a symptom; the timezone offset is the fact. In both cases the authoritative value was one command
away and the inferred value was wrong.

This repo already has the rule — *"every ID, rank, count, and queue name in a status report must come
from a command run in the same turn"* (`BEN-027`). Both numbers here **did** come from commands run in
the same turn. That is what makes this a distinct finding rather than a repeat: `BEN-027` is satisfied by
a fresh `squeue`, and a fresh `squeue` is exactly what produces "2 running." **The rule has to extend
from freshness to authority: run the command that reads the setting, not one that exhibits its
consequences.**

Also note which side the near-miss fell on. Both errors pointed toward **false alarm** — a collapse that
had not happened, a cap that was not binding. A lane that escalates a phantom stall spends the
mediator's and Joseph's attention and, worse, makes the next real stall report cheaper to discount.

## Mitigation

Neither half needs vigilance; both need a flag.

- **Always export `SLURM_TIME_FORMAT` with `%z`** when reading `sacct`/`squeue` times, so the offset is
  printed and cannot be assumed. Cheaper still: never mix `date -u` with default Slurm output in one
  turn — ask both clocks in the same format.
- **Read `ArrayTaskThrottle` from `scontrol show job`** before reasoning about concurrency, and treat
  the running count as occupancy. Cross-check the pending **reason**: `(JobArrayTaskLimit)` means the cap
  binds, `(Priority)` means it does not.

One more that earned its place this turn: `sacct -X` **compresses a pending array range into a single
row** and reported `PENDING 1` where `squeue -j <id> -r` showed **35**. The campaign already knows this
(`squeue -r` for per-task truth) and it held again here.
