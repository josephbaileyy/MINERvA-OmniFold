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
  *Status:* Drafted in round 1; verify exact wording matches record.

* **AUD-E3 [R]** — **1B pre-check Part 1 (flux and detector groups).**  
  *Finding:* State Part 1 pre-check outcome: both flux and detector groups reproduce within the [0.9, 1.1] window; GEANT neutron and proton bands depart in named cells.  
  *Record:* `OUTCOME-20261108-1b-precheck-part1.md:49-62` (`CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_fived16.tex:253`.  
  *Status:* Drafted in round 1.

* **AUD-E4 [R]** — **Valid-region classes of the 16 cells.**  
  *Finding:* Tabulate each cell's V-ATLAS class (14 valid; fails in R02, R06 from A7 GiBUU hybrid truth alone) and V-PRIOR class (14 valid; fails in R08, R15), with 12 valid under both, and reading (3)'s printed quantities labeled "computed after the pulls against the prior were seen (L4)".  
  *Record:* `OUTCOME-20261107-valid-region.md:21-25` (`CITABLE FOR`), `:27-37` (`NOT CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_fived16.tex:218`.  
  *Prohibitions (`NOT CITABLE FOR` lines 27–37):* Must strictly carry all negative constraints: (1) NOT citable for coverage (diagnostics grade bias, not coverage; no interval is validated); (2) NOT citable as a measurement (diagnostics of estimator on committed products; no reported value changes); (3) NOT citable for any physics claim about generators; (4) NOT citable for the cause of any departure; (5) NOT citable for V-PRIOR, or its threshold of 0.5, as ATLAS's or as the advisor's own formulation; (6) NOT citable as non-valid cells being excluded, wrong, or unreported (no cell is excluded or changed); (7) NOT citable for held-out truths; (8) ATLAS guide item 5 is NOT met; (9) NOT citable that 2D mismodeling is localized in the extra dimensions, or that it is not, in either direction; (10) reading (3) is NOT citable as a test.  
  *Resolution:* Incorporate classification as descriptive diagnostics while enforcing all negative constraints.

* **AUD-E5 [R]** — **Per-period 2D benchmark.**  
  *Finding:* Add the per-period 2D benchmark combined sentence from `readout.json` and the R5-bar sentence after `sec_results.tex:134`.  
  *Record:* `OUTCOME-20261107-per-period-2d-benchmark.md:13-16`, `:152`.  
  *Target:* `docs/analysis-note/sec_results.tex:134`.  
  *Status:* Drafted in round 1.

* **AUD-E6 [R]** — **RS1 rounding mechanism.**  
  *Finding:* Report numerical precision / float32 rounding findings (shifts up to 2.6σ_stat, median 0.8σ; separate tie-break vs refinement legs).  
  *Record:* `OUTCOME-20261108-rs1-rounding-mechanism.md:128-135`.  
  *Target:* `docs/analysis-note/sec_5d.tex:91`.  
  *Status:* Drafted in round 1.

* **AUD-E7 [T]** — **OVERCLAIM: The 2D comparison called a validation.**  
  *Finding:* Note called 2D comparison a validation (`sec_intro.tex:18`, `:30`, `sec_method.tex:25`, `sec_results.tex:1`, `sec_execsummary.tex:3`, `tab:validation-questions`).  
  *Record:* `AUDIT.txt` row E7; `CAMPAIGN-REVIEW-20260929.md:27-28`; `VALIDATION_LEDGER.md:175`.  
  *Target:* `docs/analysis-note/sec_intro.tex`, `sec_method.tex`, `sec_results.tex`, `sec_execsummary.tex`.  
  *Resolution:* Replace "validates" with "descriptive comparison" or "benchmark comparison against publication".

* **AUD-E8 [T]** — **The CH correction's scope.**  
  *Finding:* Executive summary stated CH correction without restricting it to joint cells.  
  *Record:* `AUDIT.txt` row E8; `sec_joint.tex:145-148`.  
  *Target:* `docs/analysis-note/sec_execsummary.tex:17`.  
  *Resolution:* Scope CH correction explicitly to joint cells.

* **AUD-E9 [R]** — **Response-only sensitivity ($N_3$) in `sec_fived16.tex`.**  
  *Finding:* Include Joseph's response-only sensitivity, median 1.65× interaction block σ (range 0.42–6.50), grid-dependent and not a bound.  
  *Record:* `DECISION-20261101-joseph-1b-keep-block-redesign-test.md:38-40`.  
  *Target:* `docs/analysis-note/sec_fived16.tex`.  
  *Status:* Drafted in round 1 as E9.

* **AUD-E10 [T]** — **Second post hoc choice ($N_7$) in Executive Summary.**  
  *Finding:* Executive summary must state background-treatment choice beside learner choice.  
  *Record:* `AUDIT.txt` row E10; `sec_method.tex:79`, `:103`; `DECISION-20261105-joseph-765-abstract-and-2d-disclosure.md:61-63`.  
  *Target:* `docs/analysis-note/sec_execsummary.tex:9`.  
  *Resolution:* Add sentence ending "the comparison with the publication is therefore not an independent test of the method".

### HELD and NOT DRAFTED in Round 1 (Status in Round 2)

* **AUD-N1 [T]** — **Note reframed from measurement to methods-and-benchmark record.**  
  *Finding:* Title, abstract, executive summary, `sec_fived16.tex`, and appendices must be unfrozen and reframed to the methods study. Ruled by Joseph in `DECISION-20261108` (#947).  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` item 1.  
  *Target:* `docs/analysis-note/main_note.tex:73`, `sec_execsummary.tex:6`, `sec_fived16.tex:1`, `app_landscape.tex:59`, `app_statmethods.tex:5`.  
  *Status:* Already drafted at `b1da7ba8` (commit `8cd2a974`); Round 2 verifies implementation and cross-section alignment.

* **AUD-N2 [T]** — **REF-G1 algorithm dependence as a stated limitation.**  
  *Finding:* The IBU vs OmniFold 16-cell difference ($T = 194.4$ against calibrated bar 28.12) must enter as a stated limitation with no new covariance block. Ruled by Joseph in `DECISION-20261108` (#947).  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` item 3, `OUTCOME-20261106-ref-g1-r1-differ.md:40-41`.  
  *Target:* `docs/analysis-note/sec_fived16.tex:280-320` (`sec:fived16-ibu`), `sec_execsummary.tex`.  
  *Status:* Already drafted at `b1da7ba8` (commit `12186634` as `sec:fived16-ibu`); Round 2 verifies implementation and cross-section alignment.

* **AUD-N3 [R]** — **Response-only sensitivity.**  
  *Finding:* Response-only sensitivity ($N_3$) documented under AUD-E9.  
  *Record:* `DECISION-20261101-joseph-1b-keep-block-redesign-test.md:38-40`.  
  *Status:* Drafted as AUD-E9.

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
  *Status:* Already drafted at `b1da7ba8` (commit `8cd2a974`); Round 2 verifies implementation and cross-section alignment.

* **AUD-N7 [T]** — **Second post hoc choice in Executive Summary.**  
  *Finding:* Background treatment choice documented under AUD-E10.  
  *Record:* `AUDIT.txt` row N7; `DECISION-20261105-joseph-765-abstract-and-2d-disclosure.md:61-63`.  
  *Status:* Drafted as AUD-E10.

### FLAGGED in Round 1 (No Record Contradicts; For Referee Read)

* **AUD-L1 [T]** — **Retract descriptive extra-dimensional localization claims.**  
  *Finding:* Descriptive central-value excesses must not be claimed as physical model localization in higher dimensions without covariance.  
  *Record:* `OUTCOME-20261107-valid-region.md:36` (`NOT CITABLE FOR localization in either direction`).  
  *Target:* `docs/analysis-note/sec_execsummary.tex:13`, `sec_3d.tex:140`, `sec_eavailw.tex:151`, `sec_joint.tex:237`.  
  *Resolution:* Strip physical localization wording; qualify as exploratory central comparisons.

* **AUD-L2 [T]** — **Tension anatomy run-period cause statement.**  
  *Finding:* Remove causal attribution for the 2D shape tension; state that run period accounts for variance only in poorly determined modes and cause remains unknown.  
  *Record:* `OUTCOME-20261107-per-period-2d-benchmark.md:18-25`.  
  *Target:* `docs/analysis-note/app_statmethods.tex:536`, `:554`, `:559`.  
  *Resolution:* Reconcile with per-period outcome record.

* **AUD-L3 [T]** — **5D estimator validation claim qualification.**  
  *Finding:* `sec_validation.tex:41` at base `b1da7ba8` claims "The five-dimensional estimator is validated", which conflicts with 1B STOP and unvalidated coverage.  
  *Record:* `OUTCOME-20261106-1b-stage1-receipt-stop.md`.  
  *Target:* `docs/analysis-note/sec_validation.tex:41`.  
  *Resolution:* Change "is validated" to "is evaluated under technical closure checks; coverage is unvalidated".

* **AUD-L4 [T]** — **Training-seed band description.**  
  *Finding:* `sec_method.tex:150` describes training-seed band as controlling ML stochasticity, but for configuration (e) training-seed block is zero while rounding shifts results up to 2.6σ_stat.  
  *Record:* `DECISION-20261106-joseph-b0-reconciliation-sentence.md:8`.  
  *Target:* `docs/analysis-note/sec_method.tex:150`.  
  *Resolution:* Clarify distinction between seed variance and floating-point rounding sensitivity.

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
  *Resolution:* Reconcile executive summary and §7.6 with §7.8 by removing contradictions. The rewrite adds no sentence claiming where the data–Tune difference sits; strip any localization wording per `OUTCOME-20261107-valid-region.md:36` and AUD-L1.

* **S1-ACC-2 [R]** — **Tune v1 normalization deficit quoted four ways.**  
  *Finding:* Deficit quoted as ~9% (ratio 0.91) in §6.5; 0.883 (10–28%) in §7.6; integrated data/Tune = 1.13 (0.885) in §7.8; ~12% in §2.5.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:45`, `sec_results.tex:85`, `sec_3d.tex:138`, `sec_eavailw.tex:148`.  
  *Resolution:* Reconcile all text to quote the exact values through `values.tex` / `values_fived16.tex` macros and specify phase-space definitions (reco vs truth fiducial vs $E_{\\text{avail}}$ marginal).

* **S1-ACC-3 [T]** — **Location of Tune v1 deficit in $p_T$.**  
  *Finding:* §2.5 says data/MC rises with $p_T$ (0.88 to 1.2), §6.5 says deficit is concentrated in low-$p_T$ peak, Fig. 14 says ratios below unity at lowest $p_T$.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:48`, `sec_results.tex:88`.  
  *Resolution:* Reconcile text: data/MC deficit is concentrated at lowest $p_T$ (< 0.4 GeV/c), rising above unity at $p_T > 1.0\\text{ GeV/c}$.

* **S1-ACC-4 [T]** — **5D coverage test conflation.**  
  *Finding:* Abstract says 5D coverage test "did not run to a result", conflating the 1,200-pseudo-experiment futility test (§9.5, ran, failed) with the staged 16-cell test (§10.5, stopped at 892/900 non-positive draws).  
  *Evidence:* `docs/analysis-note/main_note.tex:73`, `sec_5d.tex:216`, `sec_fived16.tex:253`.  
  *Resolution:* Disentangle the two tests explicitly in the abstract, §9.5, and §10.5.

* **S1-ACC-5 [T]** — **"Fresh" versus reused pseudo-experiments.**  
  *Finding:* §9.3 and App. C.8 say "40 fresh pseudo-experiments", while §9.4 states they "were used during development".  
  *Evidence:* `docs/analysis-note/sec_5d.tex:145`, `app_statmethods_nd.tex:112`.  
  *Resolution:* Replace "fresh" with "developmental pseudo-experiments".

* **S1-ACC-6 [T]** — **Unusable covariance used as a benchmark yardstick.**  
  *Finding:* Configuration-(a) 5D covariance is marked "not to be used" (§9.6), yet is used as a scale in §5.1, §8.4, §9.2, §9.3, Table 5, App. G.2.  
  *Evidence:* `docs/analysis-note/sec_5d.tex:225`, `sec_eavailw.tex:162`, `app_release.tex:72`.  
  *Resolution:* Governed by S2-COM-2. Do not type 6.145 and do not write "five bands unmeasured." The release checklist stays unedited while app_release.tex is held under AUD-N4. This row authorizes no tex edit.

* **S1-ACC-7 [T]** — **Executive summary marginalization claim (1–2%) vs body.**  
  *Finding:* Executive summary claims 4D and 5D marginalization passes to 1–2%, but §8.1 gives 0.11% total and 0.3–1.5% median per axis; §7.8 gives no number for 4D→3D.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:15`, `sec_eavailw.tex:110`, `sec_3d.tex:170`.  
  *Resolution:* Replace vague "1–2%" in executive summary with exact numbers from §8.1; add exact 4D→3D marginal closure number.

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
  *Resolution:* Replace "validation" with "feature-recovery closure tests".

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
  *Resolution:* Standardize numbers to exact macro values across all sections.

### Section 4: Completeness as a Citable Record

* **S2-COM-1 [T]** — **Unquantified "methodological finding" on nonlinear cross-terms.** Same finding as S1-COM-5.
* **S2-COM-2 [R]** — **Configuration-(a) 5D covariance exceeds seed-sensitivity limit.**  
  *Finding:* Configuration-(a) 5D covariance exceeds its predeclared stability limit ($s_{\\text{proj}} = 6.145\\%$ against the $5\\%$ bound, with 5 of 45 seed-pinned bands unmeasured in either direction, and pre-production null bound not met).  
  *Evidence:* `VALIDATION_LEDGER.md` `VL142`–`VL144`, `docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`, `CORRECTION-20260920-lower-bound-inference-withdrawn.md`, `OPERATIVE-SHEET-scalar5d.md`.  
  *Resolution:* The disclosure, when it is drafted, uses the adoption's words. M1 is s_proj = 6.145% against a 5% bound (DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:57). M3 (:73-79) says the seed variation does not probe those five bands, and the effect on the total when they also vary has not been measured. The lower-bound reading is withdrawn (CORRECTION-20260920-lower-bound-inference-withdrawn.md). The note must not say "five bands unmeasured" and must not type 6.145. This row authorizes no tex edit.
* **S2-COM-3 [T]** — **Learner and configuration dependence table.**  
  *Finding:* Consolidate algorithmic variations (exact-split vs LightGBM, seed shifts, MLP vs GBDT) into a unified summary table.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:115`.  
  *Resolution:* Create consolidated algorithmic variation table in §4 / §7.
* **S2-COM-4 [T]** — **Joint test condition (i) disclosure.**  
  *Finding:* Condition (i) fine-grid convergence unmeasured; disclose sub-grid residual limits.  
  *Evidence:* `docs/analysis-note/sec_joint.tex:120`.  
  *Resolution:* State condition (i) bounds explicitly in §11.
* **S2-COM-5 [T]** — **Joint tests omit hadronic response nuisance.**  
  *Finding:* Response model not shown to be complete; $\\pm 4\\%$ study did not regenerate nulls.  
  *Evidence:* `docs/analysis-note/sec_joint.tex:165`.  
  *Resolution:* Disclose hadronic response omission and implications in §11.
* **S2-COM-6 [T]** — **Offset control check failure disclosure.**  
  *Finding:* Offset check gives $\\chi^2 = 245.74$ for 16 ndf; disclose failure and implications.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:240`.  
  *Resolution:* Document offset check failure clearly in §10.
* **S2-COM-7 [T]** — **Sixteen-cell output algorithm dependence and stability.** Same finding as S1-COM-3 / AUD-N2 / REF-G1.
* **S2-COM-8 [T]** — **No 3D/4D uncertainty; no 3D/4D generator $\\chi^2$.**  
  *Finding:* 3D and 4D central values used for generator comparisons without evaluated covariance.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:145`, `sec_eavailw.tex:140`.  
  *Resolution:* Qualify all 3D/4D generator comparisons as purely descriptive central comparisons.
* **S2-COM-9 [T]** — **Ascencio et al. comparison unresolved.**  
  *Finding:* Data sit 9.2% and 6.0% above Ascencio on super-cells, confounded by differing $E_{\\text{avail}}$ definitions.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:185`.  
  *Resolution:* Detail definition differences ($11\\%$ event shift) and present comparison descriptively.
* **S2-COM-10 [T]** — **Hidden-variable closure fails at largest amplitude.**  
  *Finding:* Hidden-variable closure fails at $A = 0.30$; injected bump closures have narrow passes or no predeclared thresholds.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:170`.  
  *Resolution:* Disclose failure at $A = 0.30$ and discuss sensitivity limitations.
* **S2-COM-11 [T]** — **Purity-subtracted central value in use in 5D.**  
  *Finding:* Config-(a) 5D value retains known purity background bias (8–12$\\sigma$ stat at high $W$).  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:130`, App. C.8.  
  *Resolution:* Transparently state that configuration (a) retains purity bias in high-$W$ cells.
* **S2-COM-12 [T]** — **Unverified items admitted in text.** Same finding as S1-COM-7.
* **S2-COM-13 [T]** — **Reproduction is not possible.** Same finding as S1-CONT-6.
* **S2-COM-14 [T]** — **Fake-data tests are not held-out truths.** Same finding as S1-COM-3.
* **S2-COM-15 [T]** — **Extended fiducial prior envelope.**  
  *Finding:* Tier-2 prior envelope has median 7.9% (90th percentile 62%) with no covariance.  
  *Evidence:* `docs/analysis-note/sec_fps.tex:85`.  
  *Resolution:* Clarify exploratory nature of extended fiducial central values.

### Section 5: Self-Containment

* **S2-CONT-1 [T]** — **Ref. [52] specification and decisions.** Same finding as S1-CONT-2.
* **S2-CONT-2 [T]** — **Diagnostic record cited for definitions.** Same finding as S1-CONT-1.
* **S2-CONT-3 [T]** — **Companion journal article dependencies.** Same finding as S1-CONT-3.
* **S2-CONT-4 [T]** — **Numbers quoted from superseded/retired material.** Same finding as S1-CONT-4.
* **S2-CONT-5 [T]** — **Internal design review factor derivation.** Same finding as S1-CONT-2.
* **S2-CONT-6 [T]** — **Repository paths and file names in text.** Same finding as S1-CONT-6.
* **S2-CONT-7 [T]** — **Citations to private communications.** Same finding as S1-CONT-5.
* **S2-CONT-8 [T]** — **Internal stage/date jargon.**  
  *Finding:* Avoid internal milestone dates and phrases ("Stage 0", "condition set in July 2026").  
  *Evidence:* `docs/analysis-note/sec_5d.tex:135`, `sec_fived16.tex:210`.  
  *Resolution:* Replace internal project milestones with objective physical descriptions.
* **S2-CONT-9 [T]** — **Repository labels used before defined.** Same finding as S1-PRES-4.

### Section 6: Support for Claims

* **S2-CLM-1 [T]** — **Abstract 1% integral agreement.** Same finding as S1-CLM-1.
* **S2-CLM-2 [T]** — **Calibrated joint tests reject all ten.** Same finding as S1-CLM-5.
* **S2-CLM-3 [T]** — **Generator localization without covariance.** Same finding as S1-CLM-3.
* **S2-CLM-4 [T]** — **Closure validation claims.**  
  *Finding:* §5 claims "These closure tests validate the estimator", but 5D generator closure fails and hidden-variable closure fails at $A = 0.30$.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:30`.  
  *Resolution:* Qualify closure tests as technical feature checks rather than general statistical validation.
* **S2-CLM-5 [T]** — **$n=5$ iterations justified empirically.**  
  *Finding:* $n=5$ empirical justification based only on total cross section is incomplete given shape drift.  
  *Evidence:* `docs/analysis-note/sec_method.tex:85`.  
  *Resolution:* Fully disclose shape and dimensional sensitivity to iteration count.
* **S2-CLM-6 [T]** — **Sixteen-cell median uncertainty (7.86%).** Same finding as S1-CLM-2.
* **S2-CLM-7 [T]** — **"Methodological finding" on nonlinear cross-source terms.** Same finding as S1-COM-5 / S1-CLM-9.
* **S2-CLM-8 [T]** — **A.5 direct evidence of implicit regularization.**  
  *Finding:* App. A.5 claims direct evidence that ~1 $\\chi^2$ unit is due to implicit regularization rather than physics disagreement.  
  *Evidence:* `docs/analysis-note/app_statmethods.tex:545`.  
  *Resolution:* Reframe as demonstrating estimator sensitivity of the $\\chi^2$ statistic rather than attributing physical vs algorithmic origin.
* **S2-CLM-9 [T]** — **Five-dimensional unfolding adds information.**  
  *Finding:* Reconstructed $W$ is an exact algebraic function of $(p_T, p_\\parallel, q_3)$; added information of $W$ unmeasured.  
  *Evidence:* `docs/analysis-note/sec_method.tex:115`, `sec_eavailw.tex:40`.  
  *Resolution:* State explicitly that $W$ is kinematically redundant with $(p_T, p_\\parallel, q_3)$ and added information has not been quantified.

### Section 7: Minor Issues and Presentation

* **S2-PRES-1 [T]** — **Length and executive summary organization.** Same finding as S1-PRES-1.
* **S2-PRES-2 [T]** — **Heavy repetition of caveats.** Same finding as S1-PRES-2.
* **S2-PRES-3 [T]** — **Appendix figures/tables numbering and splitting across pages.**  
  *Finding:* Fix figures/tables numbered after use or split awkwardly across pages (Figs. 36, 37; Tables 3, 6, 13, 16, 18).  
  *Evidence:* Global formatting.  
  *Resolution:* Clean up LaTeX floats and table layouts.
* **S2-PRES-4 [T]** — **Fig. 9 prints per-panel $\\chi^2$ from weight statistics.**  
  *Finding:* Fig. 9 prints misleading per-panel $\\chi^2$ computed from MC weight statistics alone.  
  *Evidence:* Caption and annotations on Fig. 9.  
  *Resolution:* Remove misleading weight-statistical $\\chi^2$ values or explain strictly in caption.
* **S2-PRES-5 [T]** — **Fig. 7 error bars are MC weight statistics.**  
  *Finding:* Headline figure error bars are MC weight statistics, not experimental uncertainties.  
  *Evidence:* Caption to Fig. 7.  
  *Resolution:* Explicitly explain error bar meaning in caption.
* **S2-PRES-6 [T]** — **Fig. 23 colorbar reads `data/GENIE` instead of `data/Tune v1`.**  
  *Finding:* Mislabeled denominator on Fig. 23 colorbar.  
  *Evidence:* Fig. 23 graphic and caption.  
  *Resolution:* Update label to `data / Tune v1`.
* **S2-PRES-7 [T]** — **Statements citing AI agent session replay.** Same finding as S1-CONT-7.
* **S2-PRES-8 [T]** — **Dates, internal job labels, file names in text.** Same finding as S1-PRES-3.
* **S2-PRES-9 [T]** — **Terminology used before defined.** Same finding as S1-PRES-4.
* **S2-PRES-10 [T]** — **Figure-based numbers cited without tables.**  
  *Finding:* Text quotes numbers read from figures (e.g., Fig. 23 ratios) without supporting tables.  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:150`.  
  *Resolution:* Provide tabulated values or cite explicitly as visual estimates.

---

## Part 4: Gemini Report 1 (`gemini-note-r1-1.txt`)

### Section 3: Accuracy

* **G1-ACC-1 [T]** — **Inconsistent fiducial nucleon count.**  
  *Finding:* Fiducial target nucleon count is quoted as $N = 4.123 \\times 10^{30}$ in §3.4 and $4.128 \\times 10^{30}$ in §8.2.  
  *Evidence:* `docs/analysis-note/sec_method.tex:128`, `sec_eavailw.tex:50`.  
  *Resolution:* Harmonize target nucleon count across all sections to the standard MINERvA value.
* **G1-ACC-2 [T]** — **Discrepancy in raw run-period $\\chi^2$.**  
  *Finding:* Raw run-period $\\chi^2 = 209.6$ in §4.5 vs $205.8$ in Table 3.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:165`, Table 3.  
  *Resolution:* Reconcile text and Table 3 to reflect the exact value from `values.tex`.
* **G1-ACC-3 [T]** — **Inconsistent degrees of freedom in held-out-tune test.** Same finding as S2-ACC-8.
* **G1-ACC-4 [T]** — **Marginal normalization check agreement overstated in Executive Summary.** Same finding as S1-ACC-7 / S2-ACC-17.
* **G1-ACC-5 [T]** — **Discrepancy between systematic median uncertainty in text and Table 8.**  
  *Finding:* Systematic median uncertainty quoted as 5.14% in §4.1 vs 5.38% in Table 8.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:45`, Table 8.  
  *Resolution:* Reconcile text with Table 8 macros.
* **G1-ACC-6 [D]** — **Neutral pion mass subtraction for charged pions in Eq. (1).**  
  *Finding:* Referee questions $(E_{\\pi^\\pm} - m_{\\pi^0})$ in $E_{\\text{avail}}$ definition as unphysical.  
  *Resolution:* **DISPUTE.** The subtraction $E_{\\text{avail}} = \\sum T_p + \\sum T_\\pi + \\sum E_\\gamma + (E_{\\pi^\\pm} - m_{\\pi^0})$ is the established, published MINERvA analysis definition inherited from previous CC-inclusive analyses. Clarify text to state explicitly that this is an intentional convention.
* **G1-ACC-7 [T]** — **Massless-lepton approximation in Table 10.**  
  *Finding:* Table 10 lists $Q^2 = 4 E_\\nu E_\\mu \\sin^2(\\theta/2)$, which is ultra-relativistic approximation ($m_\\mu = 0$).  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:55`, Table 10.  
  *Resolution:* Add exact muon-mass formula or note that Table 10 describes nominal generator coordinate definitions.
* **G1-ACC-8 [T]** — **Exact-split estimator reproducibility description.**  
  *Finding:* Reconcile "unseeded reproducible to $7 \\times 10^{-15}$" with "reseeding moves bins by up to 1.6%".  
  *Evidence:* `docs/analysis-note/sec_method.tex:98`.  
  *Resolution:* Clarify that bitwise reproduction was achieved under the unseeded default runtime, but reseeding demonstrates 1.6% algorithmic sensitivity.
* **G1-ACC-9 [T]** — **GiBUU cell count reconciliation.**  
  *Finding:* 8 cells in §10 vs 72 cells in Table 11.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:18`, Table 11.  
  *Resolution:* Clarify in text: GiBUU covers 8 of the 16 reporting cells in §10, and 72 of the 109 joint cells in §11.

### Section 4: Completeness as a Citable Record

* **G1-COM-1 [T]** — **The 5D coverage test did not produce a result.** Same finding as S1-ACC-4.
* **G1-COM-2 [T]** — **Detector-response-mismatch closure test is unexecuted.** Same finding as S2-ACC-5.
* **G1-COM-3 [T]** — **Complete absence of 3D and 4D uncertainty quantification.** Same finding as S2-COM-8.
* **G1-COM-4 [T]** — **Headline 5D central value retains known-biased purity background subtraction.** Same finding as S2-COM-11.
* **G1-COM-5 [R]** — **The 5-axis covariance ($C_Z$) exceeds pre-declared stability thresholds.** Same finding as S2-COM-2.
* **G1-COM-6 [T]** — **Uncorrected playlist pooling bias.**  
  *Finding:* Global exposure ratio induces $-1.83\\%$ to $+3.78\\%$ single-cell pooling bias.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:202`.  
  *Resolution:* Disclose pooling bias in systematics discussion.
* **G1-COM-7 [R]** — **Ad hoc construction of run-period covariance block ($C_{\\text{PL}}$).** Same finding as S1-COM-8.
* **G1-COM-8 [T]** — **NormDISCC systematic category carried as unverified zero.**  
  *Finding:* NormDISCC carried as zero without confirmation.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:198`.  
  *Resolution:* State transparently that NormDISCC is supplied as zero in MAT inputs and carried as zero.
* **G1-COM-9 [T]** — **Numerical instability under float32 rounding.** Same finding as S2-COM-3 / AUD-E6.

### Section 5: Self-Containment

* **G1-CONT-1 [T]** — **Heavy reliance on inaccessible internal records ("Ref. [37]").** Same finding as S1-CONT-1.
* **G1-CONT-2 [T]** — **Citations to private communications with anomalous dates.** Same finding as S1-CONT-5.
* **G1-CONT-3 [T]** — **Lost run logs and unrecorded configurations.** Same finding as S2-COM-3.
* **G1-CONT-4 [T]** — **Incomplete mathematical definition of reconstructed available energy.** Same finding as S2-COM-9.

### Section 6: Support for Claims

* **G1-CLM-1 [T]** — **Claim of "reproducing" the published cross section.** Same finding as S1-CLM-1.
* **G1-CLM-2 [T]** — **Claim that native OmniFold miss handling requires no efficiency correction.**  
  *Finding:* OmniFold handles misses via Step 1 reweighting without explicit efficiency divisor.  
  *Evidence:* `docs/analysis-note/sec_method.tex:60`.  
  *Resolution:* Clarify mathematical foundation of OmniFold miss handling.
* **G1-CLM-3 [T]** — **Claim that GBDTs match or outperform neural networks for this application.**  
  *Finding:* Claim that GBDTs outperform neural networks is supported only by limited MLP checks.  
  *Evidence:* `docs/analysis-note/sec_method.tex:80`, `sec_3d.tex:135`.  
  *Resolution:* Qualify statement: GBDT provided superior training stability and convergence speed in our tabular implementation.
* **G1-CLM-4 [T]** — **Claim that low-$E_{\\text{avail}}$ excess confirms established low-recoil excess.** Same finding as S1-CLM-3 / S2-CLM-3.
* **G1-CLM-5 [T]** — **Claim of rejecting generator predictions in §11.** Same finding as S1-CLM-5.

### Section 7: Minor Issues and Presentation

* **G1-PRES-1 [T]** — **Anomalous and future dates.** Same finding as S1-PRES-3.
* **G1-PRES-2 [T]** — **Patchwork presentation of configurations.** Same finding as S1-PRES-4.
* **G1-PRES-3 [T]** — **Misleading error bar conventions in figures.** Same finding as S2-PRES-5.
* **G1-PRES-4 [T]** — **Hadronic catch bin compression.**  
  *Finding:* Explain catch bin handling in kinematic distributions.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:55`.  
  *Resolution:* Document catch bin definitions clearly in text and captions.
* **G1-PRES-5 [T]** — **Inconsistent kinematic notation ($p_\\parallel$ vs $p_z$).**  
  *Finding:* Longitudinal momentum denoted interchangeably as $p_\\parallel$, $p_z$, `p_||`.  
  *Evidence:* Figures 5, 17, 18, text.  
  *Resolution:* Standardize to $p_\\parallel$ across all LaTeX sources.
* **G1-PRES-6 [T]** — **Incomplete table entries.**  
  *Finding:* Missing entries or blank cells in summary tables.  
  *Evidence:* Table 2, Table 6.  
  *Resolution:* Populate all table cells or explicitly mark non-applicable entries.
* **G1-PRES-7 [T]** — **Confusing label conventions in Figure 23.** Same finding as S2-PRES-6.
* **G1-PRES-8 [T]** — **Missing units on corner plot axes.**  
  *Finding:* Figure 2 lacks units on several sub-axes.  
  *Evidence:* Fig. 2 graphic.  
  *Resolution:* Ensure all kinematic variables specify units (GeV, GeV/c, deg).
* **G1-PRES-9 [T]** — **Inappropriate register and defensive tone.**  
  *Finding:* Avoid internal software tracker phrases ("until 2026-10-11", "run log not found", "inferred, not verified").  
  *Evidence:* `docs/analysis-note/sec_method.tex:95`, `sec_systematics.tex:195`.  
  *Resolution:* Refactor text into formal, objective archival register while preserving full scientific disclosures.
* **G1-PRES-10 [T]** — **Average nucleon mass definition $\\bar{M}$.**  
  *Finding:* In §8.2, average nucleon mass is defined as $\\bar{M} = (1.5 M_n + M_p)/2.5$. Origin of 1.5:1 ratio for CH tracker should be stated.  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:52`.  
  *Resolution:* State the isotopic/target weighting convention used by the MAT framework.

---

## Part 5: Gemini Report 2 (`gemini-note-r1-2.txt`)

### Section 3: Accuracy

* **G2-ACC-1 [T]** — **Discrepancy in Target Nucleon Count $N$.** Same finding as G1-ACC-1.
* **G2-ACC-2 [T]** — **Inconsistent Marginal Normalization Agreement Metrics.** Same finding as S1-ACC-7 / S2-ACC-17 / G1-ACC-4.
* **G2-ACC-3 [T]** — **Inconsistent Run-Period $\\chi^2$ Values.** Same finding as G1-ACC-2.
* **G2-ACC-4 [T]** — **Conflicting Statements on Run-Period Block Variance Impact.** Same finding as S2-ACC-10.
* **G2-ACC-5 [T]** — **Discrepancy in Total Cross-Section Values.**  
  *Finding:* Total cross section quoted as $3.073 \\times 10^{-38}\\text{ cm}^2$ vs $3.07 \\times 10^{-38}\\text{ cm}^2$.  
  *Evidence:* `docs/analysis-note/sec_results.tex:80`, `sec_execsummary.tex:5`.  
  *Resolution:* Quote exact macro value everywhere.
* **G2-ACC-6 [T]** — **Inconsistent Degrees of Freedom in Held-Out Coverage Tests.** Same finding as S2-ACC-8 / G1-ACC-3.
* **G2-ACC-7 [T]** — **Unexplained Higher-Dimensional Bin Count.** Same finding as S2-ACC-18.
* **G2-ACC-8 [T]** — **Face-Invalid $\\chi^2$ Annotations in Figures 9 and 10.** Same finding as S2-PRES-4.

### Section 4: Completeness as a Citable Record

* **G2-COM-1 [D]** — **Manuscript Truncation.**  
  *Finding:* Referee reported document truncated at line 5,948 (§9.4).  
  *Resolution:* **DISPUTE / VOID.** Truncation occurred on the reader's side at 31,717 words. The rater copy `note-r1.blind.txt` was verified complete at 69,536 words (139 pp). Void per director's instructions.
* **G2-COM-2 [T]** — **Complete Absence of 3D and 4D Covariance Matrices.** Same finding as S2-COM-8 / G1-COM-3.
* **G2-COM-3 [T]** — **Unvalidated and Failing Statistical Coverage.** Same finding as S1-COM-1.
* **G2-COM-4 [T]** — **Uncorrected Miss-Weight Approximation in Systematics.**  
  *Finding:* Miss weights evaluated on central MC without reweighting under systematic universes.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:190`.  
  *Resolution:* Disclose miss-weight approximation in systematics discussion.
* **G2-COM-5 [T]** — **Pending Detector-Response Mismatch Closure Test.** Same finding as S2-ACC-5 / G1-COM-2.
* **G2-COM-6 [T]** — **Missing Configuration Records and Run Logs.** Same finding as S2-COM-3 / G1-CONT-3.
* **G2-COM-7 [T]** — **Unverified Systematics (Zeroed DIS and Inferred POT).** Same finding as S2-COM-12 / G1-COM-8.

### Section 5: Self-Containment

* **G2-CONT-1 [T]** — **Opaque Private Audit Citations (`Ref. [37]`).** Same finding as S1-CONT-1.
* **G2-CONT-2 [T]** — **Circular Dependency on the Companion Methods Paper.** Same finding as S1-CONT-3.
* **G2-CONT-3 [T]** — **Reliance on Private Communication for Modeling Choices.** Same finding as S1-CONT-5.

### Section 6: Support for Claims

* **G2-CLM-1 [T]** — **Claim of "Reproducing" Published Cross Section within ~1%.** Same finding as S1-CLM-1.
* **G2-CLM-2 [T]** — **Claim of a "Five-Observable Unfolding".** Same finding as S2-CLM-9.
* **G2-CLM-3 [T]** — **Claim of Calibrated Hypothesis-Testing Rejections of Generator Predictions.** Same finding as S1-CLM-5.
* **G2-CLM-4 [T]** — **Claim that Low-$E_{\\text{avail}}$ Excess Corresponds to Established Low-Recoil Excess.** Same finding as S1-CLM-3 / S2-CLM-3 / G1-CLM-4.
* **G2-CLM-5 [T]** — **Claim of a Meaningful 7.86% Uncertainty on 16-Cell Output.** Same finding as S1-CLM-2 / S2-CLM-6.

### Section 7: Minor Issues and Presentation

* **G2-PRES-1 [T]** — **Inappropriate Editorial Tone and Register.** Same finding as G1-PRES-9.
* **G2-PRES-2 [T]** — **Misleading Error Bars on Headline Figures.** Same finding as S2-PRES-5 / G1-PRES-3.
* **G2-PRES-3 [T]** — **Missing Uncertainties on Comparison Figures.**  
  *Finding:* Fig. 13 and Fig. 22 show comparisons without error bars.  
  *Evidence:* Figs. 13, 22.  
  *Resolution:* Explain clearly in captions that points represent central value comparisons without evaluated joint covariance.
* **G2-PRES-4 [T]** — **Mislabeled Denominator in Figure 23.** Same finding as S2-PRES-6 / G1-PRES-7.
* **G2-PRES-5 [T]** — **Proliferation and Fragmented Usage of Estimator Configurations.** Same finding as S1-PRES-4 / G1-PRES-2.
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
