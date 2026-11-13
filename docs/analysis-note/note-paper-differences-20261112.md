# Note–Supplement paragraph differences, 2026-11-12

Review status: pending Grok review. This register implements Joseph's 2026-11-12 instruction to keep the note's prose and reconcile substantive differences only.

Comparison pins: note `6c83a597b4d95e5c327c7ba71c64d25b81a02ce0` before the clarifications below; methods-paper #977 `1ccb08c29f2153647a6fe117d53a2acb09e63905`, `docs/analysis-note/supplemental_body.tex`. Paragraph identifiers below are the Supplement's historical `% source:` identifiers, not the note's current paragraph numbers. The original mapping is recoverable at note `acf934d71fce0e4805615b9b9aceb4ea3bdae444`; later paragraph splits were followed through the complete original paragraph. Moved text was checked in its destination, rather than treated as a deletion.

For every row, the recorded reason for divergence is **“rewritten for the paper's style pass, 2026-11-12”**. Thirty-six source markers say DESYNCED; two earlier restyled source markers (selection paragraph 1 and fake-data paragraph 3) complete the 38-pair list. Those two markers retain their original 2026-11-09 dates; this register records the 2026-11-12 decision to keep the note's prose. Stylistic rewrites are not copied back.

| Note source | Label; historical paragraph | Number, scope and claim check / disposition |
|---|---|---|
| `sec_experiment.tex` | `sec:selection`; 0 | Same signal, phase space, fiducial geometry and nucleon count. |
| `sec_experiment.tex` | `sec:selection`; 1 | Same reconstructed selection and successful MINOS-fit requirement. |
| `sec_experiment.tex` | `sec:selection`; 2 | May-template routing and purity agree. Reconciled the 1A-only composition and inside/outside truth-vertex description; see A below. |
| `sec_eavailw.tex` | `sec:eavailw-definitions`; 2 | Same observable table, formulae, constants and conventions. |
| `sec_eavailw.tex` | `sec:eavailw-definitions`; 4 | Same truth-axis residuals, weighted bin migrations and no-real-solution fraction. |
| `sec_eavailw.tex` | `sec:eavailw-definitions`; 5 | Same dependence and unmeasured-information limits. Supplement adds a finite-capacity explanation without claiming measured information. |
| `sec_eavailw.tex` | `sec:eavailw-definitions`; 6 | Same negative-truth-W exclusion and generator-axis effects. Supplement separately quantifies reconstruction-window losses; no truth-cut count is equated with that loss. |
| `sec_3d.tex` | `sec:eavail-definition`; 0 | Same implemented available-energy formula, species contributions and calorimetric scale. |
| `sec_3d.tex` | `sec:eavail-definition`; 2 | Same inherited pion constant and first-order result. Supplement expands its comparison with published definitions; note retains its own provenance discussion. |
| `sec_method.tex` | `sec:method-binning`; 0 | Same grids, reported-bin mask and edge-list pointers. |
| `sec_method.tex` | `sec:method-binning`; 1 | Same reconstruction-window exclusion and recovery of the corresponding in-sample truth events as misses. |
| `sec_fived16.tex` | `sec:fived16-result`; 0 | Same cells, support rule, merge and low-diagonal-fraction values; “stability” and “diagonal fraction” have the same stated definition. |
| `sec_fived16.tex` | `sec:fived16-result`; 1 | Same sixteen-cell cross sections, uncertainties and boxes. Supplement-only CSV packaging is separate context. |
| `sec_method.tex` | `sec:method-algo`; 1 | Same two-step algorithm. Supplement explicitly names the initial push weight and the push/pull product already implicit in the note. |
| `sec_method.tex` | `sec:method-algo`; 2 | Same configuration-(e) final-weight ESS scope. Supplement moves the details to its diagnostics section; note retains its citation and uncertainty/coverage/validity exclusions. |
| `sec_method.tex` | `sec:method-config`; 5 | The six learner and background-treatment roles and the selection timing agree. The note's configuration-(a) assignments also include the three- and four-observable closures and figures eavail-marg and q3excess. The Supplement's configuration table and S4.5 do not assign those closures or figures. Both assign the regenerated 3D and 4D central values to (e). The Supplement moves history to S4.5 and uses a table. The note keeps its list and table. |
| `sec_method.tex` | `sec:method-algo`; 3 | Same combined template and binwise purity formula; no separate subtraction or general genuine-background fraction is inferred. |
| `app_negweight.tex` | `app:negweight`; 1 | Qualified the pre-histogram binning statement to the purity configurations; see B. |
| `app_negweight.tex` | `app:negweight`; 4 | Same density-ratio formulae and distinction between bin integrals and continuous shape. rho/phi is local notation only. |
| `app_negweight.tex` | `app:negweight`; 5 | Same floor, positivity restriction, refinement and classifier-dependence limit. |
| `app_negweight.tex` | `app:negweight`; 36 | Scoped the absence of a coverage test to the historical refinement study; see B. The note limits the real-data comparison to method sensitivity and excludes interpreting it as a measured bias. The Supplement omits the qualifier "measured" from its bias exclusion. The note's statement about failure to follow generator-sized E_avail shape changes concerns this study's F2 estimator. The Supplement adds "cell by cell" and points to the reported estimator in supp:recovery, a different object. |
| `sec_method.tex` | `sec:method-config`; 7 | The a-priori settings are the two OmniFold classifiers and the missed-event regressor. Five iterations stay under the rule in sec:gbdt-model-dependence. The 400-tree, 31-leaf refinement was selected before the joint-test design was fixed (sec:joint5d). See C. |
| `sec_method.tex` | `sec:method-config`; 8 | Same iteration counts and exact-split movement. Note retains its stronger explicit limits: one diagnostic is not convergence of every functional, and reproduction is not an iteration test. |
| `sec_fived16.tex` | `sec:fived16-cov`; 0 | Same reported block sum, components, refit/jitter bootstrap and zero measured seed block. |
| `sec_fived16.tex` | `sec:fived16-cov`; 1 | Disambiguated fractional and cross-section covariance symbols, including fractional-trace shares; see D. Carbon ratios remain the reported construction. |
| `sec_fived16.tex` | `sec:fived16-cov`; 3 | Same response construction and exclusions. Supplement prints the category scale constants that the note describes generically; checked against build_cresp.py, with no conflicting value. |
| `sec_fived16.tex` | `sec:fived16-cov`; 5 | Same correlation matrix and route to reconstructing the reported covariance. |
| `sec_fived16.tex` | `sec:fived16-cov`; 7 | Same inversion dimensions, shape construction, mixed-block normalizations and absence of an ensemble correction. Supplement adds a matrix identity and construction table; no new note diagnostic. |
| `sec_fived16.tex` | `sec:fived16-pl`; 0 | The period offsets are exchangeable draws with a common variance. The existing interval is the chi-squared interval at the Satterthwaite degrees of freedom of the exposure-weighted spread. It depends only on the exposure shares and is not a coverage or calibration of the block. See E. |
| `sec_fived16.tex` | `sec:fived16-pl`; 1 | Same playlist statistic, partition counts, exchangeability limit and descriptive comparisons. |
| `sec_fived16.tex` | `sec:fived16-pl`; 3 | Same post-observation block choice, preceding audit and unchanged comparisons. |
| `sec_systematics.tex` | `sec:uq-combine`; 0 | Same block sum, independence/linearity assumptions, unified-throw construction and unreported two-dimensional comparison/mean-shift norm. |
| `sec_systematics.tex` | `sec:uq-combine`; 2 | Same unexplained period inconsistency and limits on interpreting its assigned block. |
| `sec_systematics.tex` | `sec:uq-combine`; 3 | Same exposure-weighted construction, rank, reported sizes and reference-period sensitivity. |
| `sec_systematics.tex` | `sec:uq-combine`; 5 | Same retained noise, conditional containment, lack of a coverage test and sensitivity-only chi-squared values. |
| `sec_fived16.tex` | `sec:fived16-fd`; 0 | Same truth families, estimator, leave-one-generator-out rule, fixed criteria and lack of held-out/detector-response validation. |
| `sec_fived16.tex` | `sec:fived16-fd`; 3 | Same separately graded groups and outcome counts. Note keeps Gaussian reference counts explicitly as context; Supplement omits those references. |
| `sec_fived16.tex` | `sec:fived16-fd`; 6 | Same held-out tunes, shape construction, pseudo-experiment/closure records, pulls and covariance dependence. Note keeps contextual Gaussian references and their dependence warning. |

