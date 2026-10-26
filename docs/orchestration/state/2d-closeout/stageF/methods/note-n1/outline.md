# Note register round n1: outline for the director (2026-10-25)

**Base:** origin/main `ddf16f10`. Branch `stageF/note-register-n1-20261025`.

**Brief:**
- the caveat-study note rules R-N1 to R-N7 (`caveat-study/REPORT.md` §5.2);
- register-prd-study R1–R10;
- the note's own sentence-level standard. The note is the fully qualified companion, so a qualifier stays wherever
  leaving it out would make a printed sentence false.

**Not touched:**
- every label the paper references through `\externaldocument` (all N- labels);
- `values.tex` and `values_inference.tex`;
- text bound by checks, including SEC4's new sites in `sec_validation.tex`:
  - "lies entirely below its window (Gaussian 0.954)";
  - "removes the tail undercoverage: $C_2=0.977$ $[0.974,0.980]$ and $C_1=0.781$";
  - the `\covTwoDCTwo` uses;
  - the `check_dead_containment.py` struck-value sites;
- the records PDF and `app_history.tex`;
- the note's abstract (`main_note.tex`). This outline proposes no abstract change;
- App. G (`app_release.tex`, result package and reproduction limits), which is release text and Joseph's.

**Data:** the caveat study's note inventory (`caveat-study/inv/ours-note-*.tsv`, 967 rows at `fe92211c`), mapped to
chapters by each quote's position in the blinded note. Only 2 rows did not map. The note has changed little since: one
sentence in r18, and the §3.1 fix.

## 1. Where the caveats are

Statements per chapter: kinds (a) history, (b) deviation, (c) untested or omitted, (d) scope, (e) process.
<!-- absence-ok: "untested or omitted" names a kind of statement in the outline's classification; not an absence claim -->

| chapter | words | statements | a | b | c | d | e | per 1,000 words |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Executive summary | 1,753 | 76 | 3 | 6 | 39 | 26 | 2 | **43.4** |
| §1 Introduction | 977 | 4 | 0 | 0 | 1 | 3 | 0 | 4.1 |
| §2 Experiment and samples | 1,333 | 6 | 0 | 0 | 6 | 0 | 0 | 4.5 |
| §3 Procedure | 3,142 | 32 | 3 | 1 | 17 | 7 | 4 | 10.2 |
| §4 Uncertainty blocks | 4,131 | 97 | **12** | 2 | 67 | 12 | 4 | 23.5 |
| §5 2D validation | 2,831 | 82 | **11** | 7 | 33 | 29 | 2 | 29.0 |
| §6 Results | 2,679 | 17 | 0 | 0 | 11 | 6 | 0 | 6.3 |
| §7 3D and 4D | 4,537 | 73 | 2 | 0 | 37 | 33 | 1 | 16.1 |
| §8 (E_avail, W) | 2,216 | 31 | 0 | 1 | 19 | 11 | 0 | 14.0 |
| §9 5D estimator | 5,459 | 116 | 1 | 2 | 75 | 31 | 7 | 21.2 |
| §10 Joint tests | 5,722 | 103 | 2 | 13 | 62 | 15 | **11** | 18.0 |
| §11 Extended fiducial | 1,129 | 19 | 0 | 1 | 11 | 7 | 0 | 16.8 |
| §12 Summary | 1,091 | 41 | 2 | 2 | 19 | 15 | 3 | **37.6** |
| App. A 2D statistics | 6,757 | 96 | **13** | 1 | 58 | 23 | 1 | 14.2 |
| App. B N-D statistics | 2,035 | 40 | 2 | 1 | 21 | 13 | 3 | 19.7 |
| App. C negative weights | 3,457 | 59 | 3 | 4 | 19 | 22 | **11** | 17.1 |
| App. D mismatch closure | 400 | 13 | 0 | 0 | 6 | 4 | 3 | 32.5 |
| App. G release (not touched) | 1,721 | 27 | 4 | 0 | 15 | 5 | 3 | 15.7 |

The long comparators run 2.1–4.8 statements per 1,000 words. Two patterns drive the excess:
1. **The executive summary and §12 restate almost every body caveat.**
2. **§4, §5 and App. A carry most of the history of superseded 2D products**, and §10 and App. C most of the process
   vocabulary.

## 2. R-N1: each caveat stated once where the method is described; the summaries restate only the principal ones

**The caveats restated most** (statements: chapter × count), and where each lands:

