# s5p transition r4 (NuWro concurrency, one lane): stop the r3 runner / start the r4 runner / post-check, run ON login33 via saul:
#   ssh saul.nersc.gov 'ssh -q login33 bash -s stop'                 < runners_r3.sh
#   ssh saul.nersc.gov 'ssh -q login33 bash -s start <deploy-short>' < runners_r3.sh
#   ssh saul.nersc.gov 'ssh -q login33 bash -s check <deploy-short> <full-sha>' < runners_r3.sh
# Uses /proc and `kill -0 -- -PGID` (ps hangs on login33 under load). Lanes, labels and old PIDs are the plan's
# (transition-r3/plan.json, observed 2026-10-04T04:42Z). Exit 0 only if every step's checks hold.
NS=/pscratch/sd/j/josephrb/s5p-20260926
LANES="NuWro_21_09:cal-NuWro_21_09.q:s5p_cal_nuwro_21_09_b5:1047840"
cmd=${1:?stop | start <deploy-short> | check <deploy-short> <sha>}
onwait() { case "$1" in *"until out=\$(squeue -h --me -n s5p-$2 "*) return 0;; *) return 1;; esac; }
fail=0
echo "$cmd start $(date -u +%FT%TZ) on $(hostname)"
case "$cmd" in
  stop)
    for spec in $LANES; do
      IFS=: read -r lane q lab pg <<< "$spec"
      L=$NS/runs/queue-prod-r3-$lane.log; before=$(tail -1 "$L")
      onwait "$before" "$lab" || { echo "ABORT $lane: not on the planned wait line ($lab): ${before:0:140}"; exit 3; }
      [ -r /proc/$pg/cmdline ] && tr '\0' ' ' < /proc/$pg/cmdline | grep -q "queues-r3/$q" || { echo "ABORT $lane: pid $pg is not the r3 runner"; exit 3; }
      [ "$(cut -d' ' -f4 /proc/$pg/stat)" = 1 ] || { echo "ABORT $lane: pid $pg ppid != 1"; exit 3; }
      kill -TERM -- -"$pg"; sleep 3
      if kill -0 -- -"$pg" 2>/dev/null; then echo "  group $pg alive after TERM; KILL"; kill -KILL -- -"$pg"; sleep 2; fi
      kill -0 -- -"$pg" 2>/dev/null && { echo "ABORT $lane: process group $pg survives"; exit 4; }
      after=$(tail -1 "$L")
      [ "$before" = "$after" ] && echo "stopped $lane (pgid $pg) at $(date -u +%T)Z; log unchanged" || { echo "WARN $lane: log advanced: ${after:0:140}"; fail=1; }
    done ;;
  start)
    D=$NS/deploy/${2:?deploy short sha}
    for spec in $LANES; do IFS=: read -r lane q lab pg <<< "$spec"; kill -0 -- -"$pg" 2>/dev/null && { echo "ABORT: old runner group $pg still alive"; exit 3; }; done
    [ -z "$(git -C $D status --porcelain --untracked-files=no)" ] || { echo "ABORT: deploy not clean"; exit 3; }
    cd $NS || exit 2
    for spec in $LANES; do
      IFS=: read -r lane q lab pg <<< "$spec"
      [ -f "$D/docs/orchestration/state/s5p/prod/queues-r4/$q" ] || { echo "ABORT: missing queues-r4/$q"; exit 3; }
      S5C_NS=$NS setsid nohup bash $D/nd-unfolding/s5c_queue.sh $D/docs/orchestration/state/s5p/prod/queues-r4/$q $NS/runs/STOP-prod-r4-$lane >> runs/queue-prod-r4-$lane.log 2>&1 < /dev/null &
      echo "started $lane pid $!"
    done
    sleep 8 ;;
  check)
    D=$NS/deploy/${2:?deploy short sha}; SHA=${3:?full sha}
    n=0
    for p in /proc/[0-9]*; do
      c=$(timeout 2 tr '\0' ' ' < $p/cmdline 2>/dev/null) || continue
      case "$c" in *"$D/nd-unfolding/s5c_queue.sh $D/docs/orchestration/state/s5p/prod/queues-r4/"*) ;; *) continue;; esac
      [ "$(cut -d' ' -f4 $p/stat 2>/dev/null)" = 1 ] && n=$((n+1)) && echo "  runner ${p#/proc/}: $(printf '%s' "$c" | grep -o 'queues-r4/[^ ]*')"
    done
    [ $n = 1 ] && echo "PASS one r4 session leader (PPID 1) on deploy $D" || { echo "FAIL r4 session leaders: $n"; fail=1; }
    for spec in $LANES; do
      IFS=: read -r lane q lab pg <<< "$spec"
      L=$NS/runs/queue-prod-r4-$lane.log
      grep -qF "deploy=$D pin=$SHA" "$L" && onwait "$(tail -1 $L)" "$lab" && echo "PASS $lane: log pinned to $SHA, waiting on $lab" || { echo "FAIL $lane: $(tail -1 $L | cut -c1-140)"; fail=1; }
      kill -0 -- -"$pg" 2>/dev/null && { echo "FAIL old r3 group $pg alive"; fail=1; }
    done ;;
  *) echo "usage"; exit 2 ;;
esac
[ $fail = 0 ] && { echo "$cmd: OK"; exit 0; } || { echo "$cmd: FAILED"; exit 1; }
