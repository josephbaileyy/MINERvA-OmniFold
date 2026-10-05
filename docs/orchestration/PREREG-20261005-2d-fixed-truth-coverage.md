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

## Amendment 1 (2026-10-05, after the design review and the pilot, before any full-run toy)

Source: an independent read-only design review of `e12af23e` (fresh Opus 5.5 subagent, same model
family as the owner): no BLOCK, one MAJOR and five MINOR findings. Pilot results follow in
§A1.7. Nothing in this amendment depends on a full-run toy, because none had been launched.

**A1.1 (MAJOR) The VL162 band contains a completeness fluctuation the central value does not.** In
`unfold_2d_omnifold_unbinned.py` the bootstrap multiplies `sig["w_truth"]` by the MC draw *before*
`compute_omnifold_completeness_2d`. That function fills its numerator from those bootstrapped
weights and its denominator from the never-bootstrapped `mc_truth_denom` tree, and the cross
section is divided by the result. Each replica is therefore `U_b · T/P_b` per truth bin, with
`P_b ∝ Σ b·w_truth` the replica's MC truth. The central value has `c ≡ 1` exactly, because
numerator and denominator are the same events (Phase 17), and so do the toys. **The primary
scoring is unchanged**: it scores the estimator that produces the central value. A **secondary,
replica-form scoring** is added: `U·T/P` with the toy's own prior `P` (`hTruthXSec2D`), scored
against the same band with the same windows and verdict rule. The secondary has no verdict role.
It serves attribution only:

- If the primary result is a FAIL-overcoverage and the replica form is not, the overcoverage is
  attributed to the completeness term in the band's construction.
- If both FAIL in the same direction, that term does not explain the miscoverage.

**A1.2 (MINOR) Band transfer.** The pilot records the distribution of `prod_mean/T` over the 205
bins (§A1.7). `r_b` is not rescaled.

**A1.3 (MINOR) The MC-stat part is close to circular.** The toys' MC scatter comes from the same
Poisson(1) resampling of the same MC that built the band. The test therefore cannot detect a
failure of the bootstrap principle for the MC stream; only the data stream is tested by a
different mechanism (genuine Poisson pseudo-data). Disclosed as a limitation.

**A1.4 (MINOR) Fixed-seed closure bias.** `compare_equivalence.py --rollup` reports
`(U0 − T)/(r_b T_b)` on the reported bins from the no-fluctuation run. This is the bias the seed-1
estimator carries into every toy, so an undercoverage can be attributed to bias or to width.
Secondary, no verdict role.

**A1.5 (MINOR) P1 is an exact-reproduction test.** Under lgbm multithreading, a difference shows up
as a flipped split, not as rounding. If P1 fails, each side is re-run twice before the failure
counts.

**A1.6 (MINOR) Text aligned with the code.**

- (a) The positive control passes only if condition (1) holds and, for a PASS, condition (2)
  holds. A PASS is void if either fails (`score_coverage.py`, `positive_control` and `run`).
- (b) Too few toys gives the decision **INSUFFICIENT-TOYS**, not INVALID. INVALID remains the
  truth-mismatch stop condition.
- (c) The false-FAIL rate at a window edge is up to about twice the per-look α, because C1 and C2
  can each trigger it: ≲ 0.01 at the interim look and ≲ 0.10 at the final look in the worst case.

**A1.7 Pilot results (toys 9001–9003 and the two equivalence runs; Perlmutter, 2026-10-05).**
Jobs 59358992_{9001,9002,9003} and 59358994_{1,2}, all `regular_1`, 1 node, billing 256.
Extraction and pilot scoring used the amended `extract_toys.py`/`score_coverage.py` from this
commit. Receipts are in `docs/orchestration/state/coverage-2d-20261005/`.

- **P1** (equivalence, exact reproduction, A1.5): **pass on the first run.** `hXSec2D` from the production driver's `--closure` run and from `fixed_truth_toy.py --no-fluctuation` agree exactly (maximum relative difference 0), and both truths equal the production `hTruthXSec2D` exactly. Both runs did five iterations. The production log shows step-2 weights with mean, minimum and maximum all exactly 1.0000, because the closure pseudo-data and the simulation are the same weighted events, so lgbm finds no split. The A1.4 closure bias `(U0 − T)/(r_b T_b)` is therefore exactly 0 on all 205 bins. The seed-1 estimator carries no bias into the toys at the unfluctuated point, so any toy miscoverage is a property of the band width relative to the toy scatter, not of a fixed closure offset.
- **P2 — pass.** `hTruthFixedXSec2D` is bit-identical across the three toys and to the production
  driver's `hTruthXSec2D` from the `--closure` run (maximum absolute difference 0).
- **P3 — failed as written, then repaired; passes after repair.** The reference in §4 was wrong:
  3.073e-38 is the *unfolded data* total (`\sigTwoD`), but the toy truth is the *MC* truth.
  The analysis MC (MINERvA Tune v1) totals 2.71e-38 over the same phase space (`sec_3d.tex`,
  model comparison), about 12 % below data. Measured `Σ T·ΔA` = 2.70598e-38 is 0.88 of the data
  total, outside the 10 % bound, and 0.9985 of the Tune v1 total. The production driver's own
  closure run prints the same 2.706e-38. **Repair:** the P3 reference becomes the analysis MC
  truth total 2.71e-38, with the 10 % bound unchanged. The purpose of P3 (catch a POT, flux or
  bin-width unit error) is unchanged, and P2 already ties T bit-exactly to the production code
  path. All 205 reported bins have `T > 0`. Under §4 this is the check's first failure. Another
  failure of P3 after this repair would stop the study.
