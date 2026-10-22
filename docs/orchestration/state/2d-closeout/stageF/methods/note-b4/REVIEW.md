# Review of batch b4: §5 Validation, App. A, guide to the appendices

Reviewer: independent and read-only. I edited no worktree and made no commits. My scratch outputs are in
`wt-note-b4-work/rv/` and my tool is in `S/rv-b4tools/numdiff.py`.

Versions:
- **Before:** `wt-note-b4-work/before/*.tex`. All three files are byte-identical to `git show 8f2df745:` (cmp).
- **After:** the uncommitted edits in `S/wt-note-b4`. Only the three batch files are modified.
- **Build:** `S/plain-language/builds/note-b4/`. Its copies of all the `.tex` files are byte-identical to the
  worktree (cmp, every tracked file).

## Findings

### BLOCKING

**F1. §5.2: the quoted statistical block's "not tested" status became "not independently tested".**
- `sec_validation.tex:269-272`
- Before: "This section's result is for the earlier band and was not re-tested."
- After: "The result above is for the earlier band; the rebuilt band and the quoted block have not been
  independently tested."
- Why it matters:
  - "independently" covers both nouns, so as read the quoted block has had some test that was not independent.
  - It has had none. The records (`coverage-fixed-truth`) say the quoted block is "the 300-replica seed-42 ensemble
    of §4.2, which these toys did not score".
  - The source comment at `sec_validation.tex:215-216` says "which this test did not score (NR)".
  - The paper, which cites this subsection, says "The coverage of this block, and of the total, has not been tested."
  - For the rebuilt band, "not independently tested" is correct, since its only test is the post hoc, partly
    circular rescoring.
  - The sentence weakens a disclosed limitation of the quoted block.
- Fix: "The result above is for the earlier band. The rebuilt band was only rescored post hoc (below), and the quoted
  block has not been tested."

**F2. §A.2.6 (MAT): the earlier MAT check now names the wrong sweep, and its comparison is no longer stated.**
- `app_statmethods.tex:392-398`
- Before: "Our band sum was verified against MAT byte-for-byte: filling a MnvH1D with the same 44 bands / 187
  universes and comparing MnvH1D::GetTotalErrorMatrix with our band sum without the normalization band (--add-norm 0)
  gives … It filled … and it ran on the sweep before the flux fix: it could not detect that the Flux band omitted
  MAT's ν–e and inverse-muon-decay constraint weights (Ref., superseded values: struck values)."
- After: "An earlier element-by-element check, with the same 44 bands / 187 universes and our band sum without the
  normalization band (--add-norm 0), gave … It filled … and it was run on the sweep before the flux-band repair, so it
  could not detect that the Flux band then omitted those constraint weights."
- (a) The referent changed: "flux fix" became "flux-band repair".
  - The note uses "flux-band repair" for the C04 constraint-weight repair (`app_statmethods.tex:604`, `:686`).
  - The check ran on the older, pre-flux-fix `universe_stage2_MEFHC_full_matcorr` sweep. The flux fix divides each
    PPFX universe by its own Φ_u.
  - Sources:
    - `docs/orchestration/state/2d-closeout/stageB/verify-c04-x01/VERIFICATION.md:122`: "Which sweep it ran on: the
      pre-fix sweep … The fluxfix product that is actually quoted was never compared against MAT";
    - `KNOWN_ISSUES.md` row 95;
    - `stageB/REPORT.md:109-110`.
  - "The sweep before the flux-band repair" reads as the product that was quoted just before C04, which is the
    fluxfix sweep that was never checked. As read, the sentence is false about which product was checked.
  - The new "so" also makes the sentence circular: the check could not see the omission because it ran before the
    repair of that omission.
- (b) What the check compared is no longer stated. "comparing MnvH1D::GetTotalErrorMatrix with our band sum" was
  dropped, so the sentence names only one side.
- (c) Moving the sentence after the 3.4e-16 sentence ties "the same 44 bands / 187 universes" to the quoted
  universe block. That block holds 43 bands plus the normalization (`:198`, `:284`) and comes from a different (July)
  sweep.
- Fix: "An earlier check compared MnvH1D::GetTotalErrorMatrix with our band sum without the normalization band
  (--add-norm 0), over 44 bands / 187 universes, and gave … It filled the MnvH1D without MAT's per-universe weights
  (SetUnivWgts), so both sides were unweighted, and it ran on an older sweep from before the flux fix
  (Ref.~\cite{NoteRecords2026}, superseded values: struck values), not on a quoted product, so it could not detect
  that the Flux band omitted those constraint weights."
  - Row 1 of R4.1 defines that pre-flux-fix rollup, so the restored pointer resolves.

