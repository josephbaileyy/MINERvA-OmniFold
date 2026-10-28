# Estimator-configuration inventory of the methods paper

Question (Joseph): does configuration (a), and do the other non-final configurations, need to be in the paper at all, rather than only in the companion note? This is an inventory only. It makes no recommendation.

## Source and method

- **Text cited.** The worktree `wt-con` at commit `69491c33`. `docs/analysis-note/paper_body.tex` was read once, with sha1 `2762b3e7…`. That is the HEAD blob: the version I read has HEAD's wording on lines 346 and 475, and `git show HEAD:` hashes to the same sha1. `main_paper.tex` was read for the abstract (line 45) and the Data availability section (line 94).
- **Later edits.** While I worked, a concurrent edit changed lines 185, 238, 274, 277, 305, 346 and 475 in the working tree. I checked the word diff. No configuration label changed, and the sentences counted as removable below did not change. One change on line 185 sentence 7, and the same one on line 475 sentence 4 ("No uncertainty quoted for…includes" became "The uncertainties of…omit"), alters final-configuration sentences that are not counted. All line numbers are the same in both versions.
- **Section, figure and table numbers.** These come from `main_paper.aux`:
  - Table I is `tab:findings`.
  - Table II is `tab:estimators`.
  - Table III is `tab:binned`.
  - Figs. 1–5 are `validation`, `bkg-residual`, `deformation`, `coverage` and `ratio16`.
  - Sec. IV A is `repro2d-pub`, IV B is `uq2d`, V A is `closure`, V B is `departure`, V C is `coverage`, V D is `cov5d`, V E is `uncertainty-status`, V F is `result16`, VI is `limits`, VII A is `central` and VII B is `gen16`.
- **How configurations were matched.** I matched explicit letters, and I matched descriptions using the aliases in `docs/orchestration/registry/ALIASES.tsv` and `ESTIMATORS.tsv`. I also searched for: configuration, Conf, seed 42, LightGBM, exact, deterministic, refine, purity, negative, joint-test estimator, baseline, higher-capacity, learner and scikit.
- **Keyword hits that are not configurations.**
  - "refine/refinement" at :46, :248, :379, :392 and :408 means grid refinement or prior reweighting, not the Stay-Positive refinement.
  - "exact" at :69, :72, :254–:317 and :379 means an exact relation or exact binned IBU, not the exact-split learner.
  - "negative" at :54 is the MINOS charge, and at :418 it is clipped interaction bands.
- **Word counts.** I counted whitespace tokens of the LaTeX source, after deleting `\cite{}`/`\label{}`, mapping `~` to a space and stripping the `\pcell` wrappers in table cells. Comment lines are excluded.
  - The source has 9,505 tokens of non-comment body text.
  - I calibrated against `pdftotext main_paper.pdf` on three paragraphs (:134, :191, :193). The PDF word count is 2–4% higher (115→120, 106→108, 86→89).
- **Roles used below.**
  - **FINAL**: the configuration of a result the paper reports.
  - **SUPERSEDED**: the configuration was once used for a reported result and has since been replaced.
  - **COMPARISON**: used only as the other arm of a comparison.
  - **DIAGNOSTIC**: a validation study on a configuration that is not the one behind the reported result.
  - **DEFINITIONAL**: needed to define another configuration.
- **Word-count codes.** **E** marks words that exist only to describe a non-final configuration; I count them as removable. **P** marks a sentence that is only partly removable, and gives the removable words.

### The main correction to the question's premise

The paper's own text makes **(a) a final configuration**, for the five-observable fine-grid central value and its covariance:

- :91 sentence 4: "The configuration-(a) five-observable central value and its covariance use the purity-based subtraction."
- The Table II row at :105–106: "5D central value and covariance of Sec. V D."
- :334 sentence 1: "configuration (a) in five."

(e) is final for the sixteen-cell five-observable result, and (a) is final for the fine-grid five-observable central value. In the paper, (a) is non-final only in its 2D, 3D and 4D roles:

- the 2D learner and seed comparisons (Sec. IV A);
- the 2D purity-vs-refined closure (Sec. V A);
- the 3D and 4D injected-bump closures, and the 4D marginal normalization (Sec. V A).

(a) is also the parent definition of (f). The fully non-final configurations are (b), (c) and (d).

---

## 1–2. Inventory per configuration

### Configuration (a): LightGBM, seed 42 in 2D, purity-based subtraction

