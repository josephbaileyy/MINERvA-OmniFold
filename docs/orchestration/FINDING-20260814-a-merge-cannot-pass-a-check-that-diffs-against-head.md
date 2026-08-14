# BEN-242 — a merge commit cannot pass a check that diffs against `HEAD`

**Filed:** 2026-08-14 by lane B (Gate 6). **Instrument:** `docs/orchestration/whose_row.py
--check-oi-ids`, the 6th pre-commit check, landed 2026-08-14 by lane A (`e4db2e2`).
**Status:** worked around here; **the fix is one line and is not mine to make** — the check is lane A's.

## What happened

Lane B committed `OI-80` (inside its declared block `80-89`); the check passed and the commit landed:

```
pre-commit: 6 checks passed
```

The very next step was mandatory: `git fetch && git merge origin/main`, because `CLAUDE.md`'s first
hard rule is that other sessions run this repo concurrently. `origin/main` had meanwhile gained
`OI-122` — the mediator's row, already pushed. Resolving the add/add conflict and committing the merge
gave:

```
PRE-COMMIT FAIL: OPEN_ITEMS OI ids
  [73 data rows, 73 OI ids, 2 duplicated, 2 waived]
  [committer 'Lane B (Gate 6)' -> block 80-89; 1 id(s) added vs HEAD: [122]]
  FAIL OI-122 IS OUTSIDE 'Lane B (Gate 6)''s block (80-89)
OI-IDS :: FAIL
```

**`OI-122` is not mine. I did not write it, and it was already pushed.** The check reported it as an id
I added because that is literally true of the diff it computes: `HEAD` at that moment was lane B's
pre-merge commit, and relative to *that* commit the merge adds `OI-122`.

## Why this is a defect in the instrument and not a lapse by the committer

The dispatcher states its own admitting rule at `.githooks/pre-commit:11`, in lane D's formulation
under `OI-64`:

> *a check belongs here iff a committer who did nothing wrong can always make it pass.*

A merge commit importing another lane's id has exactly three exits, and **all three are forbidden**:

| Exit | Why it is unavailable |
|---|---|
| Renumber `OI-122` into `80-89` | It is another lane's row and already pushed. `CONVENTION-lane-worktrees.md` — only a row's author reshapes it. Renumbering a pushed id is `BEN-223`'s harm, not its remedy. |
| `git commit --no-verify` | Prohibited by this session's standing rules, and the dispatcher's header says in terms not to `--no-verify` past a failing check. |
| Do not merge | Violates `CLAUDE.md`'s *"a result does not exist until its commit lands"* and the mediator's explicit instruction to fast-forward before the next commit. |

So the check is not merely inconvenient on a merge — **it is unpassable**, which is the precise
condition its own admitting rule was written to exclude. It is `BEN-199`'s family (a rule with no
reachable passing state) reached by a different route: `BEN-199`'s freshness check could never pass at
all, this one can never pass *on a merge*.

## The mechanism

The check computes newly-added ids as a diff against `HEAD`:

```
[committer 'Lane B (Gate 6)' -> block 80-89; 1 id(s) added vs HEAD: [122]]
```

For an ordinary commit, `HEAD` is the right baseline: the ids added relative to it are the ids this
commit authored. **For a merge commit there are two parents, and `HEAD` is only one of them.** Every id
contributed by the second parent is, relative to `HEAD`, "added by this commit" — and attributing it to
the committing identity is wrong by construction, not by accident.

## The fix, stated so whoever owns it can apply it directly

**Diff against the merge base, not `HEAD`.** For a merge, the ids this commit genuinely authors are
those present in the index but in **neither** parent:

- non-merge commit: baseline `HEAD` (unchanged behaviour);
- merge in progress (`MERGE_HEAD` exists, or `git rev-parse --verify -q MERGE_HEAD` succeeds): baseline
  is the union of the ids in `HEAD` and in `MERGE_HEAD`, so an id present in either parent is not new.

That is the same shape as the existing grandfathering of the 65 pre-table ids: an id that already
exists somewhere is not an allocation. Nothing about the block enforcement weakens — a lane that
genuinely allocates an out-of-block id in a merge commit still fails, because that id is in neither
parent.

## What I did instead, and why it is a workaround rather than a fix

**Rebased onto `origin/main` rather than merging it.** After a rebase, `HEAD` contains `origin/main`'s
history, so `OI-122` is part of the baseline and only `OI-80` reads as added — which is correct, and
the check then passes for the right reason rather than being bypassed.

This is acceptable here because **the commit was not yet pushed**, so no history that anyone else could
have fetched was rewritten and no force-push was involved. It does **not** generalise: a lane that has
already pushed cannot rebase, and would be left with no exit at all. That is why this is filed rather
than merely worked around.

One hazard I checked rather than assumed, because `BEN-225` is exactly this shape — a `pull --rebase`
falsifying a claim inside the commit message it carried. My message's claims are measurements
(sqrt-traces, rank counts, a Slurm state with a timestamp) and statements about my own block
allocation, none of which the replay can change. **The claim I had to be careful about was an absence
claim, and it had already been removed** for the reason recorded in `BEN-241`.

## Related

- `BEN-241` — the absence claim in the same commit, and why it broke.
- `BEN-224` / `BEN-222` — the hook file and the checks it runs come from different trees; a changed
  check payload is in force immediately. This check was one day old when it fired.
- `BEN-226` — a hook check has only silence and failure, no advisory channel, so "accept but warn on a
  merge" is not implementable. The baseline fix above is therefore the only available shape.
- `BEN-223` — the `OI-*` collisions this check exists to prevent. Nothing here argues against the
  check; it is a good check with a wrong baseline on one commit shape.
- `OI-62(b)` — the block-table convention is still Joseph's to ratify.
