# FINDING — `whose_row.py` false-passed a foreign row when conflict markers NEST (BEN-162)

**Filed** 2026-08-12 by Session D (verifier), lane-d worktree. Adversarial pass on `517e240`,
commissioned by Session A, which named the areas it doubted and asked me to look past them.
Every result below was reproduced in a temp dir; **nothing in any tracked file was modified to
establish it.**

**Status 2026-08-12:** all six defects below are FIXED in `whose_row.py` (the nested case now carries
a named regression check in the self-test; the four vacuous-pass shapes return 2). This file is the
record of what the defects were and why they survived, not an open item.

## The defect

`conflicted_line_numbers()` tracked conflict scope with a **boolean**, not a depth counter, so the
first `>>>>>>>` closed the region while an outer block was still open. Every row between an inner
close and the outer close escaped attribution.

Demonstrated end to end — same file, same command, differing only by one nested inner block:

    with nesting     OK :: every contested row is yours      rc=0   <- | BEN-131 | (owner C — PET) contested and unreported
    without nesting  REFUSED                                 rc=1   <- correctly routes BEN-131 to C

**A gate whose entire purpose is "no lane merges another lane's row" passed lane D on lane C's row.**

**Fix, one line, verified in a copy:** replace the flag with a depth counter — `depth += 1` on start,
emit while `depth`, `depth = max(0, depth - 1)` on end. Measured after: the nested case yields
`['BEN-131','BEN-171','BEN-172']` (the escapee is caught), the self-test's own sample is unchanged at
`['BEN-131']`, and both malformed forms — end-before-start, and missing-end-marker — behave exactly
as before.

## Why it survived — the transferable point

Session A had already learned *the battery is the form set, not one variant* from the
`lane.lower() in owner.lower()` substring false pass, and had rebuilt `lane_matches`' test into a
full lane × owner cross-product with both historical failures pinned by name.

**The scoping function two definitions above it kept its ONE variant** — a single well-formed
conflict — and that is where the next false pass was.

**A remedy applied to the site of the last failure is not applied to the class.** Third instance of
that shape in two days, after BEN-084(B) (literal command in the header, re-derived wrongly anyway)
and BEN-094(i) (pathspec commit, absorbed anyway). BEN-163 is the fourth and the first where the
class crosses artifacts.

## Four more, all vacuous-pass shapes — the `pdf_text` family found at `40ce767`

- **(a)** `--lane D` naming an **absent** file printed `OK :: every contested row is yours` and exited
  **0**. Zero rows examined, and the message asserts the opposite.
- **(b)** An empty `--diff-filter=U` printed *"no unmerged files; nothing to attribute"* and exited
  **0 even with `--lane` set** — so running the gate **after** `git add`, which clears the unmerged
  set, passes it. BEN-068's exact shape: a predicate read at a point where the state it tests has
  already been changed.
- **(c)** A `git` failure reached that same `return 0` through the `except` branch, so the tool could
  not distinguish *no conflicts* from *could not look*.
- **(d)** `ben_blocks()`'s `text[: text.find(marker)] or text[:8000]` — when the marker is **absent**
  `find()` returns `-1`, so the slice is `text[:-1]`, the whole file, and **the `or` fallback is dead
  code**. Measured: correct head 2280 chars / 5 blocks, degraded head 38179 chars / 5 blocks.
  **Latent, not occupied** — no finding row currently contains a block-shaped table row.

## Three stated limits, checked for honesty rather than taken

| stated limit | verdict |
|---|---|
| `VALIDATION_LEDGER.md` cannot be attributed | **honest** — `NO ATTRIBUTABLE ROWS`, rc=1 |
| prose conflicts are unattributable | **honest** — verified on a rows-free doc, rc=1 |
| attributes by id block, not authorship | **true, and its cited example does not demonstrate it** |

BEN-089 is offered as the instance of the third. Measured: the tool reports it `UNOWNED` and REFUSES,
because 89 is below every block — that is the **safe** case. The real failure mode is a lane filing
**inside** another lane's range, where the tool confidently names the wrong owner, and no current row
demonstrates it. **The claim is right and the evidence attached to it is wrong** — BEN-096's shape, on
a limits section written to prevent overstatement.

## Rules

1. **When a test is rebuilt because a function false-passed, rebuild the tests of every function on
   the same path.** The defect is the one-variant battery, not the function that happened to hold it.
2. **A gate that examines zero items must never print a pass.** `OK :: every contested row is yours`
   over an empty set is the vacuous-stage shape, and it appeared in two consecutive gates this
   campaign shipped.
3. **A limits section's examples need the same verification as its claims**, or it teaches the wrong
   failure mode.
