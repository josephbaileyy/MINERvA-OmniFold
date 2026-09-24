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
echo "round 1: holders=$held skipped=$skipped"
( SLURM_JOB_ID=killer; claim run && sleep 60 ) & K=$!; sleep 1; kill -9 $K; wait $K 2>/dev/null
sleep 1
( SLURM_JOB_ID=after; claim run && echo "after-kill claim OK" ) || echo "after-kill claim FAILED"
( SLURM_JOB_ID=h1; claim run && { ( SLURM_JOB_ID=probe; held_by_other run && echo "probe sees held: OK" || echo "probe sees free: FAIL" ); } )
[[ "$held" == 1 && "$skipped" == 11 ]] && echo PASS || echo FAIL
