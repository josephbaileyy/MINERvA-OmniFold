#!/bin/bash
#SBATCH --job-name=uthfps_comb
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=48G --time=03:00:00
#SBATCH --output=uq_fps/uthrowfps_comb_%A.out --error=uq_fps/uthrowfps_comb_%A.err

# Aggregate the FPS unified-throw slabs vs the FPS block-sum units -> C_unified_fps,
# C_blocksum_fps, C_cross_fps on the extended 2D grid; the fixed-seed null must be zero.
# This is the mandatory FPS_PILOT.md object (the migration-heavy corner that broke
# the 4D block sum x2 is INSIDE the FPS measurement).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
NSLAB=$(ls uq_fps/uthrow_slabs_fps/uthrowfps_slab_*.npz 2>/dev/null | wc -l)
NBLK=$(ls uq_fps/uthrow_slabs_fps/blockfps_*.npz 2>/dev/null | wc -l)
[[ ${NSLAB} -ge 18 && ${NBLK} -eq 6 ]] || { echo "[FAIL] slabs=${NSLAB} (<18) or blocks=${NBLK} (!=6)"; exit 2; }
echo "[combfps] start slabs=${NSLAB} blocks=${NBLK} $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py \
    --combine 'uq_fps/uthrow_slabs_fps/uthrowfps_slab_*.npz' \
    --expected-throws 0-159 \
    --block-slabs 'uq_fps/uthrow_slabs_fps/blockfps_*.npz' \
    --bank bank_uthrow_fps --iters 5 --null \
    --out-root uq_fps/unified_throw_cov_fps.root
echo "[combfps] done $(date -u '+%F %T UTC')"
