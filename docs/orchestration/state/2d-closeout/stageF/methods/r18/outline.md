# Register round r18: outline and proposed moves (2026-10-25)

**Base:** origin/main `e270db89`, which is r17 as merged with its accuracy fixes (`paper_body.tex` sha256 `1a0cc74a…`).
Branch `stageF/register-r18-20261025`.

**Brief:**
- R1–R10 of register-prd-study;
- the caveat-study paper rules R-P1 and R-P3 to R-P7 (`caveat-study/REPORT.md` §5.1);
- the r18 history decision (`DECISION-20261025-joseph-r18-history-to-note.md`, PR #355);
- the director's added targets: VII E and the III paragraph.

**Out of scope:**
- the abstract: R-P8 is with Joseph;
- R-P9 (fewer secondary results);
- the §6 assigned-uncertainty options;
- the data-availability text, for which r18 only proposes wording;
- `\pubhold`, KI-85 and the release text.

**Guardrails as before.** No number or claim changes, and no fact leaves both documents. A qualifier stays where leaving
it out would make a printed sentence false. Every moved fact gets a ledger row naming its note location.

## Targets: what the r17 P1 raters and the r17-baseline raters quoted

| # | passage | source of the target |
|---|---|---|
| T1 | IV B, the earlier band and its post hoc rescoring (`paper_body.tex:480-495`), and Table I's 2D-covariance cell | PR #355 item 1; quoted in 3 of 3 r17 runs |
| T2 | VII C, the design, the budget extension and the lost pseudo-experiments (`:1030-1043`) | PR #355 item 2; quoted in 3 of 3 r17 runs |
| T3 | Fig. 3 caption, the seed sentences (`:673-675`) | PR #355 item 3 |
| T4 | repeated scope statements | PR #355 item 4; R-P6 |
| T5 | VII E, "These target-corrected evaluations are descriptive. The decisions … stand" (`:1128-1130`) | quoted in 2 of 3 r17 runs |
| T6 | III, the configuration paragraph (`:309-321`) | quoted in 1 of 3 r17 runs |
| T7 | data availability | PR #355 item 5. Proposed wording only, in REPORT. |

## Proposed moves

### S1 (T1, IV B): the quoted block's status replaces the history (R-P3)

- **Before.** One paragraph:
  - the statistical block's size and construction;
  - an earlier band's predeclared fixed-truth test, its criterion, and its failure (91.2% within 2σ against 95.4%
    nominal);
  - the post hoc rescoring against a rebuilt band (97.7% and 78.1%), and why it is not independent.
- **After.**
  - The block's size and construction are kept: "with a median statistical uncertainty of \SI{0.676}{\percent}" stays
    byte-identical, because SEC4 binds it.
  - Then one plain sentence on the quoted block, positive-first. A draft: "Its coverage has not been tested; an earlier,
    superseded statistical band and its fixed-truth coverage test are described in \nsec{sec:coverage}."
  - If S7 is ruled in, this sentence also carries limitation 1's other facts (S7, row 1).
- **Facts that leave the paper** (ledger rows MOVE→note):
  - The earlier band was tested on \covTwoDNtoy{} pseudo-experiments at fixed truth. Note `sec_validation.tex:213`,
    `:234-238`.
  - The criterion (ratio in [0.9, 1.1]). Note `:228-229`.
  - The failure, 91.2% within 2σ against 0.954 nominal. Note `:236-238`, "(Gaussian 0.954)".
  - The post hoc rescoring, 0.977 and 0.781, partly circular. Note `:277-281`.
  - The band was rebuilt, and the quoted block is a third ensemble, untested. Note `:268-271`.
- **Table I** (protected except for this cell, as the decision allows). The "Test" cell changes from "an earlier band
  failed coverage" to "coverage not tested".
