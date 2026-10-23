#!/bin/bash
# RE-2: submit J0a and J0b, once, only after the director's BINDING record.   re2_submit_j0.sh <deploy> <declared sha>
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2
L=$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $RE2_SHA"; exit 2; }
B=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023
if [ -e "$B/submissions.log" ] && grep -qE " j0[ab]=" "$B/submissions.log"; then
    echo "J0 was already submitted (see $B/submissions.log); a resubmission needs the director"; exit 3
fi
source "$L/re2_env.sh" 2>/dev/null || true
mkdir -p "$B/j0/logs"
a=$(sbatch --parsable --job-name=re2-j0a --time="${J0_TIME[J0a]}" --export=ALL,C=$C,RE2_SHA=$RE2_SHA,JOB=J0a "$L/re2_j0.sbatch")
echo "$(date -u +%FT%TZ) sha=$RE2_SHA j0a=$a" | tee -a "$B/submissions.log"   # logged before J0b, so no rerun repeats it
b=$(sbatch --parsable --job-name=re2-j0b --time="${J0_TIME[J0b]}" --export=ALL,C=$C,RE2_SHA=$RE2_SHA,JOB=J0b "$L/re2_j0.sbatch")
echo "$(date -u +%FT%TZ) sha=$RE2_SHA j0b=$b" | tee -a "$B/submissions.log"
