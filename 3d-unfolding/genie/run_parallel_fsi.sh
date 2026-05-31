#!/bin/bash
# run_parallel_fsi.sh [DIAL] [NTWK] [MIN] [MAX]
# Fan grwght1p out across the 8 CV shards (work_p1..8) for one FSI dial, in
# parallel, mirroring run_parallel_cv.sh. Each shard's weights land beside its
# gst as work_p<i>/weights_<DIAL>.root (eventnum aligned to that shard's gst).
# Then fsi_variation_xsec3d.py consumes all 8 (gst, weights) pairs.
DIAL=${1:-FrInel_pi}
NTWK=${2:-3}
MIN=${3:--1}
MAX=${4:-1}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
echo "[parallel-fsi] dial=$DIAL t=$NTWK [$MIN,$MAX] start $(date -u '+%F %T UTC')"
for i in 1 2 3 4 5 6 7 8; do
  GHEP=$(ls work_p$i/gntp.*.ghep.root 2>/dev/null | head -1)
  [ -n "$GHEP" ] || { echo "[parallel-fsi] no ghep in work_p$i -- skipping"; continue; }
  bash run_fsi_reweight.sh "$GHEP" "$DIAL" "$NTWK" "$MIN" "$MAX" \
       "work_p$i/weights_${DIAL}.root" > "fsi_${DIAL}_p$i.out" 2>&1 &
done
wait
echo "[parallel-fsi] all done $(date -u '+%F %T UTC')"
ls -la work_p*/weights_${DIAL}.root 2>/dev/null | awk '{print $5,$NF}'
