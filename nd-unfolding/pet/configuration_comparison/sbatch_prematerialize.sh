#!/bin/bash
# Gather his tokens once per stage, before the campaign runs.
#
# Measured: gathering in-process cost 15.5 minutes before his arm's first
# training step, and every task of a stage gathers the SAME rows -- only the
# estimator seed varies. Thirty-two gathers of the same rows would also read
# most of the 65 GB of built inputs each time.
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --job-name=pet-prematerialize
# Sized from the arrays it actually holds, not from caution: the join index is
# 0.4 GiB, its origin 0.4, pass_reco 0.05, the loaders about 0.9 for a
# 2,000,000-row draw, and the gathered legs about 1.0 doubled by the float64
# convert -- roughly 4 GiB peak. The first version asked for 120 GB on a queue
# 933 jobs deep, which buys nothing and waits longer for it.
set -eo pipefail
checkout=${CHECKOUT:?}; output=${OUTPUT:?}; commit=${COMMIT:?}
inputs=${INPUTS_NPZ:?}; index=${THEIRS_INDEX:?}
sidecar=${IDENTITY_SIDECAR:-/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz}
events=${MAX_EVENTS:-2000000}

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$commit" ]]
[[ -f "$sidecar" ]]
mkdir -p "$output/cache"
module load python
for stage in tuning pilot final; do
  python3 nd-unfolding/pet/configuration_comparison/prematerialize_theirs.py \
    --inputs-npz "$inputs" --theirs-index "$index" \
    --identity-sidecar "$sidecar" --stage "$stage" \
    --subsample-seed 0 --max-events "$events" \
    --out "$output/cache/theirs-$stage.npz" \
    --report "$output/cache/theirs-$stage.json"
done
echo DONE > "$output/cache/terminal.txt"
