#!/bin/bash
# Fan out 8 gevgen runs (250k each = 2M) across the node's cores, then hadd.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
echo "[parallel] start $(date -u '+%F %T UTC')"
for i in 1 2 3 4 5 6 7 8; do
  bash run_gevgen.sh 250000 $((10+i)) "p$i" > "par_p$i.out" 2>&1 &
done
wait
echo "[parallel] all gevgen done $(date -u '+%F %T UTC')"
ls -la work_p*/genie_mefhc_p*.gst.root 2>/dev/null | awk '{print $5,$NF}'
# hadd combined gst
source ./setup_genie.sh >/dev/null 2>&1
hadd -f genie_mefhc_cv.gst.root work_p*/genie_mefhc_p*.gst.root > hadd_cv.log 2>&1
echo "[parallel] hadd rc=$? -> genie_mefhc_cv.gst.root $(ls -la genie_mefhc_cv.gst.root 2>/dev/null|awk '{print $5}')"
echo "[parallel] done $(date -u '+%F %T UTC')"
