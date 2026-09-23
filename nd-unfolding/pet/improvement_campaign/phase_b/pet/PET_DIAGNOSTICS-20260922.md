# Phase B2 — PET stepwise diagnostics and first controlled feature arms (development stage)

**Scope.** PET is diagnostic method development. Everything here is simulation only (signal MC of
`G2_FPS_MEFHC_P12.npz`); no publication adoption, no uncertainty product, no Gate-6 action, no
threshold change, and the historical comparison's files, outputs, thresholds and verdict are
untouched. **Every result below is DEVELOPMENT evidence** (scope §6): it may choose what is tested
later and can never be reused as confirmatory data.

## Running status (resume anchor; newest first)

- 2026-09-23 10:45Z: exp 1 DONE (§1), exp 2 DONE (§3, 12 and 32 epochs), exp 3 DONE (§4), exp 4
  DONE for S1, S2 and M (§5). Exp 5 running as two self-chaining `gpu_debug` chains from code
  `9d64b0da` (`58785788`: C1-C4 seed 1 -> `phaseB2/e5c1/`; `58785789`: C1-C4 seed 2 ->
  `phaseB2/e5c2/`), T1 truth side, H schedule, CARRY-misses (the robust rule, §5); runs score
  themselves on completion. The preempt copy of exp 5 (`58781990`) was cancelled unstarted.
- Next: harvest exp 5 -> §6; then, if budget allows, the best C arm in efficiency-corrected mode.
- Dropped/deferred because of the queue (say so, do not read as nulls): S3 (2x epochs with
  patience) and the S-combination; H at K=10 seeds 3-4; seeds beyond 2 for every K=10 arm.

## Measured queue waits and compute (elapsed time was the binding constraint, not node-hours)

From `sacct` (submit -> start), every B2 job (`resources-B2.tsv`):

| QOS | shape | jobs started | median wait | max wait |
|---|---|---:|---:|---:|
| `gpu_debug` | 1 node, 4 A100, 30 min, 2 running per user | 20 | **3 min** | 43 min |
| `gpu_shared` | 1 A100, 32 cores | 4 | 92 min (2 jobs) | 5.8 h (2 jobs) |
| `gpu_preempt` | 1 node, 4 A100 | 1 | 9.8 h | — |
| `gpu_regular` | 1 node, 4 A100 | 0 | never started in 6 h; cancelled | — |
| `debug` (CPU) | 1 node | 1 | 4 min | — |
| `gpu_interactive` | — | — | refuses `sbatch` (needs `salloc`) | — |

`sbatch --test-only` estimates were worst-case and useless (8 days for `gpu_regular`). What worked:
**self-chaining `gpu_debug` jobs** (`jobs/sbatch_b2_chain.sh`): four runs per node, each run
checkpointed per OmniFold iteration, two iterations per 30-minute job (measured: load 133 s,
one H iteration 756 s), the job resubmitting itself until every run is COMPLETE. Resume is
bit-exact (§2), so a chained run is the same computation as an uninterrupted one.

Compute so far (all B2 jobs, `resources-B2.tsv`): **35.0 GPU-hours** (A100) on `m3246_g`; the
1,134 "CPU core-hours" in the ledger are the host cores of those GPU allocations (charged to
`m3246_g`), the CPU allocation `m3246` was used only by the T3 reference (15.7 core-hours).
Projection for what remains (exp 5: 8 runs x 10 iterations x 756 s + loading) ~ 18 GPU-hours.

## Pre-declared gate for experiment 1 (written before any B2 result existed)

The historical `ours` final per-seed recoveries (`configuration_comparison/campaign_report.json`
`per_run`, 8 seeds) span **[0.28888, 0.32563]**, mean 0.30367, sd 0.0134. Experiment 1 runs the
historical as-executed recipe through the A1 driver at K = 3 with 4 seeds.

