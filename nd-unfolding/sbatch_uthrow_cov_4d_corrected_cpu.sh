#!/bin/bash
#SBATCH --job-name=uthr4dCc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=32G --time=03:00:00
#SBATCH --array=0-39%24
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/uthr4dCc_%a_%A.out --error=uq_4d/corrected/logs/uthr4dCc_%a_%A.err
# P6-4D corrected unified-throw producer on CPU: 160 joint re-unfolds (12 knob bands +
# flux) at FIXED estimator seed 1000. TPT=4 -> 40 tasks x 4 throws = 0..159. do_throws
# atomic-saves each throw. Reads the from-5D-assembled bank_uthrow_4d. uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/uthrow_slabs_4d
TPT=4; OFF=$(( SLURM_ARRAY_TASK_ID * TPT ))
OUT="uq_4d/corrected/uthrow_slabs_4d/uthrow4d_slab_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
echo "[uthr4dCc] task=${SLURM_ARRAY_TASK_ID} throws ${OFF}..$((OFF+TPT-1)) $(date -u '+%F %T')"
python3 unified_throw_cov.py --throws ${TPT} --throw-offset ${OFF} \
    --seed 1000 --bank uq_4d/corrected/bank_uthrow_4d --iters 5 --invalid-ratio neutral \
    --out "${OUT}"
