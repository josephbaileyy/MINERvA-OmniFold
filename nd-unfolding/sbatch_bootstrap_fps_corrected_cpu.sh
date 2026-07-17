#!/bin/bash
#SBATCH --job-name=bootfpsC
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=48G --time=02:00:00
#SBATCH --array=1-100%16
#SBATCH --nice=0
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/bootfpsC_%a_%A.out --error=uq_fps/corrected/logs/bootfpsC_%a_%A.err
# CORRECTED FPS C_stat (Agent C / P6-FPS). Regenerates the 100 statistical bootstrap
# replicas with the CORRECTED bootstrap_nd.py (fixed estimator seed 42; --seed varies
# only the coherent data+MC Poisson draw). The June boot_nd_fps replicas used
# seed=a.seed for the ESTIMATOR too (old contract, KNOWN_ISSUES #14) -> quarantined.
# GPU host cores for the LightGBM CPU code (buying cores with GPU-hours; CPU exhausted).
# High --nice yields to critical-path PET(B)/4D(D) work: this only backfills idle slots.
# Non-destructive: writes uq_fps/corrected/boot_nd_fps/, leaving old boot_nd_fps/ intact.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/corrected/boot_nd_fps
OUT="uq_fps/corrected/boot_nd_fps/res_boot_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
python3 bootstrap_nd.py --npz of_inputs_fps.npz --seed ${SLURM_ARRAY_TASK_ID} \
  --estimator-seed 42 --iters 5 --out "${OUT}"
