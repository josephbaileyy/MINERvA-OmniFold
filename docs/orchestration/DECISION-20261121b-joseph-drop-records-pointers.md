# DECISION 2026-11-21 (b) — Joseph: the note's pointers to the records document are dropped

**Recorded by** the limitation-resolver lane, for the director, who relayed Joseph's words.

## What led to it

- **The pointer rule.** [DECISION-20261120a](DECISION-20261120a-joseph-release-locks.md) item 5 let a qualifier's full
  statement move verbatim to the records document (main_records.tex, cited as NoteRecords2026) with a pointer printed
  in the note. limitations_export.py enforced it: a register row had "records" status only if its text was in the
  records and its `[pointer: …]` text printed in the note.
- **The journal-voice rewrite (2026-11-21).** The check stage added one records pointer per section in §2, §4 and App. A
  so that register rows moved to the records stayed located. Joseph's read of the restored sentences, relayed by the
  director, decided against note-to-records pointers.
- **The records reorganization.** Joseph wants the records document reorganized; its record cleaner will move blocks
  between records files, so a rule keyed to a records file name would break.

## Joseph's words, verbatim

As relayed by the director, 2026-11-21; the sha256 is of the text plus a final newline:

> yeah I think we should drop the records pointers

(`05fefb02e66121a2dc15827a016a21992eb5ce09c0d86a35b83f3e3bb4d12330`)

## What it decides

1. **No note-to-records pointers.** The posted note does not point readers to the records document for qualifications.
   The check-stage pointer sentences (§2, §4, App. A) are removed, and so are the remaining NoteRecords2026 citations
   in the note's body files (App. A's aggregation citation and fine-grid sentence, sec5_multidim, appC_supplementary).
   sec6_conclusions.tex's two pointers are removed by director-helper-3, whose check branch holds that file. App. A's
   fine-grid sentence now points to App. D's fine-grid table: the joint-test fine grid is the 14×16×7×7×6 analysis grid
   (the release audit's fine-to-J map has 65,856 = 14·16·7·7·6 columns).
2. **The register's records status (supersedes DECISION-20261120a item 5's pointer requirement).** A row has "records"
   status when its re-anchor quote, or its original quote, appears verbatim in any file of main_records.tex's input
   closure that the note does not also input. No printed note pointer is required, and the row's reanchor_file is
   informational, so records blocks may move between records files. limitations_export.py implements the rule and its
   self-test plants each case.
3. **The records pin.** check_note_records.py's pin no longer fails when the note cites NoteRecords2026 nowhere (the
   former Q3 "cites NoteRecords2026 nowhere" failure). The rest of the pin (Q1 the full-sha bib entry, Q2 ancestry, Q3
   the records files at the pin and any cited tags, Q4 cited headings) stays, as an internal check of the records build.
4. **Unchanged.** Each result keeps its headline limit in the note (DECISION-20261120a item 5's other clause); text
   moved out of the note that holds a register row, a disclosure or a post-hoc account still moves verbatim to the
   records, with a move-manifest row; the records document remains internal and is never posted.

## Scope

The posted note's body and appendices, limitations_export.py, check_note_records.py's pin. It does not change the
records document's content or the bibliography entry NoteRecords2026, which the records' own build still uses.
