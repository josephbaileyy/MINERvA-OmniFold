# REPORT W: product-scoping edits (five-observable integration PR, item 4), 2026-10-27

**Copy:** `S/5d/W/repo/docs/analysis-note/`, against base `S/5d/base` (main `8b0f83fd`).
**Edit script:** `edits_W.py`, 71 exact-string edits over 15 files, each of which must occur exactly once.
**Generated deliverables:** `ledger-W.md` and `changes-W.md` (`make_ledger_W.py`); the site table below (`make_report_W.py`); `abstract-proposals.md`.

**Untouched:**
- main_note.tex, main_paper.tex and app_release.tex;
- values*.tex, app_history.tex and the records files;
- the stubs and FIVED16 blocks;
- sec_fived16.tex.

**Products named:**
- **"the configuration-(a) five-dimensional central value"**, and **"the five-axis covariance of the configuration-(a) central value"** (in the paper, "its five-observable covariance" or "the covariance of Sec. V D");
- **"the sixteen-cell result"**, with a pointer: `\S\ref{sec:fived16}` and its subsections in the note; `Sec.~\ref{sec:result16}` or `\ref{sec:gen16}` in the paper.

## Counts by disposition (the 134 non-FINE sites of scope-sites.tsv)

| verdict | changed | left | hands-off | total |
|---|---|---|---|---|
| FALSE-ONCE-PRINTED | 29 | 0 | 4 (main_note 82, 89, 100; main_paper 44) | 33 |
| AMBIGUOUS | 49 | 39 | 13 (main_note ×6, main_paper ×2, app_release ×5) | 101 |

**Ledger:** 74 rows.
- 73 changed base sentences, as `--list` reports them. This includes PB235, the integrator's stub insertion, recorded as row S1 with disposition STUB.
- 1 insertion row: AMB151, the paper's Scope sentence.

## Rulings applied

- **Group C** (sites 51, 76, 112, 163, 178; ledger C1–C5):
  - each statement is scoped to "no uncertainty quoted for the configuration-(a) central value";
  - for the sixteen-cell result, the sentence says the model term of the reported covariance "is the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU)";
  - it points to `sec:fived16-cov` and `sec:fived16-fd` (in the paper, `sec:result16`);
  - it never says that C_model or the reported covariance includes, covers, accounts for or omits the bias. A scan of every new string confirms this.
- **Group E** (sites 84, 114; ledger E1, E2):
  - "none of [the precision study's] reporting definitions (RD1–RD3) met a precision target";
  - the sixteen-cell result is "the same H2 grid after a purity merge of its supported boxes, with total uncertainties";
  - pointer `sec:fived16-result`. No count and no σ.
- **No coverage claim:**
  - no new text calls the sixteen-cell intervals validated or says they have coverage;
  - four sites carry the absence form "total uncertainties, whose coverage is not validated": IN-3, SU-4, and PB-4 and PB-14 in the paper's Scope and Limitations.
- **Stage G** (sites 24, 66, 117, 168; ledger G1–G4):
  - each is scoped to the configuration-(a) covariance;
  - each points to `sec:fived16-gen`, or to `sec:gen16` in the paper.