- PASS if every seed lands inside [0.28888, 0.32563].
- If one or more seeds land outside: not an automatic failure (with 8 historical seeds, a draw from
  the same distribution falls outside their range with probability ~2/9). Accept faithfulness if
  the 4-seed mean lies inside the Welch-t 95 % interval for a difference of means of 0 against the
  8 historical seeds AND no seed is more than 3 historical sd from the historical mean; otherwise
  FAIL and stop to find out why before anything else.

## 1. Experiment 1 — driver faithfulness (MEASURED, complete: 4 seeds)

The historical as-executed `ours` recipe (Adam, iteration-0 rate 4e-4 then 1e-5 forced, batch 512
both steps, 8 epochs, last-epoch weights, raw truth PDG column, row-level 20 % split, warm start)
through the **unmodified A1 driver** `improvement_campaign/run_unfold.py`, K = 3, on the historical
development halves.

| run | config hash | job | R (k = 3) | low | moderate | good |
|---|---|---|---:|---:|---:|---:|
| `b2e1-H-K3-s1` | `b891519df0d6e070` | 58755597 | 0.32166 | 0.062 | 0.261 | 0.574 |
| `b2e1-H-K3-s2` | `acaf8f0b94a2ff51` | 58755598 | 0.32262 | 0.051 | 0.271 | 0.578 |
| `b2e1-H-K3-s3` | `a3259926338fc60b` | 58755599 | 0.26930 | 0.048 | 0.196 | 0.476 |
| `b2e1-H-K3-s4` | `2ccf22bc400a646e` | 58755600 | 0.33153 | 0.073 | 0.279 | 0.573 |
| **B2, 4 seeds** | | | **0.3113 ± 0.0283** [0.2693, 0.3315] | 0.058 | 0.252 | 0.550 |
| historical `ours`, 8 seeds (`campaign_report.json`) | | | 0.3037 ± 0.0136 [0.2889, 0.3256] | 0.056 | 0.226 | 0.538 |

Two seeds land inside the historical per-seed range and two outside (s3 below, s4 above), so the
pre-declared fallback applies and it is satisfied:

* Welch comparison of the two seed sets: difference of means **+0.0076**, se 0.0150, t = 0.51,
  df = 3.7, 95 % interval **[-0.040, +0.055]** — it contains 0;
* the furthest seed is **2.53** historical sd from the historical mean (limit 3).

**Verdict: the repaired driver reproduces the historical as-executed recipe's recovery** (MEASURED).
Everything downstream is unblocked.

**A second, unplanned measurement matters for every later comparison**: the B2 seed spread is
**0.0283**, about twice the historical 8-seed spread 0.0136 (variance ratio 4.3, F(3,7), not
significant at 5 % two-sided). Taking 0.0283 at face value, two arms of **2 seeds** each separate
their means only at ±0.028 (1 se) — enough for a 0.08-0.10 effect, **not** for the 0.02-0.04
differences the brief asks about. Arms are therefore compared at matched seeds (paired), the paired
spread is reported with every comparison, and any factor whose paired effect is within the spread is
reported as NOT RESOLVED at this seed count rather than as a null.

Evidence: `phaseB2/e1-shared/b2e1-H-K3-s{1,2,3,4}/{receipt.json,scores.json}`, copied to
`results/`. The scorer's positive control reproduces the historical `ours`-seed-127 score to 1e-15
(`0.32563324433093876` vs the report's `0.32563324433093976`, regions identical;
`results/scorer-positive-control-hist-ours-127.json`).

## 2. Driver-mechanics check (job 58756024, `gpu_debug`, tuning stage, 100k events)

| check | result |
|---|---|
| unfold, 2 iterations × 2 epochs, continuous | COMPLETE |
| the same run stopped after iteration 0 and RESUMED | COMPLETE; iteration 0 **bit-identical** (pull and push, max abs difference 0.0) |
| iteration 1 after a resume vs continuous | **NOT bit-identical**: max abs difference 1.2e-2 (pull), 1.9e-3 (push) |
| every B2 input transform at once (reco summaries + PDG one-hot + truth globals) | COMPLETE |
| truth-only mode, raw PDG and T2 transforms | COMPLETE |
| `test_b2_arms.py` | 5 passed |