- **`check_sec4_receipts.py`.** Two entries bind the departing text. I propose to **repoint** both to the note, where
  the values print, rather than retire them:
  - **"two-sigma nominal":** `paper_body.tex` "against \SI{95.4}{\percent} nominal" moves to `sec_validation.tex`
    "lies entirely below its window (Gaussian 0.954)". The pattern is `(Gaussian ([0-9.]+))` after "below its
    window", which matches once. The computed value is erf(2/√2), a fraction.
  - **"rescoring … 2 and 1 sigma":** moves to `sec_validation.tex` "$C_2=([0-9.]+)$ [...] and $C_1=([0-9.]+)$". The
    computed value is the rescore fraction, at 3 decimals.
  - `--self-test` must still pass, and the change is recorded in REPORT.
  - The values.tex entries (`\covTwoDNtoy`, `\covTwoDCTwoPctOne`, `\covTwoDCOne`) are unchanged.
- **Other checks on this text.** A grep finds no other check that binds the paragraph or the cell. The match in
  `re2/inventory.tsv` (its line 196) is a macro-use inventory, and no gate reads it for the paper. I will rerun the
  registry and results-index checks and all the SEC4 tests.
- The comment block's routes are updated to name the note's section.
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

### S2 (T2, VII C): one short statement each (R-P4, R-P7)

**Draft after**, with each fact required by PR #355 marked:
> The statistic, the decision rule and every input were fixed before any observed statistic was computed, after
> descriptive per-cell residuals of the data had been seen. The calibration budget was extended by a bounded amount
> after the observed $p$ values were visible **[1]**; under A1 and A2 the error control holds for any rule that decides
> when sampling stops **[2]**, so the extension does not affect it. Computing time limits interrupted or prevented
> \jtLostCal{} calibration and \jtLostPow{} power pseudo-experiments **[3]**; the decisions use the completed ones, and
> none of the lost calibration pseudo-experiments, when rerun, reaches the observed statistic. A2 also requires that
> they were lost independently of their outcomes, which has not been shown **[4]**. Independently written code
> reproduces every $p$ value and decision (\nsec{sec:joint5d-frozen}, \nsec{sec:joint5d-lost}).

**Mechanics and history** (timeouts, the motivation, the transition) are not in the paper now. They print in the note:
- `sec_joint.tex:250-259`: the two data-informed elements, and the extension decided while the p values were visible
  "so that the sequential rule could reach the stop set by its predeclared rule";
- `:513-555`: the interrupted and never-started split, the sensitivity, the rerun and the margins.

No fact leaves the paper.

**Open questions:**
- (Q1) Who saw the residuals. The base reads "Its reviewers had already seen …". R-P4 says not to say who saw what, but
  dropping "reviewers" could read as the designers having seen them. I can keep "the design's reviewers had seen" in
  the clause, or drop it. Which do you rule?
- (Q2) The rerun clause is kept: it is a positive fact, and it is Joseph's selected disposition. Confirm.

### S3 (T3, Fig. 3 caption)

- **Before:** "Panel (a) uses the random seeds of the estimator's development studies. Panel (b) uses separate seeds,
  which were later also used in the estimator's development."
- **After:** "Neither seed set was held out from the estimator's development; panel (b)'s seeds, separate when it was
  chosen, were used in it later."
- This holds for both panels. (b)'s "three shape changes not used while it was chosen" is unchanged.
- **Why the second clause stays.** The note prints that panel (b)'s samples "were used during development"
  (`sec_5d.tex:259-264`). It does not print that they were separate when the estimator was chosen. That positive fact
  would leave both documents, so it stays in the caption.
- **Option:** the director's one-clause form ("Neither seed set was held out from the estimator's development") is
  possible if the "separate" fact is first added to the note's sec:gbdt-model-dependence. That would be a note edit in
  r18. Your call.

### S4 (T4, scope stated once; R-P6)

Sec. I's scope paragraph keeps the scope. The restatements below go, or fold into the sentence they qualify:

