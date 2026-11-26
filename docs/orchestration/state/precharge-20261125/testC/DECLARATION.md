# Test C: choices declared before any run, fit or score

Joseph approved test C on 2026-11-26, as `../test1/NEXT.md` describes it. This file fixes the cluster request, the positive controls, every fit choice, the metric and the readings before any job runs. No true neutrino energy for this sample has been produced or seen. Any later change is made in a new commit that says what changed and why, and the original reading is reported alongside.

**What has already been seen.** The held-out playlists are not untouched for this pattern. Test 1 and tests A and B printed held-out yields by reco p∥ band, E_avail bin and curvature precision (`../test1/test1.txt`, `../testAB/`). Test C was proposed after B came back inconclusive. What this declaration protects against is choosing the reweight form, support, scored terms or thresholds after seeing how the Eν model scores.

## Cluster request

- **Programs.** `measure.cpp` is `../measure.cpp` with three changes. It refuses Data. It refuses any file whose `MasterAnaDev` tree lacks `mc_incomingE`. It appends one column, `true_enu` = `mc_incomingE`/1000 (GeV). Every other line, cut, weight and print format is unchanged, so its first 12 columns must reproduce the saved MC tables (control P1). `truth.cpp` loops the `Truth` tree with the same configuration and weights in truth mode. It keeps the published signal (ν_μ, CC, tracker 5980–8422 mm, apothem 850 mm, muon angle < 20°, true p∥ > 1.5 GeV/c), the cuts of `MINERvA101/MINERvA-101-Cross-Section/runEventLoop.cpp`. It writes weighted counts by published true (p_T, p∥) cell and 0.5 GeV Eν bin. It refuses any file whose `Truth` tree lacks `mc_incomingE`, `mc_run`, `mc_subrun` or `mc_nthEvtInFile`. That per-file check is how the branch name is verified on the tree. No separate login-node probe is made.
- **Build.** `build.sh` checks `staged.sha256` and compiles both programs in the archived MAT environment of `../build.sh` (same compiler, flags, CVUniverse source and libraries). It writes `built.sha256`. Every task re-checks both files before it starts.
- **Jobs.** `batch.sh` is a one-core `shared` array on account m3246, 4 GB, one task per playlist (`1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P`), MC only. Mode `reco` reruns the reco table, and mode `truth` writes the denominators. 24 tasks in all, submitted in two stages:
  1. **Pilot.** `sbatch --array=7 -t 01:00:00 batch.sh reco` and `sbatch --array=7 -t 04:00:00 batch.sh truth` (1L, the smallest MC playlist at 1.06 M reco entries). Both outputs are fetched, and P1 and P2 are run on 1L.
  2. **Remainder,** only if the pilot passes P1 and P2 and the projected truth time fits. `sbatch --array=0-6,8-11 -t 01:00:00 batch.sh reco` and `sbatch --array=0-6,8-11 -t 04:00:00 batch.sh truth`. The truth time is projected as the 1L elapsed time × (MC reco entries / 1.06 M), using `../file-counts.txt`. The largest playlist is 1M at 16.3 M entries. If any projection exceeds 3.5 hours, nothing more is submitted, and a resized request goes back to the director.
- **Node-hours.** The upper bound at the time limits is 12 × 1 h + 12 × 4 h = 60 task-hours. On Perlmutter CPU a 4 GB request may be charged as two physical cores of 128, so the bound is 60 × 2/128 = **0.94 node-hours**. The reco tasks should take well under the hour, since the earlier scan finished Data and MC for every playlist, 1M included, within its 45-minute limit. The truth-pass time is not known until the pilot runs, which is why the remainder waits for the pilot's projection. The actual charge is read from `sacct` elapsed times after the run and reported, never this estimate.
- **Where things are written.** Everything is under `/pscratch/sd/j/josephrb/precharge-testC-20261126/` (sources, binaries, `logs/`, outputs). Jobs read the archived manifests, the AnaTuples, the CVUniverse source and the environment script, and write nothing outside that scratch directory. Nothing is written to CFS. The outputs are copied back to this branch by `scp`. Only the `true_enu` column (after P1 passes), the truth tables, the logs and the sha256 of every scratch output are committed.

