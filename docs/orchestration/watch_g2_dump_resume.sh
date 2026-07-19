#!/usr/bin/env bash
# OS-detached one-shot watcher for the singleton G2 full-schema dump job.
set -euo pipefail

repo=${WAKE_REPO:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
state_dir=${WAKE_STATE_DIR:-${repo}/docs/orchestration/state}
job_id=${WAKE_JOB_ID:-56116598}
thread_id=${WAKE_THREAD_ID:-019f749a-857b-7790-8cec-bc36b22908be}
run_id=${WAKE_RUN_ID:-g2-dump-${job_id}}
poll_seconds=${WAKE_POLL_SECONDS:-60}
max_unreliable=${WAKE_MAX_UNRELIABLE:-10}
codex_bin=${CODEX_BIN:-$(command -v codex 2>/dev/null || true)}

event=${state_dir}/${run_id}-wakeup.json
resume_log=${state_dir}/${run_id}-resume.log
invoked=${state_dir}/${run_id}-resume.invoked
completed=${state_dir}/${run_id}-resume.done
lock=${state_dir}/${run_id}-wake.lock

fail() { printf '[g2-dump-wake][FAIL] %s\n' "$*" >&2; exit 126; }
occupied() { [[ -e "$1" || -L "$1" ]]; }
[[ "$job_id" =~ ^[0-9]+$ ]] || fail "invalid job id"
[[ "$thread_id" =~ ^[0-9a-fA-F-]{36}$ ]] || fail "invalid thread id"
[[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]] || fail "invalid poll interval"
[[ "$max_unreliable" =~ ^[1-9][0-9]*$ ]] || fail "invalid unreliable limit"
[[ -n "$codex_bin" && "$codex_bin" = /* && -x "$codex_bin" ]] || fail "codex missing/not absolute/executable"
command -v flock >/dev/null || fail "flock missing"
command -v squeue >/dev/null || fail "squeue missing"
command -v sacct >/dev/null || fail "sacct missing"
mkdir -p "$state_dir"
if [[ "${1:-}" == "--preflight-only" ]]; then
  printf 'PASS job=%s thread=%s codex=%s\n' "$job_id" "$thread_id" "$codex_bin"
  exit 0
fi

cd "$repo"
exec 9>"$lock"
flock -n 9 || fail "another watcher owns $lock"
for marker in "$event" "$invoked" "$completed"; do occupied "$marker" && fail "occupied marker: $marker"; done

unreliable=0
state=
exit_code=
while :; do
  if squeue -h -j "$job_id" -o '%T' | grep -q .; then
    unreliable=0
  else
    row=$(sacct -X -n -P -j "$job_id" --format=JobIDRaw,State,ExitCode | awk -F'|' -v j="$job_id" '$1==j {print; exit}')
    if [[ -n "$row" ]]; then
      IFS='|' read -r _ state exit_code <<<"$row"
      state=${state%%+*}
      case "$state" in
        COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE) break ;;
        *) unreliable=$((unreliable+1)) ;;
      esac
    else
      unreliable=$((unreliable+1))
    fi
  fi
  if (( unreliable >= max_unreliable )); then state=MONITOR_ERROR; exit_code=unknown; break; fi
  sleep "$poll_seconds"
done

event_type=slurm-job-error
[[ "$state" == COMPLETED && "$exit_code" == 0:0 ]] && event_type=slurm-job-complete
[[ "$state" == MONITOR_ERROR ]] && event_type=slurm-job-monitor-error
tmp=$(mktemp "${state_dir}/.${run_id}-wakeup.XXXXXX")
/usr/bin/python3.11 - "$tmp" "$event_type" "$job_id" "$state" "$exit_code" "$thread_id" "$run_id" "$repo" <<'PY'
import datetime,json,subprocess,sys
out,event,job,state,exit_code,thread,run_id,repo=sys.argv[1:9]
d={"schema_version":1,"observed_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
   "event":event,"job_id":job,"state":state,"exit_code":exit_code,
   "thread_id":thread,"watcher_run_id":run_id}
try:d["head_at_event"]=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
except Exception:d["head_at_event"]="UNKNOWN"
with open(out,"w") as f: json.dump(d,f,indent=2,sort_keys=True);f.write("\n");f.flush()
PY
ln "$tmp" "$event" || fail "event path race"; rm "$tmp"

tmp=$(mktemp "${state_dir}/.${run_id}-invoked.XXXXXX")
printf 'invoked_at_utc=%s\nevent_sha256=%s\nevent_type=%s\nthread_id=%s\ncodex_path=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(sha256sum "$event"|awk '{print $1}')" "$event_type" "$thread_id" "$codex_bin" >"$tmp"
ln "$tmp" "$invoked" || fail "invoked path race"; rm "$tmp"

prompt="A real G2 full-schema dump Slurm event occurred. Read docs/orchestration/state/${run_id}-wakeup.json exactly once and validate it; do not poll or enter a bounded wait loop. Preserve every worker UUID and do not consume the protected personal Codex Full reset. For COMPLETE, reconcile singleton job ${job_id} once, validate the hash-bound NPZ/receipt and retained-domain/schema/identity inventories, commit Gate 1B evidence, and take only the next dependency-ready Gate-2 negweight-refined construction action. For ERROR, inspect the job logs and preserved artifacts, record the exact blocker, and retry only if the committed fail-closed launcher proves safe. For MONITOR_ERROR, diagnose only the watcher. Run a complete usage snapshot before provider dispatch and refresh LIVE-STATE.md with its generator. Goals remain disabled; do not poll an empty event source."
set +e
"$codex_bin" exec resume --disable goals --dangerously-bypass-approvals-and-sandbox "$thread_id" "$prompt" >>"$resume_log" 2>&1
resume_rc=$?
set -e
tmp=$(mktemp "${state_dir}/.${run_id}-done.XXXXXX")
printf 'completed_at_utc=%s\nresume_rc=%s\nevent_type=%s\nthread_id=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$resume_rc" "$event_type" "$thread_id" >"$tmp"
ln "$tmp" "$completed" || fail "done path race"; rm "$tmp"
exit "$resume_rc"
