#!/bin/bash
# For each batch in order: every SLEEP s run `gate`. "NOT ADMITTED" (packs in flight) is a wait (DESIGN §6/§14.3).
# rc 0 with every squeue job (read first) present in the ledger: submit (rc must be 0), then wait 130 s before the next gate.
# Anything else (another refusal, a mismatch, a submit failure): print and exit 1. 5 transport failures: exit 2.
set -u
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
SLEEP=${SLEEP:-600}
for B in "$@"; do
  fail=0
  while :; do
    out=$(ssh -o ConnectTimeout=30 -o BatchMode=yes saul.nersc.gov "NS=$NS; B=$B"'
      cd $NS/repo_k/docs/orchestration/state/2d-closeout/stageC/production || exit 9
      source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1
      sq=$(squeue -h -u josephrb -o %i) || exit 8; q=$(printf "%s\n" "$sq" | grep -c .)
      USER=josephrb python3 launch.py gate $B > $NS/gatelog/${B}_gate.txt 2>&1; g=$?
      n=$(grep "in-flight at cap" $NS/gatelog/${B}_gate.txt | grep -vc "^GATE")
      # coverage: every squeue job (read BEFORE the gate) must have a ledger line (in flight, or terminal and charged
      # actual if it ended in between). A job missing from the ledger = sacct lag on a submit: refuse.
      miss=$(for j in $sq; do grep -q "^ *$j " $NS/gatelog/${B}_gate.txt || echo $j; done)
      echo "$(date -u +%FT%TZ) $B gate rc=$g squeue=$q ledger_inflight=$n missing_from_ledger=[$miss]"
      grep -E "^GATE|REFUSE|NOT ADMITTED|STOP" $NS/gatelog/${B}_gate.txt
      if [ $g -eq 3 ] && grep -q "^NOT ADMITTED" $NS/gatelog/${B}_gate.txt; then exit 10; fi
      [ $g -eq 0 ] || exit 4
      [ -z "$miss" ] && [ "$n" -le "$q" ] || { echo "COVERAGE MISMATCH"; exit 5; }
      USER=josephrb python3 launch.py submit $B > $NS/gatelog/${B}_submit.txt 2>&1; s=$?
      echo "$(date -u +%FT%TZ) $B submit rc=$s"
      grep -E "^GATE|REFUSE|STOP" $NS/gatelog/${B}_submit.txt
      grep -A1 "^+ sbatch" $NS/gatelog/${B}_submit.txt | grep -v "^+ sbatch\|^--" | tr "\n" " "; echo
      [ $s -eq 0 ] || exit 6')
    rc=$?
    case $rc in
      0) echo "$out"; break;;
      10) echo "$out" | head -1 | sed 's/$/ (wait)/'; echo "$out" | grep "^GATE"; fail=0; sleep "$SLEEP";;
      255) fail=$((fail+1)); [ $fail -ge 5 ] && { echo "TRANSPORT at $B $(date -u +%FT%TZ)"; exit 2; }; sleep 120;;
      *) echo "$out"; echo "STOPPED at $B rc=$rc"; exit 1;;
    esac
  done
  sleep 130
done
echo "ALL SUBMITTED: $*"
