# FINDING 2026-08-14 — the hook file and the checks it runs come from different trees

**`BEN-224`.** Lane A. Generalises past this hook to **every check this repo adds while four worktrees are
live**, which is why it is a row rather than a note on `BEN-222`.

## The split

`.githooks/pre-commit` is a dispatcher. Two of its properties interact:

1. **`core.hooksPath` is an absolute path into the main checkout** (`BEN-222`), shared via one `.git/config`
   across all six worktrees. So the **hook file** git executes is always the main checkout's *working-tree*
   copy, at whatever revision that tree sits at.
2. **The dispatcher's second line is `cd "$(git rev-parse --show-toplevel)"`**, which resolves to the
   **committing worktree**. Every check it invokes is a *relative* path — `python3
   docs/orchestration/whose_row.py`. So the **check payload** is the committing worktree's copy.

**The file comes from one tree and the code it runs comes from another.** Stated as a rule:

| you change | in force when |
|---|---|
| a hook **line** (adding/removing a check, the success message) | only after the **main checkout's** working tree updates |
| a check's **payload** (the script the line invokes) | **immediately**, in your own worktree |

## How it was measured

Lane A extended `whose_row.py --check-oi-ids` with a block arm (`OI-62(b)`) and committed. The commit printed
`pre-commit: 6 checks passed` — and **that number proves nothing**, because the pre-existing 6th check would
also have passed. So a deployment probe was staged instead: an `OI-95` row, outside lane A's `70-79` block.

```
PRE-COMMIT FAIL: OPEN_ITEMS OI ids
  [committer 'Lane A (Eavail)' -> block 70-79; 1 id(s) added vs HEAD: [95]]
  FAIL OI-95 IS OUTSIDE 'Lane A (Eavail)''s block (70-79) ...
```

Simultaneously: `grep -c "_block_for\|OI_BLOCK_ROW" <main checkout>/docs/orchestration/whose_row.py` → **0**.

**The main checkout did not contain the block arm, and the block arm ran.** That is the split, demonstrated
rather than reasoned about. Probe reverted; `HEAD` unchanged.

## Why this matters beyond one hook

- **A changed payload is live before review.** A lane can alter what every check *does* — in its own
  worktree — and see it take effect on its very next commit, with no pull, no coordination, and nothing in the
  success line indicating a different check ran. `BEN-222` established that a *new* check is inert until
  someone pulls; the mirror is more surprising and less safe.
- **The same commit is validated differently depending on who commits it.** Until B, C and D pull, their
  commits run the *old* `whose_row.py` while lane A's run the new one. **The tree is subject to four
  different check suites at once**, and the printed count is identical in all four.
- **`pre-commit: N checks passed` is not a version indicator.** `BEN-222` recommended reading that count as
  the authority on whether a hook armed. **That was right for a new line and wrong for a changed payload** —
  the count is unchanged by a payload edit. This finding narrows `BEN-222`'s own remedy.

## The check

**To verify a check is deployed, make a commit that only that check can reject.** Stage the specific
violation, attempt a real `git commit`, read the rejection, revert. A success line — any success line — is
consistent with the old check having run.

The corollary for a *reviewer*: asking "did the count go up?" verifies a hook line. Verifying a check's
behaviour requires the violation. Both are cheap; only one of them tests what is usually meant.

## Scope, honestly

- `core.hooksPath` being absolute is a **local configuration** fact about this machine's clone; a fresh clone
  following the dispatcher's own `git config core.hooksPath .githooks` instruction gets a *relative* path,
  where the file and the payload come from the same tree and this finding does not apply. **It applies to this
  working setup, which is the one every lane is in.**
- The split is not a defect in the dispatcher. `cd`-ing to the toplevel is what makes the checks run against
  the committing worktree's *content*, which is what a pre-commit check is for. The surprise is the
  combination with an absolute `hooksPath`, and neither half is wrong alone.
- **Not measured:** whether B/C/D have pulled (the mediator said it would tell them); whether any check other
  than `whose_row.py` differs between the trees right now.

## Related

`BEN-222` (a committed hook is not an installed hook — this is its mirror, and narrows its remedy),
`BEN-218` (one `.git/config` across six worktrees — the shared-config root cause),
`BEN-156` (the thing executing is not the thing you edited),
`OI-47` (isolation is convention, not enforcement), `OI-62(b)`, `OI-64`.
