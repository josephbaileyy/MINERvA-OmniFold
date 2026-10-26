# Changes, move by move: register round r18

**Base:** origin/main `e270db89`, which is r17 as merged with its accuracy fixes.

**Files changed:**
- `docs/analysis-note/paper_body.tex`;
- one sentence added to the note's `sec_5d.tex` (S3);
- `check_sec4_receipts.py`: three entries repointed to the note;
- one comment in `values.tex`;
- the registry's line hints, refreshed;
- the rater-copy tool `fix_da_order.py`: case 3.

`main_paper.tex`, the abstract and every `\pubhold` are unchanged. Row ids in brackets are `ledger.md`'s.

**Brief:**
- the approved outline (`outline.md`);
- the director's rulings of 2026-10-25: S7 yes; Q1 drop who and keep the fact; Q2 keep the rerun clause; Q3 compress around the registry-cited lines; Q4 state the criterion; SEC4 repoint; S3 one clause plus a note sentence; the Table I caption change approved;
- the caveat-study rules R-P1 and R-P3 to R-P7.

## S1. IV B: the quoted block's status replaces the history of the superseded bands [B1–B12]

- **Before.** One paragraph:
  - the block;
  - an earlier band's predeclared fixed-truth test, its criterion, and its failure (91.2% within 2σ against 95.4%
    nominal);
  - the post hoc rescoring against a rebuilt band (97.7% and 78.1%), and why that is not independent.
- **After.**
  - The block's size and construction are unchanged. "with a median statistical uncertainty of \SI{0.676}{\percent}"
    is byte-identical.
  - Then: "The coverage of this block and of the total covariance has not been tested. We make no coverage claim on
    independent simulated samples or simultaneously over all reported bins and projections. The block supersedes two
    earlier statistical bands, whose coverage studies are described in \nsec{sec:coverage}."
- **Where the moved facts print** (rows B1–B5): `sec_validation.tex` sec:coverage, at :213, :228, :233–238 and
  :268–281.
- **The base's limitation 1 lands here too (S7):**
  - "The covariance has not been independently validated. It provides no calibrated significance for generator
    comparisons." This goes in IV B ¶1, and K7 is verbatim.
  - The run-period clause goes in IV B ¶3.
- **Table I:**
  - The 2D-covariance test cell changes from "an earlier band failed coverage" to "coverage not tested". PR #355 item 1
    allows this. [T1, T2]
  - The caption clause changes to "numbers and limitations are in the section given, and
    Sec.~\ref{sec:limitations} summarizes the principal limitations". The director approved this on 2026-10-25,
    because S7 made the old clause false. No check binds the caption text. [T3]
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

## S2. VII C ¶2: one short statement each [J8–J16]

**After:**
> The test design was fixed before any observed statistic was computed, after descriptive per-cell residuals of the
> data had been seen. The computing budget of the calibration was extended by a bounded amount after the observed $p$
> values were visible. Under A1 and A2, the error control holds for any rule that decides when sampling stops, so the
> extension does not affect it. Of the submitted pseudo-experiments, 224 for calibration and 53 for power did not
> complete within the computing time limits, and the decisions use the completed ones. When rerun, none of the lost
> calibration pseudo-experiments reaches the observed statistic in any test or shifted null, so their outcomes change
> no decision. A2 also requires that the pseudo-experiments were lost independently of their outcomes, which has not
> been shown. Independently written code reproduces every $p$ value and decision. The design and the rerun are
> described in …

