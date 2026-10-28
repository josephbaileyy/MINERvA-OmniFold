# r19 variant B: the ledger pass over every fact leaving the paper (2026-10-28)

**Under:** `DECISION-20261028-joseph-r19-variant-b-and-moves.md` (#433), item 3. Every moved fact must print in the
note, and a fact that prints only in the paper comes to the director as a proposed note addition.

**Base:** #413 at `9df8f748`, which is step 0.

**MEASURES:** where the note already prints each leaving fact, as a verbatim probe.

**CITABLE FOR:** the paper-only list below, and the probes the r19 ledger's MOVE→note rows will use.

**NOT CITABLE FOR:** the paper's final wording. b1–b4 write it, and the ledger re-checks every probe then.

## Method

1. **`tools/move_pass.py`** lists the leaving text as sentences (166, in `move-pass/rows.tsv`):
   - Sec. VI (the calibrated tests) and Table VI;
   - the passages of O1–O6;
   - the knock-on edits K1–K14 (K11–K14 were added by this pass and accepted by the director).

   For each sentence it ranks candidate note sentences by keyword overlap. That ranking is only a finder.
2. **Four read-only agents**, one per row range, split each sentence into facts: each number, claim, qualifier and
   disclosure. For each fact they searched the whole note (the 28 inputs of `main_note.tex`) and gave a verdict, with
   a verbatim probe where the fact prints. They searched under one brief, and had neither the finder's verdicts nor
   each other's.

   The verdicts are PRINTS, PARTIAL, PAPER-ONLY, POINTER and HEADING, in `move-pass/cov-{A,B,C,D}.tsv`.
3. **The lane re-verified every probe mechanically,** with `fived16/check_ledger.py`'s normalizer (comments stripped,
   whitespace collapsed): 0 failures.
   - The lane also re-read every judgement call the agents flagged, and confirmed each PAPER-ONLY by its own grep of
     the printed and the comment text.
   - Two windows of the finder ran past their passage. They picked up the coverage warning sentence and the
     rounding-instability sentence, which both **stay** in the paper. Their rows are not moves.

## Result: 357 fact lines

| verdict | lines |
|---|---|
| PRINTS | 307 |
| POINTER | 8 |
| HEADING | 13 |
| PARTIAL | 12 |
| PAPER-ONLY | 17 |

**Everything in VI's subsections C–F and Table VI prints in the note**, with two exceptions: P3 and P4 below. The gaps
are in VI's lead paragraph, one sentence of the decision rule, Fig. 4, and K1's general definitions.

## The paper-only list

Facts that leave the paper in B and print nowhere in the note. Each comes with a proposed disposition.

| # | fact (paper text at 9df8f748) | rows | proposal |
|---|---|---|---|
| P1 | VI's lead: "For hypothesis tests the advantage is smaller. A test at reconstruction level would avoid the regularization bias, but it would still need the same response model. Each external prediction would have to be folded through the analysis simulation's response, which is the hybrid construction …, with the same composition below the fine grid." | B59–61 | **N1**, a note addition |
| P2 | "The tests of this section instead calibrate the unfolded statistic in simulation, so that the bias enters the null distribution rather than the decision." The note prints the first half (`sec_joint.tex`, "puts the estimator's bias … into each null distribution"); "rather than the decision" is only implied. | B62 | **N1** carries the contrast |
| P3 | "We have not compared their power with that of a reconstruction-level test." | B63 | **N1** |
| P4 | "The error control applies to the decisions, not separately to the point estimates $(k+1)/(B+1)$." | C95 | **N2**, one sentence in `sec:joint5d-frozen` beside "the familywise error rate of the ten decisions" |
| P5 | **Fig. 4 itself, and its caption's facts.** These are: the per-integral coverage display; one-sided Clopper–Pearson bounds, each at level 0.05/459, a Bonferroni correction over 153 integrals and three truths; "at nominal truth none lies below 0.66"; the third truth (a $q_3$ change at fixed $(\Eavail,W)$), omitted because its reweighting does not implement the intended change, and the verdict does not depend on it; and the integrals' make-up and order (the 42 $(\Eavail,W)$ cells and their sum, the 109 joint cells, the total). The note has the counts (51 of 153; 0.060; 42 at 95%; two at nominal) but not this figure: its `gbdt_coverage.pdf` is a different one (EW7 and EW41, 20 intervals). | A26–33 | **N3**: Fig. 4 enters the note in `sec:coverage-5d`, with the same file (`paper_fig_coverage`) and the paper's caption, its `\ref`s re-pointed to note labels |
| P6 | K1: "Two properties must be distinguished … The calibration of a test is the rate at which it rejects a true hypothesis. Calibration can be obtained without validated intervals by simulating the whole analysis chain at the hypothesis, so that the estimator's bias enters the simulated null distribution. A calibration obtained in this way is valid to the extent that the simulated chain reproduces the analysis of the data." The note states each for this analysis only, never as the definition. It also uses "calibration" for interval coverage elsewhere (`sec_5d.tex:8`; "interval calibration" in `sec_validation.tex`). | A36–39 | **N1** carries the definition. The note's other uses of the word are flagged for n4; r19 does not change them. |
| P7 | K13: "When intervals cannot be validated, tests can still be calibrated by simulating the analysis chain at the hypothesis." The note has only the analysis-specific halves. | A57 | **N1** |

