#!/bin/bash
#SBATCH --job-name=ssp4dCc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=32G --time=03:00:00
#SBATCH --array=1-24%24
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/ssp4dCc_%a_%A.out --error=uq_4d/corrected/logs/ssp4dCc_%a_%A.err
# P6-4D corrected C_ML (split-response) on CPU. Fixed estimator seed 42; split-seed
# varies the 80% train split. OMP pinned; skip-if-exists; uq_4d/corrected/ only.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/seedscan_split_4d
OUT="uq_4d/corrected/seedscan_split_4d/res_split_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
python3 seedscan_split.py --npz of_inputs_4d.npz --split-seed ${SLURM_ARRAY_TASK_ID} \
  --estimator-seed 42 --train-frac 0.8 --iters 5 --out "${OUT}"
