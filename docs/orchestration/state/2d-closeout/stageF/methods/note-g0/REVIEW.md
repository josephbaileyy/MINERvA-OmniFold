# Review of batch 0 (glossary register pass), analysis note

Reviewer: independent, read-only. No file in any worktree was edited and nothing was committed. My own scripts and
scratch outputs are in `S/rv-g0/` (`indep.py`, `pairs.py`, `pairs.txt`, `labels.py`, the pdftotext dumps).
Line numbers: "base" = 38a53a53, as the ledger gives them; "after" = the worktree `S/wt-note1`.

## Verdict: ADOPT-AFTER-FIXES

The mechanics are sound. The edit list reproduces the diff exactly. No number, `\ref`, `\cite` or value macro changed
without a stated and correct reason. Protected text is untouched, and the paper, primer and PET note are unchanged.
One edit removes a label that a binding ruling requires (B1). About ten edits change a status or a scope (S1-S10).
Each is a one-line fix.

---

## Findings

### BLOCKING

**B1. G104: the label required by the director's ruling is deleted.** sec_joint.tex:748 (base), :733 (after).
- Before: "The GiBUU replay carries the label ``B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its
  premise passed at $\le0.1\,\sigma_{c}$'': the sampling-closure check failed on the hydrogen sample, and a bias check
  of its premise, declared before it was computed, moves the CH prediction by ..."
- After: "For the GiBUU re-evaluation, the sampling-closure check failed on the hydrogen sample. A post hoc bias check
  of that check's premise, declared before it was computed, passed its criterion of at most $0.1\,\sigma_{c}$: it moves ..."
- Why it blocks: `BINDING-PHASE1-ADDENDUM-7.md` ruling 3 says the GiBUU-on-CH replay is reported "under the label
  'B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at ≤ 0.1 σ_c'".
  `measurement-paper/phase1/mp3c/REPORT.md` also says "**Label, required by the ruling:**" and is CITABLE only
  "under that label". The source comment directly above the sentence (sec_joint.tex:730) reads "C:7-8 (the required
  label, verbatim)". Rewording the label is a disclosure change, not a register change. The rewritten facts are
  correct (the 0.1 acceptance is in mp3c/REPORT.md §1). Only the verbatim label is lost.
- Fix: keep the plain explanation and restore the label verbatim. For example: "The GiBUU re-evaluation carries the
  label required for it, ``B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at
  $\le0.1\,\sigma_{c}$'': the sampling-closure check failed on the hydrogen sample, and a post hoc bias check of that
  check's premise, declared before it was computed, met its criterion of at most $0.1\,\sigma_{c}$: it moves ..."
  (Only the internal name "B3" stays unexplained, and the label is verbatim by rule.) Add this sentence to the
  protected spans in `apply_glossary.py`.

### SHOULD-FIX

**S1. G084: "frozen sets" became "predeclared power sets". That is wrong in context.** sec_joint.tex:505 / :499.
- Before: "These come from the frozen sets, each of which lost some of its 200 alternatives ... Against the frozen null
  ensembles, the complete power sets recovered ..."
- After: "These come from the predeclared power sets, each of which lost some of its 200 alternatives ..."
- Here "frozen" means *the power sets as evaluated for the decisions (before recovery)*, set against "the complete
  power sets recovered". "Predeclared" drops that contrast and claims a timing that is not the point.
- Fix: "These come from the power sets as evaluated for the decisions, each of which lost ..."

**S2. G088 and G092: "frozen variant shifts" became "predeclared variant shifts".** sec_joint.tex:540, :584 / :534, :574.
- After: "covers only the reading with the predeclared variant shifts"; "both with the predeclared variant shifts and with
  the shifts recomputed on all draws".
- The source is `RECORD-20261006-s5p-lost-seed-recovery-resolution.md` §3: "(a) union, S recomputed" vs "(b) frozen S".
  `DECISION-20261005-…` §5 names it the "frozen-shift reading (b)". The shift S is computed from the calibration
  draws, which is why it can be "recomputed on all draws". "Frozen" means the values from the primary evaluation,
  not values declared in advance.
