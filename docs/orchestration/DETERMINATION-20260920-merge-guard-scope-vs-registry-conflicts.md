# DETERMINATION 2026-09-20 — the merge guard refused, the refusal stands, and no override was sought

**CITABLE FOR:** what `merge_guard.sh` declares its scope to be, what it did on the 2026-09-20 merge
attempt, and the determination that the refusal is terminal.
**NOT CITABLE FOR:** any verdict on whether the guard is correct here. That is `OI-189`, and it
belongs to the guard's owner, not to the lane it refused.

## 1. What was attempted

Merging `lane/z-criteria-independent-assessment-20260910` (`935b75585a7b9cc39cd52d4aa001df4edbea875f`,
69 commits ahead) into `main`, to bring the independent clause-(c) verification onto the single
discovery route. See [`DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md`](DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md).

Two files conflicted, both single-hunk and both additive: `docs/orchestration/CATALOG.md` and
`docs/orchestration/MANIFEST-overrides.tsv`.

## 2. What the guard did

```
docs/orchestration/CATALOG.md: NO ATTRIBUTABLE ROWS -- resolve by hand and route to the author.
docs/orchestration/MANIFEST-overrides.tsv: NO ATTRIBUTABLE ROWS -- ...
REFUSED [examined 2 file(s), 0 attributable row(s)] :: you are not the author of every contested row.
```

Invoked as `bash docs/orchestration/merge_guard.sh z-criteria-independent-assessment-20260910`.
Its self-test passed first (283 checks, `SELF-TEST :: PASS`; `LEDGER-IDS :: PASS`).

## 3. The declared scope, read out rather than inferred

`merge_guard.sh:2` — *"Merge gate for a lane worktree: **refuse a merge that resolves another lane's
ledger row.**"*

`CONVENTION-lane-worktrees.md`, the section headed *"What the attributor cannot do, stated so it does
not overstate its reach"*:

> - **`VALIDATION_LEDGER.md` has no per-row id scheme and cannot be attributed.** … Conflicts there
>   print `NO ATTRIBUTABLE ROWS` and are refused, **by design**.
> - **It sees rows, not prose.** A conflict in a header paragraph is unattributable and reported as such.

**So the behaviour observed is declared and deliberate, not a bug.** `CATALOG.md` is prose and
`MANIFEST-overrides.tsv` is a path registry; neither carries a per-row id, so neither can ever be
attributed, and the declared response to unattributable is refusal.

## 4. THE DETERMINATION

**The refusal stands. No override was sought and none exists to seek.**

[`RULING-20260908-joseph-a-merge-guard-refusal-is-terminal.md`](RULING-20260908-joseph-a-merge-guard-refusal-is-terminal.md):

> **Yes, terminal. No authorizer converts a refusal into a pass.** … A guard's exit is a **fact about
> the tree**. An authorization is a **permission about an act**. Permissions govern acts, not
> measurements. … it does not weaken when the authorizer is senior, correct, or in a hurry.

That ruling names exactly two legal exits, both ending in a green run: **(1)** remove the cause and
re-run, or **(2)** if the gate is genuinely over-strict, **fix the gate** — reviewable and dated.
Exit (1) is unavailable: the cause is that these two files have no id scheme, which this lane cannot
remove. **So the route is exit (2), and it is filed as `OI-189` for the guard's owner.**

Joseph was asked for nothing here, and declined to be asked. Recording that, because the previous
instance of this shape — an integration lane overriding a refusal on a coordinating session's
authorization — is the occasion the 2026-09-08 ruling was written for.

## 5. ⚠ THE TENSION `OI-189` MUST RULE ON, stated fairly in both directions

**For the refusal being correct:** unattributable-means-refuse is declared, and the guard cannot know
that a prose conflict is harmless. Fail-closed on an unknown is the safe direction, and this
repository has a measured record of the opposite failing.

**Against:** the rule's protected object is a **ledger row**, and its measured basis is six
absorptions in `FINDINGS.md` (×3), `VALIDATION_LEDGER.md` (×2) and `OPEN_ITEMS.md` (×1).
**None of those three files is in this merge at all.** The protected population is empty while the
refusal fires — and the same convention says at `:99` that *"an unreachable pass is the defect this
state exists to repair, not a safe default."* Every merge of a long-lived docs lane conflicts in
`CATALOG.md` and `MANIFEST-overrides.tsv`, so this is not a one-off.

**This lane does not rule on that,** and deliberately: it is the party the guard refused, so its
reading of the guard's reach is the reading with an interest. Same disqualification the clause-(c)
assessor applied to itself.

## 6. State, so the next attempt starts from facts

- **Merge aborted clean.** No `MERGE_HEAD`, no conflict markers, tree clean at the time of writing.
- **Resolutions are scripted and preserved**, union and **order-preserving** — `+60/−0` on
  `MANIFEST-overrides.tsv`, `+1324/−0` on `CATALOG.md`, no reordering. (A first attempt re-sorted the
  overrides file; `origin/main`'s copy is **not** sorted, so that would have churned 283 rows. Do not
  sort it.)
- **The merge content was scanned before the abort and is clean:** 69 files, 14,008 added lines; no
  credentials, no `[M60]`, no POT value; 11 cross-section-scale literals, all covariance norms; the
  one `122 of 160 throws` hit is already public in `docs/OPEN_ITEMS.md`.
- **It lands after the audit, on a real pass or a repaired guard.** Not on anyone's say-so.

**Co-Authored-By: Claude Opus 5 (1M context)**
