#!/bin/bash
# Fail-closed controller and two-stage worker for authorized Gate-6 GAP 1. No retry path.
set -euo pipefail

die() { echo "[gate6-gap1][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
real_of() { readlink -f "$1"; }

CODE_ROOT=${G6_GAP1_CODE_ROOT:?mandatory G6_GAP1_CODE_ROOT missing}
EXPECTED_HEAD=${G6_GAP1_EXPECTED_HEAD:?mandatory G6_GAP1_EXPECTED_HEAD missing}
DATA_ROOT=${G6_GAP1_DATA_ROOT:?mandatory G6_GAP1_DATA_ROOT missing}
OUTPUT_ROOT=${G6_GAP1_OUTPUT_ROOT:?mandatory G6_GAP1_OUTPUT_ROOT missing}
PROPOSAL=${G6_GAP1_PROPOSAL:?mandatory G6_GAP1_PROPOSAL missing}
PROPOSAL_SHA=${G6_GAP1_PROPOSAL_SHA256:?mandatory G6_GAP1_PROPOSAL_SHA256 missing}
TF_PYTHON=${G6_GAP1_TF_PYTHON:?mandatory G6_GAP1_TF_PYTHON missing}
ROOT_PYTHON=${G6_GAP1_ROOT_PYTHON:?mandatory G6_GAP1_ROOT_PYTHON missing}
AUDIT_PYTHON=${G6_GAP1_AUDIT_PYTHON:?mandatory G6_GAP1_AUDIT_PYTHON missing}
ROOT_ENV_SCRIPT=${G6_GAP1_ROOT_ENV_SCRIPT:?mandatory G6_GAP1_ROOT_ENV_SCRIPT missing}
STAGE=${G6_GAP1_STAGE:-controller}

GUARD=${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py
REMAP=${CODE_ROOT}/nd-unfolding/pet/gate6_full_inventory_root_remap.py
EXTRACTOR=${CODE_ROOT}/nd-unfolding/pet/extract_fullevent_fps.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
SUBMITTER=${CODE_ROOT}/nd-unfolding/pet/submit_gate6_full_inventory_members.sh
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
FLUX=${DATA_ROOT}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root

[[ -d "$CODE_ROOT" && ! -L "$CODE_ROOT" ]] || die "invalid/symlink code root"
[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "code root is not a checkout"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "HEAD drift"
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "immutable code root is dirty"
[[ "$(real_of "$CODE_ROOT")" != "$(real_of "$DATA_ROOT")" ]] || die "primary/data checkout forbidden as code root"
[[ "$(real_of "$CODE_ROOT")" != "/pscratch/sd/j/josephrb/MINERvA-OmniFold" ]] \
  || die "canonical primary checkout forbidden as code root"
for file in "$PROPOSAL" "$GUARD" "$REMAP" "$EXTRACTOR" "$LOADER" "$SUBMITTER" \
            "$INPUT" "$FLUX" "$ROOT_ENV_SCRIPT"; do
  [[ -f "$file" && ! -L "$file" ]] || die "missing/non-regular/symlink supplier $file"
done
for interpreter in "$TF_PYTHON" "$ROOT_PYTHON" "$AUDIT_PYTHON"; do
  [[ -x "$interpreter" && -f "$(real_of "$interpreter")" ]] || die "invalid interpreter $interpreter"
done
[[ "$(sha_of "$PROPOSAL")" == "$PROPOSAL_SHA" ]] || die "proposal hash drift"
[[ "$(sha_of "$INPUT")" == "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625" ]] \
  || die "G2 input hash drift"
[[ "$(stat -c %s "$INPUT")" == "9897374636" ]] || die "G2 input size drift"

"$AUDIT_PYTHON" - "$PROPOSAL" "$CODE_ROOT" "$DATA_ROOT" <<'PY'
import hashlib
import json
import pathlib
import sys

import numpy as np

proposal_path, code_root, data_root = map(pathlib.Path, sys.argv[1:])
p = json.loads(proposal_path.read_text(encoding="utf-8"))

def fail(message):
    raise SystemExit("[gate6-gap1][FAIL] " + message)

if p.get("contract_id") != "GATE6-GAP1-FULL-INVENTORY-20260830":
    fail("contract identity mismatch")
if p.get("status") != "AUTHORIZED_CONDITIONAL_READY" or p.get("launchable") is not True:
    fail("proposal is not authorized/launchable")
auth = p.get("authorization", {})
if auth.get("authorized_by") != "Joseph" or auth.get("exactly_five_evaluations") is not True:
    fail("authorization identity/count drift")
if auth.get("no_retraining") is not True or auth.get("unchanged_retry_authorized") is not False:
    fail("training/retry authorization drift")
if auth.get("a100_hour_ceiling") != 5.0:
    fail("authorization A100 ceiling drift")
prohibitions = ["do_not_select_passing_subset", "do_not_construct_C_ML", "do_not_move_central",
                "do_not_start_leg_2", "do_not_retry_unchanged"]
if p.get("prohibitions_applied") != {key: True for key in prohibitions}:
    fail("prohibitions drift")
if p.get("C_ML", "unexpected") is not None or p.get("publication_result") is not False:
    fail("C_ML/publication boundary drift")
resources = p.get("resources", {})
if resources.get("gpu_array") != "1-5%5" or resources.get("allocated_a100_hours") != 5.0:
    fail("five-task A100 allocation drift")
for relative, expected in p.get("source_hashes", {}).items():
    path = code_root / relative
    if not path.is_file() or path.is_symlink():
        fail("missing/symlink source " + relative)
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        fail("source hash drift: " + relative)
members = p.get("member_artifacts", [])
if [item.get("member") for item in members] != [1, 2, 3, 4, 5]:
    fail("member inventory is not exactly 1..5")
for item in members:
    path = data_root / item["relative_path"]
    marker = pathlib.Path(str(path) + ".done")
    if not path.is_file() or path.is_symlink() or not marker.is_file() or marker.is_symlink():
        fail("missing/symlink member artifact or marker: " + str(path))
    if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
        fail("member artifact hash drift: " + str(item["member"]))
    with np.load(path, allow_pickle=True) as z:
        indices = np.asarray(z["mc_indices"])
        contract = z["inference_contract"].item()
    if indices.size != 2_000_000 or np.unique(indices).size != 2_000_000:
        fail("member training inventory drift: " + str(item["member"]))
    checkpoint = pathlib.Path(str(contract["step2_checkpoint"]))
    if not checkpoint.is_file() or checkpoint.is_symlink():
        fail("missing/symlink final checkpoint: " + str(checkpoint))
print("PASS: authorization, five members, checkpoints, source hashes, and 5 A100-hour ceiling")
PY

if [[ "$STAGE" == "controller" && "${G6_GAP1_PREFLIGHT_ONLY:-0}" == "1" ]]; then
  echo "PASS: Gate-6 GAP 1 controller preflight complete; no sbatch"
  exit 0
fi

export G6_GAP1_CODE_ROOT="$CODE_ROOT" G6_GAP1_EXPECTED_HEAD="$EXPECTED_HEAD"
export G6_GAP1_DATA_ROOT="$DATA_ROOT" G6_GAP1_OUTPUT_ROOT="$OUTPUT_ROOT"
export G6_GAP1_PROPOSAL="$PROPOSAL" G6_GAP1_PROPOSAL_SHA256="$PROPOSAL_SHA"
export G6_GAP1_TF_PYTHON="$TF_PYTHON" G6_GAP1_ROOT_PYTHON="$ROOT_PYTHON"
export G6_GAP1_AUDIT_PYTHON="$AUDIT_PYTHON" G6_GAP1_ROOT_ENV_SCRIPT="$ROOT_ENV_SCRIPT"
export MNV_REPO="$CODE_ROOT" PYTHONUNBUFFERED=1
export PYTHONPATH="${CODE_ROOT}/omnifold_nn:${CODE_ROOT}/2d-unfolding:${CODE_ROOT}/nd-unfolding:${CODE_ROOT}/nd-unfolding/pet"

check_inventory() {
  local log=$1
  grep -F "distinct checkout roots: 1" "$log" >/dev/null || die "OI-136 inventory is not one root: $log"
  grep -F "[expect-root,this-guard] $(real_of "$CODE_ROOT")" "$log" >/dev/null \
    || die "OI-136 inventory does not name only the immutable checkout: $log"
  if grep -Eq "IMPORT TREE VIOLATION|NOT expect-root|MORE THAN ONE CHECKOUT|INVENTORY EMISSION FAILED" "$log"; then
    die "OI-136 guard/inventory failure: $log"
  fi
}

if [[ "$STAGE" == "push" || "$STAGE" == "xsec" ]]; then
  MEMBER=${SLURM_ARRAY_TASK_ID:?array task ID missing}
  [[ "$MEMBER" =~ ^[1-5]$ ]] || die "member must be exactly 1..5, got $MEMBER"
  MEMBER_DIR=${DATA_ROOT}/nd-unfolding/pet/fullevent_ml_ensemble/member_${MEMBER}
  WEIGHTS=${MEMBER_DIR}/pet_fullevent_ml_member${MEMBER}_weights.npz
  OUTDIR=${OUTPUT_ROOT}/member_${MEMBER}
  PUSH=${OUTDIR}/GATE6_GAP1_FULL_PUSH.npz
  XSEC=${OUTDIR}/GATE6_GAP1_FULL_XSEC.npz
  SUMMARY=${OUTDIR}/GATE6_GAP1_FULL_XSEC.summary.json
  mkdir -p "$OUTDIR"
fi

case "$STAGE" in
  push)
    for path in "$PUSH" "$PUSH.done"; do
      [[ ! -e "$path" && ! -L "$path" ]] || die "collision/no-clobber guard: $path"
    done
    module load tensorflow/2.15.0
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$TF_PYTHON")" ]] \
      || die "TensorFlow interpreter drift"
    "$TF_PYTHON" -c 'import tensorflow as tf; import numpy; print(tf.__version__)' \
      || die "TensorFlow preflight failed"
    LOG=${OUTDIR}/GATE6_GAP1_PUSH_OI136.log
    set +e
    "$TF_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$REMAP" \
      --stage push --weights "$WEIGHTS" --inputs "$INPUT" --push-out "$PUSH" \
      --chunk 250000 --batch-size 4096 --subsample-agreement-tol 0.001 2>&1 | tee "$LOG"
    status=${PIPESTATUS[0]}
    set -e
    [[ "$status" == 0 ]] || die "member $MEMBER inference failed with status $status"
    check_inventory "$LOG"
    [[ -s "$PUSH" && -s "$PUSH.done" ]] || die "member $MEMBER push product incomplete"
    ;;
  xsec)
    [[ -s "$PUSH" && -s "$PUSH.done" && ! -L "$PUSH" && ! -L "$PUSH.done" ]] \
      || die "member $MEMBER push prerequisite incomplete"
    for path in "$XSEC" "$XSEC.done" "$SUMMARY"; do
      [[ ! -e "$path" && ! -L "$path" ]] || die "collision/no-clobber guard: $path"
    done
    set +u; source "$ROOT_ENV_SCRIPT"; set -u
    [[ "$(real_of "$(command -v python3)")" == "$(real_of "$ROOT_PYTHON")" ]] \
      || die "ROOT interpreter drift"
    "$ROOT_PYTHON" -c 'import ROOT, numpy; assert ROOT.gROOT' || die "ROOT preflight failed"
    LOG=${OUTDIR}/GATE6_GAP1_XSEC_OI136.log
    set +e
    "$ROOT_PYTHON" "$GUARD" --expect-root "$CODE_ROOT" -- "$REMAP" \
      --stage xsec --inputs "$INPUT" --push-out "$PUSH" --out "$XSEC" \
      --summary "$SUMMARY" --mcfile "$FLUX" 2>&1 | tee "$LOG"
    status=${PIPESTATUS[0]}
    set -e
    [[ "$status" == 0 ]] || die "member $MEMBER extraction failed with status $status"
    check_inventory "$LOG"
    [[ -s "$XSEC" && -s "$XSEC.done" && -s "$SUMMARY" ]] \
      || die "member $MEMBER extraction product incomplete"
    ;;
  controller)
    [[ ! -e "$OUTPUT_ROOT" && ! -L "$OUTPUT_ROOT" ]] || die "new output root occupied"
    mkdir -p "${OUTPUT_ROOT}/logs"
    PUSH_JOB=$(sbatch --parsable --job-name=g6gap1push --account=m3246 --qos=shared \
      --constraint='gpu&hbm80g' --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 \
      --mem=57472M --time=01:00:00 --array=1-5%5 \
      --output="${OUTPUT_ROOT}/logs/push_%A_%a.out" \
      --error="${OUTPUT_ROOT}/logs/push_%A_%a.err" \
      --export=ALL,G6_GAP1_STAGE=push "$SUBMITTER")
    XSEC_JOB=$(sbatch --parsable --job-name=g6gap1xsec --account=m3246 --qos=shared \
      --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=64G --time=01:00:00 \
      --array=1-5%5 --dependency="aftercorr:${PUSH_JOB}" \
      --output="${OUTPUT_ROOT}/logs/xsec_%A_%a.out" \
      --error="${OUTPUT_ROOT}/logs/xsec_%A_%a.err" \
      --export=ALL,G6_GAP1_STAGE=xsec "$SUBMITTER")
    "$AUDIT_PYTHON" - "${OUTPUT_ROOT}/GATE6_GAP1_SUBMISSION_RECEIPT.json" \
      "$EXPECTED_HEAD" "$PROPOSAL_SHA" "$PUSH_JOB" "$XSEC_JOB" <<'PY'
