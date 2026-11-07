#!/bin/bash
# Every 15 min: read-only fetch (q.sh) and flags.py against the baseline $1 (default proj.txt).
# END-SLIP and OVER-1.3MEAN (fixed: proj.txt + out.txt, the 15:22 snapshot) exit at once. RUN-OVER-MAX lines (a correlated slowdown makes them fire on most runs) are appended,
# deduplicated by label, to overmax.log and the watch continues; it prints the count each cycle.
# Also exits when no cov2d job at or after 60895562 is RUNNING or PENDING.
P=$(cd "$(dirname "$0")" && pwd); BASE=${1:-$P/proj.txt}; touch $P/overmax.log
for i in $(seq 1 60); do
  ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 bash -s" < $P/q.sh > $P/now.txt 2>&1 || { echo "fetch failed"; sleep 600; continue; }
  python3 -I -B $P/flags.py $BASE $P/now.txt $P/proj.txt $P/out.txt > $P/flags.out; rc=$?
  [ "$rc" = 0 ] || [ "$rc" = 3 ] || { cat $P/flags.out; echo "flags.py rc=$rc (a crash: not a flag)"; exit 0; }
  grep '^FLAG RUN-OVER-MAX' $P/flags.out | while read -r l; do grep -qF "$(echo "$l" | cut -d' ' -f3-4) " $P/overmax.log || echo "$(head -1 $P/flags.out | cut -d' ' -f1) $l" >> $P/overmax.log; done
  echo "$(head -1 $P/flags.out) | overmax.log=$(wc -l < $P/overmax.log | tr -d ' ')"
  grep -qE '^FLAG (END-SLIP|OVER-1.3MEAN)' $P/flags.out && { grep -E '^FLAG (END-SLIP|OVER-1.3MEAN)' $P/flags.out; cp $P/now.txt $P/flag-snapshot.txt; echo FLAGGED; exit 0; }
  awk -F'|' '$2 ~ /^cov2d-/ && $1 >= 60895562 && $3 ~ /^(RUNNING|PENDING)/' $P/now.txt | grep -q . || { echo BASELINE-ENDED; exit 0; }
  sleep 900
done
echo expired
