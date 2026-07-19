#!/usr/bin/env bash
# One canonical final-writer path for the batch/interactive Gate-2 hedge.
# Both routes share this lock and publish weights first, receipt last.
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
INPUT=${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
PRODUCER_RECEIPT=${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json
INDEPENDENT_RECEIPT=${REPO}/docs/orchestration/state/g2-gate1b-npz-validation-20260719.json
VALIDATOR=${REPO}/nd-unfolding/pet/gate2_target_runtime.py
LOADER=${REPO}/nd-unfolding/pet/fullevent_fps_dataloader.py
U2D=${REPO}/2d-unfolding/unfold_2d_omnifold_unbinned.py
FINAL_DIR=${REPO}/nd-unfolding/g2_fullevent/gate2/final
FINAL_WEIGHTS=${FINAL_DIR}/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy
FINAL_RECEIPT=${FINAL_DIR}/G2_GATE2_TARGET_RUNTIME_RECEIPT.json
LOCK=${REPO}/nd-unfolding/g2_fullevent/gate2/.gate2-final-writer.lock

EXPECTED_INPUT_SHA=fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625
EXPECTED_VALIDATOR_SHA=a8539d8300f8f21290faee3c99809d775e9ae0dd44c6756217fe1a068f7a51ee
EXPECTED_LOADER_SHA=c0521d210d9c8f592613e420f6cd7bd82523b879988739eff420779106d0fdd5
EXPECTED_U2D_SHA=8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e

ROUTE=${GATE2_EXECUTION_ROUTE:-}
RUN_ID=${GATE2_RUN_ID:-}
MAX_MC_EVENTS=${GATE2_MAX_MC_EVENTS:-200000}

die() { echo "[gate2-final][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
occupied() { [[ -e "$1" || -L "$1" ]]; }

[[ "$ROUTE" == batch || "$ROUTE" == interactive ]] || die "route must be batch|interactive"
[[ "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]] || die "invalid/missing run ID"
[[ "$MAX_MC_EVENTS" =~ ^[1-9][0-9]*$ ]] || die "invalid max-MC-events"
for path in "$INPUT" "$PRODUCER_RECEIPT" "$INDEPENDENT_RECEIPT" "$VALIDATOR" "$LOADER" "$U2D"; do
  [[ -f "$path" && ! -L "$path" ]] || die "missing/non-regular/symlink prerequisite: $path"
done
[[ "$(sha_of "$INPUT")" == "$EXPECTED_INPUT_SHA" ]] || die "frozen G2 input hash mismatch"
[[ "$(sha_of "$VALIDATOR")" == "$EXPECTED_VALIDATOR_SHA" ]] || die "validator changed after hedge submission"
[[ "$(sha_of "$LOADER")" == "$EXPECTED_LOADER_SHA" ]] || die "Gate-2 loader changed after construction PASS"
[[ "$(sha_of "$U2D")" == "$EXPECTED_U2D_SHA" ]] || die "canonical u2d changed after hedge submission"

mkdir -p "$FINAL_DIR" "$(dirname "$LOCK")"
exec 200>"$LOCK"
flock -n 200 || die "another final Gate-2 writer owns $LOCK"
occupied "$FINAL_WEIGHTS" && die "refuse occupied final weights: $FINAL_WEIGHTS"
occupied "$FINAL_RECEIPT" && die "refuse occupied final receipt: $FINAL_RECEIPT"

source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "environment python3 missing"
"$PYTHON_BIN" -c 'import numpy, sklearn' || die "runtime Python lacks NumPy/sklearn"

weights_tmp=$(mktemp "${FINAL_DIR}/.gate2-weights.${RUN_ID}.XXXXXX.npy")
receipt_tmp=$(mktemp "${FINAL_DIR}/.gate2-receipt.${RUN_ID}.XXXXXX.json")
cleanup() { rm -f -- "$weights_tmp" "$receipt_tmp"; }
trap cleanup EXIT

echo "[gate2-final] route=$ROUTE run_id=$RUN_ID host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
"$PYTHON_BIN" "$VALIDATOR" validate \
  --inputs "$INPUT" \
  --producer-receipt "$PRODUCER_RECEIPT" \
  --independent-receipt "$INDEPENDENT_RECEIPT" \
  --output "$receipt_tmp" \
  --weights-output "$weights_tmp" \
  --published-weights-path "$FINAL_WEIGHTS" \
  --execution-route "$ROUTE" \
  --run-id "$RUN_ID" \
  --slurm-job-id "${SLURM_JOB_ID:-none}" \
  --max-mc-events "$MAX_MC_EVENTS"

[[ -s "$weights_tmp" && -s "$receipt_tmp" ]] || die "validator did not produce both staged products"
"$PYTHON_BIN" - "$receipt_tmp" "$weights_tmp" "$FINAL_WEIGHTS" <<'PY' || die "staged receipt/weights mismatch"
import hashlib,json,os,sys
receipt,weights,final=sys.argv[1:4]
r=json.load(open(receipt))
assert r["status"]=="PASS"
assert r["pet_training_started"] is False
assert r["step1_feed"]["weights"]["published_path"]==final
h=hashlib.sha256()
with open(weights,"rb") as f:
    for block in iter(lambda:f.read(16*1024*1024),b""): h.update(block)
assert r["step1_feed"]["weights"]["sha256"]==h.hexdigest()
assert r["step1_feed"]["weights"]["size_bytes"]==os.path.getsize(weights)
PY

# Same-filesystem hard links provide no-clobber publication. Receipt is last.
ln "$weights_tmp" "$FINAL_WEIGHTS" || die "weights publication race"
[[ "$(sha_of "$FINAL_WEIGHTS")" == "$(sha_of "$weights_tmp")" ]] || die "published weights hash mismatch"
ln "$receipt_tmp" "$FINAL_RECEIPT" || die "receipt publication race"
rm -f -- "$weights_tmp" "$receipt_tmp"
echo "[gate2-final] PASS weights=$FINAL_WEIGHTS receipt=$FINAL_RECEIPT end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
