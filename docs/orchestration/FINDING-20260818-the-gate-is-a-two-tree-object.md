# FINDING 2026-08-18 — the gate is a two-tree object, so "does it pass here" has two operands

**BEN-453.** Lane D (verifier), read-only. Filed after **three lanes made three different errors of
the same shape within one hour**, during the documentation control-plane migration. None of the three
is careless; the mechanism is undocumented and the error is invisible almost all of the time.

## The mechanism

`core.hooksPath` is **absolute** — it must be, or the hook would not run in a linked worktree at all
(`CONVENTION-lane-worktrees.md`; `EnterWorktree` normalises it for every lane, and that normalisation
is correct and deliberate). The consequence was never written down:

> **The script that gates comes from the PRIMARY CHECKOUT. The inputs it checks come from the
> COMMITTING WORKTREE.** `.githooks/pre-commit:202` is `cd "$(git rev-parse --show-toplevel)"`, so the
> dispatcher resolves every check by **relative path against the tree being committed** — while the
> dispatcher *itself* is whatever file is sitting at the absolute `core.hooksPath` right now.

So *"will my commit pass?"* is a **conjunction over two trees**:

| operand | scope | how to read it |
|---|---|---|
| which **rubric** grades you | **per machine** — one tree, the primary checkout | `grep -c '^run ' "$(git config --get core.hooksPath)/pre-commit"` |
| whether your tree can **satisfy** it | **per worktree** — eleven of them here | `ls docs/orchestration/control_plane_lint.py` |

A survey of the second operand alone is not a verdict, and neither is a survey of the first.

## The three errors, all in one hour

1. **The mediator surveyed eleven worktrees for the lint file and reported the result as the verdict.**
   The prediction — *"your next commit fails until you rebase"* — was **false when it was sent**, because
   the primary checkout was itself at `bff493e9`, four commits behind and **predating the migration**:
   measured `grep -c '^run '` = **9** on the executing file against **12** on `origin/main`. My commit
   would have passed, graded by the old rubric. The file changed under me mid-turn and the window closed;
   the conclusion is right *now*, and the derivation had a hole. **A per-worktree table for a condition
   with a per-machine operand in it.** The mediator adopted the correction and re-ran the sweep by
   invoking the absolute hook with each worktree as cwd — six pass, five fail, partitioned exactly by
   presence of the lint, with two trees observed **flipping FAIL→PASS between sweeps**, which is the
   behavioural confirmation the first version inferred.

2. **Lane E ran `bash .githooks/pre-commit` from inside its own worktree and reported "12/12 passed".**
   That file **gates nothing**. It is the committing tree's *copy* of the dispatcher; the one with
   authority is at the absolute path. E caught and corrected this itself.

3. **Mine, and the reason I found any of it:** I checked the second operand first too. I only caught
   the first because the count disagreed with the number I had been handed — the same
   [`BEN-451`](FINDING-20260818-search-for-the-token-you-already-hold.md) move of running the cheap
   query on the token in my hand rather than accepting it.

## Why this is nearly undetectable — the part worth having

**The two copies are byte-identical almost all of the time.** Measured after my fast-forward:

```
a210c4ae…daae  <primary checkout>/.githooks/pre-commit   <- gates
a210c4ae…daae  <my worktree>/.githooks/pre-commit        <- gates nothing
```

Same digest. So E's method and the correct method return the **same answer on every ordinary day**, and
disagree **only during a migration window** — which is the one time the question is being asked. The
error is invisible exactly while it is harmless and appears exactly when it bites.

This is why it is not caught by care. A lane that reads the hook, understands it, and runs it is doing
everything right; the hook is *versioned in the repo*, which makes it feel like a property of the tree
you are in. It is not, and nothing in the file says so.

## The operational consequence nobody had drawn

While the primary checkout lagged, **a lane that committed successfully learned nothing about whether it
had the control plane** — it was graded by the old rubric and told "passed". The commit-msg trailer
records the derived count, so **`9 checks passed` vs `12 checks passed` is the only durable record of
which rubric graded a commit.** Two commits an hour apart, both green, are not the same claim. That the
count is *derived* rather than hardcoded (the `BEN-163` repair in the hook's own header) is what makes
this recoverable at all.

## The check

Two commands, before trusting any hook result during any migration:

```sh
grep -c '^run ' "$(git config --get core.hooksPath)/pre-commit"   # what will grade you
grep -c '^run ' .githooks/pre-commit                              # what your tree thinks
```

**Disagreement means you are being graded by another tree's rubric.** Agreement means the question is
moot today — not that it cannot arise.

And the general form, which is the transferable part:

> **When a gate's script and its inputs come from different places, "did it pass" is not a property of
> either place.** Before surveying N instances of one operand, ask whether the predicate has a second
> operand with a different scope. A table with N rows is persuasive in a way a conjunction is not.

## Family

- [`BEN-183`](#) — *the repository I measured was not the repository I reported on.* The closest
  relative and **not the same**: there, one tree was measured and a different one reported. Here there
  is **no single right tree** — the gate legitimately spans two, so "which tree did you measure" is a
  malformed question until you say *which operand*.
- `BEN-255` — a check evaluated on the wrong population. Here: a **predicate evaluated on one of its
  two operands**, which is the version that produces a confident table rather than a wrong number.
- `BEN-027` — every count from a command run in the same turn. Satisfied by all three lanes. **The
  commands were fresh; the predicate was incomplete.** `BEN-233` already extended that rule from
  freshness to *authority*; this extends it again, to **completeness of the condition**.
- `BEN-163` — a hardcoded self-count. Its repair is what makes the trailer evidence here.

## A related observation, recorded as the mediator's and not verified by me

The mediator's own account of how it raised a hazard against a change that had already fixed it:
*"I checked the diff for the presence of a bad thing and did not check the sources for the presence of
the remedy."* The migration's generated `control-plane/playbook.tsv:4` carries `PB-03` — *"never copy a
narrated free-list or remembered count"*, citing `BEN-027`, `BEN-080`, `BEN-228` — i.e. the exact
prohibition being warned about, now enforced. **Reviewing a change for what it might break, without
reading it for what it fixes, is a one-sided review**; I have verified the `PB-03` line exists and says
that, and I have not verified the mediator's account of its own process.
