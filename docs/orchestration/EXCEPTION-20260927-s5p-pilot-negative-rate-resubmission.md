# Exception 2026-09-27: one additional corrective resubmission of the s5p all-band design pilot

**CITABLE FOR:** the owner's exception to the budget's retry rule for one development job, its conditions, the
evidence required before using it, and (appended) the review outcome. **NOT CITABLE FOR:** any other retry, any
relaxed gate, production, or any result.

## The authorization (Joseph, 2026-09-27, in the s5p session; verbatim)

> I authorize one additional corrective resubmission for the all-band pilot's negative-rate failure, plus the
> bounded diagnostic and independent review needed to validate that repair. Before resubmitting, quantify the
> weighted and per-cell effect of the proposed negative-weight treatment and justify its effect on the nuisance
> distribution; do not silently zero nonfinite values. Keep this work in development, within existing resource
> caps. This exception does not relax scientific gates, reset other retry limits, or authorize production. Record
> the exception and the review outcome.
> Only if you think it is necessary though

## Why the campaign uses it

Without it the V ensemble and the development power would have moved into the production stage (a design element
review round 2 never saw, with V built after the admission freeze). With it, V and development power exist before
the admission is frozen and reviewed, as review round 2 (L1) asked. Scope: the one job `s3v-pilot-tasks.tsv`
(61 lines, stage `stage3_repair2`, existing caps); nothing else.

## The failure and the treatment

- Job 58954259 failed (`lam < 0 or lam contains NaNs` in the pseudo-data Poisson draw): LowQ2_1 carries negative
  weights on 462 rows (435 reco-passing) and HighQ2_1 on 99 (94); the 99 are also negative in LowQ2_1.
- Treatment (`nd-unfolding/s5p_nullexp.py` `checked_ratio`, `ModelCache._ratios`): an interaction-model universe's
  negative weight RATIO is clipped to 0 per universe, before any product (so two negative bands never multiply into
  a positive weight), and counted in each experiment's `weight_treatment`; a non-finite ratio is REFUSED on any row
  where that weight is used and set to 1 only where the weight is never read (a reco weight of a reco-failing row),
  counted; a negative flux or detector ratio is refused; the combined factors must be finite and non-negative or
  the experiment is refused. `s5p_universe.weights(..., nonfinite='keep')` is used, so no loader zeroes silently.
- The one non-finite case found: MinosEfficiency_0/1 in the detector dump, 18 rows each, all reco-failing (their CV
  reco weight is never read into the pseudo-data): set to 1 and counted, per the rule above. All 324 flux and
  detector arrays were scanned; no other non-finite or negative value.

## Quantified effect (`docs/orchestration/state/s5p/stage3/negw/negative-weight-diagnostic.json`)

Reco-level J cells (the joint test's cells at reco level), clipping versus keeping the negative weights (the
analysis's histograms keep them):

| universe | negative weight / total reco weight | max \|clip - keep\| / cell yield | max over cells of \|clip - keep\| / band shift | max \|clip - keep\| / stat sigma | cells touched |
|---|---:|---:|---:|---:|---:|
| LowQ2_1 | 3e-6 | 2.1e-5 | 0.042 (median 0) | 0.010 | 57 |
| HighQ2_1 | ~1e-7 | 1e-6 | 1.3e-4 | 2.8e-4 | 21 |

For the RAW universe (reco weights, no truth preservation), each clipped universe equals the analysis's universe to
<= 4.2% of its own shift in the worst cell (median 0) and <= 1% of a cell's statistical sigma (here sigma = the
square root of the per-cell sum of squared MC reco weights: an MC-statistics scale). The review (below) replaced
this per-cell ratio by the adequate statistic, the whitened norm, with the truth preservation the pipeline applies:
clip minus keep is 0.0040 sigma (signal and background) against the band's own 3.79 sigma at J resolution, and
0.039 sigma against 11.06 sigma (0.35% of the band's shift) at the fine reco resolution; with truth preservation the
per-cell ratio reaches 2.58 only in cells where the band shift itself is ~0 (absolute <= 1.4e-3 sigma). The effect on
V (a covariance of unfolded J cells from 200 experiments, sampling error ~10%) and on the development power is
negligible. Resetting those rows to CV instead would differ from keeping them by <= 1.7% of sigma, so the choice
between the two finite treatments is immaterial, and clipping keeps every Poisson mean valid.

**Background weights (review condition C1).** The clipping also acts on the background source: LowQ2_1 has negative
background weights on 50 rows (7.6e-6 of the background weight, |ratio| up to 42.8) and HighQ2_1 on 5; their effect
is <= 5.4e-4 sigma per J cell and <= 1.6% sigma per fine cell; they are clipped per universe and counted like the
signal rows.

## Conditions kept

Development only (`stage3_repair2`, existing caps); no scientific gate relaxed; no other retry limit reset; no
production authorized. The five products of the defective run are set aside (history), not reused.

## Review outcome (2026-09-27, independent reviewer, read-only worktree `../MINERvA-OmniFold-s5p-review3` at `3e5f0c23`, left clean)

**REPAIR VALIDATED, with two documentation conditions, both met above** (C1: disclose the background clipping;
C2: restrict the per-cell 4.2% statement to the raw universe and give the whitened-norm statement). Independently
measured: LowQ2_1 and HighQ2_1 are the only universes (of 175 in the bank and 8 in the detector dump) with negative
values; the MinosEfficiency non-finite rows are all reco-failing with CV reco weight > 0 (so the refusal/declared
rule, not the CV branch, handles them); the diagnostic's numbers reproduce (relative max 2.068e-5, 0.04216 of the
band shift, 57 cells); a dry run of the fixed code on the real inputs for the seeds that failed (and for P1r-P3r
seeds, some drawing both negative universes) gives finite, non-negative Poisson means with nothing refused; across
the 200 V seeds LowQ2_1 is drawn 97 times, HighQ2_1 97, both 46 (why 12 of 12 tasks failed); peak memory 32.7 of
56 GB, ~76 min per six-seed line against 2.5 h. The two-negative-bands test fails on the pre-repair code exactly
where it guards (the old product reached +2790x CV on 99 rows). Advisory (not conditions): the used-row masks of the
model/flux/background paths and the final backstop are not individually mutation-tested; `weight_treatment` records
counts, not magnitudes; the diagnostic had no committed producer (now `nd-unfolding/s5p_negw_diagnostic.py`); the
pilot never draws MinosEfficiency (GEANT only), so that rule first matters in production. Record:
the reviewer's scratch `/pscratch/sd/j/josephrb/s5p-20260926/review3/`.

**Used:** the one additional corrective resubmission (`s3v-pilot-tasks.tsv` unchanged; queue `s3v-pilot2.q`).
