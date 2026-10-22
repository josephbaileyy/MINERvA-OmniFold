# Methods-paper rewrite: implementation record

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-19/20.
- **Brief:** [`../METHODS-FRAMING.md`](../METHODS-FRAMING.md).
- **Outline:** [`OUTLINE-DECISION.md`](OUTLINE-DECISION.md).
- **Decisions:** [`DECISION-20261019-joseph-methods-first-and-measurement-compute`](../../../../DECISION-20261019-joseph-methods-first-and-measurement-compute.md)
  and [`DECISION-20261020-joseph-nuwro-ch-claim`](../../../../DECISION-20261020-joseph-nuwro-ch-claim.md).

**CITABLE FOR:**
- what the rewrite changed and how it was checked;
- the outside-referee rounds and their triage;
- the claim changes (M8), by category;
- the open decisions for Joseph and the new work the referees asked for.

**NOT CITABLE FOR:**
- final wording or claims (provisional until the review with Ben; J3–J5 provisional);
- any outward act (J6).

## 1. Commits (branch `stageF/methods-rewrite-20261019`)

Drafts 1–8 are on the branch, on base `51da2a62`. Each draft was built in a scratch copy
(`build_copy.sh mrw1`–`mrw8`): rc 0, both gates PASS (Sec. IV receipts 15/15), no unresolved references.

| draft | content |
|---|---|
| 1 | restructured to sections I–IX ([`OUTLINE-DECISION.md`](OUTLINE-DECISION.md)); scope statement; definition, estimator and validation tables; three bias/coverage figures (M3); the certified familywise bound and nuisance-averaged size (M2); the W and target statements (M4) |
| 2 | fixes from the independent review REVIEW-1 (5 MATERIAL); abstract at 150 words; page cuts that moved content to note homes |
| 3 | SF-1 result ([`SF1-REPORT.md`](SF1-REPORT.md), PASS); Fig. 6 legend |
| 4 | outside round X5: the "E_avail tilt" corrected to a ~10% signal-rate reduction (KI 98); decision-boundary margins (a7margins receipt); Appendix A, the familywise derivation; "calibrated within the implemented simulation model" |
| 5 | Joseph's NuWro-CH decision (a high-level statement in the paper, details in note §`sec:joint5d-ch`); readability pass moving technical detail to confirmed note homes |
| 6 | REVIEW-2 (2 MATERIAL restored); outside round X6: validation findings made central, Sec. VIII presented as an application, the "total (rate-and-shape)" test defined, authorization language replaced by scientific content |
| 7 | REVIEW-3 (3 MATERIAL); outside round X7: residual bias as the observation; 5% familywise statement in the main text with 0.9α only in Appendix A; Holm and dynamic program specified; the coverage-failure diagnosis ([`M2-RATEFAIL-DIAGNOSIS.md`](M2-RATEFAIL-DIAGNOSIS.md)) |
| 8 | the draft-7 verification's findings (2 swallowed tails, 5 minor wordings), applied by the director; the classifier training details read from the code ([`M-TRAINING-DETAILS.md`](M-TRAINING-DETAILS.md)), replacing the stated documentation gap: in-sample training, raw class weights, no renormalization; no effective sample size computed |

**Page count.** Draft 8 is 18 pages: a 16-page body, Appendix A and references. The 15-page target was the director's
own. The remaining options are structural and are Joseph's call:
- merging the repository-record references into the note (P7);
- dropping a table;
- moving the appendix.

## 2. Evidence produced for the rewrite (all on `main`)

- **M2 (calibration):**
  - [`M2-AUDIT.md`](M2-AUDIT.md);
  - [`M2-FWER-RECORD.md`](M2-FWER-RECORD.md), the certified bound FWER ≤ 0.8902α, with a GPT-6.1-sol check;
  - [`M2-ARCHIVE-CHECKS.md`](M2-ARCHIVE-CHECKS.md);
  - SF-1 ([`SF1-SPEC.md`](SF1-SPEC.md), [`SF1-REPORT.md`](SF1-REPORT.md));
  - the rate-change coverage diagnosis.
- **M3 (figures):** from existing receipts. The scripts are in `docs/analysis-note/figures/methods_m3/`.
- **M4:** [`M4-DEFINITIONS.md`](M4-DEFINITIONS.md) and [`M4-W-RECORD.md`](M4-W-RECORD.md).
- **From the measurement session** (beside A7, descriptive):
  - the decision-boundary margins;
  - MP3-A, MP3-B and MP3-C (the hydrocarbon replays);
  - MP-5 (convention effects).
- **Known issues:** KI 97 (target mismatch), KI 98 (the "tilt"), KI 99 (W2 stale-cycle reader).

## 3. Reviews

**Independent Claude reviews, in both directions.** Every finding was fixed or dispositioned in the next draft.

| review | on | MATERIAL | MINOR | NOTE |
|---|---|---|---|---|
| REVIEW-1 | draft 1 | 5 | 15 | 6 |
| REVIEW-2 | drafts 4–5 | 2 | 11 | 6 |
| REVIEW-3 | draft 6 | 3 | 8 | 6 |
| verification | draft 7 | see §6 | | |

**A recurring defect:** edits that end a line in a comment, so that the sentence after it no longer prints. It
recurred in drafts 2–7, with 16 cases found in all. A mechanical check, `scratchpad/tools/swallowed_text.py`, now
flags prose that moved from printed text into a comment. Its flags are cleared by hand.

**Outside-referee rounds**, run read-only through `stageF/plain-language/run_x.sh` (agy Gemini 3.8 Flash and
codex-school GPT-6.1-sol):

| round | on | GPT-6.1-sol | Gemini |
|---|---|---|---|
| X4 | pass-2 text | framing round (outline, scope, abstract, dispositions) | the same |
| X5 | draft 3 | major revision | major revision |
| X6 | draft 5 | major revision; "choose the validation-study paper" | major revision |
| X7 | draft 7 | major revision; "a focused validation study … could be valuable" | major revision |

The stopping rule of the brief (at most three X5-type rounds) has been reached. Gemini's overclaims were rejected each
round: "first application", "eigenvalues collapse to zero", "three independent variables". GPT-6.1-sol's arithmetic
found KI 98.

## 4. Claim changes (M8), by category

Each change is marked in a LaTeX comment at its site. The full lists are in the writer's per-draft reports, kept in
the director's scratchpad.

