# The referee presentation round (2026-11-04)

Joseph approved this round from the two-referee read, and the director issued the work order the same day. The read
is `secondary-results/referee-rerun-20261104/` (#757): `sonnet-referee-answer.txt` §§3 and 6, and
`gemini-referee-answer.txt`.

The round is presentation only. No result, covariance or claim changes, and every fact stays in the paper plus the note.
Branch `docs/referee-presentation-20261104`, from main `c5e42840a`.

**Before this goes to Joseph:** the director's PRD-referee read of the changed wording. The item-1 wording and the item-4
abstract are Joseph's to approve. The abstract is a **draft**.

## What changes

| item | referee | change | where |
|---|---|---|---|
| 1 | Sonnet Major 9, minor 12 | The contradiction resolved: the two sentences are about two different choices (below) | paper Sec. III, IV B; note sec:method-config |
| 2 | Sonnet Major 12, minors 7, 9, 10 | New Appendix A, "Uncertainty tables": the systematic groups defined, "lateral" included; the per-group uncertainty table; the 16×16 correlation matrix. "Lateral" defined at first use in IV A. The flux integral and range in Sec. II | paper |
| 3 | Sonnet minor 1 | Jargon defined at first use or replaced | paper |
| 4 | Sonnet minor 2 | Abstract: the χ² range presented as descriptive; "predeclared" becomes "fixed in advance" (draft) | main_paper.tex |
| 5 | Sonnet minor 4 | Table I: the two closure truths marked; "listed" becomes "flagged"; the text says the table lists all twelve | paper IV G |
| 6 | Sonnet minor 3 | Noise-level precision rounded in the paper; the note keeps the exact values | paper Table I, IV G, V B |
| 7 | Sonnet minor 13, Gemini | Fig. 2's caption says that neither panel is the reported result or covariance; the moves are proposed below, none made | paper Fig. 2 |
| 8 | Sonnet minor 14 | The 2D χ²/ndf with the pseudo-inverse at condition number 1.5×10¹² is said to be descriptive, with no p-value | paper IV B |

The paper grows from 11 to 13 pages, the appendix adding about a page. After PRD read 1, Figs. 1 and 2 are defined
before Sec. IV B and the appendix has no page break of its own; see "After PRD read 1" and Checks.

## Item 1: the contradiction, from the records

The two sentences are about different choices.

**(a) The learner settings were not tuned on data.** Sec. III's sentence is about these.
- The nominal settings are "fixed a priori": the GradientBoosting defaults, with LightGBM at matched capacity
  (`sec_method.tex:149`, from the advisor round, 242e996c6, 2026-07-04).
- The refinement capacity (400 trees, 31 leaves) was chosen on simulation closure (`app_negweight.tex:179`). Both
  estimators share it (paper :55).
- The joint-test estimator's five iterations were set by a rule fixed before the comparison, over simulated development
  truths (`sec_5d.tex:136`).
- The two-observable estimator's five iterations follow common practice (`sec_method.tex:151`: "typically uses ~5"). That
  count is "justified empirically" by two data checks: the 5-vs-10 total, measured with purity-based subtraction (the
  exact-split cross-check gives 0.026 %; the LightGBM seed-1 χ² moves by +0.01), and the published reproduction. There
  was no search. On the director's caution, it is not called "fixed in advance" or "chosen in simulation".

**(b) The learner implementation of the 2D central value was chosen after both comparisons with the published result.**
IV B's sentence is about this.
- `docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md`:
  - :3, Joseph: "switch to the LightGBM central value";
  - :20, the settings are unchanged;
  - :73-74, Disclosure 1: "decided after both learners' comparisons with the publication were known, and it lowers the
    published-covariance χ²/ndf from 3.66 to 2.65";
  - :28 and :32, seed 42 was chosen by matching cost, "not by the central values", and ranks 4th of 11.

**(c) The 2D background treatment.** This goes in the note and this REPORT only (director), not the paper.
- It was decided on the C2 simulation closure (`DECISION-20261023-joseph-2d-refined-integrate-ci.md` :5-7 and item 1).
  On data, only the shift of at most 0.497 σ_total was known then.
- The refined result's published-covariance χ²/ndf of 2.27 first appears in `RE2-PARTC-REPORT.md` :190 (3c2c3c0c6,
  2026-10-24).
- The adoption came after it (`DECISION-20261024-joseph-adopt-re2-2d-refined.md`).
- RE1-REPORT-2 has no published-covariance χ² for the refined 2D. Its only check against the published result is a plain
  content sum (:24, :352).

