#!/bin/bash
# Submit the promoted 50-member full-input extraction plus an after-any family validator.
set -eo pipefail

CODE_ROOT=$(git rev-parse --show-toplevel)
DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50
ARRAY_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_replica_extract_array.sh
VALIDATE_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_extraction_family_validate.sh
DRIVER=${CODE_ROOT}/nd-unfolding/pet/extract_fullevent_replica.py
VALIDATOR=${CODE_ROOT}/nd-unfolding/pet/validate_gate5_extraction_family.py
NOMINAL_EXTRACTOR=${CODE_ROOT}/nd-unfolding/pet/extract_fullevent_fps.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
PROMOTION=${CODE_ROOT}/docs/orchestration/state/gate5-training-family-promotion-56933831.json
PROMOTED_REPORT=${CODE_ROOT}/docs/orchestration/state/gate5-training-family-promotion-evidence-56933831/GATE5_TRAINING_ARTIFACT_VALIDATION.slurm-56933831.json
EXPECTED_INPUT_SHA=fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625

die() { echo "[gate5-extract-submit][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "code worktree is dirty"
HEAD=$(git -C "$CODE_ROOT" rev-parse HEAD)
for f in "$ARRAY_SCRIPT" "$VALIDATE_SCRIPT" "$DRIVER" "$VALIDATOR" \
         "$NOMINAL_EXTRACTOR" "$LOADER" "$INPUT" "$PROMOTION" "$PROMOTED_REPORT"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
/usr/bin/python3.11 - "$PROMOTION" "$PROMOTED_REPORT" <<'PY'
import json, sys
p, a = map(lambda x: json.load(open(x)), sys.argv[1:])
assert p["promotion_verdict"] == "GATE5_TRAINING_FAMILY_PROMOTION_PASS"
assert p["validators"]["training_artifacts"]["members_passing"] == 50
assert p["C_stat"] is None
assert a["verdict"] == "GATE5_TRAINING_ARTIFACTS_PASS"
assert a["declared_inventory"] == 50
assert len(a["members"]) == 50
PY
if squeue -h -u "$USER" -n g5extract,g5xmanifest | grep -q .; then
  squeue -h -u "$USER" -n g5extract,g5xmanifest -o '%i|%j|%T|%R' >&2
  die "an existing Gate-5 extraction/manifest job is already active"
fi
for index in $(seq 0 49); do
  replica=$(printf 'replica_%02d' "$index")
  base=${ROOT}/replicas/${replica}
  for f in \
    "$base/extraction/GATE5_REPLICA_FULL_PUSH.npz" \
    "$base/extraction/GATE5_REPLICA_FULL_PUSH.npz.done" \
    "$base/extraction/GATE5_REPLICA_XSEC.npz" \
    "$base/extraction/GATE5_REPLICA_XSEC.npz.done" \
    "$base/extraction/GATE5_REPLICA_XSEC.summary.json" \
    "$base/extraction/GATE5_REPLICA_XSEC.summary.json.done" \
    "$base/extraction/GATE5_REPLICA_EXTRACTION_RECEIPT.json" \
    "$base/extraction/GATE5_REPLICA_EXTRACTION_RECEIPT.json.done"; do
    [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
  done
done
mkdir -p "${ROOT}/logs" "${ROOT}/validation"

EXPORTS="ALL,HOME=/global/homes/j/josephrb,GATE5_CODE_ROOT=$CODE_ROOT,GATE5_DATA_ROOT=$DATA_ROOT"
EXPORTS+=",GATE5_EXPECTED_HEAD=$HEAD,GATE5_EXPECTED_INPUT_SHA=$EXPECTED_INPUT_SHA"
EXPORTS+=",GATE5_EXPECTED_EXTRACT_DRIVER_SHA=$(sha_of "$DRIVER")"
EXPORTS+=",GATE5_EXPECTED_NOMINAL_EXTRACTOR_SHA=$(sha_of "$NOMINAL_EXTRACTOR")"
EXPORTS+=",GATE5_EXPECTED_LOADER_SHA=$(sha_of "$LOADER")"

ARRAY_JOB=$(sbatch --parsable --array=0-49%10 --export="$EXPORTS" "$ARRAY_SCRIPT") \
  || die "extraction array submission failed"
[[ "$ARRAY_JOB" =~ ^[0-9]+$ ]] || die "unexpected extraction array job id $ARRAY_JOB"
if ! MANIFEST_JOB=$(sbatch --parsable --dependency="afterany:${ARRAY_JOB}" \
      --export="${EXPORTS},GATE5_EXTRACTION_ARRAY_JOB=${ARRAY_JOB}" "$VALIDATE_SCRIPT"); then
  scancel "$ARRAY_JOB" || true
  die "manifest job submission failed; exact extraction array $ARRAY_JOB cancelled"
fi
[[ "$MANIFEST_JOB" =~ ^[0-9]+$ ]] || die "unexpected manifest job id $MANIFEST_JOB"
echo "GATE5_EXTRACTION_ARRAY_JOB=$ARRAY_JOB"
echo "GATE5_EXTRACTION_MANIFEST_JOB=$MANIFEST_JOB"
echo "GATE5_MANIFEST_DEPENDENCY=afterany:$ARRAY_JOB"
echo "GATE5_CODE_HEAD=$HEAD"
echo "GATE5_OUTPUT_ROOT=$ROOT"
