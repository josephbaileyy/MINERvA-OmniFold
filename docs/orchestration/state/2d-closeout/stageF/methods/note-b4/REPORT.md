# Batch b4 report: §5 Validation, guide to the appendices, App. A

Worktree `wt-note-b4` (branch `stageF/note-register-b4-20261021`, base origin/main 8f2df745). I edited only
`sec_validation.tex`, `app_statmethods.tex` and `app_guide.tex`. There are no commits and no git writes. Builds used
`PAR_GLOBAL_TMPDIR` under `wt-note-b4-work/`: `note-b4-base` was the unchanged base and `note-b4` the final build.

## Word counts (printed source words, comments stripped)

| file | before | after | change |
|---|---|---|---|
| sec_validation.tex | 2756 | 2855 | +99 |
| app_statmethods.tex | 6873 | 6808 | -65 |
| app_guide.tex | 367 | 364 | -3 |

The note went from 119 to 118 pages. §5 grew because overdense sentences were split and scope clauses written out
in full.

## Moves to the records
The records already print every item below. I did not edit the records document.
- The §5.1 W row clause "Replaces an earlier null run". Records: superseded values, withdrawn arguments, "From §closure-map, injected-W closure".
- The 2026-10-06 rebuild date. Records: superseded values, struck values table and provenance note ("rebuilt on 2026-10-06").
- The §5.3 pointer to the withdrawn split-sample reinterpretation. Records: "From §coverage, the 2D coverage test".
- App. A:
  - the superseded 50-replica bootstrap ("From §invert, rank deficiency");
  - the pointer on the superseded seed-varying set ("From §bootstrap");
  - the band-medians caption pointer and the two struck-values pointers of §minerva and "What is reported" (struck values);
  - the sentence on retracted pre-flux-fix predecessors;
  - the mask-origin pointer ("From §205bins");
  - the pointer to the withdrawn hidden-variable arithmetic ("From §closure-hv").
- The ten-seed-scan pointer is now cited once, at the closure thresholds where the scan matters, with heading "superseded values: retired material".
- The 2026-10-11 date was cut from App. A in two places. It still prints in sec_method ("Until 2026-10-11 the quoted 2D central value was an exact run").

Constraints the check scripts enforce, all respected:
- The posted records-move ledger pins two passages, so they keep their wording:
  - L10: "are kept in a separate internal records document, Ref., which is not part of this note";
  - L17: "Run period 2.137% (Ref., superseded values: struck values)."
- The records inventory requires 3 `coverage-fixed-truth` pointers in sec_validation. All 3 are kept.

