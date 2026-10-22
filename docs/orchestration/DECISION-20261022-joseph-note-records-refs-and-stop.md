# DECISION 2026-10-22 (second) — Joseph: thin the note's records citations; stop model-scored note rounds

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The note's register pass is finished: batches 0 and b3–b8 and bhi are merged, and the records
move is done. A re-rating of the posted note (`xmodel/note-cal2/`, P1N with sol2 and Gemini) found:
- **Scores.** The whole note moved from 2.83 to 3.04 with sol; the published long-paper anchors score 3.875.
  - The body moved +0.10, within noise after the drift control.
  - Most of the gain is from the records move.
  - sol gave 3.0 in 24 of 28 runs, so the prompt no longer resolves versions.
- **Records citations.** The posted note cites the internal records document (`NoteRecords2026`, printed "Ref. [38]")
  70 times. 31 of the 126 rated quotes contain one, so the raters read them as bookkeeping.

The director put two questions; Joseph's answers are below, and the option text is the director's.

> Records refs: "Thin to essentials (Recommended)" — say once, in the appendix guide, that provenance and superseded
> values are kept in the analysis repository; keep a citation only where a reader needs the record to check a specific
> number or claim (estimate 10–15); drop the rest, with a check that every dropped citation's tag still exists in the
> records document.
>
> Note next: "Stop; human read (Recommended)" — stop model-scored rounds on the note; Joseph and Ben read it next.

sha256 of the two answer lines plus a final newline begins `d0b85f02d47c649f`.

## What is decided

1. **Thin the posted note's records citations,** in one more reviewed batch:
   - one statement in the appendix guide;
   - a citation kept only where a reader needs the record to check a specific number or claim;
   - every dropped citation's tag checked to exist in the records document, so no record becomes unreachable.

   The records-move probe is amended to accept a dropped pointer listed with its tag.
2. **Model-scored register rounds on the note stop after that batch.** The next step is Joseph's and Ben's read.
   The before/after pairwise comparison already running is reported for the record, and starts no further round.

## Not changed

- Claims and numbers.
- The records document itself.
- The paper. Its own loop stopped under DECISION-20261021-joseph-register-loop-2 item 5.
- No outward act.
