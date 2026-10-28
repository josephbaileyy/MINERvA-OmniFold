# Independent review: move of the non-final configurations from the paper to the note

**Operands.**
- BEFORE: `scratchpad/5d/paper_body.pre-move.tex`. It is byte-identical to `HEAD:docs/analysis-note/paper_body.tex` (HEAD `1f7f93da`; checked with `cmp`).
- AFTER: the working-tree `docs/analysis-note/paper_body.tex` in `wt-con`. This is the only modified file (`git status`: ` M docs/analysis-note/paper_body.tex`). The diff is 35 insertions and 48 deletions.
- Inventory: a sentence-level `difflib` diff of the comment-stripped text, 28 hunks (`scratchpad/5d/rv/sdiff.txt`). I built it myself and used no author ledger.
- Note: the `.tex` sources (records, history and provenance excluded) and the built `main_note.pdf` (10:39). Every fact matched to the note was confirmed by `grep -F` on the PDF text (`scratchpad/5d/rv/note_flat.txt`).
- Macros resolved from `values.tex`:
  - `\chiPaperExact` 3.66, `\chiPaperExactSeeded` 3.57, `\chiPaperPurity` 2.65, `\chiPaper` 2.27;
  - `\zprojCells` 42, `\sprojBound` 5, `\sprojMeasured` 6.145, `\pinnedBandsSqrtTr` 26.0;
  - `\figTwoHiHiLo/Hi` 12/30, `\figTwoLowWLo/Hi` 23/31, `\genRatioTotLo/Hi` 1.07/1.39.
- Build state: `main_paper.pdf`/`.aux` date from 10:39 and `paper_body.tex` from 11:04, so **AFTER has not been built**. Paper labels were therefore checked against the sources: every `\ref` in AFTER and `main_paper.tex` has a `\label`, and no label was removed. Every `N-` and `\nsec`/`\napp` target exists in `main_note.aux`.

## BLOCKING findings

1. **AFTER l.159: the pointer target does not contain what the sentence says.** The sentence reads "Normalization and closure checks of a purity-subtracted variant in three to five observables are described in \nsec{sec:closure-map}". Sec. 5.1 (`sec_validation.tex:50-105`) is the closure table and holds no normalization check.
   - The 4D/5D marginal-normalization result (approx. 1–2 %) left the paper in this move. In the note it prints only in `sec_summary.tex:19`, `sec_execsummary.tex:40` and the note abstract.
   - Its body homes are `sec_eavailw.tex:18` (5D→4D, 0.11 %) and `sec_3d.tex:183` (4D→3D, qualitative only).
   - The paper's only route to this fact therefore points to the wrong place.
   - Fix: "…are described in \nsec{sec:closure-map} (closures) and \nsec{sec:eavailw-axis} (normalization)", or point to \nsec{sec:summary}.
2. **AFTER l.462: orphaned citation.** The sentence reads "The three- and four-observable central values lack intervals of validated coverage (Sec.~\ref{sec:departure})".
   - In BEFORE the citation supported the clause that left ("…the uncertainties of the configuration-(a) five-observable central value omit its regularization bias").
   - Sec. departure says nothing about 3D/4D intervals. The statement is made in the Scope paragraph (l.46) and in Sec. central (l.323, "without uncertainties").
   - Fix: change the citation to "(Sec.~\ref{sec:central})", or drop it.
3. **Note-side, made false by the move: `sec_method.tex:93`.** The sentence reads "Six estimator configurations, labeled (a)–(f) **as in the article**". After the move the article labels no configuration.
   - Fix: delete "as in the article".
   - Two related note sentences are now inaccurate (MINOR, listed in Direction B): `sec_method.tex:116` ("Estimator configurations of the article") and `sec_5d.tex:17,20`. The latter, "Validation studies of the article", still lists "Three-, four-observable closure (a)", which has left the article.

