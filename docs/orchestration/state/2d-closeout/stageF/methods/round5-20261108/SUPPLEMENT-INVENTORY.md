# Round 5: the paper's pointers into the analysis note, and what moved to the Supplemental Material (2026-11-08)

**Why.** All eight round-4 referee reads (`../secondary-results/referee-methods-round4-20261106/`) say the paper
relies on the note (Ref. [14]) for what a reader needs to judge it. They name the support rule, the model-term
construction, the IBU configuration, the null calibration, the test statistics, the coverage test design, the
estimator names, the cell cuts R00–R15 and the correlation matrix. Joseph asked (2026-11-08) for referee rounds on
the paper, the Supplement and the note.

**The inventory.** `docs/analysis-note/paper_body.tex` at the branch's merge `23891b39` held 48 pointers into the
note: 40 `\nsec`/`\napp` and 8 plain `\cite{AnalysisNote2026}` (the two macro definitions not counted). Each is
classed:
- **E**, essential to judge a claim in the paper. It now points to the Supplemental Material
  (`main_supplement.tex`, `supplemental_body.tex`).
- **D**, a detail the reader may skip. It stays a pointer to the note.

Line numbers are at `23891b39`. The numbering of the Supplement's sections is checked by
`docs/analysis-note/check_supp_pointers.py`.

