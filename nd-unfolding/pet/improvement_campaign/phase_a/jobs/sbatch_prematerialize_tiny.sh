#!/bin/bash
# Task A1: gather his tokens for the tiny audit subsample with the HISTORICAL
# `prematerialize_theirs.py`, unmodified, exactly as the campaign's own cache job
# did (sbatch_prematerialize.sh), but at --max-events 100000 / --stage tuning.
# Output lands under the campaign task dir, never under campaign-20260920.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=110G
#SBATCH --time=01:00:00
#SBATCH --job-name=pa1-premat
set -eo pipefail
: "${HIST:?}" ; : "${OUT:?}" ; : "${MAX_EVENTS:?}" ; : "${STAGE:?}"
HIST_COMMIT=68cf9d29f8ab1b0f5acd933d4baec1962b29e34d
HARDCODED=/pscratch/sd/j/josephrb/MINERvA-OmniFold
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
INDEX=/pscratch/sd/j/josephrb/campaign-20260920/join
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac

cd "$HIST"
[[ "$(git rev-parse HEAD)" == "$HIST_COMMIT" ]]
[[ -z "$(git status --porcelain)" ]]
mkdir -p "$OUT/cache"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/cache/allocation-premat.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0
cd "$OUT/cache"
python "$HIST/nd-unfolding/mnv_guarded_run.py" --expect-root "$HIST" \
  --allow "$HARDCODED" --inventory "$OUT/cache/guard-premat.json" --label "A1-premat" \
  -- "$HIST/nd-unfolding/pet/configuration_comparison/prematerialize_theirs.py" \
  --inputs-npz "$INPUTS" --theirs-index "$INDEX" --identity-sidecar "$SIDECAR" \
  --stage "$STAGE" --subsample-seed 0 --max-events "$MAX_EVENTS" \
  --out "$OUT/cache/theirs-$STAGE-$MAX_EVENTS.npz" \
  --report "$OUT/cache/theirs-$STAGE-$MAX_EVENTS.json" > "$OUT/cache/premat.log" 2>&1
cd "$HIST"
[[ -z "$(git status --porcelain)" ]]
echo COMPLETE > "$OUT/cache/terminal-premat.txt"
