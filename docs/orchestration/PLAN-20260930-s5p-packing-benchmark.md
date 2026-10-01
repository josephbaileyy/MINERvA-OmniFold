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
- (b) cost per experiment within the pre-declared tolerance, and
- (c) shorter start delays and completion time for the same eight-task workload,

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
  - `W_S_last` = max start(S tasks) − submit(S), the time until every shared task has started;
  - `W_S_median` = median start(S tasks) − submit(S).

  A shared probe can finish before another starts. `W_S_last` does **not** measure eight simultaneously running
  slots, and does not credit useful work that earlier tasks could have performed. These probes measure start
  delays only. The matched compute workload below measures completion time including the earlier starts.

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
- **Matched controls.** All **8** selected rows are also rerun as ordinary 1/8-node shared tasks, at most 2 h each,
  with separate isolated outputs and otherwise identical arguments. Submit the packed job and the eight-task
  shared array in the same minute, with no array throttle below 8. The pair uses at most 2 nodes concurrently.
  Every packed row has its own shared control; two controls cannot establish reproducibility for the other six.
- **Completion time.** For each execution path, record submit-to-last-product time for the identical eight rows,
  the completed experiment count, failures and timeouts. If any required product is missing, report an incomplete
  workload rather than a shorter successful completion time. Keep queue wait, computation time and idle tails
  separate. A single matched workload pair supports a descriptive comparison, not a general scheduling claim.
- **Measurements:**
  - allocation elapsed time;
  - per worker: elapsed, CPU time, per-experiment `seconds_unfold`, exit code;
  - node memory high-water, sampled every 30 s, plus per-worker peak RSS;
  - CPU binding as printed by each worker;
  - node id and queue wait.

### 3.3 Numerical comparison

- **What is compared:** for every selected row and seed, compare `xsec_flat` and `xtrue_flat` pairwise between the
  packed rerun, its matched shared rerun and the original production product. Require the expected seed set and
  complete products on both rerun paths before comparing; missing products are not numerical passes.
- **Tiers:** exact equality first. Otherwise report the maximum absolute and relative difference per array.
  Timestamps or other metadata are not numerics.
- **Interpretation:**
  - both reruns agree exactly with production: numerical equivalence is demonstrated for that tested seed;
  - packed differs from its matched control, including when the control agrees with production: an
    **execution-associated discrepancy**, a finding that blocks the recommendation. One rerun per path cannot
    determine whether packing or rerun variability caused it;
  - both reruns agree with each other but differ from production: historical reproducibility is unresolved;
    record the differences and block the recommendation;
  - neither reproduces production and the reruns differ: report all three comparisons; do not subtract a
    baseline inferred from other rows or declare equivalence from similar difference magnitudes;
  - nothing is tuned. Any unresolved difference blocks the recommendation. Exact matches establish equivalence
    only for the selected workload, not every future input or machine.

## 4. Pre-declared decision rules (fixed before any observation)

- **A probe start-delay advantage** is claimed **only if** both hold over **at least 8 pairs**:
  - `W_R < W_S_last` in **at least 7 of 8** pairs (one-sided sign test, p ≈ 0.035), with the same proportion if more
    pairs are run;
  - the median of `W_S_last − W_R` is at least 0.5 h, about half a task duration.

  With fewer than 8 pairs no scheduling claim is made in either direction. A reverse advantage is reported the same
  way. Probe waits are a proxy that depends on the requested time limit, fair-share and time of day; that
  limitation is stated with every result. This rule does not establish simultaneous shared-slot availability or
  overall throughput. Report the matched compute workload's completion-time comparison separately; if it is
  incomplete or does not finish sooner under packing, no end-to-end advantage is demonstrated. Even a faster
  single matched workload pair is not a general estimate of campaign speed-up.
- **Compute:** packed experiments per billed node-h must be at least 0.95 × the shared production value (2,353
  experiments per 56.29 node-h, i.e. 41.8). This is an **efficiency floor**, equivalent to cost per experiment
  **at most `1 / 0.95 = 1.052632` times baseline** (about 5.3% higher cost permitted). It is not a claim of equal
  or lower cost. Report cost per experiment for the matched shared controls as well, including idle allocation
  time in packed billing. The node memory high-water must stay at or below 90% of the node.
  There must be no OOM, guard failure, CPU-set overlap, output collision or seed mismatch.
