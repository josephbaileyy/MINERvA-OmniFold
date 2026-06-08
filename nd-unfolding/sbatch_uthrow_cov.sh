#!/bin/bash
#SBATCH --job-name=uthrow_cov
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --array=0-19
#SBATCH --output=uq_4d/uthrow_slabs/uthrow_%A_%a.out
#SBATCH --error=uq_4d/uthrow_slabs/uthrow_%A_%a.err

# Rigorous many-throw unified covariance (prepub #1). Each array task runs a slab
# of THROWS_PER throws (one OmniFold re-unfold each, ~5.5 min/throw), composing
# per-event weights across all 12 reweight knobs + 1 sampled flux universe. 20
# tasks x 8 = 160 throws. Shared QoS so the slabs backfill fast.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
mkdir -p uq_4d/uthrow_slabs

THROWS_PER="${THROWS_PER:-8}"
OFF=$(( SLURM_ARRAY_TASK_ID * THROWS_PER ))
echo "[uthrow] task=${SLURM_ARRAY_TASK_ID} throws ${OFF}..$((OFF+THROWS_PER-1)) $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py --throws "${THROWS_PER}" --throw-offset "${OFF}" \
    --seed 1000 --bank bank_uthrow --iters 5 \
    --out "uq_4d/uthrow_slabs/uthrow_slab_${SLURM_ARRAY_TASK_ID}.npz"
echo "[uthrow] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
