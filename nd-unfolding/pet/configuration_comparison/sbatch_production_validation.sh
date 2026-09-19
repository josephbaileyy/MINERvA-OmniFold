#!/bin/bash
# The execution path we would actually run, validated: XLA, GPU, float32, 33 tokens,
# effective batch 2048, initialized from Gregor's real pretrained checkpoint.
#
# WHY THIS EXISTS. Every port check so far ran in float64 on a CPU against upstream
# torch, which establishes that the port IS his network. It does not establish that
# the EXECUTED path computes the same thing, and the cost figure the campaign rests
# on is XLA's. Item 10 of the goal requires this before comparative training.
#
# Limits are fixed before the measurement and are never widened to accommodate it:
# each is twice the EAGER path's own round-off floor, measured by permuting batch
# rows, and every check carries a negative control -- one weight tensor scaled by
# 1 + 1e-4 -- which must miss the same limit by 10x.
#
# NOT AUTHORIZED BY ITS OWN EXISTENCE. Trains nothing to convergence, produces no
# closure statistic, reads no real source.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=01:30:00
#SBATCH --job-name=pet-prod-validate
set -euo pipefail

checkout=$1
output=$2
expected_commit=$3
state=$4
manifest=$5

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
[[ -f "$state" ]]
[[ -f "$manifest" ]]

mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
nvidia-smi --query-gpu=uuid,pci.bus_id,name,memory.total --format=csv > "$output/gpu.csv"
sha256sum "$state" "$manifest" > "$output/inputs.sha256"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_FORCE_GPU_ALLOW_GROWTH=true

driver=nd-unfolding/pet/configuration_comparison/validate_production_path.py

# One process per step schema: an OOM is process-fatal, and a missing receipt is
# then itself a measurement rather than a lost run.
( module load tensorflow/2.15.0
  for step in step1_reco step2_gen; do
    timeout --kill-after=30s 1500s python "$driver" --repo "$checkout" \
      --state-npz "$state" --manifest "$manifest" --step "$step" \
      --tokens 33 --batch 2048 \
      --output "$output/validation-$step.json" || true
  done
  # The 40 GB confirmation the freeze proposal owes: same cell, native batch.
  ) > "$output/validation.log" 2>&1

[[ -s "$output/validation-step1_reco.json" ]]
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
