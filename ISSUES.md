# Companion Analysis Note: Round 1 Referee Findings and Currency Audit Issue Ledger (ISSUES.md)

**Scope and Context:**  
This issue ledger governs Round 2 of the MINERvA companion analysis note (`docs/analysis-note/`). The note is reframed from a primary measurement to the technical record of the methods-and-benchmark study under `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` (`af7356504`, PR #947). The previous measurement-framed note is archived at `archive-note-measurement-framed-20261108/` (`main_note.pdf`, 137 pp, sha256 `f6d7d80c...`).  
Work is conducted on branch `draft/note-round2-20261108` in isolated worktree `/Users/josephbailey/MINERvA-OmniFold-note-round2`, cut from `draft/note-round1-20261108` at `b1da7ba8372348d9600d043eb381f676db25e1df`.  
Roles: Antigravity is the drafting owner; Grok verifies each change against governing records before landing and logs the check in this ledger. Claude is currently out of usage (~3 hours). No note prose or structural move merges without approval from Joseph.

## Classification Taxonomy

Every item is assigned a single, unambiguous class:
* **[T] (Textual / Editorial):** A finding requiring textual or editorial adjustment in the note (e.g., resolving inconsistencies, harmonizing definitions, clarifying scope, correcting typos, or removing overclaims).
* **[R] (Record-Backed):** A finding requiring an update to numbers, tables, or macros backed by a landed, immutable OUTCOME, DECISION, or pinned receipt in `docs/orchestration/`.
* **[A] (New Analysis):** A finding requiring new scientific analysis or compute, which goes to the director and cannot be resolved by drafting.
* **[D] (Dispute / Void):** A referee finding that is demonstrably refuted by code, mathematics, or governing records (with technical proof recorded in the resolution); or voided by instruction (e.g., reader-side text truncation).

## Summary of Classifications

| Source | [T] Textual | [R] Record | [A] Analysis | [D] Dispute/Void | Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Part 1: Currency Audit (`AUDIT.txt`)** | 12 | 9 | 0 | 0 | **21** |
| **Post-Audit Record Items (`AUD-L5`)** | 0 | 0 | 0 | 1 | **1** |
| **Part 2: Sonnet Report 1 (`sonnet-note-r1-1.txt`)** | 61 | 4 | 0 | 1 | **66** |
| **Part 3: Sonnet Report 2 (`sonnet-note-r1-2.txt`)** | 63 | 3 | 0 | 1 | **67** |
| **Part 4: Gemini Report 1 (`gemini-note-r1-1.txt`)** | 34 | 2 | 0 | 1 | **37** |
| **Part 5: Gemini Report 2 (`gemini-note-r1-2.txt`)** | 27 | 0 | 0 | 3 | **30** |
| **Total Enumerated Findings** | **197** | **18** | **0** | **7** | **222** |

---

## Part 1: Currency Audit Items (`AUDIT.txt`)

Base commit: `b1da7ba8372348d9600d043eb381f676db25e1df`

### EDITED in Round 1 (Review & Verification)

* **AUD-E1 [R]** — **COV2D held-out tune result.**  
  *Finding:* Held-out tune test results (joint in-region count 0 of 300 at AR23 and G18, reading UNDER-COVERS, with flagged cells attributed to bias and false-flag rate $\le 0.036$) are reported as an empirical test of the procedure's covariance at those tunes.  
  *Record:* `OUTCOME-20261108-cov2d-both-tunes-under-cover.md:99-106` (`CITABLE FOR`), `:108-119` (`NOT CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_validation.tex:199`, `sec_systematics.tex:53`, `sec_systematics.tex:214`, `sec_execsummary.tex:21`.  
  *Prohibitions (`NOT CITABLE FOR` lines 108–119):* Must strictly carry all negative constraints: (1) NOT citable for coverage of reported intervals at the data's point ($Q_R$ is made at the data, not at $T$); (2) NOT citable for a coverage rate or statements about truths unlike these two; (3) NOT citable for a cause of joint under-coverage or of any flag; (4) NOT citable for anything about $C_{\\text{PL},R}$ or $C_{\\text{model}}$ (neither drawn); (5) NOT citable for independence from training rows; (6) does NOT replace or remove earlier fixed-truth failure (`VL162`; adds to it); (7) NOT citable as wording for the paper or the note (must go through PRD-referee read and Joseph, §12); (8) the "both COVER" sentence of §13 is not available.  
  *Resolution:* Under prohibition (7) and `OUTCOME-20261108-cov2d-both-tunes-under-cover.md:118-119`, this result is not wording for the note until the paper lane, a PRD-referee read, and Joseph say so; this row adds no note sentence and authorizes no text change.

* **AUD-E2 [R]** — **1B STOP rule and counts.**  
  *Finding:* The 5D coverage pre-check fail-closed rule and exact draw counts (892 of 900 draws with non-positive composite denominator; up to 62 cells) must be explicitly stated.  
  *Record:* `OUTCOME-20261106-1b-stage1-receipt-stop.md:27-30`, `:101-104`.  
  *Target:* `docs/analysis-note/sec_fived16.tex:253`, `sec_5d.tex:216`.  
  *Resolution:* This row authorizes no tex edit. The fail-closed rule and the counts are already stated through the macros stop-flagged, stop-draws, and stop-maxcells, which print 892, 900, and 62. The sentence already says the stop says nothing about whether the intervals cover, in either direction. Do not type 892. Do not add a further sentence.

* **AUD-E3 [R]** — **1B pre-check Part 1 (flux and detector groups).**  
  *Finding:* State Part 1 pre-check outcome: both flux and detector groups reproduce within the [0.9, 1.1] window; GEANT neutron and proton bands depart in named cells.  
  *Record:* `OUTCOME-20261108-1b-precheck-part1.md:49-62` (`CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_fived16.tex:253`.  
  *Resolution:* This row authorizes no tex edit. The Part 1 pre-check is already stated. The pseudo-experiments reproduce the simulation-side block within the gate window, which prints 0.9 to 1.1, in every resolved cell. The GEANT neutron and proton bands depart in the named cells. Do not add a cause. Do not add a coverage statement. Do not add a further sentence.

* **AUD-E4 [R]** — **Valid-region classes of the 16 cells.**  
  *Finding:* Tabulate each cell's V-ATLAS class (14 valid; fails in R02, R06 from A7 GiBUU hybrid truth alone) and V-PRIOR class (14 valid; fails in R08, R15), with 12 valid under both, and reading (3)'s printed quantities labeled "computed after the pulls against the prior were seen (L4)".  
  *Record:* `OUTCOME-20261107-valid-region.md:21-25` (`CITABLE FOR`), `:27-37` (`NOT CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_fived16.tex:218`.  
  *Prohibitions (`NOT CITABLE FOR` lines 27–37):* Must strictly carry all negative constraints: (1) NOT citable for coverage (diagnostics grade bias, not coverage; no interval is validated); (2) NOT citable as a measurement (diagnostics of estimator on committed products; no reported value changes); (3) NOT citable for any physics claim about generators; (4) NOT citable for the cause of any departure; (5) NOT citable for V-PRIOR, or its threshold of 0.5, as ATLAS's or as the advisor's own formulation; (6) NOT citable as non-valid cells being excluded, wrong, or unreported (no cell is excluded or changed); (7) NOT citable for held-out truths; (8) ATLAS guide item 5 is NOT met; (9) NOT citable that 2D mismodeling is localized in the extra dimensions, or that it is not, in either direction; (10) reading (3) is NOT citable as a test.  
  *Resolution:* This row authorizes no tex edit. The valid-region paragraph already states the two rules. V-ATLAS prints 14 valid, every cell except R02 and R06. V-PRIOR is stated as ours, not the guide's, and prints 14 valid, every cell except R08 and R15, with 12 valid under both. Neither rule is a coverage test, and no cell is excluded or changed. Do not add a table. Do not add a localization claim. Do not state V-HALF. Do not add reading (3).

* **AUD-E5 [R]** — **Per-period 2D benchmark.**  
  *Finding:* Add the per-period 2D benchmark combined sentence from `readout.json` and the R5-bar sentence after `sec_results.tex:134`.  
  *Record:* `OUTCOME-20261107-per-period-2d-benchmark.md:13-16`, `:152`.  
  *Target:* `docs/analysis-note/sec_results.tex:134`.  
  *Resolution:* This row authorizes no tex edit. The combined sentence and the R5-bar sentence are already in sec_results.tex. The combined sentence prints the licensed statement that the run-period step does not account for the distance in the best-determined directions, at the resolved size. The following sentence states the 132 poorly determined directions, the 0.69 difference, the 0.31 fraction, and the 10 replicas. The paragraph already says the noise is a lower bound and that neither reading identifies a cause or which period is right. Do not add a second copy. Do not add the 0.29 resolved-size figure. Do not say which period is right, that 1G-1M is wrong, or that the published result is right. Do not edit app_statmethods.tex under this row.

* **AUD-E6 [R]** — **RS1 rounding mechanism.**  
  *Finding:* Report numerical precision / float32 rounding findings (shifts up to 2.6σ_stat, median 0.8σ; separate tie-break vs refinement legs).  
  *Record:* `OUTCOME-20261108-rs1-rounding-mechanism.md:128-135`.  
  *Target:* `docs/analysis-note/sec_5d.tex:91`.  
  *Resolution:* This row authorizes no tex edit. The float32 paragraph in sec_5d.tex already reports the 0.8 and 2.6 shifts and states the tie-breaking leg and the refinement leg separately, in the outcome's licensed wording. It already says neither finding is about the data's spread and that equal float32 values are not a defect of the inputs. Do not add a second account. Do not add K2, K3, K4, or K6. Do not join the two findings into one mechanism. Do not say either stage alone suffices. Do not add a remedy. Do not edit "40 fresh pseudo-experiments." Do not add an estimator table.

* **AUD-E7 [T]** — **OVERCLAIM: The 2D comparison called a validation.**  
  *Finding:* Note called 2D comparison a validation (`sec_intro.tex:18`, `:30`, `sec_method.tex:25`, `sec_results.tex:1`, `sec_execsummary.tex:3`, `tab:validation-questions`).  
  *Record:* `AUDIT.txt` row E7; `CAMPAIGN-REVIEW-20260929.md:27-28`; `VALIDATION_LEDGER.md:175`.  
  *Target:* `docs/analysis-note/sec_intro.tex`, `sec_method.tex`, `sec_results.tex`, `sec_execsummary.tex`.  
  *Resolution:* This row authorizes no tex edit. Do not run a global replacement of "validates". The audit's three sentences already use its wording. The introduction says the comparison is descriptive, not a blind validation. The analysis-strategy paragraph says the published 2D cross section provides a quantitative, descriptive comparison. The method paragraph says the unfolded result reproduces the integrated cross section of an independently published binned measurement. Do not add a further sentence. Do not copy article text into the note. Do not change the validation-section title. Do not edit sec_5d.tex under this row.

* **AUD-E8 [T]** — **The CH correction's scope.**  
  *Finding:* Executive summary stated CH correction without restricting it to joint cells.  
  *Record:* `AUDIT.txt` row E8; `sec_joint.tex:145-148`.  
  *Target:* `docs/analysis-note/sec_execsummary.tex:17`.  
  *Resolution:* This row authorizes no tex edit. The executive summary already says the CH correction moves both predictions toward the data on the joint cells, and that on the sixteen cells GiBUU's total chi-squared rises. The joint section already says that rise is on GiBUU's eight cells. Do not add a second sentence. Do not type a chi-squared value. Do not change "sixteen cells" to "eight" in the summary. Do not edit the paper or sec_joint.tex under this row.

* **AUD-E9 [R]** — **Response-only sensitivity ($N_3$) in `sec_fived16.tex`.**  
  *Finding:* Include Joseph's response-only sensitivity, median 1.65× interaction block σ (range 0.42–6.50), grid-dependent and not a bound.  
  *Record:* `DECISION-20261101-joseph-1b-keep-block-redesign-test.md:38-40`.  
  *Target:* `docs/analysis-note/sec_fived16.tex`.  
  *Resolution:* This row authorizes no tex edit. The response-only sensitivity is already in sec_fived16.tex. It prints, through the existing macros, a median of 1.65 times the reported interaction block, with range 0.42 to 6.50, and it says the quantity depends on the fine-cell grid and is not a bound. Do not type those numbers. Do not add a coverage statement. Do not say the intervals should carry the response-only spread. Do not add a second sentence. AUD-N3 is a later row.

* **AUD-E10 [T]** — **Second post hoc choice ($N_7$) in Executive Summary.**  
  *Finding:* Executive summary must state background-treatment choice beside learner choice.  
  *Record:* `AUDIT.txt` row E10; `sec_method.tex:79`, `:103`; `DECISION-20261105-joseph-765-abstract-and-2d-disclosure.md:61-63`.  
  *Target:* `docs/analysis-note/sec_execsummary.tex:9`.  
  *Resolution:* This row authorizes no tex edit. The executive summary already states the learner choice and the background-treatment choice beside it. The background sentence says the treatment was decided on a closure test before the rebuilt result's distance from the published result was computed, and that the rebuilt result was adopted after that distance was known, and it ends with the clause that the comparison with the publication is therefore not an independent test of the method. Do not add a second sentence. Do not add the broader claim that the background treatment was selected with the published result known. Do not copy article text into the note. Do not edit the status-table cell. AUD-N7 is a later row.

### HELD and NOT DRAFTED in Round 1 (Status in Round 2)

* **AUD-N1 [T]** — **Note reframed from measurement to methods-and-benchmark record.**  
  *Finding:* Title, abstract, executive summary, `sec_fived16.tex`, and appendices must be unfrozen and reframed to the methods study. Ruled by Joseph in `DECISION-20261108` (#947).  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` item 1.  
  *Target:* `docs/analysis-note/main_note.tex:73`, `sec_execsummary.tex:6`, `sec_fived16.tex:1`, `app_landscape.tex:59`, `app_statmethods.tex:5`.  
  *Resolution:* This row authorizes no tex edit. The note is already reframed as the technical record of a methods and benchmark study. The abstract, the executive summary, and the sixteen-cell section say the sixteen-cell output is illustrative and not for fitting or for constraining models. The landscape row for that output says illustrative output. The statistics appendix opens on this note's results and the 2D comparison. The measurement-framed note is archived. Do not change the title. Do not sweep the remaining "this measurement" phrases that name the 2D result. Do not copy article text into the note.

* **AUD-N2 [T]** — **REF-G1 algorithm dependence as a stated limitation.**  
  *Finding:* The IBU vs OmniFold 16-cell difference ($T = 194.4$ against calibrated bar 28.12) must enter as a stated limitation with no new covariance block. Ruled by Joseph in `DECISION-20261108` (#947).  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` item 3, `OUTCOME-20261106-ref-g1-r1-differ.md:40-41`.  
  *Target:* `docs/analysis-note/sec_fived16.tex:280-320` (`sec:fived16-ibu`), `sec_execsummary.tex`.  
  *Resolution:* This row authorizes no tex edit. The algorithm dependence is already a stated limitation in sec:fived16-ibu. T and the calibrated bars print through the existing macros. The paragraph says no uncertainty block is added and the reported cells and covariance are unchanged, and that a reading of differ does not show that either method is correct. The executive summary already lists the dependence. Do not type 194.4 or 28.12. Do not add a new uncertainty block. Do not add the per-cell percentages. Do not add a second sentence.

* **AUD-N3 [R]** — **Response-only sensitivity.**  
  *Finding:* Response-only sensitivity ($N_3$) documented under AUD-E9.  
  *Record:* `DECISION-20261101-joseph-1b-keep-block-redesign-test.md:38-40`.  
  *Resolution:* This row authorizes no tex edit. Same disposition as AUD-E9. The response-only sensitivity is already in sec_fived16.tex, through the existing macros, a median of 1.65 times the reported interaction block, with range 0.42 to 6.50, and it says the quantity depends on the fine-cell grid and is not a bound. Do not type those numbers. Do not add a coverage statement. Do not say the intervals should carry the response-only spread. Do not add a second sentence. Do not edit the AUD-E9 resolution.

* **AUD-N4 [T]** — **Release appendix update.**  
  *Finding:* The release appendix still specifies the measurement release; archive package is not mentioned.  
  *Record:* `AUDIT.txt` row N4; `DECISION-20261106-joseph-methods-study-and-archive.md:57-61, :64-67` ("Publication, release and contact acts stay Joseph's").  
  *Target:* `docs/analysis-note/app_release.tex:4`, `:58`.  
  *Status:* **HELD.** Held by the director (2026-11-08) and Joseph; kept out of steps 4 and 5; no release schema change drafted.

* **AUD-N5 [R]** — **Event-loop preservation.**  
  *Finding:* Event-loop preservation CFS paths in `app_release.tex:50, :53`.  
  *Record:* `AUDIT.txt` row N5; `DECISION-20261101-joseph-eventloops-copy-to-cfs.md:28-34, :38-48` has no CITABLE FOR block.  
  *Target:* `docs/analysis-note/app_release.tex:50`, `:53`.  
  *Status:* **HELD.** Held by the director (2026-11-08) and Joseph; kept out of steps 4 and 5; no text drafted without authorization.

* **AUD-N6 [T]** — **Abstract resync.**  
  *Finding:* Resync note abstract to match reframed paper abstract per `DECISION-20261105-joseph-765-abstract-and-2d-disclosure.md:57-59`.  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md`.  
  *Target:* `docs/analysis-note/main_note.tex:73`.  
  *Resolution:* This row authorizes no tex edit. The abstract already contains the licensed fake-data sentence. The criteria print through the existing macros, 0.01 and 2. The two coverage statements stay separate. Do not copy the paper abstract into the note. Do not type 0.01 or 2. Do not merge the two coverage tests. Do not add a further sentence.

* **AUD-N7 [T]** — **Second post hoc choice in Executive Summary.**  
  *Finding:* Background treatment choice documented under AUD-E10.  
  *Record:* `AUDIT.txt` row N7; `DECISION-20261105-joseph-765-abstract-and-2d-disclosure.md:61-63`.  
  *Resolution:* This row authorizes no tex edit. Same disposition as AUD-E10. The executive summary already states the learner choice and the background-treatment choice beside it, and the background sentence already ends with the clause that the comparison with the publication is therefore not an independent test of the method. Do not add a second sentence. Do not add the broader claim that the background treatment was selected with the published result known. Do not copy article text into the note. Do not edit the status-table cell. Do not edit the AUD-E10 resolution.

### FLAGGED in Round 1 (No Record Contradicts; For Referee Read)

* **AUD-L1 [T]** — **Retract descriptive extra-dimensional localization claims.**  
  *Finding:* Descriptive central-value excesses must not be claimed as physical model localization in higher dimensions without covariance.  
  *Record:* `OUTCOME-20261107-valid-region.md:36` (`NOT CITABLE FOR localization in either direction`).  
  *Target:* `docs/analysis-note/sec_execsummary.tex:13`, `sec_3d.tex:140`, `sec_eavailw.tex:151`, `sec_joint.tex:237`.  
  *Resolution:* Two localization clauses are removed. The 3D sentence no longer says the high-E_avail excess is localized on the (E_avail, W) plane. The shallow-inelastic sentence no longer says the same localized excess or that a location was identified. The named-bin ratios and the Valencia paragraph stay. Do not add the word exploratory. Do not restore the deleted corner sentence.

* **AUD-L2 [T]** — **Tension anatomy run-period cause statement.**  
  *Finding:* Remove causal attribution for the 2D shape tension; state that run period accounts for variance only in poorly determined modes and cause remains unknown.  
  *Record:* `OUTCOME-20261107-per-period-2d-benchmark.md:18-25`.  
  *Target:* `docs/analysis-note/app_statmethods.tex:536`, `:554`, `:559`.  
  *Resolution:* This row authorizes no tex edit. The audit says no record contradicts the earlier exact-split statements in the tension anatomy, and those statements stay. The results section already says the source of the shape difference has not been identified and already carries the licensed run-period sentences. Do not add a second copy. Do not say which period is right or that a period caused the difference. Do not edit the conclusion paragraph.

* **AUD-L3 [T]** — **5D estimator validation claim qualification.**  
  *Finding:* `sec_validation.tex:41` at base `b1da7ba8` claims "The five-dimensional estimator is validated", which conflicts with 1B STOP and unvalidated coverage.  
  *Record:* `OUTCOME-20261106-1b-stage1-receipt-stop.md`.  
  *Target:* `docs/analysis-note/sec_validation.tex:41`.  
  *Resolution:* This row authorizes no tex edit. The sentence in sec_validation.tex already says the five-dimensional estimator is evaluated under the technical closure checks and that its coverage is unvalidated. Do not change it again. Do not run a global replacement of "validates". Do not edit sec_5d.tex under this row. Do not add a coverage statement in either direction.

* **AUD-L4 [T]** — **Training-seed band description.**  
  *Finding:* `sec_method.tex:150` describes training-seed band as controlling ML stochasticity, but for configuration (e) training-seed block is zero while rounding shifts results up to 2.6σ_stat.  
  *Record:* `DECISION-20261106-joseph-b0-reconciliation-sentence.md:8`.  
  *Target:* `docs/analysis-note/sec_method.tex:150`.  
  *Resolution:* This row authorizes no tex edit. The method sentence describes the training-seed band of the quoted 2D result, configuration (f). Configuration (e) is already said to have a training-seed block of zero in every cell, and the rounding shifts are already stated in the five-dimensional stability paragraph. Do not add a second account. Do not type 2.6. Do not copy the paper's reconciliation sentences into the note. Do not edit "40 fresh pseudo-experiments."

---

## Post-Audit Record Items

* **AUD-L5 [D]** — **Audit of `\uqMedian` and `\uqIntegral` uses across deliverables.**  
  *Finding:* Prior hypothesis that `\uqMedian` (6.41) and `\uqIntegral` (4.76) were stale round-1 cut values that conflicted with adopted 2D uncertainty $Q$ (6.45% and 4.75%).  
  *Record:* `DECISION-20261024-joseph-adopt-re2-2d-refined.md:9, 30`; `values.tex:60, 64`.  
  *Target:* `docs/analysis-note/sec_results.tex`, `sec_systematics.tex`, `paper_body.tex`, `primer_body.tex`.  
  *Sites (use-by-use list at cf1b504):*  
  * `docs/analysis-note/paper_body.tex:126` — both macros; live sentence.  
  * `docs/analysis-note/primer_body.tex:107` — both macros; live sentence.  
  * `docs/analysis-note/primer_body.tex:114` — `\uqMedian`; comment.  
  * `docs/analysis-note/primer_body.tex:120` — `\uqIntegral`; comment.  
  * `docs/analysis-note/primer_body.tex:130` — `\uqMedian`; live sentence.  
  * `docs/analysis-note/sec_results.tex:88` — both macros; live sentence.  
  * `docs/analysis-note/sec_systematics.tex:40` — `\uqMedian`; live sentence.  
  * `docs/analysis-note/sec_systematics.tex:227` — `\uqIntegral`; live sentence.  
  * `docs/analysis-note/values.tex:4` — `\uqMedian`; comment.  
  * `docs/analysis-note/values.tex:60` — `\uqMedian`; definition.  
  * `docs/analysis-note/values.tex:64` — `\uqIntegral`; definition.  
  * `docs/analysis-note/app_history.tex:50` — `\uqMedian`; historical mention.  
  * `docs/analysis-note/app_history.tex:84` — `\uqMedian`; historical mention.  
  *Resolution:* **DISPUTE / WITHDRAWN.** Class [D]. As corrected by the director (messages `b4b151c9` / `b8d06de8`), `\uqMedian = 6.41` and `\uqIntegral = 4.76` are not stale; they are the current headline adopted values for the refined 2D covariance $Q_R$ under `DECISION-20261024-joseph-adopt-re2-2d-refined.md:9, 30` ("The adopted 2D result is $E_R$, with $Q_R$ as its headline uncertainty. This replaces $E_U$ and $Q$"). Line 9 gives the refined covariance $Q_R$ a per-cell median of 6.41% ($Q$: 6.45%). Line 30 says the adopted 2D result is $E_R$, with $Q_R$ as its headline uncertainty, and that this replaces $E_U$ and $Q$. In `values.tex`, lines 60 and 64 cite the RE-2 figures 6.41367 and 4.75917 and note that the macros were 6.45 and 4.75. DECISION-20261017's 6.45% and 4.75% belong to the superseded $Q$. The 13 sites in the deliverables using `\uqMedian` and `\uqIntegral` are $Q_R$ and must not change. In the citability matrix (`Table~\ref{tab:result-status}`), the 2D uncertainty row states $Q_R$ through `\uqMedian` and `\uqIntegral` on `\lrval{q-ncells}` cells (re-pinned to `RE2-PARTC-REPORT.md:134`).

---

## Part 2: Sonnet Report 1 (`sonnet-note-r1-1.txt`)

### Section 3: Accuracy

* **S1-ACC-1 [T]** — **Tune v1 in quasielastic-Δ dip inconsistency.**  
  *Finding:* Executive summary and §7.6 assert all four generators under-predict data in the dip ($0.1 \\le E_{\\text{avail}} < 0.4\\text{ GeV}$), but §7.8 states the $E_{\\text{avail}}$-marginal data/Tune v1 ratio dips to 1.01, and Fig. 23 shows cells dipping to 0.66.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:13`, `sec_3d.tex:140`, `sec_eavailw.tex:151`.  
  *Resolution:* The executive summary no longer says that all four generators under-predict the dip. The 4D paragraph already states the marginal ratios, including the dip to 1.01 and the cell ratio down to 0.66, and it already distinguishes Tune v1 from untuned GENIE. The clause that the data excess concentrates at low E_avail and toward high q3 is removed. Do not add a sentence about where the difference sits. Do not add the word exploratory.

* **S1-ACC-2 [R]** — **Tune v1 normalization deficit quoted four ways.**  
  *Finding:* Deficit quoted as ~9% (ratio 0.91) in §6.5; 0.883 (10–28%) in §7.6; integrated data/Tune = 1.13 (0.885) in §7.8; ~12% in §2.5.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:45`, `sec_results.tex:85`, `sec_3d.tex:138`, `sec_eavailw.tex:148`.  
  *Resolution:* This row authorizes no tex edit. The four quotes are different quantities and already name their phase spaces: the reconstructed signal-plus-background excess of about 12 percent, the 2D total ratio 0.91, the 3D full-phase-space range of 10 to 28 percent, and the E_avail-marginal data/Tune ratio 1.13. Do not replace them with one macro. Do not add a sentence that equates them.

* **S1-ACC-3 [T]** — **Location of Tune v1 deficit in $p_T$.**  
  *Finding:* §2.5 says data/MC rises with $p_T$ (0.88 to 1.2), §6.5 says deficit is concentrated in low-$p_T$ peak, Fig. 14 says ratios below unity at lowest $p_T$.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:48`, `sec_results.tex:88`.  
  *Resolution:* This row authorizes no tex edit. The reconstructed comparison, the 2D comparison, and the ratio-map caption already agree: the ratio is below unity at the lowest pT, the deficit is concentrated in the low-pT peak, and the ratio rises above unity at higher pT. Do not add a boundary at 0.4 GeV/c. Do not add a further sentence. Do not equate the reconstructed excess with the 2D total.

* **S1-ACC-4 [T]** — **5D coverage test conflation.**  
  *Finding:* Abstract says 5D coverage test "did not run to a result", conflating the 1,200-pseudo-experiment futility test (§9.5, ran, failed) with the staged 16-cell test (§10.5, stopped at 892/900 non-positive draws).  
  *Evidence:* `docs/analysis-note/main_note.tex:73`, `sec_5d.tex:216`, `sec_fived16.tex:253`.  
  *Resolution:* This row authorizes no tex edit. The abstract, the five-dimensional section, and the sixteen-cell section already name the two tests separately. The 1,200-pseudo-experiment test failed its futility criterion. The declared sixteen-cell coverage test did not run to a result. Do not merge them. Do not edit the abstract. Do not type 892. Do not add a further sentence.

* **S1-ACC-5 [T]** — **"Fresh" versus reused pseudo-experiments.**  
  *Finding:* §9.3 and App. C.8 say "40 fresh pseudo-experiments", while §9.4 states they "were used during development".  
  *Evidence:* `docs/analysis-note/sec_5d.tex:145`, `app_statmethods_nd.tex:112`.  
  *Resolution:* This row authorizes no tex edit. Do not replace "fresh" with "developmental". The 40 fresh pseudo-experiments and the experiments used during development have not been shown to be the same set. The negative-weight appendix already counts 20 development and 40 fresh separately. Leave "40 fresh pseudo-experiments" as written.

* **S1-ACC-6 [T]** — **Unusable covariance used as a benchmark yardstick.**  
  *Finding:* Configuration-(a) 5D covariance is marked "not to be used" (§9.6), yet is used as a scale in §5.1, §8.4, §9.2, §9.3, Table 5, App. G.2.  
  *Evidence:* `docs/analysis-note/sec_5d.tex:225`, `sec_eavailw.tex:162`, `app_release.tex:72`.  
  *Resolution:* Governed by S2-COM-2. Do not type 6.145 and do not write "five bands unmeasured." The release checklist stays unedited while app_release.tex is held under AUD-N4. This row authorizes no tex edit.

* **S1-ACC-7 [T]** — **Executive summary marginalization claim (1–2%) vs body.**  
  *Finding:* Executive summary claims 4D and 5D marginalization passes to 1–2%, but §8.1 gives 0.11% total and 0.3–1.5% median per axis; §7.8 gives no number for 4D→3D.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:15`, `sec_eavailw.tex:110`, `sec_3d.tex:170`.  
  *Resolution:* This row authorizes no tex edit. The executive summary no longer says the marginal checks pass to 1 to 2 percent. It says the 4D and 5D checks pass, and it gives the 3D marginal agreement as 0.141 percent in the total. Do not add 0.11 percent, 0.3 to 1.5 percent, 3.7 percent, or 4.52. Do not add a 4D-to-3D number.

* **S1-ACC-8 [D]** — **Band count in cross-covariance at `sec_fived16.tex:66-72`.**  
  *Finding:* Referee asserts §10.2 / `sec_fived16.tex:66-72` has a typo: it names four failing weight checks (AGKYxF1pi, AhtBY, BhtBY, MinosEfficiency) and then writes "These five enter as...", so referee proposes changing "five" to "four".  
  *Resolution:* **DISPUTE.** Class [D]. At base `b1da7ba8` (`sec_fived16.tex:66-72`), "These five enter" follows the paired terms: the systematic bands, the lateral shifts, the normalization, the run-period terms, and the $C_{\text{model}}$ shifts. The statistical correlation is the part that is not measured. Do not change "five" to "four".

* **S1-ACC-9 [T]** — **"At least fifteen-fold" arithmetic error.**  
  *Finding:* §3.2 claims purity bias reduced "at least fifteen-fold (from 3.5% to 4.1% to 0.11% to 0.24%)"; worst case is 3.5 / 0.24 = 14.58.  
  *Evidence:* `docs/analysis-note/sec_method.tex:92`.  
  *Resolution:* Landed at 786a38814631b37d8a2df6d5a0d43c333053285e. The configuration-(e) item now says "by about an order of magnitude". The ranges 3.5--4.1% and 0.11--0.24% are unchanged. No further tex edit.

* **S1-ACC-10 [T]** — **Hyperparameter tuning sequence clarification.**  
  *Finding:* §3.2 claims learner settings fixed a priori, but refinement classifier (400 trees, 31 leaves) was adapted after background bias was observed.  
  *Evidence:* `docs/analysis-note/sec_method.tex:90`, `sec_5d.tex:140`.  
  *Resolution:* Do not draft this chronology. OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md:23-31 and OUTCOME-20260925-s5n-stage1-development-fail.md:25-28 do not say that the refinement capacity was increased after the purity bias was observed. This row authorizes no tex edit.

* **S1-ACC-11 [T]** — **Two $\\chi^2$ values for same quantity in §4.5.**  
  *Finding:* §4.5 reports $p_\\parallel$ $\\chi^2 = 34.4$ against earlier 2D budget, then $34.8$ against other blocks alone.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:168`.  
  *Resolution:* The two comparators are already distinguished in sec_systematics.tex: 34.4 against the earlier 2D budget, and 34.8 against the other blocks alone. This row authorizes no tex edit.

* **S1-ACC-12 [R]** — **Suspicious duplicate numbers.**  
  *Finding:* Check 0.141% 3D marginal difference vs QA $d/S_{2D}$; 3.71% $C_{\\text{model}}$ vs flux band median; identical $r_c$ ratios (0.923/0.963) for NuWro and GiBUU.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:170`, `sec_3d.tex:112`, `sec_fived16.tex:85`, `sec_joint.tex:180`.  
  *Resolution:* This row authorizes no tex edit. The listed pairs stay as written until a readout shows that the two numbers in a pair are the same quantity.

* **S1-ACC-13 [T]** — **Configuration mismatch in 3D/4D closures vs reported values.**  
  *Finding:* 3D/4D central values quoted from configuration (e), while closures use configuration (a).  
  *Evidence:* Table 9, `docs/analysis-note/sec_3d.tex:120`.  
  *Resolution:* The 3D closure section already states that the test is configuration (a) only and does not extend to (e). This row authorizes no tex edit. Do not add a 4D sentence in this commit.

* **S1-ACC-14 [T]** — **Matched-projection claim in executive summary.**  
  *Finding:* Executive summary states matched coarse projections reject as well, but GENIE 2.12.10 is not rejected in $(p_T, p_\\parallel)$ ($p = 0.48$ total, $0.63$ shape).  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:16`, Table 29.  
  *Resolution:* Landed at 3394f20971b995e83309cc3c7476f899b3cf190a. The executive summary now says each matched coarse projection rejects in at least one of the two projections, and that GENIE 2.12.10 is not rejected in the muon-only projection. No p-value was added. No further tex edit.

* **S1-ACC-15 [T]** — **Terminology of $J$ (109 cells).**  
  *Finding:* Reconcile §9.4 / Table 12 ("109 supported fine joint cells") with §11.1 ("coarse $3^5$ grid").  
  *Evidence:* `docs/analysis-note/sec_5d.tex:150`, `sec_joint.tex:45`.  
  *Resolution:* The two descriptions already differ by what they are compared with. sec_joint.tex places the 109 supported cells on the coarse $3^{5}$ grid. The sec_5d.tex table calls those cells fine relative to the 27 H2 cells. This row authorizes no tex edit.

* **S1-ACC-16 [T]** — **Reconciliation of related counts.**  
  *Finding:* Reconcile 4830 populated 4D bins vs 4825 in App. B.1; ndf = 204 vs 205 in §5.3; 27 boxes merged into 16 cells in §10.1; truth $W$ real solutions ($0.15\\%$) vs negative $W^2$ fraction ($4.9 \\times 10^{-5}$) in §8.2.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:175`, `sec_validation.tex:198`, `sec_fived16.tex:35`, `sec_eavailw.tex:50`, App. B.1.  
  *Resolution:* This row authorizes no tex edit. Each listed pair stays as written until a record shows what the two counts are and why they differ.

* **S1-ACC-17 [T]** — **Seed dependence vs training-seed block magnitude.**  
  *Finding:* Single seed variation (seed 1 vs 42 per-bin median 0.18%, max 1.79%) exceeds training-seed block median (0.048%).  
  *Evidence:* `docs/analysis-note/sec_method.tex:95`, `sec_systematics.tex:110`.  
  *Resolution:* This row authorizes no tex edit. Do not compare a seed-1 versus seed-42 shift with the training-seed block until a record states both numbers and what each measures.

* **S1-ACC-18 [T]** — **Iteration stability justification.**  
  *Finding:* Justifying $n=5$ iterations via 0.026% total cross section stability overlooks 1.54% per-bin shape variation in §5.4 and iteration drift in 5D.  
  *Evidence:* `docs/analysis-note/sec_method.tex:85`, `sec_validation.tex:210`.  
  *Resolution:* The shape figure is already next to the total-agreement figure in sec_validation.tex, and the method paragraph cites that section. Do not add a bias-variance claim. This row authorizes no tex edit.

* **S1-ACC-19 [T]** — **2p2h standard magnitude arithmetic in §7.7.**  
  *Finding:* Reconcile statement that closing deficit requires 2p2h at ~45% of QE with $f_{\\text{MEC}} = 2.87\\%$ of CC total and $\\text{QE} = 11\\%$.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:155`.  
  *Resolution:* Those statements are already in sec_3d.tex. Do not add an arithmetic that identifies 2.87% of the CC total with 45% of QE. This row authorizes no tex edit.

### Section 4: Completeness as a Citable Record

* **S1-COM-1 [T]** — **Missing Per-Result Status & Citability Matrix.**  
  *Finding:* No result carries a validated interval; reader needs an explicit table defining what each product is citable for.  
  *Evidence:* All 4 referee reports.  
  *Resolution:* The per-result citability matrix is already in sec_execsummary.tex. This row authorizes no further tex edit.

* **S1-COM-2 [T]** — **5D config-(a) covariance citability.**  
  *Finding:* Explicitly state what may be cited from config-(a) 5D value and uncertainty (exploratory central comparisons only; covariance unusable).  
  *Evidence:* `docs/analysis-note/sec_5d.tex:225`.  
  *Resolution:* Those two rows are already in sec_execsummary.tex. Do not call $C_Z$ exploratory. This row authorizes no tex edit.

* **S1-COM-3 [R]** — **Fake-data bias in physical units.**  
  *Finding:* Tabulate per-cell bias in % and relative to reported $\\sigma$ for GiBUU hybrid and $q_3$ tilt in Table 18.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:225`, Table 18.  
  *Resolution:* This row authorizes no tex edit. Do not type per-cell bias values into Table 18 until each value is bound through the checked-values macros from a named readout.

* **S1-COM-4 [T]** — **$q_3$ truth in abstract vs omitted $q_3$ reweighting.**  
  *Finding:* Fig. 36 caption notes $q_3$ reweighting omitted because it did not implement intended change, while abstract cites synthetic $q_3$ tilt.  
  *Evidence:* `docs/analysis-note/main_note.tex:73`, Fig. 36 caption, `sec_fived16.tex:220`.  
  *Resolution:* Those are two different objects. Do not call the omitted reweighting exploratory. This row authorizes no tex edit.

* **S1-COM-5 [T]** — **Quantification of nonlinear cross-source terms.**  
  *Finding:* Executive summary names omitted nonlinear cross-terms as a methodological finding without quantification.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:19`, `sec_systematics.tex:180`, `sec_5d.tex:230`.  
  *Resolution:* Do not quote a trace ratio until it is bound through a checked-values macro from a named receipt. This row authorizes no tex edit.

* **S1-COM-6 [T]** — **Unexecuted or incomplete tests.**  
  *Finding:* Clarify status of tests that did not run (App. D response mismatch, §5.2 re-test, §10.5 16-cell coverage, §10.3 reco info).  
  *Evidence:* `docs/analysis-note/sec_validation.tex:160`, `app_response_mismatch.tex:4`.  
  *Resolution:* Do not label all four unexecuted. Each protocol keeps the status the note already gives it. This row authorizes no tex edit.

* **S1-COM-7 [T]** — **Unresolved items in 2D covariance.**  
  *Finding:* Document bounds: only 7 of 187 universes reproduced by committed code, NormDISCC zero, POT counting inferred.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:195`.  
  *Resolution:* This row authorizes no tex edit. Do not add those three statements until a record states each one.

* **S1-COM-8 [R]** — **Run-period block $C_{\\text{PL}}$ characterization.**  
  *Finding:* $C_{\\text{PL}}$ true-to-estimated $\\sigma$ ratio interval is 0.73–2.56; quote adopted uncertainty $Q = S_5 + C_{\\text{PL}}$ (median per bin 6.45%).  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:165`, Table 8; `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md`.  
  *Resolution:* The 6.45% clause is superseded. The headline uncertainty is $Q_R$, already printed by \uqMedian and \uqIntegral (`DECISION-20261024-joseph-adopt-re2-2d-refined.md:9`, `:30`). Do not put 6.45 back into the note. This row authorizes no tex edit.

* **S1-COM-9 [T]** — **Background normalization & composition.**  
  *Finding:* Tabulate composition of ~3% purity correction vs 0.35% genuine background.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:42`, `sec_method.tex:75`.  
  *Resolution:* The 0.35% genuine-background fraction is already in sec_experiment.tex. Do not add a 2.65% out-of-phase-space fraction until it is bound through a checked-values macro from a named record. This row authorizes no tex edit.

* **S1-COM-10 [T]** — **Own-covariance $\\chi^2$ vs publication.**  
  *Finding:* State $\\chi^2/\\text{ndf} = 22.29$ with own covariance against published result, alongside 2.27 with published covariance.  
  *Evidence:* `docs/analysis-note/sec_results.tex:125`, `app_statmethods.tex:520`.  
  *Resolution:* The published-covariance distance is already \chiPaper. Do not type 22.29. This row authorizes no tex edit until an own-covariance distance is bound through a checked-values macro and a record says it may be quoted.

* **S1-COM-11 [T]** — **Correlation sensitivity of 16-cell generator $\\chi^2$.**  
  *Finding:* Generator $\\chi^2$ drops sharply when flux correlations are shrunk or removed.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:185`, Table 22.  
  *Resolution:* This row authorizes no tex edit. Do not add that discussion until a record states the shrinkage and says the sentence may be quoted. The 16-cell covariance is not a benchmark yardstick.

* **S1-COM-12 [T]** — **Joint tests condition and nuisance model disclosure.**  
  *Finding:* Fine-grid convergence has not shown convergence (condition (i)). No hadronic-response nuisance band in declared nuisance model (§11.8; ±4% study moves observed statistics by up to ≈11% without regenerating null; compare the ≈11% hadronic-response shift with the NuWro total margin of observed 7427 against a null median 6324, and the GiBUU total margin of 2867 against 1791, table cells at `sec_joint.tex:287-288`). No rejection rate measured for null pseudo-data processed like data (§11.3). A1/A2 unproven. Calibration conditional on data-derived inputs (§11.2). CH-target correction makes NuWro total rejection not robust (§11.9).  
  *Evidence:* `docs/analysis-note/sec_joint.tex:120`, `:165`, `:210`, `:287-288`.  
  *Resolution:* This row authorizes no tex edit. Do not type 7427, 6324, 2867, or 1791 into new prose. Each condition keeps the status the note already gives it.

* **S1-COM-13 [T]** — **Extended-fiducial study uncertainties and envelope.**  
  *Finding:* No covariance; central value uses purity subtraction, not designated treatment. Three-prior envelope depends on NuWro-shaped prior built from flux-mis-sampled sample, not rebuilt after flux repair (§12.2). 28% of rate in tier 2 has only prior-spread envelope (±1.5% total cross section spread). Total uncertainty for $\\sigma_{\\text{ext}} = 4.502 \\times 10^{-38}$ is unquantified.  
  *Evidence:* `docs/analysis-note/sec_fps.tex:45-90`.  
  *Resolution:* That matrix row is already in sec_execsummary.tex. Do not type 4.502\times10^{-38}. This row authorizes no tex edit.

* **S1-COM-14 [T]** — **Ascencio et al. comparison uncertainties.**  
  *Finding:* Central values are 9.2% and 6.0% above Ascencio on two super-cells. Note says comparison "neither refutes nor validates". Ascencio's covariance is in hand, yet no uncertainty on the difference is given. At minimum, give Ascencio's own uncertainty on the two super-cells.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:185`.  
  *Resolution:* Do not tabulate new Ascencio uncertainties until each value is bound through a checked-values macro. This row authorizes no tex edit.

* **S1-COM-15 [T]** — **Reproducibility tolerances and archival completeness.**  
  *Finding:* Quoted central values reproducible only within float32 rounding spread (≈0.8 median, 2.6 max statistical SD under perturbations, §9.3); rerun tolerance should be stated. App. G package not deposited, repository/snapshot placeholders unfilled, 2D uncertainty and coverage figures not reproduced by it, 489 simulation AnaTuples have no preservation copy. Release schema marks 5-axis covariance as fixed identity despite failing criteria.  
  *Evidence:* `docs/analysis-note/sec_5d.tex:95`, `app_release.tex:25`.  
  *Resolution:* Do not edit app_release.tex. Do not add a reproducibility tolerance until a record states it. This row authorizes no tex edit.

### Section 5: Self-Containment

* **S1-CONT-1 [T]** — **Opaque citations to internal records document [37].**  
  *Finding:* Reference [37] cited by internal entry numbers (R1.1, R1.4, R1.14) for results required by reader.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:185`, `sec_5d.tex:160`.  
  *Resolution:* This row authorizes no tex edit. Do not inline those values until each one is bound through a checked-values macro and a record says it may be quoted.

* **S1-CONT-2 [T]** — **Dependence on internal joint test specification [52].**  
  *Finding:* Specification and decisions of joint tests cited from internal Ref. [52].  
  *Evidence:* `docs/analysis-note/sec_joint.tex:40`.  
  *Resolution:* This row authorizes no tex edit. Do not copy that specification into the note. The joint-test counts stay in the table.

* **S1-CONT-3 [T]** — **Dependencies on companion journal article definitions.**  
  *Finding:* Note invokes "companion journal article" for classifier definitions (Table 10), recovery figures, and printed values.  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:55`, `sec_5d.tex:142`, Table 20.  
  *Resolution:* This row authorizes no tex edit. Do not copy article text into the note.

* **S1-CONT-4 [T]** — **Reliance on superseded/retired records for numbers.**  
  *Finding:* Numbers quoted from superseded values (e.g., 0.28% and 0.18% in §4.7, A.4 split bootstrap).  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:215`, `app_statmethods.tex:430`.  
  *Resolution:* This row authorizes no tex edit. Do not remove or replace those figures until a named record identifies each as superseded and the replacement is a checked-values macro.

* **S1-CONT-5 [T]** — **Citations to private communications.**  
  *Finding:* Private communications cited for key methodology choices (pseudo-inverse convention, FrInel_pi degeneracy, McFarland suggestion).  
  *Evidence:* `docs/analysis-note/app_statmethods.tex:450`, `app_response_mismatch.tex:10`.  
  *Resolution:* This row authorizes no tex edit. Do not replace a private-communication citation with a rationale the note does not already state.

* **S1-CONT-6 [T]** — **App. G placeholders and unreleased RC7 package.**  
  *Finding:* Placeholder strings (`[repository] ... [snapshot identifier pending deposit]`) and unreleased package references.  
  *Evidence:* `docs/analysis-note/app_release.tex:25`.  
  *Resolution:* Do not edit app_release.tex while AUD-N4 is held. This row authorizes no tex edit.

* **S1-CONT-7 [T]** — **Reference to AI agent session replay for verification.**  
  *Finding:* Verification claim cites replay by "a separate AI agent session (Opus 5.5)".  
  *Evidence:* `docs/analysis-note/app_release.tex:45`.  
  *Resolution:* Do not edit app_release.tex while AUD-N4 is held. Do not replace the session citation with a claim of an automated verification pipeline. This row authorizes no tex edit.

### Section 6: Support for Claims

* **S1-CLM-1 [T]** — **Abstract 1% integral agreement without method-choice caveats.**  
  *Finding:* Abstract quotes 1% integral agreement without disclosing that LightGBM and background treatment were selected with published result known.  
  *Evidence:* `docs/analysis-note/main_note.tex:73`, `sec_method.tex:90`.  
  *Resolution:* Do not add that broader claim. This row authorizes no tex edit.

* **S1-CLM-2 [T]** — **"Comparable" uncertainty budget wording in §6.3.**  
  *Finding:* Claiming uncertainty budget is "comparable" to publication overlooks post hoc run-period addition and smaller bootstrap block.  
  *Evidence:* `docs/analysis-note/sec_results.tex:95`.  
  *Resolution:* Landed at 0da1dc3f7b4ab7b5bed1d851c2da45b22b81e30a. The budget sentence now says the combined budget differs from the published total in both directions. Do not add "not independently validated". No further tex edit.

* **S1-CLM-3 [T]** — **$(E_{\\text{avail}}, W)$ excess localization without covariance.**  
  *Finding:* Localizing excess at high $E_{\\text{avail}}$ and $W$ rests on biased purity estimator without evaluated joint covariance.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:13`, `sec_eavailw.tex:150`.  
  *Resolution:* The Tune v1 corner sentence was deleted at 904e1e99851b07ed883fcb53e5b64f3137eddeb0, and the fig:eavailWband caption clause at df56846001e9dc9522b8d0c21ce4d1043f45e138. The named-bin central-value ratios and the Valencia paragraph stay. This row authorizes no further tex edit.

* **S1-CLM-4 [T]** — **Generator $\\chi^2$ values sensitivity and interpretation.**  
  *Finding:* Generator $\\chi^2$ values presented as definitive tests despite extreme correlation sensitivity and circularity with $C_{\\text{model}}$.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:17`, `sec_fived16.tex:190`.  
  *Resolution:* Those statements are already in sec_execsummary.tex and sec_fived16.tex. Do not add "purely" or "assumed correlation models". This row authorizes no tex edit.

* **S1-CLM-5 [T]** — **"Calibrated joint tests reject all ten" scoping.**  
  *Finding:* Claiming tests are "calibrated" overlooks sub-grid non-convergence, omitted hadronic response, and target composition differences.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:16`, `sec_joint.tex:150`.  
  *Resolution:* Those statements are already in sec_execsummary.tex. Do not replace the six conditions with a new scope sentence. This row authorizes no tex edit.

* **S1-CLM-6 [T]** — **Joint tests as methodological illustration vs power measurement.**  
  *Finding:* Tests do not demonstrate added power over coarse projections; represent methodological demonstration.  
  *Evidence:* `docs/analysis-note/sec_joint.tex:210`.  
  *Resolution:* That sentence is already in sec_execsummary.tex. Do not add a claim that the tests do not demonstrate added power. This row authorizes no tex edit.

* **S1-CLM-7 [T]** — **3D, 4D, 5D unfolds reported as central values only.**  
  *Finding:* Higher-dimensional results lack valid covariances and represent illustrative central values.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:14`, `sec_3d.tex:100`.  
  *Resolution:* Do not relabel the 3D or 4D central values. This row authorizes no tex edit.

* **S1-CLM-8 [T]** — **3D marginal agreement: report shape scatter alongside total.**  
  *Finding:* Quoting 0.141% total agreement conceals 3.7% per-bin shape scatter and $\\chi^2/\\text{ndf} = 4.52$.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:14`, `sec_3d.tex:115`.  
  *Resolution:* Do not type those figures into the executive summary until each is a checked-values macro. This row authorizes no tex edit.

* **S1-CLM-9 [T]** — **Validation language vs descriptive feature recovery.**  
  *Finding:* Closure tests describe recovery of injected features, not formal statistical validation of the estimator.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:40`.  
  *Resolution:* This row authorizes no tex edit. The closure sentence already says these tests recover injected features and are not a formal statistical validation of the estimator, and that no non-closure uncertainty is assigned from them. Do not replace "validation" with "feature-recovery closure tests". Do not change that sentence. Do not restore "validate the estimator".

* **S1-CLM-10 [T]** — **Pion-FSI variation limits.**  
  *Finding:* Claim that pion-FSI cannot explain excess should be scoped strictly to the two dials varied.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:160`.  
  *Resolution:* That limit is already stated. This row authorizes no tex edit.

* **S1-CLM-11 [T]** — **Run-period block overlap wording.**  
  *Finding:* State that overlap between run-period differences and systematic errors is neither established nor excluded.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:180`.  
  *Resolution:* Those statements are already there. Do not add "distinct physical origin". This row authorizes no tex edit.

### Section 7: Minor Issues and Presentation

* **S1-PRES-1 [T]** — **Length and executive summary organization.**  
  *Finding:* Document is ~130 pages; executive summary is overly dense with inline citations.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:1-30`.  
  *Resolution:* Do not rewrite the executive summary in this row. The citability matrix stays. This row authorizes no tex edit.

* **S1-PRES-2 [T]** — **Repeated limitation lists across sections.**  
  *Finding:* Identical limitation paragraphs repeated verbatim in Introduction, ES, §10, and §13.  
  *Evidence:* Global text.  
  *Resolution:* This row authorizes no tex edit. Do not consolidate limitation paragraphs until a later instruction names two paragraphs that are the same text.

* **S1-PRES-3 [T]** — **Provenance narrative reading like a lab notebook.**  
  *Finding:* Chronological forensic notes ("decided during production", specific calendar dates) clutter physics text.  
  *Evidence:* `docs/analysis-note/sec_method.tex:95`, `sec_systematics.tex:190`.  
  *Resolution:* This row authorizes no tex edit. Do not move provenance sentences out of the body until a later instruction names them.

* **S1-PRES-4 [T]** — **Proliferation of configuration labels and unclear tables.**  
  *Finding:* Confusing proliferation of labels ((a)–(f), R, J, H2, EW, RD1–3, P1–P3).  
  *Evidence:* Table 2, Table 9.  
  *Resolution:* This row authorizes no tex edit. Do not add a glossary until its rows are copied from the configuration list already in sec_method.tex, one row per existing label, with no new claim.

* **S1-PRES-5 [T]** — **Table 3 missing column headers.**  
  *Finding:* Headers run together in Table 3.  
  *Evidence:* Table 3 in `sec_systematics.tex`.  
  *Resolution:* Those headers are already separate. This row authorizes no tex edit.

* **S1-PRES-6 [T]** — **Table layouts hard to follow (Tables 2, 6, 18).**  
  *Finding:* Ambiguous column pairings and alignments.  
  *Evidence:* Tables 2, 6, 18.  
  *Resolution:* This row authorizes no tex edit. Do not change a column pairing until a later instruction names the pairing that is wrong and the record for the correct one.

* **S1-PRES-7 [T]** — **Purity and stability terminology confusion.**  
  *Finding:* "Diagonal purity" vs "reconstruction stability" used inconsistently.  
  *Evidence:* Fig. 3 caption, `sec_fived16.tex:30`.  
  *Resolution:* This row authorizes no tex edit. Do not replace one term with the other until a record says they are the same quantity.

* **S1-PRES-8 [T]** — **Exponents of statistics in §3.2.**  
  *Finding:* Standard errors quoted on $\\sigma$ (4.1%) and variance (71%) without distinction.  
  *Evidence:* `docs/analysis-note/sec_method.tex:92`.  
  *Resolution:* This row authorizes no tex edit. The cited line is a comment. The 4.1% and 71% sentences already name the quantity each percentage applies to. Do not add an identification.

* **S1-PRES-9 [T]** — **Pseudo-inverse cutoff conventions (A.1 vs A.4).**  
  *Finding:* Cutoff quoted as $10^{-15} \\sigma_{\\max}$ in A.1 vs $10^{-10} \\lambda_{\\max}$ in A.4.  
  *Evidence:* `docs/analysis-note/app_statmethods.tex:85`, `:350`.  
  *Resolution:* This row authorizes no tex edit. The cited lines are not the cutoff sentences. The two cutoffs already name different operations. Do not add an explanation.

* **S1-PRES-10 [T]** — **Eq. (3) radical extraction.**  
  *Finding:* Missing radical sign on $W$ formula in some text extractions.  
  *Evidence:* `docs/analysis-note/sec_method.tex:110`.  
  *Resolution:* This row authorizes no tex edit. The cited line is a comment. The W formula already includes the square root. Do not change the formula.

* **S1-PRES-11 [T]** — **Unusual phrases to remove.**  
  *Finding:* Remove colloquialisms, AI agent references, and named suggestions.  
  *Evidence:* `docs/analysis-note/app_release.tex:45`, `app_response_mismatch.tex:10`.  
  *Resolution:* This row authorizes no tex edit. Do not edit app_release.tex. The cited response-mismatch line is an equation. Do not remove the private-communication citation or the RC1 session citation.

* **S1-PRES-12 [T]** — **Dense figures and missing uncertainty labels in captions.**  
  *Finding:* Descriptive figures (Figs. 19–23) lack error bars without explicit explanation in captions.  
  *Evidence:* Captions to Figs. 19–23.  
  *Resolution:* This row authorizes no tex edit. The first four captions already say uncertainties are not drawn because no covariance is quoted. The fifth is a ratio map, and the section already says no 4D uncertainty is reported. Do not add the proposed sentence.

* **S1-PRES-13 [T]** — **Mixed 2D and N-D degrees of freedom labeling.**  
  *Finding:* Clarify ndf = 205 in 2D vs retained rank in N-D at each quoted $\\chi^2$.  
  *Evidence:* `docs/analysis-note/sec_results.tex:120`, `sec_5d.tex:190`.  
  *Resolution:* This row authorizes no tex edit. The cited lines are not chi-squared statements. The 2D and sixteen-cell sections already state what their divisors count. Do not add an ndf sentence at every chi-squared citation.

* **S1-PRES-14 [T]** — **Inconsistent rounding across sections.**  
  *Finding:* Inconsistent precision (e.g., 0.13% vs 0.14%, 6.41% vs 6.414%).  
  *Evidence:* Global text.  
  *Resolution:* This row authorizes no tex edit. Do not change a printed precision until a later instruction names the two occurrences and the record for each rounding.

---

## Part 3: Sonnet Report 2 (`sonnet-note-r1-2.txt`)

### Section 3: Accuracy

* **S2-ACC-1 [T]** — **"At least fifteen-fold" is false on its own numbers.** Same finding as S1-ACC-9.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-ACC-9, which has landed. Do not restore "at least fifteen-fold."
* **S2-ACC-2 [R]** — **Tune v1 normalization deficit quoted four ways.** Same finding as S1-ACC-2.  
  *Resolution:* This row authorizes no tex edit. The four quotes are different comparisons. Do not replace them with one macro.
* **S2-ACC-3 [T]** — **Tune v1 in quasielastic–Δ dip inconsistency.** Same finding as S1-ACC-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-ACC-1, which has landed. Do not restore the dip under-prediction sentence, and do not add a localization claim.
* **S2-ACC-4 [T]** — **Which coverage test "did not run to a result".** Same finding as S1-ACC-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-ACC-4, which has landed. The abstract already names the two tests separately. Do not merge them.
* **S2-ACC-5 [T]** — **Detector-response-mismatch closure status.**  
  *Finding:* §5 says "not run", while App. D reports shifted response closures with $|\\Delta|/\\sigma$ up to 0.97.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:35`, `app_response_mismatch.tex:12`.  
  *Resolution:* This row authorizes no tex edit. The rescaling test and the shifted-response closures already have separate statuses. Do not call the shifted-response closures exploratory, and do not say they did not run.
* **S2-ACC-6 [D]** — **Count of bands that failed pairing.** Same finding as S1-ACC-8.  
  *Resolution:* **DISPUTE.** Class [D]. At base `b1da7ba8` (`sec_fived16.tex:66-72`), "These five enter" follows the paired terms: the systematic bands, the lateral shifts, the normalization, the run-period terms, and the $C_{\text{model}}$ shifts. The statistical correlation is the part that is not measured. Do not change "five" to "four".
* **S2-ACC-7 [T]** — **Band counts and classifications across sections.**  
  *Finding:* 44 evaluated systematic bands plus 1 global normalization; clarify GEANT FSI lateral treatment.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:35`, `app_statmethods.tex:210`.  
  *Resolution:* This row authorizes no tex edit. The two band counts and the GEANT FSI laterals are already distinguished. Do not collapse the counts into one number.
* **S2-ACC-8 [T]** — **ndf in held-out-tune test (204 vs 205).**  
  *Finding:* §5.3 gives $\\chi^2/\\text{ndf}$ "(ndf = 204)" at AR23 and "(ndf = 205)" at G18 without explanation.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:198`.  
  *Resolution:* This row authorizes no tex edit. Do not write that a kinematically inaccessible cell was excluded. The two ndf macros already print 204 and 205.
* **S2-ACC-9 [R]** — **Positive control window in §5.2.**  
  *Finding:* 0.955 lies inside stated window $C_2 \\in [0.928, 0.972]$; check window endpoint arithmetic.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:155`.  
  *Resolution:* This row authorizes no tex edit. The window endpoints match the stated formula. Do not change them. The 0.955 is the high control point, not an endpoint.
* **S2-ACC-10 [T]** — **Run-period effect on 2D median.**  
  *Finding:* §6.3 states run-period block raises per-bin median from 5.98% to 6.41% (+7%), while Table 3 says median ratio is 5.8%.  
  *Evidence:* `docs/analysis-note/sec_results.tex:90`, Table 3.  
  *Resolution:* This row authorizes no tex edit. The two medians and the median of the per-bin increases are already stated separately. Do not add a ratio of the two medians.
* **S2-ACC-11 [T]** — **Repeated numbers that may be copy errors.** Same finding as S1-ACC-12.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-ACC-12. The listed pairs stay as written until a readout shows that the two numbers in a pair are the same quantity.
* **S2-ACC-12 [T]** — **2p2h closure arithmetic in §7.7.** Same finding as S1-ACC-19.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-ACC-19. Do not identify 2.87% of the CC total with 45% of QE.
* **S2-ACC-13 [T]** — **Size of background correction.** Same finding as S1-COM-9.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-COM-9. Do not add a 2.65% out-of-phase-space fraction.
* **S2-ACC-14 [T]** — **Flux units and integration bounds.**  
  *Finding:* Formula in §3.4 uses $\\text{m}^2$, text uses $\\Phi = 6.243 \\times 10^{-8}\\text{ cm}^{-2}$; per-$p_T$ flux integral vs 0–100 GeV integrated flux.  
  *Evidence:* `docs/analysis-note/sec_method.tex:125`.  
  *Resolution:* This row authorizes no tex edit. The unit conversion and the two flux integrals are already stated. Do not add another conversion.
* **S2-ACC-15 [T]** — **Cross-checks description in §3.2.**  
  *Finding:* §3.2 mentions MLP/transformer cross-checks in §7.5, but §7.5 contains only Keras MLP, and App. F notes no transformer result is used.  
  *Evidence:* `docs/analysis-note/sec_method.tex:90`, `sec_3d.tex:130`.  
  *Resolution:* Landed in this commit. The method sentence now says MLP cross-checks. The point-cloud transformer study is unchanged.
* **S2-ACC-16 [T]** — **"Differ in learner" description in §7.3.**  
  *Finding:* 3D marginal (e) and 2D result (f) are both LightGBM, differing in seed and refinement capacity, not learner family.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:115`.  
  *Resolution:* This row authorizes no tex edit. Do not say the two results differ in learner capacity. Both are LightGBM and the table says both use the same refinement.
* **S2-ACC-17 [T]** — **Marginal checks agreement overstated in executive summary.** Same finding as S1-ACC-7.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-ACC-7, which has landed. Do not add further marginal percentages to the executive summary.
* **S2-ACC-18 [T]** — **5D bin count definitions.**  
  *Finding:* "10,694 reported bins" undefined; distinguish dense grid (65,856), occupied cells (10,499), and 4D projections (4,830).  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:210`, `sec_5d.tex:150`.  
  *Resolution:* This row authorizes no tex edit. The counts already name different objects. Do not identify 4830 with 4825, and do not add a combined definition.
* **S2-ACC-19 [T]** — **Model-dependence magnitudes.**  
  *Finding:* Table 5 quotes median 2–6% for held-out shapes, §9.4 quotes prior dependence of 10–13% per coarse cell.  
  *Evidence:* `docs/analysis-note/sec_5d.tex:145`, Table 5.  
  *Resolution:* This row authorizes no tex edit. The two percentages already name different studies. Do not add a further label.
* **S2-ACC-20 [T]** — **GiBUU domain cutoffs.**  
  *Finding:* $p_\\parallel < 4.5\\text{ GeV/c}$ in 16-cell vs $< 6\\text{ GeV/c}$ in joint tests.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:165`, `sec_joint.tex:55`.  
  *Resolution:* This row authorizes no tex edit. Each section already states its GiBUU domain and the neutrino-energy limit. Do not treat the two edges as one cutoff.
* **S2-ACC-21 [T]** — **Extended fiducial bin counts and fractions.**  
  *Finding:* 185 vs 205 published cells; $\\sigma_{\\text{ext}}/\\text{control} = 4.502/3.073 = 68\\%$ vs 66.4% MC.  
  *Evidence:* `docs/analysis-note/sec_fps.tex:45-80`.  
  *Resolution:* This row authorizes no tex edit. The 66.4% and the 185 cells already name their own quantities. Do not type 4.502, and do not identify 185 with 205.
* **S2-ACC-22 [T]** — **App. C.5 vs Table 8 ensemble variance.**  
  *Finding:* Negative-weight rebuild has $\\sqrt{\\text{Tr} C} = 2.98 \\times 10^{-39}$ vs Table 8 $2.69 \\times 10^{-39}$.  
  *Evidence:* `docs/analysis-note/app_negweight.tex:85`, Table 8.  
  *Resolution:* This row authorizes no tex edit. The two traces already name different ensembles. Do not identify them.
* **S2-ACC-23 [T]** — **Terminology mismatch across sections.** Same finding as S1-ACC-15.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-ACC-15. Do not merge the two descriptions of the 109 cells.
* **S2-ACC-24 [T]** — **Minor numerical mismatches.**  
  *Finding:* Reconcile $p_T$ peak ranges (0.7 vs 0.55–0.70 vs ~0.6), GiBUU carbon $\\chi^2$ (45.49 vs 45.25), and 1G–1M $p_\\parallel$ $\\chi^2$ (34.4 vs 34.8).  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:45`, `sec_fived16.tex:185`, `sec_systematics.tex:168`.  
  *Resolution:* This row authorizes no tex edit. The three pairs already name different quantities. Do not reconcile them.

### Section 4: Completeness as a Citable Record

* **S2-COM-1 [T]** — **Unquantified "methodological finding" on nonlinear cross-terms.** Same finding as S1-COM-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-COM-5. Do not quote a trace ratio until it is a checked macro.
* **S2-COM-2 [R]** — **Configuration-(a) 5D covariance exceeds seed-sensitivity limit.**  
  *Finding:* Configuration-(a) 5D covariance exceeds its predeclared stability limit ($s_{\\text{proj}} = 6.145\\%$ against the $5\\%$ bound, with 5 of 45 seed-pinned bands unmeasured in either direction, and pre-production null bound not met).  
  *Evidence:* `VALIDATION_LEDGER.md` `VL142`–`VL144`, `docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`, `CORRECTION-20260920-lower-bound-inference-withdrawn.md`, `OPERATIVE-SHEET-scalar5d.md`.  
  *Resolution:* The disclosure, when it is drafted, uses the adoption's words. M1 is s_proj = 6.145% against a 5% bound (DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:57). M3 (:73-79) says the seed variation does not probe those five bands, and the effect on the total when they also vary has not been measured. The lower-bound reading is withdrawn (CORRECTION-20260920-lower-bound-inference-withdrawn.md). The note must not say "five bands unmeasured" and must not type 6.145. This row authorizes no tex edit.
* **S2-COM-3 [T]** — **Learner and configuration dependence table.**  
  *Finding:* Consolidate algorithmic variations (exact-split vs LightGBM, seed shifts, MLP vs GBDT) into a unified summary table.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:115`.  
  *Resolution:* This row authorizes no tex edit. The estimator configurations already have a table. Do not add a second one.
* **S2-COM-4 [T]** — **Joint test condition (i) disclosure.**  
  *Finding:* Condition (i) fine-grid convergence unmeasured; disclose sub-grid residual limits.  
  *Evidence:* `docs/analysis-note/sec_joint.tex:120`.  
  *Resolution:* This row authorizes no tex edit. Condition (i) already says the below-grid residual is unmeasured and unbounded by the scan. Do not add a bound.
* **S2-COM-5 [T]** — **Joint tests omit hadronic response nuisance.**  
  *Finding:* Response model not shown to be complete; $\\pm 4\\%$ study did not regenerate nulls.  
  *Evidence:* `docs/analysis-note/sec_joint.tex:165`.  
  *Resolution:* This row authorizes no tex edit. The omission of a hadronic-response band, and the fact that the 4% study did not regenerate the nulls, are already stated. Do not add a further disclosure.
* **S2-COM-6 [T]** — **Offset control check failure disclosure.**  
  *Finding:* Offset check gives $\\chi^2 = 245.74$ for 16 ndf; disclose failure and implications.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:240`.  
  *Resolution:* This row authorizes no tex edit. The offset-check failure and its consequence are already stated through the macro. Do not type 245.74.
* **S2-COM-7 [T]** — **Sixteen-cell output algorithm dependence and stability.** Same finding as S1-COM-3 / AUD-N2 / REF-G1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-COM-3 and AUD-N2. The algorithm dependence is already stated, and no per-cell bias values are added.
* **S2-COM-8 [T]** — **No 3D/4D uncertainty; no 3D/4D generator $\\chi^2$.**  
  *Finding:* 3D and 4D central values used for generator comparisons without evaluated covariance.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:145`, `sec_eavailw.tex:140`.  
  *Resolution:* This row authorizes no tex edit. The comparisons are already called descriptive central values, with no 3D or 4D covariance and no generator chi-squared. Do not add purely.
* **S2-COM-9 [T]** — **Ascencio et al. comparison unresolved.**  
  *Finding:* Data sit 9.2% and 6.0% above Ascencio on super-cells, confounded by differing $E_{\\text{avail}}$ definitions.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:185`.  
  *Resolution:* This row authorizes no tex edit. The differences, the definition shift, and the absence of a chi-squared are already stated. Do not tabulate new uncertainties.
* **S2-COM-10 [T]** — **Hidden-variable closure fails at largest amplitude.**  
  *Finding:* Hidden-variable closure fails at $A = 0.30$; injected bump closures have narrow passes or no predeclared thresholds.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:170`.  
  *Resolution:* This row authorizes no tex edit. The A=0.30 failure and the narrow or unthresholded closures are already stated. Do not add a further discussion.
* **S2-COM-11 [T]** — **Purity-subtracted central value in use in 5D.**  
  *Finding:* Config-(a) 5D value retains known purity background bias (8–12$\\sigma$ stat at high $W$).  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:130`, App. C.8.  
  *Resolution:* This row authorizes no tex edit. The purity bias in the highest-W column is already stated, as 0.36--1.07 standard deviations of the configuration-(a) total uncertainty. Do not type 8--12.
* **S2-COM-12 [T]** — **Unverified items admitted in text.** Same finding as S1-COM-7.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-COM-7. Do not add those three statements until a record states each one.
* **S2-COM-13 [T]** — **Reproduction is not possible.** Same finding as S1-CONT-6.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-6. Do not edit app_release.tex while AUD-N4 is held.
* **S2-COM-14 [T]** — **Fake-data tests are not held-out truths.** Same finding as S1-COM-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-COM-3. Do not type per-cell bias values, and do not add a sentence that the fake-data tests are not held-out truths.
* **S2-COM-15 [T]** — **Extended fiducial prior envelope.**  
  *Finding:* Tier-2 prior envelope has median 7.9% (90th percentile 62%) with no covariance.  
  *Evidence:* `docs/analysis-note/sec_fps.tex:85`.  
  *Resolution:* This row authorizes no tex edit. The preliminary status, the absence of a covariance, and the 7.9% and 62% envelope are already stated. Do not add a further label, and do not type 4.502.

### Section 5: Self-Containment

* **S2-CONT-1 [T]** — **Ref. [52] specification and decisions.** Same finding as S1-CONT-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-2. Do not copy that specification into the note. The joint-test counts stay in the table.
* **S2-CONT-2 [T]** — **Diagnostic record cited for definitions.** Same finding as S1-CONT-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-1. Do not inline those values until each one is a checked macro and a record says it may be quoted.
* **S2-CONT-3 [T]** — **Companion journal article dependencies.** Same finding as S1-CONT-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-3. Do not copy article text into the note.
* **S2-CONT-4 [T]** — **Numbers quoted from superseded/retired material.** Same finding as S1-CONT-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-4. Do not remove or replace those figures until a named record identifies each as superseded and the replacement is a checked macro.
* **S2-CONT-5 [T]** — **Internal design review factor derivation.** Same finding as S1-CONT-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-2. Do not copy that specification into the note, and do not add a derived factor. The joint-test counts stay in the table.
* **S2-CONT-6 [T]** — **Repository paths and file names in text.** Same finding as S1-CONT-6.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-6. Do not edit app_release.tex while AUD-N4 is held.
* **S2-CONT-7 [T]** — **Citations to private communications.** Same finding as S1-CONT-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-5. Do not replace a private-communication citation with a rationale the note does not already state.
* **S2-CONT-8 [T]** — **Internal stage/date jargon.**  
  *Finding:* Avoid internal milestone dates and phrases ("Stage 0", "condition set in July 2026").  
  *Evidence:* `docs/analysis-note/sec_5d.tex:135`, `sec_fived16.tex:210`.  
  *Resolution:* This row authorizes no tex edit. The sentence already names the three conditions. Do not replace the July 2026 parenthetical, and do not edit the Stage 0 comments.
* **S2-CONT-9 [T]** — **Repository labels used before defined.** Same finding as S1-PRES-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-PRES-4. Do not add a glossary until its rows are copied from the configuration list already in sec_method.tex, one row per existing label, with no new claim.

### Section 6: Support for Claims

* **S2-CLM-1 [T]** — **Abstract 1% integral agreement.** Same finding as S1-CLM-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CLM-1. Do not add that broader claim.
* **S2-CLM-2 [T]** — **Calibrated joint tests reject all ten.** Same finding as S1-CLM-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CLM-5. Do not replace the six conditions with a new scope sentence.
* **S2-CLM-3 [T]** — **Generator localization without covariance.** Same finding as S1-CLM-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CLM-3, which has landed. Do not restore the corner sentence, and do not add a localization claim.
* **S2-CLM-4 [T]** — **Closure validation claims.**  
  *Finding:* §5 claims "These closure tests validate the estimator", but 5D generator closure fails and hidden-variable closure fails at $A = 0.30$.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:30`.  
  *Resolution:* This row authorizes no tex edit. The sentence already says the closure tests are not a formal statistical validation. Do not restore "validate the estimator," and do not add a new failure claim.
* **S2-CLM-5 [T]** — **$n=5$ iterations justified empirically.**  
  *Finding:* $n=5$ empirical justification based only on total cross section is incomplete given shape drift.  
  *Evidence:* `docs/analysis-note/sec_method.tex:85`.  
  *Resolution:* This row authorizes no tex edit. The total agreement and the shape difference are already stated in the section the method paragraph cites. Do not add a dimensional-sensitivity claim.
* **S2-CLM-6 [T]** — **Sixteen-cell median uncertainty (7.86%).** Same finding as S1-CLM-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CLM-2, which has landed. Do not add "not independently validated," and do not type 7.86.
* **S2-CLM-7 [T]** — **"Methodological finding" on nonlinear cross-source terms.** Same finding as S1-COM-5 / S1-CLM-9.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-COM-5. Do not quote a trace ratio until it is a checked macro, and do not replace the closure sentence.
* **S2-CLM-8 [T]** — **A.5 direct evidence of implicit regularization.**  
  *Finding:* App. A.5 claims direct evidence that ~1 $\\chi^2$ unit is due to implicit regularization rather than physics disagreement.  
  *Evidence:* `docs/analysis-note/app_statmethods.tex:545`.  
  *Resolution:* Landed in this commit. The sentence no longer calls the estimator gap direct evidence of regularization rather than physics. The chi-squared values stay.
* **S2-CLM-9 [T]** — **Five-dimensional unfolding adds information.**  
  *Finding:* Reconstructed $W$ is an exact algebraic function of $(p_T, p_\\parallel, q_3)$; added information of $W$ unmeasured.  
  *Evidence:* `docs/analysis-note/sec_method.tex:115`, `sec_eavailw.tex:40`.  
  *Resolution:* This row authorizes no tex edit. The kinematic relation and the unmeasured added information are already stated, including the clamp. Do not drop the clamp.

### Section 7: Minor Issues and Presentation

* **S2-PRES-1 [T]** — **Length and executive summary organization.** Same finding as S1-PRES-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-PRES-1. Do not rewrite the executive summary. The citability matrix stays.
* **S2-PRES-2 [T]** — **Heavy repetition of caveats.** Same finding as S1-PRES-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-PRES-2. Do not consolidate limitation paragraphs until a later instruction names two paragraphs that are the same text.
* **S2-PRES-3 [T]** — **Appendix figures/tables numbering and splitting across pages.**  
  *Finding:* Fix figures/tables numbered after use or split awkwardly across pages (Figs. 36, 37; Tables 3, 6, 13, 16, 18).  
  *Evidence:* Global formatting.  
  *Resolution:* This row authorizes no tex edit. Do not run a global float cleanup. The named figures and tables are layout comments on a built PDF. No one of them is identified as a broken float in the source. Do not move floats, and do not reformat a table.
* **S2-PRES-4 [T]** — **Fig. 9 prints per-panel $\\chi^2$ from weight statistics.**  
  *Finding:* Fig. 9 prints misleading per-panel $\\chi^2$ computed from MC weight statistics alone.  
  *Evidence:* Caption and annotations on Fig. 9.  
  *Resolution:* This row authorizes no tex edit. The caption already says the annotated per-panel chi-squared uses only the weight statistics of the reweighted simulated sample and is a descriptive scale. Do not remove the annotated values.
* **S2-PRES-5 [T]** — **Fig. 7 error bars are MC weight statistics.**  
  *Finding:* Headline figure error bars are MC weight statistics, not experimental uncertainties.  
  *Evidence:* Caption to Fig. 7.  
  *Resolution:* This row authorizes no tex edit. The Fig. 7 caption already says the vertical error bars are the weight statistics of the reweighted simulated sample, and that they are neither the data's statistical uncertainty nor the reported covariance. Do not add a further explanation.
* **S2-PRES-6 [T]** — **Fig. 23 colorbar reads `data/GENIE` instead of `data/Tune v1`.**  
  *Finding:* Mislabeled denominator on Fig. 23 colorbar.  
  *Evidence:* Fig. 23 graphic and caption.  
  *Resolution:* This row authorizes no tex edit. Do not relabel the figure. The caption already says the ratio is data/Tune v1 and that the figure prints data/GENIE. The denominator is the tune-weighted prior.
* **S2-PRES-7 [T]** — **Statements citing AI agent session replay.** Same finding as S1-CONT-7.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-7. Do not edit app_release.tex while AUD-N4 is held. Do not replace the session citation with a claim of an automated verification pipeline.
* **S2-PRES-8 [T]** — **Dates, internal job labels, file names in text.** Same finding as S1-PRES-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-PRES-3. Do not move provenance sentences out of the body until a later instruction names them.
* **S2-PRES-9 [T]** — **Terminology used before defined.** Same finding as S1-PRES-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-PRES-4. Do not add a glossary until its rows are copied from the configuration list already in sec_method.tex, one row per existing label, with no new claim.
* **S2-PRES-10 [T]** — **Figure-based numbers cited without tables.**  
  *Finding:* Text quotes numbers read from figures (e.g., Fig. 23 ratios) without supporting tables.  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:150`.  
  *Resolution:* This row authorizes no tex edit. Do not add a table of the figure ratios, and do not relabel them as visual estimates. The cited line is a source comment. The named ratios stay until each is a checked macro.

---

## Part 4: Gemini Report 1 (`gemini-note-r1-1.txt`)

### Section 3: Accuracy

* **G1-ACC-1 [T]** — **Inconsistent fiducial nucleon count.**  
  *Finding:* Fiducial target nucleon count is quoted as $N = 4.123 \\times 10^{30}$ in §3.4 and $4.128 \\times 10^{30}$ in §8.2.  
  *Evidence:* `docs/analysis-note/sec_method.tex:128`, `sec_eavailw.tex:50`.  
  *Resolution:* This row authorizes no tex edit. The cited 4.123e30 and 4.128e30 are not in the note. The printed counts are 3.2353e30 and 3.235e30, two roundings of the same tracker-geometry constant. Do not harmonize them to a typed standard value.
* **G1-ACC-2 [T]** — **Discrepancy in raw run-period $\\chi^2$.**  
  *Finding:* Raw run-period $\\chi^2 = 209.6$ in §4.5 vs $205.8$ in Table 3.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:165`, Table 3.  
  *Resolution:* This row authorizes no tex edit. The cited 209.6 and 205.8 are not in the note. Table 3 does not quote a run-period chi-squared. Do not reconcile a run-period chi-squared to a value from values.tex.
* **G1-ACC-3 [T]** — **Inconsistent degrees of freedom in held-out-tune test.** Same finding as S2-ACC-8.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-ACC-8. Do not write that a kinematically inaccessible cell was excluded. The two ndf macros already print 204 and 205.
* **G1-ACC-4 [T]** — **Marginal normalization check agreement overstated in Executive Summary.** Same finding as S1-ACC-7 / S2-ACC-17.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-ACC-17. The executive summary no longer says the marginal checks pass to 1-2%. Do not add further marginal percentages to the executive summary.
* **G1-ACC-5 [T]** — **Discrepancy between systematic median uncertainty in text and Table 8.**  
  *Finding:* Systematic median uncertainty quoted as 5.14% in §4.1 vs 5.38% in Table 8.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:45`, Table 8.  
  *Resolution:* This row authorizes no tex edit. The cited 5.14% and 5.38% are not in the note. The cited line is a source comment. Do not harmonize a median uncertainty to a value from values.tex.
* **G1-ACC-6 [D]** — **Neutral pion mass subtraction for charged pions in Eq. (1).**  
  *Finding:* Referee questions $(E_{\\pi^\\pm} - m_{\\pi^0})$ in $E_{\\text{avail}}$ definition as unphysical.  
  *Resolution:* This row authorizes no tex edit. The subtraction is the inherited 135 MeV constant, and the note already says there is no unique published definition. Do not call it unphysical, and do not add a sentence that it is the published definition.
* **G1-ACC-7 [T]** — **Massless-lepton approximation in Table 10.**  
  *Finding:* Table 10 lists $Q^2 = 4 E_\\nu E_\\mu \\sin^2(\\theta/2)$, which is ultra-relativistic approximation ($m_\\mu = 0$).  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:55`, Table 10.  
  *Resolution:* This row authorizes no tex edit. The truth-W cell already prints the massless formula the implementation uses. The sentence before the table already says exact Q^2 is the four-vector quantity and that truth W uses the massless-muon Q^2. Do not replace the implemented formula.
* **G1-ACC-8 [T]** — **Exact-split estimator reproducibility description.**  
  *Finding:* Reconcile "unseeded reproducible to $7 \\times 10^{-15}$" with "reseeding moves bins by up to 1.6%".  
  *Evidence:* `docs/analysis-note/sec_method.tex:98`.  
  *Resolution:* This row authorizes no tex edit. The paragraph already separates the unseeded regeneration from the one reseeded run. The spread over seeds is already said to be unmeasured. Do not add a further sentence.
* **G1-ACC-9 [T]** — **GiBUU cell count reconciliation.**  
  *Finding:* 8 cells in §10 vs 72 cells in Table 11.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:18`, Table 11.  
  *Resolution:* This row authorizes no tex edit. The 8 cells are the sixteen-cell comparison below the mid-p_parallel cut. The 72 cells are the joint-test domain with p_parallel below 6 GeV/c. They are not one grid. Do not call 72 the full grid.

### Section 4: Completeness as a Citable Record

* **G1-COM-1 [T]** — **The 5D coverage test did not produce a result.** Same finding as S1-ACC-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-ACC-4. The abstract already names the two tests separately. Do not merge them.
* **G1-COM-2 [T]** — **Detector-response-mismatch closure test is unexecuted.** Same finding as S2-ACC-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-ACC-5. The rescaling test and the shifted-response closures already have separate statuses. Do not call the shifted-response closures exploratory, and do not say they did not run.
* **G1-COM-3 [T]** — **Complete absence of 3D and 4D uncertainty quantification.** Same finding as S2-COM-8.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-COM-8. The comparisons are already called descriptive central values, with no 3D or 4D covariance and no generator chi-squared. Do not add purely.
* **G1-COM-4 [T]** — **Headline 5D central value retains known-biased purity background subtraction.** Same finding as S2-COM-11.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-COM-11. The purity bias in the highest-W column is already stated, as 0.36-1.07 standard deviations of the configuration-(a) total uncertainty. Do not type 8-12.
* **G1-COM-5 [R]** — **The 5-axis covariance ($C_Z$) exceeds pre-declared stability thresholds.** Same finding as S2-COM-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-COM-2. Do not edit that row. The note must not say "five bands unmeasured" and must not type 6.145.
* **G1-COM-6 [T]** — **Uncorrected playlist pooling bias.**  
  *Finding:* Global exposure ratio induces $-1.83\\%$ to $+3.78\\%$ single-cell pooling bias.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:202`.  
  *Resolution:* This row authorizes no tex edit. The systematics section already says the twelve playlists are combined with one global exposure ratio, that the resulting bias is not corrected, and that single cells differ by -1.83% to +3.78%. Do not add a further disclosure.
* **G1-COM-7 [R]** — **Ad hoc construction of run-period covariance block ($C_{\\text{PL}}$).** Same finding as S1-COM-8.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-COM-8. The 6.45% clause is superseded. The headline uncertainty is Q_R, already printed by the median and integral macros. Do not put 6.45 back into the note.
* **G1-COM-8 [T]** — **NormDISCC systematic category carried as unverified zero.**  
  *Finding:* NormDISCC carried as zero without confirmation.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:198`.  
  *Resolution:* This row authorizes no tex edit. The systematics section already says NormDISCC is identically zero, that it is carried as zero, and that this has not been confirmed as intended. Do not add a further sentence.
* **G1-COM-9 [T]** — **Numerical instability under float32 rounding.** Same finding as S2-COM-3 / AUD-E6.  
  *Resolution:* This row authorizes no tex edit. The float32 rounding mechanism is already stated in sec_5d.tex, including the tie-breaking and the refinement entry. AUD-E6 records that draft. Do not add a second account. Do not apply the S2-COM-3 table instruction to this row.

### Section 5: Self-Containment

* **G1-CONT-1 [T]** — **Heavy reliance on inaccessible internal records ("Ref. [37]").** Same finding as S1-CONT-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-1. Do not inline those values until each one is bound through a checked-values macro and a record says it may be quoted.
* **G1-CONT-2 [T]** — **Citations to private communications with anomalous dates.** Same finding as S1-CONT-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-5. Do not replace a private-communication citation with a rationale the note does not already state.
* **G1-CONT-3 [T]** — **Lost run logs and unrecorded configurations.** Same finding as S2-COM-3.  
  *Resolution:* This row authorizes no tex edit. The exact-split paragraph already says the seed was not fixed and the run log was not found. Do not add a further sentence. Do not apply the S2-COM-3 table instruction as a new table.
* **G1-CONT-4 [T]** — **Incomplete mathematical definition of reconstructed available energy.** Same finding as S2-COM-9.  
  *Resolution:* This row authorizes no tex edit. The table already states reconstructed E_avail as 1.17 times the calorimetric recoil energy in the tracker and electromagnetic calorimeter, with muon deposits removed. Do not replace that implemented definition. Do not apply the S2-COM-9 instruction to add Ascencio uncertainties.

### Section 6: Support for Claims

* **G1-CLM-1 [T]** — **Claim of "reproducing" the published cross section.** Same finding as S1-CLM-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CLM-1. Do not add the broader claim that the background treatment was selected with the published result known.
* **G1-CLM-2 [T]** — **Claim that native OmniFold miss handling requires no efficiency correction.**  
  *Finding:* OmniFold handles misses via Step 1 reweighting without explicit efficiency divisor.  
  *Evidence:* `docs/analysis-note/sec_method.tex:60`.  
  *Resolution:* This row authorizes no tex edit. The method section already says misses receive step-1 weights from a regressor, that this requires no separate efficiency correction, and that a later efficiency-histogram division would double-correct. Do not add a further derivation.
* **G1-CLM-3 [T]** — **Claim that GBDTs match or outperform neural networks for this application.**  
  *Finding:* Claim that GBDTs outperform neural networks is supported only by limited MLP checks.  
  *Evidence:* `docs/analysis-note/sec_method.tex:80`, `sec_3d.tex:135`.  
  *Resolution:* This row authorizes no tex edit. The method sentence cites the tabular-data result for match or outperform, and it already says the trees train deterministically and far faster on CPU. The 3D cross-check reports agreement between the two families. Do not add a claim that the GBDT was superior in this analysis.
* **G1-CLM-4 [T]** — **Claim that low-$E_{\\text{avail}}$ excess confirms established low-recoil excess.** Same finding as S1-CLM-3 / S2-CLM-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-CLM-3. Do not restore the corner sentence, and do not add a localization claim.
* **G1-CLM-5 [T]** — **Claim of rejecting generator predictions in §11.** Same finding as S1-CLM-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CLM-5. Do not replace the six conditions with a new scope sentence.

### Section 7: Minor Issues and Presentation

* **G1-PRES-1 [T]** — **Anomalous and future dates.** Same finding as S1-PRES-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-PRES-3. Do not move provenance sentences out of the body until a later instruction names them.
* **G1-PRES-2 [T]** — **Patchwork presentation of configurations.** Same finding as S1-PRES-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-PRES-4. Do not add a glossary until its rows are copied from the configuration list already in sec_method.tex, one row per existing label, with no new claim.
* **G1-PRES-3 [T]** — **Misleading error bar conventions in figures.** Same finding as S2-PRES-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-PRES-5. The Fig. 7 caption already says the vertical error bars are the weight statistics of the reweighted simulated sample, and that they are neither the data's statistical uncertainty nor the reported covariance. Do not add a further explanation.
* **G1-PRES-4 [T]** — **Hadronic catch bin compression.**  
  *Finding:* Explain catch bin handling in kinematic distributions.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:55`.  
  *Resolution:* This row authorizes no tex edit. The control-plot caption already says the wide hadronic catch bins extend to 100 GeV and are compressed at each panel's right edge. The corner-plot caption already says those bins are dropped. The reporting edges are already in sec_method.tex. Do not add a further sentence.
* **G1-PRES-5 [T]** — **Inconsistent kinematic notation ($p_\\parallel$ vs $p_z$).**  
  *Finding:* Longitudinal momentum denoted interchangeably as $p_\\parallel$, $p_z$, `p_||`.  
  *Evidence:* Figures 5, 17, 18, text.  
  *Resolution:* This row authorizes no tex edit. Do not run a global notation sweep. The note body already uses \pPar. The Cartesian p_z in sec_pet.tex is a particle momentum component and must not be renamed. The mismatches are inside the installed figures: Figure 5 uses $p_{||}$ and "row-major pT,pz", Figure 17 prints "p_|| bin", and Figure 18 titles a panel "(b) pz". Do not regenerate those figures in this commit.
* **G1-PRES-6 [T]** — **Incomplete table entries.**  
  *Finding:* Missing entries or blank cells in summary tables.  
  *Evidence:* Table 2, Table 6.  
  *Resolution:* This row authorizes no tex edit. Tables 2 and 6 have no blank cells. Do not populate them. The em dashes in Table 3 (tab:pl-added) stay. Do not fill them with numbers. No record quoted in the note gives a variance share for those two maximum rows. Do not add a footnote that states a cause for the dashes.
* **G1-PRES-7 [T]** — **Confusing label conventions in Figure 23.** Same finding as S2-PRES-6.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-PRES-6. Do not relabel the figure. The caption already says the ratio is data/Tune v1 and that the figure prints data/GENIE. The denominator is the tune-weighted prior.
* **G1-PRES-8 [T]** — **Missing units on corner plot axes.**  
  *Finding:* Figure 2 lacks units on several sub-axes.  
  *Evidence:* Fig. 2 graphic.  
  *Resolution:* This row authorizes no tex edit. Do not regenerate the figure. The installed corner plot already prints units on its axis labels: p (GeV/c), E_avail (GeV), q_3 (GeV), p_T (GeV/c), and W (GeV). Do not add degrees.
* **G1-PRES-9 [T]** — **Inappropriate register and defensive tone.**  
  *Finding:* Avoid internal software tracker phrases ("until 2026-10-11", "run log not found", "inferred, not verified").  
  *Evidence:* `docs/analysis-note/sec_method.tex:95`, `sec_systematics.tex:195`.  
  *Resolution:* This row authorizes no tex edit. Do not refactor the register. The three phrases are disclosures and stay: "until 2026-10-11" names when the exact-split central value stopped being the quoted 2D result; "its run log was not found" stays, same disposition as G1-ACC-8; and "inferred, not verified" states that two links in the POT-counting argument were not verified. Do not delete those sentences.
* **G1-PRES-10 [T]** — **Average nucleon mass definition $\\bar{M}$.**  
  *Finding:* In §8.2, average nucleon mass is defined as $\\bar{M} = (1.5 M_n + M_p)/2.5$. Origin of 1.5:1 ratio for CH tracker should be stated.  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:52`.  
  *Resolution:* This row authorizes no tex edit. The formula is already printed. Do not add a target-weighting convention. The defining header sets the constant and does not derive 1.5 from the tracker composition. Do not replace the factor with a CH ratio.

---

## Part 5: Gemini Report 2 (`gemini-note-r1-2.txt`)

### Section 3: Accuracy

* **G2-ACC-1 [T]** — **Discrepancy in Target Nucleon Count $N$.** Same finding as G1-ACC-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-ACC-1. The cited 4.123e30 and 4.128e30 are not in the note. The printed counts are 3.2353e30 and 3.235e30, two roundings of the same tracker-geometry constant. Do not harmonize them to a typed standard value.
* **G2-ACC-2 [T]** — **Inconsistent Marginal Normalization Agreement Metrics.** Same finding as S1-ACC-7 / S2-ACC-17 / G1-ACC-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-ACC-4. Do not follow the S1-ACC-7 wording. The executive summary no longer says the marginal checks pass to 1-2%. Do not add further marginal percentages to the executive summary.
* **G2-ACC-3 [T]** — **Inconsistent Run-Period $\\chi^2$ Values.** Same finding as G1-ACC-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-ACC-2. The cited 209.6 and 205.8 are not in the note. Table 3 does not quote a run-period chi-squared. Do not reconcile a run-period chi-squared to a value from values.tex.
* **G2-ACC-4 [T]** — **Conflicting Statements on Run-Period Block Variance Impact.** Same finding as S2-ACC-10.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-ACC-10. The two medians and the median of the per-bin increases are already stated separately. Do not add a ratio of the two medians.
* **G2-ACC-5 [T]** — **Discrepancy in Total Cross-Section Values.**  
  *Finding:* Total cross section quoted as $3.073 \\times 10^{-38}\\text{ cm}^2$ vs $3.07 \\times 10^{-38}\\text{ cm}^2$.  
  *Evidence:* `docs/analysis-note/sec_results.tex:80`, `sec_execsummary.tex:5`.  
  *Resolution:* This row authorizes no tex edit. Do not quote one macro for both numbers. The cited lines do not contain them. The quoted 2D total is \sigTwoD, which prints 3.069e-38. The purity-subtracted control is \sigTwoDPurity, which prints 3.073e-38, and the note already says they differ. The 3.07e-38 figures in the 3D and (E_avail, W) comparisons stay as printed. Do not replace one with another.
* **G2-ACC-6 [T]** — **Inconsistent Degrees of Freedom in Held-Out Coverage Tests.** Same finding as S2-ACC-8 / G1-ACC-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-ACC-3. Do not write that a kinematically inaccessible cell was excluded. The two ndf macros already print 204 and 205.
* **G2-ACC-7 [T]** — **Unexplained Higher-Dimensional Bin Count.** Same finding as S2-ACC-18.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-ACC-18. The counts already name different objects. Do not identify 4830 with 4825, and do not add a combined definition.
* **G2-ACC-8 [T]** — **Face-Invalid $\\chi^2$ Annotations in Figures 9 and 10.** Same finding as S2-PRES-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-PRES-4. The Fig. 9 caption already says the annotated per-panel chi-squared uses only the weight statistics and is a descriptive scale. Fig. 10 says it uses the same error bars. Do not remove the annotated values. Do not add a further sentence.

### Section 4: Completeness as a Citable Record

* **G2-COM-1 [D]** — **Manuscript Truncation.**  
  *Finding:* Referee reported document truncated at line 5,948 (§9.4).  
  *Resolution:* **DISPUTE / VOID.** Truncation occurred on the reader's side at 31,717 words. The rater copy `note-r1.blind.txt` was verified complete at 69,536 words (139 pp). Void per director's instructions.
* **G2-COM-2 [T]** — **Complete Absence of 3D and 4D Covariance Matrices.** Same finding as S2-COM-8 / G1-COM-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-COM-3. The comparisons are already called descriptive central values, with no 3D or 4D covariance and no generator chi-squared. Do not add purely.
* **G2-COM-3 [T]** — **Unvalidated and Failing Statistical Coverage.** Same finding as S1-COM-1.  
  *Resolution:* This row authorizes no tex edit. The pointer to S1-COM-1 is the citability matrix and is not this row. Same disposition as G1-COM-1. The abstract already names the two coverage tests separately. Do not merge them. Do not edit the abstract.
* **G2-COM-4 [T]** — **Uncorrected Miss-Weight Approximation in Systematics.**  
  *Finding:* Miss weights evaluated on central MC without reweighting under systematic universes.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:190`.  
  *Resolution:* This row authorizes no tex edit. The approximation is already disclosed. The systematic-universe unfolds approximate the weighting of events that fail reconstruction, the approximation is not corrected, and its effect has not been measured beyond the two-universe test. Do not add a further sentence. Do not add the internal label miss-weight.
* **G2-COM-5 [T]** — **Pending Detector-Response Mismatch Closure Test.** Same finding as S2-ACC-5 / G1-COM-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-COM-2. The rescaling test and the shifted-response closures already have separate statuses. Do not call the shifted-response closures exploratory, and do not say they did not run.
* **G2-COM-6 [T]** — **Missing Configuration Records and Run Logs.** Same finding as S2-COM-3 / G1-CONT-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-CONT-3. Do not apply the S2-COM-3 table instruction. The exact-split paragraph already says the seed was not fixed and the run log was not found. Do not add a further sentence. Do not add a second estimator table.
* **G2-COM-7 [T]** — **Unverified Systematics (Zeroed DIS and Inferred POT).** Same finding as S2-COM-12 / G1-COM-8.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-COM-8. The paragraph already says NormDISCC is identically zero, that it is carried as zero, and that this has not been confirmed as intended. The same paragraph already says two POT-counting links are inferred, not verified. Do not add a further sentence. Do not add the 7-of-187 statement.

### Section 5: Self-Containment

* **G2-CONT-1 [T]** — **Opaque Private Audit Citations (`Ref. [37]`).** Same finding as S1-CONT-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-CONT-1. Do not inline those values until each one is bound through a checked-values macro and a record says it may be quoted.
* **G2-CONT-2 [T]** — **Circular Dependency on the Companion Methods Paper.** Same finding as S1-CONT-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-3. Do not copy article text into the note. The observable definitions are already in the note's table.
* **G2-CONT-3 [T]** — **Reliance on Private Communication for Modeling Choices.** Same finding as S1-CONT-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S1-CONT-5. Do not replace a private-communication citation with a rationale the note does not already state.

### Section 6: Support for Claims

* **G2-CLM-1 [T]** — **Claim of "Reproducing" Published Cross Section within ~1%.** Same finding as S1-CLM-1.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-CLM-1. Do not add the broader claim that the background treatment was selected with the published result known.
* **G2-CLM-2 [T]** — **Claim of a "Five-Observable Unfolding".** Same finding as S2-CLM-9.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-CLM-9. The kinematic relation and the unmeasured added information are already stated, including the clamp. Do not drop the clamp. Do not rename configuration (e).
* **G2-CLM-3 [T]** — **Claim of Calibrated Hypothesis-Testing Rejections of Generator Predictions.** Same finding as S1-CLM-5.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-CLM-5. Do not replace the six conditions with a new scope sentence.
* **G2-CLM-4 [T]** — **Claim that Low-$E_{\\text{avail}}$ Excess Corresponds to Established Low-Recoil Excess.** Same finding as S1-CLM-3 / S2-CLM-3 / G1-CLM-4.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-CLM-4. Do not restore the corner sentence, and do not add a localization claim.
* **G2-CLM-5 [T]** — **Claim of a Meaningful 7.86% Uncertainty on 16-Cell Output.** Same finding as S1-CLM-2 / S2-CLM-6.  
  *Resolution:* This row authorizes no tex edit. Same disposition as S2-CLM-6. Do not type 7.86, and do not add "not independently validated." The budget sentence has already landed. Do not edit it again.

### Section 7: Minor Issues and Presentation

* **G2-PRES-1 [T]** — **Inappropriate Editorial Tone and Register.** Same finding as G1-PRES-9.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-PRES-9. Do not refactor the register. The three phrases are disclosures and stay: "until 2026-10-11" names when the exact-split central value stopped being the quoted 2D result; "its run log was not found" stays; and "inferred, not verified" states that two links in the POT-counting argument were not verified. Do not delete those sentences.
* **G2-PRES-2 [T]** — **Misleading Error Bars on Headline Figures.** Same finding as S2-PRES-5 / G1-PRES-3.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-PRES-3. The Fig. 7 caption already says the vertical error bars are the weight statistics of the reweighted simulated sample, and that they are neither the data's statistical uncertainty nor the reported covariance. Do not add a further explanation.
* **G2-PRES-3 [T]** — **Missing Uncertainties on Comparison Figures.**  
  *Finding:* Fig. 13 and Fig. 22 show comparisons without error bars.  
  *Evidence:* Figs. 13, 22.  
  *Resolution:* Fig. 13 (fig:model) already says uncertainties are not drawn. It is not edited. The 2D covariance is quoted and is not drawn on that figure. One sentence is added at the end of the Fig. 22 caption (fig:q3excess): uncertainties are not drawn because no 4D covariance is quoted. Do not relabel the figure. Do not add purely.
* **G2-PRES-4 [T]** — **Mislabeled Denominator in Figure 23.** Same finding as S2-PRES-6 / G1-PRES-7.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-PRES-7. Do not relabel the figure. The caption already says the ratio is data/Tune v1 and that the figure prints data/GENIE. The denominator is the tune-weighted prior. The sentence added under G2-PRES-3 stays.
* **G2-PRES-5 [T]** — **Proliferation and Fragmented Usage of Estimator Configurations.** Same finding as S1-PRES-4 / G1-PRES-2.  
  *Resolution:* This row authorizes no tex edit. Same disposition as G1-PRES-2. Do not add a glossary until its rows are copied from the configuration list already in sec_method.tex, one row per existing label, with no new claim. Do not rename configuration (e).
* **G2-PRES-6 [D]** — **Physical Truncation of Document Text.**  
  *Finding:* Physical text cut at §9.4.  
  *Resolution:* **DISPUTE / VOID.** Truncation occurred on reader's side; void per director's instructions.

### Void Findings

* **G2-VOID [D]** — **Completeness findings on §§9.5–13 and Appendices A–H.**  
  *Finding:* Gemini 2 claimed §§9.5–13 and Appendices are missing.  
  *Evidence:* Input cut at 31,717 words on reader's side; rater copy contains full 69,536 words.  
  *Resolution:* **VOID per director's instructions.**

---

## Part 6: Cross-Cutting Structural Synthesis

The companion note is restructured into a coherent methods-and-benchmark narrative per `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md`:

1. **Executive Summary as Methods-and-Benchmark Scope:**  
   * Opens with the comprehensive **Per-Result Status & Citability Matrix**:
     * 2D central value: Citable for reproduction of published integral; not citable as independent validation.
     * 2D uncertainty ($Q_R$): headline uncertainty, printed by \uqMedian and \uqIntegral; DECISION-20261024 replaces the 2026-10-17 sizes. Not citable for validated coverage. Do not put 6.45 or 4.75 back.
     * 3D & 4D central values: Citable for dimensional consistency and marginal normalization; not citable with covariance.
     * 5D configuration-(a) central value: Citable as exploratory unregularized 5D central value; not citable with covariance.
     * 5D configuration-(a) covariance ($C_Z$): Adopted under the §6.4 exception; non-passing (M1, DECISION-20260920 line 57; M3, lines 73-79: the seed variation does not probe those five bands, and the effect on the total when they also vary has not been measured; the pre-production null bound not met); not a yardstick and not an uncertainty product (governed by S2-COM-2). The note must not type 6.145.
     * 16-cell five-observable result: Illustrative output demonstrating multi-differential data handling; not citable as physical measurement or for model tuning.
     * Generator joint tests: Methodological demonstration of calibrated hybrid-null hypothesis testing with biased estimators; not citable as measured cross sections.
     * Extended fiducial volume: Exploratory demonstration of unbinned phase-space extension; not citable as finalized cross section.

2. **The 2D Benchmark (Sections 2–6):**  
   * Integral agreement with publication.  
   * Paper-covariance distance $\\chi^2/\\text{ndf}$ quoted strictly through `\\chiPaper` over 205 bins, with correlated shape difference of unidentified origin.  
   * Stated limitations: run-period block $C_{\\text{PL}}$ absorbs playlist inconsistency by construction; no COV2D note sentence is added under AUD-E1.  
   * Method choice disclosures: LightGBM architecture, negative-weight subtraction refinement, and result adoption were selected with published distance known.

3. **Multidimensional Central Values & Marginal Anchors (Sections 7–8):**  
   * 3D $E_{\\text{avail}}$ and 4D $(E_{\\text{avail}}, q_3)$ central values.  
   * Recovery of lower-dimensional marginals (0.11% total, 0.3–1.5% median per axis).  
   * Purely descriptive comparisons to generator predictions without evaluated covariance.

4. **Scalar 5D Unfolding Methodology & Limitations (Section 9):**  
   * Configuration-(a) 5D central value on $(p_T, p_\\parallel, E_{\\text{avail}}, q_3, W)$.  
   * Full disclosure of the non-passing status of covariance $C_Z$ uses S2-COM-2's resolution. The note must not say "five bands unmeasured" and must not type 6.145.  
   * Technical closure and futility-stopped 1,200-pseudo-experiment coverage test.

5. **Illustrative Sixteen-Cell Five-Observable Output (Section 10):**  
   * Presented strictly as illustrative output on data, not for fitting or constraining models.  
   * Full disclosure of pre-check Stage-1 STOP (892/900 non-positive composite denominator draws).  
   * Valid-region classifications (V-ATLAS, V-PRIOR; 12 valid under both) as descriptive diagnostics.  
   * Algorithm dependence (REF-G1: IBU vs OmniFold $T = 194.4$ against calibrated bar 28.12) as a stated limitation.  
   * Failed offset control check ($\\chi^2 = 245.74$ for 16 ndf).

6. **Calibrated Joint Generator Hypothesis Tests (Section 11):**  
   * Methodological illustration of hybrid-null testing with biased estimators.  
   * Rejection of all ten simple hypotheses within the simulation framework.  
   * Full disclosure of conditions (i)–(vi), including unmeasured sub-grid residual.

7. **Extended Fiducial Volume Study (Section 12):**  
   * Methodological study of phase-space extension.  
   * Two-tier reporting framework and prior-envelope uncertainties.

8. **Systematic Methodology & Algorithmic Diagnostics (Section 13 & Appendices):**  
   * Self-contained technical definitions replacing internal record pointers.  
   * Explicit characterization of numerical stability, float32 rounding, and seed sensitivity.

---

## Ledger Action Item Index

1. **Step 1:** Establish this exhaustive issue ledger on `draft/note-round2-20261108` and obtain confirmation from Grok (`client-grok-shell-open-agent-bridge-c4a99362fc6f`).
2. **Step 2:** Execute structural reordering in `docs/analysis-note/main_note.tex` in its own commit (2D benchmark before 16-cell result; Executive Summary methods-and-benchmark opening; no prose edits).
3. **Step 3:** Draft the comprehensive Per-Result Status & Citability Matrix in `sec_execsummary.tex` / Section 1.
4. **Step 4:** Execute editorial and wording reconciliations ([T] items, excluding held items AUD-N4 and AUD-N5) across all sections, replacing hardcoded numbers with `values*.tex` macros and removing overclaims. Held items (AUD-N4 [T] and AUD-N5 [R]) remain unedited without director/Joseph authorization.
5. **Step 5:** Inline essential mathematical definitions from internal records ([R] items, excluding held item AUD-N5) into self-contained appendices and text. Held item AUD-N5 [R] remains unedited without director/Joseph authorization.
6. **Step 6:** Verify entire test suite (`test_build_all.py`, `check_body_pointers.py`, `check_note_records.py pin .`), ensure clean PDF builds, and submit for rater review.


---

## Part 7: Round 3 Referee Audit Ledger Index (Blind Reads #1023)

Base commit: `1a16763347b9a17224f9e943f722b1cfa4c12810`  
Reports: `docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/note-round2-blind-reads-20261110/gpt.txt` and `gemini.txt` (PR #1023, commit `5d324d0ed`).  
Scope: Index of referee findings for Round 3 resolution. Resolution column remains pending; no text changes authorized by this index.

### Section 7.1: GPT Report Findings (§3, §4, §5, §6)

| Item | Source (#1023) | Referee Claim (One Sentence) | Note Target (1a167633) | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| **GPT-3.1** | `gpt.txt:11` | Table 1 5D covariance row cites non-resolving '§6.4 exception' for adoption. | `docs/analysis-note/sec_execsummary.tex:25` | Replaced "Adopted under the \S6.4 exception" with "Used in this note" in sec_execsummary.tex:25. |
| **GPT-3.2** | `gpt.txt:13` | Table 1 transfers companion covariances' stability failure to adopted covariance C_Z where criterion was uncomputed. | `docs/analysis-note/sec_execsummary.tex:25` | Clarified in sec_execsummary.tex:25 that the estimator-seed criterion has not been computed for this covariance, and removed parenthetical comparison reference. |
| **GPT-3.3** | `gpt.txt:15` | Table 1 incorrectly labels configuration-(a) central value as 'unregularized'. | `docs/analysis-note/sec_execsummary.tex:23` | Replaced "exploratory unregularized five-observable central value" with "exploratory five-observable central value (\S\ref{sec:method-algo})" in sec_execsummary.tex:23. |
| **GPT-3.4** | `gpt.txt:17` | Table 1 assigns passing injected-shape closures to configuration (e) when tested under (a) without threshold. | `docs/analysis-note/sec_execsummary.tex:21` | Clarified in sec_execsummary.tex:21 that the injected-Eavail closure is configuration (a), has no predeclared threshold, and does not extend to (e). |
| **GPT-3.5** | `gpt.txt:19` | Main text claims negative-weight injection targets identical continuous density (D-B)/S contrary to App. C.1. | `docs/analysis-note/sec_method.tex:28` | Clarified in sec_method.tex:28 that negative-weight injection targets bin-integrated estimand (D_b-B_b)/S_b and treatments do not share continuous density. |
| **GPT-3.6** | `gpt.txt:21` | Section 2.3 asserts 'neither prediction carries an uncertainty' while background variation is propagated in ensembles. | `docs/analysis-note/sec_experiment.tex:26` | Replaced "neither prediction carries an uncertainty" with "no uncertainty is printed beside either quoted fraction" in sec_experiment.tex:26. |
| **GPT-3.7** | `gpt.txt:23` | Section 3.5 describes reconstructed q3 as built from Eavail rather than calorimetric recoil estimate q0_reco. | `docs/analysis-note/sec_method.tex:198` | Replaced "$q_{3}$, built from $\Eavail$ and the muon," with "$q_{3}$, reconstructed from the muon $Q^{2}$ and the calorimetric recoil," in sec_method.tex:198. |
| **GPT-3.8** | `gpt.txt:25` | Figure 3 and §3.5 label truth-bin-conditional reconstruction probabilities as purity rather than stability. | `docs/analysis-note/sec_method.tex:196-203` | Replaced migration diagonal purity labels with reconstruction stability in sec_method.tex:196-203 and Fig. 3 caption. |
| **GPT-3.9** | `gpt.txt:27` | Flux extraction formula includes 10^4 factor for m^-2 without indicating how higher-dimensional cm^-2 flux enters. | `docs/analysis-note/sec_method.tex:181-188` | Clarified flux extraction formula units and higher-dimensional integrated flux conversion in sec_method.tex:184,188. |
| **GPT-3.10** | `gpt.txt:29` | Section 7.4 quotes Eavail-marginal recovered/truth ratio spread (0.0006) alongside 1.84% residual without defining the latter. | `docs/analysis-note/sec_3d.tex:104` | Rebutted. sec_3d.tex:104 already separates the marginal recovered/truth scatter from the feature-recovery residual defined at sec_validation.tex:35 and reported at sec_validation.tex:91. No formula and no new number. |
| **GPT-3.11** | `gpt.txt:31` | Section 7.8 states 44-cell Ascencio comparison requires re-unfolding, contradicting claim that reporting edges need no re-unfolding. | `docs/analysis-note/sec_3d.tex:209` | Clarified in sec_3d.tex:209 that binning onto Ascencio edges does not require re-running unfolding and noted systematic sweep has not been done. |
| **GPT-3.12** | `gpt.txt:33` | Section 9.4 states budget allowed 5 iterations max at that capacity while Fig. 26 caption probes to 10. | `docs/analysis-note/sec_5d.tex:142` | Clarified in sec_5d.tex:142 that capacity probe traces reach 10 iterations while 5 iterations was the comparison used under budget allowance. |
| **GPT-3.13** | `gpt.txt:35` | Section 12.2 cites agreement over all 185 reported cells while analysis reports 205 cells (185 being interior mask). | `docs/analysis-note/sec_fps.tex:26` | Clarified in sec_fps.tex:26 that 185 cells refers to that sub-block and not the 205-cell reported set. |
| **GPT-3.14** | `gpt.txt:37` | Section 11.6 states 'no assignment of lost draws changes any decision' before recovering actual assignment. | `docs/analysis-note/sec_joint.tex:222` | Rebutted. sec_joint.tex:222 is the selected disposition: the determinism check identifies each recovered draw with the lost draw, and none reaches the observed statistic, so that assignment changes no decision (DECISION-20261005 §5). The pre-recovery sensitivity stays at sec_joint.tex:220. |
| **GPT-3.15** | `gpt.txt:39` | Figure 15 annotation states 29 of 30 measurements at 2 simultaneous variables while Table 36 has 19 2D, 10 1D, 1 3D. | `docs/analysis-note/sec_3d.tex:15` | Rebutted. The figure annotation already says at most two simultaneously unfolded variables (plot_minerva_landscape.py:74-75). The thirty historical rows are 19 of dimension 2, 10 of dimension 1 and 1 of dimension 3. |
| **GPT-3.16** | `gpt.txt:41` | Section 4.6 defines s_k as relative change and adds outer product C_model = sum s_k s_k^T to dimensional cross section without diagonal scaling. | `docs/analysis-note/sec_systematics.tex:227, docs/analysis-note/sec_fived16.tex:99` | Stated that C_model is a fractional covariance and in cross-section units is diag(x) C_model diag(x) in sec_systematics.tex and sec_fived16.tex. |
| **GPT-3.17** | `gpt.txt:43` | Section 9.6 states diagonal inflation G C_vert G 'never falls below block baseline' while GCG-C is not guaranteed PSD. | `docs/analysis-note/sec_5d.tex:289` | Clarified in sec_5d.tex:289 that each diagonal entry is at least the block-sum diagonal (g_i >= 1) without implying every projected variance exceeds baseline. |
| **GPT-3.18** | `gpt.txt:45` | Appendix A.3.4 calls 'all-bins-up' direction the kernel of J = (I - s w^T)/T instead of the right-null direction proportional to s. | `docs/analysis-note/app_statmethods.tex:435` | Clarified in app_statmethods.tex:435 that w^T J = 0 is a left-null relation and the right kernel of J is the direction s proportional to x. |
| **GPT-3.19** | `gpt.txt:47` | Section 10.7 calls shape-only normalization 'free' while §10.3 adds finite 100 f f^T penalty. | `docs/analysis-note/sec_fived16.tex:287` | Clarified in sec_fived16.tex:287 that shape-only chi^2 uses the finite penalty 100 f f^T (sec:fived16-cov), which approximates a free normalization. |
| **GPT-3.20** | `gpt.txt:49` | Section 9.6 conflates algebraic matrix rank with numerical cutoff rank by stating 'Rank is a property of the cutoff'. | `docs/analysis-note/sec_5d.tex:306` | Clarified in sec_5d.tex:306 that algebraic rank is a property of the matrix while numerical rank depends on the cutoff. |
| **GPT-3.21** | `gpt.txt:51` | Appendix A.1 asserts N=300 > 205 bootstrap replicas guarantees full rank without citing measured rank. | `docs/analysis-note/app_statmethods.tex:20` | Clarified in app_statmethods.tex:20 and app_history.tex:108 that N=300 > 205 permits full rank but does not establish it, and noted body does not claim full rank. |
| **GPT-3.22** | `gpt.txt:53` | Appendix A.2.4 claims mean-centering gives near-zero variance for asymmetric pairs while half-difference can remain large. | `docs/analysis-note/app_statmethods.tex:146` | Clarified in app_statmethods.tex:146 that mean-centering removes a common offset from the central value while the half-difference remains and CV-centering adds the offset as a second direction. |
| **GPT-3.23** | `gpt.txt:55` | Appendix A.6.2 hidden-variable closure changes reco weights leaving truth unchanged, altering effective response despite §5 claim. | `docs/analysis-note/sec_validation.tex:12` | Clarified in sec_validation.tex:12,41 that the simulated detector is unchanged while the hidden-variable arm changes the effective response by reweighting reco events without changing truth weights. |
| **GPT-3.24** | `gpt.txt:57` | Table 32 and §A.2 claim matching seed means 'ML noise cancels' while weights change tree construction and retraining scatter rivals shifts. | `docs/analysis-note/app_statmethods.tex:634` | Clarified in app_statmethods.tex:61,634 that pinning the seed correlates training noise and does not cancel it (sec:uq-2d-scope). |
| **GPT-3.25** | `gpt.txt:59` | Section 5.3 categorically asserts omitted covariance terms 'can only lower the flag rate' despite non-monotonic bias effects. | `docs/analysis-note/sec_validation.tex:206` | Clarified in sec_validation.tex:206 that the effect of omitted covariance terms on the flag rate was not measured. |
| **GPT-3.26** | `gpt.txt:61` | Appendix C.8 equates \|t\| > 3.6 to Bonferroni-corrected 5% level without qualifying normal vs Student-t reference. | `docs/analysis-note/app_negweight.tex:168` | Qualified \|t\| > 3.6 as fixed threshold at about two-sided 5% level for normal reference in app_negweight.tex:168. |
| **GPT-4.1** | `gpt.txt:65` | Give definitive validation inventory listing exact tests, configurations, and outcomes for all quoted results. | `docs/analysis-note/sec_execsummary.tex:17` | Clarified in sec_execsummary.tex:17 that iteration comparison was measured for exact-split, completeness is a monitored self-check with no recovery claim, and closure passes depend on deformation and amplitude (sec:validation). |
| **GPT-4.2** | `gpt.txt:67` | Held-out-tune test cannot be reconstructed from §5.3 without statistical model, scoring equations, and C08 definition. | `docs/analysis-note/sec_validation.tex:188` | Clarified in sec_validation.tex:188,206 that pseudo-experiments are inside cell when within 1 sigma and inside joint region when chi^2 <= 1 sigma quantile, clarified clipping rule, and defined C08 as the training-seed block (sec:uq-ml). |
| **GPT-4.3** | `gpt.txt:69` | Provide complete mathematical construction of C_model including grid, pooling, gating, boundaries, and unit scaling. | `docs/analysis-note/sec_systematics.tex:227` | Clarified in sec_systematics.tex:227 that ratio is constant per cell, keeps own ratio if relative-error gate passes, uses coarser pooled cell if pooled error passes, and leaves prior unchanged otherwise, outside grid, or where GiBUU undefined. |
| **GPT-4.4** | `gpt.txt:71` | Explain statistical target and derivation of training-seed block constructed from 5 means of 20 replicas. | `docs/analysis-note/sec_systematics.tex:99` | Clarified in sec_systematics.tex:99 that statistical block at central seed already contains training noise at that seed, so training-seed block adds covariance of per-seed means rather than spread of single unfolds. |
| **GPT-4.5** | `gpt.txt:73` | Complete description of unified-throw investigation with throw count, composition law, and mean shifts. | `docs/analysis-note/sec_execsummary.tex:47` | Clarified in sec_systematics.tex:156 and sec_execsummary.tex:47 that no 2D comparison of a joint throw with block sum is reported, and stored mean-shift norm is not quoted. |
| **GPT-4.6** | `gpt.txt:75` | Define 5D covariance diagnostics s_proj, s_agg, s_med with explicit formulas, functionals, and band partitions. | `docs/analysis-note/sec_5d.tex:314` | Defined s_proj, s_agg, and s_med explicitly in sec_5d.tex:314 with functionals over projected cells, trace, and median per-bin relative standard deviations. |
| **GPT-4.7** | `gpt.txt:77` | Resolve whether acceptance correction is needed at destination binning for the displayed 5D projection. | `docs/analysis-note/sec_5d.tex:304` | Clarified in sec_5d.tex:304 that projection matrix factor is bin widths and not an acceptance weight, unfolding is efficiency-corrected via step 1, and no separate acceptance weight was declared or applied to Fig. 33. |
| **GPT-4.8** | `gpt.txt:79` | Specify the missing-event systematic approximation for reconstruction failures through completeness. | `docs/analysis-note/sec_systematics.tex:237` | Clarified in sec_systematics.tex:237 that unreconstructed events keep central-value weight and are divided by universe completeness rather than receiving universe truth weight. |
| **GPT-4.9** | `gpt.txt:81` | Provide complete nuisance inventory defining all 45 bands, counts, amplitudes, centering, and zero NormDISCC band. | `docs/analysis-note/sec_systematics.tex:243` | The zero NormDISCC band and the proton-on-target statement are named as part of the quoted two-dimensional universe block, and that block is distinguished from C_Z, the sixteen-cell covariance, and the joint-test draws. |
| **GPT-4.10** | `gpt.txt:83` | Specify recoil-response covariance numerically with category magnitudes, cross-talk terms, and observable mapping. | `docs/analysis-note/sec_fived16.tex:106` | Each deposit category is scaled by its own factor of its reconstructed energy, the three recoil observables move, each contribution is the half-difference outer product, and the cross-talk deposit stays out of the sum as a separate variant. |
| **GPT-4.11** | `gpt.txt:85` | Provide explicit run-period covariance equations with period exposures, reliability weights, and offsets. | `docs/analysis-note/sec_fived16.tex:174` | The target moved to sec_fived16.tex:174; the block is written with the exposure shares, the fractional offsets, and the reliability-weight factor, and the printed interval is the chi-squared interval of that weighted spread. |
| **GPT-4.12** | `gpt.txt:87` | Assign compact documentary statuses to stopped and incomplete studies rather than active internal workflow. | `docs/analysis-note/sec_fived16.tex:102` | The target moved to sec_fived16.tex:102; the reconstruction-information study remains incomplete, is not a pass and not a stop, and the validated-coverage route that depended on it is not pursued further. |
| **GPT-4.13** | `gpt.txt:89` | Explain the statistical mechanism and denominator formula behind the 892/900 non-positive composite draws. | `docs/analysis-note/sec_fived16.tex:258` | The composite denominator is the first-order sum of the drawn universes' denominators, and the record does not establish why cells in that sum are non-positive. |
| **GPT-4.14** | `gpt.txt:91` | Define joint-test calibration as an explicit probability law with universe weights, nuisance laws, and residual models. | `docs/analysis-note/sec_joint.tex:53` | The calibration paragraph states the draw probabilities, the normal laws for the lateral, normalization, rounding and prediction-residual terms, and that the diagonal prediction-error model is an assumption. |
| **GPT-4.15** | `gpt.txt:93` | Clarify joint-test shift uncertainty set and whether simultaneous simulation-size and below-grid shifts were evaluated. | `docs/analysis-note/sec_joint.tex:197` | The target moved to the caption of fig:joint5d-nulls; each listed shift is applied alone, and the largest p value does not bound a combination or another direction. |
| **GPT-4.16** | `gpt.txt:95` | Disclose malformed third truth in 5D coverage experiment up front in text and define Bonferroni family scope. | `docs/analysis-note/sec_5d.tex:221` | The opening states that the third truth did not implement its reweighting and is not an interpretable test, and that the 68% and 95% assessments are separate Bonferroni families of the same size. |
| **GPT-4.17** | `gpt.txt:97` | Reconcile generator normalization between MEC event fraction (2.87%) and no-catch-bin deficit shift (7.2% to 2.7%). | `docs/analysis-note/sec_3d.tex:170` | f_MEC is the unweighted event fraction of the regenerated sample, counted before the flux reweight. The integrated-deficit shift is the flux-repaired rate without the catch bin, and it is not that fraction. |
| **GPT-4.18** | `gpt.txt:99` | Complete extended-fiducial reporting definitions including grid, anchor mask, partially accepted cells, and tier metrics. | `docs/analysis-note/sec_fps.tex:58` | The reporting paragraph names the extended grid, the 185-cell anchor, and the non-overlapping acceptance fractions. Cells crossed by the angular cut are not split. The tier shares stay fractions of the rate. Neither tier is a completed measurement, and the three-prior envelope is not a coverage interval. |
| **GPT-4.19** | `gpt.txt:101` | Provide full GBDT and Keras-MLP learner configurations, architectures, determinism settings, and tie handling. | `docs/analysis-note/sec_method.tex:150` | The hyperparameter paragraph states that configurations (a) and (f) take histogram edges from the library's default row sample, and that the configurations called deterministic take them from every training row and enable the library's deterministic training. It names the Keras cross-check network and points the float32 tie sensitivity to the existing paragraph. |
| **GPT-4.20** | `gpt.txt:103` | Distinguish genuine background from out-of-phase-space subtraction quantitatively across full analysis sample. | `docs/analysis-note/sec_experiment.tex:26` | The selection paragraph states that the 0.35 percent figure is the playlist-1A genuine-background fraction, that the overall correction in the method section is the total of both pieces, and that this paragraph does not split that total or give either piece's kinematic distribution. The sub-percent scale is the genuine-background fraction. |
| **GPT-5.1** | `gpt.txt:107` | Ensure standard literature citations adequately ground foundational methods and external tools. | `docs/analysis-note/sec_intro.tex:10` | Rebutted. gpt.txt:107 says the standard citations need not be reproduced in full and that the removed reference list is not a fault. sec_intro.tex:6, :8 and :10 already cite the detector, the published measurement, iterative Bayesian unfolding, and OmniFold. No citation was added. |
| **GPT-5.2** | `gpt.txt:109` | Embed indispensable scientific definitions directly in note rather than delegating them to internal repository records. | `docs/analysis-note/sec_5d.tex:84` | The binned-response paragraph defines an identified quantity as a relative Cram\'er--Rao width at or below 2.5 percent, and a width between that bound and the 10 percent bound as neither. The exclusion count stays. The record citation is kept for the numerical verification. |
| **GPT-5.3** | `gpt.txt:111` | Fully describe learned-estimator configurations rather than delegating specifications to code names. | `docs/analysis-note/sec_method.tex:150` | Rebutted. gpt.txt:111 asks for the histogram setting and the float32 tie mechanism. sec_method.tex:150 states both the histogram construction and the Keras network, and sec_5d.tex states the tie mechanism. No setting was added. |
| **GPT-5.4** | `gpt.txt:113` | Provide complete operational definition of reconstructed calorimetric recoil estimator q0_reco. | `docs/analysis-note/scalar_kinematics.tex:11` | The shared-input paragraph states that the recoil is one calorimetric energy transfer, not decomposed into calorimeter regions and not the available-energy scale factor. The equation's clamps are the stated treatment of a negative Q squared or W squared, and the note states no further cut on the recoil. |
| **GPT-5.5** | `gpt.txt:115` | Define or replace internal control labels (C08, B3, Stage 0, natures) with self-contained scientific descriptions. | `docs/analysis-note/sec_fived16.tex:181` | The run-period paragraph states the three predeclared results that would have stopped the addition, and that none occurred. The rendered note does not use the labels C08, B3, Stage 0, or natures. |
| **GPT-5.6** | `gpt.txt:117` | Embed necessary recovery figures or evidence locally rather than relying solely on companion paper. | `docs/analysis-note/sec_5d.tex:142` | Rebutted. sec_5d.tex:142 cites the note's Figure fig:gbdt-recovery and states the traces. The caption states the capacities and the iteration ranges. The rendered sentence does not cite the paper's figure. |
| **GPT-5.7** | `gpt.txt:119` | Provide in-note mathematical construction of data-derived lateral surrogate and its draw law. | `docs/analysis-note/sec_joint.tex:53` | The generative-model paragraph states that each lateral shift is half the difference of that band's two real-data endpoint unfolds, and that each coefficient is an independent standard normal. |
| **GPT-5.8** | `gpt.txt:121` | Accompany recomputation claims with precise targets and boundaries in note text rather than bare checksums. | `docs/analysis-note/sec_joint.tex:118` | Rebutted. sec_joint.tex:118 states that the independent recomputation reproduces the p values and the decisions and verifies the calculation, not the adequacy of the calibration. sec_5d.tex:258 identifies the file by checksum, and the same subsection states the assembly. app_cstat.tex:83 limits the in-tree checks to arithmetic and ordering. No sentence was changed. |
| **GPT-6.1** | `gpt.txt:125` | Align abstract caveats with body text regarding 2.6 sigma rounding shifts and malformed third coverage truth. | `docs/analysis-note/main_note.tex:74` | The abstract states that the rounding shift is configuration (e) on the joint cells, the (E_avail, W) cells, their sum and the integrated total, and that the third generated truth of the 1,200-experiment test did not implement its reweighting. |
| **GPT-6.2** | `gpt.txt:127` | Narrow broad 'validated' and 'pass' language to performance on specific diagnostic tests. | `docs/analysis-note/sec_method.tex:150` | The hyperparameter paragraph says the listed checks report performance on those diagnostics, and that they do not validate the quoted estimator or its intervals. |
| **GPT-6.3** | `gpt.txt:129` | Restrict five-iteration justification to stability of tested diagnostics rather than asserting general convergence. | `docs/analysis-note/sec_method.tex:152` | The iteration paragraph limits the five-to-ten comparison to the exact-split total cross section, and the appendix limits it to that chi-squared movement. Neither states convergence of every functional. |
| **GPT-6.4** | `gpt.txt:131` | Qualify assertion that simulation prior describes shapes well to acknowledge specific normalization and shape trends. | `docs/analysis-note/sec_experiment.tex:45` | Replaced overclaim with explicit normalization (+12%) and p_T trend (0.88 to 1.2) in sec_experiment.tex:45 and sec_method.tex:152. |
| **GPT-6.5** | `gpt.txt:133` | Reframe C2ST from demonstrating 'removal' of mismatch to a descriptive training-sample discrimination diagnostic. | `docs/analysis-note/sec_validation.tex:224` | The C2ST paragraph reports the AUC drop as a training-sample discrimination diagnostic and says it does not show that the mismatch was removed. |
| **GPT-6.6** | `gpt.txt:135` | Restrict 2D Tune-v1 conclusion to descriptive quadratic distance under covariance rather than calibrated exclusion. | `docs/analysis-note/sec_results.tex:164` | The Tune-v1 paragraph reports the quadratic distances as descriptive and points to the covariance's statement that it gives no calibrated significance for a generator comparison. |
| **GPT-6.7** | `gpt.txt:137` | Restrict higher-dimensional validation language to measured marginal normalization checks rather than full distribution recovery. | `docs/analysis-note/sec_execsummary.tex:21` | The 3D and 4D citability cell is limited to the measured normalization and projection checks, and it says those checks do not establish recovery of the joint distribution. |
| **GPT-6.8** | `gpt.txt:139` | Reframe background-covariance agreement as close aggregate size rather than absence of method bias. | `docs/analysis-note/app_negweight.tex:102` | The covariance paragraph states that the two residuals are aggregate sizes, and it does not attribute them to sampling noise or to the absence of a method bias. |
| **GPT-6.9** | `gpt.txt:141` | Narrow claim of cross-estimator subtraction robustness to removal of tested pathology on evaluated backends. | `docs/analysis-note/app_negweight.tex:40` | The comparison paragraph says the clipped refinement removes the exact-split pathology in this comparison, and that this does not establish robustness across estimators or background regimes. |
| **GPT-6.10** | `gpt.txt:143` | Reframe comparable seed-scan and split-varied band sizes as comparable magnitudes rather than seed dominance. | `docs/analysis-note/sec_systematics.tex:299` | The stochasticity paragraph says the two aggregate sizes are comparable, and it does not conclude that estimator stochasticity dominates the split-varied band. |
| **GPT-6.11** | `gpt.txt:145` | Qualify exact-versus-histogram difference as backend-associated difference among available runs rather than ruling out seed effects. | `docs/analysis-note/app_statmethods.tex:554` | The appendix says the available runs differ by backend, and that the histogram-seed jitter does not measure the unmeasured exact-split seed spread. |
| **GPT-6.12** | `gpt.txt:147` | Preserve restrictions of binned-response diagnostic to eligible residuals and signal-only calculation in summaries. | `docs/analysis-note/sec_5d.tex:84` | Rebutted. sec_5d.tex:84 states the noise-free signal-only calculation, the named deformations, and the 144 eligible residuals, and it limits the conclusion to those residuals. No sentence was changed. |
| **GPT-6.13** | `gpt.txt:149` | State familywise error guarantee as conditional on stated assumptions rather than experimentally demonstrated validity. | `docs/analysis-note/sec_execsummary.tex:29` | The executive summary says the generator tests are calibration within the implemented model under the stated assumptions, and that they are not a measured rejection rate for the experiment. |
| **GPT-6.14** | `gpt.txt:151` | Restrict ten joint-test rejections to original hybrid hypotheses rather than physical generator exclusions. | `docs/analysis-note/sec_joint.tex:168` | Rebutted. sec_joint.tex:168 reports rejections of the ten tests. sec_execsummary.tex:44 says they are not physical exclusions. sec_joint.tex:305 keeps the target-corrected evaluations descriptive. sec_joint.tex:237 states no additional joint discrimination. No sentence was changed. |
| **GPT-6.15** | `gpt.txt:153` | Limit response robustness claim to sensitivity under coherent variation rather than full calibration robustness. | `docs/analysis-note/sec_joint.tex:272` | Rebutted. sec_joint.tex:272 states the re-unfold against the original null distributions. sec_joint.tex:295 says those distributions were not regenerated and that the response model is not shown to be complete. No sentence was changed. |
| **GPT-6.16** | `gpt.txt:155` | Designate extended-fiducial tier 1 as an acceptance-supported central estimate rather than a qualified measurement. | `docs/analysis-note/sec_execsummary.tex:49` | The executive summary calls tier 1 an acceptance-supported central estimate rather than a qualified measurement. |
| **GPT-6.17** | `gpt.txt:157` | Narrow appendicial claims regarding alternative-model robustness and small standardized differences to direct test metrics. | `docs/analysis-note/app_statmethods.tex:419` | The pull paragraph calls the paper-covariance mean a small difference between two estimates, not an absence of bias. The alternative-model closure calls its residuals recovery relative to the constructed reference, not general model robustness. |

### Section 7.2: Gemini Report Findings (§3, §6, and Structural Requests)

| Item | Source (#1023) | Referee Claim (One Sentence) | Note Target (1a167633) | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| **GEM-3.1** | `gemini.txt:23` | Reconcile contradictory statements in §5.3 regarding whether C_model was included or excluded in held-out-tune draws. | `docs/analysis-note/sec_validation.tex:206` | The limits sentence says the model term is in the remade covariance and is not drawn in the pseudo-experiments. |
| **GEM-3.2** | `gemini.txt:28` | Harmonize target nucleon count between 2D (3.2353e30) and higher-dimensional extractions (3.235e30). | `docs/analysis-note/sec_method.tex:187` | The higher-dimensional sentence uses the fiducial nucleon count already printed in the formula. It does not print a second rounding. |
| **GEM-3.3** | `gemini.txt:33` | Provide structural accounting for clashing bin counts (10,976 vs 10,694 vs 10,499 vs 4,830). | `docs/analysis-note/sec_systematics.tex:294` | The higher-dimensional ratio is over the five-observable cells whose central value is positive. The four-dimensional grid, its populated subset, and the occupied reconstructed cells stay as already named. |
| **GEM-3.4** | `gemini.txt:39` | Correct Table 1 non-existent '§6.4 exception' cross-reference for 5D covariance adoption. | `docs/analysis-note/sec_execsummary.tex:25` | Rebutted. sec_execsummary.tex:25 does not cite a section 6.4 exception. The cell points to sec:eavailw-adopted. No sentence was changed. |
| **GEM-3.5** | `gemini.txt:44` | Reconcile Table 1 designating configuration (e) for 3D/4D central values with Figs. 17 and 23 using configuration (a). | `docs/analysis-note/sec_execsummary.tex:21` | pending |
| **GEM-3.6** | `gemini.txt:49` | Correct degrees-of-freedom normalization in truncated subspace chi^2 (136 on 73 modes is chi^2/73=1.86, not chi^2/205=0.66). | `docs/analysis-note/sec_results.tex:128` | pending |
| **GEM-3.7** | `gemini.txt:54` | Reconcile 0.35% genuine background with ~3% total subtraction by explicitly quantifying out-of-phase-space signal. | `docs/analysis-note/sec_experiment.tex:26` | pending |
| **GEM-3.8** | `gemini.txt:59` | Reconcile exclusion of negative W^2 events (0.15%) with claim of exact completeness c = 1.000000. | `docs/analysis-note/sec_method.tex:184` | pending |
| **GEM-3.9** | `gemini.txt:64` | Disclose and justify inherited 135 MeV subtraction for charged pions in true available energy definition Eq. (1). | `docs/analysis-note/sec_3d.tex:24` | pending |
| **GEM-6.1** | `gemini.txt:118` | Narrow claim that unbinned unfolding 'reproduces' published cross section to integrated rate with correlated shape tension. | `docs/analysis-note/sec_execsummary.tex:17` | pending |
| **GEM-6.2** | `gemini.txt:122` | Narrow claim that joint 5D tests reject generator predictions to synthetic hybrid nulls under stated target and phase-space limits. | `docs/analysis-note/sec_joint.tex:168` | pending |
| **GEM-6.3** | `gemini.txt:126` | Clarify that 5D simultaneous unfolding unfolds four independent kinematic variables with algebraically redundant W. | `docs/analysis-note/sec_execsummary.tex:40` | pending |
| **GEM-6.4** | `gemini.txt:130` | Reframe reduced bootstrap statistical variance as regularization shrinkage rather than demonstrated precision gain given tail undercoverage. | `docs/analysis-note/sec_systematics.tex:50` | pending |
| **GEM-6.5** | `gemini.txt:134` | Reframe 1D Gaussian bump recovery as insensitive marginal feature recovery rather than validation of multidimensional fidelity. | `docs/analysis-note/sec_execsummary.tex:21` | pending |
| **GEM-REQ-1** | `gemini.txt:161` | State scope and technical rationale for distinct estimator configurations (a)-(f) rather than unifying analysis. | `docs/analysis-note/sec_method.tex:128` | pending |
| **GEM-REQ-2** | `gemini.txt:73` | State scope and diagnostic status of higher-dimensional uncertainty covariances rather than constructing new 3D/4D matrices. | `docs/analysis-note/sec_3d.tex:10` | pending |
| **GEM-REQ-3** | `gemini.txt:162` | State scope, hybrid-null framing, and material-correction sensitivity of generator tests rather than retracting them. | `docs/analysis-note/sec_joint.tex:168` | pending |
