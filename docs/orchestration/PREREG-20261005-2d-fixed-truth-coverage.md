# Pre-registration: fixed-truth coverage of the production 2D statistical band (2026-10-05)

**Status: PRE-REGISTERED, committed before any launch.** Amendments are allowed only after the pilot
and before the full run, each appended as a dated section below. Nothing in §5–§6 may change after
any full-run toy has been scored.

Authorization: Joseph, 2026-10-05 (`/goal` launch of `HANDOFF-20261005-2d-coverage-test.md`): this
study end to end, 60 CPU node-hours on `m3246` (regular/shared/debug QOS; never premium or
overrun), outside the s5p pool.

## 1. Question, and what an answer cannot license

**Question.** Does the production 2D statistical band (ledger `VL162`) cover toy-to-toy scatter of
the 5-iteration lgbm unfold around a **fixed, unfluctuated** truth at its nominal rate?

**Scope.** The statistical band only, in fixed-truth closure toys whose prior equals the truth.
The result, pass or fail, cannot change the 2D central value, its estimator, or any adopted or
quoted uncertainty. It says nothing about systematic, ML-seed, total, FPS, 3D or 5D coverage. It does
not test regularization bias under a mis-specified prior, because in these toys the prior is the
truth.

**Campaign choice (per `CAMPAIGN-REVIEW-20260929.md` §1).** Owner: this Opus 5.5 session.
Independent review: a fresh read-only reviewer (own subagent or claude-school, Opus 5.5) of the
design, and an independent recomputation of the headline numbers from the extracted toy outputs.
Codex/Astra is excluded by Joseph's instruction, so the reviewer is not cross-model; this is stated
as a limitation, not hidden. Terminal outcomes: PASS, FAIL (any direction, including an interim
futility stop) or INCONCLUSIVE, each recorded as a result. Repair budget: a check that fails twice
after repair stops the study.

## 2. What the production band is (measured from the code, 2026-10-05)

`VL162` is the 300-replica set written by `2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_bootstrap_scaleup.sh`:

```
unfold_2d_omnifold_unbinned.py --iters 5 --use-weights --estimator lgbm \
  --bootstrap-seed N --seed 1          # N = 1..300, default --bkg-mode purity
```

The bootstrap (`unfold_2d_omnifold_unbinned.py`, block "Poisson(1) bootstrap weights") draws,
per replica, `Poisson(1)` per **data** event from `default_rng(N)` (multiplying the purity
weights) and `Poisson(1)` per **signal-MC** event from `default_rng(N + 10_000_000)`, the same draw
multiplying both `w_truth` and `w_reco`. The background MC is not fluctuated. So the band represents
**data statistics plus signal-MC statistics**, at fixed GBDT seed. Its per-bin σ is the across-replica
standard deviation (ddof = 1) of `hXSec2D`, stored as `sqrt(diag(hCov2D_reported))` in
`uq/bootstrap_MEFHC_300/uq_covariance_boot300.root` (sha256 `f7c734b1…`, reproduced by `VL162`),
with `hMean2D > 0` defining the 205 reported bins.

## 3. Toy design

One toy `t` (driver `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py`, pure pieces in
`toy_design.py`) reuses the production driver's helpers unchanged and repeats its
`--closure --use-weights` path:

| Element | Toy | Mirrors |
|---|---|---|
| Pseudo-data | each closure event `i` (`pass_reco & pass_truth`) enters `k_i ~ Poisson(w_reco,i)` times; `w_reco` is POT-scaled to data, so the sample has data-sized Poisson statistics and expectation equal to the MC reco distribution. Zero-count events are dropped; a selected event is one row of weight `k_i`. | the data stream of the production bootstrap (a data-sized Poisson sample) |
| MC | `b_i ~ Poisson(1)` per signal event multiplying `w_truth` and `w_reco` | the production MC stream, exactly |
| Truth | `hTruthFixedXSec2D`: the **unfluctuated** MC truth marginal (`w_truth` before any draw, `pass_truth` events), through the same `extract_cross_section_2d` normalization (completeness ≡ 1, as in closure) | — |
| Estimator | lgbm, 5 iterations, `--seed 1`, `--use-weights` | the `VL162` replicas |
| Seeds | data `20_261_005_000_000 + t`, MC `20_261_005_500_000 + t`; full run `t = 1..200`, pilot `t = 9001..9003` | disjoint from production (1..300, 10_000_001..300) and the old toys (1001..1200, 10_001_001..200); tested |

