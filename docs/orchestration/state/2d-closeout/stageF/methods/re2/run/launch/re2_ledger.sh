#!/bin/bash
# RE-2 ledger from sacct:  re2_ledger.sh JOBID [JOBID ...] > ledger.tsv (a copy of re1_ledger.sh)
# charge (node-h) = ElapsedRaw / 3600 x billing / 256, as RE-1's first pass and the XR ledgers compute it.
set -eo pipefail
printf 'jobid\tname\tqos\tstate\tstart\tend\telapsed_s\tbilling\tcharge_node_h\n'
ids=$(IFS=,; echo "$*")
sacct -j "$ids" -X -n -P -o JobID,JobName,QOS,State,Start,End,ElapsedRaw,AllocTRES | while IFS='|' read -r id name qos state start end el tres; do
    billing=$(tr ',' '\n' <<<"$tres" | sed -n 's/^billing=//p'); billing=${billing:-0}
    awk -v id="$id" -v n="$name" -v q="$qos" -v s="$state" -v a="$start" -v e="$end" -v el="$el" -v b="$billing" \
        'BEGIN { printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.4f\n", id, n, q, s, a, e, el, b, el / 3600 * b / 256 }'
done