**Counts.**
- Direction A: 64 facts; 62 OK, 2 DIFFERS, 0 MISSING. No fact left both documents.
- Direction B: 34 rows; 2 BLOCKING (B16, B31), 10 MINOR (B5, B8, B11, B12, B20, B22, B26, B32, B33, B34) and 22 OK.
- Note-side: 1 BLOCKING (N1) and 2 MINOR (N2, N3).
- Total BLOCKING: 3.

---

## Direction A — nothing lost

Note locations are `file:line` in `docs/analysis-note/`, and every quoted phrase was confirmed in the PDF text.

| # | Fact that left the paper or was reworded | BEFORE line | AFTER status | Note home: file:line and quote | Verdict |
|---|---|---|---|---|---|
| 1 | Table I "Conf." column; caption "Conf.: configuration (Table II)" | 25–40 | removed | `sec_method.tex:116-131` tab:estimators-matrix "Results" column; `sec_5d.tex:28-41` tab:validation-design-5d gives a letter for each study | OK |
| 2 | "4D and 5D (a) marginal normalizations agree at about 1–2 %" | 34, 170 | removed | `sec_summary.tex:19` "In configuration (a), the 4D and 5D unfolds pass marginal-normalization checks against the lower-dimensional results to ≈1–2 %"; `sec_execsummary.tex:40`; `sec_eavailw.tex:18` "integrating over W recovers the configuration-(a) 4D normalization to 0.11 %" | OK (but not at the target the paper now names: BLOCKING 1) |
| 3 | Table I: the 3D marginal is (e) and the 2D result is (f), a cross-estimator comparison | 34 | the table row lost the qualifier; the body (l.159) keeps "a comparison across the two estimators" | `sec_3d.tex:69` "This is a cross-configuration comparison: the 3D marginal is configuration (e), and the 2D result is configuration (f)" | OK |
| 4 | Table I row 4 configurations (c), (d) | 35 | "purity-based" in words | `sec_5d.tex:32` "Background closure (c), (d)" | OK |
| 5 | Table I "seed-dependent (a) covariance" | 38 | removed | `sec_5d.tex:306` "s_proj = 6.145 %, against the 5 % movement limit" | OK |
| 6 | Table I gives the configuration of each finding | 49 | "with its test" | as row 1 | OK |
| 7 | "All estimator configurations use five iterations" | 88 | "Both estimators" | `sec_method.tex:93` "All use five OmniFold iterations" | OK |
| 8 | (f) = learner and seed of (a), with negative weights and the refinement of (e) | 91 | in words (l.89) | `sec_method.tex:97` "(f), the nominal LightGBM configuration above with refined negative-weight subtraction and the refinement classifier of (e)" | OK |
| 9 | The (a) 5D central value and its covariance use purity subtraction, whose bias is in Sec. closure | 91 | removed | `sec_method.tex:101` "The five-dimensional central value … and its five-axis covariance use configuration (a): they were produced before the purity bias was found"; matrix row (a) "purity-based subtraction" | OK |
| 10 | The sixteen-cell result uses (e), with negative weights and higher-capacity refinement | 91 | in words (l.89) | `sec_method.tex:99` (e) "gives … the sixteen-cell five-dimensional result" | OK |
| 11 | "(c)–(e) are deterministic LightGBM (fixed seeds, reproducible training)" | 96 | only "the joint-test estimator is deterministic" | `sec_method.tex:93` "'deterministic' means fixed seeds and reproducible training"; matrix (c) "LightGBM, deterministic", (d), (e) "as (c)" | OK |
| 12 | "Results from different configurations are not combined" | 96 | narrowed to "the two estimators" | `sec_method.tex:93` "Results from different configurations are not combined." | OK |
| 13 | Table II rows (a)–(d) and their uses | 105–112 | removed | `sec_method.tex:120-128`: (a) "five-observable central value … three- and four-observable closures … two-observable purity-subtracted comparisons"; (b) "two-observable cross-check"; (c) "background bias; coverage test"; (d) "background bias; generator-sized E_avail change" | OK |
| 14 | "The distance depends on the estimator." | 134 | removed | `sec_results.tex:131` "With the purity-based subtraction, the choice of GBDT estimator spreads the distance over about one unit, a methodological band" | OK |
| 15 | Ten LightGBM seeds with purity subtraction: χ²/ndf 2.64–2.75 | 134 | removed | `sec_results.tex:131` "LightGBM with seeds 1--10 gives 2.64--2.75" | OK |
| 16 | Exact-split, unseeded: \chiPaperExact = 3.66 | 134 | removed | `sec_method.tex:71` "It gives χ²/ndf=\chiPaperExact (unseeded, reproducible)"; `sec_results.tex:131` | OK |
| 17 | Exact-split, one fixed-seed run: \chiPaperExactSeeded = 3.57 | 134 | removed | `sec_method.tex:71` "one reseeded run (random_state 1/2/3) … gives χ²/ndf=\chiPaperExactSeeded" | OK |
| 18 | At seed 42, refined subtraction lowers LightGBM from \chiPaperPurity 2.65 to \chiPaper 2.27 | 134 | removed | `sec_results.tex:131` "the refined negative-weight subtraction of the quoted result lowers the LightGBM distance from \chiPaperPurity to \chiPaper" | OK |
| 19 | "This learner was chosen after both comparisons were known." | 134 | reworded (l.123): "after comparisons with other training seeds, with purity-based subtraction and with an exact-split learner were known" | `sec_method.tex:71` "LightGBM was chosen for the central value after both comparisons with the publication were known" | DIFFERS: AFTER names three comparisons, among them one "with purity-based subtraction", that the note does not list (see B11) |
| 20 | Central value and exact-split differ in learner and background treatment | 134 | kept as "The exact-split learner, with purity-based subtraction, differs…" | `sec_method.tex:71` "the quoted central value, which also differs from it in background treatment" | OK |
| 21 | Exact-split vs central: median 1.03 %, maximum 17.6 % | 134 | kept | `sec_method.tex:71` "by a per-bin median of 1.03 % (maximum 17.6 %)" | OK |
| 22 | "Both estimators are described in \nsec{method-config}" | 134 | "These comparisons are described in \nsec{method-config}" | `sec_method.tex:71` (seed-1, seeds 1–10, exact-split and the χ² values, with a link to results-tension for the ten-seed χ² band) | OK |
| 23 | "Each higher-dimensional result is checked against the lower-dimensional result it extends." | 170 | removed; the removal is more accurate, since only the 3D (e) marginal is compared | `sec_summary.tex:19` (each check named) | OK |
| 24 | For (e), only the 3D marginal compared: 0.141 %, across configurations | 170 | kept (l.159) | `sec_3d.tex:69` "agrees with the 2D result's to 0.141 %" | OK |
| 25 | 3D (a) E_avail bump: residual 0.10 of the injected change | 170 | removed | `sec_3d.tex:88` "1.84 % vs 18.1 % injected (ratio 0.102)"; `sec_validation.tex` closure-map row "configuration (a)" | OK |
| 26 | 4D (a) q3 bump: within 1.1 % | 170 | removed | `sec_validation.tex:93` "Marginal q_3 ratios within 1.1 %" (row "configuration (a)") | OK |
| 27 | "These closure tests reweight the simulated signal only." | 170 | removed | `sec_5d.tex:30-31` "Three-, four-observable closure (a)", Backgrounds: "none" | OK |
| 28 | Purity (c) bias up to 4 % at high W | 174 | kept in words | `sec_5d.tex:51` "return the highest-W column … 3.5–4.1 % low" | OK |
| 29 | "…about one standard deviation of the covariance of Sec. cov5d in one (E_avail,W) cell" | 174 | removed | `sec_5d.tex:51` "Relative to these cells' total uncertainty in the configuration-(a) covariance, the bias is 0.36–1.07 standard deviations" | OK |
| 30 | "This bias is not included in the uncertainties quoted for the configuration-(a) central value." | 174 | removed | `sec_5d.tex:51` "It comes from the purity-based subtraction …, enters no quoted covariance" | OK |
| 31 | (d) reduces the bias to <0.3 % (≤0.4 % elsewhere; up to 1 % in joint cells) | 174 | kept in words (l.163) | `sec_5d.tex:51` "brings the highest-W column to 0.11–0.24 % … Some joint cells remain up to 1.0 % high" | OK |
| 32 | "configuration (f)" for the 2D result | 177 | "the refined estimator" | `app_negweight.tex:116` sec:negweight-footing | OK |
| 33 | GiBUU-to-GENIE deformation unfolded with (d): several %, up to 74 % | 185 | kept in words | `sec_5d.tex:61` "up to 74 % in the highest-W column"; `sec_5d.tex:34` "Generator-sized change (d)" | OK |
| 34 | 30 iterations −26 %; a larger classifier improves the reco fit only | 185 | kept, with the new "in noise-free studies of that variant" | `sec_5d.tex:77` "Thirty iterations reduce the E_avail residual by 26 % … A larger classifier improves the reco-level fit without improving the E_avail truth residual" (the note does not name the variant; the source does, see B19) | OK |
| 35 | "This total uncertainty is that of the covariance of Sec. cov5d." | 185 | "…of an earlier purity-subtracted five-observable central value (\nsec{eavailw-adopted})" | `sec_5d.tex:95` "within the configuration-(a) total uncertainty in 20 of the 42 (E_avail,W) cells" | OK |
| 36 | "The uncertainties of the configuration-(a) central value omit the regularization bias." | 185 | removed | `sec_5d.tex:77` "a regularization (unfolding-model) bias of the estimator, enter no uncertainty quoted for the configuration-(a) central value"; `sec_summary.tex:46` | OK |
| 37 | Coverage test uses (c) | 191 | in words | matrix (c) "coverage test"; `sec_5d.tex:38` "Coverage (c)" | OK |
| 38 | Fig. bkg-residual: (c) with 9 PE, (d) with 60 PE | 199 | in words | `sec_method.tex:122-125` | OK |
| 39 | Fig. deformation (a) (d), (b) (e); band from the Sec. cov5d covariance | 208 | in words | `sec_5d.tex:34-37` | OK |
| 40 | Fig. coverage: configuration (c) | 227 | in words | `sec_5d.tex:38` | OK |
| 41 | The (a) covariance (42-cell projection) does not meet its specification's validation criteria | 238 | removed | `sec_5d.tex:250` "its (E_avail,W) projection has \zprojCells cells … does not meet the acceptance criteria of its specification" | OK |
| 42 | "The comparisons of Sec. departure use this covariance and no other five-observable covariance." | 238 | removed | `sec_5d.tex:37` "compared with the configuration-(a) total σ"; `sec_5d.tex:250` "the use covers only them, not any other covariance built to the same specification" | OK |
| 43 | "The calibration of the joint tests does not use it." | 238 | removed | `sec_joint.tex:5` "They do not use, and do not validate, the five-axis covariance of the configuration-(a) central value" | OK |
| 44 | One seed pair moves two further covariances by about 6.1 %, beyond \sprojBound = 5 %; diagonal measures stay within it | 238 | removed | `sec_5d.tex:306` "Companion covariances at seed offsets {0,1200} give … s_proj = 6.145 %, against the 5 % movement limit … The diagonal-only measures pass" | OK |
| 45 | "We therefore quote no generator significance based on this covariance; the sixteen-cell comparison is in Sec. gen16" | 238 | removed | `sec_summary.tex:46` "so no significance based on the configuration-(a) covariance is quoted (…; the comparison on the sixteen cells: §fived16-gen)"; `sec_eavailw.tex:129` | OK |
| 46 | Seed dependence studied with only one seed pair | 238 | removed | `sec_5d.tex:309` "subset scatter at a single seed pair (offsets {0,1200}); the width of the distribution over seed pairs is unmeasured" | OK |
| 47 | Five fixed-seed bands carry \pinnedBandsSqrtTr = 26.0 % of √Tr C; their seed sensitivity is unmeasured | 238 | removed | `sec_5d.tex:311` "They carry 26.0 % of √Tr C and move by exactly zero; their seed sensitivity is unmeasured" | OK |
| 48 | "The estimators are also unstable at the level of rounding" (a property of the family) | 242 | narrowed to the joint-test estimator | `sec_5d.tex:90` "place this instability in the estimator family" | OK (paper narrowed; see B26) |
| 49 | Baseline estimator: up to 2.5 σ_stat | 242 | removed | `sec_5d.tex:90` "The baseline estimator's shifts, a median of 0.8 and at most 2.5" | OK |
| 50 | The higher-capacity refinement moves results by up to 2.6 and fails the stability requirement | 242 | "its results … so it fails" (the joint-test estimator) | `sec_5d.tex:90` "The candidate fails the data-stability test … at most 2.6"; `sec_5d.tex:95` "This candidate is configuration (e)" | OK |
| 51 | "configuration (e)'s data result on 16 cells"; "uncertainties of configuration (e)" | 274 | "the joint-test estimator" | matrix row (e) | OK |
| 52 | Descriptive comparisons use the (a) central value in five observables | 334 | 5D dropped; 3D/4D (e) kept | `sec_3d.tex:10`; `sec_eavailw.tex:100-134` | OK |
| 53 | Two thirds of the positive difference at E_avail ≥ 0.8 GeV, most of it at W ≥ 1.8 GeV | 337 | removed (pointer at l.327) | `sec_eavailw.tex:100` "the region E_avail ≥ 0.8 GeV carries 67 %, with 83 % of that at W ≥ 1.8 GeV" | OK |
| 54 | A fifth in the single widest overflow cell | 337 | removed | `sec_eavailw.tex:100` "The largest cell, the corner E_avail>3 GeV, W>3 GeV, holds 22 %" | OK |
| 55 | Data exceed Tune v1 by 12–30 % in those cells and by 23–31 % at W<1.1 GeV for every E_avail; the excess extends to low W | 337 | removed | The ranges appear only as **figure cell labels** in Fig. eavailWexcess (PDF p. 54: corner cells 1.12–1.30; W<1.1 column 1.23–1.31). The text `sec_eavailw.tex:100` has "A secondary excess lies at W<1.1 GeV". The `\figTwo*` macros are used only in `primer_body.tex`. | DIFFERS (figure only; no stated range) |
| 56 | Data above all four predictions overall (1.07–1.39) and at high W | 340 | removed | `sec_eavailw.tex:120` "integrated ratios 1.11, 1.07 and 1.15 … GiBUU (integrated 1.39)"; `:129` "At W∈[2.2,3.0) GeV, data/generator = 1.12, 1.11, 1.13 and 1.34"; `:134` | OK |
| 57 | GiBUU, the most deficient, stops at E_ν ≈ 20 GeV | 340 | removed | `sec_eavailw.tex:120` "it was generated only up to E_ν≈20 GeV … GiBUU is lower than the others everywhere" | OK |
| 58 | The NuWro and GiBUU ratios contain the target difference | 340 | removed | `sec_eavailw.tex:95` "The NuWro and GiBUU comparisons contain a target difference of this kind" | OK |
| 59 | The high-E_avail, high-W region is where the regularization bias is largest | 340 | removed | `sec_eavailw.tex:105` "the regularization bias of Sec. 9 is largest at high E_avail and high W" | OK |
| 60 | The map describes where the central value differs from Tune v1 | 340 | removed | `sec_eavailw.tex:134` "The localization in §map is relative to MINERvA Tune v1" | OK |
| 61 | No closure test with a mismodelled detector response has been run for the map | 340 | removed | `sec_eavailw.tex:105` "These statements hold under the nominal detector response … [the response-mismatch closure] has not yet produced a result" | OK |
| 62 | Limitations: "the higher-dimensional central values" (including 5D (a)) lack validated-coverage intervals | 475 | narrowed to 3D/4D | `sec_summary.tex:46` "Above two dimensions the results are central values without intervals of validated coverage" | OK |
| 63 | Limitations: the uncertainties of the (a) 5D central value omit its regularization bias | 475 | removed | `sec_summary.tex:46` "No uncertainty quoted for the configuration-(a) central value includes this residual bias" | OK |
| 64 | Sec. cov5d subsection title "Covariance and estimator stability" | 234 | "Estimator stability" | `sec_5d.tex:244` subsection title | OK |
<!-- absence-ok: quotes the paper's removed sentences and their note homes as this review's inventory; not a new absence claim -->

