# CORRECTION 2026-08-04 — the waker tick is not broken. It runs clean, and there is no malformed record to repair.

*This retracts a claim I made in commit `f424427`'s message. Recording it in the tree because
that message is immutable and its claim would send the next reader hunting for a defect that does
not exist.*

## What I said, and what is actually true

Commit `f424427` asserted:

> `wakerctl.py tick` has been **CRASHING** since Jul 20 … The cron is a no-op today for that
> reason and not for the intended one — two failure modes hiding each other.

**Both halves are wrong.** Measured 2026-08-04 05:15–05:30 EDT:

* The scrontab job `56160911` ran a real tick at 05:15 and wrote **nothing** to
  `cron-tick.log` — size, mtime (Jul 20 00:40) and traceback count (19) all unchanged.
* Run by hand: `wakerctl.py tick --quiet` → **exit 0**. Without `--quiet` →
  `{"emitted": [], "dispatch": []}`, exit 0. Tree clean afterwards.
* All **16** watches under `state/waker/watches/` are terminal (`fired` or `disarmed`), and
  **0 of 16 carry a `submitted` field at all**, so `parse_utc` is never handed anything.
* **There is no malformed state record.** The string `'1784527278\nRUNNING|1784527278'` exists
  only inside *log text* — `logs/cron-tick.log` plus three `logs/evt-*.log` — and the
  `cron-tick.log` occurrence is the traceback message I originally read it from.

So the cron **is** still installed and **is** a no-op, but for exactly the intended reason:
`idle_guard_ticks = 0` and every watch terminal. The codex-school lane's park does what its
ledger row claimed. There were not two failure modes hiding each other; there was one, and it
had already resolved.

## How I got it wrong, which is the part worth keeping

I read the tail of a log whose mtime was **fifteen days old** and reported it as current state.
The traceback was genuine, dated, and completely stale. Nothing in the log's last lines says
"this already stopped happening" — that only comes from checking whether the condition still
holds, which is a different action from reading the evidence of it.

That is the same error class I spent the night catching elsewhere: an artifact that looks like a
live signal because nothing in it is labelled with its own expiry.

## What survives, and is still worth doing

The historical crash was real and its cause is legible. `cron-tick.log` contains exactly one
timestamped line:

```
[2026-07-19T16:40:33.622] error: *** JOB 56139864 ON login22 CANCELLED AT
                                     2026-07-19T16:40:33 DUE TO TIME LIMIT ***
```

followed by 19 undated tracebacks, with the file's mtime at Jul 20 00:40. So a scrontab tick was
killed at its 12 h walltime **mid-write**, leaving a `submitted` field holding two values joined
by a newline — precisely the `<epoch>\nRUNNING|<epoch>` shape. The crashes ran from that
cancellation until the affected watch went terminal, then stopped on their own.

Two robustness points therefore stand on their own merits, as prophylaxis rather than repair:

1. **Make the watch writer atomic.** A walltime cancellation mid-write produced a torn record
   once and can again. `agentctl.atomic_write_json` already exists and is already used elsewhere
   in `wakerctl.py` (e.g. the idle-state write at ~line 1017); the watch-record path evidently is
   not using it.
2. **Make `evaluate()` fail closed per watch, not per scan.** `scan()` (line 544) calls
   `evaluate()` inside its loop with no isolation, so one unparseable record aborts the whole
   scan and silently disables **every** watch, not just its own. That is not hypothetical — it is
   what the July incident did. A per-watch `try` that disarms and reports the offender would have
   turned a global outage into one flagged watch.

## What is retracted

* "the tick is crashing" / "has been crashing since Jul 20" — **no**, it runs clean.
* "the cron is harmless because it crashes" — **no**, it is harmless because of the park.
* the remediation step "find the offending watch with `grep -rn 'RUNNING|' state/waker/` and
  repair its `submitted` field" — **moot**. That grep hits four log files and zero records.

The scratchpad note this supersedes (`FINDING-20260804-wakerctl-tick-crashes.md`) was never
committed and should be discarded rather than read.
