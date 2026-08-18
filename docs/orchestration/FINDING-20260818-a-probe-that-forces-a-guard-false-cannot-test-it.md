# FINDING 2026-08-18 — a probe that forces a guard false cannot test that guard

**BEN-452.** Lane D (verifier), read-only, at the mediator's request after the Codex session found a
defect that **five lanes missed, two of them by mutation review.**

## The shape

> A harness is built to make the code under test **reachable**. The same construction can make a
> **guard** under test **unreachable** — always taking one branch, never the other. Every assertion
> the harness makes then lives **downstream of that guard**, and an assertion downstream of a guard
> cannot test the guard.

**It is not an unexercised guard** (`BEN-258` amendment 1's third category). The guard runs on every
probe invocation. **It runs in one direction only, and the direction is chosen by the harness rather
than by the case.**

## The instance

The `M(ii)` launcher probe stubs `python3` and `sbatch`, runs the real launcher under real bash, and
asserts on the **observed argv**. That is the right instrument for the question it was built for —
*"does `--estimator-seed` receive an integer on every branch"* — and it found real defects.

But the launchers guard their work with a **resume check**: if the product already exists, skip. In
the probe's temporary environment **no product exists**, so the resume guard is false on every run
and the command branch is always taken.

**The probe's assertion requires the command to have run.** Argv only exists on the branch where the
guard is false. So the harness cannot observe the skip branch **even in principle** — and the skip
branch is exactly where the defect lives: all 50 offsets write to the same fixed-literal paths, those
paths are already complete on NERSC, so a real launch resume-skips, exits 0 without running Python,
and returns 50 copies of the published archive. **Fast, green, and the archive.**

**The single regime where the bug cannot appear is the regime the probe constructs.**

## Why mutation review did not catch it either — and this is the part worth having

Two lanes mutation-reviewed this instrument, and mutation review is the right tool. It failed here
for a reason that is structural rather than careless:

> **Mutation tests the code the harness reaches. It cannot test the code the harness has made
> unreachable, because mutating unreachable code changes no observable.**

Delete the resume guard entirely and every probe assertion still passes. Invert it and they still
pass. **A mutation in a branch the harness never enters is indistinguishable from no mutation** — so
the tool that exists to prove a test can fail is silent exactly where the test was never able to
succeed.

## The check

Two questions, asked of any harness, and both cheap:

1. **What does my setup make FALSE?** Enumerate the conditions the fixture establishes — empty temp
   dir, absent products, stubbed binaries, fresh environment — and for each, name the branch it
   forecloses. **Those branches are untested by construction, whatever the coverage says.**
2. **Is my assertion downstream of a guard?** If the observable only exists on one side of a branch,
   the assertion is conditioned on that side. **Assert on something that exists on both** — here, a
   probe would need to observe *"the launcher exited 0 having run nothing"* as a distinct outcome
   from *"the launcher ran the command"*, which is the same
   [`BEN-450`](FINDING-20260818-detection-without-propagation.md) distinction between an absent
   observation and an observed absence.

## Family

- `BEN-258` amendment 1 — a **live guard that has never fired**. There, nothing exercised it. **Here
  the harness exercises it every time, in the one direction that hides the defect.**
- `BEN-450` — detection without propagation. Its remedy applies: make *"ran nothing"* observable
  rather than inferring it from the absence of an observation.
- `BEN-255` — a check evaluated on the wrong population. Here: on the wrong **branch**.
- **`BEN-452`** — the harness selects the branch, so the guard is tested in one direction and
  mutation cannot reach the other.
