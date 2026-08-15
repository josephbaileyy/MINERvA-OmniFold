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

## THE GENERAL FORM, which is larger than line numbers

Lane D's mediator supplied the unification and it is better than this finding's first framing:

> **A hand-maintained index of a machine-derivable fact goes stale silently.**

**A line number is exactly that** — `grep -n` derives it in milliseconds, and writing it down converts a
derivable fact into a hand-maintained one with a hidden timestamp. Every instance below is the same defect at
a different size:

| the hand-maintained index | what derives it | how it went stale |
|---|---|---|
| `…promotion…json:95` in prose | `grep -n 'That OI-23 is discharged'` | a block inserted above it, **same commit** |
| `FINDINGS.md`'s *"`221-229` free"* | `grep -oE '^\| BEN-22[0-9] \|' \| sort -u` | wrong since `BEN-221`, **in the same file as the "derived, not narrated" rule that forbids it** — cell at `:19`, rule at `:79` |
| `MANIFEST.tsv`'s `generated` + producer for `live-state.json` | reading `generate_live_state.py:22-23` | the file is that script's **input**; it is never written by it (`OI-73`) |
| a bare sha256 in prose | `git show <ref>:<path> \| shasum -a 256` | the file was edited after the note (`BEN-227`) |

**The free-list instance is the one that shows the mechanism cleanly**, because it was found only by someone
editing the row for an unrelated reason — the filer is the last person who will ever reread their own
free-list, so the index is maintained by exactly the party with no reason to check it. **`OI-73` is this
shape one size up**, and it is the worst of the four because its stale index does not merely mislead: it makes
the documented remedy look forbidden, so following the procedure exactly cannot fix it.

**The unified rule, and it subsumes the procedure above:** *if a fact is machine-derivable, cite the
derivation or an address that survives edits — never the coordinate.* Content addresses
(`explicitly_not_claimed[2]`, a quoted phrase, a key path) survive insertion; line numbers, counts and
free-lists do not.

## Related

`BEN-225` (the concurrency version, and the remedy that does *not* cover this), `BEN-219` (a citation correct
at write time — same family, longer interval, different cause), `BEN-216` (why cited ids are not renumbered),
`CONVENTION-verifying-a-check-is-deployed.md` (*a fact about a concurrently-written repository is a measurement
with a timestamp* — here the repository is not even concurrent; the writer is).