The four other source-marked blocks were checked as controls: `sec:eavailw-definitions` paragraphs 1 and 3, and `sec:fived16-cov` paragraphs 4 and 6. Their definitions, reconstruction clamp and covariance-table entries agree; punctuation, reference formatting and adjacent Supplement-only headings do not change their claims. The shared `values_fived16.tex` keys used by the 42 note blocks were compared: 609 are present in both pinned sources. No shared numeric value differs. The two tune-name differences wrap the same strings in `\mbox{...}` in the Supplement.

## Substantive clarifications

A. **Background composition.** `sec_experiment.tex`, `sec:selection`: the template is the May combined template, 2.91 percent over the full sample and 2.72–3.23 percent by playlist. Its 1A-only weighted composition is about 10 percent out-of-phase-space signal with a true vertex inside the fiducial volume; the remainder is genuine background, mostly muon-neutrino charged-current events outside it. Both components enter the subtracted template, and the template's bin sum enters the purity weight. The last clarification makes the 1A scope part of the fraction's sentence and specifies the inside vertex. Evidence: #977 `06ac37c1935a56bba9623ba6d8b15e30ae9f00fe`, `docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/cbkg2-20261112/README.md` and `members/cbkg2_summary.json`; the README traces the actual MAT fiducial inequalities. No full-sample composition or general genuine-background fraction is asserted.

