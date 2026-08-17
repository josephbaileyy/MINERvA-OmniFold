# Testing the gate disabled the gate, for every lane, silently

**`BEN-370`. 2026-08-17, lane A. Self-inflicted, found by accident, ~30 minutes of exposure.**

Within an hour of adding a pre-commit check whose entire purpose is *"a safety mechanism can read green
on precisely the case it does not cover"*, I turned the whole pre-commit hook off for every lane in the
shared checkout, and nothing said so.

## The mechanism, in one line

`git config core.hooksPath <path>` run **inside a linked worktree** writes to the **shared** `.git/config`,
because `extensions.worktreeConfig` is not enabled in this repo. I set it to a throwaway worktree's
`.githooks` to prove that check 8 blocks a real commit — then removed the worktree.

```
git config --show-origin --get core.hooksPath
  file:.git/config   /Users/.../tmp/blk/.githooks
ls -d <that path>                            ->  No such file or directory
git config --get extensions.worktreeConfig   ->  rc 1   (worktrees SHARE .git/config)
```

**Git skips a missing `core.hooksPath` with no diagnostic.** No warning, no error, exit 0. A commit that
runs zero checks looks exactly like a commit that runs all of them, minus one line of output nobody is
watching for.

## Why it is worth a row rather than an apology

**Three separate properties had to hold for this to be invisible, and all three are general:**

1. **A worktree's config write is not scoped to the worktree.** The isolation that `CONVENTION-lane-worktrees.md`
   establishes for the index and the working tree **does not extend to config**. Worktrees isolate
   *writes to files*, not *writes to settings* — and the convention's own summary, "worktrees isolate
   WRITES, not ATTENTION", turns out to have a third exception nobody had named.
2. **A dangling hooks path fails open.** Every other guard in this campaign was built to fail closed. This
   one cannot be: the thing that would refuse is the thing that is missing.
3. **The evidence that a hook ran is the PRESENCE of a line, and absence does not look like failure.**
   `BEN-344`'s rule — a null must be shown capable of being non-null by the same instrument in the same
   run — applied to the hook itself. I caught it only because I happened to be reading commit output for
   the all-passed line for an unrelated reason. **Had I not been, this would have persisted.**

And the shape is the one the check I had just written exists to name: **`KNOWN_ISSUES 48`, green on
exactly the case it does not cover** — reached here by *testing* the mechanism rather than by neglecting
it. The test was correct and necessary; verifying that a hook blocks a commit is precisely what
`CONVENTION-verifying-a-check-is-deployed.md` demands. **The defect is in how I made the hook point
somewhere, not in checking that it does.**

## Blast radius, measured

| commit | time | owner | status |
|---|---|---|---|
| `388abd8` | 01:36 | **another lane** (PET critical path map) | ran **zero** of 9 checks |
| `b7b7c0c` | 01:44 | this lane (GBDT blocker map) | ran **zero** of 9 checks |

**Post-hoc, all nine checks were run directly against `HEAD`: every one `rc=0`**, including
`verify_hash_bindings.py`, the freeze gate whose silent absence would matter most. **So nothing broken
landed — but that is a verification after the fact, not the gate having run**, and the two states are
not interchangeable. The owner of `388abd8` was told, because a lane is entitled to know its commit was
unchecked rather than checked.

## The fix, and the habit that prevents a repeat

```
git config core.hooksPath .githooks        # restored, to the relative form the enable line documents
```

**Use `git -c key=value <cmd>` for a one-shot override.** `git -c core.hooksPath=... commit …` cannot
leak, because it never touches a config file. That is the whole remedy, and it is shorter than the
command that caused this.

**The committed tooling is clean and was not the fault.** `shared_push.sh` creates linked worktrees and
drives them with `git -C <wt> …`; it runs no `git config` anywhere, and
`shared_push_e2e_test.sh`'s `git config user.email` calls are inside independent `git init` clones, not
linked worktrees. Verified rather than assumed, because "my scripts do the same thing" was the first
thing worth ruling out.

## What is NOT fixed, and why I am not fixing it

**There is still no signal that the hook is live.** The natural check — "does `core.hooksPath` resolve to
an existing directory" — **cannot live in the hook**, because a disabled hook does not run to complain.
It has to be either a self-test other lanes invoke or a line in the session workflow telling a lane to
confirm the all-passed line appeared.

**Deliberately left to another lane.** Hooks are shared machinery, I have just demonstrated the cost of
being casual with them, and the lane that broke a mechanism is the wrong one to design its
tamper-detection unprompted. Routed to the mediator with that reasoning rather than patched.

Related: `[[BEN-344]]` (a null shown capable of being non-null), `[[BEN-303]]`, and
`CONVENTION-lane-worktrees.md`, whose isolation guarantees this adds an exception to.
