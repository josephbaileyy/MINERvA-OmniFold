#!/bin/bash
#SBATCH --job-name=uthCombFpsC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=16 --time=01:30:00
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/uthCombFpsC_%A.out --error=uq_fps/corrected/logs/uthCombFpsC_%A.err
# CORRECTED FPS unified-throw combine: aggregate 160 seed-stamped throw slabs vs the
# 124-unit block-sum -> C_unified/C_blocksum/C_cross on the 285-bin extended grid, with
# the fixed-seed null == 0. Mandatory FPS_PILOT.md object (the migration-heavy corner
# that broke the 4D block-sum x2 is INSIDE the FPS measurement).
# -> uq_fps/corrected/unified_throw_cov_fps.root
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
NSLAB=$(ls uq_fps/corrected/uthrow_slabs_fps_neutral/uthrowfps_slab_*.npz 2>/dev/null | wc -l)
NBLK=$(ls uq_fps/corrected/uthrow_slabs_fps_neutral/blockfps_*.npz 2>/dev/null | wc -l)
[[ ${NSLAB} -eq 40 && ${NBLK} -eq 26 ]] || { echo "[FAIL] slabs=${NSLAB} (!=40) or blocks=${NBLK} (!=26)"; exit 2; }
echo "[combfpsC] start slabs=${NSLAB} blocks=${NBLK} $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py \
    --combine 'uq_fps/corrected/uthrow_slabs_fps_neutral/uthrowfps_slab_*.npz' \
    --expected-throws 0-159 \
    --block-slabs 'uq_fps/corrected/uthrow_slabs_fps_neutral/blockfps_*.npz' \
    --bank bank_uthrow_fps --iters 5 --invalid-ratio neutral --null \
    --out-root uq_fps/corrected/unified_throw_cov_fps.root
echo "[combfpsC] done $(date -u '+%F %T UTC')"