| caveat | now | lands (stated once) | the summaries keep |
|---|---|---|---|
| residual regularization bias, unassigned | §9 ×12, §5 ×3, ES ×2, §4, §8, §12, abstract | **§9.2** (sec:val-departure) | one clause in ES and §12 |
| generator comparisons are descriptive central values | §7 ×6, ES ×3, §8 ×3, §12, abstract | **§7 lead** (one sentence for §7 and §8) | one clause |
| comparisons identify no mechanism | §7 ×6, ES ×3, §8 ×3, §12, abstract | **§7 lead** | one clause |
| the earlier 2D statistical band undercovered | §5 ×10, ES ×2, §4 ×2, §12 | **§5.2** (sec:coverage, the history's home; check-bound) | ES and §12: "the quoted block's coverage is untested (§5.2)" |
| recoil-response uncertainty omitted from the tests | §10 ×11, ES, §12, abstract | **§10.4** (sec:joint5d-response), with one clause at each consequence | one clause |
| scalar-5D covariance limitations | ES ×6, §9 ×5, §12 ×2 | **§9.6** (sec:eavailw-adopted, its four measured limitations) | ES: one sentence pointing to §9.6 |
| 5D statistical-interval miscoverage | §9 ×9, ES ×2, §12 | **§9.4** (sec:coverage-5d) | one clause |
| no 3D or 4D covariance quoted | §7 ×9, §4 ×2, §3 | **§7 lead** | none needed |
| the generator tests' calibration assumptions | §10 ×7, ES ×2, §12, abstract | **§10.3** (sec:joint5d-frozen; A1, A2) | one clause |
| no detector-response-mismatch test | §5 ×6, §9 ×2, §1, §8 | **App. D's pointer from §5**: one sentence in §5, the rest at App. D | none |
| PET is future work | ES ×3, §1 ×2, §12 ×2, §2, §3, abstract | **§1** once (R-N5 scope) and App. F | none |
| the extended-fiducial value is prior-dominated | §11 ×6, ES ×2, §2, §12 | **§11** | one clause |
| the 2D uncertainty is not independently validated | §5 ×6, §4 ×2, abstract | **§4.6** (sec:uq-2d-scope) | the abstract stays as is |
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

**Moves:**
- **S1, the executive summary.**
  - The executive summary keeps its results and replaces the "What is not claimed" list with one paragraph that restates
    the principal limitations. Each limitation gets one clause and a section pointer, as in the paper's VIII A.
  - Every list item keeps its fact at its home section. The ledger maps each clause to its home.
  - Expected: 76 → about 30 statements.
- **S2, §12.** The same treatment: its restatement list becomes one paragraph. Expected: 41 → about 15.
- **S3, the body chapters.** Within each chapter, a caveat restated in several paragraphs keeps one statement where the
  method is described. The others become a pointer or go.
  - The biggest gains are §9 (the bias ×12, miscoverage ×9) and §10 (the recoil response ×11, calibration ×7).
  - A restatement stays where it qualifies a different printed number, so that sentence stays true. The ledger records
    each one.

## 3. R-N2: history in one passage per subject, framed as improvements; the rest to the records

| subject | where it is now | the single passage | elsewhere |
|---|---|---|---|
| **the two superseded 2D statistical bands** | §5 ×11 (check-bound), ES ×2, §4 ×2, §12, App. A ×4 | **§5.2, as it stands.** It is the paper's pointer target and SEC4's site. | ES, §4, §12 and App. A say only "the quoted block's coverage is untested (§5.2)". App. A's tables keep the label of which band a number used, which is needed for truth. |
| **the earlier 2D budget's defects** (the May sweep's truth mismatch, the Rvn1pi/Rvp1pi double count, background-template statistics not propagated) | §4 ×7 | **one compact paragraph in §4.6** (sec:uq-2d-scope), "Changes from the earlier 2D budget", framed as what the quoted budget corrects | **nothing moves out:** `app_history.tex` does not print these defects (checked), so every fact stays in that paragraph |
| **the 2D central value's history** (exact-split until 2026-10-11, then LightGBM, then refined (f) on 2026-10-24) | §3 ×3, ES, §12, App. A ×3, App. C ×2 | **one sentence in §3.2** (sec:method-config): "The quoted 2D result is configuration (f); results labelled exact-split use the exact-split cross-check" | the dates go to the records (`app_history.tex:89-92`). App. A keeps "numbers for the exact-split cross-check" labels where a number uses it. |
| **the generator-flux repair** | §7 ×2, §9 (historical deformations), App. G (not touched) | **one sentence in §2** (samples): "The predictions use the flux-repaired generator samples of 2026-09-27" | §7's narrative of the defect goes to the records; §9 keeps "built before the flux repair" as the label of its historical truths, which is needed for truth |
| **superseded 5D covariance constructions** | §4, App. B ×2 | **App. B**, one sentence | §4: a pointer |
| **the lost-draw sensitivity, superseded by the rerun** | §10 | **§10.6** (sec:joint5d-lost), as it stands (Joseph's §5 disposition) | — |
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## 4. R-N6: process vocabulary removed

Each phrase is replaced by its physics content, or removed where the fact prints without it. Any fact the phrase
carries stays. The ledger records each change.

| chapter | phrases (count) | replacement |
|---|---|---|
| ES, §12 | "recorded decisions left standing" (×2); "tests specified in advance" (×2) | "the ten decisions are unchanged"; "tests whose design was fixed before the data were examined", stated once, in §10.3 |
| §3 | "has no execution log or recorded run configuration"; "the run's own log was not found"; "seed 42 was chosen on cost …"; "selected before the joint-test design was fixed" | each kept as a plain fact where it bears on a result: the seed-42 central value's provenance limits its reproduction; the seed choice stated with its basis (R-P4); "selected before the joint-test design was fixed" kept once, in §10.3 |
| §4 | "a review of the saved products and code found …"; "the May input and code revision are not available"; "the driver version was not committed"; "no design for one has been registered in advance" | "the saved products and code show …"; the unavailability kept as one fact; "registered in advance" dropped, since "No coverage test on held-out simulation has been run" keeps the fact |
| §5 | "predeclared criteria"; "stopped under its futility rule" | **check-bound sentences are not touched.** Elsewhere: "the criteria, fixed before the test" once; the futility stop kept as fact |
| §7 | "In 2026 the collaboration confirmed that this is current practice" | "This is MINERvA's current practice" (Ref.), once |
| §9 | "fixed in advance" (×3); "the study's rules allow"; "used under an exception that covers only this file … the file's own metadata records it as not passing" | criteria stated as criteria (R-P4); the exception's fact, that this covariance does not meet its specification and is used for this projection only, stated once, plainly, in §9.6 |
| §10 | "pre-registered specification"; "[a recorded ruling on the pilot]"; "this value comes from the design review"; "independently reviewed beforehand"; "they do not re-grade the decisions …, which stand"; "reported under the label"; "documented in Ref. [53]; each later study cites its own record" | the design's pre-specification stated once (§10.3, R-P7's one sentence); the pilot ruling as its content ("negative weights clipped per universe, ≤ 0.35% of a band's shift"); "re-grade" and "stand" become "the ten decisions are unchanged". **DECISION-20261020 requires "do not re-grade" in the note (r16), so that phrase stays; it is flagged for you.** |
| App. B | "predeclared rank cut in records"; "no new independent scientific review of the synthesis is claimed" | the rank cut stated as its value; the review sentence removed (no scientific content) |
| App. C | "a recorded choice, not a silent default (Ref. [41], oi6-oi8-oi126)"; "carries an obligation to revisit the background treatment before submission" (×3); "used under an exception limited to the file with its checksum"; "removes one blocking decision" | the choice stated with its basis ("purity is kept for the five-dimensional chain because switching would have invalidated the flux-corrected covariance"); the obligation stated once, as status ("the background treatment of the five-dimensional chain is to be revisited") — **flagged for you, as it is a commitment**; the exception as in §9 |
| App. D | "an amplitude fixed before inspecting results"; "the collaboration requests"; "would not be silently absorbed" | the protocol in physics terms; App. D's protocol status ("implemented; not yet run") stays |
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## 5. R-N5: scope stated once

