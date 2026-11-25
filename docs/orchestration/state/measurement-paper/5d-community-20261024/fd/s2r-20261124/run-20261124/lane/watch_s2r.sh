#!/bin/bash
# sacct watch of s2r_run 61935360 from login38, every 600 s; an empty or failed answer is logged as such, never read as
# running; exits 0 at a terminal State, 3 after 12 consecutive failed reads, 4 after 30 polls.
LOG=${1:?log}; J=61935360; fails=0
for i in $(seq 1 30); do
  row=$(ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 saul.nersc.gov "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes login38 'sacct -X -n -P -j $J -o JobID,JobName,State,ExitCode,Start,End,ElapsedRaw,NodeList'" 2>>"$LOG.err"); rc=$?
  echo "$(date -u +%FT%TZ) poll $i ssh rc=$rc row=[$row]" >> "$LOG"
  if [ "$rc" -ne 0 ] || [ -z "$row" ]; then fails=$((fails+1)); [ "$fails" -ge 12 ] && exit 3; sleep 600; continue; fi
  fails=0
  st=$(echo "$row" | head -1 | cut -d'|' -f3 | sed 's/ by [0-9]*$//')
  case "$st" in COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE) echo "TERMINAL $st" >> "$LOG"; exit 0;; esac
  sleep 600
done
exit 4
