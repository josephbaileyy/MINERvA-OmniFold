#!/bin/bash
# Admit one interactive node through the s5c meter and run a line range of the Tier-S validation
# table on it (contract.json coverage; table docs/orchestration/state/s5c/s-valid-tasks.tsv).
#
# Usage (login node):  s5c_valid_launch.sh <deploy_tree> <pinned_sha> <pool cpu|gpu> <first> <last> [hours]
# Refuses unless the committed G-perm receipt reads PASS (the contract's development gates must all
# pass before any validation experiment runs). A CPU node takes 8 concurrent 10-seed tasks, a GPU
# node 4 (its 128 threads, CPU work only); four waves of about 52 minutes fit the default 4 hours.
# Steps request 48G: measured peaks are 10-16 GB, and an interactive CPU node grants 487,802 MB, so
# eight 60G steps cannot coexist (the eighth waits, as observed on allocation 58857016).

DEPLOY=${1:?deploy}; PIN=${2:?sha}; POOL=${3:?cpu|gpu}; FIRST=${4:?first}; LAST=${5:?last}; HOURS=${6:-4}
NS=/pscratch/sd/j/josephrb/s5c-20260924
GATE="$DEPLOY/docs/orchestration/state/s5c/gperm/gperm.json"
verdict=$(/usr/bin/python3.11 -c "import json,sys; print(json.load(open(sys.argv[1]))['verdict'])" "$GATE" 2>/dev/null)
if [ "$verdict" != "PASS" ]; then
    echo "refusing: committed G-perm receipt $GATE does not read PASS (got '${verdict:-missing}')" >&2
    exit 2
fi
cd "$DEPLOY" || exit 2
M="/usr/bin/python3.11 nd-unfolding/s5c_meter.py --budget docs/orchestration/state/s5c/budget.json --ledger $NS/ledger/admissions.jsonl"
if [ "$POOL" = cpu ]; then
    ARGS=(--pool cpu --billing 256 -- -C cpu -N 1); PAR=8
else
    ARGS=(--pool gpu --gpus-per-task 4 --billing 128 -- -C gpu -N 1 --gpus-per-node=4); PAR=4
fi
out=$(timeout 1000 $M submit --allocate --allocate-wait-s 900 --stage measurement_tier_s --qos interactive \
      --ntasks 1 --timelimit-h "$HOURS" --label "tier_s_valid_${POOL}_${FIRST}" \
      --measures "Tier-S validation experiments, s-valid-tasks.tsv lines ${FIRST}-${LAST}" \
      --cannot-authorize "a coverage verdict by itself (only the complete declared population is evaluated)" \
      "${ARGS[@]}" 2>&1)
echo "$out"
JOB=$(echo "$out" | sed -n 's/^JOB \([0-9]*\).*/\1/p')
[ -n "$JOB" ] || exit 7
mkdir -p "$NS/runs/s_valid"
cd "$NS" || exit 2
nohup bash "$DEPLOY/nd-unfolding/s5c_steps.sh" "$JOB" "$DEPLOY" "$PIN" 32 48G \
    "$DEPLOY/docs/orchestration/state/s5c/s-valid-tasks.tsv:$NS/runs/s_valid/steps_${POOL}_${FIRST}:$PAR:$FIRST:$LAST" \
    > "$NS/runs/steps-$JOB.log" 2>&1 < /dev/null &
disown
echo "LAUNCHED job=$JOB lines=$FIRST..$LAST pool=$POOL"
