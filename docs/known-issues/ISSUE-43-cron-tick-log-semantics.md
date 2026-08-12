## `cron-tick.log` is a CRASH log, not a tick log — its staleness indicates HEALTH (found 2026-08-06, re-derived wrongly 2026-08-11, filed here 2026-08-11)

The scrontab block that runs the waker's tick is:

    #SCRON -o .../state/waker/logs/cron-tick.log
    #SCRON --open-mode=append
    */5 * * * * /usr/bin/python3.11 .../wakerctl.py tick --quiet

`-o` with **no `-e`**, so it is combined stdout+stderr, opened in **append** mode. And `tick --quiet` is silent
on success — the repo asserts this rather than assuming it: `wakerctl.py:1273` requires *"quiet tick must make no
provider call"* and `:1297` prints *"quiet ticks silent"*.

**Therefore the file receives bytes only when something fails, and its mtime is the time of the last FAILURE,
not the last run.** A three-week-stale `cron-tick.log` means *no crash in three weeks*. **The staleness is the
healthy state and the name says the opposite.**

**Judge cron liveness from `state/waker/last-tick.json` (or `LEDGER.tsv`) mtime, with `TZ=UTC` pinned.** Pinning
the timezone matters: comparing a local-clock timestamp against cluster UTC produced a spurious four-hour gap
here on 2026-08-11 before it was caught.

**AMENDED the same day — "never use `cron-tick.log`" was WRONG, and the correction matters because it forecloses
the only discriminator for one real failure mode.** `scan()` calls `evaluate(ctx, watch)` inside its watch loop
**with no per-watch guard**, and `_write_tick_receipt()` is **after** the loop; `tick()` calls `scan(ctx)` as its
first statement, also unguarded, before `dispatch()` / `idle_guard()` / `notify_guard()` /
`status_report_guard()`. Verified in the file. **So one exception from one watch skips the receipt** — and
`last-tick.json` freezes while the cron process keeps running perfectly every five minutes. Under that failure
the instrument this entry designated authoritative reports "dead cron", which is the wrong conclusion in the
wrong direction. **The pair is the instrument, not either file:**

| `cron-tick.log` | `last-tick.json` | meaning |
|---|---|---|
| stale | fresh | **healthy** — the steady state |
| stale | stale | **cron not running** — queue, scrontab, or walltime |
| **growing** | **stale** | **`scan()` crashing every tick — process alive, waker DEAD** |
| growing | fresh | a non-fatal write; read it |

So: **`last-tick.json` is authoritative for liveness only while `cron-tick.log` is not growing.** Rows 2 and 3
demand opposite responses — *restart the cron* versus *fix a watch* — and only the growth of the "never use it"
file separates them. *Caught by the oversight session reading the third finding out of the same 2026-08-06 log
entry that produced this row.*

**The general rule underneath, now with two files proving it needs to be general:** `cron-tick.log` and
`last-tick.json` are both quiet-means-what? artifacts and **quiet means opposite things in each**. BEN-028 says a
quiet log does not mean a dead job; the rule underneath is that **quiet has no fixed meaning until you know the
write condition.**

**The traceback the file does contain is from a superseded revision.** Its frames are `evaluate` at `:432`,
`main` at `:1253`, module at `:1275`; `wakerctl.py` is now 1420 lines and those numbers land on unrelated code.
The current equivalent site is `:484` and is guarded twice —
`float(submitted) if submitted.isdigit() else parse_utc(submitted)` inside
`except (TypeError, ValueError): return unreliable_step()` — so the
`'1784527278\nRUNNING|1784527278'` multi-row-`squeue` path that crashed is **not reachable**. Nothing to fix in
the writer, and that parse bug is closed.

**NOT FIXED, deliberately.** The residual defect is entirely the **name**. Renaming means touching
`install_cron`, which strips and rewrites the whole scrontab table and reads fail-open (`read_scrontab` returns
`[]` on a failed listing — see the entry above), so a naming problem is not worth that blast radius on shared
infrastructure. **Document it; do not touch the table.**

**Why this is filed late, and that is the transferable part.** This mechanism was established correctly on
**2026-08-06** and written only into the chronology log
(`nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md:2953`: *"a stale mtime is the expected steady state"*). It was
**never written to its canonical home**, which per `CLAUDE.md` is this file. On 2026-08-11 **two sessions
re-derived it wrongly within an hour** — reading the staleness as *"a file that lies about liveness, worse than
no file"* — and one routed a confident, wrong diagnosis (*"the writer is broken, investigate the parse bug"*) to
another lane, which agreed with it. **A fact in the chronology is not retrievable; only its canonical home is.**
That is `CLAUDE.md`'s own *write a fact in its home, index it everywhere else*, and this is what it costs when
skipped: the same ground re-covered twice, wrongly, five days later.

It also inverts **BEN-028** in a way worth holding beside it: there, *a quiet log does not mean a dead job*.
Here, **a quiet log means a healthy job** — and the quiet was read as the symptom. Before reading any artifact as
evidence, **establish its write condition**: a file written only on failure cannot report success.


