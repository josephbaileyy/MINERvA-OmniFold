#!/bin/bash
# Bounded GPU cost calibration for the matched comparison. Measures per-example training
# cost for both arms at their real configurations on one A100. Trains nothing to
# convergence, produces no closure statistic, touches no matrix or validation receipt,
# and writes only into its own output directory.
#
# NOT AUTHORIZED BY ITS OWN EXISTENCE. This script is committed as a reviewable artifact;
# submitting it needs Joseph's approval of stage 2.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:20:00
#SBATCH --job-name=pet-cost-calibration
set -euo pipefail

checkout=$1        # our repository checkout
runtime=$2         # python runtime with TensorFlow + tf_keras
torch_runtime=$3   # python runtime with PyTorch (his backbone)
gregor=$4          # gregorkrz/minerva-ml checkout, expected at the pinned commit
output=$5
expected_commit=$6
expected_gregor_commit=${7:-fc9a099d3c9c060f03cef293c294f9de4eb019cd}

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
# Pin the OTHER repository too: a cost ratio against an unpinned upstream is not a
# measurement of the configuration this campaign names.
[[ "$(git -C "$gregor" rev-parse HEAD)" == "$expected_gregor_commit" ]]
[[ -z "$(git -C "$gregor" status --porcelain)" ]]

mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TF_USE_LEGACY_KERAS=1
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8

# The two arms live in different frameworks, so they are timed by two interpreters
# against one GPU. Each writes its own half; the reducer refuses a partial pair, so a
# silently-missing arm cannot become a one-sided cost report.
driver=nd-unfolding/pet/configuration_comparison/calibrate_cost.py

timeout --kill-after=30s 600s "$runtime/bin/python" "$driver" \
  --arm ours --repo "$checkout" \
  --output "$output/half-ours.json" > "$output/calibration-ours.log" 2>&1

timeout --kill-after=30s 600s "$torch_runtime/bin/python" "$driver" \
  --arm theirs --gregor-checkout "$gregor" \
  --output "$output/half-theirs.json" > "$output/calibration-theirs.log" 2>&1

# The reducer needs neither framework, so it runs under either interpreter.
"$runtime/bin/python" "$driver" --arm reduce \
  --ours-half "$output/half-ours.json" --theirs-half "$output/half-theirs.json" \
  --output "$output/cost-calibration.json" >> "$output/calibration-ours.log" 2>&1

[[ -s "$output/cost-calibration.json" ]]
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
