#!/bin/bash
#SBATCH --job-name=uth4d_comb
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=uq_4d/uthrow4d_comb_%A.out
#SBATCH --error=uq_4d/uthrow4d_comb_%A.err

# Aggregate the 4D unified-throw slabs vs the 4D block-sum units -> C_unified_4d,
# C_blocksum_4d, C_cross_4d on the real (pt,pz,eavail,q3) analysis binning, with the
# jitter-null correction. This is the rigorous task-14 object (the 3D run was a probe).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
echo "[comb4d] start $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py \
    --combine 'uq_4d/uthrow_slabs_4d/uthrow4d_slab_*.npz' \
    --block-slabs 'uq_4d/uthrow_slabs_4d/block4d_*.npz' \
    --bank bank_uthrow_4d --iters 5 --null \
    --out-root uq_4d/unified_throw_cov_4d.root
echo "[comb4d] done $(date -u '+%F %T UTC')"