## Positive controls (all must pass before any score)

- **P1, identity.** For every playlist, the first 12 columns of the new reco table are byte-identical to `../inputs/events/<pl>_MC.csv.gz` after decompression. Same row count, same order. A single mismatch stops the test. No score is computed, and the mismatch is reported.
- **P2, denominators.** For every playlist and each of the 224 cells with at least 100 generated events, the truth table summed over Eν agrees with that playlist's nominal generated histogram (`<pl>_T` in `../inputs/replay/playlists.npz`) to 0.1%. The check is made both with and without duplicate keys. The version that passes is the one used, and it is reported. If neither passes, the test stops with no score.
- **P3, kinematics.** Fewer than 10⁻⁴ of truth-table signal events have Eν < E_μ (printed by `truth.cpp`). In the reco table, `true_enu` is finite and positive for every fiducial ν_μ CC row.

## The reweight

**Weight.** log w(Eν) uses the three bases of `../test1/test1.py` (quadratic, cubic, and piecewise linear with 5 interior knots), in t = (clip(Eν, lo, hi) − lo)/(hi − lo). w is constant outside [lo, hi]. lo = 20 GeV. hi is the 99th percentile of fold-weighted Eν in the training fit sample, rounded up to a multiple of 10 GeV. That uses MC only. The **primary form is piecewise linear**. The other two are reported as sensitivity checks.

**No constant term.** log w has no constant column, so w = 1 at Eν ≤ lo. The rate below 20 GeV is therefore unchanged, and so is every in-grid cell through the anchor. The pwlinear form has 6 parameters, quadratic 2 and cubic 3. *Changed in the second commit, before any run or score.* The first version kept Test 1's constant column. The closure check of `test_c.py` found that the anchor cancels a constant in-grid, so the constant was set only by the few unanchored rows at reco 20–40 (σ ≈ 5 in log w). That inflated the held-out prediction variance (±1,470 events at 50–60), and an inflated variance would let the "supports" clause pass spuriously. With no constant term, the closure recovers the injected coefficients and the 50–60 prediction error is ±102.

**Closure check (code only).** `python3 test_c.py --closure` replaces true Eν with a stand-in (true muon energy + reco E_avail). It builds stand-in denominators from the selected rows, and it replaces every observed count with the MC expectation under an injected w. It reads no Data row and no true Eν. A correct implementation recovers the injected coefficients with χ² ≈ 0 in both directions and all three forms. Its output is `closure.txt`.

**Where it applies.** `../score.py` fixes three classes of simulated rows, and the reweight is set per class:
- **In the published phase space** (fiducial ν_μ CC, true p∥ 1.5–60, p_T < 4.5, angle < 20°). Each row becomes fold × w(Eν) × G_c / G′_c. G_c is the nominal generated count in its true cell, and G′_c is the same count weighted by w. Both come from the truth tables summed over all 12 playlists, MC only, using the bin center for each 0.5 GeV Eν bin. The published cross section in every cell is therefore unchanged, and the efficiency in each cell follows the reweighted Eν mix.
- **Other fiducial ν_μ CC rows** (true p∥ ≥ 60, p_T ≥ 4.5 or angle ≥ 20°). These become tune_weight × w(Eν), with no anchor.
- **Every other row** (ν̄_μ, NC, non-fiducial). Unchanged.

**Fit.** The fit sample is the training playlists, reco p∥ 20–40, negative tracks with good curvature (|σ(q/p)/(q/p)| < 0.30). The fit variable is E_vis in the 2 GeV bins of Test 1 (20–100), with a binned Poisson likelihood and MC scaled by each playlist's own POT. That is the Test 1 fit with E_vis replaced by Eν as the reweight variable and with the anchor added. G′ depends on the parameters, so the likelihood is minimized by BFGS from w = 1 with the analytic gradient. The covariance is the inverse Fisher information at the minimum, Σ_b J_b J_bᵀ/μ_b, where J_b = ∂μ_b/∂β. That is Test 1's Xᵀ μ X generalized to the anchored model. (Also changed in the second commit, before any run: the first version said "inverse numerical Hessian".)

**Directions.** The primary direction fits on training (`1A 1C 1E 1G 1M 1O`) and scores held-out (`1B 1D 1F 1L 1N 1P`). The swap is reported under the same readings.

