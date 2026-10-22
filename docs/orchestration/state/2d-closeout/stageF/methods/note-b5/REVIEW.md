# Review of register batch b5 (§2 `sec_experiment.tex`, §3 `sec_method.tex`, §4 `sec_systematics.tex`)

Reviewer: independent, read-only. Before = `551f9432` (the worktree's HEAD). After = the uncommitted edits in
`S/wt-note-b5`, built in `S/plain-language/builds/note-b5/`. I edited nothing in either worktree. My only files are
this review and `rv_numcmp.py`, `rv_paper_new.txt` and `rv_paper_base.txt` in this directory.

File:line references are to the after text in `S/wt-note-b5/docs/analysis-note/`.

---

## Findings

### BLOCKING

**B1. The scope of configuration (e) is wider than Table 3, which sits a few lines below it (§3.2, and repeated in §3.1).**
- After, §3.2, `sec_method.tex:202-205`: "(e), the joint-test estimator ... It is used for the generator tests and the
  development studies of §§9.2–9.4, and it was selected before the joint-test design was fixed".
- After, §3.1, `sec_method.tex:74-77`: "its refined form is the background treatment of the joint-test estimator, used
  for the generator tests and the development studies of §§9.2–9.4 (§3.2, App. C)". "Used for" attaches most naturally
  to "the joint-test estimator".
- Before: neither sentence existed. Configuration 2 named no uses. §3.1 said only "The quoted central values and
  uncertainties, including the extended-fiducial value, do not use it (App. C)."
- Table 3 (`tab:estimators-matrix`, `sec_method.tex:225-235`) disagrees:
  - (c) is used for background bias (§9.2) and the coverage test;
  - (d) is used for background bias and for the generator-sized E_avail change (§9.2);
  - (e) is used for the generator shapes held out of development, the precision study (§9.4) and the generator tests
    (§10).
- The validation table (`sec_5d.tex:57-70`) gives the same assignment: background closure (c), (d); generator-sized
  change (d); held-out shapes (e); coverage (c); test calibration (e).
- §9.3's raised-refinement candidate and §9.4's estimator R are (e). §10.2 (`sec_joint.tex:104-107`) points to §9.3,
  not §9.2, for (e). The §9.2 studies did not use (e).
- The held-out-shape study is, by its own label, not a development study.
- Inside §3.2 the batch now contradicts itself. The (e) bullet claims §9.2's development studies, and the next paragraph
  gives §9.2's background-bias study to (c) and (d).
- The writer copied the phrase from App. C "Scope of the numbers" (`app_negweight.tex:19-21`, batch b3). App. C has the
  same defect, but it is outside this batch. Flag it to b3's owner.
- **Fix, §3.2:** "It is used for the generator tests (§10), the study of generator shapes held out of its development
  (§9.3) and the precision study (§9.4), and it was selected before the joint-test design was fixed (§10)."
- **Fix, §3.1:** "...do not use it. Its refined form is the background treatment of configurations (d) and (e)
  (§3.2): (d) in the background-bias and generator-sized-change studies of §9.2, and (e), the joint-test estimator,
  in §§9.3–9.4 and the generator tests (App. C)."

### SHOULD-FIX

**S1. "Three configurations carry the main results" includes the exact-split cross-check (a status change).**
- After, `sec_method.tex:189` and `:206`: "Three configurations carry the main results: ... (b), the exact-split
  cross-check above."
- Before: "The note and the article use three configurations ..."
- Table 3 calls (b) a "two-observable cross-check". The new sentence promotes a cross-check to a main result, and the
  bullet calls itself a cross-check.
- **Fix:** "Three are described in this section: (a) ..., (e) ..., and (b), the exact-split cross-check above." An
  alternative is "The main results use (a) and (e); (b) is the 2D cross-check."

**S2. (c) is described as "without a refinement", which hides that it uses purity-based subtraction.**
- After, `sec_method.tex:208-210`: "Configurations (c) and (d), the deterministic variant without and with a
  nominal-capacity refinement, are used in the background-bias and coverage studies listed in the table."
- Table 3: (c) uses purity-based subtraction; (d) uses negative weights with a 100-tree, 8-leaf refinement.
- Read alone, the sentence suggests that (c) is negative-weight subtraction without refinement. It also leaves out (d)'s
  generator-sized-change study.
- **Fix:** "Configuration (c), the deterministic variant with purity-based subtraction, and (d), the same variant with
  negative weights and a nominal-capacity refinement, are used in the background-bias, generator-sized-change and
  coverage studies listed in the table."

**S3. A measured difference is restated as a seed effect before its inference flag.**
- After, `sec_method.tex:107-110`: "Changing the seed from 1 to 42 moves the central value by a per-bin median of
  0.18% ..."
- Before: "the seed-42 central value differs from the seed-1 one by a per-bin median of 0.18% ..."
- The attribution to the seed is marked "(inferred from the two regenerations)" one sentence later. The new lead sentence
  asserts it outright first. That is a stronger verb (changes.md M6: "stated as a seed effect").
- **Fix:** restore "The seed-42 central value differs from the seed-1 one by a per-bin median of ...". Keep the next
  sentence as it is.

**S4. Dropping "earlier" lets the rebuilt bootstrap read as the quoted block (§4.2).**
- After, `sec_systematics.tex:120-123`: "...the statistical band quoted when it ran, an earlier band that was later
  rebuilt, undercovered ... The split data/MC streams of the rebuilt bootstrap are in Ref. ..."
- Before: "the split data/MC streams of the earlier, rebuilt bootstrap are in Ref. ..."
- Both the first band and the rebuilt band differ from the quoted three-stream block. The paper says so: "Two earlier
  versions of the statistical band, distinct from the quoted block" (`paper_body.tex:446`).
- "An earlier band that was later rebuilt" now invites the reading that the rebuild is what is quoted. That would
  conflict with the paragraph's first sentence. The guardrail applies.
- **Fix:** "...the statistical band quoted when it ran undercovered in its tails, unevenly across bins. That band was
  later rebuilt, and neither it nor the rebuilt band is the block quoted here. The split data/MC streams of that
  earlier, rebuilt bootstrap are in Ref. ..."

**S5 (Q3, a base defect the batch moved). "Use it only after joint throws ... pass" is false for the 2D covariance.**
- After, `sec_systematics.tex:290-293`: "The block sum is therefore an approximation, valid only where the unfolding
  responds linearly, rather than the default way to build the covariance. We retain the per-source decomposition for
  attribution and use it only after joint throws and matched block endpoints pass the stated validation tests."
- Before: the same content, after the run-period block, opened by "More generally, this reframes ...".
- The 2D nominal covariance is the block sum `C = C_syst + C_stat + C_ML + C_PL` (`:271-272`). The note shows the
  unified throw used only for the five-axis covariance (`:286`, "The 5D result uses the strict joint ensemble";
  `app_statmethods.tex:247-249`). I found no 2D joint-throw test anywhere in the note.
- As read, the sentence says that the quoted 2D covariance has passed joint throws. It also contradicts "The nominal
  covariance is the block sum" from 20 lines earlier. The move made the contradiction adjacent, and "therefore" is new.
- **Fix:** scope the sentence to five dimensions: "The block sum is therefore an approximation, valid only where the
  unfolding responds linearly. In the five-axis covariance the per-source decomposition is retained for attribution,
  and the joint throws enter through the inflation of Eq. (zinflation) (§9.6)."
- If the director wants the 2D statement made explicitly ("no joint throw has tested the 2D block sum"), it needs a
  record first. I did not find one.

**S6 (Q2). One clause, with a source, resolves "no held-out split" (§3.1) against the "train/test split seed" (§4.7).**
- `M-TRAINING-DETAILS.md` §2: "`omnifold_loop` has an optional `train_frac`: it fits on a random subset and still
  evaluates on all rows (`omnifold_nn_core.py:196-204,229-246`). Only `seedscan_split.py:70` uses it."
- `seedscan_split.py`'s docstring makes it the producer of the ML-split band. `sbatch_seedscan_split_5d.sh:307-309`
  passes `--estimator-seed 42`, `--train-frac 0.8`, 24 splits. The 24 replicas match
  `PACKET-20260910-...:414-416`.
- The band's "test" set is therefore not held out. §3.1's sentence is true for the five configurations and false for
  this ensemble's replicas.
- **Fix, one clause in §4.7:** "...varies the seed of the random training subset on which each replica refits every
  classifier, evaluating on all events (the only use of a training subset; App. ... / training details §3.1)".
- Do not print "80%" unless the July producing revision is confirmed. The packet establishes only that its estimator
  line is byte-identical to today's (`Z_BUILD_PACKET.md:363`).

### NIT

- **N1.** `sec_method.tex:119`: "No execution log or run configuration was kept for the seed-42 central value". "Was
  kept" implies that a log existed. The source says only that none exists. Prefer "There is no execution log or
  recorded run configuration for ...".
- **N2.** `sec_systematics.tex:177`: "...a median 0.30 of that of the earlier ten-seed block, because the
  bootstrap×seed interaction ...". The colon became an explicit "because". The source (stageC REPORT §3) supports the
  explanation, so this is acceptable, but it is a stronger connective.
- **N3.** `sec_systematics.tex:336-352` comments:
  - The old comment still says "the three sentences from 'Its reference-free' to 'evidence of coverage' are D5's
    Required clause, verbatim". No such sentence has printed since the plain-language pass.
    `DECISION-20261018-joseph-plain-language-pass.md` (CITABLE FOR) replaced W2's verbatim requirement with "plain
    wording of the same content", so the comment is stale and binds nothing. Update it.
  - The writer's new comment cites `playlist-term/DESIGN.md §2` for the grouping, but the grouping is in §3, line 76.
    changes.md has §3 correctly.
- **N4 (Q4).** `sec_systematics.tex:540-542`: "about three percent of the combined budget in √Tr C" names no denominator.
  This is base text, not changed.
  - Against the syst+stat+ML block-sum √Tr 4.3578e-38 (SPEC-20260906 §1.1 "block-sum footing"; DECISION-20260831 §5),
    the ratios are 1.493/43.578 = 3.43% for the ML-split band and 1.306/43.578 = 3.00% for the estimator scan.
  - The scan's own log used this framing: "~3% of the 4.35e-38 total" (CRITERIA-20260811:194).
  - **Decision:** not a batch defect. If it is fixed, write "about three percent of the √Tr of the systematic,
    statistical and ML block sum", with the source in a comment. Do not use the inflated C_Z total; I did not measure
    it.
- **N5 (Q1).** The `values.tex:168-172` block comment is stale for `\gbdtMlSplitTrace`, but the new printed sentence is
  correct. Details under Q11 below. Flag it to the values.tex owner; the writer may not edit it.
- **N6.** `sec_method.tex:161-163`: the `hist` identifier was dropped while `exact` was kept. `app_guide.tex:32` and
  `app_codebase.tex:29` still list `hist`, and `sec_results.tex:228` says "HistGBT". The reader loses the link between
  them. Consider "(`hist`, ...)".
- **N7.** `REPORT.md` is missing from the writer's work directory. The writer brief lists it as a deliverable. The word
  counts, the guardrail list and the check outputs exist only in changes.md and checks_final.out.
- **N8. Merge hygiene.**
  - `origin/main` has moved to `5fb31c7e` (b4 and b6 merged). They do not touch this batch's three files.
  - `swallowed_text.py <wt> origin/main` now reports "flagged 1" in `sec_validation.tex`. That file is b6's, and the
    flag comes from main moving, not from this batch. Against `551f9432` the result is "flagged 0".
  - Re-run every check after rebasing.

---

## The specific checks requested

### 1. Q11: every link holds

| link | claim | verified |
|---|---|---|
| a | DECISION-20260920 §1 adopts `uq_5d/z_pilot_20260916_a5/z-cv.npz`, sha256 `3d7465f6…`, variant cv | yes (`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` §1; assembling revision `fb9ec356`) |
| b | That product's manifest has `ml` = `uq_cov_mlsplit_5d.root`, `27b2e456f80e15d8…` | yes (`VERDICT-20260920-third-lane-c5-c7-verification.md:65-77`, the eight manifest files of the `fb9ec356` assembly; artifact table `:155-161` lists z-cv `3d7465f6…` in the same directory; also SPEC-20260906:504 `S.ml_cov`) |
| c | √Tr of that file = 1.4934344281e-39 | yes (`Z_BUILD_PACKET.md:338-341`, "C_stat / C_ML" order, 1.8063275906e-39 / 1.4934344281e-39, with on-disk values; PACKET-20260910:414-416 independently says "the released products read 1.8063e-39 and 1.4934e-39" for stat5d and mlsplit5d) |
| d | `\gbdtMlSplitTrace` prints that value | yes (`values.tex:178`, 1.493e-39) |
| e | C_ML enters C_Z unmodified | yes: `sec_5d.tex:590-596` (Eq. zassembly) adds C_ML with no inflation; the 10,694 reported cells match the TH2D's 10,694 bins (Z_BUILD_PACKET:337) |

- **The new §4.7 opening** (`sec_systematics.tex:530-538`): "The ML term C_ML of the five-axis covariance used in this
  note (Eq. zassembly) is the split-varied band". This is supported.
- **"Candidate" removed:** correct. It entered at `6964af37` (2026-07-16), before the adoption. The before text already
  said "dominates the band used in this note".
- **§9.6 agrees:**
  - §9.6 is `sec:eavailw-construction`, page 64 in the aux. Eq. zassembly lists C_ML as a term.
  - §9.6 does not describe C_ML's construction, so there is no conflict.
- **Q1, decided: the values.tex comment.**
  - The comment says this block's macros "describe the earlier candidate campaign and are NOT the adopted product's
    numbers". For `\gbdtMlSplitTrace` the warning is wrong in substance. Z reused the same bytes (Z_BUILD_PACKET
    "REUSE 27b2e456…"), so the earlier campaign's ML band and the adopted C_ML are one object.
  - Its own trailing comment ("adopted ML split-seed band") is right.
  - No printed change is needed. Flag the block comment to the values.tex owner.
