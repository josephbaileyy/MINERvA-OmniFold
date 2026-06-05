#!/bin/bash
#SBATCH --job-name=ssplit4d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=03:00:00
#SBATCH --array=1-24%24
#SBATCH --output=ssplit4d_%a_%A.out --error=ssplit4d_%a_%A.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p seedscan_split_4d
[[ -s "seedscan_split_4d/res_split_${SLURM_ARRAY_TASK_ID}.npz" ]] && { echo "skip (exists)"; exit 0; }
python3 seedscan_split.py --npz of_inputs_4d.npz --split-seed ${SLURM_ARRAY_TASK_ID} \
  --train-frac 0.8 --iters 5 --out seedscan_split_4d/res_split_${SLURM_ARRAY_TASK_ID}.npz
