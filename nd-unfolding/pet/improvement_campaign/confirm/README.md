# Confirmatory-stage infrastructure (task V1)

## Status (resume anchor; newest first)

- 2026-09-24 01:35Z: **FINAL submitted** (code `e61ba86c`, after the sizing record below was committed):
  `runs/final.tsv`, out `/pscratch/sd/j/josephrb/pet-improvement-20260922/confirm/final`, debug
  chains 58808974 + 58809024, 36 gpu_shared copies (ids in `final/submissions.txt`). PILOT 8/9
  complete and harvested (`results/pilot/`, `CONFIRM_RESULTS.md`); `pilot-C-P2` at 4/10 on the
  pilot chain. STRESS: 6 iterations in 5 h -- its gpu_shared copies and its full-node regular
  (58800973/4) and preempt (58800975/6) chains have NOT started (Priority). Measured waits so far:
  gpu_shared 2 of 45 started, after 188 and 201 min; regular/preempt none in 4 h; gpu_debug a few
  minutes once a slot is free (2 running per user). Throughput is the binding constraint:
  ~16 run-iterations per 35-min debug cycle for both slots together.
- Harvest: `confirm/harvest.sh <stage>` then `python analyze_confirm.py > tables`.
- 2026-09-23 21:15Z: first chain round measured ONE 767 s iteration per 30-min round (60 s margin;
  the 1.1x estimate crosses the deadline). Chain v2 (`c4726062`: next round queued `afterany` at the
  start, margin 15 s) replaces it; the old-code successors 58799686/58799690 were cancelled (own
  jobs). Debug slots (2 per user) now serve PILOT only: chains 58799222 + 58799224 on
  `runs/pilot.tsv`. STRESS runs rely on their 36 gpu_shared copies (all still PENDING at 21:15Z).
  Inputs-only check of the D4c, D5 and R1 stress rows on the real inventory passed (CPU job 58798949).
- 2026-09-23 20:41Z, CONFIRMATORY STAGE SUBMITTED (code `661cb5b9`; checkout
  `/pscratch/sd/j/josephrb/pet-improvement-20260922/checkouts/661cb5b9`). PILOT (pool P, replicates
  0-2, CTL/A, B, C, K = 10: `runs/pilot.tsv`, out `.../confirm/pilot`, chain 58798408 + gpu_shared
  singles 58798410-58798419) and STRESS (pool T, replicates 0-1, the six amendment-2 cases:
  `runs/stress.tsv`, out `.../confirm/stress`, chain 58798420 + singles 58798421-58798485); population
  targets + tests on Perlmutter: CPU job 58798405 (`.../confirm/targets-log`). Every submission is in
  `<out>/submissions.txt`; each run's lock history in `<out>/<run>/lock-history.txt`.
  Resume: `squeue -u josephrb`; harvest `<out>/<run>/scores.json`. FINAL waits for the PILOT sizing
  record below (committed before any pool F row is read).
- 2026-09-23 (code `0f83a0c5`, chain 58786058 -> 58786334 -> 58786713, `results/v1-infra-0f83a0c5/`):
  items 1-6 DONE. Tests: 30 passed on Perlmutter (job 58786149, `75e4b5cf`, incl. the real-pool and
  B1-populations tests); 17 + 2 skipped locally.
  * **5(a) positive control, MEASURED.** Historical halves through this path: every engine input
    byte-identical to `closure_data.build_closure_inputs` (CPU job 58786043 and again in the GPU run);
    frozen tilt constants equal the historical half-A quantiles; pushes and pulls of k = 1-3
    **bit-identical** to B2's `b2e3-H-K10-s1` (max abs diff 0.0; resumed across 3 jobs); recovery
    k = 3 = 0.3226641379 (B2's scorer on the same bits differs at ~4e-14 absolute: summation order,
    cause not established).
  * **6 mechanics, MEASURED (pool S, replicate 0, H, K = 2, seed 1):** input build 103 s (the
    forced halves 186 s, incl. the crosscheck); iterations 759 s and 741 s on one A100 (control:
    768, 750, 729 s). R(k=1, 2) = 0.180, 0.260 against the replicate target, 0.179, 0.258 against the
    pool-S population target; oracle anchor 0.986 (replicate) / 0.991 (population); replicate vs
    population target L1 0.0024 (injected L1 0.270).
  * The race worked: the gpu_debug copy started first and cancelled the preempt copy (58786061).
- **No PILOT or FINAL run has been launched and no row of pools P or F has been read.** Both pools
  are refused by the code until the protocol carries Amendment 2 (the candidate freeze).

### Cost per run (for sizing PILOT/FINAL)

