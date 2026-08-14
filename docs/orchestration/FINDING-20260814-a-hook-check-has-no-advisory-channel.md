# FINDING 2026-08-14 — a hook check has exactly two channels, and neither of them is "advisory"

**`BEN-226`.** Lane A, found while deciding whether to close an asymmetry lane D raised. **The finding is
what made the answer "no, and here is why" instead of a one-line fix.**

## The mechanism

`.githooks/pre-commit`, line 33:

```bash
run() { local n="$1"; shift; "$@" >/tmp/.hook.$$ 2>&1 || { echo "PRE-COMMIT FAIL: $n"; cat /tmp/.hook.$$; fail=1; }; }
```

Every check's stdout and stderr go to a temp file, and that file is `cat`-ed **only on non-zero exit**. So:

| check exits | its output |
|---|---|
| non-zero | printed, under a `PRE-COMMIT FAIL:` header |
| **zero** | **captured and discarded** |

**Control**, replicating the idiom with two arms:

```
run "passing but chatty" bash -c 'echo "ADVISORY-FROM-PASSING-CHECK"; exit 0'
run "failing and chatty" bash -c 'echo "ADVISORY-FROM-FAILING-CHECK"; exit 1'
→ FAIL: failing and chatty
  ADVISORY-FROM-FAILING-CHECK
```

`ADVISORY-FROM-PASSING-CHECK` never appears. **Corroborated by evidence already in hand rather than only by
the control:** `whose_row.py --check-oi-ids` prints a census line (`[70 data rows, 70 OI ids, 2 duplicated,
2 waived]`) on every successful run, and that line appeared in **none** of the day's commits — all of which
showed only `pre-commit: 6 checks passed`.

## Why it mattered, which is the reusable part

Lane D raised a genuine asymmetry in the new `OI-*` block arm — `BEN-173`/`BEN-180`'s shape, a control on one
side and none on its mirror:

- **reject direction:** a lane that forgets `git -c` and files an id *outside* the fallback block fails
  **loudly**, and now gets a NOTE naming the `git -c` form.
- **accept direction:** a lane that forgets `git -c` and files an id *inside* the fallback block `120-129`
  is **accepted silently**, attributed to the fallback rather than to itself.

**The obvious fix is "accept but warn". This finding says that does not exist.** In a hook there are two
behaviours, fail or nothing, so the choice collapses to:

1. **Fail** — but Joseph filing in his own block is legitimate, and lane D's own admitting rule (*a committer
   who did nothing wrong can always make it pass*) forbids failing him.
2. **Nothing** — leaving the asymmetry, which is what was chosen, with the reason recorded in the check's
   docstring and a named unlock trigger rather than as an undocumented gap.

**A third branch, raised by lane D with its own objection attached, recorded because *"we considered it and it
collapses"* is more durable in a docstring than an absence** — the same reason `BEN-*` block `047-059` is
annotated `DO NOT USE` rather than left silently empty:

3. **Record** — the check writes an observation somewhere and something else surfaces it.

**It does not collapse to "nothing"; it collapses in two directions, and only one of them is a trap.** D's
objection covers the trap: **writing into the tree mid-commit touches unstaged files** — which here would also
corrupt the block arm's own `HEAD`-versus-staged diff — and **writing outside the tree creates a channel nobody
watches**, which is `BEN-156`'s shape (a check that exists and guards nothing) and `BEN-202`'s (reachable only
by agents who already knew about it). Both are worse than nothing.

**The other direction is not a trap and is already prescribed:** if the observation is recorded somewhere
*already watched* — a test that reports, a surface someone reads — that is exactly the *"put advisories in a
test"* remedy below. **So `record` is not a third option. It is the existing remedy when the destination is
watched, and an unwatched channel when it is not**, and the only thing distinguishing them is a property of the
destination rather than of the check.

**What is actually lost is attribution, not collision-safety** — two parties both defaulting to the fallback
and both running `max+1` collide, and the **duplicate** arm catches that. Attribution is `OI-62(c)` (three
parties share one git identity), `WAITING-USER`.

**The trigger, so it is a conditional TODO and not a someday:** if `OI-62(c)` resolves such that every
committer carries a lane identity, **nobody legitimately files into the fallback block**, and an id arriving
there becomes free to detect as an error. Revisit then.

## The design rule

**Design a hook check as binary.** If a check has something to say that should not block a commit, a hook is
the wrong host — put it in a test that reports, or in a report someone reads. Advisory output added to a hook
check is written into a void, and will look like it works to whoever adds it, because they will run it by hand
where it prints.

**Corollary for reading a hook's silence:** `pre-commit: N checks passed` is not merely uninformative about
*what* was checked (`BEN-222`, `BEN-224`) — it is the **only** thing a passing hook can ever say. Any
expectation that a check will surface a nuance on the happy path is mistaken.

## Related

`BEN-173`, `BEN-180` (a control on one side and none on its mirror — the shape of the asymmetry this decides
not to close), `BEN-222` / `BEN-224` (a green count is a statement about what ran), `OI-62(c)` (the unlock
trigger), `CONVENTION-verifying-a-check-is-deployed.md`.
