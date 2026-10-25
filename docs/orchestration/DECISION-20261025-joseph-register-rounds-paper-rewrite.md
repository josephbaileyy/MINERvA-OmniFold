# DECISION 2026-10-25 — Joseph: more model-scored register rounds on the paper and the note, by a new paper rewrite lane

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The paper's last register round, r16 (`state/2d-closeout/stageF/methods/r16/REPORT.md`), won its blind pairwise
  comparison 4 of 4. Its P1 score stayed at 3.0.
- The director's reading then was that further rounds would pay little until RE-2 landed. RE-2 has since been integrated
  (PR #343).
- Model-scored rounds on the note stopped under `DECISION-20261022-joseph-note-records-refs-and-stop.md` item 2.
- Joseph opened a new session, "paper rewrite", and told it to take instructions from the director.

Joseph's words, verbatim:

> what do you think about having the fresh session I made called paper rewrite do another few rounds of restructuring and reordering/rewriting paragraphs of the note and paper in order to get a high score from independent agents on if it reads like a PRD publication

sha256 of the text plus a final newline begins `f097a592ec22a321`.

> if you agree can you give it the correct instructions? I told it to listen to you

sha256 of the text plus a final newline begins `b892bfd9ee9a0ffe`.

The director agreed and gave the work order.

## What is decided

1. **Model-scored register rounds reopen, for the paper and then the note.**
   - The note part amends `DECISION-20261022-joseph-note-records-refs-and-stop.md` item 2.
   - The rounds may restructure, reorder and rewrite paragraphs.
   - The paper rewrite lane runs them and takes instructions from the director.
2. **The method is the recorded one, unchanged:**
   - `state/2d-closeout/stageF/methods/register-method/HANDOFF.md`;
   - the calibration in `rater-calibration/REPORT.md` §§4–5;
   - rules R1–R10 and the KEEP list in `register-prd-study/REPORT.md`;
   - `DECISION-20261021-joseph-register-loop-2.md` items 3–4;
   - the paper standard of `DECISION-20261023-joseph-5d-a-and-register-round.md` item 2.

   **Each round:**
   - a baseline;
   - an outline approved by the director before any writing;
   - an independent two-direction review, with agy agreeing on every printed passage;
   - a ledger check;
   - a blind pairwise comparison against the previous version, and P1.

   **A round is adopted** if it wins at least 3 of 4 pairwise runs, sol2 shows no order flip, and P1 does not fall.
3. **Stopping.** Stop when either of these comes first:
   - the pairwise comparison no longer prefers the new version in both models;
   - P1 with sol2 reaches at least 3.5 on 3 of 3 runs, the calibrated level of published anchors.

   **There is also a cap of 4 rounds per document**, after which the lane reports to the director. The human read by
   Joseph and Ben follows.
4. **Presentation and language only.** No number, claim, scope, citation or figure meaning changes, and no fact leaves
   both documents.
   - Protected text stays as it is: holds, the KEEP list, gate-bound text, authors, acknowledgments, funding and
     release text.
   - The 5D sections may be reordered and their language fixed. The S1 covariance and the fake-data plan are not
     integrated.
5. **Process.**
   - Each round is a PR to the director, who merges it.
   - Nothing goes to the standalone note repository or Overleaf except through the director.
   - Nobody is contacted.

## Not changed

- **Claims, KI-85, `\pubhold` and release text** are Joseph's. Nothing is submitted, deposited or tagged.
- **Publication** needs Joseph's and Ben's review and MINERvA collaboration review, which is Joseph's act.
