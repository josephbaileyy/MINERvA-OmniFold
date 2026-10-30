# r22 Step 2 triage: differs.tsv rows of chunk04 and chunk05 (58 rows)

Base = `git -C $WT show 9d3054f9:docs/analysis-note/<file>`; "now" = the current file in `$WT/docs/analysis-note/`.
Every "now prints" quote below was checked with `grep -F` on the current file (count 1 unless noted).

| chunk | Q | file tag | class | evidence | fix |
|---|---|---|---|---|---|
| chunk04 | Q1 | sec_3d.tex TD74 | REAL (minor) | "Tune v1 is the analysis simulation's truth" is supported (base item list: "taken directly from the truth of the analysis simulation"), but "processed" is lost: base "We generated and processed GENIE, NuWro and GiBUU samples"; now "were generated for this analysis". | restore "generated and processed" (pair 1) |
| chunk04 | Q2 | sec_3d.tex TD82 | MOVED-OK | now sec_3d.tex:130, end of the flux paragraph: "Each prediction is normalized by its own flux-averaged total CC cross section per nucleon." | none |
| chunk04 | Q3 | sec_3d.tex TD94 | SUPPORTED | base caption of fig:3dmodels: "Models track the $\pT$ and $\pPar$ shapes but differ on $\Eavail$". | none |
| chunk04 | Q4 | sec_3d.tex TD97 | SUPPORTED | base: "invisible in 2D"; base caption: "Models track the $\pT$ and $\pPar$ shapes but differ on $\Eavail$". The displayed projections are pT, pPar, Eavail, so "only $\Eavail$" follows. | none |
| chunk04 | Q7 | sec_3d.tex TD110 | RATER-WRONG | (control only) "only" is evaluative; the range and the $\pm1\sigma$ are unchanged. | none |
| chunk04 | Q8 | sec_3d.tex TD112 | MOVED-OK | the conclusion prints as the paragraph heading, sec_3d.tex:158: "\paragraph{The tested pion-FSI variations do not account for it.}" | none |
| chunk04 | Q11 | sec_3d.tex TD128 | SUPPORTED | base TD96: "Data lie \emph{above} all four across the quasielastic--$\Delta$ dip", so "sitting low" means below the data; "that need" is the antecedent of base "it". | none |
| chunk04 | Q12 | sec_3d.tex TD151 | SUPPORTED | base caption fig:q3excess: "4D data/Tune~v1 ratio ... with $q_{3}$ (center)"; "mild" is evaluative and the 1.03--1.19 range stays. | none |
| chunk04 | Q13 | sec_3d.tex TD154 | REAL | the added gloss narrows the unified throw to "interaction-model bands". Base sec_systematics.tex:156: "jointly re-unfolding all reweightable knob bands and the flux multisim"; base app_statmethods.tex:159: "simultaneously perturbing every reweightable band and the flux multisim". The base never calls them interaction-model bands. | gloss in the base terms (pair 2) |
| chunk04 | Q14 | sec_3d.tex TD172 | RATER-WRONG (wording only) | the limitation is kept ("has not been made"); "finer" is carried by "all 44 cells" against the two super-cells of the preceding paragraph; "remains future work" is a statement of intent, not a fact or a limitation. | none (optional: restore "remains future work" if intent should print) |
| chunk04 | Q15 | sec_3d.tex TD176 | SUPPORTED | base comment beside the caption: "Comparator: the MINERvA Tune~v1 prior"; base caption title "4D data/Tune~v1 ratio"; the ratio rising with $q_3$ is the structure; "genuine" is evaluative (review fix B-F04). | none |
| chunk04 | Q16 | sec_eavailw.tex EW0 | SUPPORTED + MOVED-OK | config glosses: base sec_method.tex:96 "(a), the same learner with purity-based background subtraction" and :97 "(e), ... a deterministic LightGBM variant with the unbinned negative-weight background treatment"; the covariance pointer now prints where the covariance is used: "are a small fraction of the projected uncertainties (\S\ref{sec:eavailw-adopted})" and EW73's "(\S\ref{sec:eavailw-adopted})". | none |
| chunk04 | Q17 | sec_eavailw.tex EW7 | MOVED-OK + SUPPORTED | "establishes no X" = "does not establish X"; "across estimator settings": base sec_5d.tex:105 "The studies do not establish a bias--variance tradeoff across estimator settings"; accessor names at the B07-g-01 ledger home, HEAD `EVIDENCE-MAP-20261019.md:264` (`GetTrueExperimentersW`) and `:266` (`RecoW`). | none |
| chunk04 | Q19 | sec_eavailw.tex EW27 | REAL (minor) | base "The article distinguishes"; now "The analysis distinguishes". The same file renders base "as used by the article" (EW19) as "the companion journal article", so the subject changed from the article to the analysis. | pair 3 |
| chunk04 | Q21 | sec_eavailw.tex EW32 | SUPPORTED | base sec_joint.tex:342: "$\sigma_{c}$ is the standard deviation of the cell's result over NuWro's null distribution"; base app_provenance.tex:116 uses the same "null spread" with its "$0.2\,\sigma_c$ rule". | none |
| chunk04 | Q23 | sec_eavailw.tex EW44 | REAL | base "The largest cell, the corner ..., holds \SI{22}{\percent}" names the widest (catch-bin) cell, as the n4 ledger reads it ("the single widest overflow cell", map-doubtful.md:55). Now "holds the largest share", a ranking claim that no base text states. | restore base (pair 4) |
| chunk04 | Q24 | sec_eavailw.tex EW47 | SUPPORTED | base sec_5d item 4: "Seed shifts in central values are a small fraction of their uncertainty" (now sec_5d.tex:312); dropping "item~4" is pointer precision only. | none |
| chunk04 | Q26 | sec_eavailw.tex EW57 | SUPPORTED | base sec_3d.tex:115: "Each prediction is normalized by its own flux-averaged total CC cross section per nucleon"; flux-repaired becomes flux-corrected, wording only. | none |
| chunk04 | Q27 | sec_eavailw.tex EW61 | MOVED-OK | "none reaches the data" is in the subsection's first sentence, now sec_eavailw.tex:133: "All four external generators fall below the data in the high-$\Eavail$, high-$W$ corner."; "close to" now prints as "each generator's central-value corner ratio lies close to its integrated ratio" (EW68) with the 1--7% figure. | none |
| chunk04 | Q28 | sec_eavailw.tex EW68 | SUPPORTED + MOVED-OK | base EW67: "If GiBUU is instead supplied with the shares that GENIE and NuWro carry above this energy, data/GiBUU becomes about $1.37$ in the corner and $1.29$ integrated"; the energy-limit cause now prints as "GiBUU's larger contrast comes from its sample's energy limit". | none |
| chunk04 | Q29 | sec_eavailw.tex EW73 | SUPPORTED | base sec_5d item 1: "Estimator-seed sensitivity exceeds its limit. Companion covariances ... against the ... movement limit set before production"; "five-axis covariance": base sec_5d "The five-axis covariance used in this note"; the $\chi^2$ is base sec_fived16-gen. | none |
| chunk04 | Q31 | sec_eavailw.tex EW77 | REAL | the gloss "(the look-elsewhere effect)" is added; no base .tex file contains "look-elsewhere" or "trial(s) factor" (grep over all 48 base files). It is general knowledge, so the brief counts it as REAL. | delete gloss (pair 5) |
| chunk04 | Q32 | sec_5d.tex FD0 | RATER-WRONG | the new first sentence says the section "validates the five-dimensional estimator", so "the coverage test (\S\ref{sec:coverage-5d})" is the five-dimensional one; "validation test" to "test" follows from the same sentence. | none |
| chunk04 | Q34 | sec_5d.tex FD14 | MOVED-OK | flag name now in app_guide.tex:18: "\texttt{purity}, \texttt{negweight}, \texttt{negweight-refined}". | none |
| chunk04 | Q37 | sec_5d.tex FD28 | RATER-WRONG | "up to 74% in the worst cell" and "74% in the worst cell" state the same maximum. | none |
| chunk04 | Q39 | sec_5d.tex FD40 | SUPPORTED | base, end of the same paragraph: "The exclusions, definitions and numerical verification are in the binned response diagnostic record (Ref.~\cite{NoteRecords2026}, ...)" (still prints). | none |
| chunk04 | Q40 | sec_5d.tex FD49 | RATER-WRONG | the scope (binned, signal-only, noise-free, development truths, 144 residuals only) is kept whole and now attaches to the conclusion it limits, which the brief allows. The base's "comparison" and "diagnostic" are the same study, so "it establishes no impossibility" keeps the disclaimer. | none |
| chunk05 | Q1 | sec_5d.tex FD54 | SUPPORTED | base FD63: "This candidate is configuration (e), which gives the sixteen-cell result (\S\ref{sec:fived16})". | none |
| chunk05 | Q2 | sec_5d.tex FD59 | SUPPORTED | base FD56: "input perturbations within floating-point rounding move functionals by a median of 0.8 ...", which is what "this spread" refers to. | none |
| chunk05 | Q3 | sec_5d.tex FD63 | MOVED-OK | now in FD54: "A candidate with raised refinement capacity, configuration (e) of the sixteen-cell result (\S\ref{sec:fived16}), passes ...". | none |
| chunk05 | Q5 | sec_5d.tex FD70 | SUPPORTED | base label table: "$R$ & the raised-refinement-capacity estimator of \S\ref{sec:val-departure}". | none |
| chunk05 | Q6 | sec_5d.tex FD72 | MOVED-OK | the table now has sec_5d.tex:121 "J & 109 supported fine joint cells, subdividing all five axes", :122 "H2 & 27 supported coarser joint cells, also subdividing all five axes, not nested within J", and "EW & 39 supported $(\Eavail,W)$ cells". | none |
| chunk05 | Q7 | sec_5d.tex FD78 | SUPPORTED | base FD72: "Both joint partitions subdivide all five axes". | none |
| chunk05 | Q8 | sec_5d.tex FD84 | SUPPORTED | in the base the preceding sentences are about W3 ("W3's J-cell median absolute residual rises ..."), so "This persistence" is that of the W3 residual. | none |
| chunk05 | Q9 | sec_5d.tex FD88 | MOVED-OK | the verdict prints in the next paragraph: "None of the three reporting definitions can meet these precision targets with any estimator configuration the study's selection procedure permits within its computing budget." | none |
| chunk05 | Q10 | sec_5d.tex FD98 | SUPPORTED | in the same base paragraph the model-component medians are 12.0% (RD1) and 13.4% (RD3), against a total-width target of at most 10%, so the model component alone exceeds the target; RD2's 9.6% + 1.4% gives the 11.0%. | none |
| chunk05 | Q11 | sec_5d.tex FD114 | REAL (minor) | base "Coarser cells can have smaller residuals and spread ...; this is not an improvement in precision"; now "so their smaller residuals are not an improvement", which drops spread from the disclaimer. | pair 6 |
| chunk05 | Q12 | sec_5d.tex FD130 | REAL | base app_statmethods_nd.tex:37: "The rounding study keeps the fine-grid membership fixed under uniform input perturbations within half a float32 unit in the last place". The half-unit part is supported. "values on bin edges kept" is not: the base says fine-grid membership is kept, not that edge values are left unmoved. "every input coordinate" is also unstated. | gloss in base terms (pair 7) |
| chunk05 | Q13 | sec_5d.tex FD133 | RATER-WRONG | (control only) H2 and EW are defined as supported cells in the label table ("27 supported coarser joint cells", "39 supported ... cells"), and the 71% was already the J figure ("W3's J correlation"). | none |
| chunk05 | Q14 | sec_5d.tex FD149 | MOVED-OK | "10% lower rate, weak slope" now in sec_5d.tex:214: "under a 10\% reduction of the signal rate with a weak $\Eavail$ slope (below)". "accounts for the failure" is carried by the paragraph's body: "The miscoverage is a residual bias that the nominal-truth bias correction does not remove ... removing that bias restores coverage". | none |
| chunk05 | Q17 | sec_5d.tex FD173 | SUPPORTED | base Eq. zassembly applies $D(\sum_V C_b)D$ with $V$ the vertical bands and $D=\diag(g)$, so "the same information" is the inflation of the vertical bands, as the formula $\mathbf{G}\mathbf{C}^{\mathrm{vert}}\mathbf{G}$ shows. | none |
| chunk05 | Q20 | sec_5d.tex FD202 | SUPPORTED | base, end of item 2: "Within these limits, the failure ... is not the statistic's own resampling noise" and "Statistical noise must fall with $N$". | none |
| chunk05 | Q21 | sec_fived16.tex FV4 | SUPPORTED | base app_statmethods_nd.tex:25: "A cell is supported when both its expected reconstructed signal and selected truth weight at data exposure are at least 1000". | none |
| chunk05 | Q22 | sec_fived16.tex FV9 | SUPPORTED | "PPFX": base FV77 "\fvval{fb-universes} PPFX flux universes"; reweight versus shift: base sec_systematics.tex:281 "five detector bands using shifted reconstructed kinematics. MINOS efficiency and the three GEANT ... keep their weight-based treatment" and :278 (lateral bands = shifted observables). | none |
| chunk05 | Q23 | sec_fived16.tex FV12 | SUPPORTED | base FV68: "Each $C_{\mathrm{model}}$ vertex is a data shift unfolded with a prior reweighted by one generator's ratio to GENIE CV"; "statistical gate": base FV48 "fails the ratio's statistical gate"; base FV18: "$C_{\mathrm{resp}}$ ... summed over the four". | none |
| chunk05 | Q24 | sec_fived16.tex FV21 | MOVED-OK | now prints: "The median per-cell relative $\sigma$ of $C_{\mathrm{resp}}$ is \fvval{sigmed-C_resp}\%, and adding $C_{\mathrm{resp}}$ to $C_{\mathrm{total}}$ raises the per-cell $\sigma$ by a factor of \fvval{sigratio-min}--\fvval{sigratio-max} (median \fvval{sigratio-med})". | none |
| chunk05 | Q25 | sec_fived16.tex FV25 | MOVED-OK | the grading stays attached: the next sentences list exactly the 12 truths and give "A truth is listed as failing when $p<\fvval{trig-p}$ or when any cell has $|z|>\fvval{trig-z}$"; "deposit categories" is base FV18's "protons, mesons, electromagnetic deposits and other deposits". | none (optional: "\fvval{f0b-all-truths} tested truths") |
| chunk05 | Q26 | sec_fived16.tex FV29 | SUPPORTED | the dropped "so that ..." clause restates the first clause; "listed" means failing: base FV34 "truths are listed: [failures]" and FV36 "At the other ... truths the bias passes both criteria". | none |
| chunk05 | Q27 | sec_fived16.tex FV33 | MOVED-OK | the own-generator exclusion prints as a rule: "A truth from a $C_{\mathrm{model}}$ generator is compared with the covariance without that generator's shift." It is also marked per row in the table ($-$). "listed" = "fail" as in Q26. | none |
| chunk05 | Q28 | sec_fived16.tex FV36 | MOVED-OK + SUPPORTED | the criteria print in "A truth is listed as failing when ..."; "ungraded because the offset control failed" now prints as "the six power alternatives built on that correction are therefore descriptive and not judged against the failure criteria"; "four records" = 2 tunes x (mean, closure), base FV49; "One control check failed": values_fived16.tex:610 shows controls 0--6 and 8 passed. | none |
| chunk05 | Q32 | sec_fived16.tex FV62 | MOVED-OK | "reported" stays attached in the fake-data caption: "against the reported $C_{\mathrm{total}}+C_{\mathrm{resp}}$". | none |
| chunk05 | Q33 | sec_fived16.tex FV65 | MOVED-OK | now prints in the $C_{\mathrm{model}}$ paragraph: "in the GENIE CV and NuWro samples (which stop at $E_\nu=\fvval{gagg-range-max}$~GeV)". | none |
| chunk05 | Q34 | sec_fived16.tex FV68 | MOVED-OK | now prints: "the prior is reweighted in turn by the ratio of GENIE + MEC, NuWro or GiBUU to GENIE CV, and the data are unfolded again." | none |
| chunk05 | Q35 | sec_fived16.tex FV71 | SUPPORTED | the shrink method is base FV76 ("These are descriptive sensitivities of the reported $\chi^2$, not alternative results: one group's correlations are shrunk ..."); "fail" = "list" (base FV34/FV36). | none |
| chunk05 | Q36 | sec_fived16.tex FV76 | MOVED-OK | method now in FV71; the constraint weighting prints at $C_{\mathrm{e}}$: "the PPFX flux universes, weighted by the neutrino--electron and inverse-muon-decay constraint;". The flux sentence points to \S\ref{sec:fived16-cov}. | none |
| chunk05 | Q38 | sec_fived16.tex FV82 | SUPPORTED | base FV62 defines each prediction's matrix as $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$; an eigenmode of a matrix is its eigenvector. | none |
| chunk05 | Q39 | sec_joint.tex JT0 | SUPPORTED + MOVED-OK | "simulating the full analysis chain": base sec_joint.tex:14 "simulating the whole analysis chain at the hypothesis, so that the estimator's bias enters the simulated null distribution"; "in total and in shape": base total and shape statistics (e.g. :334); config (a) gloss: base sec_method.tex:96. "in the words of the test specification" goes with B10-8, which moved the verbatim conditions to the records: app_provenance.tex "with its six conditions verbatim". | none (see note) |
| chunk05 | Q40 | sec_joint.tex JT56 | SUPPORTED | base Table tab:joint5d pairs "claim $p$" with "Holm thr."; base caption of fig:joint5d-nulls: "the declared claim variant ... among those used in the decisions". | none |

