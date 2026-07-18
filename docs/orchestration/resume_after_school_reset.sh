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

date -u '+[wakeup] %Y-%m-%dT%H:%M:%SZ starting agent-C-fps'
"$python" "$ctl" send --role agent-C-fps \
  --prompt-file orchestration/followup-agent-C-fps-02.md

date -u '+[wakeup] %Y-%m-%dT%H:%M:%SZ starting agent-A-standard'
"$python" "$ctl" send --role agent-A-standard \
  --prompt-file orchestration/followup-agent-A-standard-02.md

date -u '+[wakeup] %Y-%m-%dT%H:%M:%SZ starting agent-B-p5b'
"$python" "$ctl" send --role agent-B-p5b \
  --prompt-file orchestration/followup-agent-B-p5b-02.md

date -u '+[wakeup] %Y-%m-%dT%H:%M:%SZ all reset rounds returned'
