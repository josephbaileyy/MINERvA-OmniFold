# Review of batch b8 (abstract, executive summary, §1, §11, §12)

Reviewer: independent, read-only. Before: `5fb31c7e` (origin/main = worktree HEAD). After: the uncommitted edits in
`S/wt-note-b8` (5 files modified, `git status` clean otherwise; nothing edited by me). Build: `S/plain-language/builds/note-b8/`.

## Findings

### B1. BLOCKING: the reproducibility limit is narrowed to an unused estimator
`sec_execsummary.tex:153` (Estimator stability).
- Before: "That rounding spread is already contained in the refit-per-replica data bootstrap (about 37% of its
  variance), so **the central value** is reproducible only to that size"
- After: "The candidate's refit-per-replica data bootstrap already contains this rounding spread (about 37% of its
  variance), so **its central values** are reproducible only to that size"
- What is wrong: the limitation now applies only to the candidate, which is not used for any quoted result. The body
  (`sec_5d.tex:220-226`) says "The baseline estimator's shifts, 0.8 and 2.5, place this instability in the estimator
  family … Central values are reproducible only to this size." KNOWN_ISSUES row 80 says "Reproducibility of the
  published central value is still limited to this size." The new text also drops the clause that places the
  instability in the estimator family. The writer was right to drop "as does its baseline", because nothing grades
  the baseline against the criterion, and the 2.5 is correct.
- Fix: "…and those of the baseline estimator by up to 2.5, so the instability belongs to the estimator family. The
  candidate's refit-per-replica data bootstrap already contains this rounding spread (about 37% of its variance), and
  central values are reproducible only to that size (§9.3)."

### B2. BLOCKING: a new independence claim in the abstract's first result
`main_note.tex:57-59`.
- Before: "An independent unfolding method reproduces the integral of the published double-differential cross section…"
- After: "**Unfolded independently of the publication**, the double-differential cross section … reproduces the
  published integral…"
- What is wrong: before, the method was independent. Now the unfold itself is said to be independent of the
  publication. The executive summary and §3.2 disclose that the LightGBM estimator "was chosen after both comparisons
  with the publication were known". As read, the new phrase claims an independence that the post-hoc estimator choice
  contradicts. The paper's abstract makes no independence claim.
- Fix: "With this method, the double-differential cross section in muon transverse and longitudinal momentum
  reproduces the published integral within about one percent, …". Or keep the old subject: "An unfolding method
  independent of the published one reproduces …".

### S1. SHOULD-FIX: the uncertainties are said to "keep" the purity bias
- Locations:
  - `main_note.tex:92-93`: "The quoted central values and uncertainties use the purity subtraction, …, and keep its
    bias of up to 4%";
  - `sec_execsummary.tex:136`: "the quoted central values and uncertainties keep the purity subtraction and its bias of
    up to 4%";
  - `sec_summary.tex:58-59`: "a purity-subtraction bias of up to 4% …, which the quoted central values and
    uncertainties keep".
- Before, all three said "the central values keep the purity subtraction and its bias".
- What is wrong: adding "and uncertainties" makes the uncertainties the subject of "keep its bias". That reads as
  though the uncertainties carry or include the bias. They do not: §9.2 says the bias "enters no quoted covariance",
  and the paper (`paper_body.tex:488-491`) says "the quoted uncertainties omit this bias". The §12 version reads worst.
- Fix: say that both use purity, and that only the central values keep the bias. For example: "The quoted central
  values and uncertainties use the purity subtraction; the central values keep its bias of up to 4% in the
  highest-W cells, which no quoted uncertainty includes."

### S2. SHOULD-FIX: "enters only (d) and (e)" is still an overreaching "only" (brief item 1)
`sec_execsummary.tex:136`; `sec_summary.tex:60-63`.
- The (d)/(e) mapping is correct. Table 3 (`sec_method.tex:203-229`) and Table `tab:validation-design-5d`
  (`sec_5d.tex:56-69`) give:
  - (c): purity, used for the background bias (§9.2) and the coverage test (§9.5);
  - (d): negative weights with a 100-tree/8-leaf refinement, used for the background bias and the generator-sized
    change (§9.2);
  - (e): negative weights with a 400-tree/31-leaf refinement, used for the held-out shapes (§9.3), the precision study
    (§9.4) and the generator tests (§10).
