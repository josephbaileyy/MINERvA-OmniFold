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

### The Supplement-note sync check (the director, 2026-11-10)

- **The check.** `check_supp_sync.py` (check_round check 12; report only) pairs each of the 58 note-copied Supplement
  paragraphs with its note source.
  - It runs three-way, against the Supplement's seed commit 9680db24e. Each difference is attributed to the side that
    moved: same, seed-adapted, explained (a restyled/adapted/fixed comment), UNEXPLAINED (an edit under a comment
    that still says verbatim), NOTE-CHANGED (the note's paragraph changed since the seed), or synced (the Supplement
    has followed the note's change).
  - Paragraphs are counted from 0. The pair is the best match among n-2..n+2, and cross-references are reduced to one
    token on both sides.
- **First run, against the worktree's note:** 24 UNEXPLAINED. These were stale "verbatim" labels over wording edits:
  - 17 were edits after 531fefe42, which the meaning check of 2026-11-10 read;
  - 7 were edits of rounds 5-6, before 531fefe42 (supp lines 82, 123, 188, 201, 288, 427, 442), which no reader has
    checked. They are the estimator rename to "five-observable", the acronym and date edits, and two pre-read fixes.
    They went to the director's meaning read (`sync-pairs.tsv`, Y01-Y07).
  - All 24 comments now say "adapted since seeding" and name which read covers them.
- **Against #952's head (06ce7b5e0):** two note paragraphs had changed since the seed, both narrowings, and the
  Supplement now follows them:
  - "reduces … bias … at least fifteen-fold" -> "by about an order of magnitude". The quoted ranges, 3.5-4.1% to
    0.11-0.24%, give a ratio of 14.6 at worst.
  - "reproduces an independently published binned measurement" -> "reproduces the integrated cross section of an
    independently published binned measurement", which matches the paper's benchmark finding.
  These are sync-pairs Y08-Y09.
- **Now:** against the worktree, explained 43, same 14, seed-adapted 1; against 06ce7b5e0, explained 41, same 14,
  seed-adapted 1, synced 2. Nothing is unexplained. Rerun with `check_round.py . --note-rev <the note's head>` when
  the note's round 3 lands.
- **Checks:** check_restyle against 99575b29e PASS (the 23 #981 quotes, the 35 pointers; no paragraph left under a
  stale verbatim label); the Supplement's rater copy rc 0, 25 pages; registry PASS; check_round PASS, and its
  self-test PASS.
- **The meaning read of the sync pairs** (the director, 2026-11-10; `sync-read/out-sync.txt`, pairs
  `sync-read/sync-pairs.tsv`) flagged 3 of 9, all LESS and all intended:
  - Y03: the ISO date was removed by the round-6 fix (the rule against printing dates);
  - Y08: "at least fifteen-fold" -> "by about an order of magnitude", a correction (14.6 at worst);
  - Y09: the narrowing to the integrated cross section, which matches the paper's benchmark.
  No MORE or DIFF flags. The 7 pre-531fefe42 edits (Y01-Y07) are thereby read, and their source comments now say
  so. d61bb9ad1 is accepted.

## The interim referee round (#1025), group A, batch 1 (the director, 2026-11-10)

GPT gave 5/10 and Gemini 4/10, both major revision (`secondary-results/referee-methods-interim-20261110/`). The director
put the scope to Joseph and released group A: points both readers make, within the existing records, with no new
claim. Batch 1 takes the items that don't touch the paragraphs Codex's caption repair edits:
- **A4 (§1):** the orphan paragraph "Interval coverage has not been validated. …" is merged into the paragraph above. <!-- absence-ok: quotes the paper's existing scoping sentence, unchanged -->
- **A3 (§3.1):** the two-estimator paragraph is split into (i) common settings, how the two estimators differ, and
  "not combined"; (ii) the two estimators and their uses. "This estimator removes most of the bias …" moves to the
  background paragraph as "With the refinement classifier, the negative-weight treatment removes most of the bias …",
  the attribution of S4 and the note's sec:val-negweight.
- **A3 (§3.2):** split into the ordinary components, C_model and C_resp, and the run-period block. No word changes.
- **A6 (§2):** the section opens with the signal phase space, from S1 and ref. MINERvA:2021owq. The sixteen-cell
  paragraph moves before the diagnostic grids and defines the support rule itself.
  - A compact cell table (tab:cells) gives each cell's box, purity and diagonal fraction. The director approved
    purity and diagonal fraction only, with no efficiency, since no committed record defines one, and one name for
    the diagonal fraction, as defined in §2.
  - Its values are new make_values keys (cell-purity-Rxx, cell-diag-Rxx), two decimals, from the pinned
    h2_definition.json reporting_cells; the record calls the diagonal fraction "stability". The boxes reuse Table
    S2's keys.
  - The new table prints as Table 1, so the test map and the fake-data table become Tables 2 and 3; every reference
    is a \ref.
  - 4.5 (p_T < 4.5 GeV/c) is in NEW_NUMERALS with its source.
- **A8 (Table 1, the test map):** its source already follows the test definitions. The key is shortened by moving the
  status glossary, word for word, to a note under the table; the caption is now 39 words.
- **A10:** "best-determined directions" -> "the 73 largest-eigenvalue directions" (three uses and Table 1's row), using
  the paper's definition λ/λmax > 1e-4. The note's sec_results "best-measured" (:128, :134) is queued for the note
  lane by the director.
- **A11 (§6.3):** the LL5D null (nd-unfolding/fd_1b_null.py:111-122) defines the joint region one-sided, χ² ≤
  F⁻¹_χ²(ndf)(P0), so adding positive-semidefinite terms can only lower χ², and the carry-over holds whenever ndf is
  equal. The sentence now names the region: "the joint reading, the fraction with χ² below a cut fixed in advance,
  carries over only if both matrices have 16 degrees of freedom". It stays pending Joseph.
- **Checks:**
  - the rater copy PASS (16 and 16 pages); no Overfull;
  - check_round with the fill test PASS; make_values --check PASS (3843 values);
  - registry, sec4 (16/16, 17 passed) and pointers (37/0) PASS;
  - check_restyle against 7de6c6031 fails only on the additions (the cell table's keys, label and refs, the S1
    pointer and its \cite, 4.5).
- The registry: ALIASES rows 39 and 48 and ATTRIBUTION row 17 cited paper_body.tex:68, which the §3.1 split changed; re-cited by
  hand to :103 (the five-observable estimator, its joint-test use) and :100 (the refinement capacity).
- The pairs (`interim/batch1-pairs/pairs.tsv`) go to the director's meaning read.

### Batch 1's meaning read (the director, 2026-11-10)

`interim-b1-read/out-b1.txt` over `interim-b1-read/pairs.tsv` (40 rows): 3 flags (M026, M037, M038), all the intended A10
relabelling. The paper's selection, λ/λmax > 1e-4, keeps the largest eigenvalues of the covariance, so "best-determined"
was the mislabel. The director accepted bd08582ee, the hand re-cites of ALIASES and ATTRIBUTION included.

## The caption repair's integration (Codex 3045fcbb5, 5406ceee7, 7815eaa73; the director, 2026-11-10)

- Merged at a0d69f5b6. The one conflict is §4's benchmark paragraph: Codex's inserted sentence ("The two bands in
  figure~\ref{fig:validation} are correlated, …") is kept with batch 1's A10 wording.
- Codex's later 1a3b175ba ("caption-first") is not integrated. Against 7815eaa73 it differs only in Fig 3's caption,
  which drops "not the reported estimator" ahead of A1, and it lacks 5406ceee7's panel compaction. The director accepted
  the 3045/5406/7815 set, and journal-editor asked that the four words stay until panel (a) moves.
- The director's read of the repair (`caption-read/out-caps2.txt`, 4 flags) and journal-editor's review gave eight fixes:
  - journal-editor 1: the stability paragraph of §6.1 is back to its text before the repair (equal at 5bfb8185c,
    d53af941a and bd08582ee). The 153 quantities and the perturbations return to Fig 5's caption.
  - journal-editor 2: Fig 3's lead reads "per (E_avail,W) cell, at the changed truth, with backgrounds".
  - journal-editor 3: Fig 4 uses \fvval{f0b-all-truths} (prints 12).
  - journal-editor 4: Fig 3(a) reads "(refinement 100 trees, 8 leaves; the configuration of the generator-sized-change
    study)".
  - director 1: Fig 2 reads "C the published covariance".
  - director 2: Fig 4's numbers. The producer (make_figures.py bias_figure) prints signed z, to two decimals, at each row's
    largest-|z| cell, only in rows with an outline. The caption reads "in each row with an outline, z of the cell with
    the largest |z|, to two decimals".
  - director 3: Fig 5's denominator is "the study's data-bootstrap statistical standard deviation". It is the s5e
    candidate-R assessment's 100 data replicas (make_figures.py: boot_b1..b100; assess_receipt data_boot_replicas = 100).
    - §6.1's 0.37% is a different estimate: the median J-cell σ_boot of the s5p paired study
      (s5p/stage2/stage2_receipt.json study_N/N1_data: n_replicas 50, J median_sigma_boot_pct 0.3677; its b1 and b2
      equal s5e boot_b1 and b2).
    - The caption says so: "the 0.37% quoted in that section is a 50-replica median over joint cells".
  - director 4: the markers are drawn at the exact values and labelled with .1f, the text's 0.8 and 2.6, so the
    caption reads "Markers: the observed median and largest shift, labelled at the text's precision".
- captions-short.tex is regenerated from paper_body's six figure captions (nothing reads it; it is Codex's copy).
- Checks:
  - the rater copy PASS; no Overfull;
  - check_round with the fill test PASS; make_values --check PASS (3843);
  - registry, sec4 (16/16, 17 passed) and pointers (37/0) PASS;
  - check_restyle against a0d69f5b6 fails only on the intended changes (f0b-all-truths, the \ref moved into the
    caption, \SI{0.37}).
- The typeset captions of Figs 2–5 were read back from the PDF.

## The interim referee round (#1025), group A, batch 2 (the director, 2026-11-10)

- **A1 (Fig 3) and §5.1**, under the director's ruling on limitation-resolver's row-2 finding:
  - (e) itself gives 73.86% in EW29 at the GiBUU-to-GENIE change (assess_receipt.json points.eavail_gibuu;
    OUTCOME-20260926-s5e-oi192:68,85). The lower-capacity variant gives 74.07% in the same cell (B0_reference_s5n.eavail).
  - The paper's Fig 3 shows the reported estimator only (Codex 12dbe081c, merged at c03d5554c; legend "GENIE + MEC",
    faf7c35fc, merged at 1c46477d5).
  - Panel (a) is the new Supplement figure fig:supp-lowcap in S4, configuration (d), and keeps "not the reported
    estimator".
  - §5.1 leads with (e): "the five-observable estimator deviate[s] … by several percent in the largest cells and by up to
    74 % at high W …; a lower-capacity variant, not the reported estimator, with a 100-tree, 8-leaf refinement, gives
    the same 74 % in that cell (supplementary material, figure S1)".
  - "Several percent in the largest cells" holds for (e) by fig_m3_deformation.py's own test (EW7, -10 < r < -2): EW7 is
    -6.79 ± 0.07% for (e) and -6.66% for the variant. The two differ by at most 0.84 points in any of the 42 cells.
  - Table 2's generator-sized row reads "at the GiBUU-to-GENIE change: up to 74 %", with no variant attribution.
  - The Fig 3 caption follows journal-editor's read of the split (items 1, 2 and 5):
    - the injected changes are not drawn;
    - "Sixteen-cell results at these truths: table 3";
    - the standard errors are smaller than the markers: SE ≤ 0.22% for (e) (W1–W3) and ≤ 0.12% for the variant, from
      the receipts, against 2.6–3.0 pt markers.
  - New keys (make_values, the new READOUTS "s5e", assess_receipt.json 84266e30):
    - s5e-gibuu-ewmax and s5e-gibuu-ewmax-lowcap (74 and 74), with both argmaxes asserted EW29 and EW7's sign test;
    - s5e-round-median and s5e-round-max (0.8 and 2.6, A3.data_rounding_probe_over_data_sigma 0.783 and 2.584), used in
      §6.1's observation sentence and Table 2's rounding row. The third use, B1's row 7, comes with group B.
    - The "2.6" inside the protected B0 sentences stays a literal: check_restyle protects that span.
  - check_sec4_receipts:
    - text() now resolves \fvval{key} from values_fived16.tex;
    - a new row checks (e)'s printed 74 against assess_receipt (73.86);
    - VL151's row now reads the variant's clause ("gives the same … in that cell", 74.07).
  - check_supp_pointers gains \sfig (figure environments counted in order), with a self-test. There are 37 pointers:
    the caption's S4 pointer went with panel (a), and §5.1 and the figure's text add one \sfig.
- **A2:** Fig 6 (prior response) and "Two findings indicate that the unfolded result retains part of its prior …" move
  from §6.1 and §7 to the head of §5.3, verbatim.
