#!/bin/bash
# The director's batch go (2026-11-13): "go ebf576f5 with D_Uc 031819cc, D_Ud 900df2ba, G18_Ua a5948d2e, G18_Ub 5307f0bf,
# G18_Uc defd7291, G18_Ud e59b87dc, AR23_Ua 5d67b502, AR23_Ub 426c6e06, AR23_Uc ff10dec1, AR23_Ud 1f277af0".
# Sequential, in that order. Before each: the launcher and the connect re-hashed against the go (full sha256 from
# connects-batch.sha256.txt, whose prefixes are the go's). Each launch must end rc 0 with the connect's log showing
# "submit <job> rc=0", a job id, DONE, and no STOP line; and the balance's half (the connect's balance line) at least
# LL5D's cap plus G2R's cap (148 + 110 = 258, which bounds both lanes' remaining). Anything else halts the rest: exit 1.
#     bash launch-batch.sh            (from this directory)
set -u
H=$(cd "$(dirname "$0")" && pwd); cd "$H" || exit 2
L=ebf576f5374ea778be3d43173a733a9b612f529fefa64f694f67a66d31c82170
GO="D_Uc:031819cc D_Ud:900df2ba G18_Ua:a5948d2e G18_Ub:5307f0bf G18_Uc:defd7291 G18_Ud:e59b87dc AR23_Ua:5d67b502 AR23_Ub:426c6e06 AR23_Uc:ff10dec1 AR23_Ud:1f277af0"
NEED=258.0
halt() { echo "HALT $(date -u +%FT%TZ) $*"; exit 1; }
echo "batch start $(date -u +%FT%TZ)"
for pair in $GO; do
    j=${pair%%:*}; pre=${pair#*:}
    want=$(awk -v j="$j" '$1 == j {print $2}' connects-batch.sha256.txt)
    [ "${want:0:8}" = "$pre" ] || halt "$j: connects-batch.sha256.txt has $want, not the go's $pre"
    have=$(shasum -a 256 "connect-g2r-$j.sh" | cut -c1-64); lh=$(shasum -a 256 launch-g2r.sh | cut -c1-64)
    echo "== $j $(date -u +%FT%TZ) connect=$have launcher=$lh"
    [ "$have" = "$want" ] || halt "$j: connect is $have, not $want"
    [ "$lh" = "$L" ] || halt "launcher is $lh, not $L"
    [ -e "run-$j" ] && halt "$j: run-$j exists"
    bash launch-g2r.sh "$j" "$want" > "launch-$j-stdout.txt" 2>&1; lrc=$?
    log=run-$j/connect.log
    echo "   launcher rc=$lrc; $(grep -E '^(balance_node_h|recompute)' "$log" 2>/dev/null | tr '\n' ' ')"
    grep -E "^(realization|submit $j rc=)" "$log" 2>/dev/null | sed 's/^/   /'
    grep -E " job=$j id=[0-9]+ " "$log" 2>/dev/null | tail -1 | sed 's/^/   /'
    [ "$lrc" = 0 ] || halt "$j: launcher rc=$lrc (see launch-$j-stdout.txt)"
    grep -q '^STOP' "$log" && halt "$j: the connect STOPped: $(grep '^STOP' "$log")"
    grep -qx "submit $j rc=0" "$log" || halt "$j: no 'submit $j rc=0' in $log"
    grep -qE " job=$j id=[0-9]+ " "$log" || halt "$j: no job id in $log"
    [ "$(tail -1 "$log")" = DONE ] || halt "$j: $log does not end with DONE"
    half=$(sed -n 's/^balance_node_h=[0-9.]* half=\([0-9.]*\) .*/\1/p' "$log")
    [ -n "$half" ] && awk -v h="$half" -v n="$NEED" 'BEGIN{exit !(h >= n)}' || halt "$j: the balance's half ${half:-unread} is below $NEED"
    echo "   ok half=$half >= $NEED"
done
echo "BATCH DONE $(date -u +%FT%TZ)"
