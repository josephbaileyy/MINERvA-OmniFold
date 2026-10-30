#!/usr/bin/env bash
# usage: M=<stageF/methods dir> XMODEL_DIR=<scratch> step2p_runs.sh <old-manuscript> <new-manuscript> <out-dir>
# r22 Step 2's paper adoption runs (STEP2-PAPER.md section 4; STEP2-PLAN.md section 4, the paper rule, as r21):
#   - P2 blind pairwise (rater-calibration/prompts/P2.prompt.txt), sol2 and gemini, both orders (AB: A = old;
#     BA: A = new), on the blinded rater copies (make_rater_copy.sh's .blind.txt);
#   - P1 (rater-calibration/prompts/P1.prompt.txt) on NEW, sol2 x3 (r1-r3).
# step2_runs.sh's layout, with gapjob.sh's tested with_timeout (900 s) and one retry per run. A run that fails both
# attempts is logged FAILED; the adoption rule counts a failed pairwise run as a loss for NEW.
# Outputs: <out>/<P2|P1>.paper.<model>.<AB|BA|rN>.md and <out>/status.tsv.
set -u
T=$(cd "$(dirname "$0")" && pwd); M=${M:?set M to the stageF/methods directory}
export RX=$M/register-method/tools/run_x.sh P2=$M/rater-calibration/prompts/P2.prompt.txt P1=$M/rater-calibration/prompts/P1.prompt.txt
export XMODEL_DIR=${XMODEL_DIR:?set XMODEL_DIR to a scratch directory} OLD=$1 NEW=$2 OUT=$3 T
mkdir -p "$OUT"
one() { kind=$1; m=$2; o=$3; out=$OUT/$kind.paper.$m.$o.md
  eval "$(sed -n '/^with_timeout() {/,/^}/p' "$T/gapjob.sh")"
  if [ "$kind" = P2 ]; then want=WINNER:; else want=RATING:; fi
  grep -q "$want" "$out" 2>/dev/null && return 0
  d=$OUT/in.$kind.$o; mkdir -p "$d"
  if [ "$kind" = P2 ]; then p=$P2
    if [ "$o" = AB ]; then cp "$OLD" "$d/Document_A.txt"; cp "$NEW" "$d/Document_B.txt"
    else cp "$NEW" "$d/Document_A.txt"; cp "$OLD" "$d/Document_B.txt"; fi
    set -- "$d/Document_A.txt" "$d/Document_B.txt"
  else p=$P1; cp "$NEW" "$d/manuscript.txt"; set -- "$d/manuscript.txt"; fi
  for a in 1 2; do t0=$(date +%s)
    with_timeout 900 bash "$RX" "$m" "$p" "$out" "$@" > /dev/null 2>&1 < /dev/null; rc=$?
    printf '%s\t%s\t%s\tattempt=%s\trc=%s\tsecs=%s\n' "$kind" "$m" "$o" $a $rc $(( $(date +%s) - t0 )) >> "$OUT/status.tsv"
    [ "$rc" = 0 ] && grep -q "$want" "$out" 2>/dev/null && return 0
    [ -f "$out" ] && mv "$out" "$out.failed$a"
  done
  printf '%s\t%s\t%s\tFAILED\n' "$kind" "$m" "$o" >> "$OUT/status.tsv"; }
export -f one
( printf '%s\n' "P2 sol2 AB" "P2 sol2 BA" "P1 sol2 r1" "P1 sol2 r2" "P1 sol2 r3" | xargs -P 3 -L 1 bash -c 'one "$@"' _ ) &
( printf '%s\n' "P2 gemini AB" "P2 gemini BA" | xargs -P 2 -L 1 bash -c 'one "$@"' _ ) &
wait
