#!/bin/bash
# Framework-MATCHED timing: our incumbent PET and the ported PET2, both in
# TensorFlow, on one GPU, at both OmniFold step schemas, both token counts, both
# intended batches, in production precision (float32), training and inference.
#
# WHY THIS EXISTS. Every ratio measured before this one compared our TensorFlow PET
# against his PyTorch PET2, so it folded a framework difference into a number that
# was going to be read as an architecture difference. The Keras port now makes the
# same-engine comparison possible, and this is the measurement the final costing
# should use. Only ONE module is needed, because both arms are Keras.
#
# NOT AUTHORIZED BY ITS OWN EXISTENCE. It trains nothing to convergence, produces no
# closure statistic, touches no matrix or validation receipt, reads no real source,
# and writes only into its own output directory.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:40:00
#SBATCH --job-name=pet-matched-timing
set -euo pipefail

checkout=$1
output=$2
expected_commit=$3

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]

mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
nvidia-smi --query-gpu=uuid,pci.bus_id,name --format=csv > "$output/gpu.csv"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8

driver=nd-unfolding/pet/configuration_comparison/calibrate_cost.py
( module load tensorflow/2.15.0
  timeout --kill-after=30s 2100s python "$driver" \
    --arm matched --repo "$checkout" --output "$output/matched-timing.json" \
  ) > "$output/matched-timing.log" 2>&1

[[ -s "$output/matched-timing.json" ]]
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
