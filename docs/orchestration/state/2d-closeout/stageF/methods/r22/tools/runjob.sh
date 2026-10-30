#!/usr/bin/env bash
# usage: runjob.sh <id> <prompt> <out> <input> -- one sol2 run via run_x.sh, one retry if it fails or is empty;
# a completed output is skipped. Status goes to runs/status.tsv.
R=$(cd "$(dirname "$0")/.." && pwd); id=$1; p=$2; out=$3; inp=$4
cd "$R"; [ -s "$out" ] && grep -q '^RATING:' "$out" && exit 0
for a in 1 2; do
  t0=$(date +%s); XMODEL_DIR=$R/x bash tools/run_x.sh sol2 "$p" "$out" "$inp" > /dev/null 2>&1; rc=$?
  w=$(wc -w < "$out" 2>/dev/null || echo 0)
  printf '%s\tattempt=%s\trc=%s\twords=%s\tsecs=%s\t%s\n' "$id" $a $rc $w $(( $(date +%s) - t0 )) "$(date +%T)" >> runs/status.tsv
  [ $rc -eq 0 ] && [ "$w" -gt 0 ] && exit 0
done
exit 1
