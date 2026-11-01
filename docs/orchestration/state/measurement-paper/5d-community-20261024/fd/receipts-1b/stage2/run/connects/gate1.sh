# waits for job JOB (2a-0) to end, ledgers it, then runs gate 1: repro and walls --after 2a-0
JOB=60623576
P=/pscratch/sd/j/josephrb; B=$P/fd-1b-20261030; D=$B/deploy/stage2; F1C=$P/fd-f1-20261027/f1c
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
SUMS=$D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster/manifest/f1-products-SHA256SUMS
end=$(( $(date +%s) + 9000 ))
while [ $(date +%s) -lt $end ]; do
  st=$(sacct -j $JOB -X -n -P -o State 2>/dev/null | head -1)
  case "$st" in PENDING|RUNNING|REQUEUED|SUSPENDED|CONFIGURING|COMPLETING|"") sleep 60;; *) break;; esac
done
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ) state=[$st]"
sacct -j $JOB -X -P -n -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End,AllocTRES >> $B/logs/LEDGER.psv
sacct -j $JOB -X -P -n -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End
echo "--- steps"; sacct -j $JOB -P -n -o JobID,State,ExitCode,Elapsed | head -20
echo "--- lane rc"; grep -h -E 'rc|FAIL|Traceback|refus' $B/runs/2a-0/*.log $B/logs/fd1b2a-0n0_$JOB.out 2>/dev/null | tail -20
echo "--- products"; ls $B/runs/derivation $B/runs/pilot $B/runs/repro-g18 $B/runs/repro-ar23 2>&1
ls $B/runs/*/*.partial-* 2>/dev/null && echo "PARTIALS PRESENT"
case "$st" in COMPLETED) ;; *) echo "STOP: 2a-0 state $st"; exit 2;; esac
$PY $D/nd-unfolding/fd_1b_score.py repro --pair $B/runs/repro-g18/fd1b_repro-g18_s806000.npz=$F1C/pe/genie_v3_g18/ratio_nd_a1_s806000.npz --pair $B/runs/repro-ar23/fd1b_repro-ar23_s807000.npz=$F1C/pe/genie_v3_ar23/ratio_nd_a1_s807000.npz --f1c-sums $SUMS --f1c-runs $F1C --out $B/score/repro.json > $B/logs/gate1-repro.log 2>&1
echo "repro rc=$?"; cat $B/logs/gate1-repro.log
$PY $D/nd-unfolding/fd_1b_tasks.py walls --after 2a-0 --out $B/score/walls-2a-0.json > $B/logs/gate1-walls.log 2>&1
echo "walls rc=$?"; cat $B/logs/gate1-walls.log
$PY -c "import json; d=json.load(open('$B/score/walls-2a-0.json')); print(json.dumps(d['rule'])); [print(r['product'], r['seconds_load'], r['seconds_unfold'], r['peak_rss_kib']) for r in d['products']]" 2>&1
$PY -c "import json; d=json.load(open('$B/score/repro.json')); print(json.dumps(d))" 2>&1