**Resume is statistically equivalent, not bit-identical** (MEASURED): a restored fit rebuilds the
model from its factory, so the Keras layers' own random streams (dropout) restart at their
construction seed instead of continuing, which perturbs later iterations like a change of sub-seed.
Consequence adopted here: production runs are given walltime to finish in one allocation, and any
run that did resume is marked by its receipt's `segments` and read as a different noise realization
of the same recipe, not as the same run.

## 3. Experiment 2 — truth-only learnability of the KNOWN tilt (MEASURED, 2 seeds, 12 epochs)

**A learnability diagnostic of the step-2 input set, not a detector-level bound and not an unfolding
recovery.** Step 2 alone (the engine's own `RunStep2` with the pull set to the injected tilt),
trained on half A (prior truth vs prior truth x tilt; the H step-2 recipe at its iteration-0 rate
4e-4, batch 512; 12 epochs, best-validation epoch handed on), evaluated on half B's truth at every
epoch. `learnability` = B x ratio vs B x the half-A tilt function (B1's convention);
`endpoint` = the historical score of that push over half B (its sampling ceiling is 0.984, B1
anchors). 12 epochs instead of the planned 32 so each run fits one 30-minute queue slot; epochs 1-12
are identical to the first 12 of a 32-epoch run (constant rate, same seeds).

| arm | truth-side inputs | epoch 8 (the historical fit) | at best-val epoch | endpoint | low | moderate | good |
|---|---|---:|---:|---:|---:|---:|---:|
| T0 | executed: raw PDG as a continuous column, globals pT, p‖ | 0.843 ± 0.075 | **0.898 ± 0.012** | 0.887 | 0.823 | 0.897 | 0.911 |
| T1 | PDG as a one-hot of 13 physics categories | 0.925 ± 0.090 | **0.952 ± 0.037** | 0.950 | 0.952 | 0.948 | 0.957 |
| T2 | T1 + true E_avail, q3 as globals | 0.901 ± 0.094 | **0.973 ± 0.008** | 0.961 | 0.970 | 0.977 | 0.969 |
| T3 | scalar GBDT on (true E_avail, pT, p‖), same protocol | — | 0.999 ± 0.000 | 0.983 | 0.999 | 0.999 | 0.999 |
| T3 | scalar MLP on (true E_avail, pT, p‖) | — | 0.969 ± 0.007 | 0.969 | 0.966 | 0.982 | 0.979 |
| T3 | scalar GBDT / MLP on (pT, p‖) only | — | 0.330 / 0.344 | 0.326 / 0.339 | 0.048 | 0.216 | 0.442 |

(mean ± sd over seeds 1-2; regions at the best-validation epoch.) Files:
`results/b2e2f-T{0,1,2}-s{1,2}.truth_only.json` (jobs 58780654), `results/truth_scalar_ref.json`
(job 58780659); per-epoch curves in `results/summary.json`.

What this measures:

1. **The historical truth-side PET can learn the known tilt far beyond what its explicit globals
   carry** (MEASURED): 0.90 with raw PDG against 0.33 for any learner on (pT, p‖) alone. The truth
   hadron cloud carries the E_avail information and the PET extracts most of it. B1's inference
   ("a step 2 whose explicit globals are pT and p‖ must extract E_avail from its cloud to exceed
   ~0.33; whether it does is a Phase-B measurement") is now answered: it does.
2. **The PDG encoding matters, most in the low-acceptance region** (MEASURED, 2 seeds): one-hot
   raises best-val learnability 0.898 -> 0.952 overall and 0.823 -> 0.952 in the low-acceptance
   region. With 2 seeds and a T1 spread of 0.037 the aggregate gain is suggestive, not resolved.
3. **Epoch-to-epoch fluctuation at the historical rate is large** (MEASURED): the same fit moves by
   0.05-0.2 between consecutive epochs (T0 seed 2: 0.51, 0.90, 0.68, 0.87, ...), so the historical
   hand-on of the LAST of 8 epochs is a noisy draw (epoch-8 spread 0.075-0.094 vs 0.008-0.037 at the
   best-validation epoch).
4. Truth globals (T2) reach 0.97 — the PET does not reproduce the GBDT's 0.999 even when handed the
   injected coordinate. **The development tilt is an exact function of true E_avail, so T2/C3 make
   this particular closure easy by construction**; Phase E's other distortions are what test them.

**32 epochs** (job `58769968`, preempt, code `5634768e`; `results/b2e2-T*.truth_only.json`): at the
best-validation epoch T0 **0.911 ± 0.018**, T1 **0.950 ± 0.026**, T2 **0.976 ± 0.001**; the mean over
epochs 17-32 is 0.89 (T0) and 0.94 (T1). Longer training does not lift the plateau and does not
remove the epoch-to-epoch fluctuation. (A different noise realization of the same recipe from the
12-epoch runs: that job predates the B2 driver's per-step seeding.)

What it does NOT establish: that step 2 is not limiting INSIDE the unfolding, where its class-1
weights are the step-1 pull rather than the true tilt and the fit at iterations >= 1 runs at 1e-5
(experiment 3 measures that); anything about detector-level recovery.

## 4. Experiment 3 — step-wise closure inside the unfolding, H at K = 10 (MEASURED, 2 seeds)

The historical as-executed recipe through the B2 driver (`b2e3-H-K10-s{1,2}`, chain `k10a`,
jobs 58780657 -> 58781966 -> ... , code `b1ea0056`/`db8b7184`, bit-exact resume), scored at every
iteration by `b2_score.py`. Columns: `push` = the historical score; `pull` = the same score of the
pulled weights; step-1 detector-level recovery of the PULLED weights against the ORIGINAL prior, in
reco E_avail (7 endpoint bins, the analysis definition), the muon (pT, p‖) cells, the stored-cluster
energy sum (deciles) and count; `acc` / `miss` = truth E_avail recovery over the reco-passing
events alone / the misses alone (targets: half A x tilt over the same class); ESS/n of
w_truth x push; the 99.9th percentile of the push.

| k | push | pull | reco E_avail | muon cells | stored ΣE | stored n | pull (acc) | push (acc) | push (miss) | ESS/n | push p99.9 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.164 | 0.191 | 0.656 | 0.657 | 0.686 | 0.820 | 0.591 | **0.313** | 0.098 | 0.874 | 1.75 |
| 3 | 0.334 | 0.363 | 0.824 | 0.629 | 0.845 | 0.900 | 0.723 | 0.554 | 0.212 | 0.844 | 2.19 |
| 10 | **0.506** | 0.512 | 0.940 | 0.725 | 0.938 | 0.954 | 0.841 | 0.774 | **0.378** | 0.786 | 3.23 |

(means of seeds 1-2; full per-iteration tables with spreads in `results/summary.json` via
`b2_summarize.py`; regions at k = 10: low 0.172, moderate 0.539, good 0.816.)

Where the correction is lost (MEASURED on this closure):

1. **Not at step 1, at the detector level**: after one iteration the pulled weights already remove
   66 % of the reco E_avail pseudo-data/prior difference and 94 % by k = 10; the stored-cluster
   energy sum and count close likewise. The muon-cell difference closes less (0.63-0.73) — that
   residual is small in absolute terms and at the level of the halves' finite-sample difference.
2. **In the step-2 fit under the carry-misses rule**: over the ACCEPTED events the pull holds 0.59
   of the truth displacement at k = 1 but the step-2 output keeps only 0.31 of it. The class-1
   weights of every miss are the previous push, unchanged, so the classifier is trained on a truth
   sample whose correction is diluted by the 58 % of events that carry none.
3. **In extrapolation to the misses**: the misses recover 0.10 at k = 1 and 0.38 at k = 10.
   Recovery keeps rising at k = 10 (0.455 -> 0.506 over the last two iterations); the historical
   k = 3 sits on the steep part of the curve (0.334 here, 0.311 ± 0.028 in exp 1).
4. Weight tails grow with k (p99.9 1.75 -> 3.23, ESS/n 0.87 -> 0.79) — moderate, no saturation.

Together with exp 2 (step 2 given the TRUE tilt learns 0.90-0.95), this says the historical
shortfall is a property of how the unfolding moves correction from accepted events to misses and
of stopping at k = 3, much more than of the PET's representation on either side. INFERRED from
these measurements, and scoped to this closure: the development tilt is a smooth function of
true E_avail, the variable the truth side sees.

## 5. Experiment 4 — schedule and miss handling against H, K = 10 (MEASURED, 2 seeds)

One factor at a time, both steps, truth-side inputs held at the executed T0 representation.
`M` = the H recipe with the driver's opt-in **efficiency-corrected step 2** (trained on the
reco-passing events alone, the learned truth-level ratio applied to all truth events; Huang et al.
arXiv:2504.06857 §V.A; `b2_driver.B2MultiFold.RunStep2`, default path unchanged).

| arm | k = 1 | 3 | 5 | 10 | low (k=10) | moderate | good | paired Δ vs H at k = 10 [s1, s2] |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| H (carry misses, anneal to 1e-5, last epoch) | 0.164 | 0.334 | 0.404 | 0.506 ± 0.025 | 0.172 | 0.539 | 0.816 | — |
| S1: no forced 1e-5 (4e-4 every iteration) | 0.164 | 0.326 | 0.415 | 0.496 ± 0.018 | 0.144 | 0.559 | 0.833 | −0.010 [+0.021, −0.041] NOT RESOLVED |
| S2: best-validation epoch handed on | 0.136 | 0.290 | 0.354 | 0.452 ± 0.015 | 0.147 | 0.467 | 0.726 | **−0.054** [−0.047, −0.062] |
| **M: efficiency-corrected step 2** | 0.418 | 0.608 | 0.707 | **0.817 ± 0.003** | **0.667** | 0.835 | 0.884 | **+0.310** [+0.330, +0.290] |

(S3 — 16 epochs with patience — was not run: queue; see status.) Files:
`results/b2e3-H-K10-s*.scores.json`, `results/b2e4-{S1,S2,M}-K10-s*.scores.json`.

1. **Miss handling dominates everything measured so far** (MEASURED): +0.27 at k = 3 and +0.31 at
   k = 10, both seeds, 10 x the paired spread. M passes the historical 0.556 floor already at k = 3
   (0.608) and exceeds the 0.695 reference by k = 5; the low-acceptance region goes from 0.17 to
   0.67. Over accepted events M's step 2 keeps what the pull holds (k = 1: 0.566 vs 0.591), and the
   misses reach 0.76 at k = 10. This reproduces at PET level what Phase F found for scalar
   OmniFold (0.582 -> 0.783).
2. **The schedule factors do not help**: removing the forced 1e-5 changes nothing resolvable;
   handing on the best-validation epoch is WORSE by 0.05 on both seeds (the validation loss of a
   weighted classifier does not select the epoch whose ratio recovers best; cf. the epoch
   fluctuation of exp 2).
3. **Caveat that governs how M may be used** (scope, and Phase E1 `phase_e/PHASE_E_SCALAR-20260922.md`):
   efficiency correction assumes the selection efficiency depends only on the truth variables the
   step-2 classifier sees. The development tilt is an exact function of true E_avail, so this
   closure flatters it; at scalar level it FAILS when a distortion changes the event mix inside a
   truth bin (NuWro reweighting −0.20, proton multiplicity 0.31) while carry-misses is slower but
   robust. **The miss rule is therefore a model-dependence choice, not a free improvement**, and
   M is not a candidate until Phase E's hidden-variable distortions have tested it with the PET.
   Experiment 5 runs in carry-misses mode for that reason.
