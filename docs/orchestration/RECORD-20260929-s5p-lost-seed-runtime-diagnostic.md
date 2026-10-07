# s5p (`OI-193`): runtime diagnostic of the seeds lost to production task timeouts (2026-09-29)

**CITABLE FOR:** which production seeds were lost to task time limits and how (interrupted or never started); the
recorded per-experiment unfolding times and their lane, node and residual components; whether residual runtime is
associated with the unshifted null statistics among COMPLETED experiments; the assumptions under which never-started
losses are outcome-independent; a correction to the campaign's earlier advice on a budget revision. **NOT CITABLE
FOR:** a claim that the missing experiments are unbiased or that validity is unaffected (a null association among
completed experiments cannot establish either); any p-value, decision or change to a frozen rule, product, status,
job, schedule or budget (none is made).

Requested by the owner on 2026-09-29, after the campaign's first statement that the losses "follow node speed, not the
value of any draw" was correctly challenged as stronger than the evidence. That statement is withdrawn; this record
replaces it.

## 1. What was run

- **Script:** `state/s5p/diag/s5p_lost_seed_runtime_diagnostic.py` (sha256 `99b7df2c…`). It is read-only and writes
  only its `--out`.
- **Where it ran:** 2026-09-29T16:33:12Z on login34, with 4 BLAS threads and no allocation.
- **Code tree:** a `git archive` of the pinned deploy `55a41765`, extracted to
  `/pscratch/sd/j/josephrb/s5p-20260926/diag-20260929/code`. Its `s5p_joint.py`, `s5p_inference.py` and
  `s5p_seqstop.py` are byte-identical to `4f5a613f`. No deploy was modified.
- **Output:** the cluster file `/pscratch/sd/j/josephrb/s5p-20260926/diag-20260929/runtime-diagnostic.json`
  (sha256 `84e46ca5…`). The committed copy is `state/s5p/diag/lost-seed-runtime-diagnostic-20260929T1633Z.json`
  (sha256 `70c0aff5…`). Its only change: each `tasks[].log` basename is prefixed with its absolute log directory,
  because the repository's receipt check reads a bare filename as a citation of a tracked file. The copy records
  this in `committed_copy_note`. No measured value changed.
