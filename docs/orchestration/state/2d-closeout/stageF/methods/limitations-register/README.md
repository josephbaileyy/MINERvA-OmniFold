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

## Refresh for 2026-11-05's outcomes

**Asked for by** the director: the register's rows for the day's outcomes, as a PR the director updates the page from. The live page was not edited in this round. One earlier edit to it is disclosed at the end.

**The outcomes:**
- **B4, the stabilisation probe: NONE_PASS.** None of its three estimator changes brought the rounding-scale spread under its predeclared bar without worsening bias. The verdict is terminal: no estimator change, and 1B stage 1 launches on configuration (e) (`OUTCOME-20261105-fd-stab-none-pass.md`, #785).
- **COV2D binding 2:** the 2D coverage amendment's code, job scripts and pilot are bound (`COV2D-BINDING-2.md`).
- **REF-G1 bindings 1 and 2:** the sixteen-cell binned head-to-head is bound. Its preconditions passed (#775), its batch passed all 233 units (#790), and its bars were committed before the central difference (#791).
- **REF-C2C1 binding 1:** the binned cross-check of the 2D shape difference is bound. Its preconditions are listed (#779; the FAIL verdict there is a listing-design error and does not block), C-DRAW passed (#784), and its code (#787) is audited, awaiting a cluster test receipt.

**Rebuilt:** `limitations.json` and `limitations-detail.json`, by `build_register.py` from the note at main `9d69945e` (its route-record check passed). `paper-rows.json` is NOT rebuilt (see below).

### Rows whose status or route changed

Every status change is this lane's proposal for the director and Joseph.

- **n22** (items.tsv `cov16`; paper q01). Status: in progress (unchanged). New route:
  > The 1B stage-1 redesign (DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md item 3a), reopened as an investigation of gate D (DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md item 1; gate D FAIL, FD-1B-STAGE2-REPORT.md; NOT LOCALIZED, FD-1B-DIAG-REPORT.md). A coverage result that lands replaces this statement (DECISION-20261102 item 2). The stabilisation probe B4 tested three estimator changes (2-fold cross-fitting and two tree-regularisation settings); none brought the rounding-scale spread under its predeclared bar without worsening bias, so its verdict is NONE_PASS, which is terminal (OUTCOME-20261105-fd-stab-none-pass.md, under DECISION-20261102-joseph-bias-and-stabilisation-routes.md). No estimator change follows from B4, so 1B stage 1 launches on configuration (e) as planned, after its binding 3.
- **n17** (items.tsv `stat2d`; paper q02). Status: fix decided → **in progress**. New route:
  > The 2D method-coverage campaign: a held-out-tune ensemble with the covariance remade at each truth, priced first (DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md item 3c; KNOWN_ISSUES 85). The earlier band's fixed-truth failure (OUTCOME-20261005-2d-fixed-truth-coverage-fail.md, VL169) is permanent and stays disclosed. Bound and under way: COV2D binding 2 (2026-11-05) binds the amendment's code, job scripts and pilot; the order is the G18 pseudo-data job, then the pilot and its readout, then the bulk, within a 165.8 CPU node-h cap.
- **n54** (items.tsv `stab`; paper q33). Status: open → **inherent**. New route:
  > Rounding instability of the data unfold, which the bootstrap already carries (KNOWN_ISSUES 80, absorption measured). The stabilisation probe B4 tested three estimator changes (2-fold cross-fitting and two tree-regularisation settings); none brought the rounding-scale spread under its predeclared bar without worsening bias, so its verdict is NONE_PASS, which is terminal (OUTCOME-20261105-fd-stab-none-pass.md, under DECISION-20261102-joseph-bias-and-stabilisation-routes.md). The paper's rounding-instability statement stays as stated. Can be stated once (paper q33, M).
- **n34** (items.tsv `shape2d`; paper q21). Status: inherent (unchanged). New route:
  > The source of the correlated shape difference is not identified. A route is now declared and bound (REF-C2C1 step one, 2026-11-05): a binned IBU unfolding of this analysis's own 2D inputs, paired with E_R, reads by rules fixed in advance whether the difference sits on the input side or the algorithm side, or stays unresolved. It can locate the difference by one level, not name its cause, and it says nothing about equality with the publication's intermediate stages, which the B-C component accounting found missing from the release (component-accounting REPORT.md). Its inputs are listed, the replica check C-DRAW passed (Q_R's 300 existing replicas are reused), and its code (PR #787) is audited, awaiting a cluster test receipt and step two. (paper q21).
- **n74** (items.tsv `power`; paper —). Status: inherent (unchanged). New route:
  > Power statements of the terminal joint tests (RECORD-20261005-s5p-joint-5d-inference-result.md). A binned head-to-head at the sixteen reporting cells (REF-G1) is bound and run: binned IBU beside configuration (e) on the same data, cells and weight-only systematics, with paired replicas and readings fixed in advance. Its batch passed all 233 units, and its agree/differ thresholds were committed before the central difference was formed. Whatever it reads, it does not license a claim that the five-observable method adds discrimination.
- **Q01** (paper-rows.tsv `Q01`; paper Q01). Status: in progress (unchanged). New route:
  > 1B staged method coverage: stage 0 PASS (#679); stage 1 stopped at its weight guard 11-02 (0 node-h); redesign approved (#690 item 3a). Still printed in the abstract, Sec. I and VI A after #695. The stabilisation probe B4 tested three estimator changes (2-fold cross-fitting and two tree-regularisation settings); none brought the rounding-scale spread under its predeclared bar without worsening bias, so its verdict is NONE_PASS, which is terminal (OUTCOME-20261105-fd-stab-none-pass.md, under DECISION-20261102-joseph-bias-and-stabilisation-routes.md). No estimator change follows from B4, so 1B stage 1 launches on configuration (e) as planned, after its binding 3.
- **Q02** (paper-rows.tsv `Q02`; paper Q02). Status: in progress (unchanged). New route:
  > 2D method-coverage ensemble approved (#690 item 3c). Since #695, VI A also states the earlier fixed-truth failure (OUTCOME-20261005-2d-fixed-truth-coverage-fail.md), as #690 item 2 required. Bound and under way: COV2D binding 2 (2026-11-05) binds the amendment's code, job scripts and pilot; the order is the G18 pseudo-data job, then the pilot and its readout, then the bulk, within a 165.8 CPU node-h cap.
- **Q15** (paper-rows.tsv `Q15`; paper Q15). Status: in progress (unchanged). New route:
  > Same campaign as Q01 (1B stage-1 redesign). The stabilisation probe B4 tested three estimator changes (2-fold cross-fitting and two tree-regularisation settings); none brought the rounding-scale spread under its predeclared bar without worsening bias, so its verdict is NONE_PASS, which is terminal (OUTCOME-20261105-fd-stab-none-pass.md, under DECISION-20261102-joseph-bias-and-stabilisation-routes.md). No estimator change follows from B4, so 1B stage 1 launches on configuration (e) as planned, after its binding 3.
- **Q21** (paper-rows.tsv `Q21`; paper Q21). Status: inherent (unchanged). New route:
  > 2D shape difference vs the published result; source not identified. A route is now declared and bound (REF-C2C1 step one, 2026-11-05): a binned IBU unfolding of this analysis's own 2D inputs, paired with E_R, reads by rules fixed in advance whether the difference sits on the input side or the algorithm side, or stays unresolved. It can locate the difference by one level, not name its cause, and it says nothing about equality with the publication's intermediate stages, which the B-C component accounting found missing from the release (component-accounting REPORT.md). Its inputs are listed, the replica check C-DRAW passed (Q_R's 300 existing replicas are reused), and its code (PR #787) is audited, awaiting a cluster test receipt and step two.
- **Q23** (paper-rows.tsv `Q23`; paper Q23). Status: in progress (unchanged). New route:
  > 2D method coverage (#690 item 3c); wording consolidated by #695. Bound and under way: COV2D binding 2 (2026-11-05) binds the amendment's code, job scripts and pilot; the order is the G18 pseudo-data job, then the pilot and its readout, then the bulk, within a 165.8 CPU node-h cap.
- **Q33** (paper-rows.tsv `Q33`; paper Q33). Status: open → **inherent**. New route:
  > Rounding instability of the data unfold. The stabilisation probe B4 tested three estimator changes (2-fold cross-fitting and two tree-regularisation settings); none brought the rounding-scale spread under its predeclared bar without worsening bias, so its verdict is NONE_PASS, which is terminal (OUTCOME-20261105-fd-stab-none-pass.md, under DECISION-20261102-joseph-bias-and-stabilisation-routes.md). The paper's rounding-instability statement stays as stated.
- **Q39** (paper-rows.tsv `Q39`; paper Q39). Status: in progress (unchanged). New route:
  > 1B stop disclosure: superseded when the staged campaign reports The stabilisation probe B4 tested three estimator changes (2-fold cross-fitting and two tree-regularisation settings); none brought the rounding-scale spread under its predeclared bar without worsening bias, so its verdict is NONE_PASS, which is terminal (OUTCOME-20261105-fd-stab-none-pass.md, under DECISION-20261102-joseph-bias-and-stabilisation-routes.md). No estimator change follows from B4, so 1B stage 1 launches on configuration (e) as planned, after its binding 3.

**Why the status changes are proposed:**
- **Rounding instability (n54, Q33): open → inherent.** B4's terminal NONE_PASS leaves no declared route to remove it from the kept estimator. The statement stays, can still be stated once (class M), and the bootstrap already carries it.
- **2D method coverage (n17): fix decided → in progress.** The campaign is bound, with its code, job scripts and pilot sequence (COV2D binding 2).
- **The 2D shape difference (n34, Q21) stays inherent.** REF-C2C1 can locate the difference by one level, not name its cause, so it narrows the statement rather than closing it. The old route's "no route is recorded" is no longer true, and is replaced.

### Rows whose location only changed (the note moved since `108040f8`)

- n53: `sec_5d.tex:83` → `sec_5d.tex:84`
- n55: `sec_5d.tex:107` → `sec_5d.tex:108`
- n56: `sec_5d.tex:146` → `sec_5d.tex:147`
- n59: `sec_fived16.tex:43` → `sec_fived16.tex:91`; section §10 The sixteen-cell five-observable measurement > §10.1 Cells and result → §10 The sixteen-cell five-observable measurement > §10.2 Quadrant sums against the lower-dimensional results
- n60: `sec_fived16.tex:57` → `sec_fived16.tex:105`; section §10 The sixteen-cell five-observable measurement > §10.2 The reported covariance → §10 The sixteen-cell five-observable measurement > §10.3 The reported covariance
- n61: `sec_fived16.tex:120` → `sec_fived16.tex:168`; section §10 The sixteen-cell five-observable measurement > §10.2 The reported covariance → §10 The sixteen-cell five-observable measurement > §10.3 The reported covariance
- n62: `sec_fived16.tex:127` → `sec_fived16.tex:180`; section §10 The sixteen-cell five-observable measurement > §10.3 The run-period block → §10 The sixteen-cell five-observable measurement > §10.4 The run-period block
- n63: `sec_fived16.tex:134` → `sec_fived16.tex:187`; section §10 The sixteen-cell five-observable measurement > §10.4 Fake-data tests of the estimator's bias → §10 The sixteen-cell five-observable measurement > §10.5 Fake-data tests of the estimator's bias
- n64: `sec_fived16.tex:163` → `sec_fived16.tex:216`; section §10 The sixteen-cell five-observable measurement > §10.4 Fake-data tests of the estimator's bias → §10 The sixteen-cell five-observable measurement > §10.5 Fake-data tests of the estimator's bias
- n65: `sec_fived16.tex:167` → `sec_fived16.tex:220`; section §10 The sixteen-cell five-observable measurement > §10.4 Fake-data tests of the estimator's bias → §10 The sixteen-cell five-observable measurement > §10.5 Fake-data tests of the estimator's bias
- n66: `sec_fived16.tex:204` → `sec_fived16.tex:258`; section §10 The sixteen-cell five-observable measurement > §10.5 Comparison with generator predictions → §10 The sixteen-cell five-observable measurement > §10.6 Comparison with generator predictions
- n67: `sec_fived16.tex:262` → `sec_fived16.tex:316`; section §10 The sixteen-cell five-observable measurement > §10.5 Comparison with generator predictions → §10 The sixteen-cell five-observable measurement > §10.6 Comparison with generator predictions
- n54 (also changed above): `sec_5d.tex:90` → `sec_5d.tex:91`

### The paper rows: routes and statuses only

`relocate_paper.py` fails at main `9d69945e`: five rows' phrases no longer print after the later paper rounds (Q31, Q32, Q39, Q40, Q43). So `paper-rows.json` keeps its 11-02 locations, and only `paper-rows.tsv`'s routes and statuses change here. The page's paper locations stand as the director's 11-04 re-anchor set them. Re-anchoring Q01–Q44 to the current paper is a separate task.

### Disclosure: one live-page edit earlier today

Before the director's instruction not to edit the page, this lane changed row q21's route on the page (version 6 → 7), replacing "Code next (after REF-G1)." with "Code written (PR #787, 11-05): binned IBU in E_R's own driver, 17 tests, 22 mutants; code audit pending, then step two." That text is now superseded by the Q21 route above.
