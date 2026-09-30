# Whole-node packing benchmark: bounded plan (2026-09-30; PREPARED, NOT AUTHORIZED, NOT RUN)

**CITABLE FOR:** the question the benchmark answers; its design, workload selection rule, controls, measurements,
pre-declared decision rules, cost, prerequisites, and the separate grant it needs; the read-only priors available
on 2026-09-30. **NOT CITABLE FOR:** any authorization, any measured speed-up or scheduling advantage, or any change
to s5p production. **Execution comes only after s5p production is terminal, and only under a separate owner
grant.** Owner instruction, 2026-09-30: *"prepare the bounded benchmark plan now, execute after terminal under a
separate grant, and gather several queue-wait observations before claiming a scheduling advantage"*.

Input: the read-only assessment by the peer session Codex,
`state/s5p/transition-r2/packing-assessment-codex-20260930/packing-assessment.txt` (sha256 `0812cba2…`).

## 1. Question

Would packing eight 32-thread GBDT pseudo-experiment tasks into one regular-partition CPU node give:
- (a) the same numerical products,
- (b) the same or better cost per experiment, and
- (c) a shorter time until eight task slots are running,

compared with the current eight 1/8-node tasks on the shared partition? The answer informs **future** campaigns
only. s5p's production is frozen and will be terminal before this runs.

## 2. Read-only priors (2026-09-30; context, not evidence of an advantage)

- **No own history.** This account ran no regular-partition jobs since 2026-08-01, so no observed wait exists.
- **One queue snapshot (23:2xZ):**
  - regular_milan_ss11: 2,952 nodes allocated and none idle; 14,925 pending jobs.
  - shared_milan_ss11: 363 pending jobs.

  This is one snapshot of queue depth. It is **not** a wait measurement, but it is a caution: a larger partition
  is not evidence of a faster start.
- **Fit (from the assessment):** eight tasks request 256 CPUs and 448 GiB, against about 476 GiB per node. The
  peak recorded MaxRSS is 42.36 GiB and the median 32.57 GiB, but aggregate concurrent memory is unmeasured.
- **Cost (from the assessment):** an idealized 16-slot schedule of the recorded durations costs 1.35% more than
  shared billing. That is illustrative, not a forecast.

## 3. Design

### 3.1 Queue-wait probes: the scheduling question, measured, not assumed

- **One pair** is submitted in the same minute:
  - **R:** one regular job (`--qos regular -C cpu -N 1`, time limit 2:00:00), running `sleep 60; hostname; date`.
  - **S:** one shared array of 8 tasks (32 CPUs and 56G each, time limit 2:00:00, no throttle), each running the
    same command.

  Both request the same time limit, because backfill depends on it.
- **Schedule:** at least **8 pairs** over at least **2 calendar days**, spread across the day (at least 2 per 6-hour
  UTC block where the calendar allows) and at least 3 h apart. Positions are fixed before the first submission.
- **Per pair, from `sacct` (Submit / Eligible / Start):**
  - `W_R` = start(R) − submit(R);
  - `W_S8` = max start(S tasks) − submit(S), the time until all eight slots run;
  - `W_S1` = median start(S tasks) − submit(S).

  Also record the pending counts of both partitions at submission.
- **Cost:** about 1–2 min × 1 node per side, roughly 0.05 node-h per pair.

### 3.2 Compute benchmark: numerics, contention, memory

- **Workload.** One regular node for at most 2 h, running **8 workers** concurrently. Each worker is one
  already-completed s5p production task row: its original argv, 32 threads, original seeds, estimator and
  settings, with `--out` redirected to an isolated benchmark namespace. **No write under `runs/prod/`.**
- **Row selection, independent of outcomes.** From the batch-0 / P1 rows whose tasks COMPLETED, choose with
  `numpy.random.default_rng(20261001)`:
  - one row per calibration null (5);
  - one more calibration row from the combined remainder;
  - two power rows from P1.

  The chosen row ids are committed before submission. Selection uses only task state and the RNG, never
  statistics.
- **Isolation.** Disjoint CPU sets: 32 logical CPUs per worker as 16 whole cores (both hyperthreads). Each worker's
  memory limit is 56G, and each keeps the original **2-h per-worker cutoff** (`timeout 7200`). There is no retry.
- **Guards.** Workers run through the same pinned clean checkout and `mnv_guarded_run` path as `s5c_array.sh`. A
  worker's row is passed explicitly, never taken from `SLURM_PROCID`.