**Cross-references new in AFTER:**
- \nsec{sec:method-config} (l.89, 94, 123) → 3.2. It holds the (c)/(d) uses, the full matrix and the 2D comparisons. OK.
- \nsec{sec:closure-map} (l.159) → 5.1. It holds no normalization checks: BLOCKING 1.
- \nsec{sec:eavailw-adopted} (l.174, 197) → 9.6 (the label sits on an unnumbered "Status" paragraph inside subsection 9.6). It holds the status of the (a) covariance. OK.
- \nsec{sec:eavailw-construction} (l.231) → 9.6. It holds the status and the seed studies, items 1–3. OK.

---

## Direction B — nothing strengthened or made false

| # | AFTER sentence (line) | Issue | Severity | Shortest true fix |
|---|---|---|---|---|
| B1 | "Table I lists each with its test" (47) | none | OK | — |
| B2 | "Both estimators use five OmniFold iterations…" (86) | true: (e) and (f) both use 5 iterations | OK | — |
| B3 | "The two-observable central value uses LightGBM at seed 42 with negative-weight … 400 trees and 31 leaves" (89) | matches matrix (f) | OK | — |
| B4 | "…joint-test estimator, a deterministic LightGBM with the same background treatment and refinement capacity, which removes most of the bias…" (89) | matches matrix (e): "as (c)" plus negative weights at 400/31. The nominal residual is 0.09 % (l.197). | OK | — |
| B5 | "The variants used in development, and the results that rest on them, are described in \nsec{method-config}" (89) | (a) was a production central value and (b) a cross-check; neither is a "development variant". The sentence under-describes what moved. | MINOR | "The other configurations, and the results that rest on them, …" |
| B6 | "The joint-test estimator keeps five iterations…" (92) | unchanged in substance | OK | — |
| B7 | Table II caption: "Both use … refined negative-weight background subtraction" (94) | true: note matrix (e) and (f) both "negative weights; refinement classifier 400 trees, 31 leaves"; `sec_3d.tex:69` "Both use refined negative-weight subtraction with a 400-tree, 31-leaf refinement" | OK | — |
| B8 | Caption: "the joint-test estimator is deterministic LightGBM (fixed seeds, reproducible training)" (94) | True of (e). But the gloss "fixed seeds, reproducible training" also describes the two-observable estimator (seed 42, "This reproducible central value", l.89; it repeats to 9×10⁻¹², `sec_method.tex:71`), so the contrast misleads. Already present in BEFORE ("(c)–(e) are deterministic"). | MINOR | Drop the parenthesis, or name the LightGBM deterministic mode |
| B9 | Caption: "Results from the two estimators are not combined." (94) | true: l.159 is a comparison, not a combination | OK | — |
| B10 | Table II rows (103–105) | match the matrix | OK | — |
| B11 | "The learner was chosen after comparisons with other training seeds, with purity-based subtraction and with an exact-split learner were known" (123) | LightGBM was chosen on 2026-10-11 (DECISION-20261011), when every LightGBM unfold was purity-subtracted. The refined/purity comparison (2.65→2.27) came later, from the 10-23/24 rebuild. Read as "the comparison with purity-based subtraction", the clause is false in time; read as "comparisons made with purity-based subtraction", it is true. The note says "after both comparisons with the publication were known". | MINOR | "LightGBM, then with purity-based subtraction, was chosen after its comparisons with the publication at ten training seeds and that of an exact-split learner were known, so…" |
| B12 | 2D χ² paragraph (122) | Lost disclosure: the paper no longer says that the distance depends on the estimator (2.27–3.66), or that the post-hoc choice lowered it. No printed sentence becomes false, so this is not BLOCKING under the rule. It is the most consequential qualifier removed. | MINOR | Restore one clause: "The distance depends on the estimator, from \chiPaper to \chiPaperExact over the variants tested (\nsec{sec:results-tension})." |
| B13 | "The exact-split learner, with purity-based subtraction, differs … 1.03 % (17.6 %)" (123) | matches `sec_method.tex:71` | OK | — |
| B14 | "These comparisons are described in \nsec{sec:method-config}" (123) | Target holds them; the ten-seed χ² band is one hop further, at results-tension | OK | — |
| B15 | "Of the joint-test estimator's results, only the three-observable marginal has been compared … 0.141 %, a comparison across the two estimators" (159) | true (`sec_3d.tex:69`; `sec_3d.tex:183`: the 4D→3D check is (a) only) | OK | — |
| B16 | "Normalization and closure checks of a purity-subtracted variant in three to five observables are described in \nsec{sec:closure-map}" (159) | The target holds closures only, with no normalization check (BLOCKING 1). Also, "a purity-subtracted variant" here means (a), while Table I (l.35) and the abstract use the same phrase for (c). | **BLOCKING** | Add \nsec{sec:eavailw-axis} for normalization; optionally "the earlier purity-subtracted estimator" |
| B17 | "with purity-based background subtraction in a deterministic LightGBM estimator … In the same estimator, unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves…" (163) | (c) and (d) described correctly | OK | — |
| B18 | "The two-dimensional result therefore uses the refined estimator" (166) | OK | OK | — |
| B19 | "unfolded with a development variant of the joint-test estimator, whose refinement has 100 trees and 8 leaves" and "in noise-free studies of that variant, thirty iterations reduce … by 26 %, and a larger classifier improves the reconstruction-level fit without reducing it" (174) | **Checked against DIAGNOSIS-20260926 and true.** D4 is "Noise-free (D4, asimov_same, B0, K = 30)", where "The E_avail median falls 26 %". D5 is the noise-free one-factor probes: "Capacity (400 trees, 31 leaves …) improves the reco fit (E_avail fold χ² 103 against 144 at k = 5) without improving the E_avail truth residual (10.7 % against 10.9 %)". B0 is "s5n family N", which the note matrix sources as (d) (refinement with the F2 parameters, 100/8). Calling (d) a "development variant of the joint-test estimator" is fair, since it differs from (e) only in refinement capacity. | OK | — |
| B20 | "…and, in about half of those cells, within the total uncertainty of the covariance of an earlier purity-subtracted five-observable central value (\nsec{eavailw-adopted})" (174) | True (20 of 42, `sec_5d.tex:95`). The yardstick fails its acceptance criteria, which now shows only behind the pointer; the paper calls it neither unvalidated nor seed-sensitive. "those cells" has no plural antecedent; it means the 42 (E_avail,W) cells, not "the most affected cell" (inherited from BEFORE). | MINOR | "…within the total uncertainty of the unvalidated covariance of an earlier … central value in 20 of the 42 (E_avail,W) cells" |
| B21 | "Statistical intervals from a deterministic LightGBM estimator with purity-based subtraction…" (180) | (c), correct | OK | — |
| B22 | Fig. bkg-residual caption "Both from a deterministic LightGBM estimator." (188) | a fragment; content true | MINOR | "Both are from a deterministic LightGBM estimator." |
| B23 | Fig. deformation caption (197): "(a) A development variant … 100 trees and 8 leaves … this variant's largest residual is 0.39 % (the squares of Fig. bkg-residual a)"; "(b) The joint-test estimator…; the grey band … covariance of an earlier purity-subtracted …" | consistent: the squares are (d) | OK (the band qualifier is as in B20) | — |
| B24 | Fig. coverage caption (216) | (c), correct | OK | — |
| B25 | Subsection title "Estimator stability" (223) | OK | OK | — |
| B26 | "The joint-test estimator is unstable at the level of rounding: … up to 2.6 … so it fails…" (231) | True ((e) is "the candidate", `sec_5d.tex:90,95`). The dropped baseline (2.5) "place[s] this instability in the estimator family", so the instability now reads as caused by the joint-test estimator's refinement. | MINOR | Add "as does the estimator without the higher-capacity refinement (2.5; \nsec{sec:val-departure})" |
| B27 | "The covariance of the earlier purity-subtracted five-observable central value, its status and its seed studies are given in \nsec{eavailw-construction}" (231) | target matches | OK | — |
| B28 | "the joint-test estimator's data result on 16 cells" / "uncertainties of the joint-test estimator" (263) | label swap only | OK | — |
| B29 | "These comparisons use the three- and four-observable central values of the joint-test estimator, without uncertainties." (323) | true: `sec_3d.tex:10`, and the 3D model figure `sec_3d.tex:129` is (e) by default (`sec_3d.tex:51`) | OK | — |
| B30 | "The five-observable (E_avail,W) map of the earlier purity-subtracted central value … are given in Ref., Secs. eavailw-map and eavailw-band" (327) | target matches | OK | — |
| B31 | "The three- and four-observable central values lack intervals of validated coverage (Sec.~\ref{sec:departure})." (462) | Orphaned citation (BLOCKING 2): it supported the clause that left; Sec. departure does not state this. | **BLOCKING** | "(Sec.~\ref{sec:central})" |
| B32 | Unchanged: "Agreement in the marginal normalizations thus coexists with substantial residual bias under the tested deformations." (184) | The plural is now orphaned: the paper prints a single normalization comparison, (e) 3D against (f) 2D, while the miscoverage is of the (c) variant. | MINOR | "Agreement in the marginal normalization of Sec.~\ref{sec:closure} thus coexists…" |
| B33 | Unchanged Scope: "for the observables, configurations, and deformations tested" (46) | "configurations" is no longer a defined term in the paper | MINOR | "estimators" |
| B34 | Table I row "3D marginal normalization agrees with the 2D result to 0.141 %" (32) | The cross-estimator qualifier is in the body only. The table's caption sends the reader to the section, so the row is not false. | MINOR | append "(across estimators)" |