- **PR #355's four facts are all present.**
- **Moved to the note:**
  - who had seen the residuals (the design's reviewers): `sec_joint.tex` sec:joint5d-frozen;
  - the interrupted versus never-started split: sec:joint5d-lost;
  - "predeclared": sec:joint5d-frozen.
- **Word choices, with their reasons:**
  - "seen", not "examined": the sources' word (note, amendment 7).
  - "computing budget of the calibration", not "budget": so that it cannot be read as a raised pseudo-experiment cap.
  - Source: DECISION-20261004 §2, CPU node-hours.

## S3. Fig. 3 caption [F1, F2]

- The two seed sentences become "Neither seed set was held out from the estimator's development."
- The note's `sec_5d.tex`, in the repeated-experiments paragraph, gains "These samples use separate assessment seeds,
  which also entered the estimator's later development."
- The note sentence is the pre-r16 caption's own wording. agy asked for it in place of a draft that added "separate
  from those of the development studies".

## S4. Scope stated once [J1, J2, J17, J18, J26]

- **VII A:** "and assign them no significance" is dropped. V D's "We therefore quote no covariance-based generator
  significance", the VII lead's "qualitative comparison" and the subsection title ("Descriptive") carry it.
- **VII D lead:** "concern the hybrid nulls" is dropped. Sec. I and VII B define the hybrid null.
- **VII E:** "Each rejection is a global assessment of a hybrid null. Assigning a discrepancy to …"

## S5. VII E [J24, J25]

"The decisions of Table IV concern each prediction on the target it was generated for. The target-corrected
evaluations are descriptive and leave them unchanged."
- "concern" is agy's fix, in place of the draft's "test": decisions do not test.
- "descriptive" is kept (DECISION-20261020).

## S6. III configuration paragraph [C1–C4]

"Table II lists the configurations and the results each is used for." The paragraph then keeps only what the table
does not state:
- (f) and its reproducibility;
- its covariance from the same estimator's ensemble;
- the 5D sentence with its bias pointer;
- the joint-test sentence.

The 3D/4D sentence collapses into Table II. The two lines the registry cites are byte-identical.

## S7. The VIII A list folded into the text

| former item | now prints in | ledger |
|---|---|---|
| 1 | IV B ¶1 (not independently validated; no calibrated significance, K7), ¶2 (coverage not tested, K6; no coverage claim), ¶3 (run-period block) | B8–B12 |
| 2 | IV A ¶1 (shape difference's source not identified), ¶2 (a reproduction, not an independent validation; K5 already there) | B13–B15 |
| 3 | V C ¶2 ("The source of this residual bias has not been established."); VI keeps its own sentence | B16 |
| 4 | V B, at the paragraph's end | B17, B18 |
| 5 | V D, after "We therefore quote no …", so that "therefore" keeps its base basis (K11 verbatim) | B19, B20 |
| 6 | VII A, the map paragraph | J3 |
| 7 | VII D (i), its last two sentences | J19 |
| 8 | VII D (ii), after the post hoc projection check | J20–J22 |
| 9 | VII C ¶1 (A1 validity, K-verbatim; the unmeasured rejection rate); VII B ¶2 (the conditioning on the lateral shifts) | J5–J7 |
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

**The new Limitations paragraph.** It keeps `\label{sec:limitations}` and restates four principal limitations, each
with its section:
- the 2D covariance, unvalidated and its coverage untested;
- the higher-dimensional results: central values without intervals of validated coverage, with an unassigned
  regularization bias;
- the rejections, conditional on the hadronic response;
- their carry-over to the predictions, only under an unshown below-grid bound;
- the calibration, valid to the extent that the chain reproduces the analysis.
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

It adds nothing the body does not state [L1, L2].

**Moves that follow from S7:**
- The roadmap sentence of Sec. I now reads "Section VIII A summarizes the principal limitations." [I1]
- The conclusions' "The following limitations apply …" is dropped.
- The three `% Search:` lines moved with their claims. A fresh configuration-(f) Search line and a run-period Search
  line were added where the claims now sit.

## S8 and S9. Process vocabulary and choices with their basis [C5–C7, J15, J16, J23]

- **III:** "Configuration (e) keeps five iterations because 10, 15, or 20 iterations did not reduce its model
  dependence, …" The pre-fixed rule prints in the note, sec:gbdt-model-dependence. "The criterion and its values"
  becomes "The comparison and its values", because "criterion" had lost its antecedent.
- **VII C:** "The predeclared design and the rerun …" becomes "The design and the rerun …".
- **VII D (ii):** "In a post hoc observation, …" becomes "A check made after the decisions shows that …". The note
  supports this: "Three studies followed the decisions".
- **IV A:** the choice and its disclosure are unchanged. They already state the choice with its basis.

## Not adopted, with reasons

- **Review I–V finding 6.** Narrowing "We make no coverage claim on independent simulated samples or simultaneously …"
  to "We make no coverage claim for it" would change a base qualifier. It is kept.
- **Review I–V finding 7.** Putting "supersedes" before the status sentence: the director's S1 example puts the status
  first.
- **Stale comment left in place:** the comment at `check_dead_containment.py:270-271` ("The paper avoids the same
  collision by printing 91.2 %"). The file's digest is recorded in `nd-unfolding/gbdt_model_dependence/
  build_evidence.json`, so a comment edit would break that record. The comment no longer describes the paper, and
  nothing reads it.
