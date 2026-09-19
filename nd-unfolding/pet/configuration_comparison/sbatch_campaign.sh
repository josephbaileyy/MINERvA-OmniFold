#!/bin/bash
# One arm-pair evaluation per array task. Stage is chosen by --export.
#
# STAGES RUN IN ORDER AND THE ORDER IS NOT OPTIONAL. Tuning selects the learning
# rate on the tuning split alone; the pilot measures sigma and sizes the final;
# the final is the comparison. Running them concurrently would let the final see
# data the tuning chose on, which is the leak the disjoint splits exist to
# prevent. Submit with `--dependency=afterok:<previous stage>`.
#
# Each task is one (arm, seed) and writes weights plus a receipt. Nothing here
# scores or compares: scoring is a separate pass over the frozen endpoint.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu&hbm40g
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=20:00:00
#SBATCH --job-name=pet-campaign
set -eo pipefail

: "${STAGE:?STAGE must be set: tuning|pilot|final}"
: "${CHECKOUT:?}" ; : "${OUTPUT:?}" ; : "${COMMIT:?}"
: "${INPUTS_NPZ:?}" ; : "${THEIRS_PACKED:?}" ; : "${THEIRS_INDEX:?}"

cd "$CHECKOUT"
[[ "$(git rev-parse HEAD)" == "$COMMIT" ]]
[[ -z "$(git status --porcelain)" ]]

# The frozen seed lists. A seed outside them is refused by the driver too; this
# is the launcher's half of the same guard.
case "$STAGE" in
  tuning) SEEDS=(17 29 43 59) ;;
  pilot)  SEEDS=(71 89 101 113) ;;
  final)  SEEDS=(127 139 151 163 179 191 211 223) ;;
  *) echo "unknown stage $STAGE" >&2; exit 2 ;;
esac
ARMS=(ours theirs)
INDEX=$((SLURM_ARRAY_TASK_ID - 1))
ARM="${ARMS[$((INDEX % 2))]}"
SEED="${SEEDS[$((INDEX / 2))]}"
LR="${LEARNING_RATE:-0.0001}"

RUN="${OUTPUT}/${STAGE}/${ARM}-seed${SEED}"
mkdir -p "$RUN"
scontrol show job -o "$SLURM_JOB_ID" > "$RUN/allocation.txt"
nvidia-smi --query-gpu=uuid,name,memory.total --format=csv > "$RUN/gpu.csv"
export PYTHONUNBUFFERED=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export NVIDIA_TF32_OVERRIDE=0

( module load tensorflow/2.15.0
  python nd-unfolding/pet/configuration_comparison/run_arm_evaluation.py \
    --arm "$ARM" --seed "$SEED" --stage "$STAGE" --learning-rate "$LR" \
    --repo "$CHECKOUT" --inputs-npz "$INPUTS_NPZ" \
    --theirs-packed "$THEIRS_PACKED" --theirs-index "$THEIRS_INDEX" \
    --weights-folder "$RUN/weights" --output "$RUN/receipt.json"
) > "$RUN/run.log" 2>&1

[[ -s "$RUN/receipt.json" ]]
echo COMPLETE > "$RUN/terminal.txt"
