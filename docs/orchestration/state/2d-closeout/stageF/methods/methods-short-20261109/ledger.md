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
| L-28 | §5.4, Table 1 | the IBU bars as "the 95th and 99.7th percentiles of its null, 28.12 and 39.04" | r5:176 ("28.12 (0.95) and 39.04 (0.997)") | the editor's B8 |
| L-29 | §1 | **W-22 draft:** the motivation for the joint unbinned approach, with "this study does not test whether that gain is realized" | the intro (r5:13); S4 `sec:method-algo` ("any binning chosen afterwards") | motivation only; see W-OPTIONS.md |
| L-30 | §5.1, Fig. 3 | panel (a)'s estimator named, with why: the configuration with which the generator-sized-change study ran; the reported estimator's result at the same truth, the sixteen cells: largest \|z\| 1.76, flagged without C_PL,5D | S4 (configurations (c) and (d) "serve the … generator-sized-change … studies"); Table 2's GiBUU E_avail shape row (`f0b-stage0c_gibuu-*`); r5:272 | the director's round-6 item 3. The note gives no reported-estimator (E_avail, W) residual at this change (`sec_5d.tex:57-63`), so none is printed |
| L-31 | §2, §5.2, §7 | "diagonal fraction" in place of "reconstruction stability", defined in §2; the three run-period groups defined in §2; the publication reports 205 of the 224 bins | `h2_definition.json` via `h2-lowstab-*` (r5:339); S5 (`sec:fived16-pl`, "playlists 1A–1F, 1G–1M and 1N–1P"); S3 (the note's `sec:205bins`) | the editor's B2 and B6 |

**Numerals new to the base** (`check_round.py` NEW_NUMERALS): 136 and 285 (row L-12b), 0.05 and 9.03 (L-27), and 99.7 (L-28). Every other numeral
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