| line | restatement | proposal |
|---|---|---|
| 889-891 | "These comparisons use central values only … and assign them no significance." | keep "central values only, of configuration (e) …, (a) …" (the configuration facts). Drop "assign them no significance": Sec. I and V D already say no significance is quoted. |
| 1048 | "The decisions concern the hybrid nulls and rest on six conditions" | keep "rest on six conditions"; drop "concern the hybrid nulls" (K2 stays in Sec. I, VII B and the abstract) |
| 1185 | "The rejections are global assessments of the hybrid nulls: assigning a discrepancy to a kinematic region or nuclear mechanism would require separate tests." | keep the second half, positive-first: "Each rejection is a global assessment; locating a discrepancy in a region or mechanism needs separate tests." |
| 1258 | "The rejections remain conditional on the simulation's hadronic response." | stays with condition (ii) (S7). It is a condition, not scope. |

Kept as is: the Sec. I negatives "does not deliver a validated five-observable cross-section measurement" and "not
physical exclusions … no measurement uncertainty". R-P6 allows one negative where a reader would otherwise infer the
broader claim.

### S5 (T5, VII E)

**After:** "The decisions of Table IV test each prediction on the target it was generated for. The target-corrected
evaluations are descriptive and leave them unchanged."
- "descriptive" is kept (DECISION-20261020).
- "stand" becomes "leave them unchanged". Same fact, positive voice.

### S6 (T6, III): the configuration paragraph defers to Table II (R-P1)

**Before.** One paragraph restates Table II's "Used for" column, plus three facts not in the table:
- (f)'s reproducibility;
- (f) being the systematic-universe ensemble's estimator, so the covariance uses the same estimator;
- (e)'s refinement removing most of the purity bias at nominal truth in the highest-W cells.

