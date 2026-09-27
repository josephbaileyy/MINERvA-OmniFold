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

So each clipped universe equals the analysis's universe to <= 4.2% of its own shift in the worst cell (median 0) and
<= 1% of a cell's statistical sigma: the drawn band shifts, hence the interaction-model prior's covariance (the band
sum), are unchanged to that level; resetting those rows to CV instead would differ from keeping them by <= 1.7% of
sigma, so the choice between the two finite treatments is immaterial, and clipping keeps every Poisson mean valid.

## Conditions kept

Development only (`stage3_repair2`, existing caps); no scientific gate relaxed; no other retry limit reset; no
production authorized. The five products of the defective run are set aside (history), not reused.

## Review outcome

(appended after the independent review)