- **A3 §5.3:**
  - The design paragraph keeps sentences 1–6 (the study, ρ and its terms, the settings, the IBU). The results follow.
  - Sentences 7, 11, 13, 14 and 15 (the classification, the IBU's margin, "clears", the labels, the scope) follow the
    results.
  - Sentences 8, 9, 10 and 12 (the threshold, the Student-t factor, the IBU's own rule, the undefined case) move to S9
    verbatim, as \paragraph{The prior-retention study's thresholds} (label supp:prr). Sentence 7 is repeated there with
    an adapted opening.
  - The two closing sentences ("No tested level clears at these truths. The IBU at five iterations does not clear at
    these truths.") are one sentence in every case of prr-pr3-any × prr-pr3-ibu. It renders "Neither a tested level
    nor the IBU at five iterations clears at these truths."
- **A3 §6.1:**
  - observation (the instability, the 153-quantity shifts, the requirement; Fig 5);
  - the B0 sentences (protected, contiguous): reproducibility, scale and inclusion in the statistical block;
  - the mechanism (RS1, one line, unchanged);
  - mitigation: the ensemble average, then the probe of cross-fitting and tree regularizations, moved verbatim from
    the first paragraph.
- **A4 §6.2:** the two one-sentence paragraphs (the earlier estimator's miscoverage; the stopped first test) are
  merged.
- **A5 §4.1:** the paragraph on how the learner and the background treatment were chosen ("chosen after three had been
  compared …", "adopted it in the analysis only after that comparison was known") moves verbatim before the
  covariance-weighted distance.
- **A7 §7:**
  - The first paragraph ends with the one statement of applicability ("Until the coverage, … the sixteen-cell output
    is an illustration of the method; its limitations are listed in section 7.1"). Its former last sentence
    ("has not achieved validated interval coverage, numerical stability or recovery …") goes to the list.
  - The limitations list is complete: coverage (item 1, unchanged); truth recovery and the retained prior;
    instability (with ENS1's scope: it meets the requirement on the pseudo-data used to test stability, is worse at
    one truth and is not adopted); the run-period inconsistency; tests that change only the truth and use the
    simulation's detector response (§3.3's statement); low diagonal fractions (unchanged).
- **Checks:**
  - the rater copy PASS (15 and 15 pages); the paper has no Overfull. The Supplement's one Overfull (3.2 pt, Table
    S6's right table) predates this batch; Codex's 4035c769f fixes it.
  - check_round with the fill test PASS; make_values --check PASS (3847 values);
  - registry, sec4 (17/17, 17 passed) and pointers (37/0) PASS;
  - check_restyle against 8320315bd fails only on the moves and additions above.
- Meaning read: `interim-b2-read/pairs-read.tsv` (37 rows) and `moved-verbatim.tsv` (58 rows, identical base-only and
  current-only sentences).

### Batch 2's meaning read and journal-editor's review (2026-11-10)

- The director's read ran a fresh Sonnet over `interim-b2-read/pairs-read.tsv` (7768d47c): 5 flags.
  - The director checked `moved-verbatim.tsv` (095b9d0d) mechanically: 29 base-only and 29 current-only sentences,
    identical multisets.
  - M002 and M023 (Table 2's row; §5.1's lead with (e)'s 74%): intended and sourced; accepted.
  - M019 and M089 ("smaller than the markers"): a perceptual claim. make_figures/fig_m3_deformation.py does not compute
    the marker radius in data units, so the captions now give the bound from keys: "Standard errors of the mean: at
    most 0.22 %" (s5e-shapes-semax: (e), W1–W3, 42 (E_avail,W) cells) and "at most 0.12 %" (s5n-gibuu-semax: the
    variant, s5n dev_receipt C4; new READOUTS "s5ndev", 1ef4096c).
  - M086 (the detector-response item) was broader than its source. It is rewritten clause by clause from the paper:
    - "The simulated detector response is not varied in the closure, deformation and fake-data tests": §3.3 "keeps the
      detector response at fixed truth"; §5.2 "The simulated detector response is not varied in these tests".
    - "beyond the descriptive closures with a shifted recoil response": §5.2, the same sentence.
    - "the coverage tests vary it only through the detector-systematic uncertainties they draw": §6.2 "the
      uncertainties propagated linearly as in the covariance's construction"; §6.3 "each drawn uncertainty group's
      pseudo-data built as its covariance block is built", with one variant adding the GEANT4 neutron and proton bands.
    - "All use simulated pseudo-data, so none tests the detector model against data": §3.3 "the simulated events used
      as pseudo-data"; "Every study uses the analysis simulation's detector response".
  - The B0 literal 2.6 stays typed. check_round gains LITERAL_KEYS and check_literal_keys, which fail if the protected
    "the quoted 2.6 statistical standard deviations" differs from \fvval{s5e-round-max}. Self-tested.
- journal-editor's review of 8ff849bf6, items 1–7:
  1. §5.1's first sentence no longer cites Fig 3, which shows no injected change. Fig 3 is cited at the 16–31 %
     sentence, with "does not show the sixteen-cell result …" and "The three shape changes it shows were not used …"
     after it.
  2. "These deviations occur with or without background" is now scoped to the variant ("The lower-capacity variant's
     deviations …, its residual"). The background-free runs are s5n's (the note's sec_5d.tex:61, "Signal-only
     experiments with the same seeds reproduce both results"), and s5e's receipt has no background-free run for (e).
     This narrows the director's "keep the background clause as is"; flagged to the director.
  3. The detector-response item: as M086 above.
  4. "(20 pseudo-experiments)" for (e)'s 74 %, with eavail_gibuu.n == 20 and the variant's 60 asserted in make_values.
     "For the reported estimator at the same truth, we report the result on the sixteen cells: the bias satisfies …"
     becomes "On the sixteen reported cells, the same truth's bias satisfies …".
  5. §5.3: "A tested level clears a flagged truth if …" moves ahead of the outcome cases.
  6. §6.1's order (probe after the ensemble, two "retained" conclusions back to back) is not changed. The director's
     A3 asks for "the ensemble right after the mechanism"; the question goes to the director.
  7. Fig S1's caption names "the companion note's generator-sized-change study, Ref. [note], Sec. N-sec:val-negweight".
- The c8 table repair (Codex cf925029d) is not merged: its paper_body.tex is byte-identical to 06a3438f1's (sha256
  7f1d6ff757c2), which #977 already has.
- Table S6 (Codex 4035c769f) is merged at dd4d7d781. The Supplement's word multiset is unchanged, apart from
  extraction effects ("Pseudo-experiment" without line-break hyphenation; "χ²₁₆" extracted as one token). Its Overfull
  is gone (0).
- Checks: the rater copy PASS; no Overfull in the paper or the Supplement; check_round with the fill test PASS (and
  its self-test); make_values --check PASS (3849); registry, sec4 (17/17) and pointers (37) PASS.
- Re-read: `interim-b2-read/fix-pairs-read.tsv` (12 rows, 26bec5eb) against dd4d7d781.

### The re-read of ef7ac93ad and the director's rulings (2026-11-10)

- The director's every-row read of `interim-b2-read/fix-pairs-read.tsv` (26bec5eb): all accepted except M007. After
  the variant clause, "the same truth's bias" could read as the variant's. Restored: "On the sixteen reported cells, the
  reported estimator's bias at the same truth satisfies both criteria …" (paper_body.tex:239).
- JE 2: the director keeps the scoped background sentence (the variant's; only s5n has background-free runs).
- JE 6: applied. §6.1 runs observation → B0 sentences (contiguous) → mechanism (RS1, verbatim) → the cross-fitting and
  regularization probe → the ensemble average. That is the order they ran in; the two "retained" conclusions are no
  longer adjacent.
- Table S6 (journal-editor's read of dd4d7d781): the relations in three TikZ nodes set with wide gaps. A minimal test
  (scratchpad s6test/t2.tex) shows that align=center with a text width stretches math glue, and \mbox restores normal
  spacing. The three relations are now in \mbox; the rendered page was checked.
- Checks: the rater copy PASS; no Overfull in either build; check_round with the fill test, sec4 (17/17) and registry
  PASS; check_restyle against ef7ac93ad fails only on the three \mbox.

## Group B (#1025; Joseph approved the director's plan, 2026-11-10)

### B5: no prediction corrected with a sample that failed its own check (director-helper-3's item; the director's rulings (a)–(e))

- **Swept by claim.** The keys and sentences whose value uses a CH-corrected NuWro or GiBUU prediction are all in S10
  (Supplement), except V-PRIOR (below). The paper, the abstract and tab:outcomes print no generator-comparison key.
- **Removed:**
  - Table S7's CH-corrected NuWro and GiBUU rows and their footnotes a and b. These are #981 quotes Q11–Q13;
    check_restyle reports them, and the re-pin is limitation-resolver's, by the director's ruling.
  - S10's correction sentence; "On carbon, NuWro gives …"; "For GiBUU, the effect of the CH correction …"; "A native CH
    generation of NuWro agrees with the combination …".
  - tab:cmodel16's "ratios from CH" column and its NuWro and GiBUU rows. Nominal C_model reads the carbon ratios:
    make_values e2_values ("The reported covariance keeps C_model on carbon (x1)"); pv-ladder config.json:58-65, the C12
    products nuwro_cv_xsec5d_full.npz and gibuu_cv_xsec5d_fluxfix.npz.
- **Kept, labelled carbon only:**
  - Table S7's NuWro and GiBUU rows on carbon, in the analysis definitions, both arms. Source: defs.json (544f4f43)
    generators.{nuwro,gibuu}.carbon.analysis_definitions.chi2.{reported,without_C_PL5D}.
  - New keys label-{nuwro,gibuu}-carbon and g-{nuwro,gibuu}-carbon-*-ndf.
- **The reason, as each generator's record states it** (S10 :602):
  - NuWro: "in NuWro's free-proton sample, the events lost to generator aborts in the supplement generated at neutrino
    energies of 50–100 GeV were not shown to be negligible". The note's sec_joint.tex sec:joint5d-ch: the
    supplement's 95% upper bound of 1.8e-4 exceeds the 1e-4 level set for it, "flagged rather than assumed negligible".
  - GiBUU: "GiBUU's free-proton sample failed its sampling-closure check" (the same section: "the sampling-closure
    check failed on the hydrogen sample").
- **Ranges re-keyed over the remaining predictions**, each from a committed readout's per-prediction values. No range
  is dropped; no new compute.
  - gdef-dmax → gdef-b5-dmax: defs.json generators[genie_cv, genie_mec].CH.delta_over_sigma and [nuwro, gibuu].carbon
    .delta_over_sigma. The value is unchanged, 0.063 (bound 0.07).
  - pl-chi2fall-* → pl-chi2fall-b5-*: Table IV's chi2 for GENIE CV, GENIE + MEC and Tune v1 (both arms), plus NuWro and
    GiBUU carbon. Total 3.6–30.6 % (was 3.6–29.3); shape-only 7.4–39.7 % (was 7.4–40.4).
  - sens-flux-fall-*, sens-detlat-fall-max, sens-joint-chi2-min → sens-b5-*: the sens2 and fup records with
    prediction ≠ nuwro, 16 cells. 23–38 %, ≤ 18 %, ≥ 41: unchanged. The readouts hold no carbon-only NuWro record, so
    the sentence names "the GENIE CV, GENIE + MEC and Tune v1 predictions".
  - fb-edge-max, fb-offset-relmax → fb-b5-*: fboot bands for genie_cv, genie_mec, mnvtune_v1. 3.8 % and 0.4 %:
    unchanged.
- **fig:ratio16:** Codex regenerates it through the printed figure's producer (nd-unfolding/fd_gencmp_ea2.py, a24d7c421)
  with NuWro and GiBUU on carbon only, from defs.json's per-cell carbon g_over_f_minus_1, if f and σ/f match the printed
  figure. Otherwise the two curves are removed. PENDING: this commit is not pushed until the figure and its caption land.
- **V-PRIOR (S11 rule 2; the paper's §5.4 "14 of the 16 cells valid and 12 under both")** uses the CH-corrected
  predictions. valid-region-20261107/DECLARATION.md:120 names I3 as fd_g_readout.json, "with NuWro and GiBUU corrected
  to CH"; :137 gives the generators. Not changed. Raised with the director for a ruling.
- check 12 (SUPP-SYNC): S10's paragraphs are "Moved from the paper", not note-copied, so the sync check pairs none of
  them. The report is unchanged (58 note-copied paragraphs: explained 43, same 14, seed-adapted 1). The intended
  divergence from the note, which keeps the CH-corrected comparison, is recorded here.

### B6, B4a, B4b, B3a, B3b, B2, B1 (limitation-resolver's drafts in its scratchpad bdraft/, the director's group B rulings)

- **Symbols** (the director's ruling 2: ρ is only the retained fraction; one meaning each across both documents):
  - ρ: the retained fraction (paper §5.3; S9 supp:prr and the B4b paragraph and table).
  - κ: the IBU-to-2D distance ratio. Paper §4.1 (was r) and S8 (was ρ); per replica κ_b (B6).
  - φ₁: the weighted density of class 1 in S4's background derivation (was ρ₁; 5 uses).
  - η: V-PRIOR's spread ratio S_b/S_g in S11 (was ρ).
  - ω: the synthetic q3 tilt's event weight (B3a; the draft's r). ω_c = k t_c and ω_T: a held-out tune's reweighting
    (B3b, B2; the draft's r_c, r_T).
  - t_c: a tune's gated ratio to the GENIE CV reference (B3b; the draft's ρ_c).
  - r is not given a new meaning. Its existing uses (S4's r = p/(1-p); S7's residual r = F - μ_G; S9's r_b) are not
    touched.
- **Every number is a build-checked key** (make_values groupb_values) except where noted. New pins: c2c1 (0ee21301),
  refg1 (4db170d3), refg1bars (ba4b6985), s5ntruth (14ee2800), f1config (b0c7a0d9), cov2dar23 (fe5263e9), cov2dg18
  (84976694), s5econtract (f6d3791c). Text pins: s5cpseudo (d81d4f46), f1prep (f31a996a), cov2ddecl (0328c916),
  ll5ddecl (6748d418), nullcode (ec1402db), stabdecl (6c91c0cc), fd1bdecl (50d9e883).
  - Declaration and code numbers are read by anchored patterns that must match exactly once.
  - The paper's own sentences that print the same numbers now use the same keys: §4.1 (T, q95, max, n, κ and its
    interval, T₁, n₁, 4 %, q95₁), §5.1 and tab:outcomes (2.7, 0.09, 40, 16–31) and §5.4 (194.4, 28.12, 39.04).
  - Not keyed:
    - B1 row 1's 187 universes, 300 replicas, three period groups and five seed settings: the paper's own §3.2
      literals, with no committed record of the counts found (round 5 printed them without a source comment). Flagged
      to the director.
    - Structural counts printed as literals elsewhere (16 cells, 205 bins, 0.5 in the V-HALF rule).
- **Placement:**
  - B6 follows S8's κ definition.
  - B4a (tab:ibu16-cells) follows the sixteen-cell comparison.
  - B4b (supp:prr's results paragraph and tab:prr-rho) follows S9's thresholds.
  - B3a (supp:q3tilt) and B3b (supp:tunes, tab:tune-gate) follow S9's held-out-tunes paragraph.
  - B2 (supp:covdesign, tab:cov-design) precedes the second test's paragraph. Its Truths row points to supp:tunes.
  - B1 opens S9. It is split into four [p] tables (tests 1–5 and 6–10, each table), because each table exceeded a page
    and the rater copy counts table environments.
- **Rulings applied:**
  - No Δ in cross-section or σ units (B4a as drafted).
  - No "CV-positive": the region is "the cells where the central value and both predictions are positive".
  - B1 row 9's result is the paper's §6.2 sentence. B1 row 10 is wired to tab:outcomes' LL5D group through
    \fvgroupalt{ll5d}{pending}{…}.
  - §6.3's carry-over sentence agrees with B2's last paragraph (one-sided, fd_1b_null.py:111-122; "the same n" = 16).
- **Checks on the working tree:**
  - the paper's rater copy PASS; the Supplement's rater copy PASS (16 of 16 table captions);
  - no Overfull in either build;
  - check_round with the fill test PASS; make_values --check PASS (4026 values) and its self-test PASS;
  - sec4 17/17 (17 passed); pointers 37; registry PASS.

## 2026-11-10 — group C: main merged, the ESS paragraph, V-ATLAS rule 1, B1 row 1's counts (director's rulings 1-4)

- **Main merged** (ruling 1): a3da98a2a, `merge --no-ff origin/main` (12 commits through b18426156, PR #1027), no
  rebase, no cherry-pick. 1a015eef, 3c3a6f74 and 4580caf5c are ancestors of the merge. None of the merged commits
  touches docs/analysis-note.
- **S4, the ESS paragraph** (ruling 2), at the end of supp:estimators. Source: fd/receipts-ess/cluster/ess/ess.json
  (sha256 d4f1268d…, pin "ess"), under its README's CITABLE FOR and NOT CITABLE FOR. Keys: make_values ess_values.
  - (B), each event's contribution to the cell integral, is the printed definition. make_values asserts that (A),
    the final weight wpush·w_truth, gives the same n_eff/n and max share at the printed figures and n_eff to 1e-6, so
    the text names both.
  - "14 of 16 ≥ 0.903" is computed. The cells split at 0.9, and make_values asserts the gap: exactly two cells (R04
    0.612, R00 0.638) are below 0.9, and both are below 0.7. ess-nhigh and ess-high-min are counted from the others.
  - Asserted: every (A) and (B) weight is positive (n_negative and n_zero are 0) in every cell and globally; verdict
    PASS; xsec_flat bound; 0 events in zero-denominator cells.
  - NOT CITABLE FOR is one clause: "describe the weights of this one result and are not an uncertainty, coverage or
    validity statement".
  - **S4's Training details** said "No effective sample size of the unfolded ensemble is computed." The ESS record has
    made that false for the reported result, so the sentence now points to the new paragraph (one content fix,
    source comment amended). The note's sec_method.tex:15 still says it. That is not this lane's file; reported to the
    director.
- **S11, V-ATLAS rule 1** (ruling 3). The deviation statement is kept. 331 614 (R07) and 0.368 % (R05) are now keys
  (vatlas-*, from the valid-region read readout.json 91bb604e, pin "vregion").
  - make_values asserts that V-ATLAS's mc_neff_truth equals the ESS record's prior_w_truth n_eff in every cell, to
    1e-9 relative. So the two records measure the same quantity on the same events.
  - One clause is added: the final-weight n_eff is at least \fvval{ess-neff-min} (325 119, R07) in every cell, so the
    first condition also holds under the definition of Ref. [ATLAS:2024jets]. The 5000 threshold is asserted under both
    definitions.
  - Rule 2 (V-PRIOR) is untouched in this commit.
- **B1 row 1 and §3.2** (ruling 4). Traced in the adopted 2D covariance Q's records (RE-2 part C r2):
  - 300 bootstrap replicas: s5.json.gz (5c489837, pin "s5q") counts 300 production outputs 2dc_P_S1_*, equal to
    budget_Q.json.gz's (971e8a9d, pin "budgetq") derived count stat_replicas_S1. Key cov2d-nstat. This is Q's statistical
    block at seed 42, not VL170's superseded seed-1 set; both have 300.
  - five seed settings: budget_Q's seed_triplets_S4B_seeds_plus_seed42 = 5, which make_values checks against S5's S4B
    seeds {45, 48, 51, 54} plus seed 42. Key cov2d-nseed-word.
  - three period groups: playlist_term.json (5b023478, pin "plterm"; its npz c1723cb5 is the C_PL that Q adopted) has
    period unfoldings PA, PB and PC at seed 42. Key cov2d-nperiod-word.
  - make_values now reads a pinned .gz readout decompressed. The pin is on the committed .gz bytes.
  - **187 universes is NOT keyed, and the record does not support it as worded.** S5's checks give the refined arm
    (Q's) "refined_j2_38_bands_175_universes" [38, 175]: 175 weight universes in 38 bands. Its production outputs add
    five lateral bands (BeamAngleX/Y, MuonResolution, Muon_Energy_MINERvA/MINOS) with 2 each, which makes 185, plus
    the flat normalization ("universe_bands_43_plus_norm"). 187 matches "may_44_bands_187_universes", the July
    sweep's count, which still includes Rvp1pi (2 universes, dropped from Q). The note words it consistently:
    sec_results.tex:123 "43 of the 44 bands of the systematic-universe sweep (187 universes) with the normalization".
    The paper's "(187 universes, including the normalization)" reads as the block's own count. Left unrepaired, per
    the stop rule, and reported to the director. Until the ruling, both sites keep the literal, and check_round's new
    LITERAL_PAIRS / check_literal_pairs (with a self-test) fails if §3.2 and Table S8 row 1 differ or either is missing.
    The literal predates this round.
- **Checks on the working tree:**
  - both rater copies PASS (16 of 16 table captions); no Overfull in either final log;
  - check_round with the fill test PASS, and its self-test PASS; make_values --check PASS (4048 values);
  - sec4 17/17; pointers 37; registry PASS;
  - check_restyle against 4580caf5c fails only on the added keys, the cite and ref, the three numerals now keyed,
    and Q11–Q13 (the B5 removals already reported; the re-pin is limitation-resolver's).

## 2026-11-10 — the group B read's two items, the universe count, V-PRIOR withheld

- **M108** (the director's group B read): S10's replacement sentence keeps both facts of GiBUU's record. Its
  free-proton sample "failed its sampling-closure check, and its deep-inelastic events, \fvval{g-gibuu-hlab-dis}\,% of
  it, do not conserve energy". That is the existing key, 46. The note's sec_joint.tex:327 says 46 % of its hydrogen
  sample.
- **M107/M118: the old-against-new values diff.** Each B5 key at this head, against its pre-B5 counterpart (key
  without "-b5") in values_fived16.tex at 78ab386e0:

  | key (new) | old key | old | new |
  |---|---|---:|---:|
  | fb-b5-edge-max (-nopl) | fb-edge-max (-nopl) | 3.8 (6.2) | 3.8 (6.2) |
  | fb-b5-offset-relmax (-nopl) | fb-offset-relmax (-nopl) | 0.4 (1.0) | 0.4 (1.0) |
  | gdef-b5-dmax, -bound | gdef-dmax, -bound | 0.063, 0.07 | 0.063, 0.07 |
  | pl-chi2fall-b5-total-lo / -hi | pl-chi2fall-total-lo / -hi | 3.6 / 29.3 | 3.6 / **30.6** |
  | pl-chi2fall-b5-shape_only-lo / -hi | pl-chi2fall-shape_only-lo / -hi | 7.4 / 40.4 | 7.4 / **39.7** |
  | sens-b5-detlat-fall-max | sens-detlat-fall-max | 18 | 18 |
  | sens-b5-detlat-fall-max-nopl | sens-detlat-fall-max-nopl | 19 | **16** |
  | sens-b5-flux-fall-lo / -hi (-nopl) | sens-flux-fall-lo / -hi (-nopl) | 23 / 38 (24 / 48) | 23 / 38 (24 / 48) |
  | sens-b5-joint-chi2-min (-nopl) | sens-joint-chi2-min (-nopl) | 41 (45) | 41 (45) |

  - The group B entry's "unchanged except pl-chi2fall" holds for every printed key.
  - One unprinted key also moved: sens-b5-detlat-fall-max-nopl went from 19 to 16. It is the automatic without-block
    copy (MATRIX_KEYS), and neither the paper nor the Supplement prints it (grep: the only detlat use is
    supplemental_body.tex's \fvval{sens-b5-detlat-fall-max}). The group B entry above is corrected by this row.
- **The universe count** (the director's ruling, option (i)). §3.2 and Table S8 row 1 now print "\fvval{cov2d-nuniv}
  universes in \fvval{cov2d-nunivbands} bands, plus the normalization", that is 185 in 43. The keys are in
  make_values cov2d_block_values, and each piece has its own record field:
  - 38 bands with 175 universes: S5's check refined_j2_38_bands_175_universes, cross-checked against the 175 U_*
    production outputs in 38 bands;
  - 5 lateral bands with 2 universes each: S5's production outputs 2dc_P_S3_<band>{0,1};
  - 43 bands plus the normalization: budget_Q's bands (44 entries, equal to its bands_in_npz), which make_values
    asserts are exactly the weight bands and the laterals, plus __Normalization_flat.
  - The asserts are 175 + 10 = 185 and 38 + 5 = 43.
  - check_round's LITERAL_PAIRS is replaced by the shared key, and GONE gains r"\b187 universes".
  - This corrects a factual error. Its pairs go in the meaning read with the V-PRIOR pairs.
- **V-PRIOR withheld.** Source: DECISION-20261110-joseph-vprior-withhold.md, on main at fc847d825 (#1028), items 1
  and 4. The reason is the consult's: secondary-results/consult-sol-vprior-20261110/.
  - Paper §5.4. The rules sentence now gives V-ATLAS alone ("leaves 14 of the 16 cells valid"). One sentence
    withholds V-PRIOR's results, with the consult's reason intact, and keeps its one-line definition inside that
    sentence, because the reason needs it: "about the analysis prior", and "its CH-corrected NuWro and GiBUU inputs".
    "12 under both" is removed. The third rule (V-HALF) and the closing "All three rules …" are unchanged; the latter
    still holds for the three rules as defined.
  - S11:
    - its opening says the second rule's results are withheld;
    - V-ATLAS is unchanged;
    - removed: V-PRIOR's 14 of 16, R08 (η = 0.522–0.534), R15 (0.564–0.565), the largest valid η (0.444, R10), the
      threshold sensitivity (11 at 1/3, 16 at 1) and "Twelve cells are valid under both rules";
    - the contrast that only V-PRIOR selected ("the two rules test different things …") is removed. Its V-ATLAS half
      is kept as "The first rule grades one truth's closure pull", with the no-interval and no-exclusion clauses;
    - the withholding sentence points to S10's app:gendefs, where the carbon-only reasons are stated.
  - **The sweep was by claim.** The patterns were: under both, generator spread, spread of the generator, bias
    spread, \eta, cells valid / are valid / valid under, validity rule, two rules, second rule, half the spread,
    fourteen, twelve, 0.444, R08, R15, supp:validity, V-PRIOR. They were run over paper_body.tex, supplemental_body.tex
    and main_paper.tex (the abstract), comments excluded.
    - V-PRIOR's claims occur only at paper §5.4 and S11. Every other R08/R15/twelve hit is about cells or playlists.
    - The abstract, tab:outcomes (whose validity row is V-HALF), B1's tables (row 6 is V-HALF; no row cites V-PRIOR),
      the captions, and §7's limitations ("The validity rules grade the estimator's bias …", which still holds of
      V-ATLAS and V-HALF) carry no V-PRIOR result.
    - V-PRIOR had no value keys: its numbers were literals. So no key is removed. η is no longer printed anywhere,
      so the symbol inventory's η entry above now has no use.
  - **Check 12** (SUPP-SYNC): S11 is "Moved from the paper", not note-copied, so the sync check pairs nothing there.
    Its report is unchanged: 58 paragraphs, explained 43, same 14, seed-adapted 1. The intended divergence is that
    the note keeps V-PRIOR (decision item 5) while the Supplement withholds it. S4's Training details paragraph is
    "explained" (adapted 2026-11-10).

## 2026-11-10 — fig:ratio16 on carbon only (B5's figure), its caption, the read pairs, the push

- **Merged** e931f8ad8: Codex's e825c47cb (figures/methods-ratio-b5-20261110), approved by the director. It is a
  --no-ff merge with no conflicts.
  - The printed PDF is docs/analysis-note/figures/fd_g_fig_ratio.pdf, sha256 1e6d550e…. It equals
    fd/gencmp/carbon-figure/fd_g_fig_ratio.pdf, and make_values' FIGURES pin passes.
  - The producer is nd-unfolding/fd_g_ratio_carbon.py, through fd_g_figures.ratio_model, paint and render
    (carbon-figure/REPORT.md). NuWro's and GiBUU's g are defs.json generators.{nuwro,gibuu}.carbon.analysis_definitions
    .chi2.reported.g. f and the error bars' sigma_total_over_f are the E-A2 readout's.
  - verify_hash_bindings.py has 169 → 178 bindings, with no removal (the director checked binding-delta.txt).
  - The figure is the Supplement's only. No note .tex file includes fd_g_fig_ratio (grep at this head), so the note
    prints no copy here. **Check 12:** the sync check pairs paragraphs, not figures. The note's lane keeps its own
    CH-corrected comparison, which is out of B5's scope. That divergence is recorded here and in the B5 entry.
- **The caption** (Supp fig:ratio16) drops "with NuWro and GiBUU corrected to CH". It now says they "are on carbon
  only, without a correction to CH", with S10's reasons word for word (M108's GiBUU clause included) and a pointer to
  app:gendefs. The GiBUU 8-cell sentence was already there. The source comment names the producer and its fields.
  The rendered page (Supplement p. 33) was checked by eye: the legend reads "NuWro 21.09: carbon only" and "GiBUU
  2019: carbon only; p∥ < 4.5 cells only", and the lower panel has 8 GiBUU points.
- **Meaning-read pairs**, 5c15753dc → this head: vprior-read/pairs.tsv (sha256 644da5e8…, 17 rows: §3.2, §5.4 ×2, Table
  S8 row 1, the caption ×2, S10, S11 ×10). The exporter is vprior-read/export.py (groupb-pairs' exporter with base
  5c15753dc).
- **Checks at this head:**
  - both rater copies PASS (16 of 16 table captions); 0 Overfull and 0 undefined references in both final logs;
  - check_round with the fill test PASS; make_values --check PASS (4050 values; 2 figures equal their sources);
  - sec4 17/17; pointers 37; registry PASS;
  - check_restyle against 716ce04ca fails only on the caption's key and ref, and on #981's quotes Q11–Q13 (B5) and
    Q20–Q22 (V-PRIOR), which the decision removes; the re-pin is limitation-resolver's.

## 2026-11-10 — batch 3 (the interim round's group A item 9): S9 as labelled studies, S4's history table

- **S9** is reorganized into separately labelled subsections. The text is moved, with the three exceptions marked
  below.
  - The overview tables (S8–S11 numbering unchanged) stay at the top.
  - Then come six subsections:
    - supp:study-band, "The superseded two-dimensional band test": the note's sec:coverage paragraphs.
    - supp:study-fd, "The fake-data bias tests": the fake-data paragraphs, the q3 tilt, the held-out tunes and
      tab:tune-gate, and the eight-cell GiBUU reading.
    - supp:study-prr, "The prior-retention study": its thresholds and tab:prr-rho. This is a sixth label beside the
      five the director listed, because the study is neither a coverage test nor one of the fake-data bias tests.
    - supp:study-cov2d, "The two-dimensional coverage test": the coverage design (supp:covdesign, tab:cov-design),
      which is shared with the second test.
    - supp:study-cov1, "The stopped first five-observable coverage test": the diagnosis.
    - supp:study-ll5d, "The second five-observable coverage test": the clipping record.
  - The three new wordings:
    - (i) The stopped test's subsection opens with the paper's §6.2 sentence on the stop (r5:223, copied). Its former
      opening "The diagnostic study gave the following results." now reads "The diagnostic study of that check gave
      the following results."
    - (ii) The second test's \paragraph heading became its subsection. One sentence points to the shared design.
    - (iii) The subsection titles.
  - Every existing label is kept. The paper's six \ssec{S9}{supp:tests} pointers still resolve, with 37 pointers
    checked.
- **S4: the history table.** The estimator-configuration paragraph keeps (e) and (f), the two reported
  configurations, as items, with their text unchanged. Three facts that sat in the following paragraph are folded
  into those items: the sixteen-cell result and its covariance pointer; the 3D and 4D regeneration with no
  covariance; and the 2D rebuild after the closure with backgrounds, with its timing. tab:estimators-matrix becomes a
  four-row history table of (a)–(d): learner and background treatment, used for, and history.
  - The history column carries the old paragraph's facts: (a)'s central value and covariance were "produced before
    the purity bias was found and the refinement was developed"; (b) was "the quoted 2D central value in an earlier
    version …; studies labeled exact-split use it and have not been recomputed", under its existing % Search line.
    (c) and (d) have no history; they show "---".
  - The table's (e) and (f) rows repeated the items, so they are dropped.
  - (d)'s row gains a pointer to Fig. S1, which shows configuration (d).
  - check_restyle reports 11 note citations and refs lost. Each one was a duplicate: every N-* target still occurs at
    least once (counted at 535147409 and now).
- **Pairs** (base 535147409): batch3-read/pairs-read.tsv (27 rows) and batch3-read/moved-verbatim.tsv (56 rows). A row is
  moved-verbatim when its sentence occurs word for word on the other side.
- **Checks:**
  - both rater copies PASS (16 of 16 captions); 0 Overfull and 0 undefined in both;
  - check_round with the fill test PASS; make_values PASS (4050); sec4 17/17; pointers 37; registry PASS;
  - check 12 reports 58 paragraphs, explained 43, same 14, seed-adapted 1. The two sec:method-config paragraphs are
    "adapted 2026-11-10", so they are explained.

## 2026-11-10 — batch 3's read fixes, journal-editor's review of 535147409, the withholding sentence moved to S11

- **Batch 3 read** (the director: moved-verbatim 28/28 identical, 27 rows read, 5 flagged):
  - M006/M016/M017: the history table's caption is now "The four configurations that give none of this paper's
    reported results". (a)'s row says it "gave the companion note's five-observable central value … and its five-axis
    covariance", and the lead-in says "The other four give none of this paper's reported results".
  - M015: (e)'s three uses from the dropped row (the generator tests, the generator shapes held out of development,
    the precision study) are all in (e)'s item, verbatim. Confirmed by grep; nothing added.
  - The prior-retention subsection is accepted as a sixth label.
- **journal-editor's review** (no blockers, 12 items). The director's rulings: items 1 and 4–12 approved as a
  presentation batch; item 2 in the director's form; item 3 by Joseph (DECISION-20261110-joseph-confirm-round-scope.md,
  PR #1030).
  - 1: Table S11 row 8 now uses the paper's wording, "no pseudo-experiment of 300 lies in the joint region at either
    tune".
  - 2: Fig. S2's caption now reads "because their free-proton samples have unresolved validation problems (Sec.
    S10.1); their ratios therefore contain a target difference (Sec. S10.1)". The reason is given in the V-PRIOR
    sentence's terms, and S10.1 already states the target difference (GENIE 8.3 % for W < 1.1 GeV). The caption also
    adds "on its own vertical scale", which is visible in the rendered panel. S10.1 changes "supplement" to
    "supplementary sample".
  - 3: the withholding sentence moves from paper §5.4 to S11, in JE's wording: "… because it uses NuWro and GiBUU
    predictions corrected from carbon to CH with free-proton samples whose validation problems are unresolved (Sec.
    S10.1)". §5.4 now gives only the rules with results: "One per-cell validity rule … A second rule asks …", and
    "Both rules …; neither …" in place of "All three rules …; none …".
  - 4: S11's heading is "The first two per-cell validity rules". Its opener: "Two of the three per-cell validity rules
    are defined here; the third, the bias-half rule, is graded in the paper's section on per-cell validity and in
    Table S11 (row 6)." "labelled separately" and "measured since" are deleted.
  - 5:
    - (a) "natures" in Table S9 rows 8 and 10 becomes "pseudo-experiments drawn from the full simulation's universes".
    - (b) The Estimator column is widened from 0.11 to 0.13 and Truth(s) narrowed from 0.19 to 0.17; 0.16 overfilled
      by 4 pt with the \mbox tune names. "2D" and "IBU-n" are defined in S9's lead-in and used in rows 1, 5 and 8.
    - (c) \addlinespace between rows in the four B1 tables. (d) 4 pt under each B1 caption.
    - (e) Row 9's "were declared" becomes "specified in advance". JE's "none ran" is not used: the staged redesign's
      first stage did run, and its record was not reopened here to say what it ran.
  - 6: Table S10.
    - Row 1: "ratio of integrated cross sections, 2D to published".
    - Row 3b: each χ² names its tune, "for 16 degrees of freedom".
    - Row 4: each result is labelled with its truth.
    - Row 5: "95th and 99.7th percentiles" (the paper's form).
    - Row 2, a **precision change for the director's read**: s5e-q3-ewmax prints 37 (was 36.8), whole percent like
      the row's 16, 31 and 74. It prints only in this row (grep: no other use).
  - 7: row 6 adds "\fvval{vhalf-n-notassessed} not assessed", as §5.4 prints.
  - 8: the ESS paragraph adds "with n the number of those events".
  - 9: Table S13 uses x̂ → x̂ + Σ_b s_bΔ_b(T)/2. The lead-in gains "with a_u an event's weight in universe u".
    \addlinespace between its rows.
  - 10: "only the range's end points were retained"; "the reading specified in advance"; "a stress amplitude chosen
    in advance"; "the cross sections of the 42 (Eavail,W) cells" (the record's 42 functionals are those cells);
    "the joint (J) grid". Table S7's "declared statistic" becomes "the statistic specified in advance".
  - 11: the key f1-tune-* is now \mbox{…} in make_values, so every use in the paper and the Supplement is
    unbreakable. 0 Overfull in either build.
  - 12: Table S7's caption adds "with f the five-observable result in the cell".
- **Pairs** (base cbb997d60): je-read/pairs.tsv, 52 rows. Many rows are table rows whose only change is the
  \addlinespace line ending.
- **Checks:** both rater copies PASS; 0 Overfull and 0 undefined in both; check_round with the fill test PASS;
  make_values PASS (4050); sec4 17/17; pointers 37; registry PASS. Tables S8 and S11 were inspected on their
  rendered pages.

## 2026-11-10 — the JE batch read's two checks; Tier 1 batch T1-0 (editorial)

- **JE read** (f311d805, 52 rows, 5 flagged; M004, M034, M045 and M051 accepted). The two checks:
  - **M038.** The 42 (Eavail,W) "functionals" are the cell cross sections, so the new wording stands. Source:
    nd-unfolding/s5n_truth_check.py:5-7 at f3ab74f78 ("every (E_avail, W) M1 functional of the analysis's own
    projection (the s5c reported functionals' first 43 rows, cross sections through the analysis extraction)"). Its
    :61-62 take M1 = U[:43] from s5c_coverage.reported_functionals, whose :43 projection M maps the fine grid onto the
    (Eavail,W) cells. Row 43 is the non-physical EW_all_ones (OUTCOME-20260925-s5n-stage1-development-fail.md:44), and
    the 42 are the cells. The outcome record's own wording is "42 physical (E_avail,W) cross-section functionals".
  - **M049.** "(row 6)" becomes "(test 6)". The tables number tests 1, 2, 3a, 3b, 4, …, so "row" was ambiguous. The
    test numbers are typed labels in the tables' first column, so no \label can carry them.
- **T1-0** (the director's Tier 1 item 9; the referees' lists: Claude 2, 10, 13, 14 and GPT 13 in
  referee-methods-confirm-20261110/):
  - Broken references:
    - Table S2's caption "(Sec. S5 and S5)": the two labels both name S5, so it becomes one pointer,
      Sec. \ref{supp:cov16}. Its source comment now says "adapted 2026-11-10 (T1-0)".
    - "App. S4" becomes "Sec. S4" (app:negweight sits inside S4).
    - "Ref. [1], App. G (Ref. [1], Sec. G.3)" becomes "Ref. [1], Sec. G.3".
  - S4's garbled range: "(from 3.5–4.1 % to 0.11–0.24 %, …)". Two \SIrange inside "from … to …" had printed
    "3.5 % to 4.1 % to 0.11 % to 0.24 %".
  - Duplicated text:
    - S2's second beam-axis sentence (moved from r5:79) is removed. The note-copied paragraph before it, from
      sec:eavailw-definitions, says the same thing with the tilt and residuals.
    - S4: the purity weight's formula appeared both in "Background subtraction" and in app:negweight's paragraph 1.
      The second now reads "the purity weight w_pur(b) defined above".
    - S4: "The nominal settings are the scikit-learn defaults, with LightGBM matched to their capacity" repeated
      "Hyperparameter choice" and is removed from the moved r5:95 paragraph.
    - Each source comment is amended.
  - Numerals at sentence start, §3.3: "…one set of truths, of which \fvval{f0b-all-truths} are graded…" and "The
    note gives \fvval{f0b-nungraded} further truths, which are descriptive."
  - Table 1: checked on the rendered page (paper p. 2). The columns are aligned: pT 0–0.7 and 0.7–4.5, then p∥, Eavail,
    q3, W, purity and diag. The referee read the blind pdftotext copy, whose column order is an extraction artefact.
    No change.
- **Pairs** (base 10b88ad9b): t1-0-read/pairs.tsv.
- **Checks:** both rater copies PASS; 0 Overfull and 0 undefined in both; check_round with the fill test PASS;
  make_values PASS (4050); sec4 17/17; pointers 37; registry PASS. Check 12: explained 44, same 13, seed-adapted 1, no
  UNEXPLAINED.

## 2026-11-10 — Tier 1 batch T1-1 (claims: ρ and PR-1's classes, instability, κ, ENS1's deficit)

- **ρ and PR-1's classes** (the director's Tier 1 item 1 and the addition on PR-1's class labels).
  - FD-PRR-DECLARATION.md §5.1 (:286-291) classes a factor "increases" when some level raises ρ by at least the bar
    and none lowers it by the bar. The class names no direction of the setting. Both referees read the bare classes as
    a direction.
  - New keys (make_values tier1_values, FD-PRR readout 9238f22b at split s991000):
    - prr-pr1-increases, prr-pr1-noeffect and prr-pr1-reduced-kinds, the classes grouped by truth;
    - prr-more-dmax, 0.031: the largest fall of ρ at a higher iteration count (K10, K20, K50) or capacity (C400,
      C1000), over both truths.
  - Asserts:
    - every "increases" comes only from reduced levels (K2; C25; O4r/O4/O3/O2; MCq);
    - no level lowers ρ by the bar;
    - every higher iteration count and capacity lowers ρ at both truths, by less than the bar.
    At these truths the raising levels are K2 at the q3 tilt (+0.057), C25 at both, and O2 at both.
  - §5.3 now opens with ρ's definition and the study design, then the classes and labels, then the results, the new
    table and the two other findings with the figure. "Two findings" became "Two other findings".
  - The classes paragraph says a class names no direction. The label glosses follow FD-PRR's table (:323-329): "some
    tested iteration count reduces ρ" and "some tested capacity reduces ρ", replacing "more iterations / more capacity
    reduce ρ", which read the classes as directions.
  - The results open with the classes and their direction: "For …, a reduced setting (fewer iterations, lower capacity
    or fewer observables) raises ρ by more than the threshold, so these are classed increases; … have no effect.
    Every higher iteration count and capacity tested lowers ρ at both truths, by at most 0.031, less than the
    threshold."
  - The IBU, swept by claim for "IBU is better" and "retains less":
    - PR-2a's printed branches now say "has a lower / higher retained fraction"; the declared names "IBU retains
      less/more" appear only in quotes in S9.3.
    - PR-2b: "its retained fraction falls".
    - A new sentence: IBU's ρ is negative at both truths (−0.116, −0.130; −0.247 and −0.377 at 200 iterations), so it
      moves past the truth, away from the prior. Its RMS bias and χ² are "larger" than (e)'s at the GiBUU hybrid truth
      and "smaller" at the q3 tilt, from the keys prr-cmp-*. make_values asserts that ρ is negative at both and that
      the RMS bias and χ² move the same way at each truth.
    - Note: the director's "its larger RMS bias and χ²" holds at the GiBUU hybrid truth only. At the q3 tilt IBU's are
      smaller (0.054 against 0.060; 31.6 against 54.9), so the text gives each truth and ranks nothing.
  - The new paper table tab:prr16 holds Table S13's essentials: ρ, RMS bias and χ² for 5D and IBU-5 at both truths.
    It points to \stab{S13}{tab:prr-rho}.
  - Table 2's PRR row, S10 row 4 and S9.3's classification sentence say the same in short form. The unprinted
    alternative branches of the abstract's prr-abs case are reworded the same way.
- **The abstract** (250-word ceiling, Joseph 2026-11-09). The longest rendered case was 248 words at 4b12493ce. As first
  drafted the additions reached 283, so the abstract carries:
  - "on noise-free pseudo-data, binned iterative unfolding moves past the truth at both". "at five iterations" is
    dropped: ρ is negative at 5 and at 200 iterations. The per-truth RMS/χ² comparison does not fit, and is in §5.3
    and tab:prr16. This is flagged to the director.
  - "…; the sixteen cells' spread is a median 0.133%". A separate clause: as a parenthetical beside 0.8/2.6 σ, the two
    different measures read as equal.
  - The longest case is now 248 words. The abstract's 0.8 and 2.6 are now the keys s5e-round-*.
- **Instability** (item 2). §6.1 already gives both scales: 0.8 / 2.6 σ in its first paragraph, and 0.133 % on the
  sixteen cells inside the protected B0 span, which stays verbatim.
  - New keys rnd16-median/min/max come from RS1's R0 read, rs1_r0.json (724f0c3a, pin "rs1r0"): the median, minimum and
    maximum of sigma_J_over_f, asserted equal to the record's own reproduction control [0.133, 0.055, 0.252].
  - check_round's LITERAL_KEYS gains the three typed literals of the protected span. check_literal_keys takes its entry
    list as a parameter, so the self-test checks the first entry alone.
  - §3.2, where the statistical block is defined: "Each bootstrap replica of the statistical block refits the whole
    unfolding with its own rounding-level perturbation of the inputs, so the block includes the estimator's
    sensitivity to such perturbations (section 6.1)." There is no numeral; §6.1 keeps the 50.
- **κ** (item 3), §4.1. "The central 90 % range of the same ratio over the paired replicas … describes its spread over
  resampled datasets and is not a confidence interval for the ratio; it straddles a class boundary fixed in advance, so
  the reading fixed in advance is unresolved." "so the source of the difference is unresolved" is dropped.
  REF-C2C1-DECLARATION.md:182-190 names the reading "unresolved", and :208 licenses only reporting ρ (κ here), its
  interval and T_δ.
- **ENS1** (DECISION-20261110-joseph-ens1-deficit-licence.md item 3, PR #1035).
  - §6.1 carries the licence's one sentence, in the paper's terms: "the floor fixed in advance" for "the declared
    floor", and "the 16 cells". Its numbers are the keys ens1-g-*, from ens1_stage2.json (c2ee701d) bias.stage0c_gibuu:
    the excess is rms − rms_control and the floor is delta_rms. All are asserted equal to the licensed figures.
  - The referee's two sentences:
    - §6.1: "It was evaluated only on simulated pseudo-data, so its meeting the stability requirement is a statement
      about pseudo-data; the illustrative data output uses the reported estimator, which fails that requirement."
      Source: ENS1-DECLARATION.md:105-107, as cited by the T2C licence note.
    - §7.1 item 3: "…so the instability of the data result itself is not mitigated".
  - The text reads no noise and ranks nothing.
- **Pairs** (base 4b12493ce): t1-1-read/pairs.tsv (58 rows).
- **Checks:**
  - both rater copies PASS; 0 Overfull and 0 undefined in both;
  - check_round with the fill test PASS (abstract 196–248 words over 678 cases), and its self-test PASS;
  - make_values PASS (4066); sec4 17/17; pointers 38 (one new \stab); registry PASS; check 12 unchanged;
  - check_restyle: the protected spans are unchanged. It reports the intended additions and Q11–Q22 as before.
  - The new table and §5.3 were inspected on the rendered page (paper p. 10).

## 2026-11-10 — Tier 1 batch T1-2 (coverage: one section, the target once, fractions from keys, Tier 2 (a))

- **Main merged** (030c1b43f, the director's ruling 1): a --no-ff merge of origin/main (27 commits) with a message file,
  so the T2a records are in the branch's tree. d6c1cd7b0, 1a015eef and 3c3a6f74 are ancestors, and the merge changes
  nothing under docs/analysis-note.
- **One coverage section.** §6.2 and §6.3 are merged under "Calibration of the uncertainties". The second test is a
  \paragraph of it. Its label sec:ll5d now sits beside sec:calib, because a label after revtex's \paragraph printed
  "6.2.0a" and overfilled Table 2's Sec. column by 12 pt.
- **The target, stated once** (item 4), opening the section: per cell, the fraction of errors with |e_c| ≤ σ_c (P0 =
  \fvval{null-p0} for a Gaussian error); jointly, the fraction with χ² below its null's quantile. Each test uses a
  content matched to its draws and a binomial threshold, flags only under-coverage, and reports over-coverage (S9's
  design; fd_1b_null.py:111-122). The second test's repeat of "Only under-coverage counts as a failure; over-coverage
  is reported" is removed.
- **The 2D paragraph's numbers are keys** from the score records (fe5263e9, 84976694): k_joint, ndf, χ²/ndf ± SE,
  and the size (per_truth_union_bound). The typed 190, 192, 204, 205, 16.55 ± 0.17, 24.17 ± 0.37, 0.0348 and 0.0363 are
  gone. "none … lies" stays as worded; make_values asserts both joint counts are 0.
- **The actual coverage, from keys** (the director's ruling 2):
  - Joint: the null's expected count is 300·q_joint (207.6 and 209.2), from the graded null "null" in null_<T>.json
    (80274e52, 6bd5259d). make_values asserts each score's null_digest is its null file's sha256. "null_minus" serves
    leave_out_mec only (COV2D-ADDENDUM-A4.md:40, :190).
  - Per cell, from grade.counts and k_cell: the range of counts (148–300 at both tunes), the thresholds (145–176 and
    144–178), and the median count (229 and 219) against the median draw-matched expectation 300·p_c (203.7 and
    203.9). The nominal Gaussian 205 = round(300·erf(1/√2)) is printed only beside it.
  - The number of cells at or below their threshold equals the flagged cells (2 and 1; asserted).
  - Over-covering cells: 90 and 67. over_covers is fd_1b_mc.py:684-685 at b25918fbd: the same binomial rule applied the
    other way at alpha_cell.
- **Tier 2 (a)** (the director's reading of 2026-11-10; t2a_AR23.json 33b7fd40 and t2a_G18.json 6757055e, #1041; keys
  t2a-*, make_values t2a_values).
  - The paper, after the 2D paragraph: the split (82 % and 87 % mean-error part; 13.6 and 21.0 per ndf against 2.94 and
    3.21 for the spread), by rank (the 32 largest directions carry under 1 %, beyond the 73 largest 77 % and 87 %), and
    the truncated tests (none of 300 at 73 or 139). It closes with the licensed sentence: "dominated by mean bias
    concentrated in the poorly determined directions of C_T, with the spread also exceeding C_T's prediction, and
    truncation to the better-determined directions does not remove it; the decomposition does not establish the cause".
  - S9.4 adds "Where the two-dimensional test's χ² sits", at the end of the subsection: the same, plus the spread's mean
    square per component (1.6 and 1.5 over ranks 1–73, 3.0 and 3.6 over ranks 74–139, 4.4 and 4.7 beyond), the
    truncated nulls' thresholds (193 and 190 at AR23; 193 and 191 at G18) and the solver agreement (≤ 1.5×10⁻⁶, no
    unresolved rank, truncated counts agree).
  - Asserted: every control passes; the score pin matches; Σb_k and Σf_k reproduce split.*; the eigenvalues are
    ordered; the top-32 share is under 1 %; the truncated counts are 0 of 300 and at or below k_joint; n_unresolved is 0.
  - "32" is the director's fixed reading. C_T_counts above 1e-4 is 32 at AR23 and 33 at G18; the text says "the 32
    directions with the largest eigenvalues".
  - The director's "about 1.5" for ranks 1–73 is 1.6 (AR23) and 1.5 (G18). Both are printed from keys.
  - The optional figure is not included: the record's figure path is a scratch path, not a committed file.
- **Pairs** (base d6c1cd7b0): t1-2-read/pairs.tsv (29 rows).
- **Checks:**
  - check_round with the fill test PASS on the tree before the last two edits: the sec:ll5d label move and the
    "none … lies" wording. check_round without the fill test PASS after them.
  - The paper's rater copy PASS, with 0 Overfull, after them. The Supplement's rater copy PASS, with 0 Overfull, before
    them; neither edit touches the Supplement.
  - make_values PASS (4117); sec4 17/17; pointers 40; registry PASS; check 12 unchanged.
  - check_restyle against d6c1cd7b0: only the intended additions and keyed numerals, and Q11–Q22 as before.

## 2026-11-10 — Tier 1 batch T1-3 (structure and run-period, with Tier 2 (b))

- **§4.2 split** (item 7): "Run periods" (sec:closure2d) and "The five-observable quadrant sums" (new sec:quad). Table
  2's quadrant row points to sec:quad.
- **Both readings of the run-period benchmark** (item 6). Source: the per-period read, readout.json 4872df32 (pin
  "ppbench"), under OUTCOME-20261107-per-period-2d-benchmark.md's licensed R5 and R5bar sentences and its NOT CITABLE
  FOR (which period is right; the cause of the shape difference or of the step; dropping 1G-1M).
  - Keys pp-k (73), pp-kbar (132), pp-res (0.29), pp-dbar (0.69), pp-fbar (0.31) and pp-nrep (10), each asserted equal
    under both noise models ("replica" and "replica+seed"); classes asserted "no change" and "farther without 1G-1M".
  - The licensed "about 15 %" share of the resolved change stays typed: it is 14 % or 15 % depending on the noise
    model.
  - §4.2 now also prints the 132-direction reading and closes with "Neither reading establishes which period is right
    or the cause of the step", with an absence-ok waiver scoped to the licence. Table 2's run-period row gives both.
  - In S6 the reading's fraction and replica count are keys. Its 132 and 0.69 stay typed, because #981's quote Q23
    quotes them, and check_round's LITERAL_KEYS (now also reading the Supplement) tests them against pp-kbar and
    pp-dbar.
- **§5.1's long paragraph** is split in three: the GiBUU-to-GENIE result; the variant, background and IBU comparison
  with "no single cause"; and the other shapes and the figure. These are paragraph breaks only.
- **§7 leads with the practical recommendations** (item 7; Claude's referee report section 3). r5:322's checklist sentence
  becomes the opening paragraph: five checks, each paired with what this paper's own section found.
  - Closure with backgrounds (§5.1).
  - Recovery of generator-sized changes measured as a retained fraction (§5.1, §5.3).
  - Coverage jointly as well as per cell and read in the eigenbasis: here 2 and 1 of 205 cells are flagged while the
    joint test fails, with mean bias in the poorly determined directions (§6.2; keys cov2d-nunder-*; T2a's licensed
    wording).
  - Rounding as well as seeds: bitwise seed-independent but not stable, acting on the pseudo-experiment studied
    through float32 ties (§6.1).
  - Run periods before and after unfolding: a step present before unfolding that survives it (§4.2).
  - No check rests on a result not shown in the paper. The pubhold stays where it was, as its own paragraph, so the
    section-7 hold is unchanged.
- **Table 2's placement** (item 7). It is already as early as the ruling "after the test definitions" allows. Defined at
  the end of §3.3 (p. 4), it floats to the top of p. 5, before §4. Defining it before §3.2 puts it on p. 4 but pushes
  §3.3 to p. 5, so the table would print before the definitions. Reverted, byte for byte. Unchanged.
- **Tier 2 (b)** (the director's reading; fd/tier2-20261110/t2b/t2b.json 0e281a61, #1039; keys t2b-*, make_values
  t2b_values).
  - S9's fake-data subsection gains "The fake-data biases against smaller matrices":
    - without C_model the largest |z| rises by at most 0.45 (0.62 → 1.07 at G18), and the |z| > 2 count changes only at
      the q3 tilt (+1, R15);
    - against the statistical block alone, χ² runs from 124 (the GENIE + MEC (E_avail,W) shape) to 37,993 (the GiBUU
      hybrid truth), and with C_resp from 13 to 23,229;
    - the two closures at the prior stay below 0.5;
    - it ends with the licensed sentence ("small next to the reported covariance and large next to the statistical
      block"), "changes no grade or criterion" and "does not show whether C_model is needed or correctly sized", with an
      absence-ok waiver.
  - §5.2 gains one pointer sentence in the same terms.
  - Asserted: every control passes; 16 records; the prior group is {nominal, A7_mnvtune}; the argmax |z| rise is
    F1_genie_v3_g18; only q3's |z| > 2 set changes, by {R15}; the M2 and M3 extremes are W2 and A7_gibuu; every prior
    closure is below 0.5 under every matrix.
  - The optional table is not added.
- **Pairs** (base 74affb297): t1-3-read/pairs.tsv (22 rows).
- **Checks:**
  - both rater copies PASS; 0 Overfull and 0 undefined in both;
  - make_values PASS (4134); sec4 17/17; pointers 41; registry PASS; check 12 unchanged; check_round's self-test PASS;
  - check_restyle against 74affb297 shows only the intended additions, the keyed numerals, and Q11–Q22 as before. Q23
    matches.
  - check_round with the fill test runs on the committed head before the push.

## 2026-11-10 — note round 3 against the Supplement (check 12, read-only); Tier 1 batch T1-4 (the additions)

- **Check 12 against note round 3** (the director's request). check_supp_sync.py with --note-rev acf934d71 (#952) at
  f433cd9f7. It is read-only: the tool reads the note through git show, so no worktree or archive was made, and #977 was
  not changed. Result: NOTE-CHANGED 8, explained 34, same 11, seed-adapted 1, synced 4. **UNEXPLAINED none.** The full
  texts of the 8 pairs went to the director (scratchpad sync-acf-pairs.md, sha256 8a22e490).
  - Rulings:
    - item 2 (supp:176, the ESS sentence) is explained: the Supplement's own ESS paragraph covers it under the same
      licence;
    - item 8 (supp:457, S7's joint throws) is explained: it moves to the note in T1-5;
    - items 1, 3, 4, 5, 6 and 7 are to be synced to the note's round-3 text as their own small batch after T1-4.
- **T1-4** (the director's Tier 1 item 5):
  - **S4: "The reported estimator, step by step"**, after the history table. Configuration (e) is written from the code
    at abdc88c5, the ESS record's code_pin. Each module's sha256 prefix equals ess_capture.py's pin:
    omnifold_nn_core.py 24f87f11, s5c_unfold.py 510d749a, s5n_pseudo.py 8981f97b, s5e_candidate.py bda8c48c,
    unfold_2d_omnifold_unbinned.py 8ebe0277, xsec_nd.py 454001f3. s1_assemble.py is cited at fe5d79c61; it does not
    exist at abdc88c5 (Search: git show abdc88c5:nd-unfolding/s1_assemble.py, empty output @ abdc88c5). The producer's argv (ess.json) is --config R --iters 5 --construction data.
    - The refinement: s5n_pseudo.py:222-229 signed sample, :264-282 refine; refine_stay_positive
      unfold_2d_omnifold_unbinned.py:409-454, ν = |w| max(0, 2g−1) with g clipped; R's 400/31 at s5e_candidate.py:33;
      seed + 3 (REFINE_SEED_OFFSET); deterministic through s5c_unfold.config_params.
    - The loop: omnifold_nn_core.py:248-266; make_estimators :143-148 (100 trees, 8 leaves, learning rate 0.1);
      _reweight :152-155; the regressor :258-260; the pull :261; step 2 :263-266.
    - The cross section: s5c_unfold.py:136-146, extract_cross_section_nd xsec_nd.py:54. The cells: s1_assemble.py:119-122.
  - **The limitations list gains a seventh item.** The two-dimensional covariance's universe unfoldings approximate the
    weighting of events that fail reconstruction. The approximation is not corrected, and its two-universe test excludes
    only an effect above twice an earlier seed block's spread (the note's sec_systematics.tex sec:uq-2d-scope; §3.2
    already states the omission). It carries an absence-ok waiver. No text counts the items.
  - **S5, C_model's carbon component.** One sentence: the NuWro and GiBUU ratios are built from the generators' carbon
    samples without a correction to CH, so their shifts include the target difference as well as the generator
    difference, and the reported C_model keeps them on carbon. Source: FD-GENCMP-AMENDMENT-E-DECLARATION.md:82;
    DECISION-20261102-joseph-cmodel-keep-carbon-state-effect.md item 1 (#680).
    - The component's measured size with CH ratios (FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md) is **not printed**.
      Its CH ratios use the free-proton samples that the paper withholds (B5; the V-PRIOR decision). Raised with the
      director.
    - The sentence does not say whether the GENIE CV reference sample is on CH; the records read do not state it.
  - **The held-out tunes** as gated, normalized shape deformations:
    - §3.3: "each enters as a gated, normalized shape deformation of the simulated truth: the ratio … to GENIE CV in each
      fine cell, kept where its relative statistical uncertainty is at most \fvval{f1-statmax}, pooled over the coarse cell
      or set to 1 otherwise, and normalized so that it changes the shape only (S9)";
    - S9's tunes paragraph names them the same way.
- **Pairs** (base f433cd9f7): t1-4-read/pairs.tsv (18 rows).
- **Checks:**
  - both rater copies PASS; 0 Overfull and 0 undefined in both;
  - check_round PASS (the fill test runs on the committed head before the push);
  - make_values PASS (4134); sec4 17/17; pointers 42; registry PASS; check 12 unchanged;
  - check_restyle against f433cd9f7: only the additions (the code line numbers and settings are new numerals in the
    Supplement), and Q11–Q22 as before.

## 2026-11-10 — T1-4's C_model-size ruling; the round-3 note sync (check 12)

- **T1-4 accepted** (the director's read, e00a1176, 18 rows, 3 flagged, all intended). The ruling on C_model's
  carbon-component size: leave it out. E2's CH ratios use the free-proton samples the paper withholds (B5;
  DECISION-20261110-joseph-vprior-withhold.md), so a number built on them would contradict both. S5's qualitative
  sentence stays. Its source comment's "pending the director" now records that reason. GENIE CV's target stays
  unstated; no record found states it.
- **The round-3 sync** (the director's rulings on check 12 against acf934d71). Six Supplement paragraphs now carry the
  note's round-3 text at acf934d71 (#952):
  - item 1: sec:selection #2 (genuine backgrounds);
  - item 3: sec:method-config #7 (hyperparameter choice), the note's paragraph 6 there;
  - item 4: sec:fived16-cov #3 (C_resp);
  - item 5: sec:fived16-pl #0 (C_PL,5D's construction);
  - item 6: sec:fived16-pl #3 (the audit's stopping condition);
  - item 7: sec:uq-combine #0 (the unified throw).
  
  How it was done:
  - The tool is sync3-read/apply_sync3.py. It takes each note paragraph with its comments out of the printed text and
    converts the cross-references to the Supplement's form: a label the Supplement carries (sec:method-algo,
    sec:uq-combine, tab:fived16-groups) stays a local \ref; every other becomes Ref. [note], Sec./App./Table \ref*{N-…}.
  - Each source comment now begins "adapted 2026-11-10: synced to the note's round-3 text at acf934d71, #952, …". It
    has no inner parenthesis, so check 12 reads it as explained against #977's own copy of the note.
  - Every value the note keys is the same key here (\fvval pl-*, sigmed-*, sigratio-*, trace-resp-*). No #981 quote
    lies in the six paragraphs, and the paper's protected spans are untouched.
  - **Item 7's absence sentences** carry an absence-ok waiver: "as the note reports (sec_systematics.tex sec:uq-combine
    at acf934d71); implementation unified_throw_cov.py; …". The note's own copy has no Search line for them; the
    director passes that to the note lane.
  - Items 2 (supp:176, the ESS sentence) and 8 (supp:477, S7's joint throws) are explained by ruling and not synced;
    item 8 moves to the note in T1-5.
  - Check 12 now reads explained 45 against #977's tree; against acf934d71, synced 10 and NOTE-CHANGED 2 (items 2 and 8).
- **Pairs** (base 93cbe7d86): sync3-read/pairs.tsv.
- **Checks:**
  - the Supplement's rater copy PASS, with 0 Overfull and 0 undefined; the paper is unchanged;
  - check_round PASS (the fill test runs on the committed head before the push);
  - make_values PASS; sec4 17/17; pointers 42; registry PASS;
  - check_restyle against 93cbe7d86 shows only the synced text's new citations, refs and the numeral 128 (the note's
    MLP layer sizes), and Q11–Q22 as before.

## 2026-11-10 — Tier 1 batch T1-5 (S7's joint tests to the note)

- **Scope** (the director's ruling of 2026-11-10, item 8): S7 only. tab:gen16 and tab:cmodel16 stay, because #981
  anchors two files on them and Fig. S2 and S10 cite tab:gen16. S9.4's diagnosis stays: the note at acf934d71 does not
  carry it (its numbers 0.986–1.015, 2.72 (0.49–6.51) and MaRES/MaCCQE/MvRES occur in no note .tex there).
- **S7.** It keeps its heading and supp:joint, followed by one pointer sentence to the note's joint-test sections
  (sec:joint5d-design, -calibration, -conditions) and the paragraph moved from the paper (the former Limitation 3 and
  the 11.5 sentence, W-18/W-12), which the note lacks. The note-copied paragraphs and the generative-model table
  (tab:joint5d-genmodel, the old Table S6) are removed; the note carries both (sec_joint.tex at acf934d71). Every
  removed citation and ref was S7's own; the LedoitWolf citation was cited only there. limitation-resolver confirmed
  that #981 has no dependency in S7.
- **Pointers.**
  - S2's \ref{sec:joint5d-design} becomes Ref. [note], Sec. \ref*{N-sec:joint5d-design}.
  - The paper's two \ssec{S7}{supp:joint} pointers stay, as ruled.
  - Removing Table S6 renumbers the later tables down by one. The paper's \stab{S13}{tab:prr-rho} becomes
    \stab{S12}{tab:prr-rho}; check_supp_pointers caught it.
- **For the note lane** (the director sends the list): the S9.4 diagnosis paragraph, the uq-combine Search line, and
  S7's paper-moved paragraph.
- **Pairs** (base ba3dd2138): t1-5-read/pairs.tsv (106 rows). Almost all are base-only removals of the note-copied
  paragraphs.
- **Checks:**
  - both rater copies PASS (15 of 15 table captions); 0 Overfull and 0 undefined in both;
  - check_round PASS (the fill test runs on the committed head before the push);
  - make_values PASS; sec4 17/17; pointers 42; registry PASS;
  - check 12: 47 note-copied paragraphs (S7's eleven are gone), explained 38, same 8, seed-adapted 1;
  - check_restyle shows only the removals and the renumbered pointer.

## 2026-11-10 — T1-5's removal check (M050); Tier 1 complete

- **The director's removal check.** A fresh Sonnet reader took the 39 removed rows that matched the note poorly by word
  shingles, together with the note's sec_joint.tex at acf934d71. It found 36 of 37 fully present in the note. The other
  64 removals matched by shingles.
  - The PARTIAL is M050: "The flux universe and the band universes are drawn independently, and their weight ratios
    multiply." The note states the bands' independence and multiplication, but not the flux universe's independence
    of them.
  - Ruling: keep that one fact in S7. It is now one clause after the pointer sentence, from S7's copy of sec_joint.tex
    sec:joint5d-calibration paragraph 2 (verbatim at ba3dd2138), with its source comment, until the note carries it.
    The director adds it to the note lane's list.
- **Tier 1 is accepted** (T1-0 to T1-5, the round-3 sync and the T2a/T2b additions). #977 waits for the LL5D fill.
- **Checks:** the Supplement's rater copy PASS, with 0 Overfull and 0 undefined; pointers 42; check 12 unchanged. The
  fill test runs on the committed head before the push.

## 2026-11-10 — The style batch (journal-editor's style review; Joseph's decision via the director)

- **The work order** (the director, 2026-11-10). Bring the paper and the Supplement close to the field baseline on the
  excess patterns of journal-editor's review (report_paper.md, report_supplement.md, report_crossdoc.md in its
  scratchpad). Keep every scope limit the records require, said positively or once in the right place. check_restyle's
  protected spans stay verbatim. Cut the repeated coverage caveat, remove the duplicate sentence, name the validity
  rules, split section 6.2 by test and every paragraph over 250 words, trim figures 4 and 6 toward 80 words, and build
  the note pointers against #952's note with a check. The "full record" wording is left alone, pending a consult.
- **Rates per 1,000 words** (style_metrics.py, sha256 8bf224280556ea41, on the PDF text; style-read/metrics-before-after.json):

  | pattern | paper before → after | Supplement before → after | field pooled / max |
  |---|---|---|---|
  | ", not X" | 0.89 (9) → 0.10 (1) | 0.55 (8) → 0.14 (2) | 0.04 / 0.30 |
  | corrective | 0.69 (7) → 0 | 0.27 (4) → 0 | 0.01 / 0.12 |
  | semicolon chains | 0.89 (9) → 0.59 (6) | 1.85 (27) → 0 | 0.17 / 0.67 |

  - What remains in the paper. ", not X": the B0 sentences' "not the typical one" (protected). Semicolon chains: the B0
    sentences and RS1's mechanism paragraph (both protected); the section 7 \pubhold, which a submission does not
    print (2); and two figure legends' "(pT; p∥; Eavail)" labels in the deformation figure, figure text that no source
    edit reaches (2).
  - What remains in the Supplement. ", not X": S2's "five simultaneous observables, not five independent measurements"
    (the review keeps it as a definition) and #981's quote Q09, "The second rule is ours, not taken from Ref. [ATLAS]"
    (protected by check_restyle).
  - Sentences of five words or fewer rose in the paper from 8 to 11. These are the new run-in headings of section 6.2
    and the prior-retention row's short entries, not prose.
- **Scope limits kept.**
  - Coverage. The coverage statement is now said once in the introduction (the third finding), once in section 6.2's
    opening paragraph for every test there ("Each such test grades the procedure's covariance as rebuilt at its truths;
    none grades the reported intervals at the data."), in the abstract and in the limitations. That is four places,
    down from six including the duplicate.
  - Every changed scope sentence was read in the meaning read (style-read/pairs.tsv, 122 rows, base 2f32b7c73).
- **Meaning read** (every pair). Three of my own first drafts were changed by it:
  - M011 "neither choice was blind to it" was wrong for the background treatment, which was chosen before the
    comparison was computed. Now: "it is not a blind validation".
  - M041 "at the held-out tunes" was too narrow for the first five-observable test, which also had a plug-in truth.
    Now: "as rebuilt at its truths".
  - M066 "the total correction is larger" added a comparison. Now: "refers to the genuine-background fraction alone".
- **Named rules.** In the paper: the usage-recommendation rule and the bias-half rule. In S11, under the new title "The
  usage-recommendation and prior-spread rules": the usage-recommendation rule (the first), the prior-spread rule (the
  second) and the bias-half rule. #981's Q09 ("The second rule is ours, …") and Q19 ("Fourteen cells are valid under it;
  R02 and R06 fail") stay verbatim, so S11's opening names the second rule before Q09 uses its number. Q09 is listed for
  the director.
- **Structure.**
  - Section 6.2 is split by test, under the headings "The two-dimensional test.", "Earlier five-observable tests." and
    "The second five-observable test.". The two-dimensional test is split into design, joint result and per-cell
    result; the second test into design and grading.
  - Paper paragraphs split: the introduction (the three findings), section 5.3 (before the IBU), and section 6.1 (the
    probe, then the ensemble average). Section 5.3's three labels are set as a list.
  - Supplement paragraphs split: S4's hyperparameter paragraph, S8's two comparison paragraphs, S9.2's held-out tunes,
    S9.4's design (three paragraphs), S9.5 (three), S10.1 and S11 (three). Lists replace the semicolon chains: C_e's
    terms, the fake-data truths, the audit's four questions, the truth groups and the smaller matrices.
  - In the four test-index tables and the configuration history table, \newline replaces "; " between entries. The
    LL5D row's copy of the paper's Table 2 cell keeps its semicolons.
- **Captions.** Figure 4: 123 → about 88 words; its q3-tilt flag, the identical bias and "assess only bias" are in the
  text. Figure 6: 145 → about 100 words; the 0.37 % median's 50 replicas moved to section 6.1's text, and the
  definition of the 153 quantities is kept.
- **The note pointers (check 13, new).**
  - make_note_labels.py writes note_release_labels.tex: the 50 note labels the paper and the Supplement cite, from the
    main_note.aux of the note at a named revision, built from git archive in a temporary directory.
  - main_paper.tex and main_supplement.tex \input it in place of \externaldocument[N-]{main_note}.
  - check_round.py check 13 fails unless the file names NOTE_RELEASE_REV (acf934d71), the drivers read it and no
    main_note.aux, and every cited label is in it. The fill test rebuilds the file from that revision and compares it
    byte for byte. The self-test plants three defects: another revision named, a driver back on main_note.aux, and a
    cited label missing.
  - Printed now: Table 4 twice (was 3), Table 19 (was 17), Sec. 10.8 (was 10.7) and Sec. 10.7 (was 10.6). The review
    and the work order said 16 → 18; the Supplement printed 17, and the note at acf934d71 numbers the table 19.
  - #952 moved to 3257d7c61 during the batch. Its 217 labels are identical to acf934d71's, so the named revision stands
    until the director names another.
- **Check 12 at #952's new head 3257d7c61** (before the batch): NOTE-CHANGED 1 (supp:176, ruled explained), explained
  27, same 8, seed-adapted 1, synced 10; the same at acf934d71. Unexplained: none.
- **The rater copy.** The shorter paper reflowed its last page. pdftotext emitted reference [1] to part of [8] between
  the acknowledgments and their tail, ahead of DATA AVAILABILITY, which no case of fix_da_order.py described. Case 7
  moves that fragment to before the rest of [8]. It is entered only where the tool exited FAIL before, so no layout that
  passed changes.

## 2026-11-11 — The style batch's fixes (the director's independent meaning read of 9ccb84f6c)

- **Rulings** (the director's Sonnet read of all 122 rows flagged 4; the batch is accepted with them):
  - M013. The paper's lower-capacity variant is now "a lower-capacity development variant with a 100-tree, 8-leaf
    refinement, which gives none of the reported results". The last clause is tab:estimators-matrix's caption. Fig.
    S1's caption is back to its 2f32b7c73 text, with "not the reported estimator", which journal-editor asked to keep.
  - M016. Figure 4's caption again gives the q3 tilt as a truth flagged by its χ² p value under the reported
    covariance.
  - M018. Figure 4's caption again says "The bias is the same in both panels; only the covariance differs."
  - M114. NuWro's reason is back in its record's terms: the abort losses "were not shown to be negligible". "Has not
    been bounded" claimed more than the record does.
  - The named release revision stays acf934d71 until the note loop reports its final head.
- **Meaning read** of the 5 pairs against 9ccb84f6c (style-fix-read/pairs.tsv). M004 and M005 restore the base wording
  exactly; M002 and M003 restore the ruled sentences; M001 is as ruled. No other change.
- **Rates after the fixes** (per 1,000 words). Paper unchanged: 0.10 / 0 / 0.59. Supplement: ", not X" 0.21 (3),
  corrective 0.07 (1), semicolon chains 0.07 (1, Fig. S1's restored caption). All are under the field maximum.
- **Checks:** both rater copies PASS. check_round with the fill test runs on the committed head before the push.

## 2026-11-11 — "Full record" reworded (Joseph's adoption of the independent consult's recommendation, via the director)

- **Paper, section 1's last sentence.** "The supplementary material gives the definitions, and the companion analysis
  note gives the full record" now reads: "The supplementary material provides additional definitions, test designs and
  results. The companion analysis note documents the analysis's development and provides further technical detail in
  the sections cited here." The director's text says "The Supplement". The paper calls it "supplementary material"
  everywhere else, and its \ssec pointers print that form, so the paper's own term is kept. The note's \cite is kept.
- **Supplement opening.** The blanket claim ("Its text is taken from the companion analysis note, which gives the full
  record; …") and supplemental_body.tex's one sentence on shared text are replaced, once, in main_supplement.tex by the
  director's three sentences.
- **The section 7 hold.** Its checklist now lists each record's published place and its record, with the note at
  NOTE_RELEASE_REV (acf934d71). The note carries:
  - the sixteen-cell IBU (10.6);
  - the 2D held-out-tune coverage (5.3);
  - the rounding floor, the probe and the mechanism study (9.3, App. B.2);
  - the two validity rules (10.5). The hold says that this section also prints the prior-spread results the paper
    withholds.
  - Items marked "only" have no counterpart in the note at that revision. The Search line beside the hold gives what was
    searched.
  - The records are printed through \holdrec (\url). check_round's numerals() skips its argument, since the hold prints
    only in drafts.
  - FD-PRR's and LL5D's own record names would print GONE tokens, so the hold cites the prior-retention readout and
    DECISION-20261110-joseph-ll5d-rerun-16-cells.md.
  - The note pointers inside the hold use "the note's section \ref*{N-…}", not \nsec: holddiff.py's hold span ends at
    the first "]", which \nsec's "[14]" would print.
  - note_release_labels.tex is regenerated at acf934d71 (53 labels; --check PASS).
- **Meaning read** (fullrecord-read/pairs.tsv, 22 rows, base 4b02f445d). It caught one defect of my own, which is
  fixed: M003 had kept "The supplementary material gives the definitions," before the new sentence. Every hold item was
  checked against the note at acf934d71.
- **Checks:** both rater copies PASS, with 0 Overfull; pointers 49 (7 new, in the hold); check_round PASS. The paper's
  rates are 0.10 / 0 / 0.49. The fill test runs on the committed head before the push.
- **Correction (2026-11-11).** afdb26f35 was pushed before its fill test had passed, and the test failed: all 31 builds
  printed "joseph" (check 8), from three DECISION file names in the hold. The push was my error, because the push
  command did not wait on the test's exit status. The hold now names those three records by subject ("the decision
  withholding the prior-spread results", "its decision record"), and the source comment beside it gives the exact file
  names. Pushes from now on are gated on the fill test's exit status in the same command.

## 2026-11-11 — The referee recheck's T batch (gpt-6.1-sol, 5/10, on 2bfb1410c)

- **The work order.** The director: Joseph wants every issue resolved, and text fixes are approved under the director's
  authority. RESPONSE.md triages 73 rows (T 61, L 5, A 2, X 1, no action 4) and records the director's rulings and each
  row's status.
- **This batch** is every T row except s7's W-4 sentence (held for Joseph) and the declined s11i and s11k. The paper:
  - eq:xsec, with c ≡ 1;
  - the regressor's equal weights;
  - the 5D universes' weights for unmatched events;
  - C_model as an implementation-specific shape sensitivity;
  - a reference tail area for the fake-data χ², a score;
  - one design sentence;
  - Table 2 reduced to the principal findings, with "No difference detected";
  - §4.1 split, with a new §4.2 "Paired comparisons with other unfoldings";
  - κ dropped;
  - the per-period readings moved to §4.1;
  - §5.1's exact-binned discussion moved to §5.3 with a grid warning;
  - §5.3 reordered, its taxonomy moved to S9.2;
  - "overshoots the truth along the prior-to-truth direction";
  - §5.4 and §5.5 split;
  - physical-unit IBU differences;
  - §6.1 led by the released cells;
  - the ensemble's floor accounting moved to S4;
  - §6.2's conditional-test list;
  - tab:cov2d;
  - the GEANT bands' restriction;
  - the 6 % sentence cut, since the note carries it;
  - §7: the ll5d-status sentence, shortened, with ONCE byte-identical;
  - limitation 8;
  - "sections 6.2 and 6.2" fixed.
- **The Supplement:**
  - tab:bookkeeping;
  - W redundancy;
  - CSV terms;
  - S4's history table as sentences;
  - the regressor;
  - m11b;
  - the lower-capacity background sentence;
  - the ensemble's criterion;
  - tab:construction;
  - the shape-only identity;
  - Fig. S2 (the tension map) and Fig. S3 (prior response) moved in;
  - κ unused;
  - the null's flux block and thresholds;
  - S9.1 removed, with a note pointer;
  - the q3 stress tilt named;
  - S9.2's classes and labels;
  - the S9.5 GEANT sentence;
  - the S10 diagonal fraction;
  - \clearpage before the references.
- **Tools:**
  - check_supp_pointers.py now checks subsection pointers. It used to match whole numbers only; the fix caught four
    stale pointers in the hold.
  - check_sec4_receipts.py's anchor moved to sec_5d.tex (17/17).
  - make_supp_rater_copy.sh counts figure captions; it fails on 2bfb1410c's sources, as it should.
  - The abstract's longest case is 248 words.
- **Meaning read** (referee4-read/pairs.tsv, 233 rows: 60 verbatim moves, the rest read). It caught three defects of my
  own, all fixed:
  - an inserted comment in S8 swallowed two sentences ("No step of the bootstrap uses the realized Δ" and the Hotelling
    self-check);
  - §5.3's IBU test lost its "or rises";
  - S4's folded history dropped (b)'s "exact-split studies have not been recomputed".
- **Second batch (2026-11-11).**
  - s7: the W-4 sentence is cut, by Joseph's decision ("Cut it (Recommended)"; DECISION-20261111-joseph-bv-sentence-cut.md, to merge).
  - 1.4: the C_resp factors are in S5. Both checks passed: the readout's code pin equals main's build_cresp.py, and xtalk is a variant.
  - m7: λ⁻¹/(fᵀC⁻¹f) < 3×10⁻⁵, in S5.
  - The pscratch L rows wait for Perlmutter (RESPONSE.md, "Second batch").

## 2026-11-11 — The fresh referee read's T batch (gpt-6.1-sol, 5/10, on 9ab00ec9)

- **RESPONSE.md section F:** 58 rows plus 8 §4 rows (T 46, L 6, A 5, X 1), with the prices of F1, F2 and F3 and each
  row's status.
- **New keys:** c2c1-dibu (1.03), c2c1-dibu-k5 (0.83), c2c1-der (2.27), from read-2/readout.json (0ee21301);
  rnd16-r0a-median, -min and -max (0.51, 0.39–0.82), from rs1_r0.json (724f0c3a).
- **Structure:**
  - S7 is folded into S3, so S8–S11 are now S7–S10.
  - In §6.2 the second test precedes the first.
  - §7 leads with the findings; §7.1 is grouped.
  - §5.5 becomes a paragraph of §5.2, with sec:vhalf on §5.2.
- **Meaning read** (fresh-read/pairs.tsv, 142 rows, 34 verbatim moves). It caught three defects of mine, all fixed:
  - "It was background to the second test." said nothing; it now says what the first test's checks led to.
  - The S5 interval sentences preceded the block's introduction.
  - The masking-convention phrase attached to the wrong clause.
- **D_IBU, Fm1, Fm5 (2026-11-11).**
  - The PRD-referee read of the D_IBU paragraph (dibu-read/referee-read.md) returned ACCEPT WITH CHANGES; the director ruled the read's wording, under Joseph's decision.
  - New keys c2c1-dibu-k1, -k20, -mid-lo and -mid-hi (D_IBU_every_K; make_values asserts the K = 2–15 range stays below D_E_R).
  - "source" → "mechanism" in §1, §4.1, §7, Table 2 and the abstract; the abstract's longest case is 244 words.
  - Meaning read: dibu-read/pairs.tsv, 16 rows, as ruled.

## 2026-11-12 — The L rows: the read-only pscratch session and its fills

- **Session:** run under the director's go on login27 (0 node-h, fence clear). Receipt `pscr-20261112/` (f70e805c).
  The director accepted the recompressed truth member, the two force-added npz, the hook-key renames and m5's
  definition (s5n_truth_check's full-sample M1 ratio).
- **New keys (14):**
  - f53-win, f53-grid (not printed);
  - f54-truth, f54-reco;
  - bkg42-frac, -pl-lo, -pl-hi;
  - bkg43-n, -share, -frac, -rho;
  - r33-dchi2-max, -z-from, -z-to.
  - All come from `l-rows-20261112/derived/l_rows.json` (READOUTS lrows 9bd9afeb), and values_fived16.tex now holds
    4158 values.
- **Printed:**
  - F5.4 in §2;
  - F5.3, the window fraction only, in S2;
  - 4.2/F4.3 as a new row of table S1 (the combined template; its split is not recorded);
  - 4.3 before fig:tension2d in S6;
  - 3.3 in S8's T2B paragraph.
- **Meaning read:** lrows-read/pairs.tsv, 5 rows, by an independent reader given the sources. Every number was
  re-derived. One defect: M003's gen-side clause contradicted S3 :148 and overlapped the negative-W² exclusion, so it
  was removed and goes back to the director. Two wordings were tightened. The re-read passed all three revised rows.
- **F5.3's "zero weight":** checked in code. In s5c_pseudo.py :104-112 (d81d4f46) the pseudo-data's measured weight
  outside the window is 0, while the MC rows enter at w_reco. So OUTCOME-20260925 :37 is right for what it describes,
  and no records correction is needed.
- **Waiting:**
  - m5/s11c's figure series, routed to the figure lane by the director;
  - the 4.2 split probe, whose script sha goes to the director first;
  - 1.5's CSVs, which are #981's release item.

## 2026-11-12 — Figure 3: m5/Fm7 and s11c; the 4.2 split STOP; table S1's composition wording

- **Split probe:** exit 6 (split-20261112/, 74cb1adc). None of the twelve May files carries the bkg_* branches.
  Provenance search, read-only: the May files and the merged CV were made with the Phase-18 routing, run before
  d1bc8813a was committed. The C++ behind $UNI was never committed. The run log says the out-of-phase-space set is
  empty (2D_OMNIFOLD_RUN_LOG.md :1002-1009), and the template's composition is not settled. S2 :222, S1 :25 and table
  S1's out-of-phase-space row are held for the director. Wording under three outcomes was sent.
- **Table S1, new row:** now reads "its composition is not recorded" (the director's ruling).
- **Figure 3**, by the director's routing ruling; the producer has no OWNER line, no other open PR touches it, and no
  figures-lane session is live. It now draws the withheld shapes' injected changes from m5_injected.json, the reported
  estimator at the GiBUU-to-GENIE change with its injected change, and the three unsupported cells shaded.
  presentation_original_arrays.json gains two asserted arrays, with their sources recorded in its additions block, and
  inputs.json re-pins it. New keys fm7-tw-lo and -hi; 4160 values.
- **Bound fix:** s5e-shapes-semax printed a rounded-down upper bound ("at most 0.22" for 0.2246). Both semax keys now
  round up, and make_values asserts each covers its maximum.
- **Meaning read:** fig3-read/pairs.tsv, by an independent reader given the figure and sources. Two defects:
  - :266's "three shape changes", now "three withheld … the GiBUU-to-GENIE change … is a development truth";
  - the caption's "100 half samples" did not say which pseudo-experiments they are; it now names the 60 and the 40.
  Fixed, and the re-read passed all five revised rows. Both rater copies were rebuilt (hold diff PASS).

## 2026-11-12 — The background wording (the director's rulings on the provenance search and the reconciliation)

- **S1 paragraph (:26):** DESYNCED from the note, with the reason at :24 (the note's 0.35 % describes the April template).
  The 0.35 % sentence and the sentences resting on it are deleted, as is the self-referential "This paragraph does not
  split …". Out-of-phase-space signal is now "routed into the background template", and their sum N_bkg(b) "enters
  the purity weight". The note is unchanged; its fix goes to Joseph.
- **Table S1:** <!-- absence-ok: quotes table S1's scope clause; the split is unmeasured here because the May files lack the truth branches (split-20261112, exit 6), and C-BKG measures it --> the 0.35 % row is deleted. The template row reads "2.91 % of selected data events … its split … is not
  measured here". The out-of-phase-space row reads "routed into the background template and subtracted with it".
- **S4 (:223, :229):** "background template comprises all selected simulated events other than signal inside the phase
  space". :229's pointer to S1 is removed.
- **Kept "playlist":** "run period" already names the three groups (:478, :481), so the twelve stay playlists.
- **Readout:** l_rows.json bkg_42 gains per_playlist_template_sum. The 1A sum, 9,781.53, matches RUN_LOG :1061's 9,782,
  and the values are unchanged.
- **Reads:** bkg-read/referee-read.md records two PRD-referee reads and two meaning reads, with their defects and fixes.
  The final confirmations are ACCEPT and OK.
- **RESPONSE.md 4.2:** the Set E record (about 82 % weighted on 1A) is entered as a record, not a measurement.
  C-BKG in the F1.2(i) pilot measures it.
- **Corrections:** two section labels in RESPONSE.md and the ledger: :222 is in S4, :148 is in S3.

## 2026-11-12 — The figure referee read: check A, the median-framing rewrite and the figure fixes

- **Record:** secondary-results/referee-figure-deformation-20261112/ (32ac4b76): the consult (gpt-6.1-sol, high) and
  check A (a_recovery.py, READOUTS recov). In EW29 the unfolded cell moves opposite to the change for GiBUU, W1 and W3.
  The median f is 56–88 %, and 0–12 cells are opposite and 1–10 overshoot per truth (supported cells with |i| > 2 %).
  σ_f ≤ 0.04, and 7 cells lie within 3σ of a class boundary.
- **Paper:**
  - §5.1 paras 1–2 now state the median and the spread; EW29 is −30 % injected against +21 % unfolded.
  - The withheld shapes' maximum is over supported cells, 9–31 % (the old 16 % was EW37, unsupported).
  - Table 2's status word is "Mixed per cell".
  - §5.4's first finding has a named IBU referent (S7 :588).
  - §7.1's limitation is scoped to fig:deformation's four changes and the sixteen-cell grades.
  - The introduction is qualified. The abstract is held for the director.
- **Supplement:** supp:recovery gives the definitions, and tab:recovery the four truths with near f = 0 and near f = 1.
  S4 :340 now reads "cell by cell".
- **Figure (B1–B6):**
  - four line patterns, each with its own legend sample;
  - a darker green; outlined markers;
  - the legend above the axes; hatched shading;
  - the title moved to the caption; a W-bin key;
  - the caption's marker and error-bar sentence replaced.
- **Checks:**
  - check_sec4_receipts recomputes the supported-cell range; its anchor and test mutation were updated, and 17 tests pass.
  - NEW_NUMERALS has the W-bin edges 1.1, 1.8 and 2.2.
  - 4206 values.
- **Reads:** recov-read/referee-read.md records two PRD reads and two meaning reads, ending ACCEPT and OK.
- **Sweep:** RESPONSE.md, "The figure referee read and check A", lists every site and its disposition.
