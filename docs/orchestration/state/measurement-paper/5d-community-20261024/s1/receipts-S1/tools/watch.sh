#!/bin/bash
# S1 over-time watcher (S1-DECLARATION.md section 3, rule 5): cancel job $1 once its run time exceeds $2 seconds
# (1.25 x its projected wall). Survives the time the job pends; exits when the job leaves the queue.
#   setsid nohup bash watch.sh <jobid> <limit seconds> <log> &
J="${1:?jobid}"; L="${2:?limit s}"; LOG="${3:?log}"
stamp() { date -u +%FT%TZ; }
secs() { local t="$1" d=0; case "$t" in *-*) d="${t%%-*}"; t="${t#*-}";; esac
  IFS=: read -r a b c <<< "$t"; if [ -z "$c" ]; then c="$b"; b="$a"; a=0; fi
  echo $(( 10#$d*86400 + 10#$a*3600 + 10#$b*60 + 10#$c )); }
echo "[watch] $(stamp) job=$J limit=${L}s host=$(hostname)" >> "$LOG"
for i in $(seq 1 40000); do
  out=$(squeue -h -j "$J" -o "%T %M" 2>/dev/null); rc=$?
  if [ $rc -ne 0 ] || [ -z "$out" ]; then
    st=$(sacct -X -n -P -j "$J" -o State,Elapsed,ExitCode 2>/dev/null | head -1)
    case "$st" in
      ""|PENDING*|RUNNING*|REQUEUED*|CONFIGURING*|COMPLETING*) sleep 30; continue ;;
      *) echo "[watch] $(stamp) job=$J left queue: $st" >> "$LOG"; exit 0 ;;
    esac
  fi
  read -r state used <<< "$out"
  if [ "$state" = RUNNING ] && [ "$(secs "$used")" -gt "$L" ]; then
    scancel "$J"; echo "[watch] $(stamp) job=$J CANCELLED: run time $used exceeds ${L}s" >> "$LOG"; exit 9
  fi
  sleep 30
done
echo "[watch] $(stamp) job=$J watcher loop exhausted" >> "$LOG"; exit 10