- **Control, for the reproducibility baseline.** Two of the 8 rows are rerun as ordinary 1/8-node shared tasks, at
  most 2 h each, with the same isolated outputs. Without it, a packed-vs-production difference could not be
  attributed to packing.
- **Measurements:**
  - allocation elapsed time;
  - per worker: elapsed, CPU time, per-experiment `seconds_unfold`, exit code;
  - node memory high-water, sampled every 30 s, plus per-worker peak RSS;
  - CPU binding as printed by each worker;
  - node id and queue wait.

### 3.3 Numerical comparison

- **What is compared:** each benchmark and control product's `xsec_flat` and `xtrue_flat`, against the production
  product of the same seed.
- **Tiers:** exact equality first. Otherwise report the maximum absolute and relative difference per array.
  Timestamps or other metadata are not numerics.
- **Interpretation:**
  - the control exact and packed not exact: a **packing-induced difference**, a finding, stop;
  - neither exact: the nondeterminism baseline is non-zero; compare the magnitudes and record them;
  - nothing is tuned.

## 4. Pre-declared decision rules (fixed before any observation)

- **Scheduling advantage** is claimed **only if** both hold over **at least 8 pairs**:
  - `W_R < W_S8` in **at least 7 of 8** pairs (one-sided sign test, p ≈ 0.035), with the same proportion if more
    pairs are run;
  - the median of `W_S8 − W_R` is at least 0.5 h, about half a task duration.

  With fewer than 8 pairs no scheduling claim is made in either direction. A reverse advantage is reported the same
  way. Probe waits are a proxy that depends on the requested time limit, fair-share and time of day; that
  limitation is stated with every result.
- **Compute:** packed experiments per billed node-h must be at least 0.95 × the shared production value (2,353
  experiments per 56.29 node-h, i.e. 41.8). The node memory high-water must stay at or below 90% of the node.
  There must be no OOM, guard failure, CPU-set overlap, output collision or seed mismatch.
- **Numerics:** as in §3.3. Any packing-induced difference blocks the recommendation.
- **Outcome:** recommend a reviewed packed dispatcher **for a future campaign** only if the compute, numerics and
  scheduling rules all pass. Otherwise report "no demonstrated advantage", with the measurements. The benchmark
  never changes s5p results, products or records.

## 5. Cost, concurrency, calendar

| part | estimate | cap |
|---|---:|---:|
| probes, 8 pairs (+2 spare) | about 0.5 | 1.0 |
| compute benchmark, 1 node | ≤ 2.0 | 2.0 |
| shared control, 2 × 1/8 node | ≤ 0.5 | 0.5 |
| **total** | **about 3** | **4.0 billed CPU node-h** |

- **Concurrency:** at most 2 nodes. One probe pair is 1 + 1 node, and the benchmark runs alone.
- **Calendar:** at least 2 days, for the probes.
- **Storage:** about 50 products × 185 kB.

## 6. Prerequisites and the grant

1. **Timing.** s5p production is terminal, by the handoff's four conditions. **The benchmark's budget revision and
   rebind come only after the recompute lane's final verification**, because a rebind makes the meter refuse the
   deploy that lane uses, as recorded for transition r2.
2. **An owner grant, separate from s5p's authorization,** stating:
   - the amount (at most 4.0 billed CPU node-h);
   - where it is accounted. The **proposed route** is a new stage, `packing_benchmark`, in an s5p budget revision
     after terminal, funded from s5p's reconciled unspent production. It is **not** funded from verification/repair
     and is within the cumulative 345.27. The alternative is a new meter campaign key, which needs a reviewed meter
     code change;
   - concurrency (at most 2 nodes) and QOS (`regular` and `shared` only);
   - that the benchmark changes nothing in s5p.
3. **Meter admission without unpriced flags.** Before any submission, pass each probe and benchmark request
   through the meter's `validate_request` as a dry validation. The regular request must be modelled as a whole node
   without `--exclusive` or `--ntasks-per-node`, which the meter refuses. If it cannot be, a reviewed meter extension
   comes first. **No bypass.**
4. **Review of the benchmark wrapper.** The 8-worker launcher and the product comparison get **one bounded
   read-only review** (a fresh session) before use, like the s5p recompute lane's review.
5. **Records:** a receipt per submission (what it measures and what it cannot authorize); the raw `sacct` rows; the
   comparison output; and one results record with the decision per §4.

## 7. Not in scope

- No change to s5p's production, queues, runners, budget or records beyond the post-terminal stage above.
- No packed production for s5p.
- No claim of speed-up from the idealized schedule.
- No scheduling claim from fewer than 8 pairs.