- **Q1, decided: the pre-flux-fix 12-seed scan.**
  - `\gbdtAiEstTrace` dates from 2026-07-14, before J28 (CRITERIA-20260811:194). The ML-split product was rebuilt on
    2026-07-13 (PACKET-20260910:419-421), also before J28.
  - The 87.5% ratio therefore compares like with like, and the new sentence's inference is no stronger than before.
    The writer's source comment records the pre-J28 date accurately.
  - It is not a term of C_Z, and the note calls it "an auxiliary robustness check, not an independent matrix".
  - No change is needed.

### 2. The estimator-scope sentences (§3.1, §3.2): FAIL (B1)

- Both sentences agree with App. C's wording word for word.
- Both disagree with Table 3, the validation table and §10.2 on §9.2. See B1.

### 3. The merged configuration list

- "Five used" is correct. (c) and (d) have results printed in §9.2 and in §9.5's coverage section.
- "Three main" is wrong for (b) (S1), and (c) is mislabeled (S2).
- The letter mapping (a) nominal, (b) exact, (e) joint-test agrees with Table 3. It also agrees with every use in the
  paper (`paper_body.tex:285,290,493,501,508,528,559-560,602,789`) and with the note (`sec_5d.tex:45` and the
  validation table).
- No fact from the two old paragraphs was lost:
  - 100 trees and 8 leaves, five iterations, "deterministic", "not combined", 400/31, the 15-fold reduction and
    3.5–4.1% → 0.11–0.24%, "selected before the joint-test design was fixed", and "not regenerated" all print.
  - "the 2D central value quoted until 2026-10-11" prints in the exact-split paragraph (`:143-144`).

