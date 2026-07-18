#!/usr/bin/env bash
set -eo pipefail

repo=/pscratch/sd/j/josephrb/MINERvA-OmniFold
state_dir="$repo/docs/orchestration/state"
target_epoch=$(date -u -d '2026-07-18 13:00:30 UTC' +%s)
now_epoch=$(date -u +%s)
delay=$((target_epoch - now_epoch))

mkdir -p "$state_dir"
exec 9>"$state_dir/school-reset-wakeup.lock"
flock -n 9 || exit 0

if (( delay > 0 )); then
  sleep "$delay"
fi

cd "$repo"
python=/usr/bin/python3.11
ctl=orchestration/agentctl.py
overall_rc=0

date -u "+[wakeup] %Y-%m-%dT%H:%M:%SZ running fail-closed usage preflight"
if "$python" orchestration/usagectl.py snapshot --json; then
  date -u "+[wakeup] %Y-%m-%dT%H:%M:%SZ usage gate passed; preserving reset credits"
else
  usage_rc=$?
  date -u "+[wakeup] %Y-%m-%dT%H:%M:%SZ usage gate failed rc=${usage_rc}; no provider dispatch"
  exit 2
fi

run_role() {
  local role="$1" prompt="$2" role_rc
  date -u "+[wakeup] %Y-%m-%dT%H:%M:%SZ starting ${role}"
  if "$python" "$ctl" send --role "$role" --prompt-file "$prompt"; then
    date -u "+[wakeup] %Y-%m-%dT%H:%M:%SZ ${role} returned rc=0"
  else
    role_rc=$?
    overall_rc=1
    date -u "+[wakeup] %Y-%m-%dT%H:%M:%SZ ${role} returned rc=${role_rc}; preserving role and continuing independent routes"
  fi
}

run_role agent-A-standard orchestration/followup-agent-A-standard-02.md
run_role agent-C-fps orchestration/followup-agent-C-fps-02.md
run_role agent-B-p5b orchestration/followup-agent-B-p5b-02.md

date -u "+[wakeup] %Y-%m-%dT%H:%M:%SZ all reset rounds returned overall_rc=${overall_rc}"
exit "$overall_rc"
