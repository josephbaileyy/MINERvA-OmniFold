# The Supplement navigation batch (2026-11-17): meaning reads

**Asked by** the director, relaying Joseph 2026-11-16 (the readability report r3 on the Supplement). Applied by
journal-editor on `style/supp-20261112`, on top of director-helper-3's readability batch (`0cb2bf172`).

**What changed** (`supplemental_body.tex`, `main_supplement.tex`):
1. a road-map paragraph at the opening;
2. a one-page definitions and conventions table after it, unnumbered and not a float, so that no Supplement table or
   section number moves;
3. redirects where the Supplement sent the reader to the note to understand a conclusion; S8.7 gains a compact
   specification of the joint tests from the note's section 11 at its release pin `8342963c1`;
4. repeated accounts reduced to one, with pointers;
5. table-layout fixes, with values unchanged;
6. S8.5 gains the GEANT4 bound sentence moved from the paper, in Joseph's A6 wording
   (`DECISION-20261116-joseph-paper-batch.md` item 3), verbatim, in the graded arm;
7. S8.6 reordered: the preliminary check stopped the first test, and the staged redesign followed and stopped at its own
   first stage (the director, on director-helper-3's meaning read). The order was checked against
   `FD-1B-STAGE2-REPORT.md` and `FD-1B-DIAG-REPORT.md` (2026-11-01), the two 2026-11-01 decisions,
   `OUTCOME-20261106-1b-stage1-receipt-stop.md` and `OUTCOME-20261108-1b-precheck-part1.md`.

Not done, for the follow-up list:
- r3's table S11 restructure;
- the S13 caption: #981's codemap row 23 follows its text, and its runner options are cut at the freeze;
- the codemap table, also cut at the freeze;
- the S2 and S5 table layouts;
- the S15 and S16 float placement.

**The reads** use gpt-6.1-sol at high effort, read-only, each with its prompt and its answer verbatim.

| read | what it read | verdict |
|---|---|---|
| `read1/` | the whole batch at `697699e0d` against the paper, the note's sections 8 and 11 and the records | FAIL, three defects: C_resp's definition, S8.7's missing claim variants, two definition pointers |
| `read2/` | the batch with the three fixes at `a891330bd` | PASS |
| `read3/` | the gate fixes at `ec15bcdd5`: S8.7 in shorter sentences, the 1.4 % dropped (still printed in S5.2 and S7), and the paragraph splits | PASS |

**CITABLE FOR:** the batch's wording as read against its cited sources.
**NOT CITABLE FOR:** any result; a locked wording.
