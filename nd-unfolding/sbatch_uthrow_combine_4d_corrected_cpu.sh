#!/bin/bash
#SBATCH --job-name=comb4dCc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=32G --time=02:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/comb4dCc_%j.out --error=uq_4d/corrected/logs/comb4dCc_%j.err
# P6-4D corrected unified-throw combine on CPU: 160 throw slabs + 124 block units ->
# C_unified_4d, C_blocksum_4d (MAT mean-centered 1/N), C_cross_4d. --expected-throws
# 0-159 (exact manifest); --null (fixed-seed CV re-unfold must be zero). Throw-mean
# centered with mean shift stored separately (hJointMeanShift). uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
cd "${REPO}/nd-unfolding"
echo "[comb4dCc] start $(date -u '+%F %T')"
python3 unified_throw_cov.py \
    --combine 'uq_4d/corrected/uthrow_slabs_4d/uthrow4d_slab_*.npz' --expected-throws 0-159 \
    --block-slabs 'uq_4d/corrected/uthrow_slabs_4d/block4d_*.npz' \
    --bank uq_4d/corrected/bank_uthrow_4d --iters 5 --seed 1000 --null \
    --out-root uq_4d/corrected/unified_throw_cov_4d.root
echo "[comb4dCc] DONE $(date -u '+%F %T')"