- Fix: "the variant shifts of the primary evaluation" in both places. Glossary A8 needs this context ("frozen X" in the
  recovery text means "as in the primary, pre-recovery evaluation").

**S3. G030: the status word "candidate" is deleted.** sec_systematics.tex:527 / :518.
- Before: "\SI{\gbdtAiEstFrac}{\percent} of the candidate split-varied band"
- After: "\SI{\gbdtAiEstFrac}{\percent} of the split-varied band"
- Commit 6964af37 (2026-07-16, "correct publication gates") deliberately changed "adopted split-varied band" to
  "candidate split-varied band". Deleting it with no ledger note loses a status (rule: status must survive). The base
  also has a tension the writer did not flag: the next sentence says this dominates "the band in use" (now "the band
  used in this note").
- Fix: restore the status, e.g. "of the split-varied band (part of a five-dimensional construction not used for any
  quoted uncertainty)". If the author confirms that this band *is* a component of the covariance in use, delete
  "candidate" and say so in the ledger. Either way, list the tension as an open question.

**S4. G108: "statistical" is inserted and "used in the analysis" is asserted.** sec_fps.tex:79.
- Before: "This probes the statistical closure-toy stream, not the full band in use."
- After: "This probes the statistical closure-toy stream, not the full statistical band used in the analysis."
- The source does not support "statistical". The sentence started as "not the full adopted band" (commit 32325db7).
  The extended-fiducial analysis assigns no uncertainty magnitude beyond the three-prior envelope (sec_fps.tex:122),
  so there is no extended-fiducial "statistical band used in the analysis".
- Fix: "not the full quoted band". If the author means a specific band (the 2D statistical block?), name it, and add
  the question to REPORT.

**S5. G170: the heading says "use", which contradicts the paragraph above it.** app_negweight.tex:295 / :273.
- Before: "\paragraph{The published pair has different footings.} The extended-fiducial lane designates ..."
- After: "\paragraph{The extended-fiducial measurement and its control use different background treatments.}"
- The preceding paragraph says the quoted extended-fiducial number used the purity default, as the control does. The
  pair differs in its *designated* publication treatment, not in what either one used.
- Fix: "\paragraph{The extended-fiducial measurement and its control are designated different background treatments.}"

**S6. G116 (new label table): "the two values of the driver's background-mode option" is false.** app_guide.tex:34 (after).
- Both drivers accept three values: `choices=["purity", "negweight", "negweight-refined"]`, at
  2d-unfolding/unfold_2d_omnifold_unbinned.py:1363 and nd-unfolding/unfold_nd_omnifold_unbinned.py:620. The plain
  `negweight` mode (injection without refinement) is the one the app_negweight comparison discusses.
- Fix: "`purity`, `negweight`, `negweight-refined` & the values of the drivers' background-mode option
  (`--bkg-mode`): purity-based subtraction, negative-weight injection, and refined negative-weight subtraction ..."

