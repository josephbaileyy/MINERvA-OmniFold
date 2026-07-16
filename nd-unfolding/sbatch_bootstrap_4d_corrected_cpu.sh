#!/bin/bash
#SBATCH --job-name=boot4dCc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=32G --time=03:00:00
#SBATCH --array=1-100%32
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/boot4dCc_%a_%A.out --error=uq_4d/corrected/logs/boot4dCc_%a_%A.err
# P6-4D corrected C_stat on CPU (normal CPU hours restored 2026-07-15). Robust,
# resumable, fire-and-forget; no GPU contention with Agents A/B/C. Coherent data+MC
# Poisson bootstrap at FIXED estimator seed 42. OMP pinned to the 16-core cpuset to
# avoid the LightGBM thread-thrash seen when packing. skip-if-exists preserves the
# replicas already produced. Writes ONLY to uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/boot_nd_4d
OUT="uq_4d/corrected/boot_nd_4d/res_boot_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
python3 bootstrap_nd.py --npz of_inputs_4d.npz --seed ${SLURM_ARRAY_TASK_ID} \
  --estimator-seed 42 --iters 5 --out "${OUT}"
