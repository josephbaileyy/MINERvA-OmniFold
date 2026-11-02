# 1B staged, stage 0, the bulk (FD-1B-STAGED-BINDING-1 ruling 3: only after walls PASS and the audit's written
# acknowledgement of D-0): two one-node jobs, 8 lanes each, at most 6 items per lane, 2:15:00 each (4.5 node-h).
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102; DD=$W/deploy; M=b3705d4360520612842c4c819ac6f51041f274f2
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
[ -e $W/logs/submit-bulk.out ] && stop "the bulk was already submitted"
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
$PY -c "import json,sys; v=json.load(open('$W/stage0/walls-d0.json'))['verdict']; print('walls', v); sys.exit(0 if v=='PASS' else 1)" || stop "walls is not PASS"
n=$(git -C $DD status --porcelain | wc -l); h=$(git -C $DD rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cd $W/tables && sha256sum -c SHA256SUMS || stop "table digests"
xargs -a $W/logs/stage0-sources.txt stat -c '%X %Y %s %n' > $W/logs/bulk-stat-before.txt; echo "stat-before lines=$(wc -l < $W/logs/bulk-stat-before.txt)"
: > $W/logs/submit-bulk.txt
for k in 0 1; do
  echo "sbatch -A m3246 -q regular -C cpu -t 02:15:00 -J fd1b_d_n$k -o $W/logs/%x_%j.out $DD/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh $DD $M $W/tables/tasks-bulk.tsv $W/stage0/lanes 32 56G $((8*k)) $((8*k+7)) inherit" >> $W/logs/submit-bulk.txt
done
cat $W/logs/submit-bulk.txt
bash $W/logs/submit-bulk.txt > $W/logs/submit-bulk.out 2>&1; echo "rc=$?" >> $W/logs/submit-bulk.out
cat $W/logs/submit-bulk.out
squeue --me -h -o "%i %j %T %l %D %R"
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
