# s5n Stage-1 independent review — round 1 (construction) and round 2 (targeted full-n verification)

Reviewer: an independent agent in the isolated read-only worktree `MINERvA-OmniFold-s5n-review1` (detached
at `82dc1517`), with its own code; outputs `review1/` beside this file (copied from
`/pscratch/sd/j/josephrb/s5n-20260925/review1/`). No Slurm submission; nothing written outside its scratch
directory; the review worktree's `git status --porcelain` was empty after each round. The reports are
reproduced as returned; the author's dispositions follow each.

## Round 1 (products partial: nominal n=30, eavail n=27, q3 n=21, σ 112 of 200)

Construction mechanics hold (independent rebuild of pseudo-experiments and refinement refit reproduce the
products exactly); two interpretations do not.

| claim | verdict | reviewer's numbers |
|---|---|---|
| 1 construction | CONFIRMED (mechanics); one MEDIUM design issue (F6) | independent rebuild of nominal seeds 300000/300001 bitwise equal to `build_pseudo`+`signed_sample`; refit of `refine_stay_positive` reproduces refined_sum exactly (3534737.1434387886); classifier = driver defaults + F2 deterministic + random_state 45 (46 at seed 43); no truth labels used |
| 2 resampling repair | CONFIRMED | 1.41508 from the input npz (λ = 2 w_reco, 20,404,292 reco-passing rows, mean count 0.3464); `--data` is exactly the unit-weight real-data bootstrap; it is NOT the driver's own `--bootstrap-seed`, which never fluctuates the template |
| 3 C0 / C2 | CONFIRMED | C0 bitwise; C2 repeat and seed-43 bitwise; permutation ≤ 4.1e-11 σ |
| 4 C7 | CONFIRMED numerically | highest-W EW5 +0.602, EW11 +0.028, EW17 +0.065, EW23 +0.072, EW29 +0.730, EW35 +1.121, EW41 −1.222%; total −0.121%; median |diff| 0.358%, max 1.419% (J93); data refined/signed 1.0000029, clipped 2.79e-4; driver vs npz path (negweight) max 1.29% (J111), median 0.19% |
| 5 C3 | FAIL CONFIRMED; affected set understated; under-subtraction interpretation NOT supported | max |t| 10.9 at n=30; 61/153 over 3.6; total +0.127% (t 8.0); background fraction of the claimed cells not exceptional (Spearman of excess bias with background fraction 0.38); the refinement's reco-level local subtraction error (median 0.48%, max 4.2%, the same pattern on data, Spearman 0.93) does not track the truth-level excess (Spearman 0.07); mechanism not established |
| 6 C6 | CONFIRMED | pull SD median 1.033 (n=30, 112 replicas) |
| 7 C4/C5, truth check | CONFIRMED | eavail EW29 +74%; pooled cov68 0.028 at both; eavail total 1 + 1e-15; q3 weight marginal 6e-14; all 42 EW functionals ≤ 3.8e-7; EW_all_ones 0.9032 (a plain sum of differential values) |
| 8 diagnostic | numbers CONFIRMED, argument REFUTED (HIGH) | the diag's agreement with 1/r − 1 is forced by its own normalization (completeness from reweighted A truth, unreweighted denominator); it shows only that pushed weights stay at 1 when pseudo-data equal the prior, which a zero-iteration estimator also passes. The ordinary residuals are NOT shrinkage to the prior: at q3 the prior and truth have identical EW values yet the unfold carries a reco-level (E_avail,W) distortion into truth (EW24 reco 1.19 → unfolded 1.30, EW36 1.16 → 1.38); at eavail 12/42 cells move opposite to the truth and 13 exceed the no-movement residual |
| 9 meter, budget, tables | CONFIRMED | CPU cap 325.184 = 345.27 − 20.0859; GPU cap 115.2138 truncated below 115.21389 |

