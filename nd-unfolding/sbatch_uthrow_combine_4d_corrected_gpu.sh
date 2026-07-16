#!/bin/bash
#SBATCH --job-name=comb4dC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/comb4dC_%j.out --error=uq_4d/corrected/logs/comb4dC_%j.err
# P6-4D corrected unified-throw combine: aggregate the 160 throw slabs + 124 block
# units -> C_unified_4d, C_blocksum_4d (MAT mean-centered 1/N), C_cross_4d on the
# (pt,pz,Eavail,q3) analysis binning. --expected-throws 0-159 enforces the exact
# throw manifest; --null requires the fixed-seed CV re-unfold to be zero; the
# stored covariance is throw-mean-centered with its mean shift stored separately
# (hJointMeanShift). No jitter subtraction. Writes ONLY to uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
echo "[comb4dC] start $(date -u '+%F %T')"
python3 unified_throw_cov.py \
    --combine 'uq_4d/corrected/uthrow_slabs_4d/uthrow4d_slab_*.npz' \
    --expected-throws 0-159 \
    --block-slabs 'uq_4d/corrected/uthrow_slabs_4d/block4d_*.npz' \
    --bank uq_4d/corrected/bank_uthrow_4d --iters 5 --seed 1000 --null \
    --out-root uq_4d/corrected/unified_throw_cov_4d.root
echo "[comb4dC] DONE $(date -u '+%F %T')"
