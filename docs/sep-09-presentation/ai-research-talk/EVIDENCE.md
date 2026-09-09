# Evidence and interpretation notes

This is a presentation working draft, not a publication-adoption record. No new
physics fit, uncertainty construction, or scheduler action was performed. The
scientific plots replot committed receipts and their hash-matched frozen ROOT inputs. Repository measurements are new local
descriptive outputs with an explicit source revision, not a causal productivity
study. They are not recorded as new scientific ledger results.

## Frozen population

All repository measurements and receipt reads use:

`901f2c647355d69412b5c190fcb1df02d1c8aa14`

The surrounding working tree was changing during preparation; using one resolved
commit avoids mixing those changes into the comparison. `measurements/metrics.json`
records the measurement timestamp and SHA-256 of every plotted scientific receipt.
`measurements/commit_inventory.json` contains the complete measured commit/path
population, without author names or message bodies. No transcript text is exported.

## Slide-by-slide support

| Slides | Claim / purpose | Source and limitation |
|---|---|---|
| 1–2 | Biography, December start, Ben conversation, use of several LLMs | Joseph's supplied opening; personal recollection, not a date inferred from git. |
| 2, 23 | MINERvA inclusive measurement | [Ruterbories et al., arXiv:2106.16210](https://arxiv.org/abs/2106.16210). |
| 2, 23 | OmniFold and software | [Andreassen et al., arXiv:1911.09107](https://arxiv.org/abs/1911.09107); [rymilton/unbinned_unfolding](https://github.com/rymilton/unbinned_unfolding). The slide is a schematic, not a complete algorithm. |
| 3–5, 17–19 | 2D direct comparison and integrals | `docs/orchestration/receipts/RECEIPT-2d-agreement-windows-20260821.json` at the frozen revision, plus the exact hash-matched ROOT inputs described below. |
| 3, 7, 18 | Completed 2D controls and uncertainty | `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md`, `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, matched-CV flux-fixed summaries under `2d-unfolding/uq/universe_stage2_MEFHC_full_matcorr_fluxfix/`. No combined paper-plus-ours chi-square. |
| 7 | Higher-D scientific scope | `3d-unfolding/3D_OMNIFOLD_STATUS.md` covariance override; `nd-unfolding/ND_OMNIFOLD_STATUS.md`; `VALIDATION_LEDGER.md` corrected 5D quarantine; `docs/OPEN_ITEMS.md` OI-126 ruling. Central/closure validation is separate from covariance adoption. |
| 7, 23 | Full-event direction | [Mikuni & Nachman, arXiv:2404.16091](https://arxiv.org/abs/2404.16091); [Krzmanc et al., arXiv:2604.12364](https://arxiv.org/abs/2604.12364); `docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md`. Influence does not establish use of a particular pretrained checkpoint. PET remains diagnostic. |
| 9 | Orchestration evolution | Historical `docs/orchestration/README.md` coordinator/worker kit; `MIGRATION-HANDOFF.md` archived July 18 role table; `WAKER.md`; commits `79e1bc52` (July 16), `42c1fd75` (July 18), `be4cd789` (July 19), `e96ba339` (August 25). Dates are documented workflow milestones, not exclusive eras or causal interventions. These historical sources are not current scientific authority. |
| 10 | Activity and edit locations | `measure_history.py`, `measurements/monthly.csv`, complete commit inventory. Counts are neither hours nor productivity. |
| 11 | Checkpoint failure and repair | `nd-unfolding/pet/fullevent_nominal/GATE_AB_PUSH_PROVENANCE.json` and `GATE_AB_PUSH_PROVENANCE.slurm-56445883.batch512.json`; `docs/orchestration/FINDING-20260807-checkpoint-is-not-the-trained-model.md`; issue 37 in `KNOWN_ISSUES.md`. Historical diagnostic example. |
| 12 | Audit-first frustration, preference for trying things | Joseph's account. Bounded exploration before broad review is proposed, not an observed controlled improvement. Scientific adoption and compute constraints remain in force. |
| 13 | Active time and routing failures | Joseph's account; historical `WAKER.md` F2/F3 record wrong executable and Python-environment failures. No complete human-time budget. |
| 13 | Simpler watcher | `docs/OPEN_ITEMS.md` OI-135, including Joseph's recorded question. Implementation/testing does not prove deployment or a measured saving. |
| 15–16 | Understanding and assessment | Joseph's uncertainty about explaining details; abstraction as a possible benefit, explicitly a hypothesis. Recommended practices are proposed speaker wording, not claimed learning gains. |
| 20 | Python file stock | `measurements/snapshots.csv`: first-parent monthly snapshots, all tracked Python paths including tests, drivers and vendored code. File-edit entropy is not code complexity. |
| 21 | Evaluation limits | No matched no-AI or model experiment, human-hours record, or learning test was assembled. |

| 8 | Higher-dimensional physics payoff | `VALIDATION_LEDGER.md` VL35–39, `docs/analysis-note/sec_eavailw.tex`, and the original four-generator log copied read-only. Ratios at recorded precision; no covariance or significance. |
| 14 | Expert feedback corrected a novelty premise | `docs/COLLABORATOR_QUESTIONS.md`, August 2 clarification. Existing 3D publication, narrower unbinned/simultaneous distinction, endorsement unanswered. No attribution of the error to AI or claim that Joseph independently discovered it. |

| 6, 22 | Full uncertainty budget and comparable published sources | Same validated 2D matrices as slide 3; band grouping matches `uq/analyze_universes.py`; paper release README defines the four separately released covariance types. |


## Frozen ROOT inputs and direct comparison

Read-only retrieval on September 9 copied existing files from the project's
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/` directory into this
presentation worktree. No remote job, fit, extraction or source mutation occurred.

| Local input | Original relative path | SHA-256 |
|---|---|---|
| `inputs/ours_2d.root` | `2d_crossSection_omnifold_MEFHC_5iter.root` | `142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5` |
| `inputs/published_2d.root` | `minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root` | `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3` |

Both hashes equal the committed agreement receipt. `plot_2d_comparison.py` requires
that equality. It reads `hXSec2D` as 14 pT by 16 longitudinal-momentum bins, and
transposes the published `pt_pl_cross_section` to the same order. The reported mask
is the positive diagonal of `StatOnlyCovariance`, yielding 205 of 224 cells.
All reported reference central values are positive. Matrix ordering is pT-major,
with longitudinal momentum varying fastest, as used by the recorded comparison.

The pT boundaries differ at three positions: ours `.07, .33, .47`, published
`.075, .325, .475` GeV/c. All other boundaries agree, and the longitudinal axis
agrees exactly. Binwise ratios are corresponding-index comparisons, not exact
common-cell integrals where these boundaries differ. The generator preserves this
fact in slide captions, slice titles and the exported CSV. It does not change or
rebin the adopted result. This is a presentation qualification, not a new result
adoption or an explanation of any residual.

For each physical projection, each input uses its own integration widths and
reported mask. Published projection covariance is `A C_total A.T`, retaining
correlations, while individual slice errors use the covariance diagonal. Both
projected integrals reproduce the separately recorded totals. Paper errors give a
reference scale only: shared inputs prevent treating these as independent results,
and no covariance of their difference is constructed. On slide 3 the teal curves now include our adopted total uncertainty, as described
below. Slice plots also display our total errors and the separate published reference
errors.

The map displays `100 * (ours / paper - 1)`, saturates at ±20%, and labels cells
beyond ±10%, including the values beyond the color scale. Gray marks the 19
unreported cells. Equal display widths are explicitly labeled. The four main
slices are zero-based pT indices 2, 7, 10 and 13, selected to span the axis with
identical boundaries in both files; all 14 are supplied in backup. The small
backup figure is also available as a standalone vector PDF.

The new outputs are descriptive replots of existing adopted/historical input
artifacts. The CSV, JSON and figures are presentation derivatives, not new
scientific ledger measurements. `check_artifacts.py` rechecks input hashes, the
205-bin mask, agreement counts and both projected totals before validating the deck.

## Our uncertainty on slide 3

The initial presentation omitted our errors pending a check of the covariance
pairing. The revision uses the existing adopted 2D construction and the same frozen
central-value input named in the committed
`2d-unfolding/uq/universe_stage2_MEFHC_full_matcorr_fluxfix/MEFHC_fig6_7_uncertainty_summary.txt`.
Three existing ROOT files were copied read-only; their exact paths, retrieved
SHA-256 hashes and committed source digests are in `measurements/two_d_uncertainty.json`.
This is a replot, not a new uncertainty construction or adoption.

The budget is the flux-fixed file's `hCov_combined` plus the ML file's
`hCov2D_reported`. `hCov_combined` already contains bootstrap statistics.
The reader verifies it equals `hCov_universe_total + C_bootstrap`, so statistics
are included once. Each component's grid, reported mask and stored sigma map are
checked against its covariance diagonal. The total is symmetric and positive
semidefinite within numerical precision.

Our projected covariance is `P C_total P.T`, using our true bin widths and all
correlations. Our fractional total error reproduces the committed summary at its
printed precision: pT median/max 6.220%/8.037%; longitudinal momentum
5.901%/14.994%. These projection errors differ from the median error over 205
individual 2D bins; no uniform 6.87% error is substituted.

Teal shading on the upper panels is our central value ± total sigma. Teal ratio
bars are sigma_ours divided by the paper central value, with that denominator
held fixed. The gray band separately displays the paper's relative total error.
Neither is a combined uncertainty on the ratio or difference. Shared data and
systematics preclude an independence assumption. The paper's own physical bin
widths remain in its projection; the existing three-boundary qualification stays.

## Sources of uncertainty and slice errors

Slides 5 and 17 now use the adopted covariance diagonal for our individual 2D-bin
errors. Teal upper bands are ours ± sigma; teal ratio bars are sigma_ours divided
by the paper central value. The gray ratio band remains the published reference
error. No shared-systematic cross-covariance or combined ratio error is invented.

Slide 6 plots our grouped source medians for both projections, with published
markers for the total, flux and statistical matrices. Slide 22 also compares
muon energy scale, using only our MINOS and MINERvA energy-scale bands; that subset
is not added again to the total. The broader muon-reconstruction group also
contains efficiency, resolution and beam-angle bands. The public release has no
separate numerical covariance for every broader category, so missing markers are
not zeros. The release README and canonical grouping source are hash-bound in
`measurements/two_d_uncertainty.json`.

`plot_uncertainty_sources.py` uses the same grouping as `uq/analyze_universes.py`,
checks that all systematic bands sum to the stored systematic total, adds the
bootstrap and ML blocks once, and checks the result against the adopted total, and reproduces every grouped
median/max in the committed projection summary at printed precision.
It projects each component's full matrix using its own input bin widths, then
computes the fractional standard deviation and median across projection bins.
`measurements/uncertainty_sources.json` exports band membership, all per-bin
fractions and median/max values. These are not additive budget shares. ML means
unfolding-model seed variation, not uncertainty or reliability of an LLM.

## Additions informed by the July-to-September preparation material

Reviewed `/Users/josephbailey/local-research/minerva-talk-prep/SINCE-JULY-16.md`
and its PDF/PowerPoint exports. It supplied editorial leads, not scientific
authority. The selected additions were checked against their original repository
sources at the same frozen revision as the existing quantitative material.

Slide 8 shows corner-integrated data/generator ratios from the August 11 all-four
run. Its original log was read and copied from Perlmutter on September 9 to
`inputs/eavailW_band_20260811_allfour.log`; no plotting or compute ran remotely.
The log's old output-creation messages describe the original August run.
`measurements/corner_comparison.json` records the copied log hash, remote path,
source commit and hashes for the ledger, analysis-note section and collaborator
record. The source log ratios agree with ledger rows VL35–38: GENIE-CV 1.535,
GENIE+MEC 1.579, NuWro 1.563 and GiBUU 1.609. The figure uses these recorded
ratios, not extra digits manufactured from rounded printed integral operands.
The generator integrations use E_avail >= 0.8 GeV and W >= 1.8 GeV over nine
cells. No covariance, significance, independence claim for generator codes,
or mechanism attribution is attached to the points.

The prep draft's "50–60% below data" wording is not used. A ratio of 1.54–1.61
means approximately 35–38% below data; explicit data/generator ratios avoid that
denominator ambiguity. The talk also does not adopt its blanket "all questions
answered", "nothing retracted", "almost nobody measures this", or causal
explanation for the schedule slip.

Slide 14 adds the collaborator exchange as an example of checking research
premises and novelty. It keeps verbal guidance distinct from endorsement and does
not identify AI as the source of the incorrect premise. Slide 11 now explains
why checkpoint identity matters to the weights entering the scientific result,
while preserving its historical diagnostic PET scope and matched-batch repair.

## Exact figure calculations

### 2D agreement

- Within 5%: `159 / 205 × 100 = 77.56098…%`.
- Within 10%: `193 / 205 × 100 = 94.14634…%`.
- Within 20%: `202 / 205 × 100 = 98.53659…%`.
- These are nested, cumulative windows, not three disjoint populations.
- Integrated totals: `3.0733131599571655e-38` versus `3.03901139455691e-38`
  cm²/nucleon. Their ratio is `1.0112871460310062`; “about 1.1% apart” avoids
  treating the older 1.11% prose and this later 1.1287% receipt as identical precision.
- Bare sums of differential bin contents: `3.7315426459249167e-37` and
  `3.6891976275220914e-37`. Their ratio is `1.011478110602404`.
- The bare sums do not have total-cross-section units. The slide explicitly says
  that only the integrated row is in cm²/nucleon. Similar ratios do not validate
  the operands. The numerical scaling ratios are not a dimensionless physical
  factor because the two calculations have different units.

### Checkpoint example

- Population: 1,999,928 `pass_gen` rows in the historical nominal diagnostic run.
- Percentiles of relative event-weight disagreement: median `0.8340065951%`,
  p90 `16.7585606644%`, p99 `42.0590275358%`, maximum `86.6347367824%`.
- Aggregate comparison: stored fold-forward ratio `0.7464834064193581` versus
  checkpoint ratio `0.7464073747108502`; absolute difference
  `0.0000760317085079`. This is an absolute difference between dimensionless
  aggregate ratios, not 0.0001% and not a statement about the mean weight.
- Mechanism belongs to the historical Keras 2.15 configuration described in the
  finding. It is not a claim about current Keras EarlyStopping behavior.
- The repaired rerun's comparison at batch size 512 records maximum difference
  `0.0` and `GATE_AB_PASSED`. The neighboring batch-1000 receipt has a nonzero
  difference and a failed gate; it must not be silently substituted.
- The corrected run is a rerun, not the same fitted model before and after file
  editing. It fixes a reproduction failure, not the scientific validation of PET.
- The ordinary checkpoint/aggregate checks being insufficient does not mean that
  no check caught the issue: the event-level comparison DID catch it.

### Repository activity

- Non-merge counts by author month: April 8; May 50; June 86; July 263;
  August 1,970; September 1–8 265.
- July orchestration touch share: `635 / 2340 = 27.1368…%`.
- August orchestration touch share: `4582 / 7296 = 62.8015…%`.
- September orchestration touch share: `608 / 875 = 69.4857…%`.
- Each distinct path in a non-merge commit contributes one touch. Repeated edits
  to a path across commits count repeatedly. A commit can touch multiple categories.
- Categories use paths only: the 2D/3D/N-D directories; legacy or current
  orchestration directories; note/presentation directories; everything else.
  Analysis directories include tests and process code; orchestration directories
  include scientific receipts. These are not “science versus waste” categories.
- Author dates can differ from merge/integration dates. The plot is reachable
  historical activity at a fixed revision, not a diary of when work became usable.
- April covers April 25–30; September ends at the frozen September 8 snapshot.
  Partial months are labeled and hatched. No extrapolation is made.

## Changes from the earlier drafts

1. No unsupported “almost never the code” frequency claim or AI-specific bug taxonomy.
2. No “published estimator” description of a historical diagnostic PET artifact.
3. No token-based productivity or verification-bottleneck inference. Preliminary
   inspection found repeated message IDs in local Claude records, and the existing
   sweep does not deduplicate them. It also omits Codex and earlier periods.
4. No file-edit entropy interpreted as code complexity, no mutual information
   interpreted as a percentage of agent contention, and no Fano-factor causality.
5. No first-person claim that Joseph discovered a defect unless supplied by him.
6. No model-release dates presented as dates of adoption or causal interventions.
7. No higher-dimensional covariance bands or quarantined significance values.

## Validation of this presentation package

The measurement script checks the parsed non-merge population against a separate
`git rev-list --count`, checks that path categories partition all touches, checks
the cumulative agreement windows, and checks the identities of the historical
failed and repaired passing receipts. These are consistency checks, not claimed
independent verification of the underlying physics.

The slide builder checks text bounds, font glyph coverage, card containment, and
the match between slide and script counts. The PDF is drawn from the same layout
as the editable PowerPoint, not converted by PowerPoint. PDF previews are inspected;
native PowerPoint rendering can differ slightly by installed font and application.
The package is not imported by the analysis or compute launchers, so the scientific
test suite cannot be affected by these new presentation-only files.

## Model slide removal and checkpoint explanation

The standalone model-access slide was removed at Joseph's request; the workflow
history now describes coordination roles without comparing named models. The
checkpoint example (slide 11) defines a checkpoint as saved network parameters,
an epoch as a training-data pass, and best validation loss as a selection
criterion rather than proof of physics accuracy. It distinguishes learned network
parameters from the per-event unfolding weights plotted in the historical
comparison. The maximum event-weight difference is not a total-cross-section shift.
The mechanism remains tied to the existing historical finding and matched-batch
repair receipt; no present-day framework behavior is inferred.