import datetime
import json
import os
import pathlib
import socket
import sys
import tempfile

out, head, proposal_sha, push_job, xsec_job = sys.argv[1:]
payload = {
    "schema": "gate6-gap1-full-inventory-submission-v1",
    "status": "SUBMITTED",
    "head": head,
    "proposal_sha256": proposal_sha,
    "jobs": {"gpu_inference_array": push_job, "cpu_extraction_array": xsec_job},
    "logical_evaluations": 5,
    "gpu_array": "1-5%5",
    "gpu_hours_allocated_ceiling": 5.0,
    "cpu_array": "1-5%5",
    "no_retraining": True,
    "automatic_retry": False,
    "unchanged_retry": False,
    "C_ML": None,
    "publication_result": False,
    "submitted_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "host": socket.gethostname(),
}
path = pathlib.Path(out)
fd, temporary = tempfile.mkstemp(prefix=".gap1_submit_", dir=str(path.parent))
with os.fdopen(fd, "w") as stream:
    json.dump(payload, stream, indent=2, sort_keys=True)
    stream.write("\n")
    stream.flush()
    os.fsync(stream.fileno())
os.replace(temporary, path)
print(json.dumps(payload, sort_keys=True))
PY
    ;;
  *) die "unknown G6_GAP1_STAGE=$STAGE" ;;
esac
