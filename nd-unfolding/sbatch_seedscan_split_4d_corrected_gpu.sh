#!/bin/bash
#SBATCH --job-name=ssp4dC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=03:00:00
#SBATCH --array=1-24%24
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/ssp4dC_%a_%A.out --error=uq_4d/corrected/logs/ssp4dC_%a_%A.err
# P6-4D corrected C_ML (split-response band): OmniFold re-fit on a random 80%
# train split at FIXED estimator seed 42 (split-seed varies the split only).
# Regenerates the corrected ML-split replicas into the corrected namespace with a
# clean seed-stamped manifest (old seedscan_split_4d archived as _prehm).
# CPU account exhausted -> GPU host cores (m3246_g), --export HOME conda fix.
# Writes ONLY to uq_4d/corrected/. skip-if-exists.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/seedscan_split_4d
OUT="uq_4d/corrected/seedscan_split_4d/res_split_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
python3 seedscan_split.py --npz of_inputs_4d.npz --split-seed ${SLURM_ARRAY_TASK_ID} \
  --estimator-seed 42 --train-frac 0.8 --iters 5 --out "${OUT}"
