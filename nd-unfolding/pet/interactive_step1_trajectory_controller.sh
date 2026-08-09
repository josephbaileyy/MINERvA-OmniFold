#!/bin/bash
# Collision-safe controller for a detached interactive-A100 hedge of the Step-1 trajectory.
#
# This script is invoked only AFTER salloc grants an interactive GPU allocation. It never waits for
# that allocation itself. The still-pending batch remains the owner until this controller proves the
# allocation, rechecks batch/output state, cancels that exact pending job, and confirms cancellation.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
OUTDIR="${PET}/fullevent_nominal"
STATE_DIR="${REPO}/docs/orchestration/state"

BATCH_JOB="${1:?usage: interactive_step1_trajectory_controller.sh BATCH_JOB_ID}"
[[ "$BATCH_JOB" =~ ^[0-9]+$ ]] || { echo "[ihedge] non-numeric batch job" >&2; exit 2; }
ALLOC_JOB="${SLURM_JOB_ID:?controller must run inside a granted salloc}"
[[ "$ALLOC_JOB" =~ ^[0-9]+$ ]] || { echo "[ihedge] non-numeric allocation job" >&2; exit 3; }

ROUTE="${STATE_DIR}/step1-traj-ihedge-${BATCH_JOB}.route.json"
TERMINAL="${STATE_DIR}/step1-traj-ihedge-${BATCH_JOB}.terminal.json"
LOCK="${OUTDIR}/.step1-trajectory-writer.lock"
BATCH_OUT="${OUTDIR}/STEP1_TRAJECTORY.slurm-${BATCH_JOB}.json"
BATCH_RUNLOG="${OUTDIR}/logs/step1_traj_${BATCH_JOB}.log"
INTERACTIVE_OUT="${OUTDIR}/STEP1_TRAJECTORY.slurm-${ALLOC_JOB}.json"
INTERACTIVE_RUNLOG="${OUTDIR}/logs/step1_traj_${ALLOC_JOB}.log"
CONTROLLER_LOG="${OUTDIR}/logs/step1_ihedge_${ALLOC_JOB}.controller.log"

mkdir -p "${OUTDIR}/logs" "$STATE_DIR"
[[ ! -e "$TERMINAL" ]] || { echo "[ihedge] terminal sentinel already exists: $TERMINAL" >&2; exit 4; }

write_record() {
    local path="$1" phase="$2" action="$3" batch_state="$4" rc="$5" terminal="$6" note="$7"
    /usr/bin/python3.11 - "$path" "$phase" "$action" "$batch_state" "$rc" "$terminal" "$note" \
      "$BATCH_JOB" "$ALLOC_JOB" "$INTERACTIVE_OUT" "$INTERACTIVE_RUNLOG" <<'PY'
import datetime as dt
import json
import os
import sys
from pathlib import Path

(path, phase, action, batch_state, rc, terminal, note, batch_job, alloc_job,
 output, runlog) = sys.argv[1:]
payload = {
    "schema": "step1-trajectory-interactive-hedge-v1",
    "observed_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    "phase": phase,
    "action": action,
    "batch_job_id": batch_job,
    "interactive_allocation_job_id": alloc_job,
    "batch_state_at_decision": batch_state,
    "return_code": int(rc),
    "terminal": terminal == "true",
    "output": output,
    "run_log": runlog,
    "note": note,
}
target = Path(path)
temporary = target.with_name(f".{target.name}.tmp-{os.getpid()}")
with temporary.open("w") as fh:
    json.dump(payload, fh, indent=2)
    fh.write("\n")
    fh.flush()
    os.fsync(fh.fileno())
os.replace(temporary, target)
PY
}

fail_terminal() {
    local rc="$1" phase="$2" note="$3" batch_state="${4:-unknown}"
    write_record "$TERMINAL" "$phase" "FAIL_CLOSED" "$batch_state" "$rc" true "$note"
    exit "$rc"
}

# Serialize hedge controllers. The original batch does not use this lock, so batch state is still
# rechecked immediately before cancellation; this lock prevents two hedge controllers racing.
exec 9>"$LOCK"
flock -n 9 || fail_terminal 10 preflight "another Step-1 hedge controller holds the writer lock"

