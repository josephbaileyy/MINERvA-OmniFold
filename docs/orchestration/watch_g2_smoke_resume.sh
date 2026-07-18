#!/usr/bin/env bash
set -euo pipefail

repo=/pscratch/sd/j/josephrb/MINERvA-OmniFold
attempt="$repo/nd-unfolding/pet/g2_smoke/attempt2"
state="$repo/docs/orchestration/state"
event="$state/g2-smoke-wakeup.log"
resume_log="$state/g2-smoke-resume.log"
invoked="$state/g2-smoke-resume.invoked"
completed="$state/g2-smoke-resume.done"
thread_id=019f749a-857b-7790-8cec-bc36b22908be
codex_bin=${CODEX_BIN:-/global/homes/j/josephrb/.local/bin/codex}

cd "$repo"
exec 9>"$state/g2-smoke-wake.lock"
flock -n 9 || exit 0

[[ ! -e "$invoked" && ! -e "$completed" ]] || exit 0

while [[ ! -e "$attempt/DONE" && ! -e "$attempt/FAILED" ]]; do
  sleep 30
done

terminal=INVALID
valid=false
if [[ -e "$attempt/DONE" && ! -e "$attempt/FAILED" ]]; then
  terminal=DONE
elif [[ -e "$attempt/FAILED" && ! -e "$attempt/DONE" ]]; then
  terminal=FAILED
fi

loop_rc=missing
if [[ -s "$attempt/loop.rc" ]]; then
  read -r loop_rc < "$attempt/loop.rc"
fi
if [[ "$terminal" == DONE && "$loop_rc" == 0 ]]; then
  valid=true
elif [[ "$terminal" == FAILED && "$loop_rc" =~ ^[0-9]+$ ]]; then
  valid=true
fi

event_tmp="$event.tmp.$$"
{
  printf 'observed_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'event=g2-attempt2-terminal\n'
  printf 'attempt_path=%s\n' "$attempt"
  printf 'terminal=%s\n' "$terminal"
  printf 'loop_rc=%s\n' "$loop_rc"
  printf 'valid=%s\n' "$valid"
  printf 'driver_pid=576350\n'
  printf 'thread_id=%s\n' "$thread_id"
  printf 'head=%s\n' "$(git rev-parse HEAD)"
} > "$event_tmp"
mv "$event_tmp" "$event"

{
  printf 'invoked_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'event_sha256=%s\n' "$(sha256sum "$event" | awk '{print $1}')"
  printf 'thread_id=%s\n' "$thread_id"
} > "$invoked"

prompt='A real G2 smoke terminal event occurred. Read docs/orchestration/state/g2-smoke-wakeup.log exactly once and validate it. Do not poll the event source. Preserve every worker UUID and do not consume the remaining personal Codex Full reset credit. If valid and DONE/rc0, run a complete usage snapshot, resume only agent-E-g2-source UUID 44b634fc-d211-4e09-9229-95a18d1984cc for Stage-4 validation/receipt/atomic isolated publication, then reconcile and commit scoped evidence. If FAILED or invalid, record the exact blocker and stop without replacement or production. Close QP5 from durable state. Goals remain disabled.'

set +e
"$codex_bin" exec resume \
  --disable goals \
  --dangerously-bypass-approvals-and-sandbox \
  "$thread_id" "$prompt" >> "$resume_log" 2>&1
resume_rc=$?
set -e

{
  printf 'completed_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'resume_rc=%s\n' "$resume_rc"
  printf 'thread_id=%s\n' "$thread_id"
} > "$completed"

exit "$resume_rc"
