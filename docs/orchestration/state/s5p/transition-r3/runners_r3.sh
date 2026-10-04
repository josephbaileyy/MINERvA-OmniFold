# s5p transition r3: stop the r2 runners / start the r3 runners / post-check, run ON login33 via saul:
#   ssh saul.nersc.gov 'ssh -q login33 bash -s stop'                 < runners_r3.sh
#   ssh saul.nersc.gov 'ssh -q login33 bash -s start <deploy-short>' < runners_r3.sh
#   ssh saul.nersc.gov 'ssh -q login33 bash -s check <deploy-short> <full-sha>' < runners_r3.sh
# Uses /proc and `kill -0 -- -PGID` (ps hangs on login33 under load). Lanes, labels and old PIDs are the plan's
# (transition-r3/plan.json, observed 2026-10-04T04:42Z). Exit 0 only if every step's checks hold.
NS=/pscratch/sd/j/josephrb/s5p-20260926
LANES="pow:pow.q:s5p_pow_p3g_a1p0:1174643 MnvTune_v1:cal-MnvTune_v1.q:s5p_cal_mnvtune_v1_b5:1174644 GENIE_2_12_10_CV:cal-GENIE_2_12_10_CV.q:s5p_cal_genie_2_12_10_cv_b5:1174645 GENIE_2_12_10_MEC:cal-GENIE_2_12_10_MEC.q:s5p_cal_genie_2_12_10_mec_b5:1174646 NuWro_21_09:cal-NuWro_21_09.q:s5p_cal_nuwro_21_09_b4:1174647 GiBUU_2019:cal-GiBUU_2019.q:s5p_cal_gibuu_2019_b4:1174648"
cmd=${1:?stop | start <deploy-short> | check <deploy-short> <sha>}
onwait() { case "$1" in *"until out=\$(squeue -h --me -n s5p-$2 "*) return 0;; *) return 1;; esac; }
fail=0
echo "$cmd start $(date -u +%FT%TZ) on $(hostname)"
case "$cmd" in
  stop)
    for spec in $LANES; do
      IFS=: read -r lane q lab pg <<< "$spec"
      L=$NS/runs/queue-prod-r2-$lane.log; before=$(tail -1 "$L")
      onwait "$before" "$lab" || { echo "ABORT $lane: not on the planned wait line ($lab): ${before:0:140}"; exit 3; }
      [ -r /proc/$pg/cmdline ] && tr '\0' ' ' < /proc/$pg/cmdline | grep -q "queues-r2/$q" || { echo "ABORT $lane: pid $pg is not the r2 runner"; exit 3; }
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
      [ -f "$D/docs/orchestration/state/s5p/prod/queues-r3/$q" ] || { echo "ABORT: missing queues-r3/$q"; exit 3; }
      S5C_NS=$NS setsid nohup bash $D/nd-unfolding/s5c_queue.sh $D/docs/orchestration/state/s5p/prod/queues-r3/$q $NS/runs/STOP-prod-r3-$lane >> runs/queue-prod-r3-$lane.log 2>&1 < /dev/null &
      echo "started $lane pid $!"
    done
    sleep 8 ;;
  check)
    D=$NS/deploy/${2:?deploy short sha}; SHA=${3:?full sha}
    n=0
    for p in /proc/[0-9]*; do
      c=$(timeout 2 tr '\0' ' ' < $p/cmdline 2>/dev/null) || continue
      case "$c" in *"$D/nd-unfolding/s5c_queue.sh $D/docs/orchestration/state/s5p/prod/queues-r3/"*) ;; *) continue;; esac
      [ "$(cut -d' ' -f4 $p/stat 2>/dev/null)" = 1 ] && n=$((n+1)) && echo "  runner ${p#/proc/}: $(printf '%s' "$c" | grep -o 'queues-r3/[^ ]*')"
    done
    [ $n = 6 ] && echo "PASS six r3 session leaders (PPID 1) on deploy $D" || { echo "FAIL r3 session leaders: $n"; fail=1; }
    for spec in $LANES; do
      IFS=: read -r lane q lab pg <<< "$spec"
      L=$NS/runs/queue-prod-r3-$lane.log
      grep -qF "deploy=$D pin=$SHA" "$L" && onwait "$(tail -1 $L)" "$lab" && echo "PASS $lane: log pinned to $SHA, waiting on $lab" || { echo "FAIL $lane: $(tail -1 $L | cut -c1-140)"; fail=1; }
      kill -0 -- -"$pg" 2>/dev/null && { echo "FAIL old r2 group $pg alive"; fail=1; }
    done ;;
  *) echo "usage"; exit 2 ;;
esac
[ $fail = 0 ] && { echo "$cmd: OK"; exit 0; } || { echo "$cmd: FAILED"; exit 1; }
