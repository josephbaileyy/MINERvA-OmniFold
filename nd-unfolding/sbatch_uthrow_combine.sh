#!/bin/bash
#SBATCH --job-name=uthrow_comb
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=48G
#SBATCH --time=00:40:00
#SBATCH --output=uq_4d/uthrow_comb_%j.out
#SBATCH --error=uq_4d/uthrow_comb_%j.err

# Aggregate the rigorous unified-throw covariance (all banked throws) vs the
# block-sum (precomputed knob + flux units) -> the decisive block-sum-vs-unified
# test (prepub #1). Supersedes the old unified_throw.py ratio-product proxy.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
echo "[comb] $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py \
    --combine "uq_4d/uthrow_slabs/uthrow_*.npz" \
    --block-slabs "uq_4d/uthrow_slabs/blocknode_*.npz" \
    --bank bank_uthrow --iters 5 --seed 1000 --null \
    --out-root uq_4d/unified_throw_cov.root
echo "[comb] done $(date -u '+%F %T UTC')"
