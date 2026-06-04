#!/bin/bash
#SBATCH --job-name=uthrow_run
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=04:00:00
#SBATCH --array=0-31%16
#SBATCH --output=uthrow_run_%a_%A.out --error=uthrow_run_%a_%A.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
START=$((SLURM_ARRAY_TASK_ID * 5))
python3 unified_throw.py --run --bankdir bank_uthrow --throw-start ${START} --throw-count 5 --iters 5