B. **Purity and historical refinement scope.** `app_negweight.tex`: the binning-only statement applies to configurations (a)–(c); the unbinned treatments already described in the appendix are separate constructions. The no-coverage-test statement refers to that historical refinement study. Evidence: the note's `tab:estimators-matrix` and `OUTCOME-20260925-s5n-stage1-development-fail.md`, especially its NOT CITABLE FOR and “no validation seed” statements. This does not retract or import any later coverage result.

C. **Settings chosen a priori.** `sec_method.tex`, `sec:method-config`: the two OmniFold classifiers and the missed-event regressor were fixed a priori. No hyperparameter search was performed on data. The joint-test estimator keeps five iterations under the rule in `sec:gbdt-model-dependence`. Its refinement classifier, 400 trees and 31 leaves, was selected before the joint-test design was fixed (`sec:joint5d`). The nominal 100-tree, learning-rate 0.1, depth-3 settings stay. No configuration, result assignment or printed number changes.

D. **Covariance units.** `sec_fived16.tex`, `sec:fived16-cov`: the outer products of relative generator shifts define the fractional matrix. Multiplication by the diagonal of the cell-integrated cross sections gives the absolute matrix used in the reported block sum. Distinct fractional/absolute symbols make the sum and the fractional-trace shares consistent. Evidence: `nd-unfolding/pv-ladder/build_cmodel5d.py`'s construction and `nd-unfolding/s1_assemble.py`, `model_abs` and the `C_model_frac`/`C_model_abs` output keys. The matrices and all printed values remain unchanged. The reported generator ratios remain carbon ratios; the note's CH sensitivity and the paper's withholding remain as recorded in the existing B5/V-PRIOR alignment ledger.

E. **Period-size interval.** `sec_fived16.tex`, `sec:fived16-pl`: the period offsets are treated as exchangeable draws with a common variance. The 68 percent interval on the ratio of the block's true sigma to its estimated sigma is the chi-squared interval at the Satterthwaite degrees of freedom of the exposure-weighted spread. It depends only on the exposure shares. It is not a coverage or calibration of the block. The endpoints are unchanged. Evidence: `2d-closeout/playlist-term/DESIGN.md` section 2 and `FD-CT-5B-AUDIT-DECLARATION.md` sections 4.4 and 5.1.

The remaining differences are wording, notation, relocation, explicit definitions, or deliberately different amounts of context. Added Supplement explanations of finite classifier capacity, particle-species definitions, scale constants, matrix identities, CSV packaging and diagnostics are not copied into the note. Existing note qualifications, including its iteration-test limits and contextual Gaussian references, are retained. No shared reported number was reconciled by changing its value.

## Boundaries retained

S8.6's stopped-test diagnostics remain in the Supplement. None is moved into the note by this comparison. This register changes no release label, external-document label, AUD-N4/N5 disposition or note-role wording, and authorizes no release, merge, submission or scientific computation.

## Clarification commits

- `e381b6cd7d841879ce1a8745782ac52d6aeadc68`: playlist 1A template composition. Passed.
- `3925864482954bbe32f9ea217d29fea5a1e37cf6`: learner-selection scope. Held. Forward correction `0b920ac79fbc0d16d4158e8e0cc056224422395c`.
- `5a5582f3750379c04baf5c59f0ca1b751691fc5d`: covariance units and interval assumptions. Held. The covariance-unit sentences stay. The period-interval sentences are corrected by `a4625238c5b099e429d5ba333b54128961cf71ba`.
- `3d2f0d0dc08c8d6fdc5dbdecf50b22913ffc09ad`: purity and refinement study scope. Passed.