### SHOULD-FIX

**F3. "branch" is back as internal jargon.**
- `sec_validation.tex:263-264`
- Before: "(its rule for the undercoverage outcome was written after the pilot pulls had been seen)"
- After: "The attribution rule was fixed before the full run, but its branch for the undercoverage outcome was
  written after …"
- The writer brief bans "branch".
- Fix: "but its clause for the undercoverage outcome was written after …"

### NIT

**N1. The ten-seed floor sentence** (`app_statmethods.tex:1039-1040`).
- Before: "the 0.166% ML floor of the ten-seed scan in force when the tests were graded"
- After: "… of the earlier ten-seed scan, against which the tests were graded"
- The tests were graded against their thresholds. Records R4.3.1 say "The closure thresholds of §A.6 were graded
  against this 0.166% floor."
- Fix: "the 0.166% ML floor of the earlier ten-seed scan, which was in force when the tests were graded".

**N2. "measures" for a check that was never run** (`sec_validation.tex:80`).
- Before: "such a check can support only conditional precision"
- After: "such a check measures only the precision conditional on them"
- Per `two-d-followup/REPORT.md:287`, the check is proposed and "nothing is measured yet".
- Fix: "such a check could establish only the precision conditional on them".

**N3. A causal link was added** (`sec_validation.tex:58-60`).
- After: "The test requires the residual … to be far smaller than the deviation itself, because unfolding cannot
  create discriminating power"
- The before text joined these with a semicolon.
- Fix: restore the semicolon.

**N4. "only" was added** (`app_statmethods.tex:804`).
- After: "The data/MC split bootstrap was run only on the earlier rebuilt bootstrap".
- The records (R4.3.1 (i)) say its MC-only stream was run before the completeness fix. The preceding paragraph
  already says the test was not repeated for the quoted block.
- Fix: drop "only".

**N5. The App. A scope was narrowed** (`app_statmethods.tex:5`).
- Before: "the measurement's statistical methods"
- After: "the statistical methods of the 2D measurement"
- App. A also sets the ours-only χ² convention over the 1431 3D bins (`:818-820`).
- Fix: "the statistical methods of this note's measurements, centred on the 2D comparison", or keep the old wording.

**N6. The heading is ambiguous about what is superseded** (Q3; `sec_validation.tex:278`).
- After: "Post hoc rescoring against the rebuilt band, since superseded."
- The heading is grammatical, but "since superseded" can attach to the rescoring.
- Fix: "Post hoc rescoring against the rebuilt (since superseded) band."

**N7. A pre-existing wording error, in a sentence the writer rewrote** (`:394`).
- The text says "maximum element-wise relative difference of 5.5e-17".
- The quantity is max|diff|/max|cov| (`VERIFICATION.md:124`). The 3.4e-16 sentence already uses the correct form:
  "of its largest element".
- Fix: "a maximum difference of 5.5e-17 of the largest element".
- This is not introduced by b4 and is optional.

**N8. A pre-existing usage that sits close to Q1** (not a b4 change).
- `app_statmethods.tex:818` still says "The ours-only goodness-of-fit uses …", while `:896` says "no
  covariance-based goodness-of-fit is claimed".
- Consider "The ours-only χ² uses …".

## The four requested checks

**1. §5.2 band history.** Each item prints exactly in §5.2 (`sec_validation.tex`):
- The test was specified before any toy: "The design, criteria and positive control of the test were specified
  before any toy was generated (Ref., coverage-fixed-truth)."
- The 100-toy undercoverage: "The band fails: it undercovers in its tails", with C2 below its window at
  N_toy = 100, and "Under the predeclared criteria this is a failure by undercoverage".
- The rescoring is post hoc and partly circular: "The rescoring is post hoc and partly circular, because the band's
  MC part reuses the toys' resampling mechanism", with C2 = 0.977 and C1 = 0.781.
- The 300-replica block: "The quoted statistical block is a third, different ensemble, 300 replicas at the central
  value's training seed (§4.2)."
- All four hold. F1 is the one defect in the adjoining sentence.

**2. History pointers moved out.** 14 printed `\cite{NoteRecords2026}` pointers were removed (2 in §5, 12 in App. A);
1 of them moved to §A.6. I checked each fact in the records' pdftotext, and each prints at the cited heading:

