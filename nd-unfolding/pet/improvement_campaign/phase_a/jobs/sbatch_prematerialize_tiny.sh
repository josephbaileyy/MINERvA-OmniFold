#!/bin/bash
# Task A1: gather his tokens for the tiny audit subsample with the HISTORICAL
# `prematerialize_theirs.py`, unmodified, exactly as the campaign's own cache job
# did (sbatch_prematerialize.sh), but at --max-events 100000 / --stage tuning.
# Output lands under the campaign task dir, never under campaign-20260920.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=110G
#SBATCH --time=00:30:00
#SBATCH --job-name=pa1-premat
set -eo pipefail
: "${HIST:?}" ; : "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}"
: "${MAX_EVENTS:?}" ; : "${STAGE:?}"
HIST_COMMIT=68cf9d29f8ab1b0f5acd933d4baec1962b29e34d
HARDCODED=/pscratch/sd/j/josephrb/MINERvA-OmniFold
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
INDEX=/pscratch/sd/j/josephrb/campaign-20260920/join
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac

for pair in "$HIST:$HIST_COMMIT" "$MINE:$MINE_COMMIT"; do
  dir=${pair%%:*}; want=${pair##*:}
  [[ "$(git -C "$dir" rev-parse HEAD)" == "$want" ]]
  [[ -z "$(git -C "$dir" status --porcelain)" ]]
done
mkdir -p "$OUT/cache"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/cache/allocation-premat.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0
cd "$OUT/cache"
# The historical module is imported from $HIST (--allow) and its main() called by
# phase_a/historical_entry.py, which first disables NumPy's lscpu-launching SVE
# probe (numpy_probe.py; the guard refuses that launch and must not be widened).
python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
  --allow "$HIST" --allow "$HARDCODED" \
  --inventory "$OUT/cache/guard-premat.json" --label "A1-premat" \
  -- "$MINE/nd-unfolding/pet/improvement_campaign/phase_a/historical_entry.py" \
  --module-dir "$HIST/nd-unfolding/pet/configuration_comparison" \
  --module prematerialize_theirs -- \
  --inputs-npz "$INPUTS" --theirs-index "$INDEX" --identity-sidecar "$SIDECAR" \
  --stage "$STAGE" --subsample-seed 0 --max-events "$MAX_EVENTS" \
  --out "$OUT/cache/theirs-$STAGE-$MAX_EVENTS.npz" \
  --report "$OUT/cache/theirs-$STAGE-$MAX_EVENTS.json" > "$OUT/cache/premat.log" 2>&1
for dir in "$HIST" "$MINE"; do [[ -z "$(git -C "$dir" status --porcelain)" ]]; done
echo COMPLETE > "$OUT/cache/terminal-premat.txt"