**Independence (design item 3).** No split sample. Given the MC sample, the pseudo-data draws `k`
and the MC draws `b` are independent, and the target is the truth of the very population the
pseudo-data are drawn from (the full MC). That is the bootstrap-world image of the real
measurement: data drawn from the population, an independent finite MC, and the population's truth as
target. A split sample would give the response half the production MC statistics, so its MC-stat
scatter would no longer match the band. It would also freeze one realization of the
pseudo-data-half versus response-half difference, and that common offset cannot be scored as a
frequency. The residual same-sample effect is that pseudo-data rows coincide with MC rows in feature
space. lgbm bins features and trains on leaves of many events, so we do not expect a per-row
memorization channel. It is listed as a limitation, not measured.

**Known differences from the production measurement, stated before the run.** (a) No background
subtraction in closure (production purity weights ≈ 0.996; the background MC is not bootstrapped in
production either). (b) Prior = truth: no regularization bias is present to be covered. (c) The
toy band is `r_b · T_b` with `r_b` the production relative σ (§5), so the band is transferred from
data level to MC level by its relative size; MC/data differs by a few percent per bin, which
changes `r_b` by ~1 % of itself.

**Equivalence check (makes "repeats the production path" a measurement).** `sbatch_equivalence.sh`
runs the production driver (`--closure --use-weights --estimator lgbm --seed 1`, no bootstrap) and
`fixed_truth_toy.py --no-fluctuation`. `compare_equivalence.py` requires `hXSec2D` agreement to
relative 1e-6 on every bin, and both truth histograms equal to the production `hTruthXSec2D`
exactly.

## 4. Pilot (2–3 toys) and its pass conditions

Pilot toys `9001–9003` plus the two equivalence runs. The pilot passes only if all of these hold:

- **P1** equivalence check passes;
- **P2** `hTruthFixedXSec2D` is bit-identical across the pilot toys and equal to the equivalence
  run's production `hTruthXSec2D`;
- **P3** units: `Σ T·ΔA` is within 10 % of the production central total 3.073e-38 cm²/nucleon, and
  every reported bin has `T > 0`;
- **P4** pseudo-data size: `Σ k` is within 5σ (Poisson) of `Σ w_reco` on the closure events;
- **P5** the scorer runs on the pilot outputs (`--stage pilot`) with finite `z` on all 205 bins;
- **P6** cost: measured node-hours per toy (`sacct` ElapsedRaw × billing/256 × QOS factor) gives a
  projected total (pilot + equivalence + N toys × measured mean × 1.05) ≤ 60. If 200 toys do not fit,
  N is cut by amendment to the largest value that fits, and never below the minimum of 150; if 150 do
  not fit, the study stops and reports.

Pilot toys are never scored in the full-run verdict. A pilot failure may be repaired and the pilot
re-run; two failures of the same check after repair stop the study.

## 5. Scoring (the verdict's executable form is `score_coverage.py`)

For toy `t` and reported bin `b`:

```
r_b = prod_sigma_b / prod_mean_b            (VL162 rollup)
σ_b = r_b · T_b,     z_tb = (U_tb − T_b) / σ_b
```

- **Primary statistics.** Pooled coverage `C1 = mean 1{|z| ≤ 1}`, `C2 = mean 1{|z| ≤ 2}` over all
  (toy, bin) pairs. Nominal: 0.682689, 0.954500.