alloc_info="$(scontrol show job -o "$ALLOC_JOB")"
if [[ "$alloc_info" != *"JobState=RUNNING"* || "$alloc_info" != *"Features=gpu"* ||
      "$alloc_info" != *"gres/gpu=1"* ]]; then
    fail_terminal 11 preflight "allocation is not a running one-GPU allocation"
fi

# The start-deadline is no longer needed once this controller exists: allocation is proven.
/usr/bin/python3.11 "${REPO}/orchestration/wakerctl.py" watch-disarm \
  --id "step1-ihedge-start-deadline-${BATCH_JOB}" >/dev/null 2>&1 || true

batch_state="$(squeue -h -j "$BATCH_JOB" -o '%T')"
if [[ "$batch_state" != "PENDING" ]]; then
    write_record "$TERMINAL" route "RETAIN_BATCH" "${batch_state:-not-in-queue}" 0 true \
      "batch was no longer prestart-pending when interactive allocation began; no cancellation and no interactive writer"
    exit 0
fi

if [[ -e "$BATCH_OUT" || -e "$BATCH_RUNLOG" ]]; then
    write_record "$TERMINAL" route "RETAIN_BATCH" "$batch_state" 0 true \
      "a batch-owned output path exists; fail closed to the batch writer"
    exit 0
fi
if [[ -e "$INTERACTIVE_OUT" || -e "$INTERACTIVE_RUNLOG" ]]; then
    fail_terminal 12 preflight "interactive allocation namespace already contains output" "$batch_state"
fi

# Cancellation is authorized only after all checks above and only for this exact PENDING job.
set +e
scancel "$BATCH_JOB"
cancel_rc=$?
set -e
[[ "$cancel_rc" -eq 0 ]] || fail_terminal 13 cancel "scancel failed" "$batch_state"

post_queue="$(squeue -h -j "$BATCH_JOB" -o '%T')"
post_acct="$(sacct -X -j "$BATCH_JOB" -n -P -o State,ExitCode)"
if [[ -n "$post_queue" || "$post_acct" != CANCELLED* ]]; then
    fail_terminal 14 cancel "cancellation not confirmed; interactive writer not started" \
      "queue=${post_queue:-empty};accounting=${post_acct:-empty}"
fi

# The old terminal watch would wake on our deliberate cancellation; the controller sentinel now
# owns continuation and was armed before salloc was launched.
/usr/bin/python3.11 "${REPO}/orchestration/wakerctl.py" watch-disarm \
  --id "step1-traj-${BATCH_JOB}" >/dev/null 2>&1 || true
write_record "$ROUTE" running "CANCEL_BATCH_RUN_INTERACTIVE" CANCELLED 0 false \
  "interactive GPU allocation proven; exact pending batch cancellation confirmed before output"

set +e
srun --overlap --exact -n 1 -c 32 --gpus=1 \
  bash -lc "cd '${REPO}' && bash 'nd-unfolding/pet/sbatch_step1_trajectory.sh'" \
  >"$CONTROLLER_LOG" 2>&1
run_rc=$?
set -e

if [[ "$run_rc" -ne 0 ]]; then
    fail_terminal "$run_rc" compute "interactive Step-1 trajectory failed; see controller and run logs" CANCELLED
fi
[[ -s "$INTERACTIVE_OUT" && -s "$INTERACTIVE_RUNLOG" ]] || \
    fail_terminal 15 validate "interactive command returned zero without both output and run log" CANCELLED

/usr/bin/python3.11 - "$INTERACTIVE_OUT" <<'PY'
import json
import sys
with open(sys.argv[1]) as fh:
    payload = json.load(fh)
assert payload.get("schema") == "pet-fullevent-step1-trajectory-v1"
assert payload.get("verdict") in {
    "BROKEN_AT_ITER0", "CORRECT_AT_ITER0_DEGRADES_LATER", "UNDER_ACHIEVES_AT_ITER0_SAME_SIGN"
}
assert payload.get("reproduction_gate")
PY

write_record "$TERMINAL" complete "INTERACTIVE_COMPLETE" CANCELLED 0 true \
  "batch cancellation preceded all output; schema, verdict and reproduction gate are present"
echo "[ihedge] complete allocation=${ALLOC_JOB} output=${INTERACTIVE_OUT}"
