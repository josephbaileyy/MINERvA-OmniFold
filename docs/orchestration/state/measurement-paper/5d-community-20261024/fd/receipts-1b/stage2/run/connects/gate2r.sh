# waits for 2a-r (JOB) to end, ledgers it, then runs gate 2 from the fixed code ($D2)
JOB=60631190
P=/pscratch/sd/j/josephrb; B=$P/fd-1b-20261030; D2=$B/deploy/stage2-r
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
CON=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
S1NPZ=$P/s1-20261024/s1_assembly.npz
TOYREAD="--s1-npz $S1NPZ --flux-constraint $CON --lateral-dir $P/s5p-20260926/runs/s3/latunf --definition $D2/nd-unfolding/pv-ladder/readouts/h2_definition.json --inputs-npz $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz --x01 $P/2d-closeout-c04repair-20261012/build/minos_rescaled.npz --manifest $D2/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt"
end=$(( $(date +%s) + 10800 ))
while [ $(date +%s) -lt $end ]; do
  st=$(sacct -j $JOB -X -n -P -o State 2>/dev/null | head -1)
  case "$st" in PENDING|RUNNING|REQUEUED|SUSPENDED|CONFIGURING|COMPLETING|"") sleep 60;; *) break;; esac
done
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ) state=[$st]"
sacct -j $JOB -X -P -n -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End,AllocTRES >> $B/logs/LEDGER.psv
row=$(sacct -j $JOB -X -P -n -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End); echo "$row"
bad=0; case "$row" in *"|COMPLETED|0:0|"*) ;; *) bad=1;; esac
echo "--- steps"; sacct -j $JOB -P -n -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
nb=$(sacct -j $JOB -P -n -o JobID,State,ExitCode | grep -E '^[0-9]+\.[0-9]+\|' | grep -v '|COMPLETED|0:0$' | wc -l); echo "steps not COMPLETED 0:0: $nb"; [ "$nb" = "0" ] || bad=1
echo "lane rc!=0: $(grep -h '^\[s5c\] task=' $B/runs/2a-r/line*-$JOB.log 2>/dev/null | grep -vc ' rc=0 ')  lanes_reporting=$(grep -h '^\[s5c\] task=' $B/runs/2a-r/line*-$JOB.log 2>/dev/null | wc -l)"
grep -h 'refusing' $B/runs/2a-r/line*-$JOB.log 2>/dev/null | head -5
echo "products: derivation=$(ls $B/runs/derivation/*.npz | wc -l) pilot=$(ls $B/runs/pilot/*.npz | wc -l) pilot-half=$(ls $B/runs/pilot-half/*.npz 2>/dev/null | wc -l)"
ls $B/runs/*/*.partial-* 2>/dev/null && { echo "PARTIALS PRESENT"; bad=1; }
[ "$bad" = "0" ] || { echo "STOP: 2a-r or a step did not complete 0:0"; exit 2; }
$PY $D2/nd-unfolding/fd_1b_score.py gate-d --derivation $B/runs/derivation --tag fd1b_derivation --s1-npz $S1NPZ --flux-constraint $CON --out $B/score/gate-d.json > $B/logs/gate2-gate-d.log 2>&1
echo "gate-d rc=$?"; cat $B/logs/gate2-gate-d.log
$PY $D2/nd-unfolding/fd_1b_score.py pairs --full $B/runs/pilot --full-tag fd1b_pilot --half $B/runs/pilot-half --half-tag fd1b_pilot_half --n 8 $TOYREAD --out $B/score/pairs.json > $B/logs/gate2-pairs.log 2>&1
echo "pairs rc=$?"; cat $B/logs/gate2-pairs.log
$PY $D2/nd-unfolding/fd_1b_tasks.py walls --after 2a --out $B/score/walls-2a.json > $B/logs/gate2-walls.log 2>&1
echo "walls rc=$?"; cat $B/logs/gate2-walls.log
$PY - <<'PY' 2>&1
import json
import numpy as np
B = "/pscratch/sd/j/josephrb/fd-1b-20261030/score"
g = json.load(open(f"{B}/gate-d.json"))
print("gate-d", {k: g.get(k) for k in ("label", "verdict", "window", "stop", "reason")})
if "rho" in g:
    r = np.array(g["rho"]); print("rho min %.4f max %.4f median %.4f" % (r.min(), r.max(), np.median(r)))
    print("rho per cell", " ".join(f"{c}:{v:.3f}" for c, v in zip(g.get("cells", []), r)))
pg = g.get("per_group_sigma_ratio")
if pg: print("per_group_sigma_ratio", json.dumps(pg)[:1200])
try:
    q = json.load(open(f"{B}/pairs.json")); d = np.array(q["per_cell_paired_difference_full_minus_half_in_sigma"])
    print("pairs shape", d.shape, "mean %.3f sd %.3f max|.| %.3f" % (d.mean(), d.std(), np.abs(d).max()), "verdict", q.get("verdict"))
except Exception as e: print("pairs read:", type(e).__name__, e)
w = json.load(open(f"{B}/walls-2a.json")); print("walls", w["verdict"], json.dumps(w["rule"]))
PY
