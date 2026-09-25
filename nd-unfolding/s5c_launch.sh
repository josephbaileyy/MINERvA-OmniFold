#!/bin/bash
# Admit one interactive node through the s5c meter and run committed task-table tracks on it
# (s5c_steps.sh). The generic form of s5c_valid_launch.sh, for construction allocations.
#
# Usage (login node):
#   s5c_launch.sh <deploy_tree> <pinned_sha> <pool cpu|gpu> <stage> <hours> <label> <mem_per_step> \
#                 <measures> <track> [<track> ...]
# A track is as in s5c_steps.sh (comma-separated stages <table>:<out>:<max_parallel>[:<first>:<last>])
# with RELATIVE paths: <table> under $DEPLOY/docs/orchestration/state/s5c/, <out> under $NS/runs/.
# Steps take 32 CPUs. On the gpu pool steps run with --gres=none (the work is CPU-only; a step that
# inherits the job's 4 GPUs excludes every other step, as on allocation 58857791).
# Exit: 0 and "LAUNCHED job=<id>" when admitted and started; otherwise the meter's exit code
# (4 = refused by concurrency, 7 = not granted), so s5c_queue.sh can tell retryable refusals apart.
# S5C_CAMPAIGN selects the campaign (default s5c; s5n = the OI-191 successor; s5e = the OI-192 diagnosis): its committed state
# directory docs/orchestration/state/<campaign>/ (task tables and budget.json) and, unless S5C_NS is
# set, its namespace; the meter then prices against that campaign's budget and ledger only.

DEPLOY=${1:?deploy}; PIN=${2:?sha}; POOL=${3:?cpu|gpu}; STAGE=${4:?stage}; HOURS=${5:?hours}
LABEL=${6:?label}; MEM=${7:?mem}; MEASURES=${8:?measures}
shift 8
[ "$#" -ge 1 ] || { echo "no tracks" >&2; exit 2; }
CAMP=${S5C_CAMPAIGN:-s5c}
case "$CAMP" in
    s5c) NS=${S5C_NS:-/pscratch/sd/j/josephrb/s5c-20260924} ;;
    s5n) NS=${S5C_NS:-/pscratch/sd/j/josephrb/s5n-20260925} ;;
    s5e) NS=${S5C_NS:-/pscratch/sd/j/josephrb/s5e-20260925} ;;
    *) echo "unknown campaign $CAMP" >&2; exit 2 ;;
esac
T="$DEPLOY/docs/orchestration/state/$CAMP"

tracks=()
for track in "$@"; do
    IFS=, read -ra stages <<< "$track"
    abs=()
    for stage in "${stages[@]}"; do
        IFS=: read -r table out rest <<< "$stage"
        [ -f "$T/$table" ] || { echo "no committed table $T/$table" >&2; exit 2; }
        abs+=("$T/$table:$NS/runs/$out:$rest")
    done
    tracks+=("$(IFS=,; echo "${abs[*]}")")
done

if [ -n "${S5C_LAUNCH_DRYRUN:-}" ]; then printf 'track %s\n' "${tracks[@]}"; exit 0; fi
cd "$DEPLOY" || exit 2
M="/usr/bin/python3.11 nd-unfolding/s5c_meter.py --budget docs/orchestration/state/$CAMP/budget.json --ledger $NS/ledger/admissions.jsonl"
if [ "$POOL" = cpu ]; then
    ARGS=(--pool cpu --billing 256 -- -C cpu -N 1)
else
    ARGS=(--pool gpu --gpus-per-task 4 --billing 128 -- -C gpu -N 1 --gpus-per-node=4)
    export S5C_STEP_GRES=none
fi
out=$(timeout 1000 $M submit --allocate --allocate-wait-s 900 --stage "$STAGE" --qos interactive \
      --ntasks 1 --timelimit-h "$HOURS" --label "$LABEL" --measures "$MEASURES" \
      --cannot-authorize "any covariance, coverage verdict or adoption by itself" "${ARGS[@]}" 2>&1)
rc=$?
echo "$out"
JOB=$(echo "$out" | sed -n 's/^JOB \([0-9]*\).*/\1/p')
[ -n "$JOB" ] || exit $((rc ? rc : 7))
cd "$NS" || exit 2
nohup bash "$DEPLOY/nd-unfolding/s5c_steps.sh" "$JOB" "$DEPLOY" "$PIN" 32 "$MEM" "${tracks[@]}" \
    > "$NS/runs/steps-$JOB.log" 2>&1 < /dev/null &
disown
echo "LAUNCHED job=$JOB label=$LABEL pool=$POOL"