| Removed pointer | Where the records print it |
|---|---|
| W row, "Replaces an earlier null run" | R4.2 "From §5.1, injected-W closure" |
| Same-ensemble split-sample reinterpretation | R4.2 "From §5.2, the 2D coverage test" |
| 50-replica bootstrap | R4.1.1 "From §A.1, rank deficiency" |
| pinv nσε convention | R4.2 "From §A.1, pseudo-inverse"; the body keeps "not that convention" |
| Seed-varying set | R4.1.1 "From §A.2.2, the bootstrap block" |
| Band-medians caption earlier values | R4.1.1 "From §A.2.4, Table 16" |
| MAT and "What is reported" struck values | R4.1 row "The Flux band omitted MAT's per-universe ν–e …" |
| Retracted pre-flux-fix predecessors | R4.2.1 "Those four figures and that inference are retracted" |
| Mask origin | R4.1.1 "From §A.3.1, the strict-interior mask" |
| Hidden-variable arithmetic | R4.2 "From §A.6.2" |
| Ten-seed scan | R4.3.1 "The ten-seed scan (VL175 era)", under the heading "…: retired material" |

- The 2026-10-06 date prints in R4.2.1: "rebuilt on 2026-10-06, because they divided by a bootstrapped
  completeness".
- The labels the records cite match the after build: A.1, A.2.2, A.2.4 (Table 16), A.2.7, A.3.1, A.6.2, 5.1 and 5.2.
- The records' pdftotext is byte-identical to the base build's.
- The 2026-10-11 date still prints in the after note, in §3.2 `sec:method-config` (`sec_method.tex:135`, label at
  `:80`): "Until 2026-10-11 the quoted 2D central value was an exact run". It also prints at `:94` and `:176`.
- The claim that the tension derivation was made while the exact-split run was quoted is supported: it was created
  in `735c909d` on 2026-05-30.

**3. The writer's questions.**
- **Q1. The writer is right.**
  - App. A:894-896 says "no covariance-based goodness-of-fit is claimed".
  - `sec_results.tex:51-54` says "none is a calibrated goodness-of-fit test".
  - Packet ruling C5 (`state/2d-closeout/stageF/DECISION-PACKET-J3-J6.md:52`) says "it cannot be a goodness-of-fit".
  - "The full-covariance comparisons are …" removes a contradiction without strengthening anything. See N8 for a
    leftover use elsewhere.
- **Q2. The writer is right.**
  - A 5.5e-17 difference is not byte identity, so "byte-for-byte" overstated the check. The phrase was the script's
    self-description (`verify_matcorr_vs_mnvh1d.py:2`), and the records do not print it.
  - "Machine precision" matches the printed (machine ε).
  - The change weakens the claim to what the number supports. See N7, which goes further.
- **Q3. Satisfied in substance.**
  - C7 (`DECISION-20261018-joseph-2d-j3-j5-provisional.md:29`; packet line 54) reads "Keep, labelled as historical.
    They describe earlier objects, so no Q claim rests on them."
  - The §5.2 heading keeps "post hoc" and marks the band "since superseded". The App. A heading reads "(earlier
    covariance; …)", and the body says "neither recomputed for the quoted central value and covariance".
  - Both labels convey that the object is earlier and that no claim about Q rests on it.
  - C7 is provisional and is "NOT CITABLE FOR final claim or disclosure wording", so the exact word is not fixed.
  - Disambiguate the §5.2 heading (N6).
  - Joseph should be told that the C7 wording changed, and that `sec_results.tex:70` (outside b4) still says "as
    history". The two batches now label the same scan differently.
- **Q4. Correct.**
  - The `fig:uqbands` caption (`sec_systematics.tex:58-64`) says "grouped as in Figs. 6--7 of
    Ref.~\cite{MINERvA:2021owq}". Its files are `MEFHC_fig6_7_*`, so "Fig. 6/7 producer" names that figure.
  - The bib key exists (`technote.bib:331`, Ruterbories, PRD 104).
  - The label numbers and the paper text are unchanged.

**4. The paper's pointers into this batch.**
- Only two `\nsec`/`\napp` pointers land in batch labels: `paper_body.tex:449` to `sec:coverage` and `:487` to
  `sec:closure-map`.
- `sec:coverage`:
  - two earlier band versions, distinct from the quoted block, scored at a fixed truth: yes;
  - the first band's test specified in advance and undercovering in the tails: yes;
  - the post hoc rescoring at 97.7% / 78.1%: yes;
  - not independent, because the simulated part reuses the resampling: yes.
  - All print in §5.2. The paper's "has not been tested" for the quoted block conflicts with the new "not
    independently tested" (F1).
- `sec:closure-map` (§5.1):
  - "1.84 % of 18.1 % injected (ratio 0.102)" and "q3 ratios within 1.1 %" are unchanged in the table.

