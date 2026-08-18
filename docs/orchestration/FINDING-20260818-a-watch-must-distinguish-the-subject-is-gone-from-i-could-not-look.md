# A watch's "nothing there" must distinguish *the subject is gone* from *I could not look*

**Lane E, 2026-08-18. `BEN-475`.** Every completion watch I armed today reduced to this:

```bash
rows=$(ssh -o BatchMode=yes saul.nersc.gov "squeue -h -j $JOB -o '%T|%R'" 2>/dev/null)
n=$(printf '%s' "$rows" | grep -c . || true)
if [ "${n:-0}" -eq 0 ]; then echo "TARGETS TERMINAL: EMPTY -- $JOB has left the queue"; break; fi
```

**An ssh failure produces an empty `rows` exactly as an empty queue does.** When the NERSC sshproxy
certificate expired mid-run, that watch was one poll away from announcing

```
TARGETS TERMINAL: EMPTY -- 57236137 has left the queue
```

about an array that was still running with 38 tasks queued.

## The blast radius, which is what makes it a finding rather than a wart

That message is not informational. It is the **trigger** for three downstream steps:

1. `verify_manifest_precedes_artifacts.py` — would have compared a commit timestamp against whatever
   *partial* artifact mtimes existed and reported a margin in seconds, as though the family were complete.
2. the 50-receipt key sweep — would have counted 3 receipts, not 50, and reported the counts.
3. the single-member training smoke — would have been submitted against a target family that does not exist
   yet.

Each of those would have **succeeded and produced a number.** None would have said "the family is
incomplete", because none of them takes completeness as an input — they take the watch's word for it.

## What hid it: `2>/dev/null`

ssh reported the failure properly. It wrote `Permission denied (publickey,password,keyboard-interactive,
hostbased)` to stderr and exited **255**. Both were discarded — stderr by the redirect, the status by never
being read — and only the empty stdout survived to be interpreted.

> **Suppressing a channel converts a loud failure into a quiet one that looks like a result.**

The redirect was there for a good reason (ssh warnings are noisy in a poll loop) and it silently widened the
watch's "empty" case from one state to two.

## The repair: three outcomes, never two

```
EMPTY        ssh exited 0 AND no rows        -> the guard will pass; proceed
BLOCKED      rows exist, all permanently stuck -> a DECISION, not a wait
UNREACHABLE  ssh exited non-zero, 3x         -> state is UNKNOWN, NOT terminal; needs a human
```

with the exit status captured **before** anything interprets the output, stderr kept rather than discarded,
and three consecutive failures required so a single dropped connection does not stop a watch that should keep
waiting.

`UNREACHABLE` names the remedy in its own message — a NERSC certificate renewal needs MFA, so no agent can do
it — because a terminal state that requires a human and does not say so gets retried forever.

**Validated in production by the failure it was written for, minutes after being written:**

```
WATCH UNREACHABLE: ssh exited 255 on three consecutive polls -- THIS IS NOT AN EMPTY QUEUE.
The array's state is UNKNOWN, not terminal.
```

## Two related mistakes made in the same hour, both worth recording

**1. I diagnosed the 255 wrongly and wrote the wrong cause down.** I attributed it to `grep -l PATTERN
$(find ...)` running with no file operands on an empty `find` — a real hazard, and not this one — and put it
in a comment block as established before testing whether ssh worked at all. **One command separated the
plausible mechanism from the trivial explanation, and I built the mechanism first.** Corrected in place with
the real cause beside it rather than silently replaced.

**2. The `UNREACHABLE` report printed an empty stderr section.** `tail -2 "$err"` produced nothing — with
connection multiplexing the diagnostic can land on the master's stderr rather than the child's. So the report
says "Last stderr:" followed by a blank, which reads as *"there was no error message"* when it means *"we did
not capture one."* Same shape as the finding itself, one level down, and now stated explicitly instead of
shown as a blank.

## The check to steal

For any watch, poll, or health check:

- **Read the exit status before interpreting the output.** An empty result and a failed call are different
  events and only one of them is about the subject.
- **Never `2>/dev/null` a channel whose failure you would act on.** Keep it, filter it, or capture it to a
  file — but do not discard the only evidence that the instrument itself failed.
- **Enumerate three outcomes: done, stuck, and could-not-look.** Two-outcome watches assign
  "could-not-look" to whichever of the other two shares its symptom, and for a queue poll that is always
  "done".
- **When an outcome needs a human, say so in the outcome.** Otherwise a retry loop treats a credential
  expiry as transient forever.
- **Ask what your watch's success message TRIGGERS.** If it starts irreversible or expensive work, its false
  positives are that work's false positives.

**Cross-references.** `BEN-472` (a watch armed on a guard's present-tense condition can wait forever — same
family, the other direction: there the condition could never be met, here it was met for the wrong reason),
`BEN-474` (an instrument must reproduce its subject's conditions; an unreachable subject makes the instrument
report on itself), `BEN-028` (a quiet log does not mean a dead job), `BEN-415`/`BEN-417` (a verdict that does
not name its population).
