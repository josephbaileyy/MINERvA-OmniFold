#!/bin/bash
# Fail-closed controller/worker for PET-v2 changed retry 3. No automatic retry, no srun.
set -euo pipefail

die() { echo "[pet-v2-retry3-submit][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
real_of() { readlink -f "$1"; }

CODE_ROOT=${PETV2_CODE_ROOT:?mandatory PETV2_CODE_ROOT missing}
EXPECTED_HEAD=${PETV2_EXPECTED_HEAD:?mandatory PETV2_EXPECTED_HEAD missing}
TF_PYTHON=${PETV2_PYTHON:?mandatory PETV2_PYTHON missing}
ROOT_PYTHON=${PETV2_ROOT_PYTHON:?mandatory PETV2_ROOT_PYTHON missing}
ROOT_ENV_SCRIPT=${PETV2_ROOT_ENV_SCRIPT:?mandatory PETV2_ROOT_ENV_SCRIPT missing}
AUDIT_PYTHON=${PETV2_AUDIT_PYTHON:?mandatory PETV2_AUDIT_PYTHON missing}
INPUT=${PETV2_INPUT:?mandatory PETV2_INPUT missing}
GATE3=${PETV2_GATE3_MANIFEST:?mandatory PETV2_GATE3_MANIFEST missing}
GATE3_SHA=${PETV2_GATE3_SHA256:?mandatory PETV2_GATE3_SHA256 missing}
FLUX_SOURCE_DIR=${PETV2_FLUX_SOURCE_DIR:?mandatory PETV2_FLUX_SOURCE_DIR missing}
EXISTING_WEIGHTED=${PETV2_EXISTING_WEIGHTED_TARGET:?mandatory archived weighted target missing}
EXISTING_WEIGHTED_RECEIPT=${PETV2_EXISTING_WEIGHTED_RECEIPT:?mandatory archived receipt missing}
OUTPUT_ROOT=${PETV2_OUTPUT_ROOT:?mandatory new PETV2_OUTPUT_ROOT missing}
PROPOSAL=${PETV2_PROPOSAL:?mandatory PETV2_PROPOSAL missing}
PROPOSAL_SHA=${PETV2_PROPOSAL_SHA256:?mandatory PETV2_PROPOSAL_SHA256 missing}
AUTHORIZATION=${PETV2_AUTHORIZATION_TOKEN:?mandatory PETV2_AUTHORIZATION_TOKEN missing}
STAGE=${PETV2_STAGE:-controller}

GUARD=${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py
TARGET_DRIVER=${CODE_ROOT}/nd-unfolding/pet/materialize_pet_v2_equivalence_target_retry3.py
TRAIN_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_pet_v2_equivalence_retry1.py
EVAL_DRIVER=${CODE_ROOT}/nd-unfolding/pet/evaluate_pet_v2_equivalence_retry1.py
VALIDATE_DRIVER=${CODE_ROOT}/nd-unfolding/pet/validate_pet_v2_equivalence_result_retry3.py
ROOT_REMAP=${CODE_ROOT}/nd-unfolding/pet/pet_v2_equivalence_root_remap.py
TARGET_BYPASS=${CODE_ROOT}/nd-unfolding/pet/pet_v2_target_package_bypass_retry2.py
SUBMIT_DRIVER=${CODE_ROOT}/nd-unfolding/pet/submit_pet_v2_equivalence_changed_retry3.sh

[[ -d "$CODE_ROOT" && ! -L "$CODE_ROOT" ]] || die "invalid/symlink code root"
[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "code root is not a checkout"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "HEAD drift"
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "immutable code root is dirty"
PRIMARY_ROOT=$(git -C "$CODE_ROOT" worktree list --porcelain | awk 'NR==1 {print $2}')
[[ "$(real_of "$CODE_ROOT")" != "$(real_of "$PRIMARY_ROOT")" ]] || die "primary checkout forbidden"
for file in "$ROOT_ENV_SCRIPT" "$INPUT" "$GATE3" "$PROPOSAL" "$EXISTING_WEIGHTED" \
            "$EXISTING_WEIGHTED_RECEIPT" "$GUARD" "$TARGET_DRIVER" "$TRAIN_DRIVER" \
            "$EVAL_DRIVER" "$VALIDATE_DRIVER" "$ROOT_REMAP" "$TARGET_BYPASS" "$SUBMIT_DRIVER"; do
  [[ -f "$file" && ! -L "$file" ]] || die "missing/non-regular/symlink supplier $file"
done
for interpreter in "$TF_PYTHON" "$ROOT_PYTHON" "$AUDIT_PYTHON"; do
  [[ -x "$interpreter" && -f "$(real_of "$interpreter")" ]] || die "invalid interpreter $interpreter"
done
[[ -d "$FLUX_SOURCE_DIR" && ! -L "$FLUX_SOURCE_DIR" ]] || die "invalid flux source directory"
for playlist in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  flux_file=${FLUX_SOURCE_DIR}/runEventLoopMC_${playlist}.root
  [[ -f "$flux_file" && ! -L "$flux_file" ]] || die "missing flux supplier $flux_file"
done
[[ "$(sha_of "$INPUT")" == "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625" ]] || die "G2 hash drift"
[[ "$(stat -c %s "$INPUT")" == "9897374636" ]] || die "G2 size drift"
[[ "$(sha_of "$GATE3")" == "$GATE3_SHA" ]] || die "Gate-3 hash drift"
[[ "$(sha_of "$EXISTING_WEIGHTED")" == "13d46574b8f8e904aee0d544b33ce0f4fcd3fd5a119b0a2fd64071c70c650c03" ]] || die "archived target hash drift"
[[ "$(stat -c %s "$EXISTING_WEIGHTED")" == "18723004" ]] || die "archived target size drift"
[[ "$(sha_of "$EXISTING_WEIGHTED_RECEIPT")" == "ff081d44aad16971a2b812b493c78cbeef25254f497ec5533dec4698c7246fc4" ]] || die "archived receipt hash drift"
[[ "$(sha_of "$PROPOSAL")" == "$PROPOSAL_SHA" ]] || die "proposal hash drift"

"$AUDIT_PYTHON" - "$PROPOSAL" "$AUTHORIZATION" "$CODE_ROOT" <<'PY'
import hashlib, json, pathlib, sys
proposal_path, token, root = sys.argv[1:]
p = json.loads(pathlib.Path(proposal_path).read_text())
fail = lambda msg: (_ for _ in ()).throw(SystemExit("[pet-v2-retry3-submit][FAIL] " + msg))
if p.get("contract_id") != "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY3-20260826":
    fail("contract identity mismatch")
if p.get("status") != "AUTHORIZED_READY_CHANGED_RETRY" or p.get("launchable") is not True:
    fail("proposal is not authorized/launchable")
a = p.get("authorization", {})
if a.get("authorization_token") != token or a.get("authorized_by") != "Joseph":
    fail("authorization mismatch")
if a.get("changed_retries_authorized") is not True or a.get("unchanged_retry_authorized") is not False:
    fail("changed/unchanged authorization drift")
prohibitions = ["do_not_select_passing_subset", "do_not_construct_C_ML", "do_not_move_central",
                "do_not_start_leg_2", "do_not_retry_unchanged"]
if p.get("prohibitions_applied") != {key: True for key in prohibitions}:
    fail("prohibitions drift")
ops = p.get("guarded_executable_operands", {}).get("future_required_operands", [])
if len(ops) != 5 or any(item.get("status") != "IMPLEMENTED_TESTED_HASH_BOUND" for item in ops):
    fail("five executable operands are not frozen")
for item in ops:
    path = pathlib.Path(root) / item["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
        fail("operand hash drift: " + item["path"])
for group in (p["guarded_executable_operands"].get("required_current_sources", {}),
              p["guarded_executable_operands"].get("new_support_sources", {})):
    if not group:
        fail("source binding group missing")
    for relative, expected in group.items():
        path = pathlib.Path(root) / relative
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            fail("source binding drift: " + relative)
resource = p.get("resource_estimate", {})
if resource.get("authorized_total_envelope", {}).get("a100_hour_ceiling") != 18:
    fail("A100 ceiling drift")
if resource.get("authorized_total_envelope", {}).get("cpu_node_hour_ceiling") != 5:
    fail("CPU ceiling drift")
if resource.get("remaining_total_envelope", {}).get("cpu_node_hours", -1) <= 0:
    fail("CPU envelope exhausted")
print("PASS: retry-3 authorization, operands, prohibitions, archive, and resource ceiling")
PY

if [[ "$STAGE" == "controller" && "${PETV2_PREFLIGHT_ONLY:-0}" == "1" ]]; then
  echo "PASS: PET-v2 retry-3 controller preflight complete; PETV2_PREFLIGHT_ONLY=1, no sbatch"
  exit 0
fi

export PETV2_CODE_ROOT="$CODE_ROOT" PETV2_EXPECTED_HEAD="$EXPECTED_HEAD"
export PETV2_PYTHON="$TF_PYTHON" PETV2_ROOT_PYTHON="$ROOT_PYTHON"
export PETV2_ROOT_ENV_SCRIPT="$ROOT_ENV_SCRIPT" PETV2_AUDIT_PYTHON="$AUDIT_PYTHON"
export PETV2_INPUT="$INPUT" PETV2_GATE3_MANIFEST="$GATE3" PETV2_GATE3_SHA256="$GATE3_SHA"
export PETV2_FLUX_SOURCE_DIR="$FLUX_SOURCE_DIR" PETV2_OUTPUT_ROOT="$OUTPUT_ROOT"
export PETV2_PROPOSAL="$PROPOSAL" PETV2_PROPOSAL_SHA256="$PROPOSAL_SHA"
export PETV2_AUTHORIZATION_TOKEN="$AUTHORIZATION"
export PETV2_EXISTING_WEIGHTED_TARGET="$EXISTING_WEIGHTED"
export PETV2_EXISTING_WEIGHTED_RECEIPT="$EXISTING_WEIGHTED_RECEIPT"
export PYTHONHASHSEED=42 TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export PYTHONUNBUFFERED=1
export PYTHONPATH="${CODE_ROOT}/omnifold_nn:${CODE_ROOT}/2d-unfolding:${CODE_ROOT}/nd-unfolding:${CODE_ROOT}/nd-unfolding/pet"

TARGET_DIR=${OUTPUT_ROOT}/target
TARGET_RECEIPT=${TARGET_DIR}/PETV2_TARGET_RECEIPT.json
WEIGHTED_TARGET=${TARGET_DIR}/PETV2_WEIGHTED_TARGET.npy
LITERAL_TARGET=${TARGET_DIR}/PETV2_LITERAL_TARGET.npz
LITERAL_AGGREGATE=${TARGET_DIR}/PETV2_LITERAL_AGGREGATE_TARGET.npy
SPLIT_MANIFEST=${TARGET_DIR}/PETV2_SPLIT_MANIFEST.npz
FLUX_NPZ=${TARGET_DIR}/PETV2_FLUX.npz
EVAL_DIR=${OUTPUT_ROOT}/evaluation
RESULT=${EVAL_DIR}/PETV2_EQUIVALENCE_RESULT.npz
RESULT_RECEIPT=${EVAL_DIR}/PETV2_EQUIVALENCE_RESULT_RECEIPT.json
VALIDATION_RECEIPT=${EVAL_DIR}/PETV2_EQUIVALENCE_VALIDATION.json

case "$STAGE" in
  target)
    set +u; source "$ROOT_ENV_SCRIPT"; set -u
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$ROOT_PYTHON")" ]] || die "ROOT interpreter drift"
    "$ROOT_PYTHON" -c 'import ROOT, numpy, sklearn; assert ROOT.gROOT' || die "ROOT preflight failed"
    "$ROOT_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$TARGET_DRIVER" --help >/dev/null
    "$ROOT_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$TARGET_DRIVER" \
      --inputs "$INPUT" --gate3-manifest "$GATE3" --expected-gate3-sha256 "$GATE3_SHA" \
      --flux-source-dir "$FLUX_SOURCE_DIR" --output-dir "$TARGET_DIR" --expected-head "$EXPECTED_HEAD"
    ;;
  train)
    module load tensorflow/2.15.0
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$TF_PYTHON")" ]] || die "TF interpreter drift"
    case "${SLURM_ARRAY_TASK_ID:?training array task missing}" in 0) ARM=W_A;; 1) ARM=W_B;; 2) ARM=L;; *) die "task outside 0..2";; esac
    TARGET_RECEIPT_SHA=$(sha_of "$TARGET_RECEIPT")
    "$TF_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$TRAIN_DRIVER" \
      --arm "$ARM" --inputs "$INPUT" --expected-head "$EXPECTED_HEAD" \
      --target-receipt "$TARGET_RECEIPT" --expected-target-receipt-sha256 "$TARGET_RECEIPT_SHA" \
      --weighted-target "$WEIGHTED_TARGET" --literal-target "$LITERAL_TARGET" \
      --literal-aggregate-target "$LITERAL_AGGREGATE" --split-manifest "$SPLIT_MANIFEST" \
      --output-dir "${OUTPUT_ROOT}/arms/${ARM}"
    ;;
  evaluate)
    module load tensorflow/2.15.0
    TARGET_RECEIPT_SHA=$(sha_of "$TARGET_RECEIPT"); FLUX_SHA=$(sha_of "$FLUX_NPZ")
    WA_RECEIPT=${OUTPUT_ROOT}/arms/W_A/PETV2_ARM_RECEIPT.json
    WB_RECEIPT=${OUTPUT_ROOT}/arms/W_B/PETV2_ARM_RECEIPT.json
    L_RECEIPT=${OUTPUT_ROOT}/arms/L/PETV2_ARM_RECEIPT.json
    mkdir -p "$EVAL_DIR"
    "$TF_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$EVAL_DRIVER" \
      --inputs "$INPUT" --expected-head "$EXPECTED_HEAD" --target-receipt "$TARGET_RECEIPT" \
      --expected-target-receipt-sha256 "$TARGET_RECEIPT_SHA" --flux-npz "$FLUX_NPZ" --expected-flux-sha256 "$FLUX_SHA" \
      --w_a-receipt "$WA_RECEIPT" --expected-w_a-receipt-sha256 "$(sha_of "$WA_RECEIPT")" --w_a-artifact "${OUTPUT_ROOT}/arms/W_A/PETV2_ARM_ARTIFACT.npz" --w_a-full-push "${OUTPUT_ROOT}/arms/W_A/PETV2_FULL_PUSH.npy" \
      --w_b-receipt "$WB_RECEIPT" --expected-w_b-receipt-sha256 "$(sha_of "$WB_RECEIPT")" --w_b-artifact "${OUTPUT_ROOT}/arms/W_B/PETV2_ARM_ARTIFACT.npz" --w_b-full-push "${OUTPUT_ROOT}/arms/W_B/PETV2_FULL_PUSH.npy" \
      --l-receipt "$L_RECEIPT" --expected-l-receipt-sha256 "$(sha_of "$L_RECEIPT")" --l-artifact "${OUTPUT_ROOT}/arms/L/PETV2_ARM_ARTIFACT.npz" --l-full-push "${OUTPUT_ROOT}/arms/L/PETV2_FULL_PUSH.npy" \
      --output "$RESULT" --receipt "$RESULT_RECEIPT"
    ;;
  validate)
    module load tensorflow/2.15.0
    "$TF_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$VALIDATE_DRIVER" \
      --expected-head "$EXPECTED_HEAD" --proposal "$PROPOSAL" --target-receipt "$TARGET_RECEIPT" \
      --w_a-receipt "${OUTPUT_ROOT}/arms/W_A/PETV2_ARM_RECEIPT.json" \
      --w_b-receipt "${OUTPUT_ROOT}/arms/W_B/PETV2_ARM_RECEIPT.json" \
      --l-receipt "${OUTPUT_ROOT}/arms/L/PETV2_ARM_RECEIPT.json" \
      --result "$RESULT" --result-receipt "$RESULT_RECEIPT" --output "$VALIDATION_RECEIPT"
    ;;
  controller)
    [[ ! -e "$OUTPUT_ROOT" && ! -L "$OUTPUT_ROOT" ]] || die "new output root occupied"
    mkdir -p "${OUTPUT_ROOT}/logs"
    TARGET_JOB=$(sbatch --parsable --job-name=petv2r3target --account=m3246 --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=02:00:00 --output="${OUTPUT_ROOT}/logs/target_%j.out" --error="${OUTPUT_ROOT}/logs/target_%j.err" --export=ALL,PETV2_STAGE=target "$SUBMIT_DRIVER")
    TRAIN_JOB=$(sbatch --parsable --job-name=petv2r3train --account=m3246 --qos=shared --constraint='gpu&hbm80g' --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 --mem=57472M --time=06:00:00 --array=0-2%3 --dependency="afterok:${TARGET_JOB}" --output="${OUTPUT_ROOT}/logs/train_%A_%a.out" --error="${OUTPUT_ROOT}/logs/train_%A_%a.err" --export=ALL,PETV2_STAGE=train "$SUBMIT_DRIVER")
    EVAL_JOB=$(sbatch --parsable --job-name=petv2r3eval --account=m3246 --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=02:00:00 --dependency="afterok:${TRAIN_JOB}" --output="${OUTPUT_ROOT}/logs/eval_%j.out" --error="${OUTPUT_ROOT}/logs/eval_%j.err" --export=ALL,PETV2_STAGE=evaluate "$SUBMIT_DRIVER")
    VALIDATE_JOB=$(sbatch --parsable --job-name=petv2r3valid --account=m3246 --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=8G --time=00:30:00 --dependency="afterok:${EVAL_JOB}" --output="${OUTPUT_ROOT}/logs/validate_%j.out" --error="${OUTPUT_ROOT}/logs/validate_%j.err" --export=ALL,PETV2_STAGE=validate "$SUBMIT_DRIVER")
    "$AUDIT_PYTHON" - "${OUTPUT_ROOT}/PETV2_SUBMISSION_RECEIPT.json" "$EXPECTED_HEAD" "$PROPOSAL_SHA" "$TARGET_JOB" "$TRAIN_JOB" "$EVAL_JOB" "$VALIDATE_JOB" <<'PY'
import datetime, json, os, pathlib, socket, sys, tempfile
out, head, proposal, target, train, evaluate, validate = sys.argv[1:]
payload = {"schema":"pet-v2-equivalence-changed-retry3-submission-v1","status":"SUBMITTED","head":head,"proposal_sha256":proposal,"jobs":{"target":target,"training_array":train,"evaluation":evaluate,"validation":validate},"submitted_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"host":socket.gethostname(),"changed_retry_number":3,"prior_target_job":"57629029","automatic_retry":False,"unchanged_retry":False,"C_stat":None,"C_ML":None}
p=pathlib.Path(out); fd,tmp=tempfile.mkstemp(prefix=".submit_",dir=str(p.parent))
with os.fdopen(fd,"w") as stream:
    json.dump(payload,stream,indent=2,sort_keys=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
os.replace(tmp,p); print(json.dumps(payload,sort_keys=True))
PY
    ;;
  *) die "unknown PETV2_STAGE=$STAGE";;
esac
