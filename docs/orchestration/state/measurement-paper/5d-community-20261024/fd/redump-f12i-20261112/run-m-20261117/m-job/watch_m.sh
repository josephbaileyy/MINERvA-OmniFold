#!/bin/bash
# RDX m watch: sacct over the merge job's id (never squeue), every 5 min. Read-only.
# Exits 0 when the job is in a terminal state (after one full read of its steps, with MaxRSS); 4 after 6 bad reads in a row.
ID=61443055
D=$(cd "$(dirname "$0")" && pwd); LOG=$D/watch.log; ERR=$D/watch.err
TERM_RE='^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)'
SSH=(-n -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
bad=0
while :; do
  now=$(date -u +%FT%TZ)
  out=$(ssh "${SSH[@]}" saul.nersc.gov "sacct -X -n -P -j $ID -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,Start,End" 2>>"$ERR")
  rc=$?
  n=$(printf '%s\n' "$out" | grep -c "^$ID|")
  { echo "== $now ssh rc=$rc rows=$n"; printf '%s\n' "$out"; } >> "$LOG"
  if [ $rc -ne 0 ] || [ "$n" -ne 1 ]; then
    bad=$((bad+1)); [ $bad -ge 6 ] && { echo "WATCH UNUSABLE: $bad consecutive bad reads at $now (rc=$rc rows=$n)"; exit 4; }
  else
    bad=0
    if printf '%s\n' "$out" | awk -F'|' -v r="$TERM_RE" '$3 ~ r' | grep -q .; then
      full=$(ssh "${SSH[@]}" saul.nersc.gov "sacct -n -P -j $ID -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,MaxRSS,Start,End" 2>>"$ERR")
      { echo "== $now final, all steps (ssh rc=$?)"; printf '%s\n' "$full"; } >> "$LOG"
      echo "ENDED at $now"; printf '%s\n' "$out"; printf '%s\n' "$full"; exit 0
    fi
  fi
  sleep 300
done
