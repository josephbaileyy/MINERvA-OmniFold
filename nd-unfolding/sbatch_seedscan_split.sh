#!/bin/bash
#SBATCH --job-name=ssplit
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=1-24
#SBATCH --output=ssplit_%a_%A.out
#SBATCH --error=ssplit_%a_%A.err

# prepub #2: train/test-split seedscan. Each array task is one split seed; the
# OmniFold classifiers are re-fit on a random 80% subset (omnifold_loop
# train_frac/split_seed) and evaluated on all events. combine_seedscan_split.py
# then forms the ensemble-mean CV + the ML-split covariance. ROOT-free (lgbm).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
mkdir -p seedscan_split

SEED="${SLURM_ARRAY_TASK_ID}"
echo "[ssplit] seed=${SEED} start $(date -u '+%F %T UTC')"
python3 seedscan_split.py --npz of_inputs_3d.npz --split-seed "${SEED}" \
    --train-frac 0.8 --iters 5 --out "seedscan_split/res_split_${SEED}.npz"
echo "[ssplit] seed=${SEED} done  $(date -u '+%F %T UTC')"
