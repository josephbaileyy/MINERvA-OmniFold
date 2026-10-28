#!/usr/bin/env bash
# usage: runjob.sh <id> <model> <prompt> <out> <inputs...> -- one rater run via register-method run_x.sh, one retry.
set -u
X=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/xmodel/prd5d; R=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con/docs/orchestration/state/2d-closeout/stageF/methods/register-method/tools/run_x.sh
id=$1; m=$2; p=$3; out=$4; shift 4
if [ -s "$out" ] && [ "$(wc -w < "$out")" -gt 5 ]; then echo -e "$id\tskip-done" >> $X/runs/status.tsv; exit 0; fi
case $id in P2S*) key="WINNER:";; *) key="T: CHOICE";; esac
for attempt in 1 2; do
  t0=$(date +%s)
  XMODEL_DIR=$X bash $R "$m" "$p" "$out" "$@" > /dev/null 2>&1; rc=$?
  w=$(wc -w < "$out" 2>/dev/null || echo 0); w=$(echo $w)
  echo -e "$id\tattempt=$attempt\trc=$rc\twords=$w\tsecs=$(( $(date +%s) - t0 ))\t$(date '+%H:%M:%S')" >> $X/runs/status.tsv
  if [ "$rc" = 0 ] && [ "$w" -gt 5 ] && grep -q "$key" "$out"; then exit 0; fi
  [ -f "$out" ] && mv "$out" "$out.failed$attempt"
done
echo -e "$id\tFAILED-TWICE" >> $X/runs/status.tsv
exit 1
