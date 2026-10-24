# Fact ledger: register round r16 (origin/main 927f40bf → branch `stageF/register-r16-20261023`)

**Governing record:** `docs/orchestration/DECISION-20261023-joseph-5d-targets-and-paper-round-2.md` ("another round for
the paper"), under the r15 standard of `DECISION-20261023-joseph-5d-a-and-register-round.md` item 2.

**Base.** `paper_body.tex` and `main_paper.tex` are byte-identical at ff1f8595 (where the worktree was made) and
927f40bf (the base the branch was fast-forwarded to). `main_paper.tex` is unchanged by this round.

**Scope.** Every printed sentence of `paper_body.tex` and `main_paper.tex` at 927f40bf that no longer prints verbatim
has at least one row here. The ids (`P#`) are those printed by `check_ledger.py --list` against 927f40bf: each numbers
the comment-stripped, whitespace-collapsed sentences of that file.

**Review fixes** (ADOPT-AFTER-FIXES, second commit): F8, F12, F13 and K1 below.

**Dispositions** (as in r15):
- `KEEP`: the fact still prints in the paper. Its wording may change, its meaning does not.
- `KEEP (disclosure)`: a disclosure the KEEP list holds in the paper (register-prd-study REPORT.md §4, "What we do that
  the corpus also does, and should keep": "disclosing a post hoc choice next to the choice"; §5 E3, the post-selection
  disclosure). The record behind it follows.
- `KEEP (narrowed)`: the new wording names the population its record covers. The record follows.
- `COLLAPSED→row`: a repeat. The fact still prints in the paper at the place named, and in the note.
- `REPOINT`: only a pointer's wording changed; its target sections are unchanged.

**Probes.** `P::text` must occur in the printed `paper_body.tex` of the worktree, `MP::` in `main_paper.tex`, and
`N:file::text` in that note file. Several probes are joined by ` && `. A probe proves only that the text is present;
each row's meaning was checked by reading.

**Nothing left both documents.** No fact was removed from the paper except the scan clause of row K2, whose content
prints twice more in the paper and once in the note. The note's text is unchanged (its `pdftotext` is byte-identical to
927f40bf's build).

## Sec. III, estimators

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| F1 | (e) keeps five iterations; the criterion was fixed in advance; 10, 15 or 20 did not reduce the model dependence, measured as the largest residual proxy over the development truth changes | P78 | KEEP (P1 target "the five-iteration rule"): "the rule's measure" restated as what it measures; "development truth changes" restated as "the truth changes used in its development". The rule and its values print in the note | III | `P::Configuration~(e) keeps five iterations by a criterion fixed in advance: 10, 15, or 20 iterations did not reduce its model dependence, measured as the largest residual proxy over the truth changes used in its development (\nsec{sec:gbdt-model-dependence}).` && `N:sec_5d.tex::a rule fixed before the comparison would have replaced its five iterations by 10, 15 or 20 only if one of them lowered the rule's measure of model dependence, the largest residual proxy over the development truth changes` |

## Sec. IV B, two-dimensional covariance

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| F2 | the 2D central value is reproducible; its covariance is built with the same estimator | P114 | KEEP: "therefore" dropped. The sentence closed the subsection as "In summary, ..." before r12; after r15 it follows the earlier-band history, from which it does not follow | IV B | `P::The two-dimensional central value is reproducible, and its covariance is built with the same estimator.` && `P::The two-dimensional central value is that of its systematic-universe ensemble, so its covariance is built with the same estimator.` |

## Sec. V A, closure

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| F3 | 2D closure with backgrounds: 20 pseudo-experiments at nominal truth; 14 of 205 cells >1 stat. sd apart; purity up to 5.9 stat. sd (>1 total sd in one cell); refined within 0.44 in every cell | P124 | KEEP (R10: split into two sentences) | V A | `P::In two observables, a closure test with backgrounds (20 pseudo-experiments at nominal truth) puts the purity and refined estimates more than one statistical standard deviation apart in 14 of the 205 cells, with the purity estimate up to 5.9 statistical standard deviations from the truth (more than one total standard deviation in one cell) and the refined one within 0.44 in every cell.` |
| F4 | the 2D result is being moved to the refined estimator | P124 | KEEP (decision-fixed: `DECISION-20261023-joseph-2d-refined-integrate-ci.md` item 1, "say plainly ... that the 2D result is being moved to the refined estimator"); now its own sentence, with the same pointer | V A | `P::The two-dimensional result is being moved to the refined estimator (\napp{sec:negweight-footing}).` |

## Fig. 3 caption (generator-sized truth changes)

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| F5 | panel (a) uses the random seeds of the estimator's development studies; panel (b) uses separate seeds, which were later also used in its development | P149 | KEEP (disclosure; P1 target "the seed panels"). It qualifies the caption's "not used while it was chosen" and Table II's "held-out shapes": the shapes were held out, the pseudo-experiments were later reused. Record: commit a6b9c705 replaced a "seeds not used before" label by this disclosure; the note states the reuse in sec:gbdt-model-dependence. Only "assessment seeds" and "entered" were reworded | Fig. 3 | `P::Panel (a) uses the random seeds of the estimator's development studies, and panel (b) separate seeds that were later also used in its development.` && `P::changes not used while it was chosen` && `N:sec_5d.tex::Because these samples were used during development, they provide no independent validation here.` |

## Sec. VII C, decision rule and familywise error

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| F6 | the error control is a property of the decisions; the point estimates (k+1)/(B+1) carry none of their own | P224 | KEEP: "carry no separate validity claim" restated without the record word "claim" | VII C | `P::The error control applies to the decisions, not separately to the point estimates $(k+1)/(B+1)$.` |
| F7 | the test design was fixed before any observed statistic; its reviewers had seen descriptive per-cell residuals of the data | P225 | KEEP (disclosure: a data-informed element; note sec:joint5d-frozen, "two data-informed elements") | VII C | `P::The test design was fixed before any observed statistic was computed; its reviewers had already seen descriptive per-cell residuals of the data.` && `N:sec_joint.tex::The design's reviewers had seen descriptive per-cell residuals of the data before it was fixed.` |
| F8 | the calibration's computing budget was increased by a bounded amount with the observed p values visible | P226 | KEEP (disclosure; P1 target "the budget extension"): a post hoc choice with the outcomes visible, stated where the sampling is described. "Computing budget ... extended" restated as "computing time available ... increased"; "with observed p values visible" kept as "after the observed p values had become visible" (review fix: the record says "visible", and nobody is recorded as having viewed them). Record: `DECISION-20261004-s5p-production-budget-extension.md` §3 ("made during production, after the controllers' looks had become visible"; "changes no statistic, criterion or decision rule") | VII C | `P::The computing time available to the calibration was later increased by a bounded amount after the observed $p$ values had become visible.` && `N:sec_joint.tex::a bounded extension of the production budget was decided while they were visible` |
| F9 | the error control is unaffected, because it holds for any stopping rule | P226 | KEEP (split, R10); "any stopping rule" restated as "any rule that decides when sampling stops", the wording of the bound two sentences earlier | VII C | `P::The error control above does not depend on this, because it holds for any rule that decides when sampling stops.` && `P::whatever rule determines when sampling stops` |
| F10 | computing time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments | P227 | KEEP (counts unchanged; macros \jtLostCal{}, \jtLostPow{}) | VII C | `P::Computing time limits interrupted or prevented \jtLostCal{} calibration and \jtLostPow{} power pseudo-experiments` |
| F11 | the decisions use the completed pseudo-experiments | P227 | KEEP: made explicit; it was implicit in Table IV's caption ("completed at the stopping point"). Note: "The decisions ... were evaluated on the completed draws" | VII C | `P::and the decisions use the completed ones.` && `P::null pseudo-experiments completed at the stopping point` && `N:sec_joint.tex::were evaluated on the completed draws.` |
| F12 | rerun, none of the lost calibration pseudo-experiments reaches the observed statistic in any test or shifted null | P227 | KEEP (narrowed; P1 target "the rerun"): "none" now names the calibration draws, the population whose statistics the record compares with the observed statistic. Record: `RECORD-20261006-s5p-lost-seed-recovery-resolution.md` §2 ("no recovered draw reaches the observed statistic (k_rec = 0 for all ten tests)") | VII C | `P::When rerun, none of the lost calibration pseudo-experiments reaches the observed statistic in any test or shifted null` && `N:sec_joint.tex::No recovered draw reaches the observed statistic in any test, claim variant or robustness variant` |
| F13 | their observed outcomes change no decision | P227 | KEEP (rewording of the §5 disposition; review fix 1): the old clause, "no assignment of the lost outcomes changes any decision", is Joseph's selected disposition (`DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §5: with every submitted draw observed and none reaching T_obs, "no missing-draw assignment changes any decision"), and the note prints the same sentence. After the recovery every draw was observed, so the old clause was true; the new wording states the same result in terms of the observed outcomes | VII C | `P::so their outcomes change no decision.` && `N:sec_joint.tex::so no assignment of the lost draws changes any decision` && `N:sec_joint.tex::is superseded by their observed outcomes` |
| F14 | independently written code reproduces every p value and decision | P227 | KEEP (unchanged sentence; listed because the sentence boundary moved) | VII C | `P::Independently written code reproduces every $p$ value and decision.` |
| F15 | pointer: the design and the rerun, note sec:joint5d-frozen and sec:joint5d-lost | P229 | REPOINT ("The design record ... are given in" → "The predeclared design ... are described in"); targets unchanged | VII C | `P::The predeclared design and the rerun are described in Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:joint5d-frozen} and~\ref*{N-sec:joint5d-lost}.` |

## Sec. VII E, results

<!-- absence-ok: this record quotes the paper's own condition (i) and Sec. VIII A item 7, whose source lines carry their Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| K1 | the target-corrected evaluations are descriptive; the decisions concern each prediction on its generation target, and stand | P249 | KEEP (decision-fixed; P1 target "descriptive ... do not re-grade"): `DECISION-20261020-joseph-nuwro-ch-claim.md`, "keep the ten recorded decisions"; "descriptive" is KEEP-list E3's adjective. "Do not re-grade" is restated as its content, that the decisions stand, in its own sentence (review fix 3: a colon read "they stand" as the reason); the note keeps its own wording | VII E | `P::These target-corrected evaluations are descriptive. The decisions of Table~\ref{tab:joint} concern each prediction on the target it was generated for, and they stand.` && `N:sec_joint.tex::they do not re-grade the decisions of Table~\ref{tab:joint5d}, which stand.` |
| K2 | a scan of the multiplier along δ_fine, outside the decision rule, finds all ten rejections determined up to about 5.2; it probes that one direction | P250 | KEEP | VII E | `P::As a sensitivity check outside the decision rule, a scan of the multiplier of the shift along $\delta_{\mathrm{fine}}$ finds all ten rejections determined up to a multiplier of about 5.2; it probes that one direction.` |
| K3 | the scan bounds neither the actual residual nor the convergence | P250 | COLLAPSED→condition (i) and Sec. VIII A item 7 (a restated caveat: condition (i) says the convergence has not been shown and the residual is unmeasured, and item 7 says a demonstrated bound on that residual is needed); the note prints the scan's own statement | VII D (i), VIII A | `P::so convergence of the fine grid has not been shown and the residual below it is unmeasured and potentially material` && `P::showing this would require a demonstrated bound on the residual below the fine grid.` && `N:sec_joint.tex::The scan probes one prescribed direction; it establishes neither convergence nor a bound on the actual below-grid residual` |
