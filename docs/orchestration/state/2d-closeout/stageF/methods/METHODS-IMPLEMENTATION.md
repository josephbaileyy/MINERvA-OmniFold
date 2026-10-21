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
