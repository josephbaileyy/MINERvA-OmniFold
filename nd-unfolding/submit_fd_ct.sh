#!/bin/bash
# The cheap tier's submission lines (state/measurement-paper/5d-community-20261024/FD-CT-3B-DECLARATION.md section 2),
# so the account, QOS, constraint, time limit and arguments of every cheap-tier job are committed, not typed.
#
#   submit_fd_ct.sh 3b <deploy> <pin> <B>   one node, eight lanes of 3b-steps.tsv (13 mismatch closures)
#
# Every job: account m3246, QOS regular (never premium), constraint cpu, one exclusive node, --no-requeue, no GPU.
set -eo pipefail
STAGE="${1:?3b}"; D="${2:?deploy}"; PIN="${3:?pin}"; B="${4:?B}"
REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/3b
mkdir -p "$B/logs"
COMMON=(--account=m3246 --qos=regular --constraint=cpu --nodes=1 --exclusive --no-requeue
        --output="$B/logs/%x_%j.out")
case "$STAGE" in
  3b)
    TABLE="$D/$REL/tasks-3b.tsv"
    [ -f "$TABLE" ] || { echo "refusing: $TABLE is missing" >&2; exit 2; }
    [ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "refusing: $D is not at $PIN" >&2; exit 2; }
    [ ! -e "$B/closures" ] && [ ! -e "$B/lanes" ] || { echo "refusing: $B/closures or $B/lanes exists" >&2; exit 2; }
    mkdir -p "$B/closures"
    sbatch "${COMMON[@]}" --time=00:45:00 --job-name=fd_ct_3b \
      "$D/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
      "$D" "$PIN" "$TABLE" "$B/lanes" 32 56G 0 7 none ;;
  *)
    echo "refusing: unknown stage $STAGE" >&2; exit 2 ;;
esac