**After:**
- One lead sentence: "Table II gives each result's configuration."
- Then only the three facts, and the 5D sentence with its bias pointer.
- The two lines the registry cites by digest ("configuration~(f): the learner and seed …" and "configuration~(e), the
  joint-test estimator, whose …") stay byte-identical.

**Open question (Q3):** compress around those two cited lines (my default), or merge freely and refresh the registry
citations (`check_registry.py --cite`, new rows)?

### S7 (R-P2, FOR YOUR RULING): fold the VIII A list into the text, and keep a short Limitations paragraph

**Structure.**
- `\subsection{Limitations}` and `\label{sec:limitations}` are kept, so Table I's caption and every `\ref` still
  resolve.
- The numbered list becomes one prose paragraph restating the principal limitations.
- Each item's full statement moves inline to the result it qualifies, with every condition attached.
- The three `% Search:` lines move with their absence claims, to the destination paragraphs.

| item | content (all conditions kept) | lands inline at |
|---|---|---|
| 1 | 2D covariance not independently validated; the coverage of the statistical block and of the total not tested; no coverage claim on independent samples or simultaneously; no calibrated significance for generator comparisons (K7); run-period block's size not validated, its consistency check cannot fail | IV B, as S1's new status sentence. The run-period clause goes into IV B ¶3, after "includes this inconsistency". |
| 2 | learner selected after both comparisons (K5/D1); so a reproduction, not an independent validation; source of the shape difference not identified | IV A ¶2, right after "This learner was chosen after both comparisons were known" |
| 3 | source of the residual bias behind the miscoverage not established | already in VI ("whether that bias has the same origin is not established") and V C ¶2. The list item merges into V C ¶2 and VI keeps its sentence (R-P1, two places now become one plus a cross-reference) |
| 4 | the generator-sized residual is interpreted as regularization bias; no quoted uncertainty includes it; the 5D covariance omits it | V B, after "We interpret it as regularization bias" |
| 5 | seed dependence rests on one seed pair; spread over pairs not measured; the five fixed-seed bands carry \pinnedBandsSqrtTr\% of √Tr C, seed sensitivity not measured | V D ¶1, after the seed-pair sentence |
| 6 | no closure with a mismodelled detector response for the (Eavail, W) map | VII A ¶3, the map paragraph |
| 7 | carry-over from hybrid nulls to the predictions only if the below-grid replacement moves the result by no more than ±κ δ_fine; needs a demonstrated bound | VII D (i), as its last sentences |
| 8 | no hadronic-response band; net effect on each p not measured; rejections conditional on the simulation's response; physical interpretation needs a band through the calibration | VII D (ii), first paragraph |
| 9 | calibration valid to the extent that the chain reproduces the data analysis (A1); a rejection rate for null pseudo-data processed like the data would need an independent sample and has not been measured; conditioning on the data-derived lateral shifts not validated | VII C, after A1 is defined (the rate). VII B ¶2, after "conditional on these data-derived inputs" (the conditioning). |
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

**Draft of the new Limitations paragraph**, about 110 words:
> The principal limitations are stated with the results they qualify. The two-dimensional covariance has not been
> independently validated, and its coverage has not been tested (Sec. IV B). The higher-dimensional results are
> central values whose regularization bias no quoted uncertainty includes (Sec. V B). The generator tests reject
> hybrid nulls, conditionally on the simulation's hadronic response and on the composition below the fine grid
> (Sec. VII D); their calibration is valid to the extent that the simulated chain reproduces the analysis of the data
> (Sec. VII C).
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

This paragraph carries Search lines for its absence claims.

**Effects:**
- The conclusions' sentence "The following limitations apply …" becomes a pointer to the paragraph.
- Several restatements fall away, because items 3, 7 and 8 already have a home inline.
- **Expected words:** about −150.
- **Protected text:** K6, K7, K8, K11 and K14 all stay. K6 moves into IV B, where E4 had it.

### S8 (R-P7, process vocabulary)

| line | words | proposal |
|---|---|---|
| 327 | "Configuration (e) keeps five iterations by a criterion fixed in advance." | "Configuration (e) keeps five iterations: 10, 15 or 20 did not reduce its model dependence, …". **Q4:** r17 named this a D1 disclosure; R-P7 removes it outside the joint tests. Drop it? |
| 483 | "A coverage test specified in advance …" | leaves with S1 |
| 1030 | "The test design was fixed before …" | kept, as R-P7's one pre-specification sentence (S2) |
| 1041 | "The predeclared design and the rerun are described in …" | "The design and the rerun are described in …" |

### S9 (R-P4: data-informed choices stated as choices)

- **IV A:** "We quote the LightGBM result, chosen after both comparisons were known, because its covariance uses the
  same estimator."
- **VII D (ii):** "In a post hoc observation, …" becomes "A check made after the decisions shows that the calibrated
  tests restricted to …". The disclosure is kept.

### S10 (R-P5 and R-P6, negation-first sentences)

- **Where:** the changed paragraphs above.
- **How:** assumptions are stated as assumptions, and limits lead with what holds. The target is fewer negation-led
  caveat sentences: the paper's 35% toward the corpus 22%.
- **Limits:** no negation that carries a fact is removed. The Search lines stay with their paragraphs.

## Batches

| batch | range | moves |
|---|---|---|
| b1 | I–III, Table I's one cell | S4 (Sec. I), S6, S8 (:327), the Table I cell |
| b2 | IV–V, Figs. 1–3 | S1, S3, S9 (IV A); if S7 is ruled in, the inline items 1, 2, 3, 4 and 5 |
| b3 | VI–VII | S2, S4, S5, S8, S9 (VII D); if S7 is ruled in, the inline items 3 (VI), 6, 7, 8 and 9 |
| b4 | VIII | S7's Limitations paragraph and the conclusions pointer, or, if S7 is declined, R-P5 rewrites of the list in place |

**Method, as in r17:**
- writer per batch;
- two-direction review;
- agy on every printed passage;
- a ledger whose MOVE→note rows have N: probes;
- SEC4 with the repointed entries and its self-test;
- registry `--repoint`, so the CI self-test does not fail as it did on r17;
- full build;
- pairwise in both orders with both models;
- P1 sol2 ×3.

## Questions for you

1. **S7 (R-P2): fold the list in, yes or no?**
2. **Q1:** keep or drop "the design's reviewers".
3. **Q2:** keep the rerun clause in VII C.
4. **Q3:** for the III paragraph, compress around the two registry-cited lines, or merge freely and refresh the
   registry rows.
5. **Q4:** drop "by a criterion fixed in advance" for (e)'s iterations.
6. **`check_sec4_receipts.py`:** repoint the two entries to the note (my proposal), or retire them.
7. **S3:** the two-clause caption, or the one-clause form plus a one-sentence note addition.
