# DECISION 2026-11-21 (a) — Joseph: limitations-register rows n01, n03 and n67 are retired

**Recorded by** director-helper-3, for the director, who forwarded the rewrite helper's relay of Joseph's decision.

## What led to it

1. **The check stage.**
   - The journal-voice rewrite of the note (`rewrite/journal-voice-20261121`) reworded every sentence the limitations register quotes.
   - The check stage brief (`CHECK-STAGE.md`, item 2, in `~/codex-reports/note-measurement/rewrite-20261121/`) has each register row re-anchored to the note's own statement of the limit. Otherwise the row's original sentence moves verbatim to the records document, with a note pointer (DECISION-20261120a item 5).
   - The gate is `limitations_export.py --check`.
2. **n01 and n03.** The rewritten note states neither sentence:
   - n01: "Whether it is ready for publication as a measurement has not been established." Earlier the executive summary's sentence, then the introduction's (sec_intro.tex:11 at e89694209).
   - n03: "The results hold for one implementation of unbinned OmniFold, applied to one data set, and for the configurations, observables and deformations tested." (sec_intro.tex:68 at e89694209)

   director-helper-3's check report (`check-h3-REPORT.md`, same directory, "Flags for the director" 1 and 2) put both rows to the director. It recommended retiring n01 and restoring n03 in Sec. 6.2. The director wrote: "I've sent P2, P7, P10, P4–P9 and the n01/n03 calls to the rewrite helper for Joseph".
3. **n67.** n67 is journal-editor's row: "These are descriptive sensitivities, not alternative results." The director forwarded the rewrite helper's relay of Joseph's decision on it.

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

1. **n01 is retired.** Its sentence conflicts with the journal framing. Its text stays in the records document (`records_compression_h3_rw.tex`, moved verbatim from e89694209).
2. **n03 is retired.** Joseph finds the one-implementation, one-data-set scope evident, and the note states its findings about the sixteen-cell estimator. Its text stays in the records document (`records_compression_h3_rw.tex`).
3. **n67 is retired, and its sentence is not added to the note.** C.2's paragraph already calls the correlation change a sensitivity check, so the sentence restates it.
4. **The export rows.**
   - director-helper-3's check branch deletes the n01 and n03 rows from `limitations-export.tsv`, citing this record.
   - journal-editor deletes the n67 row on its own branch, citing this record.
   - With the three rows deleted, the gate `limitations_export.py --check` ends at 90 of 90.
5. **The register artifact.** The claude.ai register artifact's rows n01 and n03 are marked retired, citing this record.

## Not decided here

- Any other register row, or its re-anchor or records location.
- Any other note or paper wording.
- Any value, claim or uncertainty.
- Whether the records document keeps n67's text.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - retiring register rows n01, n03 and n67;
  - keeping n01's and n03's text in the records document;
  - leaving n67's sentence out of the note;
  - deleting n01 and n03 from `limitations-export.tsv` on director-helper-3's check branch, and n67 on journal-editor's branch;
  - a gate of 90 of 90.
- **Not citable for:**
  - retiring any other row;
  - removing n01's or n03's text from the records document;
  - any other note or paper wording;
  - any claim, value or uncertainty.

Nothing is submitted.
