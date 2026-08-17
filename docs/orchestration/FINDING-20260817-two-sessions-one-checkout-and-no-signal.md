# Two sessions committed from one checkout all day, and nothing signalled it

**BEN-398.** Filed 2026-08-17 by the seconding lane (block `390-399`). **Discovered by the mediator, by
accident. The live near-miss below is this lane's own measurement**, taken before any recovery action.

## The finding is not "two sessions shared a tree." It is that nothing said so.

**Measured — `git worktree list`:**

```
/Users/josephbailey/local-research/MINERvA-OmniFold                      b42230d [main]      <- TWO sessions
.claude/worktrees/lane-b                                                e89fa56 [lane-b]
.claude/worktrees/lane-b-oi126                                          bd784e4 [worktree-lane-b-oi126]
.claude/worktrees/lane-c                                                b751659 [lane-c]
.claude/worktrees/lane-d                                                a80b167 [lane-d]
.claude/worktrees/lane-e-causes-3-4                                     78cf951 [worktree-lane-e-causes-3-4]
```

**Every other lane is isolated on its own branch. Two of us defaulted to the main checkout and neither knew.**
The collision surfaced only because `git` happened to refuse a rebase — *"cannot pull with rebase: You have
unstaged changes"* — on a file neither session was writing at that instant. **Had our writes been to different
files, nothing would ever have surfaced it.**

## The live near-miss, measured before acting

After the other session ran `git reset --mixed origin/main` in the shared tree (correctly — it preserved every
working file), my uncommitted `FINDINGS.md` edits were sitting on a moved base. **Before touching anything I ran
`git diff`, and it showed my working copy would have made these deletions:**

```
-| [`FINDING-20260817-corroboration-and-echo-have-opposite-value.md`](...) | **Corroboration and echo …
-| BEN-248 | **CORROBORATION AND ECHO HAVE OPPOSITE EVIDENTIAL VALUE …
```

**Two lines removed with no replacement — lane B's row and its long-form index entry**, because my copy of the
file predated B's `bd784e4`. Committing my own three-row edit from the shared tree would have silently deleted
another lane's finding.

**And it would have looked like a clean commit.** Three insertions, five deletions, one file, a coherent commit
message about my own rows, **and nine passing pre-commit checks** — the hook validates the tree it is handed and
has no concept of *whose* edits are in it. So the first symptom of a shared checkout is not a conflict; **it is
a well-formed commit that removes work nobody was looking at.** That is strictly worse than a conflict, which is
`BEN-247`'s asymmetry again: the loud failure forces a search, the quiet success terminates one.

## What worked, as a recovery pattern

1. **Preserve the diff before any git operation.** The other session did this to scratch, per the standing rule
   that a delegate's diff may contain real findings; that rule paid here for a peer's diff rather than a
   delegate's.
2. **Never `git checkout -- .`, `git restore .`, `git stash`, or rebase on a shared tree.** The status list
   contains a `D` for a file that *exists on `origin/main`* and two `M`s belonging to other sessions. **All
   three look exactly like damage to be cleaned up and none of them is.**
3. **Commit from a throwaway worktree at `origin/main`, re-applying your edits there** rather than committing
   the shared tree's copy. My three edits were re-applied onto `origin/main` and produced a `3 insertion / 3
   deletion` diff — no other lane's content in it.
4. **Then bring the shared file forward** with `git restore --worktree --source=origin/main -- <file>`, which
   removes the hazard for the next session to commit from that tree without touching HEAD, the index, or any
   other lane's file.

## The mechanical fix

> **A session that intends to commit should first assert it is in its own worktree** — or the dispatcher should
> give every lane one.

One command, no state written, verified both ways this turn:

```bash
[[ "$(git rev-parse --git-dir)" != "$(git rev-parse --git-common-dir)" ]] || { echo "NOT in a lane worktree"; exit 1; }
# main checkout   -> .git                     == .git                 -> fails, correctly
# linked worktree -> .git/worktrees/<name>    != .git                 -> passes
```

**This form is chosen deliberately over anything that touches configuration.** `EnterWorktree` normalises
`core.hooksPath` to an absolute path in the *shared* `.git/config` for every lane, so a worktree-related fix
routed through config is itself a cross-lane write. `git rev-parse` reads and writes nothing.

**It fails for the right reason** — a lane that has not been given a worktree is told so before it can commit,
rather than after — and it cannot fire on a healthy case, which is `BEN-381`'s bar. **Whether it belongs in the
pre-commit dispatcher is not this lane's call:** it would redden for any session legitimately working in the
main checkout, so it fails the admitting rule at `.githooks/pre-commit:11` as written and would need to be a
lane-invoked assertion instead. Routed, not wired.

## Cross-references

- `BEN-247` — a partial success satisfies the stopping condition without satisfying the question. A clean-looking
  commit is the purest form.
- `BEN-330` — two lanes, one checkout, and `git add` **by name** bounding which *files* a commit takes and not
  *whose hunks travel inside them*. **That row is this hazard's prior instance and it did not name the cause**;
  this row supplies it — the two lanes were in the same checkout, and nothing told them.
- `BEN-214` — attribution drift under a shared git identity. Same root, different symptom: shared identity
  confuses *who wrote it*, a shared checkout confuses *what is in it*.
- `BEN-370` — `core.hooksPath` written into the shared `.git/config` from inside a linked worktree. The
  complement: worktrees isolate the index and the working tree, and not settings.
