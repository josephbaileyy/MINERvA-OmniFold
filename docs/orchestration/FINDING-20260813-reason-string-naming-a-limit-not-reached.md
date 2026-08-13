# FINDING 2026-08-13 — a scheduler reason string that names a limit which is not being reached

**BEN-153.** Lane C (PET), diagnosing the Gate-5 training throughput collapse.

**One-line version:** all 25 pending Gate-5 tasks reported `Reason=JobArrayTaskLimit` while **2** tasks
were running against an `ArrayTaskThrottle=10`. The reason named a specific, checkable limit that was
demonstrably not being reached — and because it was specific and checkable, two lanes believed it and
spent their first hypothesis on the array throttle instead of on the cluster.

## The measurement

```
squeue -j 56857233 -r -h -o "%T %r" | sort | uniq -c
     25 PENDING JobArrayTaskLimit
      2 RUNNING None

scontrol show job 56857233_25   ->  ArrayTaskThrottle=10   Dependency=(null)
```

2 running, throttle 10. `JobArrayTaskLimit` means *"this array's own concurrency throttle is holding the
task"*, and at 2-of-10 that is false on its face.

The real constraint was one `sinfo` away:

```
sinfo -p shared_gpu_ss11 -h -o "%.6D %.8t %C"
  1631    alloc 208768/0/0/208768     <-- ZERO idle CPUs
     6   drain$ 0/0/768/768
    20     resv 0/2560/0/2560
     5     plnd 0/640/0/640           (idle, but committed to an already-scheduled job)
```

The partition is full. That is a sufficient and complete explanation, and it has nothing to do with the
array.

## Why a *specific* wrong reason is worse than a vague one

A reason of `Priority` or `Resources` would have sent both of us straight to `sinfo`. `JobArrayTaskLimit`
is worse precisely because it is **better information**: it names one mechanism, that mechanism is real,
it is under our control, and it is trivially checkable. So it reads as a lead rather than as noise, and
the natural next step is to investigate the throttle — which is exactly the wrong place.

This is the same shape as `BEN-131` (a message more specific than its condition) and `BEN-149` (a name
that answers the question a reader would have asked), but the source is a **third-party status field**
rather than our own code, which means:

- we cannot fix it,
- it will say this again, and
- the only available defence is a habit rather than a patch.

## The habit

> **When a status field names a limit, check the limit it names before believing it.** A reason string is
> a hypothesis emitted by software that was not necessarily re-evaluated when conditions changed. It is
> evidence about what the scheduler last concluded, not about what is currently true.

Both halves of that check are cheap here: the reason names `ArrayTaskLimit`, and `scontrol show job`
prints `ArrayTaskThrottle` in the same breath. One is 10, the other is 2. **The refutation was in the
adjacent field of the same command's output.**

This is why `AGENTS.md`'s rule about judging liveness from `sstat` and artifacts rather than from status
fields generalises past liveness: it is the same instruction — *prefer the measurement to the summary* —
and a `Reason=` string is a summary.

## What was actually going on, for the record

Two constraints, neither of them the array throttle:

1. **Binding now:** `shared_gpu_ss11` has essentially zero idle capacity. Concurrency of 10 was
   achievable at 04:40 and is not achievable at 14:55. Nothing about the campaign changed; cluster
   occupancy did.
2. **Latent:** QOS `gpu_shared` has `MaxJobsAccruePU=2` — only two jobs *per user* may accrue
   age-based priority. `sprio -u josephrb` shows both slots held by lane B's `g6_floor` array
   (`AGE=138`, `AGE=231`) while the Gate-5 array sits at **`AGE=0`**. Gate 5 still has the highest total
   priority (67679 vs 57910/57816), so this is not what is costing it a start — but it means Gate 5
   cannot improve its queue position with time while a competitor can.

Stated as latent rather than causal on purpose: the accrual limit is a real exposure over a 25-member
remainder, and it is *not* the present blocker. Reporting it as the cause would have been a second wrong
answer arrived at more impressively than the first.

## Related

- `BEN-131` — a message more specific than its condition.
- `BEN-149` — a name that claims verification suppresses the check.
- `BEN-154` — the `sacctmgr` column misread that happened while chasing this same question.
- [`state/gate5-throughput-collapse-20260813.json`](state/gate5-throughput-collapse-20260813.json) — the
  full diagnosis with every operand.
