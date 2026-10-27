# DECISION 2026-10-27 — Joseph: print MP-5's measured pT-convention effect, and correct the App. history sentence in place

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The paper rewrite lane audited the 21 grandfathered bare absence claims the TeX reflow surfaced
  (`state/2d-closeout/stageF/methods/tex-reflow-20261026/REPORT.md` §4). Two of them could only be fixed by printing a
  fact the note did not yet carry, so the director put both to Joseph.
- **Item 3, `sec_eavailw.tex:57`:** "the net effect of this difference on the cell contents has not been measured". MP-5
  (`state/measurement-paper/phase1/mp5/REPORT.md`, job 60017887, 2026-10-20) measured it:
  - for the analysis simulation, R_c over the 109 cells is 0.99649 / 1.000008 / 1.00346 (min / median / max), at its
    Monte Carlo floor;
  - for GENIE CV, Δ/σ_c is −0.47 / 0.00 / +0.53;
  - the proxy is unreliable for GENIE MEC, NuWro and GiBUU.
- **Item 4, `app_history.tex:252`:** "No positive-semidefiniteness measurement exists for either". The production status
  log records that both constructions passed the adoption step's eigenvalue test on 2026-07-14
  (`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:735, 740-741`; `nd-unfolding/adopt_unified_5d.py:149-165`).
  - Its clause "so no substitution is available" is true only as "none has been adopted": J28 background-aware
    candidates VL16 and VL17 exist (`VALIDATION_LEDGER.md:464, 478-479`).
  - The paragraph is a frozen record paragraph (`check_note_records.py` P5). The director proposed an erratum paragraph
    after it.
<!-- absence-ok: quotes two sentences of the note as audited (sec_eavailw.tex:57, app_history.tex:252) and the records that refute them; no new absence claim -->

Joseph's answers, verbatim. For item 3, the option he selected:

> (A) With the numbers (Recommended)

sha256 of the text plus a final newline begins `1cb66f630b7b6e56`.

For item 4:

> I thought we are not listing things like corrections in the note, which is only for the internal ledger. I thought the note should just have the latest updated records

sha256 of the text plus a final newline begins `ed554ab4f0f7b439`.

## What is decided

1. **Item 3: draft (A) prints.**
   - It states, at `sec_eavailw.tex:57`, the analysis simulation's cell ratios (0.9965–1.0035, median 1.000008) at its
     Monte Carlo precision, and GENIE CV's −0.47 to +0.53 of each cell's null spread.
   - It says the effect is not reliably determined for GENIE with MEC, NuWro and GiBUU.
   - It cites a new App. G records entry for MP-5. That is records text, with the pin moved under the n2 rulings.
   - agy agrees on the sentence.
2. **Item 4: the note states the current fact, with no correction notice.**
   - The erratum paragraph is not printed. A correction's history belongs to the internal ledger, as the caveat
     convention already says for superseded work (`DECISION-20261025-joseph-prd-caveat-convention.md` item 3, kind (a)).
   - `app_history.tex:252` is corrected in place. It says that both constructions passed the build's
     positive-semidefiniteness check, and that background-aware-footed candidates exist but none has been adopted. The
     wording follows the paragraph and agy agrees.
   - The paragraph is frozen by P5, whose only escape (R-EDIT) allows pointer tokens.
     - So `check_note_records.py` gains a second ledger row kind, R-FIX: an edit beyond pointer tokens, accepted only
       with the old digest, the new digest, a reason and a decision record as its authority.
     - It has planted-defect self-tests: an R-FIX with no decision record fails, as does one naming a missing decision
       record, one with a wrong digest, and a lost paragraph. A recorded R-FIX stays silent.
   - **The internal records carry the history:** the R-FIX row, the old and new text by digest, and a FIX record that
     quotes the evidence.
3. **The same rule holds for the rest of the note.** A false sentence is corrected in place to the current fact. What
   it used to say goes to the internal ledger, not into the note.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
