# FINDING — the gate learned exit 2 and the document teaching its contract did not (BEN-163)

**Filed** 2026-08-12 by Session D (verifier), lane-d worktree. Adversarial pass on `6475369` /
`6046180` at Session A's request to attack the denominator fix. The script's behaviour was re-measured
from a subprocess; **nothing was modified to establish it.**

**Status 2026-08-12:** FIXED. `CONVENTION-lane-worktrees.md` now cites `merge_guard.sh` **by path**,
quotes no command, states all exit codes, and prints no check count of its own.

## The fix under attack was sound and I could not break it

Measured against `whose_row.py` as shipped:

    my nested false pass (BEN-162)          now REFUSES                       rc=1
    absent named file                       now REFUSES                       rc=1
    B's `--lane ""` short-circuit           FATAL                             rc=2
    gate mode over zero rows                CANNOT CHECK                      rc=2   (query mode stays 0)
    self-test                               58 checks, PASS                   rc=0

**Revision anchor, per BEN-091, and it demonstrates the finding.** The `58` above is a measurement of
`whose_row.py` as of `6046180` on 2026-08-12, not a property of the suite. Re-measured a few hours
later in the same session it was **70**. That is the drift this finding is about, arriving inside the
finding — which is why the convention now cites the script by path and states no count, and why this
number is dated rather than asserted.

**The denominator is honest in both directions I could test it.** An absent file reports
`examined 0 file(s), 0 attributable row(s)` rather than counting the attempt, and `--conflicts` over a
21-row file reports the **scoped** `1 attributable row`, not the total.

## The defect is one layer out

`CONVENTION-lane-worktrees.md:50` still read `# exit 1 if a contested row is not yours` and `:51` still
read `42 checks`. The script returns **0 / 1 / 2** from six sites and runs **58** checks.

That document is the only place an operator learns the contract, and BEN-117's own text says the
empty-lane case *"is how any wrapper or hook will invoke this"* — **so the reader most likely to write
that wrapper was reading the line that omitted exit 2.** A wrapper written faithfully from the
convention tests `[ $? -eq 1 ]`, and **exit 2 — the code introduced precisely because a misconfigured
caller had been told it passed — reads as success.**

The hole was not closed. It **moved from the script into the prose describing the script**, which is
strictly worse: the script has a 58-check self-test and the prose has none.

## Fourth instance of my own rule, and the first where the class crosses artifacts

*A remedy applied to the site of the last failure is not applied to the class:*

| instance | repaired | not repaired |
|---|---|---|
| BEN-162 | `lane_matches` | `conflicted_line_numbers`, two definitions above it |
| BEN-117 | the predicate | the call path that short-circuits past it |
| **BEN-163** | **the code** | **its published contract** |

Each repair was correct, complete, and bounded to the exact object that had failed.

It also lands on **BEN-099** — a claim about another artifact, never checked — and on **BEN-091**'s
shelf-life rule: `42 checks` is a bare count with no revision anchor, and it drifted to 58 within hours
of being written.

## Repair, and it is the cheap kind

State all codes on the invocation line, and **derive the check count or drop it** — a number in prose
beside a self-test that prints its own total is a second copy that can only go stale.

**Better than either: make the convention's snippet the thing that runs.** BEN-084(B) is the precedent
and it failed as prose — a literal command in a header was re-derived wrongly anyway — so the stronger
form is a committed `merge_guard.sh` the convention cites **by path**, which cannot drift from its own
exit codes because it *is* their only interpreter. Same remedy and same reason as
`waker_fired_but_unread.sh` (BEN-097). This is what shipped.

## Rules

1. **When you change a program's exit contract, grep for every document that states it, in the same
   commit.** The contract lives in two places the moment it is documented, and only one of them has a
   test.
2. **A gate's exit codes are an API.** Adding a code is a breaking change for every caller written
   against the old set — and the callers here are prose instructions to agents.
3. **Do not restate a self-test's check count in prose.** The suite prints it; a copy is drift with no
   anchor.
