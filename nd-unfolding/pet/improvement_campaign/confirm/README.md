# Confirmatory-stage infrastructure (task V1)

## Status (resume anchor; newest first)

- 2026-09-23: items 1-5 implemented; local tests pass (`test_confirm.py`, synthetic inventory:
  the forced-historical-rows path is byte-identical to `closure_data.py`). Next: the GPU positive
  control on the real halves and the pool-S mechanics run (`runs/v1-infrastructure.tsv`).
- **No PILOT or FINAL run has been launched and no row of pools P or F has been read.** Both pools
  are refused by the code until the protocol carries Amendment 2 (the candidate freeze).

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
