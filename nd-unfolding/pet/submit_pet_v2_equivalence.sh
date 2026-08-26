#!/bin/bash
# Fail-closed controller/worker for the authorized PET-v2 fixed-draw diagnostic.
# It submits one CPU target job, three dependent A100 arms, one CPU evaluator,
# and one read-only CPU validator.  It never uses srun and has no retry path.
set -euo pipefail

die() { echo "[pet-v2-submit][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
real_of() { readlink -f "$1"; }

CODE_ROOT=${PETV2_CODE_ROOT:?mandatory explicit PETV2_CODE_ROOT missing}
EXPECTED_HEAD=${PETV2_EXPECTED_HEAD:?mandatory PETV2_EXPECTED_HEAD missing}
TF_PYTHON=${PETV2_PYTHON:?mandatory explicit PETV2_PYTHON missing}
ROOT_PYTHON=${PETV2_ROOT_PYTHON:?mandatory explicit PETV2_ROOT_PYTHON missing}
ROOT_ENV_SCRIPT=${PETV2_ROOT_ENV_SCRIPT:?mandatory explicit PETV2_ROOT_ENV_SCRIPT missing}
AUDIT_PYTHON=${PETV2_AUDIT_PYTHON:?mandatory explicit PETV2_AUDIT_PYTHON missing}
INPUT=${PETV2_INPUT:?mandatory explicit PETV2_INPUT missing}
GATE3=${PETV2_GATE3_MANIFEST:?mandatory explicit PETV2_GATE3_MANIFEST missing}
GATE3_SHA=${PETV2_GATE3_SHA256:?mandatory PETV2_GATE3_SHA256 missing}
FLUX_SOURCE_DIR=${PETV2_FLUX_SOURCE_DIR:?mandatory explicit PETV2_FLUX_SOURCE_DIR missing}
OUTPUT_ROOT=${PETV2_OUTPUT_ROOT:?mandatory new PETV2_OUTPUT_ROOT missing}
PROPOSAL=${PETV2_PROPOSAL:?mandatory explicit PETV2_PROPOSAL missing}
PROPOSAL_SHA=${PETV2_PROPOSAL_SHA256:?mandatory PETV2_PROPOSAL_SHA256 missing}
AUTHORIZATION=${PETV2_AUTHORIZATION_TOKEN:?mandatory PETV2_AUTHORIZATION_TOKEN missing}
STAGE=${PETV2_STAGE:-controller}

GUARD=${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py
TARGET_DRIVER=${CODE_ROOT}/nd-unfolding/pet/materialize_pet_v2_equivalence_target.py
TRAIN_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_pet_v2_equivalence.py
EVAL_DRIVER=${CODE_ROOT}/nd-unfolding/pet/evaluate_pet_v2_equivalence.py
VALIDATE_DRIVER=${CODE_ROOT}/nd-unfolding/pet/validate_pet_v2_equivalence_result.py
SUBMIT_DRIVER=${CODE_ROOT}/nd-unfolding/pet/submit_pet_v2_equivalence.sh

[[ -d "$CODE_ROOT" && ! -L "$CODE_ROOT" ]] || die "invalid/symlink code root $CODE_ROOT"
[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "code root is not a git checkout"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "immutable code root is dirty"
PRIMARY_ROOT=$(git -C "$CODE_ROOT" worktree list --porcelain | awk 'NR==1 {print $2}')
[[ "$(real_of "$CODE_ROOT")" != "$(real_of "$PRIMARY_ROOT")" ]] \
  || die "PETV2_CODE_ROOT resolves to the primary checkout; forbidden"
for file in "$ROOT_ENV_SCRIPT" "$INPUT" "$GATE3" "$PROPOSAL" "$GUARD" "$TARGET_DRIVER" \
            "$TRAIN_DRIVER" "$EVAL_DRIVER" "$VALIDATE_DRIVER" "$SUBMIT_DRIVER"; do
  [[ -f "$file" && ! -L "$file" ]] || die "missing/non-regular/symlink supplier $file"
done
for interpreter in "$TF_PYTHON" "$ROOT_PYTHON" "$AUDIT_PYTHON"; do
  [[ -x "$interpreter" && -f "$(real_of "$interpreter")" ]] \
    || die "invalid interpreter supplier $interpreter"
done
[[ -x "$TF_PYTHON" && -x "$ROOT_PYTHON" && -x "$AUDIT_PYTHON" ]] \
  || die "a supplied interpreter is not executable"
[[ -d "$FLUX_SOURCE_DIR" && ! -L "$FLUX_SOURCE_DIR" ]] \
  || die "invalid/symlink flux source directory"
for playlist in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  flux_file=${FLUX_SOURCE_DIR}/runEventLoopMC_${playlist}.root
  [[ -f "$flux_file" && ! -L "$flux_file" ]] \
    || die "missing/non-regular/symlink flux supplier $flux_file"
done
[[ "$(sha_of "$INPUT")" == \
   "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625" ]] \
  || die "G2 input hash drift"
[[ "$(stat -c %s "$INPUT")" == "9897374636" ]] || die "G2 input size drift"
[[ "$(sha_of "$GATE3")" == "$GATE3_SHA" ]] || die "Gate-3 manifest hash drift"
[[ "$(sha_of "$PROPOSAL")" == "$PROPOSAL_SHA" ]] || die "proposal hash drift"

# Machine-check authorization, exact five operand hashes, live prohibitions, and resource ceiling.
"$AUDIT_PYTHON" - "$PROPOSAL" "$AUTHORIZATION" "$EXPECTED_HEAD" "$CODE_ROOT" <<'PY'
import hashlib, json, pathlib, sys
proposal_path, token, head, root = sys.argv[1:]
p = json.loads(pathlib.Path(proposal_path).read_text())
fail = lambda msg: (_ for _ in ()).throw(SystemExit("[pet-v2-submit][FAIL] " + msg))
if p.get("status") != "AUTHORIZED_READY" or p.get("launchable") is not True:
    fail("proposal is not AUTHORIZED_READY/launchable")
if p.get("authorization", {}).get("token") != token:
    fail("authorization token mismatch")
if p.get("authorization", {}).get("authorized_parent_head") != \
        "1f860f0c46d8f247bd81fde6a4b5dfad823d0ac0":
    fail("authorization parent-head mismatch")
required = ["do_not_select_passing_subset", "do_not_construct_C_ML",
            "do_not_move_central", "do_not_start_leg_2", "do_not_retry_unchanged"]
if p.get("governing_gate6", {}).get("prohibitions_applied") != {k: True for k in required}:
    fail("Gate-6 prohibitions drift")
ops = p.get("guarded_execution_contract", {}).get("future_required_operands", [])
if len(ops) != 5 or any(x.get("status") != "IMPLEMENTED_TESTED_HASH_BOUND" for x in ops):
    fail("five executable operands are not implemented/tested/hash-bound")
for item in ops:
    path = pathlib.Path(root) / item["path"]
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    if observed != item.get("sha256"):
        fail("operand hash drift: %s" % item["path"])
for group in (p.get("guarded_execution_contract", {}).get("required_current_sources", {}),
              p.get("guarded_execution_contract", {}).get("new_support_sources", {})):
    if not isinstance(group, dict) or not group:
        fail("required/support source hash group missing")
    for relative, expected in group.items():
        path = pathlib.Path(root) / relative
        if not path.is_file() or path.is_symlink():
            fail("required/support source missing or symlinked: %s" % relative)
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            fail("required/support source hash drift: %s" % relative)
ceiling = p.get("authorized_resource_ceiling", {})
if ceiling.get("a100_hours") != 18 or ceiling.get("cpu_node_hours") != 5:
    fail("authorized resource ceiling drift")
print("PASS: authorization, operands, prohibitions, and resource ceiling")
PY

if [[ "$STAGE" == "controller" && "${PETV2_PREFLIGHT_ONLY:-0}" == "1" ]]; then
  echo "PASS: PET-v2 controller preflight complete; PETV2_PREFLIGHT_ONLY=1, no sbatch"
  exit 0
fi

export PETV2_CODE_ROOT="$CODE_ROOT" PETV2_EXPECTED_HEAD="$EXPECTED_HEAD"
export PETV2_PYTHON="$TF_PYTHON" PETV2_ROOT_PYTHON="$ROOT_PYTHON"
export PETV2_ROOT_ENV_SCRIPT="$ROOT_ENV_SCRIPT" PETV2_AUDIT_PYTHON="$AUDIT_PYTHON"
export PETV2_INPUT="$INPUT" PETV2_GATE3_MANIFEST="$GATE3"
export PETV2_GATE3_SHA256="$GATE3_SHA" PETV2_FLUX_SOURCE_DIR="$FLUX_SOURCE_DIR"
export PETV2_OUTPUT_ROOT="$OUTPUT_ROOT" PETV2_PROPOSAL="$PROPOSAL"
export PETV2_PROPOSAL_SHA256="$PROPOSAL_SHA" PETV2_AUTHORIZATION_TOKEN="$AUTHORIZATION"
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
    # The explicit ROOT activator reaches conda hooks that legitimately inspect unset
    # variables.  Its own contract requires `set -eo pipefail` while sourcing; restore the
    # controller's nounset policy immediately afterward, before checking any supplier.
    set +u
    source "$ROOT_ENV_SCRIPT"
    set -u
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$ROOT_PYTHON")" ]] \
      || die "ROOT environment did not resolve the explicit ROOT interpreter"
    "$ROOT_PYTHON" -c 'import ROOT, numpy, sklearn; assert ROOT.gROOT' \
      || die "ROOT/NumPy/sklearn preflight failed"
    "$ROOT_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$TARGET_DRIVER" \
      --inputs "$INPUT" --gate3-manifest "$GATE3" \
      --expected-gate3-sha256 "$GATE3_SHA" --flux-source-dir "$FLUX_SOURCE_DIR" \
      --output-dir "$TARGET_DIR" --expected-head "$EXPECTED_HEAD"
    ;;
  train)
    module load tensorflow/2.15.0
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$TF_PYTHON")" ]] \
      || die "TensorFlow module did not resolve the explicit TF interpreter"
    "$TF_PYTHON" -c 'import tensorflow as tf; print(tf.__version__)' \
      || die "TensorFlow preflight failed"
    case "${SLURM_ARRAY_TASK_ID:?training requires array task ID}" in
      0) ARM=W_A ;;
      1) ARM=W_B ;;
      2) ARM=L ;;
      *) die "array task outside 0..2" ;;
    esac
    TARGET_RECEIPT_SHA=$(sha_of "$TARGET_RECEIPT")
    "$TF_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$TRAIN_DRIVER" \
      --arm "$ARM" --inputs "$INPUT" --expected-head "$EXPECTED_HEAD" \
      --target-receipt "$TARGET_RECEIPT" \
      --expected-target-receipt-sha256 "$TARGET_RECEIPT_SHA" \
      --weighted-target "$WEIGHTED_TARGET" --literal-target "$LITERAL_TARGET" \
      --literal-aggregate-target "$LITERAL_AGGREGATE" --split-manifest "$SPLIT_MANIFEST" \
      --output-dir "${OUTPUT_ROOT}/arms/${ARM}"
    ;;
  evaluate)
    module load tensorflow/2.15.0
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$TF_PYTHON")" ]] \
      || die "evaluation interpreter supplier drift"
    TARGET_RECEIPT_SHA=$(sha_of "$TARGET_RECEIPT")
    FLUX_SHA=$(sha_of "$FLUX_NPZ")
    WA_RECEIPT=${OUTPUT_ROOT}/arms/W_A/PETV2_ARM_RECEIPT.json
    WB_RECEIPT=${OUTPUT_ROOT}/arms/W_B/PETV2_ARM_RECEIPT.json
    L_RECEIPT=${OUTPUT_ROOT}/arms/L/PETV2_ARM_RECEIPT.json
    mkdir -p "$EVAL_DIR"
    "$TF_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$EVAL_DRIVER" \
      --inputs "$INPUT" --expected-head "$EXPECTED_HEAD" \
      --target-receipt "$TARGET_RECEIPT" \
      --expected-target-receipt-sha256 "$TARGET_RECEIPT_SHA" \
      --flux-npz "$FLUX_NPZ" --expected-flux-sha256 "$FLUX_SHA" \
      --w_a-receipt "$WA_RECEIPT" --expected-w_a-receipt-sha256 "$(sha_of "$WA_RECEIPT")" \
      --w_a-artifact "${OUTPUT_ROOT}/arms/W_A/PETV2_ARM_ARTIFACT.npz" \
      --w_a-full-push "${OUTPUT_ROOT}/arms/W_A/PETV2_FULL_PUSH.npy" \
      --w_b-receipt "$WB_RECEIPT" --expected-w_b-receipt-sha256 "$(sha_of "$WB_RECEIPT")" \
      --w_b-artifact "${OUTPUT_ROOT}/arms/W_B/PETV2_ARM_ARTIFACT.npz" \
      --w_b-full-push "${OUTPUT_ROOT}/arms/W_B/PETV2_FULL_PUSH.npy" \
      --l-receipt "$L_RECEIPT" --expected-l-receipt-sha256 "$(sha_of "$L_RECEIPT")" \
      --l-artifact "${OUTPUT_ROOT}/arms/L/PETV2_ARM_ARTIFACT.npz" \
      --l-full-push "${OUTPUT_ROOT}/arms/L/PETV2_FULL_PUSH.npy" \
      --output "$RESULT" --receipt "$RESULT_RECEIPT"
    ;;
  validate)
    module load tensorflow/2.15.0
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$TF_PYTHON")" ]] \
      || die "validation interpreter supplier drift"
    "$TF_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$VALIDATE_DRIVER" \
      --expected-head "$EXPECTED_HEAD" --proposal "$PROPOSAL" \
      --target-receipt "$TARGET_RECEIPT" \
      --w_a-receipt "${OUTPUT_ROOT}/arms/W_A/PETV2_ARM_RECEIPT.json" \
      --w_b-receipt "${OUTPUT_ROOT}/arms/W_B/PETV2_ARM_RECEIPT.json" \
      --l-receipt "${OUTPUT_ROOT}/arms/L/PETV2_ARM_RECEIPT.json" \
      --result "$RESULT" --result-receipt "$RESULT_RECEIPT" \
      --output "$VALIDATION_RECEIPT"
    ;;
  controller)
    [[ ! -e "$OUTPUT_ROOT" && ! -L "$OUTPUT_ROOT" ]] \
      || die "new output root is occupied: $OUTPUT_ROOT"
    mkdir -p "${OUTPUT_ROOT}/logs"
    TARGET_JOB=$(sbatch --parsable --job-name=petv2target --account=m3246 --qos=shared \
      --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G --time=02:00:00 \
      --output="${OUTPUT_ROOT}/logs/target_%j.out" \
      --error="${OUTPUT_ROOT}/logs/target_%j.err" \
      --export=ALL,PETV2_STAGE=target "$SUBMIT_DRIVER")
    TRAIN_JOB=$(sbatch --parsable --job-name=petv2train --account=m3246 --qos=shared \
      --constraint='gpu&hbm80g' --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 \
      --mem=57472M --time=06:00:00 --array=0-2%3 --dependency="afterok:${TARGET_JOB}" \
      --output="${OUTPUT_ROOT}/logs/train_%A_%a.out" \
      --error="${OUTPUT_ROOT}/logs/train_%A_%a.err" \
      --export=ALL,PETV2_STAGE=train "$SUBMIT_DRIVER")
    EVAL_JOB=$(sbatch --parsable --job-name=petv2eval --account=m3246 --qos=shared \
      --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=02:00:00 \
      --dependency="afterok:${TRAIN_JOB}" --output="${OUTPUT_ROOT}/logs/eval_%j.out" \
      --error="${OUTPUT_ROOT}/logs/eval_%j.err" \
      --export=ALL,PETV2_STAGE=evaluate "$SUBMIT_DRIVER")
    VALIDATE_JOB=$(sbatch --parsable --job-name=petv2valid --account=m3246 --qos=shared \
      --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=8G --time=00:30:00 \
      --dependency="afterok:${EVAL_JOB}" --output="${OUTPUT_ROOT}/logs/validate_%j.out" \
      --error="${OUTPUT_ROOT}/logs/validate_%j.err" \
      --export=ALL,PETV2_STAGE=validate "$SUBMIT_DRIVER")
    "$AUDIT_PYTHON" - "${OUTPUT_ROOT}/PETV2_SUBMISSION_RECEIPT.json" \
      "$EXPECTED_HEAD" "$PROPOSAL_SHA" "$TARGET_JOB" "$TRAIN_JOB" "$EVAL_JOB" \
      "$VALIDATE_JOB" <<'PY'
import datetime, json, os, pathlib, socket, sys, tempfile
out, head, proposal, target, train, evaluate, validate = sys.argv[1:]
payload = {"schema": "pet-v2-equivalence-submission-v1", "status": "SUBMITTED",
           "head": head, "proposal_sha256": proposal,
           "jobs": {"target": target, "training_array": train,
                    "evaluation": evaluate, "validation": validate},
           "submitted_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "host": socket.gethostname(), "no_retry_path": True,
           "C_stat": None, "C_ML": None}
p = pathlib.Path(out); fd, tmp = tempfile.mkstemp(prefix=".submit_", dir=str(p.parent))
with os.fdopen(fd, "w") as f:
    json.dump(payload, f, indent=2, sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
os.replace(tmp, p)
print(json.dumps(payload, sort_keys=True))
PY
    ;;
  *) die "unknown PETV2_STAGE=$STAGE" ;;
esac
