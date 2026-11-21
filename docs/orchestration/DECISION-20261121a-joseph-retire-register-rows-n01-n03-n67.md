# DECISION 2026-11-21 (a) — Joseph: limitations-register rows n01, n03 and n67 are retired

**Recorded by** director-helper-3, for the director, who forwarded the rewrite helper's relay of Joseph's decision.

## What led to it

1. **The check stage.** The journal-voice rewrite of the note (`rewrite/journal-voice-20261121`) reworded every sentence the limitations register quotes. In the check stage (`~/codex-reports/note-measurement/rewrite-20261121/CHECK-STAGE.md`, item 2), each register row is to be re-anchored to the note's own statement of the limit. Otherwise the row's original sentence moves verbatim to the records document, with a note pointer (DECISION-20261120a item 5). The gate is `docs/analysis-note/limitations_export.py --check` over `limitations-export.tsv`.
2. **Rows with neither home.** Three rows had no restatement in the rewritten note:
   - n01, at the time of the rewrite: "Whether it is ready for publication as a measurement has not been established". It was earlier the executive summary's sentence and then the introduction's (sec_intro.tex:11 at e89694209).
   - n03: "The results hold for one implementation of unbinned OmniFold, applied to one data set, and for the configurations, observables and deformations tested" (sec_intro.tex:68 at e89694209).
   - n67: "These are descriptive sensitivities, not alternative results" (sec_fived16.tex).
3. **What went to Joseph.**
   - director-helper-3's check report for the abstract and Secs. 1, 3 and 6 (`~/codex-reports/note-measurement/rewrite-20261121/check-h3-REPORT.md`, "Flags for the director" 1 and 2) put n01 and n03 to the director. It recommended retiring n01 and restoring n03 in Sec. 6.2.
   - The director sent both to Joseph through the rewrite helper.
   - n67 is journal-editor's row; the director forwarded it.

## The relay, verbatim

These are the rewrite helper's relays of Joseph's decision, as the director forwarded them on 2026-11-21. They are not Joseph's own typed words. Each sha256 is of the text plus a final newline.

1. n01 and n03:

   > - n01: RETIRE by Joseph's decision ("readiness for publication as a measurement has not been established" conflicts with the journal framing; text kept in the records).
   > - n03: RETIRE by Joseph's decision. He finds the one-implementation, one-data-set scope evident, and the note states its findings about the sixteen-cell estimator. The text is kept in the records.
   > Please record n01 and n03 as Joseph's register decisions (2026-11-21).

   (`f640495db4619585d538ede97e428dfb6edf4f96e85bea7b28ef5d2deb311eec`)

2. n67:

   > n67: RETIRE by Joseph's decision (2026-11-21). C.2's paragraph already calls the correlation change a sensitivity check, so "These are descriptive sensitivities, not alternative results" restates it. Do not add it.

   (`3be97bb7e031d52cc75c3460350942b641eb3e32b09570d339ec34277916cfef`)

## What is decided

1. **n01 is retired.** Its sentence conflicts with the journal framing, and the note does not state it. Its text stays in the records document (`records_compression_h3_rw.tex`, moved verbatim from e89694209). Its row is deleted from `limitations-export.tsv`.
2. **n03 is retired.** Joseph finds its scope evident, and the note states its findings about the sixteen-cell estimator. The note does not state the sentence. Its text stays in the records document (`records_compression_h3_rw.tex`). Its row is deleted from `limitations-export.tsv`.
3. **n67 is retired.** Its sentence is not added to the note. journal-editor deletes its row from `limitations-export.tsv` on journal-editor's branch, citing this record.
4. **The gate.** With the three rows deleted, `limitations_export.py --check` covers 90 note-anchored rows.
5. **The register artifact.** The rows n01, n03 and n67 of the claude.ai "OmniFold Limitations Register" are marked retired, citing this record.

## Not decided here

- Any other register row, or its re-anchor or records location.
- Any note or paper wording.
- Any value, claim or uncertainty.
- Whether the records document keeps n67's text.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - retiring register rows n01, n03 and n67;
  - deleting them from `limitations-export.tsv`;
  - a 90-row gate.
- **Not citable for:**
  - retiring any other row;
  - removing n01's or n03's text from the records document;
  - any note or paper wording;
  - any claim, value or uncertainty.

Nothing is submitted.
