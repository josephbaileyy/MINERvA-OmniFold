#!/bin/bash
#SBATCH --job-name=g5targ
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=0-49%10
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/target_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/target_%A_%a.err
set -eo pipefail

# Stage 1 of the predeclared Gate-5 two-stage architecture.  This array has no GPU and builds one
# learned Stay-Positive target per coherent bootstrap seed.  The matching training array uses
# Slurm aftercorr, so each GPU task becomes eligible only after this exact task succeeds.
CODE_ROOT=${GATE5_CODE_ROOT:?submit controller must export GATE5_CODE_ROOT}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_EXPECTED_HEAD:?submit controller must export GATE5_EXPECTED_HEAD}
EXPECTED_DRIVER_SHA=${GATE5_EXPECTED_TARGET_DRIVER_SHA:?missing target-driver pin}
EXPECTED_LOADER_SHA=${GATE5_EXPECTED_LOADER_SHA:?missing loader pin}
EXPECTED_INPUT_SHA=${GATE5_EXPECTED_INPUT_SHA:?missing input pin}

DRIVER=${CODE_ROOT}/nd-unfolding/pet/build_fullevent_replica_target.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
GATE3=${CODE_ROOT}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json
INDEX=${SLURM_ARRAY_TASK_ID:?array task ID missing}
SEED=$((50000 + INDEX))
REPLICA=$(printf 'replica_%02d' "$INDEX")
OUTDIR=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50/replicas/${REPLICA}/target
TARGET=${OUTDIR}/GATE5_REPLICA_TARGET.npy
RECEIPT=${OUTDIR}/GATE5_REPLICA_TARGET_RECEIPT.json

die() { echo "[gate5-target][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "invalid code worktree $CODE_ROOT"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || die "target driver hash drift"
[[ "$(sha_of "$LOADER")" == "$EXPECTED_LOADER_SHA" ]] || die "loader hash drift"
for f in "$INPUT" "$GATE3"; do [[ -s "$f" && ! -L "$f" ]] || die "missing/symlink $f"; done
for f in "$TARGET" "$TARGET.done" "$RECEIPT" "$RECEIPT.done"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
done
mkdir -p "$OUTDIR"

source "${DATA_ROOT}/setup_salloc_env.sh"
export PYTHONPATH="${CODE_ROOT}/omnifold_nn:${CODE_ROOT}/2d-unfolding:${CODE_ROOT}/nd-unfolding:${CODE_ROOT}/nd-unfolding/pet:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "ROOT environment python3 missing"
"$PYTHON_BIN" -c 'import numpy, sklearn' || die "ROOT target environment missing NumPy/sklearn"

echo "[gate5-target] index=$INDEX seed=$SEED job=${SLURM_ARRAY_JOB_ID}_${INDEX} head=$EXPECTED_HEAD"
"$PYTHON_BIN" "$DRIVER" \
  --inputs "$INPUT" \
  --output "$TARGET" \
  --receipt "$RECEIPT" \
  --bootstrap-seed "$SEED" \
  --replica-index "$INDEX" \
  --expected-input-sha256 "$EXPECTED_INPUT_SHA" \
  --gate3-manifest "$GATE3"
echo "[gate5-target] DONE index=$INDEX seed=$SEED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