**Before (Sec. III):**
> The nominal settings are the scikit-learn defaults, with LightGBM matched to their capacity. The refinement capacity of
> the joint-test estimator was chosen in simulation closure studies. No hyperparameter search was performed on data.

**After (Sec. III):**
> No learner setting, whether capacity, learning rate, refinement capacity or iteration count, was tuned on data. The
> nominal settings are the scikit-learn defaults, with LightGBM matched to their capacity. The refinement capacity,
> which the two estimators share, was chosen in simulation closure studies, and so were the joint-test estimator's five
> iterations (below). The two-observable estimator uses five iterations following common practice; this choice was
> checked on data, against ten iterations with purity-based subtraction and against the published result, without a
> search over the iteration count (Ref. [14], Sec. 3.2). Which learner implementation gives the two-dimensional central
> value, at these settings, was chosen after the implementations had been compared with the published result
> (Sec. IV B).

**Before (IV B):**
> The comparison is a consistency benchmark, not a blind validation: the learner was chosen after the LightGBM and
> exact-split results had been compared with the published result, and the distance depends on the estimator.

**After (IV B):**
> The comparison is a consistency benchmark, not a blind validation: LightGBM, rather than the scikit-learn exact-split
> estimator at the same settings, was chosen after both had been compared with the published result, a choice that
> lowered χ²/ndf from 3.66 to 2.65 (both with purity-based subtraction), and the distance depends on the estimator.

**Note, sec:method-config (added after "…found the purity bias"):**
> The change was decided on that closure test, before the rebuilt result's distance from the published result was
> computed, and the rebuilt result was adopted after that distance was known.

The 3.66 and 2.65 print through `\chiPaperExact` and `\chiPaperPurity` (values.tex:48, :81).

## Item 2: Appendix A, "Uncertainty tables"

The director chose option (a), a new appendix before the Acknowledgments. Nothing in it is a new value.

**The source list** follows `nd-unfolding/s1_assemble.py:55-60` at fe5d79c61 and the note's definitions:
- statistical: 50 bootstrap replicas;
- flux: 100 PPFX universes, weighted by the ν-e and IMD constraint, effective number 19;
- interaction: 33 GENIE bands, Rvp1pi not included;
- detector: 4 bands, MINOS matching efficiency and the GEANT4 neutron, pion and proton reweights;
- lateral: 5 bands that shift reconstructed kinematics (beam angle x and y, muon resolution, muon energy in MINERvA and
  in MINOS);
- normalization: 1.40 %;
- C_model, C_resp and C_PL,5D, as in Sec. IV A.

`make_values_fived16.py` reads s1_assemble.py's constants from its pinned source (as readout `s1code`, sha256
`b157250a…`, parsed, never imported). It asserts:
- the detector and lateral sets the appendix names;
- the counts against the S1 readout's meta.blocks;
- that the normalization is 1.40 % in every cell.

**Table IV** gives per-cell relative σ for stat, flux, interaction, detector, lateral, normalization, C_e, C_model,
C_resp, C_PL,5D and the reported total, with a median row. These are the note's tab:fived16-groups and
tab:fived16-cells keys.