- **Framing.** New title ("Performance and limitations of multidimensional OmniFold unfolding with MINERvA open
  data"). The validation findings are the main results. The generator tests are an application illustrating
  calibrated inference with a biased estimator. "Five-observable", not "five-dimensional".
- **Narrowed results:**
  - the 2D result reproduces the integral within about 1%, with a correlated shape difference;
  - residual bias under the tested deformations is the observation, interpreted as regularization bias;
  - "none of the tested reporting definitions satisfies the adopted 10% criterion under the specified envelope
    prescription";
  - "envelope over the five tested truth deformations" replaces "model dependence";
  - the 3D and 4D closure tests are stated with no recorded threshold;
  - the low-recoil mechanism, the 52% gap and the corner localization were cut or moved to the note.
- **The tests:**
  - hybrid null hypotheses defined precisely (Tune v1 composition below the fine grid, varied by the drawn
    universes);
  - size averaged over the nuisance priors;
  - familywise control at 5% under the stated calibration assumptions (≤ 0.9α in Appendix A);
  - decision-boundary margins;
  - SF-1 as a simulation-size check only;
  - NuWro's total (rate-and-shape) test rejection not robust to the hydrocarbon correction (Joseph, provisional).
- **Corrections:**
  - the "tilt" is a ~10% rate reduction, and its coverage failure is residual bias;
  - the W conventions and the truth-angle axis;
  - the target per-nucleon effect;
  - the truth deficit of the pseudo-experiments.
- **Removed:**
  - "We are not aware of an application to neutrino-scattering data";
  - the unsupported "p values remain valid" sentence, replaced.

## 5. Open for Joseph

1. **Primary configuration (both referees).** The central values use the purity-subtraction estimator (a), and the
   tests use the refined estimator (e). The options:
   - keep this, as now, stated;
   - regenerate the central values with the refinement, though it shares the estimator family's rounding instability;
   - carry the bias, stability and coverage studies through one configuration.
   The last two are new work.
2. **Pages (18).** P7, or a structural cut.
3. **The prominence of the generator tests.** They are now presented as an application. GPT-6.1-sol would shorten them
   further unless a response model and end-to-end calibration validation are added (measurement-paper work).
4. **New work the referees asked for**, not started:
   - a binned iterative-unfolding baseline under matched conditions;
   - an ablation with and without W, or with replacement observables;
   - a null ensemble processed like the data (end-to-end size);
   - a response model in the calibration (MP-1, under way in the measurement session);
   - a target-correction uncertainty;
   - the run-period step's cause;
   - the source of the W-graded residual bias (a cheap cluster test is specified in the diagnosis);
   - an effective sample size of the unfolded ensemble, which is not computed anywhere. The training split and class
     normalization are now stated from the code.
5. **The primer and note** follow the paper, as a next pass.

## 6. Draft-7 verification and draft 8

An independent verification of draft 7's changes found 2 MATERIAL, 5 MINOR and 6 NOTE findings.
- **The two MATERIAL findings:** two swallowed tails, "The point" and "The", each before a line starting with math.
  `swallowed_text.py` had missed both, so it now carries a short-tail rule.
- **The MINOR findings and NOTE 8–10:** the note's "slightly too wide" qualified; single-experiment values scoped;
  the background-fraction match hedged; 135 MeV "inherited"; the precision-target wording carried to the abstract and
  Table I.
- **The verification confirmed:**
  - all of REVIEW-3 fixed;
  - Appendix A's Holm description against `holm_determined`;
  - the dynamic-program description, the power intervals, and the pseudo-inverse rank and condition number;
  - the prior-versus-weights sentence and the diagnosis numbers.

The director applied every MATERIAL and MINOR fix and NOTE 8–10 as draft 8. The build (`mrw8`) gave rc 0, gates PASS,
no unresolved references, 18 pages and a 150-word abstract. The short-tail rule finds no case. The final PDFs are in
the director's scratchpad, `methods-final/`, with SHA256SUMS.

## 7. Shortening pass (2026-10-21, DECISION-20261020-joseph-refined-estimator-shorten-delta item 2)

**Paper 18 → 13 pages; note 125 → 131.**

**What stays in the paper:**
- the scope statement;
- Figs. 1–4 and two compact tables (estimators; joint decisions);
- the familywise statement with its assumptions;
- the margins sentence;
- the NuWro CH clause;
- the calorimetric-response and hybrid-null conditions;
- every sentence the receipt gate checks.

**What moved to named note sections:**
- the definition, generator, estimator-matrix, validation-design, generative-model and reporting tables;
- Appendix A, verbatim (note §B.5);
- the Sec. VI and VIII detail;
- Figs. 5–6;
- the repository-record citations (P7).

The 12-page target would require moving limitation text, so the pass stopped at 13.

**Independent review:**
- **1 MATERIAL, fixed.** The note citation pinned a 10-11 tree that has none of the moved material. It now points to the
  repository's main tree, with a note that the archival identifier replaces the link at deposit.
- **6 MINOR, fixed:**
  - the strength of the two-universe test;
  - a printed record pointer;
  - "(moved from the article)" captions;
  - the note's map section restated without mechanism claims, with the regularization-bias caveat;
  - the note's condition (i) wording;
  - the release-appendix figure list.
- **1 NOTE applied:** the GEANT4 bands' inclusion is now stated.

**Build `mrs2`:** rc 0, gates PASS (15/15), no unresolved references, and the swallowed-text checks are clean.

## 8. Primer and note summaries brought in line with the paper (2026-10-21)

**Files changed:**
- the primer (`main_primer.tex`, `primer_body.tex`);
- the note's executive summary, summary and abstract (`sec_execsummary.tex`, `sec_summary.tex`, `main_note.tex`);
- the status table (`result_status_rows.tex`);
- stale body statements in `sec_validation.tex`, `sec_3d.tex` and `sec_eavailw.tex`.

**What changed:**
- **The primer is reframed as a validation study.** Its title is now "How well does a machine-learning unfolding method
  work on neutrino data?".
- **The paper's narrowed claims and test conditions** are carried, including the NuWro CH sentence verbatim.
- **Withdrawn mechanism and "first" claims are removed.**

**Review.** An independent review found 2 MATERIAL problems (a count-type CH statement; the primer abstract lacking
the rejections' limits), 1 coupled MATERIAL (the status table) and 13 MINOR. All are fixed, and the build `mps2` gives
rc 0, gates PASS and no unresolved references.

**Pages:** primer 15, note 133, paper 13.

## 9. Note depositability pass (2026-10-21)

### Mechanical

- **Deposit export.** `build_all.sh --export-deposit DIR` writes a comment-free, flattened source tree with its
  figures, then checks it: no comments remain, it builds standalone, and its PDF text equals the note's.
- **Fixed title.** "Version 1.0 (review), 20 October 2026".
- **Visible holds.** "[funding statement pending]" and "[snapshot identifier pending deposit]".
- **Body pointers.** Every internal pointer left in the body is routed to App. G ("Provenance"), and the body states
  the substance.
- **Lint.** `check_body_pointers.py` runs before the build and fails it on internal pointers in the title block and
  body.
  - Self-test: 24 cases.
  - It found 18 hits on main, and 0 after the pass.
  - The build tests (49) pass.

### Judgment

- **§10 is self-contained.** It quotes the six pre-registered conditions verbatim, with bracketed annotations. It
  also carries the lost-draw disposition, the projection p-value table and the recoil table.
- **Governance language** in §9.3–9.6, Table 1, the executive summary and elsewhere is rewritten as criterion,
  value and outcome.

### Review

An independent review found 1 MATERIAL and 7 MINOR issues. All are fixed except the export tests (m7):
- Table 1 keeps "readiness … has not been established".
- "no recovered draw".
- "was constructed".
- The metadata's "not to be used".
- The annotation is placed correctly.
- The lint covers the title block.
- The export refuses `../` paths.

### Open for Joseph

- **Where App. J goes.** The superseded values are not moved.
- **The funding text.**
- **The release-state sentence**, to be worded at deposit.
- **The deposit itself.**
- **The z-cv and 2D digests** moved from the body to Apps. H and G. The director accepts that move; Joseph may
  reverse it.

**Pages:** note 135, paper 13, primer 15.

## 10. Register loop, round 1 (2026-10-21, DECISION-20261021-joseph-ai-ack-and-register-loop)

**Baseline scores** (paper at `e5ae5b11`, director's scratchpad `xmodel/r8/`):
- GPT-6.1-sol: register 3/5, readiness "nearly";
- Gemini: 3.5/5, "nearly".

**Round-1 edits** (paper and note sources only):
- Sec. VI renamed "Uncertainty estimates and their validation".
- Former Sec. VII (descriptive comparison) folded into the application section as its first subsection. The
  application section is now Sec. VII, "Application: comparison with generator predictions", and the conclusions
  are Sec. VIII.
- Repeated scope statements consolidated into Sec. I; audit phrasing rewritten as criterion, value and outcome.
- Abstract simplified along the GPT-6.1-sol rewrite (about 149 words).
- The lost-pseudo-experiment paragraph moved into the decision-rule subsection.
- AI acknowledgment condensed, per item 1 of the decision. It points to the note's full statement, which is
  unchanged and carries the tool versions (`main_note.tex`, the acknowledgments).

**Rejected suggestions.** Gemini's rewrites were not adopted where they dropped or changed a fact:
- its post-hoc paragraph, which removed who had seen the data residuals and when the budget extension was decided;
- "computationally prohibitive" as the reason the covariance was not regenerated, which no record supports.

**Rescoring** (`xmodel/r9/`, on build `mrg1`):
- GPT-6.1-sol: 3/5, "nearly";
- Gemini: 3.5/5, "nearly".

Both models' remaining requests are structural, not register:
- a summary table linking each finding to its configuration, test and limitation;
- the five-observable coverage test moved into Sec. VI;
- Sec. VII C–D condensed, with the sequential-sampling argument and development chronology moved to the note;
- the generator tests made more clearly subordinate;
- a clearer diagnosis of the recovery failures. IBU-1 and JIT-1 are specified for this
  ([`IBU1-SPEC.md`](IBU1-SPEC.md), [`JIT1-SPEC.md`](JIT1-SPEC.md)).

**Independent two-direction review** (of build `mrg1`): 2 MATERIAL, 4 MINOR. All fixed (build `mrg2`):
- M1: the condensed acknowledgment had narrowed what the tools assisted with. Restored to "substantial assistance
  with the analysis code, statistical procedures, computing campaigns, independent recomputations and reviews,
  figures, and manuscript drafts".
- M2: "within the implemented simulation model" restored to the methodological-contribution sentence.
- m1: "calibrated in simulation" restored in the abstract.
- m2: the projection study's ensembles and independent reproduction restored to the paper.
- m3: the post-hoc pointer now cites Secs. VII C and VII E.
- m4: "global assessments of the hybrid nulls".
- Also: "the Tune v1 map", and stale section numbers in source comments.

**Order deviation.** The decision says each round is reviewed before the models rescore it. Here the rescoring ran in
parallel with the review, so the models scored `mrg1`, not `mrg2`. The review's fixes restore qualifiers and facts
and do not simplify the register. Re-running the rescoring on `mrg2` would not change the stop decision below.

**Mechanics** (`mrg2`): rc 0; both gates PASS (Sec. IV receipts 15/15); no unresolved references;
`swallowed_text.py` flags 0. Pages: paper 13, note 135, primer 15.

**Stop.** Neither rating rose between the two rounds, so the decision's stopping rule ends the loop after round 1.
A structural round, built from the list above, is offered to Joseph. It is not started.

## 11. Standalone note repository synced (2026-10-21, Joseph: "push to the analysis note only repo")

- **Canonical:** `MINERvA-OmniFold` main at `4afaba5ca1b157c7a1f99ac9a5cda99731f55372` (PR #204 merge).
- **Standalone:** `MINERvA-OmniFold-Analysis-Note` main at `8b08b464fc67d6d4c613d9f238f02c2f2d9cb5a3`. This was
  checked with `git ls-remote` after the push. The previous head, `95b3474`, was the sync of `a5ac7380` (PR #113,
  2026-10-13).
- **Content:** all 141 tracked files under `docs/analysis-note/` at `4afaba5c` are byte-identical in the standalone
  checkout (`cmp`, checked before and after the build). The standalone repo's own `AGENTS.md` and `.gitignore` are
  kept.
- **Reverse direction:** the standalone history's only non-sync commits (the two Overleaf commits of 2026-10-11) are
  a whitespace toggle that cancels out, so nothing needed carrying back.
- **Standalone build** (`build_all.sh`): rc 0; body-pointer lint and struck-value containment PASS; no undefined
  references. The Sec. IV receipts check skips by design outside the canonical layout; it passed 15/15 in the
  canonical build `mrg2`. Pages: note 135, primer 15, paper 13, PET note 26.

## 12. Register loop, round 2: the structural round (2026-10-21)

**Asked for by Joseph.** The record is [`REVERSE-OUTLINE-R2.md`](REVERSE-OUTLINE-R2.md), which holds:
- the request, verbatim;
- the one-sentence reverse outline and the structural diagnosis drawn from it;
- the plan;
- Joseph's approval of the D-ID claim addition, and his reading of "move to the note".

**Two commits:**
- **Structural.** The outline is now:
  - Sec. I: the coverage/calibration distinction stated as the organizing idea; Table I (findings) replaces the
    listed results;
  - Sec. IV: the 2D benchmark with its covariance;
  - Sec. V A–E: five-observable bias, coverage, stability and precision;
  - Sec. VI: "What limits the estimator", new;
  - Sec. VII: condensed, with the recoil-response subsection folded into condition (ii);
  - Sec. VIII: shortened to refer to Table I and Sec. VI.

  Numbers and bookkeeping moved to note sections that already print them. Each paper site carries a
  `% Register round 2:` comment naming the note line. Every limitation and post-hoc disclosure is still at least a
  clause in the paper.
- **The D-ID claim addition**, approved by Joseph:
  - a paragraph in Sec. VI;
  - `\paragraph{Comparison with exact binned unfolding.}` in note `sec:val-departure`, which absorbs the note's
    former short summary in the coverage subsection;
  - the provenance row repointed to the new section.

  Source: `state/next-preparation-20261009/d-id/REPORT.md` §9.2, §9.3 and §11.

**Writer and fixes.** A writer subagent did the edit. The director fixed:
- the merge of the duplicate D-ID text in the note;
- "show" to "point to" (Sec. VI);
- note line citations shifted by the edit.

**Independent two-direction review** (on build `mrg4`): 4 MATERIAL, 7 MINOR and 6 NOTE. All MATERIAL and MINOR
findings are fixed, and N1, N3 and N6:
- M1: "with the detector response fixed at the simulation's" restored to the D-ID scope, in both documents.
- M2: "no *tested* reporting definition" in Table I.
- M3: the generator-W clause's "GENIE CV and NuWro without their 50–100 GeV samples" restored.
- M4: the carry-over list no longer calls the coverage test's truth change generator-sized.
- m1: the conclusions again carry "its quoted statistical block has had no coverage test" (DECISION-20261018 J3 C4
  site).
- m2: "statistical intervals" in Table I.
- m3: the D-ID convergence clause now says the values are last iterates, and the note gives 9–34 of 109.
- m4: a forward reference added in condition (ii).
- m5: the note stub travels in the D-ID commit.
- m6: provenance row repointed.
- m7: Table I column widths.

The fixes made the paper 14 pages. Repetition was trimmed to return it to 13: Sec. VI's opening, the D-ID lead
sentence, one clause each in Sec. I and the conclusions. Each trimmed fact still prints elsewhere in the paper.

**Rescoring** (`xmodel/r10/`, on the final build `mrg9`, after the review this time):

| | round 1 (r9) | round 2 (r10) |
|---|---|---|
| GPT-6.1-sol | 3/5, nearly | **3.5/5**, nearly |
| Gemini | 3.5/5, nearly | 3.5/5, nearly |

- **GPT-6.1-sol:** "Sec. VI provides a useful synthesis and should remain". The inverse-problem diagnostic "provides
  some of the paper's most useful explanation of *why* the method fails". Remaining asks:
  - a shorter abstract, with the generator application in one sentence;
  - one concise scope paragraph, with the qualifications moved to their sections;
  - Sec. VII C–D shorter;
  - internal-process words ("gates", "frozen", "separately authorized release decision") replaced;
  - Table I less dense.
- **Gemini:** asks for Sec. VI to merge into Sec. V as V F, and for Sec. VII's decision-rule detail to move to an
  appendix. It also asks for the internal commentary in the Fig. 3 and Fig. 4 captions to be removed.
- **Not adopted:**
  - Gemini's three rewrites, which drop the p-value visibility, the undocumented rate, and "lost independently …
    not shown";
  - its claims that the note is "private" (it is public at the cited URL) and that the target difference is
    "uncorrected" (the hydrocarbon replays are in Sec. VII E).

**Loop.** One rating rose, so the stopping rule does not end the loop. Round 3, the last allowed, takes the
register asks above.

**Mechanics** (`mrg9`): rc 0; gates PASS (Sec. IV receipts 15/15); no unresolved references; `swallowed_text.py`
flags 0. Pages: paper 13, note 135, primer 15. The structural-only commit was built separately (`mrg9s`).

## 13. Register loop, round 3, and the end of the loop (2026-10-21)

**Edits** (writer subagent; paper body, abstract and one figure title):
- Abstract shortened from 149 to 135 words. The validation findings come first; the generator application is two
  sentences, with all six of its required caveats.
- One scope paragraph in Sec. I. Each qualification stays as a clause, with a pointer to its section.
- Internal-process vocabulary replaced in printed text: "gate" became "acceptance threshold", "the frozen design"
  became "the design fixed in advance", "development truths" became "the truth changes of the estimator's
  development studies". The plain "production" wording is gone.
- GPT-6.1-sol's two r10 rewrites adopted, adapted to keep every fact.
- The Fig. 3 and Fig. 4 captions are plain statements. The director corrected the writer's Fig. 3 text: "neither
  panel is a held-out test" overstated the old caption, whose panel (b) shapes were held out when the estimator was
  chosen. The new text says which seeds each panel uses.
- Table I is a full-width `table*`.
- Condition (iv)'s procedure moved to the note (`sec_joint.tex:369-376`).

**Independent two-direction review** (build `mrg11`): 0 MATERIAL, 10 MINOR, several NOTE. All MINOR findings are
fixed, plus the Fig. 4 verdict wording:
- the central values "retain the bias" (a new inference) became "whose bias in simulation is given in Sec. V A";
- the pre-registration sentence again covers the first pseudo-experiment of the calibration and power ensembles;
- "a bounded extension of the calibration's computing budget was decided while … visible" (the decision, and the
  budget, not the per-null cap);
- D-ID's truths are "the truth changes of the estimator's development studies";
- Table I's Test cells say what was tested;
- the scope sentence says "the cross section equals a prediction on every cell";
- "calibrated size";
- the generative-model pointer;
- the conditions pointer names its note section;
- the shift-sizing sentence untangled.

**Figure.** The Fig. 4 panel title said "gate". It is regenerated from its committed receipts by
`figures/methods_m3/fig_m3_coverage.py`, with "threshold" and a shortened title (the first attempt clipped "153").
All six of the script's number checks print OK. The PDF text differs from the previous figure only in the title.

**Pages.** Three trims of short-tail paragraphs and a one-line table caption bring the paper back to 13 pages. The
cross-covariance clause, "the treatments" and "the covariance of Sec. V D" each keep their fact.

**Final rescoring** (`xmodel/r11/`, on the final build `mrg16`):

| | r8 (before) | r9 (round 1) | r10 (round 2) | r11 (round 3) |
|---|---|---|---|---|
| GPT-6.1-sol | 3/5 | 3/5 | 3.5/5 | 3/5 |
| Gemini | 3.5/5 | 3.5/5 | 3.5/5 | 3.5/5 |

All four rate the paper "nearly" ready.

- **Scoring noise.** GPT-6.1-sol's first r11 example of internal-record register is its own r10 rewrite, adopted
  nearly verbatim. Its scores therefore vary by about ±0.5 between runs on similar text.
- **Stop.** The loop's cap of three rounds is reached, and 4.5/5 was not reached. Round 3 is adopted on its
  independent review, not on the scores.
- **Both models' remaining asks:**
  - Further reduction of the chronology in Sec. VII.
  - "Why unfold before testing" moved to the opening of Sec. VII (GPT).
  - A compact quantitative display of the D-ID comparison (GPT, twice).
  - The note cited as Supplemental Material, or by stable references, instead of a repository pointer (both). This
    is tied to the deposit decision, which is Joseph's.
  - The `[HOLD]` items, which are Joseph's.
- **Scientific asks (not register).** A controlled comparison that separates background treatment, classifier
  approximation, regularization and interval construction (IBU-1 and JIT-1, after 2026-10-27), and a data-like
  null rejection-rate check.
- **Not adopted.** Gemini's rewrites that remove the chronology where it bears on interpretation. Its claims that
  the note is "unpublished" or "informal" (it is public at the cited URL, and the deposit is Joseph's decision) and
  that the paper was "unblinded".

**Mechanics** (`mrg16`): rc 0; gates PASS (Sec. IV receipts 15/15); no unresolved references; `swallowed_text.py`
flags 0. Pages: paper 13, note 135, primer 15.

## 14. Standalone note repository synced again (2026-10-21)

- **Canonical:** `MINERvA-OmniFold` main at `88354ebc` (PR #207 merge), which includes PRs #206 and #207.
- **Standalone:** `MINERvA-OmniFold-Analysis-Note` main at `b2f22c8272775031db02ed1b0f59c0519c95ce18`, checked
  with `git ls-remote` after the push.
  - The remote held two commits by Joseph since §11: `5961b6c` (Updates from Overleaf) and its merge, `69febb7`.
  - The merge's tree is identical to the §11 sync `8b08b46`: the Overleaf branch was based on the 10-13 sync and only
    caught up. Nothing needed carrying back, so the checkout was fast-forwarded before the copy.
- **Content:** six files changed, and all 141 tracked files are byte-identical to `88354ebc` (`cmp`, before and after
  the build).
- **Standalone build:**
  - `build_all.sh` rc 0; the body-pointer lint and struck-value containment pass; no undefined references.
  - The Sec. IV receipts check skips there by design.
  - Pages: note 135, primer 15, paper 13, PET note 26.

## 15. Register loop 2, round r12: the fresh rewrite (2026-10-21, DECISION-20261021-joseph-register-loop-2)

**Why.**
- GPT-6.1-sol's main complaint in rounds r8–r11 was the same each time: the paper "reads partly like an internal
  validation record".
- Joseph ruled that limitations and after-the-fact disclosures may move to the note where they print. That ruling
  carries the director's guardrail: a qualifier stays only where leaving it out makes a printed sentence false.
- **Method.** A writer with no history of the text did the work:
  - reverse-outlined `paper_body.tex` at 1a74560c;
  - built a fact ledger;
  - wrote a target outline;
  - rewrote each section from the outline and the ledger instead of patching sentences.

**Records** (in `r12/`):
- `OUTLINES.md`, before and target.
- `ledger.md`, 341 rows, and its checker `check_ledger.py`. The checker is run as `python3 check_ledger.py
  <worktree>`. It reports 457 probes and 0 failures, and a planted bad probe fails it.
- `WRITER-REPORT.md`, the first pass.
- `REVIEW.md`, the independent two-direction review and re-review.

**What changed in the paper:**
- **Length.** Printed prose went from 7,535 to 6,558 words. The paper stays at 13 pages.
- **Moves to the note.** Chronology, acceptance-rule bookkeeping, lost-pseudo-experiment recovery and derivations
  move to the note sections where they print.
- **Additions to the note.** Five facts printed only in the paper were added to the note:
  - §8.2, the W-redundancy reading of the test metric's near-degenerate directions;
  - §9.2, the cell holding the 74% residual;
  - §9.3, the 200-iteration values for W3 and q3;
  - §9.4, the joint-test estimator's iteration rule;
  - §10.7, the unmeasured power comparison.
- **Structure.**
  - "Why unfold before testing" now opens Sec. VII.
  - The introduction has one scope paragraph.
  - New Table III shows the D-ID comparison with exact binned unfolding. Its numbers are from note §9.3 and the D-ID
    REPORT §9.3.
- **Pointers.** All 38 descriptive note pointers now print as numbered sections ("Ref. [14], Sec. N"). They work
  through `xr-hyper` and `main_note.aux`, which build_all builds first. A missing label fails the build.
- **Protected text.** The `\pubhold`, funding, acknowledgment, AI-acknowledgment and data-availability text is
  byte-identical, by source hash and by printed text.

**The review.**
- **First verdict: ADOPT-AFTER-FIXES.** It had four blocking findings, each a claim read stronger than its evidence
  or a caveat lost:
  - "checked against" had become "agrees with";
  - the five-iteration sentence had lost its rule;
  - the rebuilt 2D band read as the quoted block;
  - the 135 MeV caveat that its materiality is not established was gone.
- **Should-fix findings: eight.** All were fixed by the writer.
- **Re-review.** All fourteen findings are resolved. It found one recast that overstated:
  - "These corrected evaluations do not change the decisions";
  - the director changed it to the note's own reading, "are descriptive and do not re-grade the recorded decisions".
- **Optional fixes applied by the director:**
  - "when rerun";
  - "before it was fixed";
  - Table III placed before Sec. VI, so it now prints on the page of its first citation.
- **Not adopted.** "Applied to the stored outputs" for the recomputation sentence: not verified against its source.

**Carried to Joseph for deposit (not done):**
- the paper's arXiv source must include `main_note.aux`, or have the note section numbers written in;
- Ref. [14] should cite the posted version of the note rather than its repository branch.

**Mechanics** (`builds/r12`):
- build_all rc 0, Sec. IV receipts 15/15;
- no undefined references, and no `??` in the paper text;
- `swallowed_text.py` flags 0;
- pages: paper 13, note 136, primer 15.

**Rescoring.** Not done yet. It waits for the rater calibration (DECISION-20261021-joseph-register-loop-2 item 5),
which picks the prompt and the target.

## 16. Rater calibration, and the r12 scores (2026-10-21)

**Calibration** (`rater-calibration/REPORT.md`; asked for in DECISION-20261021-joseph-register-loop-2 item 5).
- **Anchors.** Three published PRD papers were blinded and rated alongside our paper. With the rubric-anchored
  prompt P1:
  - sol gave them 3.5, 3.5 and 4.0 (mean 3.67);
  - Gemini gave them 3.39 on average;
  - no anchor scored above 4.0 from either model on any prompt.
- **Target.** The 4.5/5 target is replaced by the calibrated one: **P1 with sol ≥ 3.5 on 3 of 3 runs.**
- **Prompts:**
  - **P1 with sol** gives the absolute score. Its sd is 0.12, and it resolves our own revisions (2.50 → 3.00).
  - **P2** is the go/no-go test between versions: new against previous, both orders, both models.
  - **P3** is a source of flagged-sentence lists, not a metric.
  - **The "revised several times" framing** (P0 against P0n) has no measured effect on our paper.

**r12 scores** (`r12/scores/`). Rater copy: `make_rater_copy.sh` on `wt-reg2` at 5f717bf4. Its text is identical to the
hand-built copy, with the holds removed and the data-availability text kept.

| prompt | sol | Gemini |
|---|---|---|
| P1, r12 | 3, 3, 3 → 3.00 | 2.5, 2.5, 2.5 → 2.50 |
| P1, r11 (from the calibration) | 3, 3, 3 → 3.00 | 2, 2.5, 2 → 2.17 |
| P2, r12 against r11 (A/B and B/A orders) | r12 wins both orders (strength 2, 2) | r12 wins both orders (strength 3, 2) |

- **Go.** r12 wins 4 of 4 comparisons, sol shows no order flip, and P1 with sol does not fall. r12 is adopted.
- **The target is not met.** P1 with sol is 3.00, against the 3.5 target.
- **The passages sol quotes in all three runs, and what governs each:**
  - The design-review and budget-extension sentence in Sec. VII C, quoted 3 of 3 times. It is kept under the guardrail,
    but it can be phrased as a design fact.
  - The data-availability release bookkeeping, quoted 2 of 3 times. That text is Joseph's protected text.
  - The rebuilt-band paragraph in Sec. IV B.
  - The hydrocarbon-replay sentence in Sec. VII E.
- **Gemini's rewrites of the 135 MeV caveat again assert what is not established** ("well below the experimental
  uncertainties"). They are not adopted.

## 17. Register loop 2, round r13; the note's baseline (2026-10-21)

**Round r13** (records in `r13/`). A fresh writer worked from the rater flags on r12: both P3 runs from sol, and the P1
quotes.
- **Triage of the 47 flagged sentences** (`triage.md`):
  - 4 moved to the note, wholly or in part;
  - 27 were restated as a design fact or a scope statement beside the claim they bound;
  - 9 were left as standard register or as needed qualifiers;
  - 7 sit in the protected Data availability text.
- **Other edits:**
  - the three passages sol quoted in every r12 run were rewritten (Sec. VII C, IV B and VII E);
  - 7 long sentences were split.
- **Only `paper_body.tex` changed.** `main_paper.tex` is byte-identical to main.

**The review** (`REVIEW.md`, independent, two directions).
- **Verdict: ADOPT-AFTER-FIXES**, with nothing blocking.
  - No number was lost.
  - The protected text has the same hash.
  - The four moves print at the cited note sections.
- **Three should-fix findings,** fixed by the writer:
  - **Hydrocarbon sentence.** It again says the replays "are descriptive and do not re-grade the decisions of Table IV,
    which concern each prediction on the target it was generated for and stand". This is the note's reading in
    §10.9.
  - **Five-iteration rule.** Its scoped statement, with the rule's measure, is restored in the paper.
  - **Rebuilt-band rescoring.** It is called post hoc again.
- **Item for the note pass.** Note §9.4 (`sec_5d.tex:311–313`) prints the rule unscoped: "only if they reduced the
  model dependence; none did". That conflicts with "D1 and W1 improve slowly" in the same section.

**The r13 scores** (`r13/scores/`). They were taken on the pre-fix r13 text; the three fixes are each a single sentence.

| | sol | Gemini |
|---|---|---|
| P1, r13 | 3, 3, 3 → 3.00 | 3, 2.5, 2.5 → 2.67 |
| P2, r13 against r12 | r13 wins both orders (strength 1 and 2) | r13 wins both orders (2, 2) |

- **Go.** r13 is adopted. The calibrated target (P1 with sol ≥ 3.5) is not met.
- **sol's P1 score has stayed at 3.00 for r11, r12 and r13,** while P2 preferred each new version in 4 of 4 runs.
- **What sol now quotes:**
  - the Data availability release bookkeeping, in 3 of 3 runs (protected, Joseph's);
  - the guardrail-kept scope sentence of the binned diagnostic in Sec. VI, 3 of 3;
  - the lost pseudo-experiments in Sec. VII C, 2 of 3;
  - the design sentence, 1 of 3.

**The account switch.**
- On 2026-10-21 codex-school reported "Your workspace is out of credits", so one r13 P2 run failed twice.
- `run_x.sh` gained a `sol2` route: the same model, gpt-6.1-sol, through codex-school2, which is on the account
  allowlist.
- **Routing check.** A smoke call returned "model: gpt-6.1-sol".
- **Equivalence check.** sol2 scored r12 at P1 3, 3, the same as sol's 3, 3, 3.
- The failed P2 run was redone with sol2.

**Data availability proposal** (`r13/DA-proposal.md`, not applied). It shortens the paragraph from about 262 words to
about 140, and sends every fact to note App. H. It is Joseph's decision, because:
- the text is protected;
- the draft would reverse the earlier P6 ruling, that the package's Fig. 1 limitation stays in the paper;
- one proposed note sentence rests only on RC7's own README.

**The note's baseline** (`rater-calibration/NOTE-BASELINE.md`; prompt P1N).
- Two published long technical papers set the anchor: T2K, PRD 91, 072010, and ProtoDUNE-SP, JINST 15 P12004. They
  score 3.875 with sol.
- The note's 15 pieces score 2.83 with sol and 2.30 with Gemini.
- The appendices are worst: App. J 2.25, Apps. D–G 2.25, Apps. H–I 2.50.
- **Batch 0** (a glossary of project terms applied across the note) is in progress.
- **Apps. G–J** are records by design. Whether they stay, are shortened or move to the repository is Joseph's
  decision. It was already pending as "App. J placement".

**Mechanics** (`builds/r13`):
- build_all rc 0, Sec. IV receipts 15/15;
- no undefined references, and no `??`;
- `swallowed_text.py` flags 0;
- the ledger check: 341 rows, 470 probes, 0 failures;
- pages: paper 13, note 136.

## 18. Note register pass, batch 0: the glossary (2026-10-21)

**Why first.** The note's baseline (`rater-calibration/NOTE-BASELINE.md`) found two kinds of complaint spread widely:
project jargon in 12 of 15 pieces, and development history in 10. If each chapter batch renamed terms on its own,
the note would end up inconsistent. So one vocabulary was fixed first.

**What was done** (records in `note-g0/`). A writer with no history of the text made 192 asserted edits in 19 note
files, applied by `apply_glossary.py`.
- **Status terms** were reworded, and each kept as a concept:
  - "in use" → "used in this note";
  - "constructed, not adopted" → "computed but not used for any result in this note". In two places the wording is "not
    used for the quoted central values" instead, because the generator tests do use those products.
  - "report-only" → "reported but not used for the decisions";
  - "frozen" → "fixed" or "predeclared". In the lost-draw recovery it becomes "as in the primary evaluation".
  - "footing" → "background treatment".
- **Other project terms** and tracker IDs were cleared, about 20 of them.
- **Labels a reader needs to reproduce the analysis** moved to a "Labels used in the repository" table in `app_guide.tex`.
- **Code identifiers** are kept only where a reader needs them.

**What was not touched:**
- Apps. G–J, pending DECISION-20261021-joseph-da-and-note-records item 2;
- the acknowledgments, the AI-use statement, `\pubhold`, funding, release text and the verbatim specification quote.

**The review** (`REVIEW.md`, independent, two directions, with a re-review).
- **First verdict: ADOPT-AFTER-FIXES.**
  - **One blocking finding.** A verbatim label required by binding addendum 7, ruling 3 had been reworded. It is
    restored and is now a protected span.
  - **Ten should-fix findings** where a status or scope shifted, all fixed against their sources.
- **Re-review: ADOPT.** The reproduce steps in `REPORT.md` §7 were corrected by the director.

**S11, a claim correction committed on its own.** The joint-test chapter's opening said the tests evaluate "simple
hypotheses". They evaluate hybrid nulls, as `M2-AUDIT.md:39-40` records and `M2-ARCHIVE-CHECKS.md` confirms. It now
uses the executive summary's own words: "hybrid null hypotheses about five predictions". It is a separate commit, so
Joseph can revert it; `apply_s11.py --revert` also reverses it.

**Open, for the later batches:**
- Q11: whether the split-varied band is part of the five-axis covariance used in this note.
- The unscoped iteration-rule sentence in §9.4 (§17 above).
- "Marginal anchors agree" in the shared result-status table, and a figure label that reads "anchor ratio".

**Mechanics**, after the rebase onto 4a3f3b27:
- build_all rc 0, RESULT PASS, BODY-POINTERS PASS, Sec. IV receipts 15/15;
- no undefined references, and no `??`;
- the paper, primer and PET-note texts are unchanged by the batch, and all 205 label numbers are unchanged;
- `swallowed_text.py` flags 0;
- the ledger check: 192 rows, 383 probes, 0 failures, and its self-test passes;
- pages: note 138.

## 19. Round r14 not adopted; the paper's register loop stops (2026-10-21)

**Round r14** (branch `stageF/register-r14-20261021` at `ed117866`, pushed and NOT merged; records in `r14/`).
- **What it did.** Its theme was "scope inside the claim": each flagged caveat was restated with its scope as the
  claim's subject or opening phrase.
- **What it moved to the note,** where each item prints:
  - the lost-pseudo-experiment counts, to §10.6;
  - the binned diagnostic's exclusions, to §9.3.
- **The review** (`r14/REVIEW.md`) found it ADOPT-AFTER-FIXES. Its fixes were applied:
  - "including the recovered outcomes changes no decision";
  - A2's independence requirement stated as not shown;
  - five wording NITs.

**What was scored** (`r14/scores/`, sol2 = gpt-6.1-sol through codex-school2). Each was rated against `4ba0dd2f`, which is r13 plus the
shortened Data availability (PR #212):

| | sol2 | Gemini |
|---|---|---|
| P1, main at `4ba0dd2f` | 3, 3, 3 | 2.5, 2.5, 2.5 |
| P1, r14 | 3, 3, 3 | 2, 2.5, 2.5 |
| P2, r14 against main, A/B order | main wins (strength 1) | main wins (strength 2) |
| P2, r14 against main, B/A order | main wins (strength 1) | r14 wins (strength 2) |

- **Gemini picked document B in both orders,** which is position bias.
- **sol2 prefers the previous version in both orders.** Under the go/no-go rule (rater-calibration REPORT §4: the new
  version must win at least 3 of 4), r14 wins 1 of 4. **It is not adopted.** Main keeps r13 plus the Data availability
  change.

**The stopping rule is met.** DECISION-20261021-joseph-register-loop-2 item 5 stops the loop when the blind
side-by-side no longer prefers the new version, and here it does not. **The paper's register loop stops.**
- **P1 with sol** has been 3.00 for r11, r12, r13, main at `4ba0dd2f`, and r14. The published anchors score 3.67.
- **The shortened Data availability did not move P1** (3, 3, 3), but sol no longer quotes it. Before the change, it
  quoted it in 3 of 3 runs on r13.
- **What sol quotes now:**
  - the hydrocarbon sentence "…are descriptive and do not re-grade the decisions of Table IV…", in 6 of 6 runs on main
    and r14;
  - the scoped five-iteration rule, in 3 of 6;
  - the lost-pseudo-experiment sentence, in 3 of 3 runs on main;
  - the A2 or design sentence.
- **Most of these are qualifiers the independent reviews required for accuracy** (r12 R1, r12 B2, r13 S1). The
  register the rater objects to now comes mostly from the guardrail, not from bookkeeping. Removing them would trade
  accuracy for score.

**Carried forward:**
- r14's A2 clause ("A2 also requires the pseudo-experiments … lost independently of their outcomes, which has not been
  shown") is not on main. Main says the error control holds "under A1 and A2", which is true as read. The note prints
  the gap in §10.3.
- r14's branch stays available, if Joseph wants either the clause or r14 itself.

## 20. The records leave the posted note (2026-10-21, DECISION-20261021-joseph-da-and-note-records item 2)

**Joseph's question: is the existing archival system good enough?** It was answered from an inventory
(`note-records/PLAN.md` §0 and §2).
- **For App. G (provenance) and for the record parts of Apps. H and I: yes.** Every repository path, known-issues row
  and ledger row they cite exists elsewhere. Only App. G's index of 29 tags, which maps note sentences to records,
  existed nowhere else.
- **For App. J (superseded values and withdrawn results): no.**
  - Its 39-row table of struck values, with replacements and reasons, exists only there.
  - The repository's retracted-values index holds 23 of its 64 struck numbers.
  - The verbatim withdrawn passages survive only in git history.
  - The struck-value containment gate reads App. J.

**What was done** (option C of the plan; records in `note-records/`):
- **A separately built internal document, `main_records.tex`.**
  - It holds Apps. G and J whole, and the record parts of Apps. H and I, moved verbatim.
  - It is built and gated by `build_all.sh`, and is never posted.
- **The posted note:**
  - It cites it as `NoteRecords2026`, in 82 citations replacing 87 pointers.
  - It keeps the deposit snapshot hold visible, byte-identical, in its release appendix.
  - It prints superseded values and "an earlier version" notices only through those citations.
- **The containment gate** now treats the posted note as an outward build, with two narrow, self-checking exemptions
  for live values that coincide with struck ones.
- **The no-loss proof.** `check_note_records.py` inventories the base (`records-inventory-base.json`, frozen at
  `4ba0dd2f`) and probes P1–P7. Its self-test fires on all 12 planted defects.

**Director's rulings on the plan's questions:**
- **Q1.** The PET note is out of scope. Joseph's plan posts the methods paper and the analysis note.
- **Q2.** The snapshot hold stays visible in the posted note.
- **Q3.** App. I's code identifiers stay as reader material.
- **Q4.** Records may print only in the records document, so the App. A parenthesis of superseded values is deleted.
  - Review F1 narrowed this: the current exact-split pair 0.051/0.405 is restored.
  - The executive summary's ", which an earlier version omitted" is also removed (ledger L9b).
- **Q5.** "Where App. J goes" (§9 above) is closed by this decision and this move.

**The review** (`note-records/REVIEW.md`, independent, adversarial, with its own checks).
- **Confirmed:**
  - nothing moved was edited;
  - every base label is defined exactly once across the note and the records;
  - all 82 citations name existing tags;
  - the only change to the paper is "App. H" → "App. G", twice.
- **Verdict: ADOPT-AFTER-FIXES.** All six should-fix findings were applied:
  - F1, the current pair restored;
  - F2, the production-number limits printed at the claim;
  - F3, a check-value sentence identifying the five-axis covariance used in this note;
  - F5, one name for the retired record;
  - F6, the hold's sentence subject;
  - F7 and F8, the containment end-of-sentence boundary and its exemption guard, both moved into the gate.

**Mechanics** (`builds/rec2`, on `e05c78c7`):
- build_all rc 0; RESULT, BODY-POINTERS and Sec. IV receipts 15/15 all pass;
- all five targets have no undefined references, no multiply-defined labels and no `??`;
- containment: the records carry 64/64; the posted note, paper and primer carry 0 of 69;
- RECORDS-MOVE PASS, and its self-test 12/12;
- `swallowed_text.py` flags 0;
- `test_build_all.py` passes 69/69, with `--mutate` 10/10; `test_check_sec4_receipts.py` passes 16/16;
- pages: note 119 (from 138), records 21, paper 13, primer 15, PET note 26.

**Remaining:**
- **Pin `NoteRecords2026`** (plan commit 3, after merge): to the merge commit on main, with a check that it is an
  ancestor and carries every cited tag.
- **Sync the standalone note repository.**
- **The register rewrite of the reader parts of Apps. H and I** is a later batch.

## 21. Standalone note repository synced a third time (2026-10-21)

- **Canonical:** `MINERvA-OmniFold` main at `b603f9cf` (PR #217 merge). It includes PRs #208–#217:
  - register rounds r12 and r13;
  - the shorter Data availability;
  - note batch 0 and S11;
  - the records move and its pin;
  - the test fix.
- **Standalone:** `MINERvA-OmniFold-Analysis-Note` main at `767abd55bd5a90daa12251e918ffec39cdf124ee`, checked with
  `git ls-remote` after the push.
  - The remote held two commits by Joseph since §14: `4578974` (Updates from Overleaf) and its merge, `7741241`.
  - Their only change is `test_build_all.py`'s mode, 755 → 644. There was no content change, so the checkout was
    fast-forwarded before the copy, and the sync restores the canonical 755.
- **Content.** Six new files:
  - `main_records.tex`, `app_release_records.tex`, `app_codebase_records.tex`;
  - `check_note_records.py`, `records-inventory-base.json`, `records-move-ledger.md`.

  All 147 tracked note files are byte-identical to `b603f9cf` (`cmp`, before and after the build).
- **Standalone build:**
  - `build_all.sh` rc 0, with five targets;
  - BODY-POINTERS PASS and RESULT PASS;
  - containment: records 64/64, posted note and paper 0 of 69;
  - RECORDS-PIN and the Sec. IV receipts check skip there by design.
  - Pages: note 119, paper 13, primer 15, PET note 26, records 21.

## 22. The analysis note's chapter batches (2026-10-21/22)

**Scope.** Joseph's DECISION-20261021-joseph-register-loop-2 item 2 puts the note in scope alongside the paper.

**After batch 0** (the glossary, §18) and the records move (§20), seven chapter batches rewrote the posted note. Each
had:
- a fresh writer, under `WRITER-BRIEF.md`;
- an independent two-direction review, under `REVIEWER-BRIEF.md`;
- fixes, and re-review where needed.

The records for each batch are in `note-<batch>/`: the outline, the fact ledger and its checker, the change list and
the review.

| batch | chapters | PR | review | what the review caught, among others |
|---|---|---|---|---|
| b7 | §10 joint tests | #219 | ADOPT-AFTER-FIXES | a false "records" sentence; two paper pointers that landed on nothing (the tertile rule for the coarse edges; the projected tests outside the Holm family), now printed |
| bhi | release and code appendices (G, H) | #220 | ADOPT-AFTER-FIXES, twice | an overstated tolerance; the replayed reading (the reviewer's first mapping was wrong, and the writer's evidence corrected it); the verifier sentence from the Data availability decision made accurate (pending Joseph's confirmation); the RC1 replay stated as by a separate AI agent session |
| b3 | §9, Apps. B–C | #222 | ADOPT-AFTER-FIXES | the §9.4 iteration rule scoped by its measure; "every result uses purity" scoped; the unmet obligation to revisit the background treatment confirmed real (RUNBOOK-20260807 §2, DECISION-20260815) |
| b6 | §§6–8 | #226 | ADOPT-AFTER-FIXES | §7.1 now prints the 135 MeV numbers the paper cites it for; a caveat re-attached to its region |
| b4 | §5, App. A, guide | #227 | ADOPT-AFTER-FIXES | the quoted block "not independently tested" corrected to "not tested"; the MAT check placed on the sweep before the flux fix; the ours-only χ² no longer called a goodness of fit |
| b8 | abstract, executive summary, §§1, 11, 12 | #228 | ADOPT-AFTER-FIXES | summaries that had drifted from the body: seed sensitivity measured on the companion covariances; the low-E_avail generators; no "complete" 2D budget; no independence claim for the unfold; the purity bias kept by the central values, not the uncertainties |
| b5 | §§2–4 | #235 | ADOPT-AFTER-FIXES | configuration (e) credited with the §9.2 studies, here and in App. C (b3's sentence, corrected in the same PR); Q11 resolved (the split-varied band is the ML term of the covariance used) |

**Invariants checked at every batch, on the delivered build:**
- the paper's printed text is byte-identical apart from the `\today` line;
- all 184 note label numbers are unchanged;
- 0 undefined references, and no `??`;
- struck-value containment: the posted note carries 0 of 69, and the records carry 64 of 64;
- RECORDS-MOVE and RECORDS-PIN pass;
- `swallowed_text.py` flags 0;
- the batch's own ledger has 0 failures, and its planted bad probes fire.

**After b5 merged,** the b8 ledger was re-run against the final text. Four support probes (E1d, E6, I3 and S1b) were
re-pointed to b5's wording of the same facts, and it passes with 0 failures.

**Main at `717ecf8b`:**
- build_all rc 0, with every gate passing;
- pages: note 120, paper 13, primer 15, PET note 26, records 21;
- RECORDS-PIN: 71 citations.

**Pending with Joseph:**
- the background-treatment revisit, now stated plainly in the abstract, the executive summary, §12 and App. C;
- confirmation of the narrowed verifier sentence;
- the separate "hybrid null hypotheses" commit;
- the "since superseded" label in place of "historical".

The re-rating against the note's baseline is in progress.

## 23. The note's register pass closes: re-rating, pairwise comparison, citation thinning (2026-10-22)

**The rubric re-rating** (P1N, the baseline's prompt and splitter; 50 runs; table in `note-rating/P1N-rerating-compare.txt`).
- **Whole note:** 3.04 with sol2 against the baseline's 2.83, and 2.46 with Gemini against 2.30. The anchors score
  3.875 and 3.375.
- **Body:** 3.08 against 2.98. With the drift control, sol2 shows +0.06 on unchanged text, so the body's change is
  within noise.
- **Appendices:** most of the like-for-like gain comes from the records move.
- **Only §6 reaches 3.5.**
- **Resolution:** sol2 gave 3.0 in 24 of 28 runs. P1N no longer resolves versions.
- **The cause found:** the records citations ("Ref. [38]", 70 of them; 71 counted) read as bookkeeping. 31 of the 126
  quotes contain one.

**The blind pairwise comparison** (P2N, before = r12 against after = the final1 pieces, both orders, both models;
`note-rating/P2N-pairwise-analyze.txt`).
- **After won all 48 runs:** 12 of 12 pieces per model, in both orders, with no position flip.
- **Sign test:** p = 0.00049 per model, counted by piece.
- **Weakest piece:** N09 (§10), the least-changed chapter, at sol2 strength 1.
- **Limit:** there is no before-against-before control.

**Joseph's decision** (DECISION-20261022-joseph-note-records-refs-and-stop):
- thin the citations to essentials;
- stop model-scored note rounds;
- he and Ben read next.

**The thinning batch** (PR #243; records in `note-thin/`).
- **Result:** 71 citations become 19, each where a reader needs the record to check a number or claim printed there,
  plus one guide statement.
- **Records removed with their citations:** six record sentences, each printed in the records at its tag.
- **Guarded by `check_note_records.py`:**
  - P6 accepts only listed drops;
  - P7 checks the listed targets in the tree and at HEAD;
  - P8 fails an unlisted or still-printed drop, and reports SKIP outside git;
  - every kept citation is pinned to its sentence;
  - self-test: 21 of 21 defects fire.
- **The independent review:** ADOPT-AFTER-FIXES. C07 and C71 were restored, the guide clause was restored, SKIP
  replaced PASS outside git, and the position probes were added.
- **Out of scope:** the records document's "Cited at" column is now stale for 17 tags. The decision froze that
  document.

**Main at `9c10f6c1`:**
- build_all rc 0, with every gate passing;
- RECORDS-PIN: 19 citations;
- RECORDS-MOVE passes;
- pages: paper 13, note 119, primer 15, PET note 26, records 21.

**The reading copy** for Joseph and Ben: `main_paper.pdf` `f3b02872…`, `main_note.pdf` `6b63c80d…` and
`main_primer.pdf` `8f14122f…`, in the director's scratchpad `reading-copy-20261022/` with SHA256SUMS.

**Pending with Joseph:**
- the background-treatment revisit;
- confirmation of the narrowed verifier sentence;
- the separate "hybrid null hypotheses" commit;
- the "since superseded" label.