**PARTIAL, resolved without a note addition** (each stays in the paper in B):

| row | fact | why it stays |
|---|---|---|
| B58 | "Unfolded results can be compared with any prediction at truth level without simulating each generator through the detector …" (the note has it only for the 3D comparisons) | T4: this half of the sentence moves to V B's lead in the paper |
| A21 | "Agreement in the marginal normalizations thus coexists with substantial residual bias under the tested deformations." | a finding, not the Gaussian diagnosis; it stays with the coverage warning |
| A50 | K8: the null displacement as the third of three results pointing to prior retention. The displacement itself prints in the note (D144). | the Discussion keeps one clause on it with an `\nsec` pointer, so the synthesis is not lost |
| A56 | K12: "Every study uses the analysis simulation's detector response" | stays; only the "except the calibration of the tests" clause leaves, and it prints in the note (B74: the source half carries the detector nuisance draws) |
| A15, A23 | "400 pseudo-experiments per truth" (the note: 1,200 over three truths, and 400 for the rate-reduction truth) | N3's caption carries it |

**PARTIAL needing a source check (P8):**
- **The fact:** O3's qualifier "in noise-free studies of that variant", on the 26% and larger-classifier results (A17).
- **What the note has:** `sec_5d.tex` prints both results in the paragraph after the one that sets up noise-free
  pseudo-data, without the qualifier.
- **Proposal:** before N4 adds "noise-free" to that note sentence, the lane checks the source record the note's
  comment cites. If the record does not say noise-free, the paper's qualifier is the claim to correct, and that goes
  to the director.

## The proposed note additions

The note's text changes only by these additions, under #433 item 3, once the director approves:

| id | where | text |
|---|---|---|
| N1 | `sec_joint.tex`, head of the chapter (after its first paragraph) | one paragraph of P1, P2, P3, P6 and P7, in the paper's wording (it is reviewed text), with "this section" → "this chapter" |
| N2 | `sec_joint.tex`, `sec:joint5d-frozen` | P4's sentence |
| N3 | `sec_5d.tex`, `sec:coverage-5d` | Fig. 4 and its caption (P5); a new note label `fig:coverage-5d-paper` |
| N4 | `sec_5d.tex`, the "Thirty iterations" sentence | "noise-free", only after P8's source check |

**N3 renumbers the note's later figures.** The note's `\ref`s and the paper's `\ref*` pointers follow automatically.
But the companion rule keeps the note's label numbers unchanged.
- **The alternative:** put Fig. 4 at the end of the note's last appendix, which renumbers nothing, with a pointer
  from `sec:coverage-5d`.
- That is the director's call.

## Stale protected text (for Joseph in (d))

Unedited:
- the abstract's "all reject" sentence;
- Data Availability's "of the joint tests";
- the title's "Performance and limitations";
- `app_release.tex:29` "the article's Figs.~1--3". This last one is re-checked after B against the final numbering,
  as the director asked: Fig. 4 and Table III leave, and so do the joint tests' arrays and figures.
