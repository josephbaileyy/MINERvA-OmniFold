# Companion Analysis Note: Round 1 Referee Findings and Currency Audit Issue Ledger (ISSUES.md)

**Branch:** `draft/note-round2-20261108`  
**Base Commit:** `b1da7ba8372348d9600d043eb381f676db25e1df`  
**Governing Decision:** `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` (`af73565048b2882efa1ea52f1d8a953902aceb31`, PR #947)  
**Evidence Sources:**
- Round 1 Referee Reports (PR #950, commit `29ab9096a279eb19da6dcbed1de705aa51262a83`):
  - `sonnet-note-r1-1.txt`
  - `sonnet-note-r1-2.txt`
  - `gemini-note-r1-1.txt`
  - `gemini-note-r1-2.txt`
- Round 1 Currency Audit: `docs/orchestration/state/2d-closeout/stageF/methods/note-round1-20261108/AUDIT.txt` (`b1da7ba8372348d9600d043eb381f676db25e1df`)

---

## Classification Taxonomy

Every item is classified under one of four mutually exclusive codes per the director's instructions:
- **[T] Text fix:** Wording, qualification, reconciliation, structural reordering, or contextual explanation resolvable in LaTeX sources without changing numerical inputs.
- **[R] Existing Record Number:** Requires pulling an exact verified number or macro from an existing committed record, readout JSON, or values file (`values*.tex`, `make_values_landed.py`).
- **[A] Analysis Required:** Demands a new calculation, simulation, or compute campaign. Forwarded to the director; cannot be cured by wording.
- **[D] Dispute:** The referee's finding is factually mistaken or contradicted by governed repository decisions and records. Documented with governing evidence.

*Rule on Gemini 2:* Gemini 2's completeness findings on the missing second half (§§9.5–13, Appendices A–H) are ruled **VOID** because its rater input was truncated at 31,717 words on the reader's side.

---

## Summary of Classifications

| Source | Total Items | Class T (Text) | Class R (Record) | Class A (Analysis) | Class D (Dispute / Void) |
|---|---:|---:|---:|---:|---:|
| **AUDIT.txt** (E1–E10, N1–N7, L1–L4) | 21 | 18 | 2 | 0 | 1 |
| **Sonnet Report 1** (S1-ACC, S1-COM) | 30 | 25 | 4 | 0 | 1 |
| **Sonnet Report 2** (S2-ACC, S2-COM) | 39 | 34 | 2 | 0 | 3 |
| **Gemini Report 1** (G1-ACC, G1-COM, G1-PRES) | 27 | 23 | 0 | 0 | 4 |
| **Gemini Report 2** (G2-ACC, G2-PRES, G2-VOID) | 15 | 8 | 0 | 0 | 7 |
| **Unique Non-Redundant Issues** | **78** | **61** | **6** | **0** | **11** |

*Note on Class A:* No item in Round 2 requires new compute campaigns. Under `DECISION-20261108`, the analysis note is reframed as the technical record of the methods-and-benchmark study. Algorithmic limitations, unvalidated coverage, rounding sensitivity, and unexecuted closures are primary methodological findings and benchmark deliverables to be reported transparently, not bugs to be computed away.

---

## Part 1: Currency Audit Items (`AUDIT.txt`)

Base: `b1da7ba8372348d9600d043eb381f676db25e1df`

### EDITED in Round 1 (Review & Verification)

* **AUD-E1 [T]** — **COV2D held-out tune result.**  
  *Finding:* Held-out tune test results (0/300 coverage at AR23 and G18) must be integrated into the note without violating pinned adjacent sentences.  
  *Record:* `OUTCOME-20261108-cov2d-both-tunes-under-cover.md:99-106` (`CITABLE FOR`), `:108-119` (`NOT CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_validation.tex:199`, `sec_systematics.tex:53`, `sec_systematics.tex:214`, `sec_execsummary.tex:21`.  
  *Status:* Integrated in round 1; verify flow and placement after paragraph's final sentence to keep `check_note_records.py` green.

* **AUD-E2 [T]** — **1B STOP rule and counts.**  
  *Finding:* The 5D coverage pre-check fail-closed rule and exact draw counts (892 of 900 draws with non-positive composite denominator; up to 62 cells) must be explicitly stated.  
  *Record:* `OUTCOME-20261106-1b-stage1-receipt-stop.md:27-30`, `:101-104`.  
  *Target:* `docs/analysis-note/sec_fived16.tex:253`, `sec_5d.tex:216`.  
  *Status:* Drafted in round 1; verify exact wording matches record.

* **AUD-E3 [T]** — **1B pre-check Part 1 (flux and detector groups).**  
  *Finding:* State Part 1 pre-check outcome: both flux and detector groups reproduce within the [0.9, 1.1] window; GEANT neutron and proton bands depart in named cells.  
  *Record:* `OUTCOME-20261108-1b-precheck-part1.md:49-62` (`CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_fived16.tex:253`.  
  *Status:* Drafted in round 1.

* **AUD-E4 [T]** — **Valid-region classes of the 16 cells.**  
  *Finding:* Tabulate V-ATLAS (14 valid; not R02, R06) and V-PRIOR (14 valid; not R08, R15), with 12 valid under both. Clarify neither is a coverage test.  
  *Record:* `OUTCOME-20261107-valid-region.md:21-25` (`CITABLE FOR`), `:27-37` (`NOT CITABLE FOR`).  
  *Target:* `docs/analysis-note/sec_fived16.tex:218`.  
  *Status:* Drafted in round 1.

* **AUD-E5 [T]** — **Per-period 2D benchmark.**  
  *Finding:* Add the per-period 2D benchmark combined sentence from `readout.json` and the R5-bar sentence after `sec_results.tex:134`.  
  *Record:* `OUTCOME-20261107-per-period-2d-benchmark.md:13-16`, `:152`.  
  *Target:* `docs/analysis-note/sec_results.tex:134`.  
  *Status:* Drafted in round 1.

* **AUD-E6 [T]** — **RS1 rounding mechanism.**  
  *Finding:* Report numerical precision / float32 rounding findings (shifts up to 2.6σ_stat, median 0.8σ; separate tie-break vs refinement legs).  
  *Record:* `OUTCOME-20261108-rs1-rounding-mechanism.md:128-135`.  
  *Target:* `docs/analysis-note/sec_5d.tex:91`.  
  *Status:* Drafted in round 1.

* **AUD-E7 [T]** — **RPD-RECO reconstruction check.**  
  *Finding:* Report the reconstruction-level run-period check (+6.10% shift).  
  *Record:* `OUTCOME-20261106-rpd-reco-clean-run.md:112-118`.  
  *Target:* `docs/analysis-note/sec_fived16.tex:174`.  
  *Status:* Drafted in round 1.

* **AUD-E8 [T]** — **1B pre-check Part 0 (interaction group unlike objects).**  
  *Finding:* Report interaction group unlike-objects diagnosis; keep the two-cell caveat (R00, R05) and drop "at the data".  
  *Record:* `OUTCOME-20261106-1b-precheck-interaction-unlike.md:10-25`.  
  *Target:* `docs/analysis-note/sec_fived16.tex:248`.  
  *Status:* Drafted in round 1.

* **AUD-E9 [R]** — **Missing 16-cell values macros.**  
  *Finding:* Ensure all 16-cell values, uncertainties, and χ² values are routed through `values_fived16.tex` macros.  
  *Record:* `values_fived16.tex`, `make_values_fived16.py`.  
  *Target:* `docs/analysis-note/sec_fived16.tex`.  
  *Status:* Verified macros generated.

* **AUD-E10 [T]** — **Reframed 16-cell description.**  
  *Finding:* Frame the 16-cell output as illustrative benchmark demonstrating calibrated generator tests, not for model fitting.  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md`.  
  *Target:* `docs/analysis-note/sec_fived16.tex:1-15`.  
  *Status:* Drafted in round 1.

### HELD in Round 1 (Operative in Round 2 under DECISION-20261108)

* **AUD-N1 [T]** — **Note reframed from measurement to methods-and-benchmark record.**  
  *Finding:* Title, abstract, executive summary, `sec_fived16.tex`, and appendices must be unfrozen and reframed to the methods study.  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` item 1.  
  *Target:* `docs/analysis-note/main_note.tex:73`, `sec_execsummary.tex:6`, `sec_fived16.tex:1`, `app_landscape.tex:59`, `app_statmethods.tex:5`.  
  *Action:* Draft complete reframing in Round 2.

* **AUD-N2 [T]** — **REF-G1 algorithm dependence as a stated limitation.**  
  *Finding:* The IBU vs OmniFold 16-cell difference ($T = 194.4$ against calibrated bar 28.12) must enter as a stated limitation with no new covariance block.  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` item 3, `OUTCOME-20261106-ref-g1-r1-differ.md:40-41`.  
  *Target:* `docs/analysis-note/sec_fived16.tex`, `sec_execsummary.tex`.  
  *Action:* Draft stated limitation text.

* **AUD-N4 [T]** — **Release appendix update.**  
  *Finding:* Align data release appendix with methods-and-benchmark schema, referencing archived measurement package.  
  *Record:* `DECISION-20261106-joseph-methods-study-and-archive.md:57-61`.  
  *Target:* `docs/analysis-note/app_release.tex:4`, `:58`.  
  *Action:* Update text in Round 2.

* **AUD-N5 [T]** — **Event-loop preservation CFS path.**  
  *Finding:* Reference committed CFS event-loop preservation path.  
  *Record:* `DECISION-20261101-joseph-eventloops-copy-to-cfs.md:28-34`.  
  *Target:* `docs/analysis-note/app_release.tex:50`, `:53`.  
  *Action:* Add path reference.

* **AUD-N6 [T]** — **Abstract resync.**  
  *Finding:* Resync note abstract to match reframed paper abstract.  
  *Record:* `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md`.  
  *Target:* `docs/analysis-note/main_note.tex:73`.  
  *Action:* Completed in commit `bd4cabea7`; verify in Round 2.

* **AUD-L1 [T]** — **Retract descriptive extra-dimensional localization claims.**  
  *Finding:* Descriptive central-value excesses must not be claimed as physical model localization in higher dimensions without covariance.  
  *Record:* `OUTCOME-20261107-valid-region.md:36` (`NOT CITABLE FOR localization in either direction`).  
  *Target:* `docs/analysis-note/sec_execsummary.tex:13`, `sec_3d.tex:140`, `sec_eavailw.tex:151`, `sec_joint.tex:237`.  
  *Action:* Strip physical localization wording; qualify as exploratory central comparisons.

* **AUD-L2 [T]** — **Tension anatomy run-period cause statement.**  
  *Finding:* Remove causal attribution for the 2D shape tension; state that run period accounts for variance only in poorly determined modes and cause remains unknown.  
  *Record:* `OUTCOME-20261107-per-period-2d-benchmark.md:18-25`.  
  *Target:* `docs/analysis-note/app_statmethods.tex:536`, `:554`, `:559`.  
  *Action:* Reconcile with per-period outcome record.

* **AUD-L3 [T]** — **5D estimator validation claim qualification.**  
  *Finding:* `sec_validation.tex:39` claims "The five-dimensional estimator is validated", which conflicts with 1B STOP and unvalidated coverage.  
  *Record:* `OUTCOME-20261106-1b-stage1-receipt-stop.md`.  
  *Target:* `docs/analysis-note/sec_validation.tex:39`.  
  *Action:* Change "is validated" to "is evaluated under technical closure checks; coverage is unvalidated".

* **AUD-L4 [T]** — **Training-seed band description.**  
  *Finding:* `sec_method.tex:150` describes training-seed band as controlling ML stochasticity, but for configuration (e) training-seed block is zero while rounding shifts results up to 2.6σ_stat.  
  *Record:* `DECISION-20261106-joseph-b0-reconciliation-sentence.md:8`.  
  *Target:* `docs/analysis-note/sec_method.tex:150`.  
  *Action:* Clarify distinction between seed variance and floating-point rounding sensitivity.

---

## Part 2: Sonnet Report 1 (`sonnet-note-r1-1.txt`)

### Section 3: Accuracy

* **S1-ACC-1 [T]** — **Tune v1 in quasielastic-Δ dip inconsistency.**  
  *Finding:* Executive summary and §7.6 assert all four generators under-predict data in the dip ($0.1 \le E_{\text{avail}} < 0.4\text{ GeV}$), but §7.8 states the $E_{\text{avail}}$-marginal data/Tune v1 ratio dips to 1.01 (matching data), and Fig. 23 shows cells dipping to 0.66.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:13`, `sec_3d.tex:140`, `sec_eavailw.tex:151`.  
  *Resolution:* Correct executive summary and §7.6: Tune v1 matches data in the dip; the data excess over Tune v1 is localized at high $E_{\text{avail}}$ and high $W$.

* **S1-ACC-2 [T/R]** — **Tune v1 normalization deficit quoted four ways.**  
  *Finding:* Deficit quoted as ~9% (ratio 0.91) in §6.5; 0.883 (10–28%) in §7.6; integrated data/Tune = 1.13 (0.885) in §7.8; ~12% in §2.5.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:45`, `sec_results.tex:85`, `sec_3d.tex:138`, `sec_eavailw.tex:148`.  
  *Resolution:* Reconcile all text to quote the exact values through `values.tex` / `values_fived16.tex` macros and specify phase-space definitions (reco vs truth fiducial vs $E_{\text{avail}}$ marginal).

* **S1-ACC-3 [T]** — **Location of Tune v1 deficit in $p_T$.**  
  *Finding:* §2.5 says data/MC rises with $p_T$ (0.88 to 1.2), §6.5 says deficit is concentrated in low-$p_T$ peak, Fig. 14 says ratios below unity at lowest $p_T$.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:48`, `sec_results.tex:88`.  
  *Resolution:* Reconcile text: data/MC deficit is concentrated at lowest $p_T$ (< 0.4 GeV/c), rising above unity at $p_T > 1.0\text{ GeV/c}$.

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
  *Resolution:* Remove config-(a) covariance from the release checklist; state explicitly that it failed acceptance criteria and qualify any use as purely exploratory/diagnostic.

* **S1-ACC-7 [T]** — **Executive summary marginalization claim (1–2%) vs body.**  
  *Finding:* Executive summary claims 4D and 5D marginalization passes to 1–2%, but §8.1 gives 0.11% total and 0.3–1.5% median per axis; §7.8 gives no number for 4D→3D.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:15`, `sec_eavailw.tex:110`, `sec_3d.tex:170`.  
  *Resolution:* Replace vague "1–2%" in executive summary with exact numbers from §8.1; add exact 4D→3D marginal closure number.

* **S1-ACC-8 [T]** — **Band count typo in cross-covariance.**  
  *Finding:* §10.2 names four failing weight checks (AGKYxF1pi, AhtBY, BhtBY, MinosEfficiency), then writes "These five enter as...".  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:112`.  
  *Resolution:* Change "five" to "four".

* **S1-ACC-9 [T]** — **"At least fifteen-fold" arithmetic error.**  
  *Finding:* §3.2 claims purity bias reduced "at least fifteen-fold (from 3.5% to 4.1% to 0.11% to 0.24%)"; worst case is 3.5 / 0.24 = 14.58.  
  *Evidence:* `docs/analysis-note/sec_method.tex:92`.  
  *Resolution:* Change "at least fifteen-fold" to "an order of magnitude (from 3.5–4.1% to 0.11–0.24%)".

* **S1-ACC-10 [T]** — **Hyperparameter tuning sequence clarification.**  
  *Finding:* §3.2 claims learner settings fixed a priori, but refinement classifier (400 trees, 31 leaves) was expanded after background bias was found.  
  *Evidence:* `docs/analysis-note/sec_method.tex:85`, `sec_5d.tex:138`.  
  *Resolution:* Clarify that baseline settings were fixed a priori, while refinement capacity was expanded in configuration (e)/(f) in response to observed high-$W$ purity bias.

* **S1-ACC-11 [T]** — **Two $\chi^2$ values for same quantity in §4.5.**  
  *Finding:* $p_\parallel\ \chi^2$ given as 34.4 against earlier 2D budget and 34.8 against other blocks alone.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:168`, `:175`.  
  *Resolution:* Explicitly differentiate the two comparators in the text.

* **S1-ACC-12 [T/R]** — **Suspicious duplicate numbers.**  
  *Finding:* 3D marginal 0.141% (§7.3) vs QA difference +0.141% (§10.2); $C_{\text{model}}$ median 3.71% (§4.6) vs flux median 3.71% (§4.1); NuWro/GiBUU $r_c$ 0.923/0.963 (§11.9).  
  *Evidence:* `docs/analysis-note/sec_3d.tex:112`, `sec_fived16.tex:115`, `sec_systematics.tex:42`, `sec_joint.tex:285`.  
  *Resolution:* Verify against underlying readout files; clarify coincidences and correct any transcription typos.

* **S1-ACC-13 [T]** — **Closures use configuration (a) while quoted 3D/4D values use (e).**  
  *Finding:* §7.4 notes closures on (a) do not extend to (e), yet configurations are presented side by side.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:125`, `sec_method.tex:65`.  
  *Resolution:* State explicitly that configuration (a) was used for exploratory closures, while configuration (e) was adopted for central values to cure purity bias.

* **S1-ACC-14 [T]** — **Matched-projection claim in executive summary.**  
  *Finding:* Executive summary claims matched coarse projections reject all generators, but Table 29 shows GENIE CV is not rejected in $(p_T, p_\parallel)$ ($p = 0.48$).  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:18`, `sec_joint.tex:320`.  
  *Resolution:* Narrow executive summary claim to note that GENIE CV is consistent in muon kinematics coarse projection.

* **S1-ACC-15 [T]** — **Terminology of $J$ (109 cells).**  
  *Finding:* §9.4 calls $J$ "109 supported fine joint cells", while §11.1 calls it "coarse $3^5$ grid".  
  *Evidence:* `docs/analysis-note/sec_5d.tex:185`, `sec_joint.tex:45`.  
  *Resolution:* Standardize terminology: "109 populated joint cells of the $3^5$ grid".

* **S1-ACC-16 [T]** — **Reconciliation of related counts.**  
  *Finding:* 4830 populated 4D bins (§7.8) vs 4825 (App. B.1); ndf 204 vs 205 in §5.3; 27 boxes / 12 steps / 16 cells in §10.1; truth $W$ 0.15% no real solution vs $4.9 \times 10^{-5}$ negative $W^2$ (§8.2).  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:145`, `sec_validation.tex:142`, `sec_fived16.tex:52`, `sec_eavailw.tex:48`.  
  *Resolution:* Define each count and filtering criterion precisely.

* **S1-ACC-17 [T]** — **Seed dependence vs training-seed block magnitude.**  
  *Finding:* Individual seed shift (median 0.18%, max 1.79%, RMS 1.28) is larger than the training-seed block median (0.048%).  
  *Evidence:* `docs/analysis-note/sec_method.tex:95`, `sec_systematics.tex:110`.  
  *Resolution:* Clarify that the training-seed covariance block estimates variance across retrainings, whereas individual single-seed realizations explore wider algorithmic scatter.

* **S1-ACC-18 [T]** — **Iteration stability justification.**  
  *Finding:* Total integral converges to 0.026% at $n=5$, but shape RMS differs by 1.54% (§5.4) and 5D iteration dependence is larger (§9.4).  
  *Evidence:* `docs/analysis-note/sec_method.tex:102`, `sec_validation.tex:178`, `sec_5d.tex:192`.  
  *Resolution:* Acknowledge shape iteration variance alongside total integral convergence.

* **S1-ACC-19 [T]** — **2p2h standard magnitude arithmetic in §7.7.**  
  *Finding:* Stating that closing deficit requires 2p2h at ~45% of QE, calling it standard Valencia MEC, conflicts with $f_{\text{MEC}} = 2.87\%$ of CC total and $\text{QE} = 11\%$.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:155`.  
  *Resolution:* Clarify post-flux phase-space definitions and show exact arithmetic.

### Section 4: Completeness as a Citable Record

* **S1-COM-1 [T]** — **Missing Per-Result Status & Citability Matrix.**  
  *Finding:* No result carries a validated interval; reader needs an explicit table defining what each product is citable for.  
  *Evidence:* All 4 referee reports.  
  *Resolution:* Add comprehensive Per-Result Status & Citability Matrix to Section 1.

* **S1-COM-2 [T]** — **5D config-(a) covariance citability.**  
  *Finding:* Explicitly state what may be cited from config-(a) 5D value and uncertainty (exploratory central comparisons only; covariance unusable).  
  *Evidence:* `docs/analysis-note/sec_5d.tex:225`.  
  *Resolution:* Clarify in status matrix and §8/§9.

* **S1-COM-3 [R]** — **Fake-data bias in physical units.**  
  *Finding:* Tabulate per-cell bias in % and relative to reported $\sigma$ for GiBUU hybrid and $q_3$ tilt in Table 18.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:225`, Table 18.  
  *Resolution:* Pull numerical values from `readout.json` / `f0b` receipts and add to Table 18.

* **S1-COM-4 [T]** — **$q_3$ truth in abstract vs omitted $q_3$ reweighting.**  
  *Finding:* Fig. 36 caption notes $q_3$ reweighting omitted because it did not implement intended change, while abstract cites synthetic $q_3$ tilt.  
  *Evidence:* `docs/analysis-note/main_note.tex:73`, Fig. 36 caption, `sec_fived16.tex:220`.  
  *Resolution:* Clarify distinction: the synthetic $q_3$ tilt in §10.5 is an implemented stress test; the omitted reweighting was a separate exploratory test.

* **S1-COM-5 [T]** — **Quantification of nonlinear cross-source terms.**  
  *Finding:* Executive summary names omitted nonlinear cross-terms as a methodological finding without quantification.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:19`, `sec_systematics.tex:180`, `sec_5d.tex:230`.  
  *Resolution:* State that effect was not measured in 2D; quote 5D trace ratio from `uq_5d` receipts.

* **S1-COM-6 [T]** — **Unexecuted or incomplete tests.**  
  *Finding:* Clarify status of tests that did not run (App. D response mismatch, §5.2 re-test, §10.5 16-cell coverage, §10.3 reco info).  
  *Evidence:* `docs/analysis-note/sec_validation.tex:160`, `app_response_mismatch.tex:4`.  
  *Resolution:* Explicitly document these protocols as unexecuted and state their implications.

* **S1-COM-7 [T]** — **Unresolved items in 2D covariance.**  
  *Finding:* Document bounds: only 7 of 187 universes reproduced by committed code, NormDISCC zero, POT counting inferred.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:195`.  
  *Resolution:* State these limitations transparently in §4.

* **S1-COM-8 [T/R]** — **Run-period block $C_{\text{PL}}$ characterization.**  
  *Finding:* $C_{\text{PL}}$ true-to-estimated $\sigma$ ratio interval is 0.73–2.56; quote total uncertainty with and without $C_{\text{PL}}$ (5.98% vs 6.41%).  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:165`, Table 8.  
  *Resolution:* Tabulate and quote 2D uncertainty with and without $C_{\text{PL}}$.

* **S1-COM-9 [T]** — **Background normalization & composition.**  
  *Finding:* Tabulate composition of ~3% purity correction vs 0.35% genuine background.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:42`, `sec_method.tex:75`.  
  *Resolution:* Tabulate genuine background (0.35%) vs out-of-phase-space signal (~2.65%).

* **S1-COM-10 [T]** — **Own-covariance $\chi^2$ vs publication.**  
  *Finding:* State $\chi^2/\text{ndf} = 22.29$ with own covariance against published result, alongside 2.27 with published covariance.  
  *Evidence:* `docs/analysis-note/sec_results.tex:125`, `app_statmethods.tex:520`.  
  *Resolution:* Report both $\chi^2$ values in §6 and discuss implications.

* **S1-COM-11 [T]** — **Correlation sensitivity of 16-cell generator $\chi^2$.**  
  *Finding:* Generator $\chi^2$ drops sharply when flux correlations are shrunk or removed.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:185`, Table 22.  
  *Resolution:* Discuss covariance regularization and correlation sensitivity in §10.

---

## Part 3: Sonnet Report 2 (`sonnet-note-r1-2.txt`)

* **S2-ACC-5 [T]** — **Detector-response-mismatch closure status.**  
  *Finding:* §5 says "not run", while App. D reports shifted response closures with $|\Delta|/\sigma$ up to 0.97.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:35`, `app_response_mismatch.tex:12`.  
  *Resolution:* Reconcile text: App. D ran exploratory shifted response samples; the full formal closure protocol was not executed.

* **S2-ACC-7 [T]** — **Band counts and classifications across sections.**  
  *Finding:* 44 vs 45 bands; lateral vs weight-based GEANT bands in App. A.2.4.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:35`, `app_statmethods.tex:210`.  
  *Resolution:* Harmonize: 44 evaluated systematic bands plus 1 global normalization; clarify GEANT FSI lateral treatment.

* **S2-ACC-9 [T/R]** — **Positive control window in §5.2.**  
  *Finding:* 0.955 lies inside [0.928, 0.972]; window endpoint recheck.  
  *Evidence:* `docs/analysis-note/sec_validation.tex:155`.  
  *Resolution:* Check exact window definitions and numbers against receipt; correct text description.

* **S2-ACC-10 [T]** — **Run-period effect on 2D median.**  
  *Finding:* 5.98% to 6.41% (+7%) vs median ratio of 5.8% in Table 3.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:165`, Table 3.  
  *Resolution:* Clarify ratio of medians (+7.2%) vs median of ratios (+5.8%).

* **S2-ACC-14 [T]** — **Flux units and integration bounds.**  
  *Finding:* Formula in §3.4 uses $\text{m}^2$, text uses $\Phi = 6.243 \times 10^{-8}\text{ cm}^{-2}$; per-$p_T$ flux integral vs 0–100 GeV integrated flux.  
  *Evidence:* `docs/analysis-note/sec_method.tex:125`.  
  *Resolution:* State exact unit conversion factor ($10^4\text{ cm}^2/\text{m}^2$) and specify flux integration bounds.

* **S2-ACC-15 [T]** — **Cross-checks description in §3.2.**  
  *Finding:* §3.2 mentions MLP/transformer cross-checks in §7.5, but §7.5 contains only Keras MLP, and App. F notes no transformer result is used.  
  *Evidence:* `docs/analysis-note/sec_method.tex:90`, `sec_3d.tex:130`.  
  *Resolution:* Remove mention of transformer from §3.2.

* **S2-ACC-16 [T]** — **"Differ in learner" description in §7.3.**  
  *Finding:* 3D marginal (e) and 2D result (f) are both LightGBM, differing in seed and refinement capacity, not learner family.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:115`.  
  *Resolution:* Change "differ in learner" to "differ in learner capacity and training seed".

* **S2-ACC-18 [T]** — **5D bin count definitions.**  
  *Finding:* "10,694 reported bins" undefined; distinguish dense grid (65,856), occupied cells (10,499), and 4D projections (4,830).  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:210`, `sec_5d.tex:150`.  
  *Resolution:* Provide explicit definitions for each bin count.

* **S2-ACC-20 [T]** — **GiBUU domain cutoffs.**  
  *Finding:* $p_\parallel < 4.5\text{ GeV/c}$ in 16-cell vs $< 6\text{ GeV/c}$ in joint tests.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:165`, `sec_joint.tex:55`.  
  *Resolution:* Explain rationale for domain restrictions (sample coverage limits).

* **S2-ACC-21 [T]** — **Extended fiducial bin counts and fractions.**  
  *Finding:* 185 vs 205 published cells; $\sigma_{\text{ext}}/\text{control} = 4.502/3.073 = 68\%$ vs 66.4% MC.  
  *Evidence:* `docs/analysis-note/sec_fps.tex:45-80`.  
  *Resolution:* Explain 185 fiducial sub-block vs 205 total cells; reconcile fractions.

* **S2-ACC-22 [T]** — **App. C.5 vs Table 8 ensemble variance.**  
  *Finding:* Negative-weight rebuild has $\sqrt{\text{Tr} C} = 2.98 \times 10^{-39}$ vs Table 8 $2.69 \times 10^{-39}$.  
  *Evidence:* `docs/analysis-note/app_negweight.tex:85`, Table 8.  
  *Resolution:* Specify which ensemble configuration corresponds to each table.

* **S2-COM-3 [T]** — **Algorithmic and configuration dependence table.**  
  *Finding:* Consolidate algorithmic variations (exact-split vs LightGBM, seed shifts, MLP vs GBDT) into a unified summary table.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:115`.  
  *Resolution:* Create consolidated algorithmic variation table in §4 / §7.

* **S2-COM-4 [T]** — **Joint test condition (i) disclosure.**  
  *Finding:* Condition (i) fine-grid convergence unmeasured; disclose sub-grid residual limits.  
  *Evidence:* `docs/analysis-note/sec_joint.tex:120`.  
  *Resolution:* State condition (i) bounds explicitly in §11.

* **S2-COM-6 [T]** — **Offset control check failure disclosure.**  
  *Finding:* Offset check gives $\chi^2 = 245.74$ for 16 ndf; disclose failure and implications.  
  *Evidence:* `docs/analysis-note/sec_fived16.tex:240`.  
  *Resolution:* Document offset check failure clearly in §10.

* **S2-COM-12 [T]** — **Removal of unfulfilled placeholders.**  
  *Finding:* Remove literal placeholders like "[snapshot identifier pending deposit]" and state repository status objectively.  
  *Evidence:* `docs/analysis-note/app_release.tex:25`.  
  *Resolution:* Replace placeholders with objective statements of git repository references.

---

## Part 4: Gemini Report 1 (`gemini-note-r1-1.txt`)

* **G1-ACC-1 [T]** — **Target nucleon count discrepancy.**  
  *Finding:* §2.3 and §3.4 use $3.2353 \times 10^{30}$, but §3.4 p. 4 uses $3.235 \times 10^{30}$.  
  *Evidence:* `docs/analysis-note/sec_experiment.tex:32`, `sec_method.tex:122`, `:135`.  
  *Resolution:* Fix typo $3.235 \to 3.2353 \times 10^{30}$ in §3.4.

* **G1-ACC-6 [D]** — **Neutral pion mass subtraction in Eq. (1).**  
  *Finding:* Referee calls subtracting 135 MeV for charged pions in Eq. (1) an "unphysical error and acknowledged bug".  
  *Evidence:* `DECISION-20261101-joseph-eavail-keep-135.md:30-38`.  
  *Resolution:* **DISPUTE.** Joseph explicitly ruled in `DECISION-20261101-joseph-eavail-keep-135.md` to retain the 135 MeV constant to preserve exact, bitwise consistency with the MAT production definition. The text already transparently documents that this is an inherited MAT convention moving 0.65% weight. Clarify text to emphasize that this is a deliberate inherited convention, not an uncorrected typo.

* **G1-ACC-7 [T]** — **Massless-lepton approximation in Table 10.**  
  *Finding:* Table 10 lists $Q^2 = 4 E_\nu E_\mu \sin^2(\theta/2)$, which is ultra-relativistic approximation ($m_\mu = 0$).  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:55`, Table 10.  
  *Resolution:* Add exact muon-mass formula or note that Table 10 describes the nominal generator truth coordinate definition.

* **G1-ACC-8 [T]** — **Exact-split estimator reproducibility description.**  
  *Finding:* Reconcile "unseeded reproducible to $7 \times 10^{-15}$" with "reseeding moves bins by up to 1.6%".  
  *Evidence:* `docs/analysis-note/sec_method.tex:98`.  
  *Resolution:* Clarify that bitwise reproduction was achieved under the unseeded default runtime, but reseeding demonstrates 1.6% algorithmic sensitivity.

* **G1-ACC-9 [T]** — **GiBUU cell count reconciliation.**  
  *Finding:* 8 cells in §10 vs 72 cells in Table 11.  
  *Evidence:* `docs/analysis-note/sec_execsummary.tex:18`, Table 11.  
  *Resolution:* Clarify in text: GiBUU covers 8 of the 16 reporting cells in §10, and 72 of the 109 joint cells in §11.

* **G1-COM-6 [T]** — **Playlist pooling bias disclosure.**  
  *Finding:* Global exposure ratio induces $-1.83\%$ to $+3.78\%$ single-cell pooling bias.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:202`.  
  *Resolution:* Disclose pooling bias in systematics discussion.

* **G1-COM-8 [T]** — **NormDISCC systematic category.**  
  *Finding:* NormDISCC carried as zero without confirmation.  
  *Evidence:* `docs/analysis-note/sec_systematics.tex:198`.  
  *Resolution:* State transparently that NormDISCC is supplied as zero in MAT inputs and carried as zero.

* **G1-PRES-1 [T]** — **Editorial tone and register.**  
  *Finding:* Avoid internal software tracker phrases ("until 2026-10-11", "run log not found", "inferred, not verified").  
  *Evidence:* `docs/analysis-note/sec_method.tex:95`, `sec_systematics.tex:195`.  
  *Resolution:* Refactor text into formal, objective archival register while preserving full scientific disclosures.

* **G1-PRES-2 [T]** — **Figure error bar conventions.**  
  *Finding:* Error bars on Figs. 7, 9, 10 plot MC weight statistics ($\sqrt{\sum w^2}$), which can be mistaken for experimental precision.  
  *Evidence:* Captions to Figs. 7, 9, 10.  
  *Resolution:* Explicitly explain in captions that vertical bars represent MC weight statistics, not experimental uncertainties.

* **G1-PRES-3 [T]** — **Kinematic notation standardization.**  
  *Finding:* Longitudinal momentum denoted interchangeably as $p_\parallel$, $p_z$, `p_||`.  
  *Evidence:* Figures 5, 17, 18, text.  
  *Resolution:* Standardize to $p_\parallel$ across all LaTeX sources.

* **G1-PRES-4 [T]** — **Average nucleon mass definition $\bar{M}$.**  
  *Finding:* Origin of 1.5:1 ratio in $\bar{M} = (1.5 M_n + M_p)/2.5$ for CH tracker.  
  *Evidence:* `docs/analysis-note/sec_eavailw.tex:52`.  
  *Resolution:* State the isotopic/target weighting convention used by the MAT framework.

---

## Part 5: Gemini Report 2 (`gemini-note-r1-2.txt`)

* **G2-ACC-4 [T]** — **Ascencio et al. comparison clarification.**  
  *Finding:* Data sit 9.2% and 6.0% above Ascencio on super-cells, confounded by differing $E_{\text{avail}}$ definitions.  
  *Evidence:* `docs/analysis-note/sec_3d.tex:185`.  
  *Resolution:* Detail definition differences ($11\%$ event shift) and present comparison descriptively.

* **G2-PRES-4 [T]** — **Mislabeled comparator in Figure 23.**  
  *Finding:* Axis/color labels say `data/GENIE`, but text states comparator is MINERvA Tune v1.  
  *Evidence:* Fig. 23 labels and caption.  
  *Resolution:* Update label annotation to `data / Tune v1`.

* **G2-VOID-1..5 [D]** — **Completeness findings on §§9.5–13 and Appendices A–H.**  
  *Finding:* Gemini 2 claimed §§9.5–13 and Appendices are missing.  
  *Evidence:* Input cut at 31,717 words on reader's side; rater copy contains full 69,536 words.  
  *Resolution:* **VOID per director's instructions.**

---

## Part 6: Cross-Cutting Structural Synthesis

All four referee reports converge on three macro-architectural requirements:
1. **Front-Matter Per-Result Status & Citability Matrix:** Section 1 must establish a clear, unequivocal table declaring exactly what each result is citable for.
2. **Transition from Measurement to Methods Record:** Reframing the entire manuscript to lead with the 16-cell multidimensional benchmark and the 2D reproduction benchmark, treating coverage breakdown, rounding instability, and algorithmic differences as primary methodological deliverables.
3. **Harmonization of Estimators:** Disentangling the six configurations ((a) through (f)) into a clear chronological development and standardizing the primary benchmark results on adopted configurations ((f) for 2D, (e) for 16-cell).

---

## Ledger Action Item Index

| ID | Class | Short Title | Governing File & Line | Owner |
|---|:---:|---|---|:---:|
| AUD-N1 | **T** | Note Reframing to Methods Record | `main_note.tex:73`, `DECISION-20261108` | Antigravity |
| AUD-N2 | **T** | REF-G1 Algorithmic Dependence Stated Limitation | `sec_fived16.tex:260`, `OUTCOME-20261106-ref-g1` | Antigravity |
| S1-COM-1 | **T** | Per-Result Status & Citability Matrix | `sec_execsummary.tex`, Section 1 | Antigravity |
| S1-ACC-1 | **T** | Reconcile Tune v1 QE-Δ Dip Statements | `sec_execsummary.tex:13`, `sec_3d.tex:140` | Grok / Antigravity |
| S1-ACC-2 | **T/R** | Reconcile Tune v1 Deficit Figures | `sec_results.tex:85`, `values.tex` | Grok / Antigravity |
| S1-ACC-4 | **T** | Disentangle 5D Coverage Tests | `main_note.tex:73`, `sec_5d.tex:216`, `sec_fived16.tex:253` | Antigravity |
| S1-ACC-6 | **T** | Qualify Config-(a) Unusable Covariance | `sec_5d.tex:225`, `app_release.tex:72` | Grok / Antigravity |
| S1-ACC-8 | **T** | Fix Band Count Typo (Five -> Four) | `sec_fived16.tex:112` | Grok / Antigravity |
| S1-ACC-9 | **T** | Fix Fifteen-Fold Arithmetic (-> 14.6) | `sec_method.tex:92` | Grok / Antigravity |
| S1-COM-3 | **R** | Fake-Data Bias Physical Units in Table 18 | `sec_fived16.tex:225`, `readout.json` | Grok / Antigravity |
| S1-COM-8 | **T/R** | Quote 2D Uncertainty With & Without C_PL | `sec_systematics.tex:165`, Table 8 | Grok / Antigravity |
| S1-COM-10 | **T** | Report Own-Covariance χ² = 22.29 | `sec_results.tex:125` | Grok / Antigravity |
| G1-ACC-1 | **T** | Fix Target Nucleon Count Typo | `sec_method.tex:135` | Grok / Antigravity |
| G1-ACC-6 | **D** | Dispute Eq. 1 135 MeV Mass Error Claim | `DECISION-20261101-joseph-eavail-keep-135.md` | Antigravity |
| G1-PRES-1 | **T** | Elevate Editorial Tone and Register | Global LaTeX sources | Grok / Antigravity |
| G1-PRES-3 | **T** | Standardize Kinematic Notation ($p_\parallel$) | Global LaTeX sources | Grok / Antigravity |
| G2-VOID | **D** | Void Gemini 2 Missing Text Completeness | Truncation receipt at 31.7k words | Antigravity |
