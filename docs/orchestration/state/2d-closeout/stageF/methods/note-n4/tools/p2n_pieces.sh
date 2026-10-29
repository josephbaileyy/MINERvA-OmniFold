#!/usr/bin/env bash
# usage: p2n_pieces.sh <old-pieces-dir> <new-pieces-dir> <out-dir> <piece ids...>
# P2N (blind pairwise, note framing) per piece, both orders (AB: A = old; BA: A = new), with sol2 and gemini; one retry
# each; at most 2 concurrent runs per model. Outputs <out>/<id>.<model>.<AB|BA>.md and prints the WINNER lines.
# The n1-n3 script (lane scratchpad xmodel/p2n_pieces.sh), with its paths taken from this file's own location.
set -u
M=$(cd "$(dirname "$0")/../.." && pwd)
export RX=$M/register-method/tools/run_x.sh PR=$M/note-rating/P2N.prompt.txt
export XMODEL_DIR=${XMODEL_DIR:?set XMODEL_DIR to a scratch directory} OLD=$1 NEW=$2 OUT=$3; shift 3
mkdir -p "$OUT"
one() { m=$1; id=$2; o=$3; out=$OUT/$id.$m.$o.md
  grep -q 'WINNER:' "$out" 2>/dev/null && return 0
  d=$OUT/$id.$o; mkdir -p "$d"
  if [ "$o" = AB ]; then cp "$OLD/$id.txt" "$d/Document_A.txt"; cp "$NEW/$id.txt" "$d/Document_B.txt"
  else cp "$NEW/$id.txt" "$d/Document_A.txt"; cp "$OLD/$id.txt" "$d/Document_B.txt"; fi
  for a in 1 2; do bash "$RX" "$m" "$PR" "$out" "$d/Document_A.txt" "$d/Document_B.txt" >> "$OUT/runs.log" 2>&1
    grep -q 'WINNER:' "$out" 2>/dev/null && return 0
    grep -q 'usage limit' "$out.log" 2>/dev/null && { echo "$id $m $o QUOTA" >> "$OUT/runs.log"; return 0; }
    [ -f "$out" ] && mv "$out" "$out.failed$a"; done
  echo "$id $m $o FAILED" >> "$OUT/runs.log"; }
export -f one
( for id in "$@"; do echo "sol2 $id AB"; echo "sol2 $id BA"; done | xargs -P 2 -L 1 bash -c 'one "$@"' _ ) &
( for id in "$@"; do echo "gemini $id AB"; echo "gemini $id BA"; done | xargs -P 2 -L 1 bash -c 'one "$@"' _ ) &
wait
for id in "$@"; do
  w=""; for m in sol2 gemini; do for o in AB BA; do x=$(grep -m1 -o 'WINNER: [AB]' "$OUT/$id.$m.$o.md" 2>/dev/null | cut -c9); s=$(grep -m1 -o 'STRENGTH: [123]' "$OUT/$id.$m.$o.md" 2>/dev/null | cut -c11)
    if [ -z "$x" ]; then v="?"; elif { [ "$o" = AB ] && [ "$x" = B ]; } || { [ "$o" = BA ] && [ "$x" = A ]; }; then v="NEW$s"; else v="OLD$s"; fi
    w="$w $m.$o=$v"; done; done
  echo "$id:$w"; done
