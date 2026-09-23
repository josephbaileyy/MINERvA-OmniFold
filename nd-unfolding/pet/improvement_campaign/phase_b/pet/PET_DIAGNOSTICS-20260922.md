# Phase B2 — PET stepwise diagnostics and first controlled feature arms (development stage)

**Scope.** PET is diagnostic method development. Everything here is simulation only (signal MC of
`G2_FPS_MEFHC_P12.npz`); no publication adoption, no uncertainty product, no Gate-6 action, no
threshold change, and the historical comparison's files, outputs, thresholds and verdict are
untouched. **Every result below is DEVELOPMENT evidence** (scope §6): it may choose what is tested
later and can never be reused as confirmatory data.

## Running status (resume anchor; newest first)

- 2026-09-23 05:30Z (code `db8b7184`): exp 1 DONE (§1), exp 2 DONE at 12 epochs (§3) -> truth side
  for exp 5 = **T1 (PDG one-hot)**. Running as self-chaining `gpu_debug` jobs (2 iterations per
  30-min job; resume is bit-exact): chain `k10a` (`58781966`: H K=10 s1-s2 = exp 3 + exp-4
  reference, S1 s1-s2) and chain `k10b` (`58781967`: M = efficiency-corrected step 2 s1-s2, S2
  s1-s2). Each run has iteration 0 done (k10a) and is scored in-job when it completes. Still queued
  as a lottery ticket: `58769968` (exp 2 at 32 epochs, preempt, code `5634768e`).
- Next: when k10a/k10b complete -> exp 3 tables (step-wise closure), exp 4 (S1, S2, M vs H);
  then S3 + H s3-s4 chain; then exp 5 (C1-C4, T1 truth side, the best schedule and miss rule).
- Dropped/deferred so far because of the queue: exp 2 at 32 epochs (12 run instead; the 32-epoch
  job stays queued), T-arm seeds beyond 2.

## Measured queue waits (elapsed time is this task's binding constraint, not node-hours)

| QOS | shape | submitted | started | wait |
|---|---|---|---|---|
| `gpu_shared` | 1 GPU, 32 cores | 17:31Z | 19:03Z | **92 min** (2 of 4 jobs) |
| `gpu_shared` | 1 GPU, 32 cores | 17:31Z | still pending at 22:30Z | **> 5 h** (the other 2) |
| `gpu_debug` | 1 node, 4 GPUs, 30 min | 17:40Z | 18:06Z | **25 min** |
| `gpu_preempt`, `gpu_regular` | 1 node, 4 GPUs | 22:16Z | — | pending |

`sbatch --test-only` start estimates are worst-case and were useless here (they said 8 days for
`gpu_regular` while `gpu_shared` jobs started in 92 min). Full-node packs of 4 runs cost the same
per run as 4 single-GPU shared jobs and pay ONE queue wait, so every K = 10 batch is packed 4-up.

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

What it does NOT establish: that step 2 is not limiting INSIDE the unfolding, where its class-1
weights are the step-1 pull rather than the true tilt and the fit at iterations >= 1 runs at 1e-5
(experiment 3 measures that); anything about detector-level recovery.
