# Phase B2 — PET stepwise diagnostics and first controlled feature arms (development stage)

**Scope.** PET is diagnostic method development. Everything here is simulation only (signal MC of
`G2_FPS_MEFHC_P12.npz`); no publication adoption, no uncertainty product, no Gate-6 action, no
threshold change, and the historical comparison's files, outputs, thresholds and verdict are
untouched. **Every result below is DEVELOPMENT evidence** (scope §6): it may choose what is tested
later and can never be reused as confirmatory data.

## Running status (resume anchor; newest first)

- 2026-09-23 04:20Z: **experiment 1 is COMPLETE and PASSES** its pre-declared gate on 4 seeds
  (§1). The queue stalled every long job for 6 h, so the K = 10 work moved to self-chaining
  `gpu_debug` jobs (§ queue): `58780654` (truth-only, 12-epoch configs) and `58780657` (H K=10
  s1-s2 + S1 K=10 s1-s2), plus `58780659` (T3 scalar reference, CPU debug, started in < 1 min).
  `58769968` (exp 2 at 32 epochs, preempt) is still queued as a lottery ticket; `58769969/70/71`
  were cancelled in favour of the chains.
- Resume is now **bit-exact**: the divergence the mechanics check found was the graph-level seed
  left over from the previous fit (the `tf.data` shuffle is built before `RunModel` seeds the fit),
  not model state; the B2 driver now seeds each step from its own (step seed, step, iteration)
  before the step runs (`b2_driver.B2MultiFold.seed_step`).
- Submitted after the gate (all from checkout `5634768e`, task dir
  `/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB2/`):
  `58769968` (preempt, exp 2: T0/T1/T2 × 2 seeds, truth-only), `58769969` (regular, exp 3 H K=10
  s1-s2 + exp 4 S1 s1-s2), `58769970` (preempt, exp 4 S2 s1-s2 + M s1-s2),
  `58769971` (regular, exp 4 S3 s1-s2 + H K=10 s3-s4), `58769978` (CPU shared, T3 scalar
  reference). Jobs score themselves (`b2_score.py`) when they finish.
- Next: harvest exp 2/3/4; then experiment 5 (feature arms C1-C4 with the best step-2 variant,
  the best schedule and the better miss rule held fixed).

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
