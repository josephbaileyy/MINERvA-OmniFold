#!/bin/bash
# WHERE the ported arm's cost is, decomposed -- forward, forward+backward, apply --
# with peak device memory per section, for his COMPLETE arm at both token counts
# and both intended batches.
#
# WHY THIS EXISTS. `MATCHED_TIMING-20260919.json` established that the Keras port
# costs 23.9x our incumbent per example in the same engine. It did not establish
# where that goes, and the three candidate causes (the tape, the optimizer, his
# local neighbourhood block) have different remedies and different prices.
#
# A first CPU smoke test appeared to put 96 % of the step in `apply_gradients`.
# That was an artifact of my own measurement: the backward section returned
# `loss + 0.0 * gradient`, Grappler folded the multiply and pruned the gradient
# subgraph, and the backward pass's cost therefore landed in the apply by
# subtraction. Measured directly, applying all 176 variables costs 6.06 ms against
# 4.71 ms for stock Keras Adam -- 1.29x, not a bottleneck. The folding control now
# travels with the measurement instead of being a habit I have to remember.
#
# Also measured here: the algebraic optimisations already landed in the port
# (proved bitwise-identical by `test_port.OptimisationEquivalence`), XLA, and
# gradient accumulation at micro-batch 512.
#
# NOT AUTHORIZED BY ITS OWN EXISTENCE. Trains nothing to convergence, produces no
# closure statistic, reads no real source, writes only into its own output
# directory.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=02:30:00
#SBATCH --job-name=pet-port-profile
set -euo pipefail

checkout=$1
output=$2
expected_commit=$3
# Optional comma-separated cell list, so a subset can be re-run without
# re-measuring what already landed. Empty means every cell.
only=${4:-}

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]

mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
nvidia-smi --query-gpu=uuid,pci.bus_id,name,memory.total --format=csv > "$output/gpu.csv"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_FORCE_GPU_ALLOW_GROWTH=true
# TF's `enable_tensor_float_32_execution(False)` sets a TENSORFLOW-level flag, and
# the XLA-compiled path does not appear to honour it: with that flag reporting
# False, the XLA forward differed from eager on 100 % of rows with a median of
# 6.9e-4, and the SAME XLA program at two batch sizes differed by 2.3e-3 per row.
# A network with no cross-row operation cannot be batch-dependent at 1e-3 unless
# the arithmetic itself is changing, and 1e-3 is exactly TF32's precision.
# `NVIDIA_TF32_OVERRIDE=0` disables TF32 in cuBLAS/cuDNN themselves, below both TF
# and XLA, which is the only control that can bind the compiled path.
export NVIDIA_TF32_OVERRIDE=${NVIDIA_TF32_OVERRIDE:-0}

driver=nd-unfolding/pet/configuration_comparison/profile_ported_step.py
cells="$output/cells"
mkdir -p "$cells"

# ONE PROCESS PER CELL, for the reason job 58552592 established: a TensorFlow GPU
# OOM is process-fatal, so an in-process try/except loses every completed cell
# with it. A missing file is therefore itself a measurement, and the merge step
# lists what is missing rather than eliding it.
#
# CHEAP CELLS FIRST. If the walltime runs out it must take the XLA cells, which
# are the slowest to compile and the least load-bearing, and not the baseline the
# whole comparison is read against.
( module load tensorflow/2.15.0
  run() {
    local key=$1 limit=$2
    local safe
    if [[ -n "$only" && ",$only," != *",$key,"* ]]; then return 0; fi
    safe=$(printf "%s" "$key" | tr "|" "_")
    timeout --kill-after=20s "$limit" python "$driver" --repo "$checkout" \
      --cell "$key" --output "$cells/$safe.json" || true
  }
  for variant in ours_incumbent baseline broadcast optimised; do
    for tokens in 12 33; do
      for batch in 512 2048; do
        for mode in forward train; do
          run "$variant|$tokens|$batch|$mode" 300s
        done
      done
    done
  done
  for tokens in 12 33; do
    run "accum4|$tokens|2048|train" 420s
  done
  for variant in optimised_xla broadcast_xla; do
    for tokens in 12 33; do
      for batch in 512 2048; do
        for mode in forward train; do
          run "$variant|$tokens|$batch|$mode" 600s
        done
      done
    done
  done
  python "$driver" --repo "$checkout" --cell-dir "$cells" \
    --output "$output/port-profile.json"
  ) > "$output/port-profile.log" 2>&1

[[ -s "$output/port-profile.json" ]]
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
