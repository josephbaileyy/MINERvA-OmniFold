#!/usr/bin/env bash
set -euo pipefail

repo=${WAKE_REPO:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
state_dir=${WAKE_STATE_DIR:-${repo}/docs/orchestration/state}
job_id=${WAKE_JOB_ID:-56106974}
task_spec=${WAKE_TASK_SPEC:-1-12}
thread_id=${WAKE_THREAD_ID:-019f749a-857b-7790-8cec-bc36b22908be}
run_id=${WAKE_RUN_ID:-g2-array-${job_id}}
poll_seconds=${WAKE_POLL_SECONDS:-60}
max_unreliable=${WAKE_MAX_UNRELIABLE:-10}
status_bin=${WAKE_STATUS_BIN:-${repo}/docs/orchestration/slurm_array_status.py}
python_bin=${WAKE_PYTHON_BIN:-/usr/bin/python3.11}
codex_bin=${CODEX_BIN:-$(command -v codex 2>/dev/null || true)}

event=${state_dir}/${run_id}-wakeup.json
resume_log=${state_dir}/${run_id}-resume.log
invoked=${state_dir}/${run_id}-resume.invoked
completed=${state_dir}/${run_id}-resume.done
lock=${state_dir}/${run_id}-wake.lock

fail() { printf '[array-wake][FAIL] %s\n' "$*" >&2; exit 126; }
path_occupied() { [[ -e "$1" || -L "$1" ]]; }

preflight() {
  [[ "$job_id" =~ ^[0-9]+$ ]] || fail "invalid job id: ${job_id}"
  [[ "$task_spec" =~ ^[0-9,-]+$ ]] || fail "invalid task spec: ${task_spec}"
  [[ "$thread_id" =~ ^[0-9a-fA-F-]{36}$ ]] || fail "invalid thread id: ${thread_id}"
  [[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]] || fail "invalid poll interval: ${poll_seconds}"
  [[ "$max_unreliable" =~ ^[1-9][0-9]*$ ]] || fail "invalid unreliable limit: ${max_unreliable}"
  [[ "$status_bin" = /* && -r "$status_bin" ]] || fail "status classifier missing/not readable: ${status_bin}"
  [[ "$python_bin" = /* && -x "$python_bin" ]] || fail "Python missing/not absolute/executable: ${python_bin}"
  "$python_bin" -c 'import pathlib,sys; compile(pathlib.Path(sys.argv[1]).read_text(), sys.argv[1], "exec")' "$status_bin" \
    || fail "status classifier is not parseable by ${python_bin}: ${status_bin}"
  [[ -n "$codex_bin" && "$codex_bin" = /* && -x "$codex_bin" ]] || fail "codex missing/not absolute/executable: ${codex_bin:-missing}"
  command -v flock >/dev/null || fail "flock not found"
  command -v squeue >/dev/null || fail "squeue not found"
  command -v sacct >/dev/null || fail "sacct not found"
  mkdir -p "$state_dir"
}

run_status() {
  "$python_bin" "$status_bin" --job-id "$job_id" --tasks "$task_spec"
}

preflight
if [[ "${1:-}" == "--preflight-only" ]]; then
  printf 'PASS job=%s tasks=%s thread=%s codex=%s classifier=%s\n' \
    "$job_id" "$task_spec" "$thread_id" "$codex_bin" "$status_bin"
  exit 0
fi

cd "$repo"
exec 9>"$lock"
flock -n 9 || fail "another watcher owns ${lock}"
for marker in "$event" "$invoked" "$completed"; do
  path_occupied "$marker" && fail "refuse to reuse occupied marker: ${marker}"
done

snapshot=$(mktemp "${TMPDIR:-/tmp}/${run_id}.snapshot.XXXXXX")
event_tmp=
invoked_tmp=
completed_tmp=
cleanup() {
  rm -f -- "$snapshot"
  [[ -z "$event_tmp" ]] || rm -f -- "$event_tmp"
  [[ -z "$invoked_tmp" ]] || rm -f -- "$invoked_tmp"
  [[ -z "$completed_tmp" ]] || rm -f -- "$completed_tmp"
}
trap cleanup EXIT

unreliable=0
event_type=
while :; do
  if ! run_status >"$snapshot"; then
    unreliable=$((unreliable + 1))
  else
    read -r overall observer_errors unknown_tasks < <(
      "$python_bin" - "$snapshot" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print(d.get("overall","INVALID"), len(d.get("observer_errors",[])), len(d.get("unknown_tasks",[])))
PY
    )
    case "$overall" in
      COMPLETE) event_type=slurm-array-complete; break ;;
      ERROR)    event_type=slurm-array-error; break ;;
      ACTIVE)
        if (( observer_errors > 0 || unknown_tasks > 0 )); then
          unreliable=$((unreliable + 1))
        else
          unreliable=0
        fi ;;
      *) unreliable=$((unreliable + 1)) ;;
    esac
  fi
  if (( unreliable >= max_unreliable )); then
    event_type=slurm-array-monitor-error
    break
  fi
  sleep "$poll_seconds"
done

# If the classifier itself failed on the terminal observation, create a minimal
# snapshot; otherwise bind the exact classifier JSON into the event.
if ! "$python_bin" -m json.tool "$snapshot" >/dev/null 2>&1; then
  "$python_bin" - "$snapshot" "$job_id" "$task_spec" <<'PY'
import datetime,json,sys
path,job,tasks=sys.argv[1:4]
d={"schema_version":1,"observed_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
   "job_id":job,"expected_task_spec":tasks,"overall":"MONITOR_ERROR",
   "observer_errors":["classifier did not return valid JSON"]}
open(path,"w").write(json.dumps(d,sort_keys=True)+"\n")
PY
fi

event_tmp=$(mktemp "${state_dir}/.${run_id}-wakeup.XXXXXX")
"$python_bin" - "$snapshot" "$event_tmp" "$event_type" "$thread_id" "$run_id" "$repo" <<'PY'
import json,subprocess,sys
source,out,event_type,thread_id,run_id,repo=sys.argv[1:7]
d=json.load(open(source))
d.update({"event":event_type,"thread_id":thread_id,"watcher_run_id":run_id})
try: d["head_at_event"]=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
except Exception: d["head_at_event"]="UNKNOWN"
with open(out,"w") as f:
    json.dump(d,f,indent=2,sort_keys=True); f.write("\n"); f.flush()
PY
ln "$event_tmp" "$event" || fail "event path appeared concurrently: ${event}"
rm "$event_tmp"; event_tmp=

invoked_tmp=$(mktemp "${state_dir}/.${run_id}-invoked.XXXXXX")
{
  printf 'invoked_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'event_sha256=%s\n' "$(sha256sum "$event" | awk '{print $1}')"
  printf 'event_type=%s\n' "$event_type"
  printf 'thread_id=%s\n' "$thread_id"
  printf 'codex_path=%s\n' "$codex_bin"
} >"$invoked_tmp"
ln "$invoked_tmp" "$invoked" || fail "invoked marker appeared concurrently: ${invoked}"
rm "$invoked_tmp"; invoked_tmp=

prompt="A real G2 Slurm array event occurred. Read docs/orchestration/state/${run_id}-wakeup.json exactly once and validate it; do not poll or enter a bounded wait loop. Preserve every worker UUID and do not consume the remaining personal Codex Full reset credit. Run one complete usage snapshot before any provider dispatch. For COMPLETE, reconcile job ${job_id} once with sacct, require all 12 hash-bound per-playlist ROOT/receipt pairs to validate, commit Gate-1 production evidence, then take the next dependency-ready merge/full-schema-input action using the best live batch/interactive placement. For ERROR, inspect only the failed task logs and preserved artifacts, record the exact blocker, and retry only failed tasks if the committed fail-closed launcher proves that safe. For MONITOR_ERROR, diagnose the watcher without assuming the array failed. Refresh docs/orchestration/LIVE-STATE.md with its generator. Goals remain disabled; do not replace workers or poll an empty event source."

set +e
"$codex_bin" exec resume \
  --disable goals \
  --dangerously-bypass-approvals-and-sandbox \
  "$thread_id" "$prompt" >>"$resume_log" 2>&1
resume_rc=$?
set -e

completed_tmp=$(mktemp "${state_dir}/.${run_id}-done.XXXXXX")
{
  printf 'completed_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'resume_rc=%s\n' "$resume_rc"
  printf 'event_type=%s\n' "$event_type"
  printf 'thread_id=%s\n' "$thread_id"
} >"$completed_tmp"
ln "$completed_tmp" "$completed" || fail "completion marker appeared concurrently: ${completed}"
rm "$completed_tmp"; completed_tmp=

exit "$resume_rc"
