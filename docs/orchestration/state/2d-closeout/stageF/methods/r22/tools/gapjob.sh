#!/usr/bin/env bash
# usage: gapjob.sh <input> <model> -- one gap-prompt run via run_x.sh, one retry if it fails or is empty;
# a completed output (one with a CURRENT RATING line) is skipped. <input> is a dir under gap/inputs (paper, paper-ctl,
# B01..B15, B09-ctl); <model> is sol2 or gemini. Paper inputs get G1 and their own reference-1..3; note pieces get G1N
# and note-refs/reference-1..4. Output: gap/runs/G__<input>__<model>.txt. Status goes to gap/runs/status.tsv.
# Each attempt is killed after GAP_TIMEOUT seconds (default 900; rc=124), added 2026-10-29 after five agy runs printed
# a full answer but never exited. Attempts are numbered on from status.tsv, so a rerun makes only the one retry left.
# GAP_SUB (default gap) is the directory of inputs and runs; GAP_PAPER_PROMPT (default prompts/G1.prompt.txt) is the
# paper prompt. G1b runs set GAP_SUB=g1b and GAP_PAPER_PROMPT=prompts/G1b.prompt.txt.
R=$(cd "$(dirname "$0")/.." && pwd); inp=$1; m=$2; S=${GAP_SUB:-gap}; I=$R/$S/inputs
cd "$R"; mkdir -p $S/runs; out=$S/runs/G__${inp}__${m}.txt
[ -s "$out" ] && grep -q 'CURRENT RATING:' "$out" && exit 0
case $inp in
  paper|paper-ctl) p=${GAP_PAPER_PROMPT:-prompts/G1.prompt.txt}; set -- "$I/$inp"/reference-{1,2,3}.txt "$I/$inp/manuscript.txt" ;;
  B[0-9][0-9]|B[0-9][0-9]-ctl) p=prompts/G1N.prompt.txt; set -- "$I"/note-refs/reference-{1,2,3,4}.txt "$I/$inp/chapter.txt" ;;
  *) echo "unknown input $inp" >&2; exit 2 ;;
esac
for f in "$@"; do [ -s "$f" ] || { echo "missing $f" >&2; exit 2; }; done
# with_timeout SECS CMD...: run CMD in its own process group; after SECS, TERM then KILL the whole group (agy included).
# Returns CMD's status, or 124 on timeout. bash 3.2 has no `timeout`, and coreutils is not installed. The watcher's
# flag is written only if its sleep ran out (`&&`), so killing the watcher early can never mark a timeout.
with_timeout() {
  local secs=$1; shift; local flag; flag=$(mktemp "${TMPDIR:-/tmp}/.tmo.XXXXXX"); rm -f "$flag"
  set -m; "$@" & local pid=$!; set +m
  ( sleep "$secs" && { : > "$flag"; kill -TERM -- -$pid 2>/dev/null; sleep 5; kill -KILL -- -$pid 2>/dev/null; } ) &
  local w=$!; wait $pid; local rc=$?
  # On a timeout, let the watcher finish: CMD may die on TERM while a child that ignores TERM (agy) lives on in the
  # group until the KILL. Killing the watcher here would orphan that child; it did on 2026-10-29.
  if [ -e "$flag" ]; then wait $w 2>/dev/null; rm -f "$flag"; return 124; fi
  pkill -P $w sleep 2>/dev/null; kill -TERM $w 2>/dev/null; wait $w 2>/dev/null; rm -f "$flag"
  return $rc
}
done_n=$(awk -F'\t' -v i="$inp" -v m="$m" '$1==i && $2==m' $S/runs/status.tsv 2>/dev/null | wc -l | tr -d ' ')
for a in 1 2; do
  [ $a -le $done_n ] && continue
  t0=$(date +%s); XMODEL_DIR=$R/x with_timeout "${GAP_TIMEOUT:-900}" bash tools/run_x.sh "$m" "$p" "$out" "$@" > /dev/null 2>&1; rc=$?
  w=$(wc -w < "$out" 2>/dev/null || echo 0)
  printf '%s\t%s\tattempt=%s\trc=%s\twords=%s\tsecs=%s\t%s\n' "$inp" "$m" $a $rc $w $(( $(date +%s) - t0 )) "$(date +%T)" >> $S/runs/status.tsv
  [ $rc -eq 0 ] && [ "$w" -gt 0 ] && exit 0
done
exit 1
