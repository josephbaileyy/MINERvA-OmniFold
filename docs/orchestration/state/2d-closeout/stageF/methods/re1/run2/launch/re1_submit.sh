#!/bin/bash
# RE-1 run 2: submit job 1 (inputs), then jobs 2 (ND) and 3 (2D) after it succeeds.
#   re1_submit.sh <deploy checkout> <declared sha>
# Only after the director's BINDING record. The deploy must be a clean clone at the declared sha.
set -eo pipefail
C=$(cd "$1" && pwd); RE1_SHA=$2
L=$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch
[ "$(git -C "$C" rev-parse HEAD)" = "$RE1_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $RE1_SHA"; exit 2; }
mkdir -p /pscratch/sd/j/josephrb/methods-paper/re1-20261022/logs
j1=$(sbatch --parsable --export=ALL,C=$C,RE1_SHA=$RE1_SHA "$L/re1_inputs.sbatch")
j2=$(sbatch --parsable --dependency=afterok:$j1 --export=ALL,C=$C,RE1_SHA=$RE1_SHA "$L/re1_nd.sbatch")
j3=$(sbatch --parsable --dependency=afterok:$j1 --export=ALL,C=$C,RE1_SHA=$RE1_SHA "$L/re1_2d.sbatch")
echo "$(date -u +%FT%TZ) sha=$RE1_SHA inputs=$j1 nd=$j2 2d=$j3" | tee -a /pscratch/sd/j/josephrb/methods-paper/re1-20261022/submissions.log
