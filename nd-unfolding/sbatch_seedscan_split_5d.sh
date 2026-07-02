#!/bin/bash
#SBATCH --job-name=ssplit5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=03:00:00
#SBATCH --array=1-24%24
#SBATCH --output=ssplit5d_%a_%A.out --error=ssplit5d_%a_%A.err
# C_ML (train/test-split seedscan) for 5D: dimension-general seedscan_split.py on of_inputs_5d.npz.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p seedscan_split_5d
[[ -s "seedscan_split_5d/res_split_${SLURM_ARRAY_TASK_ID}.npz" ]] && { echo "skip (exists)"; exit 0; }
python3 seedscan_split.py --npz of_inputs_5d.npz --split-seed ${SLURM_ARRAY_TASK_ID} \
  --train-frac 0.8 --iters 5 --out seedscan_split_5d/res_split_${SLURM_ARRAY_TASK_ID}.npz
