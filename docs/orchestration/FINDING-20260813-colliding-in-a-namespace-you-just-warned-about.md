# FINDING 2026-08-13 — colliding in the namespace you filed the warning about, the same day

**`BEN-223`.** Lane A. Found on a rebase conflict, which is the only reason it was found at all.

## The sequence, and the timing is the finding

| when | what |
|---|---|
| 2026-08-13, morning | **Lane A files `OI-62(b)`**: `OI-*` ids have **no block table and no addressing convention**, unlike `BEN-*`. Routed to Joseph, `WAITING-USER`. |
| same day | **Lane A allocates `OI-64` and `OI-65`** by `max(existing)+1`. |
| same day | **Lane C allocates `OI-64` and `OI-65`** by `max(existing)+1`. |
| on rebase | Four rows, two ids. |

**A wrote the warning and then walked into it.** Not from having forgotten it — from having no mechanism,
which is precisely what the warning said.

## Why no existing guard fires

- **`BEN-*` has a block table**; `OI-*` has nothing. `max(existing)+1` is the only available algorithm, and
  it is deterministic — **two lanes running it concurrently collide by construction**, not by carelessness.
- **`BEN-214`'s check cannot reach it.** That check is *"read the row's `BEN-*` id against the block
  table"* — it takes an id and consults a table. For `OI-*` there is no table, so the check has no input.
  Lane A recorded that gap this morning as a defect in the instrument; **this is the gap being exercised.**
- **`BEN-080`** is the id-collision finding (`BEN-041`/`BEN-044` between concurrent lanes, then Packet B's
  `B1` landing on CLM-010's `B1`). `CLAUDE.md` carries its rule — *"item ids inside a document are prefixed
  with that document's short name"* — and explicitly says it **does not cover `BEN-*`**, whose exposure is
  *"known and accepted, not fixed."* `OI-*` is not mentioned at all. **Three id collisions in one namespace
  family in four days, and the newest one is in the namespace nobody wrote a rule for.**

## How it was resolved, and the second decision is the one worth copying

**Annotation, not renumbering.** Both rows now lead with `⚠ ID COLLISION — this is LANE A's / LANE C's
OI-64`, each naming the other's subject. Renumbering would rewrite another lane's row, which
`CONVENTION-lane-worktrees.md` reserves to that row's author; and a renumber breaks every inbound reference
already written elsewhere, silently.

**Then the part that required actually applying the finding.** Lane A had two follow-on items ready — the
floor-catches-collapse gap and the `_LAUNCH_CODE_FLOOR` zero margin — and the obvious move was `OI-66` and
`OI-67`.

**They were folded into A's existing `OI-64` row as sub-parts `(f)` and `(g)` instead.** Allocating two more
bare `max+1` numbers, hours after measuring that the namespace is unguarded, into a row that is *itself half
of a collision*, would be knowingly repeating the mechanism. The items are genuine follow-ons of `OI-64`'s
resolution, so a sub-part is the honest home anyway — but the reason for choosing it was collision surface,
and that reason is recorded in the row.

## The generalisation

**Knowing a namespace is unguarded does not stop you colliding in it. Only a mechanism does.**

This is the same asymmetry `CLAUDE.md` states as a principle and this finding is a measurement of it:

> *"a document costs tokens in every future session forever; a check costs zero and cannot be skipped.
> **Prefer the executable form of any rule you are tempted to write down.**"*

`OI-62(b)` was written down. It was written by the party that then violated it, on the same day, and it
prevented nothing. **The interval between filing the warning and tripping it is the measurement**, and it is
hours.

## What would actually fix it

Not lane blocks — `OI-*` items are cross-lane by nature and a block table would mis-file half of them. The
cheap executable forms, in ascending cost:

1. **A pre-commit check that `OPEN_ITEMS.md` has no duplicate `OI-*` id.** Catches the collision at the
   second commit rather than at a rebase, costs nothing, and needs no convention decision from anyone. **It
   does not prevent the collision — it makes it loud immediately**, which is the whole difference between
   this being a rebase conflict and being a wrong cross-reference someone acts on.
2. Allocate from a single monotonic counter file rather than from `max(existing)`, so two concurrent readers
   cannot get the same answer.
3. Lane-prefixed ids (`OI-A64`), which is a convention change and therefore Joseph's — `OI-62(b)`.

**(1) is available today and blocked on nobody.** It is not built here because this session is not the
owner of `OPEN_ITEMS.md`'s tooling and `OI-62(b)` is in front of Joseph with the convention question; but the
check does not depend on how he answers, which is the argument for building it first.

## Related

`OI-62(b)` (the warning, filed by this lane, `WAITING-USER`), `BEN-080` (id collisions, and the rule that
excludes this namespace), `BEN-214` (the attribution check that cannot fire on an `OI-*` id),
`BEN-222` (found in the same rebase), `CONVENTION-lane-worktrees.md`.
