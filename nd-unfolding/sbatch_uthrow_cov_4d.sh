#!/bin/bash
#SBATCH --job-name=uth4d_cov
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --array=0-19
#SBATCH --output=uq_4d/uthrow_slabs_4d/uthrow_%A_%a.out
#SBATCH --error=uq_4d/uthrow_slabs_4d/uthrow_%A_%a.err

# Rigorous many-throw unified covariance (prepub #1). Each array task runs a slab
# of THROWS_PER throws (one OmniFold re-unfold each, ~5.5 min/throw), composing
# per-event weights across all 12 reweight knobs + 1 sampled flux universe. 20
# tasks x 8 = 160 throws. Shared QoS so the slabs backfill fast.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
mkdir -p uq_4d/uthrow_slabs_4d

THROWS_PER="${THROWS_PER:-8}"
OFF=$(( SLURM_ARRAY_TASK_ID * THROWS_PER ))
echo "[uthrow] task=${SLURM_ARRAY_TASK_ID} throws ${OFF}..$((OFF+THROWS_PER-1)) $(date -u '+%F %T UTC')"
# --invalid-ratio neutral: hold ~5e-5 GENIE negative-weight artifacts (HighQ2/
# LowQ2 +1sigma, one MFP_N zero) at CV -- prior handling, now logged. See
# sbatch_uthrow_run_5d.sh for the full note.
python3 unified_throw_cov.py --throws "${THROWS_PER}" --throw-offset "${OFF}" \
    --seed 1000 --bank bank_uthrow_4d --iters 5 --invalid-ratio neutral \
    --out "uq_4d/uthrow_slabs_4d/uthrow4d_slab_${SLURM_ARRAY_TASK_ID}.npz"
echo "[uthrow] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
