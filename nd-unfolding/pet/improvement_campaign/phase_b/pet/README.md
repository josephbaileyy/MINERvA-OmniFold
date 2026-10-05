# Phase B2 — PET stepwise diagnostics and the first controlled feature arms

Report: `PET_DIAGNOSTICS-20260922.md`. Machine-readable results: `results/`. Resource ledger:
`resources-B2.tsv`. Development-stage evidence only (scope §6): it chooses what is tested later and
can never be reused as confirmatory data. PET is diagnostic method development; simulation only.

## Files

| file | role |
|---|---|
| `make_b2_configs.py` | writes `configs/*.json`: the frozen, hashed `RunConfig` of every B2 run. Numbers the historical design froze are read from it (`frozen_design`, `training_recipe` parsed without TensorFlow, the campaign's own tuning selection) |
| `b2_driver.py` | the A1 driver (`improvement_campaign/run_unfold.py`) subclassed: per-iteration pull/push and model state, resume, a deadline, the B2 input arms, an opt-in efficiency-corrected step 2, and the truth-only mode (experiment 2) |
| `b2_arms.py` | named, versioned, hashed input transforms: step-1 reco scalars and stored-cloud summaries (reco-only by construction), step-2 truth scalars, and the truth-cloud PDG encoding (raw / one-hot). `net.py` is untouched |
| `b2_score.py` | scores a run at every iteration on the historical endpoint through B1's `scalar_common` (bit-identical to `score_campaign.score_run`): push, pull, weight tails, ESS, the step-1 detector-level checks and the pulled-vs-pushed decomposition |
| `b2_truth_scalar_ref.py` | experiment 2's T3: B1's scalar classifiers under the same train-on-A / evaluate-on-B protocol |
| `b2_summarize.py` | builds `results/summary.json` and the report's tables from the committed result files |
| `test_b2_arms.py` | arm tests (numpy only): the step-1 leakage refusal, the PDG categories, the one-hot re-indexing, the median fill, hash stability |
| `jobs/sbatch_b2.sh` | guarded launcher: N configs on the allocation's N GPUs, one run per GPU, optional in-job scoring |
| `jobs/sbatch_b2_devcheck.sh` | the mechanics check on one debug node: continuous vs resumed, every transform, truth-only mode, unit tests |

## Rerun

On Perlmutter, from a clean clone of this branch pinned at `$SHA` (the launcher refuses a dirty tree
or a different HEAD):

```bash
SHA=<commit>; C=/pscratch/sd/j/josephrb/pet-improvement-20260922/checkouts/${SHA:0:8}
T=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB2
POP=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/populations.npz
L=$C/nd-unfolding/pet/improvement_campaign/phase_b/pet/jobs/sbatch_b2.sh
D=phase_b/pet/b2_driver.py

# experiment 1 (gate): the historical as-executed recipe through the UNMODIFIED A1 driver
sbatch -q shared --gpus=1 --ntasks=1 -c 32 -t 01:30:00 -o $T/e1-shared/slurm-%j.out \
  --export=ALL,MINE=$C,MINE_COMMIT=$SHA,OUT=$T/e1-shared,CONFIGS=b2e1-H-K3-s1.json $L

# experiment 2 (truth-only learnability), four runs per full node
sbatch -q preempt --requeue -C gpu -N 1 --gpus=4 -c 128 -t 03:00:00 -o $T/e2/slurm-%j.out \
  --export=ALL,MINE=$C,MINE_COMMIT=$SHA,OUT=$T/e2,DRIVER=$D,\
DRIVER_ARGS="--mode truth_only --populations $POP",\
CONFIGS="b2e2-T0-s1.json b2e2-T1-s1.json b2e2-T2-s1.json b2e2-T0-s2.json" $L

# experiments 3-5 (K = 10 unfolding), four runs per full node, scored in the job
sbatch -q regular -C gpu -N 1 --gpus=4 -c 128 -t 03:30:00 -o $T/k10a/slurm-%j.out \
  --export=ALL,MINE=$C,MINE_COMMIT=$SHA,OUT=$T/k10a,DRIVER=$D,SCORE=1,POPULATIONS=$POP,\
CONFIGS="b2e3-H-K10-s1.json b2e3-H-K10-s2.json b2e4-S1-K10-s1.json b2e4-S1-K10-s2.json" $L
```

A config token may carry its own driver arguments after a `|`, e.g.
`b2e4-M-K10-s1.json|--step2-miss-mode=efficiency_corrected`. A run that hits the allocation's
deadline exits `INCOMPLETE` and the same command resumes it (see the report on what a resume does
and does not preserve).

Copy `scores.json` / the truth-only `receipt.json` into `results/` (as `<run>.scores.json` and
`<run>.truth_only.json`) and run `python b2_summarize.py` to rebuild the tables.

Tests (any python with numpy and pytest): `python -m pytest -q test_b2_arms.py`.
