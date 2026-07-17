#!/bin/bash
#SBATCH --job-name=sspfpsC
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=48G --time=02:00:00
#SBATCH --array=1-24%12
#SBATCH --nice=0
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/sspfpsC_%a_%A.out --error=uq_fps/corrected/logs/sspfpsC_%a_%A.err
# CORRECTED FPS C_ML (Agent C / P6-FPS). Regenerates the 24 train/test-split replicas
# with the CORRECTED seedscan_split.py (fixed estimator seed 42; --split-seed varies ONLY
# the training split -> split-response-only C_ML, matching the 5D scope). The June
# seedscan_split_fps replicas used seed=split_seed for the ESTIMATOR (old contract) ->
# quarantined. GPU host cores; high --nice yields to critical-path PET(B)/4D(D) work.
# Non-destructive: writes uq_fps/corrected/seedscan_split_fps/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/corrected/seedscan_split_fps
OUT="uq_fps/corrected/seedscan_split_fps/res_split_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
python3 seedscan_split.py --npz of_inputs_fps.npz --split-seed ${SLURM_ARRAY_TASK_ID} \
  --estimator-seed 42 --train-frac 0.8 --iters 5 --out "${OUT}"
