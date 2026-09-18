#!/bin/bash
# Bounded GPU cost calibration for the matched comparison. Measures per-example training
# throughput for both arms at their real configurations, at 12 and 33 tokens, on one GPU.
# Trains nothing to convergence, produces no closure statistic, touches no matrix or
# validation receipt, and writes only into its own output directory.
#
# NOT AUTHORIZED BY ITS OWN EXISTENCE. Submitting it needs approval of the calibration
# stage.
#
# TWO ENVIRONMENTS, ONE GPU. Our arm needs the vendored Keras-2 PET, which the
# tensorflow/2.15.0 module satisfies (the pet-direct-token runtime carries keras 3.15.1
# and cannot build it). His arm needs PyTorch plus einops, which the pytorch/2.6.0 module
# plus a private site directory satisfy. Neither interpreter has both frameworks, so each
# arm writes its own half and a reducer combines them.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:25:00
#SBATCH --job-name=pet-cost-calibration
set -euo pipefail

checkout=$1           # our repository checkout, clean, at $expected_commit
gregor_src=$2         # extracted pinned upstream source tree
einops_site=$3        # private site dir carrying einops
output=$4
expected_commit=$5
expected_gregor_digest=${6:-bd832627c74eb2324d6cda5fbbdddb0e42f91d378dbdfc8cb11948731623d4a0}

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]

# Pin the UPSTREAM too, by source-tree digest rather than by git ref: the staged tree is
# an extract, not a checkout, and bytes are a stronger pin than a ref anyway. This check
# already earned its place -- it caught macOS AppleDouble `._*` files doubling the tree.
gregor_digest=$(cd "$gregor_src" && find src -type f -name '*.py' | LC_ALL=C sort \
  | xargs sha256sum | sha256sum | cut -d' ' -f1)
if [[ "$gregor_digest" != "$expected_gregor_digest" ]]; then
  echo "[calibrate] upstream src digest $gregor_digest != $expected_gregor_digest" >&2
  exit 3
fi

mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
printf "%s\n" "$gregor_digest" > "$output/upstream-src-digest.txt"
nvidia-smi --query-gpu=uuid,pci.bus_id,name --format=csv > "$output/gpu.csv"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8

driver=nd-unfolding/pet/configuration_comparison/calibrate_cost.py

# --- our arm, TensorFlow 2.15 (Keras 2) -------------------------------------------------
( module load tensorflow/2.15.0
  timeout --kill-after=30s 600s python "$driver" \
    --arm ours --repo "$checkout" --output "$output/half-ours.json" \
  ) > "$output/calibration-ours.log" 2>&1

# --- his arm, PyTorch 2.6 + einops + pinned upstream ------------------------------------
( module load pytorch/2.6.0
  export PYTHONPATH="$einops_site:$gregor_src${PYTHONPATH:+:$PYTHONPATH}"
  timeout --kill-after=30s 600s python "$driver" \
    --arm theirs --gregor-checkout "$gregor_src" --output "$output/half-theirs.json" \
  ) > "$output/calibration-theirs.log" 2>&1

# --- reduce; needs neither framework, and refuses a partial or mismatched pair ----------
( module load tensorflow/2.15.0
  python "$driver" --arm reduce \
    --ours-half "$output/half-ours.json" --theirs-half "$output/half-theirs.json" \
    --output "$output/cost-calibration.json" \
  ) >> "$output/calibration-ours.log" 2>&1

[[ -s "$output/cost-calibration.json" ]]
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
