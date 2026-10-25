# DECISION 2026-10-25 — Joseph: r18 moves the paper's history passages to the note and addresses every passage the raters quoted

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- At the r17 baseline, every sol2 rating run quoted the same passages of the methods paper (P1 3.0, 3 of 3 runs). The
  rater files are in the paper rewrite lane's `xmodel/r17base/p1/`. The passages are:
  1. the earlier-band paragraph of Sec. IV B: an earlier statistical band failed a fixed-truth coverage test, and a
     rebuilt band was rescored post hoc;
  2. the calibration budget extension and the lost pseudo-experiments of Sec. VII C;
  3. the seed sentence of the Fig. 3 caption;
  4. the data-availability package text;
  5. repeated scope qualifications.
- The director proposed that r18 move passages 1 and 2 to the note and leave a pointer in the paper, under
  `DECISION-20261021-joseph-register-loop-2.md` item 4.
- **Two of the director's protections block passage 1 as written:**
  - `check_sec4_receipts.py` binds its values to `paper_body.tex`;
  - Table I's 2D-covariance row reads "an earlier band failed coverage".
- **Passage 2's disclosure** comes from `DECISION-20261004-s5p-production-budget-extension.md` §3.

Joseph's answer, verbatim:

> yes r18 can do the move. why do we need to include that earlier band paragraph? I thought the internal ledger was the only place we put historical things. Or is it necessary in order to present the truth? same with the pseudo-experiment? how do PRD papers usually present these caveats and how is it different than ours? I think we should try and address all of passages that they quoted

sha256 of the text plus a final newline begins `980d267e9b77292a`.

## What is decided

1. **r18 may move the earlier-band history out of the paper.**
   - **Why the paper does not need it.** Both bands it describes are superseded. The note says the quoted statistical
     block is "a third ensemble" that "has not been tested" (`sec_execsummary.tex:119`; `sec_validation.tex:270-280`).
     The paper already states that fact as limitation 1 of Sec. VIII A. The history adds nothing true about the quoted
     result.
     <!-- absence-ok: quotes the note's own statement (sec_execsummary.tex:119) and paper Sec. VIII A limitation 1; no new absence claim -->
   - **Where it stays.** The history remains printed in the note, at `sec:coverage`. The full trail is in the internal
     records.
   - **What r18 may change:**
     - the Table I cell, to a statement about the quoted block (for example, "coverage not tested");
     - `check_sec4_receipts.py`, repointed to where the two rescoring values print in the note, or retired for them if
       the paper no longer prints them. The change is recorded, and the check's self-test must still pass.
2. **The budget extension and the lost pseudo-experiments keep one short statement each in the paper.** They bear on
   the validity of the joint tests' error control, a result the paper reports:
   - the budget was extended after the observed p values were visible;
   - the error control holds under A1 and A2 for any stopping rule;
   - 224 calibration and 53 power pseudo-experiments did not complete;
   - the A2 clause the director approved for r17: losses independent of their outcomes, which has not been shown,
     although none reaches the observed statistic when rerun.

   The mechanics and history (timeouts, motivation, the transition) move to the note if they are not already there.
3. **Every quoted passage is addressed.**
   - **Fig. 3:** one plain sentence saying that neither seed set was held out from the estimator's development.
   - **Scope:** stated once (R1), with no repeated disclaimers.
   - **Data availability:** that text is Joseph's. r18 proposes wording for Joseph and does not change it.
4. **The standard is unchanged.**
   - No number or claim changes, and no fact leaves both documents.
   - A qualifier stays where leaving it out would make a printed sentence false as read.
   - agy agrees on every printed passage.
   - The blind pairwise comparison and P1 decide adoption.

## Not changed

- Claims, KI-85, `\pubhold` and release text are Joseph's. Nothing is submitted, deposited or tagged.
- r17 is scored and adopted on its own before r18 starts.