## Qualifiers kept by the guardrail
- §5.2:
  - "since superseded" on the rebuilt band (ruling C7's "labelled historical");
  - "post hoc and partly circular";
  - "its branch for the undercoverage outcome was written after the pilot pulls had been seen";
  - "the rebuilt band and the quoted block have not been independently tested";
  - "not the quoted statistical block".
- "Both comparisons were measured for the exact-split cross-check" (5 versus 10 iterations; hist versus exact).
- "not a general impossibility result for 2D unfolding".
- App. A:
  - "computed with an earlier covariance built before the flux-band repair" (1.47);
  - "neither recomputed for the quoted central value and covariance" (regularization scan);
  - "the regularization scan shown above is of an earlier C^ours";
  - "Earlier statistical band" added to the audit-trail coverage row, as the source comment requires;
  - the earlier MAT check "was run on the sweep before the flux-band repair, so it could not detect ...".

## Rated quotes
- "An earlier version of this sentence used a legacy grouping …" no longer printed at base: 0 hits in either the base or the new pdftotext. The records-move ledger L17 asserts it is gone.
- "Three things have to be said … disclaimer placed elsewhere." Now reads "This is a descriptive distance, not a validation result, and three limits apply to every use of it."
- "… how much the unfold wobbles; …" Rewritten (A55).
- "Stability and efficiency. The 5-iter total σ …" Now four plain sentences.
- Other rated items, also rewritten:
  - the §5.2 opening (BOOK/HIST);
  - the attribution rule (PROC);
  - "That term was removed on 2026-10-06";
  - the rebuilt-band diagnostic sentence;
  - "No feasible route";
  - the MAT SetUnivWgts passage;
  - "quoted until 2026-10-11".

## Facts the paper points to (still printed)
- In §5.2 (`sec:coverage`):
  - the first band's test specified in advance ("specified before any toy was generated");
  - the 100-toy undercoverage;
  - the post hoc rescoring (0.977/0.781);
  - "post hoc and partly circular, because the band's MC part reuses the toys' resampling mechanism";
  - "The quoted statistical block is a third, different ensemble, 300 replicas at the central value's training seed".
- In §5.1 (`sec:closure-map`), unchanged: 3D 1.84% of 18.1% (ratio 0.102); 4D q3 within 1.1%.

## Open questions for the author
- Q1. §5 used to say "The proper full-covariance goodness-of-fit uses the χ²-vs-paper". App. A says no covariance-based goodness-of-fit is claimed. I wrote "The full-covariance comparisons are …". Confirm.
- Q2. "verified against MAT byte-for-byte" described a 5.5e-17 relative agreement. I wrote "element-by-element … (machine ε)", and "machine-precision check" in "What is reported". Confirm.
- Q3. Ruling C7 labelled the rescoring and the regularization scan "historical". I wrote "since superseded" and "(earlier covariance; …)", which keep the status without the history word. Confirm these satisfy C7.
- Q4. I added `\cite{MINERvA:2021owq}` and `Fig.~\ref{fig:uqbands}` to name the grouping ("Fig. 6/7 producer"). Both are already cited or defined in the note. The bibliography and label numbers are unchanged.

## Check outputs (final build `note-b4`)
```
== build log checks
BODY-POINTERS SELF-TEST :: PASS (25 cases: the appendix silent; 8 patterns fire in a body file and in a nested body file; a macro-printed digest fires; 7 legiti
BODY-POINTERS :: PASS (0 internal pointers in 17 body files)
RECORDS-PIN SELF-TEST :: PASS (9 of 9 cases as expected: a good pin passes; a branch, a non-ancestor, an unknown sha, a missing tag, a missing heading and no ci
RECORDS-PIN :: SKIP -- /private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-languag
SELF-TEST :: PASS
RESULT :: PASS :: head=unknown tree=unknown scope=? (tree_state.py helper not found) mode=strict products=main_records.pdf@sha256:67feee1fd82bc8af29d180e3f1618f
SELF-TEST :: PASS (18 perturbations rejected)
SEC4-RECEIPTS :: PASS (15/15)
  ok   PDF stage does NOT cover 12 \dead{} bod(ies) -- no decimal literal, or none with >=3 significant digits, so only the source check guards these: -1.6\%  [PDF-uncoverable: 1.6 -- under 3 significant digits, indistinguishable from an axis tick or a version
  ok   records.pdf carries 64/64 struck literals (positive control OK)
  ok   pet-note.pdf carries 5/5 struck literals (positive control OK)
  ok   note.pdf: 0 of 69 struck literals
  ok   paper.pdf: 0 of 69 struck literals
  ok   primer.pdf: 0 of 69 struck literals
== undefined references / citations per log
main_note: 0
main_paper: 0
main_primer: 0
pet_note: 0
main_records: 0
== ?? in pdftotext
main_note: 0
main_paper: 0
main_primer: 0
pet_note: 0
main_records: 0
== paper text vs rec3 and vs this batch's base build
paper vs rec3: byte-identical
paper vs base build: byte-identical
== note label numbers vs base build
label numbers identical (     184 labels)
== swallowed text
flagged 0
== records move probe (scratch copy)
RECORDS-MOVE :: PASS (27 labels, 29 tags, 97 struck bodies, 30 paths, 84 record and 20 reader paragraphs, 44 App. G pointers; 0 failure(s))
  fired  false ledger probe                   -> P7 ledger row L99: probe N:sec_intro.tex::'this sentence is not printed anywhere' does not hold
RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 12 of 12 planted defects fired their probe)
== records pin (worktree, a git checkout)
RECORDS-PIN :: PASS -- 70 citations, 35 tag and 48 heading references, pinned to 7986273b169e0c759f3156ddb9f784a51f0d7f72, 29 tags and 55 headings at the pin
== ledger
ledger rows 107, probes 176, failures 0; numeric audit failures 0
```

Ledger self-test (planted false N and X probes and a planted lost number 1.69 all fail):
```
-- planted false N and X probes:
Z1: NOT FOUND in sec_validation.tex: 'this sentence is not printed anywhere'
Z2: STILL PRINTS in sec_validation.tex: 'coverage'
ledger rows 109, probes 179, failures 2; numeric audit failures 0
-- planted lost number (1.69):
V3b: NOT FOUND in sec_validation.tex: '\\SI{1.69}{\\percent} for an injected \\SI{17.2}{\\percent} feature (ratio $0.098$), about ten times smaller'
NUMERIC: sec_validation.tex lost literals not in NUMLOSS: {'1.69': 1}
ledger rows 107, probes 176, failures 1; numeric audit failures 1
SELF-TEST PASS
```

## Review fixes (REVIEW.md, ADOPT-AFTER-FIXES), applied 2026-10-22

**Fixes, in the worktree's three files:**
- F1, `sec_validation.tex:270-272`: "The result above is for the earlier band. The rebuilt band was only rescored post hoc (below), and the quoted block has not been tested."
- F2, `app_statmethods.tex:392-399`:
  - "An earlier check compared MnvH1D::GetTotalErrorMatrix with our band sum without the normalization band (--add-norm 0), over 44 bands / 187 universes, and gave a maximum difference of 5.5e-17 of the largest element (machine ε) ...";
  - "... it ran on an older sweep from before the flux fix (Ref., superseded values: struck values), not on a quoted product, so it could not detect that the Flux band omitted those constraint weights." N7 is in the same sentence.
- F3, `sec_validation.tex:264`: "branch" becomes "clause".
- N1, `app_statmethods.tex:1040-1041`: "..., which was in force when the tests were graded".
- N2, `sec_validation.tex:80`: "could establish only".
- N3, `sec_validation.tex:59`: the semicolon is restored.
- N4, `app_statmethods.tex:805`: "only" is dropped.
- N5, `app_statmethods.tex:5`: "of this note's measurements, centered on the 2D comparison".
- N6, `sec_validation.tex:278`: "Post hoc rescoring against the rebuilt (since superseded) band."
- N8, `app_statmethods.tex:819`: "The ours-only χ² uses the truncated-spectral form".

**Ledger:** the rows for V7a, V16c, V16h, V17c, A1a, A7, A19b, A19c, A42a, A43 and A55b are updated. I added X probes for the old wordings.

**Rebuild:**
- A scratch copy of 5df6f96a (`git archive`, read-only) with the three files overlaid, built as `note-b4`.
- Unmodified 5df6f96a, built as `note-b4-mainbase`.
- Both used the private `PAR_GLOBAL_TMPDIR` `wt-note-b4-work/par-tmp3`.
- Outputs: `checks_main.out`, `build3.out`, `build-mainbase.out`.
