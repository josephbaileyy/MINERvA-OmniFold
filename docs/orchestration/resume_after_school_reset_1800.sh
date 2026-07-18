#!/usr/bin/env bash
set -eo pipefail

repo=/pscratch/sd/j/josephrb/MINERvA-OmniFold
state_dir="$repo/docs/orchestration/state"
target_epoch=$(date -u -d '2026-07-18 18:00:30 UTC' +%s)
now_epoch=$(date -u +%s)
delay=$((target_epoch - now_epoch))

mkdir -p "$state_dir"
exec 9>"$state_dir/school-reset-1800.lock"
flock -n 9 || exit 0

if (( delay > 0 )); then
  sleep "$delay"
fi

cd "$repo"
python=/usr/bin/python3.11
ctl=orchestration/agentctl.py
claude_bin=/global/homes/j/josephrb/.local/bin/claude
school_home=/global/homes/j/josephrb/claude-homes/school
overall_rc=0

school_heartbeat() {
  local phase="$1" heartbeat_log heartbeat_rc
  heartbeat_log=$(mktemp "$state_dir/claude-school-heartbeat-${phase}.XXXXXX.json")
  date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ Claude-school cache unknown; running disposable flat-home heartbeat phase=${phase}"
  if env HOME="$school_home" "$claude_bin" --print --output-format json \
      --model opus --dangerously-skip-permissions \
      "Reply exactly HEARTBEAT_OK. Do not use tools." >"$heartbeat_log" 2>&1; then
    date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ disposable Claude-school heartbeat succeeded; availability verified, percentage remains unknown"
    return 0
  fi
  heartbeat_rc=$?
  date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ disposable Claude-school heartbeat failed rc=${heartbeat_rc}; stopping without touching A/B/C UUIDs"
  sed -n '1,80p' "$heartbeat_log"
  "$python" orchestration/usagectl.py snapshot --json || true
  return 5
}

snapshot_and_check() {
  local phase="$1" minimum="$2" snap remaining status
  snap=$(mktemp "$state_dir/usage-${phase}.XXXXXX.json")
  date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ usage preflight phase=${phase}"
  if "$python" orchestration/usagectl.py snapshot --json >"$snap"; then
    :
  else
    local usage_rc=$?
    date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ usage gate failed rc=${usage_rc}; stopping"
    sed -n '1,240p' "$snap"
    return 2
  fi
  sed -n '1,240p' "$snap"
  read -r status remaining < <(
    "$python" - "$snap" <<'PY'
import json
import sys
value = json.load(open(sys.argv[1]))
account = (value.get("accounts") or {}).get("claude-school") or {}
window = (account.get("windows") or {}).get("five_hour") or {}
print(account.get("status", "unknown"), window.get("remaining_percent", "unknown"))
PY
  )
  if [[ "$remaining" == "unknown" ]]; then
    school_heartbeat "$phase"
    return $?
  fi
  if ! "$python" - "$remaining" "$minimum" <<'PY'
import sys
raise SystemExit(0 if float(sys.argv[1]) >= float(sys.argv[2]) else 1)
PY
  then
    date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ shared Claude remaining=${remaining}% below reserve=${minimum}%; stopping"
    return 4
  fi
  date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ shared Claude remaining=${remaining}% status=${status}; phase allowed"
}

run_role() {
  local role="$1" prompt="$2" role_rc
  date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ starting ${role}"
  if "$python" "$ctl" send --role "$role" --prompt-file "$prompt"; then
    date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ ${role} returned rc=0"
  else
    role_rc=$?
    overall_rc=1
    date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ ${role} returned rc=${role_rc}; preserving role"
    "$python" orchestration/usagectl.py snapshot --json || true
    return "$role_rc"
  fi
}

snapshot_and_check pre_A 0 || exit $?
run_role agent-A-standard orchestration/followup-agent-A-standard-04.md || exit $?

snapshot_and_check pre_C 45 || exit $?
run_role agent-C-fps orchestration/followup-agent-C-fps-03.md || exit $?

snapshot_and_check pre_B 25 || exit $?
run_role agent-B-p5b orchestration/followup-agent-B-p5b-03.md || exit $?

snapshot_and_check final 0 || overall_rc=1
date -u "+[wakeup-1800] %Y-%m-%dT%H:%M:%SZ reset repair rounds returned overall_rc=${overall_rc}"
exit "$overall_rc"
