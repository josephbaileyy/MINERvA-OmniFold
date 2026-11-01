# waits for 2a's three jobs to end, ledgers them, then runs gate 2: gate D, pairs, walls --after 2a
JOBS="60624652 60624653 60624654"
P=/pscratch/sd/j/josephrb; B=$P/fd-1b-20261030; D=$B/deploy/stage2
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
CON=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
S1NPZ=$P/s1-20261024/s1_assembly.npz
TOYREAD="--s1-npz $S1NPZ --flux-constraint $CON --lateral-dir $P/s5p-20260926/runs/s3/latunf --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json --inputs-npz $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz --x01 $P/2d-closeout-c04repair-20261012/build/minos_rescaled.npz --manifest $D/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt"
end=$(( $(date +%s) + 21600 ))
done_all() { for j in $JOBS; do st=$(sacct -j $j -X -n -P -o State 2>/dev/null | head -1)
  case "$st" in PENDING|RUNNING|REQUEUED|SUSPENDED|CONFIGURING|COMPLETING|"") return 1;; esac; done; return 0; }
until done_all || [ $(date +%s) -gt $end ]; do sleep 120; done
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
bad=0
for j in $JOBS; do
  sacct -j $j -X -P -n -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End,AllocTRES >> $B/logs/LEDGER.psv
  row=$(sacct -j $j -X -P -n -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End); echo "$row"
  case "$row" in *"|COMPLETED|0:0|"*) ;; *) bad=1;; esac
  nb=$(sacct -j $j -P -n -o JobID,State,ExitCode | grep -E '^[0-9]+\.[0-9]+\|' | grep -v '|COMPLETED|0:0$' | wc -l); echo "  steps not COMPLETED 0:0: $nb"; [ "$nb" = "0" ] || bad=1
done
echo "lane rc!=0: $(grep -h '^\[s5c\] task=' $B/logs/fd1b2an*_*.out 2>/dev/null | grep -vc ' rc=0 ')"
echo "products: derivation=$(ls $B/runs/derivation/*.npz | wc -l) pilot=$(ls $B/runs/pilot/*.npz | wc -l) pilot-half=$(ls $B/runs/pilot-half/*.npz 2>/dev/null | wc -l)"
ls $B/runs/*/*.partial-* 2>/dev/null && { echo "PARTIALS PRESENT"; bad=1; }
[ "$bad" = "0" ] || { echo "STOP: a 2a job or step did not complete 0:0"; exit 2; }
$PY $D/nd-unfolding/fd_1b_score.py gate-d --derivation $B/runs/derivation --tag fd1b_derivation --s1-npz $S1NPZ --flux-constraint $CON --out $B/score/gate-d.json > $B/logs/gate2-gate-d.log 2>&1
echo "gate-d rc=$?"; cat $B/logs/gate2-gate-d.log
$PY $D/nd-unfolding/fd_1b_score.py pairs --full $B/runs/pilot --full-tag fd1b_pilot --half $B/runs/pilot-half --half-tag fd1b_pilot_half --n 8 $TOYREAD --out $B/score/pairs.json > $B/logs/gate2-pairs.log 2>&1
echo "pairs rc=$?"; cat $B/logs/gate2-pairs.log
$PY $D/nd-unfolding/fd_1b_tasks.py walls --after 2a --out $B/score/walls-2a.json > $B/logs/gate2-walls.log 2>&1
echo "walls rc=$?"; cat $B/logs/gate2-walls.log
$PY -c "
import json
g=json.load(open('$B/score/gate-d.json')); print('gate-d keys', sorted(g)); print('verdict', g.get('verdict'), 'stop', g.get('stop'))
for k in ('rho','rho_c','per_cell_rho','window'):
    if k in g: print(k, json.dumps(g[k])[:600])
print('per_group', json.dumps(g.get('per_group_sigma_ratio'))[:1500])
w=json.load(open('$B/score/walls-2a.json')); print('walls', json.dumps(w['rule']))
" 2>&1
