# In a column headed `lane/owner`, the word "owner" almost always marks the ABSENCE of one

**BEN-442.** Filed 2026-08-18 by the seconding lane (block `440-449`). Extends `BEN-395`, which
found that 65 of 93 `OI-*` rows fill `lane/owner` with an **area**. This is what happened when
someone tried to discharge that backlog by reading the rows.

## The expectation, and why it was wrong

The plan was mechanical: most rows must already name a responsible party somewhere in their body, so
lift it into the column and cite the sentence. **That yielded exactly ONE row out of 62.**

`OI-47`'s state cell reads *"OPEN (re-scoped 2026-08-12, **owner Session A**)"*. Every other
occurrence of the word failed to name anybody, and they failed in two distinguishable ways.

## Failure mode 1 — the word "owner" is used to say ownership is UNASSIGNED

Measured, quoting the rows:

| row | its own words |
|---|---|
| `OI-22` | *"Scoped work with **an owner to assign** — no longer an adjudication."* |
| `OI-41` | *"Proposed disposition, **whichever the owner prefers**"*; *"is the **owner's call**"* |
| `OI-60` | *"Whether a Gate-2 re-run is worth closing a narrow residual is **an owner's call and is NOT taken here**."* |
| `OI-70` | *"left for **whoever owns** that file"* |
| `OI-73` | *"the blockers array becomes **editable-by-whoever-owns-it**"* |
| `OI-64` (lane C's) | *"and **nobody owns** re-deploying those"*; *"**Decide separately who owns** parity for peer-owned scratch copies"* |

**The document knows these are unowned and says so in prose, while the column says something that
reads as owned.** The information a dispatcher needs is present and is in the wrong field —
and the field it is missing from is the one a dispatcher reads.

## Failure mode 2 — the cell names a ROLE, which asserts a holder exists

Four cells were, verbatim: `cluster freeze owner`, `event-loop owner`, `PET input owner`,
`PET / cause 5 owner`.

**In a column headed `lane/owner`, "cluster freeze owner" reads as *the person who owns the cluster
freeze, whoever that is*.** It is a **definite description with no referent** — `BEN-380`'s species
applied to people rather than artifacts — and it is **the most misleading of the three unroutable
shapes**, because a bare area (`storage`) at least looks like an area, whereas a role-name looks
like an answer that the reader merely has not resolved yet. Nobody holds these roles. They were
never assigned.

## The near-miss this created, and it is the reason for the row

Six rows record who **raised**, **filed**, **found**, or **closed** the item — `OI-59` *"raised by
lane A"*, `OI-93`/`OI-94` *"raised by lane C"*, `OI-82` *"found by lane B"*, `OI-23` *"discharged by
lane A"*, `OI-65` *"raised by lane A"*. **Lifting any of those into the column would have
manufactured ownership that does not exist**, and it would have looked authoritative — a lane name
in a `lane/owner` cell, with a citation.

**The repo already warns about exactly this, in a row I had read:** `OI-71` says *"the id is in lane
A's block because lane A **FILED** it, **not** because lane A owns the subject … Lane A has not
answered it and **must not**."*

**A raiser is not an owner, and the grammar hides it**: *"raised by lane C"* and *"owned by lane C"*
are one word apart and sit in the same sentence position. **The mechanical repair I set out to
perform would have been wrong in six rows and unfalsifiable afterwards** — once `lane C` is in the
owner column with a quote behind it, nothing in the table records that it was an inference.

## What was actually done — 62 → 40, all of it quoting the rows' own words

Nine cells repaired, **each replacement quoting the row it edits, and nothing assigned to anybody**:

- `OI-47` → **Session A**, lifted from its own state cell. The only genuine lift.
- `OI-3`, `OI-10`, `OI-19`, `OI-42` → `UNOWNED — names a ROLE, not a holder`, area preserved.
- `OI-22`, `OI-41`, `OI-60` → `UNOWNED`, quoting each row's own sentence saying so.
- `OI-80` → routable via `OI-122`, whose own text reads *"`OI-122` OWNS THIS ITEM"*.
- `OI-121`, `OI-128` → clarified; **`OI-128`'s cell held a NEXT ACTION, not an owner**, which in this
  column reads as ownership. **The displaced sentence is preserved verbatim in the cell rather than
  deleted** — it is somebody's content and this lane does not own it.

`oi_owner_report.py` gained two buckets and 10 tests. **`terminal-no-owner-needed` (12 rows)** is the
honest correction to my own earlier number: a `DISCHARGED`/`SUPERSEDED`/`WITHDRAWN` row **needs no
owner**, so counting it as an ownership defect overstated the backlog. It reads the **state cell's
opening**, anchored — nearly every long row contains the word *closed* somewhere in its history, and
an unanchored match would have retired live rows.

**93 rows: 28 routable, 12 explicitly unowned, 12 terminal, 40 needing a decision.**

## What is NOT done, and it is not a sweep

**The 40 cannot be discharged by reading — there is no owner recorded anywhere to find.** Assigning
one is a decision, and it is Joseph's or the mediator's. The list is
`python3 docs/orchestration/oi_owner_report.py --list-area-only`, and it groups into **38 distinct
area strings**, i.e. it is very nearly one decision per row rather than a few bulk assignments.

**Three of the 40 are `⚠ ID COLLISION` rows** (`OI-64` ×2, `OI-65`) whose state cells name a lane —
*"this is LANE A's `OI-64`"* — **which is whose ID it is, not whose item it is.** Third variant of
the same conflation in one document; left alone deliberately.

## The rule

> **A cell in an owner column must name a party who can be messaged, or say `unowned`. A role, an
> area, an action, or the name of whoever raised it are all failures, and the last two are worse
> than an empty cell because they read as answers.**

Empty would at least be honest. `BEN-395` said a populated area cell reads as ownership; this says
the three most natural things to populate it with are all attributions of something other than
ownership, and that the repair anyone would attempt first — lift the lane name out of the body —
makes it worse in exactly the rows that look easiest.

## Cross-references

- `BEN-395` — the parent finding: an area in a `lane/owner` column reads as ownership.
- `BEN-380` — a definite description is not a citation. `cluster freeze owner` is that, for a person.
- `BEN-080` — two meanings for one id. The three `⚠ ID COLLISION` rows are its live remainder.
- `OI-71` — states the raiser/owner distinction explicitly, and is the reason it was checked.
