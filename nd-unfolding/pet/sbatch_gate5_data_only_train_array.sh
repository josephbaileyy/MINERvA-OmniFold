#!/bin/bash
#SBATCH --job-name=g5dotrain
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=08:00:00
#SBATCH --array=0-49%10
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_data_only_n50/logs/train_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_data_only_n50/logs/train_%A_%a.err
set -eo pipefail

# C_stat^data STAGE 2 -- the data-only training family, 50 x ~3.02 A100-h. Gated by aftercorr on the
# matching task of sbatch_gate5_data_only_target_array.sh.
#
# WHY A NEW FILE, AND THE PROHIBITION THAT TRAVELS WITH IT: see the header of the target array. Both
# existing arrays are HASH-PINNED, so a flag through them is a pinned edit; adding names satisfies
# CLAUDE.md's rename/delete prohibition and editing the pinned ones would not.
#
# *** THIS PAIR MUST NEVER LATER BE UNIFIED INTO ONE PARAMETRISED LAUNCHER. *** The tidy-up arrives
# as a refactor and reads as a simplification. `sbatch_*.sh` names are load-bearing provenance.
#
# WHAT THE DRIVER ASSERTS THAT THIS LAUNCHER DOES NOT, so nobody reads a green task as the product
# being correct: P1-P8, live, BEFORE the artifact is written -- product tag, MC factors explicitly
# unity, the data factor canonical, the MC legs bit-exactly unthinned (P5a) and proportional to the
# unthinned reference by one independently-derived scalar (P5b), the seed under its own key, both
# class-ratio operands with what the weights embody, and the loader's own stamp left untouched. A
# thinned-MC data-only replica therefore never comes into existence.
CODE_ROOT=${GATE5_CODE_ROOT:?submit controller must export GATE5_CODE_ROOT}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_EXPECTED_HEAD:?submit controller must export GATE5_EXPECTED_HEAD}
EXPECTED_DRIVER_SHA=${GATE5_EXPECTED_TRAIN_DRIVER_SHA:?missing train-driver pin}
EXPECTED_NOMINAL_SHA=${GATE5_EXPECTED_NOMINAL_DRIVER_SHA:?missing nominal-driver pin}
EXPECTED_LOADER_SHA=${GATE5_EXPECTED_LOADER_SHA:?missing loader pin}
EXPECTED_PREDICATES_SHA=${GATE5_EXPECTED_PREDICATES_SHA:?missing cstat_data_only pin}

DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_replica.py
NOMINAL=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_nominal.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
PREDICATES=${CODE_ROOT}/nd-unfolding/pet/cstat_data_only.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
GATE3=${CODE_ROOT}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json
INDEX=${SLURM_ARRAY_TASK_ID:?array task ID missing}
SEED=$((50000 + INDEX))
REPLICA=$(printf 'replica_%02d' "$INDEX")
BASE=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_data_only_n50/replicas/${REPLICA}
TARGET=${BASE}/target/GATE5_REPLICA_TARGET.npy
TARGET_RECEIPT=${BASE}/target/GATE5_REPLICA_TARGET_RECEIPT.json
OUTDIR=${BASE}/training
OUTPUT=${OUTDIR}/GATE5_REPLICA_WEIGHTS.npz
TRAIN_RECEIPT=${OUTDIR}/GATE5_REPLICA_TRAINING_RECEIPT.json

die() { echo "[gate5-do-train][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "invalid code worktree $CODE_ROOT"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || die "replica driver hash drift"
[[ "$(sha_of "$NOMINAL")" == "$EXPECTED_NOMINAL_SHA" ]] || die "pinned nominal driver hash drift"
[[ "$(sha_of "$LOADER")" == "$EXPECTED_LOADER_SHA" ]] || die "loader hash drift"
[[ "$(sha_of "$PREDICATES")" == "$EXPECTED_PREDICATES_SHA" ]] || die "predicate module hash drift"
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

echo "[gate5-do-train] index=$INDEX seed=$SEED job=${SLURM_ARRAY_JOB_ID}_${INDEX} head=$EXPECTED_HEAD product=data-only-v1"
"$PYTHON_BIN" "$DRIVER" \
  --inputs "$INPUT" \
  --target-npy "$TARGET" \
  --target-receipt "$TARGET_RECEIPT" \
  --output "$OUTPUT" \
  --train-receipt "$TRAIN_RECEIPT" \
  --gate3-manifest "$GATE3" \
  --bootstrap-seed "$SEED" \
  --replica-index "$INDEX" \
  --cstat-product data-only-v1
echo "[gate5-do-train] DONE index=$INDEX seed=$SEED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
