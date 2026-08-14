# CONVENTION — how to verify a check is deployed and checking what you think

**Status: method, not a finding.** Written 2026-08-14 by lane A at lane D's request, so the probe form can be
cited rather than re-derived. The failures that motivated it are `BEN-173`, `BEN-180`, `BEN-183`, `BEN-185`,
`BEN-222`, `BEN-224` — six rows in three days, across three lanes.

**The one-line generalisation, which is shared and belongs to nobody in particular:**

> **A green count is a statement about what ran, not about what was checked.**
> `pre-commit: 6 checks passed` and `39 passed, 1 skipped` fail the reader in exactly the same way.

---

## THE PROBE: commit something only that check can reject

The only form that verifies deployment *and* behaviour together:

1. **Construct the specific violation** the check exists to catch — not a general breakage.
2. **Stage it and attempt a real commit** (or run the real suite invocation, not a hand-rolled one).
3. **Read the rejection and confirm it names the reason you expected**, not merely that something failed.
4. **Revert, and confirm `HEAD` and the working tree are unchanged.**

Worked example, `BEN-224`. A new `--check-oi-ids` block arm had been added; the commit installing it printed
`pre-commit: 6 checks passed`, **which proved nothing, because the pre-existing 6th check would also pass.**

```
$ printf '| OI-95 | OPEN | probe | b | n | d | 2026-08-14 |\n' >> docs/OPEN_ITEMS.md
$ git add docs/OPEN_ITEMS.md
$ git -c user.name="Lane A (Eavail)" commit -m "PROBE: must be rejected"
PRE-COMMIT FAIL: OPEN_ITEMS OI ids
  [committer 'Lane A (Eavail)' -> block 70-79; 1 id(s) added vs HEAD: [95]]
  FAIL OI-95 IS OUTSIDE 'Lane A (Eavail)''s block (70-79) ...
$ git reset -q HEAD -- docs/OPEN_ITEMS.md && git checkout -- docs/OPEN_ITEMS.md
```

**Why it beats the two cheaper things that look equivalent:**

- **Reading the success count** verifies a hook *line* exists. It cannot see a stale *payload*, because the
  count is unchanged by a payload edit (`BEN-224`). It is the right check for the wrong half.
- **Mutating the code on a copy and confirming the tests notice** catches a weak assertion but **not** a
  stale-payload one, because the mutant and the checker are the same copy — lane D's own form on the Gate-6
  battery, and it is why D asked for this one. The probe catches both.

**Two things the probe must state, or it inherits the defect it is testing for:**

- **WHICH TREE it ran in.** Six worktrees share one `.git/config`; `core.hooksPath` is absolute into the main
  checkout while the dispatcher `cd`s to the committing worktree, so a probe's file, hook and payload can come
  from three different trees (`BEN-224`). `BEN-183` is a lane reporting a worktree measurement as `main`.
- **That the probe actually hit code.** D's first Gate-6 mutation reported `SURVIVED` because the regex matched
  a **docstring**. A probe that misses its target reports the same thing as a probe whose subject is sound.
  Confirm the injected violation is where you think it is before believing a `PASS`.

## Four reasons a check runs and tells you nothing

An index over rows that stay separate **because their remedies differ** — merging them yields one row whose
fix is several unrelated fixes, which is what makes a finding unactionable.

| cause | row | the fix |
|---|---|---|
| A control on one artifact and none on its sibling, in the same function | `BEN-173` | control both sides, or the asymmetry is the detector |
| A band tested only on the side the data is not on | `BEN-180` | test the form set, not the variant that happens to occur |
| The check **did not execute** — correctly skipped, inside a passing suite | `BEN-185` | report coverage **per object**: properties proved on the real object counted separately from those proved on a fixture |
| The check **executed against a stale payload** | `BEN-224` | make the hook bind the payload it invokes; verify by probe, never by count |
| *(announced by lane D as `BEN-186`, not yet filed when this was written)* a check fed input built by the code it re-derives with — vacuous, and invisible unless you read the caller | check the ledger | derive the input independently of the code under test |

**This table is an index, not a replacement.** Each row carries its own evidence and its own remedy; this file
exists so the shared generalisation is written once and the probe is citable.

## When the probe is not worth it

Stated because a method with no stated limits gets applied where it costs more than it returns:

- **A check whose violation cannot be constructed cheaply** — if staging the violation requires a cluster run
  or a 9 GB artifact, the probe is not cheap and a narrower unit test on the predicate is the better buy.
- **A read-only reporter** with no pass/fail semantics has nothing to reject; verify it by its output on a
  known input instead.
- **A check you just wrote and unit-tested with a negative control** is already covered for *behaviour*. The
  probe adds *deployment* evidence, which is the half a local run cannot give you when `hooksPath` is
  absolute.

## Related

`BEN-222` (a committed hook is not an installed hook), `BEN-224` (the file and the payload come from different
trees), `BEN-218` (one `.git/config` across six worktrees), `CONVENTION-lane-worktrees.md`,
`CONVENTION-receipt-ingredients.md` (the sibling heuristic: ship the ingredients so the numbers can contradict
each other).
