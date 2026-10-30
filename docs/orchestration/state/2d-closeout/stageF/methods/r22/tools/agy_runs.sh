#!/usr/bin/env bash
# usage: M=<stageF/methods> XMODEL_DIR=<scratch> agy_runs.sh <agy-dir>   -- runs agy (gemini via run_x.sh) on every
# chunk's pairs.txt and pairs-control.txt with prompt.txt; gapjob.sh's with_timeout (900 s) and one retry; 3 at a time.
set -u
T=$(cd "$(dirname "$0")" && pwd); export RX=$M/register-method/tools/run_x.sh A=$1 T XMODEL_DIR
one() { d=$1; k=$2; out=$A/$d/agy-$k.txt
  eval "$(sed -n '/^with_timeout() {/,/^}/p' "$T/gapjob.sh")"
  grep -q '^END' "$out" 2>/dev/null && return 0
  in=$A/$d/pairs.txt; [ "$k" = control ] && in=$A/$d/pairs-control.txt
  for a in 1 2; do with_timeout 900 bash "$RX" gemini "$A/prompt.txt" "$out" "$in" > /dev/null 2>&1 < /dev/null; rc=$?
    printf '%s\t%s\tattempt=%s\trc=%s\n' "$d" "$k" $a $rc >> "$A/status.tsv"
    [ "$rc" = 0 ] && grep -q '^END' "$out" && return 0; done; }
export -f one
for d in $(cd "$A" && ls -d chunk*); do echo "$d real"; echo "$d control"; done | xargs -P 3 -L 1 bash -c 'one "$@"' _