**Counts (58):** REAL 7 (4 full, 3 minor), MOVED-OK 17, SUPPORTED 28, RATER-WRONG 6, UNSURE 0. Several rows are mixed (for example
"SUPPORTED + MOVED-OK"); each is counted under its first class.

**Note (outside my rows):** JT0's dropped "in the words of the test specification" is consistent with B10-8. That row turned the
base's verbatim conditions ("quoted below from the test specification, changed only in typesetting") into
paraphrase, with the verbatim text in the records. The paraphrased conditions themselves (JT101 onward) are not in my
range and should be triaged by whoever holds them, because the base disclosure that they were verbatim no longer prints.

## REAL rows: base text, new text, fix

Each old_str below was checked to occur exactly once in the current file.

1. **chunk04 Q1, sec_3d.tex TD74** (minor: "processed" lost).
   - base: "We generated and processed GENIE, NuWro and GiBUU samples, and extracted MINERvA Tune~v1 from analysis MC truth with its full tune weight."
   - new: "The GENIE, NuWro and GiBUU samples were generated for this analysis, and MINERvA Tune~v1 is the analysis simulation's truth with its full tune weight;"
   - old_str: `samples were generated for this analysis, and MINERvA Tune~v1 is the analysis simulation's truth with its full tune weight;`
   - new_str: `samples were generated and processed for this analysis, and MINERvA Tune~v1 was extracted from the analysis simulation's truth with its full tune weight;`
   - The ledger probe B06-26 must follow.

