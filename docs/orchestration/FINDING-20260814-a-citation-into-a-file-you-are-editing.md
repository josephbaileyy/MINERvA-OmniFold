# FINDING 2026-08-14 — a line citation into a file you are editing in that commit is stale the moment you edit it

**`BEN-228`.** Lane A. **Strictly cheaper to trigger than `BEN-225`, and therefore more common: it needs no
rebase, no second lane, and no concurrency at all.** Written at the mediator's request, which called it *"the
most transferable thing"* in the report it came from.

## The mechanism

Two citations in one commit were falsified **by that same commit's own edits**:

| citation written | what it became | why |
|---|---|---|
| `ND_OMNIFOLD_STATUS.md:52` | **`:59`** | the STATUS one-liner edited *above it*, in the same commit, grew by 7 lines |
| `…gate4-nominal-promotion…json:95` | **`:102`** | a supersession block inserted *above it*, in the same commit |

Both numbers were derived correctly with `grep -n`. Both were **true when derived and false when committed**,
and the interval was minutes with nobody else involved.

## WHY THIS IS NOT `BEN-225`, AND THE DIFFERENCE IS THE POINT

`BEN-225` is: a claim verified pre-rebase, published post-rebase, falsified by **another lane's** work arriving
under a finished commit. Its remedy is **re-run the check after `git pull --rebase` and before `git push`.**

**That remedy does not catch this one.** Re-running after the rebase re-runs the *check*; it does not
re-derive the *number*. If the stale line number is sitting in prose you already wrote, a rebase-time re-run
finds nothing wrong, because nothing about the rebase caused it and nothing about the rebase reveals it.

| | `BEN-225` | **`BEN-228`** |
|---|---|---|
| needs another lane | yes | **no** |
| needs a rebase | yes | **no** |
| interval | 7 seconds | minutes, entirely self-inflicted |
| caught by re-running after rebase | yes | **no — unless numbers are RE-DERIVED, not re-used** |

**So this is the cheaper failure and it will happen more often.** Every commit that both edits a file and
cites a line in it is exposed, and multi-file bookkeeping commits do this constantly — the more thoroughly a
commit cross-references itself, the more exposed it is. **Rewarding cross-referencing while making it
self-falsifying is the trap.**

## THE RULE

> **Derive every cited line number AFTER the last edit to the file it points into. Re-derive, never re-use —
> a number you wrote down 40 minutes ago is a measurement of a file that no longer exists.**

Operationally, and this is the whole procedure:

1. Make all edits first. Do not interleave citing and editing.
2. **Then** re-derive every citation with `grep -n '<the actual text>'` — search for the *content*, not the
   line, because content survives edits and line numbers do not.
3. Only then write the numbers in, and commit without further edits to those files.
4. If a later edit becomes necessary, **go back to step 2**. There is no shortcut, because the failure is
   silent by construction.

**A cheap structural alternative where it fits: cite the content, not the coordinate.** `explicitly_not_claimed[2]`
is stable under insertion; `:95` is not. A JSON pointer, a key path, or a quoted phrase all survive edits that
a line number cannot. **Prefer them wherever the target has an addressable name** — the line number is a
last resort for prose that has no other handle.

## How both were caught, and it generalises

By re-deriving *every* cited line with `grep -n` before the push rather than trusting the numbers recorded
earlier in the same session — done because `BEN-225`'s remedy had already forced a full re-verification pass
after the third rebase of the night, and the self-inflicted pair fell out of it **as a side effect**.

**That is luck, and it should not be relied on.** Three rebases happened to force a re-derivation pass; a
commit with no rebase gets none, and would have published both stale numbers with every check green. **The
re-derivation pass therefore belongs to the commit, not to the rebase.**

## Related

`BEN-225` (the concurrency version, and the remedy that does *not* cover this), `BEN-219` (a citation correct
at write time — same family, longer interval, different cause), `BEN-216` (why cited ids are not renumbered),
`CONVENTION-verifying-a-check-is-deployed.md` (*a fact about a concurrently-written repository is a measurement
with a timestamp* — here the repository is not even concurrent; the writer is).
