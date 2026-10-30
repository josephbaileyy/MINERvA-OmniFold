#!/usr/bin/env bash
# usage: gapjob.sh <input> <model> -- one gap-prompt run via run_x.sh, one retry if it fails or is empty;
# a completed output (one with a CURRENT RATING line) is skipped. <input> is a dir under gap/inputs (paper, paper-ctl,
# B01..B15, B09-ctl); <model> is sol2 or gemini. Paper inputs get G1 and their own reference-1..3; note pieces get G1N
# and note-refs/reference-1..4. Output: gap/runs/G__<input>__<model>.txt. Status goes to gap/runs/status.tsv.
R=$(cd "$(dirname "$0")/.." && pwd); inp=$1; m=$2; I=$R/gap/inputs
cd "$R"; mkdir -p gap/runs; out=gap/runs/G__${inp}__${m}.txt
[ -s "$out" ] && grep -q 'CURRENT RATING:' "$out" && exit 0
case $inp in
  paper|paper-ctl) p=prompts/G1.prompt.txt; set -- "$I/$inp"/reference-{1,2,3}.txt "$I/$inp/manuscript.txt" ;;
  B[0-9][0-9]|B[0-9][0-9]-ctl) p=prompts/G1N.prompt.txt; set -- "$I"/note-refs/reference-{1,2,3,4}.txt "$I/$inp/chapter.txt" ;;
  *) echo "unknown input $inp" >&2; exit 2 ;;
esac
for f in "$@"; do [ -s "$f" ] || { echo "missing $f" >&2; exit 2; }; done
for a in 1 2; do
  t0=$(date +%s); XMODEL_DIR=$R/x bash tools/run_x.sh "$m" "$p" "$out" "$@" > /dev/null 2>&1; rc=$?
  w=$(wc -w < "$out" 2>/dev/null || echo 0)
  printf '%s\t%s\tattempt=%s\trc=%s\twords=%s\tsecs=%s\t%s\n' "$inp" "$m" $a $rc $w $(( $(date +%s) - t0 )) "$(date +%T)" >> gap/runs/status.tsv
  [ $rc -eq 0 ] && [ "$w" -gt 0 ] && exit 0
done
exit 1
