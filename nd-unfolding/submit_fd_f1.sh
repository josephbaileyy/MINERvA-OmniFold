#!/bin/bash
# F1's submission lines (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md sections 0 and 6), so the
# account, QOS, constraint, time limit and arguments of every F1 job are committed, not typed.
#
#   submit_fd_f1.sh f1a <deploy> <pin> <OUT>
#   submit_fd_f1.sh f1b <deploy> <pin> <OUT>          --time from <OUT>/f1a/budget.json (f1b_time_limit); GO required
#   submit_fd_f1.sh f1c <deploy> <pin> <OUT> <table>  <table>: tasks-f1c.tsv inside the deploy (the receipt commit)
#   submit_fd_f1.sh f1a2 <deploy> <pin> <OUT> <priced> <ceiling>  the re-pilot (amendment 1), with the binding's
#                                                      priced F1 total and ceiling
#   submit_fd_f1.sh f1b2 <deploy> <pin> <OUT>          --time from <OUT>/f1a2/budget2.json (f1b2_time_limit); GO required
#
# Every job: account m3246, QOS regular (never premium), constraint cpu, one exclusive node, --no-requeue, no GPU.
set -eo pipefail
STAGE="${1:?f1a|f1b|f1c}"; D="${2:?deploy}"; PIN="${3:?pin}"; OUT="${4:?out}"
mkdir -p "$OUT/logs"
COMMON=(--account=m3246 --qos=regular --constraint=cpu --nodes=1 --exclusive --no-requeue
        --output="$OUT/logs/%x_%j.out")
case "$STAGE" in
  f1a)
    sbatch "${COMMON[@]}" --time=00:20:00 --job-name=fd_f1a "$D/nd-unfolding/sbatch_fd_f1a.sh" "$D" "$PIN" "$OUT" ;;
  f1b)
    B="$OUT/f1a/budget.json"
    grep -q '"decision": "GO"' "$B" || { echo "refusing: $B is not GO" >&2; exit 2; }
    T=$(sed -n 's/.*"f1b_time_limit": "\([0-9][0-9]:[0-9][0-9]:00\)".*/\1/p' "$B")
    [ -n "$T" ] || { echo "refusing: no f1b_time_limit in $B" >&2; exit 2; }
    sbatch "${COMMON[@]}" --time="$T" --job-name=fd_f1b "$D/nd-unfolding/sbatch_fd_f1b.sh" "$D" "$PIN" "$OUT" ;;
  f1c)
    TABLE="${5:?table}"
    [ -f "$TABLE" ] && case "$TABLE" in "$D"/*) ;; *) false ;; esac || { echo "refusing: $TABLE is not in $D" >&2; exit 2; }
    [ ! -e "$OUT/f1c" ] || { echo "refusing: $OUT/f1c exists" >&2; exit 2; }
    sbatch "${COMMON[@]}" --time=00:54:00 --job-name=fd_f1c \
      "$D/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
      "$D" "$PIN" "$TABLE" "$OUT/f1c" 32 56G 0 7 none ;;
  f1a2)
    PRICED="${5:?priced node-h}"; CEIL="${6:?ceiling node-h}"
    sbatch "${COMMON[@]}" --time=00:20:00 --job-name=fd_f1a2 "$D/nd-unfolding/sbatch_fd_f1a2.sh" "$D" "$PIN" "$OUT" "$PRICED" "$CEIL" ;;
  f1b2)
    B="$OUT/f1a2/budget2.json"
    grep -q '"decision": "GO"' "$B" || { echo "refusing: $B is not GO" >&2; exit 2; }
    T=$(sed -n 's/.*"f1b2_time_limit": "\([0-9][0-9]:[0-9][0-9]:00\)".*/\1/p' "$B")
    [ -n "$T" ] || { echo "refusing: no f1b2_time_limit in $B" >&2; exit 2; }
    sbatch "${COMMON[@]}" --time="$T" --job-name=fd_f1b2 "$D/nd-unfolding/sbatch_fd_f1b2.sh" "$D" "$PIN" "$OUT" ;;
  *) echo "unknown stage $STAGE" >&2; exit 2 ;;
esac
