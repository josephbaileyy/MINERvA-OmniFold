# FINDING 2026-08-15 — a clean tree that had already pushed, and the stale code claim it caught

`BEN-351`. Lane A. Episode `EP-2026-08-15-oi6-note-footing`.

## What happened

A session was dispatched to write the `OI-6` footing passage into the analysis note, with this
framing:

> A previous session was given this and stopped responding; you are a fresh start. **The working tree
> is clean — nothing was left half-written, and you should not go looking for a partial edit to
> finish.**

Both sentences were **true of the working tree and false of the remote**. `git status` at session
start showed one untracked scratch file and nothing else, `git log --oneline -1` showed `361d83e`,
and that is exactly what a fresh start looks like. The predecessor had not stopped before finishing:
it completed the assignment and pushed `e61624b` — *"Place the standard-5D purity footing and its
limit in the analysis note: app_negweight.tex B.6, note build only, all three builds pass"* — while
this session was writing its own version of the same subsection.

The collision surfaced at the very last step:

```
$ git push
 ! [rejected]        main -> main (non-fast-forward)
## main...origin/main [ahead 1, behind 1]
```

By then this session had written a seven-subsubsection passage, run `build_all.sh` twice over three
PDFs, verified include closure and containment, and committed.

## The transferable part

**`git status` answers *"is my tree dirty"*. It does not answer *"did this work already land"*.** For
a lane starting fresh those are the same question. For a lane **resuming or replacing another lane's
task** they are different questions with different answers, and only the second one matters.

The check is free and there is no reason not to make it the first thing a takeover session does:

```sh
git fetch origin && git log --oneline origin/main -5
```

Four lanes share this checkout and sessions are killed and respawned keeping their names, so "the
predecessor stopped responding" is a statement about a channel, not about a repository. A dead
channel and an unfinished task are not the same event — the predecessor here was unreachable
*because it had finished*.

This is `BEN-228`'s family (a narrated state trusted instead of a derived one) applied to liveness
rather than to indexes.

## The part that made the duplication worth something

The landed passage identifies the standard chain's footing like this:

> It is positively identified as purity-footed rather than merely unstamped: **neither producing
> launcher passes `--bkg-mode`**, the driver's default for that flag is `purity`, and the driver
> announces its mode only on the negative-weight branches …

That is `RUNBOOK-20260807-gbdt-closeout.md` §3's finding, faithfully transcribed. **The same runbook's
G-1 packet superseded it.** Measured in this session:

| site | content |
|---|---|
| `nd-unfolding/p4_lib.py:225` | `STANDARD_BKG_MODE = "purity"  # the 2026-08-07 decision; see OPEN_ITEMS G-0` |
| `nd-unfolding/p4_lib.py:276-278` | `P4Config.validate()` requires `bkg_mode == STANDARD_BKG_MODE`, fail closed |
| `nd-unfolding/run_p4_unfold_std.sh:41` | `BKG_MODE=$(python3 -c "import p4_lib; c=p4_lib.P4Config(); c.validate(); print(c.bkg_mode)")` |
| `nd-unfolding/run_p4_unfold_std.sh:111` | `--bkg-mode "${BKG_MODE}"` — **passed explicitly** |
| `nd-unfolding/run_p4_unfold_std.sh:120` | stamps `"bkg_mode_basis":"passed explicitly to the driver by this launcher"` into every receipt |
| `nd-unfolding/run_active_lateral_unfolds_interactive.sh:41` | no `--bkg-mode` — but `:20` aborts on `MODE=standard` unless `ALLOW_RETIRED=1` |

So the sentence is **true of the 2026-07 production event and false of the chain today**, and its
error runs in the direction of *understating* the analysis: the note claimed a footing inferred from
a silent default at precisely the point where the code now asserts and stamps it. G-1 exists to make
that claim provable, and the note gave the guarantee away.

**Same tense defect as `BEN-350`, mirrored.** `BEN-350` is a *plan* read as a *product*. This is a
*superseded code state* read as *current*. Both come from copying a true sentence out of a document
written at a different moment, and in both cases the document was not wrong.

## Fix

`app_negweight.tex` §B.6's first paragraph now separates the two epochs explicitly: *"for the existing
endpoint unfolds"* keeps the identification-by-elimination argument unchanged and dates it, and *"for
the chain as it now stands"* records the pin, the explicit flag, and the receipt stamp, noting that
the change is a provenance change and a physics no-op because the value it asserts is the default it
replaces.

**One paragraph, nothing else touched.** Two lanes sharing a checkout is the condition that produced
this, and a third opinion in the same file compounds it rather than resolving it. Every other
sentence of the other lane's passage stands as written.
