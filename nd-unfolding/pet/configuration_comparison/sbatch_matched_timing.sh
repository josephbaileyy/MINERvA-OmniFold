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
#SBATCH --time=01:30:00
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
# TensorFlow grabs the whole device by default. On a shared GPU that both wastes
# memory and turns a large cell into an OOM that a neighbour caused.
export TF_FORCE_GPU_ALLOW_GROWTH=true

driver=nd-unfolding/pet/configuration_comparison/calibrate_cost.py
cells="$output/cells"
mkdir -p "$cells"

# ONE PROCESS PER CELL. A TensorFlow GPU OOM is process-fatal: measured on job
# 58552592, two ResourceExhaustedError cells were caught by the in-process
# try/except and the interpreter then died on `Unexpected Event status: 1`,
# taking every already-completed cell with it. `|| true` keeps the loop going;
# the merge step reports what is missing rather than inventing it.
( module load tensorflow/2.15.0
  for arm in ours_incumbent ported_pet2; do
    for step in step1_reco step2_gen; do
      for tokens in 12 33; do
        for batch in 512 2048; do
          for mode in train inference; do
            key="$arm|$step|$tokens|$batch|$mode"
            safe=$(printf "%s" "$key" | tr "|" "_")
            timeout --kill-after=20s 240s python "$driver" --arm cell \
              --repo "$checkout" --cell "$key" --output "$cells/$safe.json" || true
          done
        done
      done
    done
  done
  for tokens in 12 33; do
    for batch in 512 2048; do
      for mode in train inference; do
        key="theirs_complete|his_own_schema|$tokens|$batch|$mode"
        safe=$(printf "%s" "$key" | tr "|" "_")
        timeout --kill-after=20s 240s python "$driver" --arm cell \
          --repo "$checkout" --cell "$key" --output "$cells/$safe.json" || true
      done
    done
  done
  python "$driver" --arm merge-cells --cell-dir "$cells" \
    --output "$output/matched-timing.json"
  ) > "$output/matched-timing.log" 2>&1

[[ -s "$output/matched-timing.json" ]]
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
