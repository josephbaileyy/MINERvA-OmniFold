#!/bin/bash
#SBATCH --job-name=bootfps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=04:00:00
#SBATCH --array=1-100%32
#SBATCH --output=uq_fps/bootfps_%a_%A.out --error=uq_fps/bootfps_%a_%A.err

# FPS statistical bootstrap (C_stat): 100 Poisson replicas on the extended grid.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p boot_nd_fps
[[ -s "boot_nd_fps/res_boot_${SLURM_ARRAY_TASK_ID}.npz" ]] && { echo "skip (exists)"; exit 0; }
python3 bootstrap_nd.py --npz of_inputs_fps.npz --seed ${SLURM_ARRAY_TASK_ID} \
  --iters 5 --out boot_nd_fps/res_boot_${SLURM_ARRAY_TASK_ID}.npz
