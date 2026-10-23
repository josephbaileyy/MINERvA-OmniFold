# Reverse outline of the methods paper: before (origin/main afb7e1fa) and after (register round r15)

**Method:** `register-method/HANDOFF.md` §3, step 3. Each paragraph is reduced to one sentence. The writer then wrote
from this outline under the register study's rules R1–R10 (`register-prd-study/REPORT.md` §4) and the KEEP list
(§5). Paragraph ids `¶n` count body paragraphs in reading order; floats are listed where they sit. Sentence-level
detail is in `ledger.md`, and the paragraph-by-paragraph edits are in `changes.md`.

## Before (afb7e1fa), one sentence per paragraph

<!-- absence-ok: this record quotes or paraphrases the paper's own absence statements (each carries its Search line in paper_body.tex or prints at afb7e1fa); it is not a new claim that a result does not exist -->
| ¶ | section | main idea |
|---|---|---|
| abs | abstract | 2D integral within about 1%; five-observable central values only; pseudo-experiments reveal bias, incomplete recovery and undercoverage; no reporting definition meets 10% under the envelope prescription; the hybrid-null tests all reject. A trailing sentence carried four caveats and the NuWro clause. |
| 1 | I | Binned unfolding scales badly with dimension; OmniFold is unbinned and has been used at H1, ATLAS and on simulated T2K. |
| 2 | I | We reproduce the published 2D MINERvA result, then add Eavail, q3 and W for 3D to 5D central values. |
| 3 | I | This is a case study; coverage and calibration differ; Secs. IV–VI validate, and Sec. VII applies calibrated tests. |
| T1 | I | Findings table with a "principal limitation" column. |
| 4 | I | Scope, written as five sentences of negatives: one implementation; central values without validated coverage; hybrid nulls; FWER under assumptions; no recoil band; not exclusions. |
| 5–10 | II | Data, signal and selection; observable definitions and the 135 MeV constant, with a materiality hedge; W redundancy; external predictions and the target difference; grids. Five note pointers. |
| 11–15 | III | OmniFold steps; background treatments; training; configurations; the closure and coverage definitions. |
| 16 | IV A | 2D comparison: ratio, bins within 10%, descriptive χ² with the pinv detail, shape difference "source not identified", learner dependence, post-selection "so a reproduction", and a cross-covariance aside. |
| 17–20 | IV B | Four blocks and the block-sum assumptions; run-period inconsistency, "size not validated"; statistical block, replica-mean offset, "not tested", and the history of two earlier bands; a status paragraph of disclaimers and omissions. |
| 21–22 | V A | Normalizations and closures; purity bias "in simulation" with its omission; the 2D purity-vs-refined closure. |
| 23 | V B | Generator-sized change partly recovered; "not included in the quoted uncertainties"; regularization bias; joint-test-estimator shapes, "(… which omits the regularization bias)". |
| 24–25 | V C | Coverage test and outcome; diagnosis, "inferred … rather than measured directly", "source … not established", "therefore no validated frequentist coverage". |
| 26–27 | V D | 5D covariance fails its criteria; seed dependence, "one seed pair … not measured … either direction … unmeasured"; rounding instability. |
| 28–29 | V E | "Under the specified envelope prescription" first, then the definition; envelope size; the route to inference. |
| T3 | V E | Binned-unfolding comparison table. |
| 30–32 | VI | Common thread; the D-ID claim addition; the checks to carry over, "to the extent that …". |
| 33 | VII | Why unfold before testing. |
| 34–36 | VII A | Descriptive comparisons; shares; the map, "no closure test with a mismodelled detector response … does not locate an interaction mechanism". |
| 37–39 | VII B | Hybrid null; calibration generative model; statistics. |
| 40–42 | VII C | p values and shifted nulls; Holm, A1, A2; design disclosures and the lost pseudo-experiments. Three note pointers. |
| 43–50 | VII D | Conditions (i)–(vi); (i) "not shown … carry over only if"; (ii) "either direction … not measured … conditional"; a closing "calibration validity" paragraph of four disclaimers. |
| 51–52 | VII E | Results, the CH replays, the κ scan, the null locations; the contribution, matched projections, power. Five note pointers. |
| 53–54 | VIII | Conclusions re-listing the 2D, 5D and interval limitations; "provided the calibration is exact"; the physical-interpretation requirements. |

