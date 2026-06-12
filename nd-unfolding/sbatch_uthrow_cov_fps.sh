#!/bin/bash
#SBATCH --job-name=uthfps_cov
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=06:00:00
#SBATCH --array=0-19
#SBATCH --output=uq_fps/uthrow_slabs_fps/uthrow_%A_%a.out
#SBATCH --error=uq_fps/uthrow_slabs_fps/uthrow_%A_%a.err

# FPS unified-throw slabs: 20 tasks x THROWS_PER=8 = 160 throws, each composing all
# 12 reweight knobs + 1 sampled flux universe and re-unfolding on the extended grid.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/uthrow_slabs_fps
THROWS_PER="${THROWS_PER:-8}"
OFF=$(( SLURM_ARRAY_TASK_ID * THROWS_PER ))
[[ -s "uq_fps/uthrow_slabs_fps/uthrowfps_slab_${SLURM_ARRAY_TASK_ID}.npz" ]] && { echo "skip (exists)"; exit 0; }
echo "[uthrowfps] task=${SLURM_ARRAY_TASK_ID} throws ${OFF}..$((OFF+THROWS_PER-1)) $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py --throws "${THROWS_PER}" --throw-offset "${OFF}" \
    --seed 1000 --bank bank_uthrow_fps --iters 5 \
    --out "uq_fps/uthrow_slabs_fps/uthrowfps_slab_${SLURM_ARRAY_TASK_ID}.npz"
echo "[uthrowfps] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
