#!/usr/bin/env bash
# usage: runjob.sh <id> <model> <prompt> <out> <inputs...>   -- one rater run via run_x.sh, one retry on failure/empty
set -u
C=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/xmodel/cal
X=$C/..
id=$1; m=$2; p=$3; out=$4; shift 4
if [ -s "$out" ] && [ "$(wc -w < "$out")" -gt 5 ]; then echo -e "$id\tskip-done" >> $C/runs/status.tsv; exit 0; fi
for attempt in 1 2; do
  t0=$(date +%s)
  bash $X/run_x.sh "$m" "$p" "$out" $@ > /dev/null 2>&1; rc=$?
  w=$(wc -w < "$out" 2>/dev/null || echo 0); w=$(echo $w)
  echo -e "$id\tattempt=$attempt\trc=$rc\twords=$w\tsecs=$(( $(date +%s) - t0 ))\t$(date '+%H:%M:%S')" >> $C/runs/status.tsv
  if [ "$rc" = 0 ] && [ "$w" -gt 5 ]; then exit 0; fi
  [ -f "$out" ] && mv "$out" "$out.failed$attempt"
done
echo -e "$id\tFAILED-TWICE" >> $C/runs/status.tsv
exit 1