**What the outline shows:**
- the same limitation in three places (Table I, the result sentence, the conclusions);
- a scope paragraph of negatives whose content is repeated sentence by sentence;
- three history or disclaimer paragraphs: the earlier bands, the 2D status paragraph and the calibration-validity
  paragraph;
- 40 note pointers, mostly mid-sentence parentheticals.

## After (r15), one sentence per paragraph

<!-- absence-ok: this record quotes or paraphrases the paper's own absence statements (each carries its Search line in paper_body.tex or prints at afb7e1fa); it is not a new claim that a result does not exist -->
| ¶ | section | main idea |
|---|---|---|
| abs | abstract | Same findings, with no trailing caveat sentence. The envelope dependence is carried by the sentence order. Kept: hybrid nulls and "no evidence of". The NuWro clause has left (DECISION-20261023 item 3a). |
| 1–3 | I | Unchanged in substance. Table I is listed with its configuration and test. The secondary application is stated without a calibration clause, because the scope states it. |
| T1 | I | Findings table without the limitation column. Single-column; it points to Sec. VIII A. |
| 4 | I | Scope, stated once and positively, with a naming convention ("Throughout, a three- to five-observable result is a central value …"). It keeps the negatives that carry meaning (not a validated measurement; not exclusions). It points to Sec. VIII A. |
| 5–10 | II | The 135 MeV effect is given as its bound only. Pointers: one per paragraph, at the end. |
| 11–15 | III | Unchanged, except one pointer. |
| 16 | IV A | Descriptive χ² in one sentence. The post-selection fact stays at the choice. Its consequence and the unidentified source of the shape difference move to Sec. VIII A. |
| 17–19 | IV B | Blocks, with one plain omission sentence (E5) and one pointer clause; the run-period inconsistency as a finding; the statistical block; the earlier band's failed test. The post hoc rescoring stays, because a build gate binds its values (REPORT §6). |
| 20–22 | V A–B | Closures; the purity bias with its own omission sentence (E6); generator-sized changes, with the omission moved to Sec. VIII A. Figures cited in the sentence, not in parentheses. |
| 23–24 | V C | The test and its outcome (R4). The diagnosis names its method in the sentence. The source statement is in Sec. VI only. |
| 25–26 | V D | "For one pair of seed settings … beyond the 5% limit; we therefore quote no …" (E7). Rounding. |
| 27–28 | V E | The envelope is defined first, then the result (R9, E8). |
| 29–31 | VI | Common thread, with the "source not established" statement once. D-ID: the out-of-scope sentence is kept, because its record requires it. The checks. |
| 32–35 | VII, VII A | The map paragraph ends on its positive statement. The detector-mismatch closure moves to Sec. VIII A, the interaction-mechanism denial to the note. |
| 36–41 | VII B–C | Unchanged, except pointers (two in VII C). |
| 42–48 | VII D | (i) measurement and assumption; (ii) the omission, the post hoc projection result and the sensitivity study. The consequences move to Sec. VIII A. The calibration-validity paragraph is gone; its content is in Sec. VIII A or the note. |
| 49–50 | VII E | Results and the CH replays (DECISION-20261020 content kept). One pointer clause per paragraph. |
| 51 | VIII | The results are Table I's. Sec. VI relates three of them. The calibrated tests control the FWER "provided the calibration is exact" (E10). |
| 52 | VIII A | **Limitations**, numbered, each once: (1) 2D covariance not independently validated; (2) post-selected 2D learner, so a reproduction, and the unidentified source of the shape difference; (3) regularization bias in no quoted uncertainty; (4) one seed pair, unmeasured spread and fixed-seed bands; (5) no detector-mismatch closure for the map; (6) carry-over of the rejections only under the sub-grid bound; (7) the missing response band and its unmeasured effect; (8) A1 and the untested calibration fidelity. |
