#!/bin/bash
# usage: start_watcher.sh <full sha> [stop, default 2026-09-27T22:00Z]   (run on the login node; kills any running keep_busy by exact pid file)
B=/pscratch/sd/j/josephrb/pet-final-design-20260925; S=$1; M=$B/checkouts/${S:0:8}
# only the top-level watcher: its forked subshells (which may be the parents of interactive sruns)
# have a keep_busy parent and are left alone
W=$(ps -u josephrb -o pid=,args= | awk '$2=="bash" && $3 ~ /keep_busy\.sh$/ {print $1}')
for p in $W; do pp=$(ps -o ppid= -p "$p" | tr -d ' '); grep -qx "$pp" <<<"$W" || { kill "$p"; echo "killed $p"; }; done
echo "$(date -u +%FT%TZ) watcher (re)started from ${S:0:8}" >> $B/keep_busy.log
STOP=${2:-2026-09-27T22:00Z}
cd $B && nohup setsid bash $M/nd-unfolding/pet/final_design/jobs/keep_busy.sh $M $S $STOP > $B/keep_busy.out 2>&1 < /dev/null &
sleep 2; hostname > $B/keep_busy.host
ps -u josephrb -o pid=,args= | awk '$2=="bash" && $3 ~ /keep_busy\.sh$/'