**Note-side consequences of the move** (the note was not edited):

| # | Note sentence | Issue | Severity | Fix |
|---|---|---|---|---|
| N1 | `sec_method.tex:93` "Six estimator configurations, labeled (a)–(f) as in the article" | false after the move (BLOCKING 3) | **BLOCKING** | delete "as in the article" |
| N2 | `sec_method.tex:116` caption "Estimator configurations of the article." | the article now shows two estimators | MINOR | "Estimator configurations." |
| N3 | `sec_5d.tex:17,20` "validation studies of the article"; table row "Three-, four-observable closure (a)" | the 3D/4D closures have left the article | MINOR | "Validation studies of the article and of this note", or drop that row's claim |

**Specific checks requested.**
1. **"noise-free studies of that variant".** True. D4 and D5 were both run on B0 = s5n family N = configuration (d), noise-free (B19).
2. **The Table II caption.**
   - "refined negative-weight background subtraction" for both is true: the note matrix gives (e) and (f) the same treatment, and `sec_3d.tex:69` states it.
   - "the joint-test estimator is deterministic" is true.
   - The "(fixed seeds, reproducible training)" gloss wrongly implies that the two-observable estimator lacks those properties (B8, MINOR, inherited from BEFORE).

**Not verified.** The paper was not rebuilt (its PDF predates AFTER), so the Table I column widths (0.62/0.22/0.07) and the compile were not checked.
