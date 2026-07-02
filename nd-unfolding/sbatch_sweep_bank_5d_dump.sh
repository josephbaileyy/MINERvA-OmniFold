#!/bin/bash
#SBATCH --job-name=sweepbank5d_dump
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=110G --time=06:00:00
#SBATCH --array=0-7
#SBATCH --output=sweepbank5d_dump_%a_%A.out --error=sweepbank5d_dump_%a_%A.err
# One GetEntry pass per group over the 142 GB 5D _universes_full omnifile, banking the
# 175 VERTICAL universes' POT-scaled weights (+ the shared 5D CV block by group 0).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 sweep_bank_5d.py --dump --group ${SLURM_ARRAY_TASK_ID} --ngroups 8 \
  --bankdir "${REPO}/nd-unfolding/bank_sweep_5d"
