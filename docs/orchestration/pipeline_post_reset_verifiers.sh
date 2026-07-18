#!/usr/bin/env bash
# Read-only cross-provider review pipeline. It observes the saved A/C/B roles
# dispatched by resume_after_school_reset_1800.sh and overlaps each verifier
# with the next writer without replacing or concurrently messaging a worker.
set -eo pipefail

repo=/pscratch/sd/j/josephrb/MINERvA-OmniFold
state_dir="$repo/docs/orchestration/state"
registry="$state_dir/sessions.json"
python=/usr/bin/python3.11
ctl=orchestration/agentctl.py
target_epoch=$(date -u -d '2026-07-18 18:00:35 UTC' +%s)
deadline_epoch=$(date -u -d '2026-07-19 12:00:00 UTC' +%s)
overall_rc=0

mkdir -p "$state_dir"
exec 9>"$state_dir/post-reset-verifier-pipeline.lock"
flock -n 9 || exit 0

delay=$((target_epoch - $(date -u +%s)))
if (( delay > 0 )); then
  sleep "$delay"
fi
cd "$repo"

wait_for_turn() {
  local role=$1 minimum_turn=$2
  while (( $(date -u +%s) < deadline_epoch )); do
    if evidence=$($python - "$registry" "$role" "$minimum_turn" <<'PY'
import json
import sys

registry, role, minimum = sys.argv[1], sys.argv[2], int(sys.argv[3])
session = json.load(open(registry))["sessions"][role]
turns = session.get("turns") or []
if not turns or int(turns[-1].get("number", 0)) < minimum:
    raise SystemExit(1)
turn = turns[-1]
print(turn.get("stdout", ""))
raise SystemExit(0 if int(turn.get("returncode", 1)) == 0 else 2)
PY
    ); then
      printf '[review-pipeline] %s turn ready: %s\n' "$role" "$evidence"
      return 0
    else
      local rc=$?
      if [[ $rc -eq 2 ]]; then
        printf '[review-pipeline] %s latest turn failed; no verifier dispatch\n' "$role" >&2
        return 2
      fi
    fi
    sleep 20
  done
  printf '[review-pipeline] timed out waiting for %s turn %s\n' "$role" "$minimum_turn" >&2
  return 3
}

dispatch_review() {
  local role=$1 prompt=$2 log=$3
  if ! "$python" orchestration/usagectl.py snapshot --json; then
    printf '[review-pipeline] usage gate failed before %s\n' "$role" >&2
    return 4
  fi
  if "$python" "$ctl" send --role "$role" --prompt-file "$prompt" >"$log" 2>&1; then
    printf '[review-pipeline] %s completed rc=0\n' "$role"
    return 0
  else
    local rc=$?
    printf '[review-pipeline] %s failed rc=%s; preserving role\n' "$role" "$rc" >&2
    "$python" orchestration/usagectl.py snapshot --json || true
    return "$rc"
  fi
}

pids=()
if wait_for_turn agent-A-standard 5; then
  dispatch_review standard-p4-verifier \
    docs/orchestration/followup-standard-p4-verifier-03.md \
    "$state_dir/post-reset-standard-verifier.log" &
  pids+=("$!")
else
  exit $?
fi

c_ready=0
if wait_for_turn agent-C-fps 3; then
  c_ready=1
  dispatch_review fps-adopt-verifier \
    docs/orchestration/followup-fps-adopt-verifier-02.md \
    "$state_dir/post-reset-fps-verifier.log" &
  pids+=("$!")
else
  overall_rc=1
fi

if [[ $c_ready -eq 1 ]] && wait_for_turn agent-B-p5b 3; then
  dispatch_review agy-publication-redteam \
    docs/orchestration/followup-agy-pet-repair-recheck-16.md \
    "$state_dir/post-reset-agy-pet-verifier.log" &
  pids+=("$!")
elif [[ $c_ready -eq 1 ]]; then
  overall_rc=1
fi

for pid in "${pids[@]}"; do
  wait "$pid" || overall_rc=1
done
"$python" orchestration/usagectl.py snapshot --json || overall_rc=1
printf '[review-pipeline] complete overall_rc=%s at %s\n' "$overall_rc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit "$overall_rc"
