#!/bin/bash
# Fired by wakerctl when the P4 standard receipts job reaches a Slurm terminal state.
# Runs the receipt self-check immediately and leaves its output on disk, so the result exists
# whether or not any session is alive to look. Deliberately `command`, not `root-resume`:
# resuming would dispatch into the campaign root thread, which is not this lane's to take.
JOB="${1:-unknown}"
R=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OUT=$R/nd-unfolding/active_universe_5d/standard/preflight_logs
mkdir -p "$OUT"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG=$OUT/selfcheck_autofired_${STAMP}.log
{
  echo "=== wakerctl fired for job $JOB at $STAMP ==="
  sacct -X -j "$JOB" --format=JobID,State,ExitCode,Elapsed -P 2>&1 | head -4
  echo
  echo "=== receipts on disk ==="
  ls "$R/nd-unfolding/active_universe_5d/standard/unfolds"/*.done 2>/dev/null | wc -l
  echo
  bash /pscratch/sd/j/josephrb/selfcheck_receipts.sh 2>&1
} > "$LOG" 2>&1
echo "self-check written to $LOG"