- **Inputs:**
  - every task log in `runs/prod/logs/`: the header, the end line or the Slurm time-limit line, and one
    `{"out", "rc", "seconds"}` line per finished experiment (`seconds` = the product's `seconds_unfold`);
  - the frozen task tables `state/s5p/prod/tables/`;
  - product existence and modification times;
  - each product's unshifted (c = 0) null statistics, computed by `s5p_joint.ensemble` + `s5p_joint.statistics`
    with the design and the frozen V, exactly as the controller computes them. For a power set they are computed
    against its null, with its own `surrogate_seed0`.
- **Population:** 212 finished tasks (3 still running were skipped): batch 0 of all five nulls and P1 (204 tasks),
  plus 6 finished tasks of MEC batch 1 and 2 of P2.

## 2. Lost seeds

All 20 killed tasks were killed `DUE TO TIME LIMIT`, 7,193–7,223 s after their start. There were no anomalies: no
product without a log line, no log line without a product, no completed task missing a seed, and no nonzero `rc`.

| lane | completed | interrupted | never started |
|---|---:|---:|---:|
| GENIE_2_12_10_CV | 193 | 4 | 3 |
| GENIE_2_12_10_MEC (b0 + part of b1) | 229 | 2 | 5 |
| GiBUU_2019 | 195 | 3 | 2 |
| MnvTune_v1 | 195 | 4 | 1 |
| NuWro_21_09 | 197 | 3 | 0 |
| P1_a1.0 | 193 | 4 | 3 |
| P2_a1.0 (partial) | 12 | 0 | 0 |

Each killed task has exactly one **interrupted** seed, the one running at the kill. The **never-started** seeds are
those after it in the same task.

## 3. Runtime components (1,002 warm experiments; position 0 in a task carries the cache build)

- **Median and cold start:** the median is 563 s. A cold (first) experiment takes 1.155 times the warm median.
- **Lane factors:** 0.88 (MEC) to 1.07 (CV, P1, P2). They are small.
- **Node factors:** 0.71 to 3.09 (two-way median polish of log time). They are large.
- **What explains the spread:** the spread of log time is, as SD / MAD, 0.385 / 0.249 raw, 0.373 / 0.234 after
  lane, and 0.277 / 0.113 after lane and node. The node is the dominant identifiable component; the robust spread
  halves once it is removed.
- **Kills by node:** the 20 kills fell on 13 nodes, 11 of which have a node factor of at least 1.23. The top three
  are nid004113 (4 of 6 tasks killed, factor 1.94), nid004090 (2 of 3, 2.24) and nid004072 (2 of 7, 1.59). Two
  kills were on nodes that are not slow overall: nid004088 (1.09) and nid004091 (0.96).

**The interrupted seeds.** Each one's elapsed time at the kill is a **lower bound** on its runtime. Compared with the
lane × node typical time:
- **16 of 20 are below 1.5 times typical.** They were reached late because earlier experiments in their task were
  slow.
- **One is at 1.52 times typical.**
- **Three are at 2.5 times typical or more:**
  - MEC b0_23 seed 1240139 (≥ 3.35×): the task's only completed experiment took 4,995 s on nid004079, so the node
    was slow at the time.
  - GiBUU b0_1 seed 1280009 (≥ 2.78×): the same task ran 2,078 s and 1,276 s.
  - MnvTune b0_32 seed 1200197 (≥ 3.89×): nid004091's factor is 0.96 and its own task ran 794–1,435 s, yet this
    experiment ran ≥ 2,100 s. The node estimate does not explain this one; its own draw may have been slow.

## 4. Runtime vs null statistic among COMPLETED experiments (diagnostic only)

The measure is Spearman ρ between log time (raw, and node-adjusted) and T_total or T_shape, per lane, with a
two-sided permutation p (5,000 permutations).
- **The five calibration lanes and P1 (n = 159–189 each; 24 tests):** |ρ| ≤ 0.09 in 22 tests.
- **The exception is GiBUU T_total:** raw ρ = −0.197 (permutation p = 0.013) and node-adjusted ρ = −0.149 (p = 0.057).
  Across 24 tests the smallest p is not significant after a Bonferroni correction (0.31). It is recorded as weak
  evidence of an association, not dismissed.
- **P2 (n = 10)** is too small to read.

**Direction, as a conditional statement only.** In GiBUU the slower completed experiments have smaller T_total. IF
that held for the interrupted experiments (it cannot be observed), their loss would remove draws below the observed
statistic. That leaves the exceedance count unchanged and lowers B, which moves p up (conservative). This is an
extrapolation, not a finding.

## 5. What this does and does not support

- **Never-started seeds are outcome-independent only under stated assumptions.** Each was lost by its position,
  given the runtimes of the earlier experiments in its task. That makes its own statistic independent of its loss
  only if all of the following hold:
  - **(a) Fixed order:** a task runs its seeds in fixed ascending order in one process (verified:
    `s5p_nullexp.py:307–354`).
  - **(b) Seed-keyed draws:** each experiment's draws depend only on its own seed (`default_rng([seed, 0x5F5])`,
    `split_key_for(seed)`, and the prediction error keyed by `(surrogate_seed0, seed)`). The only state shared
    across seeds, a model cache, does not change results. That last part is **assumed, not verified here**.
  - **(c) Independence across seeds:** the experiments of a task are independent of one another, and the node
    affects only speed, not results. Node-dependent floating-point nondeterminism is **assumed negligible**.
  - **(d) Time-limit kills:** the kill is the time limit (verified for all 20).
- **Interrupted seeds may be outcome-selected** by their own runtime. The association above is measured only on
  completed experiments; the interrupted experiments' statistics are unobserved, so no measurement here bounds them.
- **A deterministic sensitivity is available at terminal, if the owner wants it.** For each null with I interrupted
  seeds, recompute the worst case in which every interrupted draw had exceeded the observed statistic,
  (k + I + 1) / (B + I + 1). A looser version also counts the never-started seeds. It would be a **labelled
  sensitivity** that changes no decision and no rule. The campaign does not adopt it; it is the owner's choice
  whether to report it.
- **Nothing is changed.** No seed is rerun, no schedule or node exclusion is changed, and the budget is not revised.

## 6. Correction to the campaign's advice on a budget revision

The campaign described moving the unallocated 9.647 CPU node-h into the production stage as needing "no job changes".
**That was wrong in practice.**
- Every runner calls `s5c_meter.py --budget docs/orchestration/state/s5p/budget.json` **inside its pinned deploy**
  (`55a41765` or `4f5a613f`).
- The meter refuses when the budget's sha256 differs from the last `budget` record in the shared ledger
  (`s5c_meter.py:241–246`; a changed budget needs `rebind`).
- So a revision plus a rebind would make every running runner's next submission error out and **stop its queue**.
  The only way around that is to move all six runners, at the same moment, to a new deploy that carries the revised
  budget.
- That move would be the 2026-09-28T20:50Z procedure for six lanes: `s5p_requeue.py` resume queues, a commit, a new
  deploy, and one runner per lane, each stopped while it waits on an array.

It is feasible but not cheap or risk-free. It is not proposed now. If the batch-1 forecast makes it necessary, the
campaign will prepare that transition and its checks before asking the owner for approval.