- So "(d) and (e) …, which give validation studies of §§9.2–9.4 and the generator tests" is correct, and it agrees
  with b5's corrected App. C sentence (`S/wt-note-b5/.../app_negweight.tex:18-22`). It also correctly excludes §9.5,
  which uses (c).
- The defect is "only". App. C uses the treatment outside the Table 3 configurations:
  - the 2D comparisons of App. C.4–C.5 and the measured size, on the histogram backend and with LightGBM;
  - the clipped Stay-Positive refinement on the 2D exact-split test (App. C.1);
  - the two-universe 5D spot check.
- The executive summary's subject is "Negative-weight background treatment", and §12's is "the refined negative-weight
  subtraction". Read as a statement about the whole note, "enters only" is false. It is the same defect class as the
  old "used only for the generator tests", though much smaller.
- Fix: follow b5's wording: "It is the background treatment of configurations (d) and (e) of Table 3, which give
  validation studies of §§9.2–9.4 and the generator tests (App. C compares it with the purity subtraction on the 2D
  measurement)". At minimum, drop "only".
- The abstract's "used in the generator tests and in some five-dimensional validation studies" has no "only", so it is
  true. It omits the 2D equivalence study (NIT N1).

### S3. SHOULD-FIX: an ambiguous antecedent for "a fifth" (Q4)
`sec_execsummary.tex:62`.
- Before: "a fifth of **the positive difference** sits in the single widest overflow cell".
- After: "most of the positive difference … lies at Eavail ≥ 0.8 GeV, much of it at W ≥ 1.8 GeV. A fifth **of it**
  sits…".
- "It" now most naturally means the part at high Eavail or high W. The body (`sec_eavailw.tex:208`) gives the corner
  as 22% of the whole positive excess, which is about 40% of the high-Eavail, high-W part.
- Fix: restore "A fifth of the positive difference". §12 already reads "A fifth of that positive difference" and is
  fine.
- The abstract's "a fifth of it" (`main_note.tex:84`) has the same ambiguity, inherited from the base ("A fifth of
  that excess"). Fix it the same way.

### N1. NIT: the abstract's negative-weight scope
`main_note.tex:94`. Optionally add "and in two-dimensional equivalence studies (App. C)". Not required: the sentence
is true as read.

### N2. NIT: the obligation sentence is written as process
`sec_execsummary.tex:136`, `sec_summary.tex:63-64`. "the obligation to revisit … before submission has not been met"
is process language. Its content, from App. C.6–C.7 and RUNBOOK-20260807 §2.1, is that no full five-dimensional
187-universe comparison of the two treatments at the publication configuration has been made.
- Option: "…a choice still to be revisited: no full five-dimensional comparison of the two treatments has been made
  (App. C.6–C.7)".
- This keeps what Joseph's OI-6 ruling requires: the choice is visible and recorded, and the text does not imply that
  the background treatment is irrelevant in 5D.

### N3. NIT: §11, published-region check
`sec_fps.tex:46`. "leaves the result in the published region unchanged at this level" is slightly stronger than
"does not damage". "agrees with the control at this level" says the same with less force.

### N4. NIT: executive summary, estimator choice
`sec_execsummary.tex:32`. "share the LightGBM estimator, which was chosen after both comparisons … were known; the
exact-split estimator is a cross-check" keeps the disclosure. "chosen over the exact-split estimator after both
comparisons were known" would also keep the fact that one estimator was selected over another.

### N5. NIT: lost-draw recovery
`sec_execsummary.tex:84`. "rerun and observed afterwards" became "rerun afterwards". The body fact that every submitted
draw has been observed (`sec_joint.tex:529-530`) is no longer in the summary. It is optional to restore, and nothing
is false.

### N6. NIT: unclear "cause" in §12
`sec_summary.tex:71-72`. In "Under a truth change …, the cause is a residual bias", it is unclear what "the cause"
refers to. Write "the miscoverage comes from a residual bias", as the executive summary does.

## Brief items

1. **Negative-weight scope.** See S2. The configuration mapping is right on both tables and agrees with b5. The
   "only" overreaches.
