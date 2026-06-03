#!/bin/bash
# alloc_run.sh — run a command inside a SINGLE, shared CPU allocation.
#
# Purpose: let an agent (or a login-node session) outlive the 3-hour interactive
# limit. The agent runs on the LOGIN node and dispatches every compute command
# through this wrapper. The wrapper holds at most ONE allocation (job-name guard
# + flock), reuses it across calls, and transparently requests a fresh one when
# the previous 3-hour allocation has expired. Total wall-clock is unbounded;
# each underlying allocation is <= 3 h (qos interactive).
#
# Usage:
#   ./alloc_run.sh <command...>     run command in the shared allocation (creating it if needed)
#   ./alloc_run.sh 'a | b > c'      pass a quoted string for pipes/redirects/&&
#   ./alloc_run.sh --status         show the shared allocation (squeue)
#   ./alloc_run.sh --end            release the shared allocation (scancel)
#
# The command runs on the compute node with the full env (setup_salloc_env.sh)
# already sourced, from the repo root.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JOB_NAME="${ALLOC_JOB_NAME:-claude-hold}"   # job-name that identifies the shared allocation
HOLD_SECONDS="${ALLOC_HOLD_SECONDS:-10800}" # placeholder lifetime; matches --time 180
CPUS="${ALLOC_CPUS:-128}"                   # cpus the srun step may use on the CPU node
LOCK="${SCRATCH:-/tmp}/.alloc_run.${USER}.lock"
HOLDLOG="${SCRIPT_DIR}/.alloc_hold.log"

running_jobid() { squeue --me --name="$JOB_NAME" -t R    -h -o '%i' | head -n1; }
pending_jobid() { squeue --me --name="$JOB_NAME" -t R,PD,CF -h -o '%i' | head -n1; }

case "${1:-}" in
  --status) squeue --me --name="$JOB_NAME"; exit 0 ;;
  --end)
      id="$(pending_jobid)"
      if [[ -n "$id" ]]; then scancel "$id" && echo "cancelled shared allocation $id";
      else echo "no shared allocation to cancel"; fi
      exit 0 ;;
  "" ) echo "usage: alloc_run.sh <command...> | --status | --end" >&2; exit 2 ;;
esac

# --- find-or-create exactly one allocation (serialized so two calls can't race) ---
jid="$(running_jobid)"
if [[ -z "$jid" ]]; then
  exec 9>"$LOCK"; flock 9   # only one creator at a time
  jid="$(running_jobid)"    # re-check after acquiring the lock
  if [[ -z "$jid" && -z "$(pending_jobid)" ]]; then
    echo "[alloc_run] no shared allocation; requesting one (job-name=$JOB_NAME, ${HOLD_SECONDS}s)..." >&2
    # setsid + </dev/null detaches the holder so it survives this shell exiting.
    setsid bash -c \
      "'${SCRIPT_DIR}/start_alloc.sh' --job-name='${JOB_NAME}' --no-bell sleep ${HOLD_SECONDS}" \
      </dev/null >"$HOLDLOG" 2>&1 &
  fi
  echo "[alloc_run] waiting for allocation to start..." >&2
  for _ in $(seq 1 180); do jid="$(running_jobid)"; [[ -n "$jid" ]] && break; sleep 5; done
  flock -u 9
fi

if [[ -z "$jid" ]]; then
  echo "[alloc_run] allocation did not start in time. Check: squeue --me ; tail $HOLDLOG" >&2
  exit 1
fi

echo "[alloc_run] using shared allocation $jid" >&2
# Source the env with its chatter on stderr so the command's stdout stays clean.
srun --jobid="$jid" --overlap -n 1 --cpus-per-task="$CPUS" \
  bash -lc "cd '${SCRIPT_DIR}' && source '${SCRIPT_DIR}/setup_salloc_env.sh' 1>&2 && $*"