**S7. G117: "Stage-1/Stage-2 bootstrap" became "first-stage/second-stage bootstrap", which reads as a two-stage
(double) bootstrap.** app_statmethods.tex:28.
- In the repository, "Stage-1"/"Stage-2" are project phases ("UQ Stage-1 #7", runEventLoopOmniFold.cpp:218; "Stage-2
  publication-grade full universe sweep"). The two objects are successive bootstraps: N=50 (superseded) and N=300
  (app_history.tex:114-118).
- Fix: "(the superseded 50-replica bootstrap, App.~\ref{app:history}). The 300-replica bootstrap ($N=300 > 205$) is
  full-rank." Both numbers are in App. J. Flag `num` with that reason.

**S8. G169 and Q2: "which passed the analysis's validation checks" is stronger than the source.** app_negweight.tex:290 / :269.
- Before: "The ledger-verified central value from that gated battery remains"
- After: "The central value from that battery, which passed the analysis's validation checks and is recorded with them, remains"
- See Q2 below. "Gated" refers to the battery's own gate: VALIDATION_LEDGER.md:1611-1612 records "**anchor gate
  PASS**", which the note now calls the published-region check. The ledger also called the coverage toys "the FPS
  campaign's last validation gate" (:1632). The note has since downgraded that check to a "containment diagnostic ...
  none is used as a covariance-certification test" (sec_fps.tex:74-81). "The analysis's validation checks" therefore
  overstates.
- Fix: "The central value from that battery, recorded in the validation ledger with its passed published-region check
  against the control, remains ..."

**S9. G012: the scope narrows from "not adopted" to "central values".** sec_method.tex:73.
- Before: "It is not adopted, and the quoted extended-fiducial value does not use it"
- After: "The quoted central values, including the extended-fiducial value, do not use it"
- The writer was right to avoid "not used for any result" (the joint tests use it; sec_method.tex:167-174). But "not
  adopted" also covered the quoted uncertainties, which use purity too (configuration 1: "the 2D central value and its
  uncertainty ensembles"). That fact is now lost.
- Fix: "The quoted central values and uncertainties, including the extended-fiducial value, do not use it".

**S10. Q1, left unchanged: "the adopted estimator" in app_negweight should name LightGBM.** app_negweight.tex:281.
See Q1 for the evidence. Fix: "At full statistics with LightGBM, the estimator of the quoted 2D central value, on 2D
ME~FHC, the covariance difference is one to two percent." Also add "(histogram backend)" to the next sentence that
starts "Real-data totals agree to \nwPctTot ..." in the same paragraph, because those totals come from the `hist` runs.

**S11. Q4, a pre-existing claim defect (not introduced by this batch): "simple hypotheses".** sec_joint.tex:9-10.
See Q4. Fix with the author's sign-off: "The tests evaluate hybrid null hypotheses about five predictions
(\S\ref{sec:joint5d-design})."

### NIT

- **N1. G079 and G082: "frozen stop" became "(own) predeclared stop".** sec_joint.tex:251, :445. The rule was
  predeclared; the stopping point is an outcome. Fix: "the stop set by its predeclared rule" (and in the caption, "at
  the stop set by the predeclared rule").
- **N2. G109: "(b)~Tune~v1/bare-GENIE prior-swap ratio".** sec_fps.tex:88. Elsewhere the note now says "MINERvA
  Tune~v1". The panel label inside the image is presumably still "MnvTune", which goes with Q6. Fix: "(b)~MINERvA
  Tune~v1/bare-GENIE".
- **N3. "Single-pass" is never explained.** sec_systematics.tex:496 is the first use. A reader learns what the loop
  stores but not why it is "single-pass". Fix: "The single-pass event loop, which writes every universe in one pass,
  stores ..."
- **N4. G014: "whose" can attach to the driver.** sec_method.tex:119. After: "a regeneration with the current driver,
  whose configuration was recorded, reproduces it". Fix: "a regeneration with the current driver, with its run
  configuration recorded, reproduces it".
- **N5. G156: "not replace its adoption" became "not replace, the ... construction".** app_statmethods_nd.tex:173. The
  object of "replace" changes from the decision to the construction. Fix: "would supplement the required scalar-5D
  uncertainty construction, not replace the decision to use it."
- **N6. G123: "run with each universe active" can be read as all universes at once.** app_statmethods.tex:199. Fix:
  "run with one universe active at a time".
- **N7. G116 table, `lgbm` row:** "LightGBM (central value and its uncertainty ensembles)". LightGBM also gives the 3D-5D
  central values and the joint-test estimator (sec_method.tex:162-174). Fix: "LightGBM (the quoted central values and
  their uncertainty ensembles; also the joint-test estimator)".
- **N8. Writer's documents disagree:** REPORT §4 says the MAT classes are in "App. A.2.6"; GLOSSARY G2 says "A.2.5".

---

## Answers to the writer's open questions

**Q1. "the adopted estimator" (app_negweight.tex:281) is LightGBM.**
- The sentence's subject is the covariance difference: "one to two percent" is 1 − \nwSystRatio (0.986) and
  1 − \nwStatRatio (0.982).
- values.tex:375 gives the provenance of those ratios as "covariance propagation (Phase D: lgbm, 187-universe ...;
  matched 50-seed bootstrap stat)".