2. **Corrected claims:**
   - **Seed sensitivity on the two companion covariances.** Correct. `sec_5d.tex` "What the covariance supports" says
     "Items 1, 2 and 4 use two companion covariances … only item 3 describes this file".
   - **Four generators and the low-Eavail range in §12.** Correct. The four are the truth-level generators of §7.6, in
     the quasielastic–Δ dip, matching the executive summary and `paper_body.tex` sec:central.
   - **"complete" removed.** Correct. The new claim "whose blocks are all built with the central value's own learner"
     goes beyond the body's explicit list of three blocks (`sec_systematics.tex:8-11`). I checked the fourth against
     the source: the run-period unfolds use `--estimator lgbm` (`state/2d-closeout/period-unfold-20261014/scripts/sbatch_period_unfold.sh:76`).
     So it is true.
   - **"not independently validated".** This is the body's status (`sec_systematics.tex:352-353`) and the paper's
     (`paper_body.tex:462-463`). Acceptable.
   - **The baseline's 2.5.** Correct (`sec_5d.tex:220`; KI-80: 2.48). But see B1.
3. **The background-treatment obligation.**
   - It prints in three places, not four: the abstract, the executive summary and §12. §11 prints a different fact:
     that no extended-fiducial production with refined negative-weight subtraction has been run
     (`app_negweight.tex` "What the quoted extended-fiducial number used").
   - Each statement is accurate against App. C.6 ("an obligation to revisit the background treatment before
     submission, and that obligation has not been met"), RUNBOOK-20260807 §2 ("quoted on purity, revisited before
     submission") and DECISION-20260815 (OI-6). OPEN_ITEMS OI-6 records the revisit as still open.
   - Once per summary layer is appropriate. Joseph's ruling asks that the distinction be "obvious in the note", and
     none of the three is a repetition within a layer.
   - A minor scope point: the source obligation concerns the standard 5D chain. The abstract's "quoted central values
     and uncertainties …, a choice still to be revisited" sits beside the highest-W bias, so it reads as 5D. Acceptable.
4. **The roadmap.**
   - Every appendix of the posted note, A to H, has a row. A is covered by its subsections A.3.2, A.3.3, A.5, A.6 and
     A.7.
   - The rendered letters are correct: D (response mismatch), E (survey), G and H (release and code).
   - The added D row's "(protocol implemented, not yet run)" matches App. D's heading.
   - Records-move ledger L11: the three N probes print once each, and `app:release-audit` is absent. RECORDS-MOVE
     passes with 0 failures (writer's run).
5. **The abstract against the paper's abstract.**
   - In step, apart from B2.
   - The note's added "a choice still to be revisited" and "under six stated conditions" are disclosures or
     conditions, not claims, and both are in the paper's body ("six conditions", `paper_body.tex:923`).
   - "comparable in size to the published one" is weaker than the base's "reproduces its uncertainty scale" and
     matches `sec_results.tex:150`.
   - "regularization bias is largest in this region" now matches `paper_body.tex` sec:central. The base's "there" was
     ambiguous.
   - The abstract no longer mentions the estimator-seed limitation (the base's lead-in named it without stating it).
     The paper's abstract has none either, and the limitation still prints in the executive summary, §9.6 and §12.
     Acceptable.
6. **Protected text.** Byte-identical. `main_note.tex` before `\begin{abstract}` and from `\end{abstract}` on are
   identical to `5fb31c7e`, which covers the acknowledgments, the AI-use statement, the funding hold and the deposit
   hold. No verbatim or protected markers appear in the four section files. The release sentence "**no release has been
   tagged or deposited**" is unchanged, and its new surrounding text uses App. G's own wording.
7. **Writer's questions:**
   - **Q3 ("omits cross-source response terms").** Keep. The claim is the base's. The block sum's linearity assumption
     (`sec_systematics.tex` §4.5) supports it. Optionally write "nonlinear cross-source response terms", which is the
     records' term and is more precise, since independent linear responses do add.
   - **Q4 ("a fifth" against 22%).** Keep "a fifth". It is the paper's own wording for the 22% (`paper_body.tex:803-804`).
     Fix the antecedent (S3).
   - **Q5 (§§2–5 changed to §§2–6).** Accept. The comparison with the publication and the budget-size comparison are
     in §6; §§2–5 left them out.
   - **Q6 ("(p. 2)").** Accept. The executive summary is unnumbered, the base printed "(§)", and the new text renders
     "The executive summary (p. 2)".

## Register (E): surviving bookkeeping or meta passages, quoted exactly
1. "the obligation to revisit that choice of background treatment before submission has not been met" (executive summary)
2. "It enters only estimator configurations (d) and (e) of Table 3, which give validation studies of §§9.2–9.4 and the
   generator tests" (executive summary and §12)
3. "the projection's covariance is used in this note although it has not passed its specification's acceptance criteria"
4. "Four measured limitations apply to every result built from the five-dimensional covariance used in this note, the
   first …" (names one of four)
5. "within the study's rules and computing budget"
6. "including which of its objects already have fixed identities and which are still to be produced"
7. "rebuilding this note's PDFs assembles documents and reproduces no scientific result"
8. "The executive summary (p. 2) lists each result with its scope; this section states the conclusions they support."

Overall the register is much improved. The stacked trailing qualifiers have been split, and the editorial lead-ins
("Coverage and estimator-seed studies show…", "Where to find it", "These tests are valid only under stated
conditions") are gone.

## Mechanics (D)
- **Writer's checker.** I ran it myself: "ledger rows 134, probes 320, failures 0", and its `--plant` mode reports
  "plant test: PASS (all 3 planted probes fail)". I added a bad row of my own (the old "so the central value is
  reproducible" wording). It failed with "failures 1", so the checker fires.
- **Build.** `build_all rc=0`, `RESULT :: PASS`, `BODY-POINTERS :: PASS`, `SEC4-RECEIPTS :: PASS (15/15)`, and
  struck-value containment ok (note 0/69, records 64/64). RECORDS-PIN is SKIP in the build copy and PASS in the
  worktree (writer). RECORDS-MOVE passes with 0 failures (writer's run, 12/12 self-test plants fired).
- **References.** 0 undefined references and 0 `??` in every log and pdftotext.
- **Paper.** I compared the pdftotext of `main_paper.pdf` against rec3: identical once the `(Dated: …)` line is
  excluded. The writer reports byte-identity against the batch base build.
- **Labels and pointers.** 184 note labels, identical numbers. No `\nsec`/`\napp` pointer in `paper_body.tex` or
  `main_paper.tex` targets a label defined in this batch's files.
- **Swallowed text.** `swallowed_text.py`: "flagged 0".

## Lost facts (A)
- I ran a scripted per-file comparison of the printed source (comments stripped) before and after: numerals, macros
  and number-words.
  - No numeral or value macro was lost in the abstract, the executive summary, §1 or §11.
  - §12 lost one "10" (a repeat of the 10% criterion, which still prints once in §12 at S3) and two "\Eavail".
  - The number-words "six", "five", "third" and "two" were gained, and each is supported in the body.
- I compared every changed sentence (the full word diff of the 5 files) against its before text and the body.
  Findings B1, S1, S2 and S3 are the only ones of substance.
- Nothing moved to the records. The writer has no MOVE rows, and none is needed.

## Verdict: ADOPT-AFTER-FIXES
Fix B1, B2 and S1–S3. Each is a wording change of a clause or less. None needs a records move or a label change.

## What I checked (counts)
- 5 files, the full word diff (196 lines added and 170 removed).
- 7 brief items and 4 writer questions.
- About 30 summary claims checked against their body subsections: Table 3, Table `tab:validation-design-5d`, §§9.2,
  9.3, 9.4, 9.6, 5.2, 4.5, 4.6, 8.4, 7.7, 10.6, 10.9, App. C (intro, C.4–C.8) and App. G.
- 3 source records: RUNBOOK-20260807 §2, DECISION-20260815, and KNOWN_ISSUES rows 75 and 80. Also RECORD-20260927
  §2 and the period-unfold launcher.
- The paper's abstract, sec:central, sec:conclusions and the estimator table.
- The ledger checker run with a planted bad row; 184 labels; the paper text.

## What I did not check
- The meaning of every one of the 134 ledger rows. I spot-checked about 25 and ran all their probes.
- The §11 numbers (66.4, 22.3, 11.3, 27.7, 0.9994, 1.0013, 2.9, 7.9, 62) against their receipts. They are unchanged
  from the base, so I confirmed only that they are unchanged.
- Figures.
- The records document's contents.
- I did not rebuild, and did not rerun RECORDS-MOVE or build_copy.sh myself. I relied on the build log and the
  writer's outputs, and grepped the log for gate lines.
- The interaction with other unmerged batches beyond b5's App. C sentence.
