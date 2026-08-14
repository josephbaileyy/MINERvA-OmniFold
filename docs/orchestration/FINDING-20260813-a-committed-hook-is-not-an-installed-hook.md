# FINDING 2026-08-13 — a committed hook is not an installed hook

**`BEN-222`.** Lane A, caught in the commit that was supposed to install `OI-64`'s gate. **The gate is
committed, pushed, and not yet in force.**

## The observable that caught it

I added `verify_hash_bindings.py` as a 5th pre-commit check, verified it by hand, and committed. The commit
printed:

```
pre-commit: 4 checks passed
```

**Four.** The file I had just staged says `5`. Nothing failed; the hook simply was not the file I edited.

## The mechanism

```
$ git config --get core.hooksPath
/Users/josephbailey/local-research/MINERvA-OmniFold/.githooks
```

**It is an absolute path into the main checkout, not the relative `.githooks` the dispatcher's own
"ENABLE PER CLONE" line prescribes.** And `.git/config` is shared by all six worktrees — that is `BEN-218`,
filed this morning about `git config --local` not being lane-local.

So:

| | what I assumed | what is true |
|---|---|---|
| hook git runs, from lane A's worktree | `.claude/worktrees/lane-a/.githooks/pre-commit` | `<main checkout>/.githooks/pre-commit` |
| whose revision governs | mine, at HEAD | **the main checkout's WORKING TREE**, at whatever it sits at |
| effect of committing a hook change | armed | **inert until the main checkout updates its tree** |

Confirmed from the other side: the main checkout's copy holds **0** occurrences of `verify_hash_bindings`.

## What this does to the deliverable, stated plainly

`OI-64`'s gate is **committed and pushed at `682c25f` and NOT YET RUNNING FOR ANYONE.** It arms when the main
checkout's working tree picks up the new `.githooks/pre-commit` — which is somebody else's `git pull`, in a
directory this session is correctly forbidden from writing to.

**I should not have reported it as installed, and the reason I nearly did is the interesting part.**

## The verification error, which is the transferable lesson

I ran two controls and both were sound:

- **green:** `bash .githooks/pre-commit` → exit 0, `pre-commit: 5 checks passed`
- **red:** floor forced to 200 → exit 1, `PRE-COMMIT FAIL: receipt+shell hash bindings`

**Both tested the right file by the wrong path.** `bash .githooks/pre-commit` executes the file at that
relative path — mine. Git executes `core.hooksPath` — the main checkout's. My controls proved my *script*
worked; they could not distinguish "the hook is installed" from "a file that would work if installed exists
in my worktree", because I chose the invocation instead of observing it.

**The evidence that would have caught it was already on screen and I did not read it:** every commit in this
session printed `pre-commit: 4 checks passed`, including the one whose whole purpose was to make that say 5.
This is `BEN-207`'s shape — *a PRESENT verdict is also a statement about the search* — applied to my own
output: the disqualifying content was in the output I had already produced.

## Two refinements from lane C, which observed this from the other side

C hit the same mechanism as a *reader* and its evidence is better than mine, because C changed nothing and
watched the behaviour change anyway. **C's commits went from `4 checks passed` to `5 checks passed` with no
edit in its own worktree** — the transition happened when the main checkout's tree updated.

**1. The arming is invisible, and it retroactively falsified a written statement.** C had recorded
*"the pre-commit hook doesn't run the hash-binding gate."* That was **true when written and silently became
false.** Nobody edited it; no signal marked the transition; and the sentence is exactly the kind a later
session would rely on. **My finding said the gate was "not in force until the main checkout updates" and
stopped there — the sharper point is that the update is unobservable from any worktree, so a correct
statement about hook coverage has a shelf life set by someone else's `git pull`.** Same shape as `BEN-219`
(right at write time, wrong at read time), in a different substrate.

**2. A worktree can never test its own hook changes.** This is the part I got wrong in a way worth
separating from carelessness. I wrote that I "chose the invocation instead of observing it," which implies the
correct test was available and I skipped it. **It was not available.** From a worktree there is no way to make
git run the worktree's hook, because `core.hooksPath` is absolute and shared; the only faithful test is to
commit and read the count. **So `bash .githooks/pre-commit` was not a lazy substitute for the right check —
it was the only local check that exists, and its limitation is structural.**

That makes this `BEN-156` one level out — *the thing executing is not the thing you edited* — and the
correct discipline is not "test harder locally" but **"treat the printed count as the only authority, and
expect the arming to happen in someone else's commit."**

**C declined to file these**, having exhausted block `130-159`, and declined an offered `230-239` on the
grounds that **a deployment which produced no failure does not justify claiming a ten-block to hold
nothing.** That reasoning independently reproduces this ledger's own rule 3 — *the block is claimed by the
first filing into it, not reserved ahead of one* — and rule 3 has been sharpened with C's phrasing.

## The check

**Verify a hook by reading what git ran, not by running what you wrote** — and from a worktree, the only
faithful reading is the count a real `git commit` prints.

```
git config --get core.hooksPath      # absolute? then it is NOT your worktree's copy
```

The count in the hook's own success line is a free installed-version indicator — it is why
`pre-commit: N checks passed` states a number, and the number is worth reading on every commit rather than
skimming as noise.

## Two structural consequences worth separating from my mistake

1. **Hook CONTENT is not lane-local**, the same way `git config --local` is not (`BEN-218`). That finding
   fixed the identity case and this is the same shared-`.git/config` root cause one artifact over.
2. **Whoever occupies the main checkout silently controls every lane's hooks**, at their working tree's
   revision — including a dirty or mid-rebase tree. A lane cannot tell from its own directory which checks
   will run against its commit. `OI-47` is about isolation being convention rather than enforcement; this is
   a case where isolation is *absent by configuration* in a direction nobody declared.

## Related

`BEN-218` (`git config --local` is not lane-local — same shared config, different artifact), `BEN-207` (the
disqualifying content was already on screen), `BEN-156` (a check that exists and guards nothing — which is
what this leaves `OI-64`'s gate as, until the main checkout updates), `OI-47`, `OI-64`.