- 2d-unfolding/HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh:27-32 reads
  `2d_xsec_MEFHC_5iter_lgbm_nw_uni_CV.root` and the `lgbm` bootstrap replicas.
- The `hist` backend belongs to the *central-value* comparison: values.tex:363-364 ("binned purity (hist)",
  "negative-weight (hist)"), and compare_bkg_modes.py:4 and :24 (default `hist`). The same paragraph therefore mixes
  two backends: the covariance ratios come from LightGBM and "Real-data totals agree to \nwPctTot" comes from `hist`.
  See S10.

**Q2. "ledger-verified ... gated battery" means less than "passed its validation checks".**
- "Ledger-verified" means recorded in `VALIDATION_LEDGER.md`, entry "FPS MEFHC battery (2026-06-10, job 54244120)"
  (VALIDATION_LEDGER.md:1611; App. G `fps-battery`, app_provenance.tex:199-200).
- "Gated" refers to that entry's "**anchor gate PASS**" (:1612): the published-region comparison with the control
  (integral 0.9994, median 1.0013, 185 cells), now item 1 of sec_fps's battery. The phrase dates from commit 930fb911.
- It does *not* certify a set of "the analysis's validation checks". The ledger's later "last validation gate" (coverage
  toys, :1632) is now only a diagnostic in the note. See S8 for the wording.

**Q4. Yes, the printed "simple hypotheses" is wrong.**
- docs/orchestration/state/2d-closeout/stageF/methods/M2-AUDIT.md:39-40 (Q1) says "Below the fine grid the null is a
  family, not a point" and "The text disagrees with the code. A7 calls H0(G) 'SIMPLE …' ... The code makes Tune v1's
  sub-cell shape the CV member of a prior-drawn family."
- M2-ARCHIVE-CHECKS.md:10 confirms: "The audit's other Q1 text fix still stands: below the fine grid the null is a
  family."