| # | line | pointer (note target) | what the paper says there | class | now |
|---|---|---|---|---|---|
| P01 | 58 | `\cite` (the note, general) | the note gives the full record | D | kept; a sentence before it now names the Supplement |
| P02 | 75 | sec:eavail-definition | the E_avail definition | **E** | S2 |
| P03 | 79 | `\cite`, sec:eavail-definition, sec:eavailw-definitions | "the definitions are detailed in" | **E** | S2 |
| P04 | 81 | `\cite`, sec:eavailw-axis, sec:eavailw-gen… | the carbon/CH target difference | D | kept |
| P05 | 84 | sec:joint5d-design | the support rule and the coarse grid | **E** | S7 |
| P06 | 91 | app:negweight | the negative-weight background treatment | **E** | S4 |
| P07 | 93 | sec:joint5d | the joint-test estimator's name and its tests | **E** | S7 |
| P08 | 93 | sec:val-negweight | the estimator removes most of the purity bias | D | kept |
| P09 | 93 | sec:method-config | the other configurations used | **E** | S4 |
| P10 | 95 | sec:method-config | the iteration check on data | D | kept |
| P11 | 95 | sec:method-algo | the training details | **E** | S4 |
| P12 | 98 | sec:gbdt-model-dependence | a capacity measure on 27 joint cells | D | kept |
| P13 | 105 | sec:gbdt-model-dependence | other reporting definitions | D | kept |
| P14 | 118 | sec:fived16-cov | C_model is not a calibrated bound | **E** | S5 |
| P15 | 118 | sec:fived16-pl | the playlist offsets (the run-period block) | **E** | S5 |
| P16 | 118 | sec:fived16-pl | tests given with and without the block | D | kept |
| P17 | 125 | sec:fived16-cov | each block's ensemble and normalization | **E** | S5 |
| P18 | 142 | sec:val-negweight | a figure caption's nominal residual | D | kept |
| P19 | 142 | sec:eavailw-adopted | a figure caption's earlier band | D | kept |
| P20 | 151 | sec:results-tension | the 2D leading modes | D | kept |
| P21 | 156 | sec:results-tension | the 2D χ²/ndf by estimator | D | kept |
| P22 | 156 | app sec:tension | ten iterations against five | D | kept |
| P23 | 156 | sec:method-config | the exact-split difference | D | kept |
| P24 | 187 | `\cite`, sec:results-uq, sec:uq-combine, sec:uq-2d-scope | the 2D covariance details | **E** (uq-combine) | S6; results-uq and uq-2d-scope stay in the note |
| P25 | 208 | sec:fived16-quadrants | the 3D marginal agreement | D | kept |
| P26 | 212 | sec:val-departure | a nominal closure | D | kept |
| P27 | 212 | sec:val-negweight | background closures | D | kept |
| P28 | 212 | app sec:negweight-footing | background closures | D | kept |
| P29 | 218 | sec:val-departure | the departure diagnosis | D | kept |
| P30 | 218 | sec:eavailw-adopted | the earlier covariance | D | kept |
| P31 | 218 | `\cite`, sec:val-negweight, sec:val-departure | the studies' scope and seed sets | D | kept |
| P32 | 223 | sec:coverage-5d | an earlier 5D coverage result | D | kept |
| P33 | 230 | `\cite` | the rounding spread on the joint cells | D | kept |
| P34 | 230 | `\cite` | the stability probe found no variant | D | kept |
| P35 | 280 | app:response-mismatch | response-mismatch closures | D | kept |
| P36 | 282 | sec:fived16-fd | gate D compares unlike objects | D | kept (the gate's design paragraph was not copied; see the note list) |
| P37 | 318 | sec:gbdt-model-dependence | the prior-reweighting shift | D | kept |
| P38 | 318 | sec:joint5d-results | the tests' bias toward the prior | D | kept |
| P39 | 334 | `\cite`, sec:fived16-cov, sec:fived16-pl, sec:uq-combine | the limitation sentence on C_model's coverage and the run-period blocks | **E** | S5 and S6 |
| P40 | 334 | sec:coverage | the 2D fixed-truth coverage test | **E** | S9 |
| P41 | 339 | sec:joint5d-conditions | the conditions of the joint tests | **E** | S7 |
| P42 | 353 | `\cite`, tab:fived16-cells | the uncertainties without C_PL,5D | **E** | Table S2 |
| P43 | 356 | sec:method-binning | the outer edge of the analysis grid | **E** | S3 |
| P44 | 462 | sec:joint5d-ch | NuWro's flagged supplement | D | kept |
| P45 | 465 | sec:joint5d-ch | GiBUU's free-proton sample | D | kept |
| P46 | 470 | sec:fived16-gen-target | the CH correction's dependence | D | kept |
| P47 | 475 | sec:fived16-gen-target | a table caption | D | kept |
| P48 | 492 | sec:fived16-gen | the flux-universe bands | D | kept |

**Totals.** 16 pointers moved to the Supplement (P24 in part). 32 stay with the note. One new pointer was added:
Sec. ibu → S8, for the IBU configuration, the statistic T and its null. These definitions live in REF-G1's and
REF-C2C1's declarations, not in the note.

**The Supplement's sections**, each copied from the note's own text by `seed_supplemental_body.py` (one-time
extraction; `supplemental_body.tex` names each block's source):

| | section | from |
|---|---|---|
| S1 | Signal definition and event selection | sec:selection |
| S2 | The five observables | sec:eavailw-definitions, sec:eavail-definition |
| S3 | Binning and the sixteen reporting cells | sec:method-binning, sec:fived16-result (Table S2), plus the CSV files' description |
| S4 | Algorithm, background treatment and estimator configurations | sec:method-algo, sec:method-config, app:negweight |
| S5 | The reported five-observable covariance | sec:fived16-cov (Tables S4, S5), sec:fived16-pl |
| S6 | The two-dimensional covariance | sec:uq-combine |
| S7 | Joint tests: grid, support rule, statistics, calibration and conditions | sec:joint5d-design, sec:joint5d-calibration, sec:joint5d-conditions |
| S8 | Comparisons with binned iterative Bayesian unfolding | new text from REF-G1-DECLARATION.md @ 49d82424 and REF-C2C1-DECLARATION.md @ c2ec419a |
| S9 | Designs of the coverage and fake-data tests | sec:coverage, sec:fived16-fd |

**Open (TODO):**
- **A correlation heatmap for the main text.** No producer exists for the 16-cell matrix; `uq_corr_2d.pdf` is the 2D
  one. The paper's Table `tab:corr16` stays until one is written from the pinned `xsec16_covariance.csv`.
- **Trim.** The Supplement is copied, so it is long (about 10,100 words blinded). The referee round should say what
  can go.
- **Self-containment.** Two copied sentences cited the internal records document (not posted). They now point to the
  note's section instead.

Nothing is submitted, deposited or tagged. No wording is approved.