- **Facts checked beyond the brief:**
  - **ME-5:** "a refined five-dimensional data unfold exists (configuration (e)); it gives the sixteen-cell result". Its sources:
    - `nd-unfolding/pv-ladder/build_cmodel5d.py:9-10` (x = P5's integrals on the reporting cells);
    - the sec_method.tex:104 comment ("P5, the s5p data unfold, is configuration (e)").
  - **FD-3, FD-6, VA-2:** "quoted total uncertainty" = the configuration-(a) covariance's (Eavail,W) projection. Its sources:
    - `OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:82` ("within the adopted C_EW σ");
    - `OUTCOME-20260925-s5c-…:100-103` (bias_vs_adopted).
  - **FD-7:** "this candidate is configuration (e)". Source: `records_estimators.tex:16` (e = s5e candidate R).
<!-- absence-ok: quotes or summarizes the note's printed text, before or after this PR, as the writer's record; not a new absence claim -->

## Site dispositions

| site | file:line | verdict | quote (start) | disposition |
|---|---|---|---|---|
| 1 | main_note.tex:63 | AMB | three-, four-, and five-observable MINERvA unfolds, each of which pass … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 2 | main_note.tex:72 | AMB | the regularization bias is largest in this region | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 3 | main_note.tex:82 | FALSE | The five-dimensional central value and its covariance use the purity s … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 4 | main_note.tex:83 | AMB | the central value keeps its bias of up to 4\% in the highest-$W$ cells … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 5 | main_note.tex:87 | AMB | No full five-dimensional comparison of the two background treatments h … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 6 | main_note.tex:89 | FALSE | The negative-weight treatment is used for the two-, three- and four-di … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 7 | main_note.tex:100 | FALSE | a residual bias, interpreted as regularization bias, that no quoted un … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 8 | main_note.tex:103 | AMB | Statistical intervals miscover at the tested truths | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 9 | main_note.tex:104 | AMB | none of the tested reporting definitions satisfies the predeclared 10\ … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 10 | main_paper.tex:44 | FALSE | it yields central values only, whose normalizations agree with lower-d … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 11 | main_paper.tex:44 | AMB | Pseudo-experiments measure a background-subtraction bias, a partial re … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 12 | main_paper.tex:44 | AMB | With a model-dependence envelope added linearly to the uncertainty, no … | hands-off: Joseph's abstract (proposal in abstract-proposals.md) |
| 15 | sec_execsummary.tex:58 | AMB | The high-$\Eavail$, high-$W$ region carries the largest regularization … | changed: ES-1 (ledger AMB15) |
| 17 | sec_execsummary.tex:111 | AMB | the five-dimensional estimator's regularization bias (\S\ref{sec:val-d … | changed: ES-3 (ledger AMB17) |
| 18 | sec_execsummary.tex:111 | AMB | five-dimensional intervals and their coverage (\S\ref{sec:gbdt-model-d … | left: the limitation it points to (no frequentist coverage claimed for any 5D interval, sec:coverage-5d) holds for the sixteen-cell result too; its fake-data study is NOT CITABLE FOR coverage |
| 19 | sec_execsummary.tex:111 | AMB | the five-dimensional covariance (\S\ref{sec:eavailw-adopted}); the cal … | changed: ES-3 (ledger AMB17) |
| 20 | result_status_rows.tex:25 | FALSE | 5D: LightGBM, five iterations, purity subtraction | changed: RS-1 (ledger A1) |
| 21 | result_status_rows.tex:25 | FALSE | One scalar-5D covariance, used although it has not met the validation  … | changed: RS-1 (ledger A1) |
| 22 | result_status_rows.tex:25 | AMB | No validated total-interval coverage. | left: the row is now scoped by its rsA ('purity subtraction (configuration (a))'), and the sixteen-cell result has its own row (RS-2) |
| 23 | result_status_rows.tex:25 | AMB | Central-value comparisons; the covariance's four measured limitations  … | left: 'the covariance' is the rsB of the same row, now named (RS-1) |
| 24 | result_status_rows.tex:25 | AMB | No covariance-based generator significance. | changed: RS-1, RS-2 (ledger A1, G1) |
| 27 | sec_intro.tex:28 | FALSE | Background subtraction is unbinned too in the 2D result and its covari … | changed: IN-1 (ledger A2, B1) |
| 28 | sec_intro.tex:28 | FALSE | The five-dimensional central value and its covariance, and the extende … | changed: IN-1 (ledger A2, B1) |
| 29 | sec_intro.tex:35 | AMB | The validation and uncertainty of the five-dimensional estimator (\S\r … | changed: IN-2 (ledger L2) |
| 30 | sec_intro.tex:37 | AMB | Above two dimensions the results are central values without intervals  … | changed: IN-3 (ledger AMB30) |
| 31 | sec_intro.tex:66 | AMB | Five-axis validation, model dependence, 5D coverage | left: the fake-data study is not a coverage test, so '5D coverage' still names one study; the sixteen-cell chapter has its own roadmap row (IN-4) |
| 32 | sec_intro.tex:67 | AMB | The five-axis covariance used in this note | changed: IN-4 (ledger F1) |
| 33 | sec_method.tex:28 | FALSE | every other quoted cross section and uncertainty, including the 5D cen … | changed: ME-1, ME-2 (ledger A3, B2) |
| 34 | sec_method.tex:96 | AMB | the same learner with purity-based background subtraction (\S\ref{sec: … | left: it sits inside item (a) of the configuration list, with a pointer to sec:eavailw; item (e) now names the sixteen-cell result (ME-3) |
| 35 | sec_method.tex:97 | FALSE | It gives the 3D and 4D central values (\S\ref{sec:3d}). | changed: ME-3 (ledger B3) |
| 36 | sec_method.tex:97 | FALSE | It is used for the generator tests (\S\ref{sec:joint5d}), the study of … | changed: ME-3 (ledger B3) |
| 37 | sec_method.tex:100 | FALSE | The five-dimensional central value and its covariance use configuratio … | changed: ME-4 (ledger A4) |
| 38 | sec_method.tex:100 | FALSE | A refined five-dimensional data unfold exists (configuration~(e)), but … | changed: ME-5 (ledger B4) |
| 39 | sec_method.tex:126 | FALSE | five-observable central value and covariance (\S\ref{sec:eavailw-adopt … | changed: ME-6 (ledger A5) |
| 40 | sec_method.tex:138 | FALSE | three- and four-observable central values (\S\ref{sec:3d}); generator  … | changed: ME-7 (ledger A5) |
| 41 | sec_systematics.tex:156 | AMB | The 5D result uses the strict joint ensemble and matched-endpoint comp … | changed: SY-1 (ledger AMB41) |
| 42 | sec_systematics.tex:159 | AMB | In the five-axis covariance the per-source decomposition is retained f … | changed: SY-2 (ledger AMB42) |
| 43 | sec_systematics.tex:278 | AMB | the re-selected event loops supply the lateral-band block of the five- … | changed: SY-3 (ledger AMB43) |
| 44 | sec_systematics.tex:278 | AMB | higher-dimensional products built from the single-pass shifted observa … | left, needs a fact: whether the sixteen-cell covariance's lateral bands came from re-selected or single-pass event loops was not checked (TSV 'why'); without it, the universal can be neither kept nor scoped truthfully |
| 45 | sec_systematics.tex:282 | AMB | The ML term $C_{\mathrm{ML}}$ of the five-axis covariance used in this … | changed: SY-4 (ledger AMB45) |
| 46 | sec_systematics.tex:297 | AMB | The five-axis covariance used in this note is a separate, later build | changed: SY-5 (ledger AMB46) |
| 48 | sec_systematics.tex:302 | AMB | the covariance \emph{used in this note} by \SI{0.18}{\percent} | changed: SY-6 (ledger AMB48) |
| 49 | sec_systematics.tex:302 | AMB | the 5D covariance is not transferred to them | changed: SY-6, SY-7 (ledger AMB48, AMB49) |
| 50 | sec_validation.tex:39 | AMB | The five-dimensional estimator, including its background subtraction,  … | left: a pointer to where the 5D validation tests are; it stays true for each configuration they test, and the sixteen-cell study has its own section |
| 51 | sec_validation.tex:108 | FALSE | up to \SI{74}{\percent} at highest $W$; regularization bias outside ev … | changed: VA-1 (ledger C2) |
| 52 | sec_validation.tex:113 | AMB | within total uncertainty in 20 of 42 $(\Eavail,W)$ cells | changed: VA-2 (ledger C2) |
| 53 | sec_validation.tex:129 | AMB | the generator-shaped tests, which remain the main five-dimensional rec … | changed: VA-3 (ledger AMB53) |
| 57 | sec_3d.tex:42 | AMB | This effect has not been assessed against the projection of the five-d … | changed: TD-1 (ledger AMB57) |
| 59 | sec_eavailw.tex:5 | AMB | The qualifications of the covariance are given in \S\ref{sec:eavailw-a … | left: local to sec:eavailw, whose product is named at the same paragraph ('in configuration~(a)') |
| 60 | sec_eavailw.tex:5 | AMB | which establishes no bias--variance tradeoff and no new total uncertai … | left: already scoped by 'for this projection' |
| 62 | sec_eavailw.tex:18 | AMB | The five-dimensional unfolding in $(\pT,\pPar,\Eavail,q_{3},W)$ passes … | changed: EW-1 (ledger AMB62) |
| 63 | sec_eavailw.tex:100 | AMB | shows the unfolded five-dimensional result projected onto $(\Eavail,W) … | left: local to sec:eavailw (the configuration-(a) map, named in its opening paragraph) |
| 64 | sec_eavailw.tex:105 | AMB | the regularization bias of Sec.~\ref{sec:5d} is largest at high $\Eava … | left: already scoped by its pointer ('the regularization bias of Sec.~\ref{sec:5d}') |
| 66 | sec_eavailw.tex:129 | AMB | no compatibility metric is quoted, for the reason given in \S\ref{sec: … | changed: EW-2 (ledger G3) |
| 67 | sec_5d.tex:4 | AMB | the validation of the five-dimensional estimator behind the central va … | left: the estimator 'behind the central values of §§3d–eavailw' is the pre-existing (a)/(e) mix; the sentence stays true for those central values, and the next sentence now names the sixteen-cell chapter (FD-1) |
| 68 | sec_5d.tex:4 | AMB | model dependence and the reporting definitions it rules out (\S\ref{se … | left: the fake-data study is not a coverage test (NOT CITABLE FOR coverage), so 'the five-dimensional coverage test' is still unique |
| 69 | sec_5d.tex:4 | FALSE | the status of the one five-axis covariance used in this note | changed: FD-1 (ledger F3, L3) |
| 70 | sec_5d.tex:36 | AMB | Shapes held out of development (e) | left: a row label; its criterion cell now names the configuration-(a) total (FD-2) |
| 71 | sec_5d.tex:37 | AMB | compared with the quoted total $\sigma$ | changed: FD-2 (ledger AMB71) |
| 72 | sec_5d.tex:51 | AMB | Relative to these cells' quoted total uncertainty, the bias is 0.36--1 … | changed: FD-3 (ledger AMB72) |
| 73 | sec_5d.tex:51 | AMB | It comes from the purity-based subtraction (\S\ref{app:negweight}), en … | left: literally true; the bias belongs to purity subtraction, which the sixteen-cell result does not use |
| 74 | sec_5d.tex:51 | FALSE | Negative-weight subtraction is not used for the quoted five-dimensiona … | changed: FD-4 (ledger A6) |
| 75 | sec_5d.tex:61 | AMB | not of the background treatment (status in the quoted uncertainties: \ … | left: a pointer to where the status is stated; sec:val-departure now states it per product (FD-5) |
| 76 | sec_5d.tex:77 | FALSE | The $\Eavail$ and $q_3$ residuals, a regularization (unfolding-model)  … | changed: FD-5 (ledger C3) |
| 77 | sec_5d.tex:90 | AMB | A candidate with raised refinement capacity passes the nominal backgro … | left: local naming of estimator R, defined in the label table (sec_5d:126); FD-7 now says this candidate is configuration (e) |
| 78 | sec_5d.tex:90 | AMB | about \SI{37}{\percent} of the bootstrap variance and below a tenth of … | left, needs a fact: 'below a tenth of any total uncertainty' compares a per-J-cell spread with totals on other cells; the TSV's 0.23 % vs a 4.14 % minimum is not a readout-probed comparison on the same cells |
| 79 | sec_5d.tex:95 | AMB | For historical shapes held out while this candidate was assessed | left: local naming ('this candidate'); FD-7 identifies it as configuration (e) |
| 80 | sec_5d.tex:95 | AMB | within the quoted total uncertainty in 20 of the 42 $(\Eavail,W)$ cell … | changed: FD-6 (ledger AMB80) |
| 81 | sec_5d.tex:95 | FALSE | No estimator or uncertainty from this assessment is used for the quote … | changed: FD-7 (ledger B5) |
| 82 | sec_5d.tex:113 | AMB | 27 supported coarser joint cells (H2) and 39 supported $(\Eavail,W)$ c … | left: H2 is the precision study's 27-cell grid; the Group E ruling keeps it ('the same H2 grid after a purity merge'), and §4 item 3 routes the H2 relation to the 5D session |
| 83 | sec_5d.tex:122 | AMB | H2 & 27 supported coarser joint cells, not nested within J | left: as site 82 |
| 84 | sec_5d.tex:135 | FALSE | With the study's precision targets and computing budget, no five-dimen … | changed: FD-8 (ledger E2) |
| 85 | sec_5d.tex:146 | AMB | The five-dimensional measurement study assessed three reporting defini … | changed: FD-9 (ledger AMB85) |
| 86 | sec_5d.tex:146 | AMB | the 109 J cells (RD1), the 27 H2 cells (RD2) and the 39 EW cells (RD3) | left: as site 82; the RD definitions are the study's own |
| 87 | sec_5d.tex:146 | AMB | No reporting definition can meet these precision targets with any esti … | changed: FD-10 (ledger AMB87) |
| 91 | sec_5d.tex:196 | AMB | These envelopes are sensitivities: they provide no probabilities, cova … | left: 'these envelopes' are this study's maxima over historical vertices; the sixteen-cell model term is a different object, and stating how they relate needs a fact W does not have |
| 92 | sec_5d.tex:211 | AMB | Five-dimensional coverage test | left: heading of the configuration-(c) coverage test; the fake-data study is not a coverage test |
| 94 | sec_5d.tex:214 | AMB | No frequentist coverage is therefore claimed for any five-dimensional  … | left: already says frequentist coverage, and stays true (no coverage is claimed for the sixteen-cell intervals) |
| 95 | sec_5d.tex:244 | AMB | The five-axis covariance used in this note and its $(\Eavail,W)$ proje … | changed: FD-11 (ledger AMB95) |
| 96 | sec_5d.tex:250 | AMB | The five-axis covariance used in this note is the variant centered on  … | left: purely local, inside sec:eavailw-adopted (brief); its heading is now named (FD-11) |
| 103 | sec_joint.tex:5 | AMB | They do not use, and do not validate, the five-axis covariance used el … | changed: JT-1 (ledger AMB103) |
| 108 | sec_summary.tex:19 | AMB | The regularization bias is largest in the high-$\Eavail$, high-$W$ reg … | changed: SU-1 (ledger AMB108) |
| 109 | sec_summary.tex:29 | FALSE | The quoted five-dimensional central value keeps this bias, and no quot … | changed: SU-2 (ledger D1, D2) |
| 111 | sec_summary.tex:46 | AMB | The five-dimensional estimator recovers only part of truth changes of  … | left: stays true of every 5D estimator tested, configuration (e) included (sec:val-departure: no estimator change meets the recovery requirement) |
| 112 | sec_summary.tex:46 | FALSE | No quoted uncertainty includes this residual bias, which is interprete … | changed: SU-3 (ledger C1) |
| 113 | sec_summary.tex:46 | AMB | Above two dimensions the results are central values without intervals  … | changed: SU-4 (ledger AMB113, E1) |
| 114 | sec_summary.tex:46 | FALSE | No five-dimensional measurement with total uncertainties was construct … | changed: SU-4 (ledger AMB113, E1) |
| 116 | sec_summary.tex:46 | FALSE | The one five-dimensional covariance used in this note does not meet it … | changed: SU-5 (ledger F2, G2) |
| 117 | sec_summary.tex:46 | AMB | so no covariance-based significance is quoted | changed: SU-5 (ledger F2, G2) |
| 118 | sec_summary.tex:78 | AMB | The release design and its public example have no bearing on the choic … | changed: SU-6 (ledger AMB118) |
| 119 | app_guide.tex:12 | AMB | the fixed identities and audit record of the five-axis covariance | changed: AG-1 (ledger AMB119) |
| 120 | app_guide.tex:28 | AMB | the two variants of the five-axis covariance | left: a glossary row defining the cv/mean variant names, which belong only to the configuration-(a) covariance |
| 121 | app_statmethods.tex:159 | AMB | its use in the five-axis covariance of this note | changed: AA-1 (ledger AMB121) |
| 122 | app_statmethods.tex:223 | AMB | The five-axis covariance used in this note deliberately retains the CV … | changed: AA-2 (ledger AMB122) |
| 125 | app_statmethods_nd.tex:62 | AMB | Such a benchmark would supplement, not replace, the scalar five-dimens … | left: names no product; a benchmark supplementing an uncertainty construction is true for either product |
| 126 | app_negweight.tex:106 | FALSE | binned purity remains the treatment of the five-dimensional central va … | changed: AC-1 (ledger A7) |
| 127 | app_negweight.tex:120 | AMB | The entire standard five-dimensional chain uses binned purity | changed: AC-2 (ledger AMB127) |
| 128 | app_negweight.tex:126 | FALSE | For the five-dimensional central value, which still uses purity, the r … | changed: AC-3 (ledger A8) |
| 129 | app_negweight.tex:126 | AMB | The standard chain uses purity by choice | left: 'the standard chain' is defined two paragraphs earlier as the configuration-(a) chain (AC-2) |
| 130 | app_negweight.tex:149 | AMB | The standard chain uses purity throughout. | left: as site 129 |
| 132 | app_negweight.tex:159 | AMB | this supports quoting the standard chain with purity subtraction | left: as site 129 |
| 133 | app_negweight.tex:159 | AMB | There is no full five-dimensional $187$-universe comparison of the two … | left: still true; the configuration-(a) and sixteen-cell products differ in estimator and cells, so they are not a 187-universe comparison of the two treatments. Saying so would add a claim |
| 134 | app_negweight.tex:163 | FALSE | That estimator is configuration (e), which gives the 3D and 4D central … | changed: AC-4 (ledger A9) |
| 135 | app_negweight.tex:165 | AMB | it is direct evidence for revisiting the five-dimensional background t … | changed: AC-5 (ledger AMB135) |
| 136 | app_negweight.tex:170 | AMB | this result does not close the revisit of the five-dimensional backgro … | changed: AC-6 (ledger AMB136) |
| 137 | app_negweight.tex:187 | AMB | nothing in this appendix selects a five-dimensional covariance for use | left: still true; nothing in the appendix selects either 5D covariance. The definite description that follows is named (AC-7) |
| 138 | app_negweight.tex:187 | AMB | The status of that five-axis covariance and the scope of its use | changed: AC-7 (ledger AMB138) |
| 139 | app_response_mismatch.tex:22 | AMB | The test leaves the quoted central value and the current covariance co … | left: the protocol has not run, so it leaves every quoted central value and covariance unchanged, both products included |
| 140 | app_release.tex:42 | AMB | event-level unfolding, or the quoted closure, bias and covariance-stat … | hands-off: Joseph's release text (proposal in abstract-proposals.md) |
| 141 | app_release.tex:55 | AMB | \textbf{Central values}: the five-axis array and every projection quot … | hands-off: Joseph's release text (proposal in abstract-proposals.md) |
| 142 | app_release.tex:56 | AMB | the five-axis covariance used in this note and its $(\Eavail,W)$ proje … | hands-off: Joseph's release text (proposal in abstract-proposals.md) |
| 143 | app_release.tex:63 | AMB | that travel with the five-axis covariance used in this note | hands-off: Joseph's release text (proposal in abstract-proposals.md) |
| 144 | app_release.tex:86 | AMB | The five-axis covariance used in this note is the file \texttt{z-cv.np … | hands-off: Joseph's release text (proposal in abstract-proposals.md) |
| 146 | paper_body.tex:34 | AMB | 4D and 5D marginal normalizations agree at about 1--2\%; the 3D (e) ma … | changed: PB-1 (ledger AMB146) |
| 149 | paper_body.tex:38 | AMB | seed-dependent covariance; rounding-level instability | changed: PB-2 (ledger AMB146) |
| 150 | paper_body.tex:39 | AMB | no tested reporting definition meets the 10\% target | changed: PB-3 (ledger AMB146) |
| 151 | paper_body.tex:46 | AMB | Throughout, a three- to five-observable result is a central value with … | changed: PB-4 (ledger AMB151) |
| 152 | paper_body.tex:46 | AMB | The paper does not deliver a validated five-observable cross-section m … | left, for Joseph: still true while no coverage or validation claim is made; it is a claim in the Scope paragraph (abstract-proposals.md gives options) |
| 154 | paper_body.tex:90 | FALSE | The five-observable central value uses configuration~(a), with the pur … | changed: PB-5 (ledger A10) |
| 156 | paper_body.tex:105 | FALSE | 5D central value and covariance; 3D and 4D closures; 2D learner compar … | changed: PB-6 (ledger A11) |
| 157 | paper_body.tex:113 | FALSE | 3D and 4D central values; held-out shapes (Fig.~\ref{fig:deformation}b … | changed: PB-7 (ledger A11) |
| 158 | paper_body.tex:121 | AMB | the coverage tested here is pointwise, for each reported quantity sepa … | left: the fake-data study is not a coverage test, so 'the coverage tested here' is still the pointwise one |
| 160 | paper_body.tex:173 | AMB | about one quoted standard deviation in one $(\Eavail,W)$ cell | changed: PB-8 (ledger AMB160, AMB161) |
| 161 | paper_body.tex:173 | AMB | This bias is not included in the quoted uncertainties. | changed: PB-8 (ledger AMB160, AMB161) |
| 163 | paper_body.tex:184 | FALSE | No quoted uncertainty includes the regularization bias, and the five-o … | changed: PB-9 (ledger C4) |
| 165 | paper_body.tex:207 | AMB | the grey band is $\pm$ the quoted total uncertainty of the $(\Eavail,W … | changed: PB-10 (ledger AMB165) |
| 166 | paper_body.tex:237 | AMB | The covariance of the five-observable central value, which has a \zpro … | changed: PB-11 (ledger AMB166) |
| 168 | paper_body.tex:237 | AMB | We therefore quote no covariance-based generator significance. | changed: PB-11, PB-12 (ledger AMB166, AMB169, G4) |
| 169 | paper_body.tex:237 | AMB | The seed dependence of the five-observable covariance rests on one see … | changed: PB-11 (ledger AMB166) |
| 170 | paper_body.tex:247 | AMB | none of the reporting definitions of a five-observable measurement tes … | left: already scoped ('tested in the study') |
| 173 | paper_body.tex:290 | AMB | the higher-dimensional central values usable for qualitative compariso … | changed: PB-13 (ledger L4) |
| 175 | paper_body.tex:302 | AMB | The high-$\Eavail$, high-$W$ region is where the regularization bias o … | left: already scoped by its pointer ('the regularization bias of Sec.~\ref{sec:validation}') |
| 177 | paper_body.tex:405 | AMB | The higher-dimensional results are central values without intervals of … | changed: PB-14 (ledger C5) |
| 178 | paper_body.tex:405 | FALSE | no quoted uncertainty includes their regularization bias | changed: PB-14 (ledger C5) |
<!-- absence-ok: quotes or summarizes the note's printed text, before or after this PR, as the writer's record; not a new absence claim -->

- AMBIGUOUS changed: 49
- AMBIGUOUS hands-off: 13
- AMBIGUOUS left: 39
- FALSE-ONCE-PRINTED changed: 29
- FALSE-ONCE-PRINTED hands-off: 4

## Additions beyond the site list (list items that now name the sixteen-cell result)

| edit | file | why |
|---|---|---|
| RS-2 | result_status_rows.tex | Table 1 gets a new row for the sixteen-cell result, with pointers only (configuration (e); reported covariance §; fake-data §; generator comparison §). It keeps Table 1 from omitting a quoted result. |
| ES-2 | sec_execsummary.tex | The caption of that table now lists `sec:fived16`. |
| IN-4 | sec_intro.tex | The roadmap table gets a row "Sixteen-cell five-observable result & §10". |
| ME-2 | sec_method.tex:28 | The list of configuration (e)'s uses now includes the sixteen-cell result. |
| AC-7 | app_negweight.tex:187 | "the record of the covariance used in this note" (the antecedent of site 138) is now named. |

If the integrator also adds a roadmap or status row, these are duplicates: drop one of each pair.

## Check outputs

- **check_ledger.py** (`--old-dir S/5d/base --ledger ledger-W.md`): `ledger rows 74, probes 165, changed base sentences 73, failures 0` (rc=0).
  - `--self-test`: `SELF-TEST :: PASS`, with all 9 planted defects caught.
  - **Probe control:** the same ledger was run against the base itself (`S/5d/W/basewt`, a symlink to base).
    - 163 of the 165 probes fail there: every X probe still prints, and every N probe is absent.
    - The 2 that pass are the stub row S1's N probes. They are unchanged-text anchors, by design.
    - Output: `control_base.out`.
- **reflow_tex.py --check** (the 15 edited files): `TEX-REFLOW :: PASS -- 15 sources, 0 with a paragraph or comment block split over several lines`.
- **printed_diff.py --dirs base copy** (the 15 files): `PRINTED-DIFF :: OK (154 changed sentence line(s))`.
  - Every changed line is an intended edit, or the integrator's two FIVED16 stubs in paper_body.tex.
  - There is no stray `%` truncation. Full output: `printed_diff.out`.
- **Build, the brief's exact command** (`cd S/5d/W/repo/docs/analysis-note && PAR_GLOBAL_TMPDIR=S/partmp-5dW bash build_all.sh > ../../build.log`): **rc=1, before any LaTeX runs.**
  - **The cause is not a writer edit.** `make_values_fived16.py --check` crashes with `CalledProcessError` on `git rev-parse --show-toplevel`, because the copy is not a git checkout.
  - The script's own comment in build_all.sh says it reports SKIP in a standalone note repository, but it does not: it raises.
  - **This is a defect for the integrator.** Expected per the brief: a SKIP. Actual: a crash, which stops the build.
  - Log: `S/5d/W/repo/build.log`.
- **Build, completed in a scratch copy:**
  - `S/5d/W/buildtmp/docs/analysis-note` is an rsync of the writer copy. It adds the base's 73 figure PDFs, which the writer copy lacks (it has 2 files in `figures/`, against 75 in the base).
  - It runs build_all.sh with only the make_values line replaced by an echo SKIP. Log: `S/5d/W/build.log`.
  - All five PDFs built.
  - **0 undefined references** in main_note.log and main_paper.log (only font-shape warnings). No `??` in either PDF's text.
  - `ENTRY-NUMBERS :: PASS`; `ENTRY-NUMBERS-AUX :: PASS`; dead-containment `RESULT :: PASS`.
  - `RECORDS-PIN :: SKIP`, which is expected in a copy.
  - `SEC4-RECEIPTS :: FAIL` there, because the copy layout has no `docs/orchestration` receipts. Rerun with `docs/orchestration` linked to `S/wt-con/docs/orchestration`: `SEC4-RECEIPTS :: PASS (15/15)`, `SELF-TEST :: PASS (18 perturbations rejected)`.
  - **The pending-placeholder stage did not run**, because the build stops at SEC4. Run by hand with pdftotext: 0 `PENDING:` in main_note.pdf and main_paper.pdf.
  - **Spot-check of the PDF text:**
    - the new FD-5, RS-2, FD-8, PB-12, PB-4 and IN-4 wording prints, with references resolved: note §10 is the sixteen-cell chapter; paper Sec. V F is result16 and Sec. VII B is gen16;
    - "configuration-(a)" appears 44 times in the note and 6 times in the paper.
- **Byproducts in the copy:** the failed exact-command builds left `main_note.{aux,log,toc,out,fls,fdb_latexmk,bcf-SAVE-ERROR}` in `S/5d/W/repo/docs/analysis-note/`. No `.tex` source was changed by them.

## What W could not make true without new facts (left unchanged, listed for the integrator or the director)

1. **sec_systematics:278**, "higher-dimensional products built from the single-pass shifted observables are not used for any quoted uncertainty" (site 44).
   - It now ranges over the sixteen-cell covariance.
   - Whether S1's lateral bands came from re-selected or single-pass event loops was not checked.
2. **sec_5d:90**, "below a tenth of any total uncertainty" (site 78).
   - It is likely still true: the TSV gives 0.23 % per J cell against a C_total minimum of 4.14 %.
   - That comparison is not probed on the same cells.
3. **sec_5d:196**, "These envelopes … provide no … covariance components" (site 91).
   - The sixteen-cell C_model is built from prior-reweight shifts.
   - Saying how it differs from these historical-vertex envelopes needs a stated relation.
4. **sec_systematics:282** (not in the sweep): "the only use of a training subset in this note".
   - W did not check whether any sixteen-cell component uses a training subset.
5. **sec_method:28**, "every other quoted cross section and uncertainty … uses the binned correction".
   - W listed only "the sixteen-cell 5D result" among the refined uses.
   - S1 is configuration (e)'s covariance (S1-DECLARATION.md:1), but W did not check how C_resp was built. W therefore did not write "and its covariance" there.
6. **The H2 relation** (sites 82, 83, 86): left as the study's 27-cell H2, per the Group E ruling and outline §4 item 3.
7. **A stale absence Search line**, sec_5d.tex, the comment after line 135: "no note source prints a five-dimensional measurement with total uncertainties @ 1a015eef".
   - It is no longer true once the chapter prints.
   - Per the brief, it stays in its paragraph unedited, so it needs a re-search and a new date by whoever owns absence claims.
