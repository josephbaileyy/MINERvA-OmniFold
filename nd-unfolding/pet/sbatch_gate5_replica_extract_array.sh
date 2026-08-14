#!/bin/bash
#SBATCH --job-name=g5extract
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --array=0-49%10
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/extract_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/extract_%A_%a.err
set -eo pipefail

CODE_ROOT=${GATE5_CODE_ROOT:?submit controller must export GATE5_CODE_ROOT}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_EXPECTED_HEAD:?missing immutable code HEAD}
EXPECTED_INPUT_SHA=${GATE5_EXPECTED_INPUT_SHA:?missing promoted input SHA}
EXPECTED_DRIVER_SHA=${GATE5_EXPECTED_EXTRACT_DRIVER_SHA:?missing replica extractor pin}
EXPECTED_NOMINAL_EXTRACTOR_SHA=${GATE5_EXPECTED_NOMINAL_EXTRACTOR_SHA:?missing nominal extractor pin}
EXPECTED_LOADER_SHA=${GATE5_EXPECTED_LOADER_SHA:?missing loader pin}

DRIVER=${CODE_ROOT}/nd-unfolding/pet/extract_fullevent_replica.py
NOMINAL_EXTRACTOR=${CODE_ROOT}/nd-unfolding/pet/extract_fullevent_fps.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
INDEX=${SLURM_ARRAY_TASK_ID:?array task ID missing}
SEED=$((50000 + INDEX))
REPLICA=$(printf 'replica_%02d' "$INDEX")
BASE=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50/replicas/${REPLICA}
WEIGHTS=${BASE}/training/GATE5_REPLICA_WEIGHTS.npz
TRAIN_RECEIPT=${BASE}/training/GATE5_REPLICA_TRAINING_RECEIPT.json
OUTDIR=${BASE}/extraction
PUSH=${OUTDIR}/GATE5_REPLICA_FULL_PUSH.npz
XSEC=${OUTDIR}/GATE5_REPLICA_XSEC.npz
SUMMARY=${OUTDIR}/GATE5_REPLICA_XSEC.summary.json
RECEIPT=${OUTDIR}/GATE5_REPLICA_EXTRACTION_RECEIPT.json

die() { echo "[gate5-extract][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "immutable code worktree is dirty"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || die "replica extractor hash drift"
[[ "$(sha_of "$NOMINAL_EXTRACTOR")" == "$EXPECTED_NOMINAL_EXTRACTOR_SHA" ]] \
  || die "Gate-4-pinned nominal extractor hash drift"
[[ "$(sha_of "$LOADER")" == "$EXPECTED_LOADER_SHA" ]] || die "loader hash drift"
for f in "$INPUT" "$WEIGHTS" "$WEIGHTS.done" "$TRAIN_RECEIPT" "$TRAIN_RECEIPT.done"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
for f in "$PUSH" "$PUSH.done" "$XSEC" "$XSEC.done" \
         "$SUMMARY" "$SUMMARY.done" "$RECEIPT" "$RECEIPT.done"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
done
mkdir -p "$OUTDIR"

source "${DATA_ROOT}/setup_salloc_env.sh"
module load tensorflow/2.15.0
export PYTHONPATH="${CODE_ROOT}/omnifold_nn:${CODE_ROOT}/2d-unfolding:${CODE_ROOT}/nd-unfolding:${CODE_ROOT}/nd-unfolding/pet:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
TF_PY=$(command -v python3 || true)
[[ -n "$TF_PY" && -x "$TF_PY" ]] || die "TensorFlow python3 is unavailable"
"$TF_PY" -c 'import tensorflow as tf; import omnifold; print(tf.__version__)' \
  || die "TensorFlow/PET import preflight failed"
echo "[gate5-extract] PUSH index=$INDEX seed=$SEED job=${SLURM_ARRAY_JOB_ID}_${INDEX}"
"$TF_PY" -u "$DRIVER" \
  --stage push \
  --replica-index "$INDEX" \
  --bootstrap-seed "$SEED" \
  --weights "$WEIGHTS" \
  --inputs "$INPUT" \
  --expected-inputs-sha "$EXPECTED_INPUT_SHA" \
  --push-out "$PUSH"

module unload tensorflow/2.15.0 >/dev/null 2>&1 || true
source "${DATA_ROOT}/setup_salloc_env.sh"
ROOT628_PREFIX=${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}
ROOT_PY=${ROOT628_PREFIX}/bin/python3
[[ -x "$ROOT_PY" ]] || die "ROOT python is unavailable at $ROOT_PY"
"$ROOT_PY" -c 'import ROOT, numpy; assert ROOT.gROOT' || die "ROOT import preflight failed"
echo "[gate5-extract] XSEC index=$INDEX seed=$SEED"
"$ROOT_PY" -u "$DRIVER" \
  --stage xsec \
  --replica-index "$INDEX" \
  --bootstrap-seed "$SEED" \
  --weights "$WEIGHTS" \
  --inputs "$INPUT" \
  --expected-inputs-sha "$EXPECTED_INPUT_SHA" \
  --push-out "$PUSH" \
  --out "$XSEC" \
  --summary "$SUMMARY" \
  --receipt "$RECEIPT"
echo "[gate5-extract] DONE index=$INDEX seed=$SEED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