### 4. Paper pointers into §§2–4

There are 8 pointers, all from `paper_body.tex`; `main_paper.tex` has none of its own. All 8 still hold.

| paper line | label | fact | still prints? |
|---|---|---|---|
| 274 | sec:method-algo (§3.1) | full-sample training; no held-out/cross-fitted split, early stopping or class balancing | yes, unchanged, `sec_method.tex:35-38` |
| 286 | sec:method-config (§3.2) | (a), purity subtraction | yes |
| 301 | sec:method-config | the full matrix | yes, Table 3 unchanged |
| 366 | sec:method-config | both learners; exact unseeded/seeded χ²; LightGBM chosen after the comparisons | yes (`:150-161`). The "ten seeds 2.64–2.75" range is printed in §6, not §3.2, at base too, so it is not a regression |
| 417 | sec:uq-combine (§4.5) | independent blocks, linear response; C_PL rank ≤ 2 | yes, `:271-274`, `:309-310` |
| 420 | sec:uq-2d-scope (§4.6) | miss-row approximation; two of 187 universes | yes, unchanged |
| 436 | sec:uq-combine | the size is not validated, and the block's own check cannot fail | yes, `:328-333` |
| 470 | sec:uq-2d-scope | omissions; the response family is assumed | yes, unchanged |