- The note already prints the corrected framing: sec_joint.tex:31-37 ("This \emph{hybrid null} is the hypothesis the
  calibration simulates"), sec_joint.tex:241-242 (the size is averaged over the nuisance priors and can exceed α at a
  fixed nuisance value), sec_execsummary.tex:81 (source comment: "'Simple hypotheses' was wrong: the nulls are
  hybrid"), main_note.tex:102, and paper_body.tex:834.
- Only sec_joint.tex:10 and the older records still say "simple" (RECORD-20261005 §1, which quotes amendment 7, and
  DELIVERY-20261006).
- Correct wording, from sec_execsummary.tex:83 and main_note.tex:102: **"The tests evaluate hybrid null hypotheses about
  five predictions (\S\ref{sec:joint5d-design})."** This changes a claim back to what the audit found, so it needs the
  author's sign-off (S11).

---

## Check results

**1. Every edit, by script** (`S/rv-g0/indep.py`, `pairs.py`).
- **Re-application.** I loaded the 190 edits and the 1 comment edit from `apply_glossary.py` and re-applied them to the
  files at 38a53a53 with my own code. The result is byte-identical to the worktree in all 19 changed files. No change
  sits outside the edit list, and there are no untracked files. The writer's `--dry-run` passes, and `check_ledger.py`
  passes: 190 rows, 379 probes, 0 failures.
- **Numbers.** 18 edits change the multiset of numbers. All 18 carry `allow=num` with a reason, and I checked each
  reason: digits inside dropped labels (B3, P4, VL170/172/175, KNOWN_ISSUES 92/95, 5D→five-dimensional, Stage-1/2) or
  added names (Tune~v1, "2D"). No measured value changed.
- **References.** 7 edits change refs. All 7 are additions; none removes a ref. The new targets exist:
  - KNOWN_ISSUES 92 → App. G `rvp1pi` (app_provenance.tex:233 cites "row 92");
  - KNOWN_ISSUES 95 → `app:history-errata` (app_history.tex:58 cites "KNOWN_ISSUES.md 95");
  - VL175 → `app:history-vl175`;
  - two pointers to `sec:uq-higherdim`.
- **Value macros:** 0 changed. The macro changes I found are `\texttt`, `\emph`, `\le`, `\S`/`\ref` and the table markup.
- **Negation and limit words.** 17 edits lose a word from my broader list: not/only/fails/under/non/un-, and similar. I
  read all 17. None loses a negation's meaning. G012 and G169 merge or reword a "not" correctly. "Report-only" became
  "reported but not used", which moves the "only" into a "not".
- **Parse.** Braces, `$` and parentheses balance in all 190. No doubled words, gluing or bad capitalization at any
  seam. The build has 0 undefined references and 0 "??".
- **Reading.** I read all 190 before/after pairs, and the surrounding text for the 119 that touch a status term.
- **"Frozen" → "predeclared"** (G001, G076, G079, G080, G082, G083, G084, G087, G088, G092, G093, G099, G154).
  - True: G001 (sec_execsummary.tex:158, "fixed before the study"), G076 and G080 (sec_joint.tex:244-246), G083
    (δ_fine measured before any observed statistic), G087, G093, G099, and G154 (contract-amendment-2-stage2-studies.json).
  - Wrong in context: G084 and G088/G092 (S1, S2).
  - Loose: G079 and G082 (N1).
- **"Constructed, not adopted"** (G048) is true: App. J says the projection "now exists (2026-09-22) but is not
  adopted". The writer's two catches are correct:
  - G012: the joint-test estimator uses negative-weight subtraction (sec_method.tex:167-174);
  - G179: the 400-tree, 31-leaf refinement is the joint-test configuration, and its "not adopted" comment cites the
    data-stability failure (app_negweight.tex:367-368).

**2. Status terms whose meaning differs by file.** The glossary handled "in use", "candidate", "adopted" (2D in
app_statmethods vs five-axis elsewhere) and "headline" correctly, except as follows:
- "frozen" in the lost-draw recovery text (S1, S2) has no glossary context;
- "candidate" at G030 (S3);
- "in use" at G108 (S4);
- "footing" at G170 (S5): designated vs used.

**3. Definitions.**
- "Re-selected" matches the code: runEventLoopOmniFold.cpp:104-106, where the active-universe mode "promotes one
  universe to be the ordinary event-loop universe, so truth/reco entrants and exits are handled".
- "Single-pass" matches the dump-all mode ("CV-selected shadow branches", :104-105, :218-235), but it is not
  self-explanatory (N3).
- "Lateral" ("a band that shifts reconstructed kinematics, as opposed to a vertical band, which reweights events")
  matches MAT usage and the code's `IsVerticalOnly` split.
- In the label table, J28 matches AUDIT-FINDINGS-20260731.md:478. The VL170/VL172/VL175 entries match
  app_provenance.tex:116-120 and app_history.tex:52-66. `cv`/`mean`, the July/May sweeps (sec_systematics.tex:207-215)
  and `MNV101_ACTIVE_UNIVERSE` are correct. The `--bkg-mode` row is wrong (S6), and the `lgbm` row is incomplete (N7).

**4. Open questions:** answered above.

**5. Build sanity.** Verified:
- The `note-g0` build sources equal the worktree in every `.tex` file, and the `r12` build sources equal 38a53a53 in
  every `.tex` file.
- pdftotext of main_paper, main_primer and pet_note is identical between r12 and note-g0. Page counts are 13, 15 and 26
  in both, and the paper and primer `.aux` files are byte-identical.
- main_note.aux has 205 `\newlabel`s in both builds, with 0 changes in label number. 101 labels moved page, as expected.
- main_note grew from 136 to 138 pages.

**6. Register: sentences the glossary made harder to read** (no more than 8).
1. app_negweight.tex:370 (G185). The heading "The background treatment is chosen, the obligation to revisit it is not
   yet met, and the choice of covariance is separate." and the sentence "the former settles one decision that blocked
   use while leaving every other precondition for using a component intact". Suggest "\paragraph{Background treatment
   chosen; obligation open; covariance choice separate.}" and "the choice removes one blocking decision and leaves
   every other precondition in place."
2. sec_joint.tex:477 (G083). "A scan along the predeclared direction ..., reported but not used for the decisions,
   found ... in the calibration ensembles used for the decisions." The phrase "used for the decisions" appears twice
   in one sentence, and the appositive appears six times in the section (G081, G082, G083, G091, G101). Suggest
   defining "for reporting only (outside the decision rule)" once and using "for reporting only" after that.
3. sec_joint.tex:717, :722 (G100, G103). "At its Holm position in the decisions" and "at their Holm positions in the
   decisions". Suggest "at its original Holm position".
4. sec_method.tex:317 (G019). "self-tested to reproduce stored reference lower-dimensional extractions". Suggest
   "self-tested to reproduce stored lower-dimensional reference extractions".
5. sec_experiment.tex:80-82 (G007, G008). "The trees made for the systematic universes also carry all
   systematic-universe weights and the observables as shifted by each lateral band (MAT's name for ...; ...)". The
   sentence is circular and carries a long parenthetical. Suggest "The systematic-universe trees also carry every
   universe's weight and each lateral band's shifted observables (a lateral band shifts ...)."
6. sec_joint.tex:538 (G090). "rest on the calibration run's own re-application of the sequential rule, validated only
   by that run itself". Suggest "rest on the calibration run's own re-application of the sequential rule, which only
   that run has checked."
7. app_negweight.tex:256 (G164). "Neither job script that could have launched them sets the driver's background-mode
   option". Suggest "Neither of the two possible job scripts sets the background-mode option".
8. sec_systematics.tex:496-499 (G026). The opening of sec:uq-higherdim is now three long sentences that define two
   modes, state a causal "therefore" and state a status. Suggest splitting the definition of the two event-loop modes
   from the status sentence.

---

## Counts

| what | count |
|---|---|
| edits re-applied independently and compared to the worktree | 190 + 1 comment, 19 files, 19/19 identical |
| edits machine-checked (numbers, refs, value macros, negation/limit words, balance, seams) | 190 |
| edits whose numbers changed / refs changed / value macros changed | 18 (all justified) / 7 (all additions, valid) / 0 |
| edits read in full | 190 |
| status-term edits read in context against sources | 119 |
| "predeclared" timings checked | 13 |
| label-table rows checked against sources | 7 |
| open questions resolved from sources | 3 (Q1, Q2, Q4) |
| build products compared | 4 PDFs (text), 3 aux, 205 labels |
| findings | 1 BLOCKING, 11 SHOULD-FIX (2 of them pre-existing or left unchanged: S10, S11), 8 NIT, 8 register |

## What I did not check

- Non-`.tex` build inputs (figures, `.bib`) and how the PDFs look, including the layout of the new label table. I
  compared extracted text and aux files only, and I did not rebuild.
- Whether the writer's inventory missed terms. I scanned the after-PDF for about 15 status words only, not the 57-term
  inventory.
- Apps. G-J beyond the passages I cited as sources, and the old vocabulary still in them (writer's Q7).
- Every App. G tag-pointer target (the build's BODY-POINTERS gate passed; I did not re-run it).
- Whether lateral universes shift truth-side kinematics as well. The event loop writes shifted `pT_truth`/`pz_truth`
  for lateral universes (runEventLoopOmniFold.cpp:229-233). I did not decide whether "shifts reconstructed kinematics"
  should be "shifts kinematics".
- The physics truth of any claim the batch did not change, other than Q1, Q2 and Q4.
- The baked-in figure panel labels (writer's Q6). The ledger's file:line values beyond the rows I cite.

---

# Re-review (fix round, 2026-10-21)

The re-review was read-only; I edited no worktree file. My scripts are in `S/rv-g0/`: `indep.py`, now with S11, and
`pairs.py`. `pairs-r1.txt` holds the round-1 pairs, kept for the diff below.

## Mechanics
- I re-applied the 192 edits and the 1 comment edit from `apply_glossary.py`, then S11, to 38a53a53 with my own code.
  The result is byte-identical to the worktree in 19/19 files, and there are no untracked files.
- The writer's checks pass: `--dry-run` PASS; `check_ledger.py`: 192 rows, 383 probes, 0 failures; `S11.md`: 1 row,
  2 probes, 0 failures.
- Changes since round 1:
  - 4 edits added: G103 and G104 for B1, G173 and G174 for S10;
  - 2 withdrawn: the old G030 (S3) and the old G104;
  - 28 reworded, plus S11.
- I read every added and reworded pair in full. The only new number is "0.1" in G104, which comes from the label.
  "50" and "300" in G117 come from app_history.tex:114-118. No ref was removed. No value macro changed. No negation
  was lost: G012 and G169 still pass, as in round 1.

## 1. Does each fix resolve its finding?

| finding | verdict | evidence |
|---|---|---|
| **B1** | **Resolved.** | sec_joint.tex:733-734. The label is byte-identical to the base, and the printed PDF shows it. The fixed `B3_LABEL` in `apply_glossary.py` makes the whole file protected if the label breaks. "Declared before it was computed" is **supported**: mp3c/REPORT.md §1 says "**Declared before computing:** `DECLARATION-b.json`, sha256 `00efbb25…`, recorded 05:58 PDT 10-20. The job refused to run unless the file matched." ADDENDUM-7 ruling 2 required it ("declared, and its declaration committed or hashed, before it is computed"), and the phrase is base wording. "Post hoc" is ruling 2's own label. "Met its criterion of at most $0.1\,\sigma_c$" matches the acceptance "max \|Δ/σ (a)\| ≤ 0.1" and the measured 5.1e-4 (mp3c §1). Nothing says GiBUU-on-CH "passed its gates" (ruling 1). |
| S1 | Resolved | "the power sets as evaluated for the decisions" (:499) |
| S2 | Resolved | "the variant shifts of the primary evaluation" (:534, :574); "the evaluation before recovery" (:540) matches DECISION-20261005 §5 item 1 ("the frozen evaluation's, at the frozen B") |
| S3 | Resolved (base restored) | "candidate split-varied band" is back (sec_systematics.tex:518), and the tension is Q11. Restoring the base is the right move for a register batch. |
| S4 | Resolved | "not the full quoted band" |
| S5 | Resolved | "are designated different background treatments" agrees with the paragraph above |
| S6 | Resolved | three values, matching `choices=["purity", "negweight", "negweight-refined"]` in both drivers |
| S7 | Resolved | 50-replica and 300-replica, as in app_history.tex:114-118 |
| S8 | Resolved | "recorded in the validation ledger with its passed published-region check against the control" matches VALIDATION_LEDGER.md:1611-1614 ("anchor gate PASS ... vs control") |
| **S9** | **Resolved and supported** | "The quoted central values and uncertainties, including the extended-fiducial value, do not use it." The 2D central value and its uncertainty ensembles, and the 3D-5D central values, use purity (sec_method.tex:163-166). The five-axis covariance used is built with purity subtraction (app_negweight.tex:249-252), and so is the extended-fiducial number (:264-269). No extended-fiducial uncertainty is quoted beyond the envelope. The joint tests, the one user of the treatment, are not a quoted result. |
| **S10** | **Resolved and supported** | G173: "with LightGBM, the estimator of the quoted 2D central value". The Phase D inputs are `2d_xsec_MEFHC_5iter_lgbm_*` (run_negweight_covariance_analysis.sh:10, :27-32; values.tex:375). The driver's lgbm defaults (`n_estimators=100, num_leaves=8, learning_rate=0.1`, unfold_2d_omnifold_unbinned.py:404) are the quoted configuration (sec_method.tex:97-98). The claim is about the estimator, not the seed, which the sentence does not state. G174: "Real-data totals (histogram backend)" matches values.tex:363-364. \nwMedianBin and \nwRmsBin in the same sentence come from the same `hist` comparison (compare_bkg_modes.py). |
| N1-N8 | Resolved | checked at each line in REPORT §8; N3's "which writes every universe in one pass" matches runEventLoopOmniFold.cpp:218-226 |

**The eight rewritten sentences.** None loses a fact or strengthens a claim.
1. G187, app_negweight.tex:368. Fine. A NIT is below.
2. sec_joint. "For reporting only (outside the decision rule)" is defined at its first use (:333). The later uses come
   in reading order (:443, :477, :518, :540, :720). This matches "a robustness variant, not used for the decisions"
   (sec_execsummary.tex:83) and DECISION-20261005 §5 ("report-only").
3. "Original Holm position(s)" (:717, :722) matches the source comment "frozen positions, no re-sort".
4. "Stored lower-dimensional reference extractions". Fine.
5. sec_experiment.tex:80-82 reads correctly after the comment line, and "also" still has its antecedent.
6. "Which only that run has checked" matches "the campaign's self-validated `stopping.json`" (DECISION-20261005 §5).
7. "Neither of the two possible job scripts". Fine.
8. sec_systematics.tex:496. "Two event-loop modes supply the lateral bands" holds: single-pass supplies the products
   that are not used, and re-selected supplies the quoted blocks. "One lateral universe active at a time" matches
   runEventLoopOmniFold.cpp:104-106.

## 2. S11

**Exactly supported.** The new sentence is "The tests evaluate hybrid null hypotheses about five predictions
(\S\ref{sec:joint5d-design})." It prints as "(§10.1)".
- The wording is the executive summary's: "Calibrated tests of hybrid null hypotheses for five predictions",
  sec_execsummary.tex:83, with the source comment at :81.
- The pointer goes to the definition: "This \emph{hybrid null} is the hypothesis the calibration simulates",
  sec_joint.tex:31-37.
- The audit ground is M2-AUDIT.md:39-40, confirmed by M2-ARCHIVE-CHECKS.md:10.
- Only the noun changes. The count, scope and claim strength stay the same.
- Keeping it as a separate script with `--revert` is correct. It still needs the author's sign-off, as recorded.

## 3. Build

Verified on the rebuilt `note-g0` (PDFs dated 16:58).
- Every non-build file in the build's note directory equals the worktree.
- pdftotext of main_paper, main_primer and pet_note is identical to r12. Page counts are 13, 15 and 26, and all three
  `.aux` files are byte-identical.
- main_note.aux has 205 `\newlabel`s with 0 changes in label number (102 moved page). There are 0 "??" in the text.
  BODY-POINTERS PASS and RESULT PASS.
- main_note is 138 pages.

## Remaining fixes

1. **SHOULD-FIX (handoff doc).** REPORT.md §7, "Reproduce", is stale. It quotes "190 rows, 379 probes" (now 192 and
   383) and leaves out `apply_s11.py`. Running it as written rewrites sec_joint.tex from the base and **silently
   reverts S11**: `apply_glossary.py` re-derives the file from 38a53a53, as the docstring of `apply_s11.py` itself
   warns. Fix: add `python3 apply_s11.py S/wt-note1` and `python3 check_ledger.py S/wt-note1 S11.md` after the
   apply step, and update the counts.
2. **NIT.** G187 heading, "Background treatment chosen, its obligation not yet met; ...". "Its obligation" leaves out
   *which* obligation; the base named it ("not discharged"). Suggest "Background treatment chosen, the obligation to
   revisit it open; covariance choice separate."
3. **Open, for the author, not for this batch:** Q11, whether the split-varied band is a component of the five-axis
   covariance used. Also the S11 sign-off.

**Verdict: ADOPT once item 1 is fixed.** It is a two-line change to the handoff doc, and no note text changes. Item 2 is
optional.
