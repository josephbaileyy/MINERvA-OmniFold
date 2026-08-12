# BEN-117 — `whose_row.py --lane ""` printed `OTHER` for every foreign row and exited 0

Long form of `FINDINGS.md`'s `BEN-117` row. Found 2026-08-12 by Lane B, on the orchestrator's
invitation that finding another hole in the gate would be worth more than using it. Two defects; the
first is a false pass, the second fails safe.

## Defect 1 — the false pass

Measured, in a throwaway file with one lane-C row inside conflict markers:

```
--lane B    -> exit 1   REFUSED                   (correct)
--lane ""   -> exit 0   "attribution complete"    <-- foreign row printed as OTHER, then passed
--lane "  " -> exit 1                             (already safe)
```

`--lane ""` is what `--lane "$LANE"` expands to when `LANE` is unset — which is how any wrapper, hook
or `Makefile` will invoke this. The falsy `args.lane` short-circuited **both** guards:

```python
if args.lane and not mine:                       # accumulator never runs
    foreign.append(...)
...
if args.lane and (foreign or unattributable):    # final check never runs
    return 1
```

so the tool printed `OTHER    probe.md:3  BEN-131   owner=C — PET` and returned success.

### The transferable part: the predicate was already correct

`lane_matches("C — PET", "")` returns `False`, and the self-test *already asserted exactly that*
(`case("empty lane never matches", lane_matches("C — PET", ""), False)`). The gate passed anyway,
because that correct answer was **never consulted**.

> **A unit check on a predicate cannot see a short-circuit that skips the predicate.** A gate's exit
> code must be tested *as an exit code*, from a subprocess, against a real conflicted file.

This is the orchestrator's own substring lesson (`lane.lower() in owner.lower()` matching lane `C`
against `B — uncertainty construction` via *"constru**c**tion"*) one level along. That bug was caught
by an end-to-end merge and missed by a unit self-test whose single negative control happened not to
fire. **The fix for it shipped with this hole still in it, one function away** — so *"the battery is
the form set, not one variant"* has to cover the **call path**, not only the input space. Enumerating
more inputs would never have found this; only running the process would.

### Fix and power test

Present-and-empty `--lane` now exits **2** (fatal). Omitting `--lane` stays legal — that is the
documented attribution-only mode, which reports rather than gates. The distinction is the point: the
empty case is a caller who **asked to be gated** and was told it passed.

Five end-to-end exit-code cases added to the self-test, run as subprocesses. Mutation M2 (replace the
guard's condition with `if False:`) fails exactly two of them:

```
FAIL EXIT: --lane '' is FATAL (2), was a silent 0   (got 0)
FAIL EXIT: --lane '   ' is FATAL (2)                (got 1)
```

Both directions measured, and the mutation also **measures that whitespace was already safe** — `"   "`
returned 1 before the fix, so only the truly empty string was the hole. A test that had lumped them
together would have overstated the defect.

## Defect 2 — the `200+` block was silently dropped, and it failed safe

`BLOCK_ROW` required a closed `` `NNN-NNN` `` range, so the header row
`| repo infrastructure (ledgers, read path, dispatch machinery) | `200+` |` never parsed.
`BEN-200`, `201`, `202` and `204` already exist, so live rows attributed as `<unowned>` and the gate
told the operator to *"route to its author: `<unowned>`"* — unactionable.

It **refused** rather than passed, which is why nobody had hit it. That is the argument for auditing
the conservative direction as well: **a check that refuses for the wrong reason teaches operators to
override it**, and an override habit is how the next false pass gets waved through.

Fixed with an open-ended sentinel (`OPEN_BLOCK_HI`). Verified end to end: a `BEN-200` conflict now
reports `owner=repo infrastructure (ledgers, read path, dispatch machinery)` and still exits 1 for
lane B, which is correct — B does not own it, but the routing target is now actionable.

### The fix invalidated an existing negative control, and that is worth recording

`case("absurdly high id is UNOWNED", owner_of_ben(999999, blocks), None)` became **false** — correctly,
because an open-ended block owns everything above its floor. The case was **replaced, not deleted**:
*"there exists an unowned id"* is still the real invariant, and dropping it entirely would let the
attributor answer everything again, which is the failure mode the negative control existed to catch.
The replacement asserts the new truth (an open block *does* own an arbitrary high id) **and** keeps a
genuine unowned probe (an id below the lowest block).

A **presence** check was also added, counting documented header block rows against parsed blocks:

```python
case("every documented block row is parsed (none silently dropped)", len(blocks), documented)
```

Every prior check asked whether ids **resolve**; none asked whether every block **arrived**. Absence
of a whole block is invisible to a suite that only probes presence — which is exactly why this sat
undetected while 42 checks passed. Mutation M1 (revert `BLOCK_ROW` to closed-range-only) fails it:
`got 5 want 6`.

42 checks → 55, all passing.

## A measurement error of my own, in the same session

Verifying that the other lane's vacuous-pass guard survived my merge, I ran
`python3 whose_row.py --conflicts --lane B | tail -3; echo $?` and read **0** — concluding briefly
that the merge had broken their fix. That `0` was `tail`'s exit code, not Python's. Re-run without the
pipe: **exit 2**, guard intact.

BEN-088's shape, in my own measurement, minutes after writing about call paths: **a pipeline's `$?` is
the last stage's status, so any exit code read through `| tail`/`| head`/`| grep` is the filter's and
not the program's.** Redirect to a file and read the file — which is the same rule BEN-026 gives for
diagnostic streams, for a different reason.

## Cross-references

- Instrument defects in the same file, found by other lanes:
  `FINDING-20260812-orchestrator-instrument-defects.md`
- The vacuous-pass fix (a gate over zero files is not a pass) landed independently at `b710b48`; this
  is the **third** hole found in `whose_row.py` on the day it was written, by three different lanes.
- Commit: `7e31dda`, merged to `main` at `c4501cd`.