The brief's other facts also print:
- the central values not regenerated with the refinement (`sec_method.tex:210-212`);
- the exact-split seed spread is unmeasured (`:153`);
- the rebuilt band was not tested independently (`sec_systematics.tex:123-125`);
- the samples needed for validation are not available (§4.6, unchanged).

The label numbers are identical: the md5 of the sorted `sec:` newlabels matches the base build.

### 5. The run-period paragraph (§4.5)

D5 is in `state/2d-closeout/stageF/DRAFT-disclosures.md`, under "D5. The playlist-consistency term". Every
must-carry item survives:

- unknown cause, not a measured systematic of a known source (`:297-299`);
- what it covers: 1G–1M and 1N–1P in the same construction. The after text names all three groups in the construction
  (`:308-310`), and the grouping matches `playlist-term/DESIGN.md` §3 line 76 (A = 1A–1F, B = 1G/1L/1M, C = 1N–1P);
- a separate block, added after the other blocks (`:313`);
- its size, every number (`:313-323`);
- which period is right is not established (`:306` and `:325`).

The Required clause survives in equivalent wording, which `DECISION-20261018-joseph-plain-language-pass` permits:
- own simulated responses: `:309-311`;
- no reference period: `:311-312`;
- does not identify the correct period: `:325`;
- few groups, shrinkage and noise: `:325-327`;
- containment is not coverage: `:327-329`.