Findings: **F1 HIGH** the diagnostic cannot establish prior dependence; the estimator under-unfolds.
**F2 HIGH** C3 fails more broadly than reported. **F3 MEDIUM** under-subtraction interpretation unsupported;
the refinement has a real systematic local reco-level error up to 4%. **F4 MEDIUM** x_true and the
pseudo-data build are exonerated. **F5 MEDIUM** driver and npz paths differ by up to 1.29% on data (different
loops; refinement not bitwise equal: refined sum 3972466.85 vs 3972476.93; clipped 1279 vs 1313).
**F6 MEDIUM** the bootstrap omits finite-MC terms present in the ensemble (B-half migration; source C versus
template D variance 4V against the bootstrap's 2V, ≈ 2.4% of the data variance): correct for real data,
slightly low pseudo-experiment coverage. **F7 LOW** the s5c F2 driver-purity product
(`construction/xsec_5d_MEFHC_5iter_lgbm_F2.root`) does not exist. **F8 LOW** `make_estimators` gives all three
OmniFold estimators random_state 42, not 42/43/44 as the contract's `seed_roles` says (inert, C2). **F9 LOW**
C6 on 112 replicas and C8 on n=4 at that time. **F10 LOW** the driver's `--bootstrap-seed` does not fluctuate
the template, so a driver-made data σ would not be the contract's σ object.

**Author's dispositions (all ACCEPTED).** F1: the "prior dependence" reading is withdrawn; a signal-only
departure diagnostic was run on the same seeds (round 2 (c)). F2, F3: the C3 statement names the wider set
and no mechanism. F5, F10: recorded as limitations of transfer between the npz and driver paths. F6: recorded
as a design limitation of the Tier-S σ. F7: the driver-purity parity is made optional (`e76cb126`). F8: the
contract is immutable; the correction is recorded here and in the outcome record. F9: resolved by the full
population (round 2).

## Round 2 (full n: 60 per grid point, 200 σ replicas, 8 signal-only departure products)

(a) **C3 CONFIRMED FAIL**: max |t| 14.42 (J88 +0.907%, mean pull 2.02); 89/153 |t| > 3.6; 78 with |mean pull|
> 0.5 and |t| > 3. Highest-W column s5n vs purity D1: EW5 +0.234/−3.495, EW11 +0.110/−4.056, EW17
+0.154/−3.959, EW23 +0.150/−4.020, EW29 +0.130/−4.111, EW35 +0.110/−4.009, EW41 +0.241/+1.659 (%). Pooled
coverage 0.6028/0.8696; min per-functional 0.183/0.467; pull SD median 0.960, min 0.558, max 1.725 (sampling
SE ≈ 0.092, so the extremes are outside ±3 SE: the σ is miscalibrated for some functionals).

(b) **C4/C5 CONFIRMED**: eavail pooled cov68 0.0273 (95% 0.056), EW29 +74.07%, 136/153 functionals with zero
68% hits; q3 pooled cov68 0.0273 (95% 0.0485), EW41 +6.25%, max EW36 37.4%, 141/153 zero hits.

(c) **Signal-only diagnostic CONFIRMED with scope limits**: x_true bitwise equal to the dev product on the
same seed (8/8). Signal-only vs background-inclusive: eavail max |rel| 74.07 vs 74.45%, max difference 3.01
pp (J179), median 0.33 pp, correlation 0.9994; q3 36.31 vs 37.37%, max 1.45 pp, median 0.35 pp, correlation
0.9993. The departure failure is an estimator property; the background method adds a small but significant
shift (paired differences up to 12.7 SE eavail, 24.7 SE q3), minor next to 10–74% residuals. EW7 (E_avail
row 1, W col 1) signal-only 1.188 × nominal against truth 1.273; at q3 0.861 against 1.000. The driver loop
(`unbinned_unfolding/python/omnifold.py`) and `omnifold_nn_core.omnifold_loop` were compared line by line
and match (same step-1 data and weights, same LGBM regressor fill of reco-failing events, same step 2, same
p/(1−p) with 1e-6 clip, same defaults); the only differences are per-estimator random_state and the input
path. **The conclusion transfers to the driver by code identity; it was MEASURED on the npz loop.** Only the
E_avail departure is physically anchored; q3 a = 0.3 is a declared stress amplitude. "Under-unfolding" is not
separated from the regressor's extrapolation for the 38% reco-failing events or from step-1 underfit.

(d) **C1, C2, C6 CONFIRMED**: 385 products (plus 4 diag) carry content-checked refinement evidence; refined /
signed 0.999994–1.000020 and clipped fraction 8.4e-5–5.4e-4 over nominal products; C2 permutation 4.13e-11 σ.

(e) **Disposition: outcome sound, reasoning needs two fixes.** (1) Two separable blockers: C3 is a
background-related nominal bias (+1% vs −0.2% signal-only), plausibly fixable by a background revision, so
"no revision can help" is not true of C3 itself; what makes a revision pointless is that Tier-S assurance is
0 even with a perfect nominal (136/141 functionals with zero hits at the departures; nominal itself min 0.183,
pooled 0.603). (2) Excluding estimator changes is correct: the family fixes 5 iterations and the F2
parameters; the revision rule covers background treatment, sampling model, σ object and interval
construction and bars hyperparameter change; iterations/capacity need Joseph's decision. (3) One in-rule
option not addressed: an interval-construction revision with a model-dependence allowance calibrated on the
GiBUU anchor and validated on NuWro (`eavail-ratio-nuwro-over-genie.json`); very likely futile (allowance
≈ 10% median to 74% against σ ≈ 0.2%; fails any useful-width criterion; no longer a statistical-scope
interval) and should be disposed explicitly. Verdict: STAGE1_FAIL with no revision used is sound provided
the receipt states the two-blocker logic, disposes the model-dependence option and records that estimator
changes need Joseph's decision.

**Author's dispositions (all ACCEPTED)**; implemented in
[`OUTCOME-20260925-s5n-stage1-development-fail.md`](../../../OUTCOME-20260925-s5n-stage1-development-fail.md)
§§3–5.