- **P4 — pass.** `Σ k` = 3534504, 3533531 and 3533608 against `Σ w_reco` = 3533843.46
  (Poisson σ ≈ 1880): +0.35σ, −0.17σ and −0.13σ.
- **P5 — pass.** The scorer runs with finite `z` on all 205 bins for every pilot toy.
- **P6 — pass.** ElapsedRaw for the toys is 660, 750 and 730 s; the mean of 713 s is 0.198 node-h
  per toy (billing 256/256, `regular_1` factor 1.0). The projection is the pilot (0.594) plus
  equivalence (0.204: 383 s and 350 s) plus 200 × 0.198 × 1.05 (41.6), for a total of 42.4 node-h ≤ 60. N stays at 200.
- **A1.2 record.** Over the 205 reported bins, `prod_mean/T` has minimum 0.737, 16th percentile
  1.023, median 1.145, 84th percentile 1.272 and maximum 1.712.
- **Pilot pulls (three toys; no verdict role, recorded for completeness).** Per-toy `|z| ≤ 1`
  fractions are 0.707, 0.659 and 0.659. The `|z| ≤ 2` fractions are 0.922, 0.873 and 0.932. Mean
  `z²` values are 1.67, 1.83 and 2.51. In the replica form (A1.1) the `|z| ≤ 1` fractions are 0.902, 0.737 and
  0.878, and mean `z²` is 0.45, 0.95 and 0.41.

**A1.8 The A1.1 attribution rule is made symmetric (written after the pilot pulls above were
seen, before any full-run toy).** A1.1 named only the overcoverage case. The pilot shows that the
replica form can move the pulls in either direction, because `U` and the toy's prior `P` both
move with the same MC draw. The rule now reads:

- If the primary result is a FAIL in either direction and the replica form is not a FAIL in that
  direction, the primary miscoverage is attributed to the completeness term the VL162 replicas
  carry and the central value does not.
- If both FAIL in the same direction, that term does not explain it.

The rule stays attribution only. It does not change the primary verdict, the windows, the
intervals, the positive control or N. The A1.4 closure bias is reported alongside it.

## Amendment 2 (2026-10-05 ~18:40 UTC, during wave 1, before any full-run toy output was read)

Operational only. No definition, window, interval, verdict rule, control or N changes. No
full-run toy file had been opened or extracted when this was written.

**A2.1 Queue lanes.** The regular queue started about 2.5 toys/h, which would not finish before
the NERSC certificate expires. Pending indices of the wave array are therefore moved into two
more lanes. A pending task is cancelled (`scancel --state=PENDING`, so a running task is never
touched) and the same index is resubmitted with the same script and commit:

- **debug**: at most 2 at a time (the QOS per-user limit), 128 CPUs, 30 min limit, taking the
  highest pending index;
- **shared**: at most 12 at a time, 64 CPUs, 1 h limit, taking the lowest pending index.

An index keeps its seeds and its output path, and outputs publish atomically through the resume
guard. The scored set is still "every index 1–200 with a `.done` marker". Both QOS have usage
factor 1.0, and neither is premium or overrun. The s5p campaign's jobs, state and budget are not
touched. Regular and debug submissions carry a 30 min limit, against a measured 10–13 min, which
bounds the cost of a runaway job.

**A2.2 Thread count in the shared lane.** `OMP_NUM_THREADS` follows `--cpus-per-task`, so
shared-lane toys run lgbm with 64 threads instead of 128. Histogram summation order can then
differ, so a shared-lane toy is not bit-identical to the same index at 128 threads. It is the
same estimator, inputs and seeds. P1 established exact reproduction at 128 threads. Each toy's
QOS is recorded from `sacct` in the receipts. The final report gives C1 and C2 split by lane as
a descriptive check with no verdict role.

**A2.3 Cost.** The shared-lane test toy (index 17, job 59384420) took 1091 s at billing 64/256,
which is 0.076 node-h. Regular and debug toys take 0.20 node-h. The projected total stays below
the 0.198 × 200 × 1.05 bound of A1.7 (42.4 node-h), whatever the lane mix.

The lane feeder is `docs/orchestration/state/coverage-2d-20261005/tools/qos_feeder.sh`, run from the workstation over ssh.

**A2.4 Incident.** The first version of the debug feeder cancelled pending index 100 and did
not resubmit it, because `sacct` gives no state for a cancelled pending array element. It was
stopped after that one index. Index 100 was resubmitted by hand on debug (job 59374208), with the
same seeds, and no other index was affected. The feeder now checks `squeue` instead.

## Outcome (2026-10-05, after the interim look; no criterion above was changed)

FAIL-undercoverage by the interim futility rule at toys 1–100. Toys 101–200 were not run. The
verdict, intervals, positive control, attribution and recomputation are in
[`OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`](OUTCOME-20261005-2d-fixed-truth-coverage-fail.md)
(ledger `VL168`).
