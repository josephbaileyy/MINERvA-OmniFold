# CONVENTION — how to verify a check is deployed and checking what you think

**Status: method, not a finding.** Written 2026-08-14 by lane A at lane D's request, so the probe form can be
cited rather than re-derived. The failures that motivated it are `BEN-173`, `BEN-180`, `BEN-183`, `BEN-185`,
`BEN-186`, `BEN-222`, `BEN-224`, `BEN-225` — eight rows in three days, across three lanes.

**Lane D's framing of what that count means, and it is better than the first draft's:** it is not that the
checking was bad. Most of these checks are well written and several state their own limits in their
docstrings. **Nobody had been asking what each one could not detect.**

**The one-line generalisation, which is shared and belongs to nobody in particular:**

> **A green count is a statement about what ran, not about what was checked.**
> `pre-commit: 6 checks passed` and `39 passed, 1 skipped` fail the reader in exactly the same way.

**And the companion, which governs the freshness of every measurement below** — placed here rather than inside
the taxonomy on lane D's suggestion, because it is a premise for all five causes rather than a sixth one:

> **A fact about a concurrently-written repository is a measurement with a timestamp, and publishing it without
> one is the failure.**

Measured at three timescales in three media, all on 2026-08-13/14: **15 hours** in a document (`BEN-219`, a
ledger line exact when written and 73 lines off when read), **hours** in a message (`BEN-222`, *"the hook
doesn't run the gate"* — true when written, silently false), **7 seconds** in a commit message (`BEN-225`, a
grep verified pre-rebase and false in the commit that published it). Four lanes write this repository at once;
none of those three was carelessness.

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
| A check fed input built by the code it re-derives with — vacuous, and invisible unless you read the caller | `BEN-186` | derive the input independently of the code under test |
| A claim verified pre-rebase and published post-rebase — true when measured, false in the commit carrying it | `BEN-225` | re-run after `pull --rebase`; keep absence claims in files, not messages |

**This table is an index, not a replacement.** Each row carries its own evidence and its own remedy; this file
exists so the shared generalisation is written once and the probe is citable.

## WHEN THE PROBE IS MANDATORY

**Read this before the section below it.** Lane D's caution, adopted: *a limits section is the first thing a
future agent quotes to skip the probe.* So the exemptions are bounded by a rule that is not optional.

**THE PROPERTY, which is the rule:**

> **The probe is REQUIRED whenever the green will be relied on by someone who will not re-run it.**

Stated as a property rather than a list of destinations, on lane D's caution: **an enumeration goes stale
silently the moment a seventh case appears** (`BEN-187`'s shape), and a rule that needs maintaining is one that
will eventually be quoted around. The property needs no maintenance — ask who is going to trust this green
without reproducing it, and if the answer is anyone, probe.

**Non-exhaustive examples, as recognition aids and NOT as the definition:** a gate verdict, a receipt,
`VALIDATION_LEDGER.md`, `CLAIMS.md`, a commit message another lane will act on, anything sent to a collaborator
or advisor. If a case is not on this list, the property still decides it.

The reasoning is `CONVENTION-receipt-ingredients.md`'s, one level up: **a verdict-only receipt is
unfalsifiable, and an unprobed green is a verdict without ingredients.** Citing it converts "the check did not
object" into "the property holds", and those differ by exactly the four causes tabulated above.

Corollary, from `BEN-225`: **if the citation is a count or an absence, re-run the check after
`git pull --rebase` and before `git push`.** The rebase moves the base under a finished commit and copies its
message verbatim, so a claim verified pre-rebase can be false in the commit that publishes it — measured at
7 seconds.

## When the probe is not worth it

Stated because a method with no stated limits gets applied where it costs more than it returns:

- **A check whose violation cannot be constructed cheaply** — if staging the violation requires a cluster run
  or a 9 GB artifact, the probe is not cheap and a narrower unit test on the predicate is the better buy.
- **A read-only reporter** with no pass/fail semantics has nothing to reject; verify it by its output on a
  known input instead.
- **A check you just wrote and unit-tested with a negative control** is already covered for *behaviour*. The
  probe adds *deployment* evidence, which is the half a local run cannot give you when `hooksPath` is
  absolute.

## A note on this file's own registration, because it is the same failure one level out

**`MANIFEST.tsv` is GENERATED** (`generate_manifest.py`) and `MANIFEST-overrides.tsv` is its hand-maintained
input. Lane A first hand-typed a row into the generated file — wrong, and the next regeneration proved it: the
generator's default classified this brand-new convention as **`ARCHIVAL` / `terminal` / immutable**, on the day
it was written, in the file `CLAUDE.md` names as *"the authority on what is LIVE vs ARCHIVAL"*. A `LIVE open`
override now exists, matching its two sibling conventions.

**The regenerated manifest was then NOT committed, deliberately.** Running the generator in lane A's worktree
dropped 30 rows — every `__pycache__`, `.DS_Store` and `.pytest_cache` entry that exists in the main checkout
but not here — because the generator inventories ignored artifacts too. **Committing that would have published
lane A's worktree as a description of the repository, which is `BEN-183`.** So the override lands and the
regeneration is left to whoever runs it in the main checkout. Until then this file reads `ARCHIVAL` in the
manifest and `LIVE` in `CATALOG.md`, and **the manifest is the one that is wrong.**

## Related

`BEN-222` (a committed hook is not an installed hook), `BEN-224` (the file and the payload come from different
trees), `BEN-218` (one `.git/config` across six worktrees), `CONVENTION-lane-worktrees.md`,
`CONVENTION-receipt-ingredients.md` (the sibling heuristic: ship the ingredients so the numbers can contradict
each other).
