#!/bin/bash
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$HERE"
echo "[parallel-nuwro] start $(date -u '+%F %T UTC')"
for i in 1 2 3 4 5 6 7 8; do
  bash run_nuwro.sh 250000 $((20+i)) "p$i" > "par_nuwro_p$i.out" 2>&1 &
done
wait
echo "[parallel-nuwro] all done $(date -u '+%F %T UTC')"
ls -la work_nuwro_p*/nuwro_flat.root 2>/dev/null | awk '{print $5,$9}'