- **§1** states the note's scope once:
  - one implementation, one data set;
  - central values without intervals of validated coverage above 2D;
  - tests of hybrid nulls;
  - PET as future work.
- The executive summary's scope sentences become the §1 statement's single restatement.
- The scope restated in §7–§10 leads goes, except where a section's own result needs it to be true. For example, §10's
  "hybrid nulls" stays, because it is the result's definition.

## 6. Pieces and scoring

**Pieces.** These are the n1base pieces N01–N14 (`xmodel/n1base/split_note_n1.py`), re-split on the new build at the
same chapter boundaries.

**Batches:**

| batch | chapters | moves |
|---|---|---|
| n1-A | ES, §1, §12 | S1, S2, R-N5; process in ES and §12 |
| n1-B | §3, §4, §5 | R-N2 (2D band pointers, budget defects, 2D CV history); R-N6; R-N1 within chapters |
| n1-C | §7, §8, §9 | R-N1 (§9's bias and miscoverage); flux-repair history; R-N6 |
| n1-D | §10, §11 | R-N1 (recoil response, calibration); R-N6 |
| n1-E | App. A, B, C, D | R-N2 (App. A labels kept); R-N6 (App. C) |

**Method, as in note-b3 to b8:**
- writers per batch;
- a two-direction review;
- agy agreement on every changed passage;
- a fact ledger with `N:` probes, and a probe for every moved fact's new home;
- the full build, with `check_sec4_receipts.py` and all of `build_all`'s gates.

**The decider, per piece:** P2N pairwise, both models, both orders. A piece is adopted if it wins at least 3 of 4.
P1N is reported.

**Stop:** P2N no longer prefers the new version, or P1N reaches 3.5 or more, or 4 rounds.

## 7. Questions for you

1. **App. C's "obligation to revisit the background treatment before submission"** is a commitment, not a caveat. May
   n1 restate it once, as status, or must its wording stay?
2. **§10's "do not re-grade the decisions"** is required by DECISION-20261020 (r16 kept it in the note). Keep it
   verbatim?
3. **The earlier 2D budget's defects (§4).** May n1 gather the seven statements into one compact "changes from the
   earlier budget" paragraph in §4.6? Every fact stays in the note, because `app_history.tex` does not print them.
4. **Batch order:** A first, since it has the largest restatement gain? Or all five batches in one round?
