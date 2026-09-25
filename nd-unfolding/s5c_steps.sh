#!/bin/bash
# Run committed s5c task tables as job steps on a held allocation, then release it.
#
# The allocation is admitted and priced by `s5c_meter.py submit --allocate` (salloc --no-shell);
# this runner only places steps inside it, so it adds no spend beyond that reservation, and it
# cancels the allocation once every track has finished so billing stops at the last step.
# Usage (run under nohup on a login node):
#   s5c_steps.sh <jobid> <deploy_tree> <pinned_sha> <cpus_per_step> <mem_per_step> <track> [<track> ...]
# A track is a comma-separated sequence of stages <table>:<out_dir>:<max_parallel>[:<first>:<last>]
# (optional 0-based inclusive range of task lines, so one committed table can feed many
# allocations). Tracks run
# concurrently; the stages of one track run in order (a later stage may consume an earlier one's
# products); the tasks of a stage run up to <max_parallel> at a time. Each step executes
# s5c_array.sh for one table line, exactly as an sbatch array task would.

JOB=${1:?jobid}; DEPLOY=${2:?deploy}; PIN=${3:?sha}; CPUS=${4:?cpus}; MEM=${5:?mem}
shift 5
[ "$#" -ge 1 ] || { echo "no tracks" >&2; exit 2; }
stamp() { date -u +%FT%TZ; }

run_stage() {
    local table=$1 out=$2 par=$3 first=${4:-0} last=${5:-} n i status=0
    mkdir -p "$out"
    n=$(grep -v '^#' "$table" | grep -vc '^[[:space:]]*$')
    [ -n "$last" ] || last=$((n - 1))
    [ "$last" -lt "$n" ] || last=$((n - 1))
    echo "[steps] $(stamp) stage start table=$table tasks=$first..$last of $n parallel=$par"
    local pids=()
    for ((i = first; i <= last; i++)); do
        while [ "$(jobs -rp | wc -l)" -ge "$par" ]; do sleep 10; done
        SLURM_ARRAY_TASK_ID=$i srun --jobid="$JOB" --ntasks=1 --cpus-per-task="$CPUS" --mem="$MEM" \
            --exact --output="$out/logs-step-$i.out" \
            bash "$DEPLOY/nd-unfolding/s5c_array.sh" "$DEPLOY" "$PIN" "$table" "$out" &
        pids+=($!)
    done
    for pid in "${pids[@]}"; do wait "$pid" || status=1; done
    echo "[steps] $(stamp) stage done table=$table status=$status"
    return $status
}

run_track() {
    local track=$1 stage table out par status=0
    IFS=, read -ra stages <<< "$track"
    for stage in "${stages[@]}"; do
        IFS=: read -r table out par first last <<< "$stage"
        run_stage "$table" "$out" "$par" "$first" "$last" || status=1
    done
    return $status
}

echo "[steps] $(stamp) job=$JOB deploy=$DEPLOY pin=$PIN tracks=$#"
tpids=()
for track in "$@"; do
    run_track "$track" &
    tpids+=($!)
done
status=0
for pid in "${tpids[@]}"; do wait "$pid" || status=1; done
scancel "$JOB"
echo "[steps] $(stamp) released allocation $JOB; exit $status"
exit $status