"Its own check cannot fail" also survives (`:329-331`), and so do the χ² 34.8 and 1.97 as "a sensitivity reading
only". The only problem is the stale comment (N3).

### 6. The open questions

- **Q1:** no printed change. Flag the values.tex comment (§1 above, N5).
- **Q2:** resolved by one clause (S6).
- **Q3:** a real defect, base text (S5).
- **Q4:** no denominator. Not a batch defect; a fix is given in N4.

---

## Direction checks

**A. Lost facts** (`rv_numcmp.py`, printed text without comments, before against after):
- §2: 74 numbers before and after, none lost.
- §3: 243 → 234. Lost:
  - 2026-10-11 twice (it prints once, `:144`);
  - "100" and "8" once each (stated in the paragraph above);
  - "2D" once (from "the 2D central value quoted until").
- §4: 227 → 227. Lost: one 2026-10-11 and one "5D"; gained four "1"s from the playlist names.
- No macro was lost.
- Every changed sentence was traced. The exceptions are the qualifiers in S3 and S4.

**B. Strengthened claims:** B1, S1, S3 and S5 (moved, with "therefore" added). N2 is minor.

These additions were verified and found correct:
- "not quoted" for the 3D budget (the records heading "...and why it is not quoted"; `sec_3d.tex:292`);
- "for LightGBM" after `\chiPaper` (`values.tex:125`, lgbm42);
- "LightGBM" for the ten-seed scan (source comment, "lgbm 10-seed mean");
- "so they include these migrations".