One run at the historical size = load ~100-190 s + **~750 s per OmniFold iteration on one A100**
(H recipe, 8 epochs/step). K = 3: ~0.7 GPU-h; K = 10: ~2.1 GPU-h (GPU-seconds per run; four runs
share a node). In 30-min `gpu_debug` rounds with `DEADLINE_MARGIN=90` only ONE iteration fits per
round (load + 750 s + 1.1 x 750 s > 1710 s), so each round charges ~1.1 node-GPU-h for up to four
runs x one iteration: K rounds per batch of four. Two iterations per round need `DEADLINE_MARGIN<=60`
and load <= 130 s (B2's setting); full-node `regular`/`preempt` copies avoid the per-round reload.
Pool capacity at the protocol's sizes: P 3, F 12, S 15, T 6 disjoint replicates.

## FINAL sizing record (PROTOCOL 5.3, amendment 3) — committed BEFORE any pool F row is read

Written 2026-09-24 ~01:40Z from the PILOT runs scored so far (`results/pilot/`, 8 of 9 runs
COMPLETE; `pilot-C-P2` was at iteration 4 of 10). Rule (`analyze_confirm.sizing`): n = max(8, the n
giving 80 % power at one-sided alpha = 0.05/3 (Holm's first step, conservative) to reject "paired
difference <= -0.02" when the true difference is 0, with sigma = the 80 % upper confidence bound of
the pilot sd), capped at 12 (pool F's disjoint capacity).

| paired difference | pilot replicates | mean | sd (df) | 80 % UCB of sd | n for 80 % power |
|---|---|---:|---:|---:|---:|
| A - CTL | +0.1600, +0.1794, +0.1522 | +0.1639 | 0.0140 (2) | 0.0296 | 22 |
| B@10 - CTL | +0.2456, +0.2224, +0.1895 | +0.2191 | 0.0282 (2) | 0.0597 | 81 |
| C@10 - CTL | +0.4250, +0.4670 | +0.4460 | 0.0297 (1) | 0.1172 | 200 |
| B@3 - CTL | +0.1569, +0.1263, +0.1547 | +0.1460 | 0.0171 (2) | 0.0361 | 32 |
| C@3 - CTL | +0.2384, +0.2884 | +0.2634 | 0.0354 (1) | 0.1395 | 200 |

**n = 12** (the cap; uncapped requirement 200). The A - CTL and B - CTL differences,
complete on all 3 pilot replicates, already require 22 and 81 > 12, so the missing `pilot-C-P2`
cannot change n: every value it could take leaves n at the cap. FINAL = pool F replicates 0-11 x
(CTL/A, B, C) = 36 runs (`runs/final.tsv`, configs `configs/final/`, generated by `freeze_runs.py`).
As amendment 3 anticipated, 12 replicates give less than the nominal 80 % power for the largest
pilot sds; that is reported with the FINAL result, not compensated.

## What this is

PET is diagnostic method development; simulation only. This directory turns a frozen `RunConfig` plus
(pool, replicate, distortion) into one PET unfolding with per-iteration scores, so that PILOT and
FINAL (protocol section 5) are one command once the candidates are frozen.

| file | role |
|---|---|
| `replicate_inputs.py` | draws (pool, replicate) with `phase_e/replicates.py`; loads those rows exactly as the historical loader does (its mc-only branch with `imc` = the rows, opened through `authorization_scope.SignalOnlyNpz`, so no real-data member is read); assembles the closure exactly as `closure_data.build_closure_inputs`; the development distortion `dev` = the historical tilt with its constants READ from `frozen_design.ENDPOINT` and the historical tilt spec; other truth-weight distortions from `phase_e/distortions.py` by id (reco-response ones are refused, not approximated); pools P/F refused before Amendment 2 |
| `run_replicate.py` | the run entry: `--config` + `--config-hash` (refused on mismatch), `--pool S --replicate r` or `--historical-halves`, `--distortion`; B2's training loop (per-iteration state, bit-exact resume, deadline, arms, opt-in efficiency-corrected step 2); `run_identity.json` refuses a resume onto different rows/config/distortion; receipt records the row and identity digests |
| `score_replicate.py` | per iteration: the historical score against the replicate's own pseudodata target (a historical `Endpoint`, `scalar_common.score_push`), the same against the population target, pull score, signed per-bin residuals, regions, truth-weight tails and ESS, step-1 reco E_avail closure; per run: the oracle anchor (exact distortion on the prior) against both targets; `--reference-run` byte-compares iterations with a B2 run |
| `population_target.py` | the distorted seven-bin spectrum over a whole pool (aggregate + regions), once per (pool, distortion) |
| `make_confirm_configs.py`, `configs/` | V1's two configs (B2's H seed 1, K = 3 and K = 2) |
| `runs/*.tsv` | run manifests (name, config, config hash, selection, distortion, reference run, extra args) |
| `jobs/sbatch_confirm_chain.sh` | batch launcher: 4 runs per `gpu_debug` node, self-chaining with bit-exact resume, targets and scoring in the job |
| `jobs/submit_confirm.sh` | submits a manifest; optional race against full-node `regular`/`preempt` copies (first to start wins, cancels the others it created) |
| `test_confirm.py` | scope guards, positive controls 5(a) on a synthetic inventory, 5(b) replicate disjointness/independence, 5(c) tilt reproduction, scorer anchors; `perlmutter`-only tests read the real pool codes / B1 populations |
| `resources-V1.tsv` | every job V1 submitted, from `sacct` |

## Running PILOT / FINAL once candidates are frozen

1. Commit the frozen configs (their content hashes) and the protocol's Amendment 2.
2. Write a manifest, one row per (candidate, replicate), e.g. `cand-A-P0  candA.json  <hash>  P:0  dev  -  -`.
3. On Perlmutter, from a clean clone pinned at the commit:
   `jobs/submit_confirm.sh $C runs/<manifest>.tsv /pscratch/sd/j/josephrb/pet-improvement-20260922/confirm/<stage> [regular preempt]`.
4. Scores land in `<out>/<name>/scores.json`.

Pool capacity at the protocol's sizes (600,130 + 600,111 per replicate, disjoint): **P 3, F 12, S 15,
T 6** (`test_historical_size_capacity_per_pool`). PILOT's 4 replicates do not fit disjointly in pool
P; a fourth needs `disjoint=False` (measured overlap reported) or smaller samples -- an orchestrator
decision.
