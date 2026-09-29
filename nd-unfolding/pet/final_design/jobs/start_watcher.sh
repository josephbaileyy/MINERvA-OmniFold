#!/bin/bash
# usage: start_watcher.sh <full sha> [stop, default 2026-10-03T22:00Z]
# Node-independent restart: `ssh saul.nersc.gov` lands on any login node and ps only sees that node, so a
# running watcher elsewhere is stopped through the shared stop file ($B/keep_busy.stop), whose removal is
# waited for until every running watcher has logged "keep_busy stopped" (they poll it every 120 s).
B=/pscratch/sd/j/josephrb/pet-final-design-20260925; S=$1; M=$B/checkouts/${S:0:8}; STOP=${2:-2026-10-03T22:00Z}
[[ "$(git -C "$M" rev-parse HEAD 2>/dev/null)" == "$S" ]] || { echo "checkout $M not at $S" >&2; exit 2; }
# a watcher is alive if it logged within its 120-s loop recently, or if its pid is visible here
before=$(grep -c "keep_busy stopped" $B/keep_busy.log)
started=$(grep -c "watcher (re)started" $B/keep_busy.log)
running=$(( started - before ))
if (( running > 0 )); then
  touch $B/keep_busy.stop
  echo "$(date -u +%FT%TZ) stop file set by start_watcher.sh ($running watcher(s) believed running)" >> $B/keep_busy.log
  for i in $(seq 1 30); do
    (( $(grep -c "keep_busy stopped" $B/keep_busy.log) - before >= running )) && break
    sleep 10
  done
  rm -f $B/keep_busy.stop
fi
echo "$(date -u +%FT%TZ) watcher (re)started from ${S:0:8} on $(hostname), stop $STOP" >> $B/keep_busy.log
cd $B && nohup setsid bash $M/nd-unfolding/pet/final_design/jobs/keep_busy.sh $M $S $STOP > $B/keep_busy.out 2>&1 < /dev/null &
sleep 2; hostname > $B/keep_busy.host
ps -u josephrb -o pid=,args= | awk '$2=="bash" && $3 ~ /keep_busy\.sh$/'
