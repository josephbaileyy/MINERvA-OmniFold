#!/bin/bash
# Move pending indices of a regular toy array into another QOS lane, <= MAXN at a time.
# Usage: qos_feeder.sh ARR QOS MAXN ORDER(head|tail) "EXTRA SBATCH ARGS"
# Same index => same seeds and the same output path; outputs publish atomically.
ARR=$1; QOS=$2; MAXN=$3; ORDER=$4; EXTRA=$5
H=josephrb@perlmutter.nersc.gov
fails=0
while true; do
  out=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $H "
    nd=\$(squeue -h -u josephrb -q $QOS -n cov2d_fixedtruth | wc -l)
    pend=\$(squeue -h -r -j $ARR -t PD -o %K | sort -n | $ORDER -1)
    if [ -z \"\$pend\" ]; then echo DONE; exit 0; fi
    if [ \"\$nd\" -lt $MAXN ]; then
      scancel --state=PENDING ${ARR}_\$pend
      for k in 1 2 3 4 5 6; do sleep 5; st=\$(squeue -h -r -j $ARR -o '%K %T' | awk -v i=\$pend '\$1==i{print \$2}'); [ \"\$st\" != PENDING ] && break; done
      if [ -n \"\$st\" ]; then echo \"SKIP \$pend state=\$st\"; exit 0; fi
      if squeue -h -u josephrb -n cov2d_fixedtruth -r -o %K | grep -qx \"\$pend\"; then echo \"SKIP \$pend taken\"; exit 0; fi
      if [ -e /pscratch/sd/j/josephrb/coverage-2d-20261005/toys/toy\$pend.root.done ]; then echo \"SKIP \$pend done\"; exit 0; fi
      cd /pscratch/sd/j/josephrb/MINERvA-OmniFold-2d-coverage-20261005 && \
      j=\$(sbatch --parsable --qos=$QOS $EXTRA --array=\$pend 2d-unfolding/uq/coverage_fixed_truth/sbatch_fixed_truth_toys.sh) && \
      echo \"MOVED \$pend -> $QOS \$j\"
    else echo WAIT; fi" 2>&1)
  rc=$?
  if [ $rc -ne 0 ]; then fails=$((fails+1)); echo "$(date -u +%FT%TZ) ssh fail $fails: $out"; [ $fails -ge 8 ] && { echo STOP-ssh; exit 1; }; sleep 120; continue; fi
  fails=0
  case "$out" in *DONE*) echo "$(date -u +%FT%TZ) no pending tasks in $ARR"; exit 0;; *MOVED*|*SKIP*) echo "$(date -u +%FT%TZ) $out"; sleep 5; continue;; esac
  sleep 90
done