| # | Location | Quote (≤15 words) | Role | Basis (paper text) | Words |
|---|---|---|---|---|---|
| a1 | main_paper.tex:45 (abstract) | "it yields central values only, whose normalizations agree with lower-dimensional results" | FINAL (5D central value); the normalization check is partly DIAGNOSTIC (4D (a), see a12) | No letter given; "five simultaneous observables" matches :91 s4, :105–106 and :334 s1 | keep |
| a2 | main_paper.tex:94 (Data availability) | "the numbers quoted in Sec.~\ref{sec:central}" … "the $(\Eavail,W)$ map" | FINAL (5D descriptive comparison) | The $(E_{avail},W)$ projection exists only in the five-observable result, which :334 s1 assigns to (a). Sec. VII A also covers 3D and 4D (e) | keep |
| a3 | :17 s2 | "obtain simultaneous three-, four-, and five-observable central values" | FINAL (the five-observable part is (a)) | :334 s1 | keep |
| a4 | :34 (Table I) | "4D and 5D (a) marginal normalizations agree at about 1--2\%" | 5D: FINAL check; 4D: DIAGNOSTIC (the 4D central value is (e), :113–114) | Conf. column "(a), (e), (f)" | P: about 2 ("4D and") |
| a5 | :38 (Table I) | "seed-dependent (a) covariance; rounding-level instability" | FINAL ((a)'s 5D covariance) | Sec. V D | keep |
| a6 | :91 s2 | "the learner and seed of configuration~(a) with negative-weight background subtraction" | DEFINITIONAL (defines (f)) | — | keep |
| a7 | :91 s4 | "The configuration-(a) five-observable central value and its covariance use the purity-based subtraction" | FINAL | — | keep |
| a8 | :96 (Table II caption) | "(f) is (a) with the refinement of (e)" | DEFINITIONAL | — | keep |
| a9 | :105–106 (Table II row) | "(a) central value: LightGBM, seed 42 in 2D" / "3D and 4D closures; 2D learner comparisons" | "5D central value and covariance": FINAL. "3D and 4D closures; 2D learner comparisons": DIAGNOSTIC/COMPARISON | — | E: 9 (the second clause) |
| a10 | :115 (Table II row f) | "(f) as (a), refined" | DEFINITIONAL | — | keep |
| a11 | :134 s1–s3 | "With the purity-based subtraction, ten LightGBM training seeds give 2.64--2.75" ; "lowers the LightGBM distance from $\chiPaperPurity$ to $\chiPaper$" | SUPERSEDED/COMPARISON: 2D (a) is $E_U$ (values.tex:81, "E_U (LightGBM seed 42, purity-based subtraction)"); $\chiPaper$ is (f) | Aliases "purity-based subtraction" + "LightGBM" (+ "central value's seed" = 42) | E: s2's (a) clause 10 + s3 17 = 27; s1 (6) shared with (b) |
| a12 | :170 s2 | "In configuration~(a), the four- and five-observable marginal normalizations agree" | 5D FINAL check; 4D DIAGNOSTIC | :113–114 (4D is (e)) | P: about 2 ("four- and") |
| a13 | :170 s4 | "a configuration-(a) closure test with an injected bump in truth $\Eavail$" | DIAGNOSTIC (in three observables; the 3D result is (e)) | :113–114, :334 s1 | E: 27 |
| a14 | :170 s5 | "an injected bump in truth $q_{3}$ closes to within \SI{1.1}{\percent}" … "also in configuration~(a)" | DIAGNOSTIC (the 4D result is (e)) | same | E: 21 |
| a15 | :170 s6 | "These closure tests reweight the simulated signal only." | DIAGNOSTIC (qualifies a13–a14) | — | E: 8 |
| a16 | :174 s2 | "about one standard deviation of the covariance of Sec.~\ref{sec:cov5d}" | FINAL (a) covariance, used as the yardstick for the (c) bias | — | counted under (c)+(d) |
| a17 | :174 s3 | "This bias is not included in the uncertainties quoted for the configuration-(a) central value." | FINAL limitation of (a). The bias it refers to was measured with (c) (Fig. 2 caption, :199) | — | keep (14) |
| a18 | :177 s1–s2 | "puts the purity and refined estimates more than one statistical standard deviation apart" ; "The purity estimate lies up to 5.9 statistical standard deviations from the truth" | COMPARISON: the 2D purity arm is $E_U$ = 2D (a). This is not named in the paper; the source `re1/RE1-REPORT-2.md:117` says "The purity data unfold equals `E_U`" | Alias "purity" (2D context) | E: 32 + 32 = 64 |
| a19 | :177 s3 | "The two-dimensional result therefore uses the refined estimator, configuration~(f)" | FINAL (f); its "therefore" rests on a18 | — | P: rewording (11) |
| a20 | :185 s5–s6 | "within the quoted total uncertainty in about half of those cells" ; "This total uncertainty is that of the covariance of Sec.~\ref{sec:cov5d}." | FINAL (a) covariance, used as the yardstick for (e)'s residuals (a cross-configuration comparison) | — | keep |
| a21 | :185 s7 | "No uncertainty quoted for the configuration-(a) central value includes the regularization bias" | FINAL limitation | — | keep |
| a22 | :208 s4 (Fig. 3 caption) | "the grey band is $\pm$ the total uncertainty" … "of the covariance of Sec.~\ref{sec:cov5d}" | FINAL (a) covariance, drawn in Fig. 3(b) under configuration (e) | the comment at :103–104 says the same | keep |
| a23 | :238 s1–s8 | "The covariance of the configuration-(a) five-observable central value" ; "The comparisons of Sec.~\ref{sec:departure} use this covariance" | FINAL (a) covariance: status, seed study, "We therefore quote no generator significance based on this covariance" | s4's "changing the estimator's random seed moves the projected uncertainty of two further covariances" names no configuration; I take it to be (a)'s seed study (**uncertain**) | keep (164) |
| a24 | :322 s1 | "stability under training seeds and rounding-level input changes; and run-period consistency" | FINAL lessons (the (a) seed pair, the (e) rounding test, the (f) run periods) | — | keep |
| a25 | :328 s1 | "the higher-dimensional central values usable for qualitative comparison" | FINAL ((e) 3D/4D, (a) 5D) | — | keep |
| a26 | :334 s1 | "of configuration~(e) in three and four observables and configuration~(a) in five" | FINAL | — | keep |
| a27 | :334 s2 | "all underpredict the unfolded central value at low $\Eavail$" | FINAL; which central value(s) it means, (e) and/or (a), is **uncertain** | — | keep |
| a28 | :337 s1–s2 | "two thirds of the cell-integrated positive difference in the joint $(\Eavail,W)$ projection" | FINAL (a): the $(E_{avail},W)$ projection exists only in five observables | :334 s1 | keep (67) |
| a29 | :340 s1–s6 | "The map therefore describes where the central value differs from the Tune~v1." | FINAL (a) (same basis as a28) | — | keep (100) |
| a30 | :475 s4 | "no uncertainty quoted for the configuration-(a) five-observable central value includes its regularization bias" | FINAL limitation | — | keep |

**Count.** There are 30 items:

- 22 FINAL or definitional: a1–a3, a5–a8, a10, a16, a17 and a19–a30. Three of these (a16, a20, a22) use the (a) covariance as the yardstick for (c) and (e) results.
- 8 DIAGNOSTIC/COMPARISON: a9 (second clause), a11, a13, a14, a15 and a18, plus a4 and a12 in part.

The paper never calls the 2D (a) result "superseded" in those words. It says the 2D result "uses the refined estimator, configuration (f)" (:177 s3), and Table II assigns the 2D central value to (f).

### Configuration (b): exact-split scikit-learn cross-check

| # | Location | Quote | Role | Basis | Words |
|---|---|---|---|---|---|
| b1 | :88 s3 | "The nominal settings are the scikit-learn defaults, with LightGBM matched to their capacity." | DEFINITIONAL for capacity. It refers to scikit-learn, (b)'s library, but defines the nominal settings of every configuration. Its dependence on (b) is **uncertain** | alias "scikit-learn" | keep |
| b2 | :107–108 (Table II row) | "(b) cross-check: scikit-learn exact splits, unseeded" / "2D cross-check (Sec.~\ref{sec:repro2d})" | COMPARISON | the row's own "cross-check" | E: 14 |
| b3 | :134 s1 | "The distance depends on the estimator." | COMPARISON (framing for (a)-2D and (b)) | — | E: 6 (shared with (a)) |
| b4 | :134 s2 (clause) | "the exact-split estimator gives $\chiPaperExact$ unseeded and $\chiPaperExactSeeded$ in one run" | COMPARISON. The seeded value is a seeded variant of (b) (values.tex:49, "random_state 1/2/3"), not (b) as Table II defines it ("unseeded") | alias "exact-split" | E: 16 |
| b5 | :134 s4 | "We quote the LightGBM result as the central value because its covariance uses the same estimator." | FINAL choice of (f), justified against (b) | — | P: 16 (at risk) |
| b6 | :134 s5 | "This learner was chosen after both comparisons were known." | FINAL disclosure about (f); it needs the (a)/(b) comparisons to have a referent | — | P: 9 (at risk) |
| b7 | :134 s6 | "The benchmark is therefore a reproduction rather than an independent validation." | FINAL (f) conclusion; follows from b6 | — | keep |
| b8 | :134 s7 | "The central value and the exact-split cross-check differ in learner and in background treatment." | COMPARISON | alias "exact-split" | E: 14 |
| b9 | :134 s8 | "Their per-bin difference has a median of \SI{1.03}{\percent} (maximum \SI{17.6}{\percent})." | COMPARISON ((f) vs (b)) | — | E: 10 |
| b10 | :134 s9 | "Both estimators are described in \nsec{sec:method-config}." | COMPARISON | — | E: 6 |
| b11 | :139 (Fig. 1 caption) | "it omits the learner dependence and $C_{\mathrm{model}}$" | FINAL (f) band; "learner dependence" is the (f)–(b) difference | :150 sends "learner dependence" to Sec. IV A | P: about 4 |
| b12 | :150 s5 | "the learner dependence of Sec.~\ref{sec:repro2d-pub}" | FINAL (f) covariance omission; refers to (b) | — | P: 6 |

**Count.** There are 12 items: 6 COMPARISON (b2, b3, b4, b8, b9, b10) and 6 final sentences that refer to (b) (b1, b5, b6, b7, b11, b12). The paper does not say that (b) was an earlier 2D central value. The registry records that it was until 2026-10-11 (ESTIMATORS.tsv, b-exact-split `used_for`).

### Configuration (c): deterministic LightGBM, purity-based subtraction

| # | Location | Quote | Role | Basis | Words |
|---|---|---|---|---|---|
| c1 | main_paper.tex:45 | "Pseudo-experiments measure a background-subtraction bias" ; "and statistical undercoverage at the tested truths" | DIAGNOSTIC ((c)/(d) bias; (c) coverage). No letter given | the Table I rows at :35 and :37 | P: about 3 + 7 |
| c2 | :35 (Table I) | "background-subtraction bias up to 4\% at high $W$; negative weights remove most" | DIAGNOSTIC, (c), (d) | Conf. "(c), (d)" | E: 19 (shared with (d)) |
| c3 | :37 (Table I) | "statistical intervals miscover under an about 10\% rate reduction" | DIAGNOSTIC (the coverage test is on (c), and no reported result uses (c)) | Conf. "(c)" | E: 13 |
| c4 | :91 s5 | "remove most of the bias of the purity method at nominal truth" | FINAL (e) property, stated against the purity comparator. The Sec. V A evidence is (d) (:174 s4); (e)'s own nominal residual appears only at :208 s5 | alias "purity" | P: rewording (about 16) |
| c5 | :96 (Table II caption) | "(c)--(e) are deterministic LightGBM (fixed seeds, reproducible training)" | DEFINITIONAL: (e)'s determinism is stated only through this range | — | P: rewording |
| c6 | :109–110 (Table II row) | "(c) deterministic variant" / "background bias; coverage test (Figs.~\ref{fig:bkg-residual}, \ref{fig:coverage})" | DIAGNOSTIC | — | E: 16 |
| c7 | :111 (Table II row d) | "(d) as (c), refined" | DEFINITIONAL for (d) | — | (under d) |
| c8 | :174 s1 | "with the purity-based background subtraction, end-to-end pseudo-experiments at nominal truth reproduce the input" | DIAGNOSTIC; the letter is given only in Fig. 2 (:199 s2) | alias "purity-based subtraction" (a)–(c), resolved by :199 | E: 22 (shared) |
| c9 | :174 s2 | "These cells are biased by up to \SI{4}{\percent} in simulation" | DIAGNOSTIC (scaled by the (a) covariance, a16) | — | E: 24 (shared) |
| c10 | :174 s5 | "On data, the two treatments differ by at most \SI{1.4}{\percent}." | COMPARISON on data, (d) minus (c): VALIDATION_LEDGER.md:209 (VL152, "the F2 estimator on the 5D data under `negweight-refined` minus under purity") | "the two treatments" | E: 10 (shared) |
| c11 | :174 s6 | "Both kinds of closure study are described in \nsec{sec:closure-map}." | pointer; it also covers the (a) closures of :170 | — | E: 9 (shared) |
| c12 | :191 s1–s4 | "Statistical intervals from configuration~(c), corrected for the estimator's closure bias at nominal truth" | DIAGNOSTIC: the only coverage test in the paper | — | E: 106 |
| c13 | :193 s1–s3, s5 | "attributes the miscoverage to a residual bias that grows with $W$" | DIAGNOSTIC | — | E: 33 + 10 + 18 + 10 = 71 |
| c14 | :193 s4 | "Agreement in the marginal normalizations thus coexists with substantial residual bias" | Joins the FINAL (a)/(e) normalizations to the (c) result | — | P: 15 |
| c15 | :199 (Fig. 2 caption, whole) | "Circles: purity-based background subtraction, configuration (c)" ; "Squares: … configuration (d)" | DIAGNOSTIC, (c) vs (d) | — | E: 78 (shared) |
| c16 | :227 (Fig. 4 caption, whole) | "from configuration (c) of Table~\ref{tab:estimators}, with 400 pseudo-experiments" | DIAGNOSTIC | — | E: 179 |
| c17 | :312 s5 | "The miscoverage of Sec.~\ref{sec:coverage} is also attributed to a residual bias" | DIAGNOSTIC (exists only for the (c) result) | — | E: 23 |
| c18 | :317 s3 | "What unbinned information could recover, the coverage failure, and the validity of any interval" | Table III scope; "the coverage failure" is (c) | — | P: 3 |
| c19 | :322 s1 | "coverage under changes of the truth, not only at nominal truth" | methods lesson drawn from (c) | — | P: 11 |
| c20 | :122 s2–s3 | "Coverage, how often intervals contain their target over repeated experiments" | definition used by the (c) study and by the coverage statements about final results (:46, :154) | — | keep |

**Count.** There are 20 items: 12 DIAGNOSTIC/COMPARISON (E: c2, c3, c6, c8–c13, c15–c17) and 8 partial or definitional (c1, c4, c5, c7, c14, c18–c20). The paper does not say that a coverage result for (c) carries over to (a), (e) or (f). The scope paragraph (:46 s2) says that three- to five-observable results have no validated-coverage intervals.

### Configuration (d): as (c), negative weights, refinement 100 trees, 8 leaves

| # | Location | Quote | Role | Basis | Words |
|---|---|---|---|---|---|
| d1 | main_paper.tex:45 | "a partial recovery of generator-sized truth changes" | DIAGNOSTIC for (d), FINAL-estimator study for (e) (Table I row :36, "(d), (e)") | — | keep |
| d2 | :35, :36 (Table I) | "negative weights remove most" ; "generator-sized truth changes only partly recovered" | DIAGNOSTIC | Conf. "(c), (d)" and "(d), (e)" | :35 counted under (c); :36 P: 1 ("(d),") |
| d3 | :111–112 (Table II row) | "(d) as (c), refined" / "background bias; generator-sized $\Eavail$ change" | DIAGNOSTIC/COMPARISON | — | E: 23 |
| d4 | :174 s4 | "The unbinned negative-weight background treatment, configuration~(d), reduces it to below \SI{0.3}{\percent}" | COMPARISON (vs (c)) | — | E: 30 (shared) |
| d5 | :185 s1 | "the unfolding recovers only part of a change of the $\Eavail$ shape" | the finding is shared by Fig. 3(a) (d) and Fig. 3(b) (e) | — | keep |
| d6 | :185 s2 | "the $(\Eavail,W)$ cells unfolded with configuration~(d) deviate from it" | DIAGNOSTIC (the 74% cell) | — | E: 40 |
| d7 | :185 s3 | "These deviations occur with or without background" | DIAGNOSTIC (d) (VL151: signal-only on the same seeds reproduces it) | — | E: 16 |
| d8 | :185 s4 | "thirty iterations reduce the $\Eavail$ residual by \SI{26}{\percent}" | DIAGNOSTIC. The configuration is not named; `sec_5d.tex:72–77` describes these as the development experiments (family N = (d)). **Uncertain.** This sentence carries the "regularization bias" interpretation that Sec. VI (:312 s2) and Table III (:315–317) use | — | E: 38 |
| d9 | :185 s9 | "The deformation studies, the iteration and capacity tests" | pointer | — | P: 5 |
| d10 | :199 (Fig. 2 caption) | "Squares: the unbinned negative-weight treatment, configuration (d) (60 pseudo-experiments)." | DIAGNOSTIC | — | counted under (c) shared |
| d11 | :208 s2–s3 (Fig. 3 caption) | "(a) Configuration (d), with the truth reweighted by the GiBUU/GENIE $\Eavail$ shape ratio" | DIAGNOSTIC (Fig. 3a) | — | E: 26 + 14 = 40 |
| d12 | :208 s6 | "Neither seed set was held out from the estimator's development." | covers both panels | — | P: rewording |
| d13 | :242 s2 | "as they move those of the baseline estimator (2.5)" | COMPARISON. "Baseline estimator" is B0 = (d) (ALIASES.tsv d-N-B0 `contract-name` "baseline B0"; source comment :241 "baseline 0.80 median, 2.48 max") | alias "baseline" (B0) | P: 9 |
| d14 | :254–268 (Table III), :315, :317 | "boosted-tree OmniFold (trees) against exact binned iterative unfolding (exact)" | DIAGNOSTIC; **configuration not named in the paper**. Source `d-id/REPORT.md`: the "GBDT" column comes from B0 `asimov_same` traces (`k_b0_*`, :57, :126). These are signal-only and noise-free, so no background refinement acts, and they are the (c)–(e) OmniFold classifiers at 100/8. The fifth pooled change (W2) uses the (e) assessment ensemble (:204–206). :315 s2 says "the fixed truth changes used to develop the estimator" (= (e)'s development, cf. :94) | — | **not counted** (about 360: caption 98, rows 28, prose 225) |
| d15 | :312 s2 | "which we interpret as regularization bias" | Sec. VI result 1; its basis is d6–d8 (and (e) at :185 s5) | — | keep |

**Count.** There are 15 items: 6 DIAGNOSTIC/COMPARISON (E: d3, d4, d6, d7, d8, d11) and 9 that are partial, shared or uncertain. Table I's rounding row (:38) lists "(a), (e)" but not (d), although :242 uses the (d) baseline as its comparator.

### Configuration (e): joint-test estimator (refinement 400 trees, 31 leaves)

Every (e) item is FINAL, except where the row says otherwise.

| # | Location | Quote | Role / basis |
|---|---|---|---|
| e1 | main_paper.tex:45 | "no tested reporting definition meets our 10\% precision criterion" ; "simulation-calibrated tests of hybrid null hypotheses for five generator predictions all reject" | FINAL (precision study, joint tests) |
| e2 | :17 s2 | "obtain simultaneous three-, four-, and five-observable central values" | FINAL (3D, 4D) |
| e3 | :20 s1 | "inference with a biased estimator" | FINAL (joint tests) |
| e4 | :34, :36, :38, :39, :40 (Table I) | "the 3D (e) marginal with the 2D (f) result to 0.141\%" ; "all ten hybrid-null tests reject at 5\% familywise" | FINAL |
| e5 | :46 s3 | "The sixteen-cell result of Sec.~\ref{sec:result16} also has total uncertainties" | FINAL |
| e6 | :88 s4 | "The refinement capacity of the joint-test estimator was chosen in simulation closure studies." | FINAL (the closure studies themselves are in the note) |
| e7 | :91 s4–s5 | "the sixteen-cell result (Sec.~\ref{sec:result16}) uses configuration~(e)" ; "The joint tests use configuration~(e), the joint-test estimator" | FINAL; s5's bias claim leans on the (c)/(d) comparison (c4) |
| e8 | :94 s1–s2 | "Configuration~(e) keeps five iterations because 10, 15, or 20 iterations did not reduce" | FINAL |
| e9 | :96 | "(c)--(e) are deterministic LightGBM" ; "(f) is (a) with the refinement of (e)" | DEFINITIONAL |
| e10 | :113–114 (Table II row) | "(e) joint-test estimator" / "3D and 4D central values; sixteen-cell 5D result" | FINAL |
| e11 | :170 s3 | "its area-weighted total agrees with the configuration-(f) two-dimensional result to \SI{0.141}{\percent}" | FINAL ((e) 3D vs (f) 2D, a cross-configuration check) |
| e12 | :185 s5, s8 | "For other fixed generator shapes, measured with the joint-test estimator" ; "For the sixteen-cell result, the model term of its reported covariance" | FINAL-estimator diagnostic, graded against the (a) covariance (a20) |
| e13 | :208 s4–s5 (Fig. 3b) | "(b) Configuration (e), the joint-test estimator, for three shape changes not used" | FINAL-estimator diagnostic |
| e14 | :242 s2–s4 | "move the results of the higher-capacity refinement by up to 2.6" ; "For the joint-test estimator, this spread lies inside the data-bootstrap statistical uncertainty" | FINAL-estimator diagnostic (alias "higher-capacity refinement") |
| e15 | :248 s1–s7, :250 s1–s2 | "With the joint-test estimator, the envelope alone exceeds it" | FINAL (precision study) |
| e16 | :254–268, :315, :317 | see d14 | DIAGNOSTIC; configuration unnamed, **uncertain** |
| e17 | :274, :277, Table IV :280–303, :305 | "configuration~(e)'s data result on 16 cells, R00--R15" | FINAL (sixteen-cell result and its fake-data tests) |
| e18 | :312 s3–s4 | "which tracks the same bias and alone exceeds the precision target" ; "the upward displacement of the external nulls by the estimator's pull toward its prior" | FINAL |
| e19 | :328 s1 | "the sixteen-cell result usable for the comparison" | FINAL |
| e20 | :334 s1, s3 | "of configuration~(e) in three and four observables" | FINAL (3D/4D descriptive comparisons) |
| e21 | :346, Fig. 5 :351, Table V :356–367, :372 | "compares the sixteen-cell result of Sec.~\ref{sec:result16} with five predictions" | FINAL |
| e22 | :379, :382, :386, :392, :395, :400, :405, :408, :412, :416, :418, :421, :423 | ":382 s6 "The joint-test estimator unfolds the pseudo-data with the other half of the simulation."" | FINAL (hypotheses, calibration and conditions of the joint tests; :91 s5) |
| e23 | :429, Table VI :436–454, :459 | "the external nulls are displaced far upward by the estimator's pull toward its prior" | FINAL (joint-test results, projections, power) |
| e24 | :465 s3, :475 s5–s8 | "The calibrated tests illustrate inference with a biased estimator" ; "The sixteen-cell result also has total uncertainties, whose coverage is not validated" | FINAL |
<!-- absence-ok: quotes or proposes the paper's printed text (scope and coverage statements of the sixteen-cell result and the configuration-(a) product) as this record's inventory or plan; not a new absence claim -->

### Configuration (f): (a) with the (e) refinement, the 2D central value

| # | Location | Quote | Role / basis |
|---|---|---|---|
| f1 | main_paper.tex:45 | "OmniFold reproduces the published muon-kinematic cross section's integral within about 1\%" | FINAL |
| f2 | :17 s2 | "We first reproduce the published double-differential charged-current inclusive cross section" | FINAL |
| f3 | :32, :33, :34 (Table I) | "2D integral within about 1\%; correlated shape difference" ; "2D covariance, median \SI{\uqMedian}{\percent} per bin" | FINAL |
| f4 | :91 s2–s3 | "The two-observable central value uses configuration~(f)" ; "so its covariance is built with the same estimator" | FINAL |
| f5 | :96, :115–116 | "(f) is (a) with the refinement of (e)" / "2D central value and covariance (Sec.~\ref{sec:repro2d})" | FINAL. Its definition depends on (a) and (e) |
| f6 | :131 s1–s10, Fig. 1 :139 | "The two-dimensional result is an end-to-end test of the unfolding" | FINAL (the source comment :140–141 says Fig. 1 is drawn from $E_R$, $Q_R$) |
| f7 | :134 s3–s8 | "We quote the LightGBM result as the central value because its covariance uses the same estimator." | FINAL, stated against (a) and (b) |
| f8 | :150, :154, :157, :161 | "each from LightGBM unfoldings with the central value's estimator" | FINAL (2D covariance and $C_{model}$). values.tex:60–75 tag the macros as RE-2 $E_R$/$Q_R$. **Uncertain:** the hard-coded run-period numbers at :157 (the ~7% step and the 2.0% integral) cite records that predate (f) (the comments at :156 and :149 cite `period-unfold-20261014`, `playlist-term` and `budget_Q`), so they may have been measured with (a) |
| f9 | :170 s3 | "agrees with the configuration-(f) two-dimensional result" | FINAL |
| f10 | :177 s3 | "The two-dimensional result therefore uses the refined estimator, configuration~(f)" | FINAL (its justification is a18) |
| f11 | :328 s1, :475 s3 | "which is what makes the two-dimensional result reusable" ; "The two-dimensional covariance has not been independently validated" | FINAL |

**Count.** (e) has 24 items and (f) has 11. All are final, except e16 (Table III), which is a diagnostic with an unnamed and uncertain configuration.

---

## 3. What the paper would lose if every non-final configuration moved to the note

Here "non-final" means (b), (c), (d) and the 2D, 3D and 4D roles of (a). The 5D (a) central value and covariance are FINAL by the paper's text, so they are not on this list.

### Methods findings that need a comparison configuration named in the paper

1. **Purity-based vs negative-weight background subtraction bias in five observables, (c) vs (d).** This covers:
   - Table I :35;
   - Sec. V A :174 (s1, s2, s4–s6);
   - all of Fig. 2;
   - the abstract's "background-subtraction bias";
   - the data-level method difference of 1.4%, (d) minus (c), at :174 s5.

   The same comparison supports three statements about final configurations:
   - (e)'s claim that it "remove[s] most of the bias of the purity method" (:91 s5);
   - the disclosure that the purity bias is not in the uncertainties of the 5D (a) central value (:174 s3);
   - the yardstick "about one standard deviation" of the (a) covariance (:174 s2).

   Without (c) the paper could state the purity bias of the final (a) estimator only by quoting a number measured on a different configuration, without naming that configuration.
2. **2D purity vs refined closure, 2D (a) vs (f)** (:177 s1–s2). This is the paper's stated reason ("therefore", :177 s3) for using (f) for the 2D result.
3. **2D estimator and learner dependence of the benchmark: (a) seeds, (b), and (a)→(f) at seed 42** (:134 s1–s5, s7–s9). The post-selection disclosure ("This learner was chosen after both comparisons were known", s5) and "a reproduction rather than an independent validation" (s6) refer to these comparisons. So do the "learner dependence" omitted from the 2D band and covariance (Fig. 1 caption :139; :150 s5).
4. **Coverage test under (c)** (:191, :193, Fig. 4, Table I :37, :312 s5, :322's lesson, the abstract's "statistical undercoverage"). This is the paper's only coverage measurement of a five-observable estimator. No final configuration has a coverage test in the paper.
5. **Generator-sized $E_{avail}$ change with (d)**: the 74% cell and Fig. 3(a) (:185 s2–s3, :208 s2–s3). The iteration and capacity tests behind the "regularization bias" interpretation (:185 s4; configuration uncertain) are also here. That interpretation is used by Sec. VI result 1 (:312 s2) and by the Table III diagnostic (:315–317). The finding "only partly recovered" survives with (e) alone (Fig. 3(b), 16–31%, :185 s5).
6. **Rounding-level instability, (e) vs the "baseline estimator" (d)** (:242 s2). The comparison shows that the instability is not specific to the refinement. (e)'s own number (2.6) carries the stability finding without it.
7. **Signal-only closures of (a) in 3D and 4D** (:170 s4–s6). These validate a configuration that is not the configuration of the reported 3D/4D results ((e), :113–114). The 4D part of the normalization check (:170 s2, Table I :34) has the same issue.

### Results, figures and tables that would go or be re-described

- **Fig. 2** (`fig:bkg-residual`): all (c)/(d). It would go.
- **Fig. 3(a)**: (d). It would go. Fig. 3(b) stays ((e)), and its band is the (a) covariance.
- **Fig. 4** (`fig:coverage`): all (c). It would go.
- **Table II.** Rows (b), (c) and (d) would go, and so would the "3D and 4D closures; 2D learner comparisons" clause of row (a). The caption's "(c)--(e) are deterministic" would need (e) restated on its own. Row (d)'s "as (c)" goes with the row. (f) stays defined as "(a), refined", since (a) stays for 5D.
- **Table I.** Rows :35 and :37 would go. Row :36 would lose "(d)". Row :34 would lose "4D and" and part of "(a)".
- **Table III** (`tab:binned`) and :315–317. The configuration is not named. The source says B0 signal-only traces, which coincide with (e)'s OmniFold classifiers when no background is present. Re-describing it, rather than moving it, is the uncertain case.
- **Sec. IV A** :134 would be reduced to (f)'s own numbers. The post-selection disclosure would need re-description.
- **Sec. V A** :174 and :177 s1–s2 would go, and :177 s3 would need a new justification.
- **Sec. V B** :185 s2–s4 would go, and the interpretation in s4 would need restating with (e) evidence.
- **Sec. V C** would go entirely: :191, :193 and Fig. 4.
- **Abstract.** "a background-subtraction bias" and "statistical undercoverage at the tested truths" would go or be re-described.
- **Sec. VI** :312 s5 would go. **Sec. VI** :322 would lose the coverage lesson.

---

## 4. Estimated word saving

The method is described in the Source and method section above. The figures are LaTeX source tokens; PDF words are about 2–4% higher.

| Configuration | E (removable) | Main contributors | P (partial, deletable clauses) | P at risk (rewording) |
|---|---:|---|---:|---:|
| (a), non-final roles only | 156 | :134 s2 clause 10 + s3 17; :170 s4–s6 56; :177 s1–s2 64; Table II clause 9 | about 4 | :177 s3 (11) |
| (b) | 60 | Table II row 14; :134 s2 clause 16, s7 14, s8 10, s9 6 | about 10 (Fig. 1 caption about 4, :150 s5 6) | :134 s4–s5 (25) |
| (c) | 408 | Table II row 16; Table I :37 13; :191 106; :193 71; Fig. 4 caption 179; :312 s5 23 | about 36 (abstract 7, :193 s4 15, :317 3, :322 11) | :91 s5 clause (about 16); :96 caption |
| (d) | 157 | Table II row 23; :185 s2–s4 94; Fig. 3 caption s2–s3 40 | about 15 (:242 9, :185 s9 5, Table I :36 1) | :208 s6 |
| (c)+(d) shared | 192 | Table I :35 19; :174 s1 22, s2 24, s4 30, s5 10, s6 9; Fig. 2 caption 78 | about 4 (abstract "a background-subtraction bias") | — |
| (a)+(b) shared | 6 | :134 s1 | — | — |
| **Total** | **979** | | **about 69** | **about 52** |

- **Gross saving.** About 1,050 source tokens (E + P), or about 1,100 including the at-risk sentences. That is about 1,070–1,130 PDF words, roughly 11% of the 9,505 non-comment body tokens.
- **Net saving.** The removals would need replacement wording, which I did not draft. Examples: stating that (e) is deterministic; quoting the purity bias for (a) without its measurement configuration; a new justification for (f) in place of :177; restating the regularization-bias interpretation. My guess is a few tens of words, so a net saving of roughly 950–1,050 tokens. This range is an estimate.
- **Not counted.** Table III and its prose, about 360 tokens, whose configuration the paper does not name (see d14). I also did not count the 5D (a) material, which the paper treats as final: Sec. V D :238 (164), Sec. VII A :334–:340 (about 239), and the (a) clauses at :91, :174 s3, :185 s6–s7 and :475 s4.

---

# Addendum (coordinator request): Joseph's decision that only (f) and (e) are presented

Under the decision, the paper presents (f) for 2D and (e) for 3D, 4D and the sixteen-cell 5D result. Everything else, including the configuration-(a) fine-grid 5D central value, moves to the note. The items below are cited from the same HEAD read, sha1 `2762b3e7`. Where the working tree now differs (re-measured, working tree sha1 `be161104`), I give the current wording.

## A1. Joint-test material (Sec. VII, :324–:459) that rests on a non-final configuration

This section only marks dependences. It moves nothing.

| Location | Quote (≤15 words) | Non-final dependence | How |
|---|---|---|---|
| :328 s1 | "the higher-dimensional central values usable for qualitative comparison" | (a) | "Higher-dimensional central values" includes the five-observable (a) central value (:334 s1) |
| :334 s1 | "of configuration~(e) in three and four observables and configuration~(a) in five" | (a) | Sec. VII A names (a) as its five-observable input |
| :334 s2 | "all underpredict the unfolded central value at low $\Eavail$" | **uncertain** | The source comment :333 cites VL159, a **3D** comparison (VALIDATION_LEDGER.md:168). The paper assigns 3D to (e), but I have not verified that VL159 was computed on (e) rather than an earlier 3D estimator |
| :334 s3 | "Comparisons with pion final-state-interaction variations, GENIE's Valencia 2p2h component" | none named | 3D/4D note pointers ((e) per Table II) |
| :337 s1–s2 | "two thirds of the cell-integrated positive difference in the joint $(\Eavail,W)$ projection" | (a) | The $(E_{avail},W)$ projection exists only in five observables, so this is the (a) map |
| :340 s1–s2, s4–s6 | "The map therefore describes where the central value differs from the Tune~v1." | (a) | The same map: the generator ratios $\genRatioTotLo$–$\genRatioTotHi$, and "No closure test with a mismodelled detector response has been run for this map" |
| :340 s3 | "where the regularization bias of Sec.~\ref{sec:validation} is largest" | (d) (and (e)) | The largest residual quoted in Sec. V is (d)'s 74% cell at high $E_{avail}$ and high $W$ (:185 s2); (e)'s 16–31% is at :185 s5 |
| main_paper.tex:94 | "the numbers quoted in Sec.~\ref{sec:central}" ; "the $(\Eavail,W)$ map" | (a) | The release reproduces the Sec. VII A numbers and the (a) map figure in the note |
| :250 s2 | "after a descriptive comparison of the central values" | (a) (and (e)) | Points to Sec. VII A |
| :91 s5 | "remove most of the bias of the purity method at nominal truth" | (c), (d) | The paper's reason for using (e) in the joint tests is stated against the purity method. The Sec. V A evidence it cites is (c) vs (d) (:174 s1–s4); (e)'s own nominal residual is only at :208 s5 |
| :238 s3 | "The calibration of the joint tests in Sec.~\ref{sec:joint} does not use it." | (a) (negative) | Explicitly says the calibration does **not** use the (a) covariance |
| :346–:372 (Sec. VII B) | "compares the sixteen-cell result of Sec.~\ref{sec:result16} with five predictions" | none | (e) sixteen-cell result |
| :379 (hypotheses) | "the null hypothesis $H_{0}(G)$ is that the true cross section equals $G$" | none | No estimator named |
| :382 s6 (calibration) | "The joint-test estimator unfolds the pseudo-data with the other half of the simulation." | none ((e)) | The calibration estimator is (e). The lateral $\Delta_b$ "from endpoint unfoldings of the data" (:382 s4) and the pilot-ensemble metric $V$ (:386 s4) name no estimator; I presume (e) (**not stated**) |
| :392 | "the change of the noise-free unfolded result in the last step of a refinement" | none named | $\delta_{fine}$ (grid refinement, not Stay-Positive); I presume (e) (**not stated**) |
| :395, :400 (decision rule, design) | "The ten tests are controlled at a familywise level $\alpha=\jtAlpha$ by the Holm procedure" | none | — |
| :405–:423 (conditions i–vi) | "Repeating part of the calibration with a quarter of the simulation resolved no change" | none | (e) calibration; :412 s5's projection check and :416's recoil re-unfolding use the same tests |
| :429, Table VI :436–:454 | "the external nulls are displaced far upward by the estimator's pull toward its prior" | none | (e) |
| :459 | "a calibration that puts the estimator's bias toward its prior and the nuisance terms" | none | (e): projections and power |
<!-- absence-ok: quotes or proposes the paper's printed text (scope and coverage statements of the sixteen-cell result and the configuration-(a) product) as this record's inventory or plan; not a new absence claim -->

**Summary.** Hypotheses, calibration, decision rule, conditions and results (Secs. VII C–F) rest on (e) alone. The non-final dependences are three:
- Sec. VII A's five-observable descriptive comparison and map, which are (a): :328 s1, :334 s1, :337, :340 and main_paper.tex:94.
- :340 s3's reference to where the bias is largest, which is (d).
- The stated rationale for choosing (e) (:91 s5), which rests on (c)/(d).

:334 s2 is uncertain.

## A2. Every paper item about the configuration-(a) 5D central value or its five-axis covariance

**D** marks items directly about it. **I** marks items that are indirect: the item uses the (a) covariance as a yardstick, or (a) is one of several inputs.

| Location | Quote (≤15 words) | D/I | Note |
|---|---|---|---|
| main_paper.tex:45 (abstract) | "it yields central values only, whose normalizations agree with lower-dimensional results" | D | "With five simultaneous observables" = the (a) central value; the normalization check is :170 s2 |
| main_paper.tex:45 | "Pseudo-experiments measure a background-subtraction bias" | I | The purity bias applies to (a) (:174 s3) but was measured with (c) |
| main_paper.tex:94 (Data availability) | "the numbers quoted in Sec.~\ref{sec:central}" … "the $(\Eavail,W)$ map" | D | |
| :17 s2 | "obtain simultaneous three-, four-, and five-observable central values" | D (5D part) | |
| :17 s3 | "so the five observables are simultaneous but not independent" | I | Applies to every five-observable result, (e) sixteen-cell included |
| :34 (Table I) | "4D and 5D (a) marginal normalizations agree at about 1--2\%" | D | Conf. column "(a), (e), (f)" |
| :35 (Table I) | "background-subtraction bias up to 4\% at high $W$" | I | Conf. (c), (d); the bias applies to the purity-based (a) via :174 s3 |
| :38 (Table I) | "seed-dependent (a) covariance; rounding-level instability" | D (first clause) | The rounding clause is (e)/(d) |
| :46 s2 (Scope) | "Throughout, a three- to five-observable result is a central value without intervals" | D (in part) | Covers the (a) 5D central value with the (e) 3D/4D values; unchanged in the working tree |
| :46 s4 (Scope) | "The paper does not deliver a validated five-observable cross-section measurement." | I | Applies to both five-observable results |
| :91 s4 | "The configuration-(a) five-observable central value and its covariance use the purity-based subtraction" | D | |
| :105–106 (Table II row a) | "5D central value and covariance of Sec.~\ref{sec:cov5d}" | D | Hidden comment :103–104: the covariance "supplies the band of Fig. 3(b)" |
| :170 s2 (sec:closure) | "In configuration~(a), the four- and five-observable marginal normalizations agree" | D | |
| :174 s2 (sec:closure) | "about one standard deviation of the covariance of Sec.~\ref{sec:cov5d}" | I | (a) covariance as the yardstick for the (c) bias |
| :174 s3 (sec:closure) | "This bias is not included in the uncertainties quoted for the configuration-(a) central value." | D | |
| :185 s5 (sec:departure) | "within the quoted total uncertainty in about half of those cells" | I | (e) residuals graded against the (a) covariance |
| :185 s6 (sec:departure) | "This total uncertainty is that of the covariance of Sec.~\ref{sec:cov5d}." | D | |
| :185 s7 (sec:departure) | HEAD: "No uncertainty quoted for the configuration-(a) central value includes the regularization bias" / now: "The uncertainties of the configuration-(a) central value omit the regularization bias." | D | |
| :193 s4 (sec:coverage) | "Agreement in the marginal normalizations thus coexists with substantial residual bias" | I | The normalizations are (a)'s 4D/5D and (e)'s 3D; the bias is (c)'s. This is the **only** (a) touch in Sec. V C. :191, :193 s1–s3 and s5 are (c) only |
| Fig. 3 caption :208 s4 (fig:deformation) | "the grey band is $\pm$ the total uncertainty of the $(\Eavail,W)$ projection" | D | The (a) covariance is drawn in panel (b) |
| Fig. 4 caption :227 (fig:coverage) | — | none | All (c); **no (a) content** |
| :238 s1–s8 (sec:cov5d, whole paragraph) | "The covariance of the configuration-(a) five-observable central value" | D | s5's pointer to Sec. VII B is (e). Working-tree s6 now reads "was studied with only one seed pair." |
| :322 s1 | "stability under training seeds and rounding-level input changes" | I | The seed lesson comes partly from the (a) seed pair (:238 s4) |
| :328 s1 | "the higher-dimensional central values usable for qualitative comparison" | I | |
| :334 s1 | "and configuration~(a) in five" | D | |
| :337 s1–s2 | "two thirds of the cell-integrated positive difference in the joint $(\Eavail,W)$ projection" | D | |
| :340 s1–s6 | "The map therefore describes where the central value differs from the Tune~v1." | D | s3 also leans on (d) (A1) |
| :250 s2 | "after a descriptive comparison of the central values" | I | |
| :475 s4 (Limitations) | HEAD: "no uncertainty quoted for the configuration-(a) five-observable central value includes its regularization bias" / now: "the uncertainties of the configuration-(a) five-observable central value omit its regularization bias" | D | The first clause ("higher-dimensional central values lack intervals of validated coverage") also covers (e) 3D/4D |

**Consequences for final material if the (a) 5D product leaves**, from the rows above:

- **Fig. 3(b) and :185 s5–s6.** They lose their yardstick: (e)'s held-out residuals are graded against the (a) covariance's $(E_{avail},W)$ projection.
- **:174 s2.** The (c) bias loses its "about one standard deviation" scale.
- **(f)'s definition.** (f) is defined through (a) at :91 s2, :96 and :115 ("(f) as (a), refined"). It would need a self-contained definition: LightGBM, seed 42, negative weights, refinement 400/31.

## A3. Sentences containing "configuration-(a)" or "configuration (a)" / "configuration~(a)"

I matched these with the regex `[Cc]onfiguration[-~ ]\(a\)` over HEAD and over the working tree. Both give the same 10 sentences on the same lines, and none is in a comment line. Panel labels such as ":208 '(a) Configuration (d)'" and ":199 '(a) The 42…'" do not match and are not (a).

| Line | Sentence | Falls away with the 5D (a) product? |
|---|---|---|
| :91 s2 | "the learner and seed of configuration~(a) with negative-weight background subtraction" | **No.** This is (f)'s definition; it needs rewording only if (a) is no longer defined in the paper |
| :91 s4 | "The configuration-(a) five-observable central value and its covariance use the purity-based subtraction" | **Yes** (s4 also carries the (e) sixteen-cell clause after the semicolon, which stays) |
| :170 s2 | "In configuration~(a), the four- and five-observable marginal normalizations agree" | **Yes** (5D part: product; 4D part: non-final (a) anyway) |
| :170 s4 | "a configuration-(a) closure test with an injected bump in truth $\Eavail$" | **Moves anyway.** This is the 3D (a) closure, non-final, not the 5D product |
| :170 s5 | "closes to within \SI{1.1}{\percent} in the $q_{3}$ marginal, also in configuration~(a)" | **Moves anyway.** This is the 4D (a) closure, non-final, not the 5D product |
| :174 s3 | "This bias is not included in the uncertainties quoted for the configuration-(a) central value." | **Yes** |
| :185 s7 | now: "The uncertainties of the configuration-(a) central value omit the regularization bias." | **Yes** |
| :238 s1 | "The covariance of the configuration-(a) five-observable central value" | **Yes** (with the whole of :238) |
| :334 s1 | "of configuration~(e) in three and four observables and configuration~(a) in five" | **Yes, the (a) clause.** The (e) 3D/4D clause stays |
| :475 s4 | now: "the uncertainties of the configuration-(a) five-observable central value omit its regularization bias" | **Yes, the second clause.** The first clause, on the lack of validated coverage, stays |

Items that reference (a) by letter without the word "configuration", for completeness: Table I :34 "4D and 5D (a)", :38 "seed-dependent (a) covariance"; Table II :105 "(a) central value: LightGBM, seed 42 in 2D", :115 "(f) as (a), refined"; Table II caption :96 "(f) is (a) with the refinement of (e)"; Table I Conf. column :34 "(a), (e), (f)", :38 "(a), (e)".
