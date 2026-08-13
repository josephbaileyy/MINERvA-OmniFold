#!/bin/bash
# Submit the predeclared two-stage N=50 campaign exactly once.
set -eo pipefail

CODE_ROOT=$(git rev-parse --show-toplevel)
DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
TARGET_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_replica_target_array.sh
TRAIN_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_replica_train_array.sh
TARGET_DRIVER=${CODE_ROOT}/nd-unfolding/pet/build_fullevent_replica_target.py
TRAIN_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_replica.py
NOMINAL_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_nominal.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
EXPECTED_INPUT_SHA=fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625
OUTPUT_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50

die() { echo "[gate5-submit][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "code worktree is dirty"
HEAD=$(git -C "$CODE_ROOT" rev-parse HEAD)
for f in "$TARGET_SCRIPT" "$TRAIN_SCRIPT" "$TARGET_DRIVER" "$TRAIN_DRIVER" \
         "$NOMINAL_DRIVER" "$LOADER" "$INPUT"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
[[ "$(sha_of "$INPUT")" == "$EXPECTED_INPUT_SHA" ]] || die "frozen G2 source hash mismatch"
if squeue -h -u "$USER" -n g5targ,g5train | grep -q .; then
  squeue -h -u "$USER" -n g5targ,g5train -o '%i|%j|%T|%R' >&2
  die "an existing Gate-5 array is already active"
fi
for index in $(seq 0 49); do
  replica=$(printf 'replica_%02d' "$index")
  base=${OUTPUT_ROOT}/replicas/${replica}
  for f in \
    "$base/target/GATE5_REPLICA_TARGET.npy" \
    "$base/target/GATE5_REPLICA_TARGET.npy.done" \
    "$base/target/GATE5_REPLICA_TARGET_RECEIPT.json" \
    "$base/target/GATE5_REPLICA_TARGET_RECEIPT.json.done" \
    "$base/training/GATE5_REPLICA_WEIGHTS.npz" \
    "$base/training/GATE5_REPLICA_WEIGHTS.npz.done" \
    "$base/training/GATE5_REPLICA_TRAINING_RECEIPT.json" \
    "$base/training/GATE5_REPLICA_TRAINING_RECEIPT.json.done"; do
    [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
  done
done
mkdir -p "$OUTPUT_ROOT/logs"

EXPORTS="ALL,HOME=/global/homes/j/josephrb,GATE5_CODE_ROOT=$CODE_ROOT,GATE5_DATA_ROOT=$DATA_ROOT"
EXPORTS+=",GATE5_EXPECTED_HEAD=$HEAD,GATE5_EXPECTED_INPUT_SHA=$EXPECTED_INPUT_SHA"
EXPORTS+=",GATE5_EXPECTED_TARGET_DRIVER_SHA=$(sha_of "$TARGET_DRIVER")"
EXPORTS+=",GATE5_EXPECTED_TRAIN_DRIVER_SHA=$(sha_of "$TRAIN_DRIVER")"
EXPORTS+=",GATE5_EXPECTED_NOMINAL_DRIVER_SHA=$(sha_of "$NOMINAL_DRIVER")"
EXPORTS+=",GATE5_EXPECTED_LOADER_SHA=$(sha_of "$LOADER")"

TARGET_JOB=$(sbatch --parsable --array=0-49%10 --export="$EXPORTS" "$TARGET_SCRIPT") \
  || die "target-array submission failed"
[[ "$TARGET_JOB" =~ ^[0-9]+$ ]] || die "unexpected target job id $TARGET_JOB"
if ! TRAIN_JOB=$(sbatch --parsable --array=0-49%10 --dependency="aftercorr:${TARGET_JOB}" \
      --export="$EXPORTS" "$TRAIN_SCRIPT"); then
  scancel "$TARGET_JOB" || true
  die "training-array submission failed; exact target array $TARGET_JOB cancelled"
fi
[[ "$TRAIN_JOB" =~ ^[0-9]+$ ]] || die "unexpected training job id $TRAIN_JOB"
echo "GATE5_TARGET_JOB=$TARGET_JOB"
echo "GATE5_TRAIN_JOB=$TRAIN_JOB"
echo "GATE5_DEPENDENCY=aftercorr:$TARGET_JOB"
echo "GATE5_CODE_HEAD=$HEAD"
echo "GATE5_OUTPUT_ROOT=$OUTPUT_ROOT"
