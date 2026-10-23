#!/bin/bash
# RE-2: submit J0a and J0b, only after the director's BINDING record.   re2_submit_j0.sh <deploy checkout> <declared sha>
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2
L=$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $RE2_SHA"; exit 2; }
mkdir -p /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/j0/logs
a=$(sbatch --parsable --job-name=re2-j0a --time=03:45:00 --export=ALL,C=$C,RE2_SHA=$RE2_SHA,JOB=J0a "$L/re2_j0.sbatch")
b=$(sbatch --parsable --job-name=re2-j0b --time=02:10:00 --export=ALL,C=$C,RE2_SHA=$RE2_SHA,JOB=J0b "$L/re2_j0.sbatch")
echo "$(date -u +%FT%TZ) sha=$RE2_SHA j0a=$a j0b=$b" | tee -a /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/submissions.log