- **Intervals.** Toy bootstrap: resample toys with replacement, never bins, 20,000 resamples,
  generator seed 20261005, percentile intervals. Each toy keeps all 205 bins, so bin correlations
  within a toy are preserved.
- **Window (tolerance).** The band counts as nominal if its ratio to the true scatter lies in
  [0.9, 1.1]. Under Gaussian scatter that gives `C1 ∈ [0.631880, 0.728668]` and
  `C2 ∈ [0.928139, 0.972193]`.
- **Verdict at the final look (≥ 150 toys, 95 % intervals).**
  - **PASS**: both intervals lie inside their windows.
  - **FAIL-undercoverage / FAIL-overcoverage**: at least one interval lies entirely below (or
    above) its window and none on the other side. **FAIL-mixed** if they lie on opposite sides.
  - **INCONCLUSIVE**: otherwise.
- **Interim futility look** at toys 1–100 (99.5 % intervals). If the interim result is any FAIL, the
  study stops, and that FAIL is the verdict ("futility"). Otherwise toys 101–200 run. The two looks
  spend α ≈ 0.005 + 0.05.
- **Secondary (reported, no verdict role).** Pull RMS and mean pull, with intervals; the per-bin
  coverage distribution (median, min, max); the per-bin RMS median.
- **Validity.** A toy is in the scored set iff its job finished with a resume-guard `.done` marker.
  A failed job is re-run with the same index and therefore the same seeds. No toy is excluded for
  its values. If any toy's stored truth differs from another's, the whole set is **INVALID**: the
  fixed-truth premise has failed, and that is a stop condition.

## 6. Positive control (on the real toy outputs)

The scorer is re-run with the band scaled by 0.7 and by 1.3. The control passes iff:

1. at ×0.7, both coverage intervals lie entirely below the ×1.0 point estimates, and at ×1.3,
   entirely above;
2. if the ×1.0 verdict is PASS, the ×0.7 verdict is FAIL-undercoverage and the ×1.3 verdict is
   FAIL-overcoverage.

If (2) fails, the PASS is void and is reported as INCONCLUSIVE (positive control failed). The
synthetic tests in `test_coverage_fixed_truth.py` check the same logic. They are not a substitute
for this control.

## 7. Compute plan and stop rules

- **Balance measured 2026-10-05 07:2x UTC** (`iris` on login09): `m3246` charged 16863.6 of
  20000.0 node-h (3136.4 remaining); user 1971.9 of 10000.0.
- **Estimate.** One 5-iteration lgbm MEFHC unfold is 13m24s on a 128-CPU node (2D status "Runtime
  budget"). One exclusive regular node costs 1 node-h per hour, so a toy is ≈0.22–0.25 node-h.
  Pilot plus equivalence is 5 runs ≈ 1.3 node-h; 200 toys ≈ 45–50 node-h. Total ≈ 47–52 against
  the 60 cap.
- **Launch.** Regular QOS, 1 node, 128 CPUs, 1 h limit. Full run in two waves (1–100, then 101–200
  after the interim look).
- **Accounting.** Each job is charged by `sacct`, using the s5c/s5p billing rule.
  The ledger lives in `docs/orchestration/state/coverage-2d-20261005/budget.json`. It is separate
  from the s5p pool, and no s5p job, state or budget is touched.
- **Stop and report** if the projected cost exceeds 60, if the NERSC certificate expires (valid to
  2026-10-06 06:26 UTC), if the design would need a change to production code that other results
  depend on, or if a check fails twice after repair.

## 8. Independent recomputation and records

A fresh read-only reviewer recomputes `C1`, `C2` and the pull RMS from the extracted npz with their
own code. The point estimates must agree to 1e-12. The interval endpoints must agree within 0.003,
the allowance for a different resampling stream. Records: a ledger row with the next free VL id
across all remote refs, `2D_OMNIFOLD_STUDY_STATUS.md`, `KNOWN_ISSUES.md` if anything opens, and the
receipts under `docs/orchestration/state/coverage-2d-20261005/`.
