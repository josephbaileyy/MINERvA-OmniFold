#!/usr/bin/env bash
# usage: M=<stageF/methods dir> XMODEL_DIR=<scratch> step2_runs.sh <old-pieces-dir> <new-pieces-dir> <out-dir> <ids...>
# r22 Step 2's adoption runs (STEP2-PLAN.md §4), per note piece:
#   - P2N blind pairwise (note-rating/P2N.prompt.txt), sol2 and gemini, both orders (AB: A = old; BA: A = new);
#   - P1N (rater-calibration/prompts/P1N.prompt.txt) on NEW, sol2 x3 (r1-r3).
# note-n4/tools/p2n_pieces.sh's layout, with gapjob.sh's tested with_timeout (900 s; TERM, then KILL the process
# group) and one retry per run. A run that fails both attempts is logged FAILED; the adoption rule counts a failed
# pairwise run as a loss for NEW. At most 3 concurrent runs per model. Outputs: <out>/<P2N|P1N>.<id>.<model>.<AB|BA|rN>.md
# and <out>/status.tsv.
set -u
T=$(cd "$(dirname "$0")" && pwd); M=${M:?set M to the stageF/methods directory}
export RX=$M/register-method/tools/run_x.sh P2N=$M/note-rating/P2N.prompt.txt P1N=$M/rater-calibration/prompts/P1N.prompt.txt
export XMODEL_DIR=${XMODEL_DIR:?set XMODEL_DIR to a scratch directory} OLD=$1 NEW=$2 OUT=$3 T; shift 3
mkdir -p "$OUT"
one() { kind=$1; m=$2; id=$3; o=$4; out=$OUT/$kind.$id.$m.$o.md
  eval "$(sed -n '/^with_timeout() {/,/^}/p' "$T/gapjob.sh")"
  if [ "$kind" = P2N ]; then want=WINNER:; else want=RATING:; fi
  grep -q "$want" "$out" 2>/dev/null && return 0
  d=$OUT/in.$kind.$id.$o; mkdir -p "$d"
  if [ "$kind" = P2N ]; then p=$P2N
    if [ "$o" = AB ]; then cp "$OLD/$id.txt" "$d/Document_A.txt"; cp "$NEW/$id.txt" "$d/Document_B.txt"
    else cp "$NEW/$id.txt" "$d/Document_A.txt"; cp "$OLD/$id.txt" "$d/Document_B.txt"; fi
    set -- "$d/Document_A.txt" "$d/Document_B.txt"
  else p=$P1N; cp "$NEW/$id.txt" "$d/chapter.txt"; set -- "$d/chapter.txt"; fi
  for a in 1 2; do t0=$(date +%s)
    with_timeout 900 bash "$RX" "$m" "$p" "$out" "$@" > /dev/null 2>&1 < /dev/null; rc=$?
    printf '%s\t%s\t%s\t%s\tattempt=%s\trc=%s\tsecs=%s\n' "$kind" "$id" "$m" "$o" $a $rc $(( $(date +%s) - t0 )) >> "$OUT/status.tsv"
    [ "$rc" = 0 ] && grep -q "$want" "$out" 2>/dev/null && return 0
    [ -f "$out" ] && mv "$out" "$out.failed$a"
  done
  printf '%s\t%s\t%s\t%s\tFAILED\n' "$kind" "$id" "$m" "$o" >> "$OUT/status.tsv"; }
export -f one
( for id in "$@"; do echo "P2N sol2 $id AB"; echo "P2N sol2 $id BA"; for r in r1 r2 r3; do echo "P1N sol2 $id $r"; done; done \
  | xargs -P 3 -L 1 bash -c 'one "$@"' _ ) &
( for id in "$@"; do echo "P2N gemini $id AB"; echo "P2N gemini $id BA"; done | xargs -P 3 -L 1 bash -c 'one "$@"' _ ) &
wait
