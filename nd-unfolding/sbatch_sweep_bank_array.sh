#!/bin/bash
#SBATCH --job-name=banksweep
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=48G --time=01:00:00
#SBATCH --array=1-175%48
#SBATCH --output=banksweep_%a_%A.out --error=banksweep_%a_%A.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
U=$(sed -n "${SLURM_ARRAY_TASK_ID}p" uq_4d/vertical_universes.txt)
[[ -z "$U" ]] && exit 0
python3 sweep_bank.py --run --universe "$U" --bankdir bank_sweep --iters 5