2. **chunk04 Q13, sec_3d.tex TD154/TD155** (added gloss narrows the unified throw).
   - base: "Nor is any ratio of the unified-throw to the block covariance." The base definitions are "all reweightable knob bands and the flux multisim" (sec_systematics.tex:156) and "every reweightable band and the flux multisim" (app_statmethods.tex:159, still printed).
   - new: "... a ratio of the covariance from simultaneous variation of all reweightable interaction-model bands and the flux universes (the unified throw of \S\ref{sec:uq-combine}) to the block covariance is reported."
   - old_str: `all reweightable interaction-model bands and the flux universes (the unified throw`
   - new_str: `every reweightable band and the flux multisim (the unified throw`
   - The ledger probe B06-43 must follow.

3. **chunk04 Q19, sec_eavailw.tex EW27** (subject changed from the article to the analysis).
   - base: "The article distinguishes the five classifier inputs, the lower-dimensional support they populate, and the five reported observables."
   - new: "The analysis distinguishes the five classifier inputs, ..."
   - old_str: `The analysis distinguishes the five classifier inputs`
   - new_str: `The companion journal article distinguishes the five classifier inputs`
   - This follows the file's own rendering of "the article" at EW19. The ledger probe B07-11 must follow.

4. **chunk04 Q23, sec_eavailw.tex EW44** (added ranking claim).
   - base: "The largest cell, the corner $\Eavail>\SI{3}{GeV}$, $W>\SI{3}{GeV}$, holds \SI{22}{\percent}."
   - new: "The corner cell $\Eavail>\SI{3}{GeV}$, $W>\SI{3}{GeV}$ holds the largest share, \SI{22}{\percent}."
   - old_str: `The corner cell $\Eavail>\SI{3}{GeV}$, $W>\SI{3}{GeV}$ holds the largest share, \SI{22}{\percent}.`
   - new_str: `The largest cell, the corner $\Eavail>\SI{3}{GeV}$, $W>\SI{3}{GeV}$, holds \SI{22}{\percent}.`
   - If the base meant the cell holding the most excess, its producer would show that; until then, restore. The ledger probe B07-17 must follow.