## Scored on held-out, fixed before any score

Bands are reco p∥ 40–50, 50–60, 60–80 and ≥80.
- **T1.** Negative tracks, all curvature precisions, by band × E_avail bin with edges −∞, 1, 2, 5, 10, 20 and ∞ GeV (24 yields, the Test 1 table).
- **T2.** The good-curvature fraction of negative tracks per band (4 binomial terms).
- **T3.** Positive tracks, all precisions, per band (4 yields, absolute, with no normalization from held-out data).

**Variance.** The A/B choices (`../testAB/common.py`, `../testAB/test_b.py`), with the fit-parameter variance added to the fractions:
- **Yields.** The variance is the predicted count μ, plus the MC sum of squared weights, plus the fit-parameter variance and a floor of (0.02 μ)². The parameter variance uses linear propagation with the full covariance and the analytic Jacobian.
- **Fractions.** In counts, the variance is n f(1 − f) + n² (v_MC + v_par). Here n is the observed number of negative tracks in the band, f is the predicted fraction, v_MC is its MC statistical variance by the delta method (as in B), and v_par is its fit-parameter variance. There is no floor.

*Correction, made before any run or score (second commit).* The first version of this paragraph used max(observed, 1) for yields and the data fraction for the binomial term, while saying it was the A/B choice. A and B use μ and the predicted f, so the paragraph now matches them. Nothing had been fitted or scored when this was changed.

Only terms whose nominal held-out fold is at least 5 are scored. That is decided from MC alone. The metric is the Pearson χ² over the scored terms, with degrees of freedom equal to the number of terms. The nominal fold (w = 1) is scored the same way.

## Readings

Hypothesis H_C is that a smooth reweight of the simulated rate in true Eν, fitted at reco 20–40 and anchored to the published cross section inside the grid, describes the held-out high-p∥ yields, E_avail shapes, precision and sign pattern.

- **Supports:** in both directions, the primary form's held-out p ≥ 0.01, and its χ² is at least 9 below the nominal fold's.
- **Contradicts:** in both directions, the primary form's held-out p < 0.001.
- **Inconclusive:** anything else, including the two directions disagreeing.

The following are printed and do not change the reading:
- the T1, T2 and T3 contributions;
- the quadratic and cubic forms;
- the 20–40 transfer;
- the share of the data − fold excess at 50–60, 60–80 and ≥80 carried by the prediction;
- a comparison with Test 1's w(E_vis).

If the training fit deviance per degree of freedom exceeds 3, that is stated with the reading.

**What each outcome would mean** (none is a cause determination, and no note sentence follows from any of them):
- **Supports.** The pattern is consistent with Tune v1 missing rate at high Eν, which at fixed muon kinematics means high inelasticity. Inside the grid the published anchor would hold, and the true ≥60 tail rate would carry the rest. That points to a model-level check, such as the high-Eν flux shape or the DIS/high-W weights. It does not exclude a detector effect that produces the same pattern.
- **Contradicts.** A muon-independent recoil function (A), a constant curvature offset (B) and a smooth Eν rate change fitted at 20–40 (C) would all fail to transfer. That would leave effects that are not smooth in Eν, or that live where the 20–40 fit has no lever, such as an unanchored change confined to true ≥60. It would not by itself establish a detector cause.
- **Inconclusive.** As for B: the share of the excess carried and the term contributions say which part of the pattern a rate change can and cannot describe.

**Limitation stated in advance.** Above hi, w is held constant, and true ≥60 rows carry w with no anchor, so the ≥60 prediction depends on the fit's high-Eν end. The 99th-percentile rule fixes hi before any score.

## Output

Results go in this folder. `test_c.py` and `controls.py` are committed before the outputs are fetched. One `analyze.sh` regenerates every local output from the committed inputs, and every number comes from a committed script. `controls.py` runs once on the fetched scratch outputs, whose sha256 are committed in `inputs/fetched.sha256`; its record is `controls.json`. (Changed in the second commit, before any run: the first version named the local driver `run.sh`, which is the cluster task script.) The report gives the outcome against these readings, the P1–P3 results and the `sacct` charge.
