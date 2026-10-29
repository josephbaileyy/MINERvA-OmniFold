#!/usr/bin/env bash
# usage: p1n_pieces.sh <round-dir>  -- P1N on every <round-dir>/pieces/N*.txt: 2 sol2 runs + 1 gemini run per piece,
# one retry each, at most 3 concurrent runs per model. Outputs <round-dir>/p1n/<piece>.<model>.<k>.md.
# The n1-n3 script (lane scratchpad xmodel/p1n_pieces.sh), with its paths taken from this file's own location.
set -u
M=$(cd "$(dirname "$0")/../.." && pwd)                       # .../stageF/methods
export RX=$M/register-method/tools/run_x.sh P=$M/rater-calibration/prompts/P1N.prompt.txt R=$1
export XMODEL_DIR=${XMODEL_DIR:?set XMODEL_DIR to a scratch directory}
mkdir -p "$R/p1n"
one() { m=$1; f=$2; k=$3; id=$(basename "$f" .txt); out=$R/p1n/$id.$m.$k.md
  grep -q 'RATING:' "$out" 2>/dev/null && return 0
  for a in 1 2; do bash "$RX" "$m" "$P" "$out" "$f" >> "$R/p1n/runs.log" 2>&1
    grep -q 'RATING:' "$out" 2>/dev/null && return 0; [ -f "$out" ] && mv "$out" "$out.failed$a"; done
  echo "$id $m $k FAILED" >> "$R/p1n/runs.log"; }
export -f one
( for f in "$R"/pieces/N*.txt; do echo "sol2 $f 1"; echo "sol2 $f 2"; done | xargs -P 3 -L 1 bash -c 'one "$@"' _ ) &
( for f in "$R"/pieces/N*.txt; do echo "gemini $f 1"; done | xargs -P 3 -L 1 bash -c 'one "$@"' _ ) &
wait
grep -H 'RATING:' "$R"/p1n/*.md | sort