5. **chunk04 Q31, sec_eavailw.tex EW79** (gloss from general knowledge).
   - base: "... must account for any selection of the tested region using these data."
   - new: "... must account for any selection of the tested region made with these data (the look-elsewhere effect)."
   - old_str: `made with these data (the look-elsewhere effect).`
   - new_str: `made with these data.`
   - The ledger probe B07-30 must follow.

6. **chunk05 Q11, sec_5d.tex FD114** (minor: "spread" dropped from the disclaimer).
   - base: "Coarser cells can have smaller residuals and spread, but they estimate different integrals; this is not an improvement in precision on an unchanged quantity."
   - new: "..., so their smaller residuals are not an improvement in precision on an unchanged quantity."
   - old_str: `so their smaller residuals are not an improvement in precision on an unchanged quantity.`
   - new_str: `so their smaller residuals and spread are not an improvement in precision on an unchanged quantity.`
   - The ledger probe B08-29 must follow.

7. **chunk05 Q12, sec_5d.tex FD130** (gloss partly unsupported).
   - base: "Twenty edge-safe data jitters give ..." The only base definition is app_statmethods_nd.tex:37: "keeps the fine-grid membership fixed under uniform input perturbations within half a float32 unit in the last place".
   - new: "Twenty edge-safe data jitters (every input coordinate moved within half a single-precision rounding unit, values on bin edges kept) give ..."
   - old_str: `(every input coordinate moved within half a single-precision rounding unit, values on bin edges kept)`
   - new_str: `(uniform input perturbations within half a single-precision unit in the last place that keep the fine-grid membership fixed)`
   - The ledger probe B08-32 must follow.
