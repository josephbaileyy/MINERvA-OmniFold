# FINDING 2026-08-13 — a citation that was correct when written and wrong when read

**`BEN-219`.** Lane A (E_avail). Found while source-checking `docs/EAVAIL_DEFINITION.md`: every ratio in it
re-derived exactly, and the one thing that did not resolve was a line number.

## The measurement

`docs/EAVAIL_DEFINITION.md:82` cites the adopted covariance denominator as:

> *"(13.69% median per-bin, `VALIDATION_LEDGER.md:1043`)"*

| when | where `13.69%` actually is |
|---|---|
| `f4a2e52`, 2026-08-13 **02:34Z** (the commit that first wrote the citation) | **line 1043** — exact |
| `bcdb388`, 2026-08-13 **17:53Z** (~15 h later) | **line 1116** |

The figure moved **73 lines** because the Gate-5 campaign appended ledger entries *above* it. Verified by
`git show f4a2e52:VALIDATION_LEDGER.md | grep -n 13.69` → `1043`, against `grep -n 13.69
VALIDATION_LEDGER.md` at `HEAD` → `1116`.

**Nobody made an error.** The citation was checked, was right, and decayed.

## Four documents carry it

`grep -rn "VALIDATION_LEDGER.md:1043" docs/`:

- `docs/EAVAIL_DEFINITION.md:82` — **the document written for Gregor Kafka**
- `docs/OPEN_ITEMS.md:45` — the `OI-30` row, part `(d)`
- `docs/orchestration/ADVISORY-20260813-oi30-eavail-residuals.md:252` — as a range, `1043-1045`
- `docs/orchestration/PREDECLARATION-20260813-covariance-row-order-check.md:82`

Deliberately **not** repaired here. Three of the four are other parties' text and
`CONVENTION-lane-worktrees.md` gives only a row's author the right to reshape it; the repo's practice for a
foreign stale pointer is to report it rather than fix it silently (`BEN-204`). Reported to the document's
author in the same turn as this filing.

## Why this class is worse than an ordinary dead link

- **`VALIDATION_LEDGER.md` is the canonical home for every technote-quoted number** (`CLAUDE.md`'s routing
  table) **and it is written concurrently by every lane.** So the single file most often cited by line is
  also the file whose line numbers move fastest. The two properties are the same property.
- **It fails silently and in the worst direction.** A dead *path* errors when opened. A stale *line* opens
  successfully and shows plausible, wrong content. Measured: line 1043 at `HEAD` is the closing sentence of
  an artifact list inside `## 2026-07-14 corrected 5D GBDT covariance — **CANDIDATE**; final lateral
  replacement pending` (heading at line 823), two lines above
  `## 2026-07-14 recoil-PET 5D uncertainty campaign — **QUARANTINED**`. **The citation says "the adopted
  covariance" and now lands in a CANDIDATE entry that carries quarantine-inheritance language** — the one
  distinction the ledger exists to keep.
- **The reader most likely to check it is the external one.** An advisor handed a document with a precise
  `file:line` is being invited to verify, which is the point of the citation.

## Distinct from `BEN-216`, and it is the inverse

`BEN-216` was a line range on a file that **never existed** — the citation was false the moment it was
written, and `ls` catches it. This one was **true** when written. No check performed at write time can catch
it, which is why the remedy has to live at the read end or in the citation's form.

## The check

**Do not cite `VALIDATION_LEDGER.md` by line number.** Cite the entry by its heading (they are dated and
unique — e.g. *"the 2026-06-10 Ascencio bin-identical cross-check entry"*) or quote the number itself, both
of which are `grep`-able and survive insertion above them.

Where a line number is genuinely wanted, **pin it**: `VALIDATION_LEDGER.md:1043 @ f4a2e52` is checkable
forever, and a reader who finds it moved knows immediately that the pointer is stale rather than that the
number is wrong.

**General form:** a `file:line` citation into an actively-written file has a shelf life, and the shelf life
is shorter than the document that cites it. Prefer a content-addressed pointer to a position-addressed one —
the same reason this repo's hard rules prefer the executable form of a rule over the written one.

## Related

`BEN-216` (a pointer to nothing — the inverse mechanism), `BEN-201` (a retraction that landed in the index
but not at the point of use), `BEN-204`, `BEN-220` (found in the same source-check),
`CONVENTION-receipt-ingredients.md`, `OI-30(d)`.
