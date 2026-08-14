# FINDING 2026-08-13 — "recompute ids at the moment of allocation" is a read-then-write race

**BEN-159.** Lane C (PET). Found while landing R2, by a column-count check that was looking for
something else.

**One-line version:** two lanes allocated **`OI-64` and `OI-65`** within hours, both correctly
following the instruction to recompute ids at allocation time — because that instruction describes a
**read-then-write with no lock**, and concurrent lanes race it.

## The collision

| id | lane A's | lane C's |
|---|---|---|
| `OI-64` | `verify_hash_bindings.py` guards nothing (gate enforcement) | the deployment-parity check that has no caller |
| `OI-65` | receipt-retirement exposure, measured zero instances | the `reconcile_gate5_family.py` audit repair |

**This is exactly the shape `CLAUDE.md` already names as the dangerous one.** *"OI-65 landed"* is true
of C's (R1+R2 in) and false of A's. Read at face value it supports a claim that is not the case — and
`OI-65` is the row that currently says **promotion is blocked**, so the misreading runs in the
unsafe direction.

`CLAUDE.md`'s existing rule closes the *intra-document* namespace (`PB1`, not `B1`) and explicitly
says it *"does not cover `BEN-*` ids, which have per-lane ranges that were violated anyway and caught
by attention rather than by mechanism."* **`OI-*` has neither a per-lane range nor a lock**, so it is
the weaker of the two namespaces, and this is its first measured collision.

## Why it was found late, and by accident

Nothing checks it. I found it because a script asserted the OI table's **column count** after
inserting a row, printed every `OI-6x`, and the ids appeared **twice each**. Had I not printed them
for an unrelated reason, both rows would have sat there indefinitely — the file renders fine, the
table is well-formed, and each row is individually correct.

The same script's assertion then tripped on `OI-62` having ten fields, which turned out to be
**pre-existing at `HEAD`** and not mine. Worth recording as its own small lesson: a check added for
one purpose surfaced two unrelated defects, and the second needed attributing before it could be
reported.

## What was and was not done

**No id was renumbered.** Both sides are cited in commits that are already pushed and therefore
immutable — A's in `5ad5ac7`, C's in `6bec322`, `eedcfc9` and the R2 commit — so renumbering either
side leaves some commit message pointing at an id that now means something else. That is a
coordination decision with two owners, not a unilateral edit, and **editing another lane's rows to
free up my number would be the same overreach in the other direction.**

**What was closed immediately is the misreading window.** All four rows now carry a banner naming
both claimants and pointing at the other row, so an unqualified *"OI-65"* cannot be taken at face
value; the convention is to write *"A's OI-65"* or *"C's OI-65"* until the mediator decides. Cheap,
additive, and it does not depend on anyone acting.

## The habit, and the mechanism that would replace it

> **An id namespace shared by concurrent writers needs a range or a lock, not an instruction to
> "recompute at the moment of allocation."** That phrasing sounds like diligence and is in fact a
> description of the race.

`BEN-*` at least has per-lane ranges — this lane's is `130-159`, and **`BEN-159` is its last**, which
is its own signal: the ranges are sized for a slower day than this one. `OI-*` has nothing. The cheap
executable fix is the same shape as every other one today: a pre-commit check that fails when any
`OI-\d+` or `BEN-\d+` id appears twice as a row id in its home document. That costs nothing per
session and cannot be skipped, whereas this finding costs tokens forever and was only read after the
collision.

## Related

- `CLAUDE.md`'s item-id rule — closes the intra-document namespace, explicitly not `BEN-*`, and not
  `OI-*` at all.
- `BEN-080`, `BEN-082` — the prior instances, caught by attention.
- `BEN-157` — the audit whose repair was landing when this surfaced.
