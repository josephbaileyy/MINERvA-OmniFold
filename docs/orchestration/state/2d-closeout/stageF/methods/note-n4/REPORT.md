# Note round n4: report (in progress, 2026-10-28)

**Lane:** paper rewrite, for the director.

**Base:** origin/main `371cccec`. The branch is `note/n4-front-matter-20261028`.

**Under:** `outline.md`, as approved, with the director's rulings recorded at its end.

**Records** (this directory):
- `apply_n4.py`: every edit, by batch;
- `ledger.md`, checked by `check_ledger.py`;
- `agy/`: the batch reads;
- `release-claims.md`: the release appendix's claim table (pending).

This is the first round in which the structure is not on trial (ruling 3). Joseph decided the front matter's
structure, so the pairwise and P1N judge only its wording.

## Batch C: the interval-sense "calibration" sites and the main-result sentence

These are accuracy and consistency fixes, unscored, under rulings 2a and 2b. There are nine edits in six files.

| id | site | before | after |
|---|---|---|---|
| C1 | `sec_5d.tex` sec:val-departure | "a pooled calibration test of its statistical intervals" | "a pooled test of its statistical intervals" |
| C2 | same | "does not establish calibration for every functional" | "does not establish coverage and width for every functional" |
| C3 | `sec_5d.tex` sec:coverage-5d | "a pooled calibration pass" | "a pooled pass" |
| C4 | `sec_validation.tex` lead | "checks neither interval calibration nor" | "checks neither the coverage and width of the intervals nor" |
| C5 | `sec_pet_campaigns.tex` | "H2S1T24 fails interval calibration" | "H2S1T24 fails the frozen coverage rule" |
| C6 | same | "the measured PET procedure failed calibration" | "… failed the frozen coverage rule" |
| C7 | `app_statmethods_nd.tex` | "constructs calibrated intervals" | "constructs confidence intervals" (the cited paper's title) |
| M1 | `sec_execsummary.tex` | "The main results are the validation findings. They hold …" | "The principal result is the sixteen-cell cross section of §…, with its covariance and generator comparison. The results hold …" |
| M2 | `sec_summary.tex` | "The main results are the validation findings, within the scope …" | the same sentence, then "The results hold within the scope …" |

**Evidence:**
- **C1–C3:** the candidate's test is row A2 of `OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md`. It gives
  pooled pull SD 1.023, pooled coverage 0.680 / 0.942, a Mahalanobis distance, and "a pooled pass, not per-functional
  calibration".
- **C5–C6:** H2S1T24 is ineligible under the PET campaign's coverage rule, with C1 and C4 FAIL
  (`nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md:47`, `:49`). The rule is named "the coverage
  rule" there, not "calibration", so the sentences use that name.
- **M1–M2:** the sentence is the paper's printed Conclusions (`paper_body.tex:355`), retargeted. It agrees with the
  note abstract's first sentence.

**The six sites are all of them.** A sweep of every file `main_note.tex` inputs found each remaining "calibrat…"
sentence that mentions an interval, a pull, a width, a band or the bootstrap. All of them use the test sense:
- the joint tests' calibration;
- "classifier-calibration tests" (`sec_method.tex`);
- the extended-fiducial study's "calibration–evaluation split" and "a calibrated test" (`sec_fps.tex`);
- the ES's "the calibration and nuisance model of the generator tests".

**agy** (`agy/c` … `agy/c5`; pairs built by `agy/make_pairs_c.py` from `apply_n4.C` and the sources, nothing retyped):
- **The control** (one strengthening planted per pair) caught 9 of 9 in each of the five reads.
- **C5–C7** were SAME in the first read.
- **C1–C4 took three revisions.** agy's substantive points, each now met:
  - a pull width measures dispersion, not containment, so "coverage test" narrowed what was tested. C1 and C3 drop
    the adjective;
  - "coverage" alone narrows the interval sense of "calibration", which also covers width. C2 and C4 name coverage
    and width;
  - "coverage or width" reads as "neither". C2 says "and";
  - "failed its coverage test" split. C5 and C6 use the record's rule name.
- **The final read (`agy/c5`, two runs):**
  - run 1 is SAME on all of C1–C7;
  - run 2 is SAME on C5–C7. On C1–C4 its stated reasons are only that the word "calibration" was removed. Any
    terminology fix trips that when BEFORE is accepted as correct.
- **agy is noisy here:** the same C5 text was SAME in one read and DIFFERS in the next (`agy/c` Q5, `agy/c2` Q5). So
  the reads were stopped at that point, and the director decides.
- **M1 and M2 are DIFFERS in every read:** "AFTER drops BEFORE's statement that the main results are the validation
  findings". That is the change ruling 2a decided, so it stands.

**The primer (ruling 5) is not edited. It goes to the director:**
- `primer_body.tex:13` and `:57` say its main results are the tests of the method.
- The primer prints no sixteen-cell result: no sentence names it, and it predates the five-dimensional integration.
  It also says "the study does not deliver a validated five-quantity cross-section measurement".
- So "The principal result is the sixteen-cell cross section …", retargeted to the note, would announce a principal
  result the primer never describes.
- Making the primer consistent needs a paragraph on that result, which is a content addition beyond n4's scope.
- The primer is 15 pp before, and is unchanged.

**Checks:**
- `check_ledger.py .`: 9 rows, 15 probes, 10 changed base sentences, 0 failures.
- `--self-test`: PASS. Its plants:
  - a missing probe, a dropped sentence, a removed label, a false `R:` probe, an `R:` probe naming a note file;
  - an undeclared `app_release.tex` edit, and a declared but unpinned pair;
  - a frozen sentence edited, and the readiness sentence duplicated instead of moved: each caught;
  - a pinned pair and the declared verbatim move: each silent.
- `printed_diff`: exactly the 21 intended sentence lines.
- `reflow_tex.py --note --check`: PASS.
- `build_all.sh`: rc 0; note 130 pp, paper 11, primer 15; SEC4 15/15; no undefined reference.