- **Numerics:** as in §3.3. Every tested seed must reproduce exactly on both rerun paths; any missing comparison
  or unresolved discrepancy blocks the recommendation, without assigning a cause that the controls do not establish.
- **Outcome:** recommend a reviewed packed dispatcher **for a future campaign** only if the compute, numerics and
  probe start-delay rules all pass and the complete matched workload finishes sooner under packing. Otherwise
  report "no demonstrated advantage", with the measurements. The benchmark
  never changes s5p results, products or records.

## 5. Cost, concurrency, calendar

| part | estimate | limit |
|---|---:|---:|
| probes, 8 pairs (+2 spare) | about 0.5 | 1.0 actual-spend stop threshold |
| compute benchmark, 1 node | ≤ 2.0 | 2.0 |
| shared controls, 8 × 1/8 node | about 1, ≤ 2.0 | 2.0 |
| **total** | **about 3.5, depending on runtime** | **5.0 billed CPU node-h** |

- **Reservation accounting:** use one proposed `packing_benchmark` stage of **5.0** node-h. A two-hour probe
  reserves 2.0 node-h on each side, **4.0 per pair**, even though
  `sleep 60` spends much less. The former 4.0 stage cap could admit the first pair but would refuse a later pair
  after any positive prior spend (for example, 0.05 + 2.0 + 2.0 = 4.05). Probes run before compute; at most one
  pair is open, and it must fully reconcile before the next. At most 1.0 of prior probe spend plus a 4.0 pair
  reservation fits the proposed 5.0 stage. The compute job and eight shared controls also reserve 4.0 combined,
  leaving room for at most 1.0 already spent on probes. The probe threshold is checked after each reconciliation;
  it is not a separate 1.0 stage allocation and cannot guarantee that an abnormal two-hour probe spends under
  1.0. If reconciled probe spend reaches 1.0, do not submit another pair; if it exceeds 1.0, the compute pair's
  4.0 reservation cannot fit and the study ends incomplete. The combined 5.0 meter cap remains the hard limit.
  Stop at a meter refusal; do not revise limits in response to results.
- **Admission check:** before committing any executable request, exercise `validate_request` **and** `decide`
  with both sides open and all earlier reconciled charges, through every planned pair and the compute controls.
  Also check the remaining cumulative envelope and reconcile before every actual admission. Syntax validation
  alone does not establish affordability. These are proposed limits, not a revision of the live budget.
- **Concurrency:** at most 2 nodes. One probe pair is 1 + 1 node; the matched compute pair is also 1 + 1 node.
  Queue probes and compute do not overlap.
- **Calendar:** at least 2 days, for the probes.
- **Storage:** at most 96 rerun products (eight rows of at most six seeds on each path) × 185 kB, plus logs and receipts.

## 6. Prerequisites and the grant

1. **Timing.** s5p production is terminal, by the handoff's four conditions. **The benchmark's budget revision and
   rebind come only after the recompute lane's final verification**, because a rebind makes the meter refuse the
   deploy that lane uses, as recorded for transition r2.
2. **An owner grant, separate from s5p's authorization,** stating:
   - the amount (at most **5.0 billed CPU node-h**, revised to cover all eight controls and peak reservations);
   - where it is accounted. The **proposed route** is a new stage, `packing_benchmark`, in an s5p budget revision
     after terminal, funded from s5p's reconciled unspent production. It is **not** funded from verification/repair
     and fits within the cumulative 345.27 **after terminal charges are reconciled**; if 5.0 cannot be funded
     while retaining the verification reserve, the benchmark is not affordable under this route. The alternative
     is a new meter campaign key, which needs a reviewed meter
     code change;
   - concurrency (at most 2 nodes) and QOS (`regular` and `shared` only);
   - that the benchmark changes nothing in s5p.
3. **Meter admission without unpriced flags.** Before any submission, pass each probe and benchmark request
   through the meter's `validate_request` and the reservation-aware `decide` checks in §5. The regular request must
   be modelled as a whole node
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
- No probe start-delay claim from fewer than 8 pairs, no simultaneous-slot claim from `sleep 60`, and no general
  scheduling or campaign speed-up claim from one matched compute pair.
