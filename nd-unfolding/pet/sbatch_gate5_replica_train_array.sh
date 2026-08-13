#!/bin/bash
#SBATCH --job-name=g5train
#SBATCH --account=m3246
#SBATCH --qos=gpu_shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --array=0-49%10
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/train_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/train_%A_%a.err
set -eo pipefail

CODE_ROOT=${GATE5_CODE_ROOT:?submit controller must export GATE5_CODE_ROOT}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_EXPECTED_HEAD:?submit controller must export GATE5_EXPECTED_HEAD}
EXPECTED_DRIVER_SHA=${GATE5_EXPECTED_TRAIN_DRIVER_SHA:?missing train-driver pin}
EXPECTED_NOMINAL_SHA=${GATE5_EXPECTED_NOMINAL_DRIVER_SHA:?missing nominal-driver pin}
EXPECTED_LOADER_SHA=${GATE5_EXPECTED_LOADER_SHA:?missing loader pin}

DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_replica.py
NOMINAL=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_nominal.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
GATE3=${CODE_ROOT}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json
INDEX=${SLURM_ARRAY_TASK_ID:?array task ID missing}
SEED=$((50000 + INDEX))
REPLICA=$(printf 'replica_%02d' "$INDEX")
BASE=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50/replicas/${REPLICA}
TARGET=${BASE}/target/GATE5_REPLICA_TARGET.npy
TARGET_RECEIPT=${BASE}/target/GATE5_REPLICA_TARGET_RECEIPT.json
OUTDIR=${BASE}/training
OUTPUT=${OUTDIR}/GATE5_REPLICA_WEIGHTS.npz
TRAIN_RECEIPT=${OUTDIR}/GATE5_REPLICA_TRAINING_RECEIPT.json

die() { echo "[gate5-train][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || die "replica driver hash drift"
[[ "$(sha_of "$NOMINAL")" == "$EXPECTED_NOMINAL_SHA" ]] || die "pinned nominal driver hash drift"
[[ "$(sha_of "$LOADER")" == "$EXPECTED_LOADER_SHA" ]] || die "loader hash drift"
for f in "$INPUT" "$GATE3" "$TARGET" "$TARGET.done" "$TARGET_RECEIPT" "$TARGET_RECEIPT.done"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
for f in "$OUTPUT" "$OUTPUT.done" "$TRAIN_RECEIPT" "$TRAIN_RECEIPT.done"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
done
mkdir -p "$OUTDIR"

source "${DATA_ROOT}/setup_salloc_env.sh"
module load tensorflow/2.15.0
export PYTHONPATH="${CODE_ROOT}/omnifold_nn:${CODE_ROOT}/2d-unfolding:${CODE_ROOT}/nd-unfolding:${CODE_ROOT}/nd-unfolding/pet:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "TensorFlow environment python3 missing"
"$PYTHON_BIN" -c 'import tensorflow as tf; import omnifold; print(tf.__version__)' \
  || die "TensorFlow/PET import preflight failed"

echo "[gate5-train] index=$INDEX seed=$SEED job=${SLURM_ARRAY_JOB_ID}_${INDEX} head=$EXPECTED_HEAD"
"$PYTHON_BIN" "$DRIVER" \
  --inputs "$INPUT" \
  --target-npy "$TARGET" \
  --target-receipt "$TARGET_RECEIPT" \
  --output "$OUTPUT" \
  --train-receipt "$TRAIN_RECEIPT" \
  --gate3-manifest "$GATE3" \
  --bootstrap-seed "$SEED" \
  --replica-index "$INDEX"
echo "[gate5-train] DONE index=$INDEX seed=$SEED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
