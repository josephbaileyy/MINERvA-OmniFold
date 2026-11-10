# The short methods paper: claim ledger and wording choices (2026-11-09)

**Recorded by** `director-helper-3`. The ledger covers the paper (`paper_body.tex`, and the abstract in
`main_paper.tex`) at the round's commit. It has one row per claim the round adds or changes. A paragraph kept from
round 5 (`bc8673186`) is marked "r5:N" in a comment at its head. Its claims keep their round-5 sources, which are
that line's source comments at `bc8673186:docs/analysis-note/paper_body.tex`, and they are not repeated here.

**The commits:**
- paths under `state/` are relative to `docs/orchestration/`, and are read at main `c120e0d07` as merged into this
  branch at `e9b8ea160`;
- `DECISION-20261109-joseph-methods-baseline-and-plan.md` is read at #976's head, `943d5f97`, since #976 is not yet
  merged;
- "the consult" is `state/2d-closeout/stageF/methods/secondary-results/consult-astra-publishable-path-20261109/answer.txt`.

**The licence of every row:** no row is approved wording. Every printed sentence is a draft for the round-6 blind
reads (`DECISION-20261109-joseph-placeholder-draft-reads.md`, #978), for the PRD-referee read of the W-rows, and for
Joseph.

## Claims

| id | where | claim (short) | record, file:line @ sha | licence kept |
|---|---|---|---|---|
| L-01 | §1 | benchmark finding: agreement in normalization, a correlated shape difference, source not identified | r5:151 and r5:18 (their sources); `../analysis-note/sec_results.tex:30` @ `c120e0d07` | descriptive; no calibrated significance |
| L-02 | §1 | prior-retention finding | r5:272 and Table 2 (F0b, `make_values_fived16.py` LISTED_CLAIMS); r5:319 | "retains part of its prior" as round 5 |
| L-03 | §1 | "reproducibility, stability and calibration are distinct; the estimator has the first, fails the second, the third not established" | r5:230 (bitwise; fails the requirement); `OUTCOME-20261108-cov2d-both-tunes-under-cover.md:97-106` @ `c120e0d07`; r5:283 (1B stopped) | "not established" rather than "fails": the 5D coverage test never ran to a result (`OUTCOME-20261108-1b-precheck-part1.md`, r5:284's comment) |
| L-04 | §1 | the roadmap | — | — |
| L-05 | Table 1 | rows kept from r5:27-51 | r5's rows | the rows that moved are listed in OUTLINE.md's revision |
| L-06 | §3.1 | "the joint-test estimator is the baseline this study characterizes (configuration (e)): the stability probe and the ensemble average were tested against it, and neither replaced it" | decision item 1, `:44-48` @ `943d5f97`; `OUTCOME-20261105-fd-stab-none-pass.md:20,40`; `OUTCOME-20261109-ens1-stab-pass-bias-worse.md:61` ("the reported estimator, configuration (e), is unchanged") @ `c120e0d07` | the baseline choice is Joseph's decision; no claim that it is better |
| L-07 | §3.2 | the reported covariance, cut | r5:118 | `C_model` "not a calibrated bound" kept |
| L-08 | §3.3 | 12 graded truths, 6 descriptive; the 2 held-out tunes | r5:247, r5:281; `values_fived16.tex` `f0b-all-truths`, `f0b-nungraded` | "not held out" kept |
| L-09 | §3.3 | the ensemble comparison uses noise-free closures at the 17 distinct truths, since the Tune v1 hybrid equals the prior | `state/measurement-paper/5d-community-20261024/FD-STAB-DECLARATION.md:105-122` (the 18 F0b truths, noise-free), `fd/rounding-stability-20261106/ensemble/ENS1-DECLARATION.md:122` (17 distinct); `ens1_stage2.json` (`c2ee701d`): A7_mnvtune k = 1 equals nominal k = 1 bitwise | — |
| L-10 | §3.3 | "Every criterion was fixed before the results it grades were seen", with the flagging rule, the stability requirement and the coverage grading | r5:247 ("fixed before any of the tests was graded"); r5:230 (the requirement "fixed in advance", r5's abstract); `FD-STAB-DECLARATION.md` §5; COV2D and LL5D §6 (`LL5D-DECLARATION.md:444-483`) | the coverage grading is described generically, as a threshold from the test's own null |
| L-11 | §3.3 | which estimator each finding concerns, and that the rounding sensitivity is carried in the statistical uncertainty | r5:93; the B0 sentences in r5:230 | the editor's A2 |
| L-12 | §4.1 | **new sentence:** "The two results share the data and the flux, detector and generator systematics, and their cross-covariance is not available, so no difference between them can be given a calibrated significance." | the note's `docs/analysis-note/sec_results.tex:30` @ `c120e0d07` ("The published and unbinned results share the data and the flux, detector and generator systematics, and their cross-covariance is not available"); `app_statmethods.tex:355` ("Missing cross-covariance prevents calibration") | descriptive |
| L-12b | §4.1, Table 1 | χ² = 136 (χ²/205 = 0.66) on 73 directions; χ² = 285 (χ²/205 = 1.39) on 139; ndf = 205 with no fitted parameter | `sec_results.tex:128-129` (136, and its arithmetic); `state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/receipts/figs/tension_report.txt:55-56` ("1e-06 1.391 139"; "1e-04 0.662 73"). 285: 1.391 × 205 = 285.2, and 1.391 rounds a value in [1.3905, 1.3915), so χ² ∈ [285.05, 285.26] | the director's ruling of 2026-11-09 on the divisor |
| L-13 | §5.3 | the prior-retention study's design: ρ, one factor at a time, IBU on the same pseudo-data, noise-free, one split | `FD-PRR-DECLARATION.md:21-28` (MEASURES), `:165-172` (§3.3), `:236-252` (§4.1) @ `c120e0d07` | — |
| L-14 | §5.3 | "The study selects no estimator, and its readings are descriptive of these truths, not held-out results" | `FD-PRR-DECLARATION.md:40-56` (NOT CITABLE FOR), §6 `:346-360` | the director's rulings 1 and 2 |
| L-15 | §5.3 | the variants | variants.md V-P1 to V-P7 | as there |
| L-16 | §5.4 | V-ATLAS and V-PRIOR in one sentence: 14 of 16 each, 12 under both | r5:274 and its comment r5:275 (`OUTCOME-20261107-valid-region.md`, readout `91bb604e`) | "neither validates an interval" now stands as the V-HALF sentence's "not a coverage statement", which covers all three rules ("Like the others") |
| L-17 | §5.4 | V-HALF's definition: the 1 % floor, "not assessed", "unresolved", and that it is not a statement about detector adequacy or coverage | `DECISION-20261109-joseph-bias-half-rule.md:31-35` (item 1), `:38-40` (item 3), `:49` (NOT CITABLE FOR) @ `c120e0d07`; decision item 6, `:73-78` @ `943d5f97` | V-HALF's declaration is not yet committed. **When it lands, re-read this sentence against it.** |
| L-18 | §6.1 | the ensemble sentence reworded, plus "a tested mitigation of the instability, not a replacement … the variant that meets the stability requirement is worse in bias at one of the truths tested" | `OUTCOME-20261109-ens1-stab-pass-bias-worse.md:53-61` (CITABLE FOR), `:63-71` (NOT CITABLE FOR: "a stabilised variant", "the instability fixed") @ `c120e0d07`; decision item 1, `:44-48` @ `943d5f97` ("E₉₆ is reported as a tested mitigation") | "meets the stability requirement" and "is worse in bias", not "stabilised" or "restores stability" |
| L-19 | §6.3 | the like-for-like test's design: groups built like-for-like, the covariance rebuilt per tune, two readings with the primary one without the GEANT4 neutron and proton bands | `LL5D-DECLARATION.md:76-94` @ `c120e0d07` | the readings are correlated, and neither tests the other (`:93-94`) |
| L-20 | §6.3 | its limits: rebuilt per truth, not per toy; response and run-period terms not drawn; laterals carried by a surrogate; no coverage rate; nothing about the data intervals or the ensemble average | `LL5D-DECLARATION.md:88` (no coverage rate), `:274-280` (§3.8, laterals carried), `:282-324` (§4, rebuilt at each truth; C_resp and C_PL,5D not drawn, `:318`); the consult `:39-43` | — |
| L-21 | §7 | the first paragraph, rewritten around the three findings | L-01 to L-03; r5:316 | — |
| L-22 | §7 | "The benchmark establishes normalization agreement and a qualified shape comparison in two dimensions, not the validity of the five-observable distribution." | decision item 6, `:73-78` @ `943d5f97`; the consult `:15` | not claimed: "5D validates the full distribution" |
| L-23 | §7 | "The validity rules grade the estimator's bias under simulated truths; they do not identify where the detector model is inadequate." | decision item 6; the consult `:16`, `:19`; the bias-half decision `:49` | not claimed: "V-HALF identifies detector inadequacy" |
| L-24 | §7 | localization: "not established"; what such a test would need; "the natural next step" | decision item 6 ("until then it is a stated next step"); the consult `:17`; `OUTCOME-20261107-valid-region.md` (it "licenses no localization conclusion in either direction", the consult's `:17` cites `:23,36,98-124`) | not claimed: localization. **W-5** |
| L-25 | §4.2 | "The five-observable result therefore agrees with the two-dimensional normalization in each muon-kinematic quadrant; the benchmark does not test its distribution in the three hadronic observables." | r5:208 (the quadrant sums); decision item 6 | "agrees with", not "inherits" |
| L-26 | abstract | the abstract, rewritten; LISTED_CLAIMS's anchor "at a GiBUU-like truth and at a synthetic momentum-transfer tilt find" kept | r5's abstract; L-18; COV2D CITABLE FOR (`:97-106`); variants V-A1 and V-A2 | **W-2, W-6** |

| L-27 | §5.3 | the prior-retention bar, printed: "the larger of 0.05 and 9.03 times the standard deviation of the paired change of ρ over five splits of the simulation"; ρ, b_c and d_c as symbols | `FD-PRR-DECLARATION.md:281-286` (§5.1, δ_F = max(0.05, 9.03 s_F)), `:217-224` (§3.5, s over five splits), `:236-246` (§4.1) @ `c120e0d07` | round 6, the editor's C2 and B3 |
| L-27b | §5.3, §6.1, §6.2 | after the editor's second read: the composite labels, "clears" and the 9.03's origin defined in the design paragraph; the 0.8 median named as over the 153 quantities; the 204 degrees of freedom explained; the reconstruction-level reference 1A–1E (without 1F) stated | `FD-PRR-DECLARATION.md:282-284`, `:307-310`, `:321-332`; the note's `sec_5d.tex:91` ("move functionals by a median of 0.8"); `state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/readout/AR23/README.md:38-41` (the ndf is the rank above 10⁻¹²); `state/2d-closeout/period-unfold-20261014/REPORT.md:113` | presentation; no claim changes |
| L-28 | §5.4, Table 1 | the IBU bars as "the 95th and 99.7th percentiles of its null, 28.12 and 39.04" | r5:176 ("28.12 (0.95) and 39.04 (0.997)") | the editor's B8 |
| L-29 | §1 | **W-22 draft:** the motivation for the joint unbinned approach, with "this study does not test whether that gain is realized" | the intro (r5:13); S4 `sec:method-algo` ("any binning chosen afterwards") | motivation only; see W-OPTIONS.md |
| L-30 | §5.1, Fig. 3 | panel (a)'s estimator named, with why: the configuration with which the generator-sized-change study ran; the reported estimator's result at the same truth, the sixteen cells: largest \|z\| 1.76, flagged without C_PL,5D | S4 (configurations (c) and (d) "serve the … generator-sized-change … studies"); Table 2's GiBUU E_avail shape row (`f0b-stage0c_gibuu-*`); r5:272 | the director's round-6 item 3. The note gives no reported-estimator (E_avail, W) residual at this change (`sec_5d.tex:57-63`), so none is printed |
| L-31 | §2, §5.2, §7 | "diagonal fraction" in place of "reconstruction stability", defined in §2; the three run-period groups defined in §2; the publication reports 205 of the 224 bins | `h2_definition.json` via `h2-lowstab-*` (r5:339); S5 (`sec:fived16-pl`, "playlists 1A–1F, 1G–1M and 1N–1P"); S3 (the note's `sec:205bins`) | the editor's B2 and B6 |

**Numerals new to the base** (`check_round.py` NEW_NUMERALS): 136 and 285 (row L-12b), 0.05, 9.03 and 0.01 (L-27), and 99.7 (L-28). Every other numeral
the paper prints is printed by `bc8673186` too.

**Moved text.** Every paragraph moved to the Supplement carries a comment naming its round-5 line, and it keeps that
line's evidence route. The full list is in OUTLINE.md's revision note.

**One check changed:** `check_sec4_receipts.py` now finds the statistical-block median (0.676 %) in
`supplemental_body.tex`, where it moved (S6).

## Wording choices (W-rows)

**Round 6 (2026-11-09):** W-1 to W-8, W-11 to W-18, W-20, W-22 and W-23 are the director's, under Joseph's away delegation. Their options are in W-OPTIONS.md. Each will be logged here as decided, with its independent read. W-9, W-10, W-19 and W-21 are banked for Joseph.

**The original rows:**

| id | choice | the draft | alternatives |
|---|---|---|---|
| W-1 | the title | round 5's, unchanged | a three-findings title |
| W-2 | the abstract's three-finding sentences | as drafted; one LL5D clause in total (the editor's C2) | per-tune clauses; or no pending clause in the abstract |
| W-3 | V-HALF beside V-ATLAS and V-PRIOR, or in place of them | beside: the one-sentence summary of both is kept in either branch (the editor's A5) | V-HALF alone, with V-ATLAS and V-PRIOR in S11 |
| W-4 | whether the paper names the ensemble's bias–variance study as future work | not named (decision item 4 allows the study, and says nothing about the paper) | one sentence in §7 |
| W-5 | the localization next-step sentence, and whether a separate list of what is not claimed is printed | prose next to the results, plus §7's paragraph (the editor's A6) | a printed list |
| W-6 | "illustration only" for the 16-cell output, in the abstract | kept (the director, 2026-11-09) | dropped from the abstract |
| W-7 | the per-learner χ² values in §4.1 | kept in one clause (the editor's B2: without them the selection effect cannot be sized) | moved to S4 |
| W-8 | descriptive register in approved sentences | the B0 sentences and RS1's licensed clauses are kept verbatim; elsewhere "declared" became "specified in advance" | the same change inside the approved sentences, which would need Joseph |
| W-9 | the article type and the analysis-note citation (the editor's C4 and C6) | not changed | for Joseph: regular paper or technical report; a resolvable identifier for ref. [14] |
| W-10 | authorship and the data-use statement (the editor's C8) | the title says "of MINERvA open data"; the acknowledgments are unchanged | for Joseph, per the release's terms |

## Decided, batch 1 (the director, 2026-11-09, under Joseph's away delegation)

**Every decision in this batch is reversible by Joseph on his return.**

- **The read they rest on:** "IR-sol", an independent read by a fresh gpt-6-sol session, read-only at `f51d22c8b`
  with the round-6 reports. Its answer is
  `state/2d-closeout/stageF/methods/secondary-results/independent-read-w-items-20261109/answer.txt` (#988 at `e146861b`),
  verbatim, and each row cites its lines.
- **What the director checked:** IR-sol's W-12 sources (`sec_5d.tex:196-204`, `sec_joint.tex:165`) and its W-14 count
  (`valid-region-20261107/source/SM_section2_lines25-75.txt:34`, item 1 the jet threshold).
- **Where it applies:** in `paper_body.tex`, `main_paper.tex`, `main_supplement.tex` and `supplemental_body.tex`, at
  this batch's commit.

| W | decision | what prints now | read and records |
|---|---|---|---|
| W-1 | IR-sol "other"; **Joseph, 11-09: provisional, not locked** (below) | title: "Five-observable unbinned unfolding of MINERvA open data with OmniFold: a benchmark and diagnostic study"; §1: "a benchmark and diagnostic study"; the Supplement's title to match | IR-sol `:7-10`; decision `943d5f97:…:49-51` |
| W-2 | option 1's cuts plus option 2's clause | the abstract drops "over many eigenmodes …" and the criteria in parentheses, and adds "and by a median of 0.133 % of the cross section on the 16 reported cells" | IR-sol `:12-15`. **0.133 %'s source:** `state/measurement-paper/5d-community-20261024/FD-1B-INV-I0-REPORT.md:66-67` ("σ_J/f on the data has median 0.133 %, range 0.055–0.252 %"), the source r5:238 records for §6.1's same number |
| W-3 | 1 | §5.4: "All three rules classify the bias under simulated truths: none is a coverage statement, none assesses the detector model, and none excludes a cell from the output."; S11: "neither excludes a cell from the output" | IR-sol `:17-20`; `OUTCOME-20261107-valid-region.md:21-36`; `DECISION-20261109-joseph-bias-half-rule.md:28-40` |
| W-4 | superseded by Joseph, 11-09: option 1 (below) | the option-1 sentence in §6.1 (below) | IR-sol `:22-25`; decision `943d5f97:…:59-64` |
| W-5 | 1, with "a next step" | "That test is a next step." | IR-sol `:27-30` |
| W-6 | 1 | unchanged | IR-sol `:32-35` |
| W-7 | 1 | unchanged | IR-sol `:37-40` |
| W-8 | 1 | unchanged | IR-sol `:42-45` |
| W-11 | IR-sol's wording, with the paper's term for COV2D's object | "The procedure's two-dimensional covariance, rebuilt at each of two held-out generator tunes, under-covers at both; coverage of the reported five-observable intervals is not established." The pending like-for-like sentence stays separate | IR-sol `:47-50`; COV2D `:97-106`, `:108-115`. **The term:** the paper's "the two-dimensional covariance" (§3.2) is the reported 2D covariance, while COV2D graded the procedure's covariance remade at each tune, which §6.2 calls "the procedure's two-dimensional covariance". This sentence supersedes the per-outcome W-11 entry and the editor's wording, and holds under every like-for-like outcome |
| W-12 | the director's wording | §7: "The second is on the data. When the simulation's prior is changed, the data result shifts in correlation with minus the noise-free residual at the same truth (ref. [14], section 9.4); these shifts are sensitivities, not a measured bias on data." The 11.5 sentence is in S7: "The null distributions of the note's calibrated joint tests reproduce the estimator's pull toward its prior" | IR-sol `:52-55`; `sec_5d.tex:196-204`; `sec_joint.tex:165-168` |
| W-13 | 1 | §7 ¶1 ends the list "within the reported uncertainty", then: "and the data show a run-period inconsistency, present before unfolding, of unknown cause" | IR-sol `:57-60`; `period-unfold-20261014/REPORT.md:63-67` |
| W-14 | 2 | "one based on the usage recommendations of ref. [5]"; no count of recommendations; S11 keeps the unmet correlation condition | IR-sol `:62-65`; `valid-region-20261107/source/SM_section2_lines25-75.txt:10-45` (five numbered items; item 5 unmet) |
| W-15 | 1 | §5.1 keeps "it is 16–31 % in the most affected (E_avail, W) cell", with the estimator named, and drops the comparison sentence. Fig. 3(b)'s band is removed in its producer (below) | IR-sol `:67-70`; `sec_5d.tex:247-253` (the covariance fails its specification) |
| W-16 | 1, without option 2's causal clause | abstract: "bitwise independent of its training seed in the unfolds we ran" | IR-sol `:72-75` |
| W-17 | 1 | the three-dimensions sentence follows the IBU sentence in §1's context paragraph | IR-sol `:77-80` |
| W-18 | 1 and 1 | Limitation 3 moves to S7. "the five-observable estimator" replaces "the joint-test estimator" in the printed paper, the Supplement and Fig. 3's panel title. §3.1's sentence reads "…; the note's calibrated joint tests of generator predictions use it too". Round 5's "an earlier five-observable estimator" (a different estimator) becomes "an earlier estimator of the five observables" | IR-sol `:82-85`. **Registry:** a new ALIASES row for "five-observable estimator" (`paper_body.tex:68`, digest `47a08982ce2219c5`); row 38 re-cited to the note's own definition (`sec_method.tex:100`, `ab43c270c1c00b9b`); row 47 and ATTRIBUTION row 17 re-cited to `:68`. check_registry: 67 aliases, PASS |
| W-20 | IR-sol's wording | §3.3: "The grading rules and their timing are stated with the individual tests; comparisons without a grading rule are descriptive."; "Pass" loses its global "fixed in advance". **Kept** "specified/fixed in advance" only for the FD triggers, FD-STAB, ENS1, COV2D, LL5D, REF-C2C1, REF-G1, the per-period benchmark and the FD-1B gate and its staged rules. **Removed** for the prior-retention study (three phrases) and RS1's mechanism study; none attaches to V-ATLAS, V-PRIOR or V-HALF. The two after-the-fact disclosures are kept (§4.1 background adoption; §3.2 "added after these differences were seen"), and the first coverage test's gate is one sentence pointing to S9 | IR-sol `:87-90` and its source list |
| W-22 | IR-sol's wording (it supersedes option 0) | §1: "Event weights let the same unfolded sample be histogrammed in projections or cells chosen afterwards. An uncertainty for a new choice must be constructed and checked for that choice; this study does not establish a practical gain over binned unfolding." | IR-sol `:92-95` |
| W-23 | 1, with the new name | §3.2: "…lateral and normalization uncertainties of the five-observable estimator, whose sum is $C_{\mathrm{e}}$, and $C_{\mathrm{model}}$" | IR-sol `:97-100`; S5 |
| W-24 | the neutral form. **IR-sol did not see it; the director takes it on the record alone** | §4.1: "The published covariance has a condition number of 1.5×10¹², and 73 of its 205 eigenvalues exceed 10⁻⁴ of the largest."; Table 1: "against a covariance of condition number 1.5×10¹²" | the note's `sec_results.tex:128`; re2 `tension_report.txt:55-56`; r5:151 |
| reader item 1 | **this reverses the director's divisor ruling of 2026-11-09**, on IR-sol's advice: dividing by 205 after keeping only 73 or 139 modes obscures the per-direction scale, and the per-period declaration already uses the per-direction convention | §4.1: "Keeping the 73 directions with λ/λmax > 10⁻⁴ gives χ² = 136, and the 139 with λ/λmax > 10⁻⁶ give χ² = 285." Both χ²/205 ratios and the divisor clause are gone, and no per-direction ratio is printed. The full χ²/ndf with ndf = 205 is unchanged | IR-sol `:104`; `per-period-benchmark-20261106/DECLARATION.md:143-148` |
| reader items 2–4 | no change; item 2's answer is in REPORT.md | — | IR-sol `:106-110` |

**Retired with W-15:** `check_sec4_receipts.py`'s VERBAL row "about half of those cells (VL154: 20 of 42)", retired
because the sentence no longer prints. Its self-test loops over VERBAL, now empty. VL154's count stays in the figure
producer's numbers file as a record.

**Fig. 3's producer is `figures/methods_m3/fig_m3_deformation.py`.** Before the change, it reproduced the committed
`paper_fig_deformation.pdf` byte for byte (sha256 `92544d1f…`), which settles the figure-diagnosis report's "no producer
found" for this figure. The band and its legend entry are removed there, and panel (b)'s title names the
five-observable estimator. The PDF is regenerated, not edited (new sha256 `53598045…`).

**Two test cases fixed:** `test_check_sec4_receipts.py` had two stale cases from earlier commits of this branch. The
0.676 % now prints in the Supplement, and "16–31 %" prints twice. 17 of 17 pass.

**After batch 1 (the director, 2026-11-09, verified at `2c0f6c5d1`):**
- **W-11, an applied adaptation of the decision, accepted by the director.** The decision's "the two-dimensional
  covariance" prints as "the procedure's two-dimensional covariance, rebuilt at each of two held-out generator tunes".
  That is §6.2's term for COV2D's remade covariance, and it is closer to COV2D's CITABLE FOR (`:97-106`) than "the
  two-dimensional covariance", which §3.2 uses for the reported 2D covariance.
- **W-20, two restorations under the director's rule** (restore only where the declaration shows a date before the
  run):
  - **The prior-retention study.** "A study specified in advance", "a bar fixed in advance" and "labels fixed in
    advance" are restored. The record: `state/measurement-paper/5d-community-20261024/FD-PRR-DECLARATION.md:1` (rev 2,
    2026-11-08, "for coverage-5b-audit; nothing runs") and `FD-PRR-BINDING-1.md:1` (bound 2026-11-08). The study has
    not reported, so its declaration precedes any run.
  - **The mechanism study.** "A study of the mechanism specified in advance" is restored. The record:
    `state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/RS1-DECLARATION.md:1-4` (2026-11-06,
    "Nothing has run, and nothing runs before the binding"; committed in `e5f700b2c`, 2026-11-06T18:17-08:00). Its
    outcome, `OUTCOME-20261108-rs1-rounding-mechanism.md`, was added in `9f0bf8ea6`, 2026-11-07T19:25-08:00.
- **Reader item 2, applied as approved.** Table 2 gains a middle column group, C_total + C_resp (without C_PL,5D): χ²,
  p and cells per truth.
  - **Source:** only the pinned `-nopl` keys of `make_values_fived16.py` (`fd_f0b_readout.json` `b9db935a` in
    `NOPL_READOUTS`). No new number is computed.
  - **Caption:** "The reported covariance … is primary; the readings without the run-period block … and under C_total
    alone are shown for sensitivity."
  - **Fit:** the table fits at `\footnotesize`, with no `\resizebox`. The truth and covariance columns wrap, which
    needs `\usepackage{array}` in `main_paper.tex`. The build shows no overfull box, and the page was checked by eye.
  - **§5.2** now reads "(the middle columns of table 2)", in place of "which table 2 does not show".
  - **A new figure in print:** without the block, the GiBUU hybrid truth also flags R07. It is the committed readout's
    own value.
- **check_round now runs `test_check_sec4_receipts.py`** (check 6), so stale cases fail loudly.

## Decided by Joseph (2026-11-09)

**Record:** `DECISION-20261109-joseph-bv-mention-title-preread.md` (#993), items 1–3, from Joseph's answer quoted there verbatim ("for none of these things should the
wording be locked"). **Both wordings are Joseph, 11-09: provisional, not locked.** Neither is protected text, and
neither is added to any protected-text list or check (item 3). Either may change through the PRD-referee read, a ledger
entry and the director's decision, or Joseph's.

| W | decision | what prints now | status |
|---|---|---|---|
| W-4 | option 1 (W-OPTIONS.md W-4), in §6.1 right after "not adopted" (item 1) | "Whether a small bias increase is an acceptable price for the stability gain is a bias–variance question, which a separate study, specified in advance at truths reserved from this one, is to address; this paper's conclusions do not depend on it." It states that the study exists and why, and reports no result; the plan decision's item 4 stands. **The study's description:** the plan decision `943d5f975:…-methods-baseline-and-plan.md:19-20` ("a declared bias–variance (mean-squared-error) trade-off study at reserved truths", adopted as the strengthened option C at `:59-66`) | Joseph, 11-09: provisional, not locked |
| W-1 | the provisional title stands (item 2) | "Five-observable unbinned unfolding of MINERvA open data with OmniFold: a benchmark and diagnostic study" (unchanged) | Joseph, 11-09: provisional, not locked |

**Presentation, applied with the pre-read pack (`preread-outcomes/`, #993 item 4):** in §5.3, four label variants
began "they are consistent with …", which has no antecedent when the finite-iteration label doesn't hold. They now read
"the readings are consistent with …". The pack's build of case C1 showed the fault. No claim changes.

## Pre-read fixes (the director, 2026-11-09, on `preread-outcomes/NOTES.txt`)

**The director's ruling:** apply the fixes NOTES.txt found before the pre-read, so the read is spent on corrected
text. Each fix narrows printed wording toward its record. Paths: LL5D and FD-PRR are the declarations under
`state/measurement-paper/5d-community-20261024/`, byte-identical at this commit and at main `5a028842a`.
**Coverage wording, the both-cover text above all, is pending Joseph** (#993 item 4: any sentence stating coverage
comes to him before it is final).

| # | NOTES | the fix | record |
|---|---|---|---|
| P-1 | 16 | **The stop case (a defect of mine).** "It stopped under a stopping rule fixed in advance" becomes "It stopped before its pseudo-experiments, at a check fixed in advance, ⟨the check⟩, and gives no coverage reading." A graded run after a repair carries "the repair with which it then ran was chosen after that stop was seen" (`ll5d-route` repaired) | LL5D `:66-71`, `:333-335`, `:684`; `DECISION-20261108-joseph-ll5d-stop-rule.md:28-35` |
| P-2 | 14, 15 | **The clipping-offset routing.** It is worded as a routing. The stopped case, `offset-stopped`, reads "…exceeded the bound fixed in advance, and it was stopped there, before the bulk of its pseudo-experiments, by a decision made after that check was seen". The proceed case, `ll5d-route` offset-proceeded, discloses "…and it proceeded by a decision made after that check was seen" before the graded result. "Before the bulk" because the pilot unfolds one toy | LL5D `:439-440`, `:692`; the pilot `:558` |
| P-3 | 1–5 | **Both-cover, pending Joseph.** The abstract names the object and the variant: "…the procedure's covariance, rebuilt at each tune, covers at both, in the test's primary variant, which omits the uncertainty bands for neutron and proton interactions in the detector, and with those bands; the result concerns the procedure's covariance at those tunes, not the reported intervals at the data." In §6.3: R5's fact moves after the result as "The result concerns the procedure's covariance at those tunes, not the reported intervals at the data."; the qualifier sentence becomes "It grades each of the two truths and each variant separately, and it tests the reported estimator, not the ensemble average."; the overlap sentence is added; the weakened-pass and over-coverage sentences print per reading where the record has them; "it covers" becomes "the rebuilt covariance covers" | LL5D `:52`, `:768-769`, R5 `:512` (`DECISION-20261102-joseph-1b-redesign.md:80-89`), `:146-148`, `:477`, `:478` |
| P-4 | 8 | **Primary covers, with-bands does not.** New abstract classes `both-cover-bands-under-{one,both}` and `both-cover-bands-invalid-{one,both}`, derived in code. Pending Joseph | LL5D `:89-94` |
| P-5 | 9, 10, 12 | **The other gaps.** `under-joint-only` ("under-covers jointly, with no cell flagged"); `invalid-one-covers` and `invalid-one-under` in the abstract; the clipping-artefact sentence ("may be the clipping artefact, a reading that does not remove them"). An invalid reading prints "is not graded, the test being invalid by its own controls there": the test is invalid, not the covariance (found in the pack's second build). **The bias/width attribution is not drafted:** the declaration lists it among the statistics (`:457`, `fd_1b_null.attribute`) but defines no reading or wording for it, so it is open in NOTES.txt | LL5D `:474`, `:480-481`, `:457` |
| P-6 | 18–21 | **IBU.** "same" is worded as a difference below the bar; "flat" is "neither falls nor rises by that margin", with the margin (0.05, to 200 iterations) in the fixed text; the abstract drops "the same" before "noise-free pseudo-data"; an `undefined` class is added to PR-2a and PR-2b, the two places `prr_read` emits it. PR-1's "undefined" already existed. **Open:** FD-PRR says that truth's χ² prints instead, which needs a readout key | FD-PRR `:297-300`, `:292`; `prr_read.py` @ `cf76aec7` `:300-317` |
| P-7 | 23 | **Limitation 1.** "The per-cell coverage readings cited are pointwise, for each reported quantity separately, not the stronger simultaneous coverage of all of them; the joint readings grade the fraction of pseudo-experiments whose χ² lies in a region fixed in advance." | §6.2's joint region (COV2D); LL5D `:472` |
| P-8 | 24 | **Table 1.** The coverage row prints words: through `make_values_fived16.WORDS` for the four readings, "Stopped …" for an ungraded test, and the status Covers, Under-covers, Invalid or Stopped from `ll5d-status`. The caption defines Covers and Invalid, and Stopped becomes "the test stopped before it gave a coverage result". PR-1's "both" prints "reduces and increases". A class key with no `WORDS` entry cannot be printed by `\fvval`: its value is an `\errmessage`. check_round check 8 fails any raw class name, or "joseph" outside the author line, the email and the repository URL, in every fill-test build and every `build_cases.py` build | the director's item 8 |

**Left as they were (the director):** the Supplement's three "declared"; §7 and the conclusions.

## Pre-read rulings (the director, 2026-11-09, on the pre-read #998)

**The reads:** `secondary-results/preread-outcomes-20261109/` (#998 at `8bc6d91b6`), `sonnet-preread.txt` and
`gemini-preread.txt` verbatim, on the pack at `de5d55074`. The director's rulings 1–16, O-4 and O-5 are applied below.
**Every coverage-stating case stays pending Joseph** (#993 item 4). LL5D, FD-PRR and the code are at main `ef9411a3b`.

| # | ruling | what prints now | record |
|---|---|---|---|
| P-9 | 1, what "covers" means | Every pass is "detects no under-coverage, per cell or jointly". The fixed paragraph says "a pass means that no under-coverage is detected at these thresholds, whose resolution is about 0.10 in coverage per cell and 0.08 jointly", and gives the false-flag rate: "in one variant at one tune, the cell readings flag a cell falsely with probability at most 0.025 and the joint reading with probability at most 0.025". Each case with cell flags adds "Each cell flag is a pointwise reading, at the false-flag rate stated above." **Not cited as coverage power:** the calibration record's `power.meets` (`receipts-ll5d/calib-2/calibration.json`, `c873d319a`) is the variance gate's power, 0.8 against a uniform 8 % deflation (`constants.power_min`, `uniform_deflation`; LL5D §5.2), not the coverage grade's. The declaration's figure for the grade is its resolution | LL5D `:469-475`, `:482`, `:486` |
| P-10 | 2, what isn't drawn, **with a correction to §6.3** | The fixed method sentence said only that the response and run-period terms are not drawn. LL5D §3.7 also lists **C_model** as not drawn (`:270`: "a fixed-truth draw cannot produce it. It is what should cover each tune's departure"), and §4 grades C_T = C_e(T) + C_model_abs(T), leaving C_resp and C_PL,5D out (`:305-307`, `:318-322`). It now reads "…the model term C_model in the graded covariance but not drawn, since it is what should cover each tune's departure from the simulation, the response and run-period terms neither drawn nor in the graded covariance, …". Every case with a pass adds "Each pass is for pseudo-data that do not draw the model, response and run-period terms, with the lateral uncertainties carried by a surrogate, and at tunes that are not the two truths at which the fake-data bias is flagged (section 5.2); since the response and run-period terms are also left out of the graded covariance, a pass carries over to the procedure's full covariance at that tune." Every case with an under-coverage adds "Each under-coverage is found with the response and run-period terms left out of the graded covariance, and is not shown to persist with them." The abstract adds "; each pass is for pseudo-data that do not draw the model, response and run-period terms, at tunes other than the two truths where the bias is flagged". This answers Sonnet G2: the terms left undrawn do not inflate the graded matrix, apart from C_model | LL5D §3.7 `:268-272`, §3.8 `:274-281`, §4 `:305-322`, `:768-769`; §5.2's flagged truths |
| P-11 | 3, the scope clause | The clause prints on every graded case, pass or fail (`ll5d-abs-close` scope). When no reading is graded, every reading invalid, it prints "The test therefore gives no coverage reading." (abstract: "the test therefore gives no coverage reading") | LL5D `:768-769`; R5 `:512` |
| P-12 | 4, both variants in the abstract | One clause per variant: `ll5d-abs-minus2` and `ll5d-abs-all`, each one of 15 unordered pairs of the two tunes' classes. Each keeps cells against joint, and "invalid". Derived by `ll5d_derived()` | LL5D `:89-94`, `:474` |
| P-13 | 5, Table 1 status | Covers only when all four readings cover; Under-covers when all four under-cover; Invalid when all four are invalid; **Mixed** otherwise. The caption defines Covers ("…at either truth, in either variant") and Mixed. The Result cell names each tune and adds markers for a descriptive route, weakened passes and over-coverage. VARIANTS.txt shows a row for every case | the director's ruling 5 |
| P-14 | 6, post-hoc modifiers | The route sentence (`ll5d-route`) prefixes any graded outcome. Cases are built for a pass and for a failure under each route | LL5D `:71`, `:439-440` |
| P-15 | 7, O-3 | The abstract discloses it in one clause: ", and these readings are descriptive, because the test continued past its own clipping-offset check by a decision made after that check was seen" / "…because the test ran with a repair chosen after an earlier run of it stopped". The offset-stopped case is "was stopped, by a decision made after its clipping-offset check exceeded its bound, …" | the director's ruling 7 |
| P-16 | 8, the proceed and repair cases, **pending Joseph** (a claim-scope choice) | "…the test continued past it by a decision made after that check was seen, so the readings below are descriptive, not grades fixed in advance." and "An earlier run of this test stopped at a check fixed in advance, ⟨check⟩; it then ran with a repair, ⟨repair⟩, chosen after that stop was seen, so the readings below are descriptive, not grades fixed in advance." The offset value, its cell and the bound are a placeholder (`ll5d-offset`), from clipcheck | LL5D `:439-440`, `:71`; ll5d_b clipcheck (`ffbbb7455`, `:390-411`) |
| P-17 | 9, name the failure, and the numbers the readout emits | Placeholders: `ll5d-stop-what` (the gate or check), `ll5d-repair`, `ll5d-offset`, per reading `-why` (the failed control), `-cells` (the flagged cells with their coverage fractions, counts/300) and `-stats` (joint_count against k_joint, chi2_mean_over_ndf with its se, ndf). Each is a field the readout emits: fd_1b_mc.grade (`b25918fbd`, `:657-694`); the reading rule and the step's `why` (ll5d_b `:535-549`, `:744-747`) | ll5d_b @ `ffbbb7455`; fd_1b_mc @ `b25918fbd` |
| P-18 | 10, the clipping-artefact reading | "…the flagged cells ⟨cells⟩ meet the condition fixed in advance under which a flag is read as possibly the clipping artefact, a clipping offset at or above a bound fixed in advance; that reading does not remove the flags, and no further test of it was run." The declaration defines no diagnostic of it; §7's clipping record is descriptive | LL5D `:480-481`, `:495-497` |
| P-19 | 11, the 2D contrast, **pending Joseph** | In every case with a pass: "The procedure's two-dimensional covariance under-covers at both tunes (section 6.2); this test does not establish why the five-observable result differs." | §6.2 (COV2D) |
| P-20 | 12, the missing cases | Built: the primary under-covering while the with-bands variant covers; invalid in one variant only; cell and joint outcomes differing by tune and variant; passes weakened with the bands; a numerical failure. A numerical failure is INVALID by the Cholesky reading rule, the readout's only numerical class, so the case names it in `-why`. **No class, nothing drafted (NOTES.txt):** joint over-coverage (the readout flags over-coverage per cell only, `over_covers`; `chi2_mean_over_ndf` is printed but has no class); a short pseudo-experiment count (refused, so INVALID, ll5d_b `:602-604`) | fd_1b_mc `:681-683`; ll5d_b `:602-604` |
| P-21 | 13, IBU: both truths | The abstract's class is `prr-abs`, one of the 16 ordered PR-2a pairs: "At both of those truths, …" when they agree, and "At the GiBUU-like truth, …; at the tilt, it …" when they split. "Those truths" are the previous sentence's GiBUU-like truth and synthetic momentum-transfer tilt | FD-PRR `:297-298` |
| P-22 | 14, IBU: the bar and the margin | Abstract: "by more than a bar fixed in advance". §5.3 prints the bar's value (`prr-ibu-bar`, prr_read `floor.bars.IBU`) and "five iterations". The fixed text separates "a fixed margin of 0.05, separate from that bar, between five and 200 iterations", and the variants say "by at least the fixed margin" | FD-PRR `:297-300`; prr_read @ `cf76aec7` `:371-372` |
| P-23 | 15, IBU: undefined | The fixed text gives the condition: "The retained fraction is undefined at a truth where fewer than two cells depart from the prior by at least 1 %." | prr_read @ `cf76aec7` `:20`, `:261-265`; FD-PRR `:251-252` |
| P-24 | 16, the label precedence | **Settled by the record, not open:** FD-PRR §5.4 says "Several can hold at once, and none excludes another". Each holding label prints its own sentence, and no precedence applies. Finite-iteration regularization needs PR-1 F1 = reduces and PR-2b = falls, so IBU's falling retention alone does not give it | FD-PRR `:321-323` |
| P-25 | O-4 | **Already in the caption:** "Pending, the result has not yet been reported" (`paper_body.tex` Table 1 caption, since round 6). Nothing to add | — |
| P-26 | O-5 | R5 caps the method at one sentence: "The method, in one neutral sentence: … The result follows it." The two method sentences are merged into one, and that one now carries what is not drawn. The other fixed sentences are the readings, the grading's meaning and the required facts, "stated as description" (`:85-87`) | `DECISION-20261102-joseph-1b-redesign.md:80-89`; LL5D R5 `:512` |
| P-27 | "GiBUU-like" | The abstract keeps "a GiBUU-like truth" (the hybrid; it is make_values LISTED_CLAIMS' anchor). §7's "for the GiBUU-like change" becomes "for the GiBUU-to-GENIE E_avail change", the §5.1 shape change | §5.1; Table 2 |

**Open (the director):** O-1, the attribution. fd_1b_null.attribute (`cf0505d9e`, `:170-186`) emits bias / width / both, but
the declaration defines no reading or wording for it. O-2, the χ² that prints instead when PR-1 is undefined.
**Reader points not in the rulings:** both are listed in NOTES.txt for the director. One is Sonnet A's request that the
Discussion say a pass would not lift the illustration status; the other is Sonnet AB11's "the second five-observable
coverage test without a result".

## Style integration (the director, 2026-11-09, at Joseph's request): wording only

**The brief (Joseph, through the director):** write as an experienced experimental physicist would for JINST, in plain
declarative sentences with concrete subjects. State each limitation once, where it applies. Cut the reflexive ", not X"
contrasts, give the scope once per place, and avoid labels coined for our own process. A list of AI-text indicators
is not the target. It is a validation set, scored against a field baseline (check_round check 8).

**Two drafts, from cb87c1832, compared passage by passage:**
- **GPT:** codex-school gpt-6.1-sol at high effort (the director's run; its files, CHANGES.txt and prompt are in the
  director's scratch, `restyle/`).
- **Mine:** `style/helper3-draft-20261109` at `68ea8a04d`, local, unpushed and kept for the comparison.

**The gate:** check_restyle.py (new, in this directory). It refuses any change to the \fvval keys, the (\fvcase key,
class) pairs, \fvgroup, \cite, \label, \ref, the numerals and the macros, and to the protected text (Data
availability, the B0 sentences, RS1's paragraph, the LISTED_CLAIMS anchors). It reports every changed sentence.
- **The GPT draft as delivered failed it on three counts:**
  - Data availability ("This analysis used" → "We used");
  - B0's third and fourth sentences;
  - RS1's paragraph.
  All three are restored verbatim.
- **The integrated text passes on every protected span, anchor, numeral and ONCE sentence.** It fails only on the
  structure the rulings below remove or add, each listed and intended:
  - the clipping cases, the weakened marker and the offset;
  - "not shown to persist";
  - the per-case scope clause;
  - the abstract's pass clause, now in the lead;
  - the four S9 pointers, and the S9 paragraph with its pending key;
  - one \mathrm, for "the model term".

**Where each paragraph comes from** (paper_body.tex lines, unchanged in count):
- **GPT:** 14, 17, 24, 29, 50, 53, 62, 71, 77, 81, 83, 89, 93, 146, 157, 160, 166, 169, 179, 190, 196, 222, 225,
  231, 234-236, 243, 246, 272 (results only), 294, 298 and 301, and the abstract's opening and stability sentences.
- **Mine:** 20, 91, 97 (the caption), 125, 185, 278, 281, 304 and 314.
- **Base, kept:**
  - 68, the estimator paragraph, whose line the registry cites by hash;
  - 256, B0, verbatim, with GPT's split of the probe sentence after it;
  - 259, RS1, verbatim;
  - 264, with W-4 verbatim;
  - 272's method sentence, because R5 caps the method at one sentence;
  - the acknowledgments and Data availability, which were outside the brief.
- **New, under the rulings:** 233 (the §5.3 IBU sentence: my structure, GPT's words), 285 and 288 (§6.3), and the
  abstract's coverage and IBU sentences.

**Reverted or adjusted inside the GPT paragraphs, with the reason:**
- **Decided wordings kept:**
  - §1: W-1's "This paper is a benchmark and diagnostic study…", which matches the provisional title;
  - W-22's "An uncertainty for a new choice must be constructed and checked for that choice";
  - §7's "is not established", a claim the director keeps;
  - W-5's "That test is a next step." (ONCE).
- **Chronology (W-20).** GPT's "Two choices … took account of the comparison" goes back to "were made with the
  comparison to the published result in view". The records show that the learner was chosen after the comparison and
  that the background treatment was chosen before it but adopted after. "Took account of" would claim the comparison
  drove both choices.
  - GPT's other chronology edits read true against §4.1's record and are kept: "We chose the refined negative-weight
    background treatment from a closure test in simulation, before computing the refined result's comparison…; we
    adopted it in the analysis only after that comparison was known", and §3.2's "It was added after the differences
    were observed".
- **"Readings" → "results":** kept for the paper's prose. It is our word, not a record's, except in FD-PRR §5.4's
  label names, which stay: "labels fixed in advance" and "a share specific to the implementation" (GPT had
  "interpretations" and "a contribution"). In §6.3 the variants keep "variant"; LL5D's own "reading" means variant.
- **US spelling (B15):** "neighbor", "percent".
- **Kept from mine over GPT's version:**
  - §1's scope: "is an illustration of the method". <!-- absence-ok: quotes draft wording for the comparison; states no finding that a result does not exist --> GPT's "Since interval coverage has not been validated, … is not a
    measurement" narrows §7's four reasons to one.
  - §6.2's first five-observable test stays one sentence (W-20). GPT's "Neither test gave a coverage result" counts
    one test's redesign as a second test.
  - §4.1's duplicated "does not attribute …" sentence is dropped, as in mine.
  - The C_model sentences: "It measures … and is not calibrated as a bound".
  - §5.1's "GiBUU-to-GENIE change", for the GiBUU-like label.

**The director's rulings, applied** (R5 strict; `DECISION-20261102-joseph-1b-redesign.md` item 4, carried by LL5D §8):
1. **Clipping goes to the Supplement.**
   - The weakened passes, the clipping-artefact reading, and the offset's value and cell leave the cases, including
     P-2 and P-18's sentences and Table 1's weakened marker.
   - §6.3's last fixed sentence points to supplementary material S9. S9 gets a paragraph on the second test, with
     "Negative expected counts in its pseudo-data are clipped to zero, and checks fixed in advance bound the effect of
     the clipping before the main run", and its clipping record as the printed key `ll5d-clip-record` inside the coverage test's pending group, filled from the readout. It prints "[PENDING: …]" until the fill, like the paper's other pending results. The director named a \pubhold, but the Supplement's blind build refuses holds by design (`make_supp_rater_copy.sh:9`, "The Supplement has no \pubhold"), and a pending key is filled from the readout as the ruling asks.
   - **This is the director's reading of R5's "to the note":** out of the paper's main text, into the paper's own
     Supplement, so the pointer resolves for a JINST reader. **It is reversible by Joseph, since his text names the
     note.**
   - Per-cell over-coverage stays, as one plain clause per reading.
2. **The decision after the check stays, without clipping:**
   - "A check fixed in advance was exceeded, and the test continued by a decision made after that check was seen, so
     the results below are descriptive (supplementary material, section S9)";
   - the repair route likewise;
   - the stopped case: "…was stopped there by a decision made after that check was seen".
3. **No "does not test" clause:**
   - the 2D contrast is the bare fact, "The procedure's two-dimensional covariance under-covers at both tunes
     (section 6.2).";
   - "not shown to persist" goes;
   - "does not count it as a failure" becomes the fixed text's "Only under-coverage counts as a failure; over-coverage
     is reported."
4. **R5's facts, once, in §6.3's fixed paragraph:**
   - G18's shared 2p2h family;
   - "The result concerns the procedure's covariance at those tunes, not the reported intervals at the data." This is
     the one ", not" in §6.3, Joseph's required wording.
   - The method is one sentence, and it carries what is not drawn.
5. **C_model, PENDING JOSEPH:** "The graded covariance includes the model term, whose role is to cover each tune's
   departure from the simulation, and leaves out the response and run-period terms."

**Also:**
- **The coined label is gone:** "like-for-like five-observable coverage test" is now "a second five-observable
  coverage test", in the §6.3 title, the fixed text, the abstract, Table 1, Limitation 1, the hold and
  `PENDING_GROUPS["ll5d"]`.
- **W-12, a wording change on the same record (sec_5d.tex:196-204, which calls them sensitivities):** "these shifts
  measure the result's sensitivity to the prior".
- **Kept as written, above the field by design:** the five corrective sentences that are this paper's claims, W-11,
  W-22, §1's third finding, §5.4's licensed sentence and §7. REPORT.md says so beside check 8.
- **check_sec4_receipts.py:** VL154's anchor is now `(?:it|the residual) is \SIrange…`, since GPT's "the residual is"
  replaced "it is". The value and the receipt are unchanged, and its test case follows.
- **check_round:**
  - ONCE follows the cross-covariance sentence ("…is unavailable, so the significance of their difference cannot be
    calibrated."), takes "We report the ensemble average as a tested mitigation of the instability." for the
    ensemble, and drops "These results bound what the study shows.";
  - EMPTY: ll5d-abs-close's scope class, and ll5d-anyunder is retired;
  - the no-number check now skips section pointers (\ssec{S9}…).

**A revert after the director's review of 46ed923d** (2026-11-09):
- §1's scope sentence now reads "The sixteen-cell cross section that the estimator gives on the data illustrates the
  method and is not a measurement; …", in the director's wording.
- The style pass had dropped "is therefore not a measurement". That denial carries a claim: Joseph's plan decision
  keeps the measurement as a separate conditional objective, and the result package's scope lines rest on it.
- It sits with the five corrective claims kept by design.
<!-- absence-ok: quotes the restored scope sentence; states no finding that a result does not exist -->

**Triads, read by hand** (style_metrics' 43 hits in the integrated blind manuscript):
- 25 are lists the physics or the definitions need: the five observables, the uncertainty blocks, the generators,
  the deposit species, the settings varied, the terms not drawn, and the problems still open in §7.
- 18 are the regex's artefacts: two-item lists, clause commas, and table text.
- 3 are in the protected Data availability text.
- **2 were reflexive and are cut:**
  - §1's "for the observables, configurations, and deformations tested" becomes "in the cases tested";
  - §3.2's "The blocks, their ensembles and their normalizations are given in …" becomes "Each block is defined in …".
- The three-findings frame ("the estimator has the first, fails the second, and the third…") was the GPT draft's
  cut, and is kept.
- **Reflexive triads: 3 at cb87c1832, 0 now.** The field-maximum flag stays on this pattern, because the needed lists
  remain.

## Joseph's coverage-case decision (2026-11-09), applied

**Record:** `DECISION-20261109-joseph-coverage-case-wording.md` (#1002 at `c68ec3b97`), Joseph's "yes lets apply it". It
rests on the independent gpt-6.1-sol read (`secondary-results/independent-read-coverage-status-20261109/answer.txt`).
**Nothing is locked** (item 4). A coverage sentence prints only from the test's outcome record.

| item | what prints now | record |
|---|---|---|
| 1, the pass wording | The integrated text at `9b6f5cb2`, with: (i) "The graded covariance includes the model term, whose role is to cover each tune's departure from the simulation", already in §6.3's fixed paragraph, followed by "and leaves out the response and run-period terms"; (ii) "The data result remains an illustration.", once, closing §6.3, after the case text; (iii) the carry-over sentence in the declaration's terms: "a cell that passes at a tune also passes under the procedure's full covariance there, and the joint reading carries over only if both matrices have 16 degrees of freedom". The pass cases print their numbers through `-stats` and `-cells`, as sol asks | decision item 1; LL5D `:318-319` ("The χ² region carries over only if both matrices have ndf = 16"; §6's ndf is the rank above 10⁻¹²) |
| 2, adaptive routes | Table 1's status is **Descriptive** whenever `ll5d-route` is offset-proceeded or repaired, whatever the readings (`ll5d_derived()`). The readings print in the Result cell, which says "The run continued past a check by a later decision" or "The run was repaired after a stop". The caption's Descriptive gains a second clause: "for the second five-observable coverage test, the criteria fixed in advance were applied, but the run continued, or was repaired, by a decision made after a check was seen". The abstract and §6.3 keep their disclosure. **S9** prints "The gate sample's first 300 draws are the coverage pseudo-experiments' draws, at the same seeds." in every case, and for these routes a new pending key, `ll5d-route-record`: the exceeded quantity and its bound, what was visible when the decision was made, its reason, and every repair. No value is drafted | decision item 2; LL5D `:252` |
| 3, no "Mixed" | Table 1's Result cell gives one entry per tune and variant, primary first: "primary, without the two bands: G18, ⟨entry⟩; AR23, ⟨entry⟩. With them: G18, ⟨entry⟩; AR23, ⟨entry⟩". Each entry is *no under-coverage detected*, *under-coverage flagged* or *invalid*, through `WORDS`. **No outcome summary:** the status column gives only the run's standing, *Graded*, *Descriptive*, *Invalid* (every entry invalid) or *Stopped*, and the caption defines each. *Covers* and *Mixed* are retired. The abstract's per-variant wording stays | decision item 3 |

**A layout choice, for the director:** the 2×2 is in the Result cell, the only column wide enough (8.6 cm).
- **Table 1 is now \footnotesize throughout** (it was \scriptsize from round 6), as the decision's "at \footnotesize or
  larger" asks.
- It is checked on the pending build and on the longest filled case: no overfull box, no "Float too large", 13 pages.
  No \resizebox. The status cell carries only Graded / Descriptive / Invalid / Stopped, which says how
the run stands, not what it found.

## The Supplement's style integration (the director, 2026-11-09): wording only

**The draft:** a gpt-6.1-sol restyle of supplemental_body.tex under the same general brief, on a copy at `531fefe4`
(the director's run, `restyle-supp/`; work file sha256 `b95f3dd3…`). It was integrated through check_restyle.py,
which is extended to the Supplement:
- its inventories;
- the 35 paper pointers, run through check_supp_pointers in both trees;
- the ``…'' record quotes;
- the 23 strings #981's build checks (`supp-quotes.tsv`, limitation-resolver's list, counted the way #981 counts
  them).

**The draft as delivered failed it on Q09, Q10, Q19 and Q20**, all in S11's validity paragraph.

**Reverted to the base, with the reason:**
- **:634, S11's validity paragraph:** #981's quotes.
- **:279, the rounding-mechanism lines:** RS1's licensed clauses (W-8). The draft had replaced the licensed "sufficient
  entry".
- **:496:** it dropped "The extrapolation assumes geometric convergence.", a stated assumption.
- **:507:** "show no evidence of additional discrimination" had become "do not demonstrate". That changes absence of
  evidence into "not demonstrated".
- **:605:** it dropped the claim that the χ² values "establish no exclusion of a generator".
- **:560:** my S9 paragraph, whose route sentence the draft garbled.

**Patched:**
- **:235:** "We do not adopt that recommendation." is restored.
- **:387 and :627:** the plain forms are restored ("so it carries no information about its coverage…"; "and no exclusion
  of a generator follows") in place of the draft's "does not establish" framings.
- **US spelling (B15):** the draft's new "labelled", "centres", "centring" and "standardised" are reverted. The base's
  own "labelled" at :634 is untouched, since that line reverts whole.

**Kept from the draft, read against their records:**
- the chronology rewrites at :196 and :275 (the closure test decided the background change before the distance was
  computed; LightGBM was chosen after the comparisons), which match §4.1's record;
- :504, which fixes the base's garbled "It is the simulation's per event";
- the plain descriptions in place of process labels ("matched block-sum comparator").

**Provenance (the director's ruling):** each of the 29 restyled paragraphs under a "verbatim" comment now says so.
- "(restyled 2026-11-09, wording only; the note keeps the original; comments stripped; …)", for note copies;
- "…restyled 2026-11-09 from that text, wording only…", for passages moved from round 5's paper.
check_restyle reports none left unmarked.

**Checks:**
- check_restyle: PASS (23 quotes; 35 pointers, 0 failures);
- check_sec4_receipts: 16/16, and its tests pass (S6's 0.676 % anchor holds);
- check_round: PASS; check_registry: PASS.

**check 8 on the blind Supplement, per 1,000 words** (field max in brackets; 531fefe4 → now):

| pattern | before | after |
|---|---:|---:|
| ", not" [0.30] | 0.98 | 0.33 |
| rather than [0.45] | 0.90 | 0.82 |
| corrective [0.12] | 0.25 | 0.25 |
| semicolon chains [0.67] | 1.23 | 1.07 |
| triads [2.34] | 4.35 | 3.88 |
| fragments [1.08] | 1.97 | 2.06 |
| sentences ≤ 5 words [1.00] | 1.89 | 1.98 |

The rest stay above the field by design or for structural reasons:
- most "rather than" hits are physics contrasts the reader needs ("subtracts 135 MeV rather than the charged-pion
  mass", "measured from a fixed beam axis rather than from the true neutrino direction");
- the fragment and short-sentence counts are table and caption debris in the blind text;
- the triads are lists.
They are not pushed further, to avoid overfitting the metric.
- **:174:** "No effective sample size of the unfolded ensemble is computed" is restored, since the hook flagged the draft's "is not computed" as a bare absence claim. <!-- absence-ok: quotes the restored method-scope sentence (what is computed); states no finding that a result does not exist -->

## Figures 1 and 2 of the figures lane (the director, 2026-11-09), integrated

The figures lane's branch (06ba96d12, after its repair cycle) is merged as aec48fb91. Its producer,
`figures/methods_short/make_figures.py`, reproduces the committed PDFs byte for byte. The paper prints both
figures with the lane's captions (`captions.tex`). `captions.tex` itself is the lane's file and is not edited.
(Corrected below: the first version of this paragraph, at a97e6e10c, said the only change was "Colour" -> "Color".
That was false.)

| Item | Where | Source |
|---|---|---|
| Fig. `fig:bias-cells` | section 5.2, cited after Table 2's lead sentence, placed `[tb]` before the table | F0b readouts with and without C_PL,5D (make_values READOUTS / NOPL_READOUTS); HANDOVER.md "Bias by reported cell" |
| Fig. `fig:prior-response` | end of section 6.1, `[t]`; cited in section 7 ("these shifts measure the result's sensitivity to the prior") | the note's gbdt_prior_response diagnostic (sec_5d.tex:196-204) |
| 5.17, printed in the figure only | the bias figure's right panel, GiBUU hybrid truth | `f0b-A7_gibuu-zmax-nopl` (values_fived16.tex:1171), from the pinned NOPL readout; numbers.json max_abs_z 5.172...; Table 2 does not print this key |
| 109 / 27 / 39 supported cells | the prior-response caption | app_statmethods_nd.tex:25 ("109 J, 27 H2 and 39 EW cells") |

Placement. The prior-response figure was first placed before section 7. There the normal build's long section 7
hold ("A citable home for records ...") crossed a page break with the figure's text extracted inside it, and the
blind rater copy failed its hold-diff check (`make_rater_copy.sh`: "differs from the normal build in more than
hold text"). `[b]` before section 7 and `[p]` also failed. Before section 6.2, `[t]` passes: multiset VERDICT
PASS, 14 pages in both builds, and the blind copy prints FIG. 4 (bias) and FIG. 5 (prior response) in full.

`check_round.py` gains check 9, `check_figures`, which calls the producer's `check_against(paper_body,
values_fived16)`: Table 2's truth order, `trig-z` and the plotted maxima. It passes on this tree and fails on a
swapped truth order or a changed `trig-z`.

Checks at this commit: `check_round.py . --fill-test` PASS (0 failures; 16 fill builds), `--self-test` PASS,
`check_registry.py` PASS, `check_sec4_receipts.py` 16/16 and its pytest 17 passed, `check_supp_pointers.py` 35
pointers and 0 failures. `check_restyle.py` against e97d2b20 fails only on the additions this commit makes
(labels `fig:bias-cells` and `fig:prior-response`, their refs and the captions' refs, one `\fvval{trig-z}`, the
caption macros). No protected span, LISTED_CLAIMS anchor, numeral or Supplement inventory changed. Check 8 (report
only) on the new blind manuscript: 7,649 words, against 7,595 in the pack's blind copy (531fefe42). Triads are 41 in
both (5.36 and 5.40 per 1,000 words). Semicolon chains are now 6, against 5 (0.78 per 1,000 words), just above the field
maximum of 0.67. The captions are not restyled here.

Fig. 3 (rounding shifts) is not in this commit. It waits on director-helper-2's extraction of r2_cache.npz, with
provenance pinned and the reproduction of median 0.8, maximum 2.6 and argmax J145. It is then integrated in its
own commit.

### Corrections and follow-up (journal-editor's read of a97e6e10c, item 1; the director, 2026-11-09)

- **My error at a97e6e10c.** The paper's prior-response caption dropped the lane's limiting clause ", not a measured
  bias of the data result" (licensed by sec_5d.tex:204, "shifts do not measure unknown real-data bias"), and the
  paragraph above misstated the changes. The caption is now the lane's final caption, verbatim.
- **The lane's last commit is merged.** 532f079b0 adds the J/H2/EW counts (109/27/39, app_statmethods_nd.tex:25) to
  the prior-response caption, so the table row above is now true. 39 is in check_round's NEW_NUMERALS with that
  source; 109 and 27 are in the base.
- **The bias caption's changes, all recorded.**
  - "Colour" -> "Color".
  - "to two decimals as in the table" -> "to two decimals; in the left panel they are those of table 2". Table 2
    prints max |z| for all 12 truths under the reported covariance, and only there. The right panel's maxima
    (without C_PL,5D) are figure-only: one of them is the 5.17 above.
- **The section 7 hold item, dropped.** The item read "Fig. 3 for the reported estimator: its per-cell fake-data
  residuals against C_total+C_resp+C_PL,5D are not yet drawn". It was added in 0de103f7d, beside the deformation
  figure, which plotted a development variant. The director asked whether "residuals" there means fractional
  residuals or any per-cell view.
  - My read: "against C" is the paper's usage for grading under that covariance (section 5.2, "the estimator's bias
    against the reported covariance"). So the item asked for the per-cell residuals graded under that covariance.
    That is the per-cell z that Fig. bias-cells plots, at every graded truth.
  - The item is dropped. Its "Fig. 3" also clashed with the printed numbering (the bias figure prints as FIG. 4).
  - The long section 7 hold, "A citable home ...", is Joseph's banked item and stays.
- **The placement note.** check_round now prints a NOTE on every run: a reflow of sections 6-7 can split the
  section 7 hold across a page break and fail the blind rater copy; rebuild it after any such change.
- **Semicolon chains (the director's item 3).** The one new chain against the pack's blind copy that came with the
  figures is not prose. It is the bias figure's y-axis tick labels, which pdftotext extracts as "(Eavail ; W)" and
  "(pT ; p∥ ; Eavail)". Nothing is split. The other new chain is section 6.1's rounding sentence (:264), which
  predates the figures.

Checks after these changes:
- `make_rater_copy.sh`: multiset VERDICT PASS, 14 pages in both builds. The blind copy prints FIG. 4 and FIG. 5,
  with "not a measured bias of the data result", "J, 109" and "those of table 2".
- `check_round.py . --fill-test`: PASS. `--self-test`: PASS.
- `check_registry.py`: PASS. `check_sec4_receipts.py`: 16/16, and its pytest: 17 passed.
- `check_supp_pointers.py`: 35 pointers, 0 failures.
- `check_restyle.py` against e97d2b20 fails only on the figure additions, as above, plus the numerals 27 and 39 and
  the one `\pubhold` removed.


## Figure 3 of the figures lane (rounding shifts; the director, 2026-11-09), integrated

The lane's 631f8ec2c is merged as f83a42256. The lane's branch carries main to 13d714bfc (#1006, #1007, #1008), and
the merge brings that in. journal-editor's seven items on cdc14205b are closed at 631f8ec2c.

| Item | Where | Source |
|---|---|---|
| Fig. `fig:rounding-shifts` (prints as FIG. 5) | section 6.1, after the RS1 cross-fitting paragraph, `figure` `[tb]` at `0.75\linewidth`; cited in "Over the 153 quantities ... statistical standard deviations (figure 5)" | `a3_rounding_shifts.csv` (PR #1008, sha256 9ac8f7d8b74f090c, pinned in inputs.json) |
| 153 = 109 J + 42 EW + two totals | the caption | the CSV's rows, counted: J 109, EW 42, EW_all_ones 1, total_integrated 1 |
| 42 | the caption | that count; in check_round's NEW_NUMERALS with this source |
| median 0.8, maximum 2.6 (J145) | the figure's labels, at the text's precision | the CSV: 0.7829505732456221 and 2.5837789197284393 |

- **Provenance (journal-editor's Fig. 3 item 7).** The CSV is not the original in-memory array. The receipt's own
  producer recomputed it from the 103 committed inputs (HANDOVER.md, "Rounding figure delivered from committed
  CSV"; the receipt's README.md). The recomputation reproduces the assess receipt's median, maximum and argmax bit
  for bit.
- **The caption** is the lane's, with one change: journal-editor's optional "the reference is the same input
  values represented in float64" -> "the reference is the unperturbed inputs in float64".
- **The 0.75 width is set by the blind rater copy.** At `\linewidth` and at 0.85 the normal build ran to 15 pages,
  with references 17-21 pushed over by the hold text, while the rater copy stayed at 14. The extra page number
  then failed `multiset_check.py`, whose letter multisets must match. The placements tried at full width were
  `[!tb]`/`[htb]` after the RS1 paragraph, `[!t]` at the head of 6.1 and `[tb]` at the head of section 6; all
  failed. At 0.75 both builds are 14 pages, multiset VERDICT PASS, and the blind copy prints FIGS. 1-6. I read the
  rendered page (page 10): the figure is legible at this size.
- **HANDOVER.md is stale on one point.** It still says the median and maximum "are labeled at two decimals"; the
  figure and caption now label them at the text's precision. That is the lane's file, so I have not edited it.
- **The same fragility as Figures 1 and 2.** Any later growth of the text, the fill included, can change the
  page count of one build and not the other. Rebuild the rater copy after it (check_round's NOTE).

Checks at this commit:
- `make_rater_copy.sh`: PASS, 14 pages in both builds.
- `check_round.py . --fill-test`: PASS, with check 9 against the lane's updated `check_against`. `--self-test`:
  PASS.
- `check_registry.py`: PASS. `check_sec4_receipts.py`: 16/16, and its pytest: 17 passed.
- `check_supp_pointers.py`: 35 pointers, 0 failures.
- The producer reruns with no change to any committed asset.

## The abstract's compression and journal-editor's items 4, 5, 7, 8 and 9a (the director, 2026-11-09)

On journal-editor's read of a97e6e10c, the director's rulings, after my measurement showed that the first ruling (the
longest case under 1,920 characters by compressing prr and ll5d only) could not be met:
- **Length: options (C) and (A).** The compression is committed. It is wording only, and the coverage clauses stay
  pending Joseph (#993 item 4).
  - check_round check 10 gates the printed abstract once it is filled: it fails above 2,000 characters until Joseph
    sets a limit. Before the fill, it reports the range over every consistent case. Now: 10,848 cases, 1,802 to
    2,343 characters.
  - The 1,920 characters apply to a separate arXiv metadata abstract, written at submission (REPORT.md, "Follow-up:
    before submission").
  - Joseph also decides whether the abstract cuts content at the fill (the director's option B).
- **The measurement.** `abstract_text` renders the source with `\fvgroup`/`\fvcase` resolved and `\fvval` from the
  values. On a built long case (prr same-more, ll5d uc-ujc in both variants, offset-proceeded) it gave 2,286
  characters against pdftotext's 2,287. The letters are identical; the difference is the space in "0.133 %".
- **V-A1 (prr-abs):** one sentence per class, generated from one phrase table. Every class keeps:
  - the comparator, "a binned iterative unfolding of noise-free pseudo-data at five iterations";
  - the direction at each truth;
  - "a threshold fixed in advance";
  - for "undefined", "the retained fraction is undefined, and no comparison is made".
- **V-A2 (ll5d), graded:** one sentence. It names the object ("grades the procedure's covariance at the same tunes"),
  and keeps the scope clause (where the bias tests pass; pseudo-data that do not draw the model, response and
  run-period terms), the primary variant, both per-variant pairs and the route clause, which is now a clause after a
  semicolon.
  - "under-coverage in some cells, but not jointly" -> "under-coverage in some cells only".
  - "joint under-coverage, with no cell flagged" -> "joint under-coverage only".
  - "under-coverage in some cells at both tunes, and jointly at one" (uc-ujc) and "joint under-coverage at both
    tunes, and under-coverage in some cells at one" (uj-ujc) now take the general one-tune/other-tune form. They say
    the same.
  - My first draft dropped the verb and object ("grades the procedure's covariance"), and its short forms "in cells
    only" and "per-cell" lost "some". I restored both before this commit.
- **Item 4:** "On the 16 reported cells, these changes move the results by a median of 0.133%" -> "On the 16
  reported cells, the spread under 20 such perturbations is a median of 0.133% of the cross section" (the body,
  sec:cov5d: "over 20 rounding-level perturbations of the data, it is a median 0.133%"). This adds the numeral 20 to
  the abstract.
- **Item 5:** "A second five-observable test" -> "A five-observable test built the same way as the two-dimensional
  one", in the graded case and the three stop cases. Table 1 and sections 6.2-6.3 keep first and second.
- **Item 7:** the abstract keeps its terms, which are a LISTED_CLAIMS anchor. Section 3, after its list of truths,
  now says "The abstract calls the GiBUU hybrid truth GiBUU-like and the $q_3$ tilt the synthetic momentum-transfer
  tilt."
- **Item 8:** Table 1, "Its gate compared unlike objects" -> "A preliminary check compared unlike quantities".
- **Item 9a:** section 6.1, "Over the 153 quantities defined below" -> "Over 153 quantities (the joint cells, the
  $(\Eavail,W)$ cells and two totals)". The B0 sentences, which repeat the definition, are protected and unchanged.

Checks:
- `make_rater_copy.sh`: PASS, 14 pages in both builds, FIGS. 1-6.
- `check_round.py . --fill-test`: PASS. `--self-test`: PASS, with check 10's three planted cases.
- `check_registry.py`: PASS. `check_sec4_receipts.py`: 16/16, and its pytest: 17 passed.
- `check_supp_pointers.py`: 35 pointers, 0 failures.
- `check_restyle.py` against 0bc36ce87 fails only on `\Eavail` (item 9a) and the numeral 20 (item 4). No protected
  span, anchor or Supplement inventory changed.
- **Superseded (the director, 2026-11-09):** after the multiset check's page-number fix (REPORT.md, "The rater
  copy's multiset check"), Fig. 3 is back at `\linewidth`. The rater copy passes at 15 and 14 pages.

### journal-editor's read of ce565239d, applied (wording only; the coverage clauses stay pending Joseph)

- **Item 1, a misreading I introduced.** "only" before the tune phrase attached to the tunes: for example uc-ujc
  printed "under-coverage in some cells only at one tune", although the cells under-cover at both. My ledger's
  "they say the same" above was false as printed.
  - The pair words are now "per-cell but not joint under-coverage", "joint but not per-cell under-coverage", "joint
    and per-cell under-coverage", "no under-coverage" and "fails its own controls".
  - check 10 now fails any rendered case that prints " only at " (ABSTRACT_BANNED). It fails the ce565239d abstract
    and passes this one, and its self-test plants the phrase.
- **Item 2.** The prr "same" classes read as equality, and "within it" had no referent. They now say "differs from
  the [five-observable] estimator's retained fraction of the prior by less than a threshold fixed in advance", or
  "... by less than that threshold" after a threshold is named.
- **Item 3.** The gate-failed case reads "stopped at an entry condition fixed in advance" in the abstract, Table 1 and
  section 6.3, which keeps it distinct from the stop case's "a check fixed in advance". Section 6.2's "one of its
  gates" (the first test, r5:283) and the section 7 hold are unchanged.
- **Item 4.** "where the bias tests pass" -> "where the estimator's fake-data bias is not flagged". This is the
  wording of section 6.3 ("at tunes where the bias is not flagged"), and section 5.2 (:233) supports it: "Both tunes
  satisfy the bias criteria", under the reported covariance.
- **Item 5:** "with them, it" -> "with those bands, it".
- **Item 6:** the abstract's first "estimator" is now "the five-observable estimator", in every prr class.
- **Item 8 (optional):** not applied. The section 3 sentence is already the body's first use of both names.
- **Length.** These fixes lengthen the worst case from 2,343 to 2,420 characters (prr same-more, ll5d uc-uj in both
  variants, offset-proceeded). The cut is Joseph's decision (option B) before any filled case can pass check 10.

Checks:
- `make_rater_copy.sh`: PASS (15 and 14 pages).
- `check_round.py . --fill-test`: PASS. `--self-test`: PASS.
- `check_registry.py`: PASS. `check_sec4_receipts.py`: 16/16, and its pytest: 17 passed.
- `check_supp_pointers.py`: 35 pointers, 0 failures.
- `check_restyle.py` against 7960906a2: PASS.

- **journal-editor's residue at 506c74581:** section 6.2's "one of its gates, which compared ..." -> "one of its
  preliminary checks, which compared ...", to match Table 1. No current check protects the sentence (ONCE,
  LISTED_CLAIMS, the sec4 receipts, the restyle spans). The blind copy now prints no "gate". The section 7 hold's
  "pre-check's gate" leaves with the hold. Checks: the rater copy, check_round with the fill test, the self-test,
  registry, sec4 (16/16, 17 passed), pointers (35/0) and check_restyle against 506c74581 all pass.

## journal-editor's JINST read of the Supplement (f51d22c8b -> 8cc26c0ee), applied

The Supplement's restyle, which I integrated as wording only, changed meaning in these hunks. That was my integration
error: check_restyle guards the inventories, not the sense of a sentence. Each fix below is a revert to the base or
a narrowing.
1. **Timing:** "fixed before any test was evaluated" -> "fixed before any of the tests was graded against them"
   (base). "A truth fails when" -> "A truth is flagged when" (the paper's term).
2. **S9 clipping paragraph.**
   - "checks fixed in advance bound the effect of the clipping" -> "test the effect". "Bound" asserts that the
     checks succeeded, which is false if the offset-proceeded route continued past a clipping check.
   - "The gate sample's first 300 draws are ..." -> "..., on a sample whose first 300 draws are the coverage
     pseudo-experiments' draws, at the same seeds". This keeps the fact that Joseph's #1002 item 2 requires (the
     shared first 300 seeds).
   - "Its clipping record, from the readout:" -> "The clipping checks gave the following:".
   - The two values, `ll5d-clip-record` and `ll5d-route-record`, are free text written at the fill. Their declared
     content: the passes weakened by clipping, the flags meeting the clipping-artefact condition, and the largest
     clipping offset with its cell; and the exceeded quantity and its bound, what was visible, the reason, and every
     repair. Their printed sentences get a read at the fill.
3. **"Gate".**
   - S6 diagnosis: "the departure from the gate" -> "the departure from the window" (the preliminary check's window,
     named in that paragraph).
   - The two remaining printed uses (S4 :291 and S6 :551, "the ratio's statistical gate") are the note's statistical
     requirement on the reweighting ratio, a different object, and are in the base. They are kept. Defining them as
     "the preliminary check of section 6.2" would be false.
4. "..., so the distance depends on the estimator" -> "and the distance ..." (base).
5. "flags three failures, all attributed to bias" -> "raises three flags, each attributed to bias" (paper :237).
6. "The audit establishes neither" -> "Passing the audit establishes neither" (base).
7. "Production retains the inherited constant." -> "The analysis code retains the inherited constant."
8. At (e)'s definition: "(e), the five-observable estimator (the joint-test estimator of Ref. [note])", so readers
   following the \nsec pointers find the note's name. This adds one \cite, check_restyle's only failure. The paper
   still never prints "joint-test estimator" (GONE).
9. **The director's W-batch sentences (S7), copy only.** "conditionally on" -> "conditional on"; "They are not
   physical exclusions" -> "The rejections are not physical exclusions"; "(this section)" dropped.
10. S1: "comprises" -> "is in". S2: "by construction rather than by truncation" restored. S4: "is appropriate for" ->
    "the natural treatment for" (base).

Checks:
- `check_restyle.py` against 8cc26c0ee fails only on item 8's \cite. The 23 #981 quotes and the 35 paper pointers
  hold.
- `make_supp_rater_copy.sh`: rc 0, 25 pages, 8 of 8 table captions. Every fix prints in the blind Supplement; the S9
  clipping sentence is in the pending ll5d group.
- `check_round.py`: PASS, its style report run on the new blind Supplement. `check_registry.py`: PASS.
- `check_supp_pointers.py`: 35 pointers, 0 failures.
- **After journal-editor's check of 069370826:**
  - check_round check 11 (FREE TEXT) fails any filled free-text value that prints gate, record, readout, receipt,
    lane, binding, declaration, a DECISION/OUTCOME name, a date, an .md file or a PR number. It is self-tested with
    five planted values and one clean one.
  - "the ratio's statistical gate" is kept. It is the note's own wording (sec_fived16.tex :99, :251), with no more
    specific name to point to.

## The meaning check of both restyles (the director, 2026-11-09)

This check catches what check_restyle's inventories cannot. `meaning-check/export_pairs.py` exported every changed
sentence pair:
- the paper, cb87c1832 -> 32cf5c5fe's tex: 239 rows;
- the Supplement, 531fefe42 -> 32cf5c5fe's tex: 148 rows;
- the result, `meaning-check/pairs.tsv`, sha256 a299909c30412188.

The director ran two fresh readers, one for each file, with a strict "claims more" brief
(`meaning-check/prompt.txt`). They flagged 17 of 239 paper rows and 6 of 148 Supplement rows
(`meaning-check/out-paper.txt`, `out-supp.txt`). The director's triage gave 11 FIX, 9 DISMISS and 3 VERIFY. I
checked each dismissal and verify below against the record.

| Row | Decision | What was done, or why dismissed |
|---|---|---|
| M009 | FIX | §1: "for the observables, configurations and deformations tested, not of multidimensional OmniFold in general" restored |
| M084 | FIX | §4: "It is a correlated shape difference, not a normalization difference" (the eigenmode analysis) |
| M090 | FIX | §4: "…is descriptive, not a blind validation" (the director's earlier ruling) |
| M091 | FIX | §4: "test … against" -> "compare … with" |
| M131 | FIX | §5.2: "only event counts fluctuate, with the systematic parameters fixed" |
| M212, M213 | FIX | §7: both exclusions restored once, before "Whether the two-dimensional shape difference …" (W-5 option 1; decision item 6) |
| M228 | FIX | Limitation 1: "…, not the stronger simultaneous coverage of all of them" |
| M252 | FIX | S1: the note's verbatim sentence (sec_eavailw.tex:67) restored, "do not, by themselves, provide five independent constraints: the result is five simultaneous observables, not five independent measurements". This also reverts my earlier "The result is in five …" (journal-editor item 10), since the paragraph is labelled verbatim |
| M293 | FIX | S2: "Non-negativity is structural, while the value at the floor follows …" |
| M339 | FIX | S7: the note's verbatim sentences (sec_joint.tex:34), "…, and so it affects power. The null calibration below, not the metric, sets each test's size." |
| M111 | VERIFY -> FIX | §5.1 is the E_avail shape reweighted by the GiBUU-to-GENIE ratio (its paragraph, the f0b-stage0c_gibuu key), and S8 names it "the GiBUU-to-GENIE $\Eavail$ change". So it now reads "the GiBUU-to-GENIE $\Eavail$ change", as in §7 (P-27) |
| M223 | VERIFY -> DISMISS | The COV2D scope fact prints in §6.2 (:296) and in §6.3 (:309): "The result concerns the procedure's covariance at those tunes, not the reported intervals at the data." |
| M381 | VERIFY -> KEEP | LL5D-DECLARATION.md §3.6 (the seeds table): "the gate sample (§5.2), whose first 300 are the toys' draws". §5.2 :365-366 evaluates the clipping gate on that sample, and §5.3 :432-436's clipcheck uses the 300 declared draws, which are its first 300. The merged sentence is supported |
| M069 | DISMISS | #1002 item 3: Invalid only when every entry is invalid (ledger :383-389) |
| M075, M194, M195 | DISMISS | R5 ruling 1: the clipping detail moved to S9 (ledger :306-311). M075 is a mis-paired caption row, base status words against the #1002 statuses |
| M196 | DISMISS | R5 ruling 3: no "does not establish" clause (ledger :321) |
| M192 | DISMISS | #1002 item 1: the carry-over sentence with the rank-16 condition (DECISION-20261109-joseph-coverage-case-wording.md :36-37; ledger :381) |
| M236 | DISMISS | journal-editor item 4, the director's ruling: the body's "over 20 rounding-level perturbations" (ledger :603) |
| M280 | DISMISS | the joint-test-estimator pointer the director approved (ledger :691) |
| M379 | DISMISS | "bound" -> "test", journal-editor's correction (ledger :671) |

That is 11 slips of meaning, all of which passed check_restyle. Two of them (M252, M339) were inside paragraphs
still labelled "verbatim" from the note.

A sweep of every "verbatim"-labelled Supplement paragraph against the note's sources was too noisy to use: 128 of its
sentences differ, mostly through the Supplement's pointer rewrites (\ref -> Ref.~\cite…\ref*{N-…}). So I rely on
the readers' base-against-current read here, not on that sweep.

Checks:
- `make_rater_copy.sh`: PASS (15 and 14 pages). `make_supp_rater_copy.sh`: rc 0, 8 of 8 captions. Every FIX prints
  in the blind copies.
- `check_round.py . --fill-test`: PASS. `--self-test`: PASS.
- `check_registry.py`: PASS. `check_sec4_receipts.py`: 16/16, and its pytest: 17 passed.
- `check_supp_pointers.py`: 35 pointers, 0 failures.
- `check_restyle.py` against 32cf5c5fe fails only on the one added `\Eavail` (M111). The #981 quotes hold.
- **journal-editor's read of 000f13805.**
  - Item 1 applied. §4.1: "It is a correlated shape difference" -> "The difference is a correlated shape
    difference", since "It" pointed back to the χ²/ndf value.
  - Item 3 applied as the base sentence (cb87c1832), "These tests assess bias, not coverage: only event counts
    fluctuate, with the systematic parameters fixed." The editor's wording would have dropped the "only" that M131
    restored.
  - Item 2 (rewording §7's restored benchmark exclusion as "a shape difference of unidentified source") changes
    content in a sentence held by W-5 option 1 and decision item 6, so it went to the director, not applied.
  - Item 4 (optional "deformations") not applied: it is the base wording, restored by M009.
  - Checks: the rater copy, check_round with the fill test, registry, sec4, pointers, and check_restyle against
    000f13805 all pass.
- **W-5, a wording change resting on §4.1 (the director, 2026-11-09, on journal-editor's item 2).** §7's benchmark
  exclusion (L-22) now reads "The benchmark shows agreement in normalization and a shape difference of unidentified
  source in two dimensions; it does not validate the five-observable distribution."
  - Its record is §4.1's "The source of the shape difference has not been identified", the sentence #981 quotes.
    "Qualified" was undefined.
  - Decision item 6's exclusion (:74, "that 5D validates the full distribution") survives as the denial.
  - **check_round's GONE guard changed with it.** `validat\w* the (full|five-observable) distribution` matched the
    denial. It is now `(?<!not )validat...`, so it still refuses the affirmative claim that item 6 forbids. Its
    self-test plants both forms: the affirmative is caught, and the denial passes.
  - Checks: the rater copy PASS (the denial prints once), check_round with the fill test PASS, the self-test PASS,
    and registry, sec4, pointers, and check_restyle against 1bf524e53 PASS.
  - The director's addition: the self-test also plants "not only validates the five-observable distribution", which
    is caught (an affirmative claim behind a "not"). Measured on the guard: "not only validates" is caught, "does
    not validate" passes, "validates" is caught, and "never validates" is caught, a safe false positive.

## The 200-250-word abstract (Joseph, 2026-11-09, via the director), draft for an independent read

Joseph's decision: the typical length, 200-250 words, and content may be cut if it still makes sense. The director's
structure, kept in order: the method; the benchmark; the prior-retention finding; the stability finding with the
ensemble in one clause; W-11; the coverage test per variant only; the illustration line.
- **Cut:** "Three findings follow."; the observables list (section 1 keeps it); the seed sentence (section 6.1 keeps
  it); the 0.133% sentence (section 6.1 keeps it); "medium-energy" (sections 1-2).
- **The prior-retention comparison (prr-abs) is now one clause of the fake-data sentence:** binned iterative unfolding
  of noise-free pseudo-data at five iterations "retains less / more / a similar share of the prior" at each truth, or
  an undefined share. The threshold's detail ("by more than a threshold fixed in advance") is in section 5.3. This is
  the director's "detail beyond one clause waits for the fill".
- **The coverage test (ll5d), per variant only:**
  - one sentence: "The same coverage test, applied to the procedure's five-observable covariance at those tunes, where
    the fake-data bias is not flagged, without drawing the model, response and run-period terms, finds X (primary
    variant, without two detector bands) and Y (with them); [the route disclosure]";
  - X and Y in Table 1's per-tune terms: no under-coverage, under-coverage or an invalid reading, at one tune, both
    or either. The per-cell and joint detail is in section 6.3.
  - "The same coverage test" replaces "A five-observable test built the same way as the two-dimensional one" (item
    5's antecedent), to fit the limit. The R5 object, "the procedure's ... covariance", is kept.
  - The stop cases read "The same coverage test of the procedure's five-observable covariance stopped ...".
- **Kept verbatim:** the benchmark, W-11 and the illustration line.
- **The LISTED_CLAIMS anchor** "at a GiBUU-like truth and at a synthetic momentum-transfer tilt find" is kept verbatim
  and does not move. The rest of that sentence is shortened ("residual bias beyond uncertainty-based criteria fixed
  before grading"). `make_values_fived16.py --check` passes: 10 listed-truth sentences agree.
- **The stability sentence:** "The five-observable estimator is numerically unstable: rounding-level input changes
  shift results by up to 2.6 statistical standard deviations, beyond a requirement fixed in advance; an average of 96
  fits meets it but has greater bias at one of 17 truths." This is now the abstract's first "estimator", so it names
  it.
- **check 10 is now a word limit.** Every rendered case (all 10,848 before the fill, the built one after) must be at
  most 250 words, and characters are reported. Now: 181 to 250 words, 1,248 to 1,660 characters. The 36 cases under
  200 are all stopped campaigns. The ce565239d-era abstract fails the new limit in all 10,848 cases (longest 367
  words). The self-test plants a 260-word case.
- **Checks:**
  - the rater copy PASS (14 and 14 pages);
  - check_round with the fill test PASS, and the self-test PASS;
  - registry, sec4 and pointers PASS;
  - make_values `--check` and `--self-test` PASS;
  - check_restyle against 58fdb8cf2 fails only on the cut 0.133% sentence (the numerals 0.133 and 20, and its
    \SI{}{\percent}).
- The coverage clauses stay pending Joseph. The director runs a fresh reader on the longest and shortest cases.

## The prior-retention fill (FD-PRR; DECISION-20261109-joseph-abstract-length-prr-fill.md item 2, #1010)

- **The readout.** `fd/receipts-prr/read/cluster/readout.json` (#1006), sha256 9238f22bfe29685e…, is pinned in
  make_values' READOUTS as `prr`. Its verdict is COMPLETE, schema prr-readout/1.
- **The mapping.** `prr_verdicts()` maps readout keys only to the declared classes. It uses prr_read.py's own strings
  at db0e801f1: factor_class :300-306, ibu_class :309-312, ibu_k_class :315-318, labels_for :321-333, clears :336-340.
  VERDICTS holds the result, and `make_values --check` now fails if VERDICTS differs from a fresh mapping of the
  pinned readout.
- **The classes**, at A7_gibuu and q3, both flagged truths:
  - PR-1: F1 no effect / increases; F2 increases / increases; F3 no effect / no effect; F4 increases / increases.
  - PR-2a: "IBU retains less" at both, so less. PR-2b: falls at both.
  - The labels: "consistent with an implementation-specific share" and "sensitive to the observable set" at both
    (impl and obs hold; fir, info, stat and unattr do not).
  - PR-3: every level, IBU_K5 included, "does not clear at these truths", so prr-pr3-any and prr-pr3-ibu are not.
  - prr-pr3-levels is "none". It is not printed anywhere.
  - prr-ibu-bar is 0.05, the readout's floor.bars.IBU.
  - prr-abs, from prr_derived: less-less.
  These agree with the director's report of the readout.
- **What prints.**
  - §5.3: the pre-written cases, unchanged as the decision requires. The readings are descriptive and no level is
    adopted (FD-PRR BINDING 1 rulings 2-3).
  - Table 1's row: the PR-1 classes per truth, status Descriptive.
  - The abstract's clause: "binned iterative unfolding of noise-free pseudo-data at five iterations retains less of
    the prior at both".
  - The Supplement prints no prr group.
- **Checks:**
  - the rater copy PASS (15 and 14 pages); the Supplement's rater copy rc 0, 25 pages, 8 of 8 captions;
  - the blind copies print no prr placeholder and no class name, and the manuscript no GONE term;
  - check 11 finds no internal term in the filled values;
  - check_round with the fill test PASS, and the self-test PASS;
  - check 10 over the 678 cases still open (the coverage test's): 183-239 words;
  - make_values `--check` and `--self-test` PASS;
  - registry, sec4 (16/16, 17 passed) and pointers (35/0) PASS;
  - check_restyle against the pre-fill head 74db4ea97 PASS (no .tex source changed).
- **Style, for the director.** §5.3's four label sentences read repetitively as filled ("At the GiBUU hybrid truth,
  the results are consistent with … At the GiBUU hybrid truth, the retained prior is …"). They are kept as
  pre-written.
- The director's five abstract fixes are not in this commit. As ruled, with the run-period clause dropped first, 261
  of the 678 open cases still exceed 250 words. That went to the director for a decision.
- **The independent abstract read (the director, 2026-11-09).** The director ran a fresh Gemini on the longest and
  shortest cases of 74db4ea97's abstract against the full body. Its record is `abstract-read/`: `gemini.txt`, the
  output; `prompt.txt`; `input.txt`, the prompt with the cases and the body. Verdict: the claims are honest, but the
  longest case's coverage sentence is a 76-word run-on with duplicated text. The director's five rulings on it wait
  on one further cut (see the prior-retention fill section above).

### The fill's meaning read and the abstract rulings, applied (the director, 2026-11-09)

The director's fresh reader saw the fill's three pairs (`prr-fill-pairs.tsv`) against the readout summary and the
declaration's reading and label definitions (:290-335). The rulings:
- **§5.3's threshold of 0.05 is correct (dismissed).** The IBU's threshold is max(0.05, 9.03 s_IBU). The readout gives
  s_IBU = 0.0011129, so 9.03 s_IBU = 0.0100 < 0.05 and the threshold is 0.05. The readout's floor.bars.IBU = 0.05 is
  that value.
- **§5.3, PR-3:** the declaration's text, "does not clear at these truths". It now reads "No tested level clears at
  these truths. The IBU at five iterations does not clear at these truths." The clears case reads "Some tested levels,
  …, clear at these truths; …".
- **§5.3, the labels: merged per truth, wording only.**
  - Each truth's labels print in one sentence, "At the GiBUU hybrid truth, ⟨label⟩; ⟨label⟩." Each label keeps its
    exact pre-written words, one \fvcase per label class.
  - The separators come from `\fvlist` and `\fvitem`, new in values_fived16.tex's generated header (make_values
    render()). They print "; " between whichever items print, so any subset of labels reads correctly.
- **Table 1's row:** "GiBUU hybrid, $q_3$ tilt:" now heads the result, so each value's truth is stated. On the
  rendered page (page 5, read as an image) the test name stays in its cell. The reader's "scrambled" row was
  pdftotext's reading order.
- **The abstract's prr clause** names its comparator: "retains less of the prior than the five-observable estimator
  at both". "Noise-free pseudo-data" stays (FD-PRR BINDING 1 ruling 1: route 2 runs on the same noise-free closures).
- **The abstract, on the independent read of 74db4ea97** (`abstract-read/`):
  - "the two-observable unfolding" in the benchmark;
  - the stability median, "by a median of 0.8 and up to 2.6";
  - "A corresponding five-observable test of the procedure's covariance at those tunes";
  - the bands named once, "the detector's neutron and proton interaction bands";
  - one clause when both variants read the same ("… in each variant, with and without …");
  - the IBU-on-data sentence (§5.4's "differs", "depend on the unfolding algorithm");
  - the ensemble clause and the run-period clause dropped, both in the body, as the director chose.
  The scope clause "where the fake-data bias is not flagged" is kept. To keep any 8-word clause from repeating,
  the coverage entries are stated once as per tune ("finds, for its two tunes, A and B …").
- **check 10 gains the repeated-clause check.** No rendered case may repeat a run of 8 words. It is self-tested on a
  planted repeat and a 7-word near-repeat, and it fails 74db4ea97's abstract ("at one tune and an invalid reading
  at", 7 runs). Over the 678 open cases: 195-243 words, 1,384-1,689 characters, no repeat.
- **Checks:**
  - the rater copy PASS (15 and 15 pages);
  - check_round with the fill test PASS, and the self-test PASS;
  - the blind copy prints no class name or GONE term, and no internal term in a free-text value;
  - make_values `--check` PASS; registry, sec4 (16/16, 17 passed) and pointers (35/0) PASS;
  - check_restyle against a1129402e fails only on the changes above: \fvlist/\fvitem, the dropped ensemble keys
    ens1-n and ens1-ntruths, the nested \fvcase, and 0.8.

### The second reads of 3290ae70e, applied (the director, 2026-11-09)

The director's readers: Sonnet on the fill's pairs (`prr-fill-read/out2.txt`, its input `in2.txt`) and Gemini on the
abstract against a fresh build of the body (`abstract-read/gemini2.txt`, `prompt2.txt`, `input2.txt`). The first
round's fill read is in the same record (`prr-fill-read/in.txt`, `out.txt`, the pairs files, `readout-summary.json`,
`decl-readings.txt`). The rulings:
- **The prr clause.** The reader read the noise-freeness as belonging to the IBU analogue. The director proposed "the
  same noise-free pseudo-data", but in the abstract "the same" would point back to the fake-data studies, which are
  graded on Poisson pseudo-experiments as well as noise-free pseudo-data (§3). So the condition now leads the
  comparison instead: "; on noise-free pseudo-data, binned iterative unfolding at five iterations retains less of the
  prior than the five-observable estimator at both". This scopes both methods, with no antecedent.
- **§5.3:** "by more than its threshold (0.05 at these truths)", and likewise in the "same" case, so that 0.05 reads
  as the value and not the definition. The arithmetic above stands.
- **The abstract:**
  - "As a descriptive benchmark" (§4.1, "descriptive, not a blind validation"), not the reader's "tuned";
  - "the sixteen reported cells". "Its" would point back to binned unfolding in that sentence, so it is not used;
  - "a failed test control" (Table 1's caption) for "an invalid reading";
  - "with pseudo-data that omit the model, response and run-period variations";
  - "where the fake-data bias is not flagged" kept, already right after "at those tunes";
  - "We test unbinned OmniFold unfolding of MINERvA open data …" (one word, to stay within 250).
  The readers' coverage rewrites ("failed pre-check", "exploratory study", "pre-specified validation check") are not
  used: the director ruled them inaccurate.
- **Over the 678 open cases:** 196-248 words, 1,400-1,727 characters, no 8-word repeat.
- **The run-period step** is decided at the fill, on the one built case: add "The data also show a run-period step
  present before unfolding (section 4.2)" if it keeps the built abstract at 250 words or fewer. The built abstract
  then gets its own read, and its coverage sentence may be rephrased within the approved content before Joseph signs
  off.
- **Checks:**
  - the rater copy PASS (15 and 15 pages), and each change prints;
  - check_round with the fill test PASS, and the self-test PASS;
  - make_values `--check` PASS; registry, sec4 and pointers PASS;
  - check_restyle against 3290ae70e PASS.

## The presentation round (Joseph, via the director, 2026-11-09): figures

Joseph's five presentation points, routed to the Codex figures lane to save Claude usage: caption length, figure
fonts, Fig. 6's legend, Fig. 5's label overlap, and the tables. I integrate and check; journal-editor reviews the
layout.
- **Fonts.** The baseline is my `figtext.py` (pdfminer: the characters inside each LTFigure of the built
  main_paper.pdf, at print scale). Median printed text was 6.5, 4.8, 5.9, 5.6, 6.2 and 7.8pt for Figs 1-6, against
  9.0pt captions.
- **Figs 3-6 (merged as cbe533a66; its presentation/REPORT.md).** On my own measure of the built paper after the
  merge, the medians are 8.3, 8.3, 8.3 and 8.6pt, with axis labels 9.3pt.
  - The lane asserts the plotted numbers equal to frozen copies: Fig. 3's arrays exactly, and Figs 4-6's
    numbers.json byte-identical. Both producers rerun here with no change to any committed asset.
  - Fig. 3 is a new stacked-panel asset, `figures/methods_short/m3_fig2_deformation.pdf`, included at \textwidth.
    The old `figures/paper_fig_deformation.pdf` is no longer printed by the paper and is left in place.
  - Fig. 6's legend reads "y = x". Fig. 5's median label is clear of the line.
  - I read the rendered pages at print size and found no overlaps. Captions are unchanged by this commit; "(a)/(b)"
    still fits Fig. 3, and "left/right panel" Fig. 4.
- **Figs 1-2:** held for their operands (the director). director-helper-2 has since fetched and sha-verified them;
  Codex regenerates both in a separate commit.
- **Checks:**
  - the rater copy PASS (16 and 15 pages; a first attempt failed in biber's binary extraction, an environment race,
    and the retry passed);
  - check_round with the fill test (check 9 included) PASS, and the self-test PASS;
  - make_values `--check` PASS; registry, sec4 and pointers PASS;
  - check_restyle against d1d60e74f PASS; no Overfull \hbox.
- **Captions (the lane's d53af941a, merged as 86ac751e3).** The six captions are shortened.
  - TeXcount, before -> after: Fig 1 87->52, Fig 2 46->35, Fig 3 163->64, Fig 4 167->51, Fig 5 152->65, Fig 6
    152->65. My prose-token count on paper_body: 96->61, 54->36, 169->69, 185->61, 158->67, 158->70.
  - Each dropped sentence's disposition is in `figures/methods_short/presentation/captions/REPORT.md` and
    `pairs.json`.
  - My check of the moved clauses in the merged source; each prints exactly once:
    - Fig 1: "so their overlap is not a compatibility test" (§4).
    - Fig 3: "Neither panel of figure …"; "… were not used while the estimator was chosen".
    - Fig 4: the z and N definition, reworded in §5.2; "The noise-free closure uses its single residual and $N=0$";
      "The bias is identical in both panels; only the covariance differs".
    - Fig 5: the 109 J / 42 EW / two totals population and the edge-safe definition (§6.1); "Points are different
      quantities, not repeated experiments" (in the caption).
    - Fig 6, in §7: "not a measured bias of the data result"; "The correlation supplies no per-cell bias bound";
      "The points of figure 6 are cells, not independent repeated experiments".
  - check_restyle against c8757e9f2 fails only where a caption cut is expected to: one tab:fd16 ref left Fig 4's
    caption with its p-value flag sentence, which §5.2's protected paragraph states; five \ref{fig:…} were added in
    the citing text; \chi and one \Eavail went with the dropped text.
  - The rater copy, check_round with the fill test, make_values `--check`, registry, sec4 and pointers pass.
  - My export of every changed sentence (55 rows) and the lane's pairs.json went to the director's meaning read and
    to journal-editor. Not accepted until they report.
- **Tables:** held. be76b8310 meets journal-editor's five constraints, but their review found five zero-word
  defects, and the lane is making a repair pass. c8a29cdbc is only Table 1's tabcolsep overflow fix.
- **Figs 1-2: LaTeX-only resize (the director, 2026-11-10).** The fetched operands do not reproduce the printed
  figures (the lane's finding; REPORT.md, before submission), so the regeneration stopped and the committed PDFs
  stay. Fig. 1 is now at \textwidth (median printed text 6.5 -> 7.6pt) and Fig. 2 at \columnwidth (4.8 -> 5.9pt). The
  rater copy passes (15 and 15 pages); no Overfull; check_round and check_restyle pass.
- **The caption meaning read.** The director's reader on pairs.tsv (`caption-read/out-captions.txt`; the pairs are
  `caption-read/pairs.tsv`) agrees with journal-editor's and adds five flags (M010, M011, M018, M026, M032 and
  M035; M021, M024 and M036 overlap the editor's). journal-editor found four clauses lost outright; my spot check
  had missed two of them (Fig. 4's outline note and the q3 tilt's p-value flag). All of these went to the lane for a
  caption repair commit. The captions are not accepted until the rerun read.

## V-HALF filled, and the tables (the director; DECISION-20261110-joseph-paper-asap-vhalf-diagnostic.md, #1024)

- **V-HALF is a diagnostic on R00-R15, filled from its pinned readout.** The readout is
  `valid-region-20261107/v-half/receipts/read/readout.json` (#1009), sha256 e74233901038bd71…, pinned in READOUTS as
  `vhalf`; main was merged at 308eb66dc to bring it in.
  - `vhalf_verdicts()` maps the readout's per-cell classes and counts only: 5 valid, 9 not valid (R03, R05, R07, R08,
    R10, R11, R12, R13, R15), 0 not assessed, 2 unresolved (noise). It refuses an unknown class, a cell count other
    than 16, or a "no d" cell.
  - make_values `--check` refuses any drift from the readout.
  - The decision record resolves item 5 of the bias-half decision (no rebinning) for this paper.
- **What prints.** §5.4: "Of the 16 cells, 5 are valid under it, 9 are not (R03, …, R15), 0 are not assessed and 2
  are unresolved." <!-- absence-ok: quotes the printed V-HALF class count ("not assessed" is a declared class of the rule), not a claim that a study does not exist --> Table 1: "5 of 16 cells valid, 9 not valid, 2 unresolved", status Descriptive.
  - The director's meaning read (`vhalffill/out.txt`) found V1 clean. For V2 it asked for the 2 unresolved cells;
    they are added, in the paper's own term "unresolved".
  - The reader's misplaced "departure from the prior" was pdftotext's reading order. The rendered row, read as an
    image, is correct.
- **The tables** are the lane's be76b8310 and 06a3438f1, merged; journal-editor reviewed them as typeset. I added
  their χ²/p gap fix: r@{\hspace{5pt}}l in Table 2's three groups. At 6pt the table was 1.76pt overfull; at 5pt there
  is no Overfull.
- **check_round's numeral scan** counted table column widths and \tabcolsep as printed numerals (2.25, 3.0, 5.0,
  9.0), because the new tables use tabular* and a TeX length. It now skips \begin{tabular*} lines and any number
  followed by a TeX length unit. The self-test plants both forms and confirms that a printed numeral is still caught.
- **Checks:**
  - the rater copy PASS (16 and 15 pages); no Overfull;
  - check_round with the fill test PASS, and the self-test PASS;
  - the blind copy prints no class name or GONE term, and no internal term in a free-text value;
  - make_values `--check` PASS; registry, sec4 and pointers PASS;
  - check_restyle against cc3e56c92 fails only on the ruled additions: the vhalf-n-unresolved key, and the tables'
    layout macros.
- **Correction:** the "caption meaning read" bullet above says the director's reader "adds five flags"; it lists six
  that do not overlap journal-editor's (M010, M011, M018, M026, M032, M035).

## The note's round-2 blind reads, mapped onto the Supplement (the director, 2026-11-10)

The note's round-2 reads (#1023: `secondary-results/note-round2-blind-reads-20261110/gpt.txt` and `gemini.txt`) found
errors in the note. The Supplement copies 58 paragraphs from 16 note sections. Each GPT §3 accuracy and §6 support item,
and each Gemini accuracy and support item, was searched in the Supplement by its quoted phrases and topic terms, and
each hit was read against its record. The mapping table went to the director, who approved the three fixes:
- **GPT §3.16 (S, line ~291):** C_model is "a fractional covariance; in cross-section units it is diag(x) C_model
  diag(x), with x the cell-integrated cross sections". The record is cmodel_5d.json's `form`: "C_model = sum_k s_k
  s_k^T … fractional. C_abs = diag(x) C_model diag(x)".
- **GPT §3.26 (S, ~266):** "(|t|>3.6, a fixed threshold at about the two-sided 5% level for a normal reference,
  Bonferroni-corrected over the 153)". The record is nd-unfolding/s5n_analyze_dev.py:35, `T_CRIT = 3.6`, "two-sided
  0.05/153 Bonferroni"; the normal value is about 3.59.
- **GPT §6.4 (S, ~238):** "The simulation prior differs from the measured distributions mainly in normalization: the
  data exceed it by about 12%, and the data/MC ratio rises with p_T from 0.88 to about 1.2 (Ref. [note], Sec.
  controlplots)". This replaces "already describes the measured shapes well … the data mainly require a normalization
  correction". The record is sec_experiment.tex controlplots.
- Each fixed paragraph's source comment now says "adapted 2026-11-10, one content fix" (two had said verbatim) or
  "fixed 2026-11-10", naming the item.
- **Not applied, already correct in the Supplement:** GPT §3.4, 3.5, 3.7, 3.8, 3.11, 6.12, 6.13, 6.14; Gemini §3.7,
  3.8, 3.9, 6.3, 6.5. Every other item has no counterpart in the Supplement. The director relays the three matching
  fixes to the note lane.
- **One printed sentence opens the Supplement:** "Several sections reproduce or adapt text from the companion analysis
  note [note]." I had proposed adding "each such passage gives its source section"; the director dropped that clause,
  because the source comments don't print and the clause would be false.
- **Checks:**
  - check_restyle against e543ce1e4 fails only on the additions (0.88, one \cite, the matrix macros), and the 23 #981
    quotes count as before;
  - the Supplement's rater copy rc 0, 25 pages, 8 of 8 captions, and each change prints;
  - check_supp_pointers: 35 pointers, 0 failures; check_round PASS.
