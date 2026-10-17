#!/bin/bash
# Gate-then-submit each batch in order (DESIGN §14.4 step 4). For each batch:
#   wait >= 130 s after the previous submit (sacct lags sbatch);
#   run `gate`; require rc 0 and ledger in-flight job count == squeue job count;
#   run `submit`; require rc 0.
# Any refusal, non-zero rc or count mismatch: print it and exit 1 (the closer decides; only the three navigation
# refusals named in the binding §3.4 are not stops).
set -u
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
for B in "$@"; do
  sleep 130
  out=$(ssh -o ConnectTimeout=30 -o BatchMode=yes saul.nersc.gov "NS=$NS; B=$B"'
    cd $NS/repo_k/docs/orchestration/state/2d-closeout/stageC/production || exit 9
    source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1
    q=$(squeue -h -u josephrb | wc -l)
    USER=josephrb python3 launch.py gate $B > $NS/gatelog/${B}_gate.txt 2>&1; g=$?
    n=$(grep "in-flight at cap" $NS/gatelog/${B}_gate.txt | grep -vc "^GATE")
    echo "$(date -u +%FT%TZ) $B gate rc=$g squeue=$q ledger_inflight=$n"
    grep -E "^GATE|REFUSE" $NS/gatelog/${B}_gate.txt
    [ $g -eq 0 ] || exit 4
    [ "$q" -eq "$n" ] || { echo "COUNT MISMATCH"; exit 5; }
    USER=josephrb python3 launch.py submit $B > $NS/gatelog/${B}_submit.txt 2>&1; s=$?
    echo "$(date -u +%FT%TZ) $B submit rc=$s"
    grep -E "^GATE|REFUSE" $NS/gatelog/${B}_submit.txt
    grep -A1 "^+ sbatch" $NS/gatelog/${B}_submit.txt | grep -v "^+ sbatch\|^--" | tr "\n" " "; echo
    [ $s -eq 0 ] || exit 6')
  rc=$?
  echo "$out"
  [ $rc -eq 0 ] || { echo "STOPPED at $B rc=$rc"; exit 1; }
done
echo "ALL SUBMITTED: $*"
