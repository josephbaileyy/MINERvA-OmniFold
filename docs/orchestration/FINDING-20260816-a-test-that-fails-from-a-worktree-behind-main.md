# A test that fails for anyone running the suite from a worktree behind `main`

**`BEN-343`.** Peer session `B`, 2026-08-16, found while triaging a 4th suite failure that appeared during
an unrelated edit and turned out not to be caused by it. **The test is not mine and I have not changed
it** — this records the defect and the cheapest remedy for its owner.

## What fails, and the exact assertion

`nd-unfolding/tests/test_p4_token_gate_scope_and_rev.py`,
`Defect5_SymbolicCodeRev::test_MUTATION_prefix_helper_reports_every_symbolic_rev_in_history`:

```python
for rev in ("HEAD", "main", "HEAD~0", "HEAD~3"):
    self.assertTrue(mut.code_rev_in_history(rev),
                    f"pre-fix helper should call {rev!r} in-history")
```

Observed failure: `AssertionError: False is not true : pre-fix helper should call 'main' in-history`.

## Why, measured rather than inferred

`code_rev_in_history` asks whether a rev is an ancestor of the current `HEAD`. In a **git worktree on a
feature branch**, `main` is a perfectly resolvable ref and is *not* necessarily an ancestor. Measured at
the moment of failure:

```
branch      worktree-lane-b-oi126
HEAD        e07b986b90e014f9d2c3a46a3a5b53e590111eaa
main        6e05985146d848beb4d518e0070a56704434f249
git merge-base --is-ancestor main HEAD  ->  false
git rev-list --count HEAD..main         ->  1
```

Another lane had pushed one commit while this lane was editing. `main` had moved ahead, so it was no
longer in this worktree's history and the assertion failed. **It cleared on rebase, and the ancestry was
re-measured to confirm the mechanism rather than assumed from the fact that it went away.**

**Nothing about the test's subject is wrong.** The helper behaves correctly; the fourth loop element
simply asserts a property of the *runner's git position*.

## Why this matters here specifically

**This campaign runs most work from worktrees** — `CONVENTION-lane-worktrees.md`, and audit/review lanes
are explicitly given throwaway worktrees. A worktree's branch is behind `main` for the entire window
between another lane pushing and this lane rebasing, which on a busy day is most of the day. **So this
fails for most lanes, most of the time, and each one pays the triage cost of deciding whether their own
edit caused it.** That cost is the real damage: a spurious failure adjacent to your own change is
expensive precisely because you cannot dismiss it without checking.

## `BEN-332`'s shape

`BEN-332` recorded a tracked file whose content is a function of untracked local caches, so its `--check`
gate could never be green on two machines at once. **This is the same defect with a different dependency:
a tracked test whose result is a function of the runner's branch position.** A test that passes on `main`
and fails from a worktree is not testing the code — it is reporting where you are standing.

## The remedy is cheap, and the test loses no coverage

**The other three loop elements — `HEAD`, `HEAD~0`, `HEAD~3` — are symbolic revs that are in history by
construction, from any checkout.** `'main'` is the *only* environment-dependent element, and it adds no
coverage the other three do not already provide: the property under test is that the pre-fix helper treats
**symbolic** names as in-history, and `HEAD~3` is symbolic.

So the smallest fix is to drop `'main'` from the tuple. If a branch-name case is wanted specifically —
reasonable, since a branch name is a different kind of symbolic ref from `HEAD~n` — then create one in the
test rather than borrowing the repository's:

```python
# a branch name that IS in history by construction, instead of borrowing `main`
subprocess.run(["git", "branch", "-f", "ben343-probe", "HEAD"], cwd=REPO, check=True)
```

**Not applied here.** The file is another lane's, the fix is a judgement about what the test means to
cover, and `BEN-300` says the owner should make it. Filed so it is not re-triaged from scratch by the next
lane that sees a red suite.

**Related:** `BEN-332` (same shape, different dependency), `BEN-028` (a symptom that looks like a failure
of the thing you just touched), `CONVENTION-lane-worktrees.md`.
