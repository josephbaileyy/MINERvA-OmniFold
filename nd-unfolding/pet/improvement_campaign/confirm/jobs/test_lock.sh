#!/bin/bash
# Test of confirm_lib.sh's run lock (run on a Perlmutter node; needs flock and /pscratch):
# N contenders start at once; exactly one may hold the lock at any time, a contender that finds it
# held skips, and the lock is free again as soon as the holder's processes exit (also on SIGKILL).
#   test_lock.sh <scratch dir on /pscratch>
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); T=$(realpath -m "$1"); mkdir -p "$T"; rm -rf "$T"/*
MINE=$(cd "$HERE/../../../../.." && pwd) MANIFEST=x OUT=$T
source "$HERE/confirm_lib.sh"
contender() {   # id hold_seconds
  SLURM_JOB_ID=$1
  if claim run; then echo "$1 start $(date +%s.%N)" >> "$T/log"; sleep "$2"; echo "$1 end $(date +%s.%N)" >> "$T/log"
  else echo "$1 skipped" >> "$T/log"; fi
}
require_coherent_flock || exit 1
for i in $(seq 1 12); do contender "c$i" 2 & done; wait
held=$(grep -c start "$T/log"); skipped=$(grep -c skipped "$T/log")
# the holder and its child (which inherits the descriptor, as the driver does) are SIGKILLed, as
# Slurm kills a job's processes at its time limit
( SLURM_JOB_ID=killer; claim run && sleep 60 ) & K=$!; sleep 1
ok_held=0; ( SLURM_JOB_ID=during; claim run ) || ok_held=1
pkill -9 -P $K; kill -9 $K; wait $K 2>/dev/null; sleep 1
ok_after=0; ( SLURM_JOB_ID=after; claim run ) && ok_after=1
ok_probe=0; ( SLURM_JOB_ID=h1; claim run && ( SLURM_JOB_ID=probe; held_by_other run ) ) && ok_probe=1
echo "round 1: holders=$held skipped=$skipped; held while holder alive: $ok_held; free after SIGKILL: $ok_after; probe sees held: $ok_probe"
[[ "$held" == 1 && "$skipped" == 11 && $ok_held == 1 && $ok_after == 1 && $ok_probe == 1 ]] && echo PASS || echo FAIL
