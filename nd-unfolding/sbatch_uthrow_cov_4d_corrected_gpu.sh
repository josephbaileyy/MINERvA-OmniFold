#!/bin/bash
#SBATCH --job-name=uthr4dC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=03:00:00
#SBATCH --array=0-39%6
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/uthr4dC_%a_%A.out --error=uq_4d/corrected/logs/uthr4dC_%a_%A.err
# P6-4D corrected unified-throw producer: 160 joint re-unfolds (12 knob bands + flux)
# at FIXED estimator seed 1000. THROWS_PER=4 -> 40 tasks x 4 = throws 0..159 (each
# task ~1.3h << 3h wall; do_throws atomic-saves each throw so a wall-kill loses <=1).
# Reads the from-5D-assembled bank_uthrow_4d. Writes ONLY to uq_4d/corrected/.
# %6 throttle: shares gpu_shared with Agent B (PET) / Agent C (FPS) critical work.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/uthrow_slabs_4d
TPT=4
OFF=$(( SLURM_ARRAY_TASK_ID * TPT ))
# --invalid-ratio neutral: hold ~5e-5 GENIE negative-weight artifacts (HighQ2/LowQ2
# +1sigma, one MFP_N zero) at CV -- prior handling, now logged (see 5D scripts).
echo "[uthrow4dC] task=${SLURM_ARRAY_TASK_ID} throws ${OFF}..$((OFF+TPT-1)) $(date -u '+%F %T')"
python3 unified_throw_cov.py --throws ${TPT} --throw-offset ${OFF} \
    --seed 1000 --bank uq_4d/corrected/bank_uthrow_4d --iters 5 --invalid-ratio neutral \
    --out "uq_4d/corrected/uthrow_slabs_4d/uthrow4d_slab_${SLURM_ARRAY_TASK_ID}.npz"
echo "[uthrow4dC] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T')"