**C. Protected text:**
- The only verbatim marker in the three base files is the stale D5 comment (N3). It is superseded by the
  plain-language decision.
- No acknowledgment, funding, AI-use or `\pubhold` text is in these files.
- Only the three batch files differ from `551f9432` (`git diff 551f9432 --quiet` on everything else).

**D. Mechanics, re-run by me:**
- `check_ledger.py`: 143 rows, 236 probes, 0 failures, token audit 0. Its self-test passes, and the three planted
  probes fail as they should.
- `swallowed_text.py` against `551f9432`: flagged 0. Against the moved origin/main see N8.
- The build sources are byte-identical to the worktree (cmp).
- `build_final.out`: build_all rc=0.
- The gates pass: RESULT PASS, BODY-POINTERS PASS, SEC4-RECEIPTS 15/15.
- Struck-value containment: note, paper and primer each carry 0 of 69 struck values; records carries 64 of 64.
- checks_final.out reports RECORDS-MOVE PASS and RECORDS-PIN PASS. I did not re-run either.
- 0 undefined references and 0 `??`, as reported.
- The paper's pdftotext matches the base build byte for byte (my own cmp). Against rec3 only the date line differs.

**E. Register.** The target is largely reached in §2, §3 and most of §4. These passages still read as bookkeeping,
history or meta-text:
1. `sec_systematics.tex:259`: "These findings left the earlier printed budget unchanged."
2. `sec_systematics.tex:70-71`: "The earlier budget's values without the constraint weights and with the CV $\Phi$ are
   in Ref.~\cite{NoteRecords2026}, superseded values: retired material."
3. `sec_systematics.tex:208-210`: "A review of the saved products and code~\cite{TwoDFollowup2026} found further
   defects in the construction of the earlier 2D budget."
4. `sec_systematics.tex:491-494`: "...the band-centering numbers were not recomputed independently: they cannot be
   recomputed from the saved covariance products, and the verification compared only the checksums of their inputs."
5. `sec_method.tex:124-126`: "Seed~42 was chosen on cost: of the two ways of matching the central value and the
   statistical band in seed that the analysis design costed, a matched seed-42 statistical band was the cheaper."
6. `sec_method.tex:148-149`: "the run's own log was not found. Two driver revisions regenerate it to $7\times10^{-15}$"
7. `sec_systematics.tex:25`: "Detector and model systematics use the July universe sweep" (a date used as a name).
8. `sec_systematics.tex:514-515`: "That is a change in a square-root trace and is \emph{not} a bound on any individual
   bin" (a defensive restatement).

---

## Verdict: ADOPT-AFTER-FIXES

- Fix B1 in §3.1 and §3.2, and tell b3's owner about the same phrase in App. C.
- Apply S1–S4.
- Decide S5 and S6: each needs one sentence.
- Re-run the checks after rebasing onto `5fb31c7e`.

**Counts of what I checked:**
- 3 chapter diffs, read in full (273 lines added, 230 removed);
- 544 → 535 printed numbers, compared by script (every loss accounted for);
- 8 of 8 paper pointers;
- 5 links of the Q11 chain, plus 2 corroborating sources;
- D5: 5 must-carry items, the 4-part Required clause and the own-check clause;
- configurations: 5 rows of Table 3, 7 rows of the validation table and 9 paper sites;
- 4 open questions;
- 4 added specifics;
- 7 mechanical checks re-run.

**Not checked:**
- the 143 ledger rows one by one (I ran the checker only);
- whether the records document's tags and headings exist (I relied on RECORDS-PIN and RECORDS-MOVE PASS, and re-ran
  neither);
- §2's unchanged numbers against their primary sources;
- whether the 24-replica ML-split band's July producing revision used `--train-frac 0.8`;
- the √Tr of z-cv itself;
- whether the note discloses elsewhere that C_ML predates the J28 flux fix (outside this batch);
- the primer and PET note text;
- any register rating by an outside model.
