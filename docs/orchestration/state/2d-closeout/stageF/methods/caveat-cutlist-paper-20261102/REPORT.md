# REPORT The caveat cut list: the approved moves (2026-11-02)

**By** the paper rewrite lane (Claude), for the director, the PRD-referee read, limitations-catalog's re-measure and
Joseph.

**Under:** `DECISION-20261102-joseph-caveat-cut-list.md` and the director's work order of 2026-11-02. The inputs are
limitations-catalog's cut list (`caveat-remeasure-20261102/cutlist/`, #706: `cutlist.md`, `cutlist.json` and `moves.tsv`)
and the Gemini PRD review beside it (#707).

**MEASURES:** nothing. No value changes: `values_fived16.tex` is unchanged, and `make_values_fived16.py --check` passes.

**CANNOT AUTHORIZE:** a claim, a wording or a caveat count. The re-measure is limitations-catalog's (`remeasure.py`).

## What was done, move by move

| move | done | where now | note |
|---|---|---|---|
| MV01 run periods | merged | IV A, one statement | IV C's run-period paragraph and V B's repeat of the post-hoc addition are gone. The abstract keeps the timing. The post-hoc addition is attributed to C_PL,5D only, as in the base. "Cannot fail" is said of the 2D block only (review) |
| MV02 coverage | merged | VI A item 1 | The fake-data sentences of IV H and IV's "pointwise" clause join it. 1B's status: "A staged coverage test at those two truths, with the covariance rebuilt by the same procedure at each, is under way." "Halted" is not used. The A7 sentence "We make no coverage claim …" stays verbatim (G1b:paper-g-20). The intro's frozen "Interval coverage has not been validated." stays (G1b:paper-g-02) |
| MV03 3D/4D central values | merged | V C | V's opening and VI A no longer repeat it |
| MV04 envelope | merged | III A | Three sentences become two, with every number. The conclusions keep "tracks the same bias". The sentence is held for its facts (G1:paper-g-06) |
| MV06 C_model's sources | moved | IV A, in C_model's definition | V B's "(below)" now points to IV A |
| MV07 hydrogen samples | merged | the Table III footnotes | GiBUU's row keeps its footnote, and NuWro's row gets its own (review). Fig. 4's caption keeps one pointer until E-A2 redraws the legend |
| MV07F Fig. 4 legend | **waiting** | — | E-A2 is approved in principle and goes to limitation-resolver (the director's ruling). The modes figure is redrawn from the same set |
| MV08 background subtraction | merged | IV D | Three sentences. The wording "biased by up to", "reduces it to below", "leaving up to" and "differ by at most" is bound by `check_sec4_receipts.py` (VL149, VL151, VL152), so it is kept |
| MV10 χ² correlation sensitivity | merged | V B | — |
| MV13 IV F | moved | the note, sec:coverage-5d; a pointer in IV E | The pointer keeps the correction and the strongest case (review). The conclusion sentence (Q43) moves too |
| MV14 binned diagnostic | moved | the note, sec:val-departure; IV E's existing pointer names it "with its scope" | — |
| MV15 IV G | condensed | IV G, two sentences | The numbers sentence is byte-exact (G1b:paper-g-14) |
| MV16 the seed sentence | moved | the note, sec:val-departure; IV E's pointer names the seed sets | — |
| MV17 R11 | note first | sec_fived16.tex:244 | The paper sentence stays this round |
| MV18 hydrogen-sample sign | already in the note | sec_fived16.tex:388 and the target table | The cut list did not find it. No change |
| MV19 unpaired pseudo-experiments | note first | sec_5d.tex:51 | The caption stays this round |
| MV05, MV11, MV12 | skipped | — | — |
| MV09 | stays | — | — |
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

**Pages:** the paper goes from 13 to 12 pages and the note from 134 to 135.

## Points for the director and Joseph

1. **1B's status sentence** is "A staged coverage test at those two truths, with the covariance rebuilt by the same
   procedure at each, is under way."
   - Its sources:
     - stage 0 passed (`FD-1B-STAGED-STAGE0-REPORT.md`, κ in its window in 16 of 16 cells);
     - stage 1 runs on the redesign (`DECISION-20261102-joseph-1b-redesign.md` item 1);
     - the method wording is Joseph's (item 4).
   - No stage-1 pseudo-experiment has run yet, and the implementing amendment is not yet bound. "Under way" is true of
     the campaign, not of a running job.
   - The note says the same (`sec_fived16.tex:246`).
   - The review notes that "the covariance rebuilt" simplifies the declaration's Clause M (C_total rebuilt, the lateral
     block carried, C_resp and C_PL,5D omitted). That simplification is Joseph's approved method wording.
   - `FD-1B-STAGED-DECLARATION.md` §12 says the paper is unchanged until a result. The work order asks for the status
     now. The director may want that override in the record.
2. **IV G keeps the base's tension.** The text reads "the spread lies inside the data-bootstrap statistical uncertainty"
   next to "up to 2.6 statistical standard deviations". Both are the base's facts. Condensing put them side by side, and
   reconciling them is the owner's call.
3. **Joins, not merges (the review's register note).** MV04, MV08 and MV10 mostly join base sentences. Their facts and
   the receipts' bound wording leave little room to reorganise. MV08 is now three sentences. The re-measure will show
   whether the coder counts each as one caveat.
4. **MV07F and the modes caption.** When E-A2 lands, the modes caption's "supplement FLAGGED" sentence goes (the
   director's ruling 2). Fig. 4's pointer sentence goes too if the redrawn legend no longer says "hydrogen".

## Every changed sentence, before and after

Rendered from the sources: `\fvval` values are filled in, and a pointer reads "note <label>". The base is `589eb47d0`.

### MV01 — run periods (IV A; IV C's paragraph; V B)

**Before:**

> The run-period block C_PL,5D accounts for differences among the three run-period groups, whose unfolded results, each relative to its own simulation, differ by more than their bootstrap scatter. The cause is not known. As for the two-dimensional result (Sec. sec:uq2d), the block is built from the double ratios among the groups, with no reference period; it has rank 2, is not corrected for the bootstrap noise it contains, and with three groups its size is poorly determined: the 68 % interval on the ratio of its true to its estimated size is 0.73–2.56. It was added after these differences were seen, following an audit whose stopping criterion was fixed in advance.
>
> Data from different run periods are not mutually consistent within the other uncertainties. One period group's unfolded p∥ distribution, taken relative to its own simulation, differs from that of the earliest periods by a step of about 7 % near 8 GeV/c. The cause is not known, and these data cannot establish which period is correct. The run-period block is built from double ratios among the three period groups, each group's unfolded result over its own simulated truth, with no group chosen as the reference. It includes this inconsistency in the combined result and amounts to 2.0 % on the integrated cross section. Because the block is built from the observed differences among the periods, it contains them by construction, and its own consistency check cannot fail.
>
> The run-period block was added after the data were seen (Sec. sec:cov16). With it, each total
>

**After:**

> Data from the three run-period groups are not mutually consistent within the other uncertainties: their unfolded results, each relative to its own simulation, differ by more than their bootstrap scatter, and in the two-dimensional result one period group's unfolded p∥ distribution differs from that of the earliest periods by a step of about 7 % near 8 GeV/c. The cause is not known, and these data cannot establish which period is correct. The run-period blocks, C_PL,5D here and that of the two-dimensional covariance (Sec. sec:uq2d), include this inconsistency in the combined results; the two-dimensional block amounts to 2.0 % on the integrated cross section. Each is built from the double ratios among the groups, each group's unfolded result over its own simulated truth, with no group chosen as the reference, so it contains the differences by construction; the two-dimensional block's own consistency check therefore cannot fail. C_PL,5D was added after these differences were seen, following an audit whose stopping criterion was fixed in advance; it has rank 2, is not corrected for the bootstrap noise it contains, and with three groups its size is poorly determined: the 68 % interval on the ratio of its true to its estimated size is 0.73–2.56.
>
> With the run-period block, each total
>

### MV02 — the one coverage statement (IV opening; IV H; VI A item 1)

**Before:**

> Coverage, how often intervals contain their target over repeated experiments, tests the estimator and the interval construction together, and the coverage tested here is pointwise, for each reported quantity separately, not the stronger simultaneous coverage of all of them.
>
> The tests assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested. A coverage test at these two tunes, declared in advance for the covariance without the run-period block, with pseudo-experiments that also draw the flux, interaction, and detector uncertainties, was stopped at one of its gates before any coverage pseudo-experiment ran: the uncertainties reproduced through its pseudo-experiments disagreed with the covariance blocks they draw, for reasons not established (note sec:fived16-fd).
>
> The coverage of the sixteen-cell total uncertainties has not been tested: the fake-data tests of Sec. sec:fd16 assess the estimator's bias, and the coverage test declared at two of their truths stopped before any coverage pseudo-experiment ran. Neither the coverage of C_model at truths held out of its construction nor the size of either run-period block is independently validated (note sec:fived16-cov, sec:fived16-pl and sec:uq-combine). The two-dimensional covariance has not been independently validated and gives no calibrated significance for generator comparisons. An earlier statistical band of that result undercovered in its tails in a coverage test at fixed truth (note sec:coverage); the coverage of the current statistical block and of the total covariance has not been tested. We make no coverage claim on independent simulated samples or simultaneously over all reported bins and projections. The three- and four-observable central values lack intervals of validated coverage (Sec. sec:central).
>
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

**After:**

> Coverage, how often intervals contain their target over repeated experiments, tests the estimator and the interval construction together.
>
> Coverage is discussed in Sec. sec:limitations.
>
> No reported interval has validated coverage. The fake-data tests of Sec. sec:fd16 assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested. A coverage test at two of their truths, declared in advance for the covariance without the run-period block, with pseudo-experiments that also draw the flux, interaction, and detector uncertainties, was stopped at one of its gates before any coverage pseudo-experiment ran: the uncertainties reproduced through its pseudo-experiments disagreed with the covariance blocks they draw, for reasons not established (note sec:fived16-fd). A staged coverage test at those two truths, with the covariance rebuilt by the same procedure at each, is under way. Neither the coverage of C_model at truths held out of its construction nor the size of either run-period block is independently validated (note sec:fived16-cov, sec:fived16-pl and sec:uq-combine). The two-dimensional covariance has not been independently validated and gives no calibrated significance for generator comparisons; an earlier statistical band of that result undercovered in its tails in a coverage test at fixed truth (note sec:coverage), and the coverage of the current statistical block and of the total covariance has not been tested. The coverage tests cited are pointwise, for each reported quantity separately, not the stronger simultaneous coverage of all of them. We make no coverage claim on independent simulated samples or simultaneously over all reported bins and projections.
>
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

### MV03 — the 3D/4D central values (V B opening; V C)

**Before:**

> The two-dimensional result is therefore reusable, the sixteen-cell result can be used for the comparison that follows, and the higher-dimensional central values can be used for qualitative comparison.
>
> These comparisons use the three- and four-observable central values of the joint-test estimator, without uncertainties.
>

**After:**

> The two-dimensional result is therefore reusable, and the sixteen-cell result can be used for the comparison that follows.
>
> These comparisons use the three- and four-observable central values of the joint-test estimator, which have no uncertainties and serve for qualitative comparison only.
>

### MV04 — the envelope (III A; the conclusions)

**Before:**

> With the envelope added, none of the reporting definitions of a five-observable measurement tested in the study meets this target. With the joint-test estimator, the envelope alone exceeds the target for the 109 coarse joint cells and for the 39 supported (E_avail,W) cells. For a coarser, non-nested partition of all five observables into 27 cells, the same estimator's envelope alone does not exceed the target, but the 1.4 % normalization contained in every probabilistic half-width lifts the median above it.
>
> The second is the envelope of Sec. sec:uncertainty-status, which tracks the same bias and alone exceeds the precision target in two of the three tested reporting definitions.
>

**After:**

> With the envelope added, none of the reporting definitions of a five-observable measurement tested in the study meets it. With the joint-test estimator, the envelope alone exceeds it for the 109 coarse joint cells and the 39 supported (E_avail,W) cells; for a coarser, non-nested partition of all five observables into 27 cells it does not, but the 1.4 % normalization contained in every probabilistic half-width lifts the median above it.
>
> The second is the envelope of Sec. sec:uncertainty-status, which tracks the same bias.
>

### MV06 — C_model's sources (V B to IV A)

**Before:**

> That rise comes from pairing the CH prediction with C_model, whose NuWro and GiBUU shape ratios are from carbon (below):
>
> The GENIE + MEC, NuWro and GiBUU comparisons use covariance contributions derived from those generators, and GENIE CV enters as their common reference; those contributions come from the generators' samples in their own definitions, with NuWro and GiBUU on carbon, not from the predictions compared here.
>
> The two-dimensional covariance is the sum of four blocks, each from LightGBM unfoldings with the central value's estimator: systematic universes (187 universes, including the normalization), statistical (300 bootstrap replicas), run period (three period groups), and training seed (five seed settings, so that its own size is poorly determined).
>

**After:**

> Its contributions come from those generators' samples in their own definitions, with NuWro and GiBUU on carbon and GENIE CV as the common reference, not from the predictions compared in Sec. sec:gen16. The comparisons there with GENIE + MEC, NuWro and GiBUU therefore use covariance contributions derived from the same generators.
>
> That rise comes from pairing the CH prediction with C_model, whose NuWro and GiBUU shape ratios are from carbon (Sec. sec:cov16):
>
> The two-dimensional covariance is the sum of four blocks, each from LightGBM unfoldings with the central value's estimator: systematic universes (187 universes, including the normalization), statistical (300 bootstrap replicas), run period (three period groups; Sec. sec:cov16), and training seed (five seed settings, so that its own size is poorly determined).
>

### MV07 — the hydrogen samples (Table III footnote; Fig. 4 caption)

**Before:**

> The sampling-closure check failed on that hydrogen sample; a bias check of the check's premise, added post hoc, passed at ≤0.1 σ_c, with σ_c a cell's standard deviation under the null distribution of the note's joint tests (note sec:joint5d-ch). Deep-inelastic events, 46 % of the hydrogen sample, do not conserve energy.
>
> In the legend, GiBUU's “closure B3 failed” is the sampling-closure check that failed on its hydrogen sample (the footnote to Table tab:gen16), and NuWro's “supplement FLAGGED” marks the part of its free-proton sample generated at neutrino energies of 50–100 GeV, in which the events lost to generator aborts were not shown to be negligible (note sec:joint5d-ch).
>

**After:**

> That hydrogen sample failed its sampling-closure check, B3 (a bias check of the check's premise, added post hoc, passed at ≤0.1 σ_c, with σ_c a cell's standard deviation under the null distribution of the note's joint tests), and its deep-inelastic events, 46 % of it, do not conserve energy (note sec:joint5d-ch).
>
> In NuWro's free-proton sample, the supplement generated at neutrino energies of 50–100 GeV is flagged: the events lost to generator aborts there were not shown to be negligible (note sec:joint5d-ch).
>
> The legend's hydrogen labels refer to the footnotes to Table tab:gen16.
>

### MV08 — background subtraction (IV D)

**Before:**

> Figure \reffig:bkg-residual shows that, with purity-based background subtraction in a deterministic LightGBM estimator, end-to-end pseudo-experiments at nominal truth reproduce the input except in the highest-W cells, which are biased by up to 4 % in simulation. In the same estimator, unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves reduces it to below 0.3 % in those cells and at most 0.4 % elsewhere in the projection, leaving up to 1 % in some joint cells. On data, the two treatments differ by at most 1.4 %. Both kinds of closure study are described in note sec:closure-map. In two observables, a closure test with backgrounds (20 pseudo-experiments at nominal truth) finds the purity and refined estimates more than one statistical standard deviation apart in 14 of the 205 cells. The purity estimate lies up to 5.9 statistical standard deviations from the truth, and more than one total standard deviation in one cell, while the refined one lies within 0.44 in every cell. The two-dimensional result therefore uses the refined estimator (note app. sec:negweight-footing).
>

**After:**

> With purity-based background subtraction in a deterministic LightGBM estimator, end-to-end pseudo-experiments at nominal truth reproduce the input except in the highest-W cells, which are biased by up to 4 % in simulation (Fig. fig:bkg-residual); unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves reduces it to below 0.3 % in those cells and at most 0.4 % elsewhere in the projection, leaving up to 1 % in some joint cells. In a two-dimensional closure test with backgrounds (20 pseudo-experiments at nominal truth), the purity estimate lies up to 5.9 statistical standard deviations from the truth, and more than one total standard deviation in one cell, while the refined one lies within 0.44 in every cell; the two are more than one statistical standard deviation apart in 14 of the 205 cells. On data, the two treatments differ by at most 1.4 %, and the two-dimensional result uses the refined estimator (note sec:closure-map; note app. sec:negweight-footing).
>

### MV10 — the χ² correlation sensitivity (V B)

**Before:**

> Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 23–38 %. The same change to the detector or lateral correlations lowers it by at most 18 %. With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ²≥41 for 16 degrees of freedom. The flux correlations are estimated from 100 hadron-production (PPFX) flux universes [ref], weighted by the neutrino–electron and inverse-muon-decay constraint. Bootstrapping these universes, with the flux variances kept, gives 16th–84th percentile bands for each 16-cell χ², with edges within 3.8 % of the reported value and a median at most 0.4 % above it. These bands describe the scatter of the χ² from estimating the correlations with these universes, not its sensitivity to incorrect correlations, which the weakening probes. In particular, they are not intervals for the χ² under the true correlations.
>

**After:**

> Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 23–38 %, and the same change to the detector or lateral correlations by at most 18 %; with the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ²≥41 for 16 degrees of freedom. The flux correlations are estimated from 100 hadron-production (PPFX) flux universes [ref], weighted by the neutrino–electron and inverse-muon-decay constraint. Bootstrapping these universes, with the flux variances kept, gives 16th–84th percentile bands for each 16-cell χ², with edges within 3.8 % of the reported value and a median at most 0.4 % above it; the bands describe the scatter of the χ² from estimating the correlations with these universes, not the sensitivity to incorrect correlations that the weakening probes, and are not intervals for the χ² under the true correlations.
>

### MV13 and MV14 — IV F and the binned diagnostic to the note (IV E's pointer; the conclusions)

**Before:**

> A binned, signal-only and noise-free diagnostic on the 109 joint cells and the truth changes used to develop the estimator, with the detector response fixed at the simulation's, shows that exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator. It covers only the residuals whose diagnosis does not change with the resolution of the truth binning (38 % of the joint-cell residuals above 2 %). Within that scope, the residual is consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (note sec:val-departure). The diagnostic does not address what unbinned information could recover, the miscoverage of Sec. sec:coverage, or the validity of any interval.
>
> The deformation studies, the iteration and capacity tests, the exact binned comparison and the joint-test-estimator shapes are given in Ref. [ref], Secs. \ref*N-sec:val-negweight and \ref*N-sec:val-departure.
>
> Statistical intervals from a deterministic LightGBM estimator with purity-based subtraction, corrected for the estimator's closure bias at nominal truth, miscover at the tested truths, most strongly when the true signal rate is lowered by about 10 %. Under that change, 51 of the 153 reported cell and projection integrals have a 68% coverage whose upper confidence bound lies below the acceptance threshold of 0.66, with coverage as low as 0.06. The end-to-end test unfolds 400 pseudo-experiments per truth. A diagnosis attributes the miscoverage to a residual bias that grows with W and survives the nominal-truth bias correction. The source of this residual bias has not been established. Agreement in the marginal normalizations coexists with substantial residual bias under the tested deformations. The interval construction and the diagnosis are described in note sec:coverage-5d.
>
> The miscoverage of Sec. sec:coverage is also attributed to a residual bias, but whether that bias has the same origin is not established.
>

**After:**

> The deformation studies, the iteration and capacity tests, the exact binned comparison with its scope, and the joint-test-estimator shapes with the seed sets of their pseudo-experiments are given in Ref. [ref], Secs. \ref*N-sec:val-negweight and \ref*N-sec:val-departure.
>
> Statistical intervals of an earlier five-observable estimator with purity-based subtraction, corrected for its closure bias at nominal truth, miscover at the tested truths, most strongly when the true signal rate is lowered by about 10 %; the test and its diagnosis are in note sec:coverage-5d.
>

### MV15 — IV G condensed

**Before:**

> The joint-test estimator is unstable under perturbations of its inputs within floating-point rounding. Rounding-level changes of its inputs move its results by up to 2.6 statistical standard deviations, and those of the lower-capacity development variant by up to 2.5, so the estimator fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations. This spread lies inside the data-bootstrap statistical uncertainty but limits how exactly the central values can be reproduced.
>

**After:**

> The joint-test estimator is unstable under floating-point rounding of its inputs; the spread lies inside the data-bootstrap statistical uncertainty but limits how exactly the central values can be reproduced. Rounding-level changes of its inputs move its results by up to 2.6 statistical standard deviations, and those of the lower-capacity development variant by up to 2.5, so the estimator fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations.
>

### MV16 — Fig. 3's seed sentence (caption to the note)

**Before:**

> Neither seed set was held out from the estimator's development.
>

**After:**

> (removed from the paper; see the note below)


### The note's additions

**MV13 — the note, sec:coverage-5d (added):**

> Agreement in the marginal normalizations thus coexists with a substantial residual bias under the tested deformation, and whether that bias has the same origin as the regularization bias of \S\refsec:val-departure is not established.

**MV16 — the note, sec:val-departure (added):**

> The pseudo-experiments of the paper's recovery figure, sixty for the development variant at the GiBUU-to-GENIE E_avail shape and twenty for each of three shapes not used in the joint-test estimator's selection, use seed sets that were not held out from the estimator's development.

**MV19 — the note, sec:val-negweight (extended):**

> brings the highest-W column to 0.11–0.24 % and the corner cell to 0.24 % over sixty nominal-truth experiments, which are not paired with the purity-based ones.

**MV17 — the note, sec:fived16-fd (extended):**

> In every cell of the four records, the bias is below 0.62 of the cell's reported σ; in cell R11 at G18\_10a\_02\_11b, the bias lies below the reported uncertainty only with C_model included.

**MV02 — the note, sec:fived16-fd (added: the staged campaign):**

> A staged coverage test at the two tunes, with the covariance rebuilt by the same procedure at each tune, is under way.


## Where the note prints each moved fact (by file:line, this branch)

- **IV F (MV13):**
  - `sec_5d.tex:213` (sec:coverage-5d): the test, its futility, the 10 % rate reduction, and 1,200 pseudo-experiments
    over three truths;
  - `:215`: 51 of 153 below 0.66, as low as 0.060;
  - `:228`: the residual bias, growing with W and not removed by the correction; its source not established; and,
    added here, the marginal normalizations and whether the bias has the same origin.
- **The binned diagnostic (MV14):** `sec_5d.tex:84`, with its results and its scope ("It does not address what unbinned
  or biased estimators could recover…").
- **The seed sets (MV16):** `sec_5d.tex:77`.
- **The unpaired pseudo-experiments (MV19):** `sec_5d.tex:51`.
- **R11 (MV17):** `sec_fived16.tex:244`.
- **The staged 1B campaign (MV02):** `sec_fived16.tex:246`.
- **The hydrogen-sample sign (MV18):** `sec_fived16.tex:388`, and the target table.
- **The run-period audit and the block's validation (MV01):** `sec_fived16.tex:175` and `sec_systematics.tex:186`.
- **The NuWro supplement flag (MV07):** `sec_joint.tex:327`.

## Checks

| check | result |
|---|---|
| the ledger (`check_ledger.py`, base `589eb47d0`) | 15 rows, 77 probes, 61 changed base sentences, 0 failures; self-test PASS. `sec:coverage` is declared removed from the paper. The note's own label of that name is not counted as a reference to it, and a test shows the check still fires on a paper reference |
| `make_values_fived16.py --check` | PASS; no value changes |
| `check_sec4_receipts.py` and its self-test | PASS (15/15; 18 perturbations rejected) |
| `build_all.sh` | PASS: paper 12 pp, note 135 pp, primer 15 pp; no "??". The paper's one overfull box is the base's (Table III) |
| the two-direction review (`review.md`) | nothing false, no lost fact. 4 Medium: all fixed. 8 Low: 6 fixed, and 2 reported (the 1B wording, point 1; IV G's tension, point 2) |
| the rater copy | `make_rater_copy.sh` exits 0; holddiff PASS |
| `check_held.py --fact-held` | the 3 known flags (G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07) |
| `generate_manifest.py --check` | see the PR |
| local CI | see the PR |

Nothing is submitted, deposited or tagged.
<!-- absence-ok: the report quotes the paper's caveats, before and after, with their sources; it makes no claim of its own -->
