# The verification apparatus failed in the three ways it exists to catch — inside one hour, in scripts written to catch them

*Lane E, 2026-08-19. `BEN-478`. Campaign `EP-2026-08-17-data-only-cstat`.*

## Why this is one finding and not three rows

Three separate controls failed within an hour, and each failed **in the exact manner the control was written to
detect**. That coincidence is the finding: I was, in each case, holding the right principle and applying it to
the subject while the instrument went unexamined.

| # | the control | how it failed | what it was written to catch |
|---|---|---|---|
| 1 | arming a durable watch so a 3 h job cannot finish into silence | reported `RC=0` for two commands that both died on `SyntaxError` | *a control that reports success and never executed* |
| 2 | ISSUE-42's safe procedure, so `install-cron` cannot destroy other lanes' entries | ran correctly — but I nearly ran `install-cron` anyway, for a tick that already existed | fail-open data loss |
| 3 | a free-space check before copying evidence off purgeable scratch | measured the raw 22.8 TiB filesystem, **not** the 40 GiB quota that binds | writing into a full home |

## 1. `RC=0` for two commands that both failed

```
    $PY "$W" watch-add ... 2>&1 | sed 's/^/    /'
    echo "    WATCH_ADD_RC=$?"        # <- sed's status. Always 0.
```

Both `watch-add` and `install-cron` printed a `SyntaxError` traceback **and were recorded as `RC=0`**. This is
the **fourth** time today that `$?`-after-a-pipeline has bitten me, and the first three were all in the same
session — which is why the recurrence, not the bug, is the content here.

> **A FILTER IS A COMMAND, AND `$?` BELONGS TO THE LAST ONE.** The fix is not vigilance. It is: never pipe
> anything whose status you intend to read. Redirect to a file and read the file afterwards — the same rule
> `BEN-026` already states for diagnostics, applied to statuses instead of output.

**And the failure it hid was itself instructive:** `python3` on this login node is **3.6**, which cannot parse
`from __future__ import annotations`, so *every* `wakerctl` invocation was doomed. **The working configuration
was in output I had already printed** — the live scrontab entry calls `/usr/bin/python3.11` explicitly. I read
that line for a different purpose (confirming the tick existed) and did not notice it was also the answer to a
question I was about to get wrong.

> **THE ENVIRONMENT HAD ALREADY WRITTEN DOWN THE ANSWER.** A working invocation of the tool you are about to
> invoke is the best documentation available, and it is usually one `grep` away in a crontab, a launcher, or a
> previous job's script.

## 2. The near-miss that was not a failure

ISSUE-42's procedure ran in full and correctly: `scrontab -l` exit code checked **before** its output was used,
7 lines all inside the managed markers, **0 outside**, and a post-hoc diff confirming nothing was lost.

What nearly went wrong is that I had queued `install-cron` at all. **The managed block already contained a
working 5-minute tick.** Running a command documented to *fail open and destroy other lanes' entries*, in order
to install something already present, is pure downside — and the procedure I was carefully following would have
made it *safe*, not *unnecessary*. A safe procedure around a needless action still leaves the action needless.

> **"IS THIS SAFE?" AND "IS THIS NEEDED?" ARE DIFFERENT QUESTIONS, AND A GOOD ANSWER TO THE FIRST SUPPRESSES
> THE SECOND.**

## 3. A guard that measured a quantity nobody is limited by

```
    avail_kb=$(df -Pk /global/homes/j/josephrb | awk 'NR==2{print $4}')   # -> 22,861,492,864 KiB
```

Home is a shared GPFS filesystem with a **40 GiB quota**; `df` reports the *filesystem*, which had 22.8 TiB
free. The refusal could not fire, and **would have passed a home directory at 100% of quota**. The decision was
correct only because `myquota` was printed beside it and I read that instead: `home 22.50GiB / 40.00GiB
(56.2%)`.

This is `BEN-473`'s shape — *the number that was easy to obtain rather than the one the question was about* —
occurring inside a guard I wrote **because of** BEN-473. The right instrument was already in the same output.

## The common structure

In all three the correct principle was in hand and pointed at the *subject*: verify deployment by reading it
back; follow ISSUE-42; check space before writing. **What went unchecked was the instrument** — its exit
status, its necessity, and its units.

> **AN INSTRUMENT IS NOT EXEMPT FROM THE STANDARD IT ENFORCES.** `BEN-474` says an instrument must reproduce
> its subject's conditions; this is the neighbouring claim — an instrument must survive the questions it asks.
> Ask of your own check: *did it run, does it need to run, and does it measure the quantity that binds?*

## What actually saved it

Nothing clever: **reading the output**. The `SyntaxError` was printed in full both times, immediately above the
false `RC=0`. The verification step — three independent read-backs of the watch (state file, `watch-list`, live
cron tick) — is what turned a silent failure into a visible one, and it is the only reason this is a finding
rather than a 3 A100-h job finishing into silence during an account migration.

> **THE READ-BACK IS THE CONTROL. THE ARMING IS JUST AN ATTEMPT.** Report what you read, never that you armed.

## Checks to steal

1. **Never pipe a command whose exit status you will read.** Redirect, then read the file.
2. **Before invoking an unfamiliar tool, grep for a working invocation of it** — cron, launchers, prior jobs.
   The environment usually has one, with the interpreter and flags already correct.
3. **Ask "is this needed?" separately from "is this safe?"** A careful procedure makes a needless act safe, not
   unnecessary.
4. **Check the units of every threshold.** `df` is not a quota; `Elapsed` is not a duration for a running job;
   wall-hours are not node-hours on a shared partition.
5. **Verify by reading the artifact back, and report the read, not the write.**
