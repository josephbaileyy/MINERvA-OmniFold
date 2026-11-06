# DECISION 2026-11-06 — Joseph: the four diagnoses, the recommended ones first; a JINST referee test; two corrections on main

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The second methods round** (#855, `state/2d-closeout/stageF/methods/secondary-results/referee-methods-round2-20261106/`)
scored the restructured draft 3.25 of 10, against 4.0 in round 1. Every read asked for diagnoses, not framing changes.
The director put three questions, with recommendations, through AskUserQuestion.

## Joseph's answers, verbatim

1. **Which diagnoses go ahead.** The options offered were:
   - IBU comparisons (recommended);
   - the coverage pre-check cause (recommended);
   - the rounding-instability fix;
   - the prior-convergence study.

   Joseph selected all four and added:

   > prioritize the recommended things and getting a solid publishable paper first

   sha256 of that added text plus a final newline begins `d7e48c6df122eccb`.
2. **The venue test.** Joseph chose "Yes, test JINST (Recommended)": four blind reads of the current draft under the
   same prompt, addressed to JINST.
3. **Corrections.** Joseph chose "Yes, fix now (Recommended)". The two factual problems in text on main get fixed now,
   each citing its record, with the diff shown to Joseph before merge.

## What is decided

1. **All four diagnoses go ahead, in priority order.**
   1. **The IBU comparisons.** Records on main (REF-G1 #821; REF-C2C1 #845) are brought into the methods draft. Their
      wording goes through a referee read, then to Joseph.
   2. **The coverage pre-check's cause.**
      - This is a diagnosis only: why the pseudo-experiments reproduce 0.70–2.30 times the drawn uncertainties, band by
        band.
      - It runs no coverage test and redesigns nothing in 1B. Rule (iii) still governs any 1B rerun.
        <!-- absence-ok: a scope limit on the authorized work, not a claim that a result does not exist -->
      - It is declared, priced and bound before it runs, and its result is a finding.
   3. **The rounding-instability fix.** First the spread is measured on the sixteen reported cells. Then an
      ensemble-averaged estimator is declared as a variant. It is declared, audited and bound before it runs.
   4. **The prior-convergence study.** Two or three priors on the same pseudo-data, with an iteration scan at the
      sixteen-cell level. It is declared, priced and bound.

   Items 3 and 4 follow items 1 and 2. "A solid publishable paper first" means the draft does not wait on items 3 and 4.
2. **The JINST test** uses the round-1 prompt with only the journal name and its standard changed, on the current
   draft (`0de103f7`). It costs no compute.
3. **The corrections:**
   - "No single pT or p∥ band carries more than 15%" of the 2D χ²: the receipt gives 15.2% (pT bin 12).
   - The note's "a staged coverage test is under way": it ended on 11-06 (#832).

## Not decided here

- Any wording in the methods draft.
- Any venue choice.
- Any submission or deposit.
- An override of 1B's rule (iii).

Nothing is submitted, deposited or tagged.
