# r22 Step 3: proposed abstract pair (main_note.tex), from writer B01

Not applied. main_note.tex is unchanged. The director pins this pair (step3/check_ledger.py `ABSTRACT` / `ABSTRACT_PINS`) and passes it to Joseph before adoption.

At writing, `before` is the exact current source text of the abstract's last two sentences (main_note.tex line 72 at base 14a0415f) and occurs once in the file. `after` keeps every fact, macro and number and the exact wording of each clause. It only reorders them: the two test results come first, and the coverage limitation closes the abstract as its own sentence. The abstract already leads with the measurement (Step 2 pair B01-s-04), so no earlier sentence moves. `pin` is sha256(before + NUL + after)[:16], as check_ledger.py's pin() computes it, for the director to verify, not to copy.

## B01-g-07 (ALLOW-NARROW, A4)

Narrowed form: reorder the abstract while retaining the explicit coverage limitation and the distinction between the held-out bias test and interval-width validation. Retained: "The coverage of the result's intervals has not been validated" (verbatim, now a standalone sentence) and "but does not test interval widths" (verbatim, still attached to the bias test). Not made: the rater's request to state the limits as bounded uncertainties.
<!-- absence-ok: quotes printed note sentences, the raters' flags or the reviewers' findings; not a claim that something has not been run -->

before:

```latex
The coverage of the result's intervals has not been validated; a bias test at two held-out GENIE~v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt.
```
<!-- absence-ok: quotes printed note sentences, the raters' flags or the reviewers' findings; not a claim that something has not been run -->

after:

```latex
A bias test at two held-out GENIE~v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt. The coverage of the result's intervals has not been validated.
```
<!-- absence-ok: quotes printed note sentences, the raters' flags or the reviewers' findings; not a claim that something has not been run -->

pin: `6f0fb222b469a666`; words 57 -> 57
