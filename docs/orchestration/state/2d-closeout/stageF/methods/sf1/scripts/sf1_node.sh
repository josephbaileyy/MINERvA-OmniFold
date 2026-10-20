#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# SF-1 (SF1-SPEC.md): one whole CPU node runs the lines of one task table, 8 at a time, each line through the
# production entry wrapper nd-unfolding/s5c_array.sh of the production tree (clean clone at 4f5a613f), pinned
# to one NUMA domain (16 cores, 32 hardware threads: the production tasks' --cpus-per-task=32).
# Usage: sbatch -J <name> -t <limit> -o <log> sf1_node.sh <table.tsv> <limit_minutes>
# Absolute paths only (sbatch runs a copy of this script). No set -u (the env activation aborts under it).
S=/pscratch/sd/j/josephrb/methods-paper/sf1-20261019
D=$S/deploy-4f5a613f
PIN=4f5a613f383d3776db0be64eccc05e2d89af4a86
TABLE=${1:?table}
LIMIT_MIN=${2:?limit minutes}
MARGIN_MIN=50          # no line starts with less than this left in the job
TASKOUT=$S/runs/tasks
RUN=$S/runs/jobs/$SLURM_JOB_ID
mkdir -p "$RUN" "$TASKOUT"
T0=$(date +%s)
NLINES=$(grep -v '^#' "$TABLE" | grep -c -v '^[[:space:]]*$')
echo "[sf1] job=$SLURM_JOB_ID host=$(hostname) table=$TABLE lines=$NLINES limit_min=$LIMIT_MIN start=$(date -u +%FT%TZ)"
lscpu | grep -E "NUMA node[0-9]"
echo 0 > "$RUN/next"
: > "$RUN/lock"
worker() {
    local w=$1 cpus="$((16*$1))-$((16*$1+15)),$((128+16*$1))-$((128+16*$1+15))" i
    while :; do
        i=$(flock "$RUN/lock" bash -c 'n=$(cat "$0"); echo $((n+1)) > "$0"; echo $n' "$RUN/next")
        [ "$i" -lt "$NLINES" ] || break
        if [ $(( ($(date +%s) - T0) / 60 + MARGIN_MIN )) -gt "$LIMIT_MIN" ]; then
            echo "[sf1] worker=$w line=$i NOT STARTED (deadline margin) $(date -u +%FT%TZ)"
            continue
        fi
        echo "[sf1] worker=$w line=$i cpus=$cpus start=$(date -u +%FT%TZ)"
        SLURM_ARRAY_TASK_ID=$i SLURM_CPUS_PER_TASK=32 taskset -c "$cpus" \
            bash "$D/nd-unfolding/s5c_array.sh" "$D" "$PIN" "$TABLE" "$TASKOUT" > "$RUN/line-$i.out" 2>&1
        echo "[sf1] worker=$w line=$i rc=$? end=$(date -u +%FT%TZ)"
    done
}
for w in 0 1 2 3 4 5 6 7; do worker $w & done
wait
echo "[sf1] job=$SLURM_JOB_ID all workers done $(date -u +%FT%TZ)"
