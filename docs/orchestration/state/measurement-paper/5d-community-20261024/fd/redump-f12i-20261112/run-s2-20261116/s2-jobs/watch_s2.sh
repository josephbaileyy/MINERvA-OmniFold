#!/bin/bash
# RDX s2 watch: sacct over the 11 job ids (never squeue), every 10 min. Read-only.
# Exits 0 when all 11 rows are in a terminal state; exits 4 after 6 consecutive unusable reads (ssh fail / wrong row count).
IDS=61423404,61423406,61423408,61423410,61423414,61423417,61423421,61423451,61423454,61423456,61423459
D=$(cd "$(dirname "$0")" && pwd); LOG=$D/watch.log; ERR=$D/watch.err
TERM_RE='^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)'
bad=0
while :; do
  now=$(date -u +%FT%TZ)
  out=$(ssh -n -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 \
        saul.nersc.gov "sacct -X -n -P -j $IDS -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,Start,End" 2>>"$ERR")
  rc=$?
  n=$(printf '%s\n' "$out" | grep -c '^[0-9]')
  { echo "== $now ssh rc=$rc rows=$n"; printf '%s\n' "$out"; } >> "$LOG"
  if [ $rc -ne 0 ] || [ "$n" -ne 11 ]; then
    bad=$((bad+1)); [ $bad -ge 6 ] && { echo "WATCH UNUSABLE: $bad consecutive bad reads at $now (rc=$rc rows=$n)"; exit 4; }
  else
    bad=0
    t=$(printf '%s\n' "$out" | awk -F'|' -v r="$TERM_RE" '$3 ~ r' | wc -l)
    if [ "$t" -eq 11 ]; then echo "ALL ENDED at $now"; printf '%s\n' "$out"; exit 0; fi
  fi
  sleep 600
done