**Table V** is the correlation matrix (the note's tab:fived16-corr keys). Sec. IV A's and V A's pointers to the note's
tables now point to these. The note's cells table is still cited for the uncertainties without C_PL,5D.

**Sec. II** prints the flux integral and range: Φ = 6.243×10⁻⁸ cm⁻² per POT, 0–100 GeV, after the ν-e constraint and
averaged over the twelve playlists by exposure. The sources are `sec_method.tex:186` and
`state/s5p/gen5d/README-gen5d-fluxfix.md` :43-49 and :74.

**Requests not met:**
- **The background composition table** (Sonnet minor 9). The note gives only a total, 0.35 % of selected events on
  playlist 1A, with its categories (sec_experiment.tex). I found no committed receipt for that number. Its sources are
  commit 242e996c6's message ("verified numbers (0.35% = playlist-1A genuine-only …)") and a plot,
  `2d-unfolding/PLOT_GUIDE.md:91` (`plot_minos_fix_bkg_fraction.py`). No per-category breakdown is committed. The paper
  is unchanged here (director: only with its receipt).
- **The size of the flux constraint** (Sonnet minor 10). It is not committed for these results, so it is not printed
  (director).

## Item 3: jargon

| term | first use | change |
|---|---|---|
| gate | Limitation 1 | "stopped at one of its gates" becomes "stopped by one of its preliminary checks" |
| predeclared | abstract | becomes "fixed in advance" (item 4's draft) |
| stopping criterion fixed in advance | IV A | becomes "stopping condition was fixed before any of its numbers were read" (`sec_fived16.tex:180`) |
| joint cells | Sec. II | "…, on which the note's joint tests are evaluated" |
| joint-test estimator | Sec. III | "named for the note's calibrated joint tests of generator predictions, which use it"; the later duplicate clause is dropped |
| support rule | Sec. II | already defined there ("We call this requirement the support rule"); kept, because the note and the note's records use the name |
| hybrid truth | IV G | "each equal to a generator prediction in every cell of the fine grid and to the MINERvA Tune v1 simulation's event composition within each cell" (sec_joint.tex sec:joint5d-design) |
| development variant | IV E | "used while the joint-test estimator was developed, with a 100-tree, 8-leaf refinement, not the reported estimator" |
| lateral | IV A | defined at first use, with the appendix's list |
| playlists | Sec. II | "(playlists 1A–1G and 1L–1P)" at the run periods |
| V_g | IV A | "the diagonal covariance from the finite size of the prediction's own simulated sample" |
| purity-based | Sec. III | already defined at first use (the w_pur equation); unchanged |

Gemini's suggestion to rename the support rule a "phase-space occupancy criterion" is not taken, because the note, its
tables and the records use "support rule". This is noted for the PRD read.

## Item 4: the abstract (a draft for the PRD read and Joseph)

**Before:**
> Three external generator predictions give χ² values of 107–229 for 16 degrees of freedom; GiBUU gives 48 on the eight
> cells covered by its sample. … Fake-data studies find residual bias exceeding predeclared uncertainty-based thresholds
> at a GiBUU-like truth and a synthetic momentum-transfer tilt.

**After (draft):**
> As a descriptive comparison, three external generator predictions give χ² values of 107–229 for 16 degrees of
> freedom; GiBUU gives 48 on the eight cells covered by its sample. … Fake-data studies find residual bias exceeding
> uncertainty-based thresholds fixed in advance at a GiBUU-like truth and a synthetic momentum-transfer tilt.

`check_round.py` pins main_paper.tex to its base with exactly these two replacements. The note's abstract is unchanged:
it is under its own pinned pairs (#536), and the work order names the paper.

## Item 5: Table I

- The simulation prior and the Tune v1 hybrid are marked * with the note "Closure test: the truth is the simulation's
  own". Records: the note's "prior truths" (sec:fived16-fd), FD-F0-DECLARATION.md :287, and sec_joint.tex: for the Tune
  v1 "no external prediction is combined with the Tune v1 composition".
- Sonnet counts a third trivial truth, the noise-free NuWro closure. It is a closure at a NuWro shape, not at the prior,
  and its χ² is 11, so it is not marked.
- "A truth is listed when …" became "A truth is flagged when …; Table I lists all 12 truths". "The listed truths" and
  "the listing criterion" follow, as does "fake-data listing" in IV A.
- The generator's LISTED_CLAIMS anchors follow the new wording. Its self-test mutations were updated with it.
- Sonnet's "Say how the GiBUU hybrid is built above 20 GeV" is not addressed. It needs a statement this round has no
  committed source for, so it is listed for the director.

## Item 6: precision

- Table I's χ² prints as integers, as Table III's do (DECISION-20261027-joseph-chi2-table-format.md: "109/16").
- Its p-values below 10⁻³ print as the power of ten they lie below: 5.3×10⁻²⁸ becomes <10⁻²⁷, and 9.1×10⁻⁶ becomes
  <10⁻⁵. The text's "p = …" follows (`-prel` keys).
- IV G's two tunes' χ² print as integers.
- V B's C_model sensitivities print to one decimal (−0.92 becomes −0.9, …, +119.05 becomes +119.0).
- V B's string "45.1, against 45.5 … 44.2 … 45.3 … 47.5" is replaced by the two directions it shows. `check_round.py`
  asserts both in the values:
  - with C_model's ratios from CH, GiBUU's total falls below its carbon value (45.10 < 45.49);
  - with GENIE's hydrogen, it also falls below its carbon value (44.19 < 45.25).
- The values stay in the note (sec_fived16.tex :393, :397).

**How the keys are made.** `make_values_fived16.py` makes every paper key: `-chi2int`, `-pr`, `-prel` and `-dchr1`,
`-dx2r1`, `-dx0r1`.
- The graded truths' χ² integers and the sensitivities come from the raw values.
- The other keys are derived from the printed two-decimal values. A value printed at x.50 gets no integer key, so a
  paper that printed one would stop the build. One did: W2's 0.50, which is now rounded from the raw value instead.
- The values file gains 558 keys, and no existing value changed (`git diff` of values_fived16.tex has no removed line).

## Item 7: non-reported estimators

**Fig. 2's caption** now says:
- that neither panel shows the sixteen-cell result or its reported covariance;
- that (a) is "not the reported estimator";
- that (b)'s band is "not the reported covariance".

**Proposed moves to the note.** Nothing has been moved. They are for your decision:
1. Fig. 2a, the development variant with the GiBUU/GENIE change, and the IV E sentence that reports it (the 74 %).
   This would keep Fig. 2b, which is the reported estimator.
2. IV E's last paragraph, on the coverage of an earlier purity-subtracted five-observable estimator, as low as 0.06. It
   is not the reported estimator, and Limitation 1 states the coverage position.
3. IV F's clause on the lower-capacity development variant ("and those of the lower-capacity development variant by up
   to 2.5").

Each item's facts are already in the note (sec:val-negweight, sec:val-departure, sec:coverage-5d). The SEC4 receipt
checker binds the 74 % and the 0.06 to the paper. A move would therefore need `check_sec4_receipts.py` repointed.

## Item 8: the 2D χ²/ndf

The director cautioned after #760 (merged 0e1dd76a): the code defines ndf as the bin count, not the rank.

*Before:*
> It is computed with the pseudo-inverse over the 205 bins, which keeps all 205 eigenmodes (rank 205, condition number
> 1.5×10¹²), and ndf is that rank.

*After:*
> It is computed with the pseudo-inverse over the 205 reported bins, which keeps all 205 eigenmodes of the published
> covariance (condition number 1.5×10¹²), and ndf is the number of reported bins. The value is descriptive, and no
> p-value is quoted for it.

The sources:
- `2d-unfolding/compare_to_paper_fullcov.py:99`: `ndf = n_keep`, the positive-diagonal bins;
- the RE-2 tension receipt, :5 ("reported bins: 205") and :13 ("cond(V) = 1.47e+12 rank(lam>0) = 205/205 modes kept
  by pinv (rcond=1e-15) = 205");
- diagnosis-three-items-20261104/REPORT.md B1, for "descriptive".

The first draft gave a reason, "With a condition number this large, …". It is dropped: no record gives the condition
number as the reason. #760 gives shared data and systematics instead.

## Joseph's three additions (DECISION-20261104-joseph-referee-analysis-commission.md, #759 at 1a87d209a)

The same process applies: the PRD-referee read, then Joseph before merge (that decision, item 4).

**1. Table II flags the four low-stability cells** (item 3).
- R02, R06, R10 and R15 carry a dagger.
- The caption adds "†Reconstruction stability 0.16–0.25 (Sec. VI A, item 2)".
- All 16 cells stay as reported.
- `check_round.py` requires the flagged rows to be exactly `h2-lowstab-cells`.

**2. b0, the 3b closures as a bounded statement** (item 1; the decision: descriptive, with no pass threshold).

*Before (IV G, the tunes paragraph):*
> The simulated detector response is not probed.

*After:*
> The simulated detector response is not varied in these tests. Separate noise-free closures at the nominal truth,
> with pseudo-data from a simulation whose reconstructed recoil response is shifted and the unfolding on the nominal
> response, move the sixteen cells by at most 0.40σ when each deposit category of C_resp is shifted by its ±1σ, and by
> a median of 0.50σ (at most 0.97σ) when the whole recoil energy is scaled by ±4 %, with σ the per-cell uncertainty of
> C_total + C_resp. These closures are descriptive: no pass threshold is set, and they do not establish the bias under
> the true detector response (Ref. [14], App. response-mismatch).

The sources:
- `FD-CT-3B-REPORT.md` :79 (no threshold), :96-118 (the table) and :18-22 (NOT CITABLE FOR);
- the readout `fd/readout/fd_ct_mismatch.json` (14399419), now pinned in make_values_fived16.py, which asserts its
  schema, cells, controls, labels and variant set;
- σ is defined at FD-CT-3B-DECLARATION.md :75;
- 0.50 is the larger of the two ±4 % medians (0.496 and 0.463), and 0.97 the larger maximum.

The note's response-mismatch appendix had said "implemented but not yet run". That clause is now scoped to the
reconstruction-only test it describes, and keeps the base's claim as written. I did not re-verify that claim. A tree
search for the test's flag and output name finds `state/result-20260923-issue26-issue5/scale-logs/NONQUOTABLE-DIAGNOSTIC.eavscale.*`.
Those scale E_avail in both the simulation and the data (`scale_mc` = `scale_data` = 1.1 in c3_p10), so they are a
different study from the pseudo-data-only closure. A new paragraph gives the 3b closures:
- medians 0.07–0.20 and largest 0.40 for the deposit categories;
- median at most 0.50 and largest 0.97 for the ±4 % scale;
- the scope limits, from the NOT CITABLE FOR list.

**3. The bias attribution** (item 1: "corrected to what D-ID and IBU-1 show").

*Before (IV E):*
> We interpret the residual as regularization bias, because it persists over the tested iteration numbers and
> classifier capacities, although no single cause is established.

*After:*
> In a noise-free comparison in simulation, an exact binned iterative unfolding of the same development truth changes
> leaves about the same median residual at five iterations; longer exact iteration removes much of the residual of the
> GiBUU-to-GENIE change (from 8.3 % at five iterations to 3.3 % at 200) but not of a NuWro (p_T, p_∥, E_avail) shape or
> a q3 stress test. The residual is therefore consistent with finite-iteration regularization for the GiBUU-like
> change, but not for every change tested, and no single cause is established (Ref. [14], Sec. val-departure).

*Sec. VI's echo:* "…which we interpret as regularization bias" becomes "…which for the GiBUU-like change is consistent
with finite-iteration regularization".

The sources are D-ID (`next-preparation-20261009/d-id/REPORT.md` :432-452, :524-529) as the note states it
(`sec_5d.tex:84`). "Not of" W3 and q3 follows the note's "It does not do so for W3 and the q3 stress". W3's median at
K = 200 is 4.4 %, against 4.9 % at K = 5, and 8.9 % after 10⁵ iterations. So "does not fall", the scope report's
phrase, is not used.

**IBU-1 is not printed** (`stageF/methods/ibu1/REPORT.md` :57-60: with pseudo-data noise and template background, IBU's
median residual is 0.77–1.31 × OmniFold's). The note does not carry IBU-1, and the round keeps every printed fact in the
note. If you want IBU-1 cited, it needs one note sentence (sec:val-departure) and one paper clause, and I can add both.

## After PRD read 1 (prd-read-1/; the director's rulings R1–R10)

The read is committed verbatim in `prd-read-1/`: prompt.md, answer.md (as answer.txt; prd-read-1/README.md), tex.diff, the reading copy and its SHA256SUMS,
with answer sha256 69374629…. tex.diff is `git diff ff6ba1885 e24ad2cc1 -- 'docs/analysis-note/*.tex'` (checked by
regenerating it). The verdict is still major revision, and the director expected that: the top three issues are
substance. Every number below was checked against its producer before the text changed.

**R1. Table I against IV G.** The base already had this defect before the round.
- z = 2.01 and 1.76 are F0b's R06 without and with the run-period block: fd/readout/fd_f0b_readout.json (b9db935a)
  and fd/with-cpl/readout/fd_f0b_readout.json (5f542830). F0b's matrix is C_total + C_resp.
- Table I's right-hand columns are F0 (fd/readout/fd_f0_readout.json, 6e7d718b), under C_total alone. Its
  triggers.listed is W3, q3, stage0c_gibuu and A7_gibuu.
- The base text named the without-block list ("Without C_PL,5D, …") beside a table whose second column is C_total, and
  it never named W3, which C_total flags (p = 0.0027).

*Before:*
> Without C_PL,5D, the GiBUU E_avail shape also meets the flagging criterion, in cell R06 (z = 2.01, against 1.76 with
> the block).

*After:*
> Under C_total + C_resp, the covariance without C_PL,5D, which Table I does not show, the GiBUU E_avail shape also
> meets the flagging criterion, in cell R06 (z = 2.01, against 1.76 with the block). … Under C_total alone, the
> right-hand columns of Table I, the flagged truths are the GiBUU hybrid truth, the GiBUU E_avail shape (cell R06,
> p = 0.0031), the synthetic q3 tilt and the NuWro (p_T, p_∥, E_avail) shape, the last by p alone (p = 0.0027).

`make_values_fived16.py`'s LISTED_CLAIMS gains a kind, "ctotal": the sentence's typed truths must equal F0's listed
set. Its self-test plants an omission, and the check catches it.

The note's sec:fived16-fd was already right: its table prints all three covariances, and its text names only the
reported and without-block lists. It is unchanged.

**R2. Table III's 229/229 and 262/262 are real, not a transcription error.**
- The Stage G readout fd_g_readout.json (a19009e0) gives GENIE + MEC 229.09 total against 229.00 shape-only, and
  Tune v1 262.06 against 261.88.
- `prd-read-1/r2_check.py` (output R2-CHECK.txt) reproduces all four 16-cell predictions' χ² from the committed matrix
  and vectors.
- The drop from freeing the normalization is, by construction, the residual's squared component along f in C⁻¹'s
  metric. Here it is 0.09 and 0.18. The GLS scales of f − g along f are −0.013 and −0.018 (±0.04), although g < f in
  13 and 14 of the 16 cells.

*Added (V B):*
> For GENIE + MEC and the Tune v1, the shape-only χ² is within one unit of the total, although Fig. 3 shows both
> predictions below the data in most cells: freeing the normalization lowers χ² only by the residual's component along
> the result's own cell values in the metric of the reported covariance, and for these two predictions that component
> is small.

check_round.py asserts both halves, from the values and the readout. No number is added to the paper.

**R3. "Fixed in advance" (for Joseph: pick one).**
- *(a), now in the source.* IV G adds "these criteria were fixed before any of the tests was graded against them",
  and the note's sec:fived16-fd adds the same clause.
  - The record is `state/measurement-paper/5d-community-20261024/FD-DIRECTOR-RULINGS.md` §2 ("|z| > 2 per cell; or
    a χ² with P(χ²_16 > χ²_T) < 0.01 per truth"). It was committed at 092702292 (2026-10-25 10:32 −0700), and the
    file's sha256 begins 2bfba459806310a3; it is unchanged since.
  - That precedes F0's declaration (7d7dac1d3, 13:43) and F0's report (28c4870f4, 15:04). F0b and F1 reuse the
    criteria unchanged.
  - The abstract keeps "uncertainty-based thresholds fixed in advance".
- *(b).* Drop the clause from IV G and the note, and the abstract reads "Fake-data studies find residual bias exceeding
  uncertainty-based thresholds at a GiBUU-like truth and a synthetic momentum-transfer tilt."

**R4. The learner and background choices (a draft for Joseph).**

*Sec. III, before:*
> Which learner implementation gives the two-dimensional central value, at these settings, was chosen after the
> implementations had been compared with the published result (Sec. IV B).

*Sec. III, after:*
> Two choices for the two-dimensional result are not learner settings: its learner implementation was chosen, and its
> background treatment adopted, after the comparison with the published result was known (Sec. IV B).

*IV B, added after the LightGBM clause:*
> The refined negative-weight background treatment of the quoted result was chosen on a closure test in simulation, in
> which the purity-based and refined estimates differed by more than one statistical standard deviation in 14 of the
> 205 bins, where the purity-based estimate lay up to 5.9 statistical standard deviations from the truth and the
> refined one within 0.44; it was adopted after its distance from the published result was known, a change that
> lowered χ²/ndf from 2.65 to 2.27.

The sources:
- DECISION-20261023 :5-7 and item 1, for the choice on the C2 closure;
- DECISION-20261024, for the adoption with 2.27 against 2.65;
- the note's sec_summary.tex:9 and app_negweight.tex:136, for the numbers as printed;
- `\chiPaperPurity` and `\chiPaper`.

The new numerals 5.9 and 0.44 are declared in check_round.py's NEW_NUMERALS. 14 and 205 were already printed.

**R5.** The "NuWro, closure" row becomes "NuWro shape, noise-free closure", the text's own term.

**R6.** The abstract now reads "GiBUU gives 48 for 8 degrees of freedom on the eight cells covered by its sample". It is
pinned as check_round.py's third abstract edit.

**R7. Definitions at first use.**
- *z*: "where z is the cell's bias divided by its uncertainty under the same covariance" (FD-F0-DECLARATION.md: S-1,
  the per-cell pulls).
- *Purity and supported box*: "each supported box (one that meets the support rule) with purity, the fraction of the
  simulated signal reconstructed in it that was generated in it, below 0.1". The source is h2_definition.py:72, where
  purity = same / reco_all.
- *Audit*: "an audit of its overlap with the other blocks and of its noise treatment" (sec_fived16.tex:180).
- *Null distribution and hybrid null*: defined at their first use in Sec. VI, as sec_joint.tex defines them.
- *One-parameter family*: "each such cross term taken as a common fraction, from zero to one, of its fully
  correlated value" (sec:fived16-quadrants, r S16^{1/2} S2D^{1/2} for r in [0, 1]).

**R8.** Table IV prints new keys, sig1- and sigmed1-. Each is one decimal of the raw value the note's two-decimal key is
rounded from, so nothing in the note forces 0.01. The generator's MATRIX_KEYS pattern covers the new keys of the
with/without-block families. Table II and the note keep two decimals.

**R9.** IV E now reads "(its median falls from 8.3 % at five iterations to 3.3 % at 200)". Sec. II's 8.3 % (carbon
against CH) is unchanged.

**R10.** Left as ruled.

**Listed for Joseph, not ruled now:**
- the moves of Fig. 2a, and with it the 74 % and the 0.06 (item 7);
- the 3b closures' 0.97σ, which carries no verdict;
- the read's top three substance issues.

**The figure moves, and the check_held input.**
- After these edits, the rater copy's text extraction split two held sentences:
  - G1b:paper-g-13, "Those uncertainties come from …", split by Fig. 1 floating to the top of the next page;
  - then, with Fig. 1 moved, G1b:paper-g-14, "Rounding-level changes …", split by Fig. 2.
- Both figure environments are now defined, verbatim, just before Sec. IV B. They float onto pp. 5 and 6, and no held
  sentence crosses a page with a float at its top. Fig. 2 is first cited in Sec. III, so its earlier place is
  consistent.
- The appendix's `\clearpage` is dropped. At this layout the blinded copy keeps Limitation 1 in order without it, and
  the paper is back to 13 pages.
- **A correction to my earlier records.** check_held's documented input is the *blinded* copy, make_rater_copy.sh's
  `.blind.txt` (check_held.py docstring). The CHECK-HELD records before this section, and the RPD-sentence round's
  (#753), ran it on the unblinded `blind.txt`.
  - Rerun on the blinded copies kept from this round: the e24ad2cc1 layout gives the 3 known flags, and so does the
    final layout.
  - The first appendix layout did split G1b:paper-g-20 in the blinded copy too, so that page break was a real fix at
    the time.
  - #753's build is not kept, so its record is not rerun.

## Joseph's wording decision (DECISION-20261105-joseph-765-abstract-and-2d-disclosure.md, #772 at fa0718e8f)

Joseph decided after a PRD-referee read of the exact sentences: `consult-wording-20261105/`, answer sha256 aa9fe2fd….
He has approved merging after the director's check.

**Item 1, the abstract.**
> Fake-data studies at a GiBUU-like truth and at a synthetic momentum-transfer tilt find residual bias exceeding
> uncertainty-based criteria (p < 0.01, or any cell with |z| > 2) that were fixed before the tests were graded.

The criteria print through `\fvval{trig-p}` and `\fvval{trig-z}`. IV G's clause stays as it was at 36b903c46.
check_round.py's second abstract edit is repinned to this sentence. The generator's LISTED_CLAIMS anchor for the
abstract follows ("at a GiBUU-like truth and at a synthetic momentum-transfer tilt find"), and so does its self-test
plant.

**Item 2, Sec. III.** "No learner setting … was tuned on data" is kept. Then:
> Two other choices for the two-dimensional result were made with the comparison to the published result in view: the
> learner implementation and the background-subtraction treatment (Sec. IV B). That comparison is therefore not an
> independent test of the method.

**Item 3, IV B.** The LightGBM sentence is kept, with item 4's precision (below). Then the reviewer's framing:
> The refined negative-weight background treatment was chosen on a closure test in simulation: over 20
> pseudo-experiments at the simulation's own truth, the mean residual of the purity-based estimate reached 5.9
> statistical standard deviations, the data result's per-bin statistical uncertainties, in its most affected bin,
> against at most 0.44 for the refined estimate over all bins, and the two estimates differed by more than one
> statistical standard deviation in 14 of the 205 bins. That choice was made on the closure test, before the refined
> result's comparison with the published result was computed. It was formally adopted after its distance from the
> published result was known, and the change lowered χ²/ndf from 2.65 to 2.27. The χ²/ndf values quoted for the
> two-dimensional comparison are therefore conditional on both choices, and the comparison should be read as a
> consistency check, not a blind validation.

IV B's earlier "The comparison is a consistency benchmark, not a blind validation:" is removed, so the point is made
once.

**Item 4, the reviewer's precision points, each checked against its producer.**
- **"Both had been compared" implied exactly two implementations, and that is not so.** The scikit-learn histogram
  estimator's χ²/ndf against the published covariance (2.70 ± 0.04) was already in the note on 2026-10-03 (0e62b5cfb,
  sec:results-tension), before the 10-11 choice. The choice itself was between LightGBM and exact-split
  (DECISION-20261011 :3-4). The sentence now reads "… was chosen after both had been compared with the published
  result, as had a third implementation, the scikit-learn histogram estimator".
- **5.9 and 0.44 are the same statistic: each arm's 20-seed mean residual against the truth, in σ_stat.** Both are
  maxima over all 205 cells, in the same cell, gid 128 (RE1-REPORT-2.md §2 table: purity 5.89, refined 0.44, with 13
  and 0 cells above 1).
  - The 14 is a different count, the FLAG clause: cells where the mean refined − purity difference exceeds 1 σ_stat.
  - DECISION-20261023's "+5.89 σ_stat in 14 of 205 cells" compresses the two.
  - The text now gives each statistic separately and says which is a maximum over which bins.
- **The 3.66 → 2.65 → 2.27 sequence is in one paragraph,** with "ndf the 205 reported bins" stated at its first
  χ²/ndf (compare_to_paper_fullcov.py:99).
- **"Statistical standard deviations" is defined** as "the data result's per-bin statistical uncertainties", which is
  RE1-REPORT-2's σ_stat: sqrt(diag(stat)) of the production covariance.
- **The order of the closure and the comparison** is now stated: "That choice was made on the closure test, before
  the refined result's comparison with the published result was computed."
  - The choice was DECISION-20261023 item 1 (10-23).
  - The refined result's published-covariance χ² first appears in RE2-PARTC-REPORT.md :190 (10-24).
  - RE1-REPORT-2 computed only the refined − purity data shift (D2) and no published-covariance χ².
- **Not changed, and the reason for each:**
  - The reviewer's "why 0.01 and 2": the record (FD-DIRECTOR-RULINGS.md §2) bound them as proposed by FD-PLAN.md §7,
    and the paper gives no reason for those values.
  - A public citation for "before": FD-DIRECTOR-RULINGS.md is an internal record. The analysis note cites the
    records, and the release decision for them is Joseph's.

**Keeping the note in step.** The note already carries each fact:
- sec_method.tex sec:method-config: the background choice on the closure, before the distance was computed, and the
  adoption after;
- sec:results-tension: the HistGBT and exact-split values and the 3.66, 2.65 and 2.27;
- app_negweight.tex :136 and sec_summary.tex :9: the closure numbers;
- sec:fived16-fd: the criteria fixed before grading.

The note's text does not change in this step.

## Checks

| check | result | record |
|---|---|---|
| ledger (`check_ledger.py`, step2's checks with base fa0718e8f) | 17 rows, 0 failures; self-test PASS (LEDGER-CHECK.txt gives the probe and sentence counts) | LEDGER-CHECK.txt |
| round (`check_round.py`) and its self-test | PASS (22 removals, 30 additions, 3 abstract edits); 17/17 planted defects caught, each by its intended check | ROUND-CHECK.txt |
| values (`make_values_fived16.py --self-test`, `--check`) | PASS (3,617 values; 10 listed-truth sentences, including R1's "ctotal") | VALUES-CHECK.txt |
| rater copy (`make_rater_copy.sh`) | PASS | RATER-COPY.txt |
| held sentences (`check_held.py`, on the blinded copy) | the 3 known flags (G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07) | CHECK-HELD.txt |
| builds (`build_all.sh`) | paper 13 pp, note 136 pp; SEC4 receipts 17/17 | — |
| registry | the four citations into edited lines re-cited by hand (ALIASES rows 35, 38, 47; ATTRIBUTION row 17), the rest repointed | — |

**The rater copy's reading order.** See "After PRD read 1", which also corrects which file check_held reads.

**A pre-existing warning.** The one overfull box in main_paper.log (9.7 pt, Table III) is at lines this round does not
change.
