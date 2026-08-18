#!/bin/bash
# Submit the C_stat^data N=50 campaign exactly once. Two stages, aftercorr-gated, disjoint root.
#
# WHY A NEW CONTROLLER RATHER THAN A FLAG ON submit_gate5_replica_n50.sh: that controller is not
# pinned, but both ARRAY launchers it submits are, and this one submits the new pair. Adding a name
# satisfies CLAUDE.md's rename/delete prohibition (lane C, BEN-420).
#
# *** THE TWO CONTROLLERS AND THE TWO ARRAY PAIRS MUST NEVER LATER BE UNIFIED. *** `sbatch_*.sh` and
# `submit_*.sh` names are load-bearing provenance in RUN_LOGs, ledgers and receipt JSONs.
#
# WHAT THIS PRODUCT IS, so a reader does not have to reconstruct it: the data stream alone is
# resampled, so the published sigma_stat is not dominated by MC statistics and is comparable to
# MINERvA's own and to T2K/MicroBooNE/NOvA, and profileable as a nuisance term in a global fit. The
# motivation is DEFINITIONAL rather than magnitude-based -- reducible-by-more-MC versus
# reducible-by-more-data is a category distinction at any ratio. THE THREE-STREAM FAMILY IS NOT
# SUPERSEDED, NOT DISCARDED AND NOT RE-VERDICTED (lane C, BEN-404).
set -eo pipefail

CODE_ROOT=$(git rev-parse --show-toplevel)
DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
TARGET_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_data_only_target_array.sh
TRAIN_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_data_only_train_array.sh
TARGET_DRIVER=${CODE_ROOT}/nd-unfolding/pet/build_fullevent_replica_target.py
TRAIN_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_replica.py
NOMINAL_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_nominal.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
PREDICATES=${CODE_ROOT}/nd-unfolding/pet/cstat_data_only.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
EXPECTED_INPUT_SHA=fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625
OUTPUT_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_data_only_n50
THREE_STREAM_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50

die() { echo "[gate5-do-submit][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "code worktree is dirty"
HEAD=$(git -C "$CODE_ROOT" rev-parse HEAD)
for f in "$TARGET_SCRIPT" "$TRAIN_SCRIPT" "$TARGET_DRIVER" "$TRAIN_DRIVER" \
         "$NOMINAL_DRIVER" "$LOADER" "$PREDICATES" "$INPUT"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
[[ "$(sha_of "$INPUT")" == "$EXPECTED_INPUT_SHA" ]] || die "frozen G2 source hash mismatch"

# L1 -- THE ROOTS MUST BE DISJOINT, ASSERTED. If this ever resolved to the three-stream root the
# submission would overwrite or collide with the archived 50, which is the one outcome no guard
# downstream can undo.
[[ "$OUTPUT_ROOT" != "$THREE_STREAM_ROOT" ]] || die "L1 output root is the three-stream root"
case "$OUTPUT_ROOT" in *fullevent_cstat_data_only_n50) ;; *) die "L1 unexpected output root" ;; esac

# Both name sets are checked, because a live three-stream array shares the cluster and the input.
if squeue -h -u "$USER" -n g5dotarg,g5dotrain | grep -q .; then
  squeue -h -u "$USER" -n g5dotarg,g5dotrain -o '%i|%j|%T|%R' >&2
  die "an existing C_stat^data array is already active"
fi
if squeue -h -u "$USER" -n g5targ,g5train | grep -q .; then
  squeue -h -u "$USER" -n g5targ,g5train -o '%i|%j|%T|%R' >&2
  die "a three-stream Gate-5 array is active; refusing to interleave two families on one input"
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
# The predicate module is pinned at submit like the drivers: T1-T5 and L2 live in it, so a change
# there changes what "data-only" MEANS, and a family built against a different set is a different
# product wearing the same name.
EXPORTS+=",GATE5_EXPECTED_PREDICATES_SHA=$(sha_of "$PREDICATES")"

TARGET_JOB=$(sbatch --parsable --array=0-49%10 --export="$EXPORTS" "$TARGET_SCRIPT") \
  || die "target-array submission failed"
[[ "$TARGET_JOB" =~ ^[0-9]+$ ]] || die "unexpected target job id $TARGET_JOB"
if ! TRAIN_JOB=$(sbatch --parsable --array=0-49%10 --dependency="aftercorr:${TARGET_JOB}" \
      --export="$EXPORTS" "$TRAIN_SCRIPT"); then
  scancel "$TARGET_JOB" || true
  die "training-array submission failed; exact target array $TARGET_JOB cancelled"
fi
[[ "$TRAIN_JOB" =~ ^[0-9]+$ ]] || die "unexpected training job id $TRAIN_JOB"
echo "GATE5_DATAONLY_TARGET_JOB=$TARGET_JOB"
echo "GATE5_DATAONLY_TRAIN_JOB=$TRAIN_JOB"
echo "GATE5_DATAONLY_DEPENDENCY=aftercorr:$TARGET_JOB"
echo "GATE5_DATAONLY_CODE_HEAD=$HEAD"
echo "GATE5_DATAONLY_OUTPUT_ROOT=$OUTPUT_ROOT"
echo "GATE5_DATAONLY_PRODUCT=data-only-v1"
