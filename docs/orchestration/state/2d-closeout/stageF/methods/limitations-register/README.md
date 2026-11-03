# The analysis note's limitations, for the limitations register (2026-11-02)

**Asked for by** the director, for Joseph's limitations register
(`DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md` item 4; page
https://claude.ai/artifact/JcNVgJ7vTz4WkZzbiAGXBu). This is the register's note phase: rows n01–n84, beside the
paper's q01–q44.

**Done by** the limitations-catalog session. The work was read-only on the note. No model was used beyond the caveat
coders of `../caveat-remeasure-20261102/`.

**CITABLE FOR:**
- where the note, as built from main `108040f8` (`main_note.tex` and its `\input` closure; not `app_history` or the
  records document), states each limitation;
- which register row each paper q-item duplicates.

**NOT CITABLE FOR:**
- any physics claim;
- a class or status as a decision. Every class and status is this lane's proposal, for the director and Joseph. Each
  route cites records, and each cited record is checked mechanically to exist. Only the routes' readings of those
  records are this lane's.

## What is in it

`limitations.json` holds one object per item, with the register's fields:
- `id`, `q`, `doc` ("note");
- `loc` (TeX `file:line` of the item's home statement);
- `section` (with the built note's section number);
- `quote` (the home statement, verbatim from the built note);
- `cls`: K (inherent), M (could move or merge), or R (resolvable with work);
- `status`: closed, fix decided, in progress, open, or inherent;
- `route` (to closure, citing records);
- `line`, and `order` (101 onward, in note order).

`limitations-detail.json` gives, for each item:
- every location where the note states it;
- its issue labels;
- any statement the locator matched only partly.

It also records the population counts and the history and process labels that were left out.

**The count.** There are 84 items, from 842 coded statements.
- **By class:** K 54, R 25, M 5.
- **By status:** inherent 54, open 24, fix decided 4, in progress 2.
- **Duplicates of paper items:** 41 items carry the paper q-id they duplicate. Some q-ids map to more than one
  note item, because the note states their parts separately. For example, q02 is both n17 (coverage of the 2D
  statistical block) and n23 (independent validation).

**Under a decided or running campaign** (DECISION-20261102 item 3):
- n22: coverage of the sixteen-cell intervals. The 1B stage-1 redesign is in progress.
- n17 and n23: coverage and independent validation of the 2D covariance. The 2D method-coverage campaign is decided.
- n20 and n21: the run-period cause and the block's size. The run-period diagnosis is in progress and decided,
  respectively.
- n48: the CH correction. It is adopted for the paper.

**R items with no declared campaign** (the open work list):
- **Construction:** n07 seed ensemble; n10 the refinement classifier's residual bias (KNOWN_ISSUES 75); n11 a 3D or
  4D covariance; n16 why the statistical block is smaller than the published one; n18 learner dependence in the
  covariance; n61 the finite-ensemble correction.
- **Response:** n13 the detector-response mismatch test; n60 a wider C_resp; n75 a calorimetric band for the joint
  tests (s5p is terminal).
- **Generator samples:** n40 regenerate GENIE and NuWro with a correctly sampled flux (KNOWN_ISSUES 83); n46 the
  predictions' W and pT conventions; n49 a GiBUU sample above 20 GeV (KNOWN_ISSUES 82); n78 NEUT.
- **Other studies:** n43 a correlated Ascencio comparison; n45 a bias-variance study; n47 the information W adds;
  n58 a stability criterion for the cells (Joseph decides); n76 the extended-fiducial covariance and a
  refined-subtraction rerun.
- **Administrative:** n83 the deposit, which is Joseph's separate authorization.

**M items** (could move to the records document, or be merged into one statement):
- n01 the 2D result's publishability;
- n02 the different background treatments;
- n39 configuration (a)'s 3D closure scope;
- n54 the rounding instability;
- n81 the exact-split diagnostics.

## Method

1. **The population is a covering search, not a reading list.** It is every statement the caveat re-measure's
   coders put in kinds (b) deviation, (c) untested or omitted, or (d) scope: 797 statements under 331 issue labels.
   Coding was exhaustive, one coder per part, under the caveat study's codebook.
   <!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->
   - It also includes every (a) history or (e) process statement whose label states a limitation, because a coder's
     kind does not decide that. For example, the deposit status was coded (e). These add 45 statements.
   - 39 (a)/(e) statements under 28 labels are left out as history or process. They are listed in the detail file.
2. **Consolidation.** `items.tsv` maps each label to one item. `build_register.py` fails if:
   - a (b)/(c)/(d) label is unmapped, or mapped twice;
   - an item's home is not found in the TeX;
   - a class or status is outside the vocabulary;
   - a route cites a record (DECISION-, OUTCOME-, RECORD-, …, `*REPORT.md`, KNOWN_ISSUES row, VL, OI) that is not
     in the repository.
3. **The home** is the first located statement of the item's first-listed label, outside the abstract, the
   executive summary and the summary. The location comes from `locate.py`, which matches tokens against the
   comment-stripped TeX, the method of `note-consolidate/recount.py`. Records named in TeX comments near each
   statement were collected to seed the routes.

**Rebuild:**

    python3 -I build_register.py <docs/analysis-note> <built main_note.aux> <outdir>

The self-tests are `--self-test` on `build_register.py` and on `locate.py`.

## Limits

- **One coder per part.** A limitation the coder did not code is not in the population. The caveat study puts the
  coder spread at about ±25% in row count.
- **The consolidation into 84 items is a judgment.** The labels behind each item are in the detail file, so the
  director can split or merge.
- **Lines are TeX source lines.** Most note paragraphs are one line, so `loc` names a paragraph. The quote pins the
  sentence.
- **Coded on `108040f8`.** A note round moves lines, so rebuild after one. The build fails loudly if a home
  statement is gone.

## The paper rows re-located after #695 (2026-11-02)

`paper-rows.json` holds Q01–Q44 re-located in the paper at main `58fa0b89`. It has the register's shape (id, q, doc,
loc, section, quote, cls, status, route, line, order), plus `prints`.
- `loc` lists every line where the row's phrases print, home first.
- `section` uses the built paper's numbering.

`relocate_paper.py` builds the rows from `paper-rows.tsv`, which gives each row's literal phrases, the wording that
must no longer print, and the row's class, status, quote and route. The run fails if:
- a phrase prints nowhere;
- "gone" wording still prints;
- a route cites an absent record;
- a class or status is outside the vocabulary.

**Status changes against the register as loaded:**
- **Q26: fix decided → closed.** The quadrant sentence (#695) compares the sixteen-cell result with the 2D result.
  The clause that remains is narrower ("Of the joint-test estimator's other results, only the three-observable
  marginal has been compared …"), and it is now its own caveat.
- **Q14, Q19 and Q22: open → inherent.**
  - Q14: #695 put the one coverage statement in VI A.
  - Q19: the block is post hoc by construction. The audit clause still prints at :81.
  - Q22: IV B was rewritten neutrally, with the choice stated once.
- **Q08 and Q10 stay closed.**
  - Q08: "no correction to CH" no longer prints; only the explanation of the target difference does.
  - Q10: what prints is a scope sentence about comparisons outside the sixteen cells.
- **Q02's route** now records that VI A states the earlier fixed-truth failure.