## Mechanics (D)

- **build_all:** rc=0 (`build1.out`, `build2.out`).
- **Build log:** BODY-POINTERS PASS, RECORDS-PIN SELF-TEST PASS, RECORDS-PIN SKIP in the build copy, RESULT PASS,
  SEC4-RECEIPTS 15/15, and struck-value containment passing (note 0 `\dead`, records 97).
- **Undefined references:** none in `main_note.log`. The 30 "undefined" lines are font-shape warnings.
- **`??`:** none in the note's or the paper's pdftotext.
- **Paper:** the pdftotext of `main_paper.pdf` is byte-identical to the base build and to rec3 (sha256 `82701c0e…`
  for all three). Its `\newlabel`s are identical to the base.
- **Note labels:** 184 label numbers, identical to the base build.
- **Records and primer:** pdftotext identical to the base build.
- **Swallowed text:** `swallowed_text.py` against 8f2df745 reports "flagged 0".
  - origin/main has moved to 551f9432 since. I compared against the batch base.
- **Writer's checker:** rc=0, with 107 rows, 176 probes and 0 failures. A planted `N:` probe for "verified against
  MAT byte-for-byte" fails, at rc=1.
- **My own numeric diff** of comment-stripped printed literals, before against after, finds only these losses:
  - the dates 2026-10-06 and 2×2026-10-11;
  - "5-iter"/"10-iter"/"≈10×", now spelled out in words;
  - "50" (50-replica, now in the records);
  - one "205" ("205 is not assumed"; the 205-bin scan stays).
  - The gains are the "2D" in χ² strings and the `2021owq` cite key.
  - No `\cov…` or `\chi…` value macro was lost.
- **Protected text:** the verbatim comment block at `app_statmethods.tex:251-260` is untouched. Both pinned
  records-move passages print:
  - L10, the guide sentence "are kept in a separate internal records document, Ref., which is not part of this note";
  - L17, "Run period 2.137% (Ref., superseded values: struck values)", at `:299`.

## Register (E)

The batch largely reaches the target register. The rated meta and history quotes are gone. These passages still read
as bookkeeping or meta-text:
1. "This test asks whether the 2D statistical band quoted when it ran covers a fixed truth at its nominal rate. That
   band is an earlier one (Ref. [38], superseded values and coverage-fixed-truth), not the quoted statistical block."
   "Quoted when it ran" and "an earlier one" say the same thing twice.
2. "Post hoc rescoring against the rebuilt band, since superseded."
3. "The power has to be named because the two ratios describe the same comparison and differ by more than a factor
   of two."
4. "The data/MC split bootstrap was run only on the earlier rebuilt bootstrap; its closure, its data-only stream and
   its structure comparison are given in Ref. [38], superseded values: retired material."
5. "the convention of the earlier 3D generator scan over all 1431 reported bins (Ref. [38], superseded values:
   superseded uncertainty constructions)"
6. "Its numbers are for the exact-split cross-check, which was the quoted 2D central value when it was made (§3.2)."
7. "exact-split, 5 iter (cross-check; earlier central value)"
8. "The attribution rule was fixed before the full run, but its branch for the undercoverage outcome was written
   after the pilot pulls had been seen". The paper needs this disclosure. Only its wording (F3) is at issue.

## Verdict

**ADOPT-AFTER-FIXES.** F1 and F2 are one-sentence repairs. F3 is a word.

## Counts

- Diff hunks: 3 files, every hunk read (word diff).
- Records pointers: 14 removed or moved, each verified in the records' pdftotext; 11 record headings and passages
  matched.
- Writer's questions: 4 decided from sources.
- Paper pointers: 2 checked.
- Builds: 3 pdftotext comparisons (paper, records, primer) and 1 label comparison (184 labels).
- Writer's checker: run, plus 1 planted probe.
- Numeric literals: diffed in 3 files.
- Sources opened for specific claims:
  - C7 and C5 records;
  - the MAT check sources (VERIFICATION.md, KI-95, Stage B REPORT, STUDY_STATUS);
  - the two-d-followup REPORT;
  - the `fig:uqbands` caption;
  - the git history of the tension derivation and of the "both measured" clause (25720215);
  - `sec_method` for the 2026-10-11 date.

## Not checked

- Every one of the 107 ledger rows by hand. I relied on the writer's checker plus my independent diff and numeric
  scan.
- The Canelli guide's wording of its recovery test (N3).
- Whether the pre-flux-fix May sweep had exactly 44 bands / 187 universes. I took the count from the before text.
- The P1N register re-rating.
- Any pointer from the primer or the PET note into the batch labels.
