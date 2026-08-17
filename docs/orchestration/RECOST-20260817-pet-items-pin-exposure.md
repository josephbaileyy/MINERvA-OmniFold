# RE-COST — pin exposure across the remaining PET items, measured by asking the gate rather than reading the rows

> **SUPERSEDED 2026-08-17 by [`SWEEP-20260817-pet-pin-exposure-complete.md`](SWEEP-20260817-pet-pin-exposure-complete.md), and left in place rather than rewritten because its error is the instructive half.** Two defects, both found by extending this probe rather than by reading it (`BEN-385`):
> **(1) THE `OI-64C` LINE BELOW IS A CORRECT MEASUREMENT OF THE WRONG FILE.** `check_canonical_designation.py` is not that item's edit site; its sites are `verify_executing_copy_is_committed.py` and the two callers it must be wired into, **both of which are PINNED**. Read the `OI-64C` row here as answering nothing.
> **(2) THE BINARY BELOW HAS NO CELL FOR TWO REAL STATES** — *pinned but tolerated* (`KNOWN_PREEXISTING`, four files, gate stays green) and *bound by a comparator the gate cannot resolve* (`BEN-322`; for `OI-60` that is nine of eleven sites). A `not pinned` cell below means "this gate stayed green", not "this file is free".
> **What stands unchanged:** the `OI-61` finding, the positive-control discipline, and the closing rule about re-running the gate after writing.

**Lane E, 2026-08-17.** `BEN-384` turned into a sweep, on the mediator's instruction: *"for each
remaining candidate, check whether any file it touches is hash-pinned, before writing anything."*

**No batch job, no compute, nothing submitted. Every probe restored the file byte-exactly and the
gate was re-checked afterwards.**

---

## Why a grep is not the test

`BEN-384`'s lesson is that **the pin is invisible from the row and from the code** — I found `OI-60`'s
only by writing the whole diff and watching `verify_hash_bindings.py` go red. A grep for a filename
finds mentions, not bindings, and would have answered the wrong question in both directions: the
loader is named in dozens of places and pinned by two, while a file can be pinned under a path spelled
differently from how the row spells it.

**So the probe asks the gate the question the gate answers:** append one comment line, run
`verify_hash_bindings.py`, restore. Script:
`docs/orchestration/state/probe-pin-exposure-20260817.py`.

**The result is only meaningful because it carries a positive control.** `OI-60`'s loader is included
deliberately as a **known-pinned** case: if it had come back "not pinned" the probe would be broken
and every negative below would be vacuous. It came back `PINNED`, so the negatives are measurements.

```
baseline: ALL BINDINGS INTACT

OI-96    not pinned   nd-unfolding/pet/check_canonical_designation.py
OI-96    not pinned   docs/orchestration/verify_hash_bindings.py
OI-12    not pinned   nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py
OI-12    not pinned   nd-unfolding/p4_lib.py
OI-61    PINNED       nd-unfolding/pet/train_fullevent_nominal.py
OI-61    not pinned   nd-unfolding/pet/train_fullevent_replica.py
OI-64C   not pinned   nd-unfolding/pet/check_canonical_designation.py
OI-60    PINNED       nd-unfolding/pet/fullevent_fps_dataloader.py   <- positive control

re-check after all probes: INTACT
```

## What it changes

**`OI-61` is worse than its row says, and this is the new information.** The row's cost is *"two
receipt-vocabulary fixes, cosmetic-to-value, rides the next Gate-5 launcher."* But it touches
`train_fullevent_nominal.py`, which is **PINNED** — so it is blocked on a GPU launcher run **and** on
the same class of pin that re-costed `OI-60`. **Corroborated independently rather than resting on my
probe alone:** `OI-57`'s row already records `train_fullevent_nominal.py:642` as *"pinned by
`gate6-leg0-tier-calibration` `pinned_paths[8]` and deliberately NOT touched"*, written by a different
lane for a different reason. Two instruments, same answer.

**`OI-96`, `OI-12` and C's `OI-64` are clean on the pin axis.** That does not make them free — `OI-96`
is a change to pre-commit check 6, `OI-12` belongs to the FPS lane and its own audit says so — but
**neither carries the hidden Gate-re-run cost**, which is the thing that could not be seen from the
rows.

**Two of the eight files probed are pinned, and they belong to two different items.** So the earlier
observation stands and sharpens: **"is this area pinned?" has no answer — it is per file, and within
one item's file set the answer differs** (`OI-61`: nominal driver pinned, replica driver not;
`OI-60`: loader pinned, target builder and trainer not).

## The bounded negative

**This sweep covers the files the rows name, and no others.** An item whose fix turns out to need a
file its row does not mention is not covered — which is exactly how `OI-60` surprised me, since its
row named the loader but the cost lived in a Gate-2 receipt two hops away. **The probe answers "is
this file pinned", not "is this item cheap".** The honest form of the rule is therefore:

> Run the probe before writing, and **run the real gate again after writing**, because the second is
> the only one that sees the file you actually had to touch.

## Cost of the sweep

One script, eight probes, seconds. **Against `OI-60`, where the same fact cost a complete
implementation, a test suite and a revert.**
