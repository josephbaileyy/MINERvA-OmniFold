#!/bin/bash
#SBATCH --job-name=g5xmanifest
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/extraction_family_validate_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/extraction_family_validate_%j.err
set -eo pipefail

CODE_ROOT=${GATE5_CODE_ROOT:?submit controller must export GATE5_CODE_ROOT}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_EXPECTED_HEAD:?missing immutable code HEAD}
EXPECTED_INPUT_SHA=${GATE5_EXPECTED_INPUT_SHA:?missing promoted input SHA}
EXPECTED_DRIVER_SHA=${GATE5_EXPECTED_EXTRACT_DRIVER_SHA:?missing replica extractor pin}
EXPECTED_NOMINAL_EXTRACTOR_SHA=${GATE5_EXPECTED_NOMINAL_EXTRACTOR_SHA:?missing nominal extractor pin}
EXPECTED_LOADER_SHA=${GATE5_EXPECTED_LOADER_SHA:?missing loader pin}
SOURCE_ARRAY=${GATE5_EXTRACTION_ARRAY_JOB:?missing extraction array job ID}

VALIDATOR=${CODE_ROOT}/nd-unfolding/pet/validate_gate5_extraction_family.py
ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50
PROMOTED=${CODE_ROOT}/docs/orchestration/state/gate5-training-family-promotion-evidence-56933831/GATE5_TRAINING_ARTIFACT_VALIDATION.slurm-56933831.json
JOB=${SLURM_JOB_ID:?job ID missing}
OUT=${ROOT}/validation/GATE5_EXTRACTION_FAMILY_MANIFEST.slurm-${JOB}.json

die() { echo "[gate5-extract-validate][FAIL] $*" >&2; exit "${2:-1}"; }
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "immutable code worktree is dirty"
for f in "$VALIDATOR" "$PROMOTED"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
for f in "$OUT" "$OUT.done"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
done
mkdir -p "${ROOT}/validation"
export PYTHONUNBUFFERED=1
source "${DATA_ROOT}/setup_salloc_env.sh"
ROOT628_PREFIX=${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}
PYTHON_BIN=${ROOT628_PREFIX}/bin/python3
[[ -x "$PYTHON_BIN" ]] || die "analysis python is unavailable at $PYTHON_BIN"
"$PYTHON_BIN" -c 'import numpy; print(numpy.__version__)' || die "numpy import preflight failed"
echo "[gate5-extract-validate] job=$JOB source_array=$SOURCE_ARRAY head=$EXPECTED_HEAD"
"$PYTHON_BIN" -u "$VALIDATOR" \
  --root "$ROOT" \
  --promoted-training-report "$PROMOTED" \
  --source-array-job "$SOURCE_ARRAY" \
  --expected-head "$EXPECTED_HEAD" \
  --expected-inputs-sha "$EXPECTED_INPUT_SHA" \
  --expected-driver-sha "$EXPECTED_DRIVER_SHA" \
  --expected-nominal-extractor-sha "$EXPECTED_NOMINAL_EXTRACTOR_SHA" \
  --expected-loader-sha "$EXPECTED_LOADER_SHA" \
  --out "$OUT"
echo "[gate5-extract-validate] DONE job=$JOB $(date -u +%Y-%m-%dT%H:%M:%SZ)"
