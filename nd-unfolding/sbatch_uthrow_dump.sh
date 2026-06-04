#!/bin/bash
#SBATCH --job-name=uthrow_dump
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=110G --time=06:00:00
#SBATCH --array=0-7
#SBATCH --output=uthrow_dump_%a_%A.out --error=uthrow_dump_%a_%A.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 unified_throw.py --dump --group ${SLURM_ARRAY_TASK_ID} --ngroups 8 --bankdir bank_uthrow
